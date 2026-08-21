#!/usr/bin/env python3
"""AGE B, EXPRESSIVE FACES, AND THE BROKEN TUSK -- the three 2026-08-21 rulings
turned into job yaml.

    python3 pipeline/derive_jerry_ageb_0821.py sample     # beat 13, ONE frame
    python3 pipeline/derive_jerry_ageb_0821.py wave       # the seven beats
    python3 pipeline/derive_jerry_ageb_0821.py isolate    # only if the sample breaks
    python3 pipeline/derive_jerry_ageb_0821.py --selftest

WHAT THIS FILE IS FOR. `pipeline/derive_jerry_wave_0821.py` emits the seven-beat
patch wave at the ADULT proportion with the frozen mannequin face. All three of
those things were ruled on this morning and this file is the same wave with the
rulings applied. It is a separate file rather than an edit because the adult wave
already RENDERED and was judged -- b02/b03/b07/b13/b20 passed, b04/b08 went to
round two -- and overwriting the deriver that produced those verdicts would make
them unreproducible.

THE THREE RULINGS, and each one names what it moves.

  1. AGE = OPTION B. Founder, 2026-08-21: "younger, not chibi"; then, shown the
     nine-frame ladder, "these are practically the same and they look
     lifeless... i already approved enough goblin images for you to decide".
     The final call is DELEGATED and B is the steward's, veto-able in one line.
     B is head_frac 0.240 -- 4.17 heads -- and the wording column w2,
     `teenage goblin boy, slim, soft rounded jaw`, because that is the exact
     frame he was shown as B (review/ep2-goblin-age-0821/B-h240-kid.png is
     sha-identical to farm-out/ep2-jerry-age-h240w2-0821/...-ipahead.png). The
     ladder's own finding is that the wording barely moves the age and the
     geometry does all of it, so w2 is carried for fidelity to the pixels he
     looked at, not because the adjectives are load-bearing.

  2. EXPRESSIVE FACES. The blank-eyes/expressionless block is STRUCK AS THE
     DEFAULT. It was identity-instrument scaffolding from the era when wording
     was the only lever on the face, and it produced mannequins -- "lifeless",
     his word, about frames that passed every clause of the bar. Identity is now
     held by the ADAPTER (ip-adapter-plus-face at the tile's own head crop), the
     SKELETON and the AGE GEOMETRY, none of which existed when that block was
     written. Each beat's plate carries ITS OWN emotion, read off that beat's
     stage direction in node.md, as positive expression tags.

     STRUCK: `blank eyes`, `jitome`, `half-closed eyes` -- and, from the older
     tile recipe that some plates still carry, `expressionless`, `:|` and
     `closed mouth`.
     KEPT: `tsurime` and `thick eyebrows`. These are not expressions. `tsurime`
     is the tile's own upward-slanting slit SHAPE and `thick eyebrows` is the
     brow the P1 clause scores; striking them would move the face's geometry
     under cover of a ruling about its mood.

  3. THE BROKEN TUSK RETURNS. It is in the script -- node.md, THE SPRINT:
     "A SCAVENGER -- goblin-ish, enormous ears, one broken tusk, patchwork
     cloak". It has never once been in a prompt. The founder asked what happened
     to the original design; this is what happened to it. Positive tag.

WHAT IS NOT ON THE TABLE, because a ruling on three axes is not a ruling on all
of them: the adapter, its reference crop, its scale, the openpose net and its
scale, the seed, the checkpoint, and every creature attribute the tile owns --
green skin, bald dome, no nose bridge, the SHORT LOW SWEPT-BACK EAR FLANGE. The
ear especially. Danbooru has no tag for it, absence-plus-suppression is the only
thing that has ever drawn it, and it now has to survive a bigger head AND an
expression. That is the clause most likely to be quietly lost, so it is scored
first in the bar below.

$0 to emit. No model, no network, no GPU.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import author_jerry_skel_0820 as skel   # noqa: E402
import derive_fetch_guard               # noqa: E402
import derive_spec                      # noqa: E402
import jerry_standard_0821 as S         # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 1. THE AGE. ──────────────────────────────────────────────────────────────
AGE_B_HEAD_FRAC = 0.240          # 4.17 heads. OPTION B.

# THE AGE CLAUSE IS w1, NOT THE w2 THAT DREW THE PICKED FRAME, AND THE SWAP IS
# PAID FOR IN MEASUREMENT RATHER THAN CONVENIENCE. B-h240-kid.png is sha-
# identical to the w2 render, so w2 is what he was shown. But the ladder's own
# headline finding is that inside a row the three wordings were NEARLY
# INDISTINGUISHABLE -- "the age you are looking at is carried by proportion, not
# by adjectives" -- and all three h240 frames are published for anyone to check
# that claim rather than take it. The geometry, which is what actually carries
# the read, is identical.
#
# WHAT BUYS THE SWAP IS CLIP'S 77-TOKEN CEILING, and it is a hard refusal, not a
# preference: controlnet_plate.token_overflow REFUSES a prompt past 77 because
# diffusers TRUNCATES SILENTLY and what falls off the end is the TAIL -- which in
# every prompt in this repo is the POSE. A frame rendered with its pose truncated
# looks like the recipe failed. Ruling 2 and ruling 3 add ~16 tokens between
# them, so something had to come out of a 72-token prompt, and the honest place
# to take it from is the axis this tree has MEASURED as decorative.
AGE_B_CLAUSE = "young goblin, slim"
AGE_B_CLAUSE_SHOWN = "teenage goblin boy, slim, soft rounded jaw"   # w2, for the record

# The four stances the wave needs at B. `stand` already exists from the ladder
# and keeps its published digest; these were authored this morning by the same
# author_jerry_skel_0820.build() with head_frac 0.240 and nothing else moved.
AGE_B_SKELETONS = {
    "jerry-skel-h240-0821":       ("stand",
        "8d42ffbb42434449dabe3e9c06d19e20fe182097bc11d1abe9980a4ad41195e8"),
    "jerry-skel-h240seat-0821":   ("seatspan",
        "1e95abc723f366f2e8c6b486937cfe8709edcbe2d8af0186fa82461c8e792686"),
    "jerry-skel-h240stride-0821": ("stride",
        "f6150add3a2c603b2681d5e2f5c76e252ccb2442c43d15d285e7b15141eb67a2"),
    "jerry-skel-h240crouch-0821": ("crouch",
        "57fcd5fcaf8186a786708cf9afd839d49bb1759392b3d12b7bdd5ca35c03aece"),
    "jerry-skel-h240hunch-0821":  ("hunch",
        "8b42677cb09f534bcbcf7682a4d19e2ce4248484266239d9496e85ae4749600c"),
}
S.SKELETONS.update(AGE_B_SKELETONS)


# ── 2. THE MASK, AND WHY IT IS TWO RULES COMPOSED AND NOT A NEW GUESS. ───────
def age_mask_stand(head_frac=AGE_B_HEAD_FRAC):
    """k6a's box SCALED about its own centre by head_frac / 0.190.

    THE LADDER'S RULE, byte-for-byte, and it is reused rather than re-derived
    because Option B's pixels were rendered through it: at 0.240 this returns
    289,101,541,379, which is the --ip-mask on ep2-jerry-age-h240w2-0821, which
    is the frame the founder was shown as B. Re-deriving a "better" box here
    would mean the wave is not rendering the thing he picked.

    The scale is necessary and the translation rule alone is not enough: every
    pose before the ladder held head_frac at 0.190, so the head was the same
    SIZE in every frame. This moves head_frac itself, and at 0.240 the authored
    head is 1.26x k6a's -- a box that used to sit a little outside the head
    starts sitting INSIDE it, and the adapter would paint a face onto the middle
    of a skull and leave its edges to the checkpoint's own prior, which is the
    man-read.
    """
    k = head_frac / S.HEAD_FRAC
    x0, y0, x1, y1 = S.MASK_STAND
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hw, hh = (x1 - x0) * k / 2.0, (y1 - y0) * k / 2.0
    return [max(0, int(round(cx - hw))), max(0, int(round(cy - hh))),
            min(S.RENDER_W, int(round(cx + hw))),
            min(S.RENDER_H, int(round(cy + hh)))]


def age_mask(pose, head_frac=AGE_B_HEAD_FRAC):
    """The standing age box TRANSLATED by this pose's head-block offset.

    ONE RULE PER AXIS, each already validated on its own axis, composed in the
    order they were established: SCALE for head_frac (the ladder, nine frames),
    then TRANSLATE for pose (the standard, nine poses). Both hold at 0.240 for
    the same reason they held at 0.190 -- the five head keypoints move as one
    rigid block when a pose lowers them, so a pose never resizes the head box,
    it only slides it. For `stand` the delta is zero and this returns Option B's
    own mask.
    """
    bx, by = _head_centre(pose="stand", head_frac=head_frac)
    cx, cy = _head_centre(pose=pose, head_frac=head_frac)
    dx, dy = cx - bx, cy - by
    r = age_mask_stand(head_frac)
    r = [int(round(r[0] + dx)), int(round(r[1] + dy)),
         int(round(r[2] + dx)), int(round(r[3] + dy))]
    r[0] = max(0, r[0]); r[1] = max(0, r[1])
    r[2] = min(S.RENDER_W, r[2]); r[3] = min(S.RENDER_H, r[3])
    if r[2] - r[0] < 40 or r[3] - r[1] < 40:
        raise ValueError("pose %r at head_frac %r leaves a %dx%d mask"
                         % (pose, head_frac, r[2] - r[0], r[3] - r[1]))
    return "%d,%d,%d,%d" % tuple(r)


def _head_centre(pose, head_frac):
    kp, _ = skel.figure(head_frac, pose=pose)
    xs = [kp[k][0] for k in S.HEAD_KEYPOINTS]
    ys = [kp[k][1] for k in S.HEAD_KEYPOINTS]
    return sum(xs) / len(xs), sum(ys) / len(ys)


# ── 3. THE WORDING. ──────────────────────────────────────────────────────────
# k6a's head with the age clause swapped and the mannequin block removed. What
# is left of the identity clause is the tile's SHAPE, not its mood.
PROMPT_LEAD = "masterpiece, best quality, very aesthetic, 1boy, solo"
IDENTITY = "green skin, bald head, patchwork cloak, tsurime, thick eyebrows"
TUSK = "tusks, broken tusk"

# STRUCK from k6a's frozen positive by ruling 2, listed so a later lane can see
# exactly what left and put it back in one line if the sample says to.
STRUCK = ("blank eyes", "jitome", "half-closed eyes")

# The ladder's negative, unchanged: k6a's minus `child` (he asked for a kid read
# and negating `child` fights the ruling) plus the three that carry his floor.
# NOTHING IS ADDED HERE FOR THE EXPRESSION OR THE TUSK. Ban et al. (ECCV 2024,
# arXiv:2406.02965) and this tree's own w1 rung both say a negative acts only
# after the positive has drawn the thing, so a negative cannot pre-empt a tag we
# are adding on purpose -- it can only be the wrong instrument, loudly.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, pointy ears, "
            "long pointy ears, elf, monster boy, pointy nose, dot nose, "
            "human face, wrinkled skin, old man, hair, beard, chibi, "
            "super deformed, round-bellied, squat, grey skin, pale skin")


MAX_TOKENS = 77


def prompt_for(expression, pose_words):
    """Lead, age, identity, tusk, THIS BEAT'S EMOTION, pose. In that order."""
    p = ", ".join([PROMPT_LEAD, AGE_B_CLAUSE, IDENTITY, TUSK,
                   expression, pose_words])
    n = tokens(p)
    if n > MAX_TOKENS:
        raise SystemExit(
            "!! %d tokens, %d past CLIP's %d, and controlnet_plate REFUSES it "
            "rather than letting diffusers truncate the POSE off the tail:\n   "
            "%s" % (n, n - MAX_TOKENS, MAX_TOKENS, p))
    return p


