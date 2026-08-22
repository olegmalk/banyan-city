# Posing a character LoRA whose dataset has one pose — external research + the in-house measurement that reframes it

**2026-08-22, the goblin v3 lane.** Grades are
`character-lora-sdxl-0820.md`'s: **DEMONSTRATED** (we ran it),
**MAINTAINER**, **COMMUNITY**, **FOLKLORE**.

---

## 0. The question, narrowed so it can be answered

`bnyjerry v2` draws his face and cannot be posed. The fix everyone converges on
is a v3 trained on POSED frames of him, so the question is not "how do I pose a
LoRA" — it is:

> **How do we produce N frames that are (a) recognisably HIM to the standard the
> founder ratified on 2026-08-22, and (b) in a lower-body configuration that is
> not two vertical legs — at `$0`, on SDXL / kohya / one RTX 5090?**

---

## 1. THE DIAGNOSIS WAS UNDERSTATED, AND THE CORRECTION CAME FROM OUR OWN MANIFEST — **DEMONSTRATED**

Every document in this tree says the pose is locked because *"21 of 21 training
frames are standing"*. Measured on `pipeline/lora/manifest-jerry-v2-0822.yaml`:

| framing | frames |
|---|---|
| upper body | 11 |
| cowboy shot (mid-thigh) | 8 |
| **full body** | **2** |

and the two full-body frames are `canon-full` and `canon-full-flip`, verified
byte-identical to `taste/refs/goblin-canon-founder-0821.png` and to its mirror
(mean abs delta 0.000, maxdiff 0, both directions).

**The standing prior is not 21 frames deep. It is one frame deep.** The trigger
has been shown this character's legs once, plus that once flipped. Round seven's
weight ladder and the two-pass's six cells were both hunting for a competing
lower-body configuration to fade *toward*; there is no second configuration in
the weights to fade to.

