"""002b goblin wave — draw ONE sample against the founder's goblin definition.

WHY THIS FILE EXISTS. `render_wave_goblin.py` (box-only, `C:\\banyan-farm\\
wave-goblin-prep\\`) measures the fifteen wave drafts and then stops: its last
branch prints "RENDERING IS GATED … Re-run with --beat <n> once he has" and
returns 8. On 2026-08-10 the founder defined the goblin, `--beat 04` was passed,
and it returned 8 anyway — because that file contains no rendering code at all.
No torch, no diffusers, no image write. `WAVE-PREP-0810.md` says
`run-wave-sample.cmd` "draws ONE sample"; it cannot, and never could.

So this is the render half the harness's own message points at. It does NOT
touch the harness and does NOT weaken its refusal: the whole-wave path there
still exits 8. Prompt construction is IMPORTED from it rather than copied, so
the string this sends is the string that was measured, by the same code.

THE ONE-SAMPLE RULE IS THE POINT, not a formality (CLAUDE.md, founder
2026-08-03). `--beat` is mandatory and takes exactly one integer: there is no
"all beats" path in this file to forget to guard. His definition is a RECIPE
CHANGE, so one beat renders and his verdict on it releases the other fourteen.
The K recipe cost an hour twice by skipping to fifteen.

`--goblin-def` is mandatory too, and that is deliberate. The harness defaults it
to r8's `green skin, plump` — the steward's own pair. Letting that default reach
a render would draw the steward's theory of the goblin under the founder's name,
which is the exact error ledger record 33 was graded a miss for.

  python render_wave_sample.py --harness C:\\banyan-farm\\wave-goblin-prep
      --root <repo> --beat 4 --goblin-def "green skin, tusks" --task <id>

$0 — local GPU, no provider, nothing published.
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


def sidecar(png: Path, *, seed: int, row: dict, secs: float, task: str,
            goblin_def: str, harness_sha: str, drafts_sha: str, wg) -> None:
    """§7.2 provenance, written at render time beside the frame."""
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())

    lines = [
        "# Still provenance (7.2), written AT RENDER TIME by render_wave_sample.py",
        "# on the rtx5090. ONE SAMPLE against the founder's goblin definition —",
        "# not a wave. The other fourteen beats wait on his verdict on this one.",
        "# The negative below is what the model actually saw; the recipe's own",
        "# negative, before the one deliberate removal, was:",
        f"#   {row['neg_full']}",
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
        "render_round: wave-sample-1",
        "candidate_set: wave1",
        f"count_tag: {row['tag']}",
        f"negative_terms_removed: {wg.DROP_NEG}",
        "goblin_definition_source: >-",
        block("the founder, 2026-08-10, verbatim: \"he is just a simple green "
              "goblin, nothing complex\". Recorded in cuts/cuts.yaml item 18 "
              "(settled) and taste/steward-model.ledger.yaml record "
              "ep2-goblin-definition-0810."),
        "goblin_definition_as_sent: >-",
        block(f"{goblin_def} — the steward's translation of his sentence into "
              "slot tags, NOT his words as tags. `green skin` is his one named "
              "attribute; `tusks` is his own shots.md ('one broken tusk') and "
              "the measured lever that took not-female to 4/4 in r9. `plump` "
              "was dropped: it is the steward's word, it is in neither his "
              "sentence nor his script, and record 42 read it as overshoot on "
              "2 of 4. He has not ratified this translation."),
        "prompts_from: wave-drafts.yaml (NOT shots.md — shots.md is untouched)",
        f"draft_variant: {row.get('variant', 'authored')}",
        f"harness_sha256: {harness_sha}",
        f"drafts_sha256: {drafts_sha}",
        "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
        f"positive_tokens: {row['pos_tok']}",
        f"negative_tokens_sent: {row['neg_tok']}",
        f"extra_negative_tier: {row['extra_neg_tier']}",
        "prompt: >-",
        block(row["pos"]),
        "negative_prompt: >-",
        block(row["neg"]),
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
    ap.add_argument("--beat", type=int, default=None,
                    help="EXACTLY ONE beat. Omitting it is refused, not defaulted.")
    ap.add_argument("--goblin-def", default=None,
                    help="tags filling {{GOBLIN}}. Mandatory: the harness default "
                         "is the steward's pair, not the founder's definition.")
    ap.add_argument("--task", default=None, help="queue/heartbeat id for provenance")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry", action="store_true", help="measure, draw nothing")
    # WHICH DRAFT TEXT TO SEND. Defaults to `authored`, so every caller written
    # before 2026-08-11 sends exactly the bytes it always did — including the
    # ungated goblin_ipa_* crossbeat jobs, which read `authored` for beats 2, 15
    # and 20 and must not have their prompt changed underneath them.
    # `authored_staged` is the 2026-08-11 staging fix (see wave-drafts.yaml's
    # header): the b15 sample proved the CHARACTER and failed on STAGING, three
    # of four seeds from behind with the sapling drifting to a houseplant.
    ap.add_argument("--variant", default="authored",
                    help="draft key to render: `authored` (default) or "
                         "`authored_staged`. Never falls back.")
    a = ap.parse_args()

    if a.beat is None:
        print("!! --beat is mandatory and takes ONE beat. This file has no "
              "whole-wave path: his definition is a recipe change, so ONE "
              "sample renders and his verdict on it releases the rest "
              "(CLAUDE.md, founder 2026-08-03).", flush=True)
        return 8
    if not a.goblin_def:
        print("!! --goblin-def is mandatory. The harness defaults to r8's "
              "`green skin, plump`, which is the STEWARD's pair — rendering it "
              "unlabelled would put the steward's goblin under the founder's "
              "definition. Pass his, explicitly.", flush=True)
        return 8

    harness = Path(a.harness).resolve()
    sys.path.insert(0, str(harness))
    import render_wave_goblin as wg                                  # noqa: E402

    root = Path(a.root).resolve()
    sys.path.insert(0, str(root / "pipeline"))
    import sd_prompt as sd                                           # noqa: E402

    if sd._clip_tokenizer() is None:
        print("!! no CLIP tokenizer here — compress() would drop different "
              "sentences than the box does and every count would be an "
              "estimate. Refusing.", flush=True)
        return 9

    drafts_path = harness / "wave-drafts.yaml"
    drafts = wg.load_drafts(drafts_path)
    if a.beat not in drafts:
        print(f"!! beat {a.beat} is not in {drafts_path.name}. Present: "
              f"{sorted(drafts)}", flush=True)
        return 4

    d = drafts[a.beat]
    # NO FALLBACK TO `authored`, DELIBERATELY. If the box's drafts file is stale
    # and lacks the requested key, silently sending the old text would render the
    # OLD staging under the NEW job id — the failure would be invisible in the
    # frames and would only surface as another round of "why is he facing away".
    if a.variant not in d:
        print(f"!! beat {a.beat:02d} ({d['slug']}) has no `{a.variant}` key in "
              f"{drafts_path.name}. Keys present: "
              f"{sorted(k for k in d if k.startswith('authored'))}. This box's "
              "copy of wave-drafts.yaml is older than the job that was queued "
              "against it — copy the repo's pipeline/wave-drafts.yaml over and "
              "re-run. Refusing rather than falling back.", flush=True)
        return 4
    authored = d[a.variant]
    # A draft may declare that it holds NO person — an object-reference sheet, a
    # prop drawn alone. That declaration is per-VARIANT and lives in the drafts
    # file as `object_sheet_variants`; every other variant on this beat keeps the
    # beat slot's count guard untouched. See render_wave_goblin.check.
    d = wg.apply_variant_declaration(d, a.variant)
    # THE GOBLIN-SLOT REFUSAL IS FOR BEATS THAT ARE SUPPOSED TO HAVE A GOBLIN.
    # It used to fire on ANY beat without the marker, which made the six guard
    # beats of this wave (05, 06, 07, 09, 10, 11) unrenderable by this file —
    # every one of them would have returned 4 the moment its spec was cleared,
    # and their specs were written and staged that way. A guard beat legitimately
    # has no goblin in it; render_wave_goblin.py's own equivalent check has
    # always excluded `kind == "guard"` for exactly this reason. Mirror it.
    if wg.GOBLIN_SLOT not in authored and d["kind"] != "guard":
        print(f"!! beat {a.beat:02d} ({d['slug']}, kind={d['kind']}) carries no "
              f"{wg.GOBLIN_SLOT} marker, so the founder's definition would have "
              "nowhere to go and this render would test nothing about the "
              "goblin. Pick a beat whose kind is goblin or two-subject.",
              flush=True)
        return 4

    row = wg.check(a.beat, d, authored.replace(wg.GOBLIN_SLOT, a.goblin_def), sd)
    row["variant"] = a.variant
    row["extra_neg_tier"] = d["extra_neg"]
    if row["faults"]:
        print("\n!! FAULTS — nothing drawn: " + "; ".join(row["faults"]),
              flush=True)
        return 1

    harness_sha = hashlib.sha256(
        (harness / "render_wave_goblin.py").read_bytes()).hexdigest()
    drafts_sha = hashlib.sha256(drafts_path.read_bytes()).hexdigest()
    task = a.task or f"ep2-b{a.beat:02d}-wave-sample-{int(time.time())}"

    print(f"\nONE SAMPLE — beat {a.beat:02d} {d['slug']}, 4 seeds, $0", flush=True)
    print(f"   draft variant: {a.variant}", flush=True)
    print(f"   goblin definition: {a.goblin_def!r}", flush=True)
    print(f"   task: {task}", flush=True)
    print(f"   harness sha256: {harness_sha}", flush=True)
    print(f"   drafts  sha256: {drafts_sha}", flush=True)

    if a.dry:
        print("\nDRY OK — 1 beat x 4 seeds = 4 frames, nothing drawn", flush=True)
        return 0

    out = Path(a.out).resolve() if a.out else harness / "out"
    out.mkdir(parents=True, exist_ok=True)

    import torch                                                     # noqa: E402
    from diffusers import StableDiffusionXLPipeline                  # noqa: E402
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(
        wg.BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s", flush=True)

    for i in range(4):
        seed = wg.SEED + a.beat + i * 1000
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=row["pos"], negative_prompt=row["neg"],
                   num_inference_steps=wg.STEPS, guidance_scale=wg.CFG,
                   generator=g, width=wg.W, height=wg.H).images[0]
        f = out / f"{a.beat:02d}-{d['slug']}-wave1-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, row=row, secs=secs, task=task,
                goblin_def=a.goblin_def, harness_sha=harness_sha,
                drafts_sha=drafts_sha, wg=wg)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills — ONE beat. The other fourteen wait on his verdict.",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
