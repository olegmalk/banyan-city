#!/usr/bin/env python3
r"""THE TILE-READ WEDGE: eight plates, one seed, two clean axes, $0.

WHAT QUESTION THIS ANSWERS, AND IT IS NOT A TASTE QUESTION.
The founder ruled 2026-08-20 night that the goblin must read as the B TILE'S
CREATURE and that `adult` in `pipeline/canon.yaml` was steward drift
(`correction_2026_08_20`). The design axis is now FIDELITY TO
review/ep2-goblin-design-0819/adult-b19-0819.jpg. The post-ship wave is seven
beats (02 03 04 07 08 13 20) and NOT ONE OF THEM CAN BE AUTHORED until we own a
wording that puts that creature on the canvas ON PURPOSE. This is that wording,
measured instead of asserted.

THE REPO FINDING THIS IS BUILT ON. The two tile-faithful frames in the shipping
cut -- beat 19 (which IS the tile) and beat 15 (the next-best match) -- were BOTH
rendered from the SAME man-read string that produced beats 03, 04, 13 and 20,
and both are WIDE with `close-up` in the negative. So the phrase is not the
discriminator; FRAMING is. At distance animagine draws the face as a blank mask
and the creature read is a by-product of scale. THAT IS NOT A RECIPE, IT IS AN
AVOIDANCE: b04's own `done_when` is a face-fills-frame close-up whose subject is
the eyes. So this wedge runs at the CLOSE-UP, the hardest framing in the episode.

=============================================================================
THE OUTSIDE RESEARCH, WHICH OVERTURNED MY FIRST DRAFT OF THIS FILE
=============================================================================
Run 1 of this wedge was authored from invented vocabulary. A research pass
against the animagine-xl-3.1 model card and the Danbooru tag database
(post counts via safebooru.donmai.us/tags.json, 2026-08-20) found that half of
it was untrained tokens. Recorded here because the corrections are the finding:

  * `blank eyes` (18,467 posts) IS the tile's eye, exactly -- the wiki says
    "eyes that are missing both the irises and pupils; only the sclera are
    present." I had also written `no pupils` and `white eyes`. BOTH ARE WRONG:
    `no pupils` KEEPS THE IRIS, and `white eyes` keeps iris AND pupil (its own
    wiki says "not to be confused with blank eyes"). Dropped.
  * `tsurime` (64,520, upward-slanting eyes) and `jitome` (49,408, a flat line
    across the top narrowing the eye into a slit) are the tile's eye SHAPE and
    I had no tags for it at all. Added.
  * `no nose` (30,317) is real and exact: "no discernible nose projecting from
    their face."
  * `lipless mouth` DOES NOT EXIST. Neither does `flat mouth`, `straight mouth`
    or `line mouth`. The only real tag for the tile's single thin line is the
    emoticon tag `:|` (14,379), with `closed mouth` and `expressionless`.
  * THERE IS NO TAG FOR THE TILE'S EARS. `short pointy ears` has ZERO posts,
    `round ears` does not exist, and `long ears` is an ALIAS TO `pointy ears`.
    Danbooru cannot express "short, broad, low-set, swept back." So the only
    sourced lever is to NAME NO EAR TAG AT ALL and negate the spike tags --
    `pointy ears` (592,662) and `long pointy ears` (34,353).
  * `smooth skin` has ZERO posts. `shiny skin` (156,330) and `two-tone skin`
    (18,474) are real, and two-tone is literally the tile's chartreuse crown
    grading to a deeper green.
  * `colored skin` (210,118) is the species lever that carries no facial
    baggage: "skin that is any color that would be unnatural for a normal
    human ... fantasy races ... aliens ... not-entirely-human characters."
  * AND THE ONE THAT MATTERS MOST -- `goblin` (4,326) IS FIGHTING US. Its own
    Danbooru wiki defines the creature as having "pointy noses and ears." The
    tag encodes our two loudest defects. `orc` (tusks, pointy ears) and
    `monster boy` ("a human face and torso with non-human arms or legs") are
    worse. So `goblin` LEAVES the positive from v2 up, and `monster boy` goes
    in the negative.
  * `1other` (126,608) means GENDER-ambiguous, not species-non-human, and is 6%
    the size of `1boy` (2,100,960). No published source says what swapping them
    does in this model family. The research's own recommendation is that the
    bigger lever is probably DROPPING `1boy` entirely rather than substituting
    a weaker token -- so this wedge samples all three rather than guessing.
  * NEGATIVES ARE A WEAK INSTRUMENT FOR THIS and the ladder is built around it.
    Ban et al., ECCV 2024 (arXiv:2406.02965): a negative acts only AFTER the
    positive has rendered the thing, and introducing one too early "paradoxically
    results in the generation of the specified object." Alhamoud et al., CVPR
    2025 (NegBench): CLIP text encoders barely parse "no"/"not"/"without".
    `no nose` therefore works NOT because CLIP understands the negation but
    because it is a literal 30,317-post trained tag string. Which is exactly
    why inventing `lipless` or `short pointy ears` could never have worked.
    The work is done in the POSITIVE; the negative is a backstop.
  * Model card: quality prepend "masterpiece, best quality, very aesthetic",
    template "1girl/1boy, character name, from what series, everything else in
    any order", and "optimized for Danbooru-style tags rather than natural
    language prompts."

NOT ADOPTED, AND WHY IT IS NAMED RATHER THAN QUIETLY SKIPPED. The card also
recommends CFG 5-7, steps under 30 and Euler a; this wedge runs 40 steps at
cfg 7.5 because THAT IS WHAT THE TILE ITSELF WAS RENDERED AT
(b19-sapgloss-s20260819), and matching the target's own sampler is worth more
here than matching the card. A sampler rung is a separate, later, one-variable
question and must not be mixed into a wording ladder.

=============================================================================
THE LADDER -- TWO AXES, NOT ONE, AND THEY ARE KEPT APART ON PURPOSE
=============================================================================
Everything is held constant: seed 20260820, checkpoint, 40 steps, cfg 7.5,
832x1216, the scene clause, the quality prepend and ONE shared negative.

  AXIS 0 -- THE CONTROL PAIR, and it turns the framing finding into a measured
  pair inside this batch instead of an argument from memory:
    v0  the canon string, CLOSE.  Predicted: an adult human male.
    v1  the canon string, WIDE.   Predicted: the tile creature.

  AXIS A -- THE SUBJECT TAG. Identical bodies, close framing, NO creature
  feature tags, so the only thing that moves is the count tag:
    v2  `1boy, ...`      the 2.1M-post human-male attractor, still present
    v3  `...`            no count tag at all
    v4  `1other, ...`    the 126k-post ambiguous-humanoid tag

  AXIS B -- THE FEATURE CLAUSES, all built on the `1other` base so the ladder
  is monotone, one tile attribute added per rung:
    v5  + EYES   blank eyes, tsurime, jitome
    v6  + FACE   no nose, closed mouth, :|, expressionless
    v7  + SKIN   two-tone skin, shiny skin, no eyebrows   <- the full recipe

ONE SAMPLE BEFORE ANY BATCH IS SATISFIED, and here is the argument, because this
looks like eight renders and the rule says one. The rule is one sample per
RECIPE CHANGE and what it forbids is scaling an unapproved recipe across a set
of beats -- "the K recipe ... rendered across all fifteen beats". This is the
opposite shape: eight DIFFERENT recipes, ONE sample each, ONE beat, no beat
rendered twice, nothing promoted. It is the shape of the canaries that rule
blesses by name, the step sweep and the shake A/B.

WHAT IS DELIBERATELY NOT HERE: no LoRA, no IP-Adapter, no ControlNet, no
reference set, no init image, no second seed, no beat but 04. The
`--control`/`--control-sha256`/`--scale` flags are carried byte-identical from
the parent and are INERT on `--arm nocontrol` (controlnet_plate.py:592 -- every
use is inside `if use_cn:`), kept rather than deleted so the derivation stays
one-variable against its parent.

Usage:  python3 pipeline/derive_b04_tileread_0820.py [--write]
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import sd_prompt  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b02-adultplate-s20260820-0820.yaml"
PARENT_DIR_TOKEN = "b02adultplate-s20260820-0820"
PARENT_ID_TOKEN = "ep2-b02-adultplate-s20260820-0820"
SEED = 20260820

HEAD = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                      capture_output=True, text=True).stdout.strip()

# ---------------------------------------------------------------- the wedge --
QUALITY = "masterpiece, best quality, very aesthetic"
SCENE_CLOSE = "in tall grass, close-up, portrait"
SCENE_WIDE = "in tall grass, wide shot, full body"

# ONE negative for all eight, and it is SHORT BECAUSE RUN 1 WAS REFUSED AND THE
# REFUSAL WAS RIGHT. Run 1 (2026-08-20 17:48Z) filed a 45-term negative; all
# eight jobs exited rc=9 in four seconds each, $0, no weights loaded:
#     "!! the negative runs 49 tokens past CLIP's 77 and diffusers would
#      TRUNCATE it silently. The tail of every draft in this repo is the style
#      anchor, so what gets dropped is exactly what makes the plate look like
#      the show."
# 126 tokens against a 77 limit. Silent truncation would have dropped the back
# half -- the man-read suppressors, the whole point -- and eight pictures would
# have come back looking like a real answer. Every string here is now sized with
# sd_prompt.negative_tokens(), which the box measured as ~10% CONSERVATIVE
# against the real CLIP tokenizer (est 75 where the box counted 68), and this
# file refuses to write a spec whose strings do not fit.
#
# `goblin` IS NOT IN THIS NEGATIVE even though the tag fights us, because it is
# in v0's positive and negating a word the positive is simultaneously producing
# is the mutual-neutralisation failure Ban et al. describe. It is handled by
# ABSENCE from v2 upward instead.
NEGATIVE = (
    "lowres, worst quality, low quality, text, watermark, pointy ears, "
    "long pointy ears, elf, monster boy, pointy nose, dot nose, human face, "
    "wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi, "
    "grey skin, pale skin, 2boys"
)

CANON_STRING = ("1boy, solo, lean wiry adult goblin man, green skin, "
                "bald head, patchwork cloak")
BODY = "solo, colored skin, green skin, bald, patchwork cloak"
EYES = "blank eyes, tsurime, jitome"
FACE = "no nose, closed mouth, :|, expressionless"
SKIN = "two-tone skin, shiny skin, no eyebrows"

RUNGS = [
    ("v0", "AXIS 0 CONTROL, CLOSE - the canon string at the hard framing",
     CANON_STRING, SCENE_CLOSE),
    ("v1", "AXIS 0 CONTROL, WIDE - the same string at the framing that works",
     CANON_STRING, SCENE_WIDE),
    ("v2", "AXIS A - subject tag `1boy`, no creature feature tags",
     "1boy, " + BODY, SCENE_CLOSE),
    ("v3", "AXIS A - NO subject tag at all, no creature feature tags",
     BODY, SCENE_CLOSE),
    ("v4", "AXIS A - subject tag `1other`, no creature feature tags",
     "1other, " + BODY, SCENE_CLOSE),
    ("v5", "AXIS B - + EYES (blank eyes / tsurime / jitome)",
     "1other, " + BODY + ", " + EYES, SCENE_CLOSE),
    ("v6", "AXIS B - + FACE (no nose / closed mouth / :| / expressionless)",
     "1other, " + BODY + ", " + EYES + ", " + FACE, SCENE_CLOSE),
    ("v7", "AXIS B - + SKIN (two-tone / shiny / no eyebrows) - the full recipe",
     "1other, " + BODY + ", " + EYES + ", " + FACE + ", " + SKIN, SCENE_CLOSE),
]

BAR = """PRE-REGISTERED BEFORE THE RENDER, read at 1:1 beside
review/ep2-goblin-design-0819/adult-b19-0819.jpg. Six clauses, and the first
four are what "the creature, not a man" means:
  T1 EYES      blank white, no iris and no pupil drawn, narrow and upslanting.
  T2 NOSE      no bridge, no tip, no drawn nostrils.
  T3 AGE       no brow furrows, no nasolabial folds, no jowls. A smooth mask.
  T4 EARS      ear length under about a third of head height, low and swept
               back. LONG TAPERING SPIKES ARE A FAIL on this clause even though
               four beats in the shipping cut have them. NOTE, because it
               changes how this clause should be read: Danbooru has NO tag for
               the tile's ear, so no rung can ask for it -- T4 measures whether
               omitting every ear tag plus negating the spike tags is enough.
  T5 SKULL     large smooth dome; no neck reading as a distinct cylinder.
               `no neck` has 36 posts, i.e. is untrained, so this is likewise
               unaskable and only observable.
  T6 COLOUR    two-tone, crown lighter than the muzzle.
