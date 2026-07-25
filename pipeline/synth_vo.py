#!/usr/bin/env python3
"""Directed VO synthesis — the voice track with performance direction.

Two local engines, both $0:

  kokoro      kokoro-82M (the released season's cast). Fast, clean, but
              cannot act — rhythm only. Runs under the kokoro TTS venv.
  chatterbox  Chatterbox 0.5B (MIT, Resemble AI) on Apple-Silicon MPS.
              Zero-shot voice cloning from per-character reference wavs
              (built FROM the kokoro cast by build_refs.py, so every
              character keeps their established voice) plus real emotion
              control — per-line exaggeration/pace from script cues.
              Outputs carry Resemble's Perth watermark (a responsible-AI
              feature; the tree labels its AI content anyway, §7.2).
              Runs under the chatterbox venv (torch/MPS, python3.11).

Shared direction layer (loop cycles 001-002):
  trim        engine head/tail silence is cut — every pause is authored
  gaps        a standalone 'Beat.' breathes ~1.2s, rapid short exchanges
              snap at ~0.18s, trailing ellipses hang, sentence ends ~0.5s
  emotion     (chatterbox) exaggeration/cfg from parenthetical hints
              ('(quiet)', '(panicking)', '(without emotion)'),
              punctuation shape, and caps emphasis
  chunks      every caption chunk is synthesized SOLO to measure its
              spoken length → manifest lines[].chunks → render_t3 burns
              captions on the voice, not on a word-count guess

Writes NN-vo.mp3 + NN-vo.json into the node's clips dir; existing takes
are archived to clips/vo-archive/ first (R6: nothing deleted).

    <engine-venv>/bin/python3 pipeline/synth_vo.py <ffmpeg> <genome> \
        <node-slug> [...] [--engine kokoro|chatterbox]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from captions import caption_chunks  # noqa: E402
from render_t1 import extract_script, parse_frames, strip_inline_md  # noqa: E402
from render_t2 import clean_speech, load_voices, speaker_key, voice_for  # noqa: E402

GAP_DEFAULT, GAP_TRAIL, GAP_SNAP, GAP_BEAT = 0.50, 0.35, 0.18, 1.2
SNAP_WORDS = 4          # both lines this short → rapid exchange
ACTION_MAX_WORDS = 14   # stage directions this short become on-screen beats
ACTION_MIN_HOLD = 1.4   # seconds a displayed action owns the track
TRIM_THRESH = 0.003     # amplitude floor for head/tail engine silence
TRIM_PAD_S = 0.04
CACHE = Path.home() / ".cache" / "banyan-tts"

# emotion vocabulary: parenthetical direction → (exaggeration, cfg_weight).
# cfg lower = more deliberate/dramatic pacing; exaggeration 0.5 = neutral.
EMOTION_HINTS = {
    ("quiet", "whisper", "small", "soft"):        (0.42, 0.50),
    ("flat", "deadpan", "without emotion"):       (0.30, 0.55),
    ("panic", "scream", "frantic", "alarmed"):    (1.10, 0.25),
    ("excited", "delighted", "joy", "triumphant"): (0.95, 0.28),
    ("tired", "weary", "sigh"):                   (0.45, 0.45),
    ("angry", "furious", "snaps"):                (1.00, 0.28),
}
# The house register is DEADPAN (R3: comedy from the gap between a dry
# report and an absurd world). A "storyteller lean" default (0.65) put the
# wrong emotion on every unmarked line — founder, 2026-07-25: "voices are
# giving off the wrong emotions which makes it confusing." Unmarked lines
# are dry; only explicit script cues push a performance.
EMOTION_DEFAULT = (0.40, 0.50)


def direction_for(raw_who: str, text: str) -> tuple:
    """(exaggeration, cfg_weight) from script cues; kokoro ignores this."""
    hint = raw_who.lower() + " " + " ".join(re.findall(r"\(([^)]*)\)", text)).lower()
    ex, cfg = EMOTION_DEFAULT
    for keys, (e, c) in EMOTION_HINTS.items():
        if any(k in hint for k in keys):
            ex, cfg = e, c
            break
    # No punctuation-guessed emotion: this script uses '!' and CAPS for
    # bureaucratic emphasis, not shouting, and guessing put the wrong
    # performance on straight lines. Only '…' (hesitation) survives, as pace.
    if "…" in text or "..." in text:
        cfg += 0.05
    return min(max(ex, 0.30), 1.20), min(max(cfg, 0.20), 0.60)


class KokoroEngine:
    name = "kokoro-82M"

    sr = 24000

    def __init__(self):
        from kokoro_onnx import Kokoro
        self.k = Kokoro(str(CACHE / "kokoro-v1.0.onnx"), str(CACHE / "voices-v1.0.bin"))

    def synth(self, text: str, voice: str, speed: float, direction: tuple):
        samples, sr = self.k.create(text, voice=voice, speed=speed, lang="en-us")
        return np.asarray(samples), sr


class ChatterboxEngine:
    name = "chatterbox-0.5B"

    def __init__(self):
        import torch
        _load = torch.load  # checkpoints are saved CUDA-side; map locally
        torch.load = lambda *a, **kw: _load(*a, **{**kw, "map_location": "cpu"})
        from chatterbox.tts import ChatterboxTTS
        self.torch = torch
        self.dev = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = ChatterboxTTS.from_pretrained(device=self.dev)
        self.sr = self.model.sr
        self.refs = CACHE / "cb-refs"
        if not self.refs.is_dir():
            raise SystemExit("no reference voices — run pipeline/build_refs.py "
                             "(kokoro venv) to build ~/.cache/banyan-tts/cb-refs/")

    def synth(self, text: str, voice: str, speed: float, direction: tuple):
        ref = self.refs / f"{voice}.wav"
        if not ref.exists():
            raise SystemExit(f"missing reference voice {ref} — extend build_refs.py")
        ex, cfg = direction
        # NO torch.manual_seed here: seeding the MPS generator kills the
        # process silently at ~sampling step 250 (Metal pipeline dies, no
        # traceback — verified empirically on 002b, five identical deaths;
        # unseeded, the same generate succeeds). Takes are therefore
        # non-deterministic on MPS; keep the take you like (R6 archives).
        wav = self.model.generate(text, audio_prompt_path=str(ref),
                                  exaggeration=ex, cfg_weight=cfg)
        out = wav.squeeze(0).cpu().numpy()
        if self.dev == "mps":
            # MPS accumulates across generate() calls; a long dialogue beat
            # (002b: 8 lines + chunk measures) climbs until the OS SIGKILLs
            # the process with no traceback. Release after every take.
            self.torch.mps.empty_cache()
        return out, self.model.sr


def trim_silence(x: np.ndarray, sr: int) -> np.ndarray:
    idx = np.where(np.abs(x) > TRIM_THRESH)[0]
    if not len(idx):
        return x
    a = max(0, int(idx[0]) - int(TRIM_PAD_S * sr))
    b = min(len(x), int(idx[-1]) + int(TRIM_PAD_S * sr))
    return x[a:b]


def pacing(base: float, who: str, text: str) -> float:
    """Per-line speed from delivery hints and punctuation shape (kokoro)."""
    spd = base
    if any(w in who.lower() for w in ("quiet", "whisper", "small")):
        spd = max(0.92, spd - 0.10)
    if text.rstrip().endswith(("?", "!")) or "??" in text:
        spd += 0.07
    if text.strip().startswith(("…", "...")):
        spd -= 0.04
    if len(text.split()) <= 3:
        spd -= 0.03  # short lines land, they don't rush
    return spd


def gap_before(prev_text: str | None, cur_text: str, beat_pause: bool) -> float:
    """The pause a line takes before speaking, from script intent."""
    if prev_text is None:
        return 0.0
    if beat_pause:
        return GAP_BEAT
    if (len(prev_text.split()) <= SNAP_WORDS
            and len(cur_text.split()) <= SNAP_WORDS):
        return GAP_SNAP
    if prev_text.rstrip().endswith(("…", "...", "—", ",")):
        return GAP_TRAIL
    return GAP_DEFAULT


def is_beat_pause(action_text: str) -> bool:
    """A standalone 'Beat.' / 'A beat.' stage direction is a scripted
    breath (cycle-001 defect 14: the render dropped it entirely)."""
    return bool(action_text) and action_text.strip().rstrip(".").lower() in ("beat", "a beat")


def displayable_action(action_text: str) -> str | None:
    """Short stage directions become on-screen beats (cycle 006: the tree's
    entire performance — 'One leaf tilts.' — lived in action lines that
    never reached the viewer). Long paragraphs are camera direction and
    stay off screen; their FIRST sentence is used when it is short enough."""
    t = action_text.strip()
    if not t or is_beat_pause(t):
        return None
    first = re.split(r"(?<=[.!?…])\s+", t)[0]
    if re.search(r"\b(camera|frame|shot|close-up|wide|montage|cut to|we see)\b",
                 first, re.I):
        return None  # camera direction — production language, not story
    if len(first.split()) <= ACTION_MAX_WORDS:
        return first
    return None


def action_hold(text: str) -> float:
    """Seconds a displayed stage direction owns: reading time + a breath."""
    return max(ACTION_MIN_HOLD, 0.28 * len(text.split()) + 0.6)


LONG_LINE_WORDS = 22   # chatterbox generations past ~250 sampling steps die
CHUNK_JOIN_GAP = 0.12  # breath between stitched chunk takes


def measured_chunks(engine, text: str, voice: str, spd: float, direction: tuple,
                    start: float, end: float) -> list:
    """Caption chunks timed by their own measured synthesis, scaled into
    the line's real speech window [start, end]."""
    chunks = caption_chunks(strip_inline_md(text))
    if len(chunks) == 1:
        return [{"text": chunks[0], "start": round(start, 3), "end": round(end, 3)}]
    durs = []
    for c in chunks:
        speak = clean_speech(c)
        if not speak:
            # display-only stage direction ('(aggressively nothing)') —
            # nominal read time, the voice never says it
            durs.append(0.6)
            continue
        samples, sr = engine.synth(speak, voice, spd, direction)
        durs.append(len(trim_silence(samples, sr)) / sr)
    total = sum(durs) or 1.0
    spans, t = [], start
    for c, d in zip(chunks, durs):
        dt = (end - start) * d / total
        spans.append({"text": c, "start": round(t, 3), "end": round(t + dt, 3)})
        t += dt
    return spans


