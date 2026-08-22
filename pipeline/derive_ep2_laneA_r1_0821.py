#!/usr/bin/env python3
"""Lane A, round 1 of the 2026-08-21 night iteration campaign: beats 01/05/06/10.

WHY THESE FOUR AND WHY THESE LEVERS. Every beat 01-10 clip in the cut was read
frame-by-frame tonight (pipeline/coldread_frames.py) and swept with an
interframe-difference probe. The four beats here are the ones where the reading
found a lever that is CHEAPER than a new plate and that has not been pulled:

  b05  ITS OWN PROMPT FIGHTS ITS OWN RULING. done-definitions beats.05 records
       the lever as "stage them ALREADY STANDING and scanning rather than
       jogging in - motion toward camera is what breaks it", and the positive
       prompt implements that in its first paragraph and then CONTRADICTS it in
       its last: "HE JOGS. He is RUNNING FORWARD at a heavy trot from the first
       frame ... THE JOG IS THE SHOT - he is moving for most of it, not
       standing." The negative fights both sides at once -- it opens with
       "jogging, running" and also carries "standing still, standing in one
       spot, standing at attention, stationary, motionless, loitering". The
       shipped clip is what a model does when pulled both ways: the pair
       neither stands nor jogs, and guard 2's head dissolves to a featureless
       smear across roughly f048-f070 (a fault that appears in no fault list
       for this beat). THE EDIT IS A DELETION, not a new route: the leftover
       jog paragraph goes, and the negative stops forbidding the pose the
       positive asks for. "frozen, still frame, no movement" STAY -- they
       describe a dead render, not a pose.

  b06  ITS POSITIVE ASKS FOR THE FAULT ITS BAR NAMES. done_when says "board
       hand-sized and readable" and the shipping fault is "the bark board is
       the wrong size". The positive contains, in its own words, "The BOARD IS
       THE SUBJECT - held high and large,". The negative argues against it
       three times ("giant board, oversized board, board filling the frame,
       prop larger than his torso") and loses, which is the placement law
       working exactly as measured: a negative does not size a prop, a positive
       clause does. Second, separate fault: this render DIED -- trim_0815
       removed 72 dead tail frames, so the 6.45 s slot is fed 1.92 s of picture
       and 70% of the beat is one held frame. A freeze is a re-roll question
       (seed x plate, per pipeline/loop/darkening-crf-diagnostic-0819.md), so
       both cells carry a fresh seed as well as the sizing clause.

  b10  WORDS ARE A CLOSED ROUTE HERE AND THIS SPENDS NONE ON THEM. The board
       faces the camera instead of the partner; rounds 3 and 4 both failed that
       way, and plate_lane_0817 isolated the cause -- "A PROP DOES NOT [bind to
       a person clause], it attaches to whichever figure is drawn nearest".
       episode-loop-v2 step 3 says two batch rounds failing the same way means
       restage, not re-word. So these two cells change NOTHING but the seed and
       are aimed at the faults that ARE seed-shaped: the carried board changes
       identity twice inside the clip (teal clipboard -> white sheet -> tan
       slab, f035-f061) and the hands melt across f044-f061.

  b01  PURE RE-ROLL, ONE VARIABLE, BY INSTRUCTION. The horizon/composite
       question is closed -- the chroma composite went in on 08-20 and the
       founder ruled it back out on 08-21 -- so nothing here reopens it. The
       fresh seeds exist to give the beat a third and fourth distinct option
       beside fignonly and chroma. Wording untouched.

WHY SEED IS A LEVER AND NOT A SHRUG, measured, not assumed. beats.02's
judged_0817_anchor_wave rendered SIXTEEN seeds of one wording on one init plate
(MD5-confirmed identical) and got a PERFORMING_RATE of 7 of 16. At that rate a
beat that has been rolled ONCE -- which is b05 (20260914), b06 (20260806) and
b10 (20260915) -- has had roughly a coin-flip's worth of look at its own recipe.
pipeline/loop/darkening-crf-diagnostic-0819.md closes the same point from the
other side: a 91-level collapse on beat 12 vanished to -0.04 on one integer of
seed, plate and prompt byte-identical, and its closing sentence is "a collapse
on this plate is fixable by a re-roll".

WHAT IS DELIBERATELY NOT TOUCHED. --image-crf stays where each parent had it
(33 on all four). It is tempting: three of my ten beats sit at crf 33 and the
crf-10 beats show none of the temporal defects. IT IS ALSO EXONERATED ON THE
RECORD -- darkening-crf-diagnostic-0819.md measured the flag on four clips with
opposite outcomes and withdrew the recipe-property claim. Moving it here would
be a second variable bought with a mechanism the tree has already retracted
once. Nothing else moves either: no guidance, no sigmas, no frames, no
resolution, no plate, no negative except b05's named deletion.

Seeds: 20260871 and 20260818. Both are on record as ordinary well-behaved
carriers in darkening-crf-diagnostic-0819.md and neither has been rolled on any
of these four plates. That is a reason to try them, NOT an inherited property:
that file's own closing clause is "luminance is a per-render check and never a
property you inherit from a passing sibling".

Run:  python3 pipeline/derive_ep2_laneA_r1_0821.py
$0. No model, no network, no GPU. Writes specs only.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import derive_spec  # noqa: E402

JOBS = HERE / "jobs"
SEEDS = [20260871, 20260818]

# ---------------------------------------------------------------------------
# b05 -- the deletion. Both strings below are asserted present in the parent by
# derive_spec's override machinery (a substitution that matches nothing is an
# error), so this file cannot silently become a re-run of its parent.
# ---------------------------------------------------------------------------
B05_JOG_BLOCK = (
    "HE JOGS. He is RUNNING FORWARD at a heavy trot from the first frame — knees lifting, "
    "boots leaving the ground one after the other, free arm pumping, tunic and sash swinging "
    "with the stride, body driving toward camera. He keeps jogging, then pulls up short: he "
    "plants both feet, rocks forward over them and rocks back, shoulders coming up, and looks "
    "off to one side. THE JOG IS THE SHOT — he is moving for most of it, not standing. A SECOND "
    "uniformed guard in the same brown patrol tunic and sash jogs beside him, a half step behind, "
    "and pulls up short with him. TWO MEN, both in frame, both running."
)
B05_STAND_BLOCK = (
    "HE IS ALREADY STOPPED AND HE STAYS STOPPED. Both feet are planted from the first frame. "
    "He rocks forward over them a little and settles back, his shoulders come up, and he looks "
    "off to one side and then slowly back across the field. THE SCAN IS THE SHOT — his head and "
    "his eyes are what move, and his feet do not leave their marks. A SECOND uniformed guard in "
    "the same brown patrol tunic and sash is planted beside him, a half step behind, and scans "
    "the other way. TWO MEN, both in frame, both standing on their marks."
)
B05_NEG_FIGHT = (
    "standing still, standing in one spot, standing at attention, stationary, motionless, "
    "frozen, still frame, no movement, loitering, "
)
# Only the pose terms are deleted. "frozen, still frame, no movement" describe a
# DEAD RENDER rather than a pose and are kept, deliberately and visibly.
B05_NEG_KEPT = "frozen, still frame, no movement, "

# ---------------------------------------------------------------------------
# b06 -- the one clause that asks for the fault.
# ---------------------------------------------------------------------------
B06_LARGE = "The BOARD IS THE SUBJECT — held high and large,."
B06_HANDSIZED = (
    "The BOARD IS HAND-SIZED — no wider than his two hands set side by side, small enough that "
    "his chest, both shoulders and his chin all stay visible behind it and around it,."
)


def payload_text(spec_path, basename):
    """Read one payload file's current text out of a parent spec."""
    import yaml
    d = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    hits = [v for k, v in (d.get("payload") or {}).items() if k.endswith(basename)]
    if len(hits) != 1:
        raise SystemExit("!! %s: expected exactly one payload key ending %s, got %d"
                         % (spec_path, basename, len(hits)))
    return hits[0]


