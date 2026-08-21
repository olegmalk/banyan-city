#!/usr/bin/env python3
r"""THE MOTION TRANCHE FOR THE GOBLIN PATCH WAVE. Seven beats, two seeds each.

    python3 pipeline/derive_jerry_motion_0821.py

WHAT THIS CONSUMES. `pipeline/derive_jerry_wave_0821.py` rendered eleven plates
across two rounds at the k6a standard (`pipeline/jerry_standard_0821.py`, the
2026-08-21 steward ruling) and all seven beats came out of it with a plate that
reads as the B tile's creature rather than as an adult man, a child or an old
man. Those seven picks are the `PICKS` table below, each pinned by sha256 --
which is not ceremony: `cover_crop.py` asserts the digest before it writes an
init frame, so a re-rendered or edited plate stops the job instead of quietly
animating a different character.

WHY TWO SEEDS AND NOT ONE. The stills question is answered -- the recipe is
settled and every beat has a picked frame. What is NOT answered is whether LTX
holds that face for 121 frames, and i2v identity drift is a per-seed lottery in a
way a still is not. Two seeds per beat is the smallest batch that can tell a
drifting recipe from a bad draw, and it is also the sustained card load the
stills could not give: ~7 min a job against ~1 min for a plate.

WHY THE PROMPTS LOOK LIKE THIS. Inherited wholesale from
`ep2-b16-motion-0820`, which is the only motion spec in this tree that shipped a
goblin into the cut on its first sample (7/7 on its bar, 01:05 on 08-21). Its
shape is: 2D anime and locked framing first, `Subject already in frame:` and a
description that matches the init, THE ONE THING THAT MOVES in capitals, then a
HALFWAY THROUGH clause. The negative is its negative plus `purple cowl`, because
three of our folded plates showed magenta at the neck.

WHAT THIS DOES NOT DO. It does not touch `review/ep2-ship-0821`. A motion take
here becomes a candidate; swapping one into the cut is a separate judgement with
its own bar, and the audit that named this wave says in as many words that every
re-render it names is a post-ship patch.

$0 to emit. No model, no network, no GPU.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b16-motion-0820.yaml"
PARENT_ID = "ep2-b16-motion-0820"

# The plates live on the box already, in the courier's own farm-out, because the
# runner published them there. Same root ep2-b16-motion-0820 read its source
# from, so the crop step needs no fetch.
BOX_OUT = r"C:\banyan-farm\courier-box\farm-out"

SEEDS = [20260821, 20260822]

# beat: (round picked, plate path in repo, sha256)
#
# REPOINTED 2026-08-21 TO THE AGE-B ROUND-TWO PLATES. The `tilefix` plates these
# used to name are the ADULT goblin with the mannequin face, and every one of
# them is superseded by a founder ruling: the age is Option B (his pick off the
# ladder), the faces carry each beat's own emotion (his "lifeless" correction),
# the blank slit eye is back (his ratified tile), and the broken tusk is in the
# prompt at last (his "what happened to the original design"). The old table is
# not deleted from history -- the tilefix plates rendered, were judged, and are
# the evidence the FRAMING half of this problem was solved before the face was.
PICKS = {
    "02": ("r2", "ep2-b02-ageb-r2-0821",
           "0240e8986947d77fcf238743984f5fc98395ce462b3e94f8413120533467d757"),
    "03": ("r2", "ep2-b03-ageb-r2-0821",
           "b342803b06b8a102be37d9d802064513a2fe93445a4e0e19e696f98c1d25fcbb"),
    "04": ("r2", "ep2-b04-ageb-r2-0821",
           "eaa1e79adf1bcf7ee09683bfc8fad73e4286aff9f00f846ae65758b09076b937"),
    "07": ("r2", "ep2-b07-ageb-r2-0821",
           "02a41be4ebf4d34e85cb283f2794858b68120e53102ba8f82ddf767f83305f15"),
    "08": ("r2", "ep2-b08-ageb-r2-0821",
           "a6f696b67588b417760a5001751cee4f1503f5c9657229ea4e22a786e3663667"),
    "13": ("r2", "ep2-b13-ageb-r2-0821",
           "30a79995bf4682698386f713bd95ac0eba584c1491cb58b4e08b1c09e9541d93"),
    "20": ("r2", "ep2-b20-ageb-r2-0821",
           "73bccac699ec666985c830dc3322ca2bc877dbc3e985b7c6572c7e38865fdd32"),
}

SLUG = {"02": "the-sprint", "03": "bad-cover", "04": "the-footnote",
        "07": "confiscate", "08": "inside-him", "13": "the-shade",
        "20": "evidence"}

WHY_PICKED = {
    "02": "age-B round two. Blank slit eyes, mouth wide open on `scared, open "
          "mouth` -- the alarm is on the face, not just in the stride.",
    "03": "age-B round two. Sweatdrop on the brow, frown, gaze off to the "
          "side. Furtive, which is the beat. CARRIES THE C1 COLLAR FAULT.",
    "04": "age-B round two. `parted lips, looking to the side` -- the peek is "
          "in the face now, and the lean is still handed to the motion prompt "
          "below rather than re-asked of the plate.",
    "07": "age-B round two. Bald, blank-eyed, sweatdrop and a heavy frown. "
          "Apprehension without panic, which is the read this beat wants.",
    "08": "age-B round two. `blush, frown` lands a full orange blush -- caught "
          "out, with the cloak still covering the belly that made round one of "
          "the adult wave read as a chubby child.",
    "13": "age-B round two, AND IT IS THE FRAME OF THE DAY. `closed eyes, "
          "smile, parted lips` gives a real smile with the tusks showing. Four "
          "earlier samples on this beat could not produce warmth and an "
          "expressive-reference build was started to chase it; two stronger "
          "tags did it instead. CARRIES THE C1 COLLAR FAULT.",
    "20": "age-B round two. Open mouth, blank eyes, red fruit in both hands. "
          "CARRIES THE C1 COLLAR FAULT.",
}

# The subject clause must describe THE PLATE THE MOTION STARTS FROM, or the
# video model drifts the face back toward its own prior over the clip. Two words
# are added for the age pivot -- `young` and the broken tusk -- because both are
# now in every init frame and neither was in the adult plates this text was
# written for. `blank white eyes` was already correct and is why round two put
# `blank eyes` back in the plates: the motion prompt had been asking for an eye
# the plates had stopped drawing.
HEAD = ("2D anime, hand-drawn cel animation, static locked framing, the frame "
        "never moves, flat cel shading, clean ink linework, anime key art. "
        "Subject already in frame: ONE lean young green goblin alone, bald "
        "head, blank white eyes, one broken tusk, patchwork cloak, ")

# beat: (what is already in frame, THE ONE THING THAT MOVES, halfway clause)
ACTION = {
    "02": ("mid-stride in tall grass on open ground, leaning forward, seen full "
           "body at a distance.",
           "HE IS RUNNING AND THEN HE GOES DOWN: he drives forward two more "
           "strides, plants a foot, and skids low into the grass with his "
           "weight dropping, arms coming forward to break the fall, the grass "
           "flattening and springing where he passes.",
           "HALFWAY THROUGH he is low and still moving forward, one arm out, "
           "the grass bent around him."),
    "03": ("squatting low behind a thin upright trunk in tall grass, hands on "
           "his knees, seen full body.",
           "HE IS TRYING TO HIDE AND FAILING: he shifts his weight from one "
           "side to the other trying to fit behind the thin trunk, pulls his "
           "shoulders in, glances to one side and then the other, and settles "
           "back exactly as exposed as he began.",
           "HALFWAY THROUGH he is leaning to one side, shoulders drawn in, "
           "still plainly visible past the trunk."),
    "04": ("standing in tall grass, arms at his sides, seen full body, the "
           "grass blades crossing in front of him.",
           "HE PEEKS AND PULLS BACK, ON A LOOP: he leans his head and one "
           "shoulder out sideways past the grass to look, holds it a moment, "
           "then pulls straight back in behind the blades the same way he "
           "came, and leans out again -- the same trip repeating, and STILL "
           "GOING when the shot ends.",
           "HALFWAY THROUGH he is leaned out to one side, head clear of the "
           "grass, looking."),
    "07": ("standing in tall grass, arms at his sides, seen full body.",
           "HE IS BEING TOLD SOMETHING AND HE DOES NOT LIKE IT: his head turns "
           "a little toward the sound, his shoulders drop, and his hands close "
           "at his sides. He stays where he is.",
           "HALFWAY THROUGH his head is turned, shoulders low, hands closed."),
    "08": ("standing in tall grass, head slightly bowed, arms at his sides, "
           "seen full body.",
           "HE LOOKS DOWN AT HIMSELF: his chin comes down, his head tips "
           "forward to look at his own middle, his shoulders round, and he "
           "holds the look.",
           "HALFWAY THROUGH his chin is down and he is looking at his own "
           "middle."),
    "13": ("sitting on the grass, small and folded, hands clasped between his "
           "knees, head low, seen full body.",
           "HE SETTLES AND SPEAKS ONCE: his shoulders drop as he lets a breath "
           "out, his head lifts a little, his mouth opens and closes on a "
           "short line, and his head lowers again. The daylight slides slowly "
           "across the grass.",
           "HALFWAY THROUGH his head is up and his mouth is open on the line."),
    "20": ("squatting low in tall grass, holding a small round red fruit in "
           "both hands in front of him, seen full body.",
           "HE LOOKS FROM THE FRUIT UP AND ACROSS: his eyes and head come up "
           "off the fruit and turn to look level and to one side, he holds "
           "that look, and his hands stay closed around the fruit the whole "
           "time.",
           "HALFWAY THROUGH his head is up and turned to the side, the fruit "
           "still in both hands."),
}

# b16's negative, plus the three terms this wave's own plates earned.
NEG = (
    "second face, second goblin, two goblins, 2boys, crowd, child, chibi, baby, "
    "girl, round head, big eyes, cute, different face, changing face, face "
    "changing, morphing, melting face, skin colour change, human skin, pale "
    "skin, human face, human nose, wrinkled skin, old man, hair, wig, beard, "
    "glasses, purple cowl, purple scarf, bare belly, exposed stomach, "
    "flickering light, strobe, strobing, pulsing light, flashing light, "
    "blinking glow, camera pan, camera tilt, panning, tilting, camera movement, "
    "dolly, zoom, push in, pull back, tripod, camera, camera equipment, film "
    "equipment, walking out of frame, leaving the frame, scene change, shot "
    "change, new camera angle, different location, photorealistic, 3D render, "
    "CGI, live action, motion blur, text")

BAR = """SCORED AS A CANDIDATE FOR A POST-SHIP SWAP, not as a shipped clip.
  M1 IDENTITY HELD FOR 121 FRAMES. The face at f000, f060 and f120 is the same
     creature: blank white eyes with no iris or pupil, no human nose, bald,
     green. A frame where he acquires a pupil or a nose bridge FAILS, and it
     fails even if only one third of the clip does it -- the still already
     passed, so the only thing this job can add is drift.
  M2 THE ACTION IS THE ONE ASKED FOR, and it is legible without the caption.
  M3 THE FRAME NEVER MOVES. Locked camera. Any pan, tilt, push or drift FAILS.
  M4 NO SECOND FIGURE and no purple cowl arriving in motion.
  M5 NO FREEZE. A clip whose subject is static for its whole length is a still
     with a runtime, and this tree has shipped that mistake before.
