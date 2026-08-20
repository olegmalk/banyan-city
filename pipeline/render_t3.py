#!/usr/bin/env python3
"""T3 renderer — full-video leaves assembled from generated clips, PRD §7.4.

The generation platform (Kling, Veo, Seedance, …) supplies raw per-beat
footage; everything the platform is bad at stays deterministic post:

  beats      parsed from node.md (same beat structure as the T1 storyboard);
             each beat's target duration comes from its `— 0:00–0:12` slug
             timing, falling back to a reading-speed estimate.
  clips      --clips <dir> holds one clip per beat, named by beat number
             (`01-*.mp4`, `02-*.mp4`, …). Each clip is fitted to 9:16
             (scale + center-crop), trimmed or last-frame-padded to the
             beat's duration. A beat with no clip renders as a $0 slate —
             the episode always assembles end-to-end, footage lands later.
  overlays   the script's terminal code-fences are burned in as green
             monospace panels; VO lines appear as timed bottom captions,
             chunked to short phrase units (loop cycle 001). The episode
             title is a compact overlay on the opening footage — never a
             full-screen leading card. Text is rasterized by Pillow and
             composited with ffmpeg's core `overlay` filter — no
             freetype/drawtext build needed.
  voice      per-beat audio, muxed in sync: a supplied track (NN-*.mp3 in the
             clips dir) wins, else optional --tts openai narration (render_t2's
             engine). Each beat's audio is padded/trimmed to its slot so VO
             stays aligned; a whisper wind bed runs under the whole episode
             and the final track is loudness-normalized for short-form
             platforms. No audio anywhere → silent animatic.
  assembly   per-beat encodes concatenated losslessly, then a single aligned
             audio track muxed on, into <node>-t3-<sfx>.mp4.

Provenance (§7.2): clip-side `<clip>.meta.yaml` files (platform, model,
prompt, cost) are aggregated into the leaf yaml. Without --out the leaf is
published into the genome and registered in lineage.yaml; with --out it is a
bench render (pipeline development, platform trials) and touches nothing.

Deps: pyyaml, pillow, ffmpeg on PATH (any build with libx264).

Usage:
    python3 pipeline/render_t3.py <genome> <node-id> --clips <dir> [--tts openai]
    python3 pipeline/render_t3.py sapling 001 --clips /tmp/trial --out /tmp/bench.mp4
"""

import argparse
import os
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import licence_gate as lg  # noqa: E402 — the tolerant sidecar reader
from captions import (CAPTION_MAX_WORDS, caption_chunks, chunk_spans,  # noqa: E402,F401 — shared with synth_vo
                      split_caption_display)
from render_t1 import extract_script, parse_frames, strip_inline_md  # noqa: E402
from render_t2 import ffmpeg_exe  # noqa: E402 — shared resolver: bundled imageio-ffmpeg, else PATH

REPO = Path(__file__).resolve().parent.parent
FFMPEG = ffmpeg_exe()
WIDTH, HEIGHT = 720, 1280
FPS = 24
MIN_SEC, MAX_SEC = 3.0, 12.0
READ_CPS = 15.0
GREEN, INK, BG = (111, 206, 138, 255), (230, 239, 232, 255), (10, 15, 11, 255)
PANEL_BG, CAPTION_BG = (10, 15, 11, 200), (0, 0, 0, 200)
CAPTION_SIZE = 44
# platform safe area (cycle-001 defect, verified): TikTok/Reels chrome covers
# the bottom ~17-20% and a right-side action rail — captions anchored at
# H-h-160 lost their last line under it. Keep blocks above the chrome and
# narrower than the rail line.
# +2, and the reason is an off-by-one worth writing down. A block anchored at
# H-h-M has its LOWEST DRAWN PIXEL at H-M-1, while the band qa_episode measures
# starts at int(H*(1-0.22)) = 998. At M = int(1280*0.22) = 281 the caption's last
# row lands on y999 — two rows inside the very band this constant exists to
# clear. The margin was equal to the band when it needed to exceed it, which is
# the same class of mistake as the cycle-001 defect it was written for.
CAPTION_MARGIN = int(HEIGHT * 0.22) + 2
CAPTION_MAX_W = WIDTH - 160
# Caps the OPT-IN palindrome branch only (`wants_pingpong`) — reverse buffers
# every raw frame, so a long source would eat memory. Since 2026-08-19 the
# default fill for footage is a last-frame hold, which streams and needs no cap.
PINGPONG_MAX_S = 16.0

# speaker attribution (cycle 006): the tree's inner voice is tinted its own
# green and carries no label; every other speaker gets a colored name tag.
VO_INK = (196, 232, 205, 255)            # pale leaf-green — the tree thinking
ACTION_INK = (147, 196, 160, 255)        # stage-direction captions
SPEAKER_COLORS = {
    "SCAVENGER": (240, 200, 100, 255),   # warm amber
    "FARMER": (222, 171, 128, 255),      # clay
    "ASSESSOR": (168, 190, 230, 255),    # ledger blue
    "MAGISTRATE": (216, 160, 230, 255),  # seal violet
    "GUARD 1": (170, 196, 210, 255),
    "GUARD 2": (150, 176, 190, 255),
}
FALLBACK_COLORS = [(235, 180, 180, 255), (180, 225, 235, 255), (225, 225, 160, 255)]


def speaker_style(who: str) -> tuple:
    """(label, label_color, text_color) for a caption chunk.

    The protagonist is tagged like everyone else. Leaving his inner voice
    untagged (cycle 006, first pass) backfired: in caption grammar an
    untagged line means "same speaker, continuing", so a cold viewer
    assigned every one of his thoughts — including the closing punchline —
    to whoever spoke last (verified, cold-viewer re-test 2026-07-25).
    THE TREE also tells a first-time viewer what the protagonist IS."""
    if not who or who == "VO":
        return "THE TREE:", VO_INK, VO_INK
    color = SPEAKER_COLORS.get(who) or FALLBACK_COLORS[hash(who) % len(FALLBACK_COLORS)]
    return f"{who}:", color, INK

MONO_FONTS = [
    "/System/Library/Fonts/Menlo.ttc",                       # macOS
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",   # debian/ubuntu CI
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
]
BOLD_FONTS = [
    ("/System/Library/Fonts/Menlo.ttc", None),  # collection — scan for the Bold face
    ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 0),
    ("/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf", 0),
]


def mono_font(size: int) -> ImageFont.FreeTypeFont:
    for f in MONO_FONTS:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    raise SystemExit("no monospace font found — extend MONO_FONTS")


def mono_bold(size: int) -> ImageFont.FreeTypeFont:
    """Bold face for captions — regular-weight 28px measured ~2/3 of
    platform-native caption size and smears after re-encode (loop cycle 001,
    defect 9). Menlo.ttc packs its faces in one collection, so the Bold
    index is found by name; falls back to regular rather than failing."""
    for path, idx in BOLD_FONTS:
        if not Path(path).exists():
            continue
        if idx is not None:
            return ImageFont.truetype(path, size, index=idx)
        for i in range(6):
            try:
                f = ImageFont.truetype(path, size, index=i)
            except OSError:
                break
            if f.getname()[1] == "Bold":
                return f
    return mono_font(size)


def beat_duration(slug: str, items: list) -> float:
    """`COLD OPEN — 0:00–0:12` → 12.0; otherwise estimate from text."""
    m = re.search(r"(\d+):(\d+)\s*[–—-]\s*(\d+):(\d+)", slug)
    if m:
        a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
        if b > a:
            return float(b - a)
    text = " ".join(str(p) for item in items for p in item[1:])
    return min(MAX_SEC, max(MIN_SEC, len(text) / READ_CPS))


def find_clips(clips_dir: Path, num: int) -> list:
    """All footage for a beat, primary take first (NN-slug.mp4, then
    NN-slug-alt1.mp4, …). Multiple clips are SEQUENCED to fill the beat before
    any looping starts — a beat with 3 distinct clips loops a 30s sequence,
    not a 5s shot. Sorted on the stem, not the filename: '-' < '.' would put
    NN-slug-alt1.mp4 ahead of the primary NN-slug.mp4 otherwise."""
    if not clips_dir:
        return []
    return (sorted(clips_dir.glob(f"{num:02d}-*.mp4"), key=lambda p: p.stem)
            or sorted(clips_dir.glob(f"{num:02d}.mp4")))


def find_clip(clips_dir: Path, num: int) -> Path | None:
    hits = find_clips(clips_dir, num)
    return hits[0] if hits else None


