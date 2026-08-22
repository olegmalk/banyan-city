#!/usr/bin/env python3
r"""COUNT A COMPOSITED OBJECT, FRAME BY FRAME, AND FLAG WHEN THE COUNT MOVES.

    python3 pipeline/count_composited_objects.py \
        --clip farm-out/ep2-b19-dropmotion-r2-0822/19-the-drop-...mp4 \
        --geometry farm-out/ep2-b19-figcomp-0822/b19-figcomp-in-0822.png.geometry.json \
        --class fig
    python3 pipeline/count_composited_objects.py --selftest

WHY THIS EXISTS. On 2026-08-22 two independent beats measured the same fault in
one morning: `ep2-b19-dropmotion-r2-0822` put TWO EXTRA FIGS in the sky off a
plate with exactly one, and `ep2-b21-twoleaf-r2-0822` grew a THIRD BLADE off a
plate with exactly two -- with the correct count named in the positive, in a
sentence written for that plate. The ladder's conclusion:

  > A COMPOSITED OBJECT HOLDS ITS IDENTITY THROUGH MOTION (b12's leaves), ITS
  > SIZE (b06's board) AND ITS POSITION AT THE START (b19) -- BUT IT DOES NOT
  > STOP THE MODEL ADDING MORE OF IT. That is a fourth axis and it is the one
  > still open. The next instrument for it is NOT a seventh adjective; the
  > wording ladder for leaf count closed by measurement on 08-17 at 0 of 16
  > frames.

So this is the instrument instead of the adjective. It is only possible because
the object was COMPOSITED: the tool that drew it wrote down the palette it drew
it in, where it drew it and how big -- `beat16_sapling_composite.py`'s geometry
json. Nothing here is a detector trained on anything; it is arithmetic over
numbers this repo already recorded.

THE ONE THING THAT DOES NOT WORK, AND IT IS THE OBVIOUS ONE. "Count connected
components in the object's palette band" counts FIGS correctly and counts LEAVES
wrong, because two leaves on one stem are ONE component -- they meet at the
apex, so the answer is 1 whether the plant has two blades or five. Measured on
beat 21's frame 1: the whole leaf pair came back as a single 43,179 px blob.

  > A BLADE IS A LOBE, NOT A COMPONENT. The stem is thin and the blades are fat,
  > so eroding the mask by more than the stem's half-width and less than a
  > blade's disconnects the blades from each other and from the plant. Count the
  > survivors. This is the classic distance-transform separation and it costs
  > one binary erosion per frame.

AND EROSION ALONE IS NOT ENOUGH EITHER, which took a second measurement to find.
Beat 21's third blade grows in ALONGSIDE the second and the two share a long
edge, so they are one fat region and no erosion radius splits them: swept from 6
to 45 px, the count is 2 at every radius on the frame where the eye plainly sees
3. What separates them is the thing this dialect draws between any two shapes --
THE INK LINE. So the fill mask has the plate's own ink colour SUBTRACTED from it
before the erosion, and the blades come apart along the outline the artist
already drew. With that in, beat 21 reads 2 at frame 0 and 3 at frame 118, which
is what the verdict says by eye.

  > THE INK IS NOT NOISE TO BE CLEANED OFF A CEL FRAME. It is the frame's own
  > statement about where one object stops and the next begins, and a counter
  > that throws it away is counting silhouettes instead of objects.

A FIG needs no erosion (it is already a disconnected blob) and gets one anyway,
at a smaller radius, because it costs nothing and it kills the antialiasing
fringe that a colour band picks up along an edge.

WHAT EACH CLASS LOOKS AT, and the difference is not cosmetic:

  leaf  the plant's own palette, inside the PLANT'S EXTENT padded by --roi-pad.
        An extra leaf grows ON the plant, so the plant's neighbourhood is the
        right place to look, and restricting there is what keeps a green field
        band or a bank of grass out of the count.
  fig   the fig's own fill colour, over THE WHOLE FRAME. b19's extra figs
        appeared floating in the SKY, nowhere near the plant, so a region
        restriction would have missed exactly the fault this was built for. It
        can afford the whole frame because canon violet is a colour the plate
        does not otherwise contain.

A MEASURED LIMIT, found on beat 16 the day this was written. Pointed at
`ep2-b16-plantmotion-0822` the leaf class reads SIXTEEN objects at frame 0,
because that plant stands in GRASS OF ITS OWN PALETTE inside its own ROI. The
leaf class works where the plant is silhouetted against something that is not
its colour -- beat 12's cumulus, beat 21's sky and golden field -- and it does
not work where the plant stands in matching foliage. An opening count that is
not the number you drew is the tool telling you it cannot see this beat; it is
not a count fault, and it is not something to threshold around.

WHAT IT IS NOT. It is not a taste judgement and it does not know what a leaf
looks like. It answers one question -- did the number of objects in the
object's own colour change during the clip -- and it answers it as a NUMBER
PER FRAME so a reader can see whether the count wobbled for two frames or
climbed and stayed. A flag is a reason to LOOK, and the eye is still the
instrument, which is this tree's standing rule about every metric it owns.

$0. numpy + scipy + ffmpeg. No model, no network, no GPU.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The three clips the instrument is calibrated on, and it is calibrated on all
# three at once with ONE parameter set. Two must flag and one must not; a
# threshold that only satisfies two of the three is not a threshold, it is a
# fit. See --selftest.
SELFTEST = [
    {
        "name": "b19 two extra figs",
        "clip": ("farm-out/ep2-b19-dropmotion-r2-0822/"
                 "19-the-drop-LTX-ep2-b19-dropmotion-r2-0822.mp4"),
        "geometry": ("farm-out/ep2-b19-figcomp-0822/"
                     "b19-figcomp-in-0822.png.geometry.json"),
        "cls": "fig",
        "must_flag": True,
        "note": ("the verdict says TWO EXTRA FIGS APPEAR FLOATING IN THE SKY at "
                 "the end, so the last second has three fruit where the beat "
                 "wants one"),
    },
    {
        "name": "b21 third blade",
        "clip": ("farm-out/ep2-b21-twoleaf-r2-0822/"
                 "21-the-answer-LTX-poolD-0812.mp4"),
        "geometry": ("farm-out/ep2-b21-sapnat-0822/"
                     "b21-sapnat-in-0822.png.geometry.json"),
        "cls": "leaf",
        "must_flag": True,
        "note": ("round 2 named the count in the positive -- THE PLANT HAS "
                 "EXACTLY TWO LEAVES AND KEEPS EXACTLY TWO -- and the third "
                 "blade still grows in"),
    },
    {
        "name": "b12 holds two",
        "clip": ("review/ep2-beats-0821/candidates/"
                 "12-related-LTX-leaf-0813.mp4"),
        "geometry": ("farm-out/ep2-b12-sapnat-0822/"
                     "b12-sapnat-in-0822.png.geometry.json"),
        "cls": "leaf",
        "must_flag": False,
        "note": ("exactly two average leaves on one stem in every frame of 121 "
                 "-- the first time canon's leaf shape survived a full render, "
                 "so a flag here is a FALSE POSITIVE and kills the instrument"),
    },
]


def read_frames(clip, stride=1, limit=None):
    """Decode to raw rgb24 through ffmpeg. No temp files, no image library."""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames",
         "-of", "csv=p=0", clip],
        capture_output=True, text=True, encoding="utf-8",
        check=True).stdout.strip()
    w, h, n = (int(v) for v in probe.split(",")[:3])
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", clip,
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True)
    buf = np.frombuffer(proc.stdout, dtype=np.uint8)
    got = buf.size // (w * h * 3)
    frames = buf[:got * w * h * 3].reshape(got, h, w, 3)
    if limit:
        frames = frames[:limit]
    return frames[::stride], (w, h, n)


def class_spec(geom, cls, size):
    """Colours, region and erosion radius for one object class, off the json the
    compositor wrote. Everything scales if the clip is not the plate's size."""
    gw, gh = geom.get("size", size)
    sx, sy = size[0] / float(gw), size[1] / float(gh)
    if cls == "fig":
        fig = geom.get("fig")
        if not fig:
            raise SystemExit("!! this geometry json has no `fig` -- the plate "
                             "it describes has no composited fruit in it")
        rx, ry = fig["radii"]
        rx, ry = rx * sx, ry * sy
        return {
            "colours": [tuple(fig["fill"])],
            "ink": tuple(geom["palette"]["ink"]),
            # THE WHOLE FRAME. b19's extras were in the sky.
            "roi": (0, size[0], 0, size[1]),
            # A radius that keeps the fig and kills a colour fringe: a quarter
            # of the fig's smaller radius, floored at 2.
            "erode": max(2, int(min(rx, ry) * 0.25)),
            "ref_area": 3.1416 * rx * ry,
            # MEASURED ON b19, not shared with the leaf class. At 90 the fig is
            # only found on 62 of 105 frames -- LTX shifts a small violet blob
            # far enough that a tight band loses it -- and the extras register
            # on 3 scattered frames. At 120 the single fig holds for 98 frames
            # and the count rises to 2 and 3 across f098-f104 UNBROKEN, which
            # is the verdict's own "the last second has three fruit". At 150
            # the band starts eating the plate and the opening frame already
            # reads 2. A fig is one small object on a plate with no other
            # violet, so it can afford a wider band than a leaf on a green one.
            "tol": 120,
            "what": "one fig at %.0fx%.0f px" % (2 * rx, 2 * ry),
        }
    pal = geom["palette"]
    x0, x1, y0, y1 = geom["plant_extent"]
    x0, x1, y0, y1 = x0 * sx, x1 * sx, y0 * sy, y1 * sy
    # THE BLADE'S HALF-WIDTH IS THE EROSION SCALE and it comes from the drawing.
    # `_blade`'s profile peaks at LEAF_NORM of its length, and the tool draws a
    # blade whose width is 0.42 of its length, so half-width ~= 0.21 * len. Take
    # a third of that: comfortably over any stem (the tool's stems run 8-16 px)
    # and comfortably under a blade.
    leaf_len = float(geom.get("leaf_len_px", 200.0)) * (sx + sy) / 2.0
    # MEASURED ON TWO PLANTS, not derived from the drawing's own constants. The
    # radius has to clear the stem (the tool draws 8-16 px) and stay inside a
    # blade. Measured over whole clips, not sampled frames: beat 21 peaks at 3
    # blades on 56 of 121 frames at radius 9, on 14 frames at 10, and NEVER at
    # 11 -- the window closes fast on the upper side because the third blade
    # arrives narrow. Beat 12 reads 2 on all 121 frames at 8, 9, 10 and 11, so
    # it constrains nothing and beat 21 sets the number. 0.033 of the leaf
    # length lands at 9 and 8.
    erode = max(6, int(round(0.033 * leaf_len)))
    return {
        "colours": [tuple(pal[k]) for k in ("dark", "mid", "light")],
        "ink": tuple(pal["ink"]),
        "roi": (x0, x1, y0, y1),
        "erode": erode,
        "ref_area": (0.42 * leaf_len) * leaf_len * 0.5,
        "tol": 90,
        "what": "blades on a plant whose leaf is %.0f px" % leaf_len,
    }


