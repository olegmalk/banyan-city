#!/usr/bin/env python3
"""THE THREE COMPOSITE PLATES GET THEIR FIRST MOTION SAMPLE -- beats 15, 03, 13.

ONE RUNG, THREE SAMPLES, AND THE TABLE IS THE POINT. These are not three
unrelated jobs: they are the same recipe change (a composited canon two-leaf
sapling as the i2v init) fired once on each of the three plates the
composite-then-inpaint route converted, at ONE seed, so that a difference
between them is attributable to the PLATE and not to the seed or the flags.
Writing them from one table is what makes that claim checkable -- the per-beat
differences are the rows, and everything not in a row is byte-identical by
construction.

PARENT: pipeline/jobs/ep2-b19-dropmotion-0819.yaml -- the b14 crf-10 LTX recipe
as cloned for beat 19, i.e. the nearest proven i2v job whose init is ALSO a
composited sapling plate. Its beat clause FAILED; its RECIPE did not. What the
recipe has demonstrated, across b04/b09/b14/b19/b20: 121 frames at 704x1280,
a locked camera, and the founder-ratified adult goblin surviving the render
without drifting -- that last one is what `--image-crf 10` is for, and at 33
the parent's man was a different, younger person by frame 21.

WHAT CHANGES PER JOB, and it is the same two things every time (the b04-eyes
formula): THE INIT PICTURE AND THE WORDS. Not one sampler number moves --
size, frames, fps, guidance, distilled sigmas, two-stage, offload, mode and
--image-crf 10 are all the parent's, so a bad result is attributable to this
beat rather than to the recipe.

THREE THINGS THIS RUNG CARRIES FORWARD FROM WHAT THE LADDER ALREADY PAID FOR:

1. THE ANCHOR IS MEASURED BEFORE THE GPU, NOT AFTER. 832x1216 -> 704x1280
   cover-crops at 1.0526 and then throws away 81.7 ORIGINAL px off EACH SIDE.
   Beat 13's composited sapling starts at original x=13: a CENTRED crop cuts 72
   px off the subject of the beat. Beat 03's mask reaches x=67 and is also
   clipped. Both are filed `--anchor left`; beat 15 clears a centred crop with
   41 px to spare and keeps the default, which reproduces every earlier copy of
   cover_crop.py byte for byte.

2. THE FRAMING ASSERT IS THE MASK, NOT A COLOUR PREDICATE. Beat 19's
   assert_framing.py found its fruit with a hue window. That cannot work here:
   these plants are green objects on green fields, and this ladder has twice
   now recorded a colour predicate producing a clean, wrong number (the
   green-OR-purple growmotion mask; the b08 probe that landed on a sleeve). The
   composite MASK is the plant's own authored footprint, it is published beside
   the plate, and pushing it through the identical cover-crop gives the plant's
   exact output bbox with no predicate at all. Every WANT_BBOX below was
   measured that way on this Mac before any of these jobs existed.

3. THE PLANT IS PLACED POSITIVELY, WHICH IS THE ONE DELIBERATE DEPARTURE FROM
   THE PARENT'S PROMPT. Beat 19's F-PLANT-REVERT fired hardest of all its fail
   modes -- two leaves became four-plus, an upright stem became a runner, and
   four drawing rounds died in 90 frames -- and its prompt said NOTHING positive
   about the plant, naming `a second fruit` only in the negative. "Positive
   placement beats negatives" has now been sighted six times. So each prompt
   here states the plant's end state as a fact of the shot, and the negative is
   the backstop rather than the mechanism.

$0. No provider, no paid engine. Writes three spec files and nothing else.
Run:  python3 pipeline/derive_sapcomp_motion_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b19-dropmotion-0819.yaml"
SEED = 20260820           # the sapcomp seed, held across all three
RAW_BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/farm-out/"

STYLE_TAIL = ("2D anime, hand-drawn cel animation, flat cel shading, clean ink "
              "linework, anime key art, cinematic lighting, detailed, newest, "
              "masterpiece, best quality, very aesthetic.")

# Shared negative spine. The plant clauses lead it because F-PLANT-REVERT is
# the pre-registered top risk on all three; the identity and camera clauses are
# the parent's, unchanged.
NEG_COMMON = (
    "a third leaf, extra leaves, more leaves, a leafy bush, a branching weed, "
    "extra stems, a second plant, a flower, a fruit, a berry, the plant growing, "
    "the plant getting taller, the plant lying down, a horizontal runner, "
    "a big tree, a tree trunk, "
    "a second goblin, two goblins, 2boys, crowd, child, chibi, baby, round head, "
    "cute, human skin, pale skin, hair, wig, changing face, morphing, melting face, "
    "camera pan, camera tilt, zoom, dolly, push in, pull back, tripod, "
    "cut to another shot, scene change, shot change, new camera angle, "
    "different location, split screen, walking out of frame, leaving the frame, "
    "still image, freeze frame, photorealistic, 3D render, CGI, live action, text")

IDENTITY_CLAUSE = (
    "He stays the same lean wiry adult goblin man from the first frame to the "
    "last: green skin, bald head, long pointed ears, patchwork cloak, one face "
    "and one figure only. The camera never moves.")

PLANT_CLAUSE = ("The little plant stays exactly as it is and does not grow: ONE "
                "thin stem, TWO leaves, rooted in the grass, shorter than he is.")

# --------------------------------------------------------------------------
# THE TABLE. Every number in `plate`, `bbox` and `skin` was measured on this
# Mac, on the real published bytes, before this file was run.
BEATS = [
    dict(
        new_id="ep2-b15-listenmotion-0820",
        beat=15,
        tag="listenmotion",
        out_base="15-good-listener-LTX-sapcomp-0820",
        src_dir="ep2-b15-sapcomp-0819",
        src_png="b15-sapcomp-s20260819.png",
        src_sha="df399888424071e5b9281748937a1e422eff6756dbe62c452b28d7b5456d30b8",
        mask_png="15-good-listener-sapcomp-mask-0819.png",
        mask_sha="f7933427bba319044058d8712a1574b35ad084768e5807b4f3e060a6ea810fdb",
        anchor="center",
        bbox=(41, 300, 240, 636),
        anchor_why=(
            "CENTRE, i.e. the default, and it is checked rather than assumed. The "
            "composited plant occupies original x 121..310, which a centred crop "
            "puts at output x 41..240 with 41 px of air to the left edge and the "
            "whole seated figure still inside. This is the only one of the three "
            "that clears a centred crop, so it is the only one that reproduces "
            "every earlier copy of cover_crop.py byte for byte."),
        skin=(302, 408, 356, 448),
        skin_where="his left cheek, below the spectacle rim and above the cloak collar",
        success_action=(
            "he TIPS HIS HEAD DOWN AND SIDEWAYS toward the two leaves, ends with his eyes level with them, and his mouth moves as he talks to them, with both him and the plant in shot in every frame"),
        skin_f000="R 67.9 G 114.6 B 50.3, R-B 17.6, luma 93.3 (std 20.3)",
        action=(
            "He tips his head down and sideways toward the two leaves until his "
            "eyes are level with them, and talks to them from a hand's width "
            "away; his mouth moves as he speaks to the plant. He stays sitting "
            "in the grass with his hands on his knees, and he does not stand up "
            "and does not lean away. Both he and the plant stay in the frame "
            "together the whole time."),
        neg_extra="open sky between them, the plant out of frame, standing up, ",
        script_line=(
            "Beat 15 GOOD LISTENER (1:10-1:15), node.md:98 as rewritten 2026-08-17 "
            "and READ AND APPROVED BY THE FOUNDER 2026-08-19: \"He tips his head "
            "down and sideways until his eyes are level with the two leaves, and "
            "talks to them from a hand's width away; both of them share the "
            "frame.\" His spoken line in the beat is \"You're a good listener. The "
            "last three people I talked to filed a report.\" -- so a MOVING MOUTH "
            "is correct here, unlike beat 04."),
        bar_beat={
            "B1_eyes_level_with_the_two_leaves_at_the_end": (
                "His eye line ends inside the blade band. Read at 1:1 on f120, not "
                "from a metric. On the init his pupils are at output y ~378 and the "
                "blades are centred at output y ~390, so he starts nearly there: the "
                "clause is that the tip DOWN AND SIDEWAYS happens and does not "
                "overshoot past the leaves or come back up. A clip where he raises "
                "his head fails, and it fails against his OWN approved line."),
            "B2_both_in_one_frame_for_all_121_frames": (
                "He and the sapling are both in shot in every frame. This is the whole "
                "of beats.'15'.done_when -- 'a close-up of him looking up at nothing "
                "fails it however well he acts' -- and twenty-four artifacts could not "
                "produce it with a real plant. NOTE THE STALE HALF OF THAT DEFINITION: "
                "done_when was written 2026-08-15 and says 'he LOOKS UP'; node.md:98 "
                "was rewritten 2026-08-17 to 'tips his head DOWN' and the founder "
                "approved that on 08-19. The approved line governs the direction; "
                "done_when governs the framing, on which the two agree."),
            "B3_his_mouth_moves": (
                "He talks. The mouth opening is a PASS on this beat and a fail on "
                "beat 04, and the difference is that beat 15 has a spoken line. No "
                "lip-sync is claimed or scored: the VO is muxed later by render_t3."),
        },
        risk=("F-HEAD-RISES: he starts almost at the target attitude, so the "
              "engine's easiest motion is to lift the head back to a neutral pose "
              "-- which is the OLD, superseded staging and would read as correct to "
              "anyone holding the 08-15 done_when. Named here so it is a finding "
              "and not a disappointment."),
    ),
    dict(
        new_id="ep2-b03-covermotion-0820",
        beat=3,
        tag="covermotion",
        out_base="03-bad-cover-LTX-sapcomp-0820",
        src_dir="ep2-b03-sapcomp-0820",
        src_png="b03-sapcomp-s20260820.png",
        src_sha="7d3ab86a3f419f0d39c3c8960483008e61da99592dc77b4ff5cbb46cd2471671",
        mask_png="03-bad-cover-sapcomp-mask-0820.png",
        mask_sha="5bd2074189015a87a52e9872bf16d1a21211a4b22ccab3010bfd78ac1ccf3e6c",
        anchor="left",
        bbox=(70, 561, 485, 1235),
        anchor_why=(
            "LEFT, and it is a framing fix and not a preference. The composite mask "
            "reaches original x=67 and a centred crop starts at original x=81.7, so "
            "the left edge of the authored region falls outside the frame. "
            "Left-anchored the whole mask lands at output x 70..485 with 218 px of "
            "air to the RIGHT, and the discarded strip (original x > 668.7) is open "
            "field with no figure and no plant in it -- checked by eye on the real "
            "crop before this job was filed."),
        skin=(232, 352, 282, 404),
        skin_where="his cheek and jaw, below the eye and above the black scarf",
        success_action=(
            "he DUCKS DOWN behind the little plant and freezes there reading as CAUGHT OUT rather than resigned, while the plant still hides almost none of him"),
        skin_f000="R 101.5 G 108.2 B 70.1, R-B 31.4, luma 101.8 (std 20.8)",
        action=(
            "He ducks down low behind the little two-leaf plant and freezes there, "
            "trying to hide behind it: his head and shoulders drop toward the "
            "grass, his eyes go wide and dart to one side, and then he holds "
            "completely still. The plant hides almost none of him and he stays "
            "plainly visible in full view. He stays down where he is and does not "
            "stand up and does not leave the frame."),
        neg_extra="hidden behind the plant, concealed, obscured, out of sight, "
                  "standing up, walking, running, ",
        script_line=(
            "Beat 03 BAD COVER (0:11-0:16), node.md:38 verbatim: \"The scavenger "
            "crouches behind a trunk that hides roughly one-sixth of him.\" The "
            "preceding beat 02 THE SPRINT (node.md:35) is where he \"dives behind "
            "the sapling's thin trunk\", so the dive is beat 02's action and beat "
            "03 is the held, inadequate cover it lands in. THE `trunk` WORDING IS "
            "SUPERSEDED by the founder's ruling that the sapling is tiny "
            "(\"thats ridiculous, lmao. the sapling is tiny\"); the END STATE -- "
            "cover that is comically inadequate -- is what the beat needs."),
        bar_beat={
            "B1_the_cover_is_comically_inadequate": (
                "At f120 he is still plainly visible with the plant in front of him "
                "and hiding a strip of him and nothing more. A clip in which the "
                "plant grows enough to actually conceal him FAILS the beat -- "
                "beats.'03'.done_when says so in as many words: 'A crouch that "
                "actually conceals him fails the beat.'"),
            "B2_he_reads_CAUGHT_OUT_rather_than_RESIGNED": (
                "THE CLAUSE THIS RUNG EXISTS FOR, and the open item the plate's own "
                "verdict left: r1s1 read 'RESIGNED, not caught out', and the "
                "composite pass fixed the size-and-position relation without "
                "touching the acting. PASS needs a visible DUCK -- head and "
                "shoulders lower than they start -- and a held freeze after it. "
                "Judged at 1:1 by eye. This is the one clause a metric cannot "
                "decide and none is offered for it."),
        },
        risk=("F-STANDS-UP: the only motion this plate obviously affords from a "
              "kneeling pose is rising, and 'he does not stand up' is the kind of "
              "abstract prohibition the b04 head-lock rung proved a positive "
              "placement beats. If he rises, the next rung is a positive placement "
              "of the DOWN attitude ('his shoulders stay below the top of the "
              "leaves in every frame'), not a seventh wording of the negative."),
    ),
    dict(
        new_id="ep2-b13-shademotion-0820",
        beat=13,
        tag="shademotion",
        out_base="13-the-shade-LTX-sapcomp-0820",
        src_dir="ep2-b13-sapcomp-0820",
        src_png="b13-sapcomp-s20260820.png",
        src_sha="bb0ad70c4294aa1647a0db1567df30482c97780359adc799818ff1dd88e0f7b2",
        mask_png="13-the-shade-sapcomp-mask-0820.png",
        mask_sha="702ce6b0cb0584ae6ac0080b85b317d9afd2333fdf0102bf17d6dfc9696d013e",
        anchor="left",
        bbox=(14, 681, 265, 1236),
        anchor_why=(
            "LEFT, and this is the one that would have cost a GPU fire. The "
            "composited sapling begins at original x=13 and a centred crop begins "
            "at original x=81.7: 72 px of the plant -- the subject of the clause "
            "this whole composite route exists to satisfy -- would be OUTSIDE THE "
            "FRAME, on the beat whose r1s1 verdict was 'NO IDENTIFIABLE SAPLING'. "
            "Left-anchored it lands at output x 14..265. 14 px is a thin margin and "
            "it is stated rather than rounded up; the framing assert refuses below "
            "8."),
        skin=(286, 282, 352, 336),
        skin_where="his cheek, below the eye and clear of the ink linework",
        success_action=(
            "he TIPS HIS HEAD SIDEWAYS into the plant's small patch of shade until it falls across his eyes, from a seat he never leaves -- no slide and no rise"),
        skin_f000="R 100.1 G 123.8 B 65.7, R-B 34.4, luma 110.1 (std 6.0)",
        action=(
            "He is already sitting folded small in the grass beside the little "
            "two-leaf plant with his knees up. He tips his head slowly sideways "
            "into the plant's small patch of shade until the shade falls across "
            "his eyes, lets his shoulders drop, and breathes out. He stays sitting "
            "exactly where he is with his knees up, and he does not stand up, does "
            "not slide, and does not move to a different spot."),
        neg_extra="sliding down a trunk, sliding, standing up, getting up, "
                  "lying down, moving to a different spot, ",
        script_line=(
            "Beat 13 THE SHADE (1:00-1:04), node.md:88 as rewritten 2026-08-17 and "
            "RATIFIED BY THE FOUNDER 2026-08-18 by his own board ruling -- \"the "
            "shipped version stands (no slide, he sits down beside it, thin "
            "shade)\": \"The scavenger's legs give out and he drops to sit in the "
            "grass at the base of the stem, then tips his head sideways into the "
            "sapling's hand-sized patch of shade -- the only part of him it will "
            "cover -- knees up around his ears.\" THE PLATE IS ALREADY THE SEATED "
            "END STATE, so the only action left in the beat is the head tipping "
            "into the shade. Rendering a slide would be re-opening a question the "
            "founder closed."),
        bar_beat={
            "B1_NO_SLIDE_AND_NO_RISE": (
                "He stays seated where the plate puts him for all 121 frames. This "
                "is a FOUNDER RULING, not a steward preference -- 'no slide, he sits "
                "down beside it' -- and a clip that stands him up or slides him is a "
                "FAIL however well it moves."),
            "B2_the_head_tips_sideways_into_the_shade": (
                "A visible sideways tip of the head, ending with the shade patch on "
                "his eyes. Read at 1:1. If nothing tips, the finding is that this "
                "engine will not move a head that starts already lowered, and the "
                "next rung is a positive placement of the END attitude rather than "
                "of the movement."),
            "B3_folded_small_knees_up_holds": (
                "Knees still up around his ears at f120. The plate's ACTION clause is "
                "the one thing beat 13 already had -- its r1s1 was 'THE BEST OF THE "
                "THREE... PASS on cast and on pose' -- so losing it to motion would "
                "be a net regression even if everything else passed."),
        },
        risk=("F-NOTHING-MOVES. This is the most static of the three inits -- he is "
              "already folded, already down, already still -- and `--image-crf 10` "
              "exists precisely to hold an init hard. A frozen clip here is a real "
              "outcome and is scored as a FAIL of B2, not as a safe result."),
    ),
]


# --------------------------------------------------------------------------
def fetch_init_py(b):
    """Restore the plate AND its mask to the courier path they came from."""
    return '''#!/usr/bin/env python3
"""RESTORE beat {beat:02d}'s composite plate AND ITS MASK to the courier path
they were published from, and refuse on any sha mismatch.

