#!/usr/bin/env python3
r"""File the spec that OWNS farm-out/ep2-b09-platecrop-0820, so the refs guard resolves.

    python3 pipeline/derive_b09_platecrop_producer_0820.py

WHY THIS FILE EXISTS AND WHY IT IS NOT A WORKAROUND. `box_enqueue`'s refs check
traces a job's `--src` back to the job that DREW it, so it can look at the
reference set that plate was conditioned on and refuse a costume card. It
resolves `farm-out/<dir>/<file>` to "the spec NAMED <dir>, or the one spec whose
publish step writes into <dir>", and refuses if neither exists -- "could not
check is not fine". `ep2-b09-cropmotion-0820` hit exactly that refusal, because
its plate was produced by a CPU script on a Mac and no spec owned the directory
it was published into.

THE HONEST FIX IS TO MAKE THE PRODUCER EXIST, NOT TO WAIVE THE CHECK. The
alternative the refusal offers is `plate_ack: "unresolved: ..."`, and
`guards_CORRECTION_0816` forbids a plate_ack on this beat family by name. So the
directory gets the spec it should always have had.

IT IS DERIVED FROM `ep2-b09-cast-0817` BECAUSE THAT IS TRULY THE PARENT. The
crop's pixels are that job's pixels. A crop introduces no conditioning of its
own -- no model, no sampler, no reference image, no prompt -- so the reference
set that drew this plate IS `refs-guards-twoinfield-nos2-0815`, carried here
from the job that used it rather than re-asserted by hand. That is the whole
question the refs guard asks, and this spec answers it with the true answer.
(That set is not on `CARD_REFS_DENYLIST`, checked rather than assumed.)

WHAT IS OVERRIDDEN: `steps`, to the command that actually ran, and the runner
and its needs, because this job used no GPU, no CUDA and no farm venv. The
artifacts are the files that exist. NOTHING HERE IS A PLAN -- every step in it
has already executed and its outputs are on `origin/farm-results-rtx5090` with
a sha manifest. This spec is a RECORD, filed so the guard can read it.

IT IS NOT ENQUEUED AND MUST NOT BE. Nothing in pipeline/jobs runs by existing;
the box drains `backlog/` and `ready/`, which this never enters. $0.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec

PARENT = "pipeline/jobs/ep2-b09-cast-0817.yaml"
NEW_ID = "ep2-b09-platecrop-0820"
OUTDIR = "farm-out/ep2-b09-platecrop-0820"

STEPS = [
    {"name": "crop",
     "argv": ["python3", "pipeline/beat09_plate_crop.py", "--all"]},
    {"name": "publish",
     "argv": ["git", "push", "origin",
              "<commit-tree over origin/farm-results-rtx5090>:"
              "refs/heads/farm-results-rtx5090"]},
]

child = derive_spec.derive(
    src=PARENT,
    new_id=NEW_ID,
    by="the b09/b16 slate lane, 2026-08-20",
    fresh={
        "owner": ("the b09/b16 slate lane, 2026-08-20 -- filed AFTER the work ran, "
                  "as the ownership record farm-out/ep2-b09-platecrop-0820 needs"),
        "why": (
            "beat 09's wording ladder closed by measurement at eight renders and "
            "the work ladder named the replacement instrument in one sentence: "
            "condition on the refs to get the hair, then recover the framing with "
            "a crop pass rather than with words. This is that crop pass. It takes "
            "the parent's own frames -- which won the hair at 3 of 12 and lost the "
            "framing at 0 of 12, the parent's pre-registered fail mode firing "
            "because the refs depict two men at full length -- and buys the "
            "framing back geometrically."),
        "consumer": (
            "ep2-b09-cropmotion-0820, whose --src is this job's r1s3 output, and "
            "box_enqueue's refs check, which must be able to name the reference "
            "set this plate was drawn with. That set is the parent's and is "
            "carried here rather than re-asserted, because a crop conditions on "
            "nothing of its own."),
        "success": (
            "ALREADY MEASURED, and recorded in the sidecars beside the outputs "
            "rather than described here. r1s3: head 25.5% -> 55.0% of frame "
            "height, 2.157x, face highpass sigma-1 11.79 -> 4.38, 45% of a native "
            "57%-head close-up of the same beat. r2s2: 37.8% -> 55.0%, 1.454x, "
            "13.73 -> 8.83, 90% of native. Both were also OPENED and looked at, "
            "because this house has just had an instrument that ranked two clips "
            "backwards. NO PICK and NO PROMOTION: a plate is a fixture, and beat "
            "09's adult read is an open R4 card."),
    },
    overrides={
        "key:steps": STEPS,
        "key:runner": "local-mac",
        "key:needs": [],
        "key:needs_gpu": False,
        "key:est_minutes": 1,
        "key:artifacts": [
            OUTDIR + "/09-the-pause-platecrop-r1s3.png",
            OUTDIR + "/09-the-pause-platecrop-r1s3.yaml",
            OUTDIR + "/09-the-pause-platecrop-r2s2.png",
            OUTDIR + "/09-the-pause-platecrop-r2s2.yaml",
            OUTDIR + "/ep2-b09-platecrop-0820.sha256",
        ],
    },
    extra={
        "already_ran": {
            "when": "2026-08-20",
            "where": "this Mac checkout, CPU only -- numpy and PIL, no model, no network",
            "cost_usd": 0.0,
            "published_to": "origin/farm-results-rtx5090",
            "note": ("This spec is a RECORD of work that has executed, not a plan. "
                     "It is filed in pipeline/jobs so resolve_producer() can name "
                     "the directory's owner, and it is never enqueued."),
        },
        "refs_are_the_parents_and_that_is_the_point": (
            "A crop applies no reference conditioning, no prompt and no sampler, "
            "so the reference set that drew these pixels is the parent's "
            "refs-guards-twoinfield-nos2-0815 -- inherited through the steps this "
            "derivation carried from ep2-b09-cast-0817 before they were "
            "overridden, and true of the bytes either way. Not on "
            "box_enqueue.CARD_REFS_DENYLIST, checked rather than assumed."),
        "source_frames": {
            "r1s3": ("farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r1-w015-s3.png -- "
                     "the one frame in the corpus carrying near-black cropped hair, "
                     "wire-rims and BOTH EYES OPEN at once; fails only on framing"),
            "r2s2": ("farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r2-w015-s2.png -- "
                     "the largest head of the three c1 passes, so it needs only "
                     "1.45x: the easy end of the same instrument, kept as the "
                     "control that gives the softness curve two points"),
        },
    },
)

path = derive_spec.write(child, "pipeline/jobs/%s.yaml" % NEW_ID)
print("wrote", path)
