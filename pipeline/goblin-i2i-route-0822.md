# The goblin img2img-from-canon route (2026-08-22)

Round one's reasoning lived in a deriver docstring and a commit message. Round
two closed the route, so it gets a home.

## 1. Where this started, and what round one bought

Sixteen rounds of goblin face work all moved a WORD or an IP-ADAPTER SCALE. The
founder vetoed the result four times, most recently all four eye rounds
including r11a — "these are not my goblin". `pipeline/canon.yaml`
`route_closure_2026_08_22` forbids any further face tag, adapter scale or
reference re-crop.

The reason those rounds could not work was measured without being read: an
IP-Adapter reference is ENCODED — CLIPImageProcessor resizes to 224 and
centre-crops — so his face arrives as a few hundred embedding tokens and the
denoiser RESOLVES a face out of animagine's prior. Round nine's own numbers said
so out loud: at sq65 (58.9 % of the frame encoded) the eye came back a green
anime iris; at sq45 (28.3 %) it came back closer. **Less of his face reaching the
encoder produced more of his face in the output.**

**Round one (`ep2-b13-i2icanon-*-0822`) sent his pixels as PIXELS.**
`taste/refs/goblin-canon-founder-0821.png` became the INIT, not the reference,
with an all-white mask turning `inpaint_fruit.py` on base weights
(`unet.in_channels=4`) into plain img2img at `--pad-crop 0`. It worked:

- **his eye reached an output for the first time in sixteen rounds**
- the face breaks between **0.40 and 0.45** — measured once, by a 0.55 probe
  filed as a probe and not a candidate
- and round one named, in advance, the thing it did not test: at 0.30–0.45 the
  init owns the composition, so the figure stays STANDING and beat 13 is SEATED

## 2. Round two: the pose does not adopt, and the reason is the reason the face survives

`ep2-b13-i2icnet-{s30,s35,s40}-0822`. Round one's command line plus four flags:
`xinsir/controlnet-openpose-sdxl-1.0` at scale 1.0 on
`jerry-canon-h37fsit-0821.png` — beat 13's seated pose authored at head_frac
0.370, the proportion measured off the founder's own image (337 px head, 912 px
figure, 2.71 heads), 832×1216, the init's exact size. Strength the only
variable. 15 seconds of card, $0.

| cell | vs no-net twin | face E1–E5 | pose P1 | J1 |
|---|---|---|---|---|
| s30 (0.30) | 15.05 | **PASS** | FAIL — standing | FAIL |
| s35 (0.35) | 19.00 | **PASS** | FAIL — standing | FAIL |
| s40 (0.40, the ceiling) | 25.13 | **PASS** (palette warms) | FAIL — standing | FAIL |

**The net was not inert.** `s30` differs from its no-net round-one twin — same
strength, same seed 20260823, same words — by mean abs **15.05**, against that
twin's own departure from the init of **7.13**. The net moved more than twice as
many pixels as the strength did. It moved grass, light and background. It did
not move the body: no knee bend, no hip drop, no seated fold, not even partial
adoption. The log confirms the stack was real —
`StableDiffusionXLControlNetInpaintPipeline, 1 net(s), scales 1.0`,
`HINT MAGNIFICATION 1.000x`, hint `832x1216, MATCHES the init`.

### THE FINDING

> **The face survives and the pose cannot move FOR THE SAME REASON. They are not
> two curves that fail to overlap; they are one knob read in two directions.**

img2img at strength *s* over *N* steps runs only the LAST *s·N* steps. At 0.30
with 40 steps that is **12 steps, entered at timestep index 28** — deep in the
low-noise regime. Global structure — where a body is and what pose it is in — is
decided in the HIGH-noise steps, and **a low-strength img2img never runs them**.

So the init's structure is preserved (his face survives) and the net's structure
cannot be imposed (the pose cannot change), and those are the same sentence. The
strength that would give a pose net the early steps it needs is far past 0.45,
where round one already measured the face gone.

**This also kills the obvious next lever before it is spent.** Raising the
conditioning scale cannot help: the scale multiplies residuals in steps that are
never executed. The pre-registered `round_3_lever` #1 on these specs is
therefore closed on a mechanism, not on a trial.

## 3. What the route IS good for, which is not nothing

