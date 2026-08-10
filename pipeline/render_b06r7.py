#!/usr/bin/env python3
r"""node 001 beat 06 — ROUND 7, TOO BLUE. Same two options, the door shut. 2026-08-10.

ROUND 6 WORKED AND THEN SOMETHING WALKED IN THROUGH THE SAME HOLE. r6 kept both
of the founder's compositions and fixed the defect he named: the cities are gone
8 of 8, people stay gone 8 of 8, arm A drew tall grass with blades at the camera
4 of 4, arm B drew sky with no ground 4 of 4. Then a LARGE WHITE ANIMAL took over
arm A's s1 and s3 — a cat or wolf face-on filling three quarters of s1, a flank
and a pink ear across s3's upper right, blocking the sky the beat is about
(observed at commit deabee9, `taste/steward-model.ledger.yaml`, record
`ep1-b06-r6-two-arms-observed`).

    ARM A  ground visible, covered in TALL GRASS
    ARM B  no ground at all, the frame is SKY

Both of his readings are still alive and this round still picks between them
nowhere. What changes is one thing.

IT IS THE SAME FAULT AS THE CITIES, ONE ROUND LATER, AND THE FIX IS A CLASS FIX.
r6's sent negative contains no `animal`, no `cat`, no `dog`, no `wolf`, no
`creature` — an animal was never forbidden here, exactly as a city never was, and
at 59 of 77 tokens it was not a trim either. Three rounds running, the defect has
been A NOUN NOBODY HAD EVER NEGATED, found only after somebody looked. Patching
the newest noun would set up round 8 to discover the next one.

So this round adds a PRE-FLIGHT (trap 9) rather than a term. Before a
non-character exterior beat renders, the SENT negative must NAME EVERY CLASS OF
THING THAT CAN OCCUPY A FRAME THE SCRIPT SAYS IS EMPTY — people, animals, built
structure, vehicles, text. Any class not named is a predicted defect and the run
stops. It costs no card time and it would have caught both the city and the
animal before the founder did.

AND `no humans` IS WHY THE ANIMAL CAME, WHICH IS THE UNCOMFORTABLE HALF. On the
vocabulary this checkpoint is captioned in, `no humans` asserts that no HUMAN
character is present — not that the frame is empty of creatures. `animal focus`
is a separate tag in the same vocabulary precisely because such pictures exist
AND are tagged `no humans`, and `tall grass` walks straight into the
animal-in-long-grass composition drawn under both at once. The tag that fixed the
girls opened the door the girls were holding shut. It STAYS — it is r5's one
confirmed win and people are still gone 8 of 8 — and the door gets shut on the
negative side instead, where no person noun is involved (traps 7 and 8 unchanged).

THE BUDGET IS 77 TOKENS AND THAT IS A HARD CEILING HERE, NOT A STYLE CHOICE.
diffusers' SDXL pipeline truncates each CLIP encoder at 77 tokens; the chunked
"unlimited" negatives people are used to are an A1111/ComfyUI behaviour, and in
diffusers they need compel with `truncate_long_prompts=False` and hand-passed
`prompt_embeds`/`pooled_prompt_embeds` (compel #45; diffusers #4043; A1111
discussion #2378, all read 2026-08-10). That is a recipe change and would need
its own one sample, so it is NOT done here. Instead the class block is sized to
what actually fits, measured on the box's real CLIP before the render, and each
arm buys the terms its own composition can actually be invaded by:

    ARM A  animal, animal focus, cat, dog, creature, vehicle, car
    ARM B  animal, bird, aircraft

Arm B is structurally animal-proof for a boring reason — a frame with nothing
but sky has nowhere to put a cat — and what a sky CAN hold is a bird and a
plane. Naming it arm A's way costs four more terms and measured out `jpeg
artifacts`, a quality negative that matters on a smooth blue gradient more than
anywhere else in this episode. Arm A pays a price too and it is recorded rather
than hidden: `realistic skin texture` is sold out of the house tier to fit the
animal block, on the one beat in the episode with no skin in it.

THE CITIES ARE OUR BUG AND THE EVIDENCE IS IN OUR OWN SIDECARS. Every negative
this beat has ever sent was read back from
`takes/stills/06-too-blue-{r3,r4,r5,fix}-s*.png.meta.yaml`, and NOT ONE of them
contains `city`, `cityscape`, `building`, `skyline`, `skyscraper`, `industrial`,
`town` or `architecture`. A city has never once been forbidden on this beat. So
this is not a term that fit_negative trimmed — the token budget was never the
problem here and r5's negative had 26 tokens of headroom (51 of 77, measured on
the box's real CLIP and recorded in its sidecars). The term was never written.

AND THE r5 POSITIVE ASKED FOR THE CITY IN THE MODEL'S OWN DIALECT. r5's one
tactic was to speak native Danbooru tags, and the tag it chose for "a landscape"
was `scenery`. On the vocabulary animagine-xl-3.1 is captioned in, `scenery` is
the umbrella term whose children include `cityscape`: 62,273 posts tagged
`scenery` against 19,945 tagged `cityscape` (Danbooru tag table, read 2026-08-10
via the `qdlabs/danbooru-tags` mirror on HuggingFace — danbooru.donmai.us itself
timed out from here, as it did for r5, and is not cited as if it had been read).
`no humans` at 177,679 posts is the other half of the same distribution: art
tagged "nobody in it" on that site is overwhelmingly landscape AND cityscape.
r5 is the first beat-6 round to carry `scenery`, and r5 is the round that drew a
city through s0's ring and an industrial skyline along s1's bottom edge. So
BOTH arms delete `scenery` from the positive and BOTH negate the urban block
explicitly. Two fixes for one defect, on purpose: the positive stops asking and
the negative starts refusing.

THE ARMS ARE A ONE-PHRASE DELTA FROM EACH OTHER AND FROM r5. Every arm keeps
r5's confirmed win untouched — `no humans` at the HEAD of the POSITIVE, and not
one person noun anywhere in the negative. That mechanism took this beat from a
girl in 2 of 4 (r3) and 3 of 4 (r4) to zero in 4 of 4, and he did not mention
people in this verdict. It is not being reopened while two other things move.

    r5 positive:  no humans, scenery, sky, blue sky, day, cloud, sunlight, …
    ARM A:        no humans, tall grass, grass, sky, blue sky, day, cloud, …
    ARM B:        no humans, sky, blue sky, day, cloud, sunlight, …

WHAT `tall grass` IS WORTH, MEASURED, BECAUSE IT IS WEAKER THAN IT LOOKS.
`tall_grass` is a real tag on this model's vocabulary but a nearly empty one:
785 posts, against 89,292 for plain `grass`. His word is sent because it is his
word and because it is the tag that means what he asked for, but it cannot carry
the frame alone, so `grass` rides behind it as the term with the training mass.
If arm A comes back as a mown lawn, that ratio is the first thing to look at and
it was measured before the render, not after.

ARM A REMOVES `plant` AND `foliage` FROM THE NEGATIVE AND THIS IS THE ONE
JUDGEMENT CALL IN THE FILE. Grass is a plant. Asking for tall grass while
negating `plant, foliage` is the same self-cancelling prompt that r3 sent when it
asked for "one thin wisp of white cloud" against `no big clouds` and got a wall
of cumulus. `leaf`, `stem` and `tree` STAY negated in both arms — those are the
founder's own 2026-08-07 rule and they are about the CHARACTER, not the ground:
"there shouldnt be a leaf in the image, doesnt make sense that he can see himself
when he is looking at the sky." Arm B keeps the full block, since arm B has no
ground and therefore nothing that needs to be a plant.

SHOTS.MD IS NOT EDITED. The fence is asserted byte-for-byte before a weight
loads (trap 1) and the r5 control is rebuilt from this checkout and asserted
against its recorded sidecars (trap 2), so a stale checkout cannot start and the
delta is one measurement rather than two instruments.

MEASURE ON THE BOX OR NOT AT ALL. `sd_prompt._token_estimate` falls back to a
prose approximation without `transformers` and over-counts near 77. This script
exits 8 rather than report an estimate as a measurement.

NOTHING HERE IS A PICK, A PROMOTION, A PUBLICATION OR A SPEND.

Usage:
    python render_b06r7.py --root C:\banyan-farm\banyan-city --arm A --measure
    python render_b06r7.py --root C:\banyan-farm\banyan-city --arm A --dry
    python render_b06r7.py --root C:\banyan-farm\banyan-city --arm A --out <dir>
"""
import argparse
import hashlib
import sys
import time
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
       "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
       "realistic skin texture")