def tokens(text):
    """Exact where a CLIP tokenizer exists, the repo's tag-calibrated estimate
    where it does not -- which is here, and it reads ~5% HIGH. An over-estimate
    is the safe direction: it costs a word we did not have to cut, where an
    under-estimate costs a render and a round trip to the card."""
    import sd_prompt
    return sd_prompt.negative_tokens(text)


# ── 4. THE SEVEN BEATS, THEIR STANCES AND THEIR EMOTIONS. ────────────────────
# beat, skeleton, pose words, expression tags, the stage direction they come from
#
# THE POSE WORDS ARE ROUND ONE'S, UNCHANGED, INCLUDING b04's AND b08's ROUND-TWO
# CORRECTIONS. This wave moves age, expression and the tusk; re-litigating the
# stances at the same time would make every result unattributable. Where round
# two already replaced a wording (b04 stood upright, b08 drew a bare belly) the
# round-two wording is what is carried, because that is the wording that passed.
#
# EVERY EXPRESSION TAG IS A DANBOORU TAG, for the reason canon gives: the
# checkpoint's own card says animagine-xl-3.1 is "optimized for Danbooru-style
# tags rather than natural language", and the fourteen-sample tile read was won
# by tags and lost by sentences.
#
# FOUR BEATS ARE TRIMMED AGAINST CLIP'S 77 AND EACH CUT IS NAMED, because a
# silent trim is how a pose disappears off the tail and gets blamed on a recipe:
#   b04  `leaning out to one side ... looking sideways` -> `leaning out
#        sideways`. Round two's finding was that the words must name THE LEAN
#        AND THE DIRECTION -- round one only said `leaning out past tall grass
#        blades` and the figure stood upright. Both are still named, in three
#        words instead of six. `looking to the side` also left the EXPRESSION
#        group, where it never belonged: a gaze direction is a pose, not a mood.
#   b13  `head lowered` cut. The stage direction is that he tips his head
#        SIDEWAYS into the shade, not down, and the seatspan skeleton already
#        places the head; this was round one's wording, not the script's.
#   b20  `with both hands` cut. It is in the script, and this plate is judged
#        ON THE CREATURE -- the wave's own consumer note says the fig's colour
#        and the branch are beat 20's separate canon question and untouched
#        here. `surprised` also cut: `wide-eyed, open mouth` IS the surprise,
#        and three tags for one emotion spends tokens on redundancy.
#   b13  `parted lips` cut for the same redundancy reason -- `light smile`
#        already carries E2's "the mouth is doing something".
WAVE = [
    ("02", "jerry-skel-h240stride-0821",
     "walking, arm outstretched, in tall grass, full body",
     "scared, wide-eyed, open mouth",
     "THE SPRINT -- 'sprints into frame, skids, and dives behind the sapling's "
     "thin trunk'. He is running from the guards and has not seen the sapling "
     "yet. This is the most frightened he is in the episode."),
    ("03", "jerry-skel-h240crouch-0821",
     "squatting, hiding behind a thin trunk, in tall grass, full body",
     "nervous, sweatdrop, looking to the side",
     "BAD COVER -- 'crouches behind a trunk that hides roughly one-sixth of "
     "him'. The comedy is that he believes it is working, so the face is "
     "furtive rather than terrified -- held breath, not a scream."),
    ("04", "jerry-skel-h240hunch-0821",
     "hunched over, leaning out sideways, in tall grass, full body",
     "wide-eyed, parted lips",
     "THE FOOTNOTE -- 'leans out from behind the trunk to look, and pulls "
     "straight back the moment he has looked'. THE PEEK, which is the "
     "founder's own restaging pick (A, 2026-08-20). The eyes are the whole "
     "beat: rung 1 and rung 2 both measured that on this engine the gaze does "
     "not move without the head, so the LOOK has to be in the plate."),
    ("07", "jerry-skel-h240-0821",
     "standing, arms at sides, beside tall grass, full body",
     "nervous, sweatdrop, frown",
     "CONFISCATE -- 'Guard 1 points at the scavenger, decisive.' He is the "
     "object of the sentence and has just been identified. Apprehension, not "
     "panic: the guards are absurd and he is starting to notice."),
    ("08", "jerry-skel-h240-0821",
     "standing, head bowed, looking down, arms at sides, in tall grass, "
     "full body",
     "embarrassed, blush, frown",
     "INSIDE HIM -- 'Guard 2 lowers the clipboard and points at the "
     "scavenger's belly.' He is caught, and the thing he is caught with is "
     "already eaten. Sheepish. NOTE the round-two finding held: the words ask "
     "for the LOOK DOWN and never name the belly, because round one named it "
     "and the model drew a bare round pot belly and with it the child read."),
    ("13", "jerry-skel-h240seat-0821",
     "sitting, hands clasped between knees, in tall grass, full body",
     "tired, half-closed eyes, light smile",
     "THE SHADE -- 'The scavenger's legs give out and he drops to sit in the "
     "grass at the base of the stem, then tips his head sideways into the "
     "sapling's hand-sized patch of shade'. Line: '...Thanks for the shade.' "
     "EXHAUSTED RELIEF, and the first kind thing that happens to him."),
    ("20", "jerry-skel-h240crouch-0821",
     "squatting, holding a small fruit, looking up, in tall grass, full body",
     "wide-eyed, open mouth",
     "EVIDENCE -- 'crouches back down, picks the fig up with both hands, and "
     "looks from it to the sapling's thinnest branch beside him'. Line: "
     "'...Did you just ANSWER me?' Awe. This is the episode's turn and the "
     "one frame where a blank face costs the story its ending."),
]
WAVE_BY_BEAT = {b: row for row in WAVE for b in (row[0],)}


