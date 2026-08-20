#!/usr/bin/env python3
r"""THE POSE SET AT THE RATIFIED PROPORTION -- the LoRA's remaining gate.

WHAT LICENSES A SET HERE, because the standing rule is ONE SAMPLE BEFORE ANY
BATCH and this is a batch. The recipe change -- the ratified face wording plus a
COCO-18 skeleton authored at the tile's measured head_frac -- WAS sampled:
`ep2-jerry-skel-n1-0820` came back at about 5.3 heads with blank eyes, no nose
and no patchwork on the skull, and `ep2-jerry-skel-n5-0820`, the same scale,
seed and words over a 3.1-head skeleton, came back a BOBBLEHEAD. Two frames, one
variable between them, and the variable is geometry. The instrument is settled;
what is not settled is pose breadth, and pose breadth is the LoRA's gate.

WHY THE GATE IS BREADTH AND NOT A BETTER FACE. `pipeline/lora/curation-tile-0820.yaml`
left seven usable frames in FOUR poses (b14 kneel x2, b15 sit x2, b19 seat x3),
and the audit's own words are that a pose-locked character LoRA is worse than
none because it looks like it works on the beat it was trained on. Six poses at
the tile's proportion is the arithmetic that changes.

WHAT IS HELD, IN EVERY RUNG. The face wording, the negative and the seed are
byte-identical to `ep2-jerry-tileset-p04-0820`'s and therefore to n1's. The
conditioning scale is 1.0. `head_frac` is 0.190 in all six, and the five head
keypoints move as ONE RIGID BLOCK when a pose lowers them -- asserted in
`author_jerry_skel_0820 --selftest` and visible as an ear span of 136.0 px in
every pose. What moves per rung is the SKELETON and the two or three pose words
that describe it, and those move together because a kneeling skeleton under
`standing, arms at sides` is a contradiction rather than a control.

THESE ARE NOT BEAT PLATES. Nothing here is promoted to a cut. The consumer is
the training set and the gate on entry is an eye verdict against the tile.

    python3 pipeline/derive_jerry_poseset_0820.py

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
ASSET_COMMIT = "b889227bc1f0e7b96c271235de7bc61466438ae0"

# Each hint's sha, read off the published assets directory.
POSE_SHA = {
    "jerry-skel-h19kneel-0820":
        "96cf22c5fe60cee184de5b91bc04e83fdb599a714a1667f01cc49512acf163d4",
    "jerry-skel-h19sit-0820":
        "ce25c2f17bf158f650fc7f1a74fcacf32b9603ad74da9b4dd6ef85d00834f908",
    "jerry-skel-h19crouch-0820":
        "b3028a04ed18ed992cfa884900443d8ee547423e0dcfd72e42c4dfa52d2352fe",
    "jerry-skel-h19reach-0820":
        "fb22b82c713891ff875116cbc68649ac08c1f981fb57750f34289ff2aae1119f",
    "jerry-skel-h19point-0820":
        "1b0876d4eb8381c0052d2281a4fbe0319868f96faf626f62d8fa378083595d23",
    "jerry-skel-h19hunch-0820":
        "78422b89fa81d5d6fadc53fbf4a275e3d08c964f148f1cd2dd845a6fc90331f0",
}
skel.HINT_SHA.update(POSE_SHA)

RUNGS = [
    ("kneel", "jerry-skel-h19kneel-0820",
     "kneeling, in tall grass, full body"),
    ("sit", "jerry-skel-h19sit-0820",
     "sitting, hands on own knees, in tall grass, full body"),
    ("crouch", "jerry-skel-h19crouch-0820",
     "squatting, in tall grass, full body"),
    ("reach", "jerry-skel-h19reach-0820",
     "arms up, in tall grass, full body"),
    ("point", "jerry-skel-h19point-0820",
     "arm outstretched, pointing, in tall grass, full body"),
    ("hunch", "jerry-skel-h19hunch-0820",
     "standing, hunched over, arms at sides, in tall grass, full body"),
]

BAR = """EVERY FRAME IS SCORED FOR ENTRY TO THE TRAINING SET, not for a cut.
  T8 HEAD-TO-BODY. 4.5 heads or better BY EYE against adult-b19-0819.jpg, with
     lean limbs. n1 set the standard this batch is held to.
  T1 BLANK EYES -- no iris, no pupil, no lashes.
  T2 NO HUMAN NOSE -- no bridge, no tip, no drawn nostrils.
  T3 NO AGE MODELLING -- no brow furrows, no folds, no jowls.
  T7 NO PATCHWORK ON THE SKULL. The wedge measured `patchwork cloak` bleeding
     stitch marks onto the head in six of eight rungs; n1-n5 did not show it at
     full body and this batch is where that holds or does not.
  T9 THE POSE IS THE ONE ASKED FOR. A rung whose skeleton the net ignored is
     not a pose in the set, however good the figure is.
