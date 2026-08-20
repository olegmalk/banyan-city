import os, sys
sys.path.insert(0, "/Users/artovonkugler/banyan-city/pipeline")
import derive_fetch_guard, derive_spec
import derive_jerry_skel_0820 as skel

REPO = "/Users/artovonkugler/banyan-city"
HINT = "jerry-skel-h19-0820"
TILE = ("1boy, solo, lean wiry adult goblin man, green skin, bald head, "
        "patchwork cloak")
NEG = skel.NEG.replace(", grey skin, pale skin, 2boys", ", grey skin, pale skin")

RUNGS = [
    ("f4", TILE + ", blank eyes",
     "f3's wording PLUS `blank eyes`, and nothing else. f3 drew a real face -- "
     "mouth, ears, shading, modelling -- on a lean 6-head body, and failed T1 "
     "on drawn pupils and T2 on a small nose. `blank eyes` is the single tag "
     "the wedge measured as 'the whole game' for T1, and this asks whether it "
     "can be added to a wording that draws a face without collapsing it back "
     "into a mask."),
    ("f5", TILE + ", blank eyes, no nose",
     "f4 PLUS `no nose`, and nothing else. The wedge's second half. If f4 keeps "
     "the face and fixes the eyes, this is the rung that decides whether the "
     "nose tag is what flattens everything or whether the collapse needed all "
     "four subtractive tags together."),
]

for suffix, core, variable in RUNGS:
    new_id = "ep2-jerry-face-%s-0820" % suffix
    job_dir = "jerryface-%s-0820" % suffix
    prompt = "%s, %s, %s" % (skel.QUALITY, core, skel.POSE_STAND)
    child = derive_spec.derive(
        src=skel.PARENT, new_id=new_id,
        fresh={
            "owner": "goblin reference-route lane, 2026-08-20 night",
            "why": ("RUNG %s: %s\nf1 (drop `thick eyebrows`) and f2 (`no nose` "
                    "-> `snout`) both came back the SAME BLANK EGG as n1 -- one "
                    "tag cannot reach the face at this framing. f3, the struck "
                    "tile wording at the same skeleton, came back with a mouth, "
                    "ear flanges, facial shading and a lean 6-head body, and "
                    "failed T1 and T2 on drawn pupils and a small nose. So the "
                    "face IS reachable at full body and the subtractive recipe "
                    "is what flattens it. This walks the two clauses that "
                    "matter back in, one at a time, onto the wording that "
                    "works." % (suffix, variable)),
            "consumer": ("THE JERRY LoRA SET, HELD. A frame that passes T1-T3 "
                         "and T8 with a face on it is the first trainable "
                         "full-body frame this project has produced; the "
                         "close mac plates carry the face and no reliable "
                         "proportion, and the reference-route frames so far "
                         "carry the proportion and no face. No beat plate."),
            "success": ("ONE 832x1216 png at seed %d on the h19 skeleton at "
                        "scale 1.0 with %s Scored on T1 (blank eyes), T2 (no "
                        "human nose), T3 (no age modelling), T8 (4.5+ heads) "
                        "AND on P1-P4 -- brow, muzzle, mouth, shading. This is "
                        "the first rung where a frame can pass both halves."
                        % (skel.SEED, variable)),
        },
        overrides={
            "seed": skel.SEED, "argv:--scale": "1.0",
            "argv:--control-sha256": skel.HINT_SHA[HINT],
            "argv:--repo-commit": skel.ASSET_COMMIT,
            "payload:prompt.txt": prompt, "payload:negative.txt": NEG,
            "key:beat": 2, "key:priority": 28, "key:est_minutes": 3,
        },
        retoken=[(skel.PARENT_DIR_TOKEN, job_dir), (skel.PARENT_HINT_TOKEN, HINT)],
        extra={
            "bar": ("BOTH HALVES, and this is the first rung that can pass "
                    "both.\nPRESENCES: P1 brow bar, P2 forward muzzle, P3 a "
                    "mouth line, P4 facial shading. f3 scored 2 of 4; n1, f1 "
                    "and f2 scored 0 of 4.\nABSENCES: T1 no iris and no pupil "
                    "-- f3's hard fail. T2 no human nose bridge, tip or "
                    "nostrils -- f3's second fail. T3 no age modelling. T8 4.5 "
                    "heads or better.\nPASS is 2 of 4 presences with T1, T2, T3 "
                    "and T8 all intact. Nothing has ever scored that."),
            "the_one_variable": variable,
            "the_rung_this_is_one_variable_from":
                ("ep2-jerry-face-f3-0820" if suffix == "f4"
                 else "ep2-jerry-face-f4-0820"),
            "failure_predicted_in_advance": (
                "THE THING I EXPECT AND DO NOT WANT: `blank eyes` is a strong "
                "attractor and may drag the whole face back to the mask rather "
                "than only the eyes -- the wedge's own finding was that it is "
                "'the whole game', and a tag that decides a face is a tag that "
                "can flatten one. If f4 returns the egg, the reading is that "
                "the subtractive tags are not additive with a descriptive "
                "wording and the two dialects cannot be mixed; the route then "
                "is IP-ADAPTER off the tile for the FACE over an openpose "
                "skeleton for the BODY -- attribute instrument and geometry "
                "instrument each doing the job the record says it does, which "
                "is where Sec 11 and Sec 13 pointed all along.\nf5 IS THE "
                "RISKIER OF THE TWO and is filed anyway because if f4 works and "
                "f5 does not, that isolates `no nose` as the flattener, which "
                "is worth a rung."),
            "one_sample_rule": (
                "Two rungs, one variable each, ~20 s a render, on a card whose "
                "queue this lane is already feeding. Round 2 of 2 on the "
                "face-at-full-body question; if neither passes, the stop gets "
                "written and training stays held rather than forced."),
        },
        by="pipeline/derive_jerry_face_fullbody_0820.py (f4/f5 addendum)",
    )
    child["steps"] = [{
        "name": "stage",
        "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                 skel.stage_step(job_dir, HINT)],
    }] + list(child["steps"])
    out = "pipeline/jobs/%s.yaml" % new_id
    derive_spec.write(child, out)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out), must_hold=("controlnet_plate.py", HINT + ".png"))
    print("wrote", out)