# ── 5. THE BAR. ──────────────────────────────────────────────────────────────
BAR = """THE k6a BAR WITH THE THREE RULINGS FOLDED IN. Read at 1:1 against
review/ep2-goblin-design-0819/adult-b19-0819.jpg for the CREATURE and against
review/ep2-goblin-age-0821/B-h240-kid.png for the AGE.

  IDENTITY -- unchanged, and this is what the rulings put at risk.
  T4  SHORT LOW SWEPT-BACK EAR FLANGES, not spikes. SCORED FIRST because it is
      the clause with no instrument behind it: Danbooru has no tag for this
      ear, absence-plus-suppression is the only thing that has ever drawn it,
      and it now has to survive a bigger head AND an expression. If this is
      lost, the pivot has a cost nobody has priced.
  T1  NO IRIS, NO PUPIL, NO LASHES. `blank eyes` IS STRUCK, so this clause is
      now carried by the ADAPTER alone. It is the single most likely thing to
      break and the sample exists to find out.
  T1b EYE SIZE <= 1.4x the tile's relative to the head box; EYE SHAPE <= 0.65.
      NOT relaxed for expression. `wide-eyed` is a legitimate emotion on beats
      02, 04 and 20 and it is also a direct argument with this clause.
  T2  NO HUMAN NOSE -- no bridge, no tip, no drawn nostrils.
  T3  NO AGE MODELLING -- no brow furrows, no folds, no jowls. A YOUNGER read
      makes this easier, not harder; a frame that fails it has gone the wrong
      way down the axis entirely.
  T7  NO PATCHWORK ON THE SKULL.
  C1  CONTAINMENT -- green head to foot, no purple cowl, no horns.
  C2  THE POSE IS THE ONE ASKED FOR.

  AGE -- the founder's axis, now decided.
  A1  READS AS OPTION B. Not merely younger than the tile: this frame and
      B-h240-kid.png should look like the same character, and 4.17 heads is
      measurable rather than a matter of opinion.
  A2  NOT THE KILLED DESIGN. His floor, verbatim: "NOT the killed round-chibi
      design". Round-bellied, squat or mascot FAILS.

  EXPRESSION -- the new axis, and the one the whole change is for.
  E1  THE BEAT'S EMOTION IS LEGIBLE WITH THE CAPTION COVERED. Not "has a
      face": a stranger shown this frame and the beat's stage direction should
      agree they match. This is the clause "lifeless" was about.
  E2  A MOUTH, AND IT IS DOING SOMETHING. P3 asked only that a line exist,
      because `closed mouth, :|` kept drawing none at all. The bar is raised:
      the mouth carries part of the emotion.
  E3  IT IS STILL HIM. An expression that changes the face's SHAPE -- a
      different jaw, a different eye geometry, a human cast under the emotion
      -- fails, and fails as an IDENTITY problem, not a mood one.

  THE TUSK.
  K1  ONE TUSK, AND IT IS BROKEN. Two intact tusks is a MISS and a named one:
      `tusks` is the plural Danbooru tag and `one broken tusk` is the script's
      own words rather than a tag with a post count behind it, so if the count
      or the break is wrong the wording is the suspect and the fix is a tag,
      not another adjective.
  K2  IT DID NOT COST THE MOUTH. A tusk drawn over a closed muzzle that has
      lost its lipless line is a regression on P3/E2.

A frame failing ANY clause is REJECTED. Near-misses are what made the 31-frame
LoRA set untrainable."""


PREDICTED = """THREE THINGS ARE MOVING AND I EXPECT THEM TO FAIL IN A KNOWN
ORDER. Filed before the render.

MOST LIKELY TO BREAK: T1, and it is `blank eyes` leaving. Canon's own words are
"`blank eyes` IS THE WHOLE GAME and `no nose` IS THE SECOND HALF" -- that
sentence was written when WORDING WAS THE ONLY LEVER, before the adapter, the
skeleton and the reference crop existed, and the whole claim of ruling 2 is that
the instrument has changed under the finding. If the eyes come back with irises,
the finding survived the instrument change and the answer is not to re-argue: it
is to put `blank eyes` back and get the emotion from the MOUTH and BROW alone,
which is one rung and is the isolate mode of this file.

SECOND: K1, two intact tusks. `tusks` is plural in Danbooru and there is no tag
for a broken one. I expect the tag to fire and the BREAK to be ignored, which is
a partial pass and is worth having -- the tusk is in the script and has been
absent from every prompt this tree has ever run.

THIRD, AND THE ONE THAT WOULD COST THE MOST: T4, the ear. It has no tag holding
it up. The age ladder already flagged that a younger read and a rounder head are
the same direction, and now an expression is being asked for on top. This did not
break at 0.240 on the ladder's standing frames, which is real evidence, but the
ladder's frames were expressionless.

WHAT I DO NOT EXPECT TO MOVE: the age. The ladder rendered 4.17 heads across
three different wordings and they were "nearly indistinguishable", so the
geometry is carrying it and an expression is not a geometric change.

AND ONE HONEST WEAKNESS OF THIS SAMPLE, said out loud rather than discovered
later: beat 13's emotion is `tired, half-closed eyes, light smile, parted lips`,
and `half-closed eyes` is a tag k6a ALREADY CARRIED. So the sample tests the
STRIKE of `blank eyes`/`jitome` hard and the tusk hard, and tests the
expression-tag axis only weakly. The beats that really test it are 02, 04 and 20,
where `wide-eyed` and `open mouth` argue with T1b directly. That is a reason to
judge the wave on its own faces rather than assume the sample covered them -- it
is NOT a reason to sample three beats, because the thing that can break the
identity is the same in all seven and beat 13 is the frame the founder actually
ruled on."""


