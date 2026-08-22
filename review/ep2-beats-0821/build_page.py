#!/usr/bin/env python3
"""review/ep2-beats-0821/build_page.py — ONE page, 21 sections, one per beat.

WHY THIS PAGE EXISTS. The founder's directive on 2026-08-21: "let me review each
beat one by one. iteration. im talking about the clip for each beat." Every
previous review surface in this tree is a CUT — a 116-second master he has to
watch end to end and then remember what he wanted to say about beat 13. This one
is the other shape: one section per beat, each self-sufficient, each ending in a
sentence he can copy into chat.

WHAT IS READ AND WHAT IS AUTHORED. Everything mechanical is read from the tree at
build time and nothing about it is retyped here:

  * the beat list, its stage directions and its spoken lines come from
    genomes/sapling/nodes/002b-first-citizen/node.md through
    queue_history.parse_node_script — the same parser /queue uses, so a card here
    and a card there cannot drift apart;
  * "what it has to show" is review/ep2-picks/done-definitions.yaml, which is the
    shipping lane's own bar and the most literal answer the tree owns;
  * THE CURRENT CLIP, its slot, and how the assembly fills that slot come from
    review/ep2-ship-0821/ep2-ship-0821.mp4.meta.yaml `sources:` — the sidecar
    render_t3 wrote AT ASSEMBLY, not from the ship manifest. That distinction is
    load-bearing: ship-manifest.yaml still describes the five age-B swaps and the
    beat-01 chroma composite, and every one of those was REVERTED by 5412a452
    after the founder watched the cut. The sidecar is what the mp4 is made of.
    A page that read the manifest would show him six clips that are not in his
    episode;
  * the VO line is the text in sources/NN-vo.json, i.e. the words that were
    actually synthesised, not the script's copy of them.

The `BEATS` table below is the AUTHORED half: the faults in plain language and
the candidate list. Every fault sentence is a translation of a row that already
exists in review/ep2-ship-0821/sources/ship-manifest.yaml (its `fault_shipping`,
`verdict_quoted`, `superseded_*` and `goblin_design_audit_0820` blocks) or of a
verdict in the job spec named beside it. Nothing here scores a clip; the plain
words are a reading aid over somebody else's verdict.

Run:  python3 review/ep2-beats-0821/build_page.py
"""
import html
import json
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import queue_history as qh  # noqa: E402

NODE = REPO / "genomes" / "sapling" / "nodes" / "002b-first-citizen" / "node.md"
DONE = REPO / "review" / "ep2-picks" / "done-definitions.yaml"
SHIP = REPO / "review" / "ep2-ship-0821"
MASTER = SHIP / "ep2-ship-0821.mp4.meta.yaml"
SRC = SHIP / "sources"

SHIP_URL = "/review/ep2-ship-0821/sources"
PROOF_URL = "/review/ep2-ship-0821/proof"
CAND_URL = "/review/ep2-beats-0821/candidates"
POSTER_URL = "/review/ep2-beats-0821/posters"
# The age-B wave's own directory (review/motion-ageb-0821) carries no
# index.html, so build_site never copies it into _site and its mp4s were never
# tracked — linking there would have published fourteen 404s. The clips this
# page shows are therefore copies living in this page's own candidates/, which
# is also the rule the coordinator set: stay out of the other lanes' dirs.
AGEB_URL = "/review/ep2-beats-0821/candidates"

GOBLIN_PAGE = "/review/ep2-goblin-age-0821"

# ---------------------------------------------------------------------------
# THE AUTHORED HALF.
#
# faults      what is wrong with THE CLIP THAT IS IN THE CUT, plainly. Source is
#             named in `faults_from`.
# wins        what that same clip genuinely gets right. A page that only lists
#             faults invites "redo everything", which is not the question.
# note        anything he needs to know that is neither a fault nor a win —
#             usually a reversal, so he is not shown a decision he already made
#             as though it were open.
# candidates  other footage that EXISTS AND IS JUDGED. `tag` is the judging
#             lane's own word, `verdict` its own sentence shortened, `diff` the
#             one thing that is different about it.
# inflight    a render that is queued or running right now and has no pixels
#             yet. Named so a "redo" answer is not filed twice.
# ---------------------------------------------------------------------------
AGEB_PULLED = ("Rendered this morning in the age-B wave, swapped into the cut, "
               "and pulled back out the same day — you watched that cut and said "
               "it was worse than the last one, and these five swaps were steward "
               "picks you had never approved.")