def count_frame(rgb, spec, tol, roi_pad, min_area_frac, ndi, ink_tol=120):
    H, W, _ = rgb.shape
    a = rgb.astype(np.int16)
    m = np.zeros((H, W), bool)
    for c in spec["colours"]:
        m |= np.abs(a - np.array(c, dtype=np.int16)).sum(axis=2) <= tol
    # CUT THE MASK ALONG THE PLATE'S OWN INK, so two blades that share an edge
    # are two objects and not one fat region. Dilated by one so an antialiased
    # line still cuts.
    inked = np.abs(a - np.array(spec["ink"], dtype=np.int16)).sum(axis=2) <= ink_tol
    m &= ~ndi.binary_dilation(inked, np.ones((3, 3)), iterations=1)
    x0, x1, y0, y1 = spec["roi"]
    px, py = (x1 - x0) * roi_pad, (y1 - y0) * roi_pad
    r = np.zeros((H, W), bool)
    r[max(0, int(y0 - py)):min(H, int(y1 + py)),
      max(0, int(x0 - px)):min(W, int(x1 + px))] = True
    m &= r
    m = ndi.binary_opening(m, np.ones((3, 3)), iterations=1)
    e = ndi.binary_erosion(m, ndi.generate_binary_structure(2, 1),
                           iterations=spec["erode"])
    lab, n = ndi.label(e)
    if n == 0:
        return 0, []
    sizes = ndi.sum(e, lab, range(1, n + 1))
    floor = max(min_area_frac * H * W, spec["ref_area"] * 0.05)
    keep = [int(s) for s in sizes if s >= floor]
    return len(keep), sorted(keep, reverse=True)


