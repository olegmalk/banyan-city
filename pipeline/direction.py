#!/usr/bin/env python3
"""Which stage directions reach the viewer, and for how long.

Pure text rules, no audio dependencies — `synth_vo.py` needs numpy and
soundfile, and these need to be testable in CI without them. Shared by
synth_vo (which allocates the silent hold) and the caption layer.
"""

import re

ACTION_MAX_WORDS = 14   # stage directions this short become on-screen beats
ACTION_MIN_HOLD = 1.4   # seconds a displayed gesture owns the track
ACTION_MAX_HOLD = 2.2   # past this a silent hold reads as a stalled video

# The tree cannot speak aloud, so its ANSWERS are stage directions ("One leaf
# tilts."). Cycle 006 put those on screen because they never reached the viewer
# otherwise. That was right, but it was implemented as a blocklist of camera
# words, which let nearly every short action through: "Close on the sapling's
# leaf…" (the list had `close-up`, not `close on`), "The sun arcs overhead three
# times…", "GUARD 2 turns over a clipboard…". Each one then owned 3.6-4.5s of
# SILENT track before the line, displayed as a caption nobody says — which is
# both founder complaints in one mechanism: "no sound for like 3 seconds
# straight staring at the random ai animation", and "this is literally just the
# script being put as dialogue".
#
# So it is an allowlist now: an action reaches the screen only when it is the
# tree's own gesture — its leaves/branches/crown doing something. Everything
# else is production language or another character's business, and it belongs in
# the shot prompt, not on the viewer's screen.
TREE_PART = r"(leaf|leaves|branch|branches|crown|canopy|bough|frond)"
GESTURE = (r"(tilts?|tilting|dips?|nods?|curls?|shivers?|trembles?|lifts?|rises?|"
           r"drops?|holds?|stills?|straightens?|turns?|folds?|unfurls?|"
           r"twitch(?:es)?|angles?|leans?)")
CAMERA_WORDS = (r"\b(camera|frame|framing|shot|close-?up|close on|wide|extreme|macro|"
                r"montage|cut to|we see|insert|pov|angle on|pull (?:in|out)|"
                r"push (?:in|out)|pan|zoom|underground|cross-?section)\b")
# Mentioning a leaf is not the same as the leaf doing the talking. "He holds the
# fig up beside the bare branch it fell from" is the goblin's business and "The
# sun arcs overhead three times as one new leaf unfurls" is a timelapse; both
# name a tree part and neither is the tree answering. So the SUBJECT has to be
# the tree: a direction opening on a character or on the weather is out.
NOT_THE_TREE = (r"^(he|she|they|his|her|the (?:goblin|scavenger|farmer|magistrate|"
                r"assessor|pilgrim|stranger|man|guard\w*)|guard \d|the (?:sun|moon|"
                r"wind|sky|grass|light|water|field)|dawn|wind|moonlight|sunrise)\b")


def displayable_action(action_text: str) -> str | None:
    """The tree's own gesture, or None.

    Only the protagonist's leaf-language earns screen time and silence — that
    is the show's substitute for it having a mouth. Camera direction, scenery
    and other characters' business stay off screen: they are already described
    to the renderer in `shots.md`, and putting them in front of the viewer
    reads as the script leaking into the episode."""
    t = action_text.strip()
    if not t or is_beat_pause(t):
        return None
    first = re.split(r"(?<=[.!?…])\s+", t)[0]
    if re.search(CAMERA_WORDS, first, re.I):
        return None
    if len(first.split()) > ACTION_MAX_WORDS:
        return None
    if re.match(NOT_THE_TREE, first.strip(), re.I):
        return None  # someone else's business, or the weather
    if not re.search(TREE_PART, first, re.I):
        return None  # not the tree gesturing — scenery or someone else acting
    if not re.search(GESTURE, first, re.I):
        return None  # the tree is present but not answering
    return first