BEATS = {
    1: dict(
        goblin=False,
        faults=[
            "The grass moves with the fig. The field is supposed to be locked and it is not — on all three colour bands — and it is the first thing on screen.",
            "Three other things about this beat have never been scored at all: nobody counts the leaves, nobody measures the grass line, and the camera probe refuses to give a reading.",
        ],
        wins=["Seven of its eight scored clauses pass. The fig grows from green nub to full purple fig inside the clip."],
        note=(
            "TWO ANSWERS TO YOUR NOTE, AND ONE OF THEM IS THAT THE COLOUR IS SUPPOSED TO DO THAT. "
            "Your own approved script for this beat reads: \"On the thinnest branch a green nub swells, "
            "darkens and rounds into a single fig — the only thing in frame that moves.\" The green-to-purple "
            "IS the ripening, and it is the entire event of the cold open; beat 20's fig was corrected TO "
            "purple on the same canon. So it has been left in the picture rather than quietly frozen — say "
            "the word and it changes, but that is a script change and it is yours. "
            "THE SHAPE IS A REAL DEFECT AND ITS CAUSE WAS IN THE PROMPT: the instruction under this clip "
            "literally says the nub \"swells, darkens and ROUNDS into a single deep purple fig\", and nothing "
            "in it or its ban list ever said what a fig looks like. It has now been said, and the clip "
            "below is the result — it took two rounds, and the first one is not shown to you because it "
            "was my mistake rather than a finding: rewriting the prompt to describe the silhouette "
            "dropped the words \"deep purple\" out of it and the fig ripened teal. "
            "IF THE ONE FAULT LEFT IN IT BOTHERS YOU, the next lever is not more words — it is drawing "
            "the fig-shaped bud into the picture instead of the round blob the tool draws today, which is "
            "the same thing that had to be done for this fruit's COLOUR back in August when words would "
            "not carry it either. "
            "Separately: a composite that fixed two of the three failing colour bands was swapped in on "
            "08-20 and you ruled it back out on 08-21. This is the take you kept, and that decision is "
            "closed unless you reopen it."),
        faults_from="ship-manifest.yaml beat 1 (the row for the take this one replaced) + verdict_chromaticity_rung_0820",
        candidates=[
            dict(file=f"{CAND_URL}/01-cold-open-LTX-figshape-r2-0822.mp4",
                 poster=f"{POSTER_URL}/01-cold-open-LTX-figshape-r2-0822.jpg",
                 label="THE FIG, RE-SHAPED — tonight, newest", tag="warn",
                 verdict="The stick is gone. It is no longer a ball with a pin in the top: the fruit is a leaning teardrop, heavier at the bottom, and it meets the branch directly with nothing standing clear above it. It still ripens green to purple, which is the script. THE NEW FAULT, and it is yours to price: a pale green crescent sits on its upper shoulder for the whole second half — it reads either as an unripe patch or as a bite taken out of it, depending on the frame. It is one fruit, not two, and it is not a highlight.",
                 diff="Wording only — same plate, same recipe, same everything as the take in the cut. One clause describing the silhouette, and the lollipop reading banned. Round 1 of this is not shown: describing the shape accidentally dropped the words \"deep purple\" out of the prompt and the fig ripened teal. That was my error, not a finding.",
                 src="pipeline/jobs/ep2-b01-figshape-r2-0822.yaml"),
        ],
    ),
    2: dict(
        goblin=True,
        faults=[
            "He is not green. He is bone-grey with a big round child skull, a chubby child body, grey shirt and shorts, barefoot. This is the worst character break in the episode.",
            "No bar has ever been written for beat 02, so nothing has ever judged this clip. It was caught by an audit on 08-20, not by a test.",
            "There is no sapling trunk in frame for him to dive behind — the beat's own staging says he has not found the sapling yet.",
        ],
        wins=[],
        note=(
            "Beat 02 is silent by design — there is no line here. "
            "ON \"TOO SERIOUS, LIKE A SOLDIER\": that is not something this engine will take from words. "
            "It was measured four separate ways on this exact recipe — moving the mask, halving the "
            "adapter's strength, dropping the expression tags — and the face came back the same every "
            "time; a version with NO expression tags at all wore it too. What DID move it was repainting "
            "the brow and the mouth of the picture itself. So the panic is being painted into the plate, "
            "over those two bands, with the eyes left alone because the slit pupil is the thing this "
            "character loses most often. "
            "ON \"HE JUST FACEPLANTS\": the last round's own notes say the same thing from the other side — "
            "the dive \"reads as a duck\". The landing is now written as a placement rather than an "
            "adjective: forearms take it, chin off the ground, and he ends lying flat behind the stem with "
            "his head up. Your script says he dives BEHIND the trunk, not into the dirt. "
            "Both are in the first clip below."),
        faults_from="ship-manifest.yaml goblin_design_audit_0820 beats.2 + ship_status.2",
        candidates=[
            dict(file=f"{CAND_URL}/02-the-sprint-LTX-ep2-b02-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/02-the-sprint-LTX-ep2-b02-w4motion-0822.jpg",
                 label="THE SPRINT ON YOUR GOBLIN'S FACE — tonight, newest, uncut", tag="pass",
                 verdict="The whole beat, and the face is the one you approved for every frame of it. He runs in, plants, skids down flat and lands on his forearms with his chin off the ground and his head up — and he STAYS down; he does not stand back up, so there is nothing to cut. Small off-white eyes with dark pupils, broad head, ears low and sideways, mouth open the whole way. No camera pull-back and he never leaves the frame.",
                 diff="Same action as the clip below — it was already the right one. What changed is underneath it: a new plate on the corrected eye, and the sentence that describes him no longer says \"slit pupils\", which is the eye you threw out. The old wording would have dragged the face back toward a big iris over the five seconds even from a good starting picture.",
                 src="pipeline/jobs/ep2-b02-w4motion-0822.yaml + review/ep2-goblin-eye-0822"),
            dict(file=f"{CAND_URL}/02-the-sprint-LTX-b02-panic-trim78-0822.mp4",
                 poster=f"{POSTER_URL}/02-the-sprint-LTX-b02-panic-trim78-0822.jpg",
                 label="the same staging on the OLD face — last night", tag="warn",
                 verdict="He is not a soldier any more: brows up and arched, mouth open, all the way through. And he does not faceplant — he runs in, skids, and goes down flat on his chest behind the sapling with his chin off the ground and his head up, which is where this cut ends and freezes. Green, canon ears, slit pupils, collar and boots hold to the last frame, and the sapling stays put.",
                 diff="Two changes, both aimed at your note. The face was repainted into the picture before anything moved — three strengths were tried and looked at side by side, and 0.60 is the one that draws raised brows instead of washing the old ones out. The landing was written as a placement rather than an adjective: forearms take it, chin off the ground, head up. Then cut at frame 77 — the full take stands him back up afterwards, and the assembly freezes on the last frame, so an uncut version would end on him standing in the open.",
                 src="pipeline/jobs/ep2-b02-panic-0822.yaml + review/ep2-beats-0821/candidates/02-the-sprint-LTX-b02-panic-trim78-0822.mp4.meta.yaml"),
            dict(file=f"{CAND_URL}/02-evidence-LTX-ep2-b02-panic-0822.mp4",
                 poster=f"{POSTER_URL}/02-evidence-LTX-ep2-b02-panic-0822.jpg",
                 label="the same take, uncut — he gets back up at the end", tag="warn",
                 verdict="Identical to the clip above for its first 78 frames, then he pushes back up onto his feet and is standing in the open when it ends. Shown so the cut above is not hiding anything from you: if you want him to come back up, this is what that looks like, and the slot would freeze on it.",
                 diff="No trim. Same render, all 105 frames.",
                 src="pipeline/jobs/ep2-b02-panic-0822.yaml"),
            dict(file=f"{CAND_URL}/02-evidence-LTX-ep2-b02-canonmotion-r2-0821.mp4",
                 poster=f"{POSTER_URL}/02-evidence-LTX-ep2-b02-canonmotion-r2-0821.jpg",
                 label="canon-motion, round 2 — tonight, newest", tag="fail",
                 verdict="The frame HOLDS now. He is the same size at the first frame and the last, and the sapling from the plate is still there — no invented tree. But the move is wrong: he drifts back and to the left, then comes back to centre and bends over. No run in, no skid, no dive.",
                 diff="The sapling trunk is now IN the starting picture. Round 1 named a trunk the picture did not contain, and the model rebuilt the whole shot to fit one in.",
                 src="pipeline/jobs/ep2-b02-canonmotion-r2-0821.yaml verdict_canonmotion_r2_0821"),
            dict(file=f"{CAND_URL}/02-evidence-LTX-ep2-b02-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/02-evidence-LTX-ep2-b02-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="fail",
                 verdict="The camera pulls back until he is a speck at the bottom right of a wide shot dominated by a big bare tree that is in none of our pictures. No sprint, no skid, no dive.",
                 diff="First clip built on the canon goblin plate — your tile's face handed to the motion model as pixels. The face held; the camera did not.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/02-the-sprint-LTX-b02-ageb-s2-trim97-0821.mp4",
                 poster=f"{POSTER_URL}/02-the-sprint-LTX-b02-ageb-s2-trim97-0821.jpg",
                 label="age-B seed 2 (the one that was swapped in, then reverted)", tag="warn",
                 verdict="Face, eyes and mouth intact for the whole slot; the sprint, the push off and the dive all complete. The ears are long tapering spikes where your tile has short low flanges, and there is a magenta collar.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b02-tilemotion-s2-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/02-the-sprint-LTX-ep2-b02-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/02-the-sprint-LTX-ep2-b02-tilemotion-s1-0821.jpg",
                 label="age-B seed 1", tag="fail",
                 verdict="The face stops being drawn partway — a featureless green head from frame 55.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b02-tilemotion-s1-0821.yaml", quiet=True),
        ],
    ),
    3: dict(
        goblin=True,
        faults=[
            "The last 0.79 s of the clip is a dead picture — 15 identical frames at the end. It is baked into the footage, so the assembly cannot cover it.",
            "He reads as an adult man, not the creature in your tile: human nose with nostrils, a rounded human ear, folds either side of the mouth, flat olive skin instead of two-tone.",
        ],
        wins=[],
        faults_from="ship-manifest.yaml beat 3 what_it_fixed + goblin_design_audit_0820 beats.3",
        note=(
            "\"Looks like an old man\" is this clip, and the 08-20 audit agrees with you in almost the same "
            "words — human nose with nostrils, a rounded human ear, folds either side of the mouth. THAT "
            "FACE IS ALREADY FIXED IN A CLIP YOU HAVE NOT SEEN: the round-2 candidate below is drawn off "
            "your own tile — no horn, no dissolve, features held in all 105 frames — and it also finally "
            "has the trunk this beat is supposed to be hiding behind. Its one fault is that nothing "
            "happens in it. That is a wording problem, not a design one: the instruction told a motion "
            "model to hold still, and it did. The first clip below is that same picture with an action "
            "that has a start, a bottom and a return — it is the one to watch."),
        candidates=[
            dict(file=f"{CAND_URL}/03-bad-cover-LTX-ep2-b03-repeat-0822.mp4",
                 poster=f"{POSTER_URL}/03-bad-cover-LTX-ep2-b03-repeat-0822.jpg",
                 label="tonight, newest — a rewritten action, and a correction to why it was filed", tag="warn",
                 verdict="Your face all the way through, and the beat is still what it was: he crouches, his head dips and comes back, a stalk grows in beside him and the camera drifts. The two counted ducks the new wording asked for do not read as two ducks. IT IS NOT WORSE THAN THE ONE BELOW AND IT IS NOT MUCH BETTER, and the honest reason is that this beat was filed on a premise that turned out to be wrong.",
                 diff="A rewrite of the action into a counted repeat, which had just worked on beat 17. It was filed on the belief that this beat's 'barely moves' fault was the same parked-clip problem — and measuring the clip below AFTER filing showed it never was: it already scored 0 of 104 frame pairs under 0.5, the best score of any clip in the wave except beat 16. What is actually still on this beat is that HIS BODY barely moves while the STALK grows and the CAMERA drifts, and a frame-difference number cannot tell those apart. So the number was never the fault here, and the next move on beat 03 is a figure-motion question and not a timing one.",
                 src="pipeline/jobs/ep2-b03-repeat-0822.yaml"),
            dict(file=f"{CAND_URL}/03-bad-cover-LTX-ep2-b03-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/03-bad-cover-LTX-ep2-b03-w4motion-0822.jpg",
                 label="YOUR GOBLIN'S FACE, on this beat's best action — tonight, newest", tag="warn",
                 verdict="The face is the one you approved and it stays that face for all 105 frames — small off-white eyes with dark pupils, broad head, ears low and sideways, no old-man folds. That part is done. What is still weak is the same thing as before: he barely moves. A stalk grows in beside him and the camera drifts a little, and that is the whole clip. Crouching badly hidden is a quiet beat, but this is quieter than a beat should be.",
                 diff="New plate on the corrected eye, and the sentence describing him no longer says \"slit pupils\". The action is unchanged from the clip below — it is this beat's best one, and swapping it at the same time as the face would have told us nothing about either.",
                 src="pipeline/jobs/ep2-b03-w4motion-0822.yaml + review/ep2-goblin-eye-0822"),
            dict(file=f"{CAND_URL}/03-evidence-LTX-ep2-b03-crouchlife-0822.mp4",
                 poster=f"{POSTER_URL}/03-evidence-LTX-ep2-b03-crouchlife-0822.jpg",
                 label="THE OLD-MAN FIX, with something happening in it — tonight, newest", tag="pass",
                 verdict="Your design, and it moves. He drops his head down and away behind the stem, brings it back up and centred, drops it away again, and is back up with his face to camera on the last frame — which is the frame the assembly freezes on, so the beat ends on a face rather than the top of a skull. No horn, no old-man nose, no melting; the stem is there, unmoved, hiding about the sixth of him the script asks for; and he does not shrink across the clip. His face is turned away for parts of two of the four moves — on a beat about a creature trying to hide, that reads as looking around rather than as a defect, but it is your call.",
                 diff="Same plate and same recipe as the round-2 clip below. The only change is the instruction: \"crouch low and hold still, eyes flicking sideways\" became three head-and-shoulder moves with a bottom and a return. The eye flicks were dropped rather than re-asked — this engine was measured twice on beat 04 refusing to move eyes without moving the head.",
                 src="pipeline/jobs/ep2-b03-crouchlife-0822.yaml"),
            dict(file=f"{CAND_URL}/03-evidence-LTX-ep2-b03-canonmotion-r2-0821.mp4",
                 poster=f"{POSTER_URL}/03-evidence-LTX-ep2-b03-canonmotion-r2-0821.jpg",
                 label="canon-motion, round 2 — your design, and the trunk is there", tag="warn",
                 verdict="THE FACE IS FIXED: it is your tile's creature, the horn round 1 grew is gone, and the features are drawn in all 105 frames. The composited two-leaf stem is present, unmoved, crossing his chest and hiding about the sixth of him the script asks for. WHAT IS WRONG: almost nothing happens — the pose barely changes from the first frame to the last and the only event is that his eyes close near the end. He also still recedes, by 27% across the clip, down from about 50% in round 1.",
                 diff="The starting picture now contains the trunk the prompt names. That is the whole change from round 1, and it removed the horn, halved the recede and gave the beat its cover — at the cost of the model's reason to move at all.",
                 src="pipeline/jobs/ep2-b03-canonmotion-r2-0821.yaml verdict_canonmotion_r2_0821"),
            dict(file=f"{CAND_URL}/03-evidence-LTX-ep2-b03-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/03-evidence-LTX-ep2-b03-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="fail",
                 verdict="A curved pointed horn grows out of the top of a bald head from about frame 72 and is still there at the end. The camera pulls back and he halves in height. And there is still no trunk in frame to hide behind.",
                 diff="Canon goblin plate, 105 frames. Features stay drawn the whole way — no dissolve — which the previous wave could not manage.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/03-bad-cover-LTX-ep2-b03-tilemotion-s2-0821.mp4",
                 poster=f"{POSTER_URL}/03-bad-cover-LTX-ep2-b03-tilemotion-s2-0821.jpg",
                 label="age-B seed 2 (was swapped in, then reverted)", tag="warn",
                 verdict="Face holds all 121 frames, no costume morph, no dead tail. The motion is very small — he sits, hands on knees, and leans near the end.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b03-tilemotion-s2-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/03-bad-cover-LTX-ep2-b03-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/03-bad-cover-LTX-ep2-b03-tilemotion-s1-0821.jpg",
                 label="age-B seed 1", tag="fail",
                 verdict="The most real body motion in the whole wave — he shifts, comes up onto a knee, turns — and his costume changes on screen: a dark cloak becomes a brown plaid blanket between frames 65 and 76.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b03-tilemotion-s1-0821.yaml", quiet=True),
        ],
    ),
    4: dict(
        goblin=True,
        faults=[
            "This is the round child you ruled against on 08-19 — \"c kinda is but still pretty bad so change it\".",
            "The clip abandons its own first frame: between frame 1 and frame 2 it jumps from the wide picture to a close-up in a single frame pair.",
            "The glance is a head turn, not the eyes. The eyes never move.",
        ],
        wins=[],
        faults_from="ship-manifest.yaml beat 4 superseded_why_0820 + why_this_is_still_the_better_ship",
        note="You said \"wouldn't be bad if he didnt look so chibi in this\". The first clip below is the answer and it needed no new render — it already existed, unwatched, and it is trimmed to this beat's slot so it drops straight in. Side by side with what is in the cut: the cut is a teal head filling the frame with red eyes and no ears; the candidate is a whole body in your design — bald, big lateral ears, slit pupils, mandarin collar, boots — leaning out and back inside the slot. A second seed was rendered so you would have two of these to choose between, and it is NOT shown: the camera pushes in on it and the peek never happens, so it loses both of the things the first one gets right.",
        candidates=[
            dict(file=f"{CAND_URL}/04-the-footnote-LTX-ep2-b04-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/04-the-footnote-LTX-ep2-b04-w4motion-0822.jpg",
                 label="your goblin's face, and he stays on his feet — tonight, newest", tag="warn",
                 verdict="Canon face, standing, feet planted, upright at the start and the end. The lean-out reads as a HEAD lean rather than a body one, and around the middle of the clip his head rolls far enough over that the face smears for about half a second before it comes back clean. The out-and-back shape is there; the middle of it is ugly.",
                 diff="The first version of this on the new plate FELL OVER — the whole figure rotated ninety degrees and lay down across the frame. The old sentence said he leans out \"from behind the trunk\", and the new plate has no trunk in it, so a phrase about where his body sits relative to an object that is not there got resolved by tipping him. Rewritten with no object in it and an explicit instruction that his feet stay planted. That worked; the head-roll is what is left.",
                 src="pipeline/jobs/ep2-b04-w4motion-0822.yaml + pipeline/work-ladder-0819.md"),
            dict(file=f"{CAND_URL}/04-the-footnote-LTX-b04-canonmotion-trim97-0822.mp4",
                 poster=f"{POSTER_URL}/04-the-footnote-LTX-b04-canonmotion-trim97-0822.jpg",
                 label="THE CHIBI FIX — canon-motion, trimmed to the slot", tag="pass",
                 verdict="This is your design instead of the round child, and the peek still lands: he leans out and across, is fully extended in the middle, and is back upright before the clip ends. Same 97 frames as the take in the cut, so it occupies the slot identically. The one gap is the same one the untrimmed clip has: with no trunk in frame there is nothing to lean out FROM, so it reads as a stumble-and-recover rather than a peek.",
                 diff="The same canon-motion clip below, cut from 105 frames to 97 — the wave's own trim plan, and the length the take in the cut already is. f097–f104 were opened first and are clean, so nothing is being hidden by the trim.",
                 src="review/ep2-beats-0821/candidates/04-the-footnote-LTX-b04-canonmotion-trim97-0822.mp4.meta.yaml"),
            dict(file=f"{CAND_URL}/04-evidence-LTX-ep2-b04-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/04-evidence-LTX-ep2-b04-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="pass",
                 verdict="6 of 7, and the most encouraging clip of the seven. He leans out and across, is fully extended in the middle, and is back upright inside the trim — so the pull-back, which is the joke, lands in the slot. Frame holds. Bald head, big lateral pointed ears, off-white eyes with slit pupils, all held to the last frame. The one gap: with no trunk in frame there is nothing to lean out from, so it reads as a stumble-and-recover rather than a peek.",
                 diff="Canon goblin plate. This is the one missing-prop beat that did NOT re-stage itself, because its instruction never names the missing trunk — it only names body verbs.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/04-the-footnote-LTX-ep2-b04-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/04-the-footnote-LTX-ep2-b04-tilemotion-s1-0821.jpg",
                 label="age-B seed 1 (was swapped in, then reverted)", tag="warn",
                 verdict="Face holds all 121 frames and stays large in frame; the head tilts and turns down. The gaze is still not in the pupils, and a fifth of the beat would be a frozen frame.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b04-tilemotion-s1-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/04-the-footnote-LTX-ep2-b04-tilemotion-s2-0821.mp4",
                 poster=f"{POSTER_URL}/04-the-footnote-LTX-ep2-b04-tilemotion-s2-0821.jpg",
                 label="age-B seed 2", tag="warn",
                 verdict="Same recipe, second seed. Its last frame — the one the assembly would freeze on — is the weaker of the two.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b04-tilemotion-s2-0821.yaml", quiet=True),
        ],
    ),
    5: dict(
        goblin=False,
        faults=[
            "Four of its seven clauses fail.",
            "Neither guard wears the sash you froze for the cast — the clip contradicts a ruling that is already final.",
        ],
        wins=["Two figures in the field from the first frame to the 117th — never one, never three. Four rounds of rewording never got that."],
        note="Guard 1's voice was re-pitched across the whole episode on 08-21 after you said he sounded like a little kid. He now renders at 99.6–122.8 Hz instead of 192 Hz. The picture is unchanged.",
        faults_from="ship-manifest.yaml beat 5 + pipeline/jobs/ep2-b05-standB-0814.yaml",
        candidates=[
            dict(file=f"{POSTER_URL}/05-the-patrol-PLATE-pose-0822.jpg", still=True,
                 label="a PLATE — a different method, and TWO MEN ARE IN THE FIELD", tag="warn",
                 verdict="Two grown men, whole, side by side, standing in a bright grass field under a blue sky. That is the composition this beat has fought for through four wording rounds and then lost twice tonight, and it is here because it was DRAWN rather than asked for. They are also two DIFFERENT men — one has the thick moustache and the other does not — which was the single most likely failure and it did not fire. THREE THINGS ARE WRONG. There are still no white sashes: both are in dark hooded robes, so the ruling this beat contradicts is still contradicted. The round glasses landed on BOTH faces when only one man was given them. And the two men are the wrong way round — the moustache was written for the man on the right and it came back on the left.",
                 diff="No reference photograph. Two stick-figure skeletons, both five heads tall, on one ground line with the left one drawn taller, set where the two men stand; the men themselves come from the words. The daylight is here because it was ASKED FOR this time instead of the dark being banned — the same correction that fixed the beat-06 plate's night sky. WHAT THIS SETTLES for the rest of the episode: a figure COUNT is now solvable, and it is solvable by drawing rather than by rewording. What it does not settle is which man is which — telling the model 'the left man has X, the right man has Y' bound one feature to one face and spread the other across both, and reversed the sides. THE MOUSTACHED MAN IS STILL ON LOAN: guard 2 is your call at /review/ep2-guardcast2-0822 and nothing here decides it.",
                 src="pipeline/jobs/ep2-b05-pose-0822.yaml + pipeline/author_b05_guards_pose_0822.py"),
            dict(file=f"{POSTER_URL}/05-the-patrol-PLATE-guards-f-content-0822.jpg", still=True,
                 label="a PLATE — second attempt, the fix did not work either", tag="fail",
                 verdict="Same one man, same face close-up, same two briefs on one head — now with a much heavier black moustache and a fur collar nobody asked for. Still not two men, still not the field, still no sash. The first attempt is below it and they are near enough the same picture.",
                 diff="One variable against the attempt below: the adapter was moved from every layer of the model for a short burst to ONE layer for the whole render, which is the textbook way to take a face from a reference without taking its framing. It changed almost nothing. So the framing is not coming from HOW the reference is applied, it is coming from the reference being a tight head-and-shoulders crop at all. That closes two attempts on this route and the next one is different in kind: pose the shot with a drawn stick-figure skeleton, take the man from the WORDS — which is measured to work, ten grown men out of ten on the casting sheet — and use no reference photograph at all. Two failures for six GPU minutes and they bought the answer.",
                 src="pipeline/jobs/ep2-b05-guards-f-content-0822.yaml"),
            dict(file=f"{POSTER_URL}/05-the-patrol-PLATE-guards-f-0822.jpg", still=True,
                 label="a PLATE, not a clip — tonight's first attempt, and it FAILED", tag="fail",
                 verdict="Asked for two men side by side in a field, both in white shoulder sashes, the left one guard 1 and the right one a moustached man. What came back is ONE man in a face close-up: guard 1's dark cropped hair and round wire glasses, with the other man's moustache on the same face. The two briefs were merged into one person and the shot is the reference photograph's framing, not the one that was asked for. He is not wearing a sash you can see either. Shown rather than described because this beat has never had a single picture on this page and a failure with pixels is worth more than a fault list.",
                 diff="First time this beat has been drawn on the stack that made the guard you approved. The failure is useful and it corrects our own reasoning: the spec argued the reference could not impose its layout here because a two-figure medium shot is nothing like a face close-up. It imposed anyway. So a tight-crop reference wins the composition on its own, whatever is asked for — and the next rung is already named, an adapter scoped to one block instead of all of them, which is the standard way to take identity from a reference without taking its framing. THE MOUSTACHED MAN IS ON LOAN AND NOT CAST: guard 2 is still your call at /review/ep2-guardcast2-0822 and nothing here decides it.",
                 src="pipeline/jobs/ep2-b05-guards-f-0822.yaml + taste/refs/guard1-canon-founder-0822-sq.png"),
        ],
    ),
    6: dict(
        goblin=False,
        faults=[
            "The bark board is the wrong size. Three of four clauses pass and that one fails. \u2014 ANSWERED IN A PLATE THIS MORNING, not yet in a clip: see the top picture below.",
            "1.9 s of picture in a 6.5 s slot — 4.5 s of this beat is one frozen frame. It is the biggest ratio in the episode.",
        ],
        wins=["The freeze is a clean freeze. An earlier cut had this window turning the board over, back, and over again; that is gone."],
        faults_from="ship-manifest.yaml beat 6 + pipeline/jobs/ep2-b06-scene-0814r.yaml",
        candidates=[
            dict(file=f"{CAND_URL}/06-the-clipboard-LTX-boardmotion-0822.mp4",
                 poster=f"{POSTER_URL}/06-the-clipboard-LTX-boardmotion-0822.jpg",
                 label="THIS BEAT'S FIRST REAL CLIP — he reads the board, and the board stays small", tag="warn",
                 verdict="He holds the bark board in both hands, brings it up, and reads off it — his lips move, a hand comes up to the board's face, and by halfway there are MARKS ON IT, so it reads as a thing with writing on it rather than a blank slab. THE BOARD NEVER INFLATES. That is the beat's oldest fault and the biggest risk in this render, and it did not fire: it is the same hand-sized tablet in the last frame as in the first. And there are 5.0 s of picture in the 6.5 s slot instead of 1.9 s, so the held frame at the end drops from 4.5 s to about 1.4 s. TWO FAULTS, BOTH REAL. The camera PUSHES IN over the first second and the colour warms with it — the shot you see at the end is closer and sunnier than the picture it started from, and the instruction said the frame never moves. And the last third is nearly still again: almost all the movement is in the first half.",
                 diff="First time this beat has been asked to move off a plate that contains a board — every previous attempt asked a man to read an object that was not in the picture. The board is DRAWN into the frame at 160 px wide and settled in, and the reading action is worded with a COUNT in it (his fingertip runs down the board twice), which is the lever that took another beat from 89 dead frame-pairs out of 104 down to 52 this morning. Measured here: 55 of 120 pairs barely move, against the shipped take's 19 of 45 — comparable, but this clip spends its motion early and the old one spread it out. Not offered as a swap; offered because this beat has never had a picture of the thing it is about.",
                 src="pipeline/jobs/ep2-b06-boardmotion-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-boardnat-r3-0822.jpg", still=True,
                 label="a PLATE — a HAND-SIZED bark board, held and read. This is the beat.", tag="warn",
                 verdict="A grown man alone in a summer field, head down, reading off a small slab of bark held in both hands at chest height. The board is about as wide as his own head — hand-sized, which is what this beat has always asked for — with grain across its face and a torn edge, and he is unchanged behind it: same hair, same round glasses, same daylight. Nothing is glowing and nothing is oversized. WHAT IS LEFT is small and cosmetic: a soft crease down the middle still makes it read for a moment like an open book rather than one piece of bark. Still a plate, not a clip — the motion render is the next thing, and this beat's other fault (4.5 s of its 6.5 s slot is one frozen frame) is a question that has never been askable until there was a plate with the object in it.",
                 diff="Two changes from the picture below it, and both were measured rather than guessed. The board is 160 px wide instead of 240 — I had the size guard the WRONG WAY ROUND. This beat's fault is that the prop INFLATES: its own definition says 'hand-sized and readable' and the job that shipped the current take says 'no bigger than his own forearm' and banned 'giant board, oversized board' and still failed to hold it. I built the tool with that as a floor instead of a ceiling and drew a shield. Corrected in the tool, not in a note, so it cannot come back. And the settling pass runs at the stronger setting the picture below established.",
                 src="pipeline/jobs/ep2-b06-boardnat-r3-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-boardnat-r2-0822.jpg", still=True,
                 label="the same board TOO BIG — kept, because it is what proved the surface setting", tag="fail",
                 verdict="OVERSIZED, AND THAT IS MY ERROR RATHER THAN THE MODEL'S — this slab is as wide as his shoulders, which is the same fault the clip already has, pointing the other way. Shown because it is what proved the ONE THING that carried into the picture above: the slab here has WOOD IN IT — a warm grain running across the face, a torn irregular edge, a bark colour rather than a flat brown fill. It has not moved, it has not narrowed, it is not glowing, and he is unchanged behind it. WHAT IS LEFT, and it is small: a soft crease down the middle makes it read for a second like an open book rather than one piece of bark. Not in the cut yet — this is a still, and the motion render off it is the next thing.",
                 diff="One number against the picture below IT: the settling pass went from 0.30 to 0.45. That was written into the previous attempt's notes before it ran, as the thing to try if the board came back flat. It did come back flat, and this fixed it. The finding is worth more than the beat: every previous use of this pass has settled a PLANT, and 0.30 is enough for a leaf; a hard-edged made object needs more. The board itself is byte-identical between the two — same drawing, same width, same place.",
                 src="pipeline/jobs/ep2-b06-boardnat-r2-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-boardnat-0822.jpg", still=True,
                 label="the same board at the old setting — kept so the one number is visible", tag="fail",
                 verdict="SUPERSEDED BY THE PICTURE ABOVE, and shown because the whole difference between the two is one number. Everything structural is already right here: the board is as wide as his shoulders, in both hands, at chest height, not a clipboard, not glowing, and he is unchanged behind it. WHAT IS WRONG IS THE SURFACE: it reads as a flat piece of card with ruled lines on it rather than as a rough slab of bark, and the torn edge looks cut rather than broken. The light pass that turns a drawn leaf into a drawn leaf did almost nothing to it \u2014 which was written down as a possible outcome before the job ran, and the reading is that a hard-edged made object needs a stronger pass than a leaf does. One more round, and it is a number rather than a redraw.",
                 diff="The board is DRAWN into the picture in software and then settled in with the same light pass beats 12, 16, 19 and 21 use, instead of being asked for from a conditioning net. Its width is a number \u2014 240 px against a 220 px shoulder floor \u2014 and the tool refuses to write the frame if the board is too narrow, if it does not sit in his hands, or if it rises above his chin. That is the whole reason to do it this way: 'the wrong size' is the fault, and a size is the one thing a drawing can guarantee and a sentence cannot.",
                 src="pipeline/jobs/ep2-b06-boardnat-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-pose-r4-0822.jpg", still=True,
                 label="a PLATE — this morning, and it is the best picture this beat has ever had", tag="warn",
                 verdict="A whole grown man, standing in a bright field, head bowed over his own hands with his fingers laced together. Dark cropped hair, round wire-rim glasses, cream shirt — he is the man you picked, from words alone, with no reference photograph anywhere in the job. No night, no glowing ball, no plank standing in front of him, no head-and-shoulders crop. WHAT IS MISSING IS THE BOARD, AND THAT IS ON PURPOSE: his hands are empty because the next step needs clean pixels to draw into. Not a candidate for the cut on its own — it is the picture the board gets painted onto, and that job is on the card as you read this.",
                 diff="The one edit is that the second ControlNet — the one that was supposed to draw the board — was TAKEN OUT rather than tuned again. Three attempts bracketed its strength twice and the rectangle's position twice, and read together they say the same thing three ways: this kind of net draws a white stroke as LIGHT. So the picture below is where that route stops. The board now comes from the same tool that gave beats 16 and 19 their sapling: it is drawn into the frame in software at a width measured in pixels — which matters, because 'the bark board is the wrong size' is this beat's actual fault and a size is the one thing a drawing can guarantee.",
                 src="pipeline/jobs/ep2-b06-pose-r4-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-pose-r3-0822.jpg", still=True,
                 label="a PLATE — round three, and it went backwards. Shown, and the route stops here.", tag="fail",
                 verdict="A glowing white square on a plinth, with the man reduced to a dark shrouded shape behind it and no face at all. Round three moved the drawn rectangle up so it sat between his hands instead of hanging below them — and the net drew the rectangle itself, as a LIT PANEL, right where his chest was, and lost the figure to it. Worse than round two on every count.",
                 diff="This is the third and last attempt at getting the board out of a drawn rectangle, and the three of them together say something clear enough to stop on: at low strength no board arrives, at high strength the rectangle is drawn as a glowing object rather than read as a slab, and moving it over his chest lets it eat the figure. That is the same behaviour the beat-08 lane measured when a drawn skeleton came back as glowing limbs — this kind of net renders a white stroke as light. THE ROUTE THAT SHOULD HAVE THE OBJECT IS THE ONE THIS TREE ALREADY HAS FOUR PASSES ON: draw the bark slab into a finished plate in software and settle it in with a light pass, which is how beats 16 and 19 got their sapling. Round one's frame already has the man standing in the field correctly — it needs a board painted into his hands, not a fourth conditioning setting. That is the handover, and it is the same tool beats 12 and 21 are waiting on.",
                 src="pipeline/jobs/ep2-b06-pose-r3-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-pose-r2-0822.jpg", still=True,
                 label="a PLATE — round two of the drawn method. THE BOARD ARRIVES.", tag="warn",
                 verdict="Three of the four things wrong with the frame below have moved, on two edits that its own notes named in advance. The sky is DAYLIGHT instead of night. A big slab of dark wood is now IN THE PICTURE, which no attempt on this beat had ever produced. He is still the man you picked — dark cropped hair, round wire glasses, an adult, standing in grass. WHAT IS STILL WRONG: the slab stands in front of him like a post instead of being HELD, and his hands have dropped to his sides; there is a hot glow across his chest that nothing asked for; and there is a large dark triangular mass behind him that is not a hedgerow. Not a candidate for the cut. Put up because this beat has never had a picture with a board in it and now it has one.",
                 diff="Two edits, both written into the previous attempt's notes before it ran. The light went into the words as something to ASK FOR rather than something to ban — the frame below came back at night with 'dark' and 'night' banned and no daylight requested, which is the eighth time in this tree that banning a thing has failed to place its opposite. And the drawn rectangle for the board was applied harder, from half strength to most. The board arrived and it arrived TOO LITERALLY — the net anchored on the drawn rectangle's top edge and grew a plank downward out of it. The next move is on the drawing, not the words: put the rectangle in his hands rather than in front of him, and give it the proportions of a slab held up to read.",
                 src="pipeline/jobs/ep2-b06-pose-r2-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-pose-0822.jpg", still=True,
                 label="round one of the drawn method — it put him in the field, at night, with no board", tag="warn",
                 verdict="A WHOLE MAN STANDING IN A FIELD, at the size he was drawn at, hands together at chest height with his head down over them. That is the thing the two attempts below could not do at any setting, and it is the beat's framing. He is also unmistakably guard 1 — dark hair, round wire glasses, an adult — with NO reference photograph anywhere in the job; that came out of the words alone. TWO THINGS ARE WRONG AND BOTH ARE ALREADY FIXED IN THE NEXT ONE. It is NIGHT, which is my error rather than the model's: the words banned 'dark' and 'night' and never once asked for daylight, and this tree has now watched a negative fail to place a thing eight times. And there is no board — he is cupping a GLOW. His hands are in exactly the right place and nothing rectangular arrived in them.",
                 diff="No reference image at all. The picture comes from two drawings instead: a stick-figure skeleton, five heads tall, that sets where he stands and how he holds his hands, and a second drawing of one rectangle exactly as wide as that skeleton's shoulders for the board. The man comes from the words. Both drawings are in the repo beside the frame so they can be looked at. The board's drawing was deliberately applied at half strength to avoid a literal white box floating in the field, and the spec said in advance that if no board arrived the answer was to raise it — so round two raises it and puts the morning light in the positive, which is the correction the failure earned.",
                 src="pipeline/jobs/ep2-b06-pose-0822.yaml + pipeline/author_b06_guard_pose_0822.py"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-guard1-content-0822.jpg", still=True,
                 label="a PLATE — second attempt, and it fails the same way as the first", tag="fail",
                 verdict="The man is right — dark cropped hair, round wire glasses, a grown man, drawn in the look you approved. Everything else is wrong in the same way as the attempt below: it is a head-and-shoulders close-up with his hands clasped at his chest, and THERE IS NO BARK BOARD IN IT AT ALL. The beat is a man reading a board and the board is the beat's standing fault, so a frame without one cannot answer anything.",
                 diff="One variable against the attempt below: the reference was applied to a single layer of the model for the whole render instead of to every layer for a short burst. The frame barely moved. Both attempts also reproduce the reference photograph's own POSE — his hands are up by his face because they are up by his face in the reference.",
                 src="pipeline/jobs/ep2-b06-guard1-content-0822.yaml"),
            dict(file=f"{POSTER_URL}/06-the-clipboard-PLATE-guard1-w015-0822.jpg", still=True,
                 label="a PLATE — first attempt, this beat's first picture on the ratified guard", tag="fail",
                 verdict="He is unmistakably the man you picked, in the right style, and that is the only good news. It is a face close-up, not the medium shot that was asked for; his hands are clasped at his chest exactly as they are in the reference; there is no bark board, no field, and no sash you can see. Beat 06 has never had a picture on this page and this is the first one, so it goes up even though it fails.",
                 diff="The first time this beat has been drawn on the stack that made the guard you approved, and the spec argued in advance that the reference could not impose its framing here because a man holding a board is nothing like a portrait. It imposed anyway, and then imposed again through the fix. TWO ROUTES ARE NOW CLOSED BY MEASUREMENT, which is worth the six GPU minutes: with this method a tight-crop reference dictates the crop, and neither the timing of the reference nor which layer it touches changes that. The next attempt uses no reference photograph — a drawn skeleton sets the pose and the board, and the man comes from the words, which is measured to draw grown men reliably.",
                 src="pipeline/jobs/ep2-b06-guard1-0822.yaml + taste/refs/guard1-canon-founder-0822-sq.png"),
        ],
    ),
    7: dict(
        goblin=True,
        faults=[
            "The scavenger is dressed in the guard's own pale wrap tunic and white sash, so a beat that has to read \"an official points at a scavenger\" reads as two officials in matching kit.",
            "The goblin has WHITE HAIR, on a character whose canon is bald — plus the guard's round spectacles and a human nose.",
        ],
        wins=["The action lands: the guard raises his own arm at frame 45 and holds the point to frame 96."],
        faults_from="ship-manifest.yaml beat 7 + goblin_design_audit_0820 beats.7",
        candidates=[
            dict(file=f"{POSTER_URL}/07-confiscate-PLATE-pose-0822.jpg", still=True,
                 label="a PLATE — an attempt at the crossover problem, and it FAILED loudly", tag="fail",
                 verdict="The two characters swapped bodies. The tall figure — the one drawn as the guard — came back as a big green goblin with pointed ears, and the short one — drawn as the goblin — came back human with the round wire glasses on. Three more goblin heads are floating in the grass at the edges. Not a candidate for anything; shown because the failure closes a question rather than just wasting three minutes.",
                 diff="No reference photograph, two drawn stick-figure skeletons — a five-head adult on the right and a shorter big-domed one on the left — and the two characters described in words. The DRAWING bound perfectly for the third time tonight: two figures, at the drawn sizes, in the drawn places, with the tall one's arm reaching across to the short one. What the words could not do is say WHICH skeleton is WHICH character. Across three plates tonight that is now measured: one figure alone comes out right, two figures come out as two figures but the descriptions land on the wrong bodies or on both. So the crossover on the clip below is NOT going to be fixed by better wording or by better staging, and the next instrument is the one this repo already built for beat 08 — conditioning each figure separately through a mask cut from these same skeletons. Named, and left for a lane with daylight.",
                 src="pipeline/jobs/ep2-b07-pose-0822.yaml + pipeline/author_b07_twofig_pose_0822.py"),
            dict(file=f"{CAND_URL}/07-confiscate-LTX-b07-w4motion-r2-trim81-0822.mp4",
                 poster=f"{POSTER_URL}/07-confiscate-LTX-b07-w4motion-r2-trim81-0822.jpg",
                 label="BEST AVAILABLE — the sash arrived, the collar did not — tonight, newest", tag="warn",
                 verdict="Same two figures and the same landed point as the clip below, and the WHITE SHOULDER SASH is now on the guard — the one item of his kit the goblin does not own anywhere in the sentence, and the one item that came through. Everything else about the guard's tunic is still the goblin's: the same standing mandarin collar, the same four black frog closures down the front, even though the wording now bans both by name. And he has a POINTED EAR behind the glasses, which nobody had spotted before, so it is not only the costume crossing over — it is the species. Cut at frame 81, where the finger is still on the goblin's cheek. The goblin himself is right: broad dome, small off-white almond eyes with dark pupils, near-horizontal ears, flat mouth.",
                 diff="The wardrobe was rewritten to guard-1 canon at the same level of detail as the goblin's, on the finding that the detailed description wins both figures. Result splits cleanly and the split is the finding: the DISTINCTIVE item landed and the SHARED-CLASS items did not. A sash has no counterpart in the sentence, so there is only one figure it can go on; \"tunic\", \"collar\" and \"buttons\" all have a goblin version three clauses earlier, and naming a second version of a garment that is already described does not move it — it duplicates it. Banning the goblin's version by name did nothing, which is the positive-placement law again from the other side. Next rung is not more wardrobe adjectives: it is per-figure conditioning, or a guard whose kit shares no noun with the goblin's.",
                 src="pipeline/jobs/ep2-b07-w4motion-0822.yaml (re-run --again2b0c48) + taste/refs/guard1-canon-founder-0822.png"),
            dict(file=f"{CAND_URL}/07-confiscate-LTX-b07-w4motion-trim83-0822.mp4",
                 poster=f"{POSTER_URL}/07-confiscate-LTX-b07-w4motion-trim83-0822.jpg",
                 label="the same beat before the wardrobe rewrite — no sash", tag="warn",
                 verdict="For the first time this beat has a guard in it. He is the man you picked — dark cropped hair, round wire glasses, no helmet — he is taller, he raises his arm and his finger ends up aimed at the goblin's face, and the goblin is your goblin: small off-white eyes, dark pupils, broad head, no white hair, no spectacles. Cut at frame 83, where the point is still landing. TWO THINGS STILL WRONG: the guard is wearing the goblin's mandarin-collar tunic instead of his own tan tunic and white sash, and past frame 86 the goblin shrinks out of frame and leaves the guard alone with a stray boot in the grass.",
                 diff="This beat came back with NO GUARD AT ALL on both previous tries, because the wording never PLACED him — a figure this model is not told to put somewhere is a figure it does not draw. He is placed now. The old wording also called him \"one tall armoured city guard in a helmet\", which stopped being the character on 08-22 when you picked the beat-09 close-up; a helmet would also have hidden the hair that ruling is about. Wardrobe is the next thing to fix and it is a wording fix, not a new plate.",
                 src="pipeline/jobs/ep2-b07-w4motion-0822.yaml + taste/refs/guard1-canon-founder-0822.png"),
            dict(file=f"{CAND_URL}/07-evidence-LTX-ep2-b07-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/07-evidence-LTX-ep2-b07-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="fail",
                 verdict="THE GUARD ARRIVED, which nobody expected — a tall armoured guard in a helmet from frame 24, and his arm comes up and is fully aimed by frame 96. But THE GOBLIN IS GONE by then. The last frames are a guard pointing at empty grass.",
                 diff="The wording placed both figures before asking anything of either, and four \"no second figure\" terms were struck from the negative. A prompt cannot summon what its own negative deletes.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/07-confiscate-LTX-ep2-b07-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/07-confiscate-LTX-ep2-b07-tilemotion-s1-0821.jpg",
                 label="age-B seed 1", tag="fail",
                 verdict="No guard anywhere in the clip. His only gesture is hands clasping near the end. The beat's action is absent, not weak.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b07-tilemotion-s1-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/07-confiscate-LTX-ep2-b07-tilemotion-s2-0821.mp4",
                 poster=f"{POSTER_URL}/07-confiscate-LTX-ep2-b07-tilemotion-s2-0821.jpg",
                 label="age-B seed 2", tag="fail",
                 verdict="No guard either, and the motion is close to zero.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b07-tilemotion-s2-0821.yaml", quiet=True),
        ],
    ),
    8: dict(
        goblin=True,
        faults=[
            "Nobody has ever judged this clip. There is no verdict for it, and there never was one.",
            "Both figures come back green with pointed ears, because \"green skin\" lands on both bodies in the prompt.",
            "He reads as a child — small body, big head, closed sad eyes, buttoned coat. The pre-ruling round one.",
        ],
        wins=[],
        faults_from="ship-manifest.yaml beat 8 + goblin_design_audit_0820 beats.8",
        candidates=[
            dict(file=f"{CAND_URL}/08-inside-him-LTX-ep2-b08-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/08-inside-him-LTX-ep2-b08-w4motion-0822.jpg",
                 label="your goblin's face, and the shrink reads — tonight, newest", tag="pass",
                 verdict="He starts standing with his arms at his sides and ends with his hands clasped low in front of him and his head down — he gets smaller, which is what this beat is. Canon face for all 105 frames: small off-white eyes with dark pupils, broad head, ears low and sideways, and the flush stays on his cheeks. Modest motion, but it is the right motion and it does not stop halfway.",
                 diff="New plate on the corrected eye, and the sentence describing him no longer says \"slit pupils\". The action is this beat's own, unchanged.",
                 src="pipeline/jobs/ep2-b08-w4motion-0822.yaml + review/ep2-goblin-eye-0822"),
            dict(file=f"{CAND_URL}/08-evidence-LTX-ep2-b08-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/08-evidence-LTX-ep2-b08-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="pass",
                 verdict="7 of 7, the only clean sweep of the seven. Hands reach the belly by frame 48, head bowed by 57 — the action completes early. Collar, frogging, shirt, shorts, cuffs and boots all hold, and the waist boundary survives, which is the fault this beat used to have. THE COST, and it is yours to price: from about frame 57 to the end, over half the clip is the top of his bowed head. It reads as looking down; his face is small.",
                 diff="Canon goblin plate, 105 frames, one figure. A first read of a tight crop called this the featureless green head; a taller crop shows the features ARE drawn, foreshortened at the bottom edge of a bowed skull.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/08-inside-him-LTX-ep2-b08-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/08-inside-him-LTX-ep2-b08-tilemotion-s1-0821.jpg",
                 label="age-B seed 1", tag="fail",
                 verdict="The head goes uniformly bright yellow-green with no features at all from frame 55, while sitting roughly upright. A real dissolve.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b08-tilemotion-s1-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/08-inside-him-LTX-ep2-b08-tilemotion-s2-0821.mp4",
                 poster=f"{POSTER_URL}/08-inside-him-LTX-ep2-b08-tilemotion-s2-0821.jpg",
                 label="age-B seed 2", tag="fail",
                 verdict="Same failure at the same frame, plus a detached brow bar floating below the head from frame 65.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b08-tilemotion-s2-0821.yaml", quiet=True),
        ],
    ),
    9: dict(
        goblin=False,
        faults=[
            "His hand changes pose mid-shot: it slides from covering his mouth to resting along his jaw, and the fingers merge into a thumb and a mitt rather than four drawn fingers. It is a move, and it is not a move the script asked for.",
            "One eye is squinted from the first frame. It opens in the middle of the shot and narrows again by the end.",
            "The picture is a 1.45x enlargement of a wider plate, not a native close-up.",
        ],
        wins=[
            "This beat played over a black card in every cut before 08-21. It now has a face on the episode's biggest laugh.",
            "The hand is present and readable at every checked frame of the slot, and both round spectacle rims survive the whole clip — the take this replaced lost a rim by frame 8 and nobody had noticed.",
        ],
        note="He reads young in close-up. You ruled on that on 08-20 — \"they should look like grown men. yes. dumb grown men.\" — so it is a known, accepted fact rather than an open question.",
        faults_from="ship-manifest.yaml beat 9 + pipeline/jobs/ep2-b09-r2s2-m1-0821.yaml verdict_0821",
        candidates=[
            dict(file=f"{CAND_URL}/09-the-pause-LTX-ep2-b09-r2s2-c1-0821.mp4",
                 poster=f"{POSTER_URL}/09-the-pause-LTX-ep2-b09-r2s2-c1-0821.jpg",
                 label="same batch, cell c1", tag="pass",
                 verdict="Also a pass. The hand holds the whole slot and the frame is nearly as locked. It loses to the clip in the cut on acting — the face does less.",
                 diff="Same crop, a different sentence describing the hand.",
                 src="pipeline/jobs/ep2-b09-r2s2-c1-0821.yaml"),
            dict(file=f"{CAND_URL}/09-the-pause-LTX-ep2-b09-r2s2-c2-0821.mp4",
                 poster=f"{POSTER_URL}/09-the-pause-LTX-ep2-b09-r2s2-c2-0821.jpg",
                 label="same batch, cell c2", tag="fail",
                 verdict="His mouth is open at frames 50, 70 and 93, on a silent thinking beat. Best hand numbers in the batch and it does not matter.",
                 diff="Different seed.", src="pipeline/jobs/ep2-b09-r2s2-c2-0821.yaml", quiet=True),
            dict(file=f"{CAND_URL}/09-the-pause-LTX-ep2-b09-r2s2-c3-0821.mp4",
                 poster=f"{POSTER_URL}/09-the-pause-LTX-ep2-b09-r2s2-c3-0821.jpg",
                 label="same batch, cell c3", tag="fail",
                 verdict="The longest hand hold in the batch, bought by stopping. Frames 1 to 70 are one held picture and then it jumps.",
                 diff="Different seed.", src="pipeline/jobs/ep2-b09-r2s2-c3-0821.yaml", quiet=True),
            dict(file=f"{CAND_URL}/09-the-pause-LTX-ep2-b09-r2s2-m2-0821.mp4",
                 poster=f"{POSTER_URL}/09-the-pause-LTX-ep2-b09-r2s2-m2-0821.jpg",
                 label="same batch, cell m2", tag="fail",
                 verdict="Mouth opens, same as c2 and at the same seed — which is how we know the open mouth belongs to the seed and not to the wording.",
                 diff="Different seed.", src="pipeline/jobs/ep2-b09-r2s2-m2-0821.yaml", quiet=True),
        ],
    ),
    10: dict(
        goblin=False,
        faults=[
            "The two things they are holding shapeshift into one. Two separate boards at the first frame — a grey-blue one and a dark teal one — drifting together by frame 48 and gone by frame 72, leaving a single tan board held between them.",
            "He holds the blank board out to the CAMERA instead of to his partner. From frame 65 to 96 it is flat to the lens, so his partner would be seeing it edge-on. That is the clause that IS the beat, and it fails.",
        ],
        wins=[],
        note=(
            "Your note found a bug in the sentence, not in the picture. The word \"board\" was in "
            "that prompt five times and every one of them was the NEAR guard's — his partner was "
            "never given anything to hold. So the plate handed the model two boards, the words "
            "handed it one, and it resolved the disagreement by deleting one. The partner now has "
            "his own board, named and coloured, and the same sentence turns the blank side toward "
            "him instead of toward the lens."),
        faults_from="ship-manifest.yaml beat 10 + pipeline/jobs/ep2-b10-pairB-0814.yaml + founder note 2026-08-22",
        candidates=[
            dict(file=f"{CAND_URL}/10-no-form-LTX-b10-twoboards-trim79-0822.mp4",
                 poster=f"{POSTER_URL}/10-no-form-LTX-b10-twoboards-trim79-0822.jpg",
                 label="TWO BOARDS THAT STAY TWO — tonight, newest", tag="pass",
                 verdict="Two separate boards the whole way through: the near man's grey-blue one and his partner's dark teal one, in different hands, never touching and never merging. Both men stay in frame, nobody walks off, and the boards stay hand-sized. Cut at frame 79, which is 3.3 s of a 4.1 s slot, so the assembly will hold the last frame for about eight tenths of a second.",
                 diff="Two changes, both in the wording, no new plate. His partner was given his OWN board — named, and named a different colour, because the two boards in the picture already ARE different colours and a difference the sentence admits to is one the model has a reason to keep. And the blank side of the near man's board is now angled at his partner rather than flat to the camera, which is your older note on this beat.",
                 src="pipeline/jobs/ep2-b10-twoboards-0822.yaml + review/ep2-beats-0821/candidates/10-no-form-LTX-b10-twoboards-trim79-0822.mp4.meta.yaml"),
            dict(file=f"{CAND_URL}/10-no-form-LTX-b10-twoboards-full-0822.mp4",
                 poster=f"{POSTER_URL}/10-no-form-LTX-b10-twoboards-full-0822.jpg",
                 label="the same take, uncut — the merge comes back at the end", tag="warn",
                 verdict="Identical to the clip above for its first 79 frames. Between frame 78 and frame 86 the teal board disappears and the two of them end up holding one big pale board between them — the old fault, arriving late instead of early. Shown so the cut above is not hiding anything: this is what the last second looks like.",
                 diff="No trim. Same render, all 121 frames.",
                 src="pipeline/jobs/ep2-b10-twoboards-0822.yaml"),
        ],
    ),
    11: dict(
        goblin=False,
        faults=[
            "Guard B turns his face to camera in a beat whose whole point is backs turned.",
            "It has no standing verdict. An earlier pass was withdrawn over \"total identity collapse away from the plate\" across frames 16 to 21, and nothing has passed it since.",
        ],
        wins=[],
        note="STATUS, 2026-08-22: nothing was rendered for this beat tonight and nothing is queued for it, and the reason is that its obvious next move was already tried and already failed. An earlier pass was withdrawn over an identity collapse across frames 16 to 21, and that window was later explained by a compression setting on the starting image rather than by the plate \u2014 so on 08-19 the beat was re-run at the corrected setting. IT CAME BACK WORSE: guard B still turns his face to camera in the same window, and guard A now walks out of the left edge and is gone for the last twelve frames. That run also settled something larger, which is why it was worth it: changing that setting does not CLEAN a take, it RE-ROLLS it into a different one. So beat 11 has no cheap lever left. Its fault \u2014 a guard turning to camera in a beat whose point is backs turned \u2014 is a staging problem and needs a plate authored for it, and that is a piece of work rather than a re-run. Named honestly, not scheduled tonight.",
        faults_from="ship-manifest.yaml beat 11",
        candidates=[],
    ),
    12: dict(
        goblin=False,
        faults=[
            "The sapling GROWS across the shot — its tip climbs 140 px, 11% of the frame height, steadily — against an approved line that says \"perfectly still\".",
        ],
        wins=["Fixed on 08-21: the clip used to open on 13 frames of a completely different, warmer shot — four or five big pointed leaves — which breaks the canon leaf shape. Those frames are cut, and nothing after them was touched."],
        note=(
            "STATUS, 2026-08-22 MORNING \u2014 THE DRAWING IS DONE. The two leaves in the clip "
            "below are PERFECT ROUND DISCS, and canon since your 08-17 ruling is \u201caverage "
            "leaves\u201d \u2014 the shape anyone draws when you say leaf. That is now fixed in the "
            "picture rather than argued about in a prompt: the old plant was erased out of the "
            "frame in software, two ordinary leaves were drawn in its place, and a light pass "
            "settled them into the frame's own line and shading. The plate is below. A motion "
            "render off it is on the card as you read this and will appear here as a candidate. "
            "SAID PLAINLY: erasing two 250-pixel discs left a soft horizontal smear across the "
            "cloud bank behind the plant, and the light pass did not remove it \u2014 that was "
            "written down as a likely outcome before the job ran, and it is the one thing about "
            "the new plate that is worse than the old one. THE MOTION RENDER HAS LANDED and it is the first candidate this beat has ever had \u2014 see below."),
        faults_from="review/ep2-picks/done-definitions.yaml beats.12 + review/ep2-b12-trim-0821/verdict-0821.yaml",
        candidates=[
            dict(file=f"{CAND_URL}/12-related-LTX-leaf-0813.mp4",
                 poster=f"{POSTER_URL}/12-related-LTX-leaf-0813.jpg",
                 label="THIS BEAT'S FIRST CANDIDATE — canon's two leaves, and they last the whole clip", tag="warn",
                 verdict="TWO AVERAGE LEAVES ON ONE STEM IN EVERY FRAME, first to last. That is the fault this beat has been sitting on and it is gone: no discs, no third leaf, no second plant, and the plant stays rooted in the same place with the camera locked the whole time. WHAT IS NOT FIXED, AND IT IS THE SAME FAULT IN A NEW FORM: your line says 'perfectly still' and this is not still. The clip in the cut has the plant GROWING upward; this one has the two leaves opening, spreading, drooping and lifting again over the five seconds. It is prettier and it is arguably more alive, but it is still motion where the script asks for none, so this is your call rather than mine. AND THE SMEAR SURVIVED: the soft horizontal band across the cloud bank, left by removing the old discs, is still there in every frame — a hundred and twenty-one frames of LTX did not repaint it.",
                 diff="Same action sentence, byte for byte. Same seed, same size, same frame count, same everything — the ONLY change is the starting picture, which is now the plate above with canon's leaves drawn into it. That is deliberate: neither this beat's wording nor its timing has ever been the problem, so changing them at the same time would make it impossible to say which edit did what. What this proves beyond the beat is that a hand-drawn plant survives a full motion render at the right shape, which is the thing beats 16, 20 and 21 are all waiting on.",
                 src="pipeline/jobs/ep2-b12-leafmotion-0822.yaml"),
            dict(file=f"{POSTER_URL}/12-related-PLATE-leafcanon-0822.jpg", still=True,
                 label="a PLATE — canon's two average leaves, drawn in. This morning.", tag="warn",
                 verdict="Two ordinary leaves on one thin stem, in the grass, against the same clouds. Not discs. The plant is where it was and the sky, the grass and the framing are the clip's own \u2014 this is the first frame of the take you are already shipping with exactly one thing changed. THE FAULT IT CARRIES: a soft horizontal band across the cumulus where the two old discs were removed. It was predicted before the job ran and it is inside the region the pass was allowed to touch, so the pass had its chance at it and did not take it.",
                 diff="Not a re-render and not a re-wording. The leaf shape was closed as a wording problem by measurement a week ago \u2014 the strongest sentence available returned 0 of 16 frames with two correct leaves \u2014 so the plant is DRAWN into the picture and then finished by a light pass, which is the route that has now worked five times. The motion render off this plate is queued.",
                 src="pipeline/jobs/ep2-b12-sapnat2-0822.yaml"),
        ],
    ),
    13: dict(
        goblin=True,
        faults=[
            "This is the round child you ruled against on 08-19.",
            "It grows a mature forked tree and he climbs it, against your ruling that the sapling is tiny — \"thats ridiculous, lmao. the sapling is tiny\".",
        ],
        wins=[],
        note="A seated take on a real 60 px seedling was swapped in on 08-20 and you ruled on its best frame — \"this is one of the images where the goblin looks like an adult, which is wrong\". A second swap went in on 08-21 and came back out with the rest of the age-B wave. So this beat has been swapped and reverted twice and is back to the original.",
        faults_from="ship-manifest.yaml beat 13 superseded_why_0820",
        candidates=[
            dict(file=f"{CAND_URL}/13-the-shade-LTX-ep2-b13-repeat-0822.mp4",
                 poster=f"{POSTER_URL}/13-the-shade-LTX-ep2-b13-repeat-0822.jpg",
                 label="tonight, newest — an attempt to fill the dead half, and it FAILED", tag="fail",
                 verdict="Worse than the take below it, and shown because the failure says something. The rewrite asked him to settle TWICE instead of once, on the strength of that wording having just fixed beat 17. He settles once — faster and harder than before — and then stops even earlier: frames 40 to 90 move by 0.04 to 0.09, which is a deader freeze over a longer stretch, and there is a jump at the very end. 81 of 104 frame pairs under 0.5 against the earlier take's 76.",
                 diff="The reason it failed is worth more than the clip. A settle is not a repeatable action. You cannot settle down twice from one pose without coming back up in between, and the prompt forbids exactly that — your ruling that HE NEVER RISES is in the sentence and was kept there. So the two instructions contradict each other and the model resolved it by doing one settle and stopping. The rule this leaves behind is narrower and truer than the one it was filed on: a counted repeat fills a clip only when the action can actually happen twice. A brush can. A settle cannot.",
                 src="pipeline/jobs/ep2-b13-repeat-0822.yaml"),
            dict(file=f"{CAND_URL}/13-the-shade-LTX-b13-w4curl-trim58-0822.mp4",
                 poster=f"{POSTER_URL}/13-the-shade-LTX-b13-w4curl-trim58-0822.jpg",
                 label="BEST AVAILABLE — the curl-down you asked for, on your face — tonight, newest", tag="warn",
                 verdict="This is your story ruling for the beat drawn out: he starts on his feet, folds all the way down, ends with his knees up and his hands between them, and he never rises. That is the beat's done_when — 'he ends FOLDED SMALL, knees up' — and no take before this one reached it. Your face holds every frame: broad dome, off-white almond eyes with dark pupils, near-horizontal pointed ears, flat mouth, sage mandarin collar. TWO THINGS TO KNOW. There is no sapling in the frame, so 'in the sapling's shade' is not delivered, only the folding. And the full take stops dead after this cut: frames 60 to 99 move by 0.03 to 0.15 against 3.5 to 5.0 earlier — forty frozen frames — so it is cut at 58, where the fold has just completed.",
                 diff="Two variants of this beat were rendered tonight off the same corrected plate; this is the CURL one, written to your ruling that he goes down small and stays down. The other is directly below and sits upright with his arms crossed. Which pose the beat wants is yours, not ours — the only thing measured here is that both hold the face.",
                 src="pipeline/jobs/ep2-b13-w4motioncurl-0822.yaml"),
            dict(file=f"{CAND_URL}/13-the-shade-LTX-ep2-b13-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/13-the-shade-LTX-ep2-b13-w4motion-0822.jpg",
                 label="the same plate, upright pose — the wave's first clip", tag="warn",
                 verdict="The clip that proved the corrected face survives motion: the approved head holds all 105 frames and the eye never drifts back to a green iris, which is what the whole re-plate was for. Its weakness is the opposite of the curl take's — he barely moves. Shown so the pose choice is a real A/B and not a description.",
                 diff="Same plate, same recipe, this beat's existing upright action carried verbatim. It was queued alone as the sample before the other nine motion jobs were released.",
                 src="pipeline/jobs/ep2-b13-w4motion-0822.yaml"),
            dict(file=f"{CAND_URL}/13-evidence-LTX-ep2-b13-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/13-evidence-LTX-ep2-b13-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — yesterday", tag="pass",
                 verdict="6 of 7. No dissolve anywhere in 105 frames — the same creature start to finish, ears large and lateral, slit pupil visible whenever the lids are open, collar and shirt and waist all holding. The gap: the head-tip starts around frame 72 and is still travelling at the last frame the trim keeps, so inside the slot it reads as begun rather than finished. And his eyes CLOSE from about frame 48 and stay closed — defensible for exhaustion turning into relief, but the canon eye is only legible for the first two seconds.",
                 diff="Canon goblin plate. The previous wave's best b13 seed lost its face to a featureless green head at frame 65; this one does not.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/13-the-shade-LTX-ep2-b13-tilemotion-s2-0821.mp4",
                 poster=f"{POSTER_URL}/13-the-shade-LTX-ep2-b13-tilemotion-s2-0821.jpg",
                 label="age-B seed 2 (was swapped in, then reverted)", tag="warn",
                 verdict="Face holds all 121 frames. Through the slot he is seated, head down, eyes closed. Its own expressive lift — head up, mouth open — starts 0.06 s AFTER the slot ends, so the cut would never show it.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b13-tilemotion-s2-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/13-the-shade-LTX-ep2-b13-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/13-the-shade-LTX-ep2-b13-tilemotion-s1-0821.jpg",
                 label="age-B seed 1", tag="fail",
                 verdict="It carries a real smile for the first 44 frames — the thing this beat was re-rendered for — and then its face becomes a featureless green head from frame 65, inside the slot.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b13-tilemotion-s1-0821.yaml", quiet=True),
        ],
    ),
    14: dict(
        goblin=True,
        faults=[
            "Two of its clauses fail and it is still the best footage this beat has. Three separate measurements say what is left is a taste gap, not a broken mechanism.",
            "The ears are long tapering elf spikes where your tile has short low flanges, and he wears a red-and-white striped scarf instead of the purple cowl.",
        ],
        wins=["On design this is one of the two closest matches to your tile in the whole episode. Eyes, dome, two-tone skin and folded stance all match; the ears are the whole gap."],
        faults_from="ship-manifest.yaml beat 14 + goblin_design_audit_0820 beats.14",
        candidates=[
            dict(file=f"{CAND_URL}/14-the-defense-LTX-b14-w4motion-trim95-0822.mp4",
                 poster=f"{POSTER_URL}/14-the-defense-LTX-b14-w4motion-trim95-0822.jpg",
                 label="BEST AVAILABLE — the beat's two clauses, both of them — tonight, newest", tag="warn",
                 verdict="Beat 14 needs fingers at the dirt AND the glancing, with the embarrassment readable, and this take has all three: his hands are in the earth from the first frame to the last, the blush sits on both cheeks the whole way, and from about frame 80 he turns his face away and shuts his eyes. Your face throughout — broad dome, off-white almond eyes with dark pupils, near-horizontal ears, mandarin collar. The ears are the short low kind here, not the long elf spikes this beat has been faulted for, and there is no striped scarf. WHAT IS CUT AND WHY: at frame 102 the head keeps rotating until there is no face in frame at all, just the back of a bald head and one ear — the biggest single jump in the clip by a factor of three. Cut at 95, where the look-away has started and the face is still legible.",
                 diff="A new plate on the corrected eye, plus this beat's own action carried unchanged, plus a 'second goblin, crowd' negative — the first pass drew a second goblin in the grass at the right edge and this one is single-figure. The ears and the scarf were faults of the OLD plate; both are gone with it.",
                 src="pipeline/jobs/ep2-b14-w4motion-0822.yaml"),
        ],
    ),
    15: dict(
        goblin=True,
        faults=[
            "His face sits about 160 px from the leaves where the script says \"a hand's width\". No motion pass can fix that; it is baked into the plate.",
            "The last three frames freeze.",
        ],
        wins=[
            "This is beat 15's first footage in any cut, and the first take in seven attempts where his face is actually AT the two leaves, which is what the beat IS.",
            "On design it is the second-best match to your tile in the episode: blank white eyes, no nose bridge, one lipless line, big chartreuse dome, seated small and folded, barefoot. Its one named break is costume — a plaid blanket-cloak instead of the purple cowl.",
        ],
        faults_from="ship-manifest.yaml beat 15 + goblin_design_audit_0820 beats.15",
        candidates=[
            dict(file=f"{CAND_URL}/15-good-listener-LTX-ep2-b15-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/15-good-listener-LTX-ep2-b15-w4motion-0822.jpg",
                 label="tonight's re-render — FAILS, and it is shown so the failure is on the record", tag="fail",
                 verdict="Your face arrives on this beat for the first time and then the clip throws it away. For fifty frames he kneels with his hands in the grass and almost nothing moves — 0.08 average frame-to-frame, a still with a runtime — and his mouth opens once around frame 40. Then from frame 50 the whole figure ROTATES until it is UPSIDE DOWN, and it stays upside down, frozen, to the last frame. It also fails the beat's other half: there is no sapling anywhere in it, and the definition says both of them in shot is the whole point.",
                 diff="Same corrected plate and same one-phrase eye swap as every other clip in tonight's wave. This is the second beat to topple — beat 04 did it earlier and was fixed by taking the positional clause out of the action. Beat 15's action was audited in that same pass and marked clean, so this one is NOT the same cause and needs its own look before it is re-fired. The clip already in the cut is unaffected and stays.",
                 src="pipeline/jobs/ep2-b15-w4motion-0822.yaml"),
            dict(file=f"{CAND_URL}/15-good-listener-LTX-mid-0820.mp4",
                 poster=f"{POSTER_URL}/15-good-listener-LTX-mid-0820.jpg",
                 label="the other seed of the same recipe", tag="warn",
                 verdict="It leans in and stays there, and pays for it with a drooped leaf pair and a dead eye.",
                 diff="Same recipe, different seed. This is the swap named in the ship manifest's own one-line reversal for beat 15.",
                 src="ship-manifest.yaml beat 15 veto_in_one_line"),
        ],
    ),
    16: dict(
        goblin=True,
        faults=[
            "The goblin behind the plant is the superseded adult-man design. He is blurred depth and it barely reads at that scale — but it is the old design and this page says so rather than letting depth cover for it.",
            "Your eye goes to his face before it goes to the plant, because he is a face and the plant is a shape.",
            "43% of this beat is a held final frame — the voice line outruns the picture by 3.7 s.",
        ],
        wins=[
            "This is beat 16's first footage of any kind, and it retired the episode's last black card.",
            "Seven of seven on its own bar after a three-frame trim: the camera is locked, the plant holds, exactly two leaves survive to the last frame — the first time canon's two-leaf sapling has survived a whole motion render in this tree — he is visibly talking, and the plant is still the subject.",
        ],
        note=(
            "STATUS, 2026-08-22 MORNING \u2014 THE TRADE BELOW WAS ATTEMPTED AND IT DID NOT WORK "
            "YET, and the reason is specific enough to be worth telling you. The obvious move is "
            "to draw the two-leaf plant into the new plate, which is exactly what was done for "
            "beats 12 and 21 this morning and what has worked five times. It fails on THIS plate "
            "for a reason that has nothing to do with plants: the grass in front of him is a "
            "blown-out blur \u2014 the bright parts of it are almost pure white \u2014 and the "
            "tool builds the plant out of the picture's own greens ON PURPOSE, so that a pasted "
            "shape cannot arrive in a colour the frame does not contain. Given this frame's "
            "greens it draws a WHITE plant, which reads as a ghost over his chest rather than a "
            "seedling in front of him. Two placements were tried and both came back the same. "
            "SO THE HONEST STATE IS: the trade stands \u2014 new face, no plant \u2014 and the "
            "next move is a placement low in the frame where the grass is dark, or this beat's "
            "plate re-rendered without the shallow-focus blur. Not a wording problem, and not "
            "fired on a guess."),
        faults_from="ship-manifest.yaml beat 16",
        candidates=[
            dict(file=f"{CAND_URL}/16-why-LTX-ep2-b16-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/16-why-LTX-ep2-b16-w4motion-0822.jpg",
                 label="tonight's re-render — it fixes the design fault and it costs the plant", tag="warn",
                 verdict="THE CLEANEST MOTION IN THE WHOLE WAVE: not one frame pair in 105 is under 0.5, the median step is 3.04, there is no topple, no dissolve and no frozen tail — he sits with his knees up, his eyes drift from open to half-lidded and back, and the camera moves the whole time. Your face all the way through: broad dome, off-white almond eyes with dark pupils, near-horizontal ears, sage mandarin collar. That answers this beat's first fault, which is that the goblin in the cut is the superseded adult-man design. BUT IT COSTS THE BEAT'S WIN. There is no plant in this clip at all, and what is in the cut is the only render in this tree where canon's two-leaf sapling survived to the last frame. So this is a straight trade and not a replacement: new goblin, no sapling.",
                 diff="New plate on the corrected eye, this beat's own action carried unchanged. The plant was never in the new plate — the re-plate was authored for the FACE and nobody put the sapling back into it, which is the same prompt-summons law that has bitten beats 02, 03 and 20: an object absent from the init cannot be asked for in the motion. Putting the two-leaf plant into this plate is a composite job, not a re-word, and the route for it is proven.",
                 src="pipeline/jobs/ep2-b16-w4motion-0822.yaml"),
        ],
    ),
    17: dict(
        goblin=True,
        faults=[
            "Two honest costs that no clause covers: one clause passes on a thin margin where its parent passed comfortably, and overall motion is 30% lower than the take it came from, on a shot that was already still.",
            "APPROVAL FLAG (§6): this beat's restaged script line has never been read by you — \"The scavenger pushes himself up, gives his cloak a shake, and turns to go.\" It is on the publish checklist for that reason.",
        ],
        wins=["Passes all five of its clauses. Naming the colour held the colour: the cloak is navy and stays navy."],
        note="His face is never visible in this shot — he is turning away, by design — so no design claim can be made about him here either way.",
        faults_from="ship-manifest.yaml beat 17",
        candidates=[
            dict(file=f"{CAND_URL}/17-goodbye-LTX-ep2-b17-repeat-0822.mp4",
                 poster=f"{POSTER_URL}/17-goodbye-LTX-ep2-b17-repeat-0822.jpg",
                 label="BEST AVAILABLE — the brush arrives and the still opening is gone — tonight, newest", tag="warn",
                 verdict="This beat's definition is 'stand, brush, turn' and until tonight no take had ever brushed. Here his hand comes up to his chest, travels down the front of his shirt and returns to his side across the first two and a half seconds, and THEN he turns away. Your face holds the whole time it is facing you. The 3.3 seconds of frozen picture that opened the clip below are gone: measured frame to frame, 52 of 104 pairs are under 0.5 where the earlier take had 89, and the first six tenths of the clip now move at a steady rate instead of sitting still. WHAT IS STILL TRUE: the turn itself is still only in the last quarter, and the brush reads as one long slow wipe rather than the two the prompt asked for.",
                 diff="ONE STRING CHANGED and it was chosen from a measurement, not a guess. All eight clips of tonight's wave ran on one recipe, and they split by how their action sentence is written: the only two that name a REPEAT COUNT — 'twice' — are the only two that move all the way through, and the four that describe a one-shot sequence all park and do their single move in one burst. Beat 17's action was rewritten from 'turn through, plant, step' to a countable brush plus a turn, and the parked opening went away. The refinement, which is more useful than the prediction: the COUNT is what filled the runtime. The words asking the turn to be 'unbroken from the first frame to the last' did nothing at all — the turn is still where it was. So the lever for the other still beats is a countable action, not an instruction to go slowly.",
                 src="pipeline/jobs/ep2-b17-repeat-0822.yaml"),
            dict(file=f"{CAND_URL}/17-goodbye-LTX-ep2-b17-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/17-goodbye-LTX-ep2-b17-w4motion-0822.jpg",
                 label="the same beat before the action was rewritten — 3.3 s of still first", tag="warn",
                 verdict="This is the only take of this beat where you can SEE HIM before he goes: the canon face is on camera and holding — broad dome, off-white almond eyes with dark pupils, near-horizontal ears, sage collar — and then from frame 80 he turns and by the last frame you are looking at the back of his head. That is the beat's own action and the definition says so in as many words. What it does not have is the first 3.3 seconds: frames 0 to 79 move at 0.07 to 0.37 average, which is a still. No brush either — the definition asks stand, brush, turn, and this is stand, turn.",
                 diff="New plate on the corrected eye, this beat's own action carried unchanged. The clip in the cut already passes all five of its clauses and NOTHING here is a swap — that one never shows his face at all, which the page has recorded as a reason no design claim could be made about him. This one can be judged on design. If the still opening is the only objection, the head of it is trimmable in one line.",
                 src="pipeline/jobs/ep2-b17-w4motion-0822.yaml"),
        ],
    ),
    18: dict(
        goblin=False,
        faults=[
            "5.0 s of picture in an 11.0 s slot — 5.9 s of frozen frame, the longest hold in the episode.",
        ],
        wins=["Passes. Motion in all four quarters, no light pumping; the named pick of three seeds, of which one strobed and one decayed."],
        note="Open and yours: matte or gloss on the fig.",
        faults_from="ship-manifest.yaml beat 18",
        candidates=[
            dict(file=f"{POSTER_URL}/18-the-decision-PLATE-celfig-r2-0822.jpg", still=True,
                 label="a PLATE — the fig DRAWN rather than photographed. Round two is a picture.", tag="warn",
                 verdict="Round one was a flat purple rectangle; this is a drawing — clean black outlines, flat colour, one fruit hanging from a stem with leaves. So the answer to 'does the drawn look carry from a face to a fruit' is YES, and that question is closed. WHAT IT IS NOT: a fig. It reads as a dark plum or an eggplant — nearly black rather than purple-violet, no green at the neck, and it carries a big glossy highlight even though both 'glossy' and 'specular highlight' are banned in the negative, which is the seventh time in this tree that banning a thing has failed to remove it. And the look is FLAT VECTOR, not the detailed cinematic anime of your plates. Put up as the second option on the matte-or-gloss question you have open, which it answers from an unexpected direction: the drawn version came back glossier than the photographic one.",
                 diff="One variable against round one: the wording. Same driver, same settings, same seed. Round one invented a five-word style phrase and 'flat colour' ate the frame; round two uses the phrase this repo already has working — the one at the front of every motion prompt in tonight's wave — and puts it at the front, where those prompts put it. NO ROUND THREE IS FILED. Two rungs answered the question that was asked, and a third would be chasing a fig rather than testing anything; if you want this look pursued, the useful next step is a note about which part is wrong.",
                 src="pipeline/jobs/ep2-b18-celfig-r2-0822.yaml"),
            dict(file=f"{POSTER_URL}/18-the-decision-PLATE-celfig-0822.jpg", still=True,
                 label="round one of the same idea — it came apart", tag="fail",
                 verdict="A flat purple rectangle with three black brush marks in it. No fig, no stem, no sky, no picture. Shown because the failure is specific and cheap to fix rather than mysterious: the prompt asked for a purple fruit AND for 'flat colour' in the same sentence, and the model resolved that by making the whole frame one flat purple field. Nothing in the cut is affected and beat 18 still passes on its own bar.",
                 diff="The idea was worth two GPU minutes: every fig this tree has ever drawn was asked for as a lit macro photograph and came back looking like one, while the ruling for the characters since July has been detailed cinematic anime, and the measured finding from the guard sheet is that the style comes from the WORDS. This tested whether that carries from a face to a fruit. What it actually tested was a phrase nobody had used before. The wording this repo already has working — '2D anime, hand-drawn cel animation, flat cel shading, clean ink linework, anime key art' — sits at the front of every motion prompt in the wave and produces the look you approved. Round two uses that phrase and drops 'flat colour', which is the term that ate the frame.",
                 src="pipeline/jobs/ep2-b18-celfig-0822.yaml"),
        ],
    ),
    19: dict(
        goblin=True,
        faults=[
            "He does not notice. The brief asks for the fall, the landing AND him noticing, in that order; this delivers the first two exactly and the third not at all.",
            "The last 2.8 s is a still frame, and the event is small — 48 px of travel on a 33 px figure in a 1280-tall frame.",
        ],
        wins=["Eight of eight on a bar that was written before the tool that made it existed. And on design it is not merely close to your tile — it IS the tile, with the fig moved."],
        note=(
            "STATUS, 2026-08-22 MORNING. The clip below is the good news and it is still the "
            "state of this beat: the fruit falls, which it never has before. The named next step "
            "\u2014 put the fig into a plate drawn on the CORRECTED face and ask for the same "
            "fall \u2014 is NOT done and is not claimed to be. It went behind beats 12, 21 and 06 "
            "this morning because those three had a shape fault that one drawing session closes, "
            "and this one needs a fruit drawn on a stem beside a standing figure, which is a "
            "different tool from the one the leaf beats use. It is the top item on this beat and "
            "it costs a drawing session before it costs a GPU minute."),
        faults_from="ship-manifest.yaml beat 19 + farm-out/ep2-b19-dropcomp-0819/",
        candidates=[
            dict(file=f"{CAND_URL}/19-the-drop-LTX-ep2-b19-dropmotion-0822.mp4",
                 poster=f"{POSTER_URL}/19-the-drop-LTX-ep2-b19-dropmotion-0822.jpg",
                 label="THE FRUIT FALLS. First time in this beat's life. — tonight, newest", tag="warn",
                 verdict="The fig starts on the stem, comes loose, and is lying in the grass by halfway. This beat has been a slate since 08-15 and the reason has always been that the object it is about was never in the picture; two of its three events are now on screen, and the plant stays rooted and single while they happen. THAT IS WHERE THE GOOD NEWS STOPS. He does not notice — he walks out of the left edge instead and the last second is an empty field. And the figure you see in the first frame is not the figure in the second: the seated cloaked goblin of the starting picture is replaced by a standing short-sleeved one within a second, which is the biggest jump in the clip. A second fig also appears floating in the sky at the end.",
                 diff="A rung the ladder named on 08-19 and nobody had fired: motion asked of the COMPOSITE plate — the one where the plant and the fig were drawn into the field by hand and settled in, and which scored eight of eight as a still. Every previous motion attempt on this beat used a plate with no fruit in it, so the fall could not happen at any wording. What this settles is that a hand-drawn object CAN be animated by this engine, which nothing in this tree had asked before. What it also shows is that this particular plate is from 08-19 and predates your goblin correction, so the face in it was never yours — the next version wants the fig composited into a CURRENT plate rather than motion asked of an old one.",
                 src="pipeline/jobs/ep2-b19-dropmotion-0822.yaml"),
            dict(file=f"{CAND_URL}/19-the-drop-LTX-ep2-b19-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/19-the-drop-LTX-ep2-b19-w4motion-0822.jpg",
                 label="tonight's re-render — FAILS, shown so the failure is on the record", tag="fail",
                 verdict="It has your face and nothing else this beat needs. THERE IS NO FRUIT IN IT AT ALL — the beat is a fall, a landing and a noticing, and the object that does all three is absent, so none of the three can happen. Before that it is a still: frames 0 to 69 move at 0.04 to 0.31 average. Then from frame 70 he walks, and by the last frame he has walked out of the right edge of the shot and the frame is mostly empty grass.",
                 diff="A new plate on the corrected eye. The plate was authored for the FACE and the fig was never put back into it, so the motion prompt is asking for an event whose object does not exist — the same law that pulled beats 02, 03 and 20 off their framing. The clip in the cut is unaffected and still scores eight of eight on its own bar; this is not a swap and not a candidate for the slot. Beat 19 already has a proven composite route for exactly this: the plant and the fig were DRAWN into a plate on 08-19 and passed all eight clauses. That is the fix, and it is a composite, not a re-word.",
                 src="pipeline/jobs/ep2-b19-w4motion-0822.yaml"),
        ],
    ),
    20: dict(
        goblin=True,
        faults=[
            "He never looks up. The look up is the beat.",
            "The tree is the wrong tree.",
            "The clip darkens progressively across its length, about 25 luma levels.",
            "He reads as an OLD MAN — wrinkled forehead and jowls, heavy human nose, an ear with no point at all, and pupils.",
        ],
        wins=[],
        faults_from="ship-manifest.yaml beat 20 superseded_fault_shipping_0820 + goblin_design_audit_0820 beats.20",
        candidates=[
            dict(file=f"{CAND_URL}/20-evidence-LTX-ep2-b20-w4motion-0822.mp4",
                 poster=f"{POSTER_URL}/20-evidence-LTX-ep2-b20-w4motion-0822.jpg",
                 label="tonight's re-render — HE LOOKS UP, and the head comes apart doing it", tag="fail",
                 verdict="This beat's first and biggest fault is 'he never looks up. The look up is the beat.' He looks up here — his eyes come off his hands from about frame 50 and his head follows — and a bare branch enters at the top right in the last frames, which is the other thing the definition demands. It is also the first take of this beat that is not an old man: no wrinkled forehead, no jowls, no human nose, pointed ears, your eyes. AND IT PAYS FOR ALL OF IT AT THE SAME FRAME. From about frame 50 the head balloons and loses its shape, the ears droop into flat flaps, and A THIRD HAND rises at the right of frame while both of his are still cupped in his lap. The thing in his hands is a small GREEN sprout, not a purple fig.",
                 diff="New plate on the corrected eye, this beat's own action carried unchanged. The clean window and the required action do not overlap: frames 0 to 48 hold a correct figure and no look-up, frames 50 onward have the look-up and a deforming figure, so there is no trim that gives you both and none has been made. The clip in the cut is unaffected. What this does settle is that the look-up is REACHABLE — every previous attempt on this beat failed to produce it at all — so the next round is a figure-stability problem on a beat whose action is no longer in doubt.",
                 src="pipeline/jobs/ep2-b20-w4motion-0822.yaml"),
            dict(file=f"{CAND_URL}/20-evidence-LTX-ep2-b20-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/20-evidence-LTX-ep2-b20-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="fail",
                 verdict="He still never looks up — a branch enters at the top right and he never turns to it. And the pose barely changes across all 105 frames: this is close to a still with a runtime. The fruit is yellow-green where canon has the fig purple, so it is the same fault as the red fruit in a new colour.",
                 diff="Canon goblin plate. Arguably the cleanest face in the wave: bald, large lateral pointed ears, off-white sclera with vertical slit pupils, all held to the last frame.",
                 src="review/canonmotion-0821/JUDGING-0821.md"),
            dict(file=f"{AGEB_URL}/20-evidence-LTX-ep2-b20-tilemotion-s2-0821.mp4",
                 poster=f"{POSTER_URL}/20-evidence-LTX-ep2-b20-tilemotion-s2-0821.jpg",
                 label="age-B seed 2 (was swapped in, then reverted)", tag="warn",
                 verdict="THE ONLY CLIP OF THE WHOLE AGE-B WAVE THAT CLOSED A BRIEF CLAUSE: he looks up. The head rises from frame 55 and is up, eyes open and mouth parted, by frame 76 — inside the slot. It pays with a RED fig where canon says purple.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b20-tilemotion-s2-0821.yaml", quiet=True),
            dict(file=f"{AGEB_URL}/20-evidence-LTX-ep2-b20-tilemotion-s1-0821.mp4",
                 poster=f"{POSTER_URL}/20-evidence-LTX-ep2-b20-tilemotion-s1-0821.jpg",
                 label="age-B seed 1", tag="warn",
                 verdict="Same recipe, first seed; seed 2 was picked over it.",
                 diff=AGEB_PULLED, src="pipeline/jobs/ep2-b20-tilemotion-s1-0821.yaml", quiet=True),
        ],
    ),
    21: dict(
        goblin=False,
        faults=[
            "The plant is a single LANCE-shaped leaf, not two cotyledons. Wrong plant — it fails both sapling canon rules at once, the same wrong-plant fault as beats 16 and 20.",
        ],
        wins=[
            "The only beat in the episode whose definition is fully met — all four clauses, and the hard one is measured. The leaf tilts steadily in one direction over about 90 frames, with no oscillation and no reversal, AND IT STOPS.",
            "Fixed on 08-21: the opening colour jump is trimmed off, and nothing after it was touched.",
        ],
        note=(
            "STATUS, 2026-08-22 MORNING \u2014 THE DRAWING IS DONE AND IT IS CLEAN. The plant in "
            "the clip below is ONE BIG LANCE-SHAPED LEAF standing straight up, where canon is two "
            "average leaves and lance shapes are ruled out by name. The lance is gone: it was "
            "erased out of the frame and two ordinary leaves were drawn on one stem in its place, "
            "then settled in with the same light pass beats 16 and 19 used. The plate is below and "
            "nothing else in the picture moved \u2014 same golden field, same hedgerow, same sky. "
            "The motion render off it is on the card as you read this. Everything else about this "
            "beat is untouched on purpose: it is the only beat in the episode whose definition is "
            "fully met, its tilt is measured, and a rung that changed the plate AND the wording "
            "could not tell you which one did it. THE MOTION RENDER HAS LANDED \u2014 see below, and read the last second of it before anything else."),
        faults_from="ship-manifest.yaml beat 21 + pipeline/jobs/ep2-b21-daylight-0814.yaml",
        candidates=[
            dict(file=f"{CAND_URL}/21-the-answer-LTX-poolD-0812.mp4",
                 poster=f"{POSTER_URL}/21-the-answer-LTX-poolD-0812.jpg",
                 label="THIS BEAT'S FIRST CANDIDATE — the lance is gone and the tilt still works", tag="warn",
                 verdict="The lance leaf is gone and what tilts is a proper seedling: two ordinary leaves on one stem, leaning steadily over to the right across the whole five seconds in the same golden field. The tilt is the thing this beat is FOR and it survived the plate change intact — one direction, no wobble, and it comes to rest. THE FAULT, AND IT IS AT THE END: by the last second a THIRD blade has grown in, and the top leaf has stretched back toward a point. Canon is two, so the last twenty frames break it. For the first two-thirds of the clip this is the plant you asked for; after that the model's own idea of a seedling starts pushing back through.",
                 diff="Same action sentence byte for byte, same seed, same everything — the only change is the starting picture, which is the plate below. Worth knowing beyond this beat: a hand-drawn plant DOES hold its shape through a real motion render, for a while. Beat 12's ran the same way this morning and held two leaves for all 121 frames. The difference between them is what this beat's action asks for, and that is the next thing to look at rather than the compositor.",
                 src="pipeline/jobs/ep2-b21-leafmotion-0822.yaml"),
            dict(file=f"{POSTER_URL}/21-the-answer-PLATE-leafcanon-0822.jpg", still=True,
                 label="a PLATE — the lance leaf is gone. This morning.", tag="warn",
                 verdict="Two ordinary leaves on one stem in the golden field. Cel-shaded, with the frame's own ink weight, sitting in the grass where the old plant stood. The hedgerow, the cloud bands and the light are the clip's own and are untouched. This is the cleanest of the two leaf fixes done this morning \u2014 there is no side effect to report on it. One small honesty: a faint line of the old stem still runs beside the new one in the lower third.",
                 diff="The plant was drawn into the frame in software and finished with a light pass; nothing about the beat's motion, wording or seed is touched. The motion render off this plate is queued and will appear here as a candidate.",
                 src="pipeline/jobs/ep2-b21-sapnat2-0822.yaml"),
        ],
    ),
}

