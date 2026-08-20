#!/usr/bin/env python3
r"""BEAT 09: take the trade. The r2s2 crop, the hand sentence, five seeds.

    python3 pipeline/derive_b09_r2s2_0821.py [--write]

THE LEVER WAS RE-PRICED BY THE BATCH THAT DECLINED IT. `ep2-b09-hand-h1..h4-0820`
put one sentence in the positive naming the hand and it worked as a mechanism
and not as a fix: the hand left at f008 on the parent and at f039/f075/f025 on
h1/h2/h3, every seed clearing the parent's death frame by seventeen to sixty-
seven frames, none reaching the end. h1's own spec named the next move and
priced it against itself:

    "The r2s2 crop (1.454x, 90% of native) is the OTHER named route and is
     deliberately not taken: its hand is sharper and its eye is shut, which is
     a trade and not a fix."

**THE COST SIDE OF THAT TRADE HAS SINCE BEEN PAID ANYWAY.** All three scored
h-clips end with his eyes shut, and two of the three are dead in their last
twenty frames. So `keeps the eye` -- the whole reason r1s3 was preferred -- is
not what the shipping clip actually delivers, and a route rejected for costing
an eye is now being compared against a clip that costs the same eye and a hand.
That is the re-price, and it is why this batch fires.

AND THE CUT MOVES THE PRICE AGAIN, WHICH NOTHING HAD FACTORED IN. Beat 09's slot
in `review/ep2-ship-0821` is 3.92 s at 24 fps: **THE SLOT IS f001-f093** and the
manifest says so in its own fault row. The h-batch's headline cost lands at
f100+. It is off the end of the slot. What is IN the slot is the incumbent's
fault, measured this morning with `pipeline/judge_b09_crop_0821.py`:

    hand-box drift from f001:  f005 46.98   f008 48.78   f030 50.16   f093 47.70

The hand is gone by f005 and never comes back, for the whole 3.92 seconds the
audience sees. THE INCUMBENT'S EYES ARE OPEN AND ITS HAND IS NOT THERE.

WHAT IS ACTUALLY ONE VARIABLE HERE. The parent of every job below is
`ep2-b09-hand-h1-0820`, so the hand sentence, the negative, crf-10, 121 frames,
guidance 2.0, distilled sigmas, two-stage and sequential offload all cross
byte-identical. **Only the crop moves** -- `--src` and `--sha256` on the crop
step point at the r2s2 platecrop instead of the r1s3 one -- and the seeds are
chosen so that three of the five cells have a SCORED sibling at the same seed:

    c1  seed 20260819   against h1   crop only
    c2  seed 20260851   against h2   crop only
    c3  seed 20260852   against h3   crop only

THE OTHER TWO CELLS EXIST BECAUSE THE INIT IS NOT THE PICTURE THE SENTENCE
DESCRIBES, AND I FOUND THAT BY LOOKING AT IT. On r1s3 the hand lies flat
against the cheek, fingers up, both eyes open. **On r2s2 the hand is CURLED AT
HIS MOUTH AND CHIN** -- knuckles against the lips, thumb under the jaw -- and
one eye is squinted shut. The carried sentence says `his fingers rest against
his cheek ... shifting a little against his cheek`. This tree's most-measured
law is that THE POSITIVE PLACES WHAT IT NAMES, and a cheek sentence over a mouth
init is therefore not a neutral carry: it is a request to MOVE the hand, from
frame one, on the one object this beat cannot afford to lose. Carrying it
blind would confound the crop with a pose conflict and neither number would
mean anything.

    m1  seed 20260819   against c1   wording only, at the r2s2 crop
    m2  seed 20260851   against c2   wording only, at the r2s2 crop

`m` swaps ONE sentence for a pose-matched one in the same dialect and the same
ongoing-action shape (`shifting a little against his mouth as he thinks`), so
the freeze trap the h-batch pre-registered is not re-opened. Every cell in this
batch has exactly one variable against a named neighbour; nothing is a fresh
draw and nothing is a two-variable cell.

$0. Five jobs, ~7 minutes each, ~35 minutes on a card whose backlog is empty.

WHAT THIS RUNG MAY DO THAT h1's MAY NOT. h1 pre-registered `is_show_content:
false` because beat 09 was a SLATE and the adult/adolescent read was an open R4
card. Both facts have changed: beat 09 entered the cut on 08-20 under that card,
and the founder has since ruled the guards a PASS ("dumb grown men"), which
makes this an ordinary steward pick. So these jobs are `is_show_content: true`
and a winner is a veto-able swap into `review/ep2-ship-0821` -- against the bar
below, with the incumbent's own numbers quoted in it, and with faults named in
the manifest row rather than argued away.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import derive_fetch_guard  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b09-hand-h1-0820.yaml"

R2S2_SRC = (r"C:\banyan-farm\courier-box\farm-out\ep2-b09-platecrop-0820"
            r"\09-the-pause-platecrop-r2s2.png")
R2S2_SHA = "420fc2c0238eb9b4f5a615cde09ed3639ffc5cc92bfbe990a9c14686329a809a"
R2S2_REL = "farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-r2s2.png"

# The sentence h1 inserted, and the pose-matched replacement. Both are asserted
# against the PARENT'S ACTUAL BYTES below -- a substitution that silently
# matched nothing is how a two-arm batch becomes five copies of one arm.
CHEEK = ("HIS HAND IS AT HIS FACE AND STAYS THERE: his fingers rest against "
         "his cheek with the thumb under his jaw, four fingers drawn whole "
         "against the skin, and they stay resting there the whole time, "
         "shifting a little against his cheek as he thinks.")
MOUTH = ("HIS HAND IS AT HIS FACE AND STAYS THERE: his curled fingers rest "
         "against his mouth with the thumb under his chin, the knuckles and "
         "fingers drawn whole against his lips, and they stay resting there "
         "the whole time, shifting a little against his mouth as he thinks.")

INCUMBENT = """THE CLIP IN THE CUT RIGHT NOW, measured 2026-08-21 with
pipeline/judge_b09_crop_0821.py, in its own geometry, over the SLOT (f001-f093):
  hand drift from f001   f005 46.98  f008 48.78  f030 50.16  f093 47.70
                         (the hand collapses at the FIRST pair, step 46.06, and
                          the box never recovers -- gone for the whole slot)
  last live pair         92 of 92 in slot (105 of 120 whole)
  dead pairs in slot     38 of 92
  face-band interframe   1.390 mean in slot; by thirds 2.422 / 0.187 / 1.567
                         (the middle third is nearly dead)
  T0 pan residual        bg_corner 7.02 mean / 10.99 max in slot
                         bg_low    2.84 mean / 27.60 max in slot (spike at f012)
  eyes                   OPEN, both, visible irises, at f001
