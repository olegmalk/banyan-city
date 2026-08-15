# The VAE is not the hold: an encode->decode round trip, tiling ON vs OFF

Measurement pass, 2026-08-15. **Zero generation.** No denoiser ran, no render was
enqueued, no recipe, beat spec or job file was touched. The GPU work was four VAE
decodes of 3-13 s each; the render queue was checked before every one.

This executes lever **L2** of `pipeline/research/ltx23-motion-source.md` (commit
`dfa87c27`), answers **L1** and **L3**, and reports one thing the new
`pipeline/hold_period.py` (commit `d820bf3f`) needs before its readings are trusted.

---

## The answer

**The VAE round trip does not reproduce the hold, with tiling on or off.** A real
image panned at a known constant velocity goes into the LTX-2.3 VAE and comes back
still moving on every single frame, at production geometry (704x1280, 97 frames),
measured by frame alignment, not by eye. The same harness, shown a hold, reports it
at once — so the negative is a measurement, not a blind spot.

That rules the decode side **out** and puts the hold **in the latents**, which is
where the transformer put them. It also disposes of the tiled-VAE hypothesis that
was the top-ranked lever in `dfa87c27` — for our configuration. Prompts, seeds and
strengths were never going to be fixed by turning tiling off, and turning tiling off
is not a fix to try.

---

## What was actually run

Source: `C:/banyan-farm/cond-crf.png` (a real 832x1216 anime plate, our own
conditioning image), centre-cropped, resized, and **translated by a fixed integer
number of pixels per frame**. Ground truth per-pair displacement is therefore exactly
`dx`, flat, forever — a staircase in the output is the VAE's doing and nobody else's.

Then `vae.encode(x).latent_dist.mode()` -> `vae.decode(z, temb)`, bf16 on the 5090,
in the same venv the renderer uses (`C:\banyan-video\venv`, diffusers **0.39.0**,
torch 2.11.0+cu128). Arms:

| arm | encode | decode |
|---|---|---|
| `dec_off` | untiled | **untiled** |
| `dec_on` | untiled | **tiled** (what we ship) |
| `both_on` | tiled | tiled |

Harness: `pipeline/vae_roundtrip.py` (added by this pass; it generates nothing and
loads no transformer).

### Result at production geometry — 704x1280, 97 frames, 4 px/frame

Scored with the landed `hold_period()` estimator on the per-pair difference series:

| arm | period | strength | per-pair diff cv | shift histogram (px/pair) | PSNR vs source |
|---|---|---|---|---|---|
| SOURCE | **1** (no hold) | 0.97 | 0.099 | 3:12, 4:82, 5:2 | — |
| `dec_off` untiled | **1** (no hold) | 0.97 | 0.097 | 3:10, 4:84, 5:2 | 37.0 dB |
| `dec_on` tiled | **1** (no hold) | 0.96 | 0.096 | 3:9, 4:86, 5:1 | 36.6 dB |

The two arms track the source's own shift histogram to within 2 pairs of 96 and its
difference-series variability to within 0.003. **Tiling on and tiling off differ by
0.4 dB and nothing else.** Same picture at 544x960/49f and at 1 px/frame, where a
temporal quantiser would have had the easiest possible target: 1 px/frame came back
1 px/frame on every pair, both arms.

### The positive control, which is what makes the negative worth anything

Same run with `--hold 3`: the source is held at a known period 3 **before** encoding.

| arm | period | strength | lag1 | lag2 | depth | shifts |
|---|---|---|---|---|---|---|
| `dec_off` | **3** | 1.00 | -0.49 | -0.51 | 0.060 | 0, 0, 12, 0, 0, 12, ... |
| `dec_on` | **3** | 1.00 | -0.49 | -0.51 | 0.061 | 0, 0, 11, 0, 0, 12, ... |

For comparison, the real render `0815-b13-AFTER.mp4` read through the same functions:
lag3 **1.00**, lag1/lag2 **-0.42 / -0.43**, raw series `0.26 0.16 5.12 0.17 0.26 4.99
0.12 0.18 5.39 ...`. The control's signature is the clip's signature. **The harness
detects exactly the defect we have, and it does not detect it in the round trip.**