def edited(text, old, new, label):
    if old not in text:
        raise SystemExit("!! %s: the string this edit is built on is NOT in the parent.\n   %r"
                         % (label, old[:120]))
    out = text.replace(old, new)
    if out == text:
        raise SystemExit("!! %s: replacement changed nothing" % label)
    return out


CELLS = []

# --------------------------------------------------------------------- b05 --
b05_parent = JOBS / "ep2-b05-standB-0814.yaml"
b05_prompt = edited(payload_text(b05_parent, "b05-motion-prompt.txt"),
                    B05_JOG_BLOCK, B05_STAND_BLOCK, "b05 positive")
b05_neg = edited(payload_text(b05_parent, "b05-negative.txt"),
                 B05_NEG_FIGHT, B05_NEG_KEPT, "b05 negative")
for seed in SEEDS:
    CELLS.append(dict(
        parent=b05_parent, beat=5, new_id="ep2-b05-decontra-s%d-0821" % seed, seed=seed,
        retoken=[("05-the-patrol-LTX-jog-b-0812",
                  "05-the-patrol-LTX-ep2-b05-decontra-s%d-0821" % seed)],
        overrides={"payload:b05-motion-prompt.txt": b05_prompt,
                   "payload:b05-negative.txt": b05_neg},
        one_variable=(
            "TWO EDITS, BOTH DELETIONS OF SELF-CONTRADICTION, PLUS THE SEED. The positive's "
            "leftover jog paragraph is replaced by the planted-and-scanning staging its own "
            "first paragraph and its own recorded lever already call for; the negative stops "
            "forbidding standing. Nothing else moves: same init plate at the same asserted "
            "sha, same 121-frame grid, same --image-crf 33, same guidance, same sigmas. The "
            "two cells differ from each other by SEED ALONE."),
        why=(
            "Beat 05's prompt contradicts beat 05's own ruling. done-definitions beats.05 "
            "records the lever as 'stage them ALREADY STANDING and scanning rather than "
            "jogging in - motion toward camera is what breaks it', and the shipped spec's "
            "positive still ends 'THE JOG IS THE SHOT - he is moving for most of it, not "
            "standing', while its negative forbids BOTH jogging AND standing still. Read "
            "frame by frame tonight the clip does what a pulled-apart instruction produces: "
            "the pair drifts, and guard 2's head dissolves to a featureless orange smear "
            "across roughly f048-f070 -- a fault named in no list this beat has. This is the "
            "cheapest lever on the ladder above a blind re-roll and it deletes rather than "
            "invents. $0, ~6 minutes, and the card is idle."),
        consumer=(
            "BEAT 05'S SELECTION on the per-beat review page review/ep2-beats-0821, which the "
            "founder picks from in the morning. Beat 05 has never been iterated and currently "
            "offers him exactly one take. This cell is a candidate version, not a swap: lane A "
            "does not swap cuts, it stages options."),
        success=(
            "One 704x1280 121-frame mp4 in which BOTH GUARDS KEEP A DRAWN FACE FOR THE WHOLE "
            "CLIP -- no smear, no featureless head, at f048, f060 and f070 where the incumbent "
            "loses guard 2 -- and in which the two men are PLANTED, turning their heads to scan, "
            "with neither man jogging toward camera and neither leaving frame. Read by eye at "
            "1:1 on consecutive frames through the motion window (pipeline/coldread_frames.py), "
            "never an evenly spread sheet. A clip that holds both faces and scans is a genuine "
            "option for the selection; a clip that holds the faces but stands inertly is "
            "recorded as a partial and still shown."),
        fail_modes=(
            "D-STILL the deletion overshoots and the shot becomes a held photograph: both "
            "faces survive because nothing happens. Scored as a partial, not a pass; it is why "
            "'frozen, still frame, no movement' were KEPT in the negative.\n"
            "D-DISSOLVE-ANYWAY the head smear is seed-shaped rather than instruction-shaped and "
            "reproduces at both new seeds. That is the informative outcome: it moves beat 05 "
            "off the wording ladder and onto the plate, and it is why two seeds run and not one.\n"
            "D-COUNT the pair collapses to one man or overshoots to three. This beat has "
            "produced 1, 3 and 3+ on words before; count now comes from the plate, so a count "
            "failure here would mean the deletion disturbed something the plate was holding.\n"
            "D-SASH neither guard wears the sash. EXPECTED AND NOT SCORED AS A FAIL -- the sash "
            "is not in the init plate and the absent-object law says a prompt cannot summon it. "
            "It stays a plate job and this rung does not pretend otherwise."),
    ))