def action_hold(text: str) -> float:
    """Seconds a displayed gesture owns.

    Capped: the gesture is a beat of silence the viewer READS, and past a
    couple of seconds a silent hold stops reading as a pause and starts reading
    as the video having stalled (founder, 2026-07-23)."""
    return min(ACTION_MAX_HOLD, max(ACTION_MIN_HOLD, 0.28 * len(text.split()) + 0.6))


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
                # A beat with nothing to say must not keep the take it had
                # BEFORE the script changed. Skipping quietly here is how 007a
                # ended up playing its closing line ("…Who's that?") at beat 5:
                # the molt renumbered the beats, this beat lost its dialogue,
                # and the stale 05-vo.mp3 sat there for render_t3 to find.
                # Archived, not deleted (R6).
                if (clips_dir / f"{beat_num:02d}-vo.mp3").exists():
                    print(f"    {slug} b{beat_num:02d} has no spoken line — "
                          "archiving the stale take")
                    archive(clips_dir, beat_num)
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

        # takes numbered past the last beat are leftovers from a shorter cut of
        # the script; render_t3 would never reach them, but they make the clips
        # dir lie about what the episode contains
        for stray in sorted(clips_dir.glob("*-vo.mp3")):
            try:
                n = int(stray.name[:2])
            except ValueError:
                continue
            if n > len(frames):
                print(f"    {slug} b{n:02d} is past the last beat "
                      f"({len(frames)}) — archiving")
                archive(clips_dir, n)
    print("VO_DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
GESTURE = (r"(tilts?|tilting|dips?|nods?|curls?|shivers?|trembles?|lifts?|rises?|"
           r"drops?|holds?|stills?|straightens?|turns?|folds?|unfurls?|"
           r"twitch(?:es)?|angles?|leans?)")
CAMERA_WORDS = (r"\b(camera|frame|framing|shot|close-?up|close on|wide|extreme|macro|"
                r"montage|cut to|we see|insert|pov|angle on|pull (?:in|out)|"
                r"push (?:in|out)|pan|zoom|underground|cross-?section)\b")
NOT_THE_TREE = (r"^(he|she|they|his|her|the (?:goblin|scavenger|farmer|magistrate|"
                r"assessor|pilgrim|stranger|man|guard\w*)|guard \d|the (?:sun|moon|"
                r"wind|sky|grass|light|water|field)|dawn|wind|moonlight|sunrise)\b")


def is_beat_pause(action_text: str) -> bool:
    """A standalone 'Beat.' / 'A beat.' stage direction is a scripted
    breath (cycle-001 defect 14: the render dropped it entirely)."""
    return bool(action_text) and action_text.strip().rstrip(".").lower() in ("beat", "a beat")


def displayable_action(action_text: str) -> str | None:
    """The tree's own gesture, or None.

    Only the protagonist's leaf-language earns screen time and silence — that
    is the show's substitute for it having a mouth. Camera direction, scenery
    and other characters' business stay off screen: they are already described
    to the renderer in `shots.md`, and putting them in front of the viewer
    reads as the script leaking into the episode."""
    t = action_text.strip()
    if not t or is_beat_pause(t):
        return None
    first = re.split(r"(?<=[.!?…])\s+", t)[0]
    if re.search(CAMERA_WORDS, first, re.I):
        return None
    if len(first.split()) > ACTION_MAX_WORDS:
        return None
    if re.match(NOT_THE_TREE, first.strip(), re.I):
        return None  # someone else's business, or the weather
    if not re.search(TREE_PART, first, re.I):
        return None  # not the tree gesturing — scenery or someone else acting
    if not re.search(GESTURE, first, re.I):
        return None  # the tree is present but not answering
    return first


def action_hold(text: str) -> float:
    """Seconds a displayed gesture owns.

    Capped: the gesture is a beat of silence the viewer READS, and past a
    couple of seconds a silent hold stops reading as a pause and starts reading
    as the video having stalled (founder, 2026-07-23)."""
    return min(ACTION_MAX_HOLD, max(ACTION_MIN_HOLD, 0.28 * len(text.split()) + 0.6))
