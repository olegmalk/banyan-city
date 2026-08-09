#!/usr/bin/env python3
"""002b beat 13 — ROUND 8, the SPECIES correction. 2026-08-09.

WHY THIS ROUND EXISTS. The founder ruled on the r6 set in one line: "all the
goblin images look like female demihumans, definitely need to regenerate"
(taste ledger records 32 and 33). Set against the script's own noun — "A small
round goblin — enormous ears, one broken tusk, faded green patchwork cloak" —
that sentence names four axes and they are this round's target: MALE, ROUND,
GREEN-SKINNED, and NOT AN ELF.

THIS IS THE r6 BRANCH, AND THAT IS FORCED RATHER THAN PREFERRED. Record 34 ruled
that G1 — "staged on, CONDITIONED ON, or demonstrated with a still that is
REVOKED or was never approved" — fails every frame the regional IP-Adapter (r7,
§3.3) produces, because it conditions on `13-the-shade-r6-s2`, which he has now
rejected along with the rest of the set. The same bar disqualifies §3.2's
two-pass inpaint, which would need an approved plate that does not exist. The
only admissible branch is the one that draws from text alone, and §3.1 is the
reason it is worth taking: the vocabulary correction is the only move that has
ever shifted a predicate on this beat, and it shifted three at once.

THE MECHANISM IS MEASURED FROM THE CORPUS, not from our own frames. Danbooru
post counts, read 2026-08-09:

    goblin          4,257   "child-sized, with green skin, fangs, pointy noses,
                            and pointy ears" — the show's goblin IS the canonical one
    female goblin   1,717   IMPLICATES `goblin` — 40.3% of everything carrying
                            the token `goblin` is female
    elf           111,449   "grace, finesse, and youthful appearance"; implies
                            `pointy ears`. Outweighs `goblin` 26 to 1
    green skin     30,541   implicates `colored skin`; "often associated with orcs"
    plump          43,371   "slightly chubby, but not enough to be fat"
    fat            19,390   "chubbier than plump" — overshoots the script's "round"

Two in five posts carrying the token `goblin` are tagged `female goblin`, and
because the child tag implicates the parent, every one of them trained the word
`goblin` on a female demihuman. His complaint is not a mis-render; it is the
corpus, sampled faithfully. The elf is the same story one step up. NEITHER TAG
NAME HAS EVER BEEN IN A NEGATIVE ON THIS BEAT — the same class of gap §1b found
for the fusion classes, which is the gap r6 closed to take P1/P3/P4 to 4/4.

WHAT CHANGES, exactly one axis — the species/build assertion, said in the
checkpoint's own vocabulary. Both halves are that one axis:
(1) POSITIVE: the prose word `round` gives way to the tag `plump`, and the tag
    `green skin` is added. `green skin` is the attribute P2 turns on, and record
    34 filed it as the next candidate after r7 failed to transfer it from an
    image. The plant sentence and the style tail are r6's byte-for-byte, because
    P1/P3/P4 are at 4/4 and this round must not touch them.
(2) NEGATIVE: `female goblin` and `elf` join r6's nine fusion tags in the
    `explicit` tier, where `fit_negative` protects them last.

`1boy` IS NOT THE FAULT AND IT STAYS. The suspicion was that it pulls the
pretty-boy/elf reading; it does not survive the code. `_tag_from_clause` tests
`_MALE` before `_OTHER`, so removing "boy" does not give a neutral prompt — it
gives `1other` back, the tag §1a proved asserts a humanoid of indeterminate
gender and which cost r3-r5 three rounds at 0/4. The measured female mass is
inside `goblin`, not inside `1boy`. `monster boy` was considered and rejected on
its definition, not on taste: it denotes "a bishounen or ikemen mixed with a
monster" — it names the pretty-boy failure rather than curing it.

THE BUDGET DECIDED HOW MUCH VOCABULARY FITS, measured on the REAL CLIP tokenizer
before a step was spent (transformers 4.44.2, openai/clip-vit-large-patch14):

    r6 fence (control)                72 tokens   anchor INTACT
    r8, green skin + plump            77 tokens   anchor INTACT
    green skin only                   75 tokens   anchor INTACT
    green skin + colored skin         62 tokens   anchor DROPPED
    green skin + plump + male focus   62 tokens   anchor DROPPED

Every variant carrying three or more species tags comes back with the style
anchor deleted — `compress()` sheds the trailing sentence to reach 77, and that
sentence carries `masterpiece, best quality, very aesthetic`. That is the r4
defect this beat already paid for once, so it is a hard stop and not a trade.
Two tags is what the budget buys; `colored skin`, `male focus` and `pointy ears`
are FILED, NOT BUNDLED — and `pointy ears` would in any case be arguing for the
elf, which implies it.

THE ANCHOR ASSERTION BELOW IS NEW IN r8 AND IT IS WHY. r6 asserted the count
tag, the fusion negatives and the absence of positive drops, but never that the
style anchor survived — it did not have to, at 72 tokens with five to spare. r8
sits at exactly 77 of 77. There is no headroom left, so the thing that silently
breaks first is now checked explicitly rather than trusted.

THE KNOWN RISK, STATED IN ADVANCE. `elf` implies `pointy ears`, and the Danbooru
goblin has pointy ears, so negating `elf` may cost the ears this creature is
supposed to have. If r8 comes back green and plump with small round human ears,
THAT is the trade, and `pointy ears` is the next positive tag to buy — which is
also the round that would need something cut to pay for it.

Seeds are r4/r5/r6/r7's own four (20260719 + 13 + k*1000, k=0..3), so the column
stays a controlled comparison all the way down.

    python render_b13r8.py --root C:\\banyan-farm\\banyan-city --dry
    python render_b13r8.py --root C:\\banyan-farm\\banyan-city
"""
import argparse
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
QUEUE_ENTRY = "ep2-b13-r8-goblin-1786292421"
TASK = "ep2-b13-r8-goblin-1786292421"
BEAT = 13
EXPECT_DROP = 1  # `tiny`, `40cm`, `seedling` all fire _SMALL
EXPECT_TAG = "1boy"
# r6's nine fusion tags, UNCHANGED, plus the two species tags this round buys.
# `female goblin` and `elf` are the exact Danbooru names of what he rejected.
EXTRA_NEG = ("leaf on head, plant girl, alraune, monster girl, flower on head, "
             "head wreath, hair ornament, leaf hair ornament, plant hair, "
             "female goblin, elf")