BASE = "cagliostrolab/animagine-xl-3.1"
LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"
W, H, STEPS, CFG = 832, 1216, 40, 7.5
BEAT = 6
NODE = "001-capability-inventory"

# r5's own four, held — this beat's k=4..7, the same seeds r3 and r4 drew. Read
# back from takes/stills/06-too-blue-r5-s{0..3}.png.meta.yaml. Holding them is
# what makes A and B comparable to each other AND to every rejected round.
SEEDS = [20264725, 20265725, 20266725, 20267725]

# THE FENCE, BYTE-FOR-BYTE, from genomes/.../001-capability-inventory/shots.md
# beat 06. r5 rendered exactly this. This round does NOT edit it.
AUTHORED = (
    "no humans, scenery, sky, blue sky, day, cloud, sunlight, cinematic "
    "lighting, detailed, newest, masterpiece, best quality, very aesthetic No "
    "leaf, no plant, no stem, no foliage, no tree. No photorealism, no 3D "
    "render look. 9:16 vertical, no text.")

# WHAT r5 ACTUALLY SENT, from takes/stills/06-too-blue-r5-s2.png.meta.yaml.
# Rebuilt from this checkout and asserted (trap 2).
R5_POS_SENT = (
    "no humans, scenery, sky, blue sky, day, cloud, sunlight, cinematic "
    "lighting, detailed, newest, masterpiece, best quality, very aesthetic")
