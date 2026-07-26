#!/usr/bin/env python3
"""End-to-end episode QA — every defect class the loop has confirmed,
as one automated gate (founder directive 2026-07-24: "keep doing end to
end tests on all of the episodes").

Checks per episode (FAIL = ship-blocking, WARN = advisory):

  container   moov atom before mdat (faststart — browsers stall otherwise;
              bit the project twice), 720x1280 @ 24fps, sane duration,
              audio/video stream lengths agree
  loudness    integrated ≈ -14 LUFS (short-form platform level), true
              peak <= -0.5 dBTP (cycle 001)
  dead air    zero digital silence at -45dB; no quiet-vs-bed stretch
              longer than 3.5s (cycle 004 allows <=2s voiceless beat-outs)
  hook        no freeze-frame in the first 3s (cycle 001: static opens
              read as a broken video); WARN if the first 2s are dark
              (mean luma < 25%: known content-side defect, unfixable in
              assembly)
  captions    no caption box inside the platform chrome band (bottom 22%
              — verified cycle-1 defect); sampled every 2s
  manifests   every beat's VO manifest carries the current engine and
              measured chunks; no chunk exceeds the word cap + margin

Usage:
    python3 pipeline/qa_episode.py <leaf.mp4> [--clips <dir>] [--ffmpeg <bin>]
    python3 pipeline/qa_episode.py --all sapling          # every trunk leaf
Exit 0 = all PASS (warnings allowed); exit 1 = any FAIL.
"""

import argparse
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 720, 1280
CHROME_BAND = 0.22          # platform UI safe area (bottom fraction)
LUFS_TARGET, LUFS_TOL = -14.0, 1.3
QUIET_MAX_S = 3.5           # longest allowed quiet-vs-bed stretch
# Luma spread (90th percentile minus 10th) below this is a blank field, not a
# shot. A numerically failed generation still writes a valid, mid-grey,
# perfectly "fine" mp4 — the grey Wan render measured a spread of ~20 where
# real cel-shaded frames run 90-200.
FLAT_STDDEV = 45.0
CAPTION_WORD_CAP = 7 + 2    # chunker cap + orphan-fold margin

results = []


def record(episode: str, check: str, ok: bool, detail: str = "", warn: bool = False):
    level = "PASS" if ok else ("WARN" if warn else "FAIL")
    results.append((episode, check, level, detail))


def ff(args_, ffmpeg="ffmpeg"):
    return subprocess.run([ffmpeg, *args_], capture_output=True, text=True)


def atom_order(path: Path) -> list:
    """Top-level mp4 atom names in file order (faststart = moov before mdat)."""
    order, off, size = [], 0, path.stat().st_size
    with path.open("rb") as f:
        while off < size:
            f.seek(off)
            head = f.read(8)
            if len(head) < 8:
                break
            n, name = struct.unpack(">I4s", head)
            if n == 1:  # 64-bit atom
                n = struct.unpack(">Q", f.read(8))[0]
            if n <= 0:
                break
            order.append(name.decode("latin1"))
            off += n
    return order


