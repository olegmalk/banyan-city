#!/usr/bin/env python3
r"""THE RECIPE HOLDS THE FACE AND LOSES THE BODY. Three rungs on proportion.

WHAT THE TWELVE-POSE SET SHOWED, and it is not what was predicted. All twelve
`ep2-jerry-tileset-p01..p12-0820` came back CONSISTENT and tile-faithful ON THE
FACE -- blank white eyes, no nose, no eyebrows, bald dome, green, twelve for
twelve. And all twelve are BOBBLEHEADS. The head runs roughly a THIRD of the
figure's height where the tile's is a FIFTH to a SIXTH; the limbs are stubby;
p04 and p05 standing are unmistakably three-heads-tall, and p07 is a chibi
holding an apple. The B tile is a LEAN, FOLDED, ADULT-PROPORTIONED creature.

SO THE SET IS NOT TRAINABLE AND train-jerry STAYS HELD. Training on these
teaches a bobblehead, which is the founder's child complaint returning through a
different door: he ruled against the round young one on 08-19 and against the
adult man on 08-20, and a mascot is neither of the things he asked for.

WHY THE WEDGE DID NOT CATCH IT, said plainly because it is the methodological
lesson: THE WEDGE WAS FOUGHT AT A CLOSE-UP, ON PURPOSE, because that is where
the man-read lived -- and a close-up has no body in it. v6 and w2 were scored on
a face. The bar had seven clauses and every one of them is above the neck. A bar
inherits the blind spot of the failure that motivated it.

  >> T8 IS ADDED TO THE TILE BAR AND IT IS NOT OPTIONAL:
  >> HEAD-TO-BODY. The head is a FIFTH to a SIXTH of standing height, not a
  >> third. Limbs are lean and long, not stubby. Any frame with a body in it is
  >> scored on this, and the twelve-pose set is scored RETROSPECTIVELY: all
  >> twelve FAIL T8.

THE HYPOTHESIS, and q3 is the one that would embarrass me most and is therefore
the one most worth running. Tonight's wedge concluded "AXIS A IS A DEAD LEVER"
-- `1boy` / no count tag / `1other` all drew the same human FACE. That
conclusion was drawn entirely from close-ups. `1boy` is a 2,100,960-post
attractor for HUMAN MALE ANATOMY, and anatomy is mostly body. Dropping it may be
exactly why the face got better and the body got worse: we removed the human
prior and the model fell into the nearest remaining basin for a big-headed
noseless green creature, which is MASCOT. If q3 restores adult proportion
without breaking the face, then "dead lever" was a close-up artefact and the
correct reading is that the count tag governs the BODY and the feature tags
govern the FACE.

  q1  NEGATIVE gains `super deformed, mini person, doll, mascot`.
      `super_deformed` is the actual Danbooru tag for this exact defect, which
      makes it the one honest suppression attempt. But w1 already showed a
      negative cannot undo what the positive asks for, and nothing in the
      positive asks for a mascot -- so this is the weakest of the three and is
      run to find out whether the basin is reachable by suppression at all.
  q2  POSITIVE gains `long legs, narrow waist`. Real tags, and the closest
      Danbooru comes to naming lean adult proportion.
  q3  `1other` -> `1boy`, and NOTHING ELSE. The one that tests the conclusion
      this lane published four commits ago.

One variable each, one seed, p04's standing pose held constant because a
standing full body is the only framing where head-to-body can be read at all.
"""

from __future__ import annotations
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec, sd_prompt  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-jerry-tileset-p04-0820.yaml"
PARENT_DIR_TOKEN = "jerrytile-p04-0820"
PARENT_ID_TOKEN = "ep2-jerry-tileset-p04-0820"
SEED = 20260823

QUALITY = "masterpiece, best quality, very aesthetic"
CORE = ("1other, solo, colored skin, green skin, bald, patchwork cloak, "
        "blank eyes, tsurime, jitome, no nose, closed mouth, :|, expressionless")
POSE = "standing, arms at sides, in tall grass, full body"
NEG = ("lowres, worst quality, low quality, text, watermark, pointy ears, "
       "long pointy ears, elf, monster boy, pointy nose, dot nose, human face, "
       "wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi, "
       "grey skin, pale skin, 2boys")

RUNGS = [
    # q1's negative is p04's MINUS `dot nose` and `pointy nose` PLUS
    # `super deformed, mascot`, and the trade is named rather than hidden:
    # plus-four measured 80 tokens against CLIP's 77. The two nose backstops are
    # what is given up because the recipe already draws NO nose at all in twelve
    # of twelve frames, so they were suppressing nothing. `mini person` and
    # `doll` are dropped for the same budget; `super deformed` is the actual
    # Danbooru tag for this defect and is the one that had to survive.
    ("q1", "negative gains super deformed / mascot",
     CORE, NEG.replace(", dot nose", "").replace(", pointy nose", "")
     + ", super deformed, mascot"),
    ("q2", "positive gains long legs / narrow waist",
     CORE + ", long legs, narrow waist", NEG),
    ("q3", "`1other` -> `1boy`, and nothing else",
     CORE.replace("1other", "1boy"), NEG),
]