def slug_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def footage_matches_beat(clip: Path, beat_slug: str) -> bool:
    """Is this clip actually the shot for THIS beat, or just the same number?

    Footage is found by beat NUMBER, and a rewrite renumbers beats. After the
    cycle-007 molt, 31 of the season's 35 clips landed on a beat they were never
    made for — `05-realization-hook.mp4`, the footage for episode 1's ENDING,
    would have played over new beat 5, the man dying at his desk. The clip's own
    filename records the beat it was made for, so compare them and say so.

    This is the same defect class as the orphaned voice takes (cycle 008): the
    molt renumbered beats and stale media stayed behind at its old index. That
    was caught for audio and not for video, which is why this check exists."""
    made_for = slug_key(clip.stem[3:].split("-alt")[0])
    now = slug_key(beat_slug.split("—")[0])
    if not made_for or not now:
        return True
    return made_for.startswith(now[:10]) or now.startswith(made_for[:10])


def check_clips_dir(clips_dir: Path | None) -> None:
    """An explicit --clips that doesn't exist or holds no per-beat footage is
    almost certainly a typo'd path: rendering on would silently produce an
    all-slate episode and could overwrite a published leaf. Abort loudly —
    omitting --clips keeps the legitimate all-slate path."""
    if clips_dir is None:
        return
    if not clips_dir.is_dir():
        raise SystemExit(f"--clips {clips_dir}: not a directory")
    if not any(clips_dir.glob("[0-9][0-9]*.mp4")):
        raise SystemExit(f"--clips {clips_dir}: no per-beat clips (NN-*.mp4) found — "
                         "omit --clips to render an all-slate episode")


AUDIO_EXT = ("mp3", "wav", "m4a", "aac", "ogg")
AUDIO_SR = 44100
# short-form platforms normalize to about -14 LUFS; sitting under it just makes
# the episode quieter than everything around it in the feed.
# -14 LUFS is the platform reference, and chasing it was a mistake for THIS
# material: an episode with scored silences only reaches -14 integrated if the
# loud moments are shoved into the limiter, so a body hitting the floor ended up
# no louder than a spoken line. A cold-read listener heard the master "pinned at
# about -1.8 dBFS almost continuously" — that is a squashed mix, and it is why
# the thump never landed no matter where it was placed. Master quieter and let
# the platforms turn it up: they normalise upward without re-limiting, so the
# transients survive.
LOUDNESS_TARGET = -17.0
LIMIT_MASTER = 0.80   # -1.94 dBFS, ceiling during loudnorm's own 192k pass.
                      # 0.86 was not enough headroom once the loudness loop
                      # started winning: episode 1 reached -14.2 LUFS after three
                      # passes and true peak came out at +0.1 dBTP, because AAC
                      # overshoots the limiter by roughly a decibel.
# loudnorm's TP target is deliberately looser than the old -1.5: the limiter
# above holds the real ceiling, and a tight TP target makes loudnorm clamp its
# own gain and undershoot the loudness target instead.
TP_TARGET = -1.0
LOUDNESS_TOL = 0.3    # qa_episode's window around the target



def find_audio(clips_dir: Path, num: int) -> Path | None:
    """Pre-supplied per-beat VO/audio (NN-*.mp3 …), analogous to find_clip."""
    if not clips_dir:
        return None
    for ext in AUDIO_EXT:
        hits = sorted(clips_dir.glob(f"{num:02d}-*.{ext}")) or sorted(clips_dir.glob(f"{num:02d}.{ext}"))
        if hits:
            return hits[0]
    return None