R5_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, jpeg artifacts, realistic skin "
    "texture, leaf, plant, stem, foliage, tree, photorealism, text")

# The Danbooru tag that has been importing the skyline. Deleted from the
# positive in BOTH arms; see the module docstring for the post counts.
CITY_TAG_IN_POSITIVE = "scenery"

# r5's one deliberate deviation from the machine path, kept unchanged:
# sd_prompt.compress() lifts `no humans` out of the positive and _NEGATION
# appends `humans` to the negative, which on a Danbooru-captioned model inverts
# the tag. The script puts it back at the head and deletes the negated form.
# sd_prompt.py IS NOT MODIFIED BY THIS ROUND.
HEAD_TAG = "no humans"
LIFTED_NEG = "humans"

# Person nouns must stay OUT of the negative. r5 proved they were the wrong
# mechanism on this beat twice over; trap 8 refuses if one comes back.
PERSON_NOUNS = ("humans", "human", "woman", "girl", "boy", "child", "person",
                "face", "hand", "1girl", "1boy", "people")

# What every arm must forbid. Passed in fit_negative's EXPLICIT tier, which is
# last in the drop order house -> scale -> beat -> explicit, so a beat near the
# budget sheds house boilerplate before it sheds the thing the round is for.
CITY_NEG = "cityscape, city, building, skyline, road"

# THE CLASS THAT WALKED IN. `animal focus` is the umbrella this checkpoint's
# vocabulary uses for a picture whose subject is a creature and which is ALSO
# tagged `no humans`; `animal` is the plain noun; `cat`, `dog` and `creature`
# are the children r6 actually drew or is nearest to drawing (s1 reads as a
# white cat or wolf, s3 as a big white flank). `wolf` is deliberately NOT sent:
# it costs budget and `animal, animal focus, creature` already carry it.
ANIMAL_NEG = "animal, animal focus, cat, dog, creature"
# Arm B names the same classes with the terms a SKY can actually hold. A frame
# with no ground has nowhere to put a cat, and `cat, dog, creature, car` on that
# arm cost four terms that measured out `jpeg artifacts` — a quality negative
# that matters on a smooth blue gradient more than anywhere else in the episode.
# What a sky frame can hold is a bird and an aircraft, so those are the terms it
# buys. Class named, budget honest, measured before the render and not after.
ANIMAL_NEG_SKY = "animal, bird"
VEHICLE_NEG_SKY = "aircraft"
# The class r6 named nowhere on either side and which no round has drawn yet.
# Cheap, and its absence is exactly the shape of the last three defects.
VEHICLE_NEG = "vehicle, car"

# TRAP 9, THE OCCUPANCY PRE-FLIGHT — the rule the ledger asked for at deabee9,
# written as code instead of as a resolution. For a beat whose script says the
# frame is empty, every class of thing that can occupy it must be NAMED. A class
# is named if the SENT negative carries any one of its terms — except `people`,
# which is named on the POSITIVE side by `no humans` and must NOT appear in the
# negative (traps 7 and 8: person nouns failed on this beat twice).
OCCUPANCY_CLASSES = {
    "animals": ("animal", "animal focus", "creature", "cat", "dog", "wolf",
                "bird", "furry"),
    "built structure": ("cityscape", "city", "building", "skyline", "road",
                        "architecture", "ruins"),
    "vehicles": ("vehicle", "car", "truck", "boat", "aircraft"),
    "text": ("text", "watermark", "signature", "logo", "username"),
}
OCCUPANCY_POSITIVE_SIDE = {"people": HEAD_TAG}

