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
    # recast: his voice stays am_adam, this only moves his BAND.
    #
    # -9st, 2026-08-21. THE FOUNDER REVERSED THE +9st THAT USED TO BE HERE:
    # "guard 1 sounds like a little kid — why did you change his voice?" He is
    # right and the number says so — +9st shipped him at 192.0/181.8/212.4 Hz,
    # which is not an adult man. +9st was never his pick; it was taken on the
    # steward's own metric on 08-20, which is the thing the ONE SAMPLE rule
    # exists to stop.
    #
    # WHY THE OLD REASONING PICKED A CHILD. It applied a flat ">20 Hz from
    # every other character" bar, and against a tree at ~110 that bar leaves
    # only <87 or >167. But that is not the bar this show actually uses:
    # qa_voices.py flags a pair only when the pitch bands overlap AND the
    # centroids sit close, because two voices a listener can tell apart by
    # timbre are not confusable at any pitch. The tree measures centroid 3991
    # against every other character's 1900-2800 — it is the brightest thing in
    # the cast by 1100 Hz and nobody is confusable with it on pitch alone.
    # GUARD 2/VO already passes the gate at 22.4 Hz, ASSESSOR/VO at 19.0. So
    # GUARD 1 never needed to clear the tree, and clearing it is what pushed
    # him into the child register.
    #
    # THE BAND THAT IS ACTUALLY FREE. The voices GUARD 1 can be confused with
    # are the ones sharing his timbre — GUARD 2 above all (Δcentroid 28 Hz, so
    # pitch is the ONLY cue), then ASSESSOR, FARMER, SCAVENGER. Their measured
    # bands: FARMER 86.2 (68.8-90.9), ASSESSOR 132.2 (123.7-150.0), GUARD 2
    # 135.6, SCAVENGER 170.2 (151.5-189.0). That leaves one adult window,
    # 95-122 Hz, between the farmer's ceiling and the assessor's floor — and
    # the deep <90 window the old note reached for is the FARMER's, not empty.
    #
    # -9st IS MEASURED, nine rendered takes of all three of his lines:
    #   -9st (ref 77.2) b05 -> 97.6, 108.6, 104.3
    #                   b07 -> 134.8, 124.6,  96.4
    #                   b09 -> 120.6, 110.1, 113.7   7/9 inside 95-122
    #   -8st (ref 81.1) b05 -> 104.3, 85.4  b09 -> 116.5, 96.3   3/4
    #   -7st (ref 83.9) b05 ->  77.8, 102.4 b09 -> 103.0, 125.0  2/4
    # The attractor at ~110 Hz is the REASON a deep ref works rather than the
    # reason it fails: the deeper the ref, the more the attractor dominates and
    # the tighter the takes land — -9st's spread on b05 is 11 Hz where -7st's
    # is 47. The old note read that same pull as a defect only because it was
    # trying to escape a band it did not need to escape. b07 is the one line
    # that strays (5 words; short lines have too little voiced material to hold
    # a ref — measured and known since 08-19), so b07 is rolled until it lands.
    "am_adam":     {"speed": 1.08, "pitch": -9.0, "text": (
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
