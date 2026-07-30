#!/usr/bin/env python3
"""Deterministic synthesized sound effects for the assembler ($0, no assets).

The scripts write their own sound design — "one mechanical keyboard, very
fast — then it stops", "the sound of a cooling fan spinning down" — and until
cycle 012 none of it was ever built. These are the four cues episode 1 needs,
synthesized from noise and sine partials with a fixed seed so a re-render is
bit-identical (provenance: no downloaded samples, no license questions).

Each function writes a mono 44.1k PCM wav and returns its path. Placement is
the assembler's job (clips/sound.yaml → render_t3 single-mix).
"""

import struct
import wave
from pathlib import Path

import numpy as np

SR = 44100


def _write(path: Path, x: np.ndarray) -> Path:
    x = np.clip(x, -1.0, 1.0)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return path


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    """Exponential attack/decay envelope, in seconds."""
    t = np.arange(n) / SR
    a = 1 - np.exp(-t / max(attack, 1e-4))
    d = np.exp(-t / max(decay, 1e-4))
    return a * d


def room_hum(path: Path, dur: float) -> Path:
    """A machine room at 3 a.m.: mains hum + PC-fan noise floor. Its job is
    to exist so that its absence, at the fall, is audible."""
    rng = np.random.default_rng(12)
    n = int(dur * SR)
    t = np.arange(n) / SR
    hum = 0.28 * np.sin(2 * np.pi * 50 * t) + 0.12 * np.sin(2 * np.pi * 100 * t + 0.7)
    noise = rng.standard_normal(n)
    # one-pole lowpass ≈ fan wash
    out = np.empty(n)
    acc = 0.0
    k = 0.015
    for i in range(n):
        acc += k * (noise[i] - acc)
        out[i] = acc
    bed = 0.5 * hum + 3.5 * out
    fade = min(int(0.4 * SR), n // 4)
    bed[:fade] *= np.linspace(0, 1, fade)
    return _write(path, 0.22 * bed / (np.abs(bed).max() or 1))


def keyboard(path: Path, dur: float, stop_at: float | None = None) -> Path:
    """Very fast mechanical typing that stops dead. Keystrokes are short
    band-limited clicks with velocity jitter; the stop is the point."""
    rng = np.random.default_rng(3)
    n = int(dur * SR)
    x = np.zeros(n)
    t_end = stop_at if stop_at is not None else dur
    t = 0.15
    while t < t_end:
        i = int(t * SR)
        kn = int(0.035 * SR)
        if i + kn >= n:
            break
        click = rng.standard_normal(kn) * _env(kn, 0.0006, 0.006)
        # ring the keycap: a damped partial per stroke, pitch jittered
        f = rng.uniform(1600, 2600)
        click += 0.5 * np.sin(2 * np.pi * f * np.arange(kn) / SR) * _env(kn, 0.0004, 0.004)
        x[i:i + kn] += rng.uniform(0.35, 1.0) * click
        t += rng.uniform(0.055, 0.115)          # ~9-14 strokes/s: very fast
    return _write(path, 0.5 * x / (np.abs(x).max() or 1))


def mug_hit(path: Path) -> Path:
    """A ceramic mug meeting the floor: three inharmonic ring partials over a
    dull knock. Small on purpose — it lands inside silence."""
    dur = 0.9
    n = int(dur * SR)
    t = np.arange(n) / SR
    ring = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
               for f, a, d in ((2140, 0.5, 0.06), (3466, 0.35, 0.045), (5210, 0.2, 0.03)))
    rng = np.random.default_rng(7)
    knock = rng.standard_normal(n) * _env(n, 0.0005, 0.012)
    thump = 0.6 * np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.05)
    x = ring + 0.4 * knock + thump
    return _write(path, 0.8 * x / (np.abs(x).max() or 1))


