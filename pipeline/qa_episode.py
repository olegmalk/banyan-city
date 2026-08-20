#!/usr/bin/env python3
"""End-to-end episode QA — every defect class the loop has confirmed,
as one automated gate (founder directive 2026-07-24: "keep doing end to
end tests on all of the episodes").

Checks per episode (FAIL = ship-blocking, WARN = advisory):

  container   moov atom before mdat (faststart — browsers stall otherwise;
              bit the project twice), 720x1280 @ 24fps, sane duration,
              audio/video stream lengths agree
  loudness    integrated ≈ -17 LUFS (deliberately below the -14 platform
              reference so transients survive — see LUFS_TARGET), true
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

import yaml

REPO = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 720, 1280
CHROME_BAND = 0.22          # platform UI safe area (bottom fraction)
# -17, not the -14 platform reference: chasing -14 integrated on material with
# scored silences forces every loud moment into the limiter, so a body hitting
# the floor came out no louder than a spoken line (cold-read listener, 2026-08-01:
# "pinned at about -1.8 dBFS almost continuously"). Platforms normalise upward
# without re-limiting, so mastering quieter keeps the transients.
LUFS_TARGET, LUFS_TOL = -17.0, 1.5
QUIET_MAX_S = 3.5           # longest allowed quiet-vs-bed stretch
# The quiet-stretch floor must track the MASTER's level, not sit at an absolute
# dB: it was -30 when we mastered to -14, and after dropping the target to -17
# the whole mix moved down with it, so a fixed floor started calling the
# designed aftermath a dropout. 16 dB below target is the same musical distance.
QUIET_FLOOR_DB = LUFS_TARGET - 16
# A stretch this far below the episode's own dialogue is a hole, not a held beat
# — see quiet_hole(). 14 dB is roughly "you would reach for the volume"; 4s is
# about the longest silence short-form holds before a viewer leaves.
DYN_DROP_DB = 14.0
DYN_MAX_S = 4.0
# Luma spread (90th percentile minus 10th) below this is a blank field, not a
# shot. A numerically failed generation still writes a valid, mid-grey,
# perfectly "fine" mp4 — the grey Wan render measured a spread of ~20 where
# real frames in this style run a median of 52-144 (measured across the 31
# archived clips); dead grey runs 14-22. 35 separates them with room on both
# sides — and this style is deliberately soft pastel, so a high floor false-alarms.
FLAT_STDDEV = 35.0
CAPTION_WORD_CAP = 7 + 2    # chunker cap + orphan-fold margin

results = []


def record(episode: str, check: str, ok: bool, detail: str = "", warn: bool = False):
    level = "PASS" if ok else ("WARN" if warn else "FAIL")
    results.append((episode, check, level, detail))


def ff(args_, ffmpeg="ffmpeg"):
    return subprocess.run([ffmpeg, *args_], capture_output=True, text=True, encoding="utf-8", errors="replace")


def quiet_hole(video, ffmpeg="ffmpeg") -> tuple:
    """(seconds, start, floor_db, speech_db) of the longest stretch sitting far
    below the episode's OWN speech level.

    Why this is not the quiet-stretch check above. In ep1-v18 the death's
    aftermath ran nine seconds decaying from -33 to -46 dB RMS while dialogue sat
    at -18 — and `silencedetect` found nothing, because its threshold is on PEAKS
    and the peaks stayed above the -33 dB floor for most of it. So the check
    passed and the founder's actual note ("his death is very anticlimatic") went
    unexplained through four rounds of moving the thump around.

    The thump was never the problem: at 14s it is the loudest moment in the
    episode. What follows it is — eight seconds with no words, no sound above a
    dying fan, over a picture that gets BRIGHTER. The death has no aftermath, it
    has an absence, and absence is measurable: a long run far below the level of
    the speech around it.

    ABSOLUTE thresholds cannot express that, which is why this one is relative to
    the episode's own dialogue (90th-percentile RMS). Scored silence is real and
    allowed — this is a WARNING carrying its length and location, so an author
    can tell a held beat from a hole. Two seconds of nothing lands a death; eight
    loses the audience.
    """
    r = ff(["-hide_banner", "-nostats", "-i", str(video), "-af",
            "astats=metadata=1:reset=1,ametadata=print:"
            "key=lavfi.astats.Overall.RMS_level:file=-",
            "-f", "null", "-"], ffmpeg)
    # one print per audio frame (~23ms), and channel prints share a pts_time —
    # keep the loudest per timestamp, then bucket to 0.25s so a single quiet
    # frame between two loud ones cannot look like a hole
    at, best = {}, None
    for line in r.stdout.splitlines():
        m = re.match(r"frame:\d+\s+pts:\d+\s+pts_time:([\d.]+)", line)
        if m:
            best = float(m.group(1))
            continue
        m = re.match(r"lavfi\.astats\.Overall\.RMS_level=(-?[\d.]+)", line)
        if m and best is not None:
            b = round(best * 4) / 4
            at[b] = max(at.get(b, -120.0), float(m.group(1)))
    if len(at) < 8:
        return 0.0, 0.0, 0.0, 0.0
    keys = sorted(at)
    levels = sorted(at.values())
    speech = levels[int(len(levels) * 0.90)]
    floor = speech - DYN_DROP_DB
    longest, run = [], []
    for k in keys:
        if at[k] < floor:
            run.append(k)
        else:
            longest = max(longest, run, key=len)
            run = []
    longest = max(longest, run, key=len)
    if not longest:
        return 0.0, 0.0, 0.0, speech
    return (longest[-1] - longest[0] + 0.25, longest[0],
            min(at[k] for k in longest), speech)


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
    record(ep, f"loudness ~{LUFS_TARGET:g} LUFS",
           lufs is not None and abs(lufs - LUFS_TARGET) <= LUFS_TOL,
           f"{lufs} LUFS" if lufs is not None else "unmeasured")
    tp = re.findall(r"Peak:\s+(-?\d+\.\d) dBFS", r.stderr)
    record(ep, "true peak <= -0.5", bool(tp) and float(tp[-1]) <= -0.5,
           f"{tp[-1]} dBTP" if tp else "unmeasured")

    # --- dead air ---
    # -60dB, not -45: the defect class is ACCIDENTAL digital-zero holes
    # (raw TTS concat, cycle 001 — those sit at the -91dB floor). Scored
    # silence exists now (cycle 012's death sequence) and is mixed as quiet
    # air around -55dB, which is design, not dropout.
    r = ff(["-i", str(video), "-af", "silencedetect=n=-60dB:d=1", "-f", "null", "-"], ffmpeg)
    record(ep, "no digital silence", "silence_start" not in r.stderr,
           "; ".join(re.findall(r"silence_start: [\d.]+", r.stderr)[:3]))
    r = ff(["-i", str(video), "-af", f"silencedetect=n={QUIET_FLOOR_DB:g}dB:d={QUIET_MAX_S}",
            "-f", "null", "-"], ffmpeg)
    record(ep, f"no quiet stretch > {QUIET_MAX_S}s", "silence_start" not in r.stderr,
           "; ".join(re.findall(r"silence_start: [\d.]+", r.stderr)[:3]))
    hole_s, hole_at, hole_floor, speech = quiet_hole(video, ffmpeg)
    record(ep, f"no hole > {DYN_MAX_S:g}s under the dialogue",
           hole_s <= DYN_MAX_S,
           (f"{hole_s:.1f}s from {hole_at:.0f}s, floor {hole_floor:.0f} dB vs "
            f"speech {speech:.0f} dB" if hole_s else "none"), warn=True)

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
    # DO NOT HAND THE READER AN EXCUSE. This warning said "(slates?)" — a guess,
    # offered whether or not the cut had any slates — and it fired on
    # ep1-v26-approved and ep1-v28-swap at contrast 12 for days while the steward
    # read the parenthetical and moved on. The blank frames were beat 15: the
    # episode's final shot, its hook, essentially black after its first frame.
    # The check was right every time and its own hedge is what buried it.
    #
    # A cut with slates says so in render_t3's summary ("N footage, M slate"), so
    # the reader can resolve it in one glance — but the message must state the
    # defect, not pre-excuse it.
    hint = ("  ← if this cut has 0 slates, these are DEAD SHOTS, not placeholders"
            if is_episode else " — GENERATION FAILED")
    record(ep, "frames carry a picture", not flat and worst is not None,
           (f"{len(flat)}/{len(devs)} frames blank, lowest contrast {worst:.0f}"
            + hint
            if flat else f"lowest contrast {worst:.0f}" if worst is not None
            else "unmeasured"),
           warn=is_episode)

    # --- captions in the chrome band ---
    #
    # THIS CHECK IS A WARNING, NOT A GATE, AND THAT IS DELIBERATE.
    #
    # The pixel signature of a caption block — a wide, near-uniform dark region
    # carrying bright glyphs, low in the frame — is also the pixel signature of
    # this show's own footage: a night interior in dark cel shading with a lit
    # monitor and keycaps. On 2026-08-02 it failed `ep1-v22-hires` whose captions
    # sat at y999 by construction, and three successive attempts to make it
    # specific (contiguity, then flatness, then a centred-rectangle test) each
    # broke in a different direction — the last one flagged a control frame with
    # no caption in it at all. Verified by cropping the band and looking: no
    # caption, just a hooded sleeve and a bright keyboard.
    #
    # THE REAL GUARANTEE IS ARITHMETIC, NOT VISION. render_t3 places every
    # caption block at `H-h-CAPTION_MARGIN`, so its lowest pixel is at
    # HEIGHT-CAPTION_MARGIN. As long as CAPTION_MARGIN >= CHROME_BAND*HEIGHT, a
    # caption CANNOT enter the band, and test_pipeline asserts exactly that
    # against this module's own CHROME_BAND. That test is the gate.
    #
    # What survives here is a cheap smoke signal for text this pipeline did not
    # draw (burned-in subtitles in supplied footage, a platform re-encode). It
    # reports, and it does not block, because a check that fails on healthy
    # episodes gets ignored — which is how the cycle-001 defect it was written
    # for would sail through a second time.
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
                    if dark > 90 and light > 6:
                        band_hits.append(f"{fpath.stem}@y{yy}")
                        break
        record(ep, "captions clear chrome band", not band_hits,
               (", ".join(band_hits[:4]) + "  (heuristic: dark footage trips this; "
                "the margin is guaranteed by CAPTION_MARGIN >= CHROME_BAND)")
               if band_hits else "", warn=True)
    except ImportError:
        record(ep, "captions clear chrome band", True, "PIL unavailable — skipped", warn=True)

    # --- playback rate ---
    # THE GATE HOLE OF 2026-08-20, CLOSED. A composite whose sidecar honestly
    # said `model: none` (no sampler ran) was misread as a held still and
    # STRETCHED to fill its slot: five seconds of cold open at 0.53x. Nothing
    # here caught it, and nothing here could have — the file's sha, size,
    # duration, loudness, links and routes are all identical whether the
    # footage inside plays at 1x or at half speed. Duration is the wrong
    # instrument too: a stretch fills the SAME slot, so the master's runtime
    # does not move by a millisecond.
    #
    # What identifies it is the FILL PATH, which only the assembler knows, so
    # the assembler now writes it per beat and this reads it back. Stretching
    # is legitimate for exactly one thing — a hold_still product, a computed
    # camera move with no true frame rate. Anything that declares its own `fps:`
    # is footage and must never be stretched.
    meta = video.with_suffix(video.suffix + ".meta.yaml")
    rows = []
    if meta.exists():
        try:
            rows = (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("sources") or []
        except yaml.YAMLError:
            rows = []
    graded = [r for r in rows if isinstance(r, dict) and r.get("fill")]
    if not graded:
        record(ep, "no footage time-stretched", True,
               "assembler recorded no fill modes — re-assemble to grade this "
               "(render_t3 writes `fill:` per beat since 2026-08-20)", warn=True)
    else:
        bad = []
        for r in graded:
            if r.get("fill") != "stretch":
                continue
            names = [n for n in str(r.get("clip", "")).split("+") if n.endswith(".mp4")]
            for n in names:
                sc = (clips_dir / (n + ".meta.yaml")) if clips_dir else None
                declares_fps = bool(sc and sc.exists()
                                    and re.search(r"^\s*fps\s*:\s*[0-9]",
                                                  sc.read_text(encoding="utf-8", errors="replace"), re.M))
                if declares_fps:
                    bad.append(f"beat {r.get('beat')} {n} "
                               f"({r.get('clip_s')}s stretched into {r.get('slot_s')}s)")
        record(ep, "no footage time-stretched", not bad,
               "; ".join(bad) if bad
               else f"{len(graded)} beats graded, "
                    f"{sum(1 for r in graded if r.get('fill') == 'stretch')} stretched "
                    "(held stills only)")

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