ARMS = {
    "A": {
        "set": "r7a",
        "label": "ground visible, TALL GRASS",
        # r5's positive with `scenery` replaced by his word plus the term that
        # carries the training mass behind it.
        "pos_sub": ("scenery", "tall grass, grass"),
        # arm A only: grass IS a plant, so negating these would cancel the arm.
        "drop_neg": ("plant", "foliage"),
        "extra_neg": CITY_NEG + ", mountain, " + ANIMAL_NEG + ", " + VEHICLE_NEG,
        "require_pos": ("no humans", "tall grass", "grass"),
        "forbid_pos": ("scenery",),
        "require_neg": ("cityscape", "city", "building", "skyline", "road",
                        "mountain", "leaf", "stem", "tree",
                        "animal", "animal focus", "cat", "dog", "creature",
                        "vehicle", "car"),
        "forbid_neg": ("plant", "foliage"),
        "why": ("HIS OPTION A, WORD FOR WORD: \"show the ground as having tall "
                "grass\". `tall grass` is his term and a real tag on this "
                "checkpoint's vocabulary, but a thin one — 785 posts against "
                "89,292 for `grass` — so `grass` is sent behind it to carry the "
                "conditioning. `plant` and `foliage` come OUT of the negative "
                "for this arm and this arm only: grass is a plant, and asking "
                "for it while forbidding it is the self-cancelling prompt that "
                "gave r3 a wall of cumulus against `no big clouds`. `leaf`, "
                "`stem` and `tree` stay — those are the founder's 2026-08-07 "
                "rule about the CHARACTER, not about the ground. `mountain` is "
                "negated because r5's picked frame added a range the script "
                "never mentions. NEW IN r7: the animal and vehicle classes are "
                "NAMED. r6's arm A drew a large white animal as the subject of "
                "2 of 4 with nothing in the prompt asking for one and nothing "
                "forbidding one — the same fault as the cities, and `tall "
                "grass` plus `no humans` is the animal-in-long-grass "
                "composition on this vocabulary. Everything else in this arm "
                "is r6's, unchanged, because r6's arm A was right about the "
                "grass 4 of 4."),
    },
    "B": {
        "set": "r7b",
        "label": "no ground, SKY only",
        # r5's positive with `scenery` simply deleted.
        "pos_sub": ("scenery", None),
        "drop_neg": (),
        "extra_neg": (CITY_NEG + ", mountain, grass, field, horizon, ground, "
                      + ANIMAL_NEG_SKY + ", " + VEHICLE_NEG_SKY),
        "require_pos": ("no humans", "sky", "blue sky"),
        "forbid_pos": ("scenery", "grass", "ground", "field"),
        "require_neg": ("cityscape", "city", "building", "skyline", "road",
                        "mountain", "grass", "field", "horizon", "ground",
                        "leaf", "plant", "stem", "foliage", "tree",
                        "animal", "bird", "aircraft"),
        "forbid_neg": (),
        "why": ("HIS OPTION B, WORD FOR WORD: \"dont show the ground at all and "
                "show the sky\". The positive is r5's with `scenery` deleted and "
                "nothing put in its place — `sky, blue sky, day, cloud, "
                "sunlight` is already the whole subject. The ground leaves "
                "through the negative rather than through silence, which is what "
                "r5 tried: r5 named no ground noun either way and got four wide "
                "landscapes with a horizon, because `scenery` supplied one. "
                "`grass, field, horizon, ground, mountain` are negated here and "
                "`grass` is negated in exactly the arm that is not about grass. "
                "NEW IN r7: the animal and vehicle classes are named here too, "
                "with the terms a sky can actually hold — `animal, bird` and "
                "`aircraft`. r6's arm B drew no creature in any of its four and "
                "the reason is structural rather than lucky: a frame with "
                "nothing but sky has nowhere to put a cat. Naming the class arm "
                "A's way costs four terms and measured out `jpeg artifacts`, "
                "which matters more on a smooth blue gradient than anywhere "
                "else in the episode. This is a measured budget call, not a "
                "claim that the class does not apply."),
    },
}