ONE_SAMPLE = """ONE FRAME, AND IT IS BEAT 13.

The rule is one sample per RECIPE CHANGE, and this is a recipe change on three
axes at once, so it gets a sample before anything is scaled. Beat 13 is the beat
to spend it on for two reasons that are not convenience: it is the frame the
founder pointed at when he said the goblin reads as an adult ("this is one of the
images where the goblin looks like an adult, which is wrong"), and it was the
BEST PASS of the adult wave's round one, so a break here is attributable to the
three new things and not to a beat that was already marginal.

NOTHING SCALES OFF THIS UNTIL IT IS JUDGED BY EYE AT 1:1. If identity breaks, the
`isolate` mode of this file emits the one-variable rungs -- expression alone,
tusk alone -- and the wave waits. If it holds, the wave is seven frames and each
one is judged on its own face."""


def head_fit_mask(pose, head_frac=AGE_B_HEAD_FRAC):
    """THE HEAD'S OWN BOX, derived from the skeleton instead of inherited.

    FILED 2026-08-21 AFTER THE SAMPLE, and it is a defect report on our own
    instrument rather than a tuning knob. `age_mask` scales k6a's box about THE
    BOX'S OWN CENTRE, and that centre was authored 20 px above the head-keypoint
    centre so it would clear a standing figure's cranial dome. Scaling about it
    keeps the offset while growing the box, and moving head_frac ALSO moves the
    head down (nose_y = crown + 0.55 * head_h), so the two errors add.

    MEASURED on beat 13's seatspan skeleton at 0.240: crown is at y=439 and chin
    at y=673, and `age_mask` returns 364..642 -- SEVENTY-FIVE PIXELS OF SKY above
    the crown and the CHIN CUT OFF at the bottom. The adapter was conditioning
    background and the top of a skull while the mouth was left to the
    checkpoint. That is consistent with what the sample actually drew: tile-true
    blank eyes (inside the mask) under a mouth the checkpoint chose (outside it).

    WHY THIS IS NOT RETROFITTED ONTO age_mask SILENTLY: Option B's standing frame
    rendered through the old box and measured C1 at 0.00%, because above a
    standing head there is only sky and the error was harmless. It is folded
    poses that pay. The old rule stays where its pixels are, this one is filed as
    a rung, and whichever wins becomes the rule for the wave.
    """
    kp, meta = skel.figure(head_frac, pose=pose)
    hp = meta["head_px"]
    hw = skel.HEAD_RATIO * hp
    xs = [kp[k][0] for k in S.HEAD_KEYPOINTS]
    cx = sum(xs) / len(xs)
    crown = kp["nose"][1] - 0.55 * hp
    r = [int(round(cx - hw / 2)), int(round(crown)),
         int(round(cx + hw / 2)), int(round(crown + hp))]
    r[0] = max(0, r[0]); r[1] = max(0, r[1])
    r[2] = min(S.RENDER_W, r[2]); r[3] = min(S.RENDER_H, r[3])
    return "%d,%d,%d,%d" % tuple(r)


