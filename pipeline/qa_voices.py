#!/usr/bin/env python3
"""Voice-distinctness QA — are the characters actually telling apart?

Founder wince (2026-07-25): "voices are mixed up sometimes." Casting is
verified correct in the manifests, so the question is acoustic: do two
characters' takes overlap so much that a listener can't separate them?

Measures, per character, from the real rendered VO tracks:
  pitch     median F0 per line (autocorrelation on a low-passed frame)
  bright    spectral centroid (timbre placement)
Then reports pairwise separation. A pair whose pitch bands overlap AND
whose centroids sit within a few hundred Hz is a confusion candidate.

Usage (TTS venv, has numpy+soundfile):
    <tts-venv>/bin/python3 pipeline/qa_voices.py sapling [<ffmpeg>]
"""

import json
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent.parent
F0_MIN, F0_MAX = 60.0, 350.0     # human speech range of interest
MIN_SEG_S = 0.35


def median_f0(x: np.ndarray, sr: int) -> float | None:
    """Median fundamental across voiced frames (autocorrelation peak)."""
    frame = int(0.040 * sr)
    hop = int(0.020 * sr)
    lo, hi = int(sr / F0_MAX), int(sr / F0_MIN)
    vals = []
    for i in range(0, max(0, len(x) - frame), hop):
        f = x[i:i + frame]
        if np.sqrt(np.mean(f ** 2)) < 0.01:
            continue                      # unvoiced/silent
        f = f - f.mean()
        ac = np.correlate(f, f, mode="full")[len(f) - 1:]
        if ac[0] <= 0 or hi >= len(ac):
            continue
        lag = int(np.argmax(ac[lo:hi]) + lo)
        if ac[lag] / ac[0] > 0.3:         # periodic enough to trust
            vals.append(sr / lag)
    return statistics.median(vals) if len(vals) >= 3 else None


def centroid(x: np.ndarray, sr: int) -> float:
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    return float((spec * freqs).sum() / spec.sum()) if spec.sum() else 0.0


def main() -> int:
    genome = sys.argv[1] if len(sys.argv) > 1 else "sapling"
    ff = sys.argv[2] if len(sys.argv) > 2 else "ffmpeg"
    nodes = sorted((REPO / "genomes" / genome / "nodes").glob("*/clips"))
    per_char: dict[str, list] = {}

    with tempfile.TemporaryDirectory() as td:
        for clips in nodes:
            for mf in sorted(clips.glob("[0-9][0-9]-vo.json")):
                data = json.loads(mf.read_text())
                audio = clips / (mf.stem + ".mp3")
                if not audio.exists():
                    continue
                for li, line in enumerate(data.get("lines", [])):
                    dur = line["end"] - line["start"]
                    if dur < MIN_SEG_S:
                        continue
                    seg = Path(td) / f"{clips.parent.name}-{mf.stem}-{li}.wav"
                    subprocess.run(
                        [ff, "-y", "-loglevel", "error", "-ss", f"{line['start']}",
                         "-t", f"{dur}", "-i", str(audio), "-ac", "1",
                         "-ar", "24000", str(seg)], check=True)
                    x, sr = sf.read(str(seg))
                    x = np.asarray(x, dtype=float)
                    f0 = median_f0(x, sr)
                    if f0:
                        per_char.setdefault(line["who"], []).append(
                            (f0, centroid(x, sr)))
                    seg.unlink()

    print(f"\n{'character':<12} {'lines':>5}  {'pitch Hz (median, p10-p90)':<30} centroid Hz")
    prof = {}
    for who, vals in sorted(per_char.items()):
        f0s = sorted(v[0] for v in vals)
        cs = [v[1] for v in vals]
        med = statistics.median(f0s)
        p10 = f0s[int(0.1 * (len(f0s) - 1))]
        p90 = f0s[int(0.9 * (len(f0s) - 1))]
        prof[who] = (med, p10, p90, statistics.median(cs))
        print(f"{who:<12} {len(vals):>5}  {med:>6.1f}  ({p10:>5.1f}–{p90:>5.1f}){'':<12} "
              f"{statistics.median(cs):>7.0f}")

    print("\npairwise separation (confusion risk):")
    names = sorted(prof)
    risky = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ma, la, ha, ca = prof[a]
            mb, lb, hb, cb = prof[b]
            overlap = min(ha, hb) - max(la, lb)
            span = min(ha - la, hb - lb) or 1
            frac = max(0.0, overlap / span)
            dpitch, dcent = abs(ma - mb), abs(ca - cb)
            risk = frac > 0.5 and dpitch < 25 and dcent < 400
            risky += risk
            flag = "  ⚠ CONFUSABLE" if risk else ""
            print(f"  {a:<11}/{b:<11} Δpitch {dpitch:>5.1f} Hz · "
                  f"Δcentroid {dcent:>5.0f} Hz · band overlap {frac:>4.0%}{flag}")
    print(f"\n{'✗ ' + str(risky) + ' confusable pair(s)' if risky else '✓ all pairs separable'}")
    return 1 if risky else 0


if __name__ == "__main__":
    sys.exit(main())