def media_duration(f: Path) -> float | None:
    """Container duration via ffmpeg banner (no ffprobe dependency)."""
    r = subprocess.run([FFMPEG, "-i", str(f)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else None


def video_duration(f: Path) -> float | None:
    """Video-stream-only duration: exact packet count from a decode-free remux
    to the null muxer, over the stream's frame rate. The container duration
    includes the audio track, which generators pad ~20-30ms past the video;
    summing THAT overshoots the video-only sequence render_beat builds and
    loops a 1-frame flash of the first clip onto the beat's end. (The remux
    progress `time=` is DTS-based and lags B-frames — count frames instead.)
    Falls back to container duration."""
    r = subprocess.run([FFMPEG, "-i", str(f), "-map", "0:v:0", "-c", "copy",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    fps = re.search(r"(\d+(?:\.\d+)?) fps[,\s]", r.stderr)  # first hit = input banner
    frames = re.findall(r"frame=\s*(\d+)", r.stderr)        # last hit = final count
    if r.returncode == 0 and fps and frames and float(fps[1]) > 0:
        return int(frames[-1]) / float(fps[1])
    return media_duration(f)


VOICELESS_TAIL_MAX = float(os.environ.get("T3_TAIL_MAX", 2.0))
# footage may beat out this long after the last word. Env-tunable because a
# "tight cut" is a pacing experiment, not a new pipeline: cold readers found
# 001 holds static plates for seconds after the line ends (2026-07-30).


def fit_duration(script_s: float, cdur: float, vdur: float) -> float:
    """A beat slot sized to its material, VOICE-led. Playing the full clip
    regardless of VO length left multi-second dead-air tails (10s clip over
    4.6s of dialogue — founder wince, loop cycle 004): with voice present,
    footage may run at most VOICELESS_TAIL_MAX past it (visual beat-out),
    and still loops longer when the VO outruns the clip. Voice-less footage
    beats keep their full clip; slate beats (cdur 0) keep the script's paper
    timing, stretching only when the VO runs longer; dialogue is never
    hard-trimmed mid-sentence."""
    if cdur:
        if not vdur:
            # A SILENT BEAT STILL HAS A SCRIPTED LENGTH. This used to return the
            # full footage duration, so a beat with no dialogue played however
            # much material happened to exist. Beat 4 of 001 — the fall, no VO,
            # two 5s shots — therefore ran 10.08s against a script that gives it
            # 0:15–0:20. Those five extra silent seconds WERE the "very
            # anticlimatic" death: nothing said, nothing happening, at the moment
            # the story turns. Four rounds of sound work chased it before anyone
            # measured the beat length.
            #
            # The script is the edit. Footage shorter than its slot still keeps
            # its own length (nothing is stretched); footage longer is cut to the
            # slot the author wrote. Approved by the founder on the A/B
            # (2026-08-02: "yeah B4TRIM is better").
            return round(min(cdur, script_s), 2) if script_s else round(cdur, 2)
        return round(max(min(cdur, vdur + VOICELESS_TAIL_MAX), vdur + 0.4), 2)
    if vdur:
        return round(max(script_s, vdur + 0.4), 2)
    return script_s


def previously_line(genome_dir: Path, node: dict, all_nodes: list) -> str | None:
    """One-sentence recap from the PARENT's '## State change' — rough renders
    lean on captions, so a cold viewer gets the story state in one line
    (comprehension wince, edl 2026-07-22). Root episodes have no recap."""
    pid = node.get("parent")
    if not pid:
        return None
    parent = next((n for n in all_nodes if n["id"] == pid), None)
    if not parent:
        return None
    md = (genome_dir / "nodes" / parent["slug"] / "node.md").read_text()
    m = re.search(r"^## State change[^\n]*\n+(.+?)(?:\n\n|\n#)", md, re.M | re.S)
    if not m:
        return None
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(1))
    text = re.sub(r"[*_`>#]", "", text).replace("\n", " ").strip()
    first = re.split(r"(?<=[.!?])\s", text)[0]
    # truncate on a WORD boundary: a mid-word cut ("becomes the fi…") on the
    # one line meant to orient a new viewer reads as a rendering fault
    # (cold-viewer re-test, 2026-07-25). The overlay wraps, so allow more.
    if len(first) <= 150:
        return first
    cut = first[:150].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:") + "…"


def vo_manifest(clips_dir: Path, num: int) -> dict | None:
    """NN-vo.json (written by the VO synth): measured per-line timings that
    drive exact caption sync; without it captions fall back to even slicing."""
    if not clips_dir:
        return None
    f = clips_dir / f"{num:02d}-vo.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise SystemExit(f"VO manifest {f} is unreadable: {e}")
    if not isinstance(data, dict):
        raise SystemExit(f"VO manifest {f} must be a JSON object, got {type(data).__name__}")
    return data


def load_sound_design(clips_dir: Path | None) -> dict:
    """Optional per-node `clips/sound.yaml`: synthesized cues (pipeline/sfx.py)
    placed on the timeline, plus a wind-bed duck window. The scripts write
    their own sound design; this file is where it finally gets built."""
    f = (clips_dir / "sound.yaml") if clips_dir else None
    if not f or not f.exists():
        return {}
    try:
        return yaml.safe_load(f.read_text()) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"sound.yaml is unreadable: {e}")


def load_slate_notes(clips_dir: Path | None) -> dict:
    """Optional per-cut `slates.yaml`: `{beat_number: "one honest line"}`.

    Resolved against --clips like every other per-cut input, so a cut carries
    its own slate wording beside the footage that wording is about. Missing
    file, unparseable file or a beat with no entry all fall back to the default
    "[ footage pending ]" — a slate never fails an assembly.
    """
    f = (clips_dir / "slates.yaml") if clips_dir else None
    if not f or not f.exists():
        return {}
    try:
        doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"slates.yaml is unreadable: {e}")
    if not isinstance(doc, dict):
        raise SystemExit("slates.yaml must be a mapping of beat number -> line")
    out = {}
    for k, v in doc.items():
        try:
            out[int(k)] = " ".join(str(v).split())
        except (TypeError, ValueError):
            continue
    return out


def loudnorm_measure(track: Path) -> dict | None:
    """First pass of two-pass loudnorm: measured levels for a linear-gain
    second pass (dynamic single-pass loudnorm pumps on dialogue)."""
    r = subprocess.run([FFMPEG, "-i", str(track), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    keys = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
    if any(k not in data or "inf" in str(data[k]) for k in keys):
        return None  # unmeasurable (e.g. digital silence) — caller falls back
    return data


def integrated_lufs(track: Path) -> float | None:
    """Measured integrated loudness of a finished track, via ebur128.

    loudnorm cannot be trusted to land on its target: in linear mode it clamps
    its own gain against the true-peak ceiling and then reports a
    `target_offset` it never applied. On 001 that left the master at -15.4 LUFS
    against a -14 target (caught by qa_episode 2026-07-25). So the master is
    measured after the fact and the shortfall corrected as a plain gain."""
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(track),
                        "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    hits = re.findall(r"I:\s*(-?[\d.]+)\s*LUFS", r.stderr)
    if not hits:
        return None
    try:
        return float(hits[-1])
    except ValueError:
        return None


def wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list:
    out = []
    for raw in text.split("\n"):
        line = ""
        for word in raw.split(" "):
            cand = f"{line} {word}".strip()
            if font.getbbox(cand)[2] <= max_w or not line:
                line = cand
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def text_png(text: str, path: Path, size: int, fg: tuple, bg: tuple,
             max_w: int = WIDTH - 100, pad: int = 18, bold: bool = False,
             label: str = "", label_color: tuple = None) -> Path:
    """Rasterize a text block into a tight RGBA panel. An optional `label`
    ("SCAVENGER:") renders inline before the text in `label_color` — speaker
    attribution, the unanimous #1 fix from the cycle-006 cold-viewer tests
    (three viewers, three episodes: every comprehension break traced to not
    knowing who was talking)."""
    font = mono_bold(size) if bold else mono_font(size)
    full = f"{label} {text}".strip() if label else text
    lines = wrap(full, font, max_w - 2 * pad)
    lh = size + 8
    w = min(max_w, max(font.getbbox(l)[2] for l in lines) + 2 * pad)
    img = Image.new("RGBA", (w, lh * len(lines) + 2 * pad), bg)
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        if i == 0 and label and l.startswith(label):
            d.text((pad, pad + i * lh), label, font=font,
                   fill=label_color or fg)
            x_after = pad + font.getbbox(label + " ")[2]
            d.text((x_after, pad + i * lh), l[len(label):].lstrip(), font=font, fill=fg)
        else:
            d.text((pad, pad + i * lh), l, font=font, fill=fg)
    img.save(path)
    return path


def slate_png(slug: str, path: Path, note: str | None = None) -> Path:
    """A beat with no footage in the cut: its title, and ONE honest line saying
    why there is no picture.

    The default line is "[ footage pending ]" and for years it was the ONLY
    line, which understated every slate that is not waiting on a render.
    picks-0820.yaml named the defect: beat 16's footage exists and is barred by
    a founder ruling, and beat 09's two clips bar themselves in their own
    headers — neither is "pending". A cut can now hand its own wording in via
    `slates.yaml` in the --clips directory (see `load_slate_notes`), so the card
    says what is actually true of that beat instead of a generic apology.
    Wrapped, so a real sentence fits.
    """
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)
    font = mono_font(30)
    lines = wrap(slug.upper(), font, WIDTH - 120)
    lh = 42
    small = mono_font(18)
    nlines = wrap(note or "[ footage pending ]", small, WIDTH - 160)
    slh = 26
    block = lh * len(lines) + 30 + slh * len(nlines)
    y = HEIGHT // 2 - block // 2
    for i, l in enumerate(lines):
        w = font.getbbox(l)[2]
        d.text(((WIDTH - w) // 2, y + i * lh), l, font=font, fill=GREEN)
    ny = y + lh * len(lines) + 30
    for i, l in enumerate(nlines):
        d.text(((WIDTH - small.getbbox(l)[2]) // 2, ny + i * slh),
               l, font=small, fill=(147, 166, 152, 255))
    img.save(path)
    return path


def _centered(d, cx, y, text, font, fill):
    d.text((cx - font.getbbox(text)[2] / 2, y), text, font=font, fill=fill)


def card_png(lines: list, path: Path) -> Path:
    """A full-frame title/end card: centered green monospace on near-black.
    lines is a list of (text, size, color) tuples, stacked and vertically centered."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)
    rendered = [(t, mono_font(s), c) for t, s, c in lines]
    gap = 20
    total = sum(f.getbbox(t)[3] + gap for t, f, _ in rendered) - gap
    y = (HEIGHT - total) // 2
    for t, f, c in rendered:
        _centered(d, WIDTH // 2, y, t, f, c)
        y += f.getbbox(t)[3] + gap
    img.save(path)
    return path


def title_overlay_png(node: dict, prev: str | None, path: Path) -> Path:
    """Series wordmark + episode title (+ recap) as a compact centered panel,
    composited over the opening seconds of live footage. The old full-screen
    leading card spent the entire scroll-decision window on 2.5s of silent
    black (loop cycle 001, defects 1-3); footage and VO now start at t=0."""
    specs = [("SAPLING", 24, (147, 166, 152, 255)),
             (f"{node['id']} — {node['title']}", 34, GREEN),
             ("a story that branches", 18, (147, 166, 152, 255))]
    if prev:
        for seg in wrap(f"Previously: {prev}", mono_font(20), WIDTH - 200):
            specs.append((seg, 20, INK))
    rendered = [(t, mono_font(s), c) for t, s, c in specs]
    pad, gap = 22, 12
    w = min(WIDTH - 80, max(f.getbbox(t)[2] for t, f, _ in rendered) + 2 * pad)
    h = sum(f.getbbox(t)[3] + gap for t, f, _ in rendered) - gap + 2 * pad
    img = Image.new("RGBA", (w, h), PANEL_BG)
    d = ImageDraw.Draw(img)
    y = pad
    for t, f, c in rendered:
        _centered(d, w // 2, y, t, f, c)
        y += f.getbbox(t)[3] + gap
    img.save(path)
    return path


def card_clip(pngs_and_durs: list, workdir: Path, tag: str) -> Path:
    """Encode one or more still cards into a short silent mp4 segment."""
    parts = []
    for i, (png, dur) in enumerate(pngs_and_durs):
        out = workdir / f"card-{tag}-{i}.mp4"
        subprocess.run(
            [FFMPEG, "-y", "-loop", "1", "-t", str(dur), "-i", str(png),
             "-vf", f"fps={FPS},format=yuv420p", "-r", str(FPS), "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-movflags", "+faststart", str(out)],
            check=True, capture_output=True)
        parts.append(out)
    return parts


def held_still(clips: list) -> bool:
    """Is this beat's footage a held still rather than rendered video?

    Same marker `check_invention` reads — the `model: none` line hold_still
    writes into its own sidecar. It matters here because a held still is a
    COMPUTED camera move, not footage: reversing it runs the push backwards,
    which is the ping-pong the founder ruled out on 2026-08-07 ("for all of the
    images that have no animation and only zooming, first of all, do not do ping
    pong"). It also has no correct frame rate, so unlike real footage it can be
    stretched to its slot instead."""
    if not clips:
        return False
    for c in clips:
        # the INVERSE of the clip_provenance bug, and worth widening for the
        # same reason: this located `<full name>.mp4.meta.yaml` only, which is
        # what hold_still writes today, so a held clip filed under the stem
        # shape read as footage and got ping-ponged. Since 2026-08-19 that
        # misread costs less — footage holds rather than reverses — but it still
        # costs the stretch, and a computed push has no true frame rate to loop.
        meta = lg.sidecar_for(c, lg.META_EXT)
        if not meta:
            return False
        text = meta.read_text(encoding="utf-8", errors="replace")
        if "model: none" not in text:
            return False
        # `model: none` MEANS "no sampler ran", AND THAT IS NOT THE SAME THING
        # AS "no video". A composite is assembled from clips that were rendered:
        # pipeline/fig_composite.py runs no sampler, writes `model: none`
        # honestly, and produces 121 real frames at a real 24 fps. Read on the
        # substring alone, beat 01's chroma composite was classified a held
        # still on 2026-08-20 and STRETCHED 5.04s to 9.47s — the cold open
        # played at 0.53x speed, the fig growing in slow motion, and the tool
        # printed "held still ... stretched" while doing it.
        #
        # The discriminator is a DECLARED FRAME RATE. hold_still writes
        # `seconds:` and deliberately no `fps:`, because a computed push-in has
        # no true frame rate — that absence is the property the stretch relies
        # on. Anything that states its own fps is footage and gets footage's
        # treatment: play once, hold the last frame.
        if re.search(r"^\s*fps\s*:\s*[0-9]", text, re.M):
            return False
    return True


def wants_pingpong(clips: list) -> bool:
    """Does this beat's OWN record ask to be played forwards and then backwards?

    `loop_fill: pingpong` in every one of the beat's clip sidecars — the same
    tolerant lookup `held_still` uses, and ALL of them for the same reason: the
    palindrome is applied to the concatenated sequence, so one clip cannot opt
    the others in.

    IT HAS NO CALLERS IN THIS TREE, on purpose. Nothing in `genomes/`, no
    shots.md, no leaf and no sidecar under `review/` or `clips/` carries the key
    (grepped, 2026-08-19): the palindrome went from the DEFAULT fill for footage
    to an opt-in nobody has taken. It stays reachable because loop cycle 005 was
    right about the one shape it suits — a genuinely cyclic move (a sway, a
    flicker, leaves in wind) where forwards-and-back IS the motion and a plain
    loop restart is the only visible seam. It is wrong for footage that performs
    an ACTION once, which is what every take in this show is."""
    if not clips:
        return False
    for c in clips:
        if str(clip_provenance(c).get("loop_fill") or "").strip() != "pingpong":
            return False
    return True


def render_beat(beat: dict, num: int, dur: float, clips: list, workdir: Path,
                manifest: dict | None = None, extra_layers: list | None = None,
                tag_speakers: bool = True, slate_note: str | None = None) -> Path:
    """Encode one beat: fitted footage (or slate) + overlays + captions.
    Multiple clips per beat are sequenced (concat) to fill the slot, and a slot
    the sequence cannot fill ends on a HOLD of its last frame — the action
    completes, then lands. (It used to loop a palindrome; see the fill comment
    below and the 0819c audit for why a freeze beats a reversal.) Captions
    follow the VO manifest's measured line timings when one exists, chunked
    to short phrase units within each line's window. extra_layers appends
    caller-supplied (png, x, y, enable) overlays — e.g. the episode title
    panel on beat 1."""
    inputs, chains = [], []
    clip = clips[0] if clips else None
    if len(clips) > 1:
        seq_list = workdir / f"seq-{num:02d}.txt"
        seq_list.write_text("\n".join(f"file '{c.resolve()}'" for c in clips))
        seq = workdir / f"seq-{num:02d}.mp4"
        r = subprocess.run(
            [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(seq_list),
             "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
                    f"crop={WIDTH}:{HEIGHT},fps={FPS}",
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(seq)],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"beat {num} sequence concat failed:\n{r.stderr[-800:]}")
        clip = seq
    if clip:
        # WHEN THE SLOT OUTRUNS THE MATERIAL, THE FOOTAGE HOLDS ITS LAST FRAME.
        # It used to loop a PALINDROME (clip + itself reversed), because loop
        # cycle 005 measured that a plain loop restarts as a hard jump-cut
        # mid-shot and a palindrome keeps every seam motion-continuous. That is
        # still true about SEAMS and it was the wrong thing to optimise: a
        # reversal has no seam because it runs time backwards, and an action
        # played back to front is not a continuity artefact, it is a different
        # and impossible event. The 0819c assembly audited all 21 beats and
        # found the branch firing on 8 of the 18 footage beats (1, 3, 4, 6, 10,
        # 11, 17, 18) with nothing printed: beat 06's guard turned the bark
        # board over, un-turned it and turned it again in a 6.71s slot fed by a
        # 1.92s clip; beat 01's fig ripened green→purple and un-ripened, under a
        # verdict that had passed the SOURCE for "0 shrinks".
        #   A HOLD READS AS THE BEAT LANDING. A REVERSAL READS AS TIME FLOWING
        # BACKWARDS. So the fill plays the clip once, forward, and freezes its
        # final frame for the remainder — the action completes and then sits,
        # which is what the voice running longer than the picture actually means.
        # The palindrome survives as opt-in (`wants_pingpong`) for cyclic motion
        # that genuinely is forwards-and-back; reverse also buffers raw frames,
        # so that branch keeps its PINGPONG_MAX_S cap on the source length.
        #   NOT IN TENSION WITH `frozen frame` IN THE NEGATIVE PROMPTS (video_task,
        # beats 9 and 11, pinned by test). That forbids the MODEL from returning a
        # clip with no motion in it — a dead take. This freezes the tail of a clip
        # that already performed its action, after it has performed it.
        cdur = video_duration(clip) or 0
        # NO EPSILON ON THE HELD BRANCH, unlike the palindrome's +0.05. A held
        # still that falls even 0.005s short still wraps ONE frame of the loop
        # onto the end of the beat, and that frame is the widest point of the
        # push — a visible flick back at the cut. Real footage can absorb the
        # slack; a monotonic move cannot, so any shortfall at all is stretched.
        if cdur and dur > cdur and held_still(clips):
            # A HELD STILL IS NEVER PALINDROMED. This path has never fired on a
            # held beat — v30 and v31 both sized their held clips to their slots,
            # and both measure as single monotonic pushes — so this is a latent
            # path being closed, not a bug being fixed. It is worth closing: one
            # held clip left at hold_still's 2.5s default drops beat 14 into a
            # 13s slot, and the palindrome would answer that by running the push
            # in, out, in, out, in. Stretch instead — a computed zoom has no true
            # frame rate, so slowing it is the same move, gentler, still one-way.
            st = workdir / f"st-{num:02d}.mp4"
            r = subprocess.run(
                [FFMPEG, "-y", "-i", str(clip), "-filter_complex",
                 f"[0:v]setpts={(dur + 0.2) / cdur:.6f}*PTS,fps={FPS}[out]",
                 "-map", "[out]", "-an", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "23", str(st)],
                capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode:
                raise SystemExit(f"beat {num} held-still stretch failed:\n"
                                 f"{r.stderr[-800:]}")
            print(f"    beat {num:02d} held still {cdur:.2f}s stretched to fill "
                  f"{dur:.2f}s — not reversed (founder, 2026-08-07)")
            clip = st
        elif (cdur and dur > cdur + 0.05 and cdur <= PINGPONG_MAX_S
              and wants_pingpong(clips)):
            pp = workdir / f"pp-{num:02d}.mp4"
            r = subprocess.run(
                [FFMPEG, "-y", "-i", str(clip), "-filter_complex",
                 "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0[out]",
                 "-map", "[out]", "-an", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "23", str(pp)],
                capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode:
                raise SystemExit(f"beat {num} ping-pong failed:\n{r.stderr[-800:]}")
            print(f"    beat {num:02d} footage {cdur:.2f}s PALINDROMED into "
                  f"{dur:.2f}s — its record asks for it (loop_fill: pingpong)")
            clip = pp
        elif cdur and dur > cdur + 0.05:
            # HOLD THE LAST FRAME. tpad's stop_mode=clone repeats the final
            # decoded frame, so this is the same picture the clip ended on, not a
            # re-encode of a still. Padded 0.2s PAST the slot for the reason the
            # held branch overshoots too: the `-stream_loop -1` below still wraps
            # if trim finds the source even a frame short, and the frame it would
            # wrap to is frame 1 — the very jump-cut this is meant to remove.
            # KEEPS THE +0.05 EPSILON that the palindrome branch had. Under a
            # frame of shortfall is inside ffprobe's own measurement noise; the
            # loop wraps at most one frame there, and re-encoding every beat to
            # append zero frames of freeze buys nothing.
            hd = workdir / f"hd-{num:02d}.mp4"
            r = subprocess.run(
                [FFMPEG, "-y", "-i", str(clip), "-filter_complex",
                 f"[0:v]tpad=stop_mode=clone:stop_duration="
                 f"{dur - cdur + 0.2:.3f},fps={FPS}[out]",
                 "-map", "[out]", "-an", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "23", str(hd)],
                capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode:
                raise SystemExit(f"beat {num} last-frame hold failed:\n{r.stderr[-800:]}")
            print(f"    beat {num:02d} footage {cdur:.2f}s plays once then HOLDS "
                  f"its last frame to fill {dur:.2f}s — not reversed "
                  f"(0819c palindrome audit, 8 of 18 beats)")
            clip = hd
        inputs += ["-stream_loop", "-1", "-i", str(clip)]
        chains.append(
            f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},fps={FPS},"
            f"trim=duration={dur},setpts=PTS-STARTPTS[base]")
    else:
        slate = slate_png(strip_inline_md(beat["slug"]),
                          workdir / f"slate-{num:02d}.png", slate_note)
        inputs += ["-loop", "1", "-t", str(dur), "-i", str(slate)]
        chains.append(f"[0:v]fps={FPS},trim=duration={dur},setpts=PTS-STARTPTS[base]")

    layers = []  # (png, x, y, enable-expr)
    y = 100
    # a terminal chyron must not share the frame with the closing line: on 001
    # a leftover "GROW ✓" sat in the corner through "Something's coming" and
    # read as a stuck overlay, stealing the episode's hook (cold read,
    # 2026-07-30). On a beat whose voice ends before the beat does, hold the
    # chyron until the last word has landed.
    lines_here = [i for i in beat["items"] if i[0] == "line"]
    voice_end = 0.0
    if manifest and manifest.get("lines"):
        voice_end = max((float(l.get("end") or 0) for l in manifest["lines"]), default=0.0)
    ovl_at = max(dur * 0.3, voice_end + 0.15) if (lines_here and voice_end) else dur * 0.3
    if ovl_at > dur - 0.3:          # no room after the line: keep it off entirely
        ovl_at = None
    for j, block in enumerate([i[1] for i in beat["items"] if i[0] == "overlay"]):
        if ovl_at is None:
            continue
        png = text_png(block, workdir / f"ovl-{num:02d}-{j}.png", 24, GREEN, PANEL_BG)
        layers.append((png, "36", str(y), f"gte(t,{ovl_at:.2f})"))
        y += Image.open(png).height + 24

    lines = [(i[1], i[2]) for i in beat["items"] if i[0] == "line"]
    if lines:
        timed = (manifest or {}).get("lines")
        prev_who = None
        for j, (raw_who, text) in enumerate(lines):
            entry = timed[j] if (timed and len(timed) == len(lines)) else None
            who = (entry or {}).get("who") or re.sub(r"\s*\(.*$", "", raw_who).strip().upper() or "VO"
            label, label_color, ink = speaker_style(who)
            if entry and entry.get("chunks"):
                # measured on the synthesized voice (synth_vo) — exact sync
                spans = [(c["text"], c["start"], c["end"]) for c in entry["chunks"]]
            elif entry:
                # the window is the line's SPEECH span [start, end] — spanning
                # to the next line's start dragged captions across the silent
                # inter-line gap, lagging the voice (founder wince 2026-07-23)
                spans = chunk_spans(strip_inline_md(text), entry["start"],
                                    entry.get("end") or dur)
            else:
                spans = chunk_spans(strip_inline_md(text), j * dur / len(lines),
                                    (j + 1) * dur / len(lines))
            # half-open [start, end) windows per chunk avoid the 1-frame
            # flash where two captions overlap at an inclusive boundary
            for k, (chunk, s, e) in enumerate(spans):
                # the caption shows what the voice SAYS; long parentheticals
                # are stage direction and render in the action style instead
                speech, directions = split_caption_display(chunk)
                if speech:
                    # name tag on the line's first chunk, and only when the
                    # speaker changes — steady exchanges stay uncluttered.
                    # A ONE-VOICE episode gets no tags at all: on 001 every
                    # caption read "THE TREE:" from the first frame, which
                    # cold-read viewers took for a captioning bug AND which
                    # spoiled the reincarnation 40s before the episode earns
                    # it (three independent naive readers, 2026-07-30).
                    tag = label if (tag_speakers and k == 0 and who != prev_who) else ""
                    png = text_png(speech, workdir / f"cap-{num:02d}-{j}-{k}.png",
                                   CAPTION_SIZE, ink, CAPTION_BG,
                                   max_w=CAPTION_MAX_W, bold=True,
                                   label=tag, label_color=label_color)
                    layers.append((png, "(W-w)/2", f"H-h-{CAPTION_MARGIN}",
                                   f"gte(t,{s:.2f})*lt(t,{e:.2f})"))
                # `directions` are deliberately NOT rendered: on-screen text
                # nobody speaks reads as noise (founder, 2026-07-25:
                # "sometimes I see subtitles on the screen which aren't
                # said"). They are dropped from the caption and stay in the
                # script for the camera to perform.
                del directions
            prev_who = who

    # NOTE: manifest `actions` (short stage directions) keep their timed
    # PAUSE in the audio — the tree's beat still lands — but are no longer
    # burned in as text. Unspoken on-screen text confused the founder more
    # than the missing beat did (2026-07-25). If the tree's performance
    # needs to read, it has to be in the FOOTAGE (regrow-era shot grammar).

    layers += list(extra_layers or [])

    prev = "base"
    for k, (png, x, yy, enable) in enumerate(layers):
        inputs += ["-loop", "1", "-t", str(dur), "-i", str(png)]
        nxt = f"v{k}"
        chains.append(f"[{prev}][{k + 1}:v]overlay=x={x}:y={yy}"
                      f":enable='{enable}'[{nxt}]")
        prev = nxt
    chains.append(f"[{prev}]format=yuv420p[out]")

    out = workdir / f"beat-{num:02d}.mp4"
    cmd = ([FFMPEG, "-y"] + inputs +
           ["-filter_complex", ";".join(chains), "-map", "[out]",
            "-t", str(dur), "-r", str(FPS), "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-movflags", "+faststart", str(out)])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"beat {num} ffmpeg failed:\n{r.stderr[-1500:]}")
    return out


def clip_provenance(clip: Path) -> dict:
    """The clip's own record (§7.2), under either naming shape.

    with_suffix() REPLACES the extension, so this only ever built
    `<stem>.meta.yaml` and returned {} for every `<full name>.mp4.meta.yaml` —
    the shape hold_still, video_task and the farm worker all write. An empty
    dict here is not a gap in the leaf, it is a LIE in the leaf: beat_provenance
    reads the miss as `platform: none, model: none, cost 0`, so a clip that
    recorded its model honestly gets published as one that named nothing.
    """
    meta = lg.sidecar_for(clip, lg.META_EXT) if clip else None
    if not meta:
        return {}
    try:
        data = yaml.safe_load(meta.read_text()) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        raise SystemExit(f"clip metadata {meta} is unreadable: {e}")
    if not isinstance(data, dict):
        raise SystemExit(f"clip metadata {meta} must be a YAML mapping, got {type(data).__name__}")
    return data


def beat_provenance(clips: list) -> dict:
    """Provenance across ALL of a beat's clips (§7.2): platform/model joined
    unique in sequence order, cost summed — a multi-clip beat credits every
    sidecar, not just the first clip's."""
    provs = [clip_provenance(c) for c in clips]
    plats = dict.fromkeys(str(p.get("platform") or "none") for p in provs)
    models = dict.fromkeys(str(p.get("model") or "none") for p in provs)
    return {"platform": "+".join(plats) or "none",
            "model": "+".join(models) or "none",
            "cost_usd": round(sum((float(p.get("cost_usd", 0) or 0) for p in provs), 0.0), 4)}


# --------------------------------------------------- what went into the cut
# The platform line for the assembly step itself. VERBATIM from the licence
# table (`local-deterministic (pipeline/hold_still.py, render_t3.py, ffmpeg)` →
# CC-BY-4.0, our own output), and pinned there by test_pipeline's UNCHANGED set.
# Inventing a new phrasing here would hand the gate an unclassified string and
# make every cut we assemble 'unknown', i.e. unpublishable, for no reason.
ASSEMBLY_PLATFORM = "local-deterministic (pipeline/hold_still.py, render_t3.py, ffmpeg)"


def file_sha256(p: Path) -> str:
    """sha256 of a file's bytes, read in chunks — a 90s cut's inputs are large."""
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ingredient_row(src: Path, beat: int, kind: str) -> dict:
    """One line of a cut's `ingredients:` manifest: what went in, which bytes,
    and what the licence gate said about it AT THIS MOMENT.

    THE HOLE THIS FILLS. build_site.publishable() reads a file's own sidecar, and
    a concatenation keeps no trace of its inputs — so muxing N clips produced one
    new file with one clean record and every refusal inside it laundered. Two
    live instances were plugged by hand-written sidecars on 2026-08-09 (the
    provisional ep2 cut and v33, both made of material refused one directory
    down); a hand-plug is per-cut and does not survive the next assembly. This is
    the assembly writing down what it knows at the only moment it knows it.

    ASKS build_site.publishable ITSELF rather than re-deriving the verdict, the
    same way this module already borrows render_local.approved() for §6: one
    gate, one implementation. Imported inside the function because build_site
    pulls in markdown and the site theme, which an assembly has no other use for.
    """
    from build_site import publishable
    ok, why = publishable(src)
    resolved = src.resolve()
    try:
        rel = resolved.relative_to(REPO).as_posix()
    except ValueError:
        # Footage from outside the tree. Recorded as its absolute path, which
        # will not resolve on another machine — and that is the honest answer:
        # a cut nobody else can check the inputs of is a cut nobody else should
        # publish. The gate reads an unresolvable ingredient as a refusal.
        rel = resolved.as_posix()
    row = {"beat": beat, "kind": kind, "path": rel,
           "sha256": file_sha256(src), "publishable": bool(ok)}
    if why:
        row["why"] = why
    # AND WHETHER THE INGREDIENT CALLS ITSELF PROVISIONAL, which `publishable`
    # does not answer and was never asked to: that flag is the LICENCE gate's
    # word, and a steward pick out of `takes/` is perfectly licensed and
    # completely unratified. Beat 06 of v34 is exactly that clip — `hold_still`
    # stamps `provisional: true` on it (2026-08-09) — and without this line the
    # cut's manifest showed it as `publishable: true` beside fourteen frames the
    # founder chose himself, with nothing to tell them apart. That is the
    # laundering this function exists to stop, one field over.
    #
    # WHAT IT DOES NOT MEAN, and this is why the flag is COPIED rather than
    # interpreted. `provisional:` is not a settled vocabulary: twelve of v34's
    # fifteen clips inherit the flag from v33, where one lane wrote it by hand
    # onto a whole review set, and their `provisional_reason` lines say four
    # different things — "canon, unchanged", "the founder's face-B pick", "old
    # footage is the superseded picture", and beat 06's actual unratified guess.
    # Beat 15's record manages both at once: reason "canon b15-r3-s1, approved
    # 2026-08-08" under an authority line reading "the founder has ratified
    # nothing here". So a row's flag means EXACTLY "this ingredient's own record
    # marks itself provisional, see its `provisional_reason`" and nothing more
    # precise; reading a taste verdict out of it would be inventing one. Cleaning
    # up that vocabulary is a separate job and it is the author's, not this
    # function's — filed rather than guessed at here.
    side = Path(str(src) + ".meta.yaml")
    if side.is_file():
        try:
            rec = yaml.safe_load(side.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            rec = None          # an unreadable record is publishable()'s to refuse
        if isinstance(rec, dict) and rec.get("provisional") is True:
            row["provisional"] = True
    return row


def assembly_sidecar(out: Path, node_id: str, leaf: str, cost: float,
                     beats: int, sources: list, ingredients: list,
                     seconds: float, all_clips: list) -> Path:
    """Write `<cut>.mp4.meta.yaml` — the record that lets the gate see inside.

    Written for BENCH CUTS TOO, and that is the point rather than an oversight:
    the review page serves working cuts out of `cuts/`, every one of them made
    with `--out`, and those are exactly the files that had no record at all.

    `model:` is the join across every source clip, the same rule beat_provenance
    applies within one beat, so an LTX beat inside a Wan cut is named in the
    cut's own top line and refused by publishable()'s ordinary path before the
    manifest is even walked. Belt and braces on purpose: the join catches a
    licence, the manifest catches a licence AND a substitution.
    """
    prov = beat_provenance(all_clips)
    footage = sorted({r["beat"] for r in ingredients if r["kind"] == "clip"})
    # WHICH BEATS TO GO AND READ, in the cut's own head rather than N sidecars
    # down. A pointer, not a verdict — see ingredient_row on why this list is not
    # "the beats he has not seen": the flag's meaning lives in each ingredient's
    # `provisional_reason` and it is not the same sentence in all of them.
    flagged = sorted({r["beat"] for r in ingredients if r.get("provisional")})
    body = {
        "platform": ASSEMBLY_PLATFORM,
        "model": prov["model"],
        "cost_usd": cost,
        "node": node_id,
        "leaf": leaf or "bench (--out) — no leaf, not canon",
        **({"provisional": True, "provisional_beats": flagged} if flagged else {}),
        "beats": beats,
        "footage_beats": footage,
        "slate_beats": [b for b in range(1, beats + 1) if b not in footage],
        "duration_s": round(seconds, 2),
        "size": f"{WIDTH}x{HEIGHT}",
        "source_platforms": prov["platform"],
        "ingredients": ingredients,
        "sources": sources,
    }
    side = out.with_name(out.name + ".meta.yaml")
    side.write_text(
        "# Assembly provenance (§7.2) — written by pipeline/render_t3.py at\n"
        "# assembly time. `ingredients:` is the list build_site.publishable()\n"
        "# walks: one row per file muxed into this cut, its bytes as muxed, and\n"
        "# the verdict it carried then. A row that no longer resolves, no longer\n"
        "# hashes the same, or no longer passes is a REFUSAL for this whole cut —\n"
        "# a concatenation must not launder what went into it. `provisional:` on\n"
        "# a row is copied from that ingredient's OWN record and means only that\n"
        "# it marks itself provisional — read its `provisional_reason` for what\n"
        "# that means there, because the phrase is not used consistently across\n"
        "# this tree. It is a separate question from `publishable:`, which is the\n"
        "# licence gate's word and says nothing about taste either way.\n"
        + yaml.safe_dump(body, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return side


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("genome")
    p.add_argument("node")
    p.add_argument("--clips", type=Path, default=None, help="dir of per-beat clips (01-*.mp4 …)")
    p.add_argument("--tts", choices=["none", "openai"], default="none")
    p.add_argument("--out", type=Path, default=None,
                   help="bench render: write mp4 here, publish no leaf")
    p.add_argument("--suffix", default="a", help="leaf suffix (default a)")
    p.add_argument("--no-cards", action="store_true", help="skip title/end cards")
    args = p.parse_args()

    # STEWARDSHIP §6: narrative approval precedes media. This tool was one of the
    # three that made 8.7 GPU-hours of media from unread scripts on 2026-07-25 and
    # still had no gate on 2026-07-27 (principles audit, finding #1). One gate, one
    # implementation: render_local.approved().
    from render_local import approved as _approved
    _ok, _detail = _approved(args.genome, args.node)
    if not _ok:
        raise SystemExit(f"{args.node} is NOT approved — {_detail}\n"
                         "STEWARDSHIP.md §6: no episode assembly from an unread script\n"
                         "(bench cuts included — a cut IS media).")
    check_clips_dir(args.clips)

    # Before the first byte of this encode is written, take back the disk a
    # FAILED repack is sitting on. The loop: when free disk is low `git repack`
    # (fired by `git gc --auto` after commits, and a dozen lanes commit into
    # this tree) dies partway and leaves a ~350 MB `tmp_pack_*` in
    # .git/objects/pack; that lowers free disk, so the next repack is likelier
    # to die the same way. Five had piled up by 2026-08-15 — 389 MB, one of them
    # wreckage from that night's own disk incident — accumulating ~0.6 GB/day,
    # and nothing else ever removes them. Only files older than an hour go, so a
    # repack running right now is never touched; full story and the before/after
    # in-pack proof in box_cache.sweep_git_tmp_packs.
    #
    # The import is inside the try with the call: housekeeping bolted to the
    # front of an encode must never be the reason an encode does not happen.
    try:
        from box_cache import sweep_git_tmp_packs, sweep_stale_worktrees
        sweep_git_tmp_packs()
        # Same bargain one directory up: a scratchpad worktree that is clean,
        # already on origin/main and untouched for 12 h is a re-checkout nobody
        # is using — 1275 MB of one was reclaimed on 2026-08-15. Conditions and
        # the reasoning are in box_cache.prunable_worktrees.
        sweep_stale_worktrees(dry_run=False)
    except Exception as _e:               # noqa: BLE001 — see above
        print(f"  tmp_pack sweep skipped ({type(_e).__name__}: {_e})")

    genome_dir = REPO / "genomes" / args.genome
    lineage_text = (genome_dir / "lineage.yaml").read_text()
    lineage = yaml.safe_load(lineage_text)
    node = next(n for n in lineage["nodes"] if n["id"] == args.node)
    node_dir = genome_dir / "nodes" / node["slug"]

    beats = parse_frames(extract_script((node_dir / "node.md").read_text()))
    if not beats:
        raise SystemExit(f"{node['id']}: no beats in script")

    workdir = Path(tempfile.mkdtemp(prefix="t3-"))
    # timeline: ordered (video_part, duration, audio_or_None) — audio aligns to
    # each part's slot so VO stays in sync; cards are silent.
    timeline, sources, missing = [], [], 0
    # every file muxed in that the assembly did not itself make — see
    # ingredient_row(). Cards, slates and captions are generated here from repo
    # text, so they are not ingredients; a TTS take written into workdir is not
    # one either, and recording its temp path would refuse the cut forever.
    ingredients, all_clips = [], []

    tts_cost = 0.0
    tts_fn = None
    if args.tts == "openai":
        from render_t2 import tts_openai
        tts_fn = tts_openai

    title_ovl = None
    if not args.no_cards:
        prev = previously_line(genome_dir, node, lineage["nodes"])
        title_ovl = title_overlay_png(node, prev, workdir / "title-ovl.png")

    # one voice for the whole episode → no speaker tags anywhere (see the
    # caption code): tags only earn their space when there is an exchange
    voices = {re.sub(r"\s*\(.*$", "", it[1]).strip().upper()
              for b in beats for it in b["items"] if it[0] == "line"}
    tag_speakers = len(voices) > 1
    if not tag_speakers:
        print(f"  one voice ({', '.join(voices) or 'none'}) — speaker tags off")

    slate_notes = load_slate_notes(args.clips)
    mismatched = []
    for i, beat in enumerate(beats, 1):
        dur = beat_duration(beat["slug"], beat["items"])
        beat_clips = find_clips(args.clips, i)
        # footage is found by beat NUMBER, so stale footage from a previous cut
        # of the script lands on whatever beat now holds its index. Slating an
        # empty beat is honest; playing the wrong shot over a line is exactly
        # the "random video that isn't correlating" the founder reported.
        wrong = [c for c in beat_clips if not footage_matches_beat(c, strip_inline_md(beat["slug"]))]
        if wrong:
            mismatched += [(i, strip_inline_md(beat["slug"]).split("—")[0].strip(), c.name)
                           for c in wrong]
            beat_clips = [c for c in beat_clips if c not in wrong]
        if not beat_clips:
            missing += 1
        # audio: a pre-supplied per-beat track wins; else generate VO via TTS
        audio = find_audio(args.clips, i)
        if audio is None and tts_fn:
            text = " ".join(strip_inline_md(it[2]) for it in beat["items"] if it[0] == "line")
            if text.strip():
                audio = workdir / f"vo-{i:02d}.mp3"
                tts_cost += tts_fn(text, audio)
        manifest = vo_manifest(args.clips, i)
        # fit the slot to the material, not the script's paper timing:
        # exactly long enough for the footage and the FULL voice track —
        # dialogue is never trimmed mid-line (slate beats included), and
        # short footage loops (see render_beat / fit_duration). Footage is
        # measured video-only and floored to the frame grid: container
        # durations include audio padded past the video, and that overshoot
        # looped a 1-frame flash of the first clip onto the beat's end.
        vdur = (manifest or {}).get("total_s") or (media_duration(audio) if audio else 0) or 0
        cdur = 0.0
        if beat_clips:
            csum = sum(video_duration(c) or 0 for c in beat_clips)
            cdur = (math.floor(csum * FPS) / FPS) or dur
        dur = fit_duration(dur, cdur, vdur)
        extra = ([(title_ovl, "(W-w)/2", "110", "lt(t,2.8)")]
                 if i == 1 and title_ovl else None)
        timeline.append((render_beat(beat, i, dur, beat_clips, workdir, manifest,
                                     extra_layers=extra, tag_speakers=tag_speakers,
                                     slate_note=slate_notes.get(i)),
                         dur, audio))
        if not beat_clips and slate_notes.get(i):
            print(f"    beat {i:02d} SLATE — card reads: {slate_notes[i]}")
        sources.append({"beat": i, "slug": strip_inline_md(beat["slug"]),
                        "clip": "+".join(c.name for c in beat_clips) if beat_clips else "slate (no footage yet)",
                        "audio": audio.name if audio else "none",
                        **({"voice_engine": manifest["engine"]}
                           if manifest and manifest.get("engine") else {}),
                        **beat_provenance(beat_clips)})
        all_clips += beat_clips
        ingredients += [ingredient_row(c, i, "clip") for c in beat_clips]
        if audio is not None and workdir not in audio.parents:
            ingredients.append(ingredient_row(audio, i, "audio"))

    if mismatched:
        print(f"  IGNORED {len(mismatched)} clip(s) made for a different beat "
              "(a rewrite renumbered the beats; slating instead):")
        for n, title, name in mismatched[:8]:
            print(f"    beat {n:02d} {title} <- {name}")
        if len(mismatched) > 8:
            print(f"    … and {len(mismatched) - 8} more")
        print("    archive them: genomes/<g>/nodes/<n>/clips/footage-archive/")

    if not args.no_cards:
        end = card_png([
            ("banyan.city", 34, GREEN),
            ("branch this node · fork the city", 22, (147, 166, 152, 255)),
            ("every render is open data", 18, (147, 166, 152, 255)),
        ], workdir / "end.png")
        timeline.append((card_clip([(end, 3.0)], workdir, "end")[0], 3.0, None))

    leaf_id = f"{node['id']}-t3-{args.suffix}"
    out = args.out or (node_dir / "leaves" / f"{leaf_id}.mp4")
    video = workdir / "video.mp4"
    concat = workdir / "concat.txt"
    concat.write_text("\n".join(f"file '{p.resolve()}'" for p, _, _ in timeline))
    r = subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                        "-c", "copy", str(video)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"concat failed:\n{r.stderr[-1500:]}")

    # mux a single audio track only if any beat actually carries audio —
    # otherwise the episode stays a silent, captioned animatic (still valid).
    n_story_beats = len(beats)
    sound_design = load_sound_design(args.clips)
    if any(a for _, _, a in timeline) or sound_design.get("events"):
        # ---- one placed mix, not concatenated segments (cycle 012) ----
        # Per-beat AAC segments quantize to ~23 ms frames and per-beat video
        # encodes to the frame grid; concatenated separately, the two drifted
        # apart cumulatively and later captions lagged the voice (founder
        # note 2026-07-30: "some subtitles are offset"). Now every beat's
        # audio is placed at its beat's MEASURED video offset in a single
        # filtergraph, so audio position derives from the actual video files.
        rdurs = [video_duration(p) or d for p, d, _ in timeline]
        offs = [sum(rdurs[:k]) for k in range(len(rdurs))]
        total_s = sum(rdurs)
        # the timeline table: where every beat actually starts in the master —
        # sound.yaml events are placed against THESE numbers, not paper timing
        for k, (_, _, a) in enumerate(timeline):
            tag = f"beat {k + 1:02d}" if k < n_story_beats else "end card"
            print(f"    {tag}  {offs[k]:6.2f}s  +{rdurs[k]:.2f}s"
                  f"{'  ♪ ' + Path(a).name if a else ''}")

        inputs: list = []
        chains: list = []
        mix_ins: list = []
        n_in = 0

        def add_input(*spec: str) -> int:
            nonlocal n_in
            inputs.extend(spec)
            n_in += 1
            return n_in - 1

        for k, (_, d, a) in enumerate(timeline):
            if not a:
                continue
            i = add_input("-i", str(a))
            chains.append(f"[{i}:a]aresample={AUDIO_SR},aformat=channel_layouts=stereo,"
                          f"adelay={int(offs[k] * 1000)}:all=1[vo{k}]")
            mix_ins.append(f"[vo{k}]")

        # synthesized cues from clips/sound.yaml — the script's own sound
        # design (keyboard that stops, mug in the silence, fan spin-down)
        if sound_design.get("events"):
            import sfx as _sfx
            for j, ev in enumerate(sound_design["events"]):
                b = int(ev["beat"])
                if not 1 <= b <= len(rdurs):
                    raise SystemExit(f"sound.yaml event {j}: beat {b} out of range")
                name = str(ev["sfx"])
                dur = ev.get("dur")
                dur = rdurs[b - 1] if dur in (None, "full") else float(dur)
                wav = workdir / f"sfx-{j:02d}-{name}.wav"
                if ev.get("file"):
                    # a RECORDED cue: public-domain / CC0 only, provenance in
                    # the node's audio-sources/SOURCES.md. Real ceramic and real
                    # keyswitches beat anything synthesized from sine waves.
                    src = REPO / str(ev["file"])
                    if not src.exists():
                        raise SystemExit(f"sound.yaml event {j}: missing {src}")
                    af = [f"atrim=duration={dur:.2f}", f"aresample={AUDIO_SR}"]
                    if ev.get("trim_start"):
                        af.insert(0, f"atrim=start={float(ev['trim_start']):.2f}")
                    r = subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(src),
                                        "-af", ",".join(af), "-ac", "1", str(wav)],
                                       capture_output=True, text=True, encoding="utf-8", errors="replace")
                    if r.returncode:
                        raise SystemExit(f"recorded cue {src.name} failed:\n{r.stderr[-500:]}")
                elif name in _sfx.SYNTHS:
                    # everything that isn't placement is a synth parameter
                    # (stop_at, period, grow, …) — passed straight through
                    params = {k: v for k, v in ev.items()
                              if k not in ("beat", "sfx", "start", "dur", "gain_db", "file",
                                           "trim_start")}
                    _sfx.SYNTHS[name](wav, dur=dur, **params)
                else:
                    raise SystemExit(f"sound.yaml event {j}: unknown sfx {name!r} "
                                     f"(have: {', '.join(sorted(_sfx.SYNTHS))} or a file:)")
                at = offs[b - 1] + float(ev.get("start", 0))
                gain = float(ev.get("gain_db", -18))
                i = add_input("-i", str(wav))
                chains.append(f"[{i}:a]volume={gain}dB,aresample={AUDIO_SR},"
                              f"aformat=channel_layouts=stereo,"
                              f"adelay={int(at * 1000)}:all=1[fx{j}]")
                mix_ins.append(f"[fx{j}]")

        # sound floor (loop cycle 001, defects 6/7): a whisper wind bed under
        # the whole episode so no frame is digitally silent — except where the
        # design says silence IS the point (bed_duck: the death sequence).
        duck = ""
        bd = sound_design.get("bed_duck")
        if bd:
            t1 = offs[int(bd["from"]["beat"]) - 1] + float(bd["from"].get("at", 0))
            t2 = offs[int(bd["to"]["beat"]) - 1] + float(bd["to"].get("at", 0))
            # NOT a pair of afades: afade=t=in mutes everything BEFORE its
            # start, so out@t1 + in@t2 silences the whole track (found the
            # hard way — QA caught the bed at the digital floor). A windowed
            # volume expression ducks only [t1, t2]: 0.2s out-ramp, 1.2s back.
            # Floor at 0.15 (≈ −57 dB with the bed's own level): scored
            # silence is AIR, not digital zero — true zero reads as a
            # playback glitch on a phone, and qa_episode still polices real
            # dropouts at the digital floor.
            duck = (f",volume=volume='max(0.15, clip(({t1:.2f}-t)/0.2,0,1)"
                    f"+clip((t-{t2:.2f})/1.2,0,1))':eval=frame")
        i = add_input("-f", "lavfi", "-i",
                      f"anoisesrc=color=brown:seed=42:r=24000:d={total_s:.2f}")
        # darker + quieter than v1: at 0.05/300Hz the bed read as "a random
        # weird wind sound" indoors (founder, v7d notes)
        chains.append(f"[{i}:a]lowpass=f=240,volume=0.032"
                      f",afade=t=out:st={max(total_s - 3.0, 0):.2f}:d=3{duck}"
                      f",aresample={AUDIO_SR},aformat=channel_layouts=stereo[wind]")
        mix_ins.append("[wind]")

        chains.append(f"{''.join(mix_ins)}amix=inputs={len(mix_ins)}:duration=longest:"
                      f"normalize=0,apad=whole_dur={total_s:.2f}s[mix]")

        # the pre-master stays PCM: mastering is measure-then-correct, and
        # measuring an AAC generation you are about to re-encode both lies a
        # little and costs a generation of quality for nothing
        mixed = workdir / "mixed.wav"
        r = subprocess.run(
            [FFMPEG, "-y"] + inputs +
            ["-filter_complex", ";".join(chains), "-map", "[mix]",
             "-t", f"{total_s:.2f}", "-ar", str(AUDIO_SR), "-ac", "2",
             "-c:a", "pcm_s16le", str(mixed)],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"placed mix failed:\n{r.stderr[-1500:]}")
        measured = loudnorm_measure(mixed)
        master = workdir / "master.wav"

        def master_pass(offset) -> str:
            """One mastering pass at loudnorm's internal 192k, limiter included.

            The limiter MUST live in this filter chain: limiting after the 44.1k
            downsample flat-tops the wave and true peak explodes (+1.5 dBTP the
            first time, 0.1 dBTP when retried on 2026-07-25 — both caught by
            qa_episode)."""
            af = f"loudnorm=I={LOUDNESS_TARGET:g}:TP={TP_TARGET}:LRA=11"
            if measured:  # linear gain — dynamic single-pass pumps on dialogue
                af += (f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
                       f":measured_LRA={measured['input_lra']}"
                       f":measured_thresh={measured['input_thresh']}"
                       f":offset={offset:.2f}:linear=true")
            af += f",alimiter=limit={LIMIT_MASTER}:level=0"
            r = subprocess.run([FFMPEG, "-y", "-i", str(mixed), "-af", af,
                                "-ar", str(AUDIO_SR), "-c:a", "pcm_s16le", str(master)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode:
                raise SystemExit(f"master failed:\n{r.stderr[-1500:]}")
            return af

        # loudnorm does not land on its target: in linear mode it clamps its own
        # gain against the true-peak ceiling and then reports a target_offset it
        # never applied, which left 001 at -15.4 LUFS against -14 (qa_episode,
        # 2026-07-25). So measure the master and feed the shortfall back through
        # loudnorm's own offset until it lands, rather than bolting a gain stage
        # onto the end where it would wreck the peak.
        offset = float(measured["target_offset"]) if measured else 0.0
        prev = None
        for attempt in range(3):
            master_pass(offset)
            got = integrated_lufs(master)
            if got is None:
                break
            if abs(got - LOUDNESS_TARGET) <= LOUDNESS_TOL:
                if attempt:
                    print(f"  master {got:+.1f} LUFS after {attempt + 1} passes")
                break
            # peak-bound material never reaches the target: every extra dB of
            # gain is eaten by the limiter, so the passes converge somewhere
            # short of it. Stop when a pass stops buying loudness and say where
            # it landed, instead of burning encodes on an asymptote.
            if prev is not None and got - prev < 0.15:
                print(f"  master {got:+.1f} LUFS — peak-bound, {LOUDNESS_TARGET:g} "
                      f"unreachable without squashing the peaks further")
                break
            shortfall = LOUDNESS_TARGET - got
            print(f"  master measured {got:+.1f} LUFS — re-mastering {shortfall:+.2f} dB")
            prev = got
            offset = max(-6.0, min(6.0, offset + shortfall))
        r = subprocess.run([FFMPEG, "-y", "-i", str(video), "-i", str(master),
                            "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                            "-ar", str(AUDIO_SR),
                            "-c:a", "aac", "-b:a", "160k", "-shortest",
                            "-movflags", "+faststart", str(out)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"mux failed:\n{r.stderr[-1500:]}")
    else:
        # remux (not rename) so the FINAL file is faststart — the per-part
        # encodes are, but concat -c copy rewrites the container with moov
        # at the end, which stalls browser playback (regression class 068988d)
        r = subprocess.run([FFMPEG, "-y", "-i", str(video), "-c", "copy",
                            "-movflags", "+faststart", str(out)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise SystemExit(f"faststart remux failed:\n{r.stderr[-1500:]}")

    total = sum(d for _, d, _ in timeline)
    cost = round(tts_cost + sum(s["cost_usd"] for s in sources), 2)
    print(f"✓ assembled {out.name}: {len(beats)} beats ({len(beats) - missing} footage, "
          f"{missing} slate), ~{total:.0f}s, cost ${cost:.2f}")

    # BEFORE the bench return, because a bench cut is exactly the file that had
    # no record: `cuts/` is served to the review page and every cut in it was
    # made with --out.
    side = assembly_sidecar(out, node["id"], "" if args.out else leaf_id, cost,
                            len(beats), sources, ingredients, total, all_clips)
    blocked = [r for r in ingredients if not r["publishable"]]
    print(f"  ↳ {side.name}: {len(ingredients)} ingredient(s)"
          + (f", {len(blocked)} REFUSED by the licence gate — this cut will be "
             "withheld from the site" if blocked else ""))
    for r in blocked[:6]:
        print(f"    ✗ {r['path']} — {r.get('why', 'refused')}")

    if args.out:
        return 0  # bench render — no leaf, no lineage

    (node_dir / "leaves" / f"{leaf_id}.yaml").write_text(
        "# Leaf metadata — every render publishes its full provenance (§7.2)\n"
        + yaml.safe_dump({
            "leaf": leaf_id, "node": node["id"], "tier": "T3", "form": "full-video-mp4",
            "content": f"{leaf_id}.mp4",
            "author": "pipeline/render_t3.py (assembly; per-beat footage sources below)",
            "model": "per-beat — see sources", "prompt": "per-beat — see sources",
            "seed": "per-beat — see sources", "cost_usd": cost,
            "status": "live", "platform_urls": [], "sources": sources,
        }, sort_keys=False))
    if leaf_id not in (node.get("leaves") or []):
        # separator only when the list is non-empty — '[, X]' is invalid YAML
        (genome_dir / "lineage.yaml").write_text(re.sub(
            rf"(- id: \"{re.escape(node['id'])}\"\n(?:.*\n)*?    leaves: \[)([^\]]*)",
            lambda m: m.group(1) + (f"{m.group(2)}, {leaf_id}" if m.group(2).strip() else leaf_id),
            lineage_text, count=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())