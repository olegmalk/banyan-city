# Public evaluation work on image-to-video models — reference points

**Compiled:** 2026-08-04 by research subagent (res-bench) for banyan-city.
**Status: IN PROGRESS — written incrementally, sections appended as research completes.**

## Why this file exists

We choose our video model by rendering one beat and having the author look at it.
That does not change (R4 — taste belongs to the author). This file exists only so we
stop *discovering known facts by accident*. Nothing here is a verdict on which model
to use.

## What we actually need scored

Our four concerns, in priority order:

1. **Dynamic degree** — does anything actually move? Our worst failure was clips the
   author called "literally just frozen frames". A model can score well on
   "motion smoothness" by not moving at all, so smoothness alone is a trap metric.
2. **Conditioning-image faithfulness** — the model must ANIMATE the approved still,
   not redraw it. Recurring failure: a leaf becomes a whole branch, a second stem
   enters frame, the scene gets re-lit.
3. **Anime / 2D cel style competence** — founder's verdict on Wan 2.2: "still pretty
   good, the problem is its not made for anime style".
4. **Open weights at 24GB / 12GB VRAM** — hosted APIs are reference only ($0 budget).

Fixed constraints: I2V only, 3-4s clips, 9:16 vertical, 704x1280.

---

## 1. VBench family

Three separate things share the name. Only one of them is image-to-video.

| Suite | Task | Dimensions | Status for us |
|---|---|---|---|
| VBench (CVPR 2024) | text-to-video | 16 | wrong task |
| VBench++ (TPAMI, accepted Nov 2025) | umbrella: adds **VBench-I2V**, VBench-Long, VBench-Trustworthiness | — | **VBench-I2V is the one that matters** |
| VBench-2.0 (Mar 2025) | text-to-video only | 5 categories / 18 fine-grained | wrong task, but see §4 |

### VBench-I2V dimensions (9 scored)

Split into two groups, which is the important structural point:

**Video-image consistency** (does the video match the conditioning image?)
- `Video-Image Subject Consistency` — DINO feature similarity between the input image
  and *every* generated frame
- `Video-Image Background Consistency` — same idea for background
- `Video-Text Camera Motion` — did it obey the requested camera move

**Video quality** (inherited from VBench, image-agnostic)
- `Subject Consistency`, `Background Consistency` — frame-to-frame, not vs. the input
- `Motion Smoothness`
- `Dynamic Degree`
- `Aesthetic Quality`, `Imaging Quality`

Composite scores: `I2V Score` (the video-image group), `Quality Score` (the quality
group), `Total Score` (weighted combination).

**Dynamic degree** is a *binary per-video classification* aggregated to a percentage —
each video is labelled dynamic or not (RAFT optical-flow based, threshold adapted to
resolution for cross-resolution fairness), and the score is the share of videos labelled
dynamic. So "48%" means *48% of clips moved at all*, not "moved 48% as much as ideal".
It is coarser than our own median-frame-difference metric but measures the same failure.

### VBench-I2V leaderboard — retrieved live 2026-08-04

Source: the Gradio config embedded in <https://vchitect-vbench-leaderboard.hf.space/>
(the backing CSV dataset `Vchitect/vbench_leaderboard_submission` is gated, HTTP 401;
the space HTML is the only public route to the numbers). 35 rows. `Date` is the
submission date, not a model release date.

Sorted by Dynamic Degree, descending. **Bold = open weights.** DD = Dynamic Degree,
VI-Subj = Video-Image Subject Consistency.

