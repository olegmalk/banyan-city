#!/usr/bin/env python3
"""Caption-boundary alignment gate: do the burned-in caption switches land in
the silences the voice actually has?

WHY THIS EXISTS. `synth_vo.synth_line` has two paths and only one of them is
exact. LONG lines (>22 words on chatterbox) are STITCHED from per-chunk takes,
so the manifest's chunk boundaries ARE the audio's own joins — exact by
construction. Every SHORTER multi-chunk line is one generation, and
`measured_chunks` times its captions by synthesizing each chunk SOLO and
scaling those durations proportionally into the line's window. Proportional
scaling is not measurement: the engine does not pace a chunk the same way
inside a sentence as it does alone, so the boundary drifts off the pause it is
supposed to land in. Measured on the 2026-08-21 episode-2 ship cut, all 11
stitched boundaries landed inside their pause and 3 of the 17 proportional ones
missed by 207-291 ms — captions changing a fifth of a second after the voice
had moved on, which is the class the founder already reported once as "some
subtitles are offset" (2026-07-30).

WHAT IT DOES. Reads the RENDERED take (`NN-vo.mp3`) beside its manifest,
finds the pauses in it, and checks every inter-chunk boundary against the
nearest one. A boundary sitting more than `--tol` ms OUTSIDE its pause is a
defect; `--write` snaps it to the pause and records the move in the manifest.
Boundaries with no pause to land in (the engine ran the clause straight
through) are reported as UNVERIFIABLE and never moved — there is nothing to
align to, and inventing a number would be worse than the estimate.

WHERE 0.6 COMES FROM. The snap target is not the pause midpoint: it is
calibrated against the stitched path, which is known-exact. Across those 11
boundaries the true join sits at a median 0.595 of the way through the pause
this detector reports (the envelope smoothing makes a detected pause run a
little past the next speech onset). So the target is `start + 0.6 * width`,
which reproduces what the exact path already does.

WHAT IT NEVER TOUCHES. Line-level `start`/`end`, `total_s`, the audio, the
text. Only inter-chunk boundaries inside a line move, and only ones this tool
can point at a measured pause for. Caption TEXT is not this tool's business:
render_t3 burns `chunks[].text`, and that text is verified verbatim against
node.md by the caller, not here.

    python3 pipeline/align_captions.py <clips-dir> [--tol 200] [--write]

Exit 0 = every boundary within tolerance (unverifiable ones allowed);
exit 1 = at least one measurable boundary is out. $0, no network, no GPU.
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_t2 import ffmpeg_exe  # noqa: E402 — shared resolver

SR = 16000
HOP = 0.010            # 10 ms envelope frames
SMOOTH = 3             # 30 ms moving average — kills glottal-pulse notches
PAUSE_DB = -22.0       # relative to the take's own 90th-percentile RMS
PAUSE_MIN_S = 0.12     # shorter dips are inside words, not between clauses
SEARCH_S = 0.90        # how far from a boundary we will look for its pause
SNAP_FRAC = 0.60       # calibrated on the stitched path — see module docstring
TOL_MS = 200.0         # the founder-facing bar: lead/lag past this reads wrong


def decode(path: Path, ffmpeg: str) -> np.ndarray:
    r = subprocess.run([ffmpeg, "-v", "error", "-i", str(path), "-ac", "1",
                        "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    if r.returncode:
        raise SystemExit(f"{path}: ffmpeg decode failed\n{r.stderr.decode()[-800:]}")
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def envelope(x: np.ndarray) -> np.ndarray:
    n = int(SR * HOP)
    m = len(x) // n
    if m == 0:
        return np.zeros(0)
    e = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1))
    return np.convolve(e, np.ones(SMOOTH) / SMOOTH, mode="same")


def pauses(x: np.ndarray) -> list:
    """Contiguous stretches at least PAUSE_MIN_S long that sit PAUSE_DB below
    the take's own speech level. Head and tail silence are dropped: they are
    engine padding, not clause boundaries."""
    e = envelope(x)
    if not len(e):
        return []
    ref = np.percentile(e, 90) or 1e-9
    db = 20 * np.log10(np.maximum(e, 1e-12) / ref)
    quiet = db < PAUSE_DB
    out, i = [], 0
    while i < len(quiet):
        if not quiet[i]:
            i += 1
            continue
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        if (j - i) * HOP >= PAUSE_MIN_S:
            out.append((round(i * HOP, 3), round(j * HOP, 3)))
        i = j
    if out and out[0][0] <= 0.03:
        out = out[1:]
    if out and out[-1][1] >= len(e) * HOP - 0.03:
        out = out[:-1]
    return out


def boundaries(manifest: dict) -> list:
    """(line_index, chunk_index, boundary_time) for every inter-chunk switch."""
    out = []
    for li, line in enumerate(manifest.get("lines") or []):
        ch = line.get("chunks") or []
        for k in range(len(ch) - 1):
            out.append((li, k, float(ch[k]["end"])))
    return out


def assess(manifest: dict, ps: list) -> list:
    """One row per boundary: (li, k, t, pause_or_None, signed_error_ms).

    Positive error = the caption switches LATE (voice got there first);
    negative = EARLY. A boundary inside its pause scores 0. Pauses are claimed
    at most once, nearest-first, so two boundaries cannot both snap to the same
    silence and cross each other."""
    rows, claimed = [], set()
    for li, k, t in boundaries(manifest):
        best = None
        for pi, (a, b) in enumerate(ps):
            if pi in claimed:
                continue
            d = 0.0 if a <= t <= b else (a - t if t < a else t - b)
            if d > SEARCH_S:
                continue
            if best is None or d < best[0]:
                best = (d, pi, a, b)
        if best is None:
            rows.append((li, k, t, None, None))
            continue
        _, pi, a, b = best
        claimed.add(pi)
        err = 0.0 if a <= t <= b else ((t - b) if t > b else (t - a))
        rows.append((li, k, t, (a, b), err * 1000.0))
    return rows


def apply_snaps(manifest: dict, rows: list, tol_ms: float) -> list:
    """Move every out-of-tolerance boundary onto its pause. Returns the moves."""
    moves = []
    for li, k, t, pause, err in rows:
        if pause is None or err is None or abs(err) <= tol_ms:
            continue
        a, b = pause
        new = round(a + SNAP_FRAC * (b - a), 3)
        line = manifest["lines"][li]
        ch = line["chunks"]
        # never reorder: stay strictly inside the neighbouring boundaries, and
        # inside the line's own window. A snap that would cross its neighbour
        # is refused rather than clamped into a zero-length caption.
        lo = float(ch[k]["start"]) + 0.05
        hi = float(ch[k + 1]["end"]) - 0.05
        if not lo < new < hi:
            moves.append({"line": li, "chunk": k, "from": t, "to": None,
                          "refused": f"snap {new} outside ({lo:.3f}, {hi:.3f})"})
            continue
        ch[k]["end"] = new
        ch[k + 1]["start"] = new
        moves.append({"line": li, "chunk": k, "from": round(t, 3), "to": new,
                      "pause": [a, b], "was_off_ms": round(err)})
    return moves


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", type=Path, help="directory holding NN-vo.json + NN-vo.mp3")
    ap.add_argument("--tol", type=float, default=TOL_MS,
                    help="milliseconds a boundary may sit outside its pause (default 200)")
    ap.add_argument("--write", action="store_true",
                    help="snap out-of-tolerance boundaries and rewrite the manifests")
    ap.add_argument("--ffmpeg", default=None)
    args = ap.parse_args()

    ffmpeg = args.ffmpeg or ffmpeg_exe()
    if not args.clips.is_dir():
        raise SystemExit(f"{args.clips}: not a directory")
    manifests = sorted(args.clips.glob("[0-9][0-9]-vo.json"))
    if not manifests:
        raise SystemExit(f"{args.clips}: no NN-vo.json manifests")

    n_ok = n_bad = n_unver = n_moved = 0
    for jf in manifests:
        num = jf.name[:2]
        take = args.clips / f"{num}-vo.mp3"
        if not take.exists():
            print(f"  beat {num}  SKIP — no {take.name} beside the manifest")
            continue
        manifest = json.loads(jf.read_text(encoding="utf-8"))
        ps = pauses(decode(take, ffmpeg))
        rows = assess(manifest, ps)
        if not rows:
            continue
        for li, k, t, pause, err in rows:
            if pause is None:
                n_unver += 1
                print(f"  beat {num} L{li} k{k}  t={t:7.3f}  UNVERIFIABLE "
                      f"— no pause within {SEARCH_S}s; the engine ran the clause through")
            elif abs(err) <= args.tol:
                n_ok += 1
            else:
                n_bad += 1
                word = "LATE" if err > 0 else "EARLY"
                print(f"  beat {num} L{li} k{k}  t={t:7.3f}  {err:+7.0f} ms {word:5} "
                      f"(pause {pause[0]:.2f}-{pause[1]:.2f})")
        if args.write:
            moves = apply_snaps(manifest, rows, args.tol)
            if moves:
                manifest["caption_alignment"] = {
                    "tool": "pipeline/align_captions.py",
                    "date": str(date.today()),
                    "measured_on": take.name,
                    "tolerance_ms": args.tol,
                    "snap_frac": SNAP_FRAC,
                    "moved": moves,
                }
                jf.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
                n_moved += len([m for m in moves if m.get("to") is not None])
                for m in moves:
                    if m.get("to") is None:
                        print(f"    beat {num} L{m['line']} k{m['chunk']} REFUSED: {m['refused']}")
                    else:
                        print(f"    beat {num} L{m['line']} k{m['chunk']} "
                              f"{m['from']:.3f} -> {m['to']:.3f}")

    total = n_ok + n_bad + n_unver
    print(f"\nCAPTION-ALIGN: {n_ok} within {args.tol:.0f} ms, {n_bad} out, "
          f"{n_unver} unverifiable, of {total} boundaries")
    if args.write:
        print(f"CAPTION-ALIGN: {n_moved} boundaries moved")
        return 0
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
