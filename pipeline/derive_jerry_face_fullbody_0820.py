#!/usr/bin/env python3
r"""THE BODY IS RIGHT AND THE FACE WENT BLANK. Three rungs, read at 1:1.

WHAT THE 1:1 CROP SHOWED THAT THE CONTACT SHEET DID NOT. n1 passes T8 at 5.07
heads and passes T1, T2, T3 and T7 as written -- and its face, cropped and
enlarged beside the tile's, is a FEATURELESS EGG: two vertical black bars on a
smooth green oval, no brow, no muzzle, no mouth, no ear, no shading. The tile
has a heavy dark brow bar, a forward muzzle, a wide thin lipless line, low ear
flanges and two-tone modelling. Every clause in the bar passed and the face is
still not the tile's, which means the bar is scoring ABSENCES and the tile is
made of PRESENCES.

  >> THE RECIPE IS FRAMING-DEPENDENT IN THE OTHER DIRECTION TOO. canon already
  >> records that `patchwork` paints the skull at close-up and lands on cloth at
  >> full body. This is the same axis running the other way: the face wording is
  >> SUBTRACTIVE -- `blank eyes, no nose, closed mouth, expressionless` plus a
  >> negative carrying `thick eyebrows` -- and at a close-up subtraction removes
  >> the HUMAN features and leaves a creature, while at full body it removes
  >> everything and leaves a mask.

AND THE NEGATIVE IS SUPPRESSING THE TILE'S SECOND-LOUDEST FEATURE. canon's own
tile read says the eyes sit "under one heavy dark brow bar". `thick eyebrows` is
in the negative of every rung this lane has fired, inherited from the wedge,
where it was there to kill a human male's brows. At full body it is deleting the
brow bar the tile actually has.

WHY THIS MATTERS TONIGHT AND IS NOT A NICETY: these frames are for the LoRA, and
a character LoRA learns what it is shown. Six more poses of a blank egg would
teach the trigger token a blank egg exactly as twelve bobbleheads would have
taught it a mascot. The pose batch is already on the card and is still worth its
seconds -- it answers whether proportion binds across poses -- but NOTHING from
either batch enters the training set until a face rung passes.

THE THREE RUNGS, one variable each, all off `ep2-jerry-skel-n1-0820`, the same
h19 skeleton at scale 1.0, the same seed:

  f1  NEGATIVE loses `thick eyebrows`, and nothing else. The cheapest and the
      best-argued: we are negating a feature canon says the tile has.
  f2  POSITIVE `no nose` -> `snout`, and nothing else. The tile has no HUMAN
      nose and it does have a forward muzzle; `no nose` asks for the absence
      where `snout` asks for the thing. A real Danbooru tag, unlike the ear.
  f3  THE TILE'S OWN PLATE WORDING at this skeleton -- `lean wiry adult goblin
      man, green skin, bald head, patchwork cloak`, the string canon struck as
      drift. IT IS ARGUED, NOT SMUGGLED: canon's own entry says the phrase is
      not what separates the tile from the man, FRAMING IS, and that this exact
      string at a wide full-body framing is what produced adult-b19-0819.jpg in
      the first place. The reason it was struck is that it drifts toward a human
      male BUILD at close range -- and the build is now set by geometry, not by
      the sentence, which is precisely the condition under which the objection
      does not apply. If f3 wins, the reading is that the subtractive tags are a
      CLOSE-UP instrument and the tile's own words are the full-body one.

  PRE-REGISTERED, and f3 is the one that would cost me something: this lane
  argued four commits ago that wording is closed for the body and geometry is
  the instrument. f3 puts the retired wording back in with the geometry holding
  the build. If it returns a lean 5-head figure WITH a modelled face, the
  honest correction is that `adult`/`man` were only ever dangerous while wording
  was carrying the build alone. If it returns a human male face on a lean body,
  the strike stands and is now tested rather than asserted.
  f1 I EXPECT TO HELP AND NOT TO BE ENOUGH -- one brow bar on a blank egg is
  still a blank egg. f2 IS THE COIN FLIP: `snout` has real mass but reads canine
  on most checkpoints, and a dog muzzle is a different failure from a mask.

    python3 pipeline/derive_jerry_face_fullbody_0820.py

$0. No model, no network, no GPU.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
import derive_jerry_skel_0820 as skel  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HINT = "jerry-skel-h19-0820"
POSE = skel.POSE_STAND

# f3's wording: the string that produced the tile, canon's `canon_wording`.
TILE_WORDING = ("1boy, solo, lean wiry adult goblin man, green skin, "
                "bald head, patchwork cloak")

RUNGS = [
    ("f1", skel.CORE, skel.NEG.replace(", thick eyebrows", ""),
     "the NEGATIVE loses `thick eyebrows`, and nothing else. canon's tile read "
     "says the eyes sit 'under one heavy dark brow bar'; the negative "
     "inherited from the close-up wedge has been deleting it."),
    ("f2", skel.CORE.replace("no nose", "snout"), skel.NEG,
     "the POSITIVE swaps `no nose` for `snout`, and nothing else. The tile has "
     "no HUMAN nose and does have a forward muzzle; one tag asks for an "
     "absence and the other asks for the thing."),
    ("f3", TILE_WORDING, skel.NEG.replace(", grey skin, pale skin, 2boys",
                                          ", grey skin, pale skin"),
     "THE TILE'S OWN PLATE WORDING, at the h19 skeleton. `2boys` leaves the "
     "negative because `1boy` is now in the positive and negating the plural "
     "against a singular count tag was a wedge-era backstop. Everything else "
     "-- skeleton, scale, seed, framing -- is n1's."),
]

BAR = """SCORED ON PRESENCES, WHICH IS WHAT THE OLD BAR WAS MISSING.
  P1 BROW. A dark brow bar over the eyes, as in the tile. Absent in n1.
  P2 MUZZLE. The lower face reads forward and modelled, not flat. Absent in n1.
  P3 MOUTH. A line, however thin. Absent in n1 -- not thin, ABSENT.
  P4 SHADING. Any tonal modelling on the face at all. Absent in n1.