Round one's result stands and is worth keeping. img2img-from-canon at ≤ 0.40
**does** make new pictures of him with his face intact — different light,
different grass, different background, at 5 seconds a frame for $0. It is a
**re-lighting and re-grounding route**, not a re-posing route. Any beat whose
staging is close enough to the canon image's standing pose can be plated this
way today.

What it cannot do is give him a NEW BODY POSITION, and most of episode two's
goblin beats need exactly that.

## 4. What is next, and it is not another round here

Round one's own fail-mode three, reached by a different road: **a LoRA trained
on his pixels.** That is the only remaining path that puts his identity into the
HIGH-noise steps, which is where a pose net also lives — a LoRA and a skeleton
can both act at strength 1.0 because there is no init competing with them. The
sapling LoRA work (`lora-sapling-*`, `derive_saplora_*`) is the same instrument
already running on a different subject, and the goblin dataset is cheap now for
a reason round one supplied: img2img-from-canon can generate augmented views of
him with his face intact, which is exactly what a training set needs.

**Two rounds, as promised, and it goes back to the founder either way.** No plate
was staged for any beat. `review/ep2-ship-0821` is untouched.

Sheet: `review/COMPARE/GOBLIN-i2icnet-r2-0822.png` (init, hint, the no-net twin,
and the three cells at one scale). `review/**/*.png` is gitignored — the frames
in `farm-out/ep2-b13-i2icnet-*` are the durable artifact and the sheet rebuilds
from them with `pipeline/compare_sheet.py`.

## 5. What the build left behind

- `inpaint_fruit.assert_hint_survives_crop` — §28 of `b08-arm-route-0819.md` as a
  guard (rc 15) instead of a paragraph. Selftest 32 → 41 assertions, golden
  byte-identity against `ep2-b08-str70-0820` still passing.
- The discovery that **no new pipeline was needed**: this driver already composed
  ControlNet inside an inpaint pipeline, and an all-white mask already made that
  pipeline img2img. See `b08-arm-route-0819.md` §29.
- `derive_goblin_i2i_0822.assert_no_face_terms` — the route closure's vocabulary
  as one shared assertion both derivers call.

## 6. Section 3 was half wrong, and the dataset lane is what measured it (2026-08-22)

Section 3 called this a **"re-lighting and re-grounding route"**. The
re-grounding half is wrong and should not be quoted again.

`derive_goblin_dataset_0822` ran 32 cells through it to build a goblin training
set, and the ground and the background did not move. j01 asked for `dry cracked
bare earth` at strength 0.40 and came back standing on the init's own meadow.
The batch then asked for twelve distinct backgrounds — a stone wall, a dark
forest, a barn wall, a ploughed field, a sand horizon, a wall of ferns — and
**all but two came back on that same meadow.**

**It is this document's own mechanism, read a third time.** A ground and a
background are GLOBAL STRUCTURE. Section 2 says global structure is decided in
the high-noise steps and that a low-strength img2img never runs them; that is
why the pose cannot move and why the face survives. It is also why the ground
cannot move. Three readings, one sentence.

**What the route actually delivers is LIGHT, PALETTE and FRAMING** — and the
framing only because the INIT is cut before the model sees it, never because a
word asked for it.

### And a second window, at the other end of the same knob

The dataset lane also measured something section 2 did not reach: **his eye
survives only inside a WINDOW of face fraction.**

| init | face | mag | result |
|---|---|---|---|
| full body | 15 % | 1.000x | eye SHAPE holds at every strength, **pupil yellow at 0.40 / 0.35 / 0.30 / 0.25 / 0.20** |
| native square | 22 % | 1.000x | **holds** at 0.30, 0.25, 0.20 |
| cowboy | 29 % | 1.387x | **holds** at 0.20; the eye opens toward round at 0.25 |
| magnified square | 49 % | 1.486x | drifts at 0.40, 0.20 **and 0.15** — its own floor |

Above the window, animagine's prior has enough latent area to re-resolve the
face and returns the round coloured iris and tall upswept ear that four founder
vetoes name. **Below it**, his eye is a handful of latent cells, a tiny dark
pupil inside a narrow almond cannot be carried at that resolution, and the prior
repaints the iris warm no matter how few steps run. The magnified square failed
at its floor for a third reason: 1.486x of LANCZOS makes a soft feature, and a
soft feature is not a weak instruction to a denoiser but an AMBIGUOUS one.

So the law this document states — *his pixels have to enter as PIXELS* — gets
two more clauses. **At a size the latent grid can hold, and not as an
interpolation of them.**
