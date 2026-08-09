#!/usr/bin/env python3
"""node 001 beat 10 — ROUND 5, SENSE. The person negatives that actually bind. 2026-08-09.

THE DEFECT THIS ROUND ANSWERS IS MEASURED, NOT SUSPECTED. r4 drew a human hand
and forearm in one frame and a bare foot in another — 2 of 4 — on a beat whose
own text is roots, soil and a stem, with no person in it anywhere. The frame's
negative already carried `humans`, so this is not a missing fence: the term was
sent and the model drew people through it.

WHY `humans` DOES NOT BIND, AND WHAT DOES. PROVISIONAL-PICKS-0809.md's
wave-level diagnosis, defect 2, is a controlled result across five sheets:
human figures and hands came back on b01 r5 (3 of 4), b14 (3 of 4), b20 (2 of
4), b21 (2 of 4) and b15-s1, every one of them with the plural in the negative,
while node 002b beat 01 in the SAME pass with the singular set returned 0 people
in 4 of 4. Its finding, verbatim: "The word `humans` alone is not binding this
checkpoint; the terms that bind it are `1girl, 1boy, child, person, hand`."
Those are Danbooru count/subject tags and this checkpoint is animagine-xl-3.1,
trained on that vocabulary — the plural English noun is not in the dialect the
tags are.

THE ROUND IS ADDITIVE AND `humans` STAYS. Swapping the plural out would move two
things at once and leave no way to attribute the result. Trap 7 asserts the term
is still in the sent negative, so if people go away the added singulars are the
only thing that can have done it.

THE POSITIVE IS BYTE-IDENTICAL TO r4's AND TRAP 6 PROVES IT. This is the whole
design: r4's sheet was rejected on the roots (still absent 0 of 4) as well as on
the people, and this round deliberately does NOT try to fix the roots. One round
that moves two things answers neither — the same direction the lead gave the b01
r7 lane about the hairline. The root-map lead clause stays exactly where r4 put
it, so whatever the sheet says about roots is a second reading of r4's own
wording on r4's own noise, which is worth more than a fresh guess.

SEEDS ARE HELD FROM r4 — 20260729/20261729/20262729/20263729, this beat's k=0..3.
Same noise as the sheet that drew the hand and the foot, so the negative is the
only variable between the two sheets. b05's convention from r3 through r5 and
b13's from r4 through r9.

WHERE THE TERMS GO, AND WHY IT IS NOT THE FENCE. `fit_negative`'s drop order is
house -> scale -> beat -> explicit, so the EXPLICIT tier is the last thing
trimmed and the only tier that cannot be silently shed by a beat this close to
the budget. r4's negative was ALREADY over 77: its own NEGWARN records
`deduplicated: text; DROPPED: realistic skin texture, jpeg artifacts`. Writing
the new terms into shots.md as `no girl, no boy...` would land them in the BEAT
tier, third in the drop order, which is exactly the silent trim the queue entry
warned about (`eleven negated nouns is exactly the size at which fit_negative
trims silently`, e6995fc). They are passed as explicit instead, and trap 5
asserts every one of them survived into the string the model sees.

SHOTS.MD IS NOT EDITED. The fence is asserted byte-for-byte first (trap 1) so a
stale checkout cannot start, and nothing here is canon or founder-read.

MEASURE ON THE BOX OR NOT AT ALL. `sd_prompt._token_estimate` falls back to a
prose approximation without `transformers` and over-counts near 77 — it has
already produced one false failure on this tree. This script exits 8 rather than
report an estimate as a measurement.

Usage:
    python render_b10r5.py --root C:\\banyan-farm\\banyan-city --measure
    python render_b10r5.py --root C:\\banyan-farm\\banyan-city --dry
    python render_b10r5.py --root C:\\banyan-farm\\banyan-city
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
DROP_NEG = "tall tree"
EXPECT_DROP = 1
CANDIDATE_SET = "r5"
QUEUE_ENTRY = "no-humans-sweep-sample-1786292646"
TASK = "001-b10-r5-nohumans-0810"
BEAT = 10
NODE = "001-capability-inventory"

# r4's own four, held. k=0..3 of this beat's series.
SEEDS = [20260729, 20261729, 20262729, 20263729]

# defect 2's prescribed binding set, plus the two body-part nouns the r4
# failures were actually made of (a forearm, a bare foot). Sent as the EXPLICIT
# tier so fit_negative cannot shed them silently.
EXTRA_NEG = "1girl, 1boy, child, person, hand"
EXTRA_NEG_TIER = "person-binding-defect2"

# WHAT THIS ROUND COSTS, MEASURED BEFORE IT RAN, AND WHY IT IS PAID ANYWAY.
# This beat's negative is FULL: r4 already overran 77 tokens and shed two terms
# of its own. Every candidate set was priced on the box's real CLIP
# (pipeline/measure_b10_negsets.py) and there is no free one — even a
# three-term `1girl, 1boy, person` loses `blurry`. So the choice was not
# whether to pay but what to buy, and this round buys defect 2's prescription
# VERBATIM rather than a set of my own: five terms, paid for with `blurry`,
# `low quality`, `deformed`, `extra limbs` and `signature` off the house tier.
# `arm` and `foot` were in the first draft — the two body parts r4 actually
# drew — and are dropped here because they were my extrapolation, they cost
# `watermark` on top, and the prescription is the thing with evidence behind
# it. THE CONFOUND IS REAL AND IS NOT HIDDEN: if these frames come back softer
# than r4's, the missing quality negatives are a candidate cause. What makes it
# readable anyway is that r4's four frames are the control and they are on
# THESE SEEDS with a byte-identical positive, so the comparison is direct.
NEG_COST = ("blurry, low quality, deformed, extra limbs, signature — shed from "
            "the house tier by fit_negative to fit the five added terms")

# THE FENCE, BYTE-FOR-BYTE, from genomes/.../001-capability-inventory/shots.md.
# Control and staleness guard in one. r4 rendered exactly this.
AUTHORED = (
    "root-map of pale spreading roots in dark damp soil, mineral glitter, veins "
    "of dark water, one slender seedling stem rising into short grass, very low "
    "shot at the soil line, warm morning light, cinematic lighting, detailed, "
    "newest, masterpiece, best quality, very aesthetic No post, no fence, no "
    "pole, no building, no lake, no water surface, no dark background, no black "
    "void, no cave, no humans. No photorealism, no 3D render look. 9:16 "
    "vertical, no text.")

# WHAT r4 ACTUALLY SENT, from takes/stills/10-sense-r4-s0.png.meta.yaml. The
# positive must come back byte-identical this round (trap 6); the negative is
# the only thing allowed to move.
R4_POS_SENT = (
    "root-map of pale spreading roots in dark damp soil, mineral glitter, veins "
    "of dark water, one slender seedling stem rising into short grass, very low "
    "shot at the soil line, warm morning light, cinematic lighting, detailed, "
    "newest, masterpiece, best quality, very aesthetic")
R4_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, mature tree, large tree, thick "
    "trunk, full canopy, forest, bush, shrubbery, post, fence, pole, building, "
    "lake, water surface, dark background, black void, cave, humans, "
    "photorealism")

# every term this round adds. All seven must survive fit_negative's 77-token
# trim or the round has not been run.
EXPECT_NEG_ADDS = ("1girl", "1boy", "child", "person", "hand")

# the term that must NOT move: this round is additive and `humans` stays, so
# that a clean sheet cannot be explained by having removed it.
HOLD_NEG = "humans"

NOTE = (
    'round 5, THE PERSON NEGATIVES THAT BIND. r4 drew a human hand and forearm '
    'in one frame and a bare foot in another, 2 of 4, on a beat whose text is '
    'roots, soil and a stem — and its negative ALREADY carried `humans`, so the '
    'term was sent and the model drew people through it. Defect 2 of the '
    'wave-level diagnosis (PROVISIONAL-PICKS-0809.md) is the controlled version '
    'of the same result: the plural failed on b01 r5, b14, b20, b21 and b15-s1, '
    'while node 002b beat 01 in the SAME pass with the singular set returned 0 '
    'people in 4 of 4. Its terms — `1girl, 1boy, child, person, hand` — are '
    'Danbooru subject tags and this checkpoint is animagine, trained on that '
    'vocabulary; the plural English noun is not in the dialect the tags are. '
    'THIS ROUND IS ADDITIVE: `humans` STAYS (trap 7), so if the people go away '
    'the seven added singulars are the only thing that can have done it. THE '
    'TERMS GO IN THE EXPLICIT TIER, NOT THE FENCE: fit_negative drops '
    'house->scale->beat->explicit, r4 was already over budget (its own NEGWARN '
    'deduplicated `text` and DROPPED `realistic skin texture, jpeg artifacts`), '
    'and writing them into shots.md would put them in the BEAT tier where they '
    'could be shed silently — the trim the queue entry named at e6995fc. Trap 5 '
    'asserts all seven arrived. THE POSITIVE IS BYTE-IDENTICAL TO r4 AND TRAP 6 '
    'PROVES IT: r4 was also rejected on the roots (absent 0 of 4) and this round '
    'deliberately does not touch that, because one round that moves two things '
    'answers neither. Seeds are r4\'s own four, held, so the negative is the '
    'only variable between the two sheets. shots.md NOT edited.')

WHY_NOT_FENCE = (
    "The generic plural is NOT removed from the fence even though it is the "
    "term that failed. Removing it would be a second variable, and the sweep "
    "lane already measured that the fence rewrite is a no-op on the machine "
    "path anyway: sd_prompt._NEGATION lifts `no humans` out of the positive and "
    "into the negative from any position, proven on all eight of node 001's "
    "fences (pipeline/measure_no_humans.py, commit 1aab710). So the fence text "
    "was never the defect. What the fence cannot do is choose WHICH tier the "
    "term lands in, and that is the whole of this round.")


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, shots_sha: str, pos_tokens: int,
            neg_tokens: int, r4_neg_tokens: int, out_dir: Path) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b10r5.py",
             f"# on the rtx5090 ({out_dir}).",
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
            f"task: {TASK}",
            f"queue_entry: {QUEUE_ENTRY}",
            f"render_round: {CANDIDATE_SET}",
            f"candidate_set: {CANDIDATE_SET}",
            f"negative_terms_removed: {DROP_NEG}",
            f"extra_negative_tier: {EXTRA_NEG_TIER}",
            f"extra_negative_terms: {EXTRA_NEG}",
            "extra_negative_tier_note: >-",
            block("Passed as fit_negative's EXPLICIT tier, which is last in the "
                  "drop order house->scale->beat->explicit. r4's negative was "
                  "already over the 77-token budget on this beat, so terms "
                  "written into the fence would land in the BEAT tier and could "
                  "be shed without changing the picture anyone looks at. All "
                  "seven are asserted present in the sent string at run time."),
            "why_the_fence_was_not_edited: >-",
            block(WHY_NOT_FENCE),
            "additive_round: true",
            f"negative_delta_from_r4: {EXTRA_NEG}",
            f"negative_cost_from_r4: {NEG_COST}",
            "negative_cost_note: >-",
            block("Priced on the box's real CLIP before a step "
                  "(pipeline/measure_b10_negsets.py). This beat's negative was "
                  "already full — r4 overran 77 and shed two terms of its own — "
                  "so there is no free version of this round: even a three-term "
                  "`1girl, 1boy, person` loses `blurry`. The round therefore "
                  "buys defect 2's prescription VERBATIM rather than a set of "
                  "the steward's own. THE CONFOUND IS DECLARED, NOT HIDDEN: if "
                  "these frames read softer than r4's, the shed quality "
                  "negatives are a candidate cause. It stays readable because "
                  "r4's four frames are the control, on these same seeds, with "
                  "a byte-identical positive."),
            "positive_delta_from_r4: none (byte-identical, asserted)",
            "held_negative_term: humans",
            "held_negative_note: >-",
            block("`humans` is deliberately KEPT so this round is purely "
                  "additive. If the people go away, the seven added singulars "
                  "are the only thing that can have done it — a swap would have "
                  "left the result unattributable."),
            f"shots_md_sha256: {shots_sha}",
            "shots_md_edited: false",
            "authored_source: >-",
            block("genomes/sapling/nodes/001-capability-inventory/shots.md beat "
                  "10, byte-for-byte and asserted before a step. The round adds "
                  "nothing to the positive; only the negative's explicit tier "
                  "changes."),
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            f"positive_tokens: {pos_tokens}",
            f"negative_tokens_sent: {neg_tokens}",
            f"negative_tokens_r4_control: {r4_neg_tokens}",
            "r4_control_reproduced: true",
            "controls_note: >-",
            block("r4 is rebuilt from this checkout in the same run on the same "
                  "tokenizer and asserted byte-for-byte against its recorded "
                  "sidecars, positive AND negative, so the delta below is one "
                  "measurement rather than two instruments."),
            "anchor_intact: true",
            "seeds_held_from: >-",
            block("round 4, takes/stills/10-sense-r4-s*.png — this beat's own "
                  "k=0..3. Same noise as the sheet that drew the hand and the "
                  "foot, so the negative is the only variable across the two."),
            "provisional: >-",
            block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and not "
                  "canon. Scored against taste/steward-model.v1 and logged in "
                  "taste/steward-model.ledger.yaml BEFORE the founder saw it. "
                  "Ground truth is the founder (R4); he has ratified nothing "
                  "here. Never takes a canon filename, is not published, not "
                  "posted, and not assembled into an episode."),
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 4, takes/stills/10-sense-r4-s*.png — model, size, "
                  "steps, cfg, the seed series and the one-term negative "
                  "removal are unchanged from r4, which inherited them from "
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


def build(authored: str, compress, beat_negative, extra: str) -> tuple:
    """The full prompt pair for one authored fence, through the real code path."""
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, extra, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)
    return pos, neg, neg_full, dropped, warns, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print the r4 control beside r5 on this box's real "
                         "tokenizer, draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes" / NODE
    shots_path = node / "shots.md"
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

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

    # trap 1: the fence must still be the one r4 rendered, byte for byte. This
    # round does not edit shots.md, so a stale checkout would render the wrong
    # control and the delta would mean nothing.
    if authored != AUTHORED:
        print("!! shots.md Beat 10 is not the fence r4 rendered, byte for byte "
              "— the checkout is stale or the fence moved, and the control "
              "below would not be a control.\n"
              f"   expected: {AUTHORED}\n"
              f"   found:    {authored}\n   stopping.", flush=True)
        return 4

    pos, neg, neg_full, dropped, warns, removed = build(
        AUTHORED, compress, beat_negative, EXTRA_NEG)
    cpos, cneg, cneg_full, cdropped, cwarns, cremoved = build(
        AUTHORED, compress, beat_negative, "")

    print(f"\n== node {NODE} beat {BEAT} {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {', '.join(str(x) for x in SEEDS)}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}  (NOT edited by this round)", flush=True)
    print(f"   AUTHORED (fence, shared with r4): {AUTHORED}", flush=True)
    print(f"   POS(sent):        {pos}", flush=True)
    print(f"   POS(r4 control):  {cpos}", flush=True)
    print(f"   NEG(recipe):      {neg_full}", flush=True)
    print(f"   NEG(sent):        {neg}", flush=True)
    print(f"   NEG(r4 control):  {cneg}", flush=True)

    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    cneg_tokens = negative_tokens(cneg)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: r4 control {cneg_tokens} -> recipe "
          f"{negative_tokens(neg_full)} -> sent {neg_tokens} (budget 77)",
          flush=True)
    for w in cwarns:
        print(f"   NEGWARN(r4 control): {w}", flush=True)
    for w in warns:
        print(f"   NEGWARN(r5): {w}", flush=True)

    # trap 2: the r4 control must reproduce from THIS checkout, both halves.
    # Without it the delta is two instruments rather than one measurement.
    if cpos != R4_POS_SENT:
        print("!! the r4 POSITIVE does not reproduce from this checkout.\n"
              f"   recorded: {R4_POS_SENT}\n"
              f"   rebuilt:  {cpos}\n   stopping.", flush=True)
        return 5
    if cneg != R4_NEG_SENT:
        print("!! the r4 NEGATIVE does not reproduce from this checkout.\n"
              f"   recorded: {R4_NEG_SENT}\n"
              f"   rebuilt:  {cneg}\n   stopping.", flush=True)
        return 6
    print("   trap 2 OK — r4 control reproduces byte-for-byte, both halves",
          flush=True)

    # trap 3: no positive drop. compress() sheds trailing sentences and the
    # style sentence is always last, so a drop here would cost the anchor.
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3

    # trap 4: the anchor. Losing it would change the look and confound the
    # negative's effect with a style change.
    if not pos.rstrip().endswith("very aesthetic"):
        print(f"   !! ANCHOR GONE — the sent positive does not end `very "
              f"aesthetic`: …{pos[-60:]!r}; stopping.", flush=True)
        return 7

    # trap 5: every term this round buys must survive the 77-token trim. This
    # is the silent-trim failure the queue entry named; an unasserted round
    # here would report a result about terms the model never received.
    sent_terms = {p.strip().lower() for p in neg.split(",")}
    missing = [t for t in EXPECT_NEG_ADDS if t.lower() not in sent_terms]
    if missing:
        print(f"   !! TRIMMED AWAY: {', '.join(missing)} — these are the round. "
              f"fit_negative shed them to fit 77 tokens, so the sheet would "
              f"test terms the model never saw. Sell something from the house "
              f"tier and re-measure; stopping.", flush=True)
        return 9
    print(f"   trap 5 OK — all {len(EXPECT_NEG_ADDS)} added terms survived the "
          f"trim", flush=True)

    # trap 6: THE SINGLE VARIABLE. The positive must be byte-identical to r4's.
    if pos != R4_POS_SENT:
        print("!! the sent POSITIVE differs from r4's — this round is defined "
              "by moving only the negative, and a positive delta would make "
              "the sheet unattributable.\n"
              f"   r4: {R4_POS_SENT}\n   r5: {pos}\n   stopping.", flush=True)
        return 10
    print("   trap 6 OK — positive byte-identical to r4, negative is the only "
          "variable", flush=True)

    # trap 7: the round is ADDITIVE. `humans` must still be there, so a clean
    # sheet cannot be explained by its removal.
    if HOLD_NEG.lower() not in sent_terms:
        print(f"   !! `{HOLD_NEG}` is NOT in the sent negative — this round is "
              f"additive by design and dropping it would move two things at "
              f"once; stopping.", flush=True)
        return 12
    print(f"   trap 7 OK — `{HOLD_NEG}` held, round is purely additive",
          flush=True)

    if removed != EXPECT_DROP:
        print(f"   !! EXPECTED to remove {EXPECT_DROP} x '{DROP_NEG}', removed "
              f"{removed} — stopping so a human decides.", flush=True)
        return 2

    if a.measure:
        print("\nMEASURE OK — nothing drawn", flush=True)
        return 0
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

    for i, seed in enumerate(SEEDS):
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=STEPS,
                   guidance_scale=CFG, generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT:02d}-{s['slug']}-{CANDIDATE_SET}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, shots_sha=shots_sha, pos_tokens=pos_tokens,
                neg_tokens=neg_tokens, r4_neg_tokens=cneg_tokens, out_dir=out)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
