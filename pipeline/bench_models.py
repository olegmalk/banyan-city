#!/usr/bin/env python3
"""Benchmark every licence-clean video model on one beat: TIME, MEMORY, CONCURRENCY.

Why this file exists (2026-08-04): dad's standing direction was to compare the
candidate models on the 5090 and report *how long each takes, how much memory it
consumes, and how many can run in parallel*. What the repo had instead was
`MODEL-COMPARISON.mp4` — a comparison of how the engines LOOK. Every cost figure
we hold is for one model (Wan 2.2 TI2V-5B), and the concurrency answer existed
only as a comment inside `wan_i2v.py` explaining a stall bug. This turns that
into a measurement anyone can re-run.

It is deliberately NOT a quality comparison. It renders the same beat, the same
still, the same seed, the same steps and size on each model, and reports numbers.
The clips are kept side by side so the founder can judge the picture himself (R4)
— the harness never scores taste.

MUST run on the render box (CUDA). On a machine with no GPU it refuses and exits
nonzero rather than emitting an estimated table: a guessed benchmark is worse
than no benchmark, because it gets quoted later.

    # on the 5090:
    python pipeline/bench_models.py --node 001 --beat 11 --steps 14 \
        --size 704x1280 --concurrency 1,2

Writes `pipeline/bench/bench-<UTC date>.yaml` (machine-readable, committed) and
prints the markdown table. Clips land in `pipeline/bench/clips/`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import video_task as vt          # noqa: E402  (PY, ROOT, gpu_vram_gb, MODEL_LICENCE)
from wan_i2v import MODELS       # noqa: E402

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "pipeline" / "bench"
CLIPS = BENCH / "clips"

# The `[i/n] wrote <path> in 240s (81 frames, 704x1280, 14 steps, peak torch
# 22.9GB, device 24.4/26GB)` line wan_i2v prints per clip. Parsed rather than
# re-measured so the harness and the renderer can never disagree about peak VRAM.
WROTE = re.compile(
    r"^\[\d+/\d+\]\s+wrote\s+(?P<out>.+?)\s+in\s+(?P<secs>[\d.]+)s\s+"
    r"\((?P<frames>\d+)\s+frames,\s+(?P<size>\d+x\d+),\s+(?P<steps>\d+)\s+steps,"
    r"\s+peak torch\s+(?P<peak>[\d.]+)GB,\s+device\s+(?P<used>[\d.]+)/"
    r"(?P<total>[\d.]+)GB\)", re.M)


def die(msg: str) -> "None":
    print(f"bench_models: {msg}", file=sys.stderr)
    raise SystemExit(2)


def shot_for(genome: str, node: str, beat: int) -> tuple[str, str, Path]:
    """(positive, negative, still) for one beat, built by PRODUCTION's own path.

    Deliberately reuses `parse_shots` + `motion_directions` + `video_prompt`
    rather than reading shots.md directly. A benchmark that feeds the models a
    prompt production would never send measures a pipeline nobody runs — and
    `video_prompt` is not cosmetic here: it strips the still-generation quality
    tags and moves the beat's "No X" prose into the real negative, which is the
    difference between animating the frame and redrawing it.
    """
    from generate_shots import parse_shots

    nodes = REPO / "genomes" / genome / "nodes"
    hits = sorted(d for d in nodes.iterdir() if d.name.startswith(f"{node}-"))
    if not hits:
        die(f"no node directory starting {node}- under {nodes}")
    d = hits[0]
    # utf-8 pinned: cp1252 mangles the em dash in "## Beat NN —" and parse_shots
    # then finds nothing (the msi's first-light failure, 2026-07-29)
    shots = {s["num"]: s for s in
             parse_shots((d / "shots.md").read_text(encoding="utf-8"))}
    s = shots.get(beat)
    if not s:
        die(f"beat {beat} not in {d/'shots.md'}")
    still = next((q for q in sorted((d / "stills").glob(f"{beat:02d}-*.png"))
                  if "REVOKED" not in q.name), None)
    if not still:
        die(f"no approved still for beat {beat:02d} in {d/'stills'}")
    act = (vt.motion_directions(d).get(beat)
           or vt.beat_actions(d / "node.md").get(beat))
    motion = "subtle continuous motion, gentle camera drift, living scene"
    pos, neg = vt.video_prompt(f"{act}. {motion}" if act else motion,
                               s["prompt"], beat=beat)
    return pos, neg, still


def render_once(model: str, prompt: str, neg: str, still: Path, out: Path,
                a) -> dict:
    """One clip in a FRESH process — the only way the card is actually empty at
    the start of the measurement (see wan_i2v.py's between-clips comment)."""
    cmd = [str(vt.PY), str(REPO / "pipeline" / "wan_i2v.py"),
           "--stage", "simple",
           "--embeds", str(vt.ROOT / f"bench-embeds-{model}.pt"),
           "--model", model, "--prompt", prompt, "--init", str(still),
           "--out", str(out), "--steps", str(a.steps), "--size", a.size,
           "--seconds", str(a.seconds), "--seed", str(a.seed),
           "--negative", neg,
           # ALWAYS, exactly as production does: the per-beat shake decision is
           # already baked into `neg` by video_prompt, and wan_i2v's global copy
           # would re-add the terms and undo it. Measured 3.3x motion cost.
           "--no-shake-neg", "--quantise", a.quantise]
    if a.offload:
        cmd.append("--offload")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    wall = time.time() - t0
    m = WROTE.search(r.stdout or "")
    if not m:
        tail = "\n".join((r.stderr or r.stdout or "").splitlines()[-8:])
        return {"model": model, "ok": False, "wall_s": round(wall, 1),
                "error": tail[:600]}
    sample = float(m["secs"])
    return {
        "model": model,
        "repo": MODELS.get(model, model),
        "licence": dict(vt.MODEL_LICENCE).get(model, ("", "UNKNOWN"))[1],
        "ok": True,
        # wall MINUS the sampler is load+encode+export. On 2026-08-03 that
        # overhead was ~10 of every 11 minutes for per-clip processes, which is
        # the entire argument for the batch path — so it gets its own column.
        "wall_s": round(wall, 1),
        "sample_s": round(sample, 1),
        "overhead_s": round(wall - sample, 1),
        "peak_vram_gb": float(m["peak"]),
        "device_used_gb": float(m["used"]),
        "device_total_gb": float(m["total"]),
        "frames": int(m["frames"]),
        "size": m["size"],
        "steps": int(m["steps"]),
        "quantise": a.quantise,
        "offload": bool(a.offload),
        "s_per_s_video": round(sample / (int(m["frames"]) / a.fps), 1),
        "clip": str(out.relative_to(REPO)),
    }


def render_concurrent(model: str, n: int, prompt: str, neg: str, still: Path,
                      a) -> dict:
    """Launch n renders at once and see whether the card takes it.

    This is the column that has never been measured. The prediction from
    `wan_i2v.py` is that n=2 does NOT fit on a 26GB card at 704x1280 — peak is
    22.9GB — and that Windows will PAGE rather than raise, so the failure looks
    like a stall, not an error. So this bounds itself with a timeout and reports
    a stall as a stall.
    """
    outs = [CLIPS / f"conc{n}-{model}-{i}.mp4" for i in range(n)]
    procs = []
    t0 = time.time()
    for i, o in enumerate(outs):
        cmd = [str(vt.PY), str(REPO / "pipeline" / "wan_i2v.py"),
               "--stage", "simple",
               "--embeds", str(vt.ROOT / f"bench-embeds-{model}-{i}.pt"),
               "--model", model, "--prompt", prompt, "--init", str(still),
               "--out", str(o), "--steps", str(a.steps), "--size", a.size,
               "--seconds", str(a.seconds), "--seed", str(a.seed + i),
               "--negative", neg, "--no-shake-neg"]
        if a.offload:
            cmd.append("--offload")
        procs.append(subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True,
                                      encoding="utf-8", errors="replace"))
    # A single-clip render is ~4 min at 14 steps. Allow n x that x a slack
    # factor, then call it a stall — the documented failure mode is a 46-minute
    # hang, and waiting it out teaches us nothing we cannot infer from "it did
    # not finish in n x solo time".
    budget = a.stall_factor * n * max(a.solo_hint, 60)
    stalled = []
    for p in procs:
        left = budget - (time.time() - t0)
        try:
            p.communicate(timeout=max(left, 5))
        except subprocess.TimeoutExpired:
            p.kill()
            stalled.append(p.pid)
    wall = time.time() - t0
    done = [o for o in outs if o.exists() and o.stat().st_size > 0]
    return {"model": model, "concurrency": n, "wall_s": round(wall, 1),
            "completed": len(done), "requested": n,
            "stalled": len(stalled),
            "throughput_clips_per_hour": (round(3600 * len(done) / wall, 2)
                                          if wall > 0 and done else 0.0),
            "verdict": ("fits" if len(done) == n and not stalled
                        else "does not fit — stalled" if stalled
                        else "partial failure")}


