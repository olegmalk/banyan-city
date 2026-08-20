#!/usr/bin/env python3
r"""BEAT 16: ONE motion sample. The beat's first footage candidate, ever.

WHAT LANDED FIRST. `ep2-b16-sapcomp-r2-0820` is beat 16's first plate that is
actually the shot: the canon two-leaf sapling large in the near foreground, the
scavenger seated behind it, in the episode's flat cel dialect. All six plate
clauses passed — two leaves on one stem, average ovate shape, one plant in
frame (the b15 plate's own weed erased first), him unchanged, and the 0.30 pass
DREW the blades rather than leaving them flat (detail on the drawn plant 5.751
-> 5.836, movement 16.0 mean |delta| per pixel, against the big-leaf attempt's
10.45 -> 9.41). This is step 3: i2v off that plate.

THE ACTION, AND IT IS THE INVERSE OF EVERY OTHER BEAT THIS WEEK. Beat 16's VO is
the SAPLING'S: *"He talks to me because I'm the only thing here that won't file
a report. Buddy, I wish I could. I can't even wave."* So the man BEHIND the plant
is the one who talks — mouth moving, shoulders shifting — and the plant is the
one that holds still. Beats 04 and 09 spent the week asking for a shut mouth on
a still body; this beat wants the opposite of both, on the same engine.

AND THE PLANT'S STILLNESS IS NEVER STATED AS AN ABSENCE. The joke is "I can't
even wave" and the temptation is to write `the leaves do not wave`. THAT IS THE
BEAT-15 TRAP, paid for twice: a negation inside the positive is not a
prohibition, it is the phrase `wave`, placed. `Nobody touches the plant` put a
hand on the plant and `the plant is not picked up` uprooted it. So the leaves are
given something to DO that is not waving — they hang, they hold, the light moves
on them — and the word never appears.

MIDDLE AND END PLACEMENT, ONGOING. Measured 2026-08-20 across b03/b13/b15: a
terminal placement naming an ONGOING action held position at no cost (b15, HOLD
0.508, no freeze) while a STATIC attitude bought the hold by making every frame
the last frame (b03, 33 dead frames). His talking is the ongoing action and it
is placed at the middle and at the end.

WHY ONE SAMPLE. The recipe is `ep2-b04-peek-s3-0820`'s, the crf-10 i2v family
that has now run clean eight times this week on this exact stack. Only the init
and the words change. One sample before any batch, and the init has never been
animated before.

$0, ~7 min. Run:  python3 pipeline/derive_b16_motion_0820.py [--write]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-peek-s3-0820.yaml"
NEW_ID = "ep2-b16-motion-0820"

SRC = (r"C:\banyan-farm\courier-box\farm-out\ep2-b16-sapcomp-r2-0820"
       r"\b16-sapcomp-s20260820.png")
SRC_SHA = "8f4e9ba31c42130c4cc5fef841bb368b005ad7b4667ef9d648360bf9c2aabc71"

PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: a young green sapling with TWO wide oval leaves on one thin stem, "
    "close to the camera and large in the foreground, rooted in a sunny grassy "
    "field, and behind it ONE lean wiry adult goblin man alone, green skin, bald "
    "head, patchwork cloak, sitting on the grass further away, smaller and "
    "softer than the plant. THE MAN BEHIND IS TALKING, ON AND ON: his mouth "
    "opens and closes as he speaks, his jaw works, his head moves a little as he "
    "makes his point and his shoulders shift with it, and he is still going. THE "
    "SAPLING IN FRONT HOLDS ITS PLACE: its two leaves hang where they are on "
    "their stem, steady and heavy, and the daylight slides slowly across them. "
    "HALFWAY THROUGH he is mid-sentence with his mouth open and the two leaves "
    "are hanging exactly where they began. AT THE END he is still talking, "
    "mid-word, and the leaves are still hanging in the same place, the "
    "conversation unfinished and carrying on past the last frame. The plant "
    "stays THE SAME PLANT from the first frame to the last: the same two leaves, "
    "the same one stem. The light is CONSTANT and does not flicker, pulse or "
    "strobe. Soft steady daylight, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic."
)

# b04's negative with the MOUTH BLOCK REMOVED -- this beat's man is speaking --
# and the plant-count words added. Everything else is byte-identical.
NEGATIVE = (
    "second face, second goblin, two goblins, 2boys, crowd, child, chibi, baby, "
    "girl, round head, big eyes, cute, different face, changing face, face "
    "changing, morphing, melting face, skin colour change, human skin, pale "
    "skin, hair, wig, glasses, three leaves, four leaves, many leaves, "
    "leaflets, extra stalk, branching stem, second plant, two plants, flower, "
    "fruit, large tree, flickering light, strobe, strobing, pulsing light, "
    "flashing light, blinking glow, camera pan, camera tilt, panning, tilting, "
    "camera movement, dolly, zoom, push in, pull back, tripod, camera, camera "
    "equipment, film equipment, walking out of frame, leaving the frame, "
    "standing up, scene change, shot change, new camera angle, different "
    "location, photorealistic, 3D render, CGI, live action, motion blur, text"
)

BAR = """JUDGED BY EYE AT 1:1, AND T0 IS READ BEFORE ANY OTHER CLAUSE.
  T0 CAMERA LOCKED -- mean abs luma of the two TOP corner patches against f001,
     under ~3. Bought on beat 04 the hard way: s5 was the best-looking clip in
     its batch, would have been picked by eye, and read 49.4 and 52.2. A clip
     that fails T0 is not scored further.
  M1 THE PLANT HOLDS. Two leaves, one stem, in the same place at f121 as at
     f001. This beat's whole joke is that it cannot wave, so a waving plant is
     not a lively take, it is the wrong shot.
  M2 STILL TWO LEAVES at f121. Canon `sapling-two-leaves`. i2v growing a third
     is the named risk of animating a composited plant and it is the one thing
     no amount of good motion redeems.
  M3 HE IS TALKING. Mouth opening and closing, some head and shoulder movement.
     A frozen man behind a still plant is a photograph, and the beat is a
     conversation.
  M4 STILL GOING AT f121 -- visible movement in the last twenty frames. b03 and
     b13 both bought their hold by killing the clip; the placement here names an
     ongoing action for exactly that reason.
  M5 THE FIGURE SURVIVES -- one man, seated, no melt, no second goblin, no drift
     into the plant.
  M6 THE PLANT IS STILL THE SUBJECT. It is in front and it stays in front; if
     the pass pulls focus to him the shot has inverted.