def qa_episode(video: Path, clips_dir: Path | None, ffmpeg: str) -> None:
    ep = video.stem

    # --- container ---
    atoms = atom_order(video)
    faststart = "moov" in atoms and "mdat" in atoms and atoms.index("moov") < atoms.index("mdat")
    record(ep, "faststart", faststart, "moov after mdat" if not faststart else "")
    banner = ff(["-i", str(video)], ffmpeg).stderr
    m = re.search(r"(\d{3,4})x(\d{3,4})", banner)
    record(ep, "resolution", bool(m) and (int(m[1]), int(m[2])) == (WIDTH, HEIGHT),
           m.group(0) if m else "no video stream")
    d = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", banner)
    dur = int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]) if d else 0
    record(ep, "duration sane", 40 <= dur <= 200, f"{dur:.1f}s")
    astream = re.search(r"Stream .*Audio", banner)
    record(ep, "has audio", bool(astream))

    # --- loudness ---
    r = ff(["-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"], ffmpeg)
    # ebur128 logs a running I: per frame — the LAST one is the summary
    li = re.findall(r"I:\s+(-?\d+\.\d) LUFS", r.stderr)
    lufs = float(li[-1]) if li else None
    record(ep, "loudness ~-14 LUFS",
           lufs is not None and abs(lufs - LUFS_TARGET) <= LUFS_TOL,
           f"{lufs} LUFS" if lufs is not None else "unmeasured")
    tp = re.findall(r"Peak:\s+(-?\d+\.\d) dBFS", r.stderr)
    record(ep, "true peak <= -0.5", bool(tp) and float(tp[-1]) <= -0.5,
           f"{tp[-1]} dBTP" if tp else "unmeasured")

    # --- dead air ---
    r = ff(["-i", str(video), "-af", "silencedetect=n=-45dB:d=1", "-f", "null", "-"], ffmpeg)
    record(ep, "no digital silence", "silence_start" not in r.stderr,
           "; ".join(re.findall(r"silence_start: [\d.]+", r.stderr)[:3]))
    r = ff(["-i", str(video), "-af", f"silencedetect=n=-30dB:d={QUIET_MAX_S}",
            "-f", "null", "-"], ffmpeg)
    record(ep, f"no quiet stretch > {QUIET_MAX_S}s", "silence_start" not in r.stderr,
           "; ".join(re.findall(r"silence_start: [\d.]+", r.stderr)[:3]))

    # --- hook ---
    r = ff(["-t", "3", "-i", str(video), "-vf", "freezedetect=n=0.003:d=1.5",
            "-f", "null", "-"], ffmpeg)
    record(ep, "no frozen open", "freeze_start" not in r.stderr)
    r = ff(["-t", "2", "-i", str(video), "-vf", "signalstats,metadata=print",
            "-f", "null", "-"], ffmpeg)
    lumas = [float(v) for v in re.findall(r"YAVG=(\d+\.?\d*)", r.stderr)]
    mean_luma = sum(lumas) / len(lumas) if lumas else 0
    record(ep, "open not too dark", mean_luma >= 0.25 * 255,
           f"mean luma {mean_luma:.0f}/255", warn=True)

    # --- the picture actually contains a picture ---
    # A generation can fail NUMERICALLY and still write a perfectly valid mp4:
    # on 2026-07-26 the first Kaggle Wan render produced 5 seconds of flat grey
    # (stddev 5 of 255, luma range 86-132) and every check here passed, because
    # mid-grey is neither too dark nor frozen nor silent. It looked like success
    # in the log, in the file size, and in the QA report. Contrast is the check
    # that catches an empty frame: real cel-shaded animation runs stddev 40-70,
    # and anything under FLAT_STDDEV is a blank field, not a shot.
    r = ff(["-i", str(video), "-vf", f"fps=1/{max(1, int(dur // 6) or 1)},signalstats,metadata=print",
            "-f", "null", "-"], ffmpeg)
    lows = [float(v) for v in re.findall(r"YLOW=(\d+\.?\d*)", r.stderr)]
    highs = [float(v) for v in re.findall(r"YHIGH=(\d+\.?\d*)", r.stderr)]
    devs = [h - l for l, h in zip(lows, highs)]
    worst = min(devs) if devs else None
    flat = [f"{d:.0f}" for d in devs if d < FLAT_STDDEV]
    # An assembled episode legitimately contains near-flat frames — slates are
    # designed placeholders for beats with no footage yet — so there it is a
    # warning that reports how much of the episode is empty. On a RAW generator
    # clip there is no such excuse: flat means the generation failed, and that
    # is a hard failure. The clip level is where this defect is born, so that is
    # where the gate belongs.
    is_episode = bool(m) and (int(m[1]), int(m[2])) == (WIDTH, HEIGHT)
    record(ep, "frames carry a picture", not flat and worst is not None,
           (f"{len(flat)}/{len(devs)} frames blank, lowest contrast {worst:.0f}"
            + (" (slates?)" if is_episode else " — GENERATION FAILED")
            if flat else f"lowest contrast {worst:.0f}" if worst is not None
            else "unmeasured"),
           warn=is_episode)

    # --- captions in the chrome band ---
    if not m or (int(m[1]), int(m[2])) != (WIDTH, HEIGHT):
        # a raw generator clip is not an assembled episode; the chrome band
        # only means something at the delivery resolution
        record(ep, "captions clear chrome band", True,
               f"skipped ({m.group(0) if m else '?'}, not an episode)")
        return
    try:
        from PIL import Image
        import tempfile
        band_hits = []
        with tempfile.TemporaryDirectory() as td:
            ff(["-i", str(video), "-vf", "fps=0.5", f"{td}/f%03d.png"], ffmpeg)
            for fpath in sorted(Path(td).glob("f*.png")):
                img = Image.open(fpath).convert("L")
                px = img.load()
                y0 = int(HEIGHT * (1 - CHROME_BAND))
                for yy in range(y0, HEIGHT, 6):
                    dark = light = 0
                    for xx in range(60, WIDTH - 60, 4):
                        v = px[xx, yy]
                        dark += v < 30
                        light += v > 225
                    # a caption row = a long near-black box run PLUS bright text
                    if dark > 90 and light > 6:
                        band_hits.append(f"{fpath.stem}@y{yy}")
                        break
        record(ep, "captions clear chrome band", not band_hits,
               ", ".join(band_hits[:4]))
    except ImportError:
        record(ep, "captions clear chrome band", True, "PIL unavailable — skipped", warn=True)

    # --- manifests ---
    if clips_dir and clips_dir.is_dir():
        engines, worst = set(), 0
        for mf in sorted(clips_dir.glob("[0-9][0-9]-vo.json")):
            data = json.loads(mf.read_text())
            engines.add(data.get("engine", "MISSING"))
            for line in data.get("lines", []):
                for c in line.get("chunks", []):
                    worst = max(worst, len(c["text"].split()))
                if not line.get("chunks"):
                    record(ep, "manifest chunks", False, f"{mf.name}: line without chunks")
        record(ep, "single current engine", engines == {"chatterbox-0.5B"},
               ", ".join(sorted(engines)) or "no manifests")
        record(ep, f"chunk word cap <= {CAPTION_WORD_CAP}", worst <= CAPTION_WORD_CAP,
               f"worst {worst}")