REGRESSION CLAUSES, and any one of them fails the rung outright:
  T1 no iris and no pupil.  T2 no human nose bridge, tip or nostrils.
  T3 no age modelling -- no furrows, no folds, no jowls.
  T8 4.5 heads or better. The body is the thing that already works and a face
     rung that costs the body is not a trade, it is a loss.
A rung passes on 2 of 4 presences with every regression clause intact. This is
deliberately generous: the question tonight is whether the face is REACHABLE at
this framing at all, not which wording is best."""


def main():
    for suffix, core, neg, variable in RUNGS:
        new_id = "ep2-jerry-face-%s-0820" % suffix
        job_dir = "jerryface-%s-0820" % suffix
        prompt = "%s, %s, %s" % (skel.QUALITY, core, POSE)
        child = derive_spec.derive(
            src=skel.PARENT,
            new_id=new_id,
            fresh={
                "owner": "goblin reference-route lane, 2026-08-20 night",
                "why": ("RUNG %s: %s\nn1 passed T8 at 5.07 heads and passed "
                        "every face clause in the bar, and its face read at "
                        "1:1 beside the tile is a FEATURELESS EGG -- two black "
                        "bars on a smooth oval, no brow, no muzzle, no mouth, "
                        "no shading. The bar scores ABSENCES and the tile is "
                        "made of PRESENCES. The recipe is framing-dependent "
                        "the other way round: subtraction removes the human "
                        "features at a close-up and removes everything at full "
                        "body." % (suffix, variable)),
                "consumer": ("THE JERRY LoRA SET, WHICH STAYS HELD UNTIL ONE "
                             "OF THESE PASSES. The proportion problem is "
                             "solved and the frames that solve it are not "
                             "trainable: six more poses of a blank egg would "
                             "teach the trigger token a blank egg exactly as "
                             "twelve bobbleheads would have taught it a "
                             "mascot. No beat plate, nothing promoted."),
                "success": ("ONE 832x1216 png at seed %d on the h19 skeleton "
                            "at scale 1.0, differing from "
                            "ep2-jerry-skel-n1-0820 by %s Scored on P1-P4 "
                            "(brow, muzzle, mouth, shading) with T1, T2, T3 "
                            "and T8 as regression clauses."
                            % (skel.SEED, variable)),
            },
            overrides={
                "seed": skel.SEED,
                "argv:--scale": "1.0",
                "argv:--control-sha256": skel.HINT_SHA[HINT],
                "argv:--repo-commit": skel.ASSET_COMMIT,
                "payload:prompt.txt": prompt,
                "payload:negative.txt": neg,
                "key:beat": 2,
                "key:priority": 30,
                "key:est_minutes": 3,
            },
            retoken=[(skel.PARENT_DIR_TOKEN, job_dir),
                     (skel.PARENT_HINT_TOKEN, HINT)],
            extra={
                "bar": BAR,
                "the_one_variable": variable,
                "the_rung_this_is_one_variable_from": "ep2-jerry-skel-n1-0820",
                "failure_predicted_in_advance": (
                    "f1 HELPS AND IS NOT ENOUGH -- one brow bar on a blank egg "
                    "is still a blank egg. f2 IS THE COIN FLIP: `snout` has "
                    "real Danbooru mass but reads CANINE on most checkpoints, "
                    "and a dog muzzle is a different failure from a mask, not "
                    "a smaller one. f3 IS THE ONE THAT COSTS ME SOMETHING: it "
                    "puts back the wording this lane helped retire, on the "
                    "argument that the strike was about the BUILD and the "
                    "build is now geometry's job. If f3 returns a lean 5-head "
                    "figure with a modelled creature face, the correction is "
                    "that `adult`/`man` were only dangerous while wording "
                    "carried the build alone. If it returns a human male face, "
                    "the strike stands and is TESTED rather than asserted."),
                "one_sample_rule": (
                    "Three rungs on ONE question with one variable each, ~20 s "
                    "a render on a card already busy with another lane's work. "
                    "Nothing scales off these without an eye verdict at 1:1 "
                    "against adult-b19-0819.jpg -- which is the check that "
                    "caught this problem, since n1 passed every clause of the "
                    "written bar and is still not the tile."),
            },
            by="pipeline/derive_jerry_face_fullbody_0820.py",
        )
        child["steps"] = [{
            "name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                     skel.stage_step(job_dir, HINT)],
        }] + list(child["steps"])
        out = "pipeline/jobs/%s.yaml" % new_id
        derive_spec.write(child, out)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out),
            must_hold=("controlnet_plate.py", HINT + ".png"))
        print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
