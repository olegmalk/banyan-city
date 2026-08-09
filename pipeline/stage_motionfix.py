#!/usr/bin/env python3
"""Stage a v34 MOTION-FIX beat for LTX i2v on the box. Mac-side, draws nothing.

WHAT THIS IS FOR. QA-v34-0810.md measured seven of episode 1's fifteen beats at
median mean-|delta| 0.01-0.05 with 57-88% of frame pairs frozen, against 1.30
for the cut the founder picked. Those seven are `hold_still.py` outputs — a
still with a 12% push-in, which at 3.4%/s is under the encoder's noise floor —
so the measurement is honest and the fix is to actually animate them.

**IT IS THREE BEATS, NOT SEVEN, AND THAT IS THE POINT OF THIS DOCSTRING.**
Four of the seven are deliberately still and animating them would break the
script:

  * beats 04, 06 and 08 are named in motion.yaml's own header as untouched —
    "the limp hand after the fall", "everything nearly still" under the too-blue
    sky, and "the trembling stops. a beat of stillness." The founder's note is
    quoted there too: "no static at all forces it to move even when not needed,
    creating shaking".
  * beat 07's direction IS stillness, in its own words: "nothing moves at all,
    the leaf hangs completely motionless in dead calm air ... camera locked".

So the runnable set is **03, 10, 14**. A wave that "fixes the seven dead beats"
would spend four renders making the cut worse in the exact way he has already
rejected once.

BEAT 10 IS STAGED LAST ON PURPOSE. Its plate is `10-sense.png`, and beat 10 has
no approved frame — r4 was rejected and this lane has just put r5 candidates on
disk. Animating a plate that is about to be replaced spends the card twice.

PROMPTS ARE COMPOSED, NEVER RETYPED. `video_task.video_prompt` on the beat's own
action line and motion direction, the same call farm_worker makes
(video_task.py:1341), so the string the model gets is the one the pipeline would
have sent. The b12 lane's rule applies: written as utf-8 files because the
negatives carry CJK anti-static terms that a cp1252 console turns into a clip
that looks fine and was asked something else.

PLATES ARE CROPPED BY plate_prep, NOT RESIZED, cover-centre — render_t3's own
policy — and the sha of the fitted plate is printed so the box copy can be
verified byte-for-byte before a step.

Usage:
    python3 pipeline/stage_motionfix.py 3 --out /tmp/motionfix-b03
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NODE = REPO / "genomes/sapling/nodes/001-capability-inventory"
BOXDIR = "C:\\banyan-farm\\motionfix-0810"
SIZE = "704x1280"

# beats whose direction is stillness BY DESIGN. Staging one of these is a bug,
# not a choice, so the script refuses rather than warns.
DELIBERATELY_STILL = {
    4: "motion.yaml header — the limp hand after the fall",
    6: "motion.yaml header — everything nearly still under the too-blue sky",
    7: "its own direction — `nothing moves at all ... camera locked`",
    8: "motion.yaml header — the trembling stops, a beat of stillness",
}

# the still each v34 clip is held on, read off the clip sidecars' source_still.
PLATES = {3: "03-deploy-succeeded.png",
          10: "10-sense.png",
          14: "14-worth-staying-in.png"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("beat", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260810)
    a = ap.parse_args()

    sys.path.insert(0, str(REPO / "pipeline"))
    from generate_shots import parse_shots
    from video_task import motion_directions, beat_actions, video_prompt
    from plate_prep import prepare_plate

    b = a.beat
    if b in DELIBERATELY_STILL:
        print(f"!! beat {b} is DELIBERATELY STILL ({DELIBERATELY_STILL[b]}). "
              f"Animating it would break the script and re-create the defect "
              f"the founder named. Refusing.", flush=True)
        return 4
    if b not in PLATES:
        print(f"!! beat {b} is not one of the motion-fix beats "
              f"{sorted(PLATES)}; refusing.", flush=True)
        return 5

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    motions = motion_directions(NODE)
    acts = beat_actions(NODE / "node.md")
    shots = {s["num"]: s for s in parse_shots((NODE / "shots.md").read_text("utf-8"))}

    motion = motions[b]
    act = acts.get(b, "")
    still_prompt = shots[b]["prompt"]
    pos, neg = video_prompt(f"{act}. {motion}" if act else motion,
                            still_prompt, beat=b)

    still = NODE / "stills" / PLATES[b]
    if not still.exists():
        print(f"!! plate missing: {still}; refusing.", flush=True)
        return 6
    plate, info = prepare_plate(still, SIZE, out, tag=f"b{b:02d}")

    pf = out / f"{b:02d}-prompt.txt"
    nf = out / f"{b:02d}-negative.txt"
    pf.write_text(pos, encoding="utf-8")
    nf.write_text(neg, encoding="utf-8")

    def box(p):
        return f"{BOXDIR}\\{Path(p).name}"

    enc = [{"beat": b, "embeds": box(f"{b:02d}-embeds.pt"),
            "prompt_file": box(pf), "negative_file": box(nf)}]
    ren = [{"beat": b, "embeds": box(f"{b:02d}-embeds.pt"),
            "prompt_file": box(pf), "negative_file": box(nf),
            "init": box(plate),
            "out": box(f"ltx-001-b{b:02d}-motionfix.mp4"),
            "seed": a.seed}]
    (out / f"jobs-b{b:02d}-encode.json").write_text(json.dumps(enc, indent=2))
    (out / f"jobs-b{b:02d}-render.json").write_text(json.dumps(ren, indent=2))

    print(f"== beat {b} staged into {out}")
    print(f"   action:   {act!r}")
    print(f"   motion:   {motion!r}")
    print(f"   POSITIVE ({len(pos.encode())}B): {pos}")
    print(f"   NEGATIVE ({len(neg.encode())}B): {neg}")
    print(f"   plate:    {Path(plate).name}  {info.get('crop_note', '')}")
    print(f"   plate sha256: {hashlib.sha256(Path(plate).read_bytes()).hexdigest()}")
    print(f"   source:   {still}")
    print(f"   src sha256:   {hashlib.sha256(still.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