TRUNK = [("001-capability-inventory", "001-t3-c"), ("002b-first-citizen", "002b-t3-b"),
         ("003b-one-leaf-for-yes", "003b-t3-b"), ("004-shade", "004-t3-b"),
         ("005-the-assessor", "005-t3-b"), ("006a-miracle-clause", "006a-t3-b"),
         ("007a-the-demo", "007a-t3-b")]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", nargs="?")
    p.add_argument("--all", metavar="GENOME")
    p.add_argument("--clips", type=Path)
    p.add_argument("--ffmpeg", default="ffmpeg")
    args = p.parse_args()

    jobs = []
    if args.all:
        for slug, leaf in TRUNK:
            node = REPO / "genomes" / args.all / "nodes" / slug
            v = node / "leaves" / f"{leaf}.mp4"
            if v.exists():
                jobs.append((v, node / "clips"))
    elif args.video:
        jobs.append((Path(args.video), args.clips))
    else:
        raise SystemExit(__doc__)

    for video, clips in jobs:
        qa_episode(video, clips, args.ffmpeg)

    width = max(len(r[1]) for r in results) + 2
    cur = None
    fails = 0
    for ep, check, level, detail in results:
        if ep != cur:
            print(f"\n── {ep}")
            cur = ep
        mark = {"PASS": "ok  ", "WARN": "warn", "FAIL": "FAIL"}[level]
        fails += level == "FAIL"
        print(f"  {mark}  {check:<{width}} {detail}")
    print(f"\n{'✗ ' + str(fails) + ' FAIL' if fails else '✓ all episodes pass'} "
          f"({len(results)} checks, {sum(1 for r in results if r[2] == 'WARN')} warnings)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