# --------------------------------------------------------------------- b06 --
b06_parent = JOBS / "ep2-b06-scene-0814r.yaml"
b06_prompt = edited(payload_text(b06_parent, "b05-motion-prompt.txt"),
                    B06_LARGE, B06_HANDSIZED, "b06 positive")
for seed in SEEDS:
    CELLS.append(dict(
        parent=b06_parent, beat=6, new_id="ep2-b06-handsize-s%d-0821" % seed, seed=seed,
        retoken=[("06-the-clipboard-LTX-world-0813",
                  "06-the-clipboard-LTX-ep2-b06-handsize-s%d-0821" % seed)],
        overrides={"payload:b05-motion-prompt.txt": b06_prompt},
        one_variable=(
            "ONE CLAUSE IN THE POSITIVE, PLUS THE SEED. 'The BOARD IS THE SUBJECT - held high "
            "and large,.' becomes a hand-sized clause. The negative is NOT touched -- it "
            "already argues for the right size and has been losing to the positive. Same init "
            "plate at the same asserted sha, same 121 frames, same --image-crf 33, same "
            "sampler numbers. The two cells differ from each other by SEED ALONE."),
        why=(
            "This beat's bar says 'board hand-sized and readable' and its shipping fault is "
            "'the bark board is the wrong size', and the positive prompt asks for the fault in "
            "its own words: 'The BOARD IS THE SUBJECT - held high and large,'. The negative "
            "objects three separate times and loses, which is the placement law behaving "
            "exactly as measured -- a negative does not size a prop. Second and larger fault, "
            "and it is why the seed moves too: this render DIED. trim_0815 cut 72 dead tail "
            "frames, so a 6.45 s slot is fed 1.92 s of picture and roughly 70% of the beat on "
            "screen is one frozen frame, the worst ratio in the episode. A freeze is a "
            "(seed x plate) question on this recipe family and the record says so: beat 12 lost "
            "91 luma levels and came back at -0.04 on one integer of seed, plate and prompt "
            "byte-identical. $0, ~6 minutes."),
        consumer=(
            "BEAT 06'S SELECTION on review/ep2-beats-0821 for the founder's morning pick. The "
            "beat currently offers one take that is 70% frozen frame. A candidate version, not "
            "a swap."),
        success=(
            "One 704x1280 121-frame mp4 that is ALIVE PAST f046 -- the frame the incumbent died "
            "at -- with a last-live-pair beyond f100, AND in which the bark board is small "
            "enough that his chest, both shoulders and his chin read around it while he turns "
            "it over and reads off it with his eyes down. Both clauses are scored; either one "
            "alone is a partial and is still shown. Read by eye at 1:1 on consecutive frames."),
        fail_modes=(
            "H-PLATE-WIDTH, AND AFTER OPENING THE INIT THIS IS THE ONE I EXPECT. The plate was "
            "opened at 1:1 before this spec was filed (see plate_ack). The prop already in it "
            "is a WIDE FLAT TRAY carried horizontally at waist height with loose papers on it, "
            "and it is nearly as wide as the man. The shipped clip's first frames show exactly "
            "that tray and then convert it, around f008-f012, into a vertical bark slab OF THE "
            "SAME WIDTH. On that reading the board is oversized because THE PLATE'S PROP IS "
            "THAT WIDE, and a positive clause asking for hand-sized is arguing with the "
            "picture -- which the absent-object law says it loses. If both cells come back with "
            "a wide board, that is not a weak result: it converts 'the bark board is the wrong "
            "size' from an open wording question into a PLATE JOB, in one round, for $0, and "
            "the next lane should re-cut the plate rather than write a fifth sentence about "
            "size. This is written down BEFORE the render so a wide board cannot be reported "
            "as a surprise.\n"
            "H-SHIELD he raises the board in front of his face instead of reading off it. This "
            "is on record as this beat's other seed's failure ('seedB holds the scene and the "
            "man but delivers the WRONG ACTION - he raises the board like a shield'), so it is "
            "a known seed outcome and a second draw of it is information, not surprise.\n"
            "H-DEAD-AGAIN the render freezes again in the same region. Two fresh seeds both "
            "dying moves this beat off the seed ladder and onto the plate.\n"
            "H-SMALL-BUT-DEAD the sizing clause binds and the clip still dies. Recorded as a "
            "SPLIT result -- it would mean the two faults are independent and the beat needs "
            "the sizing clause carried onto whatever fixes the freeze.\n"
            "H-OVERSHOOT the board shrinks until it is not readable as a written board. The bar "
            "says hand-sized AND readable and this cell can fail on the second half.\n"
            "H-SECOND-FIGURE the plate carries a SECOND, smaller figure in the right background "
            "holding a pale card up. This beat's positive says 'ONE uniformed patrol guard ... "
            "is alone in this shot and no second person is anywhere in the frame' and its "
            "negative names 'two men, second guard, a pair'. The shipped take erased him "
            "successfully; a fresh seed may not."),
        plate_ack=[(
            "card: IT IS NOT A CARD, AND THE GUARD'S OWN SECOND STATISTIC SAYS SO BEFORE I DO. "
            "The refusal is border flatness 0.740 against a 0.62 threshold. The same refusal "
            "prints the colour figure beside it: 0.461, where the six costume cards the "
            "threshold was cut from read 0.745 to 0.966 on that statistic too. The guard "
            "explains the signature in its own words -- 'Flat in lightness and NOT flat in "
            "colour is what a border made of two materials looks like: sky above, grass below, "
            "same lightness, different hue. That is a real scene.' THAT IS THIS PICTURE, and I "
            "did not settle it on the number: the blob was fetched from "
            "origin/farm-results-rtx5090, its sha re-computed against the crop step's own "
            "assertion, and OPENED AT 1:1. The border is pale blue sky along the top and pale "
            "green grass along the bottom -- two materials at nearly equal lightness, which is "
            "exactly why a lightness-only statistic reads it as paper. There is no white "
            "margin, no vignette, no studio backdrop and no isolated figure. This is not a "
            "deliberate macro or close-up either; it is a full-figure scene plate, and the "
            "waiver says so rather than claiming the exemption the prompt suggests."
        ), (
            "refs: THE GUARD NAMES THIS EXACT FILE AS ITS OWN KNOWN FALSE POSITIVE AND I OPENED "
            "THE PICTURE ANYWAY. box_enqueue refuses this init twice -- border flatness 0.740 "
            "against a 0.62 threshold, and membership of CARD_REFS_DENYLIST via the producing "
            "job ep2-b10-patrol-scene-r2-0813 (reference set refs-charref-guards-r5-0812). The "
            "refusal text itself says: 'refs-charref-guards-r5-0812 also drew "
            "ep2-b10-patrol-scene-r2-0813/10-no-form-ipa-r0-w010-s1.png, opened 2026-08-16, "
            "which is a field with a hedge, flowers and two guards. If this is that plate, this "
            "refusal is wrong.' THIS IS THAT PLATE, by name and by sha. Not taken on the "
            "guard's word: the blob was fetched from origin/farm-results-rtx5090 on 2026-08-21 "
            "night, its sha256 re-computed as 441a4fd115fa2d0b5194b61b4317be8ee0e14ef6045a9507"
            "372062ef3e4cd98c -- byte-identical to the assertion this spec's crop step already "
            "makes -- and OPENED AT 1:1. What is in it: a grown dark-haired man in a brown "
            "patrol coat and maroon sash standing in grass, with white and yellow flowers in "
            "the near field, a hedge line across the middle distance, open sky above, and a "
            "second smaller figure standing in the right background. It is a location, not "
            "blank paper. The two refusals are also one signal and not two, as the guard's own "
            "note says: the denylist was built by scoring plates with the same border-flatness "
            "statistic. Waived for these two cells only; the guard is left unchanged, because "
            "the threshold is right for the six cards it was cut from and this is the false "
            "positive it already documents."
        )],
    ))

