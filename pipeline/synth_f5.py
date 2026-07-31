#!/usr/bin/env python3
"""Voice a beat with F5-TTS, cloned from our own takes — chunk-accurate.

Chosen as the show's engine on 2026-07-31: F5 clones the established voice
(median pitch within 3% of the Chatterbox canon) and, unlike a uniform
"emotion" dial, shifts its read per line — the panicked line came out +18Hz,
the exhausted line -6Hz. It also runs at ~5s per line on this Mac, so a note
about tone can be answered in a minute instead of a night.

Each caption chunk is synthesized SEPARATELY and the durations are measured,
so `render_t3` burns captions on the voice instead of guessing (the offsets
the founder saw in v6 came from guessed spans). Output matches synth_vo's
contract: NN-vo.mp3 + NN-vo.json with lines[].chunks.

    <f5-venv>/bin/python3 pipeline/synth_f5.py <genome> <node-slug> \
        --beats 6 [--text "override line"] [--ref 06]
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from captions import caption_chunks                      # noqa: E402
from render_t1 import extract_script, parse_frames, strip_inline_md  # noqa: E402
from render_t2 import clean_speech                        # noqa: E402

GAP = 0.12          # breath between lines
MODEL = "F5TTS_v1_Base"


def media_seconds(p: Path) -> float:
    """Duration of an audio file, via ffmpeg's banner (no ffprobe dependency)."""
    r = subprocess.run(["ffmpeg", "-i", str(p)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def ref_line(by_num: dict, num: int) -> str:
    """What beat `num`'s take says, straight from the script."""
    b = by_num.get(num)
    if not b:
        return ""
    for it in b["items"]:
        if it[0] == "line":
            return clean_speech(strip_inline_md(it[2]))
    return ""


def align_chunks(wav: Path, chunks: list, t0: float) -> list:
    """Map caption chunks onto the real speech in a whole-line take.

    Synthesizing chunk-by-chunk was the first attempt and it was wrong twice:
    F5 pads a short chunk toward its reference's pace ("Right." came out
    2.37s), and reading each fragment in isolation throws away the line's
    music — the exact thing we switched engines for. So the line is voiced in
    ONE pass and the captions are aligned to it: silence gaps become chunk
    boundaries when their count fits, else spans go by character weight.
    """
    import numpy as np
    import soundfile as sf

    x, sr = sf.read(str(wav))
    if x.ndim > 1:
        x = x.mean(1)
    win = int(0.02 * sr)
    rms = np.array([np.sqrt((x[i:i + win] ** 2).mean() + 1e-12)
                    for i in range(0, max(len(x) - win, 1), win)])
    thresh = max(rms.max() * 0.06, 1e-4)
    voiced = rms > thresh
    # gaps of >=180ms inside speech are the line's own breaths
    gaps, run = [], 0
    for i, v in enumerate(voiced):
        if not v:
            run += 1
            continue
        if run * 0.02 >= 0.18 and i - run > 0:
            gaps.append(((i - run / 2) * 0.02, run * 0.02))
        run = 0
    dur = len(x) / sr
    if len(gaps) == len(chunks) - 1:
        bounds = [0.0] + [g[0] for g in gaps] + [dur]
    else:                                   # weight by characters spoken
        tot = sum(len(c) for c in chunks) or 1
        acc, bounds = 0.0, [0.0]
        for c in chunks[:-1]:
            acc += len(c) / tot * dur
            bounds.append(acc)
        bounds.append(dur)
    return [{"text": c, "start": round(t0 + bounds[i], 3),
             "end": round(t0 + bounds[i + 1], 3)} for i, c in enumerate(chunks)]


def f5(ref_wav: Path, ref_text: str, text: str, out: Path) -> float:
    """One line → wav; returns its measured duration."""
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            [sys.executable, "-m", "f5_tts.infer.infer_cli", "--model", MODEL,
             "--ref_audio", str(ref_wav), "--ref_text", ref_text,
             "--gen_text", text, "--output_dir", td,
             "--output_file", "chunk.wav", "--device", "mps"],
            capture_output=True, text=True, timeout=900)
        got = Path(td) / "chunk.wav"
        if not got.exists():
            raise SystemExit(f"F5 failed on {text!r}:\n{(r.stderr or r.stdout)[-800:]}")
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(got),
                        "-ar", "24000", "-ac", "1", str(out)], check=True)
    import soundfile as sf
    info = sf.info(str(out))
    return info.frames / info.samplerate


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--beats", required=True, help="comma-separated beat numbers")
    ap.add_argument("--text", default="", help="override the script's line (one beat only)")
    ap.add_argument("--out", default="", help="clips dir (default the node's)")
    ap.add_argument("--ref-beat", dest="ref_beat", default="",
                    help="clone the READ of this beat's take (emotion transfer)")
    a = ap.parse_args()

    node_dir = REPO / "genomes" / a.genome / "nodes" / a.node
    clips = Path(a.out) if a.out else node_dir / "clips"
    beats = parse_frames(extract_script((node_dir / "node.md").read_text()))
    by_num = {i: b for i, b in enumerate(beats, 1)}

    for num in (int(x) for x in a.beats.split(",")):
        beat = by_num[num]
        # items are ('action', text) or ('line', who, text) — unpack by kind
        lines = [(it[1], it[2]) for it in beat["items"] if it[0] == "line"]
        if a.text:
            lines = [(lines[0][0] if lines else "VO", a.text)]
        if not lines:
            print(f"beat {num}: no spoken line")
            continue
        # clone from THIS beat's existing take when there is one, so the read
        # stays in the same voice and room as the rest of the episode
        # EMOTION TRANSFER: F5 takes no tone instructions — it inherits the
        # read of its reference. So a line's emotion is chosen by picking WHICH
        # of our own takes to clone from: the most panicked take voices the
        # panicked lines, the most exhausted one the tired lines. That is how
        # "say it a certain way, like a human" gets done with a free model
        # (founder's ask, 2026-07-30).
        rb = int(a.ref_beat or num)
        ref = clips / f"{rb:02d}-vo.mp3"
        # The reference TRANSCRIPT must be exactly what the reference audio
        # says: F5 derives the speaker's rate from duration/text-length, so an
        # abbreviated transcript makes it think he speaks slowly and it
        # stretches the output (a hand-written half-transcript turned a 12.5s
        # line into 27s, 2026-07-31). Take it from the script, always.
        ref_text = ref_line(by_num, rb) or clean_speech(strip_inline_md(lines[0][1]))
        if not ref.exists():
            ref, rb = next(clips.glob("*-vo.mp3")), 0
            ref_text = ref_line(by_num, int(ref.name[:2])) or ref_text
        # F5 wants 5-15s of reference; under ~4s the clone degrades and short
        # lines come out impossibly fast ("Something's coming." in 0.2s,
        # 2026-07-31). Substitute the longest take we own, which is always one
        # of the steady, level reads.
        if media_seconds(ref) < 4.0:
            longer = max((q for q in clips.glob("*-vo.mp3")),
                         key=media_seconds, default=None)
            if longer and media_seconds(longer) >= 4.0:
                print(f"  beat {num:02d}: reference {ref.name} is "
                      f"{media_seconds(ref):.1f}s — too short for F5, "
                      f"cloning {longer.name} instead", flush=True)
                ref = longer
                ref_text = ref_line(by_num, int(longer.name[:2])) or ref_text
        with tempfile.TemporaryDirectory() as td:
            ref_wav = Path(td) / "ref.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ref),
                            "-ar", "24000", "-ac", "1", str(ref_wav)], check=True)
            manifest_lines, parts, t = [], [], 0.0
            for li, (who, raw) in enumerate(lines):
                spoken = clean_speech(strip_inline_md(raw))
                # SENTENCE at a time: F5 batches long text internally and
                # crashed on every line over ~100 chars (beats 8/10/14, the
                # three longest). A sentence is also the natural prosodic
                # unit — reading a whole paragraph in one pass flattens it,
                # reading caption fragments shatters it.
                sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", spoken) if s.strip()]
                chunks, line_start = [], t
                for si, sent in enumerate(sents):
                    sp = Path(td) / f"l{li:02d}s{si:02d}.wav"
                    d = f5(ref_wav, ref_text, sent, sp)
                    chunks += align_chunks(sp, caption_chunks(sent), t)
                    parts.append(sp)
                    t += d + (GAP if si < len(sents) - 1 else 0.0)
                print(f"  beat {num:02d} line {li}: {t - line_start:.2f}s, "
                      f"{len(sents)} sentence(s), {len(chunks)} caption(s)", flush=True)
                manifest_lines.append({
                    "who": who.split("(")[0].strip().upper() or "VO",
                    "text": spoken, "start": round(line_start, 3),
                    "end": round(t, 3), "chunks": chunks})
                t += GAP
            # concat with the breath gaps baked in
            lst = Path(td) / "list.txt"
            sil = Path(td) / "sil.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                            "-i", f"anullsrc=r=24000:cl=mono", "-t", str(GAP),
                            str(sil)], check=True)
            seq = []
            for i, p in enumerate(parts):
                seq.append(p)
                if i < len(parts) - 1:
                    seq.append(sil)
            lst.write_text("\n".join(f"file '{p}'" for p in seq))
            mp3 = clips / f"{num:02d}-vo.mp3"
            # archive the outgoing take — R6, nothing is deleted
            if mp3.exists():
                arch = clips / "vo-archive"
                arch.mkdir(exist_ok=True)
                n = len(list(arch.glob(f"{num:02d}-vo.v*.mp3"))) + 2
                mp3.replace(arch / f"{num:02d}-vo.v{n}.mp3")
                j = mp3.with_suffix(".json")
                if j.exists():
                    j.replace(arch / f"{num:02d}-vo.v{n}.json")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                            "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                            "-b:a", "128k", str(mp3)], check=True)
        (clips / f"{num:02d}-vo.json").write_text(json.dumps(
            {"engine": "f5-tts-v1-base", "total_s": round(t - GAP, 3),
             "lines": manifest_lines}, indent=1))
        print(f"beat {num:02d}: {len(manifest_lines)} line(s), {t - GAP:.1f}s [f5-tts]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