PASS = the FIRST rung that takes T1-T4 at the close framing. T5/T6 reported.
NOT A CLAUSE, and stated so nobody scores it: whether the resulting creature is
GOOD. That is R4 and it is the founder's. This measures fidelity to a picture he
has already ruled, which is a comparison anyone can check."""

PREDICTED = """v0 FAILS T1-T3 -- an adult human male face, which is the defect
as it ships. v1 PASSES T1-T3 on framing alone; if it does not, the framing
finding is wrong and that is the most valuable single result in the batch.
AXIS A is the one nobody can predict from a source: no published work says what
`1boy` present / absent / `1other` does to species in this model family, and
`1boy` is the largest single attractor in the prompt at 2.1M posts. My inference,
flagged as inference, is that DROPPING it (v3) beats substituting it (v4).
THE HIGHEST-YIELD SINGLE FEATURE RUNG IS PREDICTED TO BE v5 (the eyes), because
a blank-eyed face reads non-human before any other feature is parsed, and
`blank eyes` is the one tag in this whole vocabulary that means exactly what the
tile shows.
THE MOST LIKELY WAY THE WHOLE LADDER FAILS, written down so a failure cannot be
re-narrated afterwards: every rung comes back a human face wearing the tags as
SURFACE DECORATION -- blank contact lenses on human anatomy, green paint on a
human skull -- because `colored skin` and `blank eyes` are attributes the model
has only ever seen ON humanoid faces. T4 is the clause most likely to fail
everywhere, since no rung is even able to ask for the right ear. If eight rungs
show that, THE WORDING ROUTE FOR THE CLOSE-UP IS CLOSED and the answer is a
reference route -- a LoRA trained on tile-faithful frames, or IP-Adapter off the
tile itself -- which is a larger, slower instrument and should not have been
reached for first."""

RESEARCH = """OUTSIDE RESEARCH, 2026-08-20, and it overturned this wedge's first
draft rather than confirming it. animagine-xl-3.1 model card + Danbooru tag
database (counts via safebooru.donmai.us/tags.json). What it changed:
  * `blank eyes` (18,467) is the tile's eye exactly -- "missing both the irises
    and pupils; only the sclera are present". `no pupils` KEEPS THE IRIS and
    `white eyes` keeps iris AND pupil; both were in draft 1 and both are wrong.
  * `tsurime` (64,520) + `jitome` (49,408) are the eye SHAPE, which draft 1 had
    no tags for at all.
  * `lipless mouth`, `flat mouth`, `straight mouth` DO NOT EXIST. `:|` (14,379)
    is the only real tag for the tile's single thin line.
  * THERE IS NO TAG FOR THE TILE'S EAR. `short pointy ears` = 0 posts,
    `round ears` absent, `long ears` is an ALIAS TO `pointy ears`. The only
    sourced lever is naming no ear tag and negating the spikes.
  * `smooth skin` = 0 posts (untrained). `shiny skin` 156,330 and
    `two-tone skin` 18,474 are real; two-tone IS the tile's gradient.
  * `goblin` (4,326) FIGHTS US -- its own wiki defines "pointy noses and ears".
    `monster boy` is worse: "a human face and torso". Both are out of the
    positive from v2 up; `monster boy` is in the negative.
  * `1other` (126,608) is GENDER-ambiguity, not species, at 6% of `1boy`'s
    2,100,960. Nobody has published what the swap does, so all three are sampled.
  * Ban et al. ECCV 2024 (arXiv:2406.02965): a negative acts only after the
    positive renders the thing, and applying one too early SUMMONS it.
    Alhamoud et al. CVPR 2025 (NegBench): CLIP barely parses "no"/"not". So
    `no nose` works as a TRAINED TAG STRING, not as a negation -- which is
    precisely why inventing `lipless` could never have worked, and why the work
    here is in the positive with the negative as a backstop.
