#!/usr/bin/env python3
r"""node 001 beat 06 — ROUND 8. His approved arm drawn wider, his other arm's leak shut.

2026-08-10, after r7. This file is a WRAPPER over `render_b06r7.py` and it owns
no render code of its own on purpose: r7's nine traps are what stopped three
rounds of silent defects, and a second copy of the sampler is a second thing to
keep in step. Everything here is done by naming a seed list and editing r7's own
`ARMS` dict before its `main()` runs.

WHAT r7 CAME BACK WITH (read off the frames, not off a metric):

    ARM B (no ground, SKY)      clean 4 of 4 — no ground, no horizon, no city,
                                no bird, no aircraft, no people
    ARM A (ground, TALL GRASS)  2 of 4 contaminated — flat ground and a city
                                skyline still arriving

Those are two different situations and this round treats them differently,
which is the whole design of the file.

ARM B IS PROVEN AND IS SCALED, NOT CHANGED. `--variant skyseeds` renders arm B
byte-for-byte as r7 sent it — same positive, same negative, same steps, cfg and
size — at seeds the beat has never drawn. Nothing about the recipe moves, so
this is depth on an approved result rather than a new one: the founder named
this composition himself, r7 delivered it clean, and what he does not yet have
is a SET to pick from. Seeds continue this beat's own arithmetic (20260725 +
k*1000) at k=8 and up, so no frame here can collide with r3/r4/r5/r6/r7's k=4..7
and any new frame still sets beside the old ones column for column.

ARM A IS A PROMPT PROBLEM AND GETS ONE SAMPLE PER FORMULATION. Reseeding arm A
would be drawing the same prompt again and hoping; the leak is in what the model
is being told. Two formulations, each a single 4-seed sample at r5's held seeds
so each is comparable to r7a column for column, and each ONE variable from the
last:

    a-neg    r7a plus `horizon, field` in the negative. Arm B already negates
             `horizon, field, ground` and arm B is the arm with no leak; arm A
             cannot negate `ground` (its ground is the point) but the other two
             cost it nothing. A flat plane meeting the sky IS a horizon, and
             `field` is the tag for the mown-lawn-to-the-distance composition
             that `grass` alone keeps importing.
    a-below  a-neg plus `from below` on the POSITIVE. One variable on top of
             a-neg. `from below` is a real Danbooru tag on this checkpoint's
             vocabulary meaning the camera looks up, and a camera looking up
             through tall grass cannot show a flat plane or a skyline — the
             blades are between the lens and the horizon. This is the founder's
             own reading of arm A ("show the ground as having tall grass")
             stated as a camera rather than as a noun.

BOTH ARM-A VARIANTS ARE UNPROVEN RECIPES AND EACH IS QUEUED EXACTLY ONCE. If one
comes back clean it may then be scaled; that is the founder's call and not this
file's.

THE TRAPS ALL STILL RUN. `require_neg` is extended with every term a variant
buys, so if the 77-token trim eats one the run stops instead of quietly testing
a prompt the model never saw (r7 trap 5). Trap 9's occupancy pre-flight, traps 7
and 8's `no humans` mechanism, trap 1's byte-for-byte fence and trap 2's r5
control are inherited untouched.

NOTHING HERE IS A PICK, A PROMOTION, A PUBLICATION OR A SPEND. The steward
chooses between arm A and arm B nowhere; the founder gave two acceptable
compositions and has chosen neither.

Usage:
    python render_b06r8.py --variant skyseeds --seeds 20268725,20269725 \
        --set r8b-k8 --root <repo> --out <dir>
    python render_b06r8.py --variant a-neg --root <repo> --measure
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The r7 module is the renderer. Its directory is where the box keeps it.
DEFAULT_R7_DIR = r"C:\banyan-farm\b06-r7"

# r5's four, which r3, r4, r6 and r7 also drew. The arm-A variants hold these so
# a formulation change is the only difference from r7a.
HELD_SEEDS = [20264725, 20265725, 20266725, 20267725]

# THE CLOUD LADDER, added after the founder's verdict on 2026-08-10 ~17:40:
# "this one, now im gonna go, bye. but actually, regenerate it. too many clouds.
# you almost got it". He was pointing at an ARM B frame, so the composition
# question is CLOSED — sky, no ground, and this file stops offering him arm A.
# "You almost got it" is the instruction that shapes these steps: the framing,
# the low upward angle and the daylight palette are RIGHT and are not touched.
# The ONLY thing that moves is how much of the frame is cloud.
#
# WHY A LADDER AND NOT ONE GUESS. He is gone and cannot look at a sample, and
# "fewer clouds" has no single setting — it is a dial, and nobody has drawn this
# beat anywhere along it. Rendering sixteen frames of one untested formulation is
# the exact thing the ONE SAMPLE rule forbids. So the axis gets stepped: five
# formulations from "noticeably fewer" to "mostly clear blue with a few small
# clouds", one job each, and when he is back he picks a point on the dial rather
# than re-rejecting another guess.
#
# THE LEVER IS THE POSITIVE, WITH THE NEGATIVE AS BACKUP. `clear sky` is a real
# tag on this checkpoint's Danbooru-captioned vocabulary and it is the term that
# means what he asked for; it goes into the slot `scenery` was deleted from in
# r7, so no other tag moves. `cloud` leaves the positive from step 3 on. The
# negative side (`cloudy sky`, `overcast`, and finally `cloud` itself) is added
# underneath it as reinforcement, and it is worth having because THIS path runs
# at guidance 7.5 — at guidance 1.0 the negative is never evaluated at all and
# every suppression written into it would be decoration.
#
# Each step's own terms are appended to require_pos/require_neg, so r7's trap 5
# and trap 6 assert that the thing the step is FOR actually survived the
# 77-token trim and reached the model.
#
# ---------------------------------------------------------------------------
# WHAT THE FIRST CUT OF THIS LADDER GOT WRONG, 2026-08-10, and what the logs say
#
# Steps 1 and 2 came back as clean upward sky. Steps 3, 4 and 5 came back as a
# machine housing with a red-eyed head in it, a rabbit-demon and a wolf head —
# six frames, not one of them sky. The cause is read off the box logs in
# `C:\banyan-queue\done\ep1-b06-r8c-clear{2,3}*.log` and it is not what it was
# first guessed to be:
#
#   * The NEGATIVE sent at step 2 (clean) and step 3 (a robot) is IDENTICAL,
#     byte for byte. The seeds are identical too — 20264725, 20265725 both times.
#   * Nothing was silently truncated. The sent negative measures 72 tokens on the
#     box's own CLIPTokenizer, under the 77 ceiling. The `84 > 77` line in the log
#     is transformers' once-per-process warning fired by `fit_negative`'s own
#     pre-trim `count(joined)`; the trim then did its job and NAMED everything it
#     shed. Trap 5 reported truthfully: all 20 required negatives were sent.
#   * So the ONLY variable between a clean sky and a robot is `cloud` leaving the
#     POSITIVE.
#
# WHY ONE WORD DID THAT. animagine-xl-3.1 is captioned on Danbooru, where nearly
# every image has a subject. `cloud` was the only tag in this positive naming a
# THING; the rest — `sky`, `blue sky`, `clear sky`, `day`, `sunlight` — are
# atmosphere, and r7 had already deleted `scenery`, the tag that tells this
# vocabulary "this picture has no subject, it is a landscape". Take `cloud` out
# and the subject slot is empty, so the checkpoint fills it from its own prior.
# `no humans` steers that prior away from people — which is exactly why what
# arrived was a mecha, a wolf and a rabbit-demon rather than a girl. Nothing in
# the negative forbids those: `humans` is lifted out by design (traps 7+8) and
# there is no `mecha`, `robot`, `creature` or `monster` term in it.
#
# THE RULE THAT FOLLOWS, and it is enforced below rather than written down and
# hoped for: AN EMPTY SKY HAS TO BE ASKED FOR, NOT PRODUCED BY DELETING THE ONLY
# WORD THAT NAMES THE FRAME. Cloud COVERAGE comes down by describing an open
# bright sky, never by removing the subject.
SUBJECT_ANCHORS = ("cloud", "scenery")
# Deliberately NOT anchors: `sky`, `blue sky`, `clear sky`, `day`, `sunlight`,
# `sunny`. All but `sunny` were present in the step-3 positive that drew a
# machine, so they are disproven as subject anchors by that frame, not by taste.

UNAUTHORED = "unauthored"

CLOUD_LADDER = {
    1: {"pos_add": "clear sky", "drop_pos": (),
        "neg": "cloudy sky",
        "what": "clear sky asked for, `cloud` still in the positive — the "
                "gentlest step, cloud kept but no longer the subject"},
    2: {"pos_add": "clear sky", "drop_pos": (),
        "neg": "cloudy sky, overcast",
        "what": "step 1 plus `overcast` negated — the banked, sky-filling mass "
                "named on the negative side while `cloud` stays in the positive"},
    # RE-AUTHORED after the six bad frames. One variable from step 2, which is
    # proven: `sunny` added to the positive. `cloud` STAYS — it is the anchor —
    # and the negative does not move at all, so this step is step 2 asked to be
    # brighter and more open rather than step 2 with its subject deleted.
    3: {"pos_add": "clear sky, sunny", "drop_pos": (),
        "neg": "cloudy sky, overcast",
        "what": "step 2 plus `sunny` — the open bright-daylight reading of the "
                "same frame, with `cloud` kept as the subject anchor so the "
                "dial moves by describing the sky, not by emptying it"},
    # STEPS 4 AND 5, AUTHORED 2026-08-10 ~20:00 — and the rung they are built on
    # is the corrected step 3, which has now been SEEN. ep1-b06-r8d-step3 came
    # back rc=0 with four files published and reads as genuine sky, so the ONE
    # SAMPLE condition that held these two back is discharged: the last
    # known-good point on the dial is step 3, not step 2, and each of these
    # moves exactly one variable off it.
    #
    # THE LEVER THAT IS NOT AVAILABLE, AND WHY THAT SHAPES BOTH STEPS.
    # The original sketch of this ladder said the negative side would gain
    # "`cloudy sky`, `overcast`, and finally `cloud` itself". That last move is
    # now KNOWN to be the failure and it is not taken here. `cloud` is the only
    # SUBJECT_ANCHOR arm B can hold — `scenery` is in arm B's forbid_pos — and
    # sending `cloud` on both sides at guidance 7.5 cancels the same direction
    # that deleting it cancelled. Trap 10 would not catch it either: trap 10
    # reads the positive TEXT, so a `cloud` that is present but negated away
    # passes the guard and still empties the subject slot. That is precisely the
    # robot-and-wolf-heads failure with a green trap on top of it. So the bare
    # word `cloud` never enters the negative on this ladder, at any step.
    #
    # WHAT IS LEFT, THEREFORE, IS NARROW, AND THESE TWO STEPS SPEND IT HONESTLY.
    # Step 3's positive already carries `clear sky, sunny, sky, blue sky, day,
    # sunlight`; the open-daylight axis is close to saturated. Each remaining
    # rung is a smaller push than the one below it, and that is expected — the
    # job specs say so out loud. A step that changes nothing visible is not a
    # failed render, it LOCATES THE BOTTOM OF THE DIAL, which is a real answer
    # to "how few clouds can this composition go" and one the founder currently
    # does not have.
    4: {"pos_add": "clear sky, sunny, sun", "drop_pos": (),
        "neg": "cloudy sky, overcast",
        "what": "step 3 plus `sun` — one variable, on the POSITIVE, and it "
                "strengthens the subject slot rather than draining it: `sun` "
                "is a real tag on this vocabulary naming a THING in the frame, "
                "and a sky with a visible sun in it is a sky with room around "
                "the cloud. The negative does not move"},
    # Step 5 is the only rung that touches the negative, and it names the CLOUD
    # FORMS that carry mass — `storm cloud` — rather than the word `cloud`. The
    # anchor survives untouched in the positive and the suppression lands on the
    # banked, frame-filling shapes he objected to.
    #
    # THE HARD CONSTRAINT ON THIS STEP, inherited from the step-3 spec and not
    # negotiable: step 3 measured negative 74 recipe -> 72 sent with all 20
    # required negatives surviving, so there are about five tokens of headroom
    # and the protective block (animal, bird, aircraft, and the whole urban and
    # ground set) has to be inside them. If `storm cloud` cannot fit alongside
    # those, the protective terms WIN and this step does not ship — losing them
    # is what produced the wolf heads. Trap 5 enforces that rather than trusting
    # it: the run stops instead of quietly testing a prompt the model never saw.
    5: {"pos_add": "clear sky, sunny, sun", "drop_pos": (),
        "neg": "cloudy sky, overcast, storm cloud",
        "what": "step 4 plus `storm cloud` negated — the bottom of the dial. "
                "The mass-carrying cloud FORM is named on the negative side "
                "while the bare anchor `cloud` stays only in the positive, "
                "which is the furthest this composition can be pushed without "
                "re-opening the empty-subject failure"},
}

VARIANTS = {
    "skyseeds": {
        "arm": "B",
        "default_set": "r8b",
        "what": "arm B exactly as r7 sent it, at seeds this beat has not drawn",
    },
    "b-clear": {
        "arm": "B",
        "default_set": "r8c",
        "ladder": True,
        "what": "arm B with the cloud dial turned down one named step",
    },
    "a-neg": {
        "arm": "A",
        "default_set": "r8a1",
        "extra_neg": "horizon, field",
        "require_neg": ("horizon", "field"),
        "what": "arm A plus `horizon, field` in the negative",
    },
    "a-below": {
        "arm": "A",
        "default_set": "r8a2",
        "extra_neg": "horizon, field",
        "require_neg": ("horizon", "field"),
        "pos_sub_new": "tall grass, grass, from below",
        "require_pos": ("from below",),
        "what": "a-neg plus `from below` on the positive",
    },
}


def parse_seeds(text: str) -> list:
    seeds = [int(p.strip()) for p in text.split(",") if p.strip()]
    if not seeds:
        raise SystemExit("!! --seeds parsed to nothing")
    if len(set(seeds)) != len(seeds):
        raise SystemExit("!! --seeds repeats a value; a repeat draws the same "
                         "frame twice under two names")
    return seeds


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--variant", required=True, choices=sorted(VARIANTS))
    ap.add_argument("--seeds", default=None,
                    help="comma-separated ints. skyseeds requires them; the "
                         "arm-A variants hold r5's four and refuse them")
    ap.add_argument("--set", dest="set_tag", default=None,
                    help="filename tag, default the variant's own (r8b/r8a1/r8a2)")
    ap.add_argument("--step", type=int, default=None,
                    help="cloud-ladder step, required by --variant b-clear. "
                         "1-3 are authored; 4 and 5 are empty until the "
                         "corrected step 3 has been looked at")
    ap.add_argument("--r7-dir", default=DEFAULT_R7_DIR,
                    help="directory holding render_b06r7.py")
    known, rest = ap.parse_known_args()
    v = VARIANTS[known.variant]
    if v.get("ladder") and known.step not in CLOUD_LADDER:
        print(f"!! --variant {known.variant} needs --step in "
              f"{sorted(CLOUD_LADDER)}; the step IS the recipe and picking one "
              f"here would be inventing it.", flush=True)
        return 24
    if known.step is not None and not v.get("ladder"):
        print(f"!! --step means nothing to --variant {known.variant}.",
              flush=True)
        return 25
    if v.get("ladder") and CLOUD_LADDER[known.step] == UNAUTHORED:
        print(f"!! cloud-ladder step {known.step} is not authored. Steps 3, 4 "
              f"and 5 as first written drew a machine, a wolf and a "
              f"rabbit-demon instead of sky; step 3 has been re-authored and "
              f"the rungs above it are deliberately empty until that corrected "
              f"sample has been LOOKED AT. Build the next rung on a rung that "
              f"is known to work, not on one nobody has seen.", flush=True)
        return 28

    r7_dir = Path(known.r7_dir)
    if not (r7_dir / "render_b06r7.py").is_file():
        print(f"!! no render_b06r7.py under {r7_dir} — this file renders "
              f"nothing on its own and will not improvise a sampler.",
              flush=True)
        return 20
    sys.path.insert(0, str(r7_dir))
    import render_b06r7 as r7                                        # noqa: E402

    if v.get("ladder"):
        # The cloud ladder REGENERATES a frame he has already looked at, so it
        # must be able to name that frame's seed -- including one of the held
        # four, which the fresh-seed variant refuses on purpose. "You almost got
        # it" is a verdict about a specific picture, and drawing the fix at a
        # different seed would answer a question he did not ask.
        if not known.seeds:
            print("!! --variant b-clear regenerates a frame the founder has "
                  "seen. Name the seed of that frame.", flush=True)
            return 26
        seeds = parse_seeds(known.seeds)
    elif known.variant == "skyseeds":
        if not known.seeds:
            print("!! --variant skyseeds is the FRESH-SEED variant and exists "
                  "only to draw seeds this beat has not drawn. Name them.",
                  flush=True)
            return 21
        seeds = parse_seeds(known.seeds)
        clash = sorted(set(seeds) & set(HELD_SEEDS))
        if clash:
            print(f"!! seeds {clash} are the held four r7 already drew — this "
                  f"variant would overwrite a comparison, not add to it.",
                  flush=True)
            return 22
    else:
        if known.seeds:
            print("!! the arm-A variants hold r5's four seeds on purpose: the "
                  "formulation is the variable and a new seed would confound "
                  "it with the noise. Drop --seeds.", flush=True)
            return 23
        seeds = list(HELD_SEEDS)

    arm_key = v["arm"]
    arm = r7.ARMS[arm_key]
    r7.SEEDS = seeds
    arm["set"] = known.set_tag or v["default_set"]

    if v.get("extra_neg"):
        arm["extra_neg"] = arm["extra_neg"] + ", " + v["extra_neg"]
        arm["require_neg"] = tuple(arm["require_neg"]) + tuple(v["require_neg"])
    if v.get("pos_sub_new"):
        old, _ = arm["pos_sub"]
        arm["pos_sub"] = (old, v["pos_sub_new"])
        arm["require_pos"] = tuple(arm["require_pos"]) + tuple(v["require_pos"])

    if v.get("ladder"):
        step = CLOUD_LADDER[known.step]
        # `clear sky` lands in the slot r7 deleted `scenery` from, so no other
        # tag in the positive moves and the frame he approved stays the frame.
        old, _ = arm["pos_sub"]
        arm["pos_sub"] = (old, step["pos_add"])
        arm["require_pos"] = tuple(arm["require_pos"]) + tuple(
            t.strip() for t in step["pos_add"].split(","))
        arm["extra_neg"] = arm["extra_neg"] + ", " + step["neg"]
        arm["require_neg"] = tuple(arm["require_neg"]) + tuple(
            t.strip() for t in step["neg"].split(","))
        # A step that stops asking for cloud must actually stop asking for it,
        # and trap 6 is what proves the tag left rather than the wrapper
        # believing it did.
        arm["forbid_pos"] = tuple(arm["forbid_pos"]) + tuple(step["drop_pos"])

        # TRAP 10 — THE SUBJECT ANCHOR, and it runs on EVERY ladder step, not
        # only the ones that delete something.
        #
        # r7's nine traps all watch the negative side or check that a tag the
        # step ASKED for arrived. Not one of them asks the opposite question:
        # after this step has had its way with the positive, is there still a
        # word in there naming what the picture is OF? There was no such guard
        # on 2026-08-10, which is why steps 3-5 rendered six frames of robots
        # and wolves with every trap reporting OK — truthfully. Trap 5 in
        # particular was never the guard for this and did not fail: it asserts
        # required NEGATIVES survived the trim, they did, and it said so.
        #
        # This is the guard that was missing. It reads the positive actually
        # about to be sent, tag-wise and never as a substring, and stops the
        # run if the subject slot is empty.
        inner = r7.build

        def build(authored, compress, beat_negative, arm_, _inner=inner,
                  _drop=step["drop_pos"], _stepno=known.step):
            pos, neg, neg_full, dropped, warns, dropped_terms = _inner(
                authored, compress, beat_negative, arm_)
            # tag-wise, never substring: `cloud` must not eat `cloudy sky`
            # if a later step ever puts one in the positive.
            parts = [p.strip() for p in pos.split(",")]
            if _drop:
                kept = [p for p in parts if p.lower() not in
                        {d.lower() for d in _drop}]
                if len(kept) == len(parts):
                    print(f"   !! step asked to drop {_drop} from the positive "
                          f"and none of them were there — the recipe moved "
                          f"under this ladder; stopping.", flush=True)
                    raise SystemExit(27)
                parts = kept
            anchors = [p for p in parts
                       if p.lower() in {a.lower() for a in SUBJECT_ANCHORS}]
            if not anchors:
                print(f"   !! NO SUBJECT ANCHOR — cloud-ladder step {_stepno} "
                      f"would send a positive that names no thing in the "
                      f"frame, only atmosphere: {', '.join(parts)}\n"
                      f"      one of {', '.join(SUBJECT_ANCHORS)} has to "
                      f"survive. On 2026-08-10 this exact prompt shape drew a "
                      f"machine housing, a wolf and a rabbit-demon: this "
                      f"checkpoint fills an empty subject slot from its own "
                      f"prior, and `no humans` only steers that prior away "
                      f"from people. Reduce cloud COVERAGE by describing an "
                      f"open sky, not by deleting the subject; stopping.",
                      flush=True)
                raise SystemExit(29)
            print(f"   trap 10 OK — positive keeps the subject anchor "
                  f"{', '.join(anchors)}", flush=True)
            return (", ".join(parts), neg, neg_full, dropped, warns,
                    dropped_terms)

        r7.build = build
    arm["why"] = ("ROUND 8, variant `%s` — %s. %s\n\nINHERITED FROM ROUND 7: %s"
                  % (known.variant + (" step %d" % known.step
                                      if v.get("ladder") else ""),
                     v["what"] + (" — " + CLOUD_LADDER[known.step]["what"]
                                  if v.get("ladder") else ""),
                     "THE FOUNDER PICKED THIS COMPOSITION AND NAMED ONE FIX: "
                     "\"regenerate it. too many clouds. you almost got it\" "
                     "(2026-08-10). The framing, the low upward angle and the "
                     "daylight palette are his and are untouched; the seed is "
                     "the seed of the frame he was looking at, so this is that "
                     "picture with less cloud in it and nothing else. The step "
                     "is one point on a dial nobody has drawn this beat along, "
                     "and the steward picks no point on it. "
                     if v.get("ladder") else
                     "Arm B came back clean 4 of 4 in r7 and is scaled here "
                     "without one token changing, because what the founder "
                     "lacks on this composition is a set to choose from. "
                     if arm_key == "B" else
                     "Arm A came back 2 of 4 contaminated in r7 with flat "
                     "ground and a skyline, so the prompt moves and the seeds "
                     "do not: reseeding a leaking prompt is drawing it again "
                     "and hoping. One sample of this formulation, at r5's held "
                     "four, comparable to r7a column for column. ",
                     arm["why"]))

    sys.argv = [sys.argv[0]] + rest + ["--arm", arm_key]
    print(f"== round 8, variant {known.variant} (arm {arm_key}, set "
          f"{arm['set']}) — {v['what']}", flush=True)
    print(f"   seeds: {', '.join(str(s) for s in seeds)}", flush=True)
    return r7.main()


if __name__ == "__main__":
    sys.exit(main())