NOT SCORED: which goblin design he is. The plate carries the superseded adult
and the creature ruling is a separate re-render for a separate day."""

PREDICTED = """M1 IS THE RISK AND IT IS THE OPPOSITE OF THE USUAL ONE. Every
other beat this week fought to get MOTION out of this engine; here the composited
plant is the largest, highest-contrast object in the frame and i2v likes to move
exactly that. If the leaves swing, the beat is lost in the funniest possible way
— an engine waving the plant that says it cannot wave — and the next lever is a
terminal placement of the leaves' position, not a negative.
SECOND, AND SPECIFIC TO A COMPOSITED INIT: M2. The plant is drawn geometry that
survived one 0.30 pass; 121 frames of i2v is a much longer argument with it, and
a third leaf or a branching stem is how it would lose. No i2v run in this tree
has ever animated a composited plant AS THE SUBJECT -- b19, b15, b03 and b13 all
carried theirs as small set dressing -- so this is genuinely unmeasured.
THIRD: M3 AND M1 MAY BE COUPLED. Beat 04 measured that holding the head holds
the eyes on this engine; if holding the plant also holds HIM, this beat needs
its stillness and its performance to come from different places and the honest
next instrument is a composite of two renders rather than one prompt.
NOT PREDICTED, WATCHED ANYWAY: the mouth. b04 and b09 spent the week keeping
mouths SHUT and their negatives are full of `open mouth`, `talking`, `lip sync`.
Those words are deleted here because this man speaks -- if the deletion also
removes something that was holding the face together, that is a finding about
the negative and not about the beat."""


def main() -> int:
    write = "--write" in sys.argv
    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat-16 restage lane, 2026-08-21",
            "consumer": (
                "BEAT 16'S SLATE IN THE EPISODE 2 CUT -- one of the last two "
                "empty slots, and the only beat in the episode with no footage "
                "candidate of any kind. Three wordings, a big-leaf composite "
                "and a four-plate field batch all failed it. Its first real "
                "plate landed tonight (ep2-b16-sapcomp-r2-0820) and this is the "
                "clip made from it. If it holds, beat 16 stops being a slate."),
            "success": (
                "One 704x1280 121-frame mp4 in which THE PLANT HOLDS STILL AND "
                "THE MAN BEHIND IT TALKS. T0 first: camera locked, top-corner "
                "mean abs luma under ~3 against f001. Then M1 two leaves on one "
                "stem in the same place at f121 as at f001 -- this beat's joke "
                "is that it cannot wave, so a waving plant is the wrong shot, "
                "not a lively one; M2 still exactly two leaves, canon "
                "sapling-two-leaves, which a composited plant under 121 frames "
                "of i2v has never been asked to survive before; M3 he is "
                "visibly talking, mouth and shoulders; M4 still moving inside "
                "the last twenty frames; M5 one man, seated, no melt; M6 the "
                "plant is still the subject and still in front."),
            "why": (
                "$0, ~7 minutes, one seed, and it is the last step between beat "
                "16 and a footage candidate it has never had. The recipe is the "
                "crf-10 i2v family that has run clean eight times this week; "
                "only the init and the words change, so a bad result is "
                "attributable to this beat rather than to the recipe. One "
                "sample before any batch -- and this init has never been "
                "animated."),
        },
        overrides={
            "seed": 20260821,
            "argv:--src": SRC,
            "argv:--sha256": SRC_SHA,
            "payload:b16-motion-prompt.txt": PROMPT,
            "payload:b16-negative.txt": NEGATIVE,
            "key:beat": 16,
            "key:est_minutes": 7,
            "key:script_line": (
                'Beat 16 WHY (1:15-1:22), node.md verbatim: "Close on the '
                "sapling's leaf; the scavenger sits blurred behind it.\" "
                "RESTAGED 2026-08-20 to CLOSE ON THE WHOLE CANON SAPLING with "
                "him behind it. The VO is the SAPLING'S and is unchanged -- the "
                "founder's own 2026-08-19 word to keep it: \"He talks to me "
                "because I'm the only thing here that won't file a report. "
                "Buddy, I wish I could. I can't even wave.\" THAT LINE IS WHY "
                "THE PLANT MUST NOT MOVE."),
            "key:script_authority": (
                "Node 002b-first-citizen, live script `002b-t0-c`, "
                "`approved_by: founder`, `approved_on: 2026-08-03`. The line is "
                "untouched; the staging is a stage direction, logged by the "
                "coordinator lane on 2026-08-20 as the option satisfying both "
                "the brief and the founder's own 08-17 canon ruling. His card "
                "/review/ep2-b16-leaf-0820 remains open and unanswered."),
        },
        # THE BEAT SLUG. Without this the clip publishes as
        # `04-the-footnote-LTX-ep2-b16-motion-0820.mp4`: retoken rewrites the
        # parent's ID and leaves the parent's BEAT NAME standing in the
        # filename. box_enqueue's own comments record this exact failure --
        # "a spec cloned from a template that predates the slug" -- and a
        # beat-16 clip filed under beat 04's name is the kind of thing that is
        # only found when someone assembles the cut.
        # EVERY PAIR IS SPECIFIC, AND THAT IS NOT TIDINESS. derive_spec appends
        # its own (parent_id -> new_id) pair LAST, so a caller's rule runs
        # first and can destroy the token that rule depends on. A blanket
        # ("b04-" -> "b16-") did exactly that here: it rewrote the parent id
        # `ep2-b04-peek-s3-0820` into `ep2-b16-peek-s3-0820` before the id rule
        # could see it, and the clip came out as
        # `16-why-LTX-ep2-b16-peek-s3-0820.mp4` -- a beat-16 file named after a
        # beat-04 job that does not exist. Basenames only.
        # `04-the-footnote-LTX` and not the bare slug: the bare form also hit
        # the parent's plate filename inside derive_spec's own provenance
        # record, logging `ep2-b04-mac-plate-0819\16-why-mac-plate-r1s1.png` --
        # a file that has never existed, in the block whose whole job is to say
        # truthfully what changed. The output name is the only place the slug
        # needs to move.
        retoken=[("04-the-footnote-LTX", "16-why-LTX"),
                 ("b04-motion-prompt", "b16-motion-prompt"),
                 ("b04-negative", "b16-negative"),
                 ("b04-jobs-", "b16-jobs-"),
                 ("b04-init-", "b16-init-"),
                 ("b04-embeds", "b16-embeds"),
                 ("bench-ep2-b04", "bench-ep2-b16")],
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "pre_registered_fail_modes": (
                "M-WAVE the leaves swing, which loses the beat in the funniest "
                "available way and is the likeliest outcome, because the "
                "composited plant is the largest high-contrast object in frame "
                "and i2v moves exactly that. M-THIRDLEAF the plant grows a leaf "
                "or a branch across 121 frames; unmeasured, because no i2v run "
                "in this tree has animated a composited plant as the SUBJECT. "
                "M-FROZEN the plant holds and takes the man with it -- beat 04 "
                "measured that holding the head holds the eyes on this engine, "
                "and if stillness is similarly contagious here the beat needs "
                "two renders rather than one prompt. M-MOUTH the deleted mouth "
                "negatives were also holding the face together and it drifts. "
                "M-INVERT the pass pulls focus to him and the plant stops being "
                "the subject."),
            "the_one_variable": (
                "THE INIT AND THE WORDS -- there is no earlier rung on this beat "
                "to hold a variable against, because this is its first animation "
                "of any kind. Every generative flag is the parent's: 704x1280, "
                "121 frames, 24 fps, guidance 2.0, distilled sigmas, two-stage, "
                "--image-crf 10, sequential offload. THE NEGATIVE'S MOUTH BLOCK "
                "IS DELETED and the plant-count words added; both are forced by "
                "the beat -- b04's negative bans `open mouth`, `talking` and "
                "`lip sync` and this man is speaking. Nothing else in it moved."),
            "why_the_word_wave_is_not_in_the_prompt": (
                "The joke is `I can't even wave` and the obvious sentence is "
                "`the leaves do not wave`. THAT IS THE BEAT-15 TRAP AND THIS "
                "TREE HAS PAID FOR IT TWICE: a negation inside the POSITIVE is "
                "not a prohibition, it is the noun phrase, placed. `Nobody "
                "touches the plant` closed a fist on the plant at f105 and the "
                "sapling was uprooted by f120. So the leaves are given "
                "something to do that is not waving -- they hang, they hold, "
                "the daylight slides across them -- and the word never appears "
                "in either file."),
            "init_provenance": (
                "farm-out/ep2-b16-sapcomp-r2-0820/b16-sapcomp-s20260820.png, "
                "sha256 8f4e9ba3...bc71, read off the box's own courier mirror "
                "and asserted by the crop step. It is the output of "
                "ep2-b16-sapcomp-r2-0820: the canon sapling drawn by "
                "pipeline/beat16_sapling_composite.py into "
                "ep2-b15-mac-plate-0819's pre-composite plate (weed erased "
                "first via b19's flood matte and within-class fill) and "
                "finished with one 0.30 pass. Its six plate clauses all passed "
                "by eye; detail on the drawn plant rose 5.751 -> 5.836 and the "
                "pass moved 16.0 per pixel, against the big-leaf attempt's "
                "10.45 -> 9.41."),
            "the_plate_reservation_carried_forward": (
                "S1 PASSED WITH A CAVEAT AND IT IS CARRIED HERE RATHER THAN "
                "DROPPED. The relation is unambiguous -- the plant is in front, "
                "large, and occludes him -- but the eye still goes to his FACE "
                "first, because he is a face and the plant is a shape. The "
                "plate spec pre-registered this and named the lever: a tighter "
                "crop, which beat 09 proved this week survives i2v at 105% of "
                "frame 1's high-frequency energy. That lever is NOT taken here, "
                "because cropping and animating in the same job would leave two "
                "candidate causes for anything that happens."),
            "not_done_on_purpose": (
                "No crop change. No crf, guidance or sigma change. No second "
                "seed. No goblin-design change -- the plate carries the "
                "superseded adult and that is a separate re-render. No cut "
                "swap and no plate_ack: beat 16 stays a slate until the founder "
                "screens something, and his /review/ep2-b16-leaf-0820 card is "
                "still open with `licence` still available to him."),
        },
        by="pipeline/derive_b16_motion_0820.py",
    )
    out = os.path.join(REPO, "pipeline", "jobs", NEW_ID + ".yaml")
    if not write:
        print("-- dry run. re-run with --write.")
        return 0
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(derive_spec._dump(child))
    print("wrote pipeline/jobs/%s.yaml" % NEW_ID)

    # the hash sweep, same law as the sapcomp deriver: a sha256 survives
    # retoken by construction, so any 64-hex token that is not this child's own
    # is a measurement of somebody else's file.
    import re
    for step in child.get("steps") or []:
        for tok in step.get("argv") or []:
            if isinstance(tok, str):
                for h in re.findall(r"\b[0-9a-f]{64}\b", tok):
                    if h != SRC_SHA:
                        print("!! step %r carries sha256 %s..., not this "
                              "child's init" % (step.get("name"), h[:12]))
                        return 1
    print("hash sweep OK")
    # THE WORDING GUARD IS DIRECTION-AWARE, and the first version of it was not
    # -- it refused this spec for the word `talking`, which is in the POSITIVE
    # on purpose because this beat's man speaks. A guard that cannot tell the
    # positive from the negative is checking a bag of words, not a prompt.
    pay = {k.replace("\\", "/").rsplit("/", 1)[-1]: str(v)
           for k, v in (child.get("payload") or {}).items()}
    neg = pay.get("b16-negative.txt", "").lower()
    pos = pay.get("b16-motion-prompt.txt", "").lower()
    for banned in ("open mouth", "talking", "speaking", "lip sync", "teeth"):
        if banned in neg:
            print("!! the NEGATIVE still bans %r. Beat 16's man is the one who "
                  "talks -- b04's mouth block has to come out or the beat "
                  "cannot happen." % banned)
            return 1
    if "mouth opens" not in pos:
        print("!! the POSITIVE does not place his mouth opening. This beat is a "
              "conversation and the mouth is the thing that says so.")
        return 1
    for f, t in (("positive", pos), ("negative", neg)):
        if "wave" in t or "waving" in t:
            print("!! 'wave' appears in the %s. That is the beat-15 trap: a "
                  "negation inside the positive is the noun phrase placed, and "
                  "in the negative it has failed to hold position four times. "
                  "The leaves are given something else to do instead." % f)
            return 1
    print("wording guard OK: the negative bans no mouth, the positive places "
          "one, and 'wave' appears in neither file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
