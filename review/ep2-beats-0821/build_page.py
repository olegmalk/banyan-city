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
            dict(file=f"{CAND_URL}/02-the-sprint-LTX-b02-panic-trim78-0822.mp4",
                 poster=f"{POSTER_URL}/02-the-sprint-LTX-b02-panic-trim78-0822.jpg",
                 label="THE PANIC + THE LANDING, cut to end behind the sapling — tonight, newest", tag="pass",
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
        note="You said \"wouldn't be bad if he didnt look so chibi in this\". The first clip below is the answer and it needed no new render — it already existed, unwatched, and it is trimmed to this beat's slot so it drops straight in. Side by side with what is in the cut: the cut is a teal head filling the frame with red eyes and no ears; the candidate is a whole body in your design — bald, big lateral ears, slit pupils, mandarin collar, boots — leaning out and back inside the slot.",
        candidates=[
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
        candidates=[],
    ),
    6: dict(
        goblin=False,
        faults=[
            "The bark board is the wrong size. Three of four clauses pass and that one fails.",
            "1.9 s of picture in a 6.5 s slot — 4.5 s of this beat is one frozen frame. It is the biggest ratio in the episode.",
        ],
        wins=["The freeze is a clean freeze. An earlier cut had this window turning the board over, back, and over again; that is gone."],
        faults_from="ship-manifest.yaml beat 6 + pipeline/jobs/ep2-b06-scene-0814r.yaml",
        candidates=[],
    ),
    7: dict(
        goblin=True,
        faults=[
            "The scavenger is dressed in the guard's own pale wrap tunic and white sash, so a beat that has to read \"an official points at a scavenger\" reads as two officials in matching kit.",
            "The goblin has WHITE HAIR, on a character whose canon is bald — plus the guard's round spectacles and a human nose.",
        ],
        wins=["The action lands: the guard raises his own arm at frame 45 and holds the point to frame 96."],
        faults_from="ship-manifest.yaml beat 7 + goblin_design_audit_0820 beats.7",
        inflight="A two-figure plate re-render is QUEUED on the box (ep2-b07-twofig-r2-0821). Its first round drew a good guard — armoured, helmeted, a grown man — but gave the goblin round green eyes instead of the canon slit, and a plain crew-neck tee instead of the collar. Round 2 buys the eye back. No clip yet.",
        candidates=[
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
            "He holds the blank board out to the CAMERA instead of to his partner. From frame 65 to 96 it is flat to the lens, so his partner would be seeing it edge-on. That is the clause that IS the beat, and it fails.",
        ],
        wins=[],
        faults_from="ship-manifest.yaml beat 10 + pipeline/jobs/ep2-b10-pairB-0814.yaml",
        candidates=[],
    ),
    11: dict(
        goblin=False,
        faults=[
            "Guard B turns his face to camera in a beat whose whole point is backs turned.",
            "It has no standing verdict. An earlier pass was withdrawn over \"total identity collapse away from the plate\" across frames 16 to 21, and nothing has passed it since.",
        ],
        wins=[],
        faults_from="ship-manifest.yaml beat 11",
        candidates=[],
    ),
    12: dict(
        goblin=False,
        faults=[
            "The sapling GROWS across the shot — its tip climbs 140 px, 11% of the frame height, steadily — against an approved line that says \"perfectly still\".",
        ],
        wins=["Fixed on 08-21: the clip used to open on 13 frames of a completely different, warmer shot — four or five big pointed leaves — which breaks the canon leaf shape. Those frames are cut, and nothing after them was touched."],
        faults_from="review/ep2-picks/done-definitions.yaml beats.12 + review/ep2-b12-trim-0821/verdict-0821.yaml",
        candidates=[],
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
            dict(file=f"{CAND_URL}/13-evidence-LTX-ep2-b13-canonmotion-0821.mp4",
                 poster=f"{POSTER_URL}/13-evidence-LTX-ep2-b13-canonmotion-0821.jpg",
                 label="canon-motion, round 1 — today", tag="pass",
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
        candidates=[],
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
        faults_from="ship-manifest.yaml beat 16",
        candidates=[],
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
        candidates=[],
    ),
    18: dict(
        goblin=False,
        faults=[
            "5.0 s of picture in an 11.0 s slot — 5.9 s of frozen frame, the longest hold in the episode.",
        ],
        wins=["Passes. Motion in all four quarters, no light pumping; the named pick of three seeds, of which one strobed and one decayed."],
        note="Open and yours: matte or gloss on the fig.",
        faults_from="ship-manifest.yaml beat 18",
        candidates=[],
    ),
    19: dict(
        goblin=True,
        faults=[
            "He does not notice. The brief asks for the fall, the landing AND him noticing, in that order; this delivers the first two exactly and the third not at all.",
            "The last 2.8 s is a still frame, and the event is small — 48 px of travel on a 33 px figure in a 1280-tall frame.",
        ],
        wins=["Eight of eight on a bar that was written before the tool that made it existed. And on design it is not merely close to your tile — it IS the tile, with the fig moved."],
        faults_from="ship-manifest.yaml beat 19 + farm-out/ep2-b19-dropcomp-0819/",
        candidates=[],
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
        inflight="Round 2 of the canon-motion recipe is QUEUED on the box (ep2-b20-canonmotion-r2-0821) with the branch composited into the starting picture. No clip yet.",
        candidates=[
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
        faults_from="ship-manifest.yaml beat 21 + pipeline/jobs/ep2-b21-daylight-0814.yaml",
        candidates=[],
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
  .cand video{width:100%;height:auto;border:1px solid var(--line);border-radius:4px;
              display:block;background:#000;margin:0 0 9px}
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
    bits.append(f'<video controls preload="none" playsinline muted loop{poster}>'
                f'<source src="{esc(c["file"])}" type="video/mp4"></video>')
    bits.append(f'<p class="lbl"><span class="tag {tag}">{esc(tag.upper())}</span>'
                f'<span>{esc(c["label"])}</span></p>')
    bits.append(f'<p>{esc(c["verdict"])}</p>')
    if c.get("diff"):
        bits.append(f'<p class="diff"><b>What is different:</b> {esc(c["diff"])}</p>')
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