Note also what the control shows in the other direction: the VAE **preserved** an
input hold perfectly. It neither creates temporal quantisation nor smooths it away.

### I opened the frames

`pipeline/research/EVIDENCE-vae-roundtrip-0815.png`, three rows of nine consecutive
frames, same crop within each row:

- **A** — real render `0815-b13-AFTER`, its *most active* 180x240 window (chosen by
  summed absolute difference, not by eye). Across frames 12-20 the pale shape at the
  top edge advances in three visible steps and sits still between them; most of the
  window does not change at all.
- **B** — VAE round trip of real motion, 704x1280x97, **tiling ON**. Nine frames,
  nine different pictures: the collar and the lit edge climb one small step per
  frame, evenly, with no repeated pair anywhere in the row.
- **C** — the positive control. Frames group visibly into 3 / 3 / 3 — the same
  read-it-across-the-page look our clips have.

B against C is the whole finding in one image, and B against A is why the tiled-VAE
lever is closed.

---

## What this rules in and out

**Out — the decode side, end to end.** Nothing between the transformer's latents and
the exported pixels does temporal work that could impose a hold:

1. The **spatial latent upsampler** we load is spatial only. Read from the
   checkpoint's own metadata this pass (`ltx-2.3-spatial-upscaler-x2-1.1.safetensors`,
   `__metadata__["config"]`): `{'spatial_upsample': True, 'temporal_upsample': False,
   'spatial_scale': 2.0, ...}`. The class supports temporal upsampling; our file does
   not use it.
2. **We never run the temporal-tiled VAE path at all.** In the installed
   `diffusers/models/autoencoders/autoencoder_kl_ltx2.py`, `_decode` reaches
   `_temporal_tiled_decode` only `if self.use_framewise_decoding and num_frames >
   tile_latent_min_num_frames`. `use_framewise_decoding` is set to `False` in
   `__init__` (line 1174) and **`enable_tiling()` does not set it** — it sets
   `self.use_tiling = True` and the six tile-size fields, nothing else (lines
   1190-1222). A `findstr` for `framewise` across the installed `pipelines/ltx2/`
   returns nothing. Our tiling is **spatial**: 512x512 tiles, 448 stride, triggered
   because 704x1280 exceeds `tile_sample_min_*`.
   That matters for how the community reports are read: ComfyUI #11767 is titled
   around *tiled encode* and *"ghosting in between temporal chunk"* — a temporal-chunk
   mechanism. **We have no temporal chunks.** (Quotes as recorded in
   `ltx23-motion-source.md` §2.3-2.4, fetched by that pass on 2026-08-15;
   **this pass did not re-fetch them and does not add any new quote**.)
3. The pixel-side round trip itself, measured above.

**In — the latents.** The hold is upstream of the decode. That is consistent with the
37-clip sweep landing alongside this pass: **b02/b03 read period 2, b13 reads period
3, `0814-b06-DONE` reads period 6.** A fixed decode-side artifact cannot be
content-dependent — it would impose the same period on every clip, and it imposes
none here. Beat-dependent periods are what a *denoiser* produces.

**Still open, and not touched by this pass:** why the transformer emits latents whose
decoded pictures repeat, and whether `stg_scale` moves it (L3 below, L4-L6 in
`dfa87c27`).

---

## L1 — decode saved latents untiled: THERE ARE NO SAVED LATENTS

Checked, rather than assumed. Every `*.pt` on the box (`dir /s /b C:\banyan-farm\*.pt`)
is a `*-embeds.pt` prompt-embedding file; no `.npy`/`.npz` outside numpy's own test
data. In `pipeline/ltx_i2v.py` the only latent capture is `cap["latents"]` inside
`_render_one`, which lives in memory for the `--decode-frame0-out` replica and is
never written. **No path exists to replay a real render's latents; I am not inventing
one.**