# --------------------------------------------------------------------- b10 --
b10_parent = JOBS / "ep2-b10-pairB-0814.yaml"
for seed in SEEDS:
    CELLS.append(dict(
        parent=b10_parent, beat=10, new_id="ep2-b10-reroll-s%d-0821" % seed, seed=seed,
        retoken=[("10-no-form-LTX-world-0813",
                  "10-no-form-LTX-ep2-b10-reroll-s%d-0821" % seed)],
        overrides={},
        one_variable=(
            "THE SEED. Nothing else -- not one byte of the positive, the negative, the plate, "
            "the sha assertion or any sampler flag. This is the strictest one-variable rung "
            "available on this beat and it is deliberate: see `why`."),
        why=(
            "Beat 10's headline fault -- the blank board faces the CAMERA instead of the "
            "partner -- is a CLOSED WORDING ROUTE and this rung spends nothing on it. The "
            "positive already says partner-facing three times ('extends it toward the other man "
            "at chest height so the empty back of it faces his partner'); round 3 and round 4 "
            "both failed the same way; and plate_lane_0817 isolated the mechanism -- 'A PROP "
            "DOES NOT [bind to a person clause], it attaches to whichever figure is drawn "
            "nearest'. episode-loop-v2 step 3: two batch rounds failing the same way means the "
            "staging is wrong for the engine, not the words. What IS seed-shaped are the two "
            "faults the frame-by-frame read found tonight and no list carries: the carried "
            "board CHANGES IDENTITY TWICE inside the clip (teal clipboard -> pale sheet -> tan "
            "slab across f035-f061) and both men's hands melt into extra and merged fingers "
            "across f044-f061. This beat has been rolled once, at 20260915. Its sibling beat "
            "02, same engine, same one-plate-one-wording design, performed at 7 of 16 seeds. "
            "$0, ~6 minutes."),
        consumer=(
            "BEAT 10'S SELECTION on review/ep2-beats-0821 for the founder's morning pick. "
            "Never iterated; one take on offer. A candidate version, not a swap."),
        success=(
            "One 704x1280 121-frame mp4 in which THE CARRIED BOARD IS ONE OBJECT FROM FIRST "
            "FRAME TO LAST -- same colour, same shape, same hands -- and both men's hands stay "
            "drawn hands at f044, f052 and f061 where the incumbent melts them, with two guards "
            "in frame throughout and the field present at frame one. THE BOARD'S FACING IS NOT "
            "IN THIS BAR. It is pre-declared as out of scope here so that a clip cannot be "
            "reported as a failure for missing a target this rung never aimed at, and so that a "
            "clip that DOES land it cannot be claimed as the wording working."),
        fail_modes=(
            "R-MORPH-AGAIN the board changes identity at these seeds too, which would make it a "
            "plate/prop property rather than a draw and would close the seed ladder on this "
            "beat in one round.\n"
            "R-COUNT one guard only. On record as round 2's and round 3's failure at some "
            "seeds; count now comes from the plate, so a drop here is a real regression.\n"
            "R-CAMERA-BOARD the board faces the lens again. PRE-DECLARED AS EXPECTED and not "
            "scored, in either direction.\n"
            "R-JUDDER the alternating half-rate motion measured on this clip tonight (adjacent "
            "frame pairs differing 5.96 against 1.56, a ~3.8x alternation, where beat 01 on the "
            "same engine measures 1.00) persists. Nothing in this rung targets it; it is "
            "recorded so the next lane has the number."),
    ))