No model, no GPU, no spend. Both files were written on this box by
{src_dir}'s publish step into
courier-box\\\\farm-out\\\\{src_dir}\\\\, but the box's courier
worktree is not a reliable place to find them later -- beat 19's had been
cleaned out by the time its motion job ran -- so they are re-fetched under the
sha256 the manifest recorded. Anyone who clones the repo can verify both
numbers.

THEY ARE RESTORED TO THEIR OWN PUBLISHED PATH rather than into this job's
payload directory, and that is not cosmetic. box_enqueue refuses a --src it
cannot trace: it reads farm-out/<dir>/<file>, fetches that plate from
origin/farm-results-rtx5090 to CHECK THE PICTURE, and resolves <dir> to the one
spec whose publish step owns it. A payload-directory path defeats both checks,
and "could not check" is not "fine". The sha assertion is what makes the
restore safe: a different file cannot take this name.

THE MASK IS FETCHED TOO because assert_framing.py reads it. The plant's
authored footprint is the only honest way to ask "is the sapling wholly in the
cropped frame" on a green object over a green field -- a colour predicate has
produced a clean, wrong number twice in this ladder.
"""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\courier-box\\farm-out\\{src_dir}"
RAW = ("{raw}{src_dir}/")
UA = {{"User-Agent": "banyan-city-{new_id}/1.0 (albert.numbro@gmail.com)"}}
WANT = {{
    "{src_png}":
        "{src_sha}",
    "{mask_png}":
        "{mask_sha}",
}}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %s -- refusing.\\n   want %s\\n   have %s"
                 % (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %s %d bytes sha %s OK" % (name, len(raw), have), flush=True)
'''.format(beat=b["beat"], src_dir=b["src_dir"], raw=RAW_BASE,
           new_id=b["new_id"], src_png=b["src_png"], src_sha=b["src_sha"],
           mask_png=b["mask_png"], mask_sha=b["mask_sha"])


def assert_framing_py(b):
    x0, y0, x1, y1 = b["bbox"]
    return '''#!/usr/bin/env python3
"""REFUSE TO RENDER IF THE COMPOSITED SAPLING IS NOT WHOLLY IN THE CROPPED INIT.

