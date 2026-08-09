#!/usr/bin/env python3
"""002b beat 01 — ROUND 7, the MEASURE correction. 2026-08-09.

WHY THIS ROUND EXISTS, in the record's own words. r6 (taste ledger record 28,
`reject_all`, 0.75) closed with the next lever already named: three of its four
failures are about the stem's LENGTH, and `40cm`, `whole plant in frame` and
`short grass` have all now failed to bound it. What is left is the suspicion that
**`rising well above the grass` — the clause r6 imported from b15 — is itself
what makes it tall**, and that naming the grass as the MEASURE says the opposite
thing. shots.md states the replacement verbatim: *no taller than the grass around
it*. This script renders that and nothing else.

THE SINGLE VARIABLE IS ONE CLAUSE AND THE SCRIPT PROVES IT RATHER THAN PROMISING
IT. r6's authored fence and r7's differ by exactly this substitution:

    its sturdy curved stem rising well above the grass
    its sturdy curved stem no taller than the grass around it

Everything else is byte-identical: the person-binding r6 proved (`no girl, no
boy, no child, no person`), the grass-height framing's ground plane (`standing in
short grass`), `40cm`, `whole plant in frame`, `wide shot`, the fruit described
without the word `fig`, the sunrise palette, the style tail, the seeds, the
model, the size, the steps, the cfg and the one-term negative removal.

THE TRAP THIS CLAUSE WALKS PAST, AND WHY IT DOES NOT SPRING. `no taller than the
grass around it` is comma-terminated and letter-initial, which is the exact shape
`sd_prompt._NEGATION` lifts OUT of the positive and into the negative — the
convention r6 used deliberately to place the four person terms. Lifted, this
round would say the opposite of what it means: the positive would lose its only
height instruction and the negative would gain "taller than the grass around it".
It is not lifted, and the reason is measurable rather than lucky: the pattern
captures `([a-z][a-z\\- ]{1,24}?)` before a comma, a 25-character ceiling, and the
clause is 31 characters. Verified on the real path — the lifted set is
character-for-character identical between r6 and r7, twelve terms, so THE SENT
NEGATIVE DOES NOT MOVE AT ALL. `assert_r6_negative` below turns that from a
finding into a precondition: the round refuses to spend a step if the negative it
is about to send differs by one byte from the negative r6 was drawn with. A
single-variable round whose negative shifted would answer nothing.

THE BUDGET IS THE REAL RISK AND IT IS MEASURED ON THE BOX, NEVER ON THE MAC.
The new clause is two words longer than the one it replaces, and r6's positive
had no measured headroom recorded. When `compress()` runs out of budget it sheds
the TRAILING sentence, which is the one carrying `masterpiece, best quality, very
aesthetic` — the r4 defect this genome has already paid for twice (308c74e on
beat 13, and r6's own third change here). So `ANCHOR` is asserted, not hoped for.

Run the measurement on the rtx5090 and nowhere else. `sd_prompt._token_estimate`
falls back to an approximation when `transformers` is absent and it OVER-COUNTS a
positive of this shape by about 3 tokens — straddling the 77 boundary. On the Mac
this exact r7 text reports the anchor DROPPED; that reading is an artefact of the
missing tokenizer and was what r8 proved (STATE.md 2026-08-09: "the box is the
only place this beat's budget can be measured"). `--measure` prints the r6
control beside r7 so the delta is read off one tokenizer, not two.

    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r7.py --root ... --measure
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r7.py --root ... --dry
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r7.py --root ...

WHAT THIS ROUND IS SCORED ON, pre-registered so it cannot be moved afterwards.
The rubric is HIS CEILING, measured rather than eyeballed: the revoked plate stood
32% of frame height on a 1-3px hairline and he threw it out, and r6-s3 — the first
frame in six rounds inside that ceiling — sat at about a fifth. So the round's
number is the STEM HEIGHT FRACTION, apex-to-groundline over frame height, reported
per seed. Person-binding must HOLD at 0 people in 4 of 4; a regression there costs
the round its control. The fig is OBSERVED AND NOT GATED — 0 of 20 across six
rounds is a conclusion the record already reached and this round changes nothing
that would move it.
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
CANDIDATE_SET = "r7"
QUEUE_ENTRY = "ep2-b01-r7-coldopen-1786292601"
TASK = "ep2-b01-r7-coldopen-1786292601"
BEAT = 1
EXPECT_DROP = 1  # `tiny`, `40cm`, `seedling` all fire _SMALL
EXTRA_NEG = ""   # r6 carried none on this beat and r7 adds none

# The round-7 clause, and the round-6 clause it replaces. Both are checked: the
# first must be present, the second absent. A stale checkout that still carried
# r6's fence would otherwise render r6 again and stamp r7's id on it.
EXPECT_CLAUSE = "no taller than the grass around it"
FORBID_CLAUSE = "rising well above the grass"
EXPECT_PREFIX = "a tiny 40cm seedling standing in short grass"

# The style anchor. compress() sheds the trailing sentence first and that is the
# sentence carrying it; r7 is two words longer than r6, so this is checked.
ANCHOR = ("cinematic lighting, detailed, newest, masterpiece, best quality, "
          "very aesthetic")

# r6's authored fence, verbatim, kept ONLY as the measurement control for
# --measure. Never rendered by this script.
R6_AUTHORED = (
    "A tiny 40cm seedling standing in short grass, its sturdy curved stem "
    "rising well above the grass, two oversized cotyledon leaves, one small "
    "round green fruit hanging from the stem, whole plant in frame, wide shot, "
    "peach and gold sunrise sky, no girl, no boy, no child, no person, no "
    "chibi, no mascot, no creature, no face, no branches, no night sky, "
    "cinematic lighting, detailed, newest, masterpiece, best quality, very "
    "aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.")

# The negative the four r6 frames were actually drawn with, read off
# 01-cold-open-r6-s0.png.meta.yaml. r7 must send this string unchanged.
R6_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, "
    "low quality, blurry, extra limbs, deformed, mature tree, large tree, "
    "thick trunk, full canopy, forest, bush, shrubbery, girl, boy, child, "
    "person, chibi, mascot, creature, face, branches, night sky, photorealism")

# The four person terms r6 proved bind on this beat. They must survive the
# 77-token fit or the round has lost its control.
PERSON_NEG = ("girl", "boy", "child", "person")

NOTE = (
    'round 7, the MEASURE correction, and the record named it before the round '
    'existed: r6 (ledger record 28, reject_all, 0.75) closed with "three of four '
    'failures are about the stem\'s LENGTH, and 40cm plus whole plant in frame '
    'plus short grass have all now failed to bound it", leaving one prompt-side '
    'idea — that `rising well above the grass`, the clause r6 imported from the '
    'b15 plate, is ITSELF what makes it tall, and that naming the grass as the '
    'MEASURE says the opposite thing. THE SINGLE VARIABLE is that substitution '
    'and nothing else: `its sturdy curved stem rising well above the grass` -> '
    '`its sturdy curved stem no taller than the grass around it`, shots.md\'s own '
    'wording. r6\'s person-binding (`no girl, no boy, no child, no person`, which '
    'returned 0 people in 4 of 4 and is this beat\'s one clean success), its '
    'ground plane (`standing in short grass`), `40cm`, `whole plant in frame`, '
    '`wide shot`, the fruit described without the word `fig`, the sunrise '
    'palette, the style tail, the four seeds, the model, size, steps, cfg and the '
    'one-term negative removal are byte-identical. THE LIFT TRAP WAS CHECKED, NOT '
    'ASSUMED: `no taller than the grass around it` is comma-terminated and '
    'letter-initial, the exact shape sd_prompt._NEGATION lifts into the negative, '
    'and lifting it would invert the round — the positive would lose its only '
    'height instruction and the negative would gain "taller than the grass around '
    'it". It is not lifted because _NEGATION captures at most 25 characters '
    'before the comma and the clause is 31, so the lifted set is identical '
    'between r6 and r7 and THE SENT NEGATIVE DOES NOT MOVE AT ALL; this script '
    'refuses to render if it differs by one byte from the negative r6 was drawn '
    'with. THE BUDGET was measured on the box\'s real CLIP tokenizer before a '
    'step was spent, with the r6 fence as the control on the same tokenizer, '
    'because the new clause is two words longer and compress() sheds the trailing '
    'sentence first — the sentence carrying `masterpiece, best quality, very '
    'aesthetic`, the r4 defect this genome has paid for twice. The same check on '
    'the Mac reports the anchor DROPPED and that reading is an artefact: '
    '_token_estimate falls back to an approximation without transformers and '
    'over-counts a positive of this shape by about 3, straddling 77 — the trap r8 '
    'documented. PRE-REGISTERED RUBRIC, so it cannot move after the pictures '
    'exist: the number is the STEM HEIGHT FRACTION (apex to groundline over frame '
    'height) per seed, against the 32% hairline he revoked and the ~20% of r6-s3, '
    'the first frame in six rounds inside his ceiling; person-binding must hold at '
    '0 of 4 or the round loses its control; the fig is OBSERVED AND NOT GATED, '
    'because 0 of 20 across six rounds is a conclusion the record already reached '
    'and nothing in this round would move it. PROVISIONAL: a steward-rendered '
    'candidate, not a pick and not canon. Ledger record written BEFORE the sheet, '
    'the sheet carries labels and seeds only with no favourite and no ordering '
    '(R4), and nothing is opened on the founder\'s screen.')


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, task: str, shots_sha: str,
            pos_tokens: int, neg_tokens: int) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b01r7.py",
             "# on the rtx5090 (C:\\banyan-farm\\sample-b01-r7).",
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
            f"task: {task}",
            f"queue_entry: {QUEUE_ENTRY}",
            f"render_round: {CANDIDATE_SET}",
            f"candidate_set: {CANDIDATE_SET}",
            f"negative_terms_removed: {DROP_NEG}",
            f"prompt_source_sha256: {shots_sha}",
            f"positive_clip_tokens: {pos_tokens}",
            f"negative_clip_tokens: {neg_tokens}",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            "negative_identical_to_r6: true",
            "single_variable: >-",
            block("`its sturdy curved stem rising well above the grass` -> "
                  "`its sturdy curved stem no taller than the grass around it`. "
                  "The authored fences differ by that substitution and nothing "
                  "else, and the SENT negative is byte-identical to r6's."),
            "provisional: >-",
            block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and not "
                  "canon. Scored against taste/steward-model.v1 and logged in "
                  "taste/steward-model.ledger.yaml BEFORE the founder saw it. "
                  "Ground truth is the founder (R4); he has ratified nothing "
                  "here. Never takes a canon filename, is not published, not "
                  "posted, and not assembled into an episode."),
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 6, takes/stills/01-cold-open-r6-s*.png — model, size, "
                  "steps, cfg, seed rule, the one-term negative removal and "
                  "every clause of the positive except the one this round "
                  "replaces are r6's unchanged. r6 in turn inherited them from "
                  "node 001 takes/stills/15-something-s-coming-r3-s1.png, the "
                  "ONE SAMPLE the founder passed on 2026-08-08."),
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
    ap.add_argument("--shots", default=None,
                    help="shots.md to read the fence from (default: root's)")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print r6 control beside r7 on this box's tokenizer, "
                         "draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = Path(a.shots).resolve() if a.shots else node / "shots.md"
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in
             parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    authored = s["prompt"]

    # THE TOKENIZER IS THE WHOLE POINT OF RUNNING THIS HERE. Without it every
    # number below is an estimate that is known to be wrong near 77.
    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts this "
              "prompt by ~3 near the 77 boundary. Run this on the box's venv; "
              "stopping.", flush=True)
        return 8

    pos, neg, neg_full, dropped, warns, removed = build(
        authored, compress, beat_negative)

    print(f"\n== beat {BEAT:02d} {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {SEED + BEAT}..{SEED + BEAT + 3000}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}", flush=True)
    print(f"   AUTHORED: {authored}", flush=True)
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
        cpos, cneg, _, cdropped, _, _ = build(
            R6_AUTHORED, compress, beat_negative)
        print("\n-- r6 CONTROL on this same tokenizer --", flush=True)
        print(f"   POS: {cpos}", flush=True)
        print(f"   positive tokens: {negative_tokens(cpos)}  "
              f"anchor {'INTACT' if cpos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={cdropped}", flush=True)
        print(f"   negative tokens: {negative_tokens(cneg)}  "
              f"identical_to_recorded_r6={cneg == R6_NEG_SENT}", flush=True)
        print(f"\n-- r7 --\n   positive tokens: {pos_tokens}  "
              f"anchor {'INTACT' if pos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={dropped}", flush=True)
        print(f"   delta r7-r6: {negative_tokens(pos) - negative_tokens(cpos)} "
              f"tokens on the positive", flush=True)
        return 0

    # trap 1: the checkout must carry r7's clause, and must NOT carry r6's.
    low = pos.lower()
    if not low.startswith(EXPECT_PREFIX):
        print(f"   !! POSITIVE does not open `{EXPECT_PREFIX}` — opens "
              f"`{pos[:60]}`; stopping.", flush=True)
        return 4
    if EXPECT_CLAUSE not in low:
        print(f"   !! r7 CLAUSE `{EXPECT_CLAUSE}` is not in the positive. Either "
              f"the checkout is stale, or _NEGATION lifted it into the negative "
              f"— which would invert this round; stopping.", flush=True)
        return 5
    if FORBID_CLAUSE in low:
        print(f"   !! r6 CLAUSE `{FORBID_CLAUSE}` is still in the positive — the "
              f"checkout is stale and this would render r6 again under r7's id; "
              f"stopping.", flush=True)
        return 6
    # trap 2: the negative must not have moved. This is what makes it ONE variable.
    if neg != R6_NEG_SENT:
        print("   !! SENT NEGATIVE DIFFERS FROM r6's. This round's whole claim is "
              "that only the positive moved.\n"
              f"      r6: {R6_NEG_SENT}\n      r7: {neg}\n   stopping.",
              flush=True)
        return 7
    missing = [t for t in PERSON_NEG
               if t not in [p.strip().lower() for p in neg.split(",")]]
    if missing:
        print(f"   !! PERSON TERMS DROPPED by the 77-token budget: "
              f"{', '.join(missing)} — that is r6's one proven success and this "
              f"round must not lose it; stopping.", flush=True)
        return 9
    # trap 3: r7 is two words longer than r6, and the trailing sentence is the
    # first thing compress() sheds. r4 shipped without the anchor once already.
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`. compress() shed the trailing sentence to reach 77, "
              f"which is the r4 defect; stopping.", flush=True)
        return 10
    if removed != EXPECT_DROP:
        print(f"   !! EXPECTED to remove {EXPECT_DROP} x '{DROP_NEG}', removed "
              f"{removed} — stopping so a human decides.", flush=True)
        return 2
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3

    if a.dry:
        print("\nDRY OK — 1 beat x 4 seeds = 4 frames, nothing drawn", flush=True)
        return 0

    import torch
    from diffusers import StableDiffusionXLPipeline
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(BASE, torch_dtype=torch.bfloat16,
                                                     use_safetensors=True)
    pipe.to("cuda")
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s", flush=True)

    for i in range(4):
        seed = SEED + BEAT + i * 1000
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=STEPS,
                   guidance_scale=CFG, generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT:02d}-{s['slug']}-{CANDIDATE_SET}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, task=TASK, shots_sha=shots_sha,
                pos_tokens=pos_tokens, neg_tokens=neg_tokens)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