That is the thing to beat, and it is beatable on exactly one axis."""

BAR = """THE H-BATCH'S BARS, WITH THE PRICE THE LADDER NAMED MOVED FROM THE FAIL
COLUMN TO THE COST COLUMN, AND WITH THE SLOT SUBSTITUTED FOR THE CLIP. Scored by
eye at 1:1 first, on f001, f008, f030, f050, f070 and f093, and then with the
committed rulers. THE SLOT IS f001-f093; f094-f121 are rendered and are NOT
SHIPPED, so no clause below is scored on them.

T0 THE PAN RULER, AND IT IS A GATE: nothing else is read off a clip that fails
   it. Background patch residual (each patch's own mean removed, because
   whole-frame luma falls ~7 levels over the first thirty frames on this recipe
   and the raw b04 form reports that exposure drift as a camera move) must not
   exceed 1.5x the incumbent's slot mean on either patch -- bg_corner 7.02 and
   bg_low 2.84, so 10.5 and 4.3. THE ABSOLUTE b04 BAR OF 3.0 IS PRINTED AND IS
   NOT USED: the SHIPPING clip fails it at 7.02, so imported unexamined it would
   fail the incumbent, and a bar that fails the thing it is meant to protect is
   not a bar. THE TOP-RIGHT CORNER IS EXCLUDED BY NAME on both crops -- it is
   his hair, not the world.
X1 THE HAND AT f008 AND f030. A whole hand -- knuckles or palm and readable
   fingers against the face -- at f008 and at f030. f008 is the frame the
   pre-crop parent died on; f030 is where the h-batch's best cell was still
   whole. This is the clause the rung exists for.
X2 THE HAND AT f093, THE LAST FRAME THAT SHIPS. This is the PROMOTION clause and
   it is separate from X1 on purpose: X1 says the mechanism carried to a sharper
   plate, X2 says the beat is fixed for the audience. A clip that passes X1 and
   fails X2 is PROGRESS and the frame it goes at is the next rung's number --
   the same reading the h-batch's H-LATE got, and it is not a swap.
