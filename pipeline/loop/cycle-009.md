# Cycle 009 — the image model was the ceiling, my prompts were the floor

Founder verdict that opened this cycle, on the first assembled cut of episode 1:

> "what the heck? this looks like the first ai generated videos ever made lol"

and, when I proposed prompt fixes:

> "nah dude, the image generator you're using also looks like ai 5 years ago. i
> don't know if the video generator is like that, but the image generator you are
> using is definitely."

He was right, and he was right about the part I had stopped looking at. SD1.5 was
in the pipeline for exactly one reason — AnimateDiff required an SD1.5 checkpoint —
and when AnimateDiff was dropped for being "cool looking static", I kept its
dependency and never revisited it. The renderer was carrying a constraint whose
cause had already been removed.

## Method

Two-stage render, four beats of 001: beat 1 as a control (the one shot that had
worked) plus beats 3, 4 and 6, the three worst failures. Stage 1 is a still
(Animagine XL 3.1, an SDXL anime finetune, 832×1216); stage 2 animates it
(Stable Video Diffusion at 512×768). Same beats re-run after each fix, so every
comparison is like-for-like.

## What the swap actually proved

Stage 1 at ~30 s per still. Stage 2 at 4.3 min per clip, **median frame-to-frame
motion 11.3** where AnimateDiff measured 0.1–1.0 on the same beats — the "just
cool looking static" complaint is answered by the architecture, not by tuning.

And on picture quality the answer was split, which is why looking at the right
artefact mattered. The *video* frames looked worse than SD1.5's. The *stills* did
not: beat 1 came back as a clean, readable anime frame — flat colour, bold
lineart, correct subject — and the other three came back as coherent-looking
abstract shapes. Same model, same settings. So the model was not the variable in
those three failures. The prompts were.

I had been about to report "SDXL is worse" off the video contact sheet. The
stills were one command away.

## Three faults, all mine, all invisible until the stills were separated out

### 1. I was forbidding the thing the shot is made of

Beat 3's subject is a terminal resolving a line of output — it *is* text on a
screen. `text` sat in the renderer's standard negative prompt, and shots.md's
boilerplate closing line "no text" was extracted into the negative a second time
on top of it. That boilerplate means *no burned-in caption*, which is render_t3's
concern; the image model read it as "do not draw the subject". Beat 3 rendered as
abstract magenta shapes, twice, and I blamed the checkpoint.

Fixed in `sd_prompt.suppressed_negatives()`: a beat whose subject is a screen
un-negates `text`. Scoped to the **first clause**, because a passing mention is
not a subject — beats 1 and 4 say "faint monitor glow on his knuckles" and "cold
monitor light", where un-negating text would only invite gibberish signage into
shots that never asked for any.

### 2. Framing was present, and therefore ignored

Shot type was appended as a trailing tag (`", medium shot"`). It survived the
token budget, it survived the test suite — and the renderer paid no attention to
it. All four test beats came back extreme macro crops regardless of what they
asked for, including a *medium shot of a man* that drew a close-up of his chair.

Framing now heads the subject's own noun phrase — "Medium shot of a hunched man
tipping sideways out of his chair" — counted inside the 77-token budget rather
than prepended after the fitting loop had already run. The distinction from the
earlier failure that pushed framing to the end matters: that was a standalone
leading *sentence* ("macro shot.") which stranded the subject in third position.
Inside the phrase, the subject noun stays at token 3–4, where it still governs.

The old assertion was `"macro shot" in out`. True, and worthless. **Presence was
never the property worth testing; position is what the model weights.**

### 3. I did not read the model card

Animagine XL 3.1 is trained with aesthetic booster tags and lists `abstract` in
its recommended negative prompt. I had neither. What I got was literal abstract
shapes in a garish palette — the exact failure its card describes.

## Two more faults found while fixing those

**The approval gate could not read an approval it had been given.** `approved()`
built its leaf glob from the caller's argument string, but leaf ids are not
directory names: `001-capability-inventory/` holds `001-t0-d.yaml`. So `push 001`
found the founder's approval and `push 001-capability-inventory` reported "no T0
leaf found" for the same node, approved that morning. It failed *closed*, which
is the correct direction — but a gate that misreports a real approval is a gate
people learn to route around with `--technical-validation`, and then STEWARDSHIP
§6 is enforced by habit instead of by code. Constructing the prefix could not
have worked in general anyway (`004c-n` holds `004c-n-t0-a.yaml`); it now globs
the node's own `leaves/` dir, which belongs to exactly one node.