BAR = """T8 IS THE ONLY SCORED CLAUSE HERE AND IT IS NEW:
  T8 HEAD-TO-BODY. Standing height divided by head height. The B tile reads 5-6;
     the twelve-pose set reads about 3. PASS is 4.5 or better BY EYE against
     adult-b19-0819.jpg, with lean limbs rather than stubby ones.
T1-T3 and T7 are REGRESSION CLAUSES: blank eyes, no nose, no age modelling, no
patchwork on the skull. A rung that fixes the body and breaks the face is a
FAIL, and it is the most likely way each of these three goes wrong.
T4 (ears) is unscorable at full body and is not scored.
T6 remains STRUCK."""

PREDICTED = """q3 WINS AND IT COSTS ME A PUBLISHED CONCLUSION. Four commits ago
this lane wrote "AXIS A IS A DEAD LEVER" off the wedge, and that was measured
entirely on close-ups, where there is no body to be wrong. If restoring `1boy`
restores adult proportion, the honest correction is that the count tag governs
the BODY and the feature tags govern the FACE, and the wedge simply never had a
body in frame to notice with.
q1 FAILS on the mechanism w1 already demonstrated: nothing in the positive asks
for a mascot, so there is nothing for the negative to cancel; per Ban et al. a
negative acts on what the positive draws, and this basin is arrived at by the
ABSENCE of a human prior rather than by any word.
q2 IS THE COIN FLIP. `long legs` is a real tag with real mass, but it describes
a proportion within a body rather than the body's relation to the head, so it
may lengthen the legs of a bobblehead and produce something worse than either.
IF ALL THREE FAIL, the wording route is finished for the BODY exactly as it
succeeded for the face, and the answer is a reference route -- IP-Adapter or
ControlNet off the tile's own silhouette, which supplies proportion as geometry
instead of asking for it as a word."""


def patch_publish(child):
    for step in child.get("steps") or []:
        step["argv"] = [a.replace("-hintskel.png", "-nocontrol.png")
                        if isinstance(a, str) else a for a in step.get("argv") or []]
    child["artifacts"] = [a.replace("-hintskel.png", "-nocontrol.png")
                          if isinstance(a, str) else a for a in child.get("artifacts") or []]
    return child


def main() -> int:
    write = "--write" in sys.argv
    base_prompt = "%s, %s, %s" % (QUALITY, CORE, POSE)
    for tag, headline, core, neg in RUNGS:
        token = "jerryprop-%s-0820" % tag
        new_id = "ep2-jerry-prop-%s-0820" % tag
        prompt = "%s, %s, %s" % (QUALITY, core, POSE)
        n = sd_prompt.negative_tokens(prompt)
        nn = sd_prompt.negative_tokens(neg)
        if n > 77 or nn > 77:
            print("!! %s past 77: prompt=%d neg=%d" % (tag, n, nn)); return 1
        ov = [("argv:--seed", str(SEED))]
        if prompt != base_prompt:
            ov.append(("payload:prompt.txt", prompt))
        if neg != NEG:
            ov.append(("payload:negative.txt", neg))
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "goblin-design audit lane, 2026-08-20 night",
                "consumer": (
                    "THE JERRY LoRA SET, WHICH IS CURRENTLY UNTRAINABLE. All "
                    "twelve tile-set poses hold the face and every one is a "
                    "BOBBLEHEAD -- head about a third of standing height where "
                    "the B tile is a fifth to a sixth. Training on them teaches "
                    "a mascot, which is the founder's child complaint arriving "
                    "through a different door. This rung is one candidate fix "
                    "for the body. No beat plate, nothing promoted."),
                "success": (
                    "ONE 832x1216 png of the standing pose at seed %d with ONE "
                    "change from the twelve-pose recipe: %s. Scored on T8 "
                    "(head-to-body) with T1-T3 and T7 as regression clauses."
                    % (SEED, headline)),
                "why": (
                    "RUNG %s: %s. THE WEDGE WAS FOUGHT AT A CLOSE-UP because "
                    "that is where the man-read lived, and a close-up has no "
                    "body in it -- every one of the tile bar's seven clauses is "
                    "above the neck. A bar inherits the blind spot of the "
                    "failure that motivated it, and this is that blind spot "
                    "being closed. T8 is added to the bar and the twelve-pose "
                    "set is scored retrospectively: all twelve FAIL it."
                    % (tag, headline)),
            },
            overrides=dict(ov),
            retoken=[(PARENT_DIR_TOKEN, token), (PARENT_ID_TOKEN, new_id)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "the_one_variable": (
                    "p04's exact prompt, negative, seed and sampler with ONE "
                    "change: q1 the negative, q2 two positive tags, q3 the "
                    "count tag alone."),
                "this_rung_tests_a_conclusion_this_lane_published": (
                    "q3 in particular. Commit `the ladder gets the recipe, the "
                    "dead lever...` states AXIS A IS A DEAD LEVER on the "
                    "strength of v2/v3/v4, all of which were close-ups with no "
                    "body in frame. If q3 restores proportion, that conclusion "
                    "is wrong as stated and the correction is that the count "
                    "tag governs the BODY while the feature tags govern the "
                    "FACE."),
            },
            by="pipeline/derive_jerry_proportion_0820.py",
        )
        child = patch_publish(child)
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-26s p=%d n=%d %s" % (new_id, n, nn, "written" if write else "(dry)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
