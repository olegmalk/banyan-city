#!/usr/bin/env python3
r"""Beat 09 motion off the CROP PLATE. One override pair, everything else carried.

    python3 pipeline/derive_b09_cropmotion_0820.py

WHAT CHANGES, AND IT IS ONE PICTURE. The parent `ep2-b09-faceturn-crf10-0819`
conditioned on `09-the-pause-ipa-r2-w015-s2.png` -- an IP-Adapter frame whose
own verdict block says, under `what_this_does_NOT_settle`: "this clip inherits
the parent's init, which fails its own plate bar on framing, a hand in frame and
the adult read; holding that init faithfully means holding those defects
faithfully too". That is the whole of what this rung replaces. `--src` and its
asserted `--sha256` move to `09-the-pause-platecrop-r1s3.png`, and NOTHING ELSE
MOVES: same sampler, same 121 frames at 24 fps, same 704x1280, same guidance
2.0, same `--image-crf 10`, same prompt payloads, same seed.

WHY THIS INIT AND NOT THE PARENT'S. Measured, in
`farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-r1s3.yaml`:

  head height        25.5% of frame  ->  55.0%     (the bar, reached by geometry)
  hair               near-black, cropped -- recorded a c1 PASS at 3 of 12 in
                     review/ep2-picks/cast-0817-scores.yaml, where the Mac
                     wording rung lost this condition at 0 of 8
  wire-rim glasses   present, `cast_gate_closed_0816` asks for them by name
  eyes               BOTH OPEN, with visible irises
  background         real grass field

The parent's init has none of the first four. Its head is 37.8%, its visible eye
is shut and its hair is mid-brown and shaggy.

WHY THERE IS NO `plate_ack` ON THIS SPEC, WHICH IS THE POINT. `guards_
CORRECTION_0816.what_this_releases` says verbatim: "DO NOT FIRE MOTION OFF A
COSTUME CARD, and do not write a `plate_ack` waiver to get past the plate guard
- that is the defect that produced beat 08's unusable clips." Both halves are
respected rather than waived. This init is not a costume card -- it is the
approved guard on a real field, which is exactly the staged plate that entry
says beats 05/06/07/09/10/11 were missing. And the guard is not waived: the
plate was PUBLISHED to `origin/farm-results-rtx5090`, the branch box_enqueue
reads, by the same route the b03/b13 sapcomp and b04 mac plates took today, and
`box_enqueue.plate_problems` resolves and passes it (flatness 0.019 of 0.62).

WHAT THIS RUNG CANNOT DO, SAID BEFORE IT RUNS. `is_show_content` stays FALSE and
the beat-09 slate stays a slate. The adult read is an OPEN R4 CARD
(/review/ep2-guards-0818, "THE GUARDS READ ADOLESCENT", the one open taste
question on the board) and no init fixes a taste call. A crop also cannot add
detail: this plate is a 2.157x LANCZOS upscale measured at 45% of a native
close-up's high-frequency energy, and whether i2v amplifies that softness across
121 frames is a real unknown and is pre-registered below as the most likely
failure. $0.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec

PARENT = "pipeline/jobs/ep2-b09-faceturn-crf10-0819.yaml"
NEW_ID = "ep2-b09-cropmotion-0820"
PLATE = (r"C:\banyan-farm\courier-box\farm-out\ep2-b09-platecrop-0820"
         r"\09-the-pause-platecrop-r1s3.png")
PLATE_SHA = "ba72dec824c6fe70102de313486f13a8f51ebcf0c3ac42e6b8a504fc10bada7d"

child = derive_spec.derive(
    src=PARENT,
    new_id=NEW_ID,
    by="the b09/b16 slate lane, 2026-08-20",
    fresh={
        "owner": ("the b09/b16 slate lane, 2026-08-20 -- backlogged the same hour "
                  "the plate was published to the results branch, on an idle card"),
        "why": (
            "The parent settled that --image-crf 10 makes the init HOLD for 121 "
            "frames and said in the same breath what it could not settle: it "
            "inherited an init that fails its own plate bar on framing, on a hand "
            "in frame and on the adult read. Beat 09's plate bar has now been met "
            "on the framing clause by geometry rather than by words -- the "
            "wording ladder was closed by measurement at eight renders, and the "
            "instrument the work ladder named instead (reference-plus-crop) ran "
            "today for $0 and reached 55% head from an IP-Adapter frame that "
            "already carried near-black cropped hair, wire-rims and open eyes. "
            "This is the first beat-09 motion job whose starting picture is not "
            "a known-miscast one."),
        "consumer": (
            "The beat-09 SLATE in review/ep2-demo-0820, one of the cut's last "
            "two. Not this clip -- is_show_content stays false while the adult "
            "read is an open R4 card. What the slot buys is the answer to "
            "whether a CROPPED plate survives i2v: if the softness of a 2.157x "
            "upscale holds across 121 frames, beat 09's framing axis is closed "
            "for good and every other beat blocked on head size inherits the "
            "route. If it does not, reference-plus-crop is a still-only "
            "instrument and the beat needs the IP-Adapter arm re-shot tighter."),
        "success": (
            "ONE 704x1280 mp4, 121 frames at 24 fps. THE BAR IS THE SOFTNESS "
            "QUESTION AND THE FRAMING IT WAS BOUGHT WITH, and nothing else; cast "
            "and taste are explicitly out of scope. "
            "C1 THE FRAMING SURVIVES: head bounding box on frame 1 measures at "
            "least 50% of frame height (the plate is 55%; the 704x1280 cover "
            "crop preserves full height, so anything under 50 means the crop "
            "step moved the head). "
            "C2 THE INIT STILL HOLDS: f001->f002 face-crop step under 20, the "
            "parent's own pass threshold, which it met at 0.66. A softer init is "
            "the one thing that could plausibly change this and that is why it "
            "is re-measured rather than assumed. "
            "C3 THE SOFTNESS DOES NOT COMPOUND: highpass sigma-1 std over the "
            "face box on frame 121 is at least 70% of frame 1's. A cropped init "
            "starts at 45% of a native plate's detail; the failure this clause "
            "catches is the sampler treating that softness as the subject and "
            "smearing further with every frame. "
            "C4 THE FACE IS STILL DOING SOMETHING: face-crop interframe mean "
            "above 1.0 with motion in both the first and last thirds, the "
            "parent's measure, which read 2.155. "
            "Report N of 4 with each number beside its threshold."),
    },
    overrides={
        "argv:--src": PLATE,
        "argv:--sha256": PLATE_SHA,
    },
    retoken=[("09-the-pause-ipa-r2-w015-s2", "09-the-pause-platecrop-r1s3")],
    extra={
        "is_show_content": False,
        "is_show_content_why": (
            "The framing clause of beat 09's plate bar is met for the first time "
            "and TWO of its clauses are not. The adult read is an open R4 card "
            "(/review/ep2-guards-0818) and a clip inherits its plate's cast "
            "defects frame for frame; the crop cannot change how old he looks. "
            "This is an INIT MEASUREMENT and must never reach a cut. The "
            "beat-09 slate stays a slate."),
        "init_provenance": {
            "plate": "farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-r1s3.png",
            "published_to": "origin/farm-results-rtx5090",
            "sha256": PLATE_SHA,
            "derived_from": ("farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r1-w015-s3.png, "
                             "an 08-17 box IP-Adapter frame"),
            "operation": ("pipeline/beat09_plate_crop.py -- crop box [223,9,609,573] "
                          "of 832x1216, LANCZOS to 832x1216, upscale 2.157x. No "
                          "sampler, no model, no GPU. Chin placed at 0.57 of frame "
                          "height to reproduce the native close-up's composition "
                          "rather than centring the head."),
            "measured": {
                "head_frac_source": 0.255,
                "head_frac_after": 0.55,
                "face_highpass_sigma1_before": 11.79,
                "face_highpass_sigma1_after": 4.38,
                "pct_of_native_closeup_control": 45.0,
                "control": "farm-out/ep2-b09-mac-plate-0819/09-the-pause-mac-plate-r3s1.png",
            },
            "no_plate_ack_on_purpose": (
                "guards_CORRECTION_0816 forbids a plate_ack waiver on this beat "
                "family by name. The plate was published to the branch the guard "
                "reads instead, and box_enqueue.plate_problems resolves it and "
                "passes it at flatness 0.019 of 0.62."),
        },
        "pre_registered_fail_modes": {
            "FAIL-SOFT-COMPOUNDS": (
                "NAMED AS THE MOST LIKELY. The init is a 2.157x upscale at 45% of "
                "a native plate's high-frequency energy. If i2v reads that as the "
                "subject's own texture, C3 fails and the clip gets progressively "
                "mushier. If it fires, reference-plus-crop is a STILLS instrument "
                "and the next rung is the IP-Adapter arm re-shot at a tighter "
                "framing so the crop starts from ~38% and only needs 1.45x -- the "
                "ratio measured today at 90% of native."),
            "FAIL-CROP-MOVES-THE-HEAD": (
                "cover_crop.py takes 832x1216 to 704x1280 by cropping WIDTH "
                "(target aspect 0.55 against the source's 0.684) and keeping full "
                "height, so the 55% head should be preserved exactly. C1 exists "
                "because 'should' is not 'measured', and this beat has already "
                "lost a rung to a framing claim that was carried in prose and "
                "moved in the string."),
            "FAIL-COLLAPSE-RETURNS": (
                "The parent's crf-10 finding was measured on a DIFFERENT init. If "
                "C2 fails here, the finding was plate-dependent, which would be a "
                "correction to a result this repo has already generalised to "
                "every i2v job on the card."),
        },
        "carried_byte_identical_from_the_parent": (
            "prompt and negative payloads, seed, 121 frames, 24 fps, 704x1280, "
            "guidance 2.0, --distilled-sigmas, --two-stage, --image-crf 10, "
            "--offload sequential. The ONLY overrides are --src and --sha256. "
            "Stated out loud per derive_spec's CARRIED VERBATIM convention rather "
            "than left to be inferred from a diff."),
    },
)

path = derive_spec.write(child, "pipeline/jobs/%s.yaml" % NEW_ID)
print("wrote", path)