def _emit(new_id, job_dir, hint, pose_words, expression, why, consumer, success,
          variable, beat, priority, extra_keys=None, prompt=None,
          mask=None, ip_scale=None, force=False):
    pose = S.SKELETONS[hint][0]
    mask = mask or age_mask(pose)
    ipa = S.ip_adapter_block(hint, pose)
    # The standard's block is authored for head_frac 0.190 and would record this
    # frame's geometry as the adult's. Three keys are corrected and each one says
    # what it now is; nothing else in that block moves.
    ipa["head_frac"] = AGE_B_HEAD_FRAC
    ipa["mask"] = mask
    ipa["mask_rule"] = (
        "TWO RULES COMPOSED, in the order they were established, and neither is "
        "new here. (1) SCALE: k6a's authored box %s scaled about its own centre "
        "by %.3f/%.3f = %.4f, which is the age ladder's own rule and returns "
        "%s for a standing figure -- the mask Option B was rendered through. "
        "(2) TRANSLATE: slid by this pose's head-block offset at head_frac "
        "%.3f. The five head keypoints move as one rigid block, so a pose "
        "slides the head box and never resizes it. Derived by "
        "pipeline/derive_jerry_ageb_0821.age_mask(%r)."
        % (",".join(str(v) for v in S.MASK_STAND), AGE_B_HEAD_FRAC,
           S.HEAD_FRAC, AGE_B_HEAD_FRAC / S.HEAD_FRAC,
           ",".join(str(v) for v in age_mask_stand()), AGE_B_HEAD_FRAC, pose))
    ipa["age_ruling"] = (
        "OPTION B of the age ladder, head_frac %.3f (4.17 heads). Founder "
        "2026-08-21 ruled the axis younger and then delegated the pick: "
        "\"these are practically the same and they look lifeless... i already "
        "approved enough goblin images for you to decide\". B is a STEWARD "
        "PICK and is veto-able in one line (R4). The reference crop is still "
        "the ADULT tile's head and is deliberately unchanged -- it supplies "
        "the creature, the skeleton supplies the age." % AGE_B_HEAD_FRAC)

    extra = {
        "bar": BAR,
        "the_one_variable": variable,
        "the_rung_this_is_one_variable_from": S.PARENT_ID,
        "failure_predicted_in_advance": PREDICTED,
        "one_sample_rule": ONE_SAMPLE,
        "ip_adapter": ipa,
        "founder_ruling_verbatim": (
            "younger, not chibi ... these are practically the same and they "
            "look lifeless... i already approved enough goblin images for you "
            "to decide"),
        "the_expression_ruling": (
            "STRUCK from k6a's frozen positive: %s. Plus `expressionless`, "
            "`:|` and `closed mouth` from the older tile recipe, wherever a "
            "plate still carries them. KEPT: `tsurime` (the tile's slit SHAPE) "
            "and `thick eyebrows` (the brow P1 scores) -- those are geometry, "
            "not mood, and striking them would move the face under cover of a "
            "ruling about its expression. ADDED, from THIS BEAT's stage "
            "direction in node.md: `%s`."
            % (", ".join("`%s`" % t for t in STRUCK), expression)),
        "the_tusk_ruling": (
            "`%s`. It is in the script and has never been in a prompt: "
            "node.md, THE SPRINT -- \"A SCAVENGER -- goblin-ish, enormous "
            "ears, one broken tusk, patchwork cloak\". The founder asked what "
            "happened to the original design. `tusks` is a Danbooru tag; `one "
            "broken tusk` is the script's own words and is the part expected "
            "to be ignored, which the K1 clause scores." % TUSK),
        "stage_direction": WAVE_BY_BEAT[beat][4] if beat in WAVE_BY_BEAT else "",
    }
    extra.update(extra_keys or {})

    overrides = {
        "argv:--control": "pipeline/control/%s.png" % hint,
        "argv:--control-sha256": S.SKELETONS[hint][1],
        "argv:--ip-mask": mask,
        "argv:--repo-commit": S.ASSET_COMMIT,
        "payload:prompt.txt": prompt or prompt_for(expression, pose_words),
        "payload:negative.txt": NEGATIVE,
        "key:beat": int(beat),
        "key:priority": priority,
        "key:est_minutes": 4,
    }
    if ip_scale is not None and ip_scale != S.IP_SCALE:
        overrides["argv:--ip-scale"] = ip_scale
        ipa["scale"] = ip_scale
    child = derive_spec.derive(
        src=S.PARENT,
        new_id=new_id,
        fresh={"owner": "wave lane, 2026-08-21",
               "why": why, "consumer": consumer, "success": success},
        overrides=overrides,
        retoken=[(S.PARENT_DIR_TOKEN, job_dir)],
        extra=extra,
        by="pipeline/derive_jerry_ageb_0821.py",
    )
    py = r"C:\banyan-farm\venv\Scripts\python.exe"
    child["steps"][0] = {"name": "stage",
                         "argv": [py, "-c", S.stage_step(job_dir, hint)]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [py, "-c",
                                   S.publish_step(job_dir, new_id, hint)]}
    child["artifacts"] = [r"C:\banyan-farm\%s\out\%s-%s.png"
                          % (job_dir, new_id, S.ARM)]

    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    for flag, want in (("--control", "pipeline/control/%s.png" % hint),
                       ("--control-sha256", S.SKELETONS[hint][1]),
                       ("--ip-mask", mask),
                       ("--ip-ref-sha256", S.IP_REF_SHA),
                       ("--ip-scale", ip_scale or S.IP_SCALE),
                       ("--ip-weight", S.IP_WEIGHT),
                       ("--scale", S.CONTROL_SCALE),
                       ("--seed", str(S.SEED)),
                       ("--arm", S.ARM),
                       ("--task", new_id)):
        if argv.count(flag) != 1:
            raise SystemExit("!! %s: %s appears %d times"
                             % (new_id, flag, argv.count(flag)))
        got = argv[argv.index(flag) + 1]
        if got != want:
            raise SystemExit("!! %s: %s is %r, want %r"
                             % (new_id, flag, got, want))
    joined = repr({k: v for k, v in child.items() if k != "derivation"})
    if S.PARENT_DIR_TOKEN in joined:
        raise SystemExit("!! %s still names the parent job dir" % new_id)
    if S.IP_WEIGHT_SHA not in joined:
        raise SystemExit("!! %s does not record the adapter digest" % new_id)
    # The rulings have to be IN the payload, not only in the prose around it.
    pay = child["payload"][r"C:\banyan-farm\%s\prompt.txt" % job_dir]
    # RULING 2 STRUCK THE BLOCK AS THE *DEFAULT*, NOT AS VOCABULARY, and this
    # guard has to encode that difference or it forbids the ruling's own point.
    # Beat 13's emotion is `tired, half-closed eyes, light smile` -- THE SHADE is
    # a man whose legs gave out, and half-closed eyes is what exhaustion looks
    # like. A struck tag arriving because a BEAT EARNED IT is the mechanism
    # working; the same tag arriving in the identity clause on every plate is the
    # mannequin coming back. So: absent from the identity clause always, allowed
    # in the expression group, and never both.
    ident = ", ".join([PROMPT_LEAD, AGE_B_CLAUSE, IDENTITY, TUSK])
    for t in STRUCK:
        if t in ident:
            raise SystemExit("!! %s: struck tag %r is back in the DEFAULT "
                             "identity clause" % (new_id, t))
        if t in pay and t not in (expression or ""):
            raise SystemExit("!! %s: struck tag %r is in the positive but is "
                             "not this beat's emotion" % (new_id, t))
    if TUSK not in pay:
        raise SystemExit("!! %s: the tusk is not in the positive" % new_id)
    if expression and expression not in pay:
        raise SystemExit("!! %s: the beat's expression is not in the positive"
                         % new_id)

    out = "pipeline/jobs/%s.yaml" % new_id
    derive_spec.write(child, out, force=force)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out),
        must_hold=(S.DRIVER, hint + ".png", S.IP_REF + ".png"))
    print("wrote %s\n   skel=%-28s mask=%-19s\n   +  %s"
          % (out, hint, mask, pay))
    return out


SAMPLE_CONSUMER = """THE JUDGEMENT THAT UNBLOCKS THE WHOLE AGE PIVOT, and
nothing else renders until it is made. On this one frame depend: the seven-beat
plate wave at age B, seven motion tranches derived from those plates, the LoRA
dataset re-curation at age B with expression variety, and `train-jerry`. All of
them are HELD -- 14 motion jobs, 20 dataset scene jobs, 2 plates and the training
job were renamed `.HOLD-age-pivot-0821` the moment the founder ruled, because
every one of them would have rendered the adult.

WHAT HAPPENS ON EACH VERDICT, decided now so the verdict is not also a design
session:
  PASS  -- the seven-beat wave is emitted and queued in one batch, judged in one
           pass, picked per beat. Motion follows per passing plate.
  BREAK -- `derive_jerry_ageb_0821.py isolate` emits the one-variable rungs
           (expression alone at age B; tusk alone at age B) and the wave waits
           for the attribution. NOT a fourth wording.

review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. Four judgements stand between
this frame and the cut -- plate judged, plate picked, motion rendered, motion
passed -- and this job is the first."""


def sample(force=False):
    beat, hint, pose_words, expression, direction = WAVE_BY_BEAT["13"]
    return [_emit(
        new_id="ep2-b13-ageb-s1-0821",
        job_dir="b13ageb-s1-0821",
        hint=hint, pose_words=pose_words, expression=expression,
        why="""THE ONE SAMPLE FOR THE 2026-08-21 AGE PIVOT. Three rulings land in
this frame at once and no set is rendered until it is judged by eye at 1:1.

  1. AGE = OPTION B, head_frac 0.240, 4.17 heads, wording column w2. The
     founder ruled the axis younger and then handed the pick back: "these are
     practically the same and they look lifeless... i already approved enough
     goblin images for you to decide". B is the steward's call and is veto-able.

  2. EXPRESSIVE FACES. `blank eyes`, `jitome` and `half-closed eyes` are struck
     as the DEFAULT and this beat's own emotion is asked for instead: `%s`,
     read off THE SHADE's stage direction. "Lifeless" was his word about frames
     that passed every clause of the old bar, which is a bar problem, not a
     draw problem. Identity is now held by the adapter, the skeleton and the
     age geometry -- instruments that did not exist when the mannequin block
     was written.

  3. THE BROKEN TUSK. In the script since the first draft, in a prompt never.

WHY BEAT 13 AND NOT ANOTHER. This is the frame he ruled the adult read on --
"this is one of the images where the goblin looks like an adult, which is wrong"
-- and it was round one's best pass at the adult proportion, so anything that
breaks here is attributable to the three new things rather than to a beat that
was already marginal.

WHAT IS HELD BYTE-IDENTICAL TO k6a so the attribution is real: the adapter, its
weight digest, its reference crop, its scale 0.7, the openpose net at 1.0, the
seed 20260823, the checkpoint, the resolution, and this beat's POSE WORDS from
round one. The skeleton changes only in head_frac and the mask only by the two
composed rules that follow from it.""" % expression,
        consumer=SAMPLE_CONSUMER,
        success=("ONE 832x1216 png at seed %d. A PASS is: the creature clauses "
                 "hold (T4 ear first, then T1 eyes with `blank eyes` GONE, T2, "
                 "T3, T7, C1), he reads as Option B (A1/A2), the beat's "
                 "exhausted relief is legible with the caption covered (E1/E2/"
                 "E3), and there is ONE tusk and it is broken (K1/K2). A PASS "
                 "releases the seven-beat wave. A BREAK releases the isolate "
                 "rungs and nothing else." % S.SEED),
        variable=("THREE, and they are named because this is a RULING BATCH and "
                  "not a rung: (1) head_frac 0.190 -> 0.240 with the age clause "
                  "`%s`, (2) the mannequin block struck and this beat's emotion "
                  "`%s` in its place, (3) the broken tusk added. They are moved "
                  "together because they are one decision -- a lifeless face at "
                  "the wrong age is not a thing anyone wants a clean rung on -- "
                  "and the ISOLATE mode exists for exactly the case where the "
                  "frame breaks and the attribution matters."
                  % (AGE_B_CLAUSE, expression)),
        beat="13", priority=2,
        extra_keys={"ship_priority": (
            "PRIORITY 2, which outranks everything on the card: the sapling "
            "lane's ten field plates are at 38 and the held ep2 patchwave at "
            "22. This is not a queue-jump for its own sake -- twenty-plus jobs "
            "across four lanes are blocked on this one verdict, and the card "
            "is otherwise running work that nothing waits on."),
            "post_ship_patch": (
            "review/ep2-ship-0821 IS NOT TOUCHED. Plate judged, plate picked, "
            "motion rendered, motion passed -- four judgements, and this job "
            "is the first of them.")},
        force=force)]


