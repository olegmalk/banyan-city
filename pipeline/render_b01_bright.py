#!/usr/bin/env python3
"""002b beat 01 — the BRIGHT BASE: r8's i35 arm with the lighting ban in the
negative, so the fig inpaint has something other than dusk to land on.

WHY THIS EXISTS, AND WHY IT IS NOT ANOTHER STRENGTH SWEEP. `ep2-b01-figmatte-0811`
proved the matte-green fig mask works, but it inpainted OVER the founder's dusk
plate, so the round inherited the plate's light and the lighting ban — the one
fix that landed tonight, on beats 04 and 02 — never got a channel that reached
the pixels. Under a mask it cannot get one: 99% of those pixels are restored by
the mask blend every step, and no negative reaches restored pixels. The fix is
the ORDER. Relight the base FIRST, then mask onto the relit frame.

WHAT THE RECORD ALREADY SETTLED, SO THIS ROUND DOES NOT RE-ASK IT. Ledger record
`ep2-b01-r8-sample` ran exactly this init at strength 0.35 and 0.55 with beat
01's own fence, which says `peach and gold sunrise sky` in those words:
    "at 0.35 the palette has not moved, and at 0.55 — the top of the range the
     2026-08-06 repaints ever measured — it has STILL not moved"
    "Retired: that a low strength can carry a foreign palette — it cannot,
     measured at two strengths."
and, in the same record, "The t2i control renders that sky correctly on all four
seeds, so the prompt is not the problem; the init is overriding it." So a higher
strength is not the lever — it was measured, twice, and it also grew the stem
back toward the 32% hairline the founder revoked. THE UNTESTED CHANNEL IS THE
NEGATIVE. Tonight's beat-04 result is the evidence that it is worth one round:
positive lighting words did not bind on this checkpoint and the negative did.

THE ONE VARIABLE IS EIGHT TERMS, AND IT IS PROVED RATHER THAN ASSERTED. The
eight terms are beat 04's block verbatim. They are inserted into the AUTHORED
fence as `no ...` clauses, which is beat 04's own mechanism: `sd_prompt`'s
negation lifter pulls each one OUT of the positive and `extra_negative_parts`
sends them as BEAT-tier terms, which `fit_negative` protects ahead of the house
defaults. The consequence is checkable and this script checks it at run time:
THE SENT POSITIVE COMES OUT BYTE-IDENTICAL TO r8'S, and the script refuses to
draw if it does not. Same init, same sha assertion, same 832x1216, same 40
steps, same cfg 7.5, same strength 0.35, and the same four seeds r8 drew —
because they are computed by the same rule from r8's own constants, which are
IMPORTED from `render_b01r8.py` rather than copied. A copy can drift; an import
cannot.

THE COST IS REAL AND IS PRINTED, NOT HIDDEN. The negative is already near CLIP's
77 and the beat tier outranks the house tier, so buying eight lighting terms
SELLS house terms off the end. On the Mac's estimator the sacrifice is
`blurry, low quality, signature, watermark, abstract, 3d render, photorealistic,
shrubbery` — but the estimator over-counts this shape by ~3 near the boundary,
so the real figure is measured here, on the box's tokenizer, and named in the
sidecar. `photorealism` (beat tier) survives and covers most of what
`photorealistic` and `3d render` were doing. The person terms are asserted
present and the style anchor is asserted intact; if either goes, nothing is
drawn.

WHAT THIS ROUND CANNOT SETTLE. If four seeds come back dusk with `dark, night,
dusk, sunset` provably sent, then beat 01's light is a property of the PLATE and
no prompt channel reaches it — and the honest next step is the question already
queued for the founder in `ep2-b01-pickpage-founder-verdict-0811` (is a fixed
dusk cold open acceptable, or does beat 01 need a plate he approves first?), or
the depth-ControlNet route shots.md named. It is not a third strength.

    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01_bright.py --root ... --dry
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01_bright.py --root ... --out ...

PROVISIONAL. Nothing here is a pick, a canon filename, or a published frame.
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

# Beat 04's block, verbatim, in the `no ...` form the fence carries. Eight terms.
LIGHT_TERMS = ("dark", "night", "dusk", "sunset", "dim lighting",
               "moody lighting", "low key", "shadows dominant")
LIGHT_CLAUSES = ", ".join("no " + t for t in LIGHT_TERMS) + ", "

# Where the block is inserted: immediately after the fence's last existing `no`
# clause, so it extends the chain the author already wrote rather than opening a
# new one somewhere the negation lifter reads differently.
ANCHOR_CLAUSE = "no night sky, "

ARM = "i35b"          # r8's i35 arm, plus the block. New name: it is not r8-i35.
CANDIDATE_SET = "bright"
TASK = "ep2-b01-brightbase-0811"


def build_fences(r8):
    """(r8 authored, bright authored) — the strip, then the insertion."""
    authored_r8 = r8.strip_height_clause(r8.R7_AUTHORED)
    if authored_r8.count(ANCHOR_CLAUSE) != 1:
        raise ValueError(f"expected exactly 1 {ANCHOR_CLAUSE!r} in the fence, "
                         f"found {authored_r8.count(ANCHOR_CLAUSE)}")
    bright = authored_r8.replace(ANCHOR_CLAUSE, ANCHOR_CLAUSE + LIGHT_CLAUSES, 1)
    return authored_r8, bright


def sidecar(png, *, r8, seed, strength, pos, neg, neg_r8, neg_full, secs, warns,
            shots_sha, pos_tokens, neg_tokens, sold) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by",
             "# render_b01_bright.py on the rtx5090.",
             "# The negative below is what the model actually saw. Before this",
             "# round's one deliberate insertion it was:",
             f"#   {neg_r8}",
             "# The recipe negative before the `tall tree` removal r8 also made:",
             f"#   {neg_full}"]
    lines += [f"#   NEGWARN: {w}" for w in warns]
    body = ["platform: local-gpu (rtx5090)",
            f"model: {r8.BASE}",
            f"model_licence: {r8.LICENCE}",
            f"shot_beat: {r8.BEAT}",
            f"size: {r8.W}x{r8.H}",
            f"steps: {r8.STEPS}",
            f"guidance: {r8.CFG}",
            f"seed: {seed}",
            "seeds_in_batch: 4",
            f"arm: {ARM}",
            "pipeline: img2img",
            f"init_image: {r8.INIT_REL}",
            f"init_sha256: {r8.INIT_SHA}",
            f"strength: {strength}",
            f"task: {TASK}",
            f"render_round: {CANDIDATE_SET}",
            f"candidate_set: {CANDIDATE_SET}-{ARM}",
            f"prompt_source_sha256: {shots_sha}",
            f"positive_clip_tokens: {pos_tokens}",
            f"negative_clip_tokens: {neg_tokens}",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            "positive_identical_to_r8: true",
            f"lighting_terms_added: {', '.join(LIGHT_TERMS)}",
            f"house_terms_sold_to_pay_for_them: {sold or 'none'}",
            "shots_md_edited: false",
            "single_variable: >-",
            block("Eight lighting terms in the SDXL negative, against ledger "
                  "record ep2-b01-r8-sample's i35 arm at the same four seeds, "
                  "the same init and the same strength. The SENT POSITIVE is "
                  "byte-identical to r8's — asserted at render time, not "
                  "claimed — because the terms are authored as `no ...` "
                  "clauses and the negation lifter removes them from the "
                  "positive before the model sees it. Anything different in "
                  "these frames is those eight terms and the budget they cost."),
            "compare_against: >-",
            block("genomes/sapling/nodes/002b-first-citizen/takes/stills/"
                  "01-cold-open-r8-i35-s*.png (ledger ep2-b01-r8-sample), whose "
                  "finding was `right size, wrong light`: the plate's dusk "
                  "palette survived both 0.35 and 0.55 while the t2i control "
                  "rendered the sunrise correctly on 4 of 4."),
            "provisional: >-",
            block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and "
                  "not canon. Ground truth is the founder (R4); he has "
                  "ratified nothing here. Never takes a canon filename, is not "
                  "published, not posted, and not assembled into an episode."),
            "approved: false",
            f"wall_seconds: {secs:.0f}",
            "cost_usd: 0",
            "prompt: |-", block(pos),
            "negative: |-", block(neg)]
    Path(str(png) + ".meta.yaml").write_text("\n".join(lines + body) + "\n",
                                             encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--shots", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--strength", type=float, default=0.35)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)
    # IMPORTED, not copied: every constant that has to match r8 comes from r8's
    # own file, so the two rounds cannot drift into a two-variable comparison.
    import render_b01r8 as r8                                       # noqa: E402

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = Path(a.shots).resolve() if a.shots else node / "shots.md"
    init_path = root / r8.INIT_REL
    out = Path(a.out).resolve() if a.out else Path(__file__).resolve().parent / "out"

    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — this round SELLS house terms to buy the "
              "lighting block, so the count is the whole safety argument and "
              "the estimator is not good enough. Run on the box's venv; "
              "stopping.", flush=True)
        return 8

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[r8.BEAT]

    # trap 1: r8's own staleness guard, unchanged. If the fence on disk is not
    # r7's, then neither r8's strip nor this round's insertion means what it says.
    if s["prompt"] != r8.R7_AUTHORED:
        print("   !! shots.md's beat 01 fence is NOT r7's — a stale checkout or "
              "an edited beat. This round inserts into that exact string.\n"
              f"      on disk: {s['prompt']}\n"
              f"      expected: {r8.R7_AUTHORED}\n   stopping.", flush=True)
        return 4

    authored_r8, authored_b = build_fences(r8)

    def build(authored):
        warns = []
        pos, dropped = compress(authored)
        neg_full = beat_negative(r8.NEG, authored, r8.EXTRA_NEG, warn=warns.append)
        neg, removed = r8.strip_term(neg_full, r8.DROP_NEG)
        return pos, neg, neg_full, dropped, warns, removed

    pos_r8, neg_r8, _, _, _, _ = build(authored_r8)
    pos, neg, neg_full, dropped, warns, removed = build(authored_b)

    print(f"\n== beat {r8.BEAT:02d} {s['slug']} [{CANDIDATE_SET}-{ARM}] "
          f"strength {a.strength}", flush=True)
    print(f"   shots.md: {shots_path}\n   sha256:   {shots_sha}", flush=True)
    print(f"   AUTHORED(bright): {authored_b}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(r8, the control):  {neg_r8}", flush=True)
    print(f"   NEG(sent, this round): {neg}", flush=True)
    pos_tokens, neg_tokens = negative_tokens(pos), negative_tokens(neg)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> sent "
          f"{neg_tokens} (budget 77); r8's sent was "
          f"{negative_tokens(neg_r8)}", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # THE ONE-VARIABLE PROOF. The eight terms are authored as `no ...` clauses so
    # the lifter takes them out of the positive; if any survived into the sent
    # positive this would be a two-channel round and the comparison would be
    # worthless.
    if pos != pos_r8:
        print("   !! SENT POSITIVE DIFFERS FROM r8's. The lighting block is "
              "supposed to leave the positive entirely.\n"
              f"      r8:     {pos_r8}\n      bright: {pos}\n   stopping.",
              flush=True)
        return 20
    sent = [t.strip().lower() for t in neg.split(",")]
    missing_light = [t for t in LIGHT_TERMS if t not in sent]
    if missing_light:
        print(f"   !! LIGHTING TERMS DROPPED BY THE BUDGET: "
              f"{', '.join(missing_light)} — the round's only variable did not "
              f"reach the model; stopping.", flush=True)
        return 21

    # What the block cost. Named here and in every sidecar; this is the price,
    # not a surprise.
    sold = ", ".join(t for t in [x.strip() for x in neg_r8.split(",")]
                     if t.lower() not in sent)
    print(f"   HOUSE TERMS SOLD to pay for the block: {sold or 'none'}",
          flush=True)

    # r8's remaining traps, unchanged in intent.
    if removed != r8.EXPECT_DROP:
        print(f"   !! expected to remove {r8.EXPECT_DROP} x '{r8.DROP_NEG}', "
              f"removed {removed}; stopping.", flush=True)
        return 2
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)}; stopping.",
              flush=True)
        return 3
    missing = [t for t in r8.PERSON_NEG if t not in sent]
    if missing:
        print(f"   !! PERSON TERMS DROPPED by the 77-token budget: "
              f"{', '.join(missing)}; stopping.", flush=True)
        return 9
    if not pos.rstrip().endswith(r8.ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED; stopping.", flush=True)
        return 10
    if not init_path.exists():
        print(f"   !! INIT MISSING: {init_path}; stopping.", flush=True)
        return 11
    init_sha = hashlib.sha256(init_path.read_bytes()).hexdigest()
    print(f"   INIT: {r8.INIT_REL}\n   init sha256: {init_sha}", flush=True)
    if init_sha != r8.INIT_SHA:
        print(f"   !! INIT SHA MISMATCH — expected {r8.INIT_SHA}; stopping.",
              flush=True)
        return 12

    if a.dry:
        print("\nDRY OK — 1 arm x 4 seeds = 4 frames, nothing drawn", flush=True)
        return 0

    out.mkdir(parents=True, exist_ok=True)
    import torch
    from PIL import Image
    from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(
        r8.BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")
    i2i = StableDiffusionXLImg2ImgPipeline.from_pipe(pipe)
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s", flush=True)

    init_img = Image.open(init_path).convert("RGB")
    if init_img.size != (r8.W, r8.H):
        print(f"   init is {init_img.size}, resizing to {(r8.W, r8.H)}", flush=True)
        init_img = init_img.resize((r8.W, r8.H))

    for i in range(4):
        seed = r8.SEED + r8.BEAT + i * 1000          # r8's rule, r8's four seeds
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = i2i(prompt=pos, negative_prompt=neg, image=init_img,
                  strength=a.strength, num_inference_steps=r8.STEPS,
                  guidance_scale=r8.CFG, generator=g).images[0]
        f = out / f"{r8.BEAT:02d}-{s['slug']}-{CANDIDATE_SET}-{ARM}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, r8=r8, seed=seed, strength=a.strength, pos=pos, neg=neg,
                neg_r8=neg_r8, neg_full=neg_full, secs=secs, warns=warns,
                shots_sha=shots_sha, pos_tokens=pos_tokens,
                neg_tokens=neg_tokens, sold=sold)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