**And this is a known failure mode of exactly the dataset method our set was
built with.** The Civitai *Single Image LoRA* method — build a set by cropping
ONE reference into many views — names its crop list as *"Full Body, Cowboy shot
3/4 of the image, Upper Body, **Lower Body**, Face view, Closeup of bangs,
Closeup any other detail you want, Head out of image shot"*, and reports as a
standing limitation that it is *"difficult to add custom outfits in a non-frontal
pose"* and that the result is *"more suitable for supplementing an img2img or
inpainting based one"* than for free text-to-image
([Civitai — Single Image LoRA Part 2](https://civitai.com/articles/1058/single-image-lora-part-2)).
**COMMUNITY.** Our set has Full Body, Cowboy and Upper Body and **no Lower Body
crop at all**, which is the one entry on that list that would have carried leg
evidence.

---

## 2. THE CAPTION HYPOTHESIS IS DEAD, AND BOTH THE HOUSE AND THE COMMUNITY SAY WHY

`character-lora-sdxl-0820.md` §4 states the rule this tree followed, and its own
table puts `pose` in the KEEP column for `bnyjerry`:

> **Keep every tag that is a variable** — pose, expression, camera framing … A
> tag kept in the caption stays promptable; a tag deleted becomes mandatory.

We did that. All 21 captions name `standing`, and pose is mandatory anyway
(`B5_pose_via_words`: FAILS). The same 21 files, same scheme, generalise the
SETTING cleanly — a snowy blue night and a sunset beach out of a dataset where
every frame stands in one hazy meadow.

**That is a controlled experiment inside one training run — DEMONSTRATED:**

| axis | dataset variance | captioned on all 21 | promptable after training? |
|---|---|---|---|
| setting | zero (one meadow) | yes | **YES** |
| pose | zero (one pose, and only 2 frames show a leg) | yes | **NO** |

**The community rule, stated correctly, predicts this.** Scenario's captioning
guidance is that *things you put in every caption become the constants the model
learns, while things you vary become variables it can be prompted with at
inference*, and that a dataset needs the variation to exist in the PIXELS
([Scenario — Advanced Captioning](https://help.scenario.com/articles/5782148871-advanced-captioning)).
The practitioner phrasing is blunter: *the same caption on every image means the
model has nothing to vary against* — and, on our exact case, *if all training
images show only one pose, the model will bind that pose to your character, and
the trigger word will absorb it regardless of how you tag it*
([offlinecreator — captioning guide](https://offlinecreator.com/guide/how-to-caption-lora-dataset),
[trigger-word guide](https://offlinecreator.com/guide/lora-trigger-word-guide)).
**COMMUNITY, and it converges with our measurement.**

**So `character-lora-sdxl-0820.md` §4 needs one clause added, and it is the
single most consequential correction in this file:**

> A caption tag keeps an attribute steerable **only where the attribute varies
> in the dataset**. Naming an attribute the dataset holds constant is a tag with
> nowhere to attach. It is free to write, which is why it reads as insurance and
> is not.

The setting axis is not a counterexample to that — it is the boundary case that
proves it. The base checkpoint varies backgrounds freely for *any* subject, so
`hazy meadow` had somewhere to attach outside the LoRA. Nothing outside the LoRA
knows what this creature's legs look like: the trigger is the only source, and
it has one picture.

**Unit 3 is therefore spent before it is asked.** "Caption the standing prior
away in v3" was tested in v2 and failed, and the reason it failed is not a
wording that can be improved.

---

## 3. THE ROUTE WE BUILT, AND THE COMMUNITY PRECEDENT FOR IT

Full detail in `pipeline/goblin-lowerbody-route-0822.md`. Four samples, ~100 s
of card, `$0`: his head held OUTSIDE an SDXL inpaint mask (base weights,
`unet.in_channels == 4`, so the unmasked latent is restored every timestep and
cannot drift **at any strength**), the legs generated INSIDE it at strength 0.95
against an openpose skeleton, **no LoRA in the pass**. It produced a seated
goblin and then a kneeling one, and the hint beat a contradicting noun.
**DEMONSTRATED.**

**This is a documented practice and we did not invent it.** "Change the
character but keep the pose and the background" via inpaint + ControlNet is an
established workflow
([Mikubill/sd-webui-controlnet discussion #748](https://github.com/Mikubill/sd-webui-controlnet/discussions/748)),
as is masking a region of a character and regenerating it under an OpenPose hint
while the rest is preserved
([Next Diffusion — outfit change with inpaint + OpenPose](https://www.nextdiffusion.ai/tutorials/change-character-outfit-with-stable-diffusion-inpaint-and-controlnet)).
**COMMUNITY.**

**What is not well documented is using it as a DATASET FACTORY.** The Single
Image LoRA method above scales a set by *"img2img and ControlNet reference"* and
recommends the resulting LoRA be used to *supplement* an inpainting workflow —
the reverse of what we are doing, which is to use the inpainting workflow to
manufacture the training set. No source found states the dataset-factory
direction outright, so **it is DEMONSTRATED here and FOLKLORE elsewhere**; the
honest read is that we are one frame ahead of the write-ups, not that we are
doing something the field knows is wrong.

**A hard mask is the strong form of "lock the identity region".** The
alternatives — regional prompter, attention couple, per-region LoRA — are
soft: `pipeline/research/ipa-ref-framing-0821.md` §5 already measured in this
tree that **masked IP-Adapter leaks**. A latent-blend mask does not leak; it is
arithmetic. Nothing found in this pass beats it for this job.

---

## 4. THE ONE ROUTE THAT COULD RESCUE THE WEIGHTS WE ALREADY HAVE — LoRA BLOCK WEIGHT

Every other lever spends a training run. This one does not: it re-weights
`bnyjerry v2` **at inference**, per UNet block, on the hypothesis that the
blocks carrying his face are not the blocks carrying his standing composition.

- The tool is real and mature: `sd-webui-lora-block-weight`
  ([hako-mikan](https://github.com/hako-mikan/sd-webui-lora-block-weight)) and
  its successor, which reports that **input blocks retain structural identity
  (facial symmetry, hair shape, facial features)** while **output blocks house
  background detail and aesthetic rendering**, and ships opposed presets —
  a CHARACTER preset that governs identity mapping and a LAYOUT preset that
  *"extracts camera angle, body pose, or background geometry"* and *"copies the
  composition and placement skeleton of the training set"*
  ([lora-block-weight-neo README](https://github.com/SiliconeShojo/lora-block-weight-neo)).
  For SDXL it notes 12 attention blocks expanded to a 26-block representation.
  **COMMUNITY.**
- There is paper-grade backing for block-level separation of identity from
  style: *Block-wise LoRA: Revisiting Fine-grained LoRA for Effective
  Personalization and Stylization*
  ([arXiv 2403.07500](https://arxiv.org/abs/2403.07500)), whose abstract claims
  images *"faithful to input prompts and target identity and also with desired
  style"* from per-block fine-tuning. **PAPER — and its abstract does not name
  which blocks do what; the block map above is COMMUNITY, not published.**
- **It is runnable on OUR stack, and that is now ASSERTED rather than hoped.**
  The docs say `set_adapters()` accepts a nested dict instead of a scalar
  ([Load adapters](https://huggingface.co/docs/diffusers/main/using-diffusers/loading_adapters),
  [using_peft_for_inference](https://github.com/huggingface/diffusers/blob/main/docs/source/en/tutorials/using_peft_for_inference.md))
  — but those docs are `main` and the box runs 0.29.2, so it was read off the
  box's own installed source instead of believed. **DEMONSTRATED, 2026-08-22, on
  the rtx5090:**

      diffusers 0.29.2 / peft 0.12.0
      UNet2DConditionLoadersMixin.set_adapters(adapter_names,
          weights: Optional[Union[float, Dict, List[float], List[Dict], List[None]]])
      ... weights = _maybe_expand_lora_scales(self, weights)

  and `unet_loader_utils._maybe_expand_lora_scales_for_one_adapter` documents in
  its own docstring that it turns
  `{"down": 2, "mid": 3, "up": {"block_0": 4, "block_1": [5, 6, 7]}}` into
  per-transformer scales. **The feature is present in the version we run.**
- **But the driver cannot use it as written, and that is the real cost.**
  `inpaint_fruit.py:877` does `pipe.fuse_lora(lora_scale=...)` — it BAKES one
  scalar delta into the UNet tensors, and its own selftest asserts the fuse
  happens before `from_pipe`. Per-block scaling needs `set_adapters` with the
  fuse skipped, so the sweep is an eight-line arm on the driver plus a selftest
  clause, not a spec-only change. **DEMONSTRATED, in-house.**
- Second caveat: `set_adapters()` **scales attention weights only**; ResNets and
  samplers stay at 1.0. If the standing prior lives outside attention, the lever
  cannot reach it. **MAINTAINER.**

**Why this is worth one card-hour anyway.** Every other candidate costs a
training run and produces a new checkpoint to grade. This one costs a sweep on
weights that already exist and whose identity bar already passes, and its
failure is informative: if no block split keeps the face while freeing the
composition, that is the fourth independent confirmation that the prior is a
DATASET property and not a placement one — the same conclusion the sapling lane
reached about B3 across three datasets and two caption schemes.

---

## 5. THE ROUTES THAT WERE RANKED AND ARE NOT RECOMMENDED

- **Video / character-animation harvest** — drive the single reference through
  poses with MimicMotion, Animate Anyone, Wan-Animate or AnimateDiff and harvest
  frames as training data. The models are real and open
  ([MimicMotion](https://github.com/tencent/MimicMotion),
  [AnimateDiff](https://github.com/guoyww/animatediff/),
  [Wan-Animate, arXiv 2509.14055](https://arxiv.org/html/2509.14055v1)), and
  there is directly adjacent published work — *PoseGen* uses in-context LoRA
  finetuning that *"inject[s] subject appearance at the token level for identity
  preservation, while simultaneously conditioning on pose information at the
  channel level"* ([arXiv 2508.05091](https://arxiv.org/html/2508.05091v1)).
  **But nothing found documents frame-harvest-as-LoRA-dataset with identity-drift
  numbers**, these are human-video models pointed at a chibi non-human, and it is
  a new stack, new weights and new VRAM on a box that already has a working
  `$0` route. **Not recommended now. Reconsider only if §3 fails to scale past
  four stances.**
- **3-D lift and repose** (CharacterGen / TripoSR / VRoid / DesignDoll →
  render → img2img). Not researched to a citation in this pass — deprioritised
  once §3 landed. Recorded as **NOT INVESTIGATED**, not as rejected.
- **IP-Adapter FaceID / InstantID / PhotoMaker.** Structurally inapplicable and
  the reason is one sentence: that family is built on InsightFace human-face
  embeddings, and the subject is a green goblin with a 2.6-head chibi skull. The
  plain image-prompt IP-Adapter is a different thing and this tree has already
  measured it — `b08-arm-route-0819.md` §11: it is an **attribute** instrument
  that *"did NOT govern geometry"*. It is the wrong tool for a pose problem.
  **DEMONSTRATED, in-house.**
- **Regularization / class images.** `character-lora-sdxl-0820.md` §3 already
  ruled these out on a kohya discussion — they *"either massively overfit or
  dampen training to nothing"*. Nothing in this pass changes that, and they
  would not supply leg pixels for THIS creature in any case.

---

## 6. THE RANKING, BY EXPECTED VALUE PER CARD-HOUR

1. **Add 3–4 posed full-body frames from §3 to an otherwise byte-identical v2
   dataset, and retrain.** The opposition is two frames of one picture (§1), so
   a handful of posed frames makes posed the majority of everything the trigger
   has ever seen below the waist. One variable against v2: the added frames.
   Spec in `goblin-lowerbody-route-0822.md` §6.
2. **A LoRA Block Weight sweep on the v2 weights (§4).** The dict API is
   confirmed present on the box, so the only build is an eight-line
   `set_adapters`-instead-of-`fuse_lora` arm on `inpaint_fruit.py`. Costs no
   training run, and its failure is a real finding either way.
3. **A `Lower Body` crop pass**, which the method our set came from lists and our
   set omits (§1). It is free — it is a crop of the canon — and it is the
   cheapest possible increase in leg evidence, though it adds no new POSE.
4. Everything in §5. Not now.

---

## 7. Method note, and an honest limit on this file

Two research subagents were dispatched at the full brief — image-space puppet
warping, 3-D lift, video harvest, IP-Adapter, regional prompting, block weights,
caption theory — and both overran without returning. **The citations above were
gathered directly and the coverage is narrower than the brief asked for**: the
3-D track is uninvestigated and the video-harvest track is cited for existence
rather than for the dataset use. What IS settled is settled on sources, and
what is not is labelled.

The two claims this file most wanted are both answered: the zero-variance
caption claim has independent community support (§2) and block-weighting is real,
mapped and runnable on our stack (§4).

## Sources

- [Civitai — Single Image LoRA Part 2](https://civitai.com/articles/1058/single-image-lora-part-2)
- [Scenario — Advanced Captioning](https://help.scenario.com/articles/5782148871-advanced-captioning)
- [offlinecreator — How to Caption a LoRA Dataset](https://offlinecreator.com/guide/how-to-caption-lora-dataset)
- [offlinecreator — LoRA Trigger Word Guide](https://offlinecreator.com/guide/lora-trigger-word-guide)
- [hako-mikan/sd-webui-lora-block-weight](https://github.com/hako-mikan/sd-webui-lora-block-weight)
- [SiliconeShojo/lora-block-weight-neo](https://github.com/SiliconeShojo/lora-block-weight-neo)
- [Block-wise LoRA, arXiv 2403.07500](https://arxiv.org/abs/2403.07500)
- [diffusers — Load adapters](https://huggingface.co/docs/diffusers/main/using-diffusers/loading_adapters)
- [diffusers — using_peft_for_inference](https://github.com/huggingface/diffusers/blob/main/docs/source/en/tutorials/using_peft_for_inference.md)
- [Mikubill/sd-webui-controlnet discussion #748](https://github.com/Mikubill/sd-webui-controlnet/discussions/748)
- [Next Diffusion — outfit change with inpaint + OpenPose](https://www.nextdiffusion.ai/tutorials/change-character-outfit-with-stable-diffusion-inpaint-and-controlnet)
- [Tencent/MimicMotion](https://github.com/tencent/MimicMotion)
- [guoyww/AnimateDiff](https://github.com/guoyww/animatediff/)
- [Wan-Animate, arXiv 2509.14055](https://arxiv.org/html/2509.14055v1)
- [PoseGen, arXiv 2508.05091](https://arxiv.org/html/2508.05091v1)