def wave(force=False):
    written = []
    for beat, hint, pose_words, expression, direction in WAVE:
        written.append(_emit(
            new_id="ep2-b%s-ageb-p1-0821" % beat,
            job_dir="b%sageb-p1-0821" % beat,
            hint=hint, pose_words=pose_words, expression=expression,
            why=("BEAT %s OF THE SEVEN-BEAT WAVE, RE-RENDERED AT AGE B WITH ITS "
                 "OWN FACE.\n\n%s\n\nTHE ADULT WAVE THIS REPLACES RENDERED AND "
                 "WAS JUDGED THIS MORNING -- b02/b03/b07/b13/b20 passed, b04 "
                 "and b08 went to round two and passed there -- and every one "
                 "of those frames is the wrong age and wears the mannequin "
                 "face. They are kept as evidence, not deleted.\n\nTHE SAMPLE "
                 "THAT RELEASED THIS BATCH is ep2-b13-ageb-s1-0821, judged by "
                 "eye at 1:1 before a single one of these was queued."
                 % (beat, direction)),
            consumer=("The ep2 patch wave's plate for beat %s at the decided "
                      "age. A pass here becomes a plate candidate; the pick is "
                      "a separate judgement and the motion re-derive is a "
                      "separate spec. review/ep2-ship-0821 is NOT touched by "
                      "this job." % beat),
            success=("ONE 832x1216 png at seed %d on the age-B recipe, scored "
                     "on the bar below. The beat's own emotion (E1) is scored "
                     "against the stage direction recorded in this spec, not "
                     "against a general impression of liveliness."
                     % S.SEED),
            variable=("THE BEAT -- its skeleton at head_frac %.3f, its round-one "
                      "pose words, its emotion `%s`, and the mask the skeleton "
                      "implies. The recipe, the age and the tusk are the "
                      "sample's and are identical across all seven, so a frame "
                      "that misses is attributable to the beat."
                      % (AGE_B_HEAD_FRAC, expression)),
            beat=beat, priority=6,
            extra_keys={"post_ship_patch": (
                "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. A plate here "
                "becomes a candidate, a candidate becomes a pick, a pick "
                "becomes a motion spec, and only a passing motion take is "
                "swapped -- four judgements, none of them this job's.")},
            force=force))
    return written


# ── ISOLATION, IF AND ONLY IF THE SAMPLE BREAKS. ─────────────────────────────
# Not queued by default and not queued speculatively. If ep2-b13-ageb-s1-0821
# comes back with irises, a human nose or a lost ear, ONE of the two new tag
# groups did it, and these two frames say which -- each moves ONE group back to
# k6a's frozen value on the same beat, the same skeleton and the same seed.
ISOLATE = [
    ("x1", "the EXPRESSION group alone. The mannequin block is RESTORED and the "
           "tusk stays. If this frame's identity is clean and the sample's was "
           "not, ruling 2 is what broke it and the answer is to keep `blank "
           "eyes` and carry the emotion in the MOUTH and BROW only.",
     "blank eyes, tsurime, jitome, thick eyebrows, half-closed eyes", True),
    ("x2", "the TUSK alone. The tusk is REMOVED and this beat's expression "
           "stays. If this frame is clean, `tusks, one broken tusk` is what "
           "broke it and the answer is a different tag, not a different mood.",
     None, False),
]


def isolate(force=False):
    beat, hint, pose_words, expression, direction = WAVE_BY_BEAT["13"]
    written = []
    for tag, note, identity_override, keep_tusk in ISOLATE:
        parts = [PROMPT_LEAD, AGE_B_CLAUSE]
        if identity_override:
            parts.append(identity_override)
            expr = ""
        else:
            parts.append(IDENTITY)
            expr = expression
        if keep_tusk:
            parts.append(TUSK)
        if expr:
            parts.append(expr)
        parts.append(pose_words)
        written.append(_emit(
            new_id="ep2-b13-ageb-%s-0821" % tag,
            job_dir="b13ageb-%s-0821" % tag,
            hint=hint, pose_words=pose_words, expression=expr,
            prompt=", ".join(parts),
            why=("ISOLATION RUNG %s, fired ONLY because ep2-b13-ageb-s1-0821 "
                 "broke identity. It moves %s\n\nAGE B IS NOT A VARIABLE HERE "
                 "and neither is anything else: head_frac 0.240, the same "
                 "skeleton, the same mask, the same seed, the same pose words. "
                 "One group moves and the other does not." % (tag, note)),
            consumer=("ATTRIBUTION for the age-B sample, and nothing else. The "
                      "seven-beat wave is waiting on which of the two new tag "
                      "groups cost the identity."),
            success=("ONE 832x1216 png. Read against the sample at 1:1: if the "
                     "identity clauses that failed there pass here, this rung's "
                     "group is the cause."),
            variable=("ONE group, and the other is at the sample's value. This "
                      "is the whole point of the rung."),
            beat="13", priority=2,
            extra_keys={"fired_because": (
                "The one-sample rule's other half: a sample that breaks is "
                "isolated before anything is re-scaled. These two rungs are "
                "emitted by `derive_jerry_ageb_0821.py isolate` and are NOT "
                "queued speculatively.")},
            force=force))
    return written


