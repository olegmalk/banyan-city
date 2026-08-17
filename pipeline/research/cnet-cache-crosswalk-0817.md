# Which of those ControlNets do we actually HAVE? — the box cache, enumerated

Companion to `pipeline/research/count-control-sdxl-0817.md`, which surveyed what
exists **upstream** and explicitly left the local inventory open. This file
closes that gap. Separate file rather than a new section in that one because it
was committed by another lane and two lanes in one file is a mistake this repo
has already declined twice today.

**Method: enumerated, not assumed.** `C:\Users\artvn\.cache\huggingface\hub` on
the rtx5090, listed over ssh; per-repo blob byte totals and a recursive
`*.incomplete` count. Sizes below are real blob bytes, not snapshot symlinks
(Windows reparse points report 0 B, which is how a half-downloaded cache passes
a naive listing).

## The answer to the question that was asked

**Both tier-2 candidates are already local. Tier 2 is FREE — no download, $0,
no network.** `xinsir/controlnet-scribble-sdxl-1.0` and `TheMistoAI/MistoLine`
are both complete on the box.

## Crosswalk

| repo named in the research survey | on the box? | blob bytes | note |
|---|---|---|---|
| `xinsir/controlnet-scribble-sdxl-1.0` | **YES** | 2,386 MiB | the tier-2 default. Apache-2.0, no attribution condition |
| `TheMistoAI/MistoLine` | **YES** | 2,386 MiB | OpenRAIL++ **plus a visible-attribution obligation** (see below) |
| `xinsir/controlnet-canny-sdxl-1.0` | **YES** | 2,386 MiB | not requested by the survey; present anyway |
| `xinsir/controlnet-depth-sdxl-1.0` | **YES** | 2,386 MiB | `B01-R9-PLAN.md` §9's named r10 substitution |
| `diffusers/controlnet-depth-sdxl-1.0` | **YES** | 2,386 MiB | openrail++; the net r9 actually rendered with |
| `xinsir/controlnet-union-sdxl-1.0` / `-promax` | no | — | would be a download. Also needs `ControlNetUnionModel`, and diffusers here is 0.29.2 — that class landed later |
| `diffusers/controlnet-canny-sdxl-1.0` | no | — | we hold the *depth* diffusers net, not the canny one |
| `diffusers/controlnet-canny-sdxl-1.0-small` | no | — | would be a download |
| `lllyasviel/*` SDXL controlnet | **does not exist** | — | dead end already documented: v1.1 is SD1.5/2.0, `sd_control_collection` aggregates others' weights |

Every present repo: `.incomplete` count **0**, and 2,386 MiB is exactly the
2,502,139,104 bytes `B01-R9-PLAN.md` §9 recorded against its own licence audit —
so these are the vetted blobs, not truncated ones.

**Annotator/estimator weights also local** (`lllyasviel/Annotators` 240 MB,
`Intel/dpt-hybrid-midas` 467 MB, `Intel/dpt-large` 1,304 MB,
`LiheYoung/depth-anything-large-hf` 1,279 MB, `facebook/dinov2-base` 330 MB).
Mostly moot for us: we **author** hints with PIL rather than extracting them from
an image, so no preprocessor runs. Which is convenient, because
`lllyasviel/Annotators` is the one licence landmine in the cache —
`B01-R9-PLAN.md` §9 flags it **DO NOT USE FOR CANON**: no LICENSE file, per-file
upstream terms differ, and CMU OpenPose upstream is non-commercial. Authoring
sidesteps it entirely.

## Two things that decide which net tier 2 should use

**Prefer scribble over MistoLine on licence grounds.** Both accept hand-drawn
input, so the tie-break is terms: xinsir is plain Apache-2.0, while MistoLine's
README requires commercial users to credit TheMisto.ai "in the documentation,
website, or other prominent and visible locations." That is a standing
obligation on every frame it ever renders, inherited by anything downstream.
Usable, but it should be a deliberate choice, not a default.

**The `variant=` trap, verified against the snapshot filenames, not assumed.**

| repo | file it ships | `variant="fp16"` |
|---|---|---|
| `xinsir/*` | `diffusion_pytorch_model.safetensors` | **must NOT pass** — raises |
| `TheMistoAI/MistoLine` | `diffusion_pytorch_model.fp16.safetensors` | **must pass** — omitting raises |
| `diffusers/controlnet-depth-sdxl-1.0` | `diffusion_pytorch_model.fp16.safetensors` | **must pass** |

This is why a naive constant-swap of `render_b01r9.py` to a xinsir net crashes:
it hardcodes `CONTROLNET_VARIANT = "fp16"` and passes it. `controlnet_probe.py`
sets `CONTROLNET_VARIANT = None` and gates the kwarg for exactly this reason.

## Compatibility with our base, measured rather than argued

The survey established the pairing from existence proofs
(`SubMaroon/ControlNet-anime-colorize` trained on animagine-xl-3.0). Measured
here from the other direction, which is stronger:

- `xinsir/controlnet-scribble-sdxl-1.0` loaded with `HF_HUB_OFFLINE=1` in the
  box venv: **1,251,014,160 params**, bf16, `cross_attention_dim` **2048**,
  `block_out_channels` **[320, 640, 1280]**.
- `cagliostrolab/animagine-xl-3.1`'s UNet config: `cross_attention_dim` **2048**,
  `block_out_channels` **[320, 640, 1280]**, `addition_embed_type: text_time`.

Identical on both markers. 2048 is the SDXL signature — SD1.5 is 768, which is
the architectural reason no SD1.5 controlnet can load here and why the
`y is None` failure the survey cites is a family mismatch rather than a bug.

## What is NOT established by any of the above

That the condition **binds**. Loading is compatibility; a ControlNet that runs
and then ignores its hint would look exactly like a working path. That is what
`pipeline/jobs/ep2-cnet-probe-0817.yaml` exists to settle, with a bar
pre-registered in code before any pixels.

And nothing here bears on leaf COUNT. Per the survey's own conclusion, a
scribble hint is **tier-2 bias on a composited init, never the count
guarantee** — the count comes from pixels drawn into the init, which is the
leaf-count lane's mechanism and its call, not this one's.

---
**Provenance.** Written 2026-08-17 by the steward (Claude Opus 5), ControlNet
capability lane. Read-only enumeration over ssh plus one offline model load on
the box; no render, no spend, no download.
