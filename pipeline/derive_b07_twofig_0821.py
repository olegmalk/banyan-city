#!/usr/bin/env python3
r"""BEAT 07's TWO-FIGURE CANON PLATE: one sample, the goblin and the guard.

    python3 pipeline/derive_b07_twofig_0821.py            # dry run
    python3 pipeline/derive_b07_twofig_0821.py --write

WHY, AND THE EVIDENCE IS THE BEAT'S OWN MOTION VERDICT
--------------------------------------------------------------------------
The canon-motion wave filed seven i2v jobs on 2026-08-21. Beat 07's verdict,
in its own spec, is the most useful result in the tranche because the
prediction filed with it was WRONG in a specific and load-bearing way:

  "THE GUARD ARRIVED. From f024 a tall armoured guard in a helmet stands at
   the right facing him and stays ... So i2v DOES place a second figure from
   wording alone on a one-figure init, once both figures are named before
   anything is asked of either AND the four second-figure terms are struck
   from the negative. THE FAILURE MOVED RATHER THAN CLEARED: the point
   completes -- arm up at f072, fully extended by f096 -- but THE GOBLIN IS
   GONE BY f096, so the guard points at empty grass. The camera also pulls
   back at f024 to fit the second figure."

So wording can summon him; what wording cannot do is keep the frame. A figure
absent from the init is a RE-STAGING instruction, and the re-stage is what ate
the goblin. That is the same law the other three failures show with objects
(b02 and b03's trunk, b20's branch) -- a prompt naming something ABSENT from
the init makes the model build it and pull the camera back to fit it. Beats
04, 08 and 13 asked only for motion their plates had a body for, and all three
held their frame.

The fix is therefore plate-side here too, but by a different route: b02, b03
and b20 need an OBJECT composited in and naturalised, and beat 07 needs a
second FIGURE, which is a generation and not a paste.

THE ROUTE, AND IT IS PROVEN ON BEAT 08
--------------------------------------------------------------------------
The twins-skeleton route: one openpose canvas carrying BOTH figures, driving
xinsir/controlnet-openpose-sdxl-1.0, with the IP-Adapter reference masked to
the goblin's head box ALONE so the founder's face lands on the goblin and
nothing else. The guard gets no adapter -- his design is carried by words and
openpose, exactly like every shipped guard beat.

The skeleton was authored by pipeline/author_b07_twofig_skel_0821.py and is
committed: goblin at head_frac 0.370 (the founder's own proportion) and
stature 0.53 at screen left; guard at head_frac 0.200 -- FIVE HEADS, A GROWN
MAN, per the founder's 2026-08-20 guards ruling "they should look like grown
men. yes. dumb grown men" -- and stature 0.86 at screen right, both on one
ground line so they share a depth. THE GUARD'S ARM IS AUTHORED MID-RAISE and
not at the completed point: b20's frozen take is what an end-state plate buys,
so the plate holds a START state and leaves the motion model travel to do.

THE ONE VARIABLE
--------------------------------------------------------------------------
THE CONTROL IMAGE, and the wording that has to match it. Everything else is
beat 07's own accepted canon-plate rung by copy: same checkpoint, same
controlnet at scale 1.0, same square IP-Adapter reference at the same sha and
the same ip-scale, same sampler, same seed 20260899, same fetch-and-sha-check
stage step. Two things move with the control image because they cannot not:
the IP mask, re-derived at the goblin's stature here (the canon head_box()
assumes 0.90 and at 0.53 would print a box around empty grass), and the
prompt/negative, which must PLACE two figures instead of banning the second.

ONE SAMPLE. One seed, one job. The plate is judged on BOTH identities before
any motion spec is re-derived off it.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import derive_fetch_guard                                     # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402

PARENT = "pipeline/jobs/ep2-b07-canon-w2b-0821.yaml"
PARENT_ID = "ep2-b07-canon-w2b-0821"
PARENT_DIRTOK = "b07canon-w2b-0821"
PARENT_CONTROL = "jerry-canon-h37f-0821.png"
PARENT_CONTROL_SHA = ("2b50d9e8076eab57373cafbe506f8f7ce73f6abbec3c65eacffc"
                      "f877234ec13b")

NEW_ID = "ep2-b07-twofig-0821"
NEW_DIRTOK = "b07twofig-0821"
CONTROL = "jerry-guard-twofig-0821.png"
CONTROL_DIR = "farm-out/jerry-canon-assets-0821"
# Printed by pipeline/author_b07_twofig_skel_0821.py --check, and re-asserted
# below against the file on disk so a re-authored skeleton stops this deriver.
CONTROL_SHA = "48bf4edd2d394549b9764215fca84c562b9099e0d155ece6e38ea29a349afcb8"
IP_MASK = "87,485,412,763"          # the goblin's head-and-ears box AT 0.53

# 75 of 77 CLIP tokens, counted not estimated. `solo` is struck and `1boy`
# becomes `2boys`: the b07 motion verdict proved the second figure arrives only
# when BOTH are named before anything is asked of either.
PROMPT = ("best quality, 2boys, goblin, green skin, bald, pointy ears, slit "
          "pupils, eyebags, thin eyebrows, mandarin collar, green shirt, "
          "black shorts, boots, standing at left, arms at sides, and one tall "
          "armored city guard in a helmet at right, facing him, arm rising to "
          "point, muted color, tall grass, full body")

# 76 of 77. FOUR SECOND-FIGURE TERMS ARE STRUCK -- `2boys`, `multiple heads`,
# `background characters`, `group` -- because this plate wants exactly two
# figures and the parent's negative was written for a solo plate. `3boys` and
# `crowd` replace them: the ban moves from "a second figure" to "a THIRD".
# `child, chibi` stay: they hold the goblin's adult proportion, not his count.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, blank eyes, "
            "no pupils, thick eyebrows, cloak, hood, patchwork, human face on "
            "the goblin, wrinkled skin, old man, hair, beard, child, chibi, "
            "3boys, crowd, multiple heads, disembodied head, glowing eyes, "
            "orange eyes, third eye, eyepatch")

BAR = """JUDGED BY EYE AT 1:1, AND BOTH IDENTITIES ARE JUDGED, not just the goblin.

  G1  TWO FIGURES, EXACTLY TWO, both whole and both standing on the same
      ground. Not one figure with a shadow, not three.
  G2  THE GOBLIN IS THE FOUNDER'S GOBLIN. Read against
      taste/refs/goblin-canon-founder-0821.png: green skin, bald, large
      pointed ears, off-white eyes with narrow vertical slit pupils, eyebags,
      mandarin-collar sage shirt, dark shorts, boots. The IP-Adapter is masked
      to his head box alone, so a face that has drifted is a mask failure and
      the box is the fix.
  G3  THE GUARD IS A GROWN MAN. The founder's 2026-08-20 ruling is "they
      should look like grown men. yes. dumb grown men". Five heads tall,
      armoured, helmeted, a full head-and-then-some over the goblin. A chibi
      guard, a second goblin, or a guard the goblin's size is a FAIL.
  G4  THE GUARD'S FACE IS NOT THE GOBLIN'S. He gets no adapter; if the
      founder's face has leaked onto him the mask leaked and G2's box is wrong.
  G5  THE ARM IS MID-RAISE AND AIMED AT THE GOBLIN. Not down at his side, not
      already fully extended. The beat needs travel left to do.
  G6  STAGING SURVIVES: goblin at left, guard at right, both full body, tall
      grass, the plate's own dialect and palette.