SAMPLE_VERDICT = """ep2-b13-ageb-s1-0821, JUDGED BY EYE AT 1:1 AGAINST BOTH
RULERS (the tile for the creature, B-h240-kid.png for the age), 2026-08-21.
VERDICT: PARTIAL -- the age landed, the identity HELD WHERE IT WAS PREDICTED TO
BREAK, and the ruling the sample existed to prove DID NOT TAKE.

WHAT PASSED, and the first one is the surprise:
  T1  BLANK EYES HELD WITH `blank eyes` STRUCK. Narrow, pale, no iris, no pupil
      -- closer to the tile's slits than Option B's big ovals. This was the
      predicted failure and it did not happen: the ADAPTER carries no-iris-
      no-pupil on its own, which is exactly ruling 2's claim and it is now
      evidence instead of an argument.
  A1  Reads as Option B. Young, big-headed, slim.
  A2  Not the killed design. No belly, no squat, no mascot.
  T7  No patchwork on the skull.
  C2  The pose is the one asked for -- seated, knees up, hands between them.

WHAT FAILED:
  E1  THE EMOTION DID NOT LAND, AND THIS IS THE HEADLINE. The beat is "...Thanks
      for the shade" -- exhausted relief -- and the frame is SCOWLING: brow
      furrowed into an angry V, mouth a downturned frown. `tired, half-closed
      eyes, light smile` did not reach the face. THE CONTROL IS ALREADY IN
      HAND: Option B carries the same scowl with NO expression tags at all, so
      the tags moved nothing and the scowl is what the adapter supplies.
  C1  THE MAGENTA COWL IS BACK. Measured, not eyeballed: 1.17% of the mask
      region against 0.00% for both the k6a anchor and Option B. Round two of
      the adult wave was already chasing this on FOLDED poses (b03, b20) and
      guessed the mechanism was the mask overlapping the neck. This corroborates
      it and adds a cause -- the age mask is 1.26x bigger.
  K1  TWO TUSKS, BOTH INTACT. Predicted in advance: `tusks` is plural and
      nothing in Danbooru tags a BREAK. The tusk arrived, the count and the
      break did not.
  T3  BROW FURROWS -- part of the scowl, and the clause says no age modelling.
  T2  A NOSE NUB. No bridge and no nostrils, so it is not the human nose the
      clause was written against, but it is more of a tip than either ruler
      has.
  T4  METAL SPIKES ON THE EAR FLANGES. The flange shape survived; grey studs
      appeared on it that are on neither ruler.

AND THE MEASUREMENT THAT EXPLAINS MOST OF IT, found while checking C1: THE MASK
IS MISALIGNED, NOT MERELY LARGE. On this pose the crown is at y=439 and the chin
at y=673; the mask ran 364..642. Seventy-five pixels of SKY above the head, and
THE CHIN AND MOUTH CUT OFF below. The adapter was conditioning background and
the top of a skull while the MOUTH was left to the checkpoint -- which is
precisely the split the pixels show: tile-true eyes inside the mask, a
checkpoint-chosen frown outside it. `age_mask` scales k6a's box about the box's
own centre, and that centre was authored 20 px high to clear a standing dome;
raising head_frac also moves the head DOWN. The two errors add, and only a
folded pose pays for them, which is why Option B measured clean.

SO THE NEXT RUNGS ARE NOT THE ONES THIS FILE PRE-WROTE. `isolate` was built for
an identity break and identity did not break. The live question is why the
wording cannot reach the face, and it has two candidate mechanisms that are
separable in two frames."""


ROUND2 = [
    ("m1", "THE MASK, FITTED TO THE HEAD IT IS SUPPOSED TO MASK.",
     "head_fit", None,
     "MECHANISM 1: the adapter is acting on the wrong region. The box is "
     "derived from the skeleton -- crown to chin, head width -- instead of "
     "inherited from a standing figure at another head_frac, and on this pose "
     "that is 323,440,509,673 against the sample's 289,364,541,642. It drops "
     "the sky, and it PICKS UP THE MOUTH.\n\n"
     "THE PREDICTION IS SPLIT AND BOTH HALVES ARE INFORMATIVE. C1 should "
     "improve -- less non-head area for the adapter to transfer a cowl "
     "through. E1 may get WORSE, because a mask that now covers the mouth "
     "hands the mouth to the adapter too, and the adapter's reference is a "
     "tile with a flat lipless line. If C1 clears and E1 worsens, the mask is "
     "the right fix for the COWL and the wrong lever for the EMOTION, and the "
     "two problems are properly separated instead of being one confused rung."),
    ("m2", "THE ADAPTER'S GRIP, LOOSENED SO THE WORDING CAN BE HEARD.",
     None, "0.45",
     "MECHANISM 2: the adapter pins the EXPRESSION along with the identity. "
     "ip-scale 0.7 -> 0.45, and nothing else -- same mask as the sample, so "
     "this is one variable from it.\n\n"
     "THE REASONING IS THE SAMPLE'S OWN CONTROL. Option B wears the same scowl "
     "with no expression tags, and this sample wears it with three. The tags "
     "are not weak, they are OUTVOTED: inside the mask the reference is worth "
     "0.7 and the reference has a face already. If 0.45 lets `tired, "
     "half-closed eyes, light smile` through while T1 still holds, then "
     "ip-scale is the expression dial and ruling 2 is deliverable. If the "
     "expression arrives and the EYES revert to irises, then identity and "
     "expression are the same knob on this instrument and ruling 2 needs a "
     "different reference -- one cropped from a face that is already doing "
     "something -- rather than a different number."),
]

ROUND2_PREDICTED = """THESE TWO CAN BOTH FAIL AND STILL SETTLE THE QUESTION,
which is why they are worth four GPU-minutes each rather than a third wording.

The sample proved the two things a wording rung cannot: the adapter HOLDS the
identity with `blank eyes` struck (T1 passed), and the adapter also holds the
EXPRESSION (E1 failed with three tags against a zero-tag control that looks the
same). Those two facts together say the face is the adapter's, not the prompt's.
So the only levers that can move the emotion are WHERE the adapter acts (m1) and
HOW HARD it acts (m2), and one of them has to give or ruling 2 is not
deliverable at this ip-scale with this reference.

IF BOTH MISS, the honest finding is that the reference crop is the constraint --
a frozen adult face at 0.7 supplies its own mood -- and the next instrument is a
reference that is not expressionless, which is a build step and not a rung. That
would be reported, not attempted the same night."""


def round2(force=False):
    beat, hint, pose_words, expression, direction = WAVE_BY_BEAT["13"]
    written = []
    for tag, headline, mask_mode, ipscale, note in ROUND2:
        pose = S.SKELETONS[hint][0]
        m = head_fit_mask(pose) if mask_mode == "head_fit" else None
        written.append(_emit(
            new_id="ep2-b13-ageb-%s-0821" % tag,
            job_dir="b13ageb-%s-0821" % tag,
            hint=hint, pose_words=pose_words, expression=expression,
            mask=m, ip_scale=ipscale,
            why=("ROUND TWO FOR THE AGE-B SAMPLE. %s\n\n%s\n\n%s"
                 % (headline, note, SAMPLE_VERDICT)),
            consumer=("THE SEVEN-BEAT WAVE, which is held on this. The sample "
                      "settled the age and the identity and left ONE thing "
                      "open -- whether the beat's own emotion can reach the "
                      "face. These two frames name the mechanism; the wave is "
                      "emitted against whichever wins, and if neither does the "
                      "wave ships at the sample's recipe with E1 recorded as "
                      "an engine limit rather than a defect we keep re-asking."),
            success=("ONE 832x1216 png. Judged against ep2-b13-ageb-s1-0821 at "
                     "1:1 on exactly three clauses -- E1 (did the exhaustion "
                     "arrive), T1 (did the blank eyes survive) and C1 (magenta "
                     "in the mask region, measured against the sample's "
                     "1.17%)."),
            variable=("ONE. %s Everything else is the sample's to the byte -- "
                      "same prompt, same negative, same skeleton, same seed, "
                      "same adapter and reference."
                      % ("The MASK, and it is derived from the skeleton rather "
                         "than chosen." if mask_mode else
                         "The IP-ADAPTER SCALE, 0.7 -> 0.45.")),
            beat="13", priority=2,
            extra_keys={
                "round": ("TWO of two. episode-loop-v2 caps a question at two "
                          "rounds. If neither rung lands, the finding is "
                          "recorded as an instrument limit and the wave ships "
                          "at the sample's recipe -- there is no round three."),
                "failure_predicted_in_advance": ROUND2_PREDICTED,
                "the_mask_defect": (
                    "Found while measuring C1 and it outlives this rung: "
                    "`age_mask` puts the box 75 px above the crown on a folded "
                    "pose at head_frac 0.240 and cuts the chin off. Crown 439, "
                    "chin 673, mask 364..642. Only folded poses pay, which is "
                    "why Option B's standing frame measured C1 at 0.00% and "
                    "nobody caught it. If m1 wins, `head_fit_mask` becomes the "
                    "rule for the whole wave and `age_mask` keeps only the "
                    "frames it already rendered.")},
            force=force))
    return written


