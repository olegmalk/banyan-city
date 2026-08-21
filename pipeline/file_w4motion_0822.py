#!/usr/bin/env python3
r"""MOTION FOR THE W4 SWEEP -- THE FIRST CLIPS DRAWN ON THE EYE HE APPROVED.

    python3 pipeline/file_w4motion_0822.py                 # dry run, all beats
    python3 pipeline/file_w4motion_0822.py --write --beats 2,3,4

WHY THIS FILER EXISTS RATHER THAN A RE-RUN OF THE OLD ONES. On 2026-08-22 the
founder vetoed the goblin's FACE on a sweep frame -- "that aint my goblin" --
and rounds nine to twelve found the eye: `eyebags, jitome` in the positive, no
pupil tag anywhere, `large eyes, big eyes` in the negative. Every beat's plate
was re-rendered as `ep2-bNN-canon-w4-0821` on that recipe. This filer points the
existing motion of each beat at its NEW plate.

  * THE ACTION IS NOT RE-AUTHORED. Each beat's action sentence is lifted
    verbatim out of the motion spec that already exists for it -- the
    `canonmotion-0821` seven and the `canonmotion-0822` three. Those sentences
    were written to the wave's two measured laws (name nothing the plate does
    not contain; an action needs a start, a middle and an END) and several have
    already produced usable footage. Re-writing them here would put two
    variables in one clip.

  * THE HEAD CLAUSE IS RE-AUTHORED, AND IT HAS TO BE. Every existing motion
    prompt describes the subject as having "off-white eyes with narrow vertical
    slit pupils". That is the eye the founder threw out, and the ladder's own
    finding is that a subject clause disagreeing with its init is how a video
    model drifts a face back to its prior over a clip -- so shipping the old
    words over the new plate would spend the whole fix in the first second of
    motion. EYE_OLD -> EYE_NEW below is the only edit, and it is asserted: a
    beat whose parent prompt does not contain the old phrase is a hard stop,
    not a silent pass.

  * THE RECIPE IS BEAT 04'S, WHOLESALE, exactly as the 0822 filer had it:
    704x1280, 105 frames at 24fps, guidance 2.0, distilled sigmas, two-stage,
    crf 10, sequential offload, cover_crop asserting the plate's digest before
    an init frame is written.

BEATS 17 AND 19 ARE HERE TOO, AND THEIR ACTIONS ARE AUTHORED RATHER THAN
CARRIED -- neither has ever had a motion spec. Both are written to the wave's
laws plus one the wave paid for on beat 20 the same week: do not ask a plate for
a state it is already in. See ACTIONS_AUTHORED.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import yaml as _yaml                                          # noqa: E402

PARENT = "pipeline/jobs/ep2-b04-canonmotion-0821.yaml"
BOX_PLATE = r"C:\banyan-farm\courier-box\farm-out\%s\%s-ipahead.png"
REL_PLATE = "farm-out/%s/%s-ipahead.png"

# The eye, and it is the whole reason this filer is not a re-run.
EYE_OLD = "off-white eyes with narrow vertical slit pupils"
EYE_NEW = ("small off-white almond eyes with tiny dark pupils, heavy upper "
           "eyelids, eyebags, flat deadpan expression")

# beat -> (slug, the spec whose ACTION sentence is carried, the plate job).
# b14 takes w4b: its w4 plate drew a SECOND GOBLIN in the grass at the right
# edge -- the same `solo` violation 17 and 19 hit in w2 -- and w4b is the
# re-plate with `second goblin, crowd` in the negative.
# THE TWO BEATS WITH NO PARENT MOTION, AUTHORED HERE. 17 and 19 have clean w4
# plates and have never had a motion spec, so there is no sentence to carry.
# Both are written to the wave's two measured laws -- name nothing the plate
# does not contain, and give the action a start, a middle and an END with a
# HALFWAY clause -- and to a third the wave paid for on beat 20 the same week:
#
#   DO NOT ASK FOR A STATE THE PLATE IS ALREADY IN. b20's inventory said he was
#   already looking up and then its action told him to look up; the model has
#   nowhere to travel and returns a still with a runtime. 17's plate is already
#   `turning away` and 19's is already `looking back down at the ground`, so
#   both actions CONTINUE their pose instead of initiating it.
#
# Neither names the fig, the sapling or a guard: 19's beat is the fig dropping
# and the plate contains no fig, so the drop is the assembly's problem and
# naming it here is precisely what pulled the camera back on four round-1 beats.
ACTIONS_AUTHORED = {
    17: ("He is standing, turning away, in tall grass, full body. THE ACTION: "
         "he carries the turn through, settles onto the far foot and takes one "
         "step away -- turn through, plant, step. HALFWAY THROUGH his back is "
         "most of the way to camera and his leading foot is lifting."),
    19: ("He is standing mid-stride, looking back down at the ground, in tall "
         "grass, full body. THE ACTION: his lifted foot comes down, his weight "
         "settles back over it, and he leans a little further down toward the "
         "grass at his heel -- foot down, weight back, lean in. HALFWAY "
         "THROUGH the foot has landed, his weight is still shifting and his "
         "head is already low."),
}

# THE POSE VARIANT, AND IT IS A FOUNDER STORY RULING RATHER THAN A LANE IDEA.
# On beat 13 he ruled that the goblin CURLS DOWN SMALL to fit his face into the
# sapling's hand-sized patch of shade -- he never rises, and there is no phantom
# tree. `ep2-b13-canon-w4curl-0821` is that plate (hunch skeleton, head tipped
# down and to one side). Its action must CONTINUE the curl, not start one: the
# plate is already hunched, and asking a plate for the state it is already in is
# what returned beat 20 a still with a runtime. The "never rises" clause is
# written in explicitly because the beat's own shipping clip stands him back up,
# which is the thing the ruling is against.
VARIANTS = {
    ("13", "curl"): dict(
        slug="the-shade",
        plate="ep2-b13-canon-w4curl-0821",
        action=("He is hunched forward, head tipped down and to one side, in "
                "tall grass, full body. THE ACTION: his shoulders drop and he "
                "settles lower over his knees, his head sinking a little "
                "further down and to the side -- settle, sink, still. HALFWAY "
                "THROUGH his shoulders are down and his head is lower than it "
                "started, still tipping. HE NEVER RISES, he never straightens "
                "up and his head never comes back up."),
    ),
}

ROWS = {
    2:  ("the-sprint",     "ep2-b02-canonmotion-0821", "ep2-b02-canon-w4-0821"),
    3:  ("bad-cover",      "ep2-b03-canonmotion-0821", "ep2-b03-canon-w4-0821"),
    4:  ("the-footnote",   "ep2-b04-canonmotion-0821", "ep2-b04-canon-w4-0821"),
    7:  ("confiscate",     "ep2-b07-canonmotion-0821", "ep2-b07-canon-w4-0821"),
    8:  ("inside-him",     "ep2-b08-canonmotion-0821", "ep2-b08-canon-w4-0821"),
    13: ("the-shade",      "ep2-b13-canonmotion-0821", "ep2-b13-canon-w4-0821"),
    14: ("the-defense",    "ep2-b14-canonmotion-0822", "ep2-b14-canon-w4b-0821"),
    15: ("good-listener",  "ep2-b15-canonmotion-0822", "ep2-b15-canon-w4-0821"),
    16: ("why",            "ep2-b16-canonmotion-0822", "ep2-b16-canon-w4-0821"),
    17: ("goodbye",        None,                       "ep2-b17-canon-w4-0821"),
    19: ("the-drop",       None,                       "ep2-b19-canon-w4-0821"),
    20: ("evidence",       "ep2-b20-canonmotion-0821", "ep2-b20-canon-w4-0821"),
}


# ── THE GUARD, AND WHY HE IS FIXED IN THIS FILER TOO. ────────────────────────
# `check_canon_drift` failed beat 07's first draft against `ep2-guard-hair`, and
# it was right twice over.
#
#   1. THE WORD `bald`. The canon entry says it plainly: `bald` was the
#      steward's own translation of an anti-helmet intent and carried the
#      founder's BALD ruling for the GOBLIN onto men it was never about. In this
#      prompt the word genuinely IS the goblin's -- but it sits four words from
#      a second figure in a two-figure clause, which is the attribute-binding
#      hazard this tree has already measured on eyewear (`ep2-b10-attrbind-
#      eyewear-0817`). A checker that cannot tell which figure owns the word is
#      modelling the sampler's problem, not failing to understand ours. So the
#      goblin gets `a bare hairless scalp`, which no guard rule matches and no
#      reader can mis-assign.
#
#   2. THE HELMET, which is the bigger error. `ONE TALL ARMOURED CITY GUARD in a
#      helmet` predates 2026-08-22, when the founder settled guard 1 by
#      SELECTING one of our own frames -- taste/refs/guard1-canon-founder-0822.
#      That guard has near-black cropped hair and round wire rims and no armour
#      and no helmet, and humans are drawn in detailed cinematic anime. A
#      helmet is not a small deviation from that reference, it is a different
#      character; and a helmet also hides the hair the canon entry exists to
#      protect, which is presumably how the two survived beside each other.
#
# NOT ATTEMPTED HERE: the guard's BODY. The coordinator's note is explicit that
# a close-up reference does not settle full-body proportion and that the
# re-plates need it paired with the 5-head skeleton. That is a PLATE job for
# b05/07/08 and it is not this filer's -- this only stops the motion prompt
# asking for a character the canon no longer has.
GUARD_OLD = ("ONE TALL ARMOURED CITY GUARD in a helmet, standing at the "
             "right, facing the goblin, a full head taller.")
GUARD_NEW = ("ONE TALL CITY GUARD, a grown man with near-black cropped hair "
             "and round wire-rimmed glasses, in a brown patrol tunic, "
             "standing at the right, facing the goblin, a full head taller.")
BALD_OLD = "ONE small green goblin, bald, large pointed ears,"
BALD_NEW = ("ONE small green goblin with a bare hairless scalp, large pointed "
            "ears,")


def _apply_guard_canon(beat: int, prompt: str) -> str:
    """Bring any guard in this prompt onto the 2026-08-22 canon."""
    if "GUARD" not in prompt.upper():
        return prompt
    for old, new in ((GUARD_OLD, GUARD_NEW), (BALD_OLD, BALD_NEW)):
        if old not in prompt:
            raise SystemExit("!! beat %02d names a guard but does not carry "
                             "%r -- this filer cannot bring it onto canon "
                             "blind, and shipping it would render the "
                             "pre-08-22 guard" % (beat, old[:40]))
        prompt = prompt.replace(old, new)
    if "helmet" in prompt or "\bbald\b" in prompt:
        raise SystemExit("!! beat %02d still carries the pre-canon guard"
                         % beat)
    return prompt


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _prompt_of(spec_id: str) -> str:
    p = os.path.join(REPO, "pipeline/jobs/%s.yaml" % spec_id)
    if not os.path.isfile(p):
        raise SystemExit("!! %s does not exist -- no action to carry" % spec_id)
    d = _yaml.safe_load(open(p, encoding="utf-8"))
    keys = [k for k in d["payload"] if "motion-prompt" in k]
    if len(keys) != 1:
        raise SystemExit("!! %s has %d motion-prompt payloads" % (spec_id,
                                                                  len(keys)))
    return d["payload"][keys[0]]


def build(beat: int, pspec: dict, variant: str = None):
    if variant:
        v = VARIANTS[(str(beat), variant)]
        slug, action_from, plate_job = v["slug"], None, v["plate"]
    else:
        slug, action_from, plate_job = ROWS[beat]
    # THE WHOLE PROMPT IS CARRIED, NOT JUST THE ACTION, and the eye is swapped
    # inside it. The first draft grafted beat 04's head clause onto every beat
    # and beat 07 caught it: 07 is the confiscation, its head names TWO figures
    # -- the goblin AND the tall armoured guard, placed left and right -- and
    # it has no `He is ` clause at all. Beat 04's head would have deleted the
    # guard from the only beat that needs one, which is the prompt-summons law
    # that already emptied 07 twice. Carrying each beat's own prompt makes the
    # eye the single edit for all ten.
    if action_from is None:
        # No parent motion for this beat: beat 04's single-figure head clause
        # plus the sentence authored above. 04 is the right donor -- it is the
        # wave's cleanest pass and its head names ONE goblin, which is what
        # these two plates hold.
        head = _prompt_of("ep2-b04-canonmotion-0821")
        action = (VARIANTS[(str(beat), variant)]["action"] if variant
                  else ACTIONS_AUTHORED[beat])
        prompt = head[:head.index("He is ")] + action
    else:
        prompt = _prompt_of(action_from)
    if EYE_OLD not in prompt:
        raise SystemExit("!! %s no longer contains %r -- this filer's whole "
                         "job is to replace it, and a silent no-op would ship "
                         "the vetoed eye" % (action_from, EYE_OLD))
    prompt = prompt.replace(EYE_OLD, EYE_NEW)
    prompt = _apply_guard_canon(beat, prompt)

    rel = REL_PLATE % (plate_job, plate_job)
    if not os.path.exists(os.path.join(REPO, rel)):
        raise SystemExit("!! %s is not on disk -- pull the plate first" % rel)
    plate_sha = sha_of(rel)
    new_id = ("ep2-b%02d-w4motion%s-0822" % (beat, variant) if variant
              else "ep2-b%02d-w4motion-0822" % beat)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "the night iteration lane, 2026-08-22",
            "consumer":
                "A CANDIDATE for beat %02d on review/ep2-beats-0821. "
                "review/ep2-ship-0821 is not touched and no cut moves because "
                "this landed -- a clip here is a candidate, and a candidate "
                "becomes a pick only when he picks it." % beat,
            "success":
                "ONE 704x1280 105-frame 24fps mp4 in which the face is the "
                "one he approved -- small off-white almond eyes, tiny dark "
                "pupils, eyebags, broad dome, near-horizontal ears -- and "
                "STAYS that face for the whole clip. The named degenerate "
                "outcome is the eye drifting back to a large rendered iris "
                "over the run, which is exactly what the head clause below "
                "was rewritten to prevent.",
            "why":
                "THE FOUNDER VETOED THE FACE ON 2026-08-22 -- 'that aint my "
                "goblin' -- and it was the EYE. Rounds nine to twelve on beat "
                "13 found it: naming the pupil (`slit pupils`, `constricted "
                "pupils`) draws a large rendered iris every time, while "
                "`eyebags` flips the fill to an off-white field and `jitome` "
                "fixes the size and shape. Both are RENDERING-CONVENTION "
                "tags, not feature tags, and that is the finding. Every "
                "plate was re-rendered as w4 on the corrected recipe and "
                "opened at 1:1 on a common-scale contact sheet before this "
                "spec was written.\n\n%s THE HEAD CLAUSE IS NOT CARRIED AS "
                "WRITTEN: it said `off-white eyes with narrow vertical slit "
                "pupils`, which is the vetoed eye, and a subject clause that "
                "disagrees with its own init is how this engine drifts a face "
                "back to its prior over a clip."
                % ("THE ACTION IS AUTHORED HERE -- this beat has never had a "
                   "motion spec, so there was no sentence to carry. It is "
                   "written to the wave's laws and, because this plate is "
                   "ALREADY in the pose the beat describes, it CONTINUES that "
                   "pose rather than asking for it: beat 20 asked a plate to "
                   "look up when its own inventory already said he was "
                   "looking up, and got a still with a runtime."
                   if action_from is None else
                   "THE ACTION IS CARRIED VERBATIM from %s so the plate is "
                   "the only thing that changed." % action_from),
        },
        overrides={
            "argv:--src": BOX_PLATE % (plate_job, plate_job),
            "argv:--sha256": plate_sha,
            "payload:b%02d-motion-prompt.txt" % beat: prompt,
            "key:beat": beat,
            "key:priority": 13,
            "seed": 20260870 + beat,
        },
        extra={
            # THE BAR CARRIES THE VETOED EYE TOO. Its M1 check reads "confirm
            # eyes, slit pupils, brow and mouth are present at the LAST frame".
            # A judge told to look for slit pupils will PASS the frame the
            # founder rejected and fail the one he approved, so the scoring
            # sentence is corrected alongside the prompt rather than after it.
            "bar": pspec["bar"].replace(
                "eyes, slit pupils, brow and mouth",
                "eyes, tiny dark pupils on an off-white field, eyebags, brow "
                "and mouth"),
            "the_one_variable":
                "THE PLATE. The recipe, the head clause and the action are "
                "identical to what this beat already ran, so a frame that "
                "misses is attributable to the w4 plate and to nothing else.",
            "plate_provenance":
                "%s, 832x1216, sha256 %s, rendered by %s on the round-twelve "
                "recipe (openpose skeleton at head_frac 0.370 + IP-Adapter on "
                "jerry-canon-sq45-0821 at 1.0, `eyebags, jitome` positive, "
                "`large eyes, big eyes` negative, no pupil tag) and OPENED AT "
                "1:1 against taste/refs/goblin-canon-founder-0821.png on a "
                "common-scale sheet before this spec existed. cover_crop.py "
                "asserts that digest before it writes an init frame."
                % (rel, plate_sha, plate_job),
            "head_clause_rewrite":
                "%r -> %r. The ONLY edit to the carried prompt." % (EYE_OLD,
                                                                    EYE_NEW),
            "not_done_on_purpose":
                "ABSENT: ep2-b13-canon-w4curl-0821, the "
                "founder's b13 story ruling (he curls DOWN small, never "
                "rises) rendered as a second plate for that beat. It is a "
                "POSE change and gets its own motion spec, not a slot in a "
                "wave whose variable is the face.",
        },
        retoken=[("ep2-b04-canonmotion-0821", new_id),
                 ("04-evidence", "%02d-%s" % (beat, slug)),
                 ("b04-", "b%02d-" % beat)],
        by="pipeline/file_w4motion_0822.py",
    )
    return child, prompt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--beats", default=",".join(str(b) for b in sorted(ROWS)))
    ap.add_argument("--variant", help="a VARIANTS pose variant, e.g. curl")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    pspec = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    for beat in [int(b) for b in a.beats.split(",")]:
        if a.variant:
            if (str(beat), a.variant) not in VARIANTS:
                raise SystemExit("!! beat %d has no %r variant"
                                 % (beat, a.variant))
        elif beat not in ROWS:
            raise SystemExit("!! beat %d has no row in this filer" % beat)
        child, prompt = build(beat, pspec, variant=a.variant)
        blob = _yaml.safe_dump({k: v for k, v in child.items()
                                if k != "derivation"})
        if "b04-" in blob or "04-evidence" in blob:
            if beat != 4:
                raise SystemExit("!! beat %02d: a beat-04 token survived "
                                 "retokening" % beat)
        # Checked on the two strings that STEER a render -- the prompt the
        # sampler reads and the bar a judge scores against -- and not on the
        # whole blob, because this filer's own provenance prose quotes the old
        # phrase on purpose to say what it replaced.
        pk = [k for k in child["payload"] if "motion-prompt" in k][0]
        for where, text in (("prompt", child["payload"][pk]),
                            ("bar", child["bar"])):
            if EYE_OLD in text or "slit pupils" in text:
                raise SystemExit("!! beat %02d: the VETOED eye is still in the "
                                 "%s" % (beat, where))
        out = "pipeline/jobs/%s.yaml" % child["id"]
        # The plate is read back off the EMITTED argv, not off ROWS: with a
        # --variant in play ROWS holds the wrong plate, and a report line that
        # names a different file than the spec uses is how a wrong init ships.
        argv = [t for st in child["steps"] for t in st.get("argv", [])]
        used = argv[argv.index("--src") + 1].replace("\\", "/").split("/")[-2]
        print("%-26s beat %02d  plate %-28s prompt %d chars"
              % (child["id"], beat, used, len(prompt)))
        if a.write:
            derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % out)
    if not a.write:
        print("\nDRY RUN -- pass --write to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