def sidecar(png: Path, *, arm: dict, arm_key: str, seed: int, pos: str, neg: str,
            neg_full: str, secs: float, warns: list, shots_sha: str,
            pos_tokens: int, neg_tokens: int, r5_neg_tokens: int,
            out_dir: Path, task: str, queue_entry: str) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b06r7.py",
             f"# on the rtx5090 ({out_dir}).",
             "# The prompt and negative below are what the model actually saw.",
             "# sd_prompt's own output, BEFORE this round's named transforms, was:",
             f"#   POS: {R5_POS_SENT}",
             f"#   NEG: {neg_full}",
             "# The transforms, all three of them named: `no humans` restored to",
             "# the HEAD of the positive and `humans` deleted from the negative",
             "# (r5's deviation, unchanged); `scenery` removed from the positive;",
             "# this arm's own substitution and negative block. sd_prompt.py is",
             "# NOT modified by this round and shots.md is NOT edited."]
    lines += [f"#   NEGWARN: {w}" for w in warns]
    body = ["platform: local-gpu (rtx5090)",
            f"model: {BASE}",
            f"model_licence: {LICENCE}",
            f"shot_beat: {BEAT}",
            f"size: {W}x{H}",
            f"steps: {STEPS}",
            f"guidance: {CFG}",
            f"seed: {seed}",
            "seeds_in_batch: 4",
            f"task: {task}",
            f"queue_entry: {queue_entry}",
            "render_round: r7",
            f"candidate_set: {arm['set']}",
            f"arm: {arm_key}",
            f"arm_label: {arm['label']}",
            "arm_is_not_a_pick: >-",
            block("Round 7 keeps the TWO arms because the founder gave two acceptable "
                  "compositions and chose neither. A and B are alternatives, not "
                  "a sweep with a winner. No arm is preferred, ranked or "
                  "recommended anywhere in this round, and the steward makes no "
                  "pick between them — that choice is R4's and only his."),
            "founder_direction_verbatim: >-",
            block("none of the beat 6 images will work, you either show the "
                  "ground as having tall grass or dont show the ground at all "
                  "and show the sky, right now its showing the ground as some "
                  "flat place, or showing cities for some reason"),
            "founder_direction_date: 2026-08-10",
            "why_this_arm: >-",
            block(arm["why"]),
            "cities_diagnosis: >-",
            block("NOT a trimmed term — a term that was never written. Every "
                  "negative this beat has sent was read back from its own "
                  "sidecars (r3, r4, r5 and the fix set) and not one contains "
                  "city, cityscape, building, skyline, skyscraper, industrial, "
                  "town or architecture. r5's negative measured 51 of 77 on the "
                  "box's real CLIP, so nothing was trimmed and there were 26 "
                  "tokens spare. The positive side is the other half: r5 "
                  "introduced the Danbooru tag `scenery`, the umbrella whose "
                  "children include `cityscape` (62,273 posts against 19,945, "
                  "qdlabs/danbooru-tags mirror read 2026-08-10; donmai.us itself "
                  "timed out and is not cited). r5 is the first round on this "
                  "beat to carry `scenery` and the round that drew a city "
                  "through s0's ring and a skyline on s1's bottom edge. Both "
                  "arms delete the tag AND negate the block."),
            f"positive_tag_removed: {CITY_TAG_IN_POSITIVE}",
            f"explicit_negatives_added: {arm['extra_neg']}",
            "explicit_negatives_tier: explicit (last in fit_negative's drop order)",
            f"occupancy_classes_named: {', '.join(sorted(OCCUPANCY_CLASSES))} "
            f"(negative), people (positive, `{HEAD_TAG}`)",
            "occupancy_preflight: >-",
            block("Trap 9, new in round 7 and asserted before a weight loads. "
                  "For a beat whose script says the frame is empty, every class "
                  "of thing that can occupy it must be NAMED in the SENT "
                  "negative — animals, built structure, vehicles, text — with "
                  "people named on the POSITIVE side by `no humans`, because "
                  "person nouns are barred from the negative on this beat "
                  "(traps 7 and 8). A class not named is a predicted defect "
                  "rather than a surprise: r5 shipped a city that way and r6 "
                  "shipped a large white animal that way, both found only after "
                  "somebody looked at the frames, neither one a token trim."),
            "token_ceiling_note: >-",
            block("77 per CLIP encoder, hard. diffusers truncates; the chunked "
                  "negatives A1111 and ComfyUI users expect need compel with "
                  "truncate_long_prompts=False and hand-passed prompt_embeds "
                  "(compel #45, diffusers #4043, A1111 discussion #2378, read "
                  "2026-08-10). That is a recipe change owing its own one "
                  "sample and is NOT done here — the class block is sized to "
                  "what fits and measured on the box's real CLIP first."),
            f"negative_terms_removed: {', '.join(arm['drop_neg']) or 'none'}",
            "negative_removal_reason: >-",
            block("Arm A only: grass is a plant, so `plant` and `foliage` in the "
                  "negative would cancel the arm the founder asked for. `leaf`, "
                  "`stem` and `tree` are kept in both arms — those are his "
                  "2026-08-07 rule about the character's own body, not about the "
                  "ground." if arm["drop_neg"] else
                  "None. Arm B has no ground, so the full plant block stands."),
            "mechanism_held_from_r5: >-",
            block("`no humans` at the HEAD of the POSITIVE and NOT ONE person "
                  "noun in the negative. That took this beat from a girl in 2 of "
                  "4 (r3) and 3 of 4 (r4) to zero in 4 of 4 (r5), and his "
                  "2026-08-10 verdict does not mention people. It is held fixed "
                  "while the composition moves, and traps 7 and 8 refuse the run "
                  "if either half of it slips."),
            "person_terms_in_negative: none — asserted at run time (trap 8)",
            f"shots_md_sha256: {shots_sha}",
            "shots_md_edited: false",
            "authored_source: >-",
            block("genomes/sapling/nodes/001-capability-inventory/shots.md beat "
                  "06, byte-for-byte and asserted before a weight loads. Every "
                  "change this round makes is applied script-side, printed, and "
                  "listed above."),
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            f"positive_tokens_real_clip: {pos_tokens}",
            f"negative_tokens_real_clip: {neg_tokens}",
            f"negative_tokens_r5_control: {r5_neg_tokens}",
            "r5_control_reproduced: true",
            "controls_note: >-",
            block("r5 is rebuilt from this checkout in the same run on the same "
                  "tokenizer and asserted byte-for-byte against its recorded "
                  "sidecars, positive AND negative, so the delta is one "
                  "measurement rather than two instruments."),
            "anchor_intact: true",
            "seeds_held_from: >-",
            block("round 5, takes/stills/06-too-blue-r5-s*.png — this beat's own "
                  "k=4..7, which r3 and r4 also drew. Both arms run the same "
                  "four, so A against B is a comparison of the prompt and not of "
                  "the noise, and either arm can still be set beside the "
                  "rejected rounds column for column."),
            "provisional: >-",
            block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and not "
                  "canon. Ground truth is the founder (R4); he has ratified "
                  "nothing here and this round deliberately offers him no "
                  "preference between its two arms. Never takes a canon "
                  "filename, is not published, not posted, and not assembled "
                  "into an episode."),
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 5, takes/stills/06-too-blue-r5-s*.png — model, size, "
                  "steps, cfg and the seed series are unchanged from r5, which "
                  "inherited them from node 001 "
                  "takes/stills/15-something-s-coming-r3-s1.png, the ONE SAMPLE "
                  "the founder passed on 2026-08-08."),
            f"wall_seconds: {secs:.0f}",
            "cost_usd: 0",
            "note: |-", block(NOTE_TEMPLATE.format(
                arm=arm_key, label=arm["label"], why=arm["why"])),
            "prompt: |-", block(pos),
            "negative: |-", block(neg)]
    png.with_suffix(".png.meta.yaml").write_text("\n".join(lines + body) + "\n",
                                                 encoding="utf-8")