T4 (ears) is unscorable at full body and is not scored. T6 remains STRUCK.
A frame failing ANY clause is REJECTED from the set. The whole reason the old
31-frame set was untrainable is that near-misses were kept."""

PREDICTED = """THE UPRIGHT POSES LAND AND THE FOLDED ONES ARE THE RISK, and the
risk is specific: `sit` and `crouch` compress the skeleton into a third of the
canvas, so the head keypoints sit far from where a standing figure's would, and
Sec 13's measured binding was on two UPRIGHT figures. If the net treats a folded
skeleton as a small figure rather than a folded one, those two come back
correctly posed and BOBBLEHEADED -- which would say head-to-body binds through
the ratio the whole skeleton spans and not through the head keypoints alone.
That is worth knowing and is why they are in the batch rather than deferred.
`reach` AND `point` ARE THE SAFEST -- legs identical to n1's, arms the only
change. `hunch` IS THE ONE I EXPECT THE NET TO SOFTEN: it differs from n1 by a
quarter of a head height and 2% of stature, which may be under the net's
resolution, in which case it is a duplicate of n1 and not a pose.
IF FOUR OF SIX PASS, the set reaches six poses at the tile's proportion counting
n1 and the stride, and the LoRA's pose gate is discharged on arithmetic rather
than on hope."""


def main():
    written = []
    for suffix, hint, pose_words in RUNGS:
        new_id = "ep2-jerry-pose-%s-0820" % suffix
        job_dir = "jerrypose-%s-0820" % suffix
        child = derive_spec.derive(
            src=skel.PARENT,
            new_id=new_id,
            fresh={
                "owner": "goblin reference-route lane, 2026-08-20 night",
                "why": ("POSE %s of six, at the ratified proportion. n1 proved "
                        "the skeleton carries head-to-body and n5 -- the "
                        "3.1-head hint at the same scale, seed and words -- "
                        "proved it by coming back a bobblehead on purpose. "
                        "What is left before the Jerry LoRA can train is POSE "
                        "BREADTH: the curated set is seven frames in four "
                        "poses, and a pose-locked character LoRA is worse "
                        "than none. The skeleton and the pose words move "
                        "together here and that is the one variable."
                        % suffix),
                "consumer": ("THE JERRY LoRA TRAINING SET. A frame passing "
                             "every clause of the bar is added to "
                             "pipeline/lora/curation-tile-0820.yaml and its "
                             "caption written against canon's corrected tile "
                             "read; a frame failing any clause is rejected, "
                             "because keeping near-misses is exactly what "
                             "made the 31-frame set untrainable. No beat "
                             "plate, nothing promoted to a cut."),
                "success": ("ONE 832x1216 png at seed %d conditioned on "
                            "%s.png through "
                            "xinsir/controlnet-openpose-sdxl-1.0 at scale 1.0, "
                            "the face wording and negative byte-identical to "
                            "n1's, and the pose words '%s'. Scored on T1, T2, "
                            "T3, T7, T8 and T9; any failure rejects it from "
                            "the set." % (skel.SEED, hint, pose_words)),
            },
            overrides={
                "seed": skel.SEED,
                "argv:--scale": "1.0",
                "argv:--control-sha256": POSE_SHA[hint],
                "argv:--repo-commit": ASSET_COMMIT,
                "payload:prompt.txt": skel.prompt_for(pose_words),
                "payload:negative.txt": skel.NEG,
                "key:beat": 2,
                "key:priority": 34,
                "key:est_minutes": 3,
            },
            retoken=[(skel.PARENT_DIR_TOKEN, job_dir),
                     (skel.PARENT_HINT_TOKEN, hint)],
            extra={
                "bar": BAR,
                "the_one_variable": (
                    "the SKELETON and the pose words that describe it, moving "
                    "together: '%s'. Everything else -- the face wording, the "
                    "negative, the seed, the scale, head_frac and the five "
                    "head keypoints -- is byte-identical to "
                    "ep2-jerry-skel-n1-0820's." % pose_words),
                "the_rung_this_is_one_variable_from": "ep2-jerry-skel-n1-0820",
                "failure_predicted_in_advance": PREDICTED,
                "one_sample_rule": (
                    "DISCHARGED BY n1 AND n5, not waived. The recipe change "
                    "under test -- ratified face wording plus an openpose "
                    "skeleton at head_frac 0.190 -- was rendered as ONE sample "
                    "(n1) and judged by eye before this set was authored, and "
                    "n5 is the control that made that judgement a mechanism "
                    "instead of a seed. This batch varies the POSE, which is "
                    "the thing the sample could not vary."),
            },
            by="pipeline/derive_jerry_poseset_0820.py",
        )
        child["steps"] = [{
            "name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                     skel.stage_step(job_dir, hint)],
        }] + list(child["steps"])
        out = "pipeline/jobs/%s.yaml" % new_id
        derive_spec.write(child, out)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out),
            must_hold=("controlnet_plate.py", hint + ".png"))
        written.append(out)
        print("wrote %s" % out)
    print("\n%d spec(s)." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
