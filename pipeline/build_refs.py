#!/usr/bin/env python3
"""Reference voices for Chatterbox cloning — identity continuity across
the engine swap. Each voice in the genome's voices.yaml cast (plus the
narrator and default pool) gets ~10s of kokoro speech saved to
~/.cache/banyan-tts/cb-refs/<voice>.wav; synth_vo --engine chatterbox
clones from these, so the tree still sounds like the tree (R4: the cast
is the founder's; this preserves it rather than recasting).

Runs under the kokoro TTS venv:
    <tts-venv>/bin/python3 pipeline/build_refs.py <genome>
"""

import sys
from pathlib import Path

import soundfile as sf
import yaml

REPO = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "banyan-tts"

# Default storyteller passage: long enough to carry timbre and cadence.
REF_TEXT = ("The town was quiet that evening. Someone had left a lantern "
            "burning by the gate, and the light moved a little in the wind. "
            "Nobody knew yet what the morning would bring, but the fields "
            "were watered, the ledger was balanced, and for one long moment "
            "everything simply held still.")

# One shared passage made every clone converge toward the same read — the
# cast stopped sounding like different PEOPLE (founder wince, 2026-07-24:
# "voices are mixed up"). Per-voice character text + the cast's own speeds
# + a small pitch offset widen the separation the clone locks onto. The
# narrator bm_fable stays untouched — that voice is the tree's released
# identity. Offsets are semitones, applied losslessly via resample+tempo.
# Measured 2026-07-25 (`pipeline/qa_voices.py`): the whole male cast landed
# inside a 20 Hz band (tree 118, guard 121, assessor 127, farmer 127,
# scavenger 136) — the acoustic cause of the founder's "voices are mixed
# up." Offsets below are sized to put every character in its OWN band:
# farmer ~95, tree ~118 (untouched — released identity), assessor ~150,
# scavenger ~180, magistrate ~206. Re-measure after any change.
VOICE_SHAPING = {
    "am_puck":     {"speed": 1.12, "pitch": +7.0, "text": (
        "Okay okay okay — hear me out. It fell off the cart! On the ground! "
        "That's basically public property. You know what, forget the apple. "
        "This is the best day I've had in three weeks, and one of those days "
        "included a moat. A MOAT. I'm not even joking, ask anyone.")},
    "bm_george":   {"speed": 0.95, "pitch": -5.0, "text": (
        "Field started drinking again. Don't much care why. Rain comes, or "
        "it doesn't. Weeds come, they get pulled. You want something said, "
        "say it plain, and don't waste my morning. Harvest won't wait on "
        "either of us, and the cart doesn't load itself.")},
    "bm_daniel":   {"speed": 1.0, "pitch": +3.5, "text": (
        "Item one: a dwelling, category shack, occupancy one. Item two: "
        "three rocks, noted individually. Item three: one tree, deciduous, "
        "responsive. Occupation: answers questions. Everything is in order "
        "when everything is written down. I will now count the fence posts.")},
    "bf_isabella": {"speed": 1.05, "pitch": 0.0, "text": (
        "The law does not concern itself with whether a thing is unusual. "
        "It concerns itself with which category the thing belongs to. Bring "
        "me the correct form, and the correct form will be considered, in "
        "the correct order, at the correct time. That is how a kingdom works.")},
}


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ff = sys.argv[2] if len(sys.argv) > 2 else "ffmpeg"
    import subprocess

    from kokoro_onnx import Kokoro
    k = Kokoro(str(CACHE / "kokoro-v1.0.onnx"), str(CACHE / "voices-v1.0.bin"))
    vcfg = yaml.safe_load((REPO / "genomes" / sys.argv[1] / "voices.yaml").read_text())

    voices = {vcfg.get("narrator", "af_sarah")}
    voices.update(vcfg.get("default_pool") or [])
    for entry in (vcfg.get("cast") or {}).values():
        voices.add(entry["voice"])

    out = CACHE / "cb-refs"
    out.mkdir(parents=True, exist_ok=True)
    for v in sorted(voices):
        shape = VOICE_SHAPING.get(v, {})
        samples, sr = k.create(shape.get("text", REF_TEXT), voice=v,
                               speed=shape.get("speed", 1.0), lang="en-us")
        dest = out / f"{v}.wav"
        st = float(shape.get("pitch", 0.0))
        if st:
            factor = 2 ** (st / 12)
            raw = out / f"{v}.raw.wav"
            sf.write(str(raw), samples, sr)
            subprocess.run(
                [ff, "-y", "-loglevel", "error", "-i", str(raw), "-af",
                 f"asetrate={sr}*{factor:.6f},aresample={sr},atempo={1 / factor:.6f}",
                 str(dest)], check=True)
            raw.unlink()
        else:
            sf.write(str(dest), samples, sr)
        print(f"ref {v}: {len(samples) / sr:.1f}s"
              + (f" (pitch {st:+.1f}st)" if st else ""))
    print(f"✓ {len(voices)} reference voices in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