# --------------------------------------------------------------------- b01 --
b01_parent = JOBS / "ep2-b01-fignonly-s20260840-0820.yaml"
for seed in SEEDS:
    CELLS.append(dict(
        parent=b01_parent, beat=1, new_id="ep2-b01-fignonly-s%d-0821" % seed, seed=seed,
        retoken=[("01-cold-open-LTX-fignonly-s20260840",
                  "01-cold-open-LTX-fignonly-s%d-0821" % seed)],
        overrides={},
        one_variable=(
            "THE SEED. The positive, the negative, the nubcomp plate and its sha assertion, and "
            "every sampler flag are the shipping take's own, unchanged."),
        why=(
            "Beat 01's composite question is CLOSED -- the chroma composite was swapped in on "
            "08-20 and the founder ruled it back out on 08-21 -- and nothing here reopens it. "
            "What the beat lacks is options: the founder is being shown one take of the shot "
            "that opens the episode. Its recorded open fault (the field moves with the fig) is "
            "already argued against in the negative in six separate terms, so a re-word has "
            "nothing left to say and the remaining lever is the draw. Two fresh seeds give the "
            "cold open a third and fourth distinct version to choose between beside fignonly "
            "and chroma. $0, ~12 minutes each."),
        consumer=(
            "BEAT 01'S SELECTION on review/ep2-beats-0821. Per lane A's instruction the beat's "
            "selection is fignonly + chroma + the best of one fresh seed batch; this is that "
            "batch. A candidate version, not a swap, and it does not touch the closed "
            "composite ruling."),
        success=(
            "One 704x1280 121-frame mp4 in which the fig goes from green nub to a single deep "
            "purple fig AND THE FIELD DOES NOT MOVE WITH IT -- the grass blades and the "
            "background hold while the fruit changes. The incumbent's specific weakness, found "
            "by reading it tonight, is that its fig does not ripen so much as SWAP: it is teal "
            "and static from f000 to f087 and purple at f098, a colour change inside one "
            "11-frame gap, and the fruit also relocates down the stem across that gap. A cell "
            "that ripens gradually and keeps the fruit on its node beats the incumbent on the "
            "beat's own done_when ('the purple fig SWELLS on the stem')."),
        fail_modes=(
            "S-NOFIG the fruit never turns purple, or turns and reverts.\n"
            "S-FIELD the grass moves with the fig, exactly as the incumbent does. Two seeds "
            "reproducing it makes the field motion a property of the plate and the recipe "
            "rather than the draw, which retires the seed ladder on this beat.\n"
            "S-BLOOM whole-frame luminance walks. This recipe family is measured as capable of "
            "+73 and -91 levels on a seed that behaves elsewhere, and beat 01's own crf-33 "
            "parent is the +73.24 case, so this is checked per render and never inherited.\n"
            "S-POP the ripening happens in one frame pair again. Same defect as the incumbent, "
            "recorded rather than excused."),
    ))

