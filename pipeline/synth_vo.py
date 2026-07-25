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
from direction import (ACTION_MAX_HOLD, ACTION_MAX_WORDS,  # noqa: E402,F401
                       ACTION_MIN_HOLD, action_hold, displayable_action,
                       is_beat_pause)
from render_t1 import extract_script, parse_frames, strip_inline_md  # noqa: E402
from render_t2 import clean_speech, load_voices, speaker_key, voice_for  # noqa: E402

GAP_DEFAULT, GAP_TRAIL, GAP_SNAP, GAP_BEAT = 0.50, 0.35, 0.18, 1.2
SNAP_WORDS = 4          # both lines this short → rapid exchange
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