NOTE_TEMPLATE = (
    "round 7, ARM {arm} — {label}. The founder's two acceptable compositions "
    "from 2026-08-10, verbatim: \"you either show the ground as having tall "
    "grass or dont show the ground at all and show the sky, right now its "
    "showing the ground as some flat place, or showing cities for some "
    "reason\". Two readings, two arms, one candidate set each, and the steward "
    "picks between them nowhere — he has chosen neither and both are alive. "
    "{why} WHAT ROUND 6 SETTLED AND IS NOT REOPENED HERE: the cities are gone 8 "
    "of 8 and people are gone 8 of 8, arm A drew tall grass with blades at the "
    "camera 4 of 4 and arm B drew sky with no ground 4 of 4. WHAT ROUND 7 "
    "CHANGES, AND IT IS ONE THING: a large white animal was the subject of r6 "
    "arm A's s1 and s3, and r6's sent negative names no animal, cat, dog, wolf "
    "or creature anywhere — an animal was never forbidden on this beat, exactly "
    "as a city never was, and at 59 of 77 tokens neither was a trim. `no "
    "humans` is why: on this vocabulary it asserts no HUMAN character, not an "
    "empty frame, which is why `animal focus` exists as a separate tag on "
    "pictures that carry both. The tag stays — it is r5's one confirmed win — "
    "and the class is shut on the negative side, where no person noun is "
    "involved. THE FIX IS A PRE-FLIGHT, NOT A TERM (trap 9): every class that "
    "can occupy a frame the script says is empty — people, animals, built "
    "structure, vehicles, text — must be named in what the model actually "
    "receives, and the run stops if one is not. Three rounds running the defect "
    "was a noun nobody had negated, found only after somebody looked. The 77 "
    "token ceiling is diffusers truncating each CLIP encoder; chunked negatives "
    "would need compel and are a recipe change with its own sample, so the "
    "class block is sized to what fits and measured before the render. Seeds "
    "are r5's own four, held again, so r7 sets beside r6 column for column. "
    "shots.md NOT edited; sd_prompt.py NOT modified. Nothing here is a pick, a "
    "promotion, a publication or a spend.")


def strip_terms(neg: str, terms) -> tuple:
    parts = [p.strip() for p in neg.split(",")]
    low = {t.lower() for t in terms}
    kept = [p for p in parts if p.lower() not in low]
    return ", ".join(kept), len(parts) - len(kept)


def build(authored: str, compress, beat_negative, arm: dict) -> tuple:
    """The full prompt pair for one arm, through the real code path."""
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, arm["extra_neg"], warn=warns.append)

    # r5's deviation, unchanged: `humans` out of the negative, `no humans` back
    # at the head of the positive as the Danbooru tag it is.
    neg, _ = strip_terms(neg_full, (LIFTED_NEG,))
    neg, dropped_terms = strip_terms(neg, arm["drop_neg"])

    pos = pos.lstrip(" ,")
    old, new = arm["pos_sub"]
    if new is None:
        pos = pos.replace(old + ", ", "", 1).replace(", " + old, "", 1)
    else:
        pos = pos.replace(old, new, 1)
    pos = f"{HEAD_TAG}, {pos}"
    return pos, neg, neg_full, dropped, warns, dropped_terms