# the round-8 leading clause; a stale checkout must not render r6's wording again
EXPECT_PREFIX = "a small goblin boy"
# the style anchor. r8 sits at exactly 77/77, so this is checked, not assumed.
ANCHOR = ("Midday light, cinematic lighting, detailed, newest, masterpiece, "
          "best quality, very aesthetic")

NOTE = ('round 8, the SPECIES correction, and the founder ordered it: "all the '
        'goblin images look like female demihumans, definitely need to '
        'regenerate" (taste ledger records 32 and 33), set against the script\'s '
        'own noun, "a small round goblin". Four axes fall out of that sentence — '
        'male, round, green-skinned, not an elf. This is the r6 text-only branch '
        'and that is forced: record 34 ruled G1 fails every frame the regional '
        'IP-Adapter (r7) produces, because it conditions on 13-the-shade-r6-s2, '
        'which he rejected; the same bar disqualifies the two-pass inpaint, which '
        'needs an approved plate that does not exist. The mechanism is measured '
        'from the Danbooru corpus rather than from our own frames: `female '
        'goblin` is 1,717 posts of `goblin`\'s 4,257 and IMPLICATES it, so 40.3% '
        'of everything carrying the token `goblin` is female — his complaint is '
        'the corpus sampled faithfully, not a mis-render — and `elf` outweighs '
        '`goblin` 111,449 to 4,257 while implying `pointy ears`. Neither tag name '
        'had ever been in a negative on this beat, the same class of gap that '
        'r6 closed for the fusion classes to take P1/P3/P4 from 0/4 to 4/4. '
        'Exactly one axis moves, the species/build assertion in the checkpoint\'s '
        'own vocabulary: positive, the prose word `round` gives way to the tag '
        '`plump` and the tag `green skin` is added (the attribute P2 turns on, '
        'filed by record 34 after r7 failed to transfer it from an image); '
        'negative, `female goblin` and `elf` join r6\'s nine fusion tags in the '
        'explicit tier that fit_negative protects last. The plant sentence and '
        'the style tail are r6\'s byte-for-byte because P1/P3/P4 are at 4/4 and '
        'this round must not touch them. `1boy` stays and was checked rather than '
        'assumed: _tag_from_clause tests _MALE before _OTHER, so deleting "boy" '
        'returns `1other`, the indeterminate-humanoid tag that cost r3-r5 three '
        'rounds at 0/4; the female mass is measured to be inside `goblin`, not '
        'inside `1boy`. `monster boy` was rejected on its definition — "a '
        'bishounen or ikemen mixed with a monster" names the pretty-boy failure '
        'rather than curing it. The budget decided how much vocabulary fits and '
        'it was measured on the real CLIP tokenizer before a step was spent: r6 '
        'control 72 tokens anchor intact, this round 77 anchor intact, but every '
        'variant with three or more species tags (green skin + colored skin, '
        'green skin + plump + male focus) came back at 62 WITH THE STYLE ANCHOR '
        'DELETED — the r4 defect this beat already paid for once, so a hard stop '
        'and not a trade. `colored skin`, `male focus` and `pointy ears` are '
        'filed, not bundled. Because 77 of 77 leaves no headroom, this script '
        'asserts the anchor survived, which r6 never had to. Stated risk: `elf` '
        'implies `pointy ears` and the Danbooru goblin has them, so negating elf '
        'may cost the ears — if r8 comes back green and plump with small round '
        'human ears, that is the trade and `pointy ears` is the next tag to buy. '
        'Same four seeds as r4-r7, a controlled column. Pre-registered gate: the '
        'memo\'s four predicates plus the two his verdict added — P1 plant is a '
        'plant, P2 goblin is a goblin, P3 no fusion, P4 two silhouettes, P5 not '
        'female, P6 not an elf; pass = at least 3 of 4 seeds passing ALL SIX. But '
        'record 32 ruled "P2 is not a valid gate until he defines the goblin, and '
        'no r8 may be scored against the old one", so this round is NOT a gate '
        'attempt: it exists to give him something to define the goblin with. '
        'Ledger record written BEFORE the sheet. No wave fires off this beat '
        'without the founder, and nothing goes on his screen tonight.')


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, task: str) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b13r8.py",
             "# on the rtx5090 (C:\\banyan-farm\\sample-b13-r8).",
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
            f"count_tag: {EXPECT_TAG}",
            "extra_negative_tier: explicit",
            "extra_negative: >-",
            block(EXTRA_NEG),
            "provisional: true",
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 6, takes/stills/13-the-shade-r6-s*.png — model, size, "
                  "steps, cfg, seed rule, the one-term negative removal, the "
                  "plant sentence and the style tail are r6's unchanged. r6 in "
                  "turn inherited them from node 001 "
                  "takes/stills/15-something-s-coming-r3-s1.png, the ONE SAMPLE "
                  "the founder passed on 2026-08-08. NOT inherited from r7: that "
                  "branch conditions on a still the founder rejected and record "
                  "34 ruled every frame it produces inadmissible under G1."),
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import beat_negative, compress, negative_tokens  # noqa: E402

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    shots = {s["num"]: s for s in
             parse_shots((node / "shots.md").read_text(encoding="utf-8"))}
    s = shots[BEAT]
    authored = s["prompt"]
    if not authored.strip().lower().startswith(EXPECT_PREFIX):
        print(f"!! shots.md Beat 13 does not carry the round-8 leading clause "
              f"(`{EXPECT_PREFIX}`) — the checkout is stale and this would render "
              f"r6's wording again; stopping.", flush=True)
        return 4
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, EXTRA_NEG, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)

    print(f"\n== beat 13 {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {SEED + BEAT}..{SEED + BEAT + 3000}", flush=True)
    print(f"   AUTHORED: {authored}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(recipe): {neg_full}", flush=True)
    print(f"   NEG(sent):   {neg}", flush=True)
    print(f"   positive tokens: {negative_tokens(pos)} (budget 77)", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {negative_tokens(neg)} (budget 77)", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # trap 1: read the count tag off the real path and confirm it BEFORE spending
    # a step. r6 bought this tag and r8 must not lose it by accident.
    if not pos.startswith(EXPECT_TAG + ","):
        print(f"   !! COUNT TAG is not `{EXPECT_TAG}` — POS opens `{pos[:40]}`. "
              f"Deleting the male token would hand back `1other`; stopping.",
              flush=True)
        return 5
    # trap 2: fit_negative must sacrifice house boilerplate, never these eleven.
    missing = [t.strip() for t in EXTRA_NEG.split(",")
               if t.strip().lower() not in
               [p.strip().lower() for p in neg.split(",")]]
    if missing:
        print(f"   !! EXPLICIT NEGATIVES DROPPED by the 77-token budget: "
              f"{', '.join(missing)} — that is what this round buys; stopping.",
              flush=True)
        return 6
    # trap 3, NEW IN r8: the positive sits at 77 of 77, so the style anchor is the
    # thing that silently disappears first. r4 shipped without it once already.
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`. compress() shed the trailing sentence to reach 77, "
              f"which is the r4 defect; stopping.", flush=True)
        return 7
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
        f = out / f"13-{s['slug']}-{CANDIDATE_SET}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, task=TASK)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