def run(clip, geometry, cls, expect=None, tol=None, roi_pad=0.12,
        min_area_frac=0.0006, stride=1, quiet=False, ink_tol=120,
        min_run=2):
    from scipy import ndimage as ndi                          # noqa: WPS433
    clip_p = clip if os.path.isabs(clip) else os.path.join(REPO, clip)
    geom_p = geometry if os.path.isabs(geometry) else os.path.join(REPO,
                                                                   geometry)
    with open(geom_p, encoding="utf-8") as fh:
        geom = json.load(fh)
    frames, (w, h, n) = read_frames(clip_p, stride=stride)
    spec = class_spec(geom, cls, (w, h))
    tol = spec["tol"] if tol is None else tol
    counts = [count_frame(f, spec, tol, roi_pad, min_area_frac, ndi,
                          ink_tol=ink_tol)[0]
              for f in frames]
    # THE EXPECTED COUNT IS THE CLIP'S OWN OPENING, not a number typed in. The
    # init is the thing the beat was filed with, so frame 0 is the ground truth
    # a count fault is a departure FROM. A caller may still pin it with
    # --expect, and the b19 case is why: if the very first frame is already
    # wrong, the clip has a different fault and this instrument should say so
    # rather than normalise it away.
    opening = counts[0] if expect is None else int(expect)
    # THE TWO DIRECTIONS ARE NOT THE SAME FINDING and collapsing them is how a
    # metric passes a selftest for the wrong reason. This was caught here: the
    # first version flagged beat 21 and looked right, and it was flagging six
    # frames where the count fell to 1 -- a detector dropout while the plant
    # swung through a dark band -- while never once seeing the third blade the
    # verdict is about.
    #   ABOVE  the model ADDED an object. That is the axis this exists for and
    #          it is the only thing that raises the flag.
    #   BELOW  the object left the mask: an occlusion, a colour drift, a blade
    #          turned edge-on. Reported, never flagged, because "I stopped
    #          seeing it" is a statement about the instrument.
    hi = [i for i, c in enumerate(counts) if c > opening]
    # AND A COUNT FAULT PERSISTS. One frame in 121 is the detector, not the
    # model: beat 12 -- the clip that holds two leaves for its whole length and
    # is the negative control here -- reads 3 on frame 109 and only frame 109.
    # Beat 19's extras run f098-f104 unbroken and beat 21's third blade runs 55
    # frames, so the real faults clear a two-frame floor by a wide margin and
    # the false positive does not clear it at all. This is the ONLY threshold in
    # the tool chosen to make a case pass, and it is named here for that reason.
    runs, cur = [], []
    for i in hi:
        if cur and i == cur[-1] + 1:
            cur.append(i)
        else:
            if cur:
                runs.append(cur)
            cur = [i]
    if cur:
        runs.append(cur)
    kept = [i for r in runs if len(r) >= min_run for i in r]
    dropped = [i for r in runs if len(r) < min_run for i in r]
    above = [(i * stride, counts[i]) for i in kept]
    blips = [(i * stride, counts[i]) for i in dropped]
    below = [(i * stride, c) for i, c in enumerate(counts) if c < opening]
    bad = above
    if not quiet:
        print("clip     %s" % os.path.relpath(clip_p, REPO))
        print("geometry %s" % os.path.relpath(geom_p, REPO))
        print("class    %-5s  %s" % (cls, spec["what"]))
        print("params   tol=%d ink_tol=%d roi_pad=%.2f erode=%d "
              "min_area=%.4f%% stride=%d"
              % (tol, ink_tol, roi_pad, spec["erode"], 100 * min_area_frac,
                 stride))
        print("frames   %d decoded at %dx%d" % (len(frames), w, h))
        runs, cur, start = [], counts[0], 0
        for i, c in enumerate(counts + [None]):
            if c != cur:
                runs.append((start * stride, (i - 1) * stride, cur))
                cur, start = c, i
        print("counts   " + "  ".join("f%03d-%03d:%d" % r for r in runs))
        print("opening  %d  |  above it: %d frames  |  below it: %d frames"
              % (opening, len(above), len(below)))
        if blips:
            print("blip     %d isolated frame(s) read above %d and are under "
                  "the %d-frame persistence floor: %s"
                  % (len(blips), opening, min_run,
                     ", ".join("f%03d" % f for f, _ in blips)))
        if below:
            print("note     the count DROPS below %d on %d frame(s) -- that is "
                  "the object leaving the mask, not the model removing it, and "
                  "it is not a flag" % (opening, len(below)))
        if above:
            print("FLAG     the count RISES above %d at f%03d and reaches %d "
                  "on %d frame(s) -- go and look"
                  % (opening, above[0][0], max(c for _, c in above),
                     len([1 for _, c in above if c == max(c for _, c in above)])))
        else:
            print("ok       the count never rises above %d" % opening)
    return {"counts": counts, "opening": opening, "bad": bad,
            "above": above, "below": below, "blips": blips,
            "flagged": bool(above), "stride": stride,
            "erode": spec["erode"], "size": [w, h]}