It is worth adding, and it is cheap: the final-stage latent tensor is
`1 x 128 x 13 x 40 x 22` bf16 = **2.9 MB**. That is 2.9 MB per beat to make L1 —
and every future latent-side question — answerable without a re-render. Recommended
as a follow-up with its own review, **not shipped by this pass** (scope: diagnosis).

## L3 — `stg_scale` IS reachable, and we do not pass it

Read in the installed source, not the docs:
`C:\banyan-video\venv\Lib\site-packages\diffusers\pipelines\ltx2\pipeline_ltx2_image2video.py`.
`LTX2ImageToVideoPipeline.__call__` takes `stg_scale: float = 0.0` (line 883) beside
`spatio_temporal_guidance_blocks: list[int] | None = None`, and its docstring says
verbatim:

> `spatio_temporal_guidance_blocks` (`list[int]`, *optional*, defaults to `None`):
> The zero-indexed transformer block indices at which to apply STG. Must be supplied
> if STG is used (`stg_scale` or `audio_stg_scale` is greater than `0`). A value of
> `[29]` is recommended for LTX-2.0 and **`[28]` is recommended for LTX-2.3**.

The machinery is real and complete: `check_inputs` refuses `stg_scale > 0` without
blocks (line 536), a second uncond forward runs under `cache_context("uncond_stg")`
(1372), and the result enters the update as `video_stg_delta = self.stg_scale *
(noise_pred_video - noise_pred_video_uncond_stg)` (1407), added at 1458.

**We never pass either.** `findstr /n /i "stg"` over the box's own
`pipeline/ltx_i2v.py` returns nothing, and so does a grep over `pipeline/*.py` here.
So the one lever a Lightricks collaborator named for this exact symptom (quoted in
`ltx23-motion-source.md` §3.1) is **available through our call path and sitting at its
default of 0** — the cost of turning it on is one extra transformer forward per step,
which is a sample-shaped question for whoever owns the recipe, not a finding.

---

## A caveat the new metric needs: strength is not depth

`hold_period` is scale-free by design, which is exactly right for finding a period —
and it means a **shallow ripple reads like a freeze**. My 544x960 round trip, whose
every frame provably advances 4 px, reports `period=2, strength=0.90, "HOLD: ...
effective 12.0 fps"`. It is not a hold. The quiet pairs are **97%** of the loud ones;
the ripple is an aliasing beat between a 4 px pan and the 1/8-scale downsample.

Add the trough/peak ratio beside the strength and the two are trivial to tell apart
(measured this pass, same estimator):

| clip | period | strength | **depth** | what it is |
|---|---|---|---|---|
| `0815-b13-AFTER.mp4` | 3 | 0.96 | **0.029** | real hold, 0.22 vs 7.40 |
| `0814-b06-DONE.mp4` | 6 | 0.65 | **0.181** | real hold, 0.98 vs 5.40 |
| `0815-b02-FIXED.mp4` | 2 | 0.96 | **0.431** | motion *pulses*, never freezes |
| this round trip (544x960) | 2 | 0.90 | **0.971** | no hold at all |
| positive control (`--hold 3`) | 3 | 1.00 | **0.060** | known hold, recovered |

Two consequences worth the metrics lane's attention. First, `0815-b02-FIXED` at depth
0.43 is a materially different animal from `b13` at 0.03 — **"every b02/b03 clip reads
period 2 at 0.90-0.99" may be several different things**, and depth separates them
without opening a single frame. Second, no b02/b03 period-2 reading should be called a
freeze until its depth is looked at. `depth()` is implemented in
`pipeline/vae_roundtrip.py`; I have deliberately **not** edited `hold_period.py`,
which another lane owns and landed hours ago.

---

## Provenance

Steward, 2026-08-15, model claude-opus-5. Every number above was produced this pass on
the RTX 5090 in the renderer's own venv, or read from the installed library source /
checkpoint metadata on that box. The GitHub issue quotes are **not re-fetched here**
and are attributed to `ltx23-motion-source.md` (`dfa87c27`) where they were fetched;
this pass adds no external quote of its own. No source was found, and none is claimed,
for anyone reporting a *content-dependent* hold period in LTX. $0 spent; no clip was
generated, no queue entry touched.