# Beats where canon.yaml counts the goblin. The goblin-age card is another
# lane's page; this one links to it and does not restate it.
GOBLIN_BEATS = {2, 3, 4, 7, 8, 13, 14, 15, 16, 17, 19, 20}


def esc(s):
    return html.escape(str(s), quote=True)


def read_master():
    d = yaml.safe_load(MASTER.read_text(encoding="utf-8")) or {}
    return {int(r["beat"]): r for r in (d.get("sources") or []) if r.get("beat")}


def vo_text(beat):
    p = SRC / f"{beat:02d}-vo.json"
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    lines = d.get("lines") or []
    if not lines:
        return None
    return [(l.get("who"), l.get("text")) for l in lines if l.get("text")]


def done_when(beat):
    d = yaml.safe_load(DONE.read_text(encoding="utf-8")) or {}
    entry = (d.get("beats") or {}).get(beat) or (d.get("beats") or {}).get(str(beat))
    return (entry or {}).get("done_when")


def fill_sentence(row):
    """`fill: hold, clip_s 4.042, slot_s 6.16` in words a person can act on."""
    fill, clip_s, slot_s = row.get("fill"), row.get("clip_s"), row.get("slot_s")
    if clip_s is None or slot_s is None:
        return None
    if fill == "hold":
        held = round(slot_s - clip_s, 2)
        pct = round(100.0 * held / slot_s)
        return (f"{clip_s:.1f} s of picture in a {slot_s:.1f} s slot — the last "
                f"{held:.1f} s ({pct}%) of this beat is ONE FROZEN FRAME.")
    if fill == "once":
        if clip_s > slot_s + 0.02:
            return (f"{clip_s:.1f} s of picture trimmed into a {slot_s:.1f} s slot — "
                    f"you never see the last {clip_s - slot_s:.1f} s of the render.")
        return f"{clip_s:.1f} s of picture in a {slot_s:.1f} s slot — it plays once, straight through."
    if fill == "slate":
        return "No footage — this beat plays as a card."
    return f"fill: {fill}, clip {clip_s:.1f} s, slot {slot_s:.1f} s"