Beat {beat:02d}'s whole reason for having a composite plate is that a canon
two-leaf sapling is in the frame. A framing bug that clips it costs a GPU fire
and produces a clip that cannot be judged on its only interesting clause -- and
a CENTRED cover-crop discards 81.7 ORIGINAL px off each side of an 832x1216
plate, which is enough to do exactly that on two of this rung's three beats.

THE INSTRUMENT IS THE COMPOSITE MASK, NOT A COLOUR PREDICATE, and that choice
is the whole reason this file differs from beat 19's. These plants are green
objects on green fields; this ladder has twice recorded a colour predicate
returning a clean, wrong number on exactly that ground (the green-OR-purple
growmotion mask that manufactured a 3.9x area step, and the b08 material probe
that landed on a sleeve at 100% "pale"). The mask is the plant's own authored
footprint, published beside the plate. Pushed through the IDENTICAL cover-crop
transform it gives the plant's exact output bbox with no predicate at all.

WANT_BBOX below was measured on a Mac against the real published bytes BEFORE
this job existed, so it cannot be moved afterwards to fit.

No model, no network, no GPU. Reads two PNGs.
"""
import sys
from PIL import Image

INIT = sys.argv[1]
MASK = r"C:\\banyan-farm\\courier-box\\farm-out\\{src_dir}\\{mask_png}"
W, H = 704, 1280
ANCHOR = "{anchor}"
WANT_BBOX = ({x0}, {y0}, {x1}, {y1})   # pre-registered
TOL = 4        # LANCZOS on a dilated mask is stable well inside this
MARGIN = 8     # px of frame the plant must clear on every side

im = Image.open(INIT).convert("RGB")
if im.size != (W, H):
    sys.exit("!! wrong init size %dx%d -- refusing." % im.size)

m = Image.open(MASK).convert("RGB")
sw, sh = m.size
scale = max(W / float(sw), H / float(sh))
nw, nh = int(round(sw * scale)), int(round(sh * scale))
m = m.resize((nw, nh), Image.LANCZOS)
if ANCHOR == "center":
    left = (nw - W) // 2
elif ANCHOR == "left":
    left = 0
else:
    left = nw - W
top = (nh - H) // 2
m = m.crop((left, top, left + W, top + H)).convert("L")

px = m.load()
xs = [x for x in range(W) if any(px[x, y] > 127 for y in range(0, H, 2))]
ys = [y for y in range(H) if any(px[x, y] > 127 for x in range(0, W, 2))]
if not xs or not ys:
    sys.exit("!! the composite mask is EMPTY after the crop -- the sapling is "
             "not in the frame at all. REFUSING.")
got = (min(xs), min(ys), max(xs), max(ys))
print("mask bbox x %d..%d y %d..%d (anchor=%s, want x %d..%d y %d..%d)"
      % (got[0], got[2], got[1], got[3], ANCHOR,
         WANT_BBOX[0], WANT_BBOX[2], WANT_BBOX[1], WANT_BBOX[3]), flush=True)

off = [abs(g - w) for g, w in zip(got, WANT_BBOX)]
if max(off) > TOL:
    sys.exit("!! mask bbox %s is not the pre-registered %s (max off %d > %d). "
             "The crop this job measured is not the crop it got. REFUSING."
             % (got, WANT_BBOX, max(off), TOL))
if got[0] < MARGIN or got[1] < MARGIN or got[2] > W - 1 - MARGIN \\
        or got[3] > H - 1 - MARGIN:
    sys.exit("!! the sapling touches a frame edge (bbox %s in %dx%d, margin "
             "%d). REFUSING." % (got, W, H, MARGIN))
print("FRAMING OK -- the composited sapling is wholly inside the cropped init. "
      "margins L%d R%d T%d B%d"
      % (got[0], W - 1 - got[2], got[1], H - 1 - got[3]), flush=True)
'''.format(beat=b["beat"], src_dir=b["src_dir"], mask_png=b["mask_png"],
           anchor=b["anchor"], x0=x0, y0=y0, x1=x1, y1=y1)


def stamp_sidecar_py(b):
    return '''#!/usr/bin/env python3
"""Stamp the clip's provenance sidecar.