def synth_line(engine, text: str, voice: str, spd: float, direction: tuple):
    """One line's audio + caption spans (relative to the line's own start).

    Short lines: one generate, chunks measured separately (their takes are
    only used for timing). LONG lines on chatterbox are built by STITCHING
    the chunk takes themselves: a single long generation dies silently on
    MPS at ~250 sampling steps (the 002b saga — five identical deaths),
    and stitching also makes caption timing exact rather than measured."""
    chunks = caption_chunks(strip_inline_md(text))
    speak_full = clean_speech(text)
    long_line = (engine.name.startswith("chatterbox")
                 and len(speak_full.split()) > LONG_LINE_WORDS
                 and len(chunks) > 1)
    if not long_line:
        samples, sr = engine.synth(speak_full, voice, spd, direction)
        samples = trim_silence(samples, sr)
        dur = len(samples) / sr
        return samples, sr, measured_chunks(engine, text, voice, spd,
                                            direction, 0.0, dur)
    takes = []
    for c in chunks:
        speak = clean_speech(c)
        if not speak:
            takes.append((c, None))
            continue
        s, sr = engine.synth(speak, voice, spd, direction)
        takes.append((c, trim_silence(s, sr)))
    sr = engine.sr
    ref = next(s for _, s in takes if s is not None)
    gap = np.zeros(int(CHUNK_JOIN_GAP * sr), dtype=ref.dtype)
    hold = np.zeros(int(0.5 * sr), dtype=ref.dtype)  # display-only chunk
    pieces, spans, t = [], [], 0.0
    for i, (c, s) in enumerate(takes):
        seg = s if s is not None else hold
        spans.append({"text": c, "start": round(t, 3),
                      "end": round(t + len(seg) / sr + CHUNK_JOIN_GAP, 3)})
        pieces.append(seg)
        t += len(seg) / sr
        if i < len(takes) - 1:
            pieces.append(gap)
            t += CHUNK_JOIN_GAP
    spans[-1]["end"] = round(t, 3)
    return np.concatenate(pieces), sr, spans