def secs(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=30)
        return float(out.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


CSS = """
  :root {
    --bg:#17181a; --panel:#1f2124; --panel2:#232629; --line:#33363b;
    --ink:#eceef1; --muted:#9aa0a8; --accent:#c8b273;
    --pass:#7fd68b; --fail:#e08b8b; --warn:#d8b46a; --new:#8fc4e8;
  }
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%; scroll-behavior:smooth; scroll-padding-top:96px}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
       padding:0 20px 120px}
  .wrap{max-width:1080px;margin:0 auto}
  a{color:#9dc2e6}
  header.top{padding:34px 0 16px}
  header.top h1{margin:0 0 6px;font-size:27px;letter-spacing:-.01em;font-weight:650}
  header.top .sub{color:var(--muted);font-size:14.5px;margin:0 0 10px;max-width:80ch}
  .callout{margin:18px 0 0;padding:15px 18px;background:var(--panel);
           border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:5px}
  .callout p{margin:0 0 9px;max-width:82ch} .callout p:last-child{margin-bottom:0}
  .callout.blue{border-left-color:#5b83a8}

  /* ---- sticky beat index ---- */
  nav.index{position:sticky;top:0;z-index:50;background:rgba(23,24,26,.96);
            backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
            margin:0 -20px;padding:9px 20px}
  nav.index .inner{max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;
                   gap:5px;align-items:center}
  nav.index a.chip{display:inline-block;min-width:31px;text-align:center;
        padding:4px 6px;border-radius:4px;border:1px solid var(--line);
        background:#26282c;color:var(--muted);font-size:12.5px;font-weight:700;
        text-decoration:none;font-variant-numeric:tabular-nums}
  nav.index a.chip:hover{border-color:#5f6570;color:var(--ink)}
  nav.index a.chip.answered{background:#23331f;border-color:#416b45;color:#c9f0cd}
  nav.index .legend{color:#6f757c;font-size:11.5px;margin-left:6px}

  section.beat{border-top:1px solid var(--line);padding:30px 0 6px}
  section.beat > h2{margin:0 0 2px;font-size:21px;font-weight:650;letter-spacing:-.01em}
  .tc{color:var(--muted);font-size:12.5px;font-variant-numeric:tabular-nums;
      letter-spacing:.03em;font-weight:600}
  h3{font-size:12.5px;margin:22px 0 7px;font-weight:700;color:#8d939b;
     letter-spacing:.07em;text-transform:uppercase}
  p{max-width:82ch;margin:0 0 10px}
  .story{margin:12px 0 0;padding:13px 16px;background:var(--panel);
         border:1px solid var(--line);border-radius:5px}
  .story .action{margin:0;font-size:15px}
  .story .line{margin:9px 0 0;font-size:15px;color:#e6dcc3}
  .story .line b{color:var(--accent);font-weight:700;font-size:12px;
                 letter-spacing:.05em;display:block;margin-bottom:1px}
  .story .bar{margin:11px 0 0;padding-top:10px;border-top:1px solid var(--line);
              font-size:13.5px;color:var(--muted)}
  .story .bar b{color:#b9bfc7;display:block;font-size:11.5px;letter-spacing:.06em;
                text-transform:uppercase;margin-bottom:3px}

  .now{display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start;margin:8px 0 0}
  .now video{width:300px;max-width:100%;height:auto;border:1px solid var(--line);
             border-radius:5px;display:block;background:#000}
  .now .meta{flex:1 1 340px;min-width:280px}
  .now .meta .fn{font:11.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;
                 color:#7d838b;word-break:break-all;margin:0 0 8px}
  .now .meta .fill{margin:0 0 10px;font-size:14px;color:#cfd4da}
  .voline{margin:0;padding:11px 14px;background:#1b2126;border:1px solid #2c3740;
          border-left:3px solid #5b83a8;border-radius:4px;font-size:15px}
  .voline b{display:block;color:#8fc4e8;font-size:11px;letter-spacing:.06em;
            font-weight:700;margin-bottom:2px}
  .silent{color:var(--muted);font-size:13.5px;font-style:italic}

  ul.faults{margin:0;padding-left:18px} ul.faults li{margin:0 0 7px;max-width:80ch}
  ul.wins{margin:0;padding-left:18px} ul.wins li{margin:0 0 7px;max-width:80ch;color:#bfd9c2}

  .cands{display:flex;flex-wrap:wrap;gap:14px;margin:2px 0 0}
  .cand{flex:1 1 320px;min-width:290px;max-width:520px;background:var(--panel);
        border:1px solid var(--line);border-radius:6px;padding:13px 15px}
  .cand.quiet{background:var(--panel2)}
  .cand video,.cand img.stillframe{width:100%;height:auto;border:1px solid var(--line);
              border-radius:4px;display:block;background:#000;margin:0 0 9px}
  .cand .lbl{font-size:14px;font-weight:650;margin:0 0 6px;display:flex;
             gap:8px;align-items:baseline;flex-wrap:wrap}
  .cand p{font-size:13.5px;margin:0 0 7px;max-width:none}
  .cand .diff{color:var(--muted)}
  .cand .src{font:11px ui-monospace,SFMono-Regular,Menlo,monospace;color:#6f757c;
             word-break:break-all;margin:0}
  .cand .swapid{font:11.5px ui-monospace,SFMono-Regular,Menlo,monospace;color:#c8b273}

  .tag{display:inline-block;padding:2px 7px;border-radius:3px;font-size:11px;
       font-weight:700;letter-spacing:.03em;white-space:nowrap}
  .tag.fail{background:#3a2a2a;border:1px solid #6b4141;color:#f0c9c9}
  .tag.warn{background:#383021;border:1px solid #6b5a33;color:#f0dfb4}
  .tag.pass{background:#23331f;border:1px solid #416b45;color:#c9f0cd}
  .tag.new{background:#1c2a36;border:1px solid #3f6280;color:#c5e2f6}

  .inflight{margin:0;padding:11px 14px;background:#20262b;border:1px solid #35424b;
            border-left:3px solid #5b83a8;border-radius:4px;font-size:13.5px}
  .nocand{color:var(--muted);font-size:13.5px;margin:0}
  .goblink{margin:10px 0 0;font-size:13px;color:var(--muted)}

  .answer{margin:20px 0 0;padding:13px 16px;background:#1c2418;
          border:1px solid #3d5b3d;border-radius:5px}
  .answer .h{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;
             color:#93b894;font-weight:700;margin:0 0 8px}
  .answer code{display:block;font:13px/1.75 ui-monospace,SFMono-Regular,Menlo,monospace;
               background:#131a11;border:1px solid #2f462f;border-radius:4px;
               padding:8px 11px;margin:0 0 6px;color:#d7ecd7;white-space:pre-wrap}
  .answer code:last-child{margin-bottom:0}
  code.inline{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;
              background:#26282c;padding:1px 5px;border-radius:3px}
  footer{border-top:1px solid var(--line);margin-top:44px;padding:22px 0 0;
         color:var(--muted);font-size:13px}
  @media (max-width:640px){
    .now video{width:100%}
    body{padding:0 14px 120px}
    nav.index{margin:0 -14px;padding:8px 14px}
  }
"""

JS = """
// Only the CURRENT clip of the beat you are looking at plays. Twenty-one
// autoplaying videos at once is a page that stutters and a laptop that heats;
// an IntersectionObserver keeps exactly the visible ones running and pauses the
// rest. Candidates never autoplay — they have controls and start on a click.
(function () {
  var live = document.querySelectorAll('video[data-auto]');
  if (!('IntersectionObserver' in window)) {
    live.forEach(function (v) { v.play().catch(function () {}); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) { v.play().catch(function () {}); }
      else { v.pause(); }
    });
  }, { rootMargin: '150px 0px', threshold: 0.15 });
  live.forEach(function (v) { io.observe(v); });
})();
"""


def cand_html(c):
    tag = c.get("tag", "warn")
    quiet = " quiet" if c.get("quiet") else ""
    swap = Path(c["file"]).stem
    bits = [f'<div class="cand{quiet}">']
    poster = f' poster="{esc(c["poster"])}"' if c.get("poster") else ""
    if c.get("still"):
        # A PLATE IS EVIDENCE TOO. Beats 05 and 06 have never had a clip, and a
        # page that can only show mp4s can only show them as prose -- which is
        # the exact thing this page exists to stop. `still: True` renders the
        # frame itself; `swap to` is suppressed because a plate is not a cut.
        bits.append(f'<img class="stillframe" src="{esc(c["file"])}" alt="{esc(c["label"])}">')
    else:
        bits.append(f'<video controls preload="none" playsinline muted loop{poster}>'
                    f'<source src="{esc(c["file"])}" type="video/mp4"></video>')
    bits.append(f'<p class="lbl"><span class="tag {tag}">{esc(tag.upper())}</span>'
                f'<span>{esc(c["label"])}</span></p>')
    bits.append(f'<p>{esc(c["verdict"])}</p>')
    if c.get("diff"):
        bits.append(f'<p class="diff"><b>What is different:</b> {esc(c["diff"])}</p>')
    if not c.get("still"):
        bits.append(f'<p class="diff">To take this one, say: <span class="swapid">'
                    f'swap to {esc(swap)}</span></p>')
    bits.append(f'<p class="src">{esc(c.get("src", ""))}</p>')
    bits.append("</div>")
    return "".join(bits)


def build():
    script = qh.parse_node_script(NODE)
    master = read_master()
    if len(script) != 21:
        raise SystemExit(f"expected 21 beats in node.md, parsed {len(script)}")
    missing = [b["n"] for b in script if b["n"] not in master]
    if missing:
        raise SystemExit(f"no assembly row for beat(s) {missing} — the sidecar and "
                         f"the script disagree; fix that before publishing a page "
                         f"that claims to show every beat's clip")

    out = ['<!doctype html>', '<html lang="en">', "<head>",
           '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<meta name="robots" content="noindex, nofollow">',
           "<title>Sapling ep2 — every beat, one at a time</title>",
           f"<style>{CSS}</style>", "</head>", "<body>"]

    # ---- sticky index -----------------------------------------------------
    chips = "".join(
        f'<a class="chip" href="#b{b["n"]:02d}">{b["n"]:02d}</a>' for b in script)
    out.append('<nav class="index"><div class="inner">' + chips +
               '<span class="legend">green = answered</span></div></nav>')

    out.append('<div class="wrap">')
    out.append("<header class=\"top\">")
    out.append("<h1>Episode 2, beat by beat</h1>")
    out.append('<p class="sub">Twenty-one sections, one per beat. Each one has the '
               'clip that is in the cut right now, the line it plays under, what '
               'the beat is supposed to show, everything known to be wrong with it, '
               'and any other footage that exists for it. You never have to '
               'scroll back: each section is answerable on its own.</p>')
    out.append('<div class="callout"><p><b>How to answer.</b> One line per beat, in '
               'chat, in any order and as few or as many as you want:</p>'
               '<p><code class="inline">b07 ok</code> &nbsp; '
               '<code class="inline">b13 swap to 13-evidence-LTX-ep2-b13-canonmotion-0821</code> &nbsp; '
               '<code class="inline">b20 redo: he still never looks up</code></p>'
               '<p>Every section repeats those three forms at the bottom with this '
               'beat\'s own number filled in, so you can copy one straight out.</p>'
               '</div>')
    out.append('<div class="callout blue"><p><b>What "the current clip" means here.</b> '
               'It is read out of the assembled episode\'s own sidecar — the file '
               'render_t3 wrote while muxing — not out of any manifest. That matters '
               'today: the ship manifest still describes five age-B face swaps and a '
               'beat-01 composite, and all six of those were reverted after you '
               'watched that cut. Every player below is a file that is in your '
               'episode as it stands.</p>'
               '<p>Muted and looping on purpose. Nothing on this page can spend money, '
               'and no clip here is published anywhere.</p></div>')
    out.append("</header>")

    for b in script:
        n = b["n"]
        row = master[n]
        meta = BEATS.get(n, {})
        slug = str(row.get("slug") or b["title"])
        clip = row.get("clip")
        clip_url = f"{SHIP_URL}/{clip}"
        poster = f"{PROOF_URL}/b{n:02d}.jpg"

        out.append(f'<section class="beat" id="b{n:02d}">')
        out.append(f'<h2>Beat {n:02d} — {esc(b["title"])}</h2>')
        out.append(f'<div class="tc">{esc(slug)}</div>')

        # --- 1. the story ---------------------------------------------------
        st = ['<div class="story">']
        if b.get("action"):
            st.append(f'<p class="action">{esc(b["action"])}</p>')
        vo = vo_text(n)
        if vo:
            for who, text in vo:
                st.append(f'<p class="line"><b>{esc(who or "VO")}</b>“{esc(text)}”</p>')
        else:
            st.append('<p class="line silent">No spoken line — this beat is silent by design.</p>')
        dw = done_when(n)
        if dw:
            st.append(f'<p class="bar"><b>What it has to show</b>{esc(dw)}</p>')
        else:
            st.append('<p class="bar"><b>What it has to show</b>No written bar has ever '
                      'been filed for this beat — the stage direction above is the '
                      'whole brief, which is itself worth knowing.</p>')
        st.append("</div>")
        out.append("".join(st))

        # --- 2. the clip that is in the cut ---------------------------------
        out.append("<h3>The clip in the cut right now</h3>")
        out.append('<div class="now">')
        out.append(f'<video data-auto autoplay loop muted playsinline preload="metadata" '
                   f'poster="{esc(poster)}"><source src="{esc(clip_url)}" '
                   f'type="video/mp4"></video>')
        out.append('<div class="meta">')
        out.append(f'<p class="fn">{esc(clip)}</p>')
        fs = fill_sentence(row)
        if fs:
            out.append(f'<p class="fill">{esc(fs)}</p>')
        if vo:
            for who, text in vo:
                out.append(f'<p class="voline"><b>{esc(who or "VO")} SAYS</b>'
                           f'“{esc(text)}”</p>')
        else:
            out.append('<p class="voline"><b>NO LINE</b>Silent beat — the picture '
                       'carries it alone.</p>')
        out.append("</div></div>")

        # --- 3. candidates ---------------------------------------------------
        cands = meta.get("candidates") or []
        out.append("<h3>Other footage that exists for this beat</h3>")
        if cands:
            out.append('<div class="cands">')
            out.extend(cand_html(c) for c in cands)
            out.append("</div>")
        else:
            out.append('<p class="nocand">None. Nothing else has been rendered and '
                       'judged for this beat, so the only two answers that mean '
                       'anything here are <b>ok</b> and <b>redo</b>.</p>')
        if meta.get("inflight"):
            out.append(f'<p class="inflight"><b>In flight:</b> {esc(meta["inflight"])}</p>')
        if n in GOBLIN_BEATS:
            out.append('<p class="goblink">The goblin is in this beat. His design — how '
                       'old he reads, and which face is canon — is one question for '
                       'the whole episode and it has its own page: '
                       f'<a href="{GOBLIN_PAGE}">the goblin age card</a>.</p>')

        # --- 4. faults --------------------------------------------------------
        out.append("<h3>What is wrong with it</h3>")
        faults = meta.get("faults") or []
        if faults:
            out.append('<ul class="faults">' +
                       "".join(f"<li>{esc(f)}</li>" for f in faults) + "</ul>")
        else:
            out.append('<p class="nocand">Nothing recorded.</p>')
        if meta.get("wins"):
            # Its own heading, because a green bullet in a grey list still reads
            # as a fault at a glance and this beat's strengths are half of the
            # ok / swap / redo decision.
            out.append("<h3>What it gets right</h3>")
            out.append('<ul class="wins">' +
                       "".join(f"<li>{esc(w)}</li>" for w in meta["wins"]) + "</ul>")
        if meta.get("note"):
            out.append(f'<p class="nocand"><b>Also:</b> {esc(meta["note"])}</p>')
        if meta.get("faults_from"):
            out.append(f'<p class="src" style="font:11px ui-monospace,Menlo,monospace;'
                       f'color:#6f757c">{esc(meta["faults_from"])}</p>')

        # --- 5. the verdict line ---------------------------------------------
        swap_hint = (Path(cands[0]["file"]).stem if cands else "<candidate>")
        out.append('<div class="answer"><p class="h">Answer in chat</p>')
        out.append(f'<code>b{n:02d} ok</code>')
        out.append(f'<code>b{n:02d} swap to {esc(swap_hint)}</code>')
        out.append(f'<code>b{n:02d} redo: &lt;one line of what is wrong&gt;</code>')
        out.append("</div>")
        out.append("</section>")

    out.append('<footer><p>Built by <code class="inline">review/ep2-beats-0821/'
               'build_page.py</code> from the assembled episode\'s own sidecar, '
               'the script node, the done-definitions and the judging logs named '
               'under each beat. No render, no voice, no spend — $0. '
               'Candidate clips pulled off the rtx5090 box and sha-verified '
               'against its own manifest, 8 of 8, before a frame was shown.</p>'
               '<p>Related pages: <a href="/review/ep2-ship-0821">the assembled cut</a> '
               '· <a href="/review/ep2-goblin-age-0821">the goblin age card</a> '
               '· <a href="/review">the review board</a></p></footer>')
    out.append("</div>")
    out.append(f"<script>{JS}</script>")
    out.append("</body></html>")

    page = "\n".join(out)
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"✓ review/ep2-beats-0821/index.html — {len(script)} sections, "
          f"{sum(len(BEATS.get(b['n'], {}).get('candidates') or []) for b in script)} "
          f"candidate clips, {len(page):,} bytes")


if __name__ == "__main__":
    build()
