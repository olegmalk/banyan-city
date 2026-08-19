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
# Calibrated against RENDERED audio (chatterbox tracks the ref loosely:
# measured ref -> rendered was 104->93, 116->108, 174->180, 200->189).
# Target rendered bands: farmer ~87, tree ~108 (ref untouched — released
# identity), assessor ~132, scavenger ~163, magistrate ~190. Verified on
# re-voiced 005: -5st left the farmer only 7 Hz under the tree, so -7.5st. Two earlier
# passes each fixed one collision and created another (scavenger vs
# assessor, then scavenger vs magistrate) — always re-run qa_voices on a
# freshly synthesized episode, not just on the refs.
VOICE_SHAPING = {
    "am_puck":     {"speed": 1.12, "pitch": +7.5, "text": (
        "Okay okay okay — hear me out. It fell off the cart! On the ground! "
        "That's basically public property. You know what, forget the apple. "
        "This is the best day I've had in three weeks, and one of those days "
        "included a moat. A MOAT. I'm not even joking, ask anyone.")},
    "bm_george":   {"speed": 0.95, "pitch": -7.5, "text": (
        "Field started drinking again. Don't much care why. Rain comes, or "
        "it doesn't. Weeds come, they get pulled. You want something said, "
        "say it plain, and don't waste my morning. Harvest won't wait on "
        "either of us, and the cart doesn't load itself.")},
    "bm_daniel":   {"speed": 1.0, "pitch": +1.5, "text": (
        "Item one: a dwelling, category shack, occupancy one. Item two: "
        "three rocks, noted individually. Item three: one tree, deciduous, "
        "responsive. Occupation: answers questions. Everything is in order "
        "when everything is written down. I will now count the fence posts.")},
    "bf_isabella": {"speed": 1.05, "pitch": +2.0, "text": (
        "The law does not concern itself with whether a thing is unusual. "
        "It concerns itself with which category the thing belongs to. Bring "
        "me the correct form, and the correct form will be considered, in "
        "the correct order, at the correct time. That is how a kingdom works.")},
    # GUARD 1 — dogged, literal, chases first and reasons second. NOT a taste
    # recast: his voice stays am_adam, this only moves his BAND. He was cast
    # after the 2026-07-25 shaping pass too, so his ref was the shared REF_TEXT
    # at pitch 0.0 — measured 117.6 Hz against bm_fable's 116.5, i.e. 1.1 Hz
    # from the tree. He passed 0819c at 131.9 Hz purely because chatterbox
    # happened to push that take up; takes are unseeded on MPS, so the next
    # re-voice could have landed him on the sapling with nothing changed.
    #
    # +9st is MEASURED, not chosen for tidiness. Sixteen rendered takes of his
    # beat-05 line across seven offsets (the ref number predicts nothing —
    # engine finding 2 on the picker page):
    #   -9st (ref  77.2) -> 117.1, 91.6, 73.7          erratic; 117 is ON the tree
    #   -8st (ref  81.1) -> 77.7-126.0 over 7 takes    43% inside the bar
    #   -7st (ref  83.9) -> 77.9, 90.1, 103.4, 110.1   erratic
    #   -6st (ref  87.9) -> 92.7                       14.7 Hz from the tree
    #   +6st (ref 160.0) -> 145.9                      lands on GUARD 2
    #   +7st (ref 170.8) -> 175.2                      10.7 Hz from the scavenger
    #   +8st (ref 181.8) -> 157.9, 167.2, 187.5, 193.5 spread 35.6
    #   +9st (ref 192.0) -> 181.1, 183.2, 189.0        spread 7.9, all clear
    # Down is unusable BECAUSE the engine's attractor sits at ~110 Hz, which is
    # exactly where the tree is: every deep ref that slips gets pulled onto the
    # sapling, which is the defect being fixed. Up is the only direction where
    # a slip lands nowhere. Episode 2's occupied bands are tree 107, GUARD 2
    # 147, scavenger 164 — so >20 Hz from the tree AND from GUARD 2 leaves
    # exactly two windows, <87 and >167, and only one of them holds still.
    "am_adam":     {"speed": 1.08, "pitch": +9.0, "text": (
        "He went this way. I saw him do it. I know what I saw. If it is not "
        "theft then what is it, because he took the apple and now the apple is "
        "gone. We can go back and look at the cart again. I do not mind "
        "looking twice.")},
    # GUARD 2 — the rules-lawyer. FOUNDER'S PICK, 2026-08-19, verbatim "B" on
    # the picker at review/ep2-guard2-voice-0819 (candidates.yaml `picked:`).
    # He heard the defect first — "guard 2 has the same voice as the sapling"
    # — and he was right to within 1.7 Hz: GUARD 2 was cast (am_echo) AFTER
    # the 2026-07-25 shaping pass, so he had no entry here and cloned from the
    # shared REF_TEXT at speed 1.0 / pitch 0.0, straight onto the tree.
    # Candidate B's exact recipe, measured 146.8 Hz on the RENDERED take
    # (39.4 Hz clear of the tree). Base voice changed am_echo -> am_michael in
    # voices.yaml by the same ruling; taste, so do not re-tune it (R4).
    "am_michael":  {"speed": 1.05, "pitch": +4.0, "text": (
        "Technically that is a different violation. Check the schedule: "
        "unlicensed consumption is section four, not section two. I am not "
        "saying we let him go. I am saying the form we would need does not "
        "exist, and I am not going to invent one standing in a field.")},
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
