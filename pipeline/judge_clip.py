#!/usr/bin/env python3
"""Three readings on a clip, deliberately NOT blended into a score.

    python3 pipeline/judge_clip.py clip.mp4 [more.mp4 ...] [--json]
    python3 pipeline/judge_clip.py clip.mp4 --geometry <init>.geometry.json \
                                            --class leaf|fig

    HOLD    period / strength / distinct pictures / effective fps, from
            `hold_period.py`. Autocorrelation, so it sees odd periods that the
            retired `cadence` parity ratio aliased to 1.00x.
    DEPTH   `depth()` from `vae_roundtrip.py`. Autocorrelation is scale-free by
            construction, so a +-3% ripple with a clean period reads like a
            freeze; depth is the number that separates them.
              refs: b13-AFTER 0.029 real hold | b06-DONE 0.215 | b02-FIXED 0.397
    COUNT   OPTIONAL, and only for a beat whose object was COMPOSITED: how
            many of that object are in each frame, and whether the number ever
            rises above the one the clip opens on. Needs --geometry and
            --class; see count_composited_objects.py. The three readings below
            are all about HOW MUCH the picture changes and none of them can see
            HOW MANY of a thing is in it -- beats 19 and 21 both scored
            normally on 2026-08-22 while growing an extra object.
    FREEZE  the terminal-freeze index: the length of the trailing run of
            consecutive-frame ncc == 1.0000.

WHY FREEZE IS REPORTED SEPARATELY AND NOT FOLDED INTO THE HOLD. They are
different failures and the hold metrics cannot see the difference. On 2026-08-16
`ep2-b06-bark-f1s3-0815` came back period 2, strength 0.92, depth 0.61 -- the
HIGHEST depth of its wave -- and it is frozen solid for its last 27 frames of 97.
Its siblings froze for 6, 3 and 1 frames with periods and strengths in the same
band. Nothing in the autocorrelation moved. A clip that holds every second frame
and a clip that stops dead at f70 are not the same defect, must not average into
one number, and the second one is invisible unless you measure it directly.

AND WHY THE DEPTH ON THAT CLIP WAS HIGH RATHER THAN LOW, which is the trap worth
naming: the clip failed by the camera pushing in on a static subject. A camera
closing steadily produces large, evenly spaced pair differences and reads as
healthy motion. Depth answers "how deep is the hold", never "is the RIGHT thing
moving". THE METRIC IS A FILTER, NEVER A VERDICT -- it chooses which frames to
open. `pipeline/coldread_frames.py` and your own eyes decide.

THE CLEANEST COUNTEREXAMPLE ON RECORD, AND THE ONE TO REMEMBER BEFORE YOU TRUST
DEPTH AS AN ACTION SIGNAL. `ep2-b06-d1neg-0816`, 2026-08-16: period 2, depth
**0.516** -- higher than the `b02-FIXED` reference of 0.397, the best number in
its wave -- and it contains **ZERO human motion**. Its beat is "GUARD 2 turns
over a clipboard made of bark and reads". Read its frames 28-39 consecutively:
the guard's head, gaze, shoulders and arms do not displace by a pixel, and the
second guard behind him is equally frozen. What the collar contour, the jaw and
the eye shapes DO is wobble and redraw from frame to frame -- the drawing is
RE-INKED IN PLACE. That re-inking, plus a board sliding in front of a still
figure and a drifting camera, is the entire 0.516.

So the failure mode has two faces and depth is blind to both: a push-in on a
static subject inflates it (f1s3, 0.606), and a re-inked still figure inflates it
(d1neg, 0.516). By 2026-08-16 SIX independent lanes had reported the identical
signature -- identical pose at f0 and f96, linework redrawn between frames.
"THE PICTURE CHANGED" IS NOT "THE ACTION PERFORMED", and every number in this
file measures the first. There is no threshold on any of these metrics that
separates a figure acting from a figure being redrawn; only opening the frames
does, and if the body's pose at f0 and f96 is the same then no depth, period or
strength value redeems the clip.

Camera scale is deliberately not computed here: the chained-NCC method rails to
its search boundary when the fit fails and then reports 1.000x for the wrong
reason (c870f08f).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hold_period import _ffmpeg, measure, pair_differences, probe  # noqa: E402
from vae_roundtrip import depth  # noqa: E402

# ncc is computed in float64 on 1/4-scale gray frames; identical frames give
# exactly 1.0, and this tolerance only absorbs the last ulp of that arithmetic.
# It is NOT a "near enough" band -- a 0.9999 pair is a real, if small, change.
FREEZE_EPS = 5e-5
FREEZE_SCALE = 4


def frames_gray(path: str, scale: int = FREEZE_SCALE):
    """The whole clip as gray frames at 1/scale.

    `-vsync 0` for the same reason `hold_period.pair_differences` uses it: a
    decoder that helpfully retimes frames would forge the very freeze we measure.
    """
    import numpy as np

    w, h, _fps = probe(path)
    sw, sh = max(8, w // scale), max(8, h // scale)
    sw, sh = sw - (sw % 2), sh - (sh % 2)
    r = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-vsync", "0",
         "-vf", "scale=%d:%d,format=gray" % (sw, sh), "-f", "rawvideo", "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s"
                           % (path, r.stderr.decode("utf-8", "replace")[:300]))
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (sw * sh)
    if n < 3:
        raise RuntimeError("only %d frames decoded from %s" % (n, path))
    return buf[:n * sw * sh].reshape(n, sh, sw).astype("float64")


def ncc_pairs(f):
    """Normalised cross-correlation for each consecutive frame pair."""
    import numpy as np

    out = []
    for i in range(len(f) - 1):
        a = f[i].ravel() - f[i].mean()
        b = f[i + 1].ravel() - f[i + 1].mean()
        den = float(np.sqrt((a * a).sum() * (b * b).sum()))
        out.append(1.0 if den == 0 else float((a * b).sum() / den))
    return out


def terminal_freeze(nccs, eps: float = FREEZE_EPS) -> int:
    """Frames in the trailing run of ncc == 1.0000 -- how long the clip is dead."""
    run = 0
    for v in reversed(nccs):
        if v >= 1.0 - eps:
            run += 1
        else:
            break
    return run


def count_reading(path: str, geometry: str, cls: str) -> dict:
    """THE FOURTH READING, AND IT IS OPTIONAL BECAUSE IT NEEDS SOMETHING THE
    CLIP DOES NOT CARRY: the geometry json the compositor wrote when it drew the
    object. Only a beat whose object was COMPOSITED can be counted, which is
    also the only kind of beat where a count is a defined question.

    It exists because the three readings above are all about HOW MUCH the
    picture changes and none of them can see HOW MANY of a thing is in it. On
    2026-08-22 beat 19 put two extra figs in the sky and beat 21 grew a third
    blade; both clips score normally on hold, depth and freeze, because adding
    an object is not a motion defect. See count_composited_objects.py."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import count_composited_objects as C          # noqa: WPS433
    r = C.run(path, geometry, cls, quiet=True)
    return {"count_opening": r["opening"], "count_peak": max(r["counts"]),
            "count_above_frames": len(r["above"]),
            "count_below_frames": len(r["below"]),
            "count_blip_frames": len(r["blips"]),
            "count_flagged": r["flagged"]}