def selftest(tol=None, roi_pad=0.12, min_area_frac=0.0006, stride=1):
    ok = True
    for case in SELFTEST:
        for f in (case["clip"], case["geometry"]):
            if not os.path.isfile(os.path.join(REPO, f)):
                print("SKIP  %-22s missing %s" % (case["name"], f))
                break
        else:
            r = run(case["clip"], case["geometry"], case["cls"], tol=tol,
                    roi_pad=roi_pad, min_area_frac=min_area_frac,
                    stride=stride, quiet=True)
            good = r["flagged"] == case["must_flag"]
            ok &= good
            print("%-4s  %-22s opening=%d peak=%d above=%d below=%d of %d "
                  "(want %s)"
                  % ("PASS" if good else "FAIL", case["name"], r["opening"],
                     max(r["counts"]), len(r["above"]), len(r["below"]),
                     len(r["counts"]),
                     "flag" if case["must_flag"] else "no flag"))
            print("      %s" % case["note"])
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clip")
    ap.add_argument("--geometry", help="the compositor's <init>.geometry.json")
    ap.add_argument("--class", dest="cls", choices=("leaf", "fig"))
    ap.add_argument("--expect", type=int, default=None,
                    help="pin the expected count; default is frame 0's")
    ap.add_argument("--tol", type=int, default=None,
                    help="sum-of-channels distance to a palette colour. "
                         "DEFAULT IS PER CLASS -- 90 for a leaf, 120 for a fig "
                         "-- and both are measured; see class_spec.")
    ap.add_argument("--ink-tol", type=int, default=120,
                    help="sum-of-channels distance to the PLATE'S INK. Pixels "
                         "inside it are cut out of the mask so two blades "
                         "sharing an outline are two objects. 0 disables it and "
                         "beat 21's third blade becomes invisible at every "
                         "erosion radius from 6 to 45.")
    ap.add_argument("--roi-pad", type=float, default=0.12,
                    help="fraction of the plant's extent to look beyond it "
                         "(leaf class only; fig looks at the whole frame)")
    ap.add_argument("--min-area-frac", type=float, default=0.0006)
    ap.add_argument("--min-run", type=int, default=2,
                    help="consecutive frames the count must stay above the "
                         "opening before it is a flag rather than a blip")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--json-out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    if a.selftest:
        return selftest(tol=a.tol, roi_pad=a.roi_pad,
                        min_area_frac=a.min_area_frac, stride=1)
    if not (a.clip and a.geometry and a.cls):
        ap.error("pass --clip, --geometry and --class, or --selftest")
    r = run(a.clip, a.geometry, a.cls, expect=a.expect, tol=a.tol,
            roi_pad=a.roi_pad, min_area_frac=a.min_area_frac, stride=a.stride,
            ink_tol=a.ink_tol, min_run=a.min_run)
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1, sort_keys=True)
        print("wrote %s" % a.json_out)
    # NONZERO ON A FLAG so this can be a judge step in a chain. A flag is "go
    # and look", not "the clip is rejected" -- the eye is still the instrument.
    return 3 if r["flagged"] else 0


if __name__ == "__main__":
    sys.exit(main())
