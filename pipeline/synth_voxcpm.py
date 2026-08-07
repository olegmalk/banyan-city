#!/usr/bin/env python3
"""VoxCPM2 voice — the engine that takes DIRECTION, not just dials.

    python3 pipeline/synth_voxcpm.py sapling 001 [--beats 2,3] [--dry-run]

WHY THIS ENGINE (founder, 2026-07-31→08-01): "F5 seems to be even worse than
chatterbox… you need to control it more mindfully, maybe you are not using it
right", then "use the high quality audio model". Both complaints were fair, and
both were really the same complaint — there was nothing to control:

  kokoro-82M    fixed voices, no performance control at all
  chatterbox    two numeric dials (exaggeration, cfg_weight) and nothing else
  f5-tts        NO tone input whatsoever — the only lever is which of our own
                takes we clone the read from. Also CC BY-NC: unpublishable, so
                the tuning argument was moot.
  voxcpm2       a natural-language style prompt PER LINE, on top of cloning

VoxCPM2 takes `(a tired, flat delivery)Production went down at 2:41.` — the
parenthetical is its documented control interface, not something it reads aloud.
That matters because it is the exact mistake VoxCPM-**0.5B** made when we tried
it: 0.5B spoke the direction out loud. Different model, opposite behaviour;
do not carry the 0.5B lesson over to this one.

And our script has carried the directions all along — `**VO (tired, flat):**`,
`**VO (relieved, almost cheerful):**`, `**VO (quiet):**`. They were written for
a human reader and no engine could use them until now. DIRECTION below maps them
to prose; nothing new is invented, the script is simply finally being read.

Licence: Apache-2.0, "free for commercial use" per the model card, verified
2026-08-01 and listed explicitly in licence_gate.MODEL_LICENCES. That is not a
detail — f5-tts came within one command of voicing a whole episode before anyone
noticed it was CC BY-NC.

§6: refuses any node the founder has not approved, same gate as every other
media tool here.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

MODEL = "openbmb/VoxCPM2"
ENGINE = "voxcpm2 (openbmb/VoxCPM2)"

# Script cue -> style prose. The house register is DEADPAN (R3: the comedy is
# the gap between a dry incident report and an absurd world), and an unmarked
# line gets the dry default — the 2026-07-25 lesson, when a "storyteller lean"
# default put the wrong emotion on every unmarked line and the founder said the
# voices were "giving off the wrong emotions which makes it confusing".
# Phrasing is deliberately behavioural ("flat", "clipped", "no lift at the end")
# rather than emotional ("sad"), because a description of DELIVERY is a thing a
# TTS model can act on, while a description of FEELING invites it to perform.
# EVERY entry states PACE explicitly, and that is the whole lesson here.
#
# The first version of this table described how a line FEELS and left pace to the
# model. Measured against the shipping voice on beat 12 ("…That's the whole API."):
#
#     no direction at all ............ 1.44s   (shipping take: 1.60s)
#     "dry, factual, deadpan,
#      no emotional colour" ......... 5.12s   — 3.5x LONGER
#
# VoxCPM2 reads "deadpan, no emotional colour" as solemn and weighty, so it slows
# right down. Left alone it matches our pace to within 0.16s. So the engine was
# never slow — the prose was. An earlier take on beat 2 was worse still, because
# I had literally written "speaking slowly at 3am" into the direction and then
# been surprised that it spoke slowly.
#
# House register: DEADPAN AND BRISK. The comedy is a dry incident report delivered
# at working speed (R3), not a man narrating his own tragedy. When in doubt say
# "brisk" — an unmarked line should sound like someone talking, not intoning.
DIRECTION = {
    ("tired", "weary", "sigh"):
        "exhausted and flat, low energy but still brisk, not drawn out",
    # relief is warm but SMALL — he thinks he is going to bed, not celebrating
    ("relieved", "cheerful", "almost cheerful"):
        "a small tired relief, warmer but quiet, normal speaking pace",
    # dazed: the words arrive before the understanding does
    ("dazed", "stunned", "confused", "distant"):
        "dazed and far away, even pace, not slowed",
    ("quiet",):
        "very quiet, almost under the breath, no projection, unhurried but not slow",
    ("deadpan", "flat", "dry"):
        "dry and matter-of-fact, brisk, no emotional colour",
    ("excited", "delighted", "joy", "triumphant"):
        "bright and quick, genuinely delighted",
    ("angry", "furious", "snaps"):
        "clipped and hard, fast, controlled anger",
    ("scared", "panicked", "afraid"):
        "tight and fast, breath high in the chest",
}
DEFAULT_DIRECTION = "dry, matter-of-fact, brisk, natural speaking pace"


def style_for(cue: str) -> str:
    """The style prose for a script cue like 'tired, flat' or 'quiet'.

    Multiple cues compose: '(dazed, quiet)' should be dazed AND quiet, so every
    match contributes rather than the first winning. A cue we have never seen is
    passed through verbatim instead of being dropped — the author writing a new
    direction is the author directing, and silently ignoring it would make the
    script a liar about how the line is read.
    """
    cue = (cue or "").strip().lower()
    if not cue:
        return DEFAULT_DIRECTION
    parts, seen = [], set()
    words = [w.strip() for w in re.split(r"[,;/]| and ", cue) if w.strip()]
    for word in words:
        hit = next((v for keys, v in DIRECTION.items()
                    if any(k == word or k in word for k in keys)), None)
        if hit is None:
            hit = word                       # author's own words, kept
        if hit not in seen:
            seen.add(hit)
            parts.append(hit)
    # "(tired, flat)" matched BOTH 'tired' and the deadpan family, and produced
    # "exhausted, flat, low energy, speaking slowly at 3am, completely deadpan,
    # dry, no emotional colour" — a prompt that argues with itself and buries the
    # actual note. Deadpan is the house default register, so it only needs saying
    # when nothing more specific was asked for.
    if len(parts) > 1:
        parts = [p for p in parts if p != DIRECTION[("deadpan", "flat", "dry")]] \
            or parts
    return ", ".join(parts) or DEFAULT_DIRECTION


VO = re.compile(r"^>\s*\*\*VO(?:\s*\(([^)]*)\))?\s*:?\*\*\s*(.+)$")
BEAT = re.compile(r"^\*\*(.+?)\s+—\s+(\d+):(\d\d)–(\d+):(\d\d)\*\*")


def script_beats(node_md: Path) -> list:
    """[{num, title, lines:[(cue, text)]}] from the approved T0 leaf.

    Reads node.md rather than a side file on purpose: the approved script IS the
    source of truth for what is said and how, and a second copy would drift.
    """
    beats, cur = [], None
    for raw in node_md.read_text(encoding="utf-8").splitlines():
        m = BEAT.match(raw.strip())
        if m:
            cur = {"num": len(beats) + 1, "title": m.group(1).strip(), "lines": []}
            beats.append(cur)
            continue
        m = VO.match(raw.strip())
        if m and cur is not None:
            cur["lines"].append((m.group(1) or "", m.group(2).strip()))
    return beats


def reference(node_dir: Path) -> tuple:
    """(wav, transcript) for cloning, or (None, None) for voice-design mode.

    'Ultimate cloning' in VoxCPM2's own words: pass the reference audio AND its
    exact transcript for maximum fidelity. We have the transcript for free —
    every take was synthesised FROM the script — so there is no reason to use
    the weaker path.

    Prefers refs/ (a curated identity clip) over the longest existing take. A
    take is a fallback, not a good reference: cloning from synthetic audio
    compounds its artifacts, which is one of the two reasons the F5 experiment
    sounded worse than what it was replacing.
    """
    refs = node_dir / "refs"
    if refs.is_dir():
        for wav in sorted(refs.glob("*.wav")) + sorted(refs.glob("*.mp3")):
            txt = wav.with_suffix(".txt")
            if txt.exists():
                return wav, txt.read_text(encoding="utf-8").strip()
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--beats", default="", help="1,2,3 (default: all)")
    ap.add_argument("--cfg", type=float, default=2.0)
    ap.add_argument("--steps", type=int, default=10,
                    help="inference_timesteps; the card's example uses 10")
    ap.add_argument("--out", default="", help="write here instead of clips/ (bench)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the exact prompt per line and synthesise nothing")
    a = ap.parse_args()

    nodes = REPO / "genomes" / a.genome / "nodes"
    hits = sorted(p for p in nodes.iterdir()
                  if p.is_dir() and p.name.startswith(a.node))
    if not hits:
        raise SystemExit(f"no node matching {a.node} under {nodes}")
    node_dir = hits[0]
    slug = node_dir.name

    # §6 — narrative approval precedes media. Same gate render_local uses; a
    # voice tool must not be the soft way around it.
    from render_local import approved
    ok, detail = approved(a.genome, slug)
    if not ok:
        raise SystemExit(f"{slug} is NOT founder-approved — {detail}\n"
                         "STEWARDSHIP.md §6: no synthesis from an unread script.")

    beats = script_beats(node_dir / "node.md")
    want = {int(b) for b in a.beats.split(",") if b.strip()} if a.beats else None
    todo = [b for b in beats if (want is None or b["num"] in want) and b["lines"]]
    if not todo:
        raise SystemExit(f"no VO lines to make for {slug} (beats={a.beats or 'all'})")

    ref_wav, ref_text = reference(node_dir)
    print(f"{slug}: {len(todo)} beat(s), reference="
          f"{ref_wav.name if ref_wav else 'NONE (voice design mode)'}")

    prompts = []
    for beat in todo:
        for i, (cue, text) in enumerate(beat["lines"]):
            style = style_for(cue)
            prompts.append({"beat": beat["num"], "line": i, "cue": cue,
                            "style": style, "text": text,
                            "prompt": f"({style}){text}"})

    if a.dry_run:
        for p in prompts:
            print(f"\n  beat {p['beat']:02d} line {p['line']}"
                  f"  cue={p['cue'] or '—'}")
            print(f"    → {p['prompt']}")
        print(f"\n{len(prompts)} line(s). Nothing synthesised (--dry-run).")
        return 0

    try:
        import soundfile as sf
        from voxcpm import VoxCPM
    except ImportError as e:
        raise SystemExit(
            f"{e}\n\nThe engine is not installed in this interpreter. VoxCPM2 "
            "wants CUDA >= 12 per its model card, so the 5090 is its machine, "
            "not this Mac:\n"
            "  pip install voxcpm soundfile\n"
            "Use --dry-run to review every prompt without installing anything.")

    out_dir = Path(a.out) if a.out else node_dir / "clips"
    out_dir.mkdir(parents=True, exist_ok=True)
    model = VoxCPM.from_pretrained(MODEL, load_denoiser=False)
    sr = model.tts_model.sample_rate

    for beat in todo:
        wavs, manifest = [], []
        for i, (cue, text) in enumerate(beat["lines"]):
            style = style_for(cue)
            kw = {"text": f"({style}){text}", "cfg_value": a.cfg,
                  "inference_timesteps": a.steps}
            if ref_wav:
                kw["reference_wav_path"] = str(ref_wav)
                # DO NOT also pass prompt_wav_path/prompt_text here. The model
                # card documents "ultimate cloning" (the same clip in both) for
                # maximum voice similarity, and separately documents style
                # control via a leading "(...)" — but the two DO NOT COMPOSE.
                # With both set, the parenthetical stops being parsed as style
                # and is SPOKEN ALOUD. Measured on "…That's the whole API.":
                #
                #   plain    + ultimate ..... 1.44s
                #   directed + ultimate ..... 5.12s   <- reciting 51 chars
                #   directed + ref-only ..... 1.44s   <- absorbed correctly
                #
                # That one line cost an evening: it looked like the engine was
                # 2.5-4.7x too slow for our beats, then like our direction prose
                # was at fault. Neither. Combining two documented features that
                # were never documented together.
            wav = model.generate(**kw)
            part = out_dir / f"{beat['num']:02d}-vo-{i}.wav"
            sf.write(str(part), wav, sr)
            dur = round(len(wav) / float(sr), 3)
            wavs.append(part)
            manifest.append({"text": text, "cue": cue, "style": style,
                             "seconds": dur})
            print(f"  beat {beat['num']:02d} line {i}: {dur:.2f}s  ({style})")

        mp3 = out_dir / f"{beat['num']:02d}-vo.mp3"
        if len(wavs) == 1:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wavs[0]),
                            "-c:a", "libmp3lame", "-q:a", "4", str(mp3)], check=True)
        else:
            lst = out_dir / f".concat-{beat['num']:02d}.txt"
            lst.write_text("".join(f"file '{w.name}'\n" for w in wavs))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                            "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                            "-q:a", "4", str(mp3)], check=True)
            lst.unlink()
        for w in wavs:
            w.unlink()

        # provenance is not optional (§7.2) — and an unprovenanced VO manifest is
        # exactly what licence_gate flagged in node 006b
        (out_dir / f"{beat['num']:02d}-vo.json").write_text(json.dumps(
            {"engine": ENGINE, "cast": "voices.yaml",
             "directed": "synth_voxcpm v1 (style prose from the script's own cues)",
             "reference": ref_wav.name if ref_wav else None,
             "cfg_value": a.cfg, "inference_timesteps": a.steps,
             "lines": manifest,
             "total_s": round(sum(m["seconds"] for m in manifest), 3)}, indent=1))
    print("VOXCPM_DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