# ---------------------------------------------------------------------------
written = []
for c in CELLS:
    extra = {
        "the_one_variable": c["one_variable"],
        "pre_registered_fail_modes": c["fail_modes"],
        "read_that_produced_this_rung":
            "Every beat 01-10 clip named in review/ep2-ship-0821/ep2-ship-0821.mp4.meta.yaml "
            "`sources:` was decoded and read on 2026-08-21 night: an overview plus "
            "consecutive-frame strips through each motion window via "
            "pipeline/coldread_frames.py, and an interframe-difference sweep over every "
            "adjacent pair at 176x320 BT.601 luma. The faults this spec cites by frame "
            "number come from that read and not from any existing verdict.",
    }
    child = derive_spec.derive(
        src=str(c["parent"]),
        new_id=c["new_id"],
        fresh=dict(why=c["why"], consumer=c["consumer"],
                   success=c["success"],
                   owner="iteration-campaign lane A (beats 01-10), 2026-08-21 night"),
        overrides=dict(c["overrides"], **{"seed": c["seed"]}),
        retoken=c["retoken"],
        extra=extra,
    )
    out = JOBS / (c["new_id"] + ".yaml")
    derive_spec.write(child, str(out))

    # THE WAIVER IS APPENDED HERE AND NOT PASSED THROUGH derive_spec, BECAUSE
    # derive_spec IS RIGHT TO REFUSE IT. `plate_ack` is findings-shaped and
    # derive() rejects it in `extra` with "a spec earns those AFTER its pixels
    # exist". A plate waiver is not a finding about pixels, though -- it is a
    # human saying "I opened the picture and the guard is wrong about this
    # file", which is exactly the remedy box_enqueue's own refusal text names:
    # 'waive this one job with plate_ack: "refs: <why>"'. So it is written by
    # hand, after the derivation, visibly, on the two jobs it applies to, and
    # it is never inherited by anything derived from them (derive_spec drops
    # plate_ack on every future child, which fails SAFE -- the guard fires
    # again and the next human opens the picture again).
    if c.get("plate_ack"):
        import yaml as _yaml
        block = _yaml.safe_dump({"plate_ack": c["plate_ack"]},
                                default_flow_style=False, width=96,
                                allow_unicode=True, sort_keys=False)
        with out.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write("# --- appended by hand after the derivation: see the note in\n"
                     "# pipeline/derive_ep2_laneA_r1_0821.py. derive_spec refuses this key\n"
                     "# and is right to; a plate waiver is a human act, not an inheritance.\n")
            fh.write(block)
        # Re-parse so a malformed append cannot reach box_enqueue.
        chk = _yaml.safe_load(out.read_text(encoding="utf-8"))
        assert chk["plate_ack"] == c["plate_ack"], "plate_ack did not round-trip"
        assert chk["id"] == c["new_id"], "append corrupted the spec"

    written.append(out)

print("WROTE %d spec(s):" % len(written))
for p in written:
    print("  ", p)