def fan_spindown(path: Path, dur: float) -> Path:
    """A cooling fan spinning down to nothing — the scripted sound of the
    machine (and its operator) switching off. Pitch and level glide to zero."""
    rng = np.random.default_rng(21)
    n = int(dur * SR)
    t = np.arange(n) / SR
    g = np.maximum(0.0, 1 - t / dur) ** 1.6          # the glide
    # blade tone: a low rotor hum whose frequency falls with the glide
    phase = np.cumsum(2 * np.pi * (46 + 74 * g) / SR)
    rotor = np.sin(phase) * (0.5 + 0.5 * np.sin(phase * 2))
    noise = rng.standard_normal(n)
    out = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += (0.004 + 0.03 * g[i]) * (noise[i] - acc)  # wash darkens as it slows
        out[i] = acc
    x = (0.55 * rotor + 5.0 * out) * g
    return _write(path, 0.4 * x / (np.abs(x).max() or 1))


def footsteps_soil(path: Path, dur: float, period: float = 1.5,
                   grow: float = 0.0) -> Path:
    """Footsteps felt THROUGH SOIL, not heard through air: paired low thumps
    (a walker's two feet) with no transient click — pressure, not impact.
    `grow` > 0 swells the level across the cue (beat 15: it's getting closer)."""
    rng = np.random.default_rng(9)
    n = int(dur * SR)
    x = np.zeros(n)
    t = 0.35
    step = 0
    while t < dur - 0.3:
        i = int(t * SR)
        kn = int(0.28 * SR)
        if i + kn >= n:
            break
        tt = np.arange(kn) / SR
        f = rng.uniform(52, 62)
        thump = np.sin(2 * np.pi * f * tt) * _env(kn, 0.012, 0.07)
        thump += 0.3 * rng.standard_normal(kn) * _env(kn, 0.008, 0.03)  # soil grit
        amp = rng.uniform(0.8, 1.0) * (1.0 + grow * (t / dur))
        x[i:i + kn] += amp * thump
        # thump-THUMP: the second foot lands close behind the first
        step += 1
        t += (0.34 if step % 2 else period)
    return _write(path, 0.85 * x / (np.abs(x).max() or 1))


def terminal_keys(path: Path, dur: float) -> Path:
    """Text typing ITSELF: softer, steadier, more distant than human typing —
    the machine's voice, not the engineer's hands."""
    rng = np.random.default_rng(15)
    n = int(dur * SR)
    x = np.zeros(n)
    t = 0.2
    while t < dur - 0.1:
        i = int(t * SR)
        kn = int(0.02 * SR)
        if i + kn >= n:
            break
        click = rng.standard_normal(kn) * _env(kn, 0.0004, 0.003)
        f = rng.uniform(2400, 3200)
        click += 0.35 * np.sin(2 * np.pi * f * np.arange(kn) / SR) * _env(kn, 0.0003, 0.002)
        x[i:i + kn] += rng.uniform(0.5, 0.8) * click
        t += rng.uniform(0.05, 0.075)          # metronomic: no human jitter
    return _write(path, 0.35 * x / (np.abs(x).max() or 1))


SYNTHS = {
    "room_hum": lambda p, dur=2.0, **kw: room_hum(p, dur),
    "keyboard": lambda p, dur=4.0, stop_at=None, **kw: keyboard(p, dur, stop_at),
    "mug_hit": lambda p, **kw: mug_hit(p),
    "fan_spindown": lambda p, dur=3.0, **kw: fan_spindown(p, dur),
    "footsteps_soil": lambda p, dur=6.0, period=1.5, grow=0.0, **kw:
        footsteps_soil(p, dur, period, grow),
    "terminal_keys": lambda p, dur=3.0, **kw: terminal_keys(p, dur),
}


if __name__ == "__main__":  # audition: python3 sfx.py /tmp/sfx
    import sys
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sfx")
    out.mkdir(parents=True, exist_ok=True)
    room_hum(out / "room_hum.wav", 4)
    keyboard(out / "keyboard.wav", 5, stop_at=4.2)
    mug_hit(out / "mug_hit.wav")
    fan_spindown(out / "fan_spindown.wav", 3.2)
    print(f"wrote 4 cues to {out}")
