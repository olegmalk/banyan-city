#!/usr/bin/env python3
r"""Beat 04, rung 3: THE STAGING ROUTE, which both wording rungs named and neither took.

WHY THIS EXISTS. Rung 1 (ep2-b04-eyes-crf10-0819) and rung 2
(ep2-b04-headlock-0820) bracket beat 04's WORDING axis from opposite sides and
close it, in their own words: "ON THIS ENGINE, HOLDING THE HEAD HOLDS THE EYES
... THE WORDING ROUTE FOR BEAT 04 IS THEREFORE CLOSED, on the terms this spec
set before either number existed: 'if both fail the answer is staging, not a
third wording.'" Both rungs then named the SAME next move and neither fired it:

    "Crop the plate tight to the face so that the small head rotation the engine
     WILL give (measured: 64.7 px at this crop) subtends enough of the frame to
     read as a glance. That reuses rung 1's recipe unchanged and changes only
     the init's framing -- a cover_crop box, not a prompt."

THIS IS ALSO NOW A DESIGN JOB, AND THAT IS WHY IT IS FILED TONIGHT. The founder
on 2026-08-20: "all of the goblin clips today has had him as an adult. very bad
character consistency." His own 08-19 ruling makes the ADULT canon
(pipeline/canon.yaml ep2-goblin-design-adult) -- the defect is the MIX, and the
audit of review/ep2-ship-0821 found four beats still carrying the pre-ruling
round child: 02, 04, 08 and 13. Beat 04's child take has been swapped out for
rung 1's clip on the design axis, faults named. These rungs exist to give that
slot a take that is BOTH the ratified adult AND the beat as written.

ONE VARIABLE, AND IT IS THE INIT'S FRAMING. Everything generative is rung 1's,
byte for byte: the same plate file and sha, the same prompt, the same negative,
the same 121 frames at 24 fps, guidance 2.0, distilled sigmas, two-stage,
sequential offload, --image-crf 10. The ONLY change is inside cover_crop.py,
which stops taking the whole plate and takes a centred sub-box of it instead.
The argv is untouched, so nothing about how the job is invoked moves either.

WHY THE ZOOM NUMBERS ARE WHAT THEY ARE, AND THEY WERE LOOKED AT BEFORE FILING.
The crop was run locally on the actual plate ($0, PIL, no model) and the three
framings were put side by side and read at 1:1 before any job was written --
this repo's own rule that a metric agreeing with me is not a sample:

  * z 1.0 (rung 1's framing) -- head and shoulders in tall grass; the head is
    about a third of the frame height and 64.7 px of rotation is a twitch.
  * z 1.7, centre y 0.42 -- THE PRIMARY. The face fills the frame, both eyes
    read, and the whole dome and BOTH LONG POINTED EARS are still inside the
    frame. The ears are the identity marker the ratified design is checked on,
    and a crop that loses them buys the glance by giving up the character.
    Against the shot spec, which asks for "a goblin's face fills the frame",
    this is the framing the beat was written for.
  * z 2.4, centre y 0.40 -- THE BRACKET END, filed once and only once. It
    maximises how much frame an eye movement subtends and it CUTS THE DOME AND
    THE EARS OFF. Named as a bracket, not as a candidate, so that if 1.7 is not
    enough the ladder already knows what more looks like and what it costs.

WHY THREE SEEDS AT 1.7 AND NOT ONE. The recipe is proven -- it has now carried
the ratified adult through 121 frames three times (b04 twice, b09 once) -- and
the thing being sampled is stochastic: whether this engine happens to put a
gaze in a given draw. ONE SAMPLE BEFORE ANY BATCH governs a RECIPE CHANGE, and
there is exactly one recipe change here, sampled on the plate before filing.
Three seeds of one proven recipe is the batch that rule permits, and an empty
card overnight is the failure this fills.

FILED TO BACKLOG, NOT READY. The box tops `ready` up from `backlog/` on its own
every three minutes, so these run whether or not any session is alive to feed
them. Judging happens in the morning against the bar below, which is written
here before any pixel exists.

$0, ~7 min each, 4 jobs. Run:  python3 pipeline/derive_b04_tightcrop_0820.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b04-eyes-crf10-0819.yaml"

# cover_crop.py, with the ONE change: a centred sub-box before the cover-crop.
# ZOOM and CY are module constants rather than new flags precisely so the argv
# stays rung 1's byte for byte -- the job is invoked identically and the only
# difference between these children and their parent is in this file.
CROP_PY = '''#!/usr/bin/env python3
"""Cover-crop an asserted source image to an exact WxH, from a ZOOMED sub-box.