And: **the rule the founder cares most about had no test.** §6 is the one he
added by hand, and the function enforcing it was untested through eight cycles.
It has one now, including a case asserting it can still say no.

**Provenance recorded the wrong negative prompt.** Leaves logged the global `NEG`
rather than the per-beat one actually sent — a prompt pair that was never used
together, which is precisely the thing §7.2 exists to prevent.

## Three beats the framing fix could not reach

Diagnosed by sweeping all fifteen compressed prompts rather than only the four
under test — and they all miss the same way. I described **light in darkness**,
and the model reached for the sky.

| beat | asked for | rendered |
|---|---|---|
| 10 SENSE | rings of light pulsing through dark soil | a lightning bolt |
| 15 SOMETHING'S COMING | the same, faster | a comet |
| 12 UNDEFINED | a sapling stem straining in open ground | a potted houseplant |

Glowing shapes on near-black *is* a night sky unless the frame says otherwise,
and "underground cross-section" is not a composition SDXL has a prior for. Both
underground beats now open on "a solid wall of dark soil filling the entire
frame, seen from the side like a cutaway" — earth first and dominant, light only
after — with sky/stars/lightning/comet/space/horizon moved into the negative,
where a "not" actually counts. Beat 12 names its ground ("in open ground … in
bare soil") and excludes flowerpot/planter/windowsill/indoors.

This is `style.md`'s own rule finally reaching the prompts: **a shot is a subject
OR a vista, never a small subject inside one.**

## The habit behind all of it

Cycle 008 recorded "contrast cannot see meaning" after a guard passed a frame the
founder called a leaf on a lilypad. This cycle is the same error one level up: I
measured motion (11.3, good), contrast (57–162, good), and VRAM, and every number
said the render was healthy while three of four shots drew the wrong thing. Every
metric I had was a property of the *file*. None was a property of the *picture*.

The correction is not another metric. It is that the founder's eye is the only
instrument that reads meaning, so shots go in front of it early and in the form
that isolates the variable — stills separately from video, or the diagnosis lands
on the wrong stage.

## Status

- SDXL + SVD confirmed as the stack: real motion, and a coherent style family
  across shots, which was the "fifteen unrelated AI images" complaint.
- Five prompt/gate fixes committed; 244 checks pass, lint clean.
- Re-render of beats 1/3/4/6 done — verdict below.
- **Open, and the founder's call:** a style plate — one image defining the show's
  look, conditioned into every beat via IP-Adapter at ~0.3 — needs him to pick
  which frame *is* the show. That is a taste judgement (R4), not mine to make.

## Addendum — v39: two of four fixed, and the fault the fixes revealed

Same four beats, prompts repaired. Motion held (median 13.1). Beat 3's contrast went
66 → 110, which is what un-negating `text` should do.

| beat | v38 | v39 |
|---|---|---|
| 01 keyboard | hands on a keyboard, correct | correct, cleaner |
| 03 deploy-succeeded | abstract magenta shapes | **an actual screen**, teal display, cursor — no terminal text yet |
| 04 the-fall | abstract grey mush | **the room opens up** — desk, chair, papers lifting — and *nobody in it* |
| 06 too-blue | a field of blades | still a field of blades |

Beat 4 is the interesting one. The framing fix worked exactly as intended — a medium
shot that shows the desk, the chair and the papers coming off it — and the man the
beat is *about* is absent. Correct furniture, no person.

**Animagine is Danbooru-trained, and in that vocabulary a person is declared by a
count tag** — `1boy`, `1girl`, `2others` — before anything else in the caption.
Without one, the human is optional scenery. None of my prompts had one, and **93 of
the genome's 177 prompts open on a person.** Over half the show was asking for
people in a dialect the model does not read that way.

That is the second time this cycle the fault was me not reading how this model
expects to be addressed — the booster tags and `abstract` negative were the first.
The lesson is cheap and I keep re-learning it expensively: **read the model card
before blaming the model.**

Fixed with the same first-clause scoping used for `text`, plus a possessive rule,
because a false positive here is as bad as a miss: a ledger page "beneath a woman's
thumb" must not summon a whole woman, and a close-up of "a goblin's clawed fingers"
stays a shot of hands. Beat 1 of 001 is the proof — a pair of hands renders
correctly with no count tag at all, so body-part shots are left alone.

Beat 6 barely moved because "grass blades swaying at the edges" was out-competing
the single leaf that is the subject; the frame filled with what the clause named.
Cut, with grass/field/other-leaves in the negative.

**Standing shape of this cycle:** every fix so far has been the renderer speaking
the model's language, not a change to the show. Nothing in the narrative moved.
