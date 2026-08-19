#!/usr/bin/env python3
r"""Score `ep2-b08-boardnet-0820` against the bar its spec pre-registered.

THE PARENT IS THE CONTROL, AND THAT IS THE WHOLE DESIGN OF THIS INSTRUMENT.
`ep2-b08-twinsipa-0819` and this frame share seed, prompt, negative, pose hint,
both capsule masks, both references, conditioning scale and ip-scale. The ONLY
difference is the second ControlNet. So every number below is reported as a
PAIR -- parent, then child -- and a change in any of them is attributable to
the one variable. A single-frame number would not be.

THE LUMA RULE IS ENFORCED HERE, NOT REMEMBERED. The parent's verdict
established that G-R COMPRESSES WITH LUMA: its goblin shin read +28.3 at luma
196.9 and +13.7 at luma 105.1, the same leg going into grass shadow, and a
first pass at the lower box scored a FAIL by one level on what was a lighting
gradient. So every probe here PUBLISHES ITS LUMA, and the script refuses to
report a figure's spread as a pass if its probes are not luma-comparable --
`--luma-band` is the width allowed, and a probe outside it is UNMEASURABLE
rather than scored.

    python3 pipeline/judge_b08_boardnet_0820.py            # both frames
    python3 pipeline/judge_b08_boardnet_0820.py --selftest
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parent.parent
PARENT_PNG = "farm-out/ep2-b08-twinsipa-0819/ep2-b08-twinsipa-0819-twinsipa.png"
CHILD_PNG = "farm-out/ep2-b08-boardnet-0820/ep2-b08-boardnet-0820-boardnet.png"

# The parent's six published probe boxes, carried verbatim so the two frames are
# measured in the SAME places. Same seed and same pose hint, so the limbs are in
# the same place; where one is not, it is reported rather than moved silently.
PROBES = {
    "guard": {"face": (548, 378, 600, 430),
              "forearm": (400, 645, 455, 678),
              "shin": (520, 1100, 558, 1130)},
    "goblin": {"face": (148, 448, 193, 504),
               "forearm": (212, 800, 242, 858),
               "shin": (118, 920, 152, 950)},
}
PARENT_MEASURED = {"guard": {"face": -13.9, "forearm": -3.3, "shin": -11.5},
                   "goblin": {"face": 28.1, "forearm": 27.6, "shin": 28.3}}

SPREAD_MAX = 25.0
GUARD_CEILING = 0.0
GOBLIN_FLOOR = 20.0
SEPARATION_MIN = 20.0

# B4a. The authored quad and its bounding box, straight out of the hint author.
BOARD_BBOX = (583, 657, 723, 820)
BOARD_CORNERS = [(608.6, 660.5), (719.5, 678.1), (697.7, 816.2), (586.7, 798.6)]
GUARD_SHOULDER_Y = 491.0
# A patch of the same frame that no hint touches, so "the child has more edges"
# can be separated from "the child is a busier picture everywhere".
CONTROL_BBOX = (60, 120, 340, 400)


def mean_rgb(img, box):
    px = img.crop(box).convert("RGB").getdata()
    n = len(px)
    r = sum(p[0] for p in px) / n
    g = sum(p[1] for p in px) / n
    b = sum(p[2] for p in px) / n
    return r, g, b


def green_excess(rgb):
    return rgb[1] - rgb[0]


def luma(rgb):
    # Rec.601, the same weighting PIL's "L" uses.
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def edge_energy(img, box):
    """Mean gradient magnitude and strong-edge count inside a box.

    A drawn board is an EDGE event: four straight boundaries where there were
    none. Mean luma would not see it (a grey board on grey grass moves the mean
    very little); gradient does.
    """
    from PIL import ImageFilter
    crop = img.crop(box).convert("L")
    edges = crop.filter(ImageFilter.FIND_EDGES)
    # DROP THE 1px BORDER. FIND_EDGES has no data beyond the crop, so it lights
    # the entire outer ring at full intensity -- a flat grey square comes back
    # with a bright frame around it. Measuring that would mean every box scored
    # its own boundary, and the smaller the box the bigger the artifact. Caught
    # by this file's own selftest on a flat field.
    w, h = edges.size
    if w > 2 and h > 2:
        edges = edges.crop((1, 1, w - 1, h - 1))
    hist = edges.histogram()
    n = sum(hist)
    mean = sum(i * v for i, v in enumerate(hist)) / n
    strong = sum(hist[40:]) / n
    return mean, strong


def score_figure(img, who, band):
    out = {}
    for name, box in PROBES[who].items():
        rgb = mean_rgb(img, box)
        out[name] = {"box": box, "gr": green_excess(rgb), "luma": luma(rgb)}
    lumas = [v["luma"] for v in out.values()]
    grs = [v["gr"] for v in out.values()]
    spread = max(grs) - min(grs)
    luma_spread = max(lumas) - min(lumas)
    return {"regions": out, "spread": spread, "luma_spread": luma_spread,
            "luma_ok": luma_spread <= band}


def report(path, band):
    from PIL import Image
    img = Image.open(path).convert("RGB")
    res = {"path": str(path), "size": img.size}
    for who in ("guard", "goblin"):
        res[who] = score_figure(img, who, band)
    res["separation"] = (res["goblin"]["regions"]["face"]["gr"]
                         - res["guard"]["regions"]["face"]["gr"])
    res["board"] = {"bbox": BOARD_BBOX, "edges": edge_energy(img, BOARD_BBOX)}
    res["control"] = {"bbox": CONTROL_BBOX, "edges": edge_energy(img, CONTROL_BBOX)}
    res["frame_luma"] = luma(mean_rgb(img, (0, 0, img.size[0], img.size[1])))
    return res


def show(tag, r):
    print("\n=== %s  %s  %s" % (tag, r["size"], r["path"]))
    for who in ("guard", "goblin"):
        f = r[who]
        print("  %-6s spread %5.1f   luma spread %5.1f  %s"
              % (who, f["spread"], f["luma_spread"],
                 "" if f["luma_ok"] else "<-- NOT LUMA-MATCHED, UNMEASURABLE"))
        for name in ("face", "forearm", "shin"):
            v = f["regions"][name]
            print("         %-8s box %-22s G-R %+6.1f   luma %5.1f"
                  % (name, str(v["box"]), v["gr"], v["luma"]))
    print("  face separation  %+.1f" % r["separation"])
    print("  board bbox %s   mean-grad %6.2f   strong-edge frac %.4f"
          % (str(r["board"]["bbox"]), r["board"]["edges"][0],
             r["board"]["edges"][1]))
    print("  control    %s   mean-grad %6.2f   strong-edge frac %.4f"
          % (str(r["control"]["bbox"]), r["control"]["edges"][0],
             r["control"]["edges"][1]))
    print("  frame mean luma %.1f" % r["frame_luma"])


def verdict(p, c):
    print("\n" + "=" * 72)
    print("SCORED AGAINST THE PRE-REGISTERED BAR (parent -> child)")
    print("=" * 72)
    ok = True

    for who, ceiling, floor in (("guard", GUARD_CEILING, None),
                                ("goblin", None, GOBLIN_FLOOR)):
        f = c[who]
        good = f["spread"] <= SPREAD_MAX and f["luma_ok"]
        signs = all(v["gr"] <= ceiling for v in f["regions"].values()) \
            if ceiling is not None \
            else all(v["gr"] >= floor for v in f["regions"].values())
        print("B7  %-6s spread %5.1f (bar <=%.1f, parent %5.1f)  signs %s  %s"
              % (who, f["spread"], SPREAD_MAX, p[who]["spread"],
                 "ok" if signs else "WRONG",
                 "PASS" if (good and signs) else "FAIL"))
        ok = ok and good and signs

    sep_ok = c["separation"] >= SEPARATION_MIN
    print("B2  face separation %+.1f (bar >=%.1f, parent %+.1f)  %s"
          % (c["separation"], SEPARATION_MIN, p["separation"],
             "PASS" if sep_ok else "FAIL"))
    ok = ok and sep_ok

    pb, cb = p["board"]["edges"], c["board"]["edges"]
    pc, cc = p["control"]["edges"], c["control"]["edges"]
    # Normalised against the untouched patch, so a globally busier frame does
    # not read as a board.
    p_rel = pb[0] / pc[0] if pc[0] else float("inf")
    c_rel = cb[0] / cc[0] if cc[0] else float("inf")
    print("B4a board region  mean-grad %6.2f -> %6.2f   strong-edge %.4f -> %.4f"
          % (pb[0], cb[0], pb[1], cb[1]))
    print("    control patch mean-grad %6.2f -> %6.2f   (normalised %.2f -> %.2f)"
          % (pc[0], cc[0], p_rel, c_rel))
    print("    ^ NUMBERS ONLY. 'Legible clipboard' is the beat's word and is")
    print("      scored BY EYE at 1:1 and 3x; this says whether anything")
    print("      structural arrived where it was asked for.")
    print("\nB1/B3/B5/B6/B8 are read by eye against the parent at 3x.")
    print("OVERALL (measured clauses only): %s" % ("PASS" if ok else "FAIL"))
    return ok


def selftest():
    fails = []

    def check(label, cond):
        print("  %s %s" % ("ok  " if cond else "FAIL", label))
        if not cond:
            fails.append(label)

    from PIL import Image
    check("the probe boxes are the parent's published six",
          len(PROBES["guard"]) == 3 and len(PROBES["goblin"]) == 3)
    check("the board bbox encloses all four authored corners",
          all(BOARD_BBOX[0] <= x <= BOARD_BBOX[2]
              and BOARD_BBOX[1] <= y <= BOARD_BBOX[3] for x, y in BOARD_CORNERS))
    check("the board sits below the guard's shoulder",
          BOARD_BBOX[1] > GUARD_SHOULDER_Y)
    check("the control patch does not overlap the board region",
          CONTROL_BBOX[2] <= BOARD_BBOX[0] or CONTROL_BBOX[0] >= BOARD_BBOX[2]
          or CONTROL_BBOX[3] <= BOARD_BBOX[1] or CONTROL_BBOX[1] >= BOARD_BBOX[3])

    # green_excess and luma on synthetic swatches
    g = Image.new("RGB", (10, 10), (60, 140, 60))
    h = Image.new("RGB", (10, 10), (200, 180, 170))
    check("a green swatch reads positive G-R",
          green_excess(mean_rgb(g, (0, 0, 10, 10))) > 20)
    check("a pale swatch reads negative G-R",
          green_excess(mean_rgb(h, (0, 0, 10, 10))) < 0)
    check("luma tracks brightness",
          luma(mean_rgb(h, (0, 0, 10, 10))) > luma(mean_rgb(g, (0, 0, 10, 10))))

    # a drawn edge must register where a flat field does not
    flat = Image.new("RGB", (80, 80), (120, 120, 120))
    drawn = flat.copy()
    from PIL import ImageDraw
    ImageDraw.Draw(drawn).rectangle([20, 20, 60, 60], outline=(240, 240, 240),
                                    width=3)
    check("edge_energy sees a drawn rectangle that a flat field lacks",
          edge_energy(drawn, (0, 0, 80, 80))[0]
          > edge_energy(flat, (0, 0, 80, 80))[0] + 1.0)
    check("a flat field has essentially no strong edges",
          edge_energy(flat, (0, 0, 80, 80))[1] < 0.01)

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", default=PARENT_PNG)
    ap.add_argument("--child", default=CHILD_PNG)
    ap.add_argument("--luma-band", type=float, default=60.0,
                    help="max luma spread across a figure's three probes "
                         "before they stop being comparable")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    pp = Path(a.parent) if Path(a.parent).is_absolute() else REPO / a.parent
    cp = Path(a.child) if Path(a.child).is_absolute() else REPO / a.child
    if not pp.exists():
        print("parent frame missing: %s" % pp, file=sys.stderr)
        return 2
    if not cp.exists():
        print("child frame missing: %s -- has it landed?" % cp, file=sys.stderr)
        return 2
    p, c = report(pp, a.luma_band), report(cp, a.luma_band)
    show("PARENT (control)", p)
    show("CHILD  (this rung)", c)
    return 0 if verdict(p, c) else 1


if __name__ == "__main__":
    raise SystemExit(main())