Rung 1 and rung 2 of beat 04 used this file with ZOOM = 1.0, i.e. the whole
plate. Their shared verdict named the next rung as "a cover_crop box, not a
prompt", and this is that box. No model, no network, no new flags: ZOOM and CY
are constants here so the step's argv is unchanged from the parent's.

ZOOM is linear: the sub-box is the largest WxH-aspect rectangle that fits the
source, divided by ZOOM, centred at (CX, CY) as fractions of the source, and
clamped inside the source so it can never sample outside the image.
"""
import argparse, hashlib, os, sys
from PIL import Image

ZOOM = %(zoom)s
CX = 0.5
CY = %(cy)s

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--sha256", default="", help="asserted before anything is written")
ap.add_argument("--out", required=True)
ap.add_argument("--size", default="704x1280")
a = ap.parse_args()

if not os.path.isfile(a.src):
    sys.exit("!! src not found: %%s" %% a.src)
h = hashlib.sha256()
with open(a.src, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        h.update(chunk)
have = h.hexdigest()
if a.sha256 and have != a.sha256:
    sys.exit("!! SRC SHA MISMATCH -- refusing.\\n   want %%s\\n   have %%s" %% (a.sha256, have))

W, H = (int(v) for v in a.size.split("x"))
im = Image.open(a.src).convert("RGB")
sw, sh = im.size
ar = W / float(H)
bh = min(sh, sw / ar) / float(ZOOM)
bw = bh * ar
if bw > sw:
    bw = sw
    bh = bw / ar
x = CX * sw - bw / 2.0
y = CY * sh - bh / 2.0
x = max(0.0, min(sw - bw, x))
y = max(0.0, min(sh - bh, y))
box = (int(round(x)), int(round(y)), int(round(x + bw)), int(round(y + bh)))
im = im.crop(box).resize((W, H), Image.LANCZOS)
os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
im.save(a.out)
print("src %%dx%%d sha %%s" %% (sw, sh, have), flush=True)
print("ZOOM %%.3f CY %%.3f -> sub-box %%s of %%dx%%d, resized to %%dx%%d" %% (ZOOM, CY, box, sw, sh, W, H), flush=True)
print("WROTE %%s" %% a.out, flush=True)
'''

# (new_id, zoom, cy, seed, one-line role)
RUNGS = [
    ("ep2-b04-tightcrop-0820", 1.7, 0.42, 20260819,
     "the primary, on rung 1's own seed so the framing is the only difference"),
    ("ep2-b04-tightcrop-s2-0820", 1.7, 0.42, 20260840,
     "second draw of the primary framing"),
    ("ep2-b04-tightcrop-s3-0820", 1.7, 0.42, 20260841,
     "third draw of the primary framing"),
    ("ep2-b04-tightcrop-z24-0820", 2.4, 0.40, 20260819,
     "the bracket end: maximum eye subtense, dome and ears cropped away"),
    ("ep2-b04-tightcrop-s4-0820", 1.7, 0.42, 20260842,
     "fourth draw of the primary framing"),
    ("ep2-b04-tightcrop-s5-0820", 1.7, 0.42, 20260843,
     "fifth draw of the primary framing"),
    ("ep2-b04-tightcrop-s6-0820", 1.7, 0.42, 20260844,
     "sixth draw of the primary framing"),
    ("ep2-b04-tightcrop-s7-0820", 1.7, 0.42, 20260845,
     "seventh draw of the primary framing"),
    ("ep2-b04-tightcrop-s8-0820", 1.7, 0.42, 20260846,
     "eighth draw of the primary framing"),
]

# WHY EIGHT DRAWS AND NOT THREE. The wording route is CLOSED by rungs 1 and 2 --
# they bracketed it from both sides and measured the coupling that closes it --
# so the seed is the only lever this beat has left that is not a founder call.
# What is being sampled is not a recipe (one recipe change, looked at on the
# plate before filing) but a stochastic outcome: whether a given draw happens to
# put a readable glance on a face that now fills the frame. Eight draws of one
# proven recipe is a PICKER SHEET, which is how this project has chosen every
# character asset it owns, and the card was measured empty at 20:57 tonight.
# Nothing scales off any of them until a person reads the sheet.

BAR = {
    "t1_the_glance_reads": (
        "At 1:1, on the frames and not on a number: he visibly looks away and "
        "back. THE WHOLE POINT OF THE RUNG IS THAT THE MECHANISM NO LONGER HAS "
        "TO BE THE PUPILS. Rung 1 was failed for redirecting the gaze with a "
        "head rotation against a prompt that forbade it; at this crop a "
        "rotation of the size the engine actually gives subtends enough frame "
        "to READ as a glance, and beat 04's done_when asks for live eyes under "
        "a held breath, not for a particular muscle. If it reads, it passes."
    ),
    "t2_head_travel_is_measured_not_forbidden": (
        "Head-band ink centroid travel, rung 1's instrument and rung 1's rows "
        "(100-520), PUBLISHED WHATEVER IT IS and scored against nothing. It is "
        "here so the three rungs are comparable -- 64.7 px at z 1.0, 4.7 px "
        "with the head locked -- and so a future reader can see what the crop "
        "did to the number. A bar on it would re-open the wording ladder these "
        "two rungs closed."
    ),
    "t3_the_ratified_adult_holds": (
        "Same lean wiry adult goblin at frame 121 as at frame 1: green skin, "
        "bald dome, long pointed ears, one face, one figure, NO DRIFT TOWARD A "
        "CHILD. Canon: pipeline/canon.yaml ep2-goblin-design-adult, "
        "founder-ratified 2026-08-19. This is the clause the whole job is for "
        "and it outranks T1: a clip that finds the glance and loses the "
        "character is a FAIL, because the character is what the founder "
        "complained about on 08-20."
    ),
    "t4_the_ears_survive_the_crop": (
        "Both long pointed ears are inside the frame at f000 and at f120. "
        "Scored on the z 1.7 rungs and EXPECTED TO FAIL on z 2.4, which is "
        "filed as a bracket. It is a separate clause from T3 because the ears "
        "are the cheapest read on this design and losing them to the crop "
        "would be buying the glance with the character."
    ),
    "t5_rung_1s_passing_clauses_hold": (
        "Mouth shut for all 121 frames -- beat 04 has no spoken line and an "
        "open mouth is a speech cue. Camera locked: no pan, tilt, dolly or "
        "zoom. Both passed in rungs 1 and 2; losing one would mean the crop "
        "bought its win somewhere else."
    ),
}

FAIL_MODES = (
    "T-FROZEN -- the tight crop removes the grass, which is most of what moved "
    "in rung 1, and the clip comes back dead. Named as the most likely and it "
    "is a FAIL, not a tidy still: rung 2 already produced the degenerate pass "
    "once and it was reported as a failure. "
    "T-THE-CROP-IS-NOT-ENOUGH -- the rotation is the same 64.7 px of plate and "
    "still reads as a twitch rather than a glance; the z 2.4 bracket exists to "
    "tell that apart from 'more crop would fix it'. "
    "T-IDENTITY-DRIFT-ON-A-BIGGER-FACE -- a face at this scale gives the "
    "sampler more room to redraw features; --image-crf 10 is what stands "
    "between this and the drift that fired at 33, and if T3 fails while the "
    "flag is at 10 that is a finding about crop scale and not about the flag. "
    "T-THE-EARS-GO -- expected on z 2.4 by construction, and would be a real "
    "loss on z 1.7. "
    "T-SEEDS-AGREE -- all three draws at z 1.7 do the same thing, in which "
    "case the answer is the framing and not the draw, and the next move is a "
    "different staging rather than more seeds."
)

for new_id, zoom, cy, seed, role in RUNGS:
    child = derive_spec.derive(
        src=PARENT,
        new_id=new_id,
        fresh={
            "owner": "goblin-design audit lane, 2026-08-20 (beat 04, rung 3 -- staging)",
            "consumer": (
                "Beat 04's slot in review/ep2-ship-0821. That slot currently "
                "holds rung 1's clip, swapped in tonight on the DESIGN axis to "
                "answer the founder's 08-20 complaint that the cut flips the "
                "goblin's age between shots -- it is the ratified adult and it "
                "is shipping with its action fault named ('the gaze is carried "
                "by a head turn, not the pupils'). This rung is what would "
                "clear that fault: the same character, at a framing where the "
                "movement the engine gives actually reads. If it lands before "
                "12:00 it swaps; after that it is a post-ship patch, and the "
                "patch is worth having either way."
            ),
            "success": (
                "One 704x1280 121-frame mp4 of the ratified adult goblin in "
                "which A GLANCE READS AT 1:1 -- he looks away and back -- with "
                "his mouth shut, the camera locked, both ears in frame and no "
                "drift toward a child. %s. The instrument for the head-band "
                "number is rung 1's, unchanged, so the three rungs sit on one "
                "scale; the number is PUBLISHED and NOT SCORED, because rungs "
                "1 and 2 already proved that scoring it is what closes the "
                "wording ladder rather than the beat. THE DEGENERATE PASS IS "
                "NAMED IN ADVANCE: a clip in which nothing moves satisfies "
                "every stillness clause on this page and fails T1, and is a "
                "FAIL." % (role[0].upper() + role[1:])
            ),
            "why": (
                "$0, ~7 minutes, and it is the rung BOTH of beat 04's wording "
                "rungs named in their own verdicts and neither fired. The card "
                "measured 0 ready / 0 running / 0 backlog at 20:57 tonight -- "
                "the exact state that wasted last night -- and this is "
                "zero-dependency work whose plate is already on the box and "
                "whose consumer is a beat the founder complained about today. "
                "Filed to backlog so autofill runs it with no session alive."
            ),
        },
        overrides={
            "payload:cover_crop.py": CROP_PY % {"zoom": repr(zoom), "cy": repr(cy)},
            "seed": seed,
            "key:est_minutes": 7,
        },
        retoken=[],
        extra={
            "the_one_variable": (
                "The init's framing, and nothing else. cover_crop.py takes a "
                "centred sub-box at ZOOM %s, centre y %s, instead of the whole "
                "plate; the step's argv, the source plate, its asserted sha, "
                "the prompt, the negative, the frame count, the fps, the "
                "guidance, the sigmas, the two-stage flag, the offload mode "
                "and --image-crf 10 are rung 1's byte for byte. The three z "
                "1.7 rungs differ from each other ONLY in seed."
                % (zoom, cy)
            ),
            "bar": BAR,
            "pre_registered_fail_modes": FAIL_MODES,
            "failure_predicted_in_advance": (
                "T-FROZEN. Rung 1's motion was spread across the frame and a "
                "large share of it was grass; this crop throws most of the "
                "grass away, and rung 2 already showed that when this engine "
                "runs out of things to move it holds rather than invents. If "
                "T-FROZEN fires on all three seeds, beat 04 as written is not "
                "reachable on this engine and the honest report to the founder "
                "is that the beat needs a different action or a different "
                "tool -- his call, not this lane's."
            ),
            "init_provenance": (
                "Rung 1's plate, unchanged and unmoved: "
                "04-the-footnote-mac-plate-r1s1.png, sha256 "
                "5dd35da532612e5d85c15ef3353068bf1e44675f8ddfc73c316ac2f654d4e350, "
                "published through ep2-b04-mac-plate-0819 and resolvable on "
                "origin/farm-results-rtx5090, so the plate and refs guards RUN "
                "and PASS with no plate_ack. The sha is asserted inside "
                "cover_crop.py before anything is written, so a crop of the "
                "wrong plate cannot happen silently. THE CROP WAS RUN ON THIS "
                "EXACT FILE LOCALLY BEFORE THIS JOB WAS FILED and the three "
                "framings were read at 1:1 -- $0, PIL only, no model."
            ),
            "not_done_on_purpose": (
                "No prompt edit. No negative edit. No crf change. No frame or "
                "fps change. No new argv flag -- the zoom lives in the payload "
                "so the invocation is identical to the parent's. No fourth "
                "wording: rungs 1 and 2 closed that route from both sides and "
                "re-opening it here would make any result ambiguous."
            ),
            "how_to_judge_this_in_the_morning": (
                "Contact-sheet level, by eye, one line per clip. Extract "
                "f000/f030/f060/f090/f120 from all four, tile them next to "
                "rung 1's clip and next to the child take that shipped, and "
                "answer T1, T3 and T4 off the sheet. Only if T1 is arguable "
                "does the head-band number get computed. The founder's "
                "complaint is a design complaint and T3 is the clause that "
                "answers it, so a rung that passes T3 and fails T1 is still "
                "worth reporting as a design-clean fallback."
            ),
        },
    )
    derive_spec.write(child, "pipeline/jobs/%s.yaml" % new_id)
    print("wrote pipeline/jobs/%s.yaml  (zoom %s, cy %s, seed %s)" % (new_id, zoom, cy, seed))