NOT ADOPTED AND NAMED: the card recommends CFG 5-7, steps <30, Euler a. This
wedge runs 40 steps at cfg 7.5 because that is what the TILE was rendered at
(b19-sapgloss-s20260819). Matching the target's own sampler beats matching the
card here, and a sampler rung is a separate one-variable question."""


def main() -> int:
    write = "--write" in sys.argv
    limit_hit = []
    for tag, headline, identity, scene in RUNGS:
        token = "b04tileread-%s-0820" % tag
        new_id = "ep2-b04-tileread-%s-0820" % tag
        prompt = "%s, %s, %s" % (QUALITY, identity, scene)
        # THE GUARD THAT RUN 1 DID NOT HAVE. Refuse to author a spec whose
        # strings the box will reject; four seconds each is cheap but eight
        # refusals for one arithmetic mistake is not a thing to do twice.
        for what, text in (("prompt", prompt), ("negative", NEGATIVE)):
            n = sd_prompt.negative_tokens(text)
            if n > 77:
                limit_hit.append("%s %s = %d tokens (est, conservative)"
                                 % (tag, what, n))
        child = derive_spec.derive(
            PARENT,
            new_id,
            fresh={
                "owner": "goblin-design audit lane, 2026-08-20 night",
                "consumer": (
                    "THE RECIPE, NOT THE BEAT. The seven-beat design wave "
                    "(02 03 04 07 08 13 20) cannot be authored until a wording "
                    "puts the B tile's creature on the canvas at a CLOSE-UP on "
                    "purpose. This rung is one sample of one candidate wording; "
                    "beat 04's framing is the test bed because it is the "
                    "tightest crop in the cut and therefore the hardest case. "
                    "No beat is re-rendered by this job and nothing is "
                    "promoted anywhere."),
                "success": (
                    "ONE 832x1216 png for rung %s (%s). Identity clause: %r. "
                    "Everything else is identical across all eight rungs -- "
                    "seed %d, one shared negative, one scene clause, one "
                    "quality prepend, same sampler numbers. Judged against the "
                    "six-clause tile bar pre-registered in this spec BEFORE "
                    "the render existed."
                    % (tag, headline, identity, SEED)),
                "why": (
                    "RUNG %s OF AN EIGHT-RUNG TILE-READ WEDGE. %s. The founder "
                    "ruled 2026-08-20 night that the goblin must read as the B "
                    "tile's CREATURE and that `adult` in canon was steward "
                    "drift. Beat 19 IS that tile and beat 15 is the next-best "
                    "match in the cut, and BOTH came off the same man-read "
                    "string -- wide, with `close-up` negated -- so framing, not "
                    "wording, is what separates the creature from the man "
                    "today. A recipe that only works at distance is an "
                    "avoidance, so this ladder asks what the positive clause is "
                    "worth AT THE CLOSE-UP. Every tag in it is a Danbooru tag "
                    "with a post count behind it; the ones this lane invented "
                    "on the first pass are listed in `outside_research` with "
                    "why they cannot work." % (tag, headline)),
            },
            overrides={
                "argv:--seed": str(SEED),
                "argv:--repo-commit": HEAD,
                "payload:prompt.txt": prompt,
                "payload:negative.txt": NEGATIVE,
            },
            retoken=[(PARENT_DIR_TOKEN, token),
                     (PARENT_ID_TOKEN, new_id)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "outside_research": RESEARCH,
                "init_provenance": (
                    "NONE, and that is the design. No init image, no mask, no "
                    "IP-Adapter, no reference set, no control hint: txt2img, so "
                    "the only thing on the canvas is what the wording put "
                    "there. --control/--control-sha256/--scale are carried "
                    "byte-identical from the parent and are INERT on "
                    "--arm nocontrol (controlnet_plate.py:592 -- every use is "
                    "inside `if use_cn:`), kept rather than deleted so the "
                    "derivation stays one-variable against its parent."),
                "the_one_variable": (
                    "Seed, checkpoint, steps, cfg, size, scene clause, quality "
                    "prepend and the whole negative are identical in all eight. "
                    "v0/v1 move FRAMING and nothing else. v2/v3/v4 move the "
                    "SUBJECT TAG and nothing else. v5/v6/v7 add one feature "
                    "clause each to the v4 base. Two axes, kept apart."),
                "one_sample_rule": (
                    "SATISFIED. The 2026-08-03 rule is one sample per RECIPE "
                    "CHANGE and forbids scaling an unapproved recipe across a "
                    "set of beats. This is eight DIFFERENT recipes at ONE "
                    "sample each, on ONE beat, nothing promoted -- the shape of "
                    "the step sweep and the shake A/B, not the shape of K."),
                "run_1_was_refused_and_the_refusal_was_right": (
                    "The first filing of these eight (2026-08-20 17:48Z) died "
                    "rc=9 in four seconds each, $0, no weights loaded: the "
                    "shared negative ran 126 tokens against CLIP's 77 and the "
                    "driver refused rather than let diffusers truncate it "
                    "silently. Truncation would have dropped the back half -- "
                    "the man-read suppressors, the whole point -- and eight "
                    "pictures would have come back looking like an answer. "
                    "This deriver now refuses to author a spec whose strings "
                    "do not fit."),
            },
            by="pipeline/derive_b04_tileread_0820.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write and not limit_hit:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-28s %3d tok  %s" % (new_id, sd_prompt.negative_tokens(prompt),
                                     "written" if (write and not limit_hit)
                                     else "(dry)"))
        print("    %s" % prompt)
    print("\nnegative (%d tok est): %s" % (sd_prompt.negative_tokens(NEGATIVE),
                                           NEGATIVE))
    if limit_hit:
        print("\n!! REFUSING TO WRITE -- these run past CLIP's 77:")
        for row in limit_hit:
            print("   " + row)
        return 1
    if not write:
        print("\n-- dry run. re-run with --write to author 8 specs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
