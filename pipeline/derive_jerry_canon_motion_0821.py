#!/usr/bin/env python3
r"""MOTION SPECS FOR THE CANON WAVE -- written, and DELIBERATELY NOT FILED.

    python3 pipeline/derive_jerry_canon_motion_0821.py --write   # emit the yamls
    python3 pipeline/derive_jerry_canon_motion_0821.py --plan    # print, write nothing

THE GATE, AND IT IS THE FOUNDER'S OWN RULE FROM THIS AFTERNOON. Narrative
approval precedes media, and one level down, a recipe is not scaled before its
result is approved. The canon plates are on his board and he has not answered.
So these seven specs exist on disk, reviewable, with every number in them
measured -- and NOTHING IS ENQUEUED. `--write` writes files; there is no flag
in this module that talks to the box. When he says it reads as his goblin, one
`box_enqueue.py` loop fires them and the tranche is four minutes of GPU.

═══════════════════════════════════════════════════════════════════════════
THE THREE THINGS CARRIED IN FROM THE FALLBACK LANE'S 14-CLIP RECORD

1. THE FACE-LOSS FAULT IS THE MOTION RECIPE'S, NOT THE PLATES'. In 6 of 14
   clips the face stops being drawn partway through 121 frames -- silhouette and
   colour persist, features vanish, and it never recovers. It is a property of
   how far the render is pushed, so it will recur on these plates unless the
   frame count changes, and the frame count is the one thing nobody had moved.

   MEASURED THE SLOTS RATHER THAN ASSUMING 121. ffprobe over the seven clips
   currently in review/ep2-ship-0821:

       beat 02   97 frames   4.042 s        beat 08  121 frames   5.042 s
       beat 03  121 frames   5.042 s        beat 13   97 frames   4.042 s
       beat 04   97 frames   4.042 s        beat 20  121 frames   5.042 s
       beat 07   97 frames   4.042 s

   Four of the seven need 97 and were being rendered at 121 -- 24 frames of
   denoising past what the cut can use, spent entirely inside the window where
   the face dissolves. Those four now render 105 (97 + 8 of trim margin) and
   trim to 97.

   THE THREE 121-FRAME BEATS GET HOLD-FILL INSTEAD OF A LONGER RENDER. They
   also render 105; the last good frame is held to reach 121. Hold-fill is
   already the cut's own technique (see beat 16's meta) and a held frame is
   strictly better than sixteen frames of a face melting. This is a STEWARD
   PICK on a tradeoff, not a founder question, and it is reversible per beat by
   setting `hold_fill: false`.

2. BEAT 07 MUST NAME THE GUARD AS A PLACED SUBJECT. Its motion drew NO guard on
   either seed, so the confiscation -- the whole beat -- was simply absent. That
   is the prompt-summons law: a subject that is not PLACED in the wording is not
   drawn. b07's motion prompt below opens with both figures in frame before it
   says anything about what they do.

3. THE WARDROBE IS SCORED PER BEAT, NOT INHERITED FROM THE PLATE. The b08
   lesson is that garments merge under conditioning load. The founder's costume
   has a waist boundary the patchwork cloak did not, so it has strictly more to
   lose, and W1/W2 are on every clip's bar rather than assumed from the frame
   that seeded it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                            # noqa: E402
import jerry_canon_0821 as C                  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b20-tilemotion-s2-0821.yaml"
PARENT_DIR_TOKEN = "ep2-b20-tilemotion-s2-0821"
NODE = "002b-first-citizen"
OWNER = "canon lane, 2026-08-21"
PY = r"C:\banyan-farm\venv\Scripts\python.exe"
VPY = r"C:\banyan-video\venv\Scripts\python.exe"

RENDER_FRAMES = 105          # every beat. See point 1 of the docstring.
TRIM_MARGIN = 8
FPS = 24

# beat -> (slot_frames measured by ffprobe, action clause, what must be legible)
SLOTS = {
    2:  (97,  "he runs into frame from the left, skids, and drops behind a "
              "thin sapling trunk",
              "entry, skid, dive, in that order, as one continuous move"),
    3:  (121, "he crouches low behind the thin trunk and holds still, eyes "
              "flicking sideways",
              "the cover is comically inadequate and he believes it is working"),
    4:  (97,  "he leans out sideways from behind the trunk, looks, and pulls "
              "straight back",
              "out, look, back -- the pull-back is the joke and must land"),
    7:  (97,  "the guard's arm comes up and points at him; he flinches back a "
              "half step",
              "TWO figures the whole clip, and the point is aimed AT him"),
    8:  (121, "he lowers his head and looks down at his own belly, shoulders "
              "sinking",
              "the look DOWN completes, and it completes early"),
    13: (97,  "he sits, his shoulders drop, and his head tips sideways into "
              "the shade",
              "exhaustion resolving into relief; the head-tip completes"),
    20: (121, "he lifts the fig in both hands and looks up from it to the "
              "branch beside him",
              "the LOOK UP completes -- the outgoing take never did it"),
}

# The plate each motion job is conditioned on. Filled from the canon wave.
PLATE_ROUND = "w2"

MOTION_STYLE = ("2D anime, hand-drawn cel animation, static locked framing, "
                "the frame never moves, flat cel shading, clean ink linework")

# THE IDENTITY CLAUSE FOR MOTION IS NOT THE PLATE'S. A plate prompt SUMMONS a
# character; a motion prompt must say he is ALREADY THERE and must not change,
# or the model re-draws him. `Subject already in frame:` is the parent's own
# wording and it is kept verbatim because it is what worked.
def identity_clause():
    return ("Subject already in frame: ONE small green goblin child alone, "
            "bald, large pointed ears, off-white eyes with narrow vertical "
            "slit pupils, mandarin-collar sage shirt, dark shorts, dark boots. "
            "His face, ears, skin colour and clothes DO NOT CHANGE for the "
            "whole clip.")


NEGATIVE = ("second face, second goblin, two goblins, extra head, "
            "disembodied head, crowd, child, chibi, baby, round head, "
            "different face, changing face, morphing, melting face, "
            "featureless face, blank face, losing facial features, "
            "skin colour change, clothes changing, cloak, hood, patchwork, "
            "camera pan, camera zoom, camera shake, text, watermark")

BAR = """THE CANON MOTION BAR. Read against taste/refs/goblin-canon-founder-0821.png
for the character and against this beat's done_when for the action.

  M1  THE FACE IS DRAWN IN EVERY FRAME OF THE TRIMMED CLIP. This is the fault
      the frame count exists to dodge and it is scored FIRST: step the clip and
      confirm eyes, slit pupils, brow and mouth are present at the LAST frame,
      not only the first. Silhouette and colour persisting while features
      vanish is the exact failure signature -- it is a FAIL, not a soft frame.
  M2  IDENTITY HOLDS. Same face at frame one and the last frame. Ears stay
      large, lateral and pointed; eyes stay off-white with a slit pupil.
  W1  WARDROBE HOLDS AND STAYS SEPARATE -- mandarin collar, shirt, dark shorts,
      dark boots, and THE WAIST BOUNDARY IS STILL THERE. Shirt and shorts
      resolving into one mass is the b08 garment-merge fault and it fails here
      even if the colours are right.
  W2  NO CLOAK, NO HOOD, NO PATCHES appear at any point in the clip.
  A1  THE BEAT'S ACTION COMPLETES INSIDE THE SLOT, and the frame number it
      completes at is RECORDED. An action that completes after the trim point
      did not happen as far as the cut is concerned.
  C1  THE FRAME NEVER MOVES. No pan, no zoom, no drift.
  C2  ONE SUBJECT, except beat 07, which requires TWO for its whole length."""


def frames_for(beat):
    slot, _, _ = SLOTS[beat]
    return RENDER_FRAMES, slot, slot > RENDER_FRAMES


def plan():
    rows = []
    for beat in sorted(SLOTS):
        render, slot, hold = frames_for(beat)
        rows.append({
            "beat": beat,
            "slot_frames": slot,
            "slot_s": round(slot / float(FPS), 3),
            "render_frames": render,
            "trim_to": min(render - TRIM_MARGIN, slot),
            "hold_fill_frames": max(0, slot - render) if hold else 0,
            "plate": "ep2-b%02d-canon-%s-0821" % (beat, PLATE_ROUND),
        })
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    rows = plan()
    if a.plan or not a.write:
        print(json.dumps(rows, indent=2))
        print("\nNOTHING IS ENQUEUED BY THIS MODULE. The plates are on the "
              "founder's board and the tranche waits on his word.")
        return 0
    print("--write is intentionally not wired to the queue; see the docstring.")
    for r in rows:
        print("  beat %02d  render %d -> trim %d  hold-fill %d  plate %s"
              % (r["beat"], r["render_frames"], r["trim_to"],
                 r["hold_fill_frames"], r["plate"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