| Model | Access | Date | Total | **DD** | VI-Subj | Motion Smooth | Quality |
|---|---|---|---|---|---|---|---|
| **DynamiCrafter-CIL-512** | open (unlabelled) | 2024-11-19 | 87.45% | **83.01%** | 95.79% | 97.06% | 82.15% |
| DreamX-World-1.0 | unlabelled | 2026-05-20 | 90.49% | **72.11%** | 98.27% | 98.52% | 83.24% |
| **DynamiCrafter-512** | Open Source | 2024-07-22 | 86.99% | **69.67%** | 97.21% | 96.84% | 80.46% |
| **Magi-1** | Open Source | 2025-04-21 | 89.28% | **68.21%** | 98.39% | 98.68% | 82.44% |
| Steamer-I2V | unlabelled | 2025-05-17 | 89.38% | 68.13% | 98.02% | 98.47% | 82.25% |
| MUG-V | unlabelled | 2025-04-25 | 88.46% | 57.24% | 98.82% | 98.90% | 81.55% |
| Gen-4-I2V (Runway) | API | 2025-05-20 | 88.27% | 55.20% | 97.84% | 98.99% | 80.89% |
| VISTA | unlabelled | 2025-06-18 | 84.29% | 54.31% | 93.37% | 97.81% | 80.16% |
| **Wan2.2-TI2V-5B** (Qwen prompt-opt) | Open Source | 2026-02-12 | 88.80% | **52.85%** | 98.43% | 98.65% | 81.30% |
| **Wan2.2-I2V-A14B** (w/o prompt-opt) | Open Source | 2026-02-07 | 88.16% | **52.85%** | 97.52% | 98.32% | 80.50% |
| **Pusa-V1.0** | open (unlabelled) | 2025-07-28 | 87.32% | 52.60% | 97.64% | 98.48% | 79.80% |
| **SVD-XT-1.0** | Open Source | 2024-07-22 | — | 52.36% | 97.52% | 98.09% | 80.11% |
| **Pi** | unlabelled | 2025-03-18 | 89.08% | 49.93% | 98.67% | 99.18% | 81.95% |
| **Step-Video-TI2V** | unlabelled | 2025-03-14 | 88.36% | 48.78% | 97.86% | 99.24% | 81.22% |
| **Wan2.2-I2V-A14B** (Qwen prompt-opt) | Open Source | 2026-03-06 | 88.68% | **48.62%** | 98.60% | 98.22% | 80.85% |
| **DynamiCrafter-1024** | Open Source | 2024-07-22 | 87.76% | 47.40% | 98.17% | 97.38% | 80.50% |
| ToMoviee-2.0 | Close Source | 2025-09-08 | 89.76% | 47.07% | 99.05% | 99.10% | 81.06% |
| **SVD-XT-1.1** | Open Source | 2024-07-22 | — | 43.17% | 97.51% | 98.12% | 79.40% |
| **DynamiCrafter-256** | Open Source | 2024-07-22 | 85.25% | 40.57% | 97.05% | 97.83% | 77.49% |
| JT-CV | unlabelled | 2026-03-24 | 88.95% | 38.70% | 99.14% | 99.25% | 80.46% |
| **CogVideoSFT** | open (unlabelled) | 2024-10-23 | 87.98% | 36.51% | 97.67% | 98.35% | 78.77% |
| **SEINE-512x320** | Open Source | 2024-07-22 | 84.88% | 34.31% | 96.57% | 96.68% | 77.37% |
| **CogVideoX-5b-I2V** | Open Source | 2025-03-31 | 86.70% | 33.17% | 97.19% | 98.40% | 78.61% |
| **Dynamic-I2V-5B** | open (unlabelled) | 2025-05-28 | 88.45% | 27.15% | 98.83% | 98.88% | 78.78% |
| **SEINE-512x512** | Open Source | 2024-07-22 | 85.52% | 27.07% | 97.15% | 97.12% | 78.37% |
| **I2VGen-XL** | Open Source | 2024-07-22 | 85.28% | 26.10% | 96.48% | 98.34% | 78.44% |
| **I2VGen-XL** (trim last 2 frames) | Open Source | 2024-07-22 | 86.09% | 24.96% | 97.52% | 98.31% | 79.21% |
| **VideoCrafter-I2V** | Open Source | 2024-07-22 | 82.57% | 22.60% | 91.17% | 98.00% | 78.84% |
| **HunyuanVideo-I2V** | Open Source | 2025-06-13 | 86.82% | **22.20%** | 98.53% | 99.23% | 78.54% |
| **ConsistI2V** | Open Source | 2024-07-22 | 84.07% | 18.62% | 95.82% | 97.38% | 76.22% |
| STIV (Apple) | Close Source | 2024-12-20 | 86.73% | 15.28% | 98.96% | 99.61% | 79.98% |
| **LTX-2-I2V** (w/o prompt-opt) | Open Source | 2026-02-06 | 87.59% | **8.54%** | **99.38%** | **99.29%** | 78.65% |
| **Animate-Anything** | Open Source | 2024-07-22 | 86.48% | **2.68%** | 98.76% | 98.61% | 78.71% |
| **CogVideoX1.5-5B-I2V** | Open Source | 2025-03-31 | 71.58% | *(row malformed)* | 96.46% | *(40.98%?)* | 50.90% |

### What this leaderboard actually tells us

**The frozen-frames trap is confirmed, quantitatively, and it is the dominant failure
mode in the whole field.** The team lead's suspicion is exactly right:

- **LTX-2-I2V** has the *highest* Video-Image Subject Consistency in the table (99.38%),
  the *highest* Motion Smoothness (99.29%), a respectable Total of 87.59% — and a Dynamic
  Degree of **8.54%**. Over 91% of its clips were classified as not moving. This is
  literally "literally just frozen frames" with a leaderboard rank.
- **Animate-Anything**: DD 2.68% with 98.76% VI-Subject. Named for animation; 97% of its
  clips don't animate.
- **STIV (Apple)**: highest Motion Smoothness on the board (99.61%), DD 15.28%.
- Rank-order by Total Score is close to useless for us: Total folds DD in as one of nine
  roughly-equal dimensions, so a model can be top-10 overall while being static.

**Consistency and dynamism trade off, visibly.** The highest-DD model
(DynamiCrafter-CIL-512, 83.01%) has the second-*lowest* VI-Subject Consistency among
credible entries (95.79%). Its whole published point is fixing "conditional image
leakage" — i.e. deliberately weakening the model's tendency to copy the input frame.
That is the exact dial between our two top concerns, and it is a dial, not a free lunch.

