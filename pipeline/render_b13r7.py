#!/usr/bin/env python3
"""002b beat 13 — ROUND 7, REGIONAL IP-ADAPTER for the goblin's identity. 2026-08-09.

WHY THIS ROUND EXISTS, and why it was chosen before the last one was scored.
`pipeline/research/two-subject-composition.md` fixed the ladder in advance so the
next step would not be picked by whoever was disappointed:

    "r6 fails on P2 (goblin off-model / a human) -> §3.3, regional IP-Adapter on
     the 5090 box, conditioning the goblin region on an approved goblin still.
     That is an A1 problem and IP-Adapter is the A1 tool."

r6 (ledger record 32) failed exactly there. Its vocabulary correction took the
plant predicates from 0/4 to 4/4 — P1 plant-is-a-plant, P3 no-fusion, P4
two-silhouettes all clean — and the pre-registered gate still failed at 1 of 4,
because P2 did not move: `goblin` loses to `1boy` in three seeds and the frame
comes back a pale elf child. Seed s2 is the exception and the reason this round
is conditioning and not another prompt: it is green-skinned with long pointed
ears and a grey cloak, the closest thing to this show's goblin yet drawn. The tag
CAN win. It needs evidence, not more adjectives.

WHAT CHANGES, exactly one thing. The r6 prompt is inherited BYTE-FOR-BYTE — same
shots.md text, same count tag, same nine fusion negatives, same four seeds — and
an IP-Adapter is added, masked to the character's region only:

  * the reference is r6 s2, cropped to the goblin. CLIP encodes the whole
    reference, and that frame carries three seedlings of its own; uncropped it
    would push plant evidence into the character's region, which is the fusion r6
    just cleared.
  * the mask is a box over where the character's head and torso land in the r6
    frames — the identity cues P2 scores are all head-and-shoulders. Both side
    bands and the bottom strip stay unmasked, so the plant is still drawn by the
    text prompt alone. The plant predicates are at 4/4 and this round must not
    touch them.

DELIBERATELY NOT BUNDLED: two-pass inpaint (§3.2, the remaining branch if this
fails), Bounded Attention (§3.6), checkpoint swap (§3.8). One axis per sample.

THE REFERENCE IS PROVISIONAL AND THE STEWARD PICKED IT, recorded as ledger record
33. It is the only frame in r6 that scored P2 pass; the founder may flip it to a
different goblin at the cost of one re-run, because nothing else in the recipe
depends on which frame it is.

    python render_b13r7.py --root C:\\banyan-farm\\banyan-city --dry
    python render_b13r7.py --root C:\\banyan-farm\\banyan-city --smoke
    python render_b13r7.py --root C:\\banyan-farm\\banyan-city
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

# ---- inherited from r6, unchanged. Any drift here breaks the controlled pair.
NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
       "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
       "realistic skin texture")
BASE = "cagliostrolab/animagine-xl-3.1"
LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"
SEED = 20260719
W, H, STEPS, CFG = 832, 1216, 40, 7.5
DROP_NEG = "tall tree"
BEAT = 13
EXPECT_DROP = 1
EXPECT_TAG = "1boy"
EXTRA_NEG = ("leaf on head, plant girl, alraune, monster girl, flower on head, "
             "head wreath, hair ornament, leaf hair ornament, plant hair")
EXPECT_PREFIX = "a small round goblin boy"
# The exact strings r6 sent, copied from 13-the-shade-r6-s2.png.meta.yaml. r7's
# whole claim is that only the conditioning changed, so the prompt is checked
# against the record rather than assumed. This also catches the environment
# difference that would otherwise pass silently: without a CLIP tokenizer
# installed, `fit_negative` estimates, over-trims, and sends a different
# negative — ten house terms dropped instead of r6's seven.
EXPECT_POS = ("1boy, a small round goblin boy, solo, folds into a thin patch of shade, "
              "knees up around his ears. Plant, grass, outdoors, a tiny 40cm seedling "
              "with two oversized cotyledon leaves rooted in the ground beside him. "
              "Midday light, cinematic lighting, detailed, newest, masterpiece, "
              "best quality, very aesthetic")
EXPECT_NEG = ("photorealistic, 3d render, abstract, text, watermark, mature tree, "
              "large tree, thick trunk, full canopy, forest, bush, shrubbery, girl, "
              "child, photorealism, leaf on head, plant girl, alraune, monster girl, "
              "flower on head, head wreath, hair ornament, leaf hair ornament, "
              "plant hair")

# ---- the one thing round 7 adds.
CANDIDATE_SET = "r7"
QUEUE_ENTRY = "ep2-b13-shade-r7-regional-ipadapter-1786320000"
IP_REPO = "h94/IP-Adapter"
IP_LICENCE = "Apache-2.0 (h94/IP-Adapter; claims nothing over output)"
IP_SUBFOLDER = "sdxl_models"
IP_WEIGHT = "ip-adapter_sdxl_vit-h.safetensors"
IP_ENCODER_FOLDER = "models/image_encoder"
IP_SCALE = 0.6
# r6 s2, the only frame that scored P2 pass. Identified by bytes, not by name:
# the stills are gitignored, so a path alone would not say which picture this was.
REF_REL = "genomes/sapling/nodes/002b-first-citizen/takes/stills/13-the-shade-r6-s2.png"
REF_SHA256 = "89310f55aa56c23d281852631260ffbfdc1686137287234007bc1309a948f1f1"
# Where the goblin is in the reference: ears to boots, corner seedlings excluded.
CROP_BOX = (0.16, 0.06, 0.90, 0.88)
# Where the character's identity lands in the r6 frames. Measured off r6 s0 and
# s2: head spans x 0.17-0.84, y 0.06-0.50 in both. The margins are the plant's.
MASK_BOX = (0.18, 0.02, 0.88, 0.78)
MASK_FEATHER = 24
# A "regional" adapter that covers the frame is a global one wearing the name.
MAX_COVERAGE = 0.75
MIN_SIDE_BAND = 0.08

NOTE = ('round 7, REGIONAL IP-ADAPTER, specified by '
        'pipeline/research/two-subject-composition.md §3.3 and selected by the '
        'ladder that memo fixed in advance for this exact branch: "r6 fails on P2 '
        '(goblin off-model / a human) -> §3.3, regional IP-Adapter on the 5090 '
        'box, conditioning the goblin region on an approved goblin still. That is '
        'an A1 problem and IP-Adapter is the A1 tool." r6 (ledger record 32) took '
        'the plant predicates from 0/4 to 4/4 — no frame wears a leaf, grows a '
        'cotyledon out of its head, or collapses the two nouns — and still failed '
        'its gate at 1 of 4, because P2 did not move: `goblin` loses to `1boy` and '
        'three seeds came back as a pale elf child. Seed s2 is why this round is '
        'conditioning rather than more adjectives — green skin, long pointed ears, '
        'grey cloak, the closest thing to this show\'s goblin yet drawn — so the '
        'tag can win and what it needs is evidence. EXACTLY ONE THING CHANGES. The '
        'r6 prompt is inherited byte-for-byte, same count tag, same nine fusion '
        'negatives, same four seeds, and an IP-Adapter is added masked to the '
        'character region only. The reference is r6 s2 CROPPED to the goblin: CLIP '
        'encodes the whole reference and that frame carries three seedlings of its '
        'own, so uncropped it would push plant evidence into the character region '
        'and re-open the fusion r6 just closed. The mask is a box over where the '
        'head and torso land in the r6 frames — every cue P2 scores is '
        'head-and-shoulders — with both side bands and the bottom strip left '
        'unmasked so the plant is still drawn by text alone, because the plant '
        'predicates are at 4/4 and this round must not touch them. The reference '
        'pick is PROVISIONAL and the steward\'s, recorded as ledger record 33; the '
        'founder may flip it to a different goblin at the cost of one re-run, '
        'since nothing else in the recipe depends on which frame it is. '
        'Pre-registered gate, unchanged from r6 (memo §5): four binary predicates '
        'per seed — plant is a plant, goblin is a goblin, no fusion, two separate '
        'silhouettes — and a pass is at least 3 of 4 seeds passing all four. '
        'Ledger record written BEFORE any screen. No wave fires off this beat '
        'without the founder.')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, task: str, ref_sha: str,
            mask_desc: str, crop_desc: str, crop_px) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b13r7.py",
             "# on the rtx5090 (C:\\banyan-farm\\sample-b13-r7).",
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
            "conditioning: regional-ip-adapter",
            f"ip_adapter_repo: {IP_REPO}",
            f"ip_adapter_weight: {IP_SUBFOLDER}/{IP_WEIGHT}",
            f"ip_adapter_image_encoder: {IP_ENCODER_FOLDER}",
            f"ip_adapter_licence: {IP_LICENCE}",
            f"ip_adapter_scale: {IP_SCALE}",
            f"ip_adapter_reference: {REF_REL}",
            f"ip_adapter_reference_sha256: {ref_sha}",
            f"ip_adapter_reference_crop: {crop_desc}",
            f"ip_adapter_reference_crop_px: {crop_px[0]},{crop_px[1]},{crop_px[2]},{crop_px[3]}",
            f"ip_adapter_mask: {mask_desc}",
            f"ip_adapter_mask_feather_px: {MASK_FEATHER}",
            "ip_adapter_reference_status: >-",
            block("PROVISIONAL, picked by the steward, ledger record 33. It is the "
                  "only frame in r6 that scored P2 (goblin-is-a-goblin) pass. The "
                  "founder has not ruled on it; flipping it to a different goblin "
                  "costs one re-run and nothing else in the recipe depends on "
                  "which frame it is."),
            "recipe_inherited_from: >-",
            block("node 002b, takes/stills/13-the-shade-r6-s2.png and its sidecar "
                  "— round 6, the ONE SAMPLE of 2026-08-09 (ledger record 32). "
                  "Prompt, negative, count tag, fusion negatives, model, size, "
                  "steps, cfg and all four seeds are inherited from it unchanged, "
                  "so r7 is a controlled comparison against a recorded 1-of-4. The "
                  "only difference is the regional IP-Adapter, which "
                  "pipeline/research/two-subject-composition.md §3.3 specifies and "
                  "the memo's ladder selected in advance for a P2 failure."),
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
    ap.add_argument("--reference", default=None,
                    help="override the reference PNG path; the sha256 is checked either way")
    ap.add_argument("--dry", action="store_true",
                    help="prompt, geometry and reference checks only — nothing drawn")
    ap.add_argument("--smoke", action="store_true",
                    help="two steps at half size, one seed, into smoke/ — proves the "
                         "masked-adapter plumbing without spending the sample")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (_clip_tokenizer, beat_negative, compress,  # noqa: E402
                           negative_tokens)
    import regional_ip as rip                                       # noqa: E402

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    out = Path(__file__).resolve().parent / "out"
    task = f"ep2-b13-r7-{int(time.time())}"

    shots = {s["num"]: s for s in
             parse_shots((node / "shots.md").read_text(encoding="utf-8"))}
    s = shots[BEAT]
    authored = s["prompt"]
    if not authored.strip().lower().startswith(EXPECT_PREFIX):
        print(f"!! shots.md Beat 13 does not carry the round-6 leading clause "
              f"(`{EXPECT_PREFIX}`) — the checkout is stale and r7 would not be a "
              f"controlled comparison against r6; stopping.", flush=True)
        return 4
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, EXTRA_NEG, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)

    print(f"\n== beat 13 {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {SEED + BEAT}..{SEED + BEAT + 3000}", flush=True)
    print(f"   AUTHORED: {authored}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(sent):   {neg}", flush=True)
    print(f"   positive tokens (comparison counter): {negative_tokens(pos)}",
          flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {negative_tokens(neg)} (budget 77)", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # The r6 guards, kept verbatim. r7 inherits that prompt, so if any of them
    # would fire now, the two rounds are not the controlled pair they claim.
    if not pos.startswith(EXPECT_TAG + ","):
        print(f"   !! COUNT TAG is not `{EXPECT_TAG}` — POS opens `{pos[:40]}`; "
              f"stopping.", flush=True)
        return 5
    missing = [t.strip() for t in EXTRA_NEG.split(",")
               if t.strip().lower() not in
               [p.strip().lower() for p in neg.split(",")]]
    if missing:
        print(f"   !! FUSION NEGATIVES DROPPED by the 77-token budget: "
              f"{', '.join(missing)}; stopping.", flush=True)
        return 6
    if removed != EXPECT_DROP:
        print(f"   !! EXPECTED to remove {EXPECT_DROP} x '{DROP_NEG}', removed "
              f"{removed} — stopping so a human decides.", flush=True)
        return 2
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3
    # r7 claims to change the conditioning and nothing else. That claim is only
    # worth anything if the text really is r6's, so it is checked against r6's
    # own sidecar rather than trusted.
    if pos != EXPECT_POS:
        print(f"   !! POSITIVE IS NOT THE ONE r6 SENT, so r7 would not be a "
              f"controlled comparison.\n      r6:  {EXPECT_POS}\n      now: {pos}\n"
              f"      Stopping.", flush=True)
        return 11
    if neg != EXPECT_NEG:
        note = ("" if _clip_tokenizer() is not None else
                "\n      No CLIP tokenizer is installed here, so fit_negative "
                "ESTIMATED the budget and trimmed more house terms than r6 lost. "
                "This check is why r7 renders on the box and not wherever it is "
                "invoked.")
        print(f"   !! NEGATIVE IS NOT THE ONE r6 SENT.\n      r6:  {EXPECT_NEG}\n"
              f"      now: {neg}{note}\n      Stopping.", flush=True)
        return 12

    # ---- the round-7 half: reference identity, then region geometry.
    ref = Path(a.reference).resolve() if a.reference else (root / REF_REL)
    if not ref.is_file():
        print(f"   !! REFERENCE MISSING at {ref} — the stills are gitignored, so a "
              f"fresh checkout will not have it; copy it to the box or pass "
              f"--reference. Stopping.", flush=True)
        return 7
    ref_sha = sha256_file(ref)
    if ref_sha != REF_SHA256:
        print(f"   !! REFERENCE IS NOT THE FRAME THIS ROUND RECORDS. Expected "
              f"sha256 {REF_SHA256}, got {ref_sha} for {ref}. The whole round is "
              f"which goblin conditions the region; stopping.", flush=True)
        return 8
    cov = rip.coverage(MASK_BOX)
    left, right, top, bottom = rip.side_bands(MASK_BOX)
    print(f"   REFERENCE: {ref} sha256 {ref_sha[:16]}… (r6 s2, provisional)",
          flush=True)
    print(f"   CROP: {rip.describe(CROP_BOX)}", flush=True)
    print(f"   MASK: {rip.describe(MASK_BOX)} feather {MASK_FEATHER}px", flush=True)
    print(f"   IP-ADAPTER: {IP_REPO} {IP_SUBFOLDER}/{IP_WEIGHT} "
          f"encoder {IP_ENCODER_FOLDER} scale {IP_SCALE}", flush=True)
    if cov > MAX_COVERAGE:
        print(f"   !! MASK COVERS {cov * 100:.0f}% OF THE FRAME (ceiling "
              f"{MAX_COVERAGE * 100:.0f}%) — that is a global IP-Adapter wearing a "
              f"mask's name, and it would condition the plant this round must not "
              f"touch; stopping.", flush=True)
        return 9
    if min(left, right) < MIN_SIDE_BAND:
        print(f"   !! NO ROOM LEFT FOR THE PLANT: side bands L{left * 100:.0f}% "
              f"R{right * 100:.0f}%, floor {MIN_SIDE_BAND * 100:.0f}%; stopping.",
              flush=True)
        return 10

    from PIL import Image
    ref_img = Image.open(ref).convert("RGB")
    crop = rip.crop_reference(ref_img, CROP_BOX)
    crop_px = rip.box_to_pixels(CROP_BOX, ref_img.width, ref_img.height)
    mask = rip.region_mask(W, H, MASK_BOX, feather=MASK_FEATHER)
    print(f"   reference {ref_img.size} -> crop {crop.size}, mask {mask.size}",
          flush=True)

    if a.dry:
        print("\nDRY OK — prompt, reference and geometry all check out; "
              "1 beat x 4 seeds = 4 frames, nothing drawn", flush=True)
        return 0

    import torch
    from diffusers import StableDiffusionXLPipeline
    from diffusers.image_processor import IPAdapterMaskProcessor
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(BASE, torch_dtype=torch.bfloat16,
                                                     use_safetensors=True)
    pipe.to("cuda")
    # In this order because `load_ip_adapter` casts the image encoder with
    # `.to(self.device, dtype=self.dtype)` as it loads: on a pipeline already on
    # the card that lands it on the card, in one move. It takes no `torch_dtype`
    # — the pipeline's own dtype is what it follows.
    pipe.load_ip_adapter(IP_REPO, subfolder=IP_SUBFOLDER, weight_name=IP_WEIGHT,
                         image_encoder_folder=IP_ENCODER_FOLDER)
    pipe.set_ip_adapter_scale(IP_SCALE)
    print(f"MODEL_LOADED cuda/bfloat16 + ip-adapter in {time.time() - t_load:.0f}s",
          flush=True)

    width, height = (W, H) if not a.smoke else (512, 768)
    steps = STEPS if not a.smoke else 2
    proc = IPAdapterMaskProcessor()
    m = proc.preprocess([rip.region_mask(width, height, MASK_BOX,
                                         feather=MASK_FEATHER)],
                        height=height, width=width)
    # One adapter, one image: diffusers wants one entry per adapter, shaped
    # (batch, images_for_this_adapter, h, w). Printed, because a silently wrong
    # shape here is a mask that conditions everything or nothing.
    masks = [m.reshape(1, m.shape[0], m.shape[2], m.shape[3])]
    print(f"MASK_TENSOR preprocess {tuple(m.shape)} -> passed "
          f"{tuple(masks[0].shape)}", flush=True)

    n = 1 if a.smoke else 4
    dest = (Path(__file__).resolve().parent / "smoke") if a.smoke else out
    dest.mkdir(exist_ok=True)
    for i in range(n):
        seed = SEED + BEAT + i * 1000
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=steps,
                   guidance_scale=CFG, generator=g, width=width, height=height,
                   ip_adapter_image=crop,
                   cross_attention_kwargs={"ip_adapter_masks": masks}).images[0]
        secs = time.time() - t0
        if a.smoke:
            f = dest / "smoke-b13-r7.png"
            img.save(f)
            print(f"\nSMOKE OK — masked adapter ran end to end, {f.name} "
                  f"{img.size} in {secs:.0f}s. Two steps: this is noise, not a "
                  f"sample. Nothing scored, nothing published.", flush=True)
            return 0
        f = dest / f"13-{s['slug']}-{CANDIDATE_SET}-s{i}.png"
        img.save(f)
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, task=task, ref_sha=ref_sha,
                mask_desc=rip.describe(MASK_BOX), crop_desc=rip.describe(CROP_BOX),
                crop_px=crop_px)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