def archive(clips_dir: Path, beat_num: int) -> None:
    arch = clips_dir / "vo-archive"
    for ext in ("mp3", "json"):
        old = clips_dir / f"{beat_num:02d}-vo.{ext}"
        if not old.exists():
            continue
        arch.mkdir(exist_ok=True)
        dest, n = arch / old.name, 2
        while dest.exists():
            dest = arch / f"{old.stem}.v{n}.{ext}"
            n += 1
        old.rename(dest)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ffmpeg")
    p.add_argument("genome")
    p.add_argument("slugs", nargs="+")
    p.add_argument("--engine", choices=["kokoro", "chatterbox"], default="kokoro")
    args = p.parse_args()

    engine = KokoroEngine() if args.engine == "kokoro" else ChatterboxEngine()
    genome_dir = REPO / "genomes" / args.genome
    vcfg = load_voices(genome_dir)

    for slug in args.slugs:
        node_dir = genome_dir / "nodes" / slug
        frames = parse_frames(extract_script((node_dir / "node.md").read_text()))
        clips_dir = node_dir / "clips"
        clips_dir.mkdir(exist_ok=True)
        for beat_num, f in enumerate(frames, start=1):
            # walk items in order: lines speak; short stage directions
            # become timed on-screen beats (cycle 006 — the tree's replies
            # lived in actions that never reached the viewer); a 'Beat.'
            # becomes the next line's breath
            events, pending_beat = [], False
            for it in f["items"]:
                if it[0] == "action":
                    t = strip_inline_md(it[1])
                    if is_beat_pause(t):
                        pending_beat = True
                        continue
                    disp = displayable_action(t)
                    if disp:
                        events.append(("action", disp))
                elif it[0] == "line":
                    text = strip_inline_md(it[2])
                    if clean_speech(text):
                        events.append(("line", it[1], text, pending_beat))
                        pending_beat = False
            if not any(e[0] == "line" for e in events):
                continue

            sr = engine.sr
            pieces, manifest, actions, cursor, prev_text = [], [], [], 0.0, None
            for ev in events:
                if ev[0] == "action":
                    hold = action_hold(ev[1])
                    pieces.append(np.zeros(int(hold * sr), dtype=np.float32))
                    actions.append({"text": ev[1],
                                    "start": round(cursor + 0.05, 3),
                                    "end": round(cursor + hold, 3)})
                    cursor += hold
                    prev_text = None  # the beat resets exchange rhythm
                    continue
                _, raw_who, text, beat_pause = ev
                who = speaker_key(raw_who) or "VO"
                voice, base = voice_for(who, vcfg)
                print(f"    {slug} b{beat_num:02d} {who} ({voice}) "
                      f"{len(text.split())}w…", flush=True)
                spd = pacing(base, raw_who, text)
                direction = direction_for(raw_who, text)
                samples, _, rel_spans = synth_line(engine, text, voice, spd, direction)
                gap = gap_before(prev_text, text, beat_pause)
                if gap:
                    pieces.append(np.zeros(int(gap * sr), dtype=samples.dtype))
                    cursor += gap
                start = cursor
                cursor += len(samples) / sr
                manifest.append({
                    "who": who, "text": text,
                    "start": round(start, 3), "end": round(cursor, 3),
                    "chunks": [{"text": c["text"],
                                "start": round(start + c["start"], 3),
                                "end": round(start + c["end"], 3)}
                               for c in rel_spans],
                })
                pieces.append(samples)
                prev_text = text
            # short settle so the last word never clips at the beat edge
            pieces.append(np.zeros(int(0.30 * sr), dtype=pieces[-1].dtype))
            cursor += 0.30

            archive(clips_dir, beat_num)
            audio = np.concatenate(pieces)
            wav = clips_dir / "tmp.wav"
            sf.write(str(wav), audio, sr)
            mp3 = clips_dir / f"{beat_num:02d}-vo.mp3"
            subprocess.run([args.ffmpeg, "-y", "-loglevel", "error", "-i", str(wav),
                            "-c:a", "libmp3lame", "-q:a", "4", str(mp3)], check=True)
            wav.unlink()
            (clips_dir / f"{beat_num:02d}-vo.json").write_text(json.dumps(
                {"cast": "voices.yaml", "engine": engine.name,
                 "directed": "synth_vo v3", "lines": manifest,
                 "actions": actions,
                 "total_s": round(cursor, 3)}, indent=1))
            print(f"{slug} beat {beat_num:02d}: {len(manifest)} lines, "
                  f"{cursor:.1f}s [{engine.name}]")
    print("VO_DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