X3 THE HAND IS A HAND. Not a mitten, not three fingers, not a smudge, not a
   fifth finger. A hand that survives by becoming a shape is a FAIL and is named
   here so it cannot be reported as a hold.
X4 THE FACE STILL WORKS, AND THE CLIP IS ALIVE AT THE END OF THE SLOT. Brows
   draw and ease, eyes shift, the head tilts a few degrees. LAST LIVE PAIR must
   reach 93 -- the incumbent's is 92 of 92, so a clip that dies inside the slot
   to hold the hand loses on the incumbent's own ruler and not on an opinion.
   Face-band interframe mean in slot >= 1.0 (incumbent 1.390) and no third of
   the slot under 0.15 (incumbent's middle third is 0.187 and that is already
   the fault this beat has).
X5 THE PARENT'S SURVIVING CLAUSES: mouth closed for the whole slot, one face,
   one man, the same man at f093 as at f001, no second hand.

ACCEPTED COSTS, PRICED IN, RECORDED AS COSTS AND NOT AS FAILS:
  * ONE EYE IS SQUINTED SHUT FROM f001. It is a property of the r2s2 plate, not
    of the motion -- it is the `shut eye` the ladder priced this route at, and
    it is visible on the very first frame rather than only at the end. THE
    INCUMBENT HAS BOTH EYES OPEN AND THIS DOES NOT. That is the trade, it is
    named here before any pixel exists, and a clip is not failed for it.
  * EYES SHUT AT THE END. Off the end of the slot (f100+) and therefore not
    scored at all; recorded because the h-batch's verdict turned on it.
  * SOFTER GLOBALLY THAN A NATIVE CLOSE-UP. 1.454x LANCZOS, 90.2% of the native
    control's high-frequency energy against r1s3's 45% -- this crop is the
    SHARPER of the two, which is the point, but neither is native.

