"""002b goblin, beat 04 — ONE SAMPLE of a CONSISTENCY MECHANISM, not of a goblin.

WHAT WAS WRONG. The wave-1 sample (commit 406909c) drew beat 04 with four seeds
against the founder's definition and came back "green four times, tusked three
times, and four different creatures". Green and tusked are prompt-level
attributes and the prompt delivered them. IDENTITY is not a prompt-level
attribute: with text conditioning alone, the seed picks the creature, so four
seeds pick four creatures. A fifteen-beat wave in which the goblin is a
different animal every beat is broken regardless of anyone's taste, which is
why this is a defect and not a question for R4.

WHAT THIS CHANGES — EXACTLY ONE THING. Same beat (04), same four seeds, same
prompt string built by the same `render_wave_goblin.check()` from the same
drafts file, same goblin definition `green skin, tusks`, same steps, guidance,
size and negative. The only difference is that the UNet also sees an image
through IP-Adapter Plus (h94/IP-Adapter, Apache-2.0, `sdxl_models/
ip-adapter-plus_sdxl_vit-h.safetensors` + `models/image_encoder`, both already
in the box HF cache — nothing downloaded, nothing spent).

WHY IP-ADAPTER AND NOT MORE TAGS. Tag-piling is the other obvious fix and it
costs prompt tokens: beat 08 of this wave has 9 tokens of headroom on the real
CLIP tokenizer, and compress() drops TRAILING sentences, so an overrun comes
back unstyled rather than truncated. IP-Adapter adds ZERO tokens. It also does
not elaborate the character in words, which is the only mechanism here that
does not argue with the founder's "nothing complex".

WHY FOUR REFERENCES AND NOT ONE. Picking one canonical goblin is R4's call and
this file does not make it. Every one of the four wave-1 frames is used as the
reference in turn, so the number this produces is a property of the MECHANISM,
not an endorsement of a creature. The headline arm is all four references at
scale 0.6; a 0.4/0.8 sweep on one reference follows, so the knob is measured
rather than asserted.

WHAT THIS SAMPLE CANNOT SHOW. Beat 04 is a face-filling close-up and so are all
four references. Agreement here cannot distinguish "holds the character" from
"copies the picture". Telling those apart needs a beat with a different
composition, and the other fourteen beats stay staged pending the founder's
look — so that is the NEXT sample, named here rather than quietly assumed.

  python goblin_ipa_sample.py --harness C:\\banyan-farm\\wave-goblin-prep
      --root <repo> --refs C:\\banyan-farm\\wave-goblin-prep\\out
      --out <dir> --task <id>

$0 — local GPU, no provider, nothing published, shots.md untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BEAT = 4
GOBLIN_DEF = "green skin, tusks"
IPA_REPO = "h94/IP-Adapter"
IPA_SUBFOLDER = "sdxl_models"
IPA_WEIGHT = "ip-adapter-plus_sdxl_vit-h.safetensors"
IPA_ENCODER_SUBFOLDER = "models/image_encoder"
IPA_LICENCE = "Apache-2.0 (h94/IP-Adapter); image encoder weights derive from laion/CLIP-ViT-H-14-laion2B-s32B-b79K, MIT"

# The headline arm first, so an interruption loses the sweep and not the A/B.
# (reference index, ip_adapter_scale)
CELLS_WHOLE = [(0, 0.6), (1, 0.6), (2, 0.6), (3, 0.6), (0, 0.4), (0, 0.8)]

# ARM 2, and it exists because arm 1 measured a real cost. Whole-model
# conditioning at scale 0.6 raised seed-to-seed agreement from 0.697 to ~0.805
# DINO and took the skin OUT of the green band while doing it: the share of
# pixels at hue 140-170 fell from 0.256 to 0.005 across all four references,
# and green is the founder's ONE named attribute. IP-Adapter carries the
# reference's colour along with its character, and beat 04's references are all
# lit like a dim interior — the wave-1 lighting fault, now being amplified.
#
# The lever is documented, not invented: set_ip_adapter_scale takes a
# per-transformer-block config (diffusers 0.29.2, docstring quotes InstantStyle's
# split), where up block_0 is where style is injected and down block_2 is where
# layout/content is. Scoping the adapter to down block_2 alone asks for the
# creature without the palette, leaving colour to the text prompt that was
# already getting it right.
CELLS_CONTENT = [(0, None), (1, None), (2, None), (3, None)]
CONTENT_SCALE = {"down": {"block_2": [0.0, 1.0]}}

# ARM 3 — WHEN, not how much and not where. Arms 1 and 2 moved the only two
# knobs anyone had tried: the adapter's strength, and which UNet blocks it
# reaches. Both bought identity with colour or colour with identity. The third
# axis is the denoise schedule, and it is untouched here: in every cell of arms
# 1 and 2 the reference is present for all 40 steps.
#
# WHY THIS SHOULD SEPARATE THEM. The two things in conflict are laid down at
# different times. A diffusion sampler fixes coarse structure — the shape of
# the head, the silhouette, WHICH CREATURE THIS IS — in the earliest, highest-
# noise steps, and spends the late steps on surface: local colour, texture,
# shading. So conditioning that is present early and absent late should buy the
# creature and leave the skin to the text prompt, which was already delivering
# green 4/4 before any reference was shown to the model (commit 406909c).
#
# NOT INVENTED HERE. This is the standard timestep window that
# ComfyUI_IPAdapter_plus exposes on every advanced node as `start_at` /
# `end_at` (percentages of the denoise, default 0.0-1.0), documented for
# exactly this use — target the early denoise for structure, the late for
# detail. diffusers has no such parameter, so the equivalent is built here from
# two documented pieces: `callback_on_step_end`, which the SDXL pipeline in
# 0.29.2 accepts and calls after each step, and `set_ip_adapter_scale`, which
# writes `.scale` on the IPAdapterAttnProcessor instances. That attribute is
# read on every forward pass (verified in this diffusers build), so setting it
# to 0 from the callback switches the adapter off for the remaining steps
# without touching weights, embeddings, or the sampler's own state.
#
# COSTS ZERO PROMPT TOKENS, like the other two arms, and adds no word to the
# founder's "nothing complex".
#
# (reference index, ip_adapter_scale, fraction of steps the adapter is ON)
WINDOW_SCALE = 0.6
CELLS_WINDOW = [(0, WINDOW_SCALE, 0.15), (0, WINDOW_SCALE, 0.25),
                (0, WINDOW_SCALE, 0.40), (0, WINDOW_SCALE, 0.60)]

# ARM 4 — the negative, and it is the only lever here that does not touch the
# adapter at all. Arms 1-3 all ask WHERE, HOW HARD or WHEN the reference should
# push. This one leaves arm 1 exactly as it was and pushes back from the other
# side.
#
# WHY IT IS WORTH A ROUND. The negative prompt this wave has been sending for
# every frame — 50 tokens of it — contains no colour term whatsoever. Not
# `greyscale`, not `monochrome`, nothing. That is a real gap and not a theory:
# these are the two most standard negatives in the anime-model dialect
# precisely because they hold saturation up, and animagine-xl-3.1 is trained on
# the tag vocabulary they come from. So the drained skin arm 1 produces has
# never had anything opposing it.
#
# IT COSTS ZERO POSITIVE TOKENS. Beat 08 of this wave has 9 tokens of headroom
# on the real CLIP tokenizer and compress() drops TRAILING sentences, so the
# positive side is where there is no room. The negative is at 50 of 77, so an
# anchor of this size fits with margin, and it adds no word to the description
# of the goblin — nothing here argues with "nothing complex".
#
# ALL FOUR REFERENCES, at the same 0.6 that arm 1 ran, so every cell differs
# from an already-rendered arm-1 row by exactly one thing: these five words in
# the negative. Nobody has picked a canonical goblin and this arm does not.
NEG_COLOUR_ANCHOR = "greyscale, monochrome, desaturated, grey skin, pale skin"
CELLS_NEGCOLOR = [(0, 0.6), (1, 0.6), (2, 0.6), (3, 0.6)]

# ONE REFERENCE ON PURPOSE, and it is not a pick. Reference s0 at scale 0.6 is
# an EXISTING measured row (arm 1, ipa-r0-c060: DINO 0.8069, green 0.00), so
# every cell below differs from a rendered control by one variable and nothing
# else. Sweeping a knob on one reference is the same shape as arm 1's own
# 0.4/0.8 sweep. If a window works, the next round runs it across all four
# references — which is where the mechanism claim would have to survive.
# Nobody has chosen a canonical goblin and this arm does not choose one.


def square(img):
    """Centre-crop to square before the CLIP image processor does it for us.

    CLIPImageProcessor resizes then centre-crops to 224; on an 832x1216 portrait
    that silently discards the top and bottom. Doing it here makes the crop a
    recorded step instead of a surprise, and keeps the face — which is what the
    reference is for — inside the frame.
    """
    w, h = img.size
    s = min(w, h)
    return img.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))


def sidecar(png: Path, *, seed: int, row: dict, secs: float, task: str,
            harness_sha: str, drafts_sha: str, self_sha: str, wg,
            ref: Path, ref_sha: str, scale: float,
            window: tuple = None) -> None:
    """§7.2 provenance, written at render time beside the frame."""
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())

    lines = [
        "# Still provenance (7.2), written AT RENDER TIME by goblin_ipa_sample.py",
        "# on the rtx5090. ONE SAMPLE of a CONSISTENCY MECHANISM on beat 04 —",
        "# not a wave, and not a candidate for the founder to pick from. The",
        "# prompt, seeds, steps, guidance and negative are byte-identical to the",
        "# wave-1 sample (commit 406909c); the ONLY change is the IP-Adapter",
        "# conditioning recorded below. The reference image is one of the four",
        "# wave-1 frames, used because all four are used in turn — it is NOT a",
        "# canonical goblin and nobody has picked one.",
    ]
    lines += [f"#   NEGWARN: {w}" for w in row["warns"]]
    body = [
        "platform: local-gpu (rtx5090)",
        f"model: {wg.BASE}",
        f"model_licence: {wg.LICENCE}",
        "cost_usd: 0.00",
        f"shot_beat: {row['beat']}",
        f"beat_slug: {row['slug']}",
        f"beat_kind: {row['kind']}",
        f"size: {wg.W}x{wg.H}",
        f"steps: {wg.STEPS}",
        f"guidance: {wg.CFG}",
        f"seed: {seed}",
        "seeds_in_batch: 4",
        f"task: {task}",
        "render_round: ipa-consistency-1",
        "candidate_set: none (mechanism test, not a pick sheet)",
        f"count_tag: {row['tag']}",
        f"negative_terms_removed: {wg.DROP_NEG}",
        "consistency_mechanism: IP-Adapter Plus (SDXL, ViT-H image encoder)",
        f"ip_adapter_repo: {IPA_REPO}",
        f"ip_adapter_weight: {IPA_SUBFOLDER}/{IPA_WEIGHT}",
        f"ip_adapter_image_encoder: {IPA_REPO}/{IPA_ENCODER_SUBFOLDER}",
        f"ip_adapter_licence: {IPA_LICENCE}",
        f"ip_adapter_scale: {scale}",
        # Absent on arms 1 and 2, where the adapter runs for every step. Named
        # here even when null so a reader can tell "all 40 steps" from "nobody
        # recorded it".
        ("ip_adapter_step_window: all %d steps (no schedule)" % wg.STEPS
         if window is None else
         "ip_adapter_step_window: >-\n" + block(
             "on for steps 0-%d of %d (%.0f%% of the denoise), then "
             "set_ip_adapter_scale(0.0) from callback_on_step_end for the "
             "remaining %d. The reference conditions the early, structure-"
             "forming steps only; the late steps are text-conditioned alone."
             % (window[0] - 1, wg.STEPS, window[1] * 100, wg.STEPS - window[0]))),
        f"ip_adapter_reference: {ref.name}",
        f"ip_adapter_reference_sha256: {ref_sha}",
        "ip_adapter_reference_prep: centre-cropped to square, then the pipeline's CLIPImageProcessor",
        "ip_adapter_reference_note: >-",
        block("one of the four wave-1 frames. All four are used as the "
              "reference in turn across this run, so the agreement number is a "
              "property of the mechanism and not an endorsement of any one "
              "creature. Choosing the goblin is R4's call and this run does "
              "not make it."),
        "goblin_definition_source: >-",
        block("the founder, 2026-08-10, verbatim: \"he is just a simple green "
              "goblin, nothing complex\". Recorded in cuts/cuts.yaml item 18 "
              "(settled) and taste/steward-model.ledger.yaml record "
              "ep2-goblin-definition-0810."),
        "goblin_definition_as_sent: >-",
        block(f"{GOBLIN_DEF} — unchanged from the wave-1 sample, on purpose. "
              "It is the steward's translation of his sentence into slot tags "
              "and he has NOT ratified it. Holding it fixed is what makes this "
              "an A/B of the mechanism rather than a second, confounded "
              "question about the words."),
        "prompts_from: wave-drafts.yaml (NOT shots.md — shots.md is untouched)",
        f"harness_sha256: {harness_sha}",
        f"drafts_sha256: {drafts_sha}",
        f"sampler_sha256: {self_sha}",
        "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
        f"positive_tokens: {row['pos_tok']}",
        f"negative_tokens_sent: {row['neg_tok']}",
        f"extra_negative_tier: {row['extra_neg_tier']}",
        "prompt_tokens_added_by_mechanism: 0",
        "prompt: >-",
        block(row["pos"]),
        "negative_prompt: >-",
        block(row["neg"]),
        # Spelled out separately from the negative it is already inside, so a
        # reader comparing this frame against an arm-1 frame can see the one
        # variable without diffing two 60-token strings.
        ("colour_anchor_negative: none (negative byte-identical to arm 1)"
         if not row.get("neg_anchor") else
         "colour_anchor_negative: " + row["neg_anchor"]),
        f"render_seconds: {secs:.1f}",
        "founder_verdict: null",
        "scored: false",
    ]
    png.with_suffix(".yaml").write_text("\n".join(lines + body) + "\n",
                                        encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", required=True,
                    help="dir holding render_wave_goblin.py and wave-drafts.yaml")
    ap.add_argument("--root", required=True, help="repo checkout with pipeline/sd_prompt.py")
    ap.add_argument("--refs", required=True,
                    help="dir holding 04-the-footnote-wave1-s0..3.png")
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default=None)
    ap.add_argument("--arm",
                    choices=("whole", "content", "window", "negcolor"),
                    default="whole",
                    help="whole = adapter on every block at a float scale; "
                         "content = adapter scoped to down block_2 only; "
                         "window = adapter on every block at 0.6 but only for "
                         "the first N%% of the denoise steps; "
                         "negcolor = arm 1 unchanged, plus a colour anchor in "
                         "the negative")
    ap.add_argument("--dry", action="store_true", help="measure, draw nothing")
    a = ap.parse_args()
    cells = {"whole": CELLS_WHOLE, "content": CELLS_CONTENT,
             "window": CELLS_WINDOW, "negcolor": CELLS_NEGCOLOR}[a.arm]

    harness = Path(a.harness).resolve()
    sys.path.insert(0, str(harness))
    import render_wave_goblin as wg                                  # noqa: E402

    root = Path(a.root).resolve()
    sys.path.insert(0, str(root / "pipeline"))
    import sd_prompt as sd                                           # noqa: E402

    if sd._clip_tokenizer() is None:
        print("!! no CLIP tokenizer here — compress() would drop different "
              "sentences than the box does and the prompt would stop being "
              "the wave-1 prompt. Refusing.", flush=True)
        return 9

    drafts_path = harness / "wave-drafts.yaml"
    drafts = wg.load_drafts(drafts_path)
    d = drafts[BEAT]
    row = wg.check(BEAT, d, d["authored"].replace(wg.GOBLIN_SLOT, GOBLIN_DEF), sd)
    row["extra_neg_tier"] = d["extra_neg"]
    if row["faults"]:
        print("\n!! FAULTS — nothing drawn: " + "; ".join(row["faults"]), flush=True)
        return 1

    # ARM 4's whole variable, applied here and nowhere else. Terms already in
    # the negative are dropped rather than repeated, so the anchor can never
    # silently double-weight a term the recipe was already sending.
    row["neg_anchor"] = None
    if a.arm == "negcolor":
        have = {p.strip() for p in row["neg"].split(",")}
        add = [t.strip() for t in NEG_COLOUR_ANCHOR.split(",")
               if t.strip() not in have]
        if not add:
            print("!! every colour-anchor term is already in the negative — "
                  "this arm would be byte-identical to arm 1. Refusing.",
                  flush=True)
            return 5
        row["neg_anchor"] = ", ".join(add)
        row["neg"] = row["neg"] + ", " + row["neg_anchor"]
        before = row["neg_tok"]
        row["neg_tok"] = sd.negative_tokens(row["neg"])
        # A negative over budget is not truncated by the tokenizer in any way we
        # can predict per-term, so it is refused rather than sent and reported.
        if row["neg_tok"] > 77:
            print(f"!! colour anchor puts the negative at {row['neg_tok']}/77 "
                  f"tokens (was {before}). Over budget — refusing rather than "
                  "sending a prompt whose tail may not bind.", flush=True)
            return 6
        print(f"\n   ARM 4 colour anchor: +{row['neg_anchor']}", flush=True)
        print(f"   negative tokens: {before} -> {row['neg_tok']} (budget 77)",
              flush=True)
        print(f"   NEG(sent): {row['neg']}", flush=True)
        print("   positive prompt UNCHANGED, 0 tokens added to it", flush=True)

    refs_dir = Path(a.refs).resolve()
    refs = [refs_dir / f"04-the-footnote-wave1-s{i}.png" for i in range(4)]
    missing = [r.name for r in refs if not r.exists()]
    if missing:
        print(f"!! reference frames missing: {missing}. This run is an A/B "
              "against the wave-1 sample and cannot be built without it.",
              flush=True)
        return 4

    self_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    harness_sha = hashlib.sha256(
        (harness / "render_wave_goblin.py").read_bytes()).hexdigest()
    drafts_sha = hashlib.sha256(drafts_path.read_bytes()).hexdigest()
    ref_sha = {r.name: hashlib.sha256(r.read_bytes()).hexdigest() for r in refs}
    task = a.task or f"ep2-b04-ipa-{int(time.time())}"
    seeds = [wg.SEED + BEAT + i * 1000 for i in range(4)]

    print(f"\nONE SAMPLE — beat {BEAT:02d} {d['slug']}, consistency mechanism, $0",
          flush=True)
    print(f"   mechanism: IP-Adapter Plus, arm={a.arm}, {len(cells)} cells "
          f"x 4 seeds = {len(cells) * 4} frames", flush=True)
    print(f"   seeds (identical to wave-1): {seeds}", flush=True)
    print(f"   prompt tokens: {row['pos_tok']} (mechanism adds 0)", flush=True)
    print(f"   task: {task}", flush=True)
    print(f"   sampler sha256: {self_sha}", flush=True)

    if a.dry:
        print(f"\nDRY OK — {len(cells) * 4} frames, nothing drawn", flush=True)
        return 0

    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    import torch                                                     # noqa: E402
    from PIL import Image                                            # noqa: E402
    from diffusers import StableDiffusionXLPipeline                  # noqa: E402
    from transformers import CLIPVisionModelWithProjection           # noqa: E402

    t_load = time.time()
    # Loaded explicitly in bf16 and handed to the pipeline, so load_ip_adapter
    # never has to guess a dtype for it and the encoder rides pipe.to("cuda").
    image_encoder = CLIPVisionModelWithProjection.from_pretrained(
        IPA_REPO, subfolder=IPA_ENCODER_SUBFOLDER, torch_dtype=torch.bfloat16)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        wg.BASE, torch_dtype=torch.bfloat16, use_safetensors=True,
        image_encoder=image_encoder)
    pipe.load_ip_adapter(IPA_REPO, subfolder=IPA_SUBFOLDER,
                         weight_name=IPA_WEIGHT, image_encoder_folder=None)
    pipe.to("cuda")
    print(f"MODEL_LOADED cuda/bfloat16 + IP-Adapter Plus in "
          f"{time.time() - t_load:.0f}s", flush=True)

    ref_img = {i: square(Image.open(refs[i]).convert("RGB")) for i in range(4)}

    n = 0
    for cell in cells:
        ref_i, scale, end_frac = (tuple(cell) + (None,))[:3]
        applied = CONTENT_SCALE if scale is None else scale

        # Steps the adapter stays ON for. round() rather than int() so 0.15 of
        # 40 is 6 and not 5, and clamped to >=1 so a window can never mean
        # "never applied", which would silently render the wave-1 baseline
        # again under an IP-Adapter filename.
        window = None
        if end_frac is not None:
            on_steps = max(1, min(wg.STEPS, round(end_frac * wg.STEPS)))
            window = (on_steps, end_frac)

        if a.arm == "negcolor":
            # Distinct from arm 1's r0-c060 even though the adapter config is
            # identical, because the only difference is in the negative and a
            # shared filename would make the two indistinguishable in a glob.
            tag = f"r{ref_i}-neg"
        elif end_frac is None:
            tag = (f"r{ref_i}-content" if scale is None
                   else f"r{ref_i}-c{int(round(scale * 100)):03d}")
        else:
            tag = f"r{ref_i}-w{int(round(end_frac * 100)):03d}"

        for i, seed in enumerate(seeds):
            # Re-armed for EVERY image, not once per cell: the callback below
            # zeroes the scale mid-run, and without this the second seed of a
            # windowed cell would render with the adapter already off.
            pipe.set_ip_adapter_scale(applied)
            cb = None
            if window is not None:
                on_steps = window[0]

                def cb(_pipe, step, _t, kwargs, _on=on_steps):
                    # Called after step index `step` completes, so step+1 is
                    # the number finished. Switching at equality leaves the
                    # adapter on for exactly `_on` steps.
                    if step + 1 == _on:
                        _pipe.set_ip_adapter_scale(0.0)
                    return kwargs

            g = torch.Generator(device="cpu").manual_seed(seed)
            t0 = time.time()
            img = pipe(prompt=row["pos"], negative_prompt=row["neg"],
                       ip_adapter_image=ref_img[ref_i],
                       num_inference_steps=wg.STEPS, guidance_scale=wg.CFG,
                       generator=g, width=wg.W, height=wg.H,
                       callback_on_step_end=cb).images[0]
            f = out / f"{BEAT:02d}-{d['slug']}-ipa-{tag}-s{i}.png"
            img.save(f)
            secs = time.time() - t0
            n += 1
            sidecar(f, seed=seed, row=row, secs=secs, task=task,
                    harness_sha=harness_sha, drafts_sha=drafts_sha,
                    self_sha=self_sha, wg=wg, ref=refs[ref_i],
                    ref_sha=ref_sha[refs[ref_i].name],
                    scale=applied, window=window)
            print(f"   {f.name} seed={seed} {secs:.0f}s  ({n}/{len(cells) * 4})",
                  flush=True)

    print(f"\nDONE {n} stills — ONE beat. The other fourteen wait on his verdict.",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
