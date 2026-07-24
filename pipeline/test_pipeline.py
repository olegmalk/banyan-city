#!/usr/bin/env python3
"""Fast, dependency-light tests for the render pipeline's parsing logic.

No ffmpeg, no chromium, no network — pure functions only, so this runs in CI
next to lint_genome.py. Catches the silent-corruption regressions: a broken
beat-timing regex or clip-naming rule would mis-time or drop episode footage
without any error. Run: python3 pipeline/test_pipeline.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_t2 as t2
import render_t3 as t3
from render_t1 import extract_script, parse_frames

REPO = Path(__file__).resolve().parent.parent
FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def test_beat_duration_from_timecode():
    # `SLUG — 0:00–0:12` → 12.0s exactly (en-dash separator)
    check("timecode 0:00–0:12 → 12.0", t3.beat_duration("COLD OPEN — 0:00–0:12", []) == 12.0)
    check("timecode 1:05–1:25 → 20.0", t3.beat_duration("HOOK — 1:05–1:25", []) == 20.0)
    check("hyphen separator 0:28-0:40 → 12.0", t3.beat_duration("X — 0:28-0:40", []) == 12.0)


def test_beat_duration_fallback():
    # no timecode → reading-speed estimate, clamped to [MIN, MAX]
    d_empty = t3.beat_duration("NO TIME", [])
    check("empty beat clamps to MIN_SEC", d_empty == t3.MIN_SEC)
    long_items = [("line", "", "x" * 500)]
    check("long beat clamps to MAX_SEC", t3.beat_duration("NO TIME", long_items) == t3.MAX_SEC)


def test_find_clip_naming(tmp: Path):
    (tmp / "01-cold-open.mp4").write_bytes(b"x")
    (tmp / "04.mp4").write_bytes(b"x")
    check("finds NN-slug.mp4", t3.find_clip(tmp, 1) is not None)
    check("finds bare NN.mp4", t3.find_clip(tmp, 4) is not None)
    check("missing beat → None", t3.find_clip(tmp, 2) is None)
    check("no clips dir → None", t3.find_clip(None, 1) is None)


def test_find_audio_naming(tmp: Path):
    (tmp / "01-vo.mp3").write_bytes(b"x")
    (tmp / "03.wav").write_bytes(b"x")
    check("finds NN-*.mp3 audio", t3.find_audio(tmp, 1) is not None)
    check("finds bare NN.wav audio", t3.find_audio(tmp, 3) is not None)
    check("beat without audio → None", t3.find_audio(tmp, 2) is None)
    check("no clips dir → None audio", t3.find_audio(None, 1) is None)


def test_wrap_never_drops_words():
    font = t3.mono_font(24)
    text = "SENSE roots air vibration and several more words here to force wrapping"
    wrapped = t3.wrap(text, font, 200)
    joined = " ".join(wrapped).split()
    check("wrap preserves all words", joined == text.split())


def test_caption_chunks():
    """Loop cycle 001 defects 8/11/12: captions are short phrase units, never
    paragraph walls, and never lose or reorder a word."""
    wall = ("Right. Sev-1. You know the drill: stay calm, assess capabilities, "
            "work the problem. Step two: what do we actually know?")
    chunks = t3.caption_chunks(wall)
    check("chunker preserves every word in order",
          " ".join(chunks).split() == wall.split())
    check("no chunk exceeds the cap (+orphan margin)",
          all(len(c.split()) <= t3.CAPTION_MAX_WORDS + 2 for c in chunks))
    check("wall becomes multiple units", len(chunks) >= 3)
    check("short sentence stays one unit", t3.caption_chunks("Huh.") == ["Huh."])
    check("sentences stay separate beats", t3.caption_chunks("Huh. Green.") == ["Huh.", "Green."])
    rapid = t3.caption_chunks("Newhaven! (no leaf) Greenrest? (nothing) Fig… holm? (aggressively nothing)")
    check("tiny sentences never fold across boundaries (004 caption wall)",
          rapid[0] == "Newhaven!" and len(rapid) == 5)
    check("empty-ish input survives", t3.caption_chunks("  ") == [""])
    check("captions clear the platform chrome (>=20% bottom margin)",
          t3.CAPTION_MARGIN >= int(t3.HEIGHT * 0.20))
    check("caption box narrower than the action-rail line",
          t3.CAPTION_MAX_W <= t3.WIDTH - 140)
    spans = t3.chunk_spans("One two three. Four five six seven eight nine.", 2.0, 8.0)
    check("spans cover the window", abs(spans[0][1] - 2.0) < 1e-6 and abs(spans[-1][2] - 8.0) < 1e-6)
    check("spans are contiguous",
          all(abs(spans[i][2] - spans[i + 1][1]) < 1e-6 for i in range(len(spans) - 1)))


def test_parse_frames_bold_emphasis_in_quote():
    # regression: a quote line opening with bold emphasis ('> **fires**. rest')
    # is a wrapped speech continuation — only a colon marks a new speaker
    md = ("**SCENE — 0:00–0:12**\n"
          "\n"
          "> **ROOT:** the line before\n"
          "> **fires**. rest of the sentence\n")
    items = parse_frames(md)[0]["items"]
    check("colon quote parses as speaker line", items[0] == ("line", "ROOT", "the line before"))
    check("bold-emphasis quote is speakerless", items[1][:2] == ("line", ""))
    check("bold-emphasis quote keeps its text", items[1][2] == "**fires**. rest of the sentence")


def test_parse_frames_bold_line_needs_timing():
    # regression: a full-bold line is a beat heading only WITH a timing range;
    # without one it is emphasis inside the scene → action item
    md = ("**SCENE — 0:00–0:12**\n"
          "\n"
          "**Both leaves tilt at once.**\n"
          "\n"
          "**NEXT BEAT — 0:12–0:20**\n")
    frames = parse_frames(md)
    check("bold line without timing is not a beat", len(frames) == 2)
    check("bold line without timing becomes action",
          frames[0]["items"] == [("action", "Both leaves tilt at once.")])
    check("bold line with timing is a beat", frames[1]["slug"] == "NEXT BEAT — 0:12–0:20")


def test_build_shots_merges_continuations():
    # regression: a wrapped speech (speakerless quote continuations, incl. one
    # opening with bold emphasis) stays one card — no mid-sentence cuts
    md = ("**SCENE — 0:00–0:12**\n"
          "\n"
          "> **ROOT:** The survey says the lot is empty. It\n"
          "> **lies**. Someone lives in every ring\n"
          "> of this trunk.\n")
    shots = t2.build_shots(parse_frames(md), "test-node")
    spoken = [s for s in shots if s["type"] in ("line", "vo")]
    check("wrapped speech is one card", len(spoken) == 1)
    check("merged card keeps its speaker", spoken[0]["who"] == "ROOT")
    check("merged card keeps the whole sentence",
          spoken[0]["text"] == "The survey says the lot is empty. It lies. "
                               "Someone lives in every ring of this trunk.")
    check("merged card re-times to the full text",
          spoken[0]["dur"] == t2.clamp(1.4, len(spoken[0]["text"]) / 18.0, 6.0))


def test_overlay_font_px():
    # regression: an 80-col terminal line must fit the ~578px card interior
    # (mono glyphs ≈ 0.62em); short lines cap at 17px, never balloon
    wide = "x" * 80
    px = t2.overlay_font_px(wide)
    check("80-col line fits the card", px <= 578 / (80 * 0.62))
    check("80-col line stays legible (>=9px)", px >= 9)
    check("widest line drives the size", t2.overlay_font_px("short\n" + wide) == px)
    check("short lines cap at 17px", t2.overlay_font_px("$ leaf status") == 17)


def test_speaker_key_strips_parentheticals():
    # regression: '(writing)' is a stage direction, not part of the cast key
    check("parenthetical stripped", t2.speaker_key("ASSESSOR (writing)") == "ASSESSOR")
    check("multi-word parenthetical stripped",
          t2.speaker_key("ASSESSOR (writing, without emotion)") == "ASSESSOR")
    check("plain speaker normalizes upper", t2.speaker_key(" root ") == "ROOT")


def test_clean_speech_drops_parentheticals():
    # regression: the voice must not read stage directions aloud
    check("stage parentheticals dropped",
          t2.clean_speech("(beat) I heard it. (softly) Everything.") == "I heard it. Everything.")
    check("plain speech untouched", t2.clean_speech("I heard it.") == "I heard it.")


def test_node_001_beats_parse():
    md = (REPO / "genomes/sapling/nodes/001-capability-inventory/node.md").read_text()
    beats = parse_frames(extract_script(md))
    check("node 001 parses 7 beats (t0-b molt)", len(beats) == 7)
    total = sum(t3.beat_duration(b["slug"], b["items"]) for b in beats)
    check("node 001 total = 80s script time (t0-b molt)", total == 80.0)
    # every beat has a nonempty slug
    check("all beats have slugs", all(b["slug"].strip() for b in beats))


def test_shot_prompt_extraction():
    # intake pulls the verbatim prompt for a shot out of prompts.md; shot C's
    # prompt contains a colon ("stylized shot:") — the bug that broke the
    # hand-built meta YAML. Assert it round-trips through yaml cleanly.
    import yaml
    sys.path.insert(0, str(REPO / "pipeline" / "t3-trials"))
    import intake
    for shot in ("A", "B", "C"):
        prompt = intake.shot_prompt(shot)
        check(f"shot {shot} prompt nonempty", len(prompt) > 40)
        # emulate intake's serialization and confirm it parses back
        dumped = yaml.safe_dump({"prompt": prompt})
        check(f"shot {shot} prompt survives YAML", yaml.safe_load(dumped)["prompt"] == prompt)


def test_generate_shots_parsing():
    # the API driver must see every beat + verbatim prompt in shots.md;
    # a silent parse miss would skip a beat and ship an episode with a hole
    from generate_shots import parse_shots
    md = (REPO / "genomes/sapling/nodes/001-capability-inventory/shots.md").read_text()
    shots = parse_shots(md)
    check("shots.md parses 7 beats (t0-b molt)", len(shots) == 7)
    check("beat numbering 1..7", [s["num"] for s in shots] == [1, 2, 3, 4, 5, 6, 7])
    check("prompts nonempty + vertical", all("9:16" in s["prompt"] for s in shots))
    # the t0-b molt shot list (2026-07-25) awaits the regrow era: no beat
    # parses as done until footage for the new skeleton exists
    check("done-status parsed", [s["done"] for s in shots] == [False] * 7)


def test_budget_guard():
    # money-drain protection: pricing must resolve, unknown models must price
    # PESSIMISTICALLY, and the caps file must parse with sane values
    import generate_shots as gs
    check("veo fast rate", gs.price_per_sec("fal-ai/veo3.1/fast") == 0.15)
    check("kling turbo rate", gs.price_per_sec("fal-ai/kling-video/v3/turbo/standard/text-to-video") == 0.112)
    check("unknown model prices at max", gs.price_per_sec("brand-new-model-x") == gs.FALLBACK_PRICE)
    # wan family: specific versions price above the generic fal-wan entry, and
    # ordering in the table must let the specific fragments win
    check("wan2.7 rate", gs.price_per_sec("wan2.7-t2v") == 0.10)
    check("wan2.6 rate", gs.price_per_sec("wan2.6-t2v") == 0.15)
    check("generic wan rate", gs.price_per_sec("fal-ai/wan-25/text-to-video") == 0.05)
    check("wan provider registered", "wan" in gs.PROVIDERS)
    caps = gs.budget()
    check("caps parse + per-run <= lifetime",
          0 < caps["hard_cap_per_run_usd"] <= caps["hard_cap_total_usd"])


def test_all_leaf_content_exists():
    # every leaf's declared content file must exist on disk — the guarantee the
    # lint content-check enforces, verified here against the real genome so a
    # renamed/deleted artifact fails fast (dead site links otherwise)
    import yaml
    gdir = REPO / "genomes" / "sapling"
    lineage = yaml.safe_load((gdir / "lineage.yaml").read_text())
    ok = True
    for n in lineage["nodes"]:
        ndir = gdir / "nodes" / n["slug"]
        for leaf_id in n.get("leaves") or []:
            meta = yaml.safe_load((ndir / "leaves" / f"{leaf_id}.yaml").read_text())
            content = str(meta.get("content", ""))
            if content and content != "../node.md" and not (ndir / "leaves" / content).exists():
                print(f"      missing content: {n['id']}/{leaf_id} -> {content}")
                ok = False
    check("every leaf content file exists on disk", ok)


def test_trials_page_renders():
    # build_site.render_trials must not crash (populated or empty) and must
    # carry the core sections (regression guard for the /trials/ page)
    sys.path.insert(0, str(REPO / "pipeline"))
    import build_site
    html = build_site.render_trials()
    check("trials page renders", "T3 platform trials" in html)
    check("trials page has prompts section", "three prompts" in html)


def test_generate_shots_fence_binding():
    # regression: an info-string fence (```text) or a beat with a missing fence
    # skidded prompts across beats — the wrong prompt went to a paid API. Each
    # fence must bind to ITS beat's section; fence-less beats are skipped.
    from generate_shots import parse_shots
    md = ("## Beat 01 — ALPHA (0:00–0:10) ⬜ needs footage\n\n"
          "```text\nprompt alpha 9:16\n```\n\n"
          "## Beat 02 — BRAVO (0:10–0:20) ⬜ needs footage\n\n"
          "commentary but no prompt fence at all\n\n"
          "## Beat 03 — CHARLIE (0:20–0:30) ✅ generated\n\n"
          "```\nprompt charlie 9:16\n```\n")
    shots = parse_shots(md)
    check("fence-less beat skipped, not swallowed", [s["num"] for s in shots] == [1, 3])
    check("info-string fence binds to its own beat",
          [s["prompt"] for s in shots] == ["prompt alpha 9:16", "prompt charlie 9:16"])
    check("done status survives fence rework", [s["done"] for s in shots] == [False, True])


def test_generate_shots_effective_duration():
    # regression: the budget gate must price the seconds the provider actually
    # bills (veo clamps to 4/6/8s, wan floors at 2s), not the raw --duration ask
    from generate_shots import effective_duration
    check("veo clamps 10s ask to 8s billed", effective_duration("veo", None, 10) == 8)
    check("veo keeps a native 6s ask", effective_duration("veo", None, 6) == 6)
    check("fal-hosted veo clamps too", effective_duration("fal", "fal-ai/veo3.1/fast", 10) == 8)
    check("fal kling passes duration through",
          effective_duration("fal", "kling-video/v3/turbo/standard/text-to-video", 10) == 10)
    check("wan floors at 2s", effective_duration("wan", None, 1) == 2)
    check("wan caps at 15s", effective_duration("wan", None, 20) == 15)
    check("kling passes duration through", effective_duration("kling", None, 10) == 10)


def test_generate_shots_download_atomic(tmp: Path):
    # regression: download wrote straight to the final NN-*.mp4, so a crash
    # left a truncated file the resume check counted as footage — must land
    # via .part + rename, and a failed fetch must leave nothing behind
    from generate_shots import download
    src = tmp / "src.bin"
    src.write_bytes(b"clip-bytes")
    dest = tmp / "01-alpha.mp4"
    download(src.as_uri(), dest)
    check("download lands complete at final path", dest.read_bytes() == b"clip-bytes")
    check("no .part temp left behind", not list(tmp.glob("*.part")))
    try:
        download((tmp / "missing.bin").as_uri(), tmp / "02-bravo.mp4")
        check("failed download raises", False)
    except OSError:
        check("failed download raises", True)
    check("failed download leaves no partial file",
          not (tmp / "02-bravo.mp4").exists() and not list(tmp.glob("*.part")))


def test_register_leaf_list_separator():
    # regression: registering a leaf into an empty `leaves: []` wrote
    # 'leaves: [, X]' — invalid YAML. The separator must appear only when
    # the list already has entries. render_t2/t3 inline the same regex +
    # replacement for their lineage writes; render_t1.register_leaf is the
    # named form under test.
    import yaml
    from render_t1 import register_leaf
    stub = ('nodes:\n'
            '  - id: "001"\n'
            '    slug: 001-x\n'
            '    leaves: []\n')
    out = register_leaf(stub, "001", "001-t1-a")
    check("empty list: no leading comma", "leaves: [001-t1-a]" in out)
    check("empty list result is valid YAML",
          yaml.safe_load(out)["nodes"][0]["leaves"] == ["001-t1-a"])
    out2 = register_leaf(stub.replace("[]", "[001-t0-a]"), "001", "001-t1-a")
    check("non-empty list appends with ', '", "leaves: [001-t0-a, 001-t1-a]" in out2)
    check("non-empty list result is valid YAML",
          yaml.safe_load(out2)["nodes"][0]["leaves"] == ["001-t0-a", "001-t1-a"])


def test_t2_openai_shots_stretch_to_audio(tmp: Path):
    # regression: --tts openai trimmed narration to the reading-time estimate
    # (-t dur) and never stretched the shot — synth_openai must extend dur to
    # the measured mp3 length + 0.35s tail, exactly like synth_kokoro
    shots = [{"type": "title", "who": "n", "text": "T", "dur": 1.3},
             {"type": "line", "who": "ROOT", "text": "a long speech", "dur": 1.4}]
    orig_tts, orig_dur = t2.tts_openai, t2.media_duration
    t2.tts_openai = lambda text, out: (out.write_bytes(b"mp3"), 0.001)[1]
    t2.media_duration = lambda ff, f: 4.0  # narration far longer than the card
    try:
        cost = t2.synth_openai("ffmpeg", shots, tmp)
    finally:
        t2.tts_openai, t2.media_duration = orig_tts, orig_dur
    check("openai narration stretches its shot", shots[1]["dur"] == 4.35)
    check("openai shot records its audio file", shots[1].get("audio") == tmp / "vo-001.mp3")
    check("title card stays silent and untimed", "audio" not in shots[0] and shots[0]["dur"] == 1.3)
    check("openai cost accumulates", cost == 0.001)


def test_t2_final_mux_keeps_faststart(tmp: Path):
    # regression: build_audio_track/mux_voice replace the assembled leaf, so
    # their final mux must carry assemble()'s -movflags +faststart — otherwise
    # every voiced render ships with the moov atom at the tail (no fast play)
    calls = []

    def fake_run(cmd, **kw):
        calls.append([str(c) for c in cmd])
        out = Path(cmd[-1])
        if out.suffix in (".mp4", ".m4a", ".wav"):
            out.write_bytes(b"x")

    mp3 = tmp / "vo-000.mp3"
    mp3.write_bytes(b"a")
    shots = [{"type": "line", "who": "R", "text": "hi", "dur": 2.0, "audio": mp3}]
    orig_run = t2.subprocess.run
    t2.subprocess.run = fake_run
    try:
        video = tmp / "leaf.mp4"
        video.write_bytes(b"v")
        t2.build_audio_track("ffmpeg", video, shots, tmp)
        kokoro_muxes = [c for c in calls if c[-1].endswith("voiced.mp4")]
        calls.clear()
        video.write_bytes(b"v")
        t2.mux_voice("ffmpeg", video, shots, tmp)
        openai_muxes = [c for c in calls if c[-1].endswith("voiced.mp4")]
    finally:
        t2.subprocess.run = orig_run
    check("kokoro final mux keeps +faststart",
          bool(kokoro_muxes) and all("+faststart" in c for c in kokoro_muxes))
    check("openai final mux keeps +faststart",
          bool(openai_muxes) and all("+faststart" in c for c in openai_muxes))
    check("openai mux voices the pre-synthesized mp3",
          any(str(mp3) in c for c in calls))


def test_t3_find_clips_primary_first(tmp: Path):
    # regression: '-' < '.' so a plain filename sort put NN-slug-alt1.mp4 ahead
    # of the primary NN-slug.mp4 — every multi-take beat led with the alt take
    for name in ("01-cold-open-alt2.mp4", "01-cold-open.mp4", "01-cold-open-alt1.mp4"):
        (tmp / name).write_bytes(b"x")
    order = [c.name for c in t3.find_clips(tmp, 1)]
    check("primary take sorts first",
          order == ["01-cold-open.mp4", "01-cold-open-alt1.mp4", "01-cold-open-alt2.mp4"])
    check("find_clip returns the primary", t3.find_clip(tmp, 1).name == "01-cold-open.mp4")


def test_t3_fit_duration():
    # footage beats: slot = max(sequence, VO + 0.4) — never the paper timing
    check("footage sizes its slot", t3.fit_duration(12.0, 10.0, 0.0) == 10.0)
    check("footage stretches for VO", t3.fit_duration(12.0, 10.0, 11.0) == 11.4)
    check("voice leads: long footage capped at VO + tail (cycle 004)",
          t3.fit_duration(12.0, 10.0, 4.6) == 6.6)
    check("short voiceless tail kept whole", t3.fit_duration(12.0, 5.0, 4.0) == 5.0)
    # slate beats: script timing, but a longer VO is never trimmed mid-sentence
    check("slate keeps script timing", t3.fit_duration(12.0, 0.0, 0.0) == 12.0)
    check("slate holds for longer VO", t3.fit_duration(12.0, 0.0, 14.0) == 14.4)
    check("slate ignores shorter VO", t3.fit_duration(12.0, 0.0, 5.0) == 12.0)


def test_t3_beat_provenance_aggregates(tmp: Path):
    # regression: multi-clip beats credited only clip[0]'s sidecar — later
    # clips' platform/model vanished and their cost dropped out of the leaf
    (tmp / "01-open.mp4").write_bytes(b"x")
    (tmp / "01-open.meta.yaml").write_text("platform: veo\nmodel: veo-3\ncost_usd: 0.40\n")
    (tmp / "01-open-alt1.mp4").write_bytes(b"x")
    (tmp / "01-open-alt1.meta.yaml").write_text("platform: kling\nmodel: kling-2.5\ncost_usd: 0.25\n")
    prov = t3.beat_provenance(t3.find_clips(tmp, 1))
    check("platforms aggregate in clip order", prov["platform"] == "veo+kling")
    check("models aggregate in clip order", prov["model"] == "veo-3+kling-2.5")
    check("cost sums across clips", prov["cost_usd"] == 0.65)
    check("no clips → none/zero provenance",
          t3.beat_provenance([]) == {"platform": "none", "model": "none", "cost_usd": 0.0})


def test_t3_sidecar_errors_named(tmp: Path):
    # regression: a corrupt sidecar died with a raw traceback that never said
    # which file — both parsers must fail loud AND name the offender
    (tmp / "01-vo.json").write_text("{not json")
    try:
        t3.vo_manifest(tmp, 1)
        ok = False
    except SystemExit as e:
        ok = "01-vo.json" in str(e)
    check("bad VO manifest names its file", ok)
    clip = tmp / "02-x.mp4"
    clip.write_bytes(b"x")
    (tmp / "02-x.meta.yaml").write_text("platform: [unclosed\n")
    try:
        t3.clip_provenance(clip)
        ok = False
    except SystemExit as e:
        ok = "02-x.meta.yaml" in str(e)
    check("bad clip meta names its file", ok)


def test_t3_check_clips_dir(tmp: Path):
    # regression: a typo'd --clips path silently rendered an all-slate episode
    # over a published leaf; only an OMITTED --clips may render all-slate
    def aborts(d):
        try:
            t3.check_clips_dir(d)
            return False
        except SystemExit:
            return True
    check("no --clips passes (all-slate path)", not aborts(None))
    check("nonexistent --clips aborts", aborts(tmp / "nope"))
    d = tmp / "trial"
    d.mkdir()
    check("empty --clips aborts", aborts(d))
    (d / "01-vo.mp3").write_bytes(b"x")
    check("audio-only --clips still aborts", aborts(d))
    (d / "01-shot.mp4").write_bytes(b"x")
    check("--clips with footage passes", not aborts(d))


def test_pingpong_loop_seams(tmp: Path):
    """Loop cycle 005: when the slot outruns the footage, render_beat loops
    a palindrome (clip+reversed) so restarts are motion-continuous; footage
    that covers its slot is never touched."""
    calls = []

    def fake_run(cmd, **kw):
        calls.append([str(c) for c in cmd])
        out = Path(cmd[-1])
        if out.suffix == ".mp4":
            out.write_bytes(b"x")
        class R:
            returncode = 0
            stderr = ""
        return R()

    clip = tmp / "01-shot.mp4"
    clip.write_bytes(b"v")
    beat = {"slug": "TEST — 0:00–0:08", "items": []}
    orig_run, orig_vd = t3.subprocess.run, t3.video_duration
    t3.subprocess.run = fake_run
    t3.video_duration = lambda f: 3.0
    try:
        t3.render_beat(beat, 1, 8.0, [clip], tmp)
        looped = any("reverse" in " ".join(c) for c in calls)
        calls.clear()
        t3.render_beat(beat, 2, 2.5, [clip], tmp)
        covered = any("reverse" in " ".join(c) for c in calls)
    finally:
        t3.subprocess.run, t3.video_duration = orig_run, orig_vd
    check("looping beat gets a palindrome", looped)
    check("covered beat is never ping-ponged", not covered)


def main():
    import tempfile
    test_beat_duration_from_timecode()
    test_beat_duration_fallback()
    with tempfile.TemporaryDirectory() as td:
        test_find_clip_naming(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_find_audio_naming(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_pingpong_loop_seams(Path(td))
    test_wrap_never_drops_words()
    test_caption_chunks()
    test_parse_frames_bold_emphasis_in_quote()
    test_parse_frames_bold_line_needs_timing()
    test_build_shots_merges_continuations()
    test_overlay_font_px()
    test_speaker_key_strips_parentheticals()
    test_clean_speech_drops_parentheticals()
    test_node_001_beats_parse()
    test_shot_prompt_extraction()
    test_generate_shots_parsing()
    test_budget_guard()
    test_all_leaf_content_exists()
    test_trials_page_renders()
    test_generate_shots_fence_binding()
    test_generate_shots_effective_duration()
    with tempfile.TemporaryDirectory() as td:
        test_generate_shots_download_atomic(Path(td))
    test_register_leaf_list_separator()
    with tempfile.TemporaryDirectory() as td:
        test_t2_openai_shots_stretch_to_audio(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_t2_final_mux_keeps_faststart(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_t3_find_clips_primary_first(Path(td))
    test_t3_fit_duration()
    with tempfile.TemporaryDirectory() as td:
        test_t3_beat_provenance_aggregates(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_t3_sidecar_errors_named(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_t3_check_clips_dir(Path(td))
    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all pipeline tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
