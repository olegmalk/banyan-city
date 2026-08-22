#!/usr/bin/env python3
r"""node 001 beat 05 — THE SAPLING REVEAL. One NEW frame, four seeds. 2026-08-11.

WHAT THIS FRAME IS FOR. Roman, 2026-08-11, verbatim and NOT withdrawn:

    "we should show that he became a sapling earlier in the video just to make
     it less confusing."

The first attempt satisfied that by cutting 1.42s of beat 12's own push-in into
the tail of beat 05 at 0:22. He rejected it, also verbatim:

    "dont show beat 12's picture twice."

So the reveal is currently OUT of the cut with nothing in its place (commit
dc77bc8) and the confusion he named is back. The draft leaf
`leaves/drafts/001-t0-e-draft.yaml` names what closes it under
`what_would_close_it`: "A NEW PLATE — one picture of the sapling that belongs to
beat 05, not borrowed from a later beat." This script draws that picture.

THIS DOES NOT EDIT shots.md AND IT ADDS NO BEAT. The script is untouched:
`node.md` and `001-t0-d.yaml` describe fifteen beats and still do. Beat 05 has
1.42s of unused slot inside its authored 4.00s, which is where the insert lives
with no timing change anywhere. The prompt is therefore NOT canon and is
injected script-side, exactly as render_b06r6/r7/r8 inject theirs — writing an
unapproved picture into shots.md would change the string every other renderer
sends for beat 05, before the author has agreed to a word of it. Beat 05's own
fence (the ceramic shards) is asserted byte-for-byte first, so a stale or
concurrently-edited checkout cannot start.

THE RECIPE IS COPIED, NOT INVENTED. Source: `stills/12-undefined.png`, the
founder's one pick of the 2026-08-08 wave (`takes/stills/12-undefined-r2-s1.png`,
seed 20261731), read out of its own sidecar. Model animagine-xl-3.1, 832x1216,
40 steps, cfg 7.5, bfloat16 on cuda, and the prompt built through the real
`compress()` + `beat_negative()` path with no script-side transform of any kind.
Trap 2 rebuilds beat 12's sent positive AND negative from this checkout and
asserts them byte-for-byte against that sidecar, so "same recipe" is a
measurement rather than a claim. The ONLY things that differ from beat 12 are
the prompt, the seeds and the output names — which is the whole permitted delta.

NO COUNT TAG, AND THAT IS THE CORRECT TAG. `_tag_from_clause` reads the first
comma-clause; this prompt's is `plant focus`, which matches no person pattern,
so the derived tag is "" and none is prepended. That is what beat 12 does and
beat 12 drew no people. The `1other` failure mode is a BARE HUMANOID NOUN
resolving to the indeterminate tag — there is no figure in this frame at all, so
there is nothing to tag. Trap 4 refuses the run if any count tag appears at the
head of the sent positive.

PROHIBITIONS GO IN THE NEGATIVE. The trailing `No …` sentence is not a ban in
the positive: `compress()`'s `_NEGATION` strips it out and `beat_negative()`
imports it into the beat tier. Trap 5 asserts the sent POSITIVE carries no `no `
ban at all, and trap 6 asserts every term the round is for survived the
77-token trim. This is the SDXL side of today's finding — the negative binds
here (beat 03, 4/4) — and it is the opposite of the LTX habit of moving bans
into the positive, which is what put `wobble` in beat 10's binding channel.

WHY THE PICTURE IS DESCRIBED AND NOT DIRECTED. Beat 02 broke today because its
prompt described shots.md's CAMERA DIRECTION while the plate was a different
framing, and the model travelled to the words. There is no plate here to
contradict, but the prompt is still written as a description of the image
wanted — an upright two-leaf sapling seen from ground level with morning sky
behind it — and it names no move, no push-in, no cut.

WHY IT CANNOT READ AS BEAT 12 TWICE. Beat 12 is a sprout BENT LOW into a taut
curve, arched almost horizontal, leaf tips pulled down, in flat sunlit field.
This is the same plant STANDING STRAIGHT, seen from low at ground level against
open sky, in early morning light that cuts into beat 06's morning sky two
seconds later. Opposite posture, different camera height, different light. The
old shape goes into the negative as `bent stem, drooping, wilting`.

FOUR SEEDS IS A ROUND, NOT A RECIPE CHANGE. The house convention. k=8..11 on
this beat's own series (20260719 + beat + k*1000), which cannot collide with
`takes/stills/05-huh-green-s{0..3}.png` at k=0..3; trap 7 checks the directory
rather than trusting the arithmetic. All four go to Roman UNRANKED. Nothing here
ranks, picks, promotes, publishes or spends, and no metric chooses: on beat 14
the flow metric scored highest on the round where the plant falls over.

MEASURE ON THE BOX OR NOT AT ALL. `sd_prompt._token_estimate` falls back to a
prose approximation without `transformers` and over-counts near 77. This script
exits 8 rather than report an estimate as a measurement.

Usage:
    python render_b05reveal.py --root C:\banyan-farm\banyan-city --measure
    python render_b05reveal.py --root C:\banyan-farm\banyan-city --dry
    python render_b05reveal.py --root C:\banyan-farm\banyan-city --out <dir>
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
W, H, STEPS, CFG = 832, 1216, 40, 7.5      # beat 12's, from its own sidecar
BEAT = 5
NODE = "001-capability-inventory"
SET = "reveal-r1"
SLUG = "sapling-reveal"

# This beat's own series, 20260719 + beat + k*1000, at k=8..11. k=0..3 are spent
# on takes/stills/05-huh-green-s{0..3}.png; trap 7 verifies that on disk.
SEEDS = [20268724, 20269724, 20270724, 20271724]

# THE FENCE, BYTE-FOR-BYTE, from shots.md beat 05. NOT edited by this round —
# asserted only, so a stale or concurrently-edited checkout cannot start.
BEAT05_FENCE = (
    "extreme macro close-up of two thick curved glazed ceramic shards lying "
    "flat on dark wooden floorboards, a thin dark spill soaking into the wood "
    "grain, almost no light, deep shadow, one weak cold grey glow from off "
    "frame, cinematic lighting, detailed, newest, masterpiece, best quality, "
    "very aesthetic No intact mug, no whole cup, no handle, no cup shape, no "
    "pink, no magenta, no red, no blood, no bright colours, no window, no "
    "doorway, no room, no furniture, no people, no paper, no cards, no "
    "kintsugi. No photorealism, no 3D render look. 9:16 vertical, no text.")

# THE RECIPE CONTROL. What beat 12 actually sent, read back from
# takes/stills/12-undefined-r2-s1.png.meta.yaml — the frame the founder picked
# on 2026-08-08 and the one promoted to stills/12-undefined.png. Rebuilt from
# this checkout and asserted (trap 2), so "same recipe as beat 12" is measured.
B12_POS_SENT = (
    "plant focus, one tiny two-leaf sprout, its thin green stem bent low into "
    "a taut curve, arched over almost horizontal, leaf tips pulled down near "
    "the grass, damp brown soil, short green grass, sunlit field, pale blue "
    "morning sky, cinematic lighting, detailed, newest, masterpiece, best "
    "quality, very aesthetic")
B12_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, jpeg artifacts, realistic skin "
    "texture, mature tree, large tree, tall tree, thick trunk, full canopy, "
    "forest, bush, shrubbery, humans, cracked ground, dry dirt, grey floor, "
    "upright stem, photorealism")

# THE REVEAL. Written as a description of the IMAGE, in beat 12's own clause
# order (subject, then setting, then the style anchor) and its own dialect. The
# trailing `No …` sentence is harvested into the NEGATIVE by beat_negative();
# trap 5 asserts none of it survives in the positive.
#
# MEASURED, AND TRIMMED ON THE MEASUREMENT. The first wording ran to 78 tokens
# and compress() paid for the overflow with the last sentence — the STYLE
# ANCHOR, `very aesthetic`, which is the one clause that must never be the thing
# that goes (trap 6 caught it and refused to draw). Two clauses were sold to buy
# it back: `both leaves open wide`, which `two-leaf` already says, and `behind
# it`, whose job — sky behind the plant, camera below — is done by `seen from
# low at ground level` beside `pale blue morning sky`. 74 tokens with the anchor
# intact, measured on the box's real CLIP.
AUTHORED = (
    "plant focus, no humans, one small two-leaf sapling standing straight and "
    "upright, its thin green stem rising clear of the grass, seen from low at "
    "ground level, dew on the leaves, short green grass, damp brown soil, pale "
    "blue morning sky, early morning sunlight, cinematic lighting, detailed, "
    "newest, masterpiece, best quality, very aesthetic No bent stem, no "
    "drooping, no wilting, no mature tree, no forest, no flower. No "
    "photorealism, no 3D render look. 9:16 vertical, no text.")

# What this round is FOR. If fit_negative sheds one of these to reach 77 tokens
# the frames would test terms the model never received (trap 6).
REQUIRE_NEG = ("bent stem", "drooping", "wilting", "mature tree", "forest",
               "flower", "humans")
# The posture and the subject. Without them this is not the reveal (trap 3).
REQUIRE_POS = ("plant focus", "sapling", "standing straight", "upright",
               "ground level", "morning")
COUNT_TAGS = ("1boy", "1girl", "1other", "2boys", "2girls", "2others",
              "multiple boys", "multiple girls", "crowd")

NOTE = (
    "THE SAPLING REVEAL — a NEW picture for beat 05, drawn because the founder "
    "asked to see that he had become a sapling earlier (\"we should show that "
    "he became a sapling earlier in the video just to make it less "
    "confusing\", 2026-08-11) and then rejected the only answer available "
    "without a render (\"dont show beat 12's picture twice\", same day). It is "
    "beat 12's plant in the opposite posture: standing straight, seen from low "
    "at ground level against open morning sky, where beat 12 is bent almost "
    "horizontal in flat sunlight. Recipe COPIED from the founder-picked "
    "12-undefined-r2-s1 (model, 832x1216, 40 steps, cfg 7.5) and asserted "
    "against its sidecar in the same run; only the prompt, the seeds and the "
    "output names differ. shots.md NOT edited and no beat added — beat 05's "
    "unused 1.42s holds this with no timing change. Four seeds, UNRANKED, no "
    "pick made, no metric consulted. Not canon, not published, not assembled.")


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, shots_sha: str, pos_tokens: int,
            neg_tokens: int, b12_neg_tokens: int, out_dir: Path, task: str,
            queue_entry: str) -> None:
    """§7.2 provenance, written beside the frame at render time."""
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())

    lines = [
        "# Still provenance (7.2), written AT RENDER TIME by render_b05reveal.py",
        f"# on the rtx5090 ({out_dir}).",
        "# The prompt and negative below are what the model actually saw. They",
        "# are sd_prompt's own output with NO script-side transform: the",
        "# positive is compress(AUTHORED) and the negative is",
        "# beat_negative(house, AUTHORED) — the same code path, unmodified,",
        "# that drew the founder-picked beat 12 frame this recipe is copied",
        "# from. The recipe's negative before fitting was:",
        f"#   NEG(recipe): {neg_full}",
    ]
    lines += [f"#   NEGWARN: {w}" for w in warns]
    body = [
        "platform: local-gpu (rtx5090)",
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
        f"candidate_set: {SET}",
        "founder_direction_verbatim: >-",
        block("we should show that he became a sapling earlier in the video "
              "just to make it less confusing"),
        "founder_rejection_verbatim: >-",
        block("dont show beat 12's picture twice"),
        "founder_direction_date: 2026-08-11",
        "what_this_frame_is: >-",
        block("The reveal the draft leaf 001-t0-e-draft.yaml names under "
              "`what_would_close_it`: one picture of the sapling that belongs "
              "to beat 05 rather than being borrowed from a later beat. It "
              "plays in beat 05's unused 1.42s at roughly 0:22, two seconds "
              "before beat 06's morning sky, which is why the light here is "
              "early morning."),
        "how_it_differs_from_beat_12: >-",
        block("Opposite posture, different camera height, different light. "
              "Beat 12 is a sprout bent low into a taut curve, arched over "
              "almost horizontal, leaf tips pulled down, in a flat sunlit "
              "field. This is the same plant standing straight and upright, "
              "seen from low at ground level with open pale morning sky "
              "behind it. `bent stem`, `drooping` and `wilting` are negated "
              "here precisely so it cannot come back as beat 12's shape."),
        "recipe_copied_from: >-",
        block("takes/stills/12-undefined-r2-s1.png (seed 20261731, round 2), "
              "the founder's pick of 2026-08-08, promoted to "
              "stills/12-undefined.png. Model, size, steps, guidance and the "
              "seed series are that frame's, read out of its own sidecar. Beat "
              "12's sent positive AND negative are rebuilt from this checkout "
              "in this run and asserted byte-for-byte against that sidecar, so "
              "the shared recipe is a measurement and not a claim."),
        "recipe_control_reproduced: true",
        "count_tag: none",
        "count_tag_reason: >-",
        block("_tag_from_clause reads the first comma-clause, which is `plant "
              "focus`; it matches no person pattern, so the derived tag is "
              "empty and none is prepended. That is beat 12's behaviour and "
              "beat 12 drew no people. There is no figure in this frame to "
              "tag — the `1other` failure is a bare humanoid noun resolving to "
              "the indeterminate tag, and no humanoid noun appears. Asserted "
              "at run time (trap 4)."),
        "prohibitions_channel: negative only",
        "prohibitions_note: >-",
        block("The authored `No …` sentence is stripped from the positive by "
              "compress()'s _NEGATION and imported into the negative's beat "
              "tier by beat_negative(). The sent positive carries no `no ` ban "
              "of any kind and this is asserted (trap 5). On SDXL the negative "
              "binds — restoring `text` to beat 03's negative killed the "
              "gibberish glyphs 4 of 4 on 2026-08-11 — so a prohibition "
              "belongs there and nowhere else."),
        f"required_negatives: {', '.join(REQUIRE_NEG)}",
        "required_negatives_survived_trim: true",
        f"shots_md_sha256: {shots_sha}",
        "shots_md_edited: false",
        "script_changed: false",
        "authored_source: >-",
        block("NOT shots.md. This prompt is injected script-side and is not "
              "canon: the founder has not read it, and writing an unapproved "
              "picture into shots.md would change the string every other "
              "renderer sends for beat 05. shots.md beat 05's own fence — the "
              "ceramic shards — is asserted byte-for-byte before a weight "
              "loads and is left exactly as it is."),
        "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
        f"positive_tokens_real_clip: {pos_tokens}",
        f"negative_tokens_real_clip: {neg_tokens}",
        f"negative_tokens_beat12_control: {b12_neg_tokens}",
        "anchor_intact: true",
        "seeds_note: >-",
        block("This beat's own series, 20260719 + beat + k*1000, at k=8..11. "
              "k=0..3 are spent on takes/stills/05-huh-green-s{0..3}.png, so "
              "nothing here overwrites or duplicates a frame already on disk; "
              "checked against the directory at run time, not assumed from the "
              "arithmetic."),
        "unranked: >-",
        block("Four candidates, in seed order, with no preference expressed "
              "anywhere. No pick is made and no metric is consulted: on beat "
              "14 the flow metric scored highest on the round where the plant "
              "falls over. The choice is R4's and only his."),
        "provisional: >-",
        block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and not "
              "canon. Never takes a canon filename, is not published, not "
              "posted, and not assembled into an episode."),
        "approved: false",
        f"wall_seconds: {secs:.0f}",
        "cost_usd: 0",
        "note: |-", block(NOTE),
        "prompt: |-", block(pos),
        "negative: |-", block(neg),
    ]
    png.with_suffix(".png.meta.yaml").write_text(
        "\n".join(lines + body) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print the beat 12 control beside this prompt on the "
                         "box's real tokenizer, draw nothing")
    ap.add_argument("--task", default=None)
    ap.add_argument("--queue-entry", default="none")
    a = ap.parse_args()

    task = a.task or f"001-b05-reveal-{int(time.time())}"
    root = (Path(a.root).resolve() if a.root
            else Path(__file__).resolve().parent.parent)
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes" / NODE
    shots_path = node / "shots.md"
    out = (Path(a.out).resolve() if a.out
           else Path(__file__).resolve().parent / "out")
    out.mkdir(parents=True, exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}

    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts near "
              "the 77 boundary. Run this on the box's venv; stopping.",
              flush=True)
        return 8

    # trap 1: beat 05's fence is what this round expects and this round does not
    # touch it. A concurrently-edited or stale checkout stops here.
    if shots[BEAT]["prompt"] != BEAT05_FENCE:
        print("!! shots.md Beat 05 is not the fence this round was written "
              "against, byte for byte — the checkout is stale or the fence "
              f"moved.\n   expected: {BEAT05_FENCE}\n"
              f"   found:    {shots[BEAT]['prompt']}\n   stopping.", flush=True)
        return 4

    # trap 2: beat 12's recipe must reproduce from THIS checkout, both halves.
    # Without it "the same recipe as the frame he picked" is an assertion.
    c_pos, _ = compress(shots[12]["prompt"])
    c_neg = beat_negative(NEG, shots[12]["prompt"], "", warn=lambda m: None)
    if c_pos != B12_POS_SENT:
        print("!! the beat 12 POSITIVE does not reproduce from this "
              f"checkout.\n   recorded: {B12_POS_SENT}\n"
              f"   rebuilt:  {c_pos}\n   stopping.", flush=True)
        return 5
    if c_neg != B12_NEG_SENT:
        print("!! the beat 12 NEGATIVE does not reproduce from this "
              f"checkout.\n   recorded: {B12_NEG_SENT}\n"
              f"   rebuilt:  {c_neg}\n   stopping.", flush=True)
        return 6

    warns = []
    pos, dropped = compress(AUTHORED)
    neg_full = beat_negative(NEG, AUTHORED, "", warn=warns.append)
    neg = neg_full

    print(f"\n== node {NODE} beat {BEAT:02d} — THE SAPLING REVEAL [{SET}]",
          flush=True)
    print(f"   seeds:    {', '.join(str(x) for x in SEEDS)}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}  (NOT edited by this round)", flush=True)
    print(f"   AUTHORED (script-side, NOT canon): {AUTHORED}", flush=True)
    print(f"   POS(sent):          {pos}", flush=True)
    print(f"   POS(b12 control):   {c_pos}", flush=True)
    print(f"   NEG(sent):          {neg}", flush=True)
    print(f"   NEG(b12 control):   {c_neg}", flush=True)
    print("   trap 1 OK — beat 05 fence unchanged", flush=True)
    print("   trap 2 OK — beat 12 recipe reproduces byte-for-byte, both halves",
          flush=True)

    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    c_neg_tokens = negative_tokens(c_neg)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: {neg_tokens} (budget 77; beat 12 control "
          f"{c_neg_tokens})", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # trap 3: the subject. compress() sheds trailing sentences and clauses to
    # fit 77 tokens, and a shed posture clause would leave a generic plant.
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3
    low_pos = pos.lower()
    miss = [t for t in REQUIRE_POS if t.lower() not in low_pos]
    if miss:
        print(f"   !! POSITIVE IS MISSING {', '.join(miss)} — the reveal is "
              f"defined by them; stopping.", flush=True)
        return 13

    # trap 4: no count tag. `plant focus` derives none; if one appears the
    # clause parser found a figure that should not be in this frame.
    head = pos.split(",")[0].strip().lower()
    if head in COUNT_TAGS:
        print(f"   !! COUNT TAG `{head}` AT THE HEAD of a frame with no figure "
              f"in it. `1other` in particular is the indeterminate-humanoid tag "
              f"three failed rounds came out of; stopping.", flush=True)
        return 15

    # trap 5: prohibitions belong in the negative. On SDXL the negative binds,
    # and a `no …` clause left in the positive is a term the model reads as
    # present. compress() should have moved every one of them.
    stray = [c.strip() for c in pos.split(",")
             if c.strip().lower().startswith("no ")]
    if stray:
        print(f"   !! BANS LEFT IN THE POSITIVE: {', '.join(stray)} — they "
              f"belong in the negative, which binds on this checkpoint; "
              f"stopping.", flush=True)
        return 17

    # trap 6: the anchor, then the terms this round is for.
    if not pos.rstrip().endswith("very aesthetic"):
        print(f"   !! ANCHOR GONE — the sent positive does not end `very "
              f"aesthetic`: …{pos[-60:]!r}; stopping.", flush=True)
        return 7
    sent_neg = {p.strip().lower() for p in neg.split(",")}
    missing = [t for t in REQUIRE_NEG if t.lower() not in sent_neg]
    if missing:
        print(f"   !! TRIMMED AWAY: {', '.join(missing)} — these are what "
              f"stops this frame coming back as beat 12's bent stem. "
              f"fit_negative shed them to fit 77 tokens, so the sheet would "
              f"test terms the model never saw; stopping.", flush=True)
        return 9
    print(f"   traps 3-6 OK — no drop, no count tag, no ban in the positive, "
          f"anchor intact, all {len(REQUIRE_NEG)} required negatives survived",
          flush=True)

    # trap 7: the seeds must be fresh. Read the directory rather than trust the
    # arithmetic — an overwritten take is a comparison destroyed, not a frame.
    takes = node / "takes" / "stills"
    if takes.is_dir():
        spent = set()
        for m in takes.glob(f"{BEAT:02d}-*.png.meta.yaml"):
            for ln in m.read_text(encoding="utf-8").splitlines():
                if ln.startswith("seed:"):
                    spent.add(ln.split(":", 1)[1].strip())
        clash = sorted(set(str(s) for s in SEEDS) & spent)
        if clash:
            print(f"   !! SEEDS ALREADY DRAWN ON THIS BEAT: {', '.join(clash)} "
                  f"— this round would duplicate a frame instead of adding "
                  f"one; stopping.", flush=True)
            return 10
    print("   trap 7 OK — four fresh seeds on this beat's own series",
          flush=True)

    if a.measure:
        print("\nMEASURE OK — nothing drawn", flush=True)
        return 0
    if a.dry:
        print("\nDRY OK — 1 frame x 4 seeds = 4 stills, nothing drawn",
              flush=True)
        return 0

    import torch
    from diffusers import StableDiffusionXLPipeline
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s",
          flush=True)

    for i, seed in enumerate(SEEDS):
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=STEPS,
                   guidance_scale=CFG, generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT:02d}-{SLUG}-{SET}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, shots_sha=shots_sha, pos_tokens=pos_tokens,
                neg_tokens=neg_tokens, b12_neg_tokens=c_neg_tokens,
                out_dir=out, task=task, queue_entry=a.queue_entry)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills — the sapling reveal, unranked", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