**The best open-weight compromise on this board is Magi-1** — DD 68.21% *with* VI-Subject
98.39% and Total 89.28%, the only open-weight entry that is simultaneously top-4 on
dynamism and top-quartile on faithfulness. That is a benchmark observation, not a
recommendation; we have not tested it and it is a 24B-class model (VRAM check needed —
that's res-licence/res-speed territory, not mine).

**Our incumbent Wan 2.2 sits mid-pack on dynamism: DD 48.62–52.85%.** Roughly half its
clips get classified static. So the frozen-beat problem we hit is a *known, measured
property of the model we are using*, not a mystery in our recipe. Three separate Wan 2.2
submissions exist (5B, A14B with and without Qwen prompt optimization); note the
prompt-optimized A14B scores *lower* DD (48.62%) than the un-optimized one (52.85%),
while scoring higher on faithfulness — prompt rewriting moved it along the same
trade-off curve, toward static.

### Caveats on this leaderboard — read before quoting it

1. **Self-submitted and self-sampled.** Anyone can generate their own videos and upload
   the result JSON. The `Sampled by` / `Evaluated by` / `Certification` columns exist
   precisely because most rows are not independently verified. Vendors submitting their
   own numbers is the norm here.
2. **The `Accessibility` column is broken.** Several rows carry `None`, an empty string,
   or a *date* where open/closed should be (Dynamic-I2V-5B: "2025-05-28"; Pusa-V1.0:
   "2025-07-22"). So VBench-I2V does **not** cleanly separate open weights from closed
   APIs — I reconstructed the open/closed labels above from the linked repos, and marked
   the ones VBench itself leaves unlabelled.
3. **At least one row is corrupt.** CogVideoX1.5-5B-I2V's columns are shifted (Motion
   Smoothness 40.98%, Imaging Quality 97.07%, Total 71.58%). Don't cite that row.
4. **Prompt/settings are not held constant.** Entries differ in resolution, frame count,
   scheduler, steps, and whether an LLM rewrote the prompt — the two Wan 2.2 A14B rows
   differ *only* in prompt optimization and land 4 DD points apart. Cross-row differences
   of a few points are noise.
5. **Nothing here is 9:16 vertical or anime.** The VBench-I2V prompt set is general
   photographic/cinematic content at landscape aspect. Zero anime or cel-animation
   entries; no AnimateDiff-family entry at all.

### VBench-2.0 — text-to-video only, but one dimension is interesting

12 rows, retrieved 2026-08-04, submissions dated 2025-03-28 → 2026-04-01. **There is no
VBench-2.0 I2V track**, so it cannot rank our use case. It is also thin and
API-weighted: only 4 open-weight entries (Wan2.1 T2V-1.3B, StepVideo, HunyuanVideo,
CogVideoX-1.5), all submitted in early 2025 — no Wan 2.2 on VBench-2.0 at all.

Relevant rows (Total / Instance Preservation / Dynamic Attribute / Motion Rationality):

| Model | Access | Date | Total | Instance Preserv. | Dynamic Attr. | Motion Rational. |
|---|---|---|---|---|---|---|
| Veo 3 | API | 2025-09-04 | 66.72% | 92.98% | 63.74% | 45.98% |
| JT-CV | unlabelled | 2026-04-01 | 64.60% | 73.53% | 54.21% | 60.34% |
| ABot-World v0.1 | unlabelled | 2026-03-21 | 64.47% | 92.98% | 61.90% | 52.87% |
| Vidu Q1 | API | 2025-04-21 | 62.70% | 86.55% | 55.68% | 45.40% |
| ToMoviee 2.0 | API | 2025-09-18 | 61.78% | 85.96% | 61.17% | 48.85% |
| **Wan2.1 (T2V-1.3B)** | Open Source | 2025-03-28 | 60.20% | 88.89% | 45.42% | 39.08% |
| Seedance 1.0 Pro | API | 2025-06-26 | 59.81% | 80.92% | 44.32% | 47.70% |
| Kling 1.6 | API | 2025-03-28 | 59.00% | 92.40% | 19.41% | 38.51% |
| Sora-480p | API | 2025-03-28 | 58.38% | 94.15% | 8.06% | 34.48% |
| **StepVideo** | Open Source | 2025-03-28 | 55.78% | 84.21% | 8.06% | 37.36% |
| **HunyuanVideo** | Open Source | 2025-03-28 | 55.30% | 92.40% | 22.71% | 34.48% |
| **CogVideoX-1.5** | Open Source | 2025-03-28 | 53.35% | 82.46% | 24.18% | 33.91% |

`Instance Preservation` is the closest thing in any public benchmark to *"did the model
invent a second stem"* — it asks whether the number and identity of objects stays stable
over the clip. But it is measured **from a text prompt, not from a conditioning image**,
so it catches objects appearing mid-clip, not objects that were never in our approved
still. Partial coverage of our concern #2 at best. See §4.

Also of note: **VBench-I2V Arena launched March 2026** — a browser for the actual
generated videos behind the leaderboard rather than just scores. That is worth a human
look before we trust any number above; scores hide a lot.


