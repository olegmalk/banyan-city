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

BEATS 17 AND 19 ARE NOT HERE. Their w4 plates came back clean -- the `second
goblin, crowd` negative did its job -- but neither beat has ever had a motion
spec, so there is no action sentence to carry and authoring two from scratch is
a separate piece of work with its own bar. Recorded rather than guessed at.
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
    20: ("evidence",       "ep2-b20-canonmotion-0821", "ep2-b20-canon-w4-0821"),
}


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


def build(beat: int, pspec: dict):
    slug, action_from, plate_job = ROWS[beat]
    # THE WHOLE PROMPT IS CARRIED, NOT JUST THE ACTION, and the eye is swapped
    # inside it. The first draft grafted beat 04's head clause onto every beat
    # and beat 07 caught it: 07 is the confiscation, its head names TWO figures
    # -- the goblin AND the tall armoured guard, placed left and right -- and
    # it has no `He is ` clause at all. Beat 04's head would have deleted the
    # guard from the only beat that needs one, which is the prompt-summons law
    # that already emptied 07 twice. Carrying each beat's own prompt makes the
    # eye the single edit for all ten.
    prompt = _prompt_of(action_from)
    if EYE_OLD not in prompt:
        raise SystemExit("!! %s no longer contains %r -- this filer's whole "
                         "job is to replace it, and a silent no-op would ship "
                         "the vetoed eye" % (action_from, EYE_OLD))
    prompt = prompt.replace(EYE_OLD, EYE_NEW)

    rel = REL_PLATE % (plate_job, plate_job)
    if not os.path.exists(os.path.join(REPO, rel)):
        raise SystemExit("!! %s is not on disk -- pull the plate first" % rel)
    plate_sha = sha_of(rel)
    new_id = "ep2-b%02d-w4motion-0822" % beat

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
                "spec was written.\n\nTHE ACTION IS CARRIED VERBATIM from %s "
                "so the plate is the only thing that changed. THE HEAD CLAUSE "
                "IS NOT: it said `off-white eyes with narrow vertical slit "
                "pupils`, which is the vetoed eye, and a subject clause that "
                "disagrees with its own init is how this engine drifts a face "
                "back to its prior over a clip." % action_from,
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
                "BEATS 17 AND 19 HAVE CLEAN W4 PLATES AND NO CLIP HERE. "
                "Neither has ever had a motion spec, so there is no action "
                "sentence to carry, and authoring two from scratch is its own "
                "piece of work with its own bar -- doing it inside a filer "
                "whose stated one variable is THE PLATE would be a lie about "
                "what changed. Also absent: ep2-b13-canon-w4curl-0821, the "
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
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    pspec = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    for beat in [int(b) for b in a.beats.split(",")]:
        if beat not in ROWS:
            raise SystemExit("!! beat %d has no row in this filer" % beat)
        child, prompt = build(beat, pspec)
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
        print("%-26s beat %02d  plate %-28s prompt %d chars"
              % (child["id"], beat, ROWS[beat][2], len(prompt)))
        if a.write:
            derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % out)
    if not a.write:
        print("\nDRY RUN -- pass --write to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