THE SWAP TEST, WHICH IS NARROWER THAN THE BAR AND IS THE ONLY THING THAT MOVES
THE CUT: a clip swaps in only if it passes T0, X1, X3, X4 and X5, beats the
incumbent on last-live-pair-in-slot AND on hand-hold by eye, and does not lose
the face acting (X4's two numbers). X2 is what makes it a clear win rather than
a marginal one. If nothing clears that, the incumbent stands and this batch is a
measurement, not a swap."""

PREDICTED = """WHAT I EXPECT, WRITTEN BEFORE IT RUNS. The crop should help X1
and X3 for a mechanical reason the ladder already established: `the init holds
where it is sharp`, and this hand is drawn at 1.454x instead of 2.157x -- 90.2%
of a native close-up's high-frequency energy against 45%. The hand is the
softest object in the r1s3 frame and it is the first thing to go; on r2s2 it is
not the softest object.
WHAT I EXPECT TO GO WRONG, IN ORDER.
H-POSE, AND IT IS WHY THE m ARM EXISTS: the carried sentence describes a hand
flat on the CHEEK and the r2s2 init has it curled at the MOUTH. If the c cells
show the hand sliding off the mouth toward the cheek over the first ten frames
while the m cells do not, that is H-POSE and the answer is the m wording. If
BOTH arms hold, the sentence's placement clause was doing less work than its
naming clause, and that is a finding about this engine worth more than the clip.
X4-FREEZE, unchanged from h1: two of three h-cells were dead in their last
twenty frames. A sharper init gives the sampler less to re-decide, which helps
the hand and may also flatten the face. That is why last-live-pair is a GATE
here and not a note.
THE EYE. I am not predicting the squint opens. It is in the init and the
positive does not mention it; the h-batch's eyes went the other way and stayed
there. If a c cell OPENS the eye mid-clip that is a bonus and it is not a bar.
AND THE ONE I CANNOT PRICE: whether a boy with one eye shut and a fist at his
mouth reads the beat better or worse than a boy with two open eyes and no hand.
That is taste and it is not mine to settle -- which is why the swap is VETO-ABLE
and the manifest row will say what was traded, in numbers, rather than claiming
an upgrade."""

FAIL_MODES = """H-POSE the cheek sentence pulls the hand off the mouth on a
plate that never had it on the cheek; visible as a hand that TRAVELS over
f001-f010 rather than one that dissolves. The m arm is the pre-spent answer and
the c/m pair at the same seed is what tells them apart.
H-FREEZE the sharper init holds the hand by holding everything. last-live-pair
under 93 or a slot third under 0.15 and it is a FAIL, not a hold.
H-SMUDGE the hand persists as a shape that is not a hand. Reads as a hold on
every number in this file and does not at 1:1, which is why the frames are
written out and looked at.
H-SECONDHAND naming a hand summons one; nothing was added to the negative, here
as in h1, so a second hand is the rung that would earn a negative edit.
H-LATE the hand clears f008 and f030 and goes before f093. PROGRESS, not a swap,
and the frame it goes at is the next rung's number.
H-EYE-COST the squint reads as a wince or a squint-at-the-sun rather than a man
thinking, and the trade is simply bad. Taste, veto-able, named up front."""

NOT_DONE = """No crf change, no strength change, no guidance/sigma change, no
negative edit, no second plate, no new crop parameters -- beat09_plate_crop.py
is not re-run and its r2s2 output is used at its committed sha. The r1s3 route
is not retired: if this fails, the incumbent stands unchanged and nothing about
it has been touched. No pick and no plate_ack is written by this file; a swap,
if one is earned, is a separate commit with its own manifest row and its own
veto line."""


def _assert_emitted_init(spec_path: str) -> None:
    r"""derive_fetch_guard's lesson, applied to the shape THIS spec actually has.

    `assert_fetch_urls_resolve` reads raw.githubusercontent URLs, and these jobs
    do not fetch over HTTP -- they read the plate off the box's own courier-box
    checkout, `C:\banyan-farm\courier-box\farm-out\...`. The trap it guards
    against is identical: derive_spec retokens EVERY string in the child, so a
    path that named the PARENT'S artifact directory would be silently rewritten
    to a directory nobody has written, and the job would die on the card. So the
    EMITTED file is re-read -- after retoken has had its way -- and its --src is
    mapped back into this repo, hashed against its own --sha256 assertion and
    checked against origin/main, which is what the box pulls.
    """
    import hashlib
    spec = derive_spec.load(os.path.join(REPO, spec_path))
    seen = 0
    for st in spec.get("steps") or []:
        argv = [str(x) for x in (st.get("argv") or [])]
        if "--src" not in argv:
            continue
        seen += 1
        src = argv[argv.index("--src") + 1]
        sha = argv[argv.index("--sha256") + 1] if "--sha256" in argv else ""
        head = "C:\\banyan-farm\\courier-box\\"
        if not src.startswith(head):
            raise SystemExit("!! %s: --src is not a courier-box path: %s"
                             % (spec_path, src))
        rel = src[len(head):].replace("\\", "/")
        abs_ = os.path.join(REPO, rel)
        if not os.path.isfile(abs_):
            raise SystemExit("!! %s: --src %s is not in this checkout -- the "
                             "retoken trap, exactly as derive_fetch_guard "
                             "describes it." % (spec_path, rel))
        with open(abs_, "rb") as fh:
            have = hashlib.sha256(fh.read()).hexdigest()
        if sha and have != sha:
            raise SystemExit("!! %s: --sha256 does not match the bytes\n"
                             "   want %s\n   have %s" % (spec_path, sha, have))
        missing = derive_fetch_guard._not_on_origin_main([rel])
        if missing:
            raise SystemExit("!! %s: --src is not on origin/main: %s"
                             % (spec_path, missing))
    if seen != 1:
        raise SystemExit("!! %s: expected exactly 1 --src step, found %d"
                         % (spec_path, seen))


def main() -> int:
    write = "--write" in sys.argv

    parent = derive_spec.load(os.path.join(REPO, PARENT))
    pkey = [k for k in parent["payload"]
            if k.replace("\\", "/").rsplit("/", 1)[-1] == "b09-motion-prompt.txt"]
    if len(pkey) != 1:
        raise SystemExit("!! parent has %d motion-prompt payloads" % len(pkey))
    cheek_prompt = parent["payload"][pkey[0]]
    if CHEEK not in cheek_prompt:
        raise SystemExit("!! the parent's positive does not contain the cheek "
                         "sentence this file quotes -- refusing to guess.\n"
                         "   looked for: %s" % CHEEK[:80])
    mouth_prompt = cheek_prompt.replace(CHEEK, MOUTH)
    if mouth_prompt == cheek_prompt:
        raise SystemExit("!! the pose substitution changed nothing")

    # The plate this batch is built on, asserted here as well as on the card.
    src_abs = os.path.join(REPO, R2S2_REL)
    import hashlib
    with open(src_abs, "rb") as fh:
        have = hashlib.sha256(fh.read()).hexdigest()
    if have != R2S2_SHA:
        raise SystemExit("!! r2s2 plate sha mismatch\n   want %s\n   have %s"
                         % (R2S2_SHA, have))
    missing = derive_fetch_guard._not_on_origin_main([R2S2_REL])
    if missing:
        raise SystemExit("!! the r2s2 plate is not on origin/main: %s\n"
                         "   the box pulls courier-box from main; push first."
                         % missing)
    print("plate OK  %s  sha %s  on origin/main" % (R2S2_REL, have[:12]))

    # tag, seed, prompt-arm, the sibling this cell is one variable away from
    CELLS = [
        ("c1", 20260819, "cheek", "ep2-b09-hand-h1-0820 (same seed, r1s3 crop)"),
        ("c2", 20260851, "cheek", "ep2-b09-hand-h2-0820 (same seed, r1s3 crop)"),
        ("c3", 20260852, "cheek", "ep2-b09-hand-h3-0820 (same seed, r1s3 crop)"),
        ("m1", 20260819, "mouth", "ep2-b09-r2s2-c1-0821 (same seed, same crop)"),
        ("m2", 20260851, "mouth", "ep2-b09-r2s2-c2-0821 (same seed, same crop)"),
    ]

    out = []
    for tag, seed, arm, sibling in CELLS:
        new_id = "ep2-b09-r2s2-%s-0821" % tag
        overrides = {
            "seed": seed,
            "argv:--src": R2S2_SRC,
            "argv:--sha256": R2S2_SHA,
        }
        if arm == "mouth":
            overrides["payload:b09-motion-prompt.txt"] = mouth_prompt

        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "beat-09 crop-trade lane, 2026-08-21 morning",
                "consumer": (
                    "BEAT 09'S SLOT IN review/ep2-ship-0821, WHICH IS ALREADY "
                    "FILLED. This is not a slate any more: the cut ships "
                    "09-the-pause-LTX-ep2-b09-cropmotion-0820.mp4 today, with a "
                    "hand that is gone by f005 of a 93-frame slot, and the "
                    "guards card that withheld the beat has been ruled a PASS. "
                    "So the consumer is an UPGRADE to a shipping clip before "
                    "the 12:00 cutoff, judged against that clip's own measured "
                    "numbers, and a clip that does not beat it changes nothing. "
                    "Cell %s of five, seed %d, %s arm." % (tag, seed, arm)),
                "success": (
                    "One 704x1280 121-frame mp4 at seed %d off the r2s2 crop IN "
                    "WHICH THE HAND IS STILL A WHOLE HAND AT f008 AND f030, and "
                    "ideally at f093, the last frame the cut shows. Scored by "
                    "eye at 1:1 at f001/f008/f030/f050/f070/f093 and by "
                    "pipeline/judge_b09_crop_0821.py --geom r2s2: T0 pan "
                    "residual within 1.5x the incumbent's, last live pair "
                    "reaching 93, face-band interframe mean >= 1.0 with no slot "
                    "third under 0.15, mouth closed, one man, no second hand. "
                    "ONE EYE IS SQUINTED SHUT FROM f001 AND THAT IS AN ACCEPTED "
                    "COST, not a fail -- it is the price the ladder named this "
                    "route at. THIS CELL IS ONE VARIABLE FROM %s."
                    % (seed, sibling)),
                "why": (
                    "The h-batch proved the hand sentence is a real mechanism "
                    "and could not make it reach the end of the clip, and it "
                    "paid the r2s2 route's own price -- a shut eye -- while "
                    "declining the route. The remaining lever is the sharper "
                    "plate: 1.454x against 2.157x, 90.2%% of a native close-up's "
                    "high-frequency energy against 45%%, on a beat whose hand is "
                    "the softest object in frame and the first to dissolve. "
                    "$0, ~7 minutes, an idle card and a 12:00 cutoff. Cell %s, "
                    "seed %d, %s arm." % (tag, seed, arm)),
            },
            overrides=overrides,
            retoken=[],
            extra={
                "bar": BAR,
                "the_incumbent_this_must_beat": INCUMBENT,
                "failure_predicted_in_advance": PREDICTED,
                "pre_registered_fail_modes": FAIL_MODES,
                "not_done_on_purpose": NOT_DONE,
                "the_one_variable": (
                    "THE CROP, AND FOR THE m CELLS ONE SENTENCE. Every other "
                    "byte is ep2-b09-hand-h1-0820's: the hand sentence in the "
                    "positive, the negative untouched, --image-crf 10, 121 "
                    "frames at 24 fps, guidance 2.0, distilled sigmas, "
                    "two-stage, sequential offload, the same cover_crop.py with "
                    "the same sha assertion. Only --src and --sha256 move, from "
                    "09-the-pause-platecrop-r1s3.png to -r2s2.png. This cell is "
                    "ONE VARIABLE from %s." % sibling),
                "init_provenance": (
                    "farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-"
                    "r2s2.png, sha256 %s, on origin/main at the time this spec "
                    "was written (checked, not assumed). Produced by "
                    "pipeline/beat09_plate_crop.py from "
                    "09-the-pause-ipa-r2-w015-s2.png on "
                    "origin/farm-results-rtx5090: a 1.454x LANCZOS crop of a "
                    "572x837 region taking a 37.83%% head to the 55%% bar with "
                    "the chin at 0.57, retaining 64.3%% of the source's own face "
                    "high-frequency energy and reaching 90.2%% of the native "
                    "close-up control. No sampler, no model, no GPU. The box "
                    "re-asserts this sha before it writes anything."
                    % R2S2_SHA),
                "the_pose_note_up_front": (
                    "THE INIT IS NOT THE PICTURE THE CARRIED SENTENCE "
                    "DESCRIBES, and it was checked by looking at it at 1:1 "
                    "rather than assumed from the filename. r1s3: hand flat on "
                    "the cheek, fingers up, both eyes open, blue irises. r2s2: "
                    "hand CURLED AT THE MOUTH, knuckles at the lips, thumb "
                    "under the chin, the left eye squinted shut, the head "
                    "turned further away. The carried sentence says `cheek` "
                    "twice. That is why two of the five cells swap it for a "
                    "pose-matched sentence at seeds the c arm also runs, so the "
                    "wording is one variable at a fixed crop instead of a "
                    "confound inside the crop result."),
                "is_show_content": True,
                "is_show_content_why": (
                    "CHANGED FROM THE PARENT, ON TWO FACTS AND NOT ON A WISH. "
                    "(1) Beat 09 is no longer a slate: it entered "
                    "review/ep2-ship-0821 on 2026-08-20 as a SHIP-MODE ENTRY "
                    "over its own pre-registered is_show_content:false, and the "
                    "cut ships with it. (2) The adult/adolescent read that "
                    "withheld it -- /review/ep2-guards-0818 -- has been RULED A "
                    "PASS by the founder (\"dumb grown men\"), so the open R4 "
                    "card h1 deferred to is closed and this is an ordinary "
                    "steward pick. A winner is therefore a VETO-ABLE SWAP into "
                    "the ship cut with its faults named in the manifest row, "
                    "not a promotion past a card."),
            },
            by="pipeline/derive_b09_r2s2_0821.py",
        )
        path = "pipeline/jobs/%s.yaml" % new_id
        if write:
            derive_spec.write(child, path, force=True)
            _assert_emitted_init(path)
            print("wrote %s   seed %d  %s arm" % (path, seed, arm))
        else:
            print("would write %s   seed %d  %s arm  (one variable from %s)"
                  % (path, seed, arm, sibling))
        out.append(child)

    # The assertion that makes the batch a batch and not five re-runs.
    prompts = {c["id"]: c["payload"][
        [k for k in c["payload"] if k.endswith("b09-motion-prompt.txt")][0]]
        for c in out}
    arms = {p for p in prompts.values()}
    if len(arms) != 2:
        raise SystemExit("!! expected exactly 2 prompt arms, got %d" % len(arms))
    srcs = set()
    for c in out:
        for st in c["steps"]:
            argv = [str(x) for x in st["argv"]]
            if "--src" in argv:
                srcs.add(argv[argv.index("--src") + 1])
    if srcs != {R2S2_SRC}:
        raise SystemExit("!! not every cell points at the r2s2 crop: %s" % srcs)
    print("checked: 5 cells, 2 prompt arms, 1 init, 3 seeds, all --src = r2s2")
    if not write:
        print("\n(dry run -- pass --write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