def _refuses(fn):
    """True if fn() raises. A guard nobody has watched fail is not a guard."""
    try:
        fn()
    except SystemExit:
        return True
    except Exception:
        return True
    return False


def _selftest():
    ok = [True]

    def check(name, cond, detail=""):
        ok[0] = ok[0] and bool(cond)
        print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                               ("  -- %s" % detail) if detail and not cond
                               else ""))

    # THE AGE IS THE GEOMETRY HE WAS SHOWN. The WORDING is w1, and the swap off
    # w2 is recorded rather than silent -- see AGE_B_CLAUSE's own comment.
    check("age clause is the ladder's w1 column",
          AGE_B_CLAUSE == "young goblin, slim")
    check("the w2 wording that drew the picked frame is kept on the record",
          AGE_B_CLAUSE_SHOWN == "teenage goblin boy, slim, soft rounded jaw")
    check("both columns are published pixels, so the swap is checkable",
          all(os.path.exists(os.path.join(
              REPO, "farm-out/ep2-jerry-age-h240%s-0821" % c,
              "ep2-jerry-age-h240%s-0821-ipahead.png" % c))
              for c in ("w0", "w1", "w2")))
    check("head_frac is Option B's 0.240", AGE_B_HEAD_FRAC == 0.240)
    check("0.240 is 4.17 heads", round(1.0 / AGE_B_HEAD_FRAC, 2) == 4.17)
    check("the standing mask IS the one Option B rendered through",
          ",".join(str(v) for v in age_mask_stand()) == "289,101,541,379",
          ",".join(str(v) for v in age_mask_stand()))
    check("mask_for('stand') at 0.190 is unchanged in the standard",
          S.mask_for("stand") == "315,130,515,350")

    # THE STRIKE IS REAL AND IT IS NARROW.
    for t in STRUCK:
        check("struck %r is absent from the identity clause" % t,
              t not in IDENTITY)
    check("`tsurime` is KEPT -- it is shape, not mood", "tsurime" in IDENTITY)
    check("`thick eyebrows` is KEPT -- P1 scores it",
          "thick eyebrows" in IDENTITY)
    check("every struck tag was actually in k6a's positive",
          all(t in S.PROMPT_HEAD for t in STRUCK))
    check("the creature attributes the ruling did NOT touch are all present",
          all(t in IDENTITY for t in ("green skin", "bald head",
                                      "patchwork cloak")))

    # THE NEGATIVE IS THE LADDER'S, AND IT IS THE FLOOR.
    check("`child` is out of the negative -- he asked for a kid read",
          "child" not in NEGATIVE.split(", "))
    check("the round-chibi floor is carried in the negative",
          all(t in NEGATIVE for t in ("chibi", "super deformed",
                                      "round-bellied", "squat")))
    check("the ear's suppression pair survived the pivot",
          "pointy ears" in NEGATIVE and "long pointy ears" in NEGATIVE)

    # SEVEN BEATS, SEVEN EMOTIONS, AND THE AUDIT'S OWN LIST.
    check("the wave is the audit's seven beats",
          [b for b, *_ in WAVE] == ["02", "03", "04", "07", "08", "13", "20"])
    check("every beat has a distinct expression",
          len({e for _, _, _, e, _ in WAVE}) == len(WAVE),
          str(sorted({e for _, _, _, e, _ in WAVE})))
    check("no beat carries the struck block as its emotion",
          not any(t in e for _, _, _, e, _ in WAVE for t in
                  ("blank eyes", "jitome", "expressionless", ":|")))
    check("every beat records the stage direction it read the emotion off",
          all(len(d) > 60 for *_, d in WAVE))

    # THE MASK COMPOSES, AND IT STAYS ON THE HEAD.
    for beat, hint, _, _, _ in WAVE:
        pose = S.SKELETONS[hint][0]
        m = [int(v) for v in age_mask(pose).split(",")]
        cx, cy = _head_centre(pose, AGE_B_HEAD_FRAC)
        check("b%s mask (%s) contains the %s head centre"
              % (beat, age_mask(pose), pose),
              m[0] < cx < m[2] and m[1] < cy < m[3])
        # 200x220 scaled by 0.240/0.190 = 1.2632 is 252.6x277.9, and the box is
        # built by rounding each EDGE rather than the size, so it lands 252x278
        # -- one pixel narrower than the naive product. Asserted at the value it
        # actually takes, because a bar written from arithmetic instead of from
        # the code is how the ladder's T1b bar came to be met only by broken
        # frames.
        check("b%s mask is k6a's box scaled to head_frac 0.240" % beat,
              (m[2] - m[0], m[3] - m[1]) == (252, 278),
              str((m[2] - m[0], m[3] - m[1])))

    # CLIP'S 77, WHICH IS A REFUSAL ON THE CARD AND NOT A WARNING.
    # The estimate reads ~5% high, so a beat at 77 here is probably fine on the
    # box -- and "probably" is a round trip. Every beat is asserted with margin.
    for beat, _, pose_words, expression, _ in WAVE:
        n = tokens(prompt_for(expression, pose_words))
        check("b%s positive fits CLIP's 77 (%d)" % (beat, n), n <= MAX_TOKENS,
              str(n))
    check("the negative fits too, and it is the ladder's unchanged",
          tokens(NEGATIVE) <= MAX_TOKENS, str(tokens(NEGATIVE)))
    check("prompt_for REFUSES an overflow rather than emitting it",
          _refuses(lambda: prompt_for("a, b, c, d, e, f, g, h, i, j, k, l, m",
                                      "n, o, p, q, r, s, t, u, v, w, x, y, z, "
                                      "aa, bb, cc, dd, ee, ff, gg, hh, ii")))

    # THE SKELETONS ARE THE ONES ON DISK AND THE DIGESTS MATCH.
    for stem, (pose, sha) in AGE_B_SKELETONS.items():
        p = os.path.join(REPO, S.ASSET_DIR, stem + ".png")
        check("%s is published" % stem, os.path.exists(p))
        if os.path.exists(p):
            check("%s digest matches the spec" % stem,
                  skel.sha256_file(p) == sha, skel.sha256_file(p))

    # AND THE ONE THING A REGEX WOULD MISS: the tusk is in the script.
    node = os.path.join(REPO, "genomes/sapling/nodes/002b-first-citizen/node.md")
    with open(node, encoding="utf-8") as fh:
        check("the broken tusk is in node.md and this is not invention",
              "one broken tusk" in fh.read())

    print("\n%s" % ("SELFTEST PASS" if ok[0] else "SELFTEST FAIL"))
    return 0 if ok[0] else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    force = "--force" in argv
    argv = [a for a in argv if a != "--force"]
    if not argv or "--selftest" in argv:
        return _selftest()
    written = []
    for m in argv:
        if m == "sample":
            written += sample(force=force)
        elif m == "wave":
            written += wave(force=force)
        elif m == "round2":
            written += round2(force=force)
        elif m == "isolate":
            written += isolate(force=force)
        else:
            print("!! unknown mode %r -- sample | wave | round2 | isolate" % m)
            return 2
    print("\n%d spec(s) written." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