def build_r5_control(authored: str, compress, beat_negative) -> tuple:
    """Rebuild exactly what r5 sent, from this checkout."""
    pos, _ = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, "", warn=warns.append)
    neg, _ = strip_terms(neg_full, (LIFTED_NEG,))
    pos = f"{HEAD_TAG}, {pos.lstrip(' ,')}"
    return pos, neg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print the r5 control beside this arm on the box's "
                         "real tokenizer, draw nothing")
    ap.add_argument("--task", default=None)
    ap.add_argument("--queue-entry", default="none")
    a = ap.parse_args()

    arm_key = a.arm
    arm = ARMS[arm_key]
    task = a.task or f"001-b06-r7{arm_key.lower()}-{int(time.time())}"

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes" / NODE
    shots_path = node / "shots.md"
    out = Path(a.out).resolve() if a.out else Path(__file__).resolve().parent / "out"
    out.mkdir(parents=True, exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    authored = s["prompt"]

    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts near "
              "the 77 boundary. Run this on the box's venv; stopping.",
              flush=True)
        return 8

    # trap 1: the fence must still be the one r5 rendered, byte for byte. This
    # round does not edit shots.md; a stale checkout would send a different
    # prompt under this round's name.
    if authored != AUTHORED:
        print("!! shots.md Beat 06 is not the fence r5 rendered, byte for byte "
              "— the checkout is stale or the fence moved.\n"
              f"   expected: {AUTHORED}\n"
              f"   found:    {authored}\n   stopping.", flush=True)
        return 4

    pos, neg, neg_full, dropped, warns, dropped_terms = build(
        AUTHORED, compress, beat_negative, arm)
    cpos, cneg = build_r5_control(AUTHORED, compress, beat_negative)

    print(f"\n== node {NODE} beat {BEAT} {s['slug']} ARM {arm_key} "
          f"[{arm['set']}] — {arm['label']}", flush=True)
    print(f"   seeds:    {', '.join(str(x) for x in SEEDS)}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}  (NOT edited by this round)", flush=True)
    print(f"   AUTHORED (fence, shared with r5): {AUTHORED}", flush=True)
    print(f"   POS(sent):        {pos}", flush=True)
    print(f"   POS(r5 control):  {cpos}", flush=True)
    print(f"   NEG(recipe):      {neg_full}", flush=True)
    print(f"   NEG(sent):        {neg}", flush=True)
    print(f"   NEG(r5 control):  {cneg}", flush=True)

    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    cneg_tokens = negative_tokens(cneg)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: r5 control {cneg_tokens} -> recipe "
          f"{negative_tokens(neg_full)} -> sent {neg_tokens} (budget 77)",
          flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # trap 2: the r5 control must reproduce from THIS checkout, both halves.
    # Without it the comparison to the rejected round is two instruments.
    if cpos != R5_POS_SENT:
        print("!! the r5 POSITIVE does not reproduce from this checkout.\n"
              f"   recorded: {R5_POS_SENT}\n"
              f"   rebuilt:  {cpos}\n   stopping.", flush=True)
        return 5
    if cneg != R5_NEG_SENT:
        print("!! the r5 NEGATIVE does not reproduce from this checkout.\n"
              f"   recorded: {R5_NEG_SENT}\n"
              f"   rebuilt:  {cneg}\n   stopping.", flush=True)
        return 6
    print("   trap 2 OK — r5 control reproduces byte-for-byte, both halves",
          flush=True)

    # trap 3: no positive drop. compress() sheds trailing sentences and the
    # style sentence is last, so a drop here would cost the anchor.
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3

    # trap 4: the anchor. Losing it changes the look and confounds the
    # composition change with a style change.
    if not pos.rstrip().endswith("very aesthetic"):
        print(f"   !! ANCHOR GONE — the sent positive does not end `very "
              f"aesthetic`: …{pos[-60:]!r}; stopping.", flush=True)
        return 7

    # trap 5: every term this arm buys must survive the 77-token trim. The
    # urban block IS the round; a silent trim would test terms the model never
    # received and the sheet would say nothing about the cities.
    sent_neg = {p.strip().lower() for p in neg.split(",")}
    missing = [t for t in arm["require_neg"] if t.lower() not in sent_neg]
    if missing:
        print(f"   !! TRIMMED AWAY: {', '.join(missing)} — these are the round. "
              f"fit_negative shed them to fit 77 tokens, so the sheet would "
              f"test terms the model never saw. Sell something from the house "
              f"tier and re-measure; stopping.", flush=True)
        return 9
    over = [t for t in arm["forbid_neg"] if t.lower() in sent_neg]
    if over:
        print(f"   !! STILL NEGATED: {', '.join(over)} — this arm asks for "
              f"grass and cannot also forbid it; stopping.", flush=True)
        return 11
    print(f"   trap 5 OK — all {len(arm['require_neg'])} required negatives "
          f"survived the trim", flush=True)

    # trap 6: the arm's own positive. Arm A must actually ask for tall grass and
    # arm B must name no ground at all, and neither may still carry `scenery`.
    low_pos = pos.lower()
    miss_pos = [t for t in arm["require_pos"] if t.lower() not in low_pos]
    if miss_pos:
        print(f"   !! POSITIVE IS MISSING {', '.join(miss_pos)} — this arm is "
              f"defined by them; stopping.", flush=True)
        return 13
    bad_pos = [t for t in arm["forbid_pos"] if t.lower() in low_pos]
    if bad_pos:
        print(f"   !! POSITIVE STILL CARRIES {', '.join(bad_pos)} — "
              f"`{CITY_TAG_IN_POSITIVE}` is the tag that imports the skyline "
              f"and a ground noun is what arm B exists without; stopping.",
              flush=True)
        return 14
    print(f"   trap 6 OK — arm {arm_key} positive asks for "
          f"{', '.join(arm['require_pos'])} and carries none of "
          f"{', '.join(arm['forbid_pos'])}", flush=True)

    # trap 7: r5's mechanism, half one. `no humans` at the HEAD of the positive.
    if not pos.startswith(HEAD_TAG + ","):
        print(f"   !! `{HEAD_TAG}` IS NOT AT THE HEAD of the sent positive. "
              f"That placement is r5's one confirmed win on this beat and this "
              f"round is not reopening it; stopping.", flush=True)
        return 15

    # trap 8: r5's mechanism, half two. No person noun anywhere in the negative.
    back = [t for t in PERSON_NOUNS if t in sent_neg]
    if back:
        print(f"   !! PERSON NOUNS BACK IN THE NEGATIVE: {', '.join(back)}. "
              f"They failed on this beat twice (r3 2 of 4, r4 3 of 4) and r5 "
              f"drew nobody without them; stopping.", flush=True)
        return 16
    print("   trap 7+8 OK — `no humans` leads the positive, no person noun in "
          "the negative", flush=True)

    # trap 9: THE OCCUPANCY PRE-FLIGHT. Three rounds running, the defect was a
    # noun nobody had ever negated — r5 a city, r6 an animal — and both were
    # found only after somebody looked at the frames. This is that discovery
    # moved before the render. Every class of thing that can occupy a frame the
    # script says is empty must be NAMED in what the model actually receives.
    unnamed = [cls for cls, terms in OCCUPANCY_CLASSES.items()
               if not any(t.lower() in sent_neg for t in terms)]
    if unnamed:
        print(f"   !! OCCUPANCY CLASS NOT NAMED: {', '.join(unnamed)}. This "
              f"beat's script says the frame is empty, and a class the sent "
              f"negative never names is a PREDICTED defect, not a surprise — "
              f"r5 shipped a city that way and r6 shipped an animal. Name it "
              f"or sell something to fit it; stopping.", flush=True)
        return 17
    for cls, tag in OCCUPANCY_POSITIVE_SIDE.items():
        if tag.lower() not in pos.lower():
            print(f"   !! OCCUPANCY CLASS `{cls}` IS NAMED ON THE POSITIVE "
                  f"SIDE BY `{tag}` AND IT IS GONE. Person nouns are barred "
                  f"from the negative here (trap 8), so this tag is the only "
                  f"thing holding that class out; stopping.", flush=True)
            return 18
    print(f"   trap 9 OK — occupancy classes all named: "
          f"{', '.join(sorted(OCCUPANCY_CLASSES))} in the negative, "
          f"{', '.join(sorted(OCCUPANCY_POSITIVE_SIDE))} by "
          f"`{HEAD_TAG}` in the positive", flush=True)

    if arm["drop_neg"] and dropped_terms != len(arm["drop_neg"]):
        print(f"   !! EXPECTED to remove {len(arm['drop_neg'])} x "
              f"{arm['drop_neg']}, removed {dropped_terms} — stopping so a "
              f"human decides.", flush=True)
        return 2

    if a.measure:
        print("\nMEASURE OK — nothing drawn", flush=True)
        return 0
    if a.dry:
        print(f"\nDRY OK — 1 beat x 4 seeds = 4 frames for arm {arm_key}, "
              f"nothing drawn", flush=True)
        return 0

    import torch
    from diffusers import StableDiffusionXLPipeline
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(BASE, torch_dtype=torch.bfloat16,
                                                     use_safetensors=True)
    pipe.to("cuda")
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s", flush=True)

    for i, seed in enumerate(SEEDS):
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=STEPS,
                   guidance_scale=CFG, generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT:02d}-{s['slug']}-{arm['set']}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, arm=arm, arm_key=arm_key, seed=seed, pos=pos, neg=neg,
                neg_full=neg_full, secs=secs, warns=warns, shots_sha=shots_sha,
                pos_tokens=pos_tokens, neg_tokens=neg_tokens,
                r5_neg_tokens=cneg_tokens, out_dir=out, task=task,
                queue_entry=a.queue_entry)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print(f"\nDONE 4 stills, arm {arm_key}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
