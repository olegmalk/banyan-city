# Vendored model licences

The licence text for every third-party model whose output we publish, copied
here verbatim so our provenance does not depend on someone else's file staying
where their own documentation says it is.

**Why this directory exists.** On 2026-08-01 the licence research found that
every Wan 2.2 weights repo on Hugging Face ships **no LICENSE.txt** — the model
card links to one and that link returns **HTTP 404**. The full text exists only
in the upstream GitHub repo. So the licence under which we publish the footage in
our live episode rested on a metadata tag plus an upstream file, neither of which
we control and one of which is already broken.

For a project whose central claim is that the repo IS the product and every
render publishes its provenance (§7.2), "trust me, it was Apache-2.0" is not
good enough. `licence_gate.py` says a licence nobody can quote is a violation;
that rule has to apply to us too.

| file | model | verified |
|---|---|---|
| `Wan2.2-LICENSE.txt` | Wan 2.2 (TI2V-5B, I2V-A14B, Diffusers variants) | 2026-08-01 — fetched from `raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt`, 11357 bytes, sha256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`. Whitespace-normalised comparison against `apache.org/licenses/LICENSE-2.0.txt` is **identical** — canonical Apache-2.0, no appended clauses, no NOTICE file to propagate. |
| `FastVideo-FastWan-LICENSE.txt` | `FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers` (the FastWan 3-step distill) | 2026-08-07 — fetched from `raw.githubusercontent.com/hao-ai-lab/FastVideo/main/LICENSE`, 10757 bytes, sha256 `5c7f173199fd7fb3cc83d86d24f3541e8ae0cb8c16e912ca519ed6a1435bd8f3`. Operative sections 1–9 are **whitespace-normalised identical** to `apache.org/licenses/LICENSE-2.0.txt`. The file differs from canonical by exactly 561 characters, all of them the APPENDIX *boilerplate template* ("Copyright [yyyy] [name of copyright owner]…"), which upstream truncated. That template is instructions for applying the licence to a new work, not terms — nothing is added and no clause is removed. GitHub's own detector resolves the repo to `spdx_id: Apache-2.0`, not `NOASSERTION`. No NOTICE file in the repo root. |
| `bilibili-Index-anisora-LICENSE.txt` | `IndexTeam/Index-anisora` **V2 / V3 / V3.1 / V3.2** (the Wan-based line only — *not* the `V1` / `5B` / `5B_RL` CogVideoX folders, which this text does not cure) | 2026-08-07 — fetched from `raw.githubusercontent.com/bilibili/Index-anisora/main/LICENSE`, 13206 bytes, sha256 `b38f8efde614507194157fc7a1e993f66b9fd3d9b687f3f11309975cb0794480`. **This file is NOT canonical Apache-2.0.** It is canonical Apache-2.0 — whitespace-normalised identical to `apache.org/licenses/LICENSE-2.0.txt` through the APPENDIX, all 10221 normalised characters — followed by **1848 characters of appended text**, a "[Model License Agreement], Based on [Apache 2.0] License with Additional Restrictions" carrying six numbered clauses. All six sit under one chapeau: *"Should you undertake fine-tuning/retraining or derivative development of this model, you must additionally comply with"*. Copied here because it lives at the `bilibili` GitHub org while the weights live at the `IndexTeam` HF org, and nothing on the HF surface links the two — see `pipeline/research/models-licence.md`, 2026-08-07 section. |

The Wan model card additionally disclaims the output: *"We claim no rights over
the your generated contents, granting you the freedom to use them."*

To add a licence here: fetch the primary text, record where from, its size and
sha256, and whether it differs from the canonical form of whatever licence it
claims to be. Never summarise — copy.
