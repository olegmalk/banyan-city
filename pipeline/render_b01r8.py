#!/usr/bin/env python3
"""002b beat 01 — ROUND 8, the ARCHITECTURE round: the height leaves the prompt.

WHY THIS ROUND IS NOT ANOTHER WORDING ROUND. Seven rounds have argued with this
beat in words and the record closed the argument twice in its own voice.
shots.md, 2026-08-06: *"The levers that are left are all outside the prompt —
img2img over a chosen plate, a pose controlnet, or a different checkpoint."*
Taste ledger record 28 (r6) and then record 41 (r7, f48b096) both end on the
same sentence: the remaining levers are outside the prompt. r7 is the proof
rather than the opinion — `no taller than the grass around it` was read by the
model as *taller than the grass around it*, because CLIP does not encode
negation and the clause is 31 characters where `sd_prompt._NEGATION` lifts at
most 25. The one seed that had been inside his ceiling at ~20% went to 39%. A
measure expressed in words cannot bind this drawing.

SO THE MEASURE STOPS BEING A WORD AND BECOMES A PICTURE. img2img starts the
denoise from an existing frame, so the composition — where the ground is, how
big the plant is against it — arrives as pixels instead of as an instruction the
text encoder has to be persuaded to honour. The init is the ONE frame of a
sapling in grass the founder has ever passed:
`genomes/sapling/nodes/001-capability-inventory/stills/15-something-s-coming.png`
(b15-r3-s1, canon since d4488de, sha256 f60c1404…). Its scale is his, not mine,
which is the entire reason to start there rather than from a beat-01 candidate
he rejected — scoring a height round against a frame I chose would be the
"a metric agreeing with me is not a sample" error the house rules name.

THE SINGLE VARIABLE, STATED HONESTLY AS ONE MOVE SEEN FROM BOTH ENDS. The height
instruction moves out of the text and into the init. That is why this script
DELETES `no taller than the grass around it` from the fence rather than
replacing it: leaving it in would point the text at the opposite of what the
init is for, and swapping it for new words would make this a wording round
again. `its sturdy curved stem no taller than the grass around it,` becomes
`its sturdy curved stem,` — the stem keeps its noun and its two adjectives, and
loses only the height predicate. Nothing else in the fence moves, and the SENT
NEGATIVE must come out byte-identical to the string r6 and r7 were drawn with
or this script refuses to spend a step.

SHOTS.MD IS NOT EDITED. The deletion happens script-side, after asserting that
the fence on disk is byte-for-byte r7's. A stale checkout therefore cannot start
at all, and the founder's approved shot list keeps ONE authored version of this
beat instead of eight. (This is r9-tusks' convention on beat 13, adopted here
for the same reason: r8 on that beat rewrote the fence, which is how a stale
checkout renders the wrong round under the right id.)

THREE ARMS, ONE AXIS, THE SAME FOUR SEEDS — because a single strength would
answer nothing it could not have guessed. The precedent for strength on THIS
beat is real but it is all same-palette: the 2026-08-06 repaints over
`01-cold-open-r3-s3.png` at 0.35 returned the plate refined and its layout
untouched, and the surviving 0.55 take kept the layout while visibly
re-drawing the subject. None of that measures what happens when the init's
PALETTE disagrees with the prompt, which is this round's real risk — b15 is a
dark amber macro under a shaft of light and beat 01 asks for a peach-and-gold
sunrise wide shot. So the round brackets the whole measured range and puts the
uninitialised render at the end of it as the control:

    i35   img2img from the plate, strength 0.35   most of his frame kept
    i55   img2img from the plate, strength 0.55   top of the measured range
    t2i   no init at all                          the r7 architecture, controlled

t2i is what makes this a controlled round rather than a demonstration: it is
r7's own pipeline on r7's own seeds with only the height clause removed, so the
difference between it and the i-arms is the init image and nothing else. All
three arms share one loaded set of weights (the img2img pipeline is built from
the text2img pipeline's own components), one dtype, one device, one tokenizer.

THE PLATFORM IS THE BOX, AND THAT IS A MEASUREMENT NOT A PREFERENCE. This round
was briefed as Mac-side on the grounds that img2img is MPS-only because
`still_local.py` is. `still_local.py` is; the capability is not. On the 5090's
venv, `StableDiffusionXLImg2ImgPipeline` imports and its `__call__` carries both
`image` and `strength` (diffusers 0.29.2, torch 2.11.0+cu128) — checked before
this file was written. Three reasons to use it. (1) r5, r6 and r7 all rendered
here in bf16 on CUDA; an fp32 MPS control arm would not be comparable to the r7
numbers it exists to control against, and a round that changes platform AND
architecture at once answers neither. (2) The token budget can only be measured
here — `sd_prompt._token_estimate` over-counts a positive of this shape by ~3
near the 77 boundary, and this script refuses to run without a real CLIP
tokenizer, exactly as r7's did. (3) ~10s a frame against ~2-3min, and the Mac is
the founder's machine — the two-subject memo §4 names rendering here as the
hazard `--no-open` was filed against, and notes that r6 "dodged it by running on
the 5090".

    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r8.py --root ... --measure
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r8.py --root ... --dry
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r8.py --root ...

PRE-REGISTERED RUBRIC, fixed before any pixel exists so it cannot move
afterwards. The number is the STEM HEIGHT FRACTION — apex to groundline over
frame height — per frame, against the 32% hairline he revoked ("its tooooo
tall") and the ~20% of r6-s3, the first frame in six rounds inside that ceiling.
The round SUCCEEDS on that axis if the i-arms sit inside the ceiling where the
t2i control does not; it FAILS if the init makes no difference, and that failure
is worth as much as the success because it retires img2img and leaves controlnet
and the checkpoint swap as the named next levers. Person-binding is reported at
n of 4 per arm — r7 regressed to 1 of 4 with a byte-identical negative, so it is
observed, not assumed. THE FIG IS OBSERVED AND NOT GATED, and the record is
already explicit about why arguing with it is wasted: size adjectives do not
shrink this fruit — the 2026-08-06 repaints asked for a "nub" and a "pea-sized"
fruit and both came back LARGER and rounder than the plate — so the fruit is
whatever it is and the note says "choose the frame instead". The init carries no
fruit at all, so whether one appears is a genuine observation about img2img and
not a prompt result.

NOTHING HERE IS A PICK. Twelve provisional candidates, a ledger record written
before the sheet, a sheet carrying addresses and seeds only with no favourite
and no ordering, and nothing opened on his screen.
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
SEED = 20260719
W, H, STEPS, CFG = 832, 1216, 40, 7.5
DROP_NEG = "tall tree"
CANDIDATE_SET = "r8"
QUEUE_ENTRY = "ep2-b01-r7-coldopen-1786292601"   # the beat's open entry; r8 is its next round
TASK = "ep2-b01-r8-i2i-1786307779"
BEAT = 1
EXPECT_DROP = 1          # `tiny`, `40cm`, `seedling` all fire _SMALL
EXTRA_NEG = ""           # r6 and r7 carried none on this beat and r8 adds none

# The init: b15-r3-s1, the one sapling-in-grass frame the founder has passed.
# Its sha256 is asserted, because "img2img from the approved plate" is the whole
# claim of this round and a different file would silently make it a different
# claim.
INIT_REL = "genomes/sapling/nodes/001-capability-inventory/stills/15-something-s-coming.png"
INIT_SHA = "f60c1404f88d45720ca295dfc753e9eaabb815446710bcfffb3c7a07b7277f54"

# arm id -> strength. None = no init (the control).
ARMS = (("i35", 0.35), ("i55", 0.55), ("t2i", None))

# THE ONE EDIT, made script-side so shots.md keeps one authored fence.
STRIP_CLAUSE = " no taller than the grass around it"
EXPECT_PREFIX = "a tiny 40cm seedling standing in short grass"
FORBID_CLAUSE = "rising well above the grass"          # r6's; a stale checkout
AFTER_STRIP = "its sturdy curved stem, two oversized cotyledon leaves"

# The style anchor. compress() sheds the trailing sentence first, and r8 is
# SHORTER than r7, so this should hold with room — asserted anyway, because that
# is the r4 defect this genome has paid for twice.
ANCHOR = ("cinematic lighting, detailed, newest, masterpiece, best quality, "
          "very aesthetic")

# r7's authored fence exactly as shots.md must still carry it. Asserted before
# the strip runs: if this does not match, the checkout is stale or someone has
# edited the beat, and either way r8 must not render under r8's name.
R7_AUTHORED = (
    "A tiny 40cm seedling standing in short grass, its sturdy curved stem no "
    "taller than the grass around it, two oversized cotyledon leaves, one small "
    "round green fruit hanging from the stem, whole plant in frame, wide shot, "
    "peach and gold sunrise sky, no girl, no boy, no child, no person, no "
    "chibi, no mascot, no creature, no face, no branches, no night sky, "
    "cinematic lighting, detailed, newest, masterpiece, best quality, very "
    "aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.")

# The negative the r6 AND r7 frames were drawn with, read off their sidecars.
# r8 must send this string unchanged: removing a positive clause that was never
# lifted must not move the negative by one byte, and if it does, the round has
# quietly become a two-variable round.
R7_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, "
    "low quality, blurry, extra limbs, deformed, mature tree, large tree, "
    "thick trunk, full canopy, forest, bush, shrubbery, girl, boy, child, "
    "person, chibi, mascot, creature, face, branches, night sky, photorealism")

PERSON_NEG = ("girl", "boy", "child", "person")

NOTE = (
    'round 8, the ARCHITECTURE round: the height instruction leaves the prompt '
    'and becomes the init image. Seven rounds of wording are spent and the '
    'record closed the argument twice in its own voice — shots.md 2026-08-06 '
    '("the levers that are left are all outside the prompt — img2img over a '
    'chosen plate, a pose controlnet, or a different checkpoint") and ledger '
    'records 28 and 41. r7 is the proof rather than the opinion: `no taller '
    'than the grass around it` was read as its own opposite, because CLIP does '
    'not encode negation and the clause is 31 characters where _NEGATION lifts '
    'at most 25, and the one seed that had been inside his ceiling at ~20% went '
    'to 39%. THE SINGLE VARIABLE is one move seen from both ends: the height '
    'predicate is DELETED from the fence (`its sturdy curved stem no taller '
    'than the grass around it,` -> `its sturdy curved stem,`, keeping the noun '
    'and both adjectives) and the composition arrives instead as pixels from '
    'the init. Replacing the clause with different words would have made this '
    'an eighth wording round; leaving it in would have pointed the text at the '
    'opposite of what the init is for. THE INIT IS HIS, NOT MINE: b15-r3-s1, '
    'the ONE sapling-in-grass frame the founder has ever passed (canon since '
    'd4488de), asserted by sha256 at render time — starting from a beat-01 '
    'frame I liked would have scored a height round against my own taste. '
    'SHOTS.MD WAS NOT EDITED; the strip happens script-side after asserting the '
    'fence on disk is byte-for-byte r7\'s, so a stale checkout cannot start. '
    'THREE ARMS ON THE SAME FOUR SEEDS, one axis: i35 (strength 0.35, most of '
    'his frame kept), i55 (0.55, the top of the range the 2026-08-06 repaints '
    'actually measured), and t2i (no init) as the CONTROL — r7\'s own pipeline '
    'on r7\'s own seeds with only the clause removed, so the difference between '
    'the arms is the init image and nothing else. All three share one set of '
    'loaded weights, one dtype, one device and one tokenizer. Why a bracket '
    'rather than one strength: the 0.35/0.55 precedent is all SAME-palette, and '
    'this init disagrees with the prompt — b15 is a dark amber macro under a '
    'shaft of light where beat 01 asks for a peach-and-gold sunrise wide shot, '
    'which is this round\'s real risk and is measured rather than assumed. THE '
    'SENT NEGATIVE IS BYTE-IDENTICAL to the string r6 and r7 were drawn with, '
    'as a precondition the script refuses to skip. THE PLATFORM IS THE BOX AND '
    'THAT IS A MEASUREMENT: img2img was briefed as MPS-only because '
    'still_local.py is, but StableDiffusionXLImg2ImgPipeline imports on the '
    '5090 venv with `image` and `strength` on its __call__ (diffusers 0.29.2, '
    'torch 2.11.0+cu128), and r5/r6/r7 all rendered here in bf16 — an fp32 MPS '
    'control arm would not be comparable to the numbers it controls against. '
    'PRE-REGISTERED RUBRIC: the number is the stem height fraction, apex to '
    'groundline over frame height, per frame, against the 32% hairline he '
    'revoked and the ~20% of r6-s3; the round SUCCEEDS if the i-arms sit inside '
    'the ceiling where the t2i control does not and FAILS if the init makes no '
    'difference — and that failure is worth as much, because it retires img2img '
    'and leaves controlnet and the checkpoint swap as the named next levers. '
    'Person-binding reported n of 4 per arm, observed not assumed, because r7 '
    'regressed to 1 of 4 on a byte-identical negative. THE FIG IS OBSERVED AND '
    'NOT GATED: the record already settled that size adjectives do not shrink '
    'it — the 2026-08-06 repaints asked for a `nub` and a `pea-sized` fruit and '
    'both came back LARGER and rounder than the plate, so the note is "choose '
    'the frame instead" — and the init carries no fruit at all, so whether one '
    'appears is an observation about img2img rather than a prompt result. '
    'PROVISIONAL: steward-rendered candidates, not picks and not canon. Ledger '
    'record written BEFORE the sheet, the sheet carries labels and seeds only '
    'with no favourite and no ordering (R4), and nothing is opened on the '
    'founder\'s screen.')


def strip_height_clause(authored: str) -> str:
    """Delete the height predicate, keep the stem. Exactly one occurrence."""
    if authored.count(STRIP_CLAUSE) != 1:
        raise ValueError(
            f"expected exactly 1 occurrence of {STRIP_CLAUSE!r}, "
            f"found {authored.count(STRIP_CLAUSE)}")
    return authored.replace(STRIP_CLAUSE, "", 1)


def sidecar(png: Path, *, seed: int, arm: str, strength, pos: str, neg: str,
            neg_full: str, secs: float, warns: list, task: str, shots_sha: str,
            pos_tokens: int, neg_tokens: int) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b01r8.py",
             "# on the rtx5090 (C:\\banyan-farm\\sample-b01-r8).",
             "# The negative below is what the model actually saw. The recipe's own",
             "# negative, before this script's one deliberate removal, was:",
             f"#   {neg_full}"]
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
            f"arm: {arm}",
            f"pipeline: {'img2img' if strength is not None else 'text2img'}",
            f"init_image: {INIT_REL if strength is not None else 'none'}",
            f"init_sha256: {INIT_SHA if strength is not None else 'none'}",
            f"strength: {strength if strength is not None else 'n/a'}",
            f"task: {task}",
            f"queue_entry: {QUEUE_ENTRY}",
            f"render_round: {CANDIDATE_SET}",
            f"candidate_set: {CANDIDATE_SET}-{arm}",
            f"negative_terms_removed: {DROP_NEG}",
            f"prompt_source_sha256: {shots_sha}",
            f"positive_clip_tokens: {pos_tokens}",
            f"negative_clip_tokens: {neg_tokens}",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            "negative_identical_to_r7: true",
            "shots_md_edited: false",
            "single_variable: >-",
            block("The height instruction moves out of the text and into the "
                  "init image: `its sturdy curved stem no taller than the grass "
                  "around it,` -> `its sturdy curved stem,`, and the "
                  "composition arrives as pixels from b15-r3-s1 instead. One "
                  "move seen from both ends. The SENT negative is "
                  "byte-identical to r6's and r7's, and the t2i arm holds the "
                  "same prompt with no init so the arms differ by the init "
                  "alone."),
            "provisional: >-",
            block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and not "
                  "canon. Scored against taste/steward-model.v1 and logged in "
                  "taste/steward-model.ledger.yaml BEFORE the founder saw it. "
                  "Ground truth is the founder (R4); he has ratified nothing "
                  "here. Never takes a canon filename, is not published, not "
                  "posted, and not assembled into an episode."),
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 7, takes/stills/01-cold-open-r7-s*.png — model, size, "
                  "steps, cfg, seed rule, the one-term negative removal and "
                  "every clause of the positive except the deleted height "
                  "predicate are r7's unchanged. The init image is node 001's "
                  "stills/15-something-s-coming.png (b15-r3-s1), the ONE "
                  "sapling-in-grass frame the founder has passed."),
            f"wall_seconds: {secs:.0f}",
            "cost_usd: 0",
            "note: |-", block(NOTE),
            "prompt: |-", block(pos),
            "negative: |-", block(neg)]
    png.with_suffix(".png.meta.yaml").write_text("\n".join(lines + body) + "\n",
                                                 encoding="utf-8")


def strip_term(neg: str, term: str) -> tuple:
    parts = [p.strip() for p in neg.split(",")]
    kept = [p for p in parts if p.lower() != term.lower()]
    return ", ".join(kept), len(parts) - len(kept)


def build(authored, compress, beat_negative):
    """(positive, sent negative, recipe negative, dropped sentences, warnings)."""
    warns = []
    pos, dropped = compress(authored)
    neg_full = beat_negative(NEG, authored, EXTRA_NEG, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)
    return pos, neg, neg_full, dropped, warns, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--shots", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print the r7 control beside r8 on this box's "
                         "tokenizer, draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = Path(a.shots).resolve() if a.shots else node / "shots.md"
    init_path = root / INIT_REL
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    authored_r7 = s["prompt"]

    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts this "
              "prompt by ~3 near the 77 boundary. Run this on the box's venv; "
              "stopping.", flush=True)
        return 8

    # trap 1: the fence on disk must be r7's, exactly. Stale checkout, or a beat
    # someone else has edited, and r8 is not the round that would be rendered.
    if authored_r7 != R7_AUTHORED:
        print("   !! shots.md's beat 01 fence is NOT r7's. This round strips one "
              "clause out of that exact string; against any other text the "
              "strip means something else.\n"
              f"      on disk: {authored_r7}\n      expected: {R7_AUTHORED}\n"
              "   stopping.", flush=True)
        return 4
    if FORBID_CLAUSE in authored_r7.lower():
        print(f"   !! r6 clause `{FORBID_CLAUSE}` is on disk — stale checkout; "
              f"stopping.", flush=True)
        return 6

    authored = strip_height_clause(authored_r7)
    pos, neg, neg_full, dropped, warns, removed = build(
        authored, compress, beat_negative)

    print(f"\n== beat {BEAT:02d} {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {SEED + BEAT}..{SEED + BEAT + 3000}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}", flush=True)
    print(f"   AUTHORED(r7, on disk): {authored_r7}", flush=True)
    print(f"   AUTHORED(r8, stripped): {authored}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(recipe): {neg_full}", flush=True)
    print(f"   NEG(sent):   {neg}", flush=True)
    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {neg_tokens} (budget 77)", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    if a.measure:
        cpos, cneg, _, cdropped, _, _ = build(R7_AUTHORED, compress, beat_negative)
        print("\n-- r7 CONTROL on this same tokenizer --", flush=True)
        print(f"   POS: {cpos}", flush=True)
        print(f"   positive tokens: {negative_tokens(cpos)}  "
              f"anchor {'INTACT' if cpos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={cdropped}", flush=True)
        print(f"   negative tokens: {negative_tokens(cneg)}  "
              f"identical_to_recorded_r7={cneg == R7_NEG_SENT}", flush=True)
        print(f"\n-- r8 --\n   positive tokens: {pos_tokens}  "
              f"anchor {'INTACT' if pos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={dropped}", flush=True)
        print(f"   delta r8-r7: {pos_tokens - negative_tokens(cpos)} tokens on "
              f"the positive", flush=True)
        return 0

    # trap 2: the strip must have landed where it was aimed, and the height
    # predicate must be gone from the SENT positive, not merely from the fence.
    low = pos.lower()
    if not low.startswith(EXPECT_PREFIX):
        print(f"   !! POSITIVE does not open `{EXPECT_PREFIX}` — opens "
              f"`{pos[:60]}`; stopping.", flush=True)
        return 4
    if AFTER_STRIP not in low:
        print(f"   !! the strip did not join up: `{AFTER_STRIP}` is not in the "
              f"positive; stopping.", flush=True)
        return 5
    if "taller than" in low:
        print("   !! `taller than` is still in the SENT positive — this round's "
              "whole claim is that the height instruction has left the text; "
              "stopping.", flush=True)
        return 5
    # trap 3: the negative must not have moved. Removing an unlifted clause must
    # not change one byte of it.
    if neg != R7_NEG_SENT:
        print("   !! SENT NEGATIVE DIFFERS FROM r6/r7's. Removing a clause that "
              "was never lifted must not move the negative.\n"
              f"      r7: {R7_NEG_SENT}\n      r8: {neg}\n   stopping.",
              flush=True)
        return 7
    missing = [t for t in PERSON_NEG
               if t not in [p.strip().lower() for p in neg.split(",")]]
    if missing:
        print(f"   !! PERSON TERMS DROPPED by the 77-token budget: "
              f"{', '.join(missing)}; stopping.", flush=True)
        return 9
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`; stopping.", flush=True)
        return 10
    if removed != EXPECT_DROP:
        print(f"   !! EXPECTED to remove {EXPECT_DROP} x '{DROP_NEG}', removed "
              f"{removed} — stopping so a human decides.", flush=True)
        return 2
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3

    # trap 4: the init is the founder's frame and not some other file.
    if not init_path.exists():
        print(f"   !! INIT MISSING: {init_path}; stopping.", flush=True)
        return 11
    init_sha = hashlib.sha256(init_path.read_bytes()).hexdigest()
    print(f"   INIT: {INIT_REL}\n   init sha256: {init_sha}", flush=True)
    if init_sha != INIT_SHA:
        print(f"   !! INIT SHA MISMATCH — expected {INIT_SHA}. 'img2img from the "
              f"approved plate' is this round's whole claim; stopping.",
              flush=True)
        return 12

    if a.dry:
        print(f"\nDRY OK — {len(ARMS)} arms x 4 seeds = {len(ARMS) * 4} frames, "
              f"nothing drawn", flush=True)
        return 0

    import torch
    from PIL import Image
    from diffusers import (StableDiffusionXLImg2ImgPipeline,
                           StableDiffusionXLPipeline)
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")
    # ONE set of weights for both pipelines: the arms must not differ by a
    # reload. from_pipe shares the loaded modules rather than copying them.
    i2i = StableDiffusionXLImg2ImgPipeline.from_pipe(pipe)
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s", flush=True)

    init_img = Image.open(init_path).convert("RGB")
    if init_img.size != (W, H):
        print(f"   init is {init_img.size}, resizing to {(W, H)}", flush=True)
        init_img = init_img.resize((W, H))

    n = 0
    for arm, strength in ARMS:
        for i in range(4):
            seed = SEED + BEAT + i * 1000
            g = torch.Generator(device="cpu").manual_seed(seed)
            t0 = time.time()
            if strength is None:
                img = pipe(prompt=pos, negative_prompt=neg,
                           num_inference_steps=STEPS, guidance_scale=CFG,
                           generator=g, width=W, height=H).images[0]
            else:
                img = i2i(prompt=pos, negative_prompt=neg, image=init_img,
                          strength=strength, num_inference_steps=STEPS,
                          guidance_scale=CFG, generator=g).images[0]
            f = out / f"{BEAT:02d}-{s['slug']}-{CANDIDATE_SET}-{arm}-s{i}.png"
            img.save(f)
            secs = time.time() - t0
            sidecar(f, seed=seed, arm=arm, strength=strength, pos=pos, neg=neg,
                    neg_full=neg_full, secs=secs, warns=warns, task=TASK,
                    shots_sha=shots_sha, pos_tokens=pos_tokens,
                    neg_tokens=neg_tokens)
            n += 1
            print(f"   {f.name} seed={seed} {secs:.0f}s  ({n}/{len(ARMS) * 4})",
                  flush=True)

    print(f"\nDONE {n} stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