def judge(path: str, geometry: str = None, cls: str = None) -> dict:
    res = measure(path)
    series, _fps, _dims, n = pair_differences(path)
    dep = depth(series, res.get("period"))
    nccs = ncc_pairs(frames_gray(path))
    tail = terminal_freeze(nccs)
    return {
        "clip": path,
        "frames": n,
        "period": res.get("period"),
        "strength": res.get("strength"),
        "distinct_pictures": res.get("distinct_pictures"),
        "effective_fps": res.get("effective_fps"),
        "reading": res.get("reading"),
        "depth": None if dep is None else round(dep, 3),
        "terminal_freeze_frames": tail,
        "terminal_freeze_starts_at_frame": (len(nccs) + 1 - tail) if tail else None,
        "min_ncc": round(min(nccs), 5),
        "max_ncc": round(max(nccs), 5),
    } | (count_reading(path, geometry, cls) if (geometry and cls) else {})


def print_report(r: dict) -> None:
    print("=" * 78)
    print(Path(r["clip"]).name)
    if "error" in r:
        print("  ERROR %s" % r["error"])
        return
    print("  HOLD    period %s  strength %s  distinct %s  eff-fps %s"
          % (r["period"], r["strength"], r["distinct_pictures"], r["effective_fps"]))
    print("          (HOW OFTEN A NEW PICTURE ARRIVES, and NOT whether the body")
    print("           acted: b17-full-s1, the one clip on record that performs")
    print("           its action, reads 24.0 distinct -- WORSE than the frozen")
    print("           b13 control's 32.0. For 'did the body move' use")
    print("           pipeline/body_motion.py median over a LADDER of pairs.)")
    # The old line here printed "(b13 0.029 hold | b06-DONE 0.215 | b02-FIXED
    # 0.397)", which reads as a ladder where higher is better. IT IS NOT ONE.
    # Depth is INVERTED as an action signal and the reference points that prove
    # it are printed instead, every run, so no lane can rank by depth without
    # reading why it must not. (727de28b / 77cc8277; docstring above.)
    print("  DEPTH   %s   RETIRED AS AN ACTION SIGNAL -- IT IS INVERTED."
          % r["depth"])
    print("          observed: 0.038 b13 control (FROZEN) < 0.293 b17-full-s1")
    print("          (A COMPLETE STAND-UP) < 0.516 b06-d1neg (NO HUMAN MOTION).")
    print("          Do not rank, threshold or judge by it in either direction.")
    if r["terminal_freeze_frames"]:
        print("  FREEZE  %d frames dead at the tail, from frame %d -- ncc 1.0000"
              % (r["terminal_freeze_frames"], r["terminal_freeze_starts_at_frame"]))
    else:
        print("  FREEZE  none")
    if "count_opening" in r:
        print("  COUNT   opens at %d, peaks at %d; %d frame(s) above it, %d "
              "below, %d isolated blip(s)"
              % (r["count_opening"], r["count_peak"], r["count_above_frames"],
                 r["count_below_frames"], r["count_blip_frames"]))
        print("          %s  (ABOVE means the model ADDED one of the object -- "
              "the axis motion does not protect. BELOW means the object left "
              "the colour band and is a statement about the instrument, never "
              "a flag.)"
              % ("FLAG -- go and look" if r["count_flagged"] else "ok"))
    print("  ncc %.5f .. %.5f" % (r["min_ncc"], r["max_ncc"]))
    print("  %s" % r["reading"])
    print("  THE METRIC IS A FILTER, NEVER A VERDICT -- open the frames "
          "(pipeline/coldread_frames.py) before calling it.")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    geometry = cls = None
    for flag in ("--geometry", "--class"):
        if flag in argv:
            i = argv.index(flag)
            val = argv[i + 1]
            del argv[i:i + 2]
            if flag == "--geometry":
                geometry = val
            else:
                cls = val
    clips = [a for a in argv if not a.startswith("--")]
    if not clips:
        print(__doc__)
        return 2
    rows = []
    for c in clips:
        try:
            rows.append(judge(c, geometry, cls))
        except Exception as e:  # noqa: BLE001
            rows.append({"clip": c, "error": "%s: %s" % (type(e).__name__, e)})
    if as_json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print_report(r)
    return 1 if any("error" in r for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