G1, G3 and G4 are killing bars -- they are the whole reason this plate exists
instead of a reworded motion prompt. G5 is a strong preference: a completed
point is what froze beat 20's take, and it is worth one more round. Two rounds
is the budget."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    import hashlib
    ctl = os.path.join(REPO, CONTROL_DIR, CONTROL)
    if not os.path.isfile(ctl):
        raise SystemExit("!! missing skeleton %s -- run "
                         "pipeline/author_b07_twofig_skel_0821.py" % ctl)
    with open(ctl, "rb") as fh:
        have = hashlib.sha256(fh.read()).hexdigest()
    if have != CONTROL_SHA:
        raise SystemExit(
            "!! the skeleton on disk hashes %s, this deriver names %s. An "
            "asset whose content changes gets a NEW NAME -- re-author it under "
            "one rather than repointing this constant." % (have, CONTROL_SHA))

    assert_under_clip77("b07 twofig prompt", PROMPT)
    assert_under_clip77("b07 twofig negative", NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "canon-motion plate-fix lane, 2026-08-21",
            "consumer": (
                "THE INIT FOR BEAT 07'S RE-DERIVED MOTION SPEC, and nothing "
                "else until then. Named consumer: the canon-motion lane, which "
                "cannot file beat 07's next i2v rung until a plate exists that "
                "already holds BOTH figures -- because the wave proved that "
                "summoning the guard by wording alone costs the frame and then "
                "the goblin. review/ep2-ship-0821 is not touched by this job "
                "and no cut changes because this plate landed."),
            "success": (
                "ONE 832x1216 png holding EXACTLY TWO FIGURES, judged by eye at "
                "1:1 on both of them. G1 two whole figures on one ground line, "
                "goblin left, guard right; G2 the goblin is the founder's "
                "goblin read against taste/refs/goblin-canon-founder-0821.png "
                "-- bald, large pointed ears, off-white eyes with narrow "
                "vertical slit pupils, mandarin-collar sage shirt; G3 the guard "
                "is a GROWN MAN, five heads, armoured and helmeted, a full head "
                "taller; G4 the guard's face is NOT the goblin's -- he gets no "
                "adapter, so a leak means the IP mask is wrong; G5 his arm is "
                "MID-RAISE toward the goblin, not completed and not down; G6 "
                "both full body in tall grass in the plate's dialect. The named "
                "degenerate outcome is TWO GOBLINS: the adapter is masked to "
                "one head box and if it has painted the founder's face on both "
                "figures this plate is a FAIL and the mask is the fix, not the "
                "seed."),
            "why": (
                "BEAT 07'S MOTION FAILED BECAUSE THE SECOND FIGURE ARRIVED BY "
                "WORDING INSTEAD OF BY PLATE, AND THE ARRIVAL RE-STAGED THE "
                "SHOT.\n\nThe beat's own canon-motion verdict is the licence "
                "and it corrected this lane's prediction: the guard DID appear "
                "from f024 once both figures were named and the second-figure "
                "terms left the negative -- 'the point completes ... but THE "
                "GOBLIN IS GONE BY f096, so the guard points at empty grass. "
                "The camera also pulls back at f024 to fit the second "
                "figure.'\n\nThat is one instance of the law the wave measured "
                "four times: a prompt naming something ABSENT from the init "
                "makes the model build it and pull the camera back hunting for "
                "it, while the three beats whose prompts ask only for motion "
                "the plate has a body for -- 04, 08 and 13 -- all held their "
                "frame. For b02, b03 and b20 the absent thing is an object and "
                "the fix is a composite. Here it is a FIGURE, so the fix is a "
                "two-figure plate.\n\nWHAT THIS JOB DOES: beat 07's accepted "
                "canon-plate rung with ONE input changed -- a two-figure "
                "openpose skeleton instead of the solo one, the IP-Adapter mask "
                "re-derived to the goblin's head box at his stature in it, and "
                "wording that places both figures. Same checkpoint, controlnet, "
                "reference, ip-scale, sampler and seed.\n\nWHAT IT DOES NOT DO: "
                "it renders no motion and files no motion spec. The re-derived "
                "i2v rung waits on a human opening this png, because the whole "
                "premise is that a plate must CONTAIN what the prompt names."),
        },
        overrides={
            "argv:--ip-mask": IP_MASK,
            "argv:--repo-commit": "a4d49f06",
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "key:priority": 16,
            "key:script_line": (
                "CONFISCATE -- 'Guard 1 points at the scavenger, decisive.' He "
                "is the object of the sentence and has just been identified. "
                "Apprehension, not panic: the guards are absurd and he is "
                "starting to notice."),
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE CONTROL IMAGE, and the two things that cannot not move "
                "with it. Changed: the openpose skeleton (solo -> two-figure), "
                "the IP mask (%s, the goblin's head-and-ears box re-derived at "
                "his stature 0.53 -- the canon head_box() assumes 0.90 and "
                "would print a box around empty grass), and the prompt and "
                "negative, which now PLACE a second figure where they used to "
                "ban one. Unchanged and carried by copy: the checkpoint, "
                "xinsir/controlnet-openpose-sdxl-1.0 at scale 1.0, the square "
                "IP-Adapter reference jerry-canon-sq45-0821.png at the same "
                "sha256 and ip-scale 1.0, ip-adapter-plus-face_sdxl_vit-h, the "
                "sampler, seed 20260899, and the fetch-and-sha-check stage step."
                % IP_MASK),
            "control_provenance": (
                "%s/%s, 832x1216, sha256 %s, authored by "
                "pipeline/author_b07_twofig_skel_0821.py and committed on "
                "origin/main. The deriver re-hashes the file on disk before it "
                "writes, and the stage step re-hashes it on the box before a "
                "GPU second is spent, so a re-authored skeleton stops the job "
                "rather than quietly conditioning on a different staging. "
                "GEOMETRY: goblin head_frac 0.370 stature 0.53 at cx 0.30; "
                "guard head_frac 0.200 (FIVE HEADS -- a grown man) stature 0.86 "
                "at cx 0.71; one shared ground line at y=1149; the guard's "
                "screen-left arm mid-raise with the wrist at (296,448), aimed "
                "at the goblin's face." % (CONTROL_DIR, CONTROL, CONTROL_SHA)),
            "founder_rulings_this_plate_answers_to": (
                "TWO, AND THEY ARE BOTH IMAGES OR VERBATIM. (1) THE GOBLIN: "
                "taste/refs/goblin-canon-founder-0821.png, supplied 2026-08-21 "
                "with 'dude, this is how the goblin should look'. It is carried "
                "here by the SAME square reference and the SAME adapter weight "
                "as the accepted solo plate -- only the mask moved. (2) THE "
                "GUARD: the founder's 2026-08-20 ruling, 'they should look like "
                "grown men. yes. dumb grown men'. That is why the guard's "
                "skeleton is FIVE HEADS TALL and not a scaled goblin, and why "
                "G3 is a killing bar rather than a note."),
            "clip77_measured_not_estimated": (
                "positive 75 of 77, negative 76 of 77, counted with "
                "animagine-xl-3.1's OWN vocab by pipeline/clip_token_count.py "
                "before this spec was written. The overflow is silent and drops "
                "from the tail, so an unmeasured prompt bans nothing at the end "
                "of itself -- and on this plate the tail is where the guard is "
                "placed."),
            "failure_predicted_in_advance": (
                "TWO GOBLINS, and it is filed before the pixels. The adapter is "
                "masked to ONE head box, but the box is a rectangle and the "
                "guard's head at cx 0.71 is nowhere near it, so a leak would "
                "mean the mask is not being honoured rather than that it is "
                "badly placed. SECOND: A CHIBI GUARD. openpose gives the model "
                "proportion, not age, and every prior guard on this show was "
                "carried by words alone -- if five heads of skeleton still "
                "yields a big child, the lever is the wording and the founder's "
                "ruling is the bar it has to clear. THIRD, AND CHEAPEST TO "
                "MISS: the arm reads as ALREADY POINTING. The skeleton is "
                "mid-raise, but SDXL may resolve an ambiguous elbow into the "
                "completed gesture, and an end-state plate is exactly what "
                "froze beat 20."),
            "not_done_on_purpose": (
                "NO MOTION IS RENDERED BY THIS JOB and no motion spec is filed "
                "by it, for the same reason as the b02/b03/b20 naturalize jobs: "
                "filing the motion rung in the same breath would assert the "
                "plate passed before anyone looked at it. ALSO NOT DONE: the "
                "guard is not given an IP-Adapter reference. There is no "
                "founder image of a guard, and inventing one to condition on "
                "would be this lane authoring a character design -- which is "
                "taste, and reserved."),
        },
        by="pipeline/derive_b07_twofig_0821.py",
        retoken=[
            (PARENT_ID, NEW_ID),
            (PARENT_DIRTOK, NEW_DIRTOK),
            (PARENT_CONTROL, CONTROL),
            (PARENT_CONTROL_SHA, CONTROL_SHA),
        ],
    )

    # A RETOKEN PAIR THAT MATCHES NOTHING PASSES SILENTLY. derive_spec asserts
    # that every OVERRIDE hit at least one site -- "a substitution that silently
    # matched nothing is how a 'one variable' rung becomes a re-run of its
    # parent under a new name" -- but it makes no such assertion for `retoken`,
    # and the parent id is the only pair it checks. This lane proved the gap the
    # expensive way: a one-character typo in PARENT_CONTROL_SHA meant the sha
    # pair matched nothing, and the emitted spec named the TWO-FIGURE skeleton
    # while asserting the SOLO skeleton's digest -- a job that fetches one image
    # and refuses it, discovered only because the yaml was re-read. So the yaml
    # is re-read, every time, and both directions are checked.
    # `derivation` is EXCLUDED, and not as a convenience: derive_spec records
    # every pair there as "old -> new", so the parent's tokens are SUPPOSED to
    # survive in the provenance block. Checking it would make the record of the
    # substitution indistinguishable from a failure to substitute.
    import yaml as _yaml
    blob = _yaml.safe_dump({k: v for k, v in child.items() if k != "derivation"},
                           allow_unicode=False)
    for old, new, what in (
            (PARENT_CONTROL, CONTROL, "control filename"),
            (PARENT_CONTROL_SHA, CONTROL_SHA, "control sha256"),
            (PARENT_DIRTOK, NEW_DIRTOK, "box working directory")):
        if old in blob:
            raise SystemExit(
                "!! the parent's %s (%s) SURVIVES retokening. The pair matched "
                "nothing or matched only some sites." % (what, old[:24]))
        if new not in blob:
            raise SystemExit(
                "!! the child names no %s (%s). The retoken pair is pointed at "
                "a string this parent does not contain -- check it against the "
                "parent yaml rather than adjusting this assertion."
                % (what, new[:24]))

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-22s control %s sha %s..  ip-mask %s"
          % (NEW_ID, CONTROL, CONTROL_SHA[:12], IP_MASK))
    print("   prompt 75/77, negative 76/77 -- measured")
    if not a.write:
        print("\n-- dry run. re-run with --write.")
        return 0
    path = derive_spec.write(child, out, force=a.force)
    derive_fetch_guard.assert_fetch_urls_resolve(path, must_hold=(CONTROL,))
    print("   wrote %s  (fetch urls resolve)" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
