# Low-VRAM / speedup tooling research — Wan 2.2 TI2V-5B on Blackwell laptops

**Date:** 2026-08-04. **Status: IN PROGRESS — appended incrementally.**

## Task

Find tooling that beats our hand-rolled `diffusers` runner. Baseline to beat:

- 13.4 s per transformer forward pass at 6,240 tokens (480x832, ~61 frames)
- 704x1280 = 18,480 tokens; 188 s sample time at 14 steps
- No optimised attention kernel at all (stock diffusers attention), no torch.compile
- `enable_model_cpu_offload()`; measured 1.93x FASTER at higher res than without
- Transformer dtype at runtime UNVERIFIED (ships fp32 on disk)

**Target hardware:** (a) RTX 5090 laptop ~24 GB, Windows, sm_120, cu128.
(b) RTX 5070 Ti laptop 12 GB, Windows, sm_120. Same gigabit LAN (unmeasured).

## Findings

_(sections appended below as research proceeds)_

### Search pass 1 — leads (URLs to verify)

- Wan2GP: <https://github.com/deepbeepmeep/Wan2GP> — "fast AI Video Generator for the
  GPU Poor. Supports Wan 2.1/2.2, LTX-2, Qwen Image, Hunyuan Video, LTX Video, Flux."
  Memory layer is a SEPARATE library: **mmgp** ("Memory Management for the GPU Poor")
  <https://github.com/deepbeepmeep/mmgp>. Claimed floor 6 GB VRAM for Wan 2.2 14B via
  model offloading + block swapping.
- SageAttention on Blackwell + Windows: **prebuilt sm_120 wheels exist** (2026-01 era):
  <https://github.com/mobcat40/sageattention-blackwell> (SageAttention 2.2.0, sm_120,
  cu128, ~35% faster diffusion sampling claimed) and a cu130/cp313 fork
  <https://github.com/ziggyxp/sageattention-blackwell-pt211-cu130-cp313>.
  Caveat already visible: built against **torch 2.11.0.dev20260127 nightly**; a
  different nightly date requires a source rebuild, and cu128 wheels do not load on
  a cu130 torch. ComfyUI discussion thread claims native Windows support:
  <https://github.com/Comfy-Org/ComfyUI/discussions/11583>

## 1. Wan2GP (WanGP)

**Repo:** <https://github.com/deepbeepmeep/Wan2GP> · memory layer:
<https://github.com/deepbeepmeep/mmgp>

### Licence — READ THIS BEFORE ADOPTING (two different licences)

- **Wan2GP itself: "WanGP Community License 2.0"** (`LICENSE.txt`), NOT an OSI licence.
  It forbids "Restricted Commercialization" = selling the software, offering paid
  API/SaaS/hosted access, white-labelling, or embedding it in a paid product without a
  separate commercial licence. It **explicitly permits** use inside a company, and
  **selling the OUTPUTS with credit attribution**, and charging for install/consulting.
  Commercial contact: deepbeepmeep@yahoo.com.
  → For banyan-city this is **fine as-is**: we generate clips (outputs), we do not
  resell the tool. We would owe **credit attribution**, which suits our §7.2
  provenance rule anyway.