Two seeds a beat: if BOTH fail the same way it is the recipe, if ONE fails it is
the draw and the other is the candidate."""

PREDICTED = """M1 IS THE ONE I EXPECT TO COST BEATS, and the reason is specific
rather than nervous: every plate here was drawn by an IP-Adapter holding a face
that the base checkpoint does not otherwise produce -- thirteen ladder rungs
established that the wording alone returns a human male. LTX has no adapter. It
is being handed the face as PIXELS in the init frame and asked to keep it for 121
frames against its own prior, and its own prior is the man-read. So drift, if it
comes, will be TOWARD A HUMAN FACE and will show up late in the clip.

IF THAT FIRES ON MOST BEATS, the finding is large and it is not a motion finding:
it says the LoRA is the only durable fix, because a LoRA moves the prior itself
where an init frame only argues with it. That would raise train-jerry-0820 from
enabler work for ep3 to the blocker for ep2's patch wave, and it is filed BEHIND
this tranche on purpose so the tranche's answer arrives first.

BEAT 04 IS THE OTHER RISK AND IT IS M2. The plate does not lean -- two rounds
failed to make it -- so the peek is being asked of the motion model alone, from a
standing init. If LTX will not produce a repeating lean-and-return from that, the
answer is a two-plate approach and not a third wording."""


def main():
    written = []
    for beat, (rnd, plate_job, sha) in sorted(PICKS.items()):
        already, moves, halfway = ACTION[beat]
        prompt = "%s%s %s %s" % (HEAD, already, moves, halfway)
        for i, seed in enumerate(SEEDS, 1):
            new_id = "ep2-b%s-tilemotion-s%d-0821" % (beat, i)
            job_dir = new_id
            src = "%s\\%s\\%s-ipahead.png" % (BOX_OUT, plate_job, plate_job)
            out_mp4 = (r"C:\banyan-farm\%s\%s-%s-LTX-%s.mp4"
                       % (job_dir, beat, SLUG[beat], new_id))
            child = derive_spec.derive(
                src=PARENT,
                new_id=new_id,
                fresh={
                    "owner": "goblin standard lane, 2026-08-21",
                    "why": ("MOTION for beat %s off the patch wave's picked "
                            "plate (%s, round %s).\n\nWHY THIS PLATE: %s\n\n"
                            "The seven plates are the first frames in this "
                            "tree where the goblin reads as the B tile's "
                            "CREATURE at these beats rather than as an adult "
                            "man, a child or an old man -- the defect the "
                            "08-20 audit found in five of seven and the "
                            "founder ruled on directly at beat 13. The stills "
                            "question is closed; this asks the only question "
                            "left, which is whether the face survives 121 "
                            "frames of LTX."
                            % (beat, plate_job, rnd, WHY_PICKED[beat])),
                    "consumer": ("A CANDIDATE for beat %s's post-ship patch. "
                                 "review/ep2-ship-0821 is NOT touched by this "
                                 "job and no clip is swapped by it: a passing "
                                 "take becomes a candidate, and the swap is a "
                                 "separate judgement with its own bar."
                                 % beat),
                    "success": ("ONE 704x1280 121-frame 24fps mp4 at seed %d, "
                                "init cover-cropped from %s with its sha256 "
                                "asserted before a frame is written. Scored on "
                                "M1-M5 in `bar`." % (seed, plate_job)),
                },
                overrides={
                    "argv:--src": src,
                    "argv:--sha256": sha,
                    "payload:b%s-motion-prompt.txt" % beat: prompt,
                    "payload:b%s-negative.txt" % beat: NEG,
                    "key:beat": int(beat),
                    "key:priority": 24,
                    "key:est_minutes": 8,
                },
                retoken=[(PARENT_ID, new_id),
                         ("b16-", "b%s-" % beat),
                         ("16-why-LTX-", "%s-%s-LTX-" % (beat, SLUG[beat])),
                         ("bench-ep2-b16-peek-s3-0820",
                          "bench-%s" % new_id)],
                extra={
                    "bar": BAR,
                    "failure_predicted_in_advance": PREDICTED,
                    "the_one_variable": (
                        "the SEED (%d of the two this beat gets). Everything "
                        "else -- init plate, prompt, negative, size, frames, "
                        "fps, guidance, sampler -- is held across the pair, so "
                        "a split between the two seeds is a draw and a matched "
                        "failure is the recipe." % seed),
                    "the_rung_this_is_one_variable_from": (
                        "ep2-b16-motion-0820, the only motion spec in this tree "
                        "that shipped a goblin into the cut on its first "
                        "sample -- 7/7 on its own bar, into review/ep2-ship-0821 "
                        "at 01:05 on 2026-08-21. Its size, frame count, "
                        "guidance, sampler settings and prompt SHAPE are "
                        "inherited unchanged; the init, the action and the "
                        "seed are what move."),
                    "one_sample_rule": (
                        "SATISFIED BY THE SHAPE OF THE BATCH, and worth stating "
                        "because fourteen jobs looks like a scaled recipe. It "
                        "is not: it is SEVEN beats, each an independent "
                        "question with its own init frame and its own action, "
                        "at two seeds. The recipe under them was sampled by "
                        "ep2-b16-motion-0820 and shipped. The plates under them "
                        "were each sampled and judged by eye at 1:1 before any "
                        "motion was filed -- that judgement is what picked "
                        "round two for beats 04, 08 and 20."),
                    "plate_provenance": (
                        "farm-out/%s/%s-ipahead.png, sha256 %s, drawn at the "
                        "k6a goblin standard (pipeline/jerry_standard_0821.py, "
                        "steward ruling 2026-08-21). cover_crop.py asserts that "
                        "digest before it writes an init frame, so an edited or "
                        "re-rendered plate stops this job rather than quietly "
                        "animating a different character."
                        % (plate_job, plate_job, sha)),
                    "post_ship_patch": (
                        "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB."),
                },
                by="pipeline/derive_jerry_motion_0821.py",
            )
            # The render job list carries the seed and the output name; both are
            # inside a JSON blob, so they are set here rather than by override.
            key = [k for k in child["payload"]
                   if k.endswith("jobs-render.json")][0]
            blob = child["payload"][key]
            import json
            rows = json.loads(blob)
            for r in rows:
                r["seed"] = seed
                r["beat"] = int(beat)
                r["out"] = out_mp4
            child["payload"][key] = json.dumps(rows)
            ekey = [k for k in child["payload"]
                    if k.endswith("jobs-encode.json")][0]
            erows = json.loads(child["payload"][ekey])
            for r in erows:
                r["beat"] = int(beat)
            child["payload"][ekey] = json.dumps(erows)
            child["artifacts"] = [out_mp4]

            argv = [t for s in child["steps"] for t in s.get("argv", [])]
            assert argv[argv.index("--sha256") + 1] == sha, new_id
            assert argv[argv.index("--src") + 1] == src, new_id
            # The parent id is NAMED ON PURPOSE in `the_rung_this_is_one_
            # variable_from`, which is provenance and must survive. What must
            # NOT survive is a PATH or a payload key still pointing at the
            # parent's job directory on the card.
            assert PARENT_ID not in repr(child["steps"]), new_id
            assert PARENT_ID not in repr(list(child["payload"])), new_id

            out = "pipeline/jobs/%s.yaml" % new_id
            derive_spec.write(child, out)
            written.append(out)
            print("wrote %s  seed=%d  init=%s" % (out, seed, plate_job))
    print("\n%d spec(s). Next: box_enqueue each one --backlog, THEN "
          "train-jerry-0820 behind them." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