video_task.write_sidecar records model, prompt, negative, init sha and
cost_usd 0, and it does not record whether the clip may ship. Appended here
rather than asserted in a commit message nobody downstream reads. REFUSES if
the sidecar is missing -- a clip whose provenance file did not get written must
not pass silently.
"""
import os, sys

META = sys.argv[1]
if not os.path.isfile(META):
    sys.exit("!! no sidecar at %s -- refusing to call the job clean." % META)
with open(META, "a", encoding="utf-8", newline="\\n") as fh:
    fh.write(
        "# --- appended by {new_id} after the render.\\n"
        "approved: false\\n"
        "provisional: true\\n"
        "is_show_content: true\\n"
        "note: |\\n"
        "  BEAT {beat:02d}'S FIRST MOTION SAMPLE OFF A COMPOSITE PLATE, a candidate\\n"
        "  for the beat's cut slot and not an engine probe. Conditioned on\\n"
        "  {src_png}, the plate\\n"
        "  {src_dir} produced and this lane\\n"
        "  did not re-pick. Judged against the bar pre-registered in\\n"
        "  pipeline/jobs/{new_id}.yaml BEFORE this render\\n"
        "  existed. NOT approved and NOT cut until all 121 frames have been\\n"
        "  opened consecutively.\\n"
        "  THE PLANT CLAUSE OVERRIDES THE PERFORMANCE CLAUSE. Beat 19's motion\\n"
        "  take turned a two-leaf sapling into a four-leaf prostrate runner in\\n"
        "  90 frames and undid four drawing rounds. If the plant is not one\\n"
        "  rooted stem with two leaves at frame 121, this clip is a FAIL\\n"
        "  however well he acts.\\n"
        "  STEWARDSHIP.md 6 is DISCHARGED for this beat -- node.md:204, the\\n"
        "  founder read and approved the 2026-08-17 rewrites on 2026-08-19 --\\n"
        "  which is what makes a footage render legal here. It confers no\\n"
        "  verdict on these pixels.\\n")
print("stamped %s" % META, flush=True)
'''.format(new_id=b["new_id"], beat=b["beat"], src_png=b["src_png"],
           src_dir=b["src_dir"])


def jobs_encode_json(b):
    d = b["new_id"]
    p = "b%02d" % b["beat"]
    return ('[\n {\n  "beat": %d,\n'
            '  "embeds": "C:\\\\banyan-farm\\\\%s-out\\\\%s-embeds.pt",\n'
            '  "prompt_file": "C:\\\\banyan-farm\\\\%s\\\\%s-motion-prompt.txt",\n'
            '  "negative_file": "C:\\\\banyan-farm\\\\%s\\\\%s-negative.txt"\n }\n]\n'
            % (b["beat"], d, p, d, p, d, p))


def jobs_render_json(b):
    d = b["new_id"]
    p = "b%02d" % b["beat"]
    return ('[\n {\n  "beat": %d,\n  "seed": %d,\n'
            '  "embeds": "C:\\\\banyan-farm\\\\%s-out\\\\%s-embeds.pt",\n'
            '  "init": "C:\\\\banyan-farm\\\\%s-out\\\\%s-init-704x1280.png",\n'
            '  "out": "C:\\\\banyan-farm\\\\%s-out\\\\%s.mp4"\n }\n]\n'
            % (b["beat"], SEED, d, p, d, p, d, b["out_base"]))


def prompt_text(b):
    return "%s %s %s %s\n" % (b["action"], PLANT_CLAUSE, IDENTITY_CLAUSE,
                              STYLE_TAIL)


def negative_text(b):
    return b["neg_extra"] + NEG_COMMON + "\n"


SCRIPT_AUTHORITY = (
    "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
    "`approved_on: 2026-08-03`. STEWARDSHIP.md 6 IS DISCHARGED FOR THIS BEAT AND "
    "THE RECORD IS node.md:204: the five beats rewritten 2026-08-17 to play at "
    "knee height (12, 13, 15, 19, 20) were put to the founder verbatim and his "
    "answer was \"all approved\" on 2026-08-19; beat 13 was additionally ratified "
    "2026-08-18 by his own board ruling. node.md states the consequence in as "
    "many words: \"voice synthesis, footage render and episode assembly are legal "
    "for all five beats as now written\". THIS IS A SILENT MOTION CLIP: no voice "
    "synthesis, no episode assembly, no publication, and the approval confers no "
    "verdict on the pixels. The one thing 6 still gates on this node is the "
    "2026-08-18 beat-17 shake restage, which this job does not touch. "
    "SUPERSESSION NOTE, because a reader will find the other sentence: "
    "pipeline/jobs/ep2-b15-macplate-publish-0819.yaml says the beat-15 6 gate is "
    "LIVE. It was, when that spec was written on the morning of 08-19; the "
    "approval landed later the same day.")


BAR_COMMON = {
    "A1_THE_PLANT_HOLDS_and_this_clause_outranks_the_others": (
        "At f120 there is exactly ONE plant with ONE thin stem and TWO leaves, "
        "still rooted, still shorter than he is. Read at 1:1 on f000/f030/f060/"
        "f090/f120 and then consecutively if those five pass. THIS IS THE "
        "PRE-REGISTERED TOP RISK ON ALL THREE JOBS and it is not theoretical: "
        "ep2-b19-dropmotion-0819's F-PLANT-REVERT fired hardest of its fail "
        "modes -- two leaves became four or more, one fig became two, an upright "
        "stem became a horizontal runner, and a plant that cost four drawing "
        "rounds and a closed three-rung wording ladder was undone in 90 frames. "
        "No beat-19 job had ever checked the count under motion. This one does, "
        "and a plant that reverts is a FAIL of the job whatever else lands."),
    "A2_THE_RATIFIED_ADULT_GOBLIN_HOLDS": (
        "The same lean wiry adult goblin man at f120 as at f000 -- green skin, "
        "bald head, long pointed ears -- with no drift toward a human or a "
        "child. Canon: pipeline/canon.yaml ep2-goblin-design-adult, "
        "founder-ratified 2026-08-19. THE PROBE IS PLACED BY EYE AT 5x ON SKIN "
        "AND NOT ON CLOTH, and it publishes its MATERIAL and not only its luma: "
        "the b08 rung's first probe was placed by colour, landed on a cream "
        "sleeve, and would have passed a naive material test with a clean wrong "
        "number. Box, region and f000 reading are in `skin_probe` below; f120 "
        "must sit within +/-25 luma and +/-15 R-B of it, and BOTH numbers are "
        "published whatever the verdict. The probe is the filter and the eyes "
        "decide: this recipe has now carried the ratified adult through 121 "
        "frames on b04 and b09, so a failure here is news."),
    "A3_CAMERA_LOCKED": (
        "No pan, tilt, dolly or zoom. Inherited clause; the parent held it, and "
        "beat 19's raw horizon shift was shown to be field RE-INKING rather than "
        "a camera move by the region-consistency test -- so a raw [dx,dy] fit is "
        "reported with its per-region spread or not at all."),
    "A4_IT_IS_NOT_FROZEN": (
        "Real motion, judged at 1:1. FAIL-FROZEN is a genuine outcome on all "
        "three of these and is NOT a safe result. NO WHOLE-FRAME INTERFRAME "
        "FLOOR IS SET: beat 19's tracker self-test showed a PERFECT 32px subject "
        "move over a frozen background reads 0.056 whole-frame and would fail "
        "any such floor. A near-still beat puts its floor on the TRACKED "
        "SUBJECT, never on the frame."),
    "A5_NO_EXPOSURE_BLOWOUT_and_this_one_is_RE_ROLLABLE": (
        "Whole-frame mean luma f000 -> f120 within +25. Measured because the "
        "growmotion five measured it: five seeds of ONE recipe on ONE init came "
        "back at +67.70, +57.06, +43.56, +22.42 and +10.68 -- a 6x spread that "
        "is SEED-SENSITIVE, not a property of the recipe. So a blowout here is "
        "re-rolled with a second seed before any flag is touched, and it is "
        "recorded as a seed result rather than as a recipe verdict."),
}


def build(b, force=False):
    p = "b%02d" % b["beat"]
    child = derive_spec.derive(
        src=PARENT,
        new_id=b["new_id"],
        by="pipeline/derive_sapcomp_motion_0820.py",
        fresh=dict(
            owner="the composite-plate motion lane, 2026-08-20",
            consumer=(
                "The episode 2 cut, beat %02d, which is a SLATE today. The "
                "composite-then-inpaint route put a canon two-leaf sapling into "
                "this beat's plate on 2026-08-20 and that closed the PLATE "
                "question; a plate is not footage, so the slate did not move. "
                "This clip is the first candidate the beat has ever had with a "
                "real sapling in it. Immediately downstream: the beat's entry in "
                "review/ep2-picks/ and, if it passes, a founder screening -- the "
                "cut swap itself is a taste call and is not proposed here."
                % b["beat"]),
            success=(
                "ONE 704x1280 121-frame mp4 off %s in which %s -- AND the "
                "composited sapling is still ONE rooted stem with TWO leaves at "
                "frame 121. Both halves are required. A clip that acts the beat "
                "and loses the plant is a FAIL, because the plant is what four "
                "wording ladders and twenty-four artifacts could not deliver and "
                "what one composite finally did; a clip that keeps the plant and "
                "does nothing is a FAIL of the beat. Scored against the "
                "pre-registered bar below and nothing else."
                % (b["src_png"], b["success_action"])),
            why=(
                "$0, ~12 minutes, no download, and the card is idle with an empty "
                "backlog while three converted plates sit with no motion take "
                "against any of them. Every generative parameter is inherited "
                "from the b14 crf-10 LTX recipe as cloned for beat 19: only the "
                "init picture and the words change, so a bad result is "
                "attributable to this beat rather than to the recipe. Filed with "
                "its two siblings at one seed so a difference between the three "
                "is a difference between the PLATES."),
        ),
        overrides={
            "argv:--src": ("C:\\banyan-farm\\courier-box\\farm-out\\%s\\%s"
                           % (b["src_dir"], b["src_png"])),
            "argv:--sha256": b["src_sha"],
            "argv:--anchor": b["anchor"],
            "key:beat": b["beat"],
            "key:script_authority": SCRIPT_AUTHORITY,
            "key:script_line": b["script_line"],
            "payload:fetch_init.py": fetch_init_py(b),
            "payload:assert_framing.py": assert_framing_py(b),
            "payload:stamp_sidecar.py": stamp_sidecar_py(b),
            "payload:%s-motion-prompt.txt" % p: prompt_text(b),
            "payload:%s-negative.txt" % p: negative_text(b),
            "payload:%s-jobs-encode.json" % p: jobs_encode_json(b),
            "payload:%s-jobs-render.json" % p: jobs_render_json(b),
            "seed": SEED,
        },
        retoken=[
            # THE PARENT ID GOES FIRST BY HAND, and this is not redundant with
            # the pair derive_spec appends. That one runs LAST, and the `b19-`
            # rule below would otherwise reach `ep2-b19-dropmotion-0819` first
            # and rewrite it to `ep2-b15-dropmotion-0819` -- a payload directory
            # named after a beat that is not this one and a parent id that no
            # longer matches anything. Caught on the first --dry-run.
            ("ep2-b19-dropmotion-0819", b["new_id"]),
            ("19-the-drop-LTX-sapgloss-0819", b["out_base"]),
            ("bench-b19-dropmotion", "bench-%s-%s" % (p, b["tag"])),
            ("ep2-b19-sapgloss-0819", b["src_dir"]),
            ("b19-", "%s-" % p),
        ],
        extra={
            "bar": dict(BAR_COMMON, **b["bar_beat"]),
            "skin_probe": {
                "box_xyxy_in_the_704x1280_init": list(b["skin"]),
                "placed_on": b["skin_where"] + " -- SKIN, not cloth, chosen by "
                             "eye at 5x on the real cropped init and not by any "
                             "colour rule",
                "f000_reading": b["skin_f000"],
                "how_to_read_it": (
                    "Re-measure the same box on f120 and publish R, G, B, R-B and "
                    "luma beside these. A green-skinned figure on a green field is "
                    "exactly the case where one scalar decides nothing, so the "
                    "whole triple is published and the verdict is written by eye "
                    "against it."),
            },
            "framing_measured_before_the_gpu": {
                "anchor": b["anchor"],
                "why": b["anchor_why"],
                "cover_crop_arithmetic": (
                    "832x1216 -> 704x1280 scales by 1.0526 to 876x1280, so the "
                    "vertical is untouched and 172 px come off the horizontal. A "
                    "centred crop discards 81.7 ORIGINAL px per side."),
                "composite_mask_bbox_in_the_cropped_init": list(b["bbox"]),
                "asserted_by": (
                    "assert_framing.py, before the model loads, against these "
                    "exact numbers -- and by the mask rather than by a colour "
                    "predicate, because these are green plants on green fields."),
            },
            "init_provenance": (
                "farm-out/%s/%s, sha256 %s. Produced by pipeline/jobs/%s.yaml, "
                "which scored PASS on its one variable on 2026-08-20: a canon "
                "two-leaf sapling composited into the plate and CONVERTED (not "
                "pasted) by 12 of 40 denoising steps at strength 0.30. NOT a "
                "founder pick and not approved -- its sidecar says approved: "
                "false, provisional: true. Byte-identity verified three ways "
                "before this spec was written: the local copy on main, the blob "
                "on origin/main, and the blob on origin/farm-results-rtx5090 "
                "that box_enqueue's plate guard actually reads."
                % (b["src_dir"], b["src_png"], b["src_sha"], b["src_dir"])),
            "the_plate_was_hand_carried_to_the_results_branch": (
                "TRUE FOR BEATS 03 AND 13, and said out loud because it is a "
                "guard-adjacent act. The courier has pushed nothing to "
                "origin/farm-results-rtx5090 since 2026-08-19T17:54 -- the branch "
                "tip before 2026-08-20 was itself another lane's hand-carry of "
                "beat 04's plate for the same reason. box_enqueue.plate_problems "
                "reads --src off that branch and nowhere else, so both plates "
                "were carried across byte-identical and re-hashed on the branch "
                "afterwards. THE ALTERNATIVE WAS A plate_ack: \"unfetchable\" "
                "WAIVER AND IT WAS NOT TAKEN: the guard's value is declining to "
                "wave through a picture it cannot see, and one of the two jobs "
                "that hit it in the 2026-08-14 wave was cropping the WRONG "
                "BEAT'S plate. Beat 15's plate was already on the branch, pushed "
                "by the runner on 08-19."),
            "failure_predicted_in_advance": b["risk"],
            "pre_registered_fail_modes": [
                "F-PLANT-REVERT -- the composited sapling grows leaves, sprouts a "
                "second stem, lies down or turns into a bush. Beat 19's, and the "
                "one this rung most expects.",
                "F-PLANT-DISSOLVES -- the sapling smears back into the field. The "
                "beat-13 composite named this as its own top risk and it did not "
                "fire at strength 0.30; 121 frames of i2v is a different and "
                "longer exposure to the same risk.",
                "F-FROZEN -- nothing moves. A real outcome, never a safe one.",
                "F-IDENTITY-DRIFT -- he stops being the ratified lean adult.",
                "F-EXPOSURE -- the whole frame blooms pale, as four of the five "
                "growmotion seeds did. Seed-sensitive; re-rolled, not re-flagged.",
                "F-WRONG-BEAT-ANIMATED -- the engine renders an adjacent beat's "
                "action, as beat 19's take rendered beat 20's fig-in-hands with "
                "no hand action prompted and `fruit in his hands` first in the "
                "negative. Positive placement beats negatives, sighted six times.",
            ],
            "not_done_on_purpose": (
                "NO RECIPE CHANGE OF ANY KIND. Size, frames, fps, guidance, "
                "distilled sigmas, two-stage, offload, mode and --image-crf 10 "
                "are all the parent's. No crf sweep -- 33 is established wrong, "
                "10 is established workable, and the optimum between them is not "
                "this beat's question. No second seed unless A5 fires. No re-pick "
                "of the plate, no plate_ack, no cut, no publication. --frames 121 "
                "is a RENDER LENGTH and not a trim: shortening it renders a "
                "different clip rather than a cut-down of this one."),
        },
    )
    out = os.path.join("pipeline", "jobs", "%s.yaml" % b["new_id"])
    return derive_spec.write(child, out, force=force)


def main():
    force = "--force" in sys.argv
    for b in BEATS:
        print(build(b, force=force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