- **mmgp: GPL-3.0** (`LICENSE.md` is verbatim GPL-3 v3, 29 June 2007 — note the
  README's looser "non commercial use as long you give me proper credits" wording is
  the author's informal ask and conflicts with the actual file; the file governs).
  → Consequence: **do not `import mmgp` into `pipeline/`.** Our repo is public and IS
  the product; linking GPL-3 code into our own modules pulls copyleft onto them.
  Driving Wan2GP as a **separate process** (CLI/subprocess) is the clean posture and
  is also how the headless mode below works. Keep that boundary deliberately.

### What the offloading actually does

mmgp is not one trick, it is a budget-driven swapper:

- **Five offload profiles**, keyed to RAM/VRAM pairs, from ~24 GB RAM / 10 GB VRAM up
  to 48 GB RAM / 24 GB VRAM. A profile presets the knobs below.
- **Per-model VRAM budget.** When a model exceeds its budget it is "broken down in
  multiple parts that will be unloaded/loaded consequently" — i.e. block-wise
  streaming of transformer blocks, not whole-model offload. This is the "block swap".
- **Async H2D transfers** so the next slice uploads while the current slice computes —
  this is the part our hand-rolled `enable_model_cpu_offload()` does NOT do, and it is
  the mechanism that makes block swap much cheaper than naive offload.
- **Pinned (page-locked) RAM** for the resident copy, to make those transfers fast.
- **On-the-fly quantisation** at load time to shrink tensors.
- Smart keep-resident: avoids evicting a model that will be needed again soon.

Relevance to us: our three failures (text-encoder eviction corrupting frames, the
two-process split bypassing image conditioning, the allocator holding 22.9/25.7 GB
after clip 1) are all things this layer already solves as a maintained library.

### Wan 2.2 image-to-video

Supported — the repo advertises Wan 2.1/2.2 across its model list (plus LTX-2,
Qwen Image, Hunyuan Video, Flux, "Wan 2.2 Animate"). Needs exact i2v task-name
confirmation from the docs (pending, next step).

### Headless / scriptable? YES (this was the blocking question)

Two non-Gradio paths are documented:

- `python wgp.py --process my_queue.zip` — "Process saved queues without launching the
  web UI". So the workflow is: build a queue (settings JSON + input images) once, then
  drive batches from our own script by generating queue files.
- A documented **"WanGP API"** for integrating generation into external applications.

Claimed VRAM figures on the README are per-model, not per-GPU-timing; no per-card
generation times are published, so **their speed claims are unverified for our cards**
and we would have to measure. Figures quoted: MiniMax H3 5–6 GB for 124 frames at
832x480; LTX-2 from 6 GB; Bernini 14B 12 GB v2v. Wan 2.2 14B floor of 6 GB is claimed
in third-party writeups, not confirmed on the README.

### Headless flags (confirmed from docs/CLI.md + DeepWiki)

Docs: <https://github.com/deepbeepmeep/Wan2GP/blob/main/docs/CLI.md> ·
<https://github.com/deepbeepmeep/Wan2GP/blob/main/docs/API.md> ·
<https://deepwiki.com/deepbeepmeep/Wan2GP/4.2-command-line-interface>

- `--process PATH` — queue `.zip` **or a settings `.json`** → enables headless mode.
  The `.json` path matters: it means we can emit a settings file per beat from
  `render_local.py`-style code, no UI round-trip and no zip packing.
- `--dry-run` — validate the file without generating. Good CI/lint hook for us.
- `--output-dir PATH` — override output dir (pairs with `--process`).
- `--verbose 0..2` — logging.
- **`--mcp` — runs WanGP as an MCP server**: `python wgp.py --mcp --config <dir>
  --output-dir <dir>`, with `--mcp-transport stdio`. There is also a documented
  Python API for programmatic access.

So: three viable drive modes (settings JSON, MCP stdio, Python API), all non-Gradio.
Verdict on the blocking question: **yes, batch-scriptable.**

### The flags that matter (confirmed in docs/CLI.md)

| Flag | Meaning | Why we care |
|---|---|---|
| `--attention sdpa\|flash\|sage\|sage2` | pick attention kernel | **This is the single biggest thing we lack.** Wan2GP wires SageAttention for us; we currently run stock SDPA and would otherwise have to integrate it by hand. |
| `--compile` | torch.compile (needs Triton) | the other speedup we lack, already plumbed |
| `--profile 1..5` (default 4) | offload tier | replaces our hand-rolled memory management wholesale |
| `--preload N` | pre-allocate N MB of model in VRAM | lets the 24 GB card keep more resident than the 12 GB card, same code path |
| `--perc-reserved-mem-max FLOAT` | cap RAM reserved for models | directly targets our "allocator held 22.9/25.7 GB after clip 1" stall |
| `--quantize-transformer BOOL` | transformer quantisation on/off | |
| `--save-quantized` | write an INT8 checkpoint at load | quantise once, reuse — avoids paying conversion per run |
| `--fp16` | "use half-precision **instead of bf16**" | ⚠️ see dtype note below |

**⚠️ Dtype smoking gun.** `--fp16` is documented as an override *instead of bf16*, i.e.
Wan2GP's default compute dtype is **bf16**. Our transformer ships fp32 on disk and we
have never verified what it actually runs in. If we are running fp32, that is on its own
a large multiple of wasted time and memory bandwidth, and would explain a big share of
the 5–10x gap — independent of any tooling change. **Check this first; it is free.**

## 2. ComfyUI + Wan wrappers

**kijai/ComfyUI-WanVideoWrapper:** <https://github.com/kijai/ComfyUI-WanVideoWrapper>
Docs: <https://deepwiki.com/kijai/ComfyUI-WanVideoWrapper/6.2-block-swapping-and-device-management>

### What "block swap" does

- Transformer blocks move GPU↔CPU **just-in-time**, via *onload hooks* (block → GPU
  before its forward pass) and *offload hooks* (block → CPU after it computes).
- **Prefetching is real and on by default:** `prefetch_blocks` defaults to 1 — "preloads
  upcoming blocks while the current block is computing". Async transfers via
  `use_non_blocking=True`. This is the same trick mmgp uses and the same one our
  `enable_model_cpu_offload()` lacks.
- Beyond transformer blocks: `offload_img_emb` and `offload_txt_emb` can stay on CPU,
  but the docs warn these are "accessed frequently" so offloading them costs speed.
  → Note this is precisely the mistake we already made by hand: our text-encoder
  eviction corrupted every frame. The maintained implementations treat text/image
  embeddings as a *reluctant* last resort, not a first move.

### VRAM it enables (user reports, not vendor claims)

`blocks_to_swap` is the dial (Wan 2.2 14B has 40 blocks; the 5B fewer):

- 5090 32 GB + 96 GB RAM: users running `blocks_to_swap` 55→75 for 145 frames at
  720x1280. <https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/898>
- `blocks_to_swap=35` held ~16 GB during inference, but **spiked to ~30 GB at the end of
  each iteration** — the end-of-step spike is the OOM trap on a 12 GB card.
- 4090 24 GB: 101 frames at 1024x768 with `blocks_to_swap=40`.
- Known-issue traffic worth reading before adopting: "Wan 2.2 14B I2V — very long
  blockswap compute time" <https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/1375>,
  plus OOM reports #1267 and #1644. Block swap is not free; over-swapping trades VRAM
  for wall-clock, which is exactly the axis we are trying to win.

### Licence

- **kijai/ComfyUI-WanVideoWrapper: Apache-2.0.** Clean — no copyleft, commercial fine.
- ComfyUI core itself is **GPL-3.0** (needs a confirming fetch; pending). Same posture
  as mmgp: drive it **over HTTP as a separate server process**, which is the native way
  anyway, and no copyleft question touches our code.
- The wrapper integrates both SageAttention (`ultravico/sageattn` folder) and
  torch.compile, and the README notes newer memory work is "less reliant on
  torch.compile for VRAM efficiency". Wan 2.2 i2v supported (incl. WanAnimate nodes).

### Can ComfyUI be driven headless from Python? YES — it is server-first by design

The UI is just one client; the backend is an HTTP + WebSocket server.

- Launch: `python main.py --disable-auto-launch` (no browser), `--port N`,
  `--listen 0.0.0.0` to accept LAN connections (relevant for the two-laptop setup).
- `POST /prompt` enqueues a workflow graph → returns `prompt_id`.
- `GET /history/{prompt_id}` fetches results; `GET /view?filename=…&subfolder=…&type=…`
  downloads an output; `POST /upload/` uploads input images (we need this for i2v
  conditioning frames).
- `ws://host/ws?clientId=<uuid>` streams execution/progress events, so a script can
  block until a clip is done rather than poll.
- Official worked example in-repo:
  `script_examples/websockets_api_example.py`
  <https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/websockets_api_example.py>
- Server API overview: <https://docs.comfy.org/development/comfyui-server/comms_overview>

Practical cost for us: the workflow is a JSON node graph, so adopting ComfyUI means our
prompts/settings stop being plain python kwargs and become a graph template we
parameterise. That is real integration work versus Wan2GP's settings-JSON, and it is the
main reason to prefer Wan2GP for a batch pipeline — but ComfyUI is where the newest Wan
optimisations land first.

## 3. Attention kernels and step caching

### SageAttention — best speedup/risk ratio, but one specific landmine

- Prebuilt **sm_120 wheels exist for native Windows (not WSL)**:
  <https://github.com/mobcat40/sageattention-blackwell> — SageAttention **2.2.0**,
  claimed **~35% faster diffusion sampling, measured on an RTX 5090 Laptop 24 GB** —
  i.e. our exact card (a). cu130/cp313 variant:
  <https://github.com/ziggyxp/sageattention-blackwell-pt211-cu130-cp313>
- Requires **torch 2.11.0.dev20260127 nightly, CUDA 12.8 or 13.x, Python 3.11**.
  A different nightly date → rebuild from source. A cu128 wheel will **not** load on a
  cu130 torch and vice versa. This pins our whole environment to a nightly, which is
  the real cost of adopting it.
- 🚨 **QUALITY LANDMINE, Wan-specific:** the global `--use-sage-attention` flag
  "produces **black output** with some models (**Qwen, Wan**)". The documented
  workaround is the KJNodes "Patch Sage Attention" node with backend
  **`sageattn_qk_int8_pv_fp16_cuda`**, which avoids the corruption.
  → Directly relevant: we have already been burned once by a memory hack that
  "corrupted every frame". If we enable Sage and get black frames, **that is a known
  bug with a known fix, not a mystery** — switch backend, do not go debugging our
  pipeline. Worth writing into the loop notes.
- Licence: **Apache-2.0** (SageAttention upstream, thu-ml) — confirm pending.
- ComfyUI's own thread claims native Windows Blackwell support ~30% faster:
  <https://github.com/Comfy-Org/ComfyUI/discussions/11583>

### FlashAttention — FA3 is OFF the table for our cards

- **FA3 does not support consumer Blackwell.** sm_120 (RTX 5090, RTX PRO 6000) **lacks
  the TMEM subsystem** FA3/FA4 depend on; FA3 targets sm_90 (H100/H200). Consumer
  Blackwell stays on **FA2**, via a Triton backend.
  <https://github.com/Dao-AILab/flash-attention/issues/1987> · issues #1853, #1683
- FA2 on sm_120 + Windows: no official support; community wheels only —
  <https://github.com/roy86/flash-attention_sm120>,
  <https://huggingface.co/White2Hand/flash-attention-v2.8.3-blackwell-windows>,
  <https://huggingface.co/IxaOne/flash-attn-blackwell-win-cp313>.
  Upstream position remains that Windows compilation "requires more testing".
  NVIDIA's own GR00T repo carries an open "FlashAttention doesn't support SM120 on
  Windows" issue: <https://github.com/NVIDIA/Isaac-GR00T/issues/309>
- Licence: BSD-3-Clause.
- **Verdict: do not chase FlashAttention.** Strictly worse bet than SageAttention here —
  no FA3 on our silicon, and FA2 on Windows/sm_120 is community-wheel roulette for a
  smaller win than Sage's 35%.