def table(rows: list[dict], conc: list[dict], card: str) -> str:
    L = [f"# Model benchmark — {card}", "",
         "Same beat, same still, same seed, same steps, same size. Numbers only —",
         "the picture is the founder's call (R4); the clips are side by side in",
         "`pipeline/bench/clips/`.", "",
         "| model | licence | size | steps | quant | offload | sample "
         "| load+export | total | s per 1s video | peak VRAM | of card "
         "| vs slowest |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    # "vs slowest" answers the iteration question directly: how many times
    # faster is a cheap proof pass than the shipping recipe.
    slowest = max((r["wall_s"] for r in rows if r["ok"]), default=0)
    for r in sorted(rows, key=lambda x: (not x["ok"], x.get("wall_s", 0))):
        if not r["ok"]:
            L.append(f"| `{r['model']}` | - | - | - | - | - | **FAILED** | - "
                     f"| {r['wall_s']}s | - | - | - | - |")
            continue
        speed = f"{slowest / r['wall_s']:.1f}x" if r["wall_s"] else "-"
        L.append(f"| `{r['model']}` | {r['licence']} | {r['size']} | {r['steps']} "
                 f"| {r['quantise']} | {'yes' if r['offload'] else 'no'} "
                 f"| {r['sample_s']}s | {r['overhead_s']}s | {r['wall_s']}s "
                 f"| {r['s_per_s_video']}s | {r['peak_vram_gb']}GB "
                 f"| {r['device_used_gb']}/{r['device_total_gb']}GB | {speed} |")
    if conc:
        L += ["", "## How many run in parallel", "",
              "| model | n | completed | wall | clips/hour | verdict |",
              "|---|---|---|---|---|---|"]
        for c in conc:
            L.append(f"| `{c['model']}` | {c['concurrency']} "
                     f"| {c['completed']}/{c['requested']} | {c['wall_s']}s "
                     f"| {c['throughput_clips_per_hour']} | {c['verdict']} |")
    for r in rows:
        if not r["ok"]:
            L += ["", f"**`{r['model']}` failed:**", "```", r["error"], "```"]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--genome", default="sapling")
    ap.add_argument("--node", default="001")
    ap.add_argument("--beat", type=int, required=True)
    ap.add_argument("--models", default=",".join(sorted(MODELS)),
                    help=f"comma list; known: {sorted(MODELS)}")
    ap.add_argument("--steps", type=int, default=14)
    ap.add_argument("--size", default="704x1280")
    # THE ITERATION QUESTION (founder, 2026-08-04): "do we have to test with
    # higher resolution, or can we drop the resolution and iterate faster?"
    # Not answerable from what we hold: the only res pair we ever measured also
    # changed --offload (462s at 480x832 WITHOUT it vs 240s at 704x1280 WITH
    # it), so it measured paging, not pixels. This sweeps size with everything
    # else pinned. 352x640 is half linear / a quarter of the pixels and still a
    # valid Wan bucket; below ~320 the 8x VAE downsample stops resolving the
    # subject at all, which is why the list does not go lower.
    # THE PAGING QUESTION (founder, 2026-08-04): "why do we have to page the
    # VRAM if we have 24GB of it? Don't have a model which doesn't require the
    # paging?" The model is not what fills the card — the T5 TEXT ENCODER is
    # ~11GB and the 5B transformer ~10GB, so ~21GB is resident before a single
    # activation. Two coded-but-unmeasured escapes exist, and both belong in
    # this table as rows rather than in an argument: 8-bit quantisation of the
    # transformer, and the two-stage encode/render split that drops the encoder
    # out of VRAM entirely (built for the 16GB box; on the 5090 it produced one
    # garbage clip because it bypassed the image conditioning — a bug, not a
    # law). Swapping to a "smaller model" does not help: AnimeGen IS Wan 2.2
    # finetuned, and the alternative A14B is nearly 3x bigger.
    ap.add_argument("--quantise-sweep", default="",
                    help="comma list from none,8bit,4bit. 8-bit should take the "
                         "transformer from ~10GB to ~5GB and may remove the "
                         "need to offload at all — never measured.")
    ap.add_argument("--sizes", default="",
                    help="comma list of WxH to sweep, e.g. 352x640,704x1280. "
                         "Overrides --size. Answers 'can we iterate at low res'.")
    ap.add_argument("--steps-sweep", default="",
                    help="comma list of step counts to cross with --sizes. "
                         "Steps are the other proof-pass lever: 14 steps "
                         "measured 188s vs 20 steps at 240s on 2026-08-03.")
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--seed", type=int, default=20260804)
    ap.add_argument("--offload", action="store_true", default=True,
                    help="on by default: measured 1.93x FASTER at 704x1280 "
                         "(462s -> 240s), because residency was paging")
    ap.add_argument("--no-offload", dest="offload", action="store_false")
    ap.add_argument("--concurrency", default="",
                    help="comma list of n to try, e.g. 1,2. Empty = skip.")
    ap.add_argument("--stall-factor", type=float, default=2.5)
    ap.add_argument("--solo-hint", type=float, default=300,
                    help="expected solo seconds; the concurrency budget is "
                         "stall_factor x n x this")
    ap.add_argument("--allow-no-gpu", action="store_true",
                    help="for testing the harness itself; the table it writes "
                         "is marked UNMEASURED and must not be quoted")
    a = ap.parse_args()

    try:
        vram = vt.gpu_vram_gb()
    except (FileNotFoundError, OSError):
        # the video venv does not exist on this machine at all (e.g. the Mac).
        # Guarded HERE and not in gpu_vram_gb, because production reads that
        # function to decide whether to batch — making it swallow a missing
        # interpreter would silently turn batching off on the render box.
        vram = 0.0
    if vram <= 0 and not a.allow_no_gpu:
        die("no CUDA device visible from the video venv. This benchmark must "
            "run on the render box. Refusing to emit an estimated table — a "
            "guessed number gets quoted as a measurement later.")
    card = (f"{vram:.0f}GB card, {a.size}, {a.steps} steps, {a.seconds}s clips"
            if vram > 0 else "UNMEASURED — no GPU, harness self-test only")

    models = [m.strip() for m in a.models.split(",") if m.strip()]
    unknown = [m for m in models if m not in MODELS]
    if unknown:
        print(f"note: passing through unrecognised model id(s) {unknown} — "
              f"their licence is NOT in MODEL_LICENCE and any clip they make "
              f"will fail the licence gate", file=sys.stderr)

    prompt, neg, still = shot_for(a.genome, a.node, a.beat)
    CLIPS.mkdir(parents=True, exist_ok=True)
    print(f"beat {a.beat:02d}  still={still.name}  models={models}", flush=True)

    sizes = [s.strip() for s in a.sizes.split(",") if s.strip()] or [a.size]
    step_list = [int(s) for s in a.steps_sweep.split(",") if s.strip()] or [a.steps]
    quants = [q.strip() for q in a.quantise_sweep.split(",") if q.strip()] or ["none"]

    rows = []
    for m in models:
        for size in sizes:
            for steps in step_list:
                for q in quants:
                    a.size, a.steps, a.quantise = size, steps, q
                    tag = f"{m}-{size}-{steps}st-{q}"
                    out = CLIPS / f"solo-{tag}-{a.node}-{a.beat:02d}.mp4"
                    print(f"--> {m} solo @ {size}, {steps} steps, "
                          f"quantise={q}, offload={a.offload}", flush=True)
                    r = render_once(m, prompt, neg, still, out, a)
                    rows.append(r)
                    print(f"    {'ok' if r['ok'] else 'FAILED'} {r['wall_s']}s",
                          flush=True)
    a.size, a.steps, a.quantise = sizes[-1], step_list[-1], quants[-1]

    conc = []
    for n in [int(x) for x in a.concurrency.split(",") if x.strip()]:
        for m in models:
            if not any(r["model"] == m and r["ok"] for r in rows):
                continue
            solo = next((r["wall_s"] for r in rows
                         if r["model"] == m and r["ok"]
                         and r["size"] == a.size and r["steps"] == a.steps
                         and r["quantise"] == a.quantise),
                        None)
            if solo is None:      # that recipe never succeeded solo
                continue
            a.solo_hint = solo
            print(f"--> {m} x{n} concurrent (budget "
                  f"{a.stall_factor * n * solo:.0f}s)", flush=True)
            c = render_concurrent(m, n, prompt, neg, still, a)
            conc.append(c)
            print(f"    {c['verdict']} ({c['completed']}/{n})", flush=True)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    BENCH.mkdir(parents=True, exist_ok=True)
    payload = {"measured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "host": os.environ.get("COMPUTERNAME") or os.uname().nodename,
               "card_vram_gb": round(vram, 1), "genome": a.genome, "node": a.node,
               "beat": a.beat, "still": still.name, "steps": a.steps,
               "size": a.size, "seconds": a.seconds, "seed": a.seed,
               "offload": a.offload, "quantise_sweep": quants,
               "sizes_swept": sizes, "steps_swept": step_list,
               "solo": rows, "concurrency": conc}
    (BENCH / f"bench-{stamp}.yaml").write_text(
        json.dumps(payload, indent=2), encoding="utf-8")   # JSON is valid YAML
    md = table(rows, conc, card)
    (BENCH / f"bench-{stamp}.md").write_text(md, encoding="utf-8")
    print()
    print(md)
    print(f"wrote {(BENCH / f'bench-{stamp}.yaml').relative_to(REPO)} and .md")
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
