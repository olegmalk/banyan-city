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
    atomic = t3.caption_chunks("Subject: (he looks at the scavenger for a long moment) …weed warden. Provisional.")
    check("chunker never splits inside a parenthetical",
          all(c.count("(") == c.count(")") for c in atomic))
    sp, dr = t3.split_caption_display("Subject: (he looks at the scavenger for a long moment) …weed warden.")
    check("long parenthetical leaves the caption", sp == "Subject: …weed warden." and
          dr == ["he looks at the scavenger for a long moment"])
    sp2, dr2 = t3.split_caption_display("(no leaf) Greenrest?")
    check("gag parenthetical stays inline", sp2 == "(no leaf) Greenrest?" and dr2 == [])
    sp3, dr3 = t3.split_caption_display("Occupations: farmer — (he writes) — and…")
    check("short pronoun-led direction still leaves the caption",
          "(he writes)" not in sp3 and dr3 == ["he writes"])
    sp4, dr4 = t3.split_caption_display("Fine. (aggressively nothing)")
    check("noun-phrase gag survives", "(aggressively nothing)" in sp4 and dr4 == [])
    # THIS is the caption-safety gate, not qa_episode's pixel heuristic (which
    # cannot separate a black caption box from this show's dark night interiors
    # and is a warning for that reason — see the comment there).
    #
    # Tied to qa_episode's OWN CHROME_BAND rather than a hardcoded 0.20: the two
    # numbers had drifted apart (test allowed 20%, QA measured 22%), so a margin
    # of 20-21% would have passed this test while genuinely intruding on the band
    # the delivery platform covers. A guarantee split across two constants is
    # only a guarantee while they agree.
    # Assert the REAL invariant, not a proxy for it: a block anchored at H-h-M
    # draws its last row at H-M-1, and that row must sit strictly ABOVE the first
    # row of the band. Asserting `M >= band_px` instead let M == band_px pass,
    # which puts two caption rows inside the band.
    import qa_episode as qa
    band_top = int(t3.HEIGHT * (1 - qa.CHROME_BAND))
    caption_bottom = t3.HEIGHT - t3.CAPTION_MARGIN - 1
    check(f"captions clear the platform chrome (last row {caption_bottom} "
          f"< band top {band_top})", caption_bottom < band_top)
    check("caption margin is measured against qa_episode's own band",
          qa.WIDTH == t3.WIDTH and qa.HEIGHT == t3.HEIGHT)
    check("caption box narrower than the action-rail line",
          t3.CAPTION_MAX_W <= t3.WIDTH - 140)
    spans = t3.chunk_spans("One two three. Four five six seven eight nine.", 2.0, 8.0)
    check("spans cover the window", abs(spans[0][1] - 2.0) < 1e-6 and abs(spans[-1][2] - 8.0) < 1e-6)
    check("spans are contiguous",
          all(abs(spans[i][2] - spans[i + 1][1]) < 1e-6 for i in range(len(spans) - 1)))


def test_sd_prompt_fits_clip_and_keeps_the_action():
    """SD1.5's text encoder stops at 77 tokens; shots.md prompts run 113-145.

    Raw, the tail is silently discarded — and since ~45 tokens of style preamble
    come first, what gets discarded is the ACTION. Measured 2026-07-26: beat 1 of
    001 was cut at "two oversized expressive leaves, no [CUT] face — trembles and
    shivers in a gust of wind…", so the renderer never saw the movement, the
    framing or the light.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    from generate_shots import parse_shots
    from sd_prompt import MAX_TOKENS, STYLE_TAG, _token_estimate, compress

    raw = ("Vertical 9:16 macro shot, hand-drawn 2D anime style, low detail: flat "
           "cel-shaded colors, bold clean linework, single shadow tone, simplified "
           "shapes, soft watercolor-wash background, gentle pastel palette. A tiny "
           "sapling trembles in a gust of wind, alone in a vast green field. Peach "
           "morning light. No photorealism, no 3D render look, no heavy texture. "
           "9:16 vertical, no text.")
    out, dropped = compress(raw)
    check("compressed prompt fits CLIP", _token_estimate(out) <= MAX_TOKENS)
    check("the style instruction survives, compactly", STYLE_TAG in out)
    # subject first: leading with style made SD draw the style as the subject
    check("the subject leads, the style trails", out.index("trembles") < out.index(STYLE_TAG))
    # Framing must not merely survive, it must LEAD. As a trailing tag it survived this
    # assertion for weeks and was still ignored by the renderer: every SDXL test beat on
    # 2026-07-26 came back an extreme macro crop, including a "medium shot" of a man that
    # drew a close-up of his chair. "Present in the string" was never the property worth
    # testing — position is what the model actually weights.
    check("the shot type LEADS — framing is not a trailing tag",
          out.lower().startswith("macro shot of "))
    check("THE ACTION SURVIVES", "trembles in a gust of wind" in out)
    check("the negative-prompt tail is dropped", "photorealism" not in out.lower())

    # compress() once anchored the style preamble on "pastel...palette" alone — the first
    # prompt rewritten WITHOUT that phrase (beat 1, 2026-07-27) kept its style sentence
    # and lost its action to the token budget. The preamble must be recognised by what it
    # is, not by one phrase every prompt happened to share until one didn't.
    no_palette = ("Vertical 9:16 medium shot, hand-drawn 2D anime style, low detail: "
                  "flat cel-shaded colors, bold clean linework, minimal shading (single "
                  "shadow tone), simplified shapes. A man hunched at a desk typing fast "
                  "on a glowing keyboard, deep blue night. No photorealism. 9:16 "
                  "vertical, no text.")
    out2, _ = compress(no_palette)
    check("a prompt with no palette phrase keeps its ACTION", "hunched at a desk" in out2)
    check("...and still sheds its style preamble", "hand-drawn" not in out2)

    # Beat 3 of 001 is a terminal resolving a line of output — its subject IS text on a
    # screen — and it rendered as abstract magenta shapes because `text` was negated
    # twice: once by the standard negative, once by shots.md's boilerplate "no text"
    # (which means "no burned-in caption", a render_t3 concern, not an image-model one).
    from sd_prompt import suppressed_negatives
    check("a screen subject un-negates 'text'",
          "text" in suppressed_negatives("Vertical 9:16 close shot. A terminal spinner "
                                         "resolving into a finished line. No text."))
    # Animagine is Danbooru-trained: people are declared by a count tag before anything
    # else. Beat 4 of 001 asks for a man tipping out of his chair and rendered the desk,
    # the chair and the flying papers with NOBODY in them (2026-07-27) — the furniture was
    # right and the man was simply absent. 93 of the genome's 177 prompts open on a person.
    from sd_prompt import count_tag
    STYLE = ("Vertical 9:16 medium shot, flat cel-shaded colors, bold clean linework, "
             "gentle pastel palette. ")
    check("a person in the subject is declared",
          count_tag(STYLE + "A hunched man tips sideways out of his chair.") == "1boy")
    check("an explicit count is honoured, not rounded up to a crowd",
          count_tag(STYLE + "Two patrol guards in armor jog into frame and halt.") == "2others")
    check("gender left unstated stays unstated",
          count_tag(STYLE + "A small round goblin crouches lower in the grass.") == "1other")
    # a possessive is not the subject — these two would put a whole person in a shot
    # that is framed on an object or a pair of hands
    check("a possessive does not summon a person",
          count_tag(STYLE + "A line of script sits on a ledger page beneath a woman's thumb.") == "")
    check("a body-part shot needs no count tag",
          count_tag(STYLE + "A pair of hands hammering on a mechanical keyboard.") == "")
    check("and a shot with nobody in it gets no tag",
          count_tag(STYLE + "An empty dirt road running away toward a pale horizon.") == "")

    check("a mere mention of a monitor does NOT un-negate it",
          suppressed_negatives("Vertical 9:16 close shot. A pair of hands on a keyboard, "
                               "faint monitor glow on his knuckles. No text.") == [])
    check("'no text' is dropped too", "no text" not in out.lower())

    # the regression that mattered most: an over-cautious token estimate once
    # judged a 55-token prompt as too long and dropped EVERY action sentence,
    # leaving only style tags — strictly worse than the truncation it prevented
    check("compression never strips the prompt down to style alone",
          len(out) > len(STYLE_TAG) + 20)

    # and it holds across the whole genome, not just one hand-made case
    worst = 0
    stripped = []
    for node in sorted((REPO / "genomes/sapling/nodes").iterdir()):
        f = node / "shots.md"
        if not f.exists():
            continue
        for s in parse_shots(f.read_text()):
            c, _ = compress(s["prompt"])
            worst = max(worst, _token_estimate(c))
            if len(c) <= len(STYLE_TAG) + 20:
                stripped.append(f"{node.name} beat {s['num']}")
    check(f"every prompt in the genome fits (worst {worst})", worst <= MAX_TOKENS)
    check(f"no prompt is reduced to style alone ({len(stripped)} were)", not stripped)


def test_footage_must_match_its_beat():
    """Footage is found by beat NUMBER, and rewrites renumber beats.

    After the cycle-007 molt, 31 of the season's 35 clips sat on a beat they
    were never made for: 05-realization-hook.mp4 — episode 1's ENDING — would
    have played over new beat 5, the man dying at his desk. Same defect class as
    the orphaned voice takes, caught for audio and missed for video."""
    check("the shot made for this beat is kept",
          t3.footage_matches_beat(Path("05-the-fall.mp4"), "THE FALL — 0:22–0:27"))
    check("an alt take of the right beat is kept",
          t3.footage_matches_beat(Path("05-the-fall-alt1.mp4"), "THE FALL — 0:22–0:27"))
    check("the episode's ending must not play over the death scene",
          not t3.footage_matches_beat(Path("05-realization-hook.mp4"), "THE FALL — 0:22–0:27"))
    check("footage for a scene that became several shots is rejected",
          not t3.footage_matches_beat(Path("04-the-inventory.mp4"), "THE RETRY LOOP — 0:17–0:22"))
    check("punctuation in a beat title does not break the match",
          t3.footage_matches_beat(Path("03-the-tree-watching.mp4"), "THE TREE, WATCHING — 0:10–0:15"))
    check("an unnamed clip is not rejected", t3.footage_matches_beat(Path("07.mp4"), "ANYTHING — 0:00–0:05"))


def test_displayable_action_is_the_trees_voice_only():
    """The tree has no mouth: its answers are stage directions, so those reach
    the screen and own a silent beat. Everything else must not.

    Cycle 006 surfaced them with a blocklist of camera words, which admitted
    nearly every short action — 258 of 271 across the genome — and each one
    took 3.6-4.5s of silence with a caption nobody speaks. That is both founder
    complaints in one mechanism ("no sound for like 3 seconds straight", "the
    script being put as dialogue"). It is an allowlist now."""
    sys.path.insert(0, str(REPO / "pipeline"))
    import direction as d

    keep = [
        "One leaf tilts against the sky.",
        "In dead-still air, one leaf tilts — and holds.",
        "Both leaves tilt at once, emphatically, in still air.",
        "The leaf stays still — then gives the smallest, most reluctant half-tilt.",
    ]
    for s in keep:
        check(f"kept: {s[:34]}", d.displayable_action(s) == s)

    drop = [
        # camera direction: 'close on' was missing from the old blocklist,
        # which only had 'close-up'
        "Close on the sapling's leaf; the scavenger sits blurred behind it.",
        # another character's business, even though it names a branch
        "He holds the fig up beside the bare branch it fell from.",
        # scenery/timelapse, even though a leaf unfurls in it
        "The sun arcs overhead three times as one new leaf unfurls from a bud.",
        # the tree is present but not answering
        "The sapling stands alone in a vast green field.",
        # production language
        "Wide, the desk in profile: the man sways and drops out of frame.",
    ]
    for s in drop:
        check(f"dropped: {s[:34]}", d.displayable_action(s) is None)

    check("a 'Beat.' is a pause, not a caption", d.displayable_action("Beat.") is None)
    # a silent hold past a couple of seconds reads as the video having stalled
    check("hold is capped", d.action_hold("word " * 40) == d.ACTION_MAX_HOLD)
    check("hold has a floor", d.action_hold("One leaf tilts.") >= d.ACTION_MIN_HOLD)


def test_parse_frames_bold_emphasis_in_quote():
    # regression: a quote line opening with bold emphasis ('> **fires**. rest')
    # is a wrapped speech continuation — only a colon marks a new speaker.
    # It MERGES into the line above: markdown hard-wraps, and an unattributed
    # fragment gets cast as the narrator by synth_vo and captioned mid-sentence
    # (found 2026-07-25 — 8 such fragments across the branch nodes).
    md = ("**SCENE — 0:00–0:12**\n"
          "\n"
          "> **ROOT:** the line before\n"
          "> **fires**. rest of the sentence\n")
    items = parse_frames(md)[0]["items"]
    check("wrapped quote merges into one spoken line", len(items) == 1)
    check("the merged line keeps its speaker", items[0][:2] == ("line", "ROOT"))
    check("the merged line keeps both halves",
          items[0][2] == "the line before **fires**. rest of the sentence")

    # ...but a blank line between quotes still means two separate lines
    md2 = ("**SCENE — 0:00–0:12**\n"
           "\n"
           "> **ROOT:** first\n"
           "\n"
           "> **ROOT:** second\n")
    items2 = parse_frames(md2)[0]["items"]
    check("a blank line still separates two quotes", len(items2) == 2)

    # an action paragraph between quotes must not let a later wrap merge across it
    md3 = ("**SCENE — 0:00–0:12**\n"
           "\n"
           "> **ROOT:** spoken\n"
           "He turns away.\n"
           "> orphaned fragment\n")
    items3 = parse_frames(md3)[0]["items"]
    check("an action between quotes blocks the merge",
          [i[0] for i in items3] == ["line", "action", "line"])


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
    # NOT a literal count: story decisions add and remove beats (the founder's
    # "give the tree one want" restored two beats to 001 on 2026-07-26), and a
    # pinned number only ever means "someone edited the script", which is fine.
    # The invariants are the shape and the 1:1 mapping, asserted below.
    check("node 001 is shot-granular, not scene-granular", 15 <= len(beats) <= 30)
    total = sum(t3.beat_duration(b["slug"], b["items"]) for b in beats)

    # cycle 007: the density rule is the fix for "the video doesn't match the
    # script" — assert it on the front door so a scene-sized beat can't return.
    # The runtime is NOT pinned to a literal: since retime_beats.py derives the
    # ranges from measured voice, pinning 88s pinned a number the episode never
    # had (it assembled at 133s). Bound the shape instead, which is what the
    # rule actually says.
    lines = sum(1 for b in beats for i in b["items"] if i[0] == "line")
    check("001 runtime is in the short-form band", 60.0 <= total <= 150.0)
    check("001 cuts at least every 7s", total / len(beats) <= 7.0)
    check("001 carries <=2 lines per shot", lines / len(beats) <= 2.0)
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
    script_beats = len(parse_frames(extract_script(
        (REPO / "genomes/sapling/nodes/001-capability-inventory/node.md").read_text())))
    check("shots.md is 1:1 with the script (the invariant, not a fixed count)",
          len(shots) == script_beats)
    check("beat numbering is 1..N with no gaps",
          [s["num"] for s in shots] == list(range(1, len(shots) + 1)))
    check("prompts nonempty + vertical", all("9:16" in s["prompt"] for s in shots))
    # the t0-b molt shot list (2026-07-25) awaits the regrow era: no beat
    # parses as done until footage for the new skeleton exists
    check("done-status parsed", [s["done"] for s in shots] == [False] * len(shots))


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


def test_marketplace_tools():
    # The request/fulfill loop is the main artifact (D11/D12) — its pure logic
    # deserves the same guardrails as the render pipeline.
    import intake_take  # noqa: F401 — must import without heavy deps
    import make_requests
    import post_motion
    # motion.yaml is the single source of motion direction: every beat covered
    import yaml as _y
    mo = _y.safe_load((REPO / "genomes/sapling/nodes/001-capability-inventory/motion.yaml").read_text())
    mp = mo["motion_prompts"]
    check("motion.yaml covers all 15 beats", sorted(mp) == list(range(1, 16)))
    check("every motion prompt locks the camera",
          all("camera locked" in v for v in mp.values()))
    # post_motion animates ONLY approved pixels — §6 for the deterministic path
    src = (REPO / "pipeline/post_motion.py").read_text()
    check("post_motion imports the approval gate", "from render_local import approved" in src)
    # intake credits the ledger with type: compute (D12 — visible contribution)
    src2 = (REPO / "pipeline/intake_take.py").read_text()
    check("intake writes compute-credit ledger rows", "compute" in src2 and "watering.csv" in src2)
    check("intake records a human screener", "screened_by" in src2)


def test_approval_gate():
    # STEWARDSHIP.md S6 is the founder's most important rule and until 2026-07-27 the
    # code enforcing it had no test at all. The gate must answer the SAME for a node
    # whether it is named by id or in full: it built its glob from the caller's argument
    # string, so `001-capability-inventory` reported "no T0 leaf found" for a node
    # approved that morning. Failing closed is right, but a gate that cries wolf on a
    # real approval is a gate people learn to bypass.
    from render_local import approved
    ok_short, why_short = approved("sapling", "001")
    ok_full, why_full = approved("sapling", "001-capability-inventory")
    check("gate reads an approved node", ok_short)
    check("id and full name agree", (ok_short, why_short) == (ok_full, why_full))
    check("it read a real leaf, not a default", "t0" in why_short)

    # multi-segment ids (004c-n holds 004c-n-t0-a.yaml) must resolve too, and an
    # unapproved node must still refuse — the gate has to be able to say no
    refused, why = approved("sapling", "004c-n")
    check("an unapproved node is refused", not refused)
    check("and the refusal names the leaf it read", "004c-n-t0-a.yaml" in why)


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


def test_kaggle_notebook_cells_parse():
    """The free-render notebook must be syntactically valid — it shipped
    2026-07-19 with a truncated string on its config line and nobody ran it
    until 2026-07-25, when the founder hit SyntaxError on cell 1. Parsed the
    way Jupyter parses (IPython transformer if available, else a magic-aware
    strip), so `%pip` lines and their backslash continuations don't false-alarm."""
    import json
    import re
    nb_path = REPO / "pipeline" / "kaggle" / "render-kaggle.ipynb"
    nb = json.loads(nb_path.read_text())
    try:
        from IPython.core.inputtransformer2 import TransformerManager
        prep = TransformerManager().transform_cell
    except ImportError:
        def prep(src):
            return re.sub(r"^\s*[%!].*(?:\\\n.*)*$", "pass", src, flags=re.M)
    bad = []
    for i, c in enumerate(nb["cells"]):
        if c.get("cell_type") != "code":
            continue
        try:
            compile(prep("".join(c["source"])), f"cell{i}", "exec")
        except SyntaxError as e:
            bad.append(f"cell {i} line {e.lineno}: {e.msg}")
    check("kaggle notebook cells all parse", not bad)
    if bad:
        print("      " + "; ".join(bad))
    # the config cell's repo URL must be a complete, cloneable string
    cfg = "".join(nb["cells"][1]["source"])
    m = re.search(r'REPO_URL\s*=\s*"([^"]*)"', cfg)
    check("REPO_URL is a closed string ending in .git",
          bool(m) and m.group(1).endswith(".git"))


def test_sync_shots_is_idempotent():
    """sync_shots rewrites shot-list headings from the script. Its first
    version mangled them (non-greedy title + optional range meant the title
    stopped at the first word and the remainder was re-appended, giving
    'COLD OPEN (0:00-0:05) OPEN (0:00-0:05)') and the linter could not see it
    because the time range was still present. A synced file must therefore be
    a fixed point, and every heading must contain its range exactly once."""
    import re
    import sync_shots
    for slug in ("001-capability-inventory", "002b-first-citizen",
                 "003b-one-leaf-for-yes", "004-shade"):
        node_dir = REPO / "genomes" / "sapling" / "nodes" / slug
        shots = node_dir / "shots.md"
        if not shots.exists():
            continue
        beats = sync_shots.beats_of(node_dir)
        heads = re.findall(r"^## Beat \d+ — .*$", shots.read_text(), re.M)
        if len(heads) != len(beats):
            continue          # counts are the linter's job, not this test's
        for i, h in enumerate(heads):
            rng = beats[i][1]
            check(f"{slug} beat {i + 1:02d} heading has one range", h.count(rng) == 1)



def test_no_undefined_locals(tmp: Path):
    """Every name a pipeline function READS must be defined somewhere it can see.

    Catches the bug class that cost the founder an evening's render on 2026-08-02:
    reverting the text-encoder eviction deleted the line defining `jobs` and left
    the line using it, so `stage_simple` raised NameError. Nothing caught it —
    py_compile passes (it is valid syntax), the tests did not exercise a GPU path,
    and the failure surfaced on a Windows box ten minutes into a batch, as
    "exit 1", with the real message three files deep in a courier log.

    A revert is a code change and deserves the same scrutiny as the change it
    undoes. This is the cheap static half of that: no GPU, no model, no network.
    """
    import ast
    import builtins

    # module dunders are always present but are not in dir(builtins)
    BUILTIN = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__spec__",
                                    "__package__", "__loader__", "__builtins__"}
    bad = []
    for src_file in sorted((REPO / "pipeline").glob("*.py")):
        tree = ast.parse(src_file.read_text(encoding="utf-8"))
        # MODULE SCOPE ONLY — tree.body, not ast.walk(tree). The first version of
        # this test walked the whole tree, so a local variable inside ANY function
        # counted as globally defined and the check found nothing. Verified by
        # reintroducing the real bug: it passed. A test you have not seen fail is
        # not a test.
        module_level = set()
        for x in tree.body:
            if isinstance(x, (ast.Import, ast.ImportFrom)):
                module_level |= {(al.asname or al.name).split(".")[0] for al in x.names}
            elif isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                module_level.add(x.name)
            elif isinstance(x, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                for n in ast.walk(x):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                        module_level.add(n.id)
            elif isinstance(x, (ast.If, ast.Try, ast.For, ast.While, ast.With)):
                # conditional imports/assignments at module level still count
                for n in ast.walk(x):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                        module_level.add(n.id)
                    elif isinstance(n, (ast.Import, ast.ImportFrom)):
                        module_level |= {(al.asname or al.name).split(".")[0]
                                         for al in n.names}

        # TOP-LEVEL functions only. A nested function legally reads its parent's
        # variables (md_chunk inside render_node_page reads genome_id), and walking
        # into it reports every closure as undefined. Checking the parent covers the
        # child, because the parent's subtree — nested defs included — is where the
        # assignments live.
        for fn in tree.body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # everything this function makes available to itself
            local = set(module_level)
            a = fn.args
            local |= {x.arg for x in a.args + a.posonlyargs + a.kwonlyargs}
            local |= {x.arg for x in (a.vararg, a.kwarg) if x}
            for n in ast.walk(fn):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    local.add(n.id)
                elif isinstance(n, (ast.Import, ast.ImportFrom)):
                    local |= {(al.asname or al.name).split(".")[0] for al in n.names}
                elif isinstance(n, ast.ExceptHandler) and n.name:
                    local.add(n.name)
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    local.add(n.name)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        na = n.args
                        local |= {x.arg for x in na.args + na.posonlyargs + na.kwonlyargs}
                        local |= {x.arg for x in (na.vararg, na.kwarg) if x}
                elif isinstance(n, ast.Lambda):
                    # lambda params are real bindings — `re.sub(..., lambda m: m[1])`
                    na = n.args
                    local |= {x.arg for x in na.args + na.posonlyargs + na.kwonlyargs}
                    local |= {x.arg for x in (na.vararg, na.kwarg) if x}
                elif isinstance(n, ast.Global):
                    local |= set(n.names)
                elif isinstance(n, (ast.comprehension,)):
                    for t2 in ast.walk(n.target):
                        if isinstance(t2, ast.Name):
                            local.add(t2.id)
            used = {n.id for n in ast.walk(fn)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            missing = used - local - BUILTIN
            if missing:
                bad.append(f"{src_file.name}:{fn.name} reads undefined {sorted(missing)}")
    for b in bad:
        print(f"      x  {b}")
    check("no pipeline function reads an undefined name", not bad)


def test_queue_render_params_reach_the_child(tmp: Path):
    """Every render parameter a queue task can set must actually be passed on.

    On 2026-08-03 a guidance 3.0 canary produced a file BYTE-IDENTICAL to the
    guidance 5.0 baseline — same sha256. Not a finding, a flag that never arrived:
    the batch path passed --guidance and the single-beat path did not, so every
    clip in the episode and every canary silently used wan_i2v's default 5.0. The
    steward had already written "guidance did nothing" into a commit message on the
    strength of that non-result. A parameter the queue is allowed to set and the
    renderer silently ignores produces confident wrong conclusions, which is worse
    than a crash.

    Two invariants:
      1. the two render paths honour the SAME parameter set, so neither can drift
      2. every flag either path sends is one wan_i2v actually accepts
    """
    import ast as A
    import re

    # AST, NOT REGEX. Two regex attempts got this wrong in opposite directions —
    # first matching the `--stage encode` call that legitimately samples nothing,
    # then matching only one of the two render calls. The call arguments are a
    # syntax tree; read them as one.
    def sampling_calls(path):
        tree = A.parse(path.read_text(encoding="utf-8"))
        found = []
        for n in A.walk(tree):
            if not (isinstance(n, A.Call) and isinstance(n.func, A.Name)
                    and n.func.id == "_run" and n.args):
                continue
            flags = set()
            for lit in A.walk(n.args[0]):
                if isinstance(lit, A.Constant) and isinstance(lit.value, str) \
                        and lit.value.startswith("--"):
                    flags.add(lit.value[2:])
            # a call that SAMPLES writes a clip: --out (single) or --jobs (batch).
            # `--stage encode` has neither; it takes a prompt and emits embeddings.
            if "stage" in flags and ({"out"} <= flags or {"jobs"} <= flags):
                found.append(flags)
        return found

    flagsets = sampling_calls(REPO / "pipeline" / "video_task.py")
    # THREE, not two: the batch path (--jobs), the single-process path
    # (--stage simple) and the legacy two-process path (--stage render). All three
    # sample, so all three must honour the same parameters.
    check(f"found every wan_i2v sampling call site (got {len(flagsets)})",
          len(flagsets) == 3)

    SAMPLING = {"seconds", "steps", "size", "guidance", "model", "quantise"}
    missing = [f"call {i+1} omits --{w}"
               for i, f in enumerate(flagsets) for w in sorted(SAMPLING) if w not in f]
    for m in missing:
        print(f"      x  {m}")
    check("both render paths pass every sampling parameter", not missing)

    wan_src = (REPO / "pipeline" / "wan_i2v.py").read_text(encoding="utf-8")
    known = set(re.findall(r'add_argument\("--([a-z-]+)"', wan_src))
    unknown = sorted({fl for f in flagsets for fl in f} - known)
    for u in unknown:
        print(f"      x  --{u} is sent but wan_i2v does not define it")
    check("no flag is sent that the renderer does not accept", not unknown)

    # a flag DEFINED but never READ is a trap: it looks like a control and does
    # nothing. --keep-text-encoder was exactly that, and I nearly reached for it to
    # fix a memory ceiling before noticing it was inert.
    read = {x.attr for x in A.walk(A.parse(wan_src)) if isinstance(x, A.Attribute)}
    dead = sorted(f for f in known if f.replace("-", "_") not in read)
    for d in dead:
        print(f"      x  --{d} is defined but never read")
    check("no renderer flag is defined but never read", not dead)


def test_hosted_path_sends_our_negative(tmp: Path):
    """The paid API path must send the same anti-scene-change terms as the local one.

    The founder, on the 2026-08-03 model comparison: "wan 2.7 has the second scene
    for like half a second at the end, which isnt very good." The steward's answer
    was that an API model's prompt cannot be edited. That was WRONG, and the code
    said so: generate_shots sent no negative_prompt at all, while also setting
    `prompt_extend: True` so Model Studio would rewrite our prompt with an LLM
    first. The one engine with nothing suppressing a cut, plus a server-side
    rewriter free to invent narrative, was the one that cut to a second scene.

    Locally these terms cut measured scene-change drift from 40.2 to 8.8. Two
    copies of a list is how they drift apart; this asserts there is one.
    """
    import video_task as vt
    import generate_shots as gs

    check("hosted API_NEG is the local ANTI_SCENE, not a copy",
          gs.API_NEG == vt.ANTI_SCENE)
    check("the local style negative still carries the scene terms",
          vt.ANTI_SCENE in vt.ANTI_STYLE)
    src = (REPO / "pipeline" / "generate_shots.py").read_text(encoding="utf-8")
    check("the API request actually sends negative_prompt",
          '"negative_prompt": API_NEG' in src)
    # prompt_extend rewrites our prompt server-side; SCRIPT-SPEC prompts are not
    # for improving
    check("prompt_extend is off in the API request",
          '"prompt_extend": False' in src and '"prompt_extend": True' not in src)


def test_antistatic_first_signal_wins(tmp: Path):
    """A direction that opens with motion must get the anti-static terms.

    Fixture is the founder's own verdicts, because they are the only calibration
    that has held. On 2026-08-03 he watched beat 1 and said "wan 2.2 basically
    doesnt move at all, literally" — of a clip whose direction the steward had
    written as "his hands type fast ... and then stop abruptly, hands going
    still". WANTS_STILL matched the bare word "still" (the END STATE of the
    motion), suppressed the anti-static terms, and a beat whose entire job is
    typing was told nothing about needing to move. Beat 12 was the same shape and
    came out lowest of all fifteen.

    The rule is now first-signal-wins, which works because these directions are
    written subject-first. Both halves matter: motion-first beats must move, and
    stillness-first beats must NOT be forced (that was the shaking the founder
    reported the day before — "no static at all forces it to move even when not
    needed").
    """
    import video_task as vt

    must_move = {
        "typing that ends still": "his hands type fast over the keyboard and then "
                                  "stop abruptly, hands going still, camera locked",
        "motion scoped by 'else still'": "the bent stem strains and quivers against "
                                         "nothing, everything else still",
        "plain motion": "the new leaf unfurls slowly and settles upright",
    }
    for label, d in must_move.items():
        check(f"antistatic APPLIED: {label}", vt.antistatic_for(d) != "")

    must_not = {
        "stillness first": "the leaf holds almost perfectly still, dust motes settle "
                           "slowly in the sunlight",
        "opens nearly still": "everything nearly still, the clouds drift very slowly",
        "deliberately motionless": "the limp hand stays motionless, one loose paper "
                                   "settles to the floor",
    }
    for label, d in must_not.items():
        check(f"antistatic suppressed: {label}", vt.antistatic_for(d) == "")

    # and the live genome must agree, so a direction edit cannot silently freeze a
    # beat again
    live = vt.motion_directions(REPO / "genomes/sapling/nodes/001-capability-inventory") or {}
    frozen_by_wording = [n for n in (1, 12) if not vt.antistatic_for(live.get(n, ""))]
    check("live beats 1 and 12 are not suppressed by their own wording",
          not frozen_by_wording)


def test_vendored_licence_does_not_launder(tmp: Path):
    """A vendored licence covers the repos it was VERIFIED for and no others.

    Pure logic, no network, because the failure mode is offline: the first
    version of `_vendored_licence` matched on filename resemblance — it split
    "Wan2.2-Lightning" on "-", took the stem "Wan2.2", found it inside
    "Wan2.2-LICENSE.txt" and handed lightx2v's LoRA weights Wan-AI's
    sha256-verified Apache text. Different org, different weights, borrowed
    permission.

    That direction of error is the dangerous one. Missing a licence makes the
    tool say "I cannot tell", which stops a render. MANUFACTURING one makes it
    say "ship it".
    """
    import vet_model as vm

    covered = ("Wan-AI/Wan2.2-TI2V-5B", "Wan-AI/Wan2.2-TI2V-5B-Diffusers",
               "wan-ai/wan2.2-i2v-a14b")
    for repo in covered:
        got = vm._vendored_licence(repo)
        check(f"vendored text covers {repo.split('/')[-1]}", bool(got))

    # every one of these merely LOOKS like the covered names
    for repo in ("lightx2v/Wan2.2-Lightning", "lightx2v/Wan2.2-Distill-Loras",
                 "quanhaol/Wan2.2-TI2V-5B-Turbo", "someone/Wan2.2-Evil",
                 "attacker/Wan-AI-Wan2.2-TI2V-5B"):
        check(f"NOT laundered onto {repo}", vm._vendored_licence(repo) is None)

    # and the map may only name files that exist, or coverage is a fiction
    d = REPO / "licences"
    missing = [f for f in vm.VENDORED_COVERS if not (d / f).is_file()]
    check("every vendored file named in the map exists", not missing)


def test_subprocess_reads_are_utf8(tmp: Path):
    """Any subprocess we read TEXT from must name its encoding.

    `text=True` alone decodes with the *locale* codec. On this Mac that is UTF-8
    and everything works; on the farm's Windows box it is cp1252, which cannot
    represent the em dash or the Chinese terms in Wan's negative prompt that
    live in our own queue file. Worse, the decode happens on subprocess's reader
    THREAD: the UnicodeDecodeError never propagates to the caller, `.stdout` is
    just quietly set to None, and the crash lands later somewhere unrelated
    ('NoneType' object has no attribute 'read', inside pyyaml).

    On 2026-08-02 that cost the 5090 a night: the worker could fetch the queue
    fine and still could not read it, and the traceback pointed at yaml. The
    platform that runs the renders is not the platform that runs these tests, so
    only a static check catches it.
    """
    import ast

    bad = []
    for src_file in sorted((REPO / "pipeline").glob("*.py")):
        tree = ast.parse(src_file.read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("run", "Popen", "check_output")):
                continue
            kw = {k.arg for k in n.keywords if k.arg}
            # text mode is what makes decoding happen at all
            if not (kw & {"text", "universal_newlines", "encoding"}):
                continue
            if "encoding" not in kw:
                bad.append(f"{src_file.name}:{n.lineno} "
                           f"subprocess.{n.func.attr}(text=...) with no encoding=")
    for b in bad:
        print(f"      x  {b}")
    check("every text-mode subprocess read names its encoding", not bad)
    # and the file that actually broke must be readable as UTF-8, not as cp1252
    raw = (REPO / "pipeline" / "farm-queue.yaml").read_bytes()
    try:
        raw.decode("utf-8")
        ok = True
    except UnicodeDecodeError:
        ok = False
    check("the farm queue is valid UTF-8", ok)


def test_licence_gate(tmp: Path):
    """The gate that should have existed on 2026-07-31, when an entire episode
    came within one command of being voiced with F5-TTS — CC BY-NC weights —
    and fish/OpenAudio (research-only) was already on disk. The tree publishes
    CC BY 4.0, so an NC input makes our own licence a lie and an *-SA input
    silently relicenses every node downstream. Neither is visible in the
    finished mp4; only code can catch it.

    Built on a throwaway genome so the assertions are about the RULES, not
    about whatever the real tree happens to contain today.
    """
    import re

    import licence_gate as lg

    # the deny families, however the identifier is dressed up
    check("CC0 ships", lg.classify("CC0")[0] == "allow")
    check("public domain ships", lg.classify("**Public domain**")[0] == "allow")
    check("CC BY 4.0 with credit prose ships",
          lg.classify("**CC BY 4.0** — credit Gravity Sound")[0] == "allow")
    check("Apache/MIT/BSD ship",
          all(lg.classify(x)[0] == "allow" for x in ("Apache-2.0", "MIT", "BSD-3-Clause")))
    check("NC is denied", lg.classify("CC BY-NC 4.0")[0] == "deny")
    check("SA is denied", lg.classify("CC BY-SA 3.0")[0] == "deny")
    # a compound must be judged by its WORST clause: 'cc-by-nc-sa' contains the
    # substring 'cc-by', so an allow-first order would have passed it
    check("NC-SA is denied, not read as CC BY",
          lg.classify("cc-by-nc-sa-4.0")[0] == "deny")
    check("research-only is denied", lg.classify("research use only")[0] == "deny")
    check("ND is denied (a fork tree is all derivatives)",
          lg.classify("CC BY-ND 4.0")[0] == "deny")
    # unclassified is a violation, not a pass — the whole point of an allowlist
    check("a custom EULA is unknown, not allowed",
          lg.classify("Sound Dogs EULA")[0] == "unknown")
    check("a blank licence is unknown", lg.classify("")[0] == "unknown")
    check("a missing licence is unknown", lg.classify(None)[0] == "unknown")

    # engines resolve through the model table; an engine nobody classified fails
    check("chatterbox is MIT", lg.engine_licence("chatterbox-0.5B") == "MIT")
    check("kokoro is Apache", lg.engine_licence("kokoro-82M") == "Apache-2.0")
    check("f5-tts is NC", lg.classify(lg.engine_licence("f5-tts-v1-base"))[0] == "deny")
    check("openaudio/fish are non-commercial",
          all(lg.classify(lg.engine_licence(e))[0] == "deny"
              for e in ("openaudio-s1-mini", "fish-speech-1.5")))
    check("an unlisted engine has no licence on record",
          lg.engine_licence("bark-small") is None)

    # Every model we have decided must NOT ship stays non-allow, whatever its
    # value string says. This exists because on 2026-08-01 the google-flow entry
    # was reworded to EXPLAIN itself — "...cannot pass through a CC BY 4.0
    # offer" — and classify() greps that value for licence identifiers, so the
    # CC-BY allow pattern matched and six Flow files silently became
    # publishable. An explanation became a verdict, and the count fell 21 -> 15
    # with no other change. The prose belongs in MODEL_NOTES (printed, never
    # classified); MODEL_LICENCES values must stay terse and name no other
    # licence. This assertion is the tripwire.
    RESTRICTED = ("pixverse", "kling", "vidu", "stable-video-diffusion",
                  "f5-tts", "openaudio", "fish", "google-flow", "veo",
                  "ltx-video", "lightricks")
    for name in RESTRICTED:
        verdict = lg.classify(lg.MODEL_LICENCES[name])[0]
        check(f"{name} is not publishable ({verdict})", verdict != "allow")
    # and the converse: a restricted value must not merely be unrecognised by
    # accident — it has to actually be in the table
    check("every restricted name is in MODEL_LICENCES",
          all(n in lg.MODEL_LICENCES for n in RESTRICTED))

    def genome(name, leaf=None, sources=None, vo=None, archive_vo=None):
        """A minimal one-node genome under tmp/name, then scan it."""
        node = tmp / name / "genomes" / "g" / "nodes" / "n"
        (node / "leaves").mkdir(parents=True)
        (node / "leaves" / "n-t0-a.yaml").write_text(leaf or "leaf: n-t0-a\n")
        if sources:
            (node / "audio-sources").mkdir()
            (node / "audio-sources" / "SOURCES.md").write_text(sources)
        for sub, body in (("clips", vo), ("clips/vo-archive", archive_vo)):
            if body:
                (node / sub).mkdir(parents=True, exist_ok=True)
                (node / sub / "01-vo.json").write_text(body)
        return lg.scan(tmp / name)

    TABLE = ("| file | what it is | source | licence |\n|---|---|---|---|\n"
             "| `x.ogg` | a thud | somewhere | %s |\n")

    # 1. a clean node: CC0 audio, an MIT-weights engine, licence keys allowlisted
    errors, _ = genome(
        "clean",
        leaf="leaf: n-t0-a\nvoice_engine: chatterbox-0.5B\nsources:\n- licence: CC0\n",
        sources=TABLE % "**CC0**",
        vo='{"engine": "chatterbox-0.5B", "lines": []}')
    check("a publish-safe node passes the gate", errors == [])

    # 2. non-commercial in the sound table — the F5 near-miss in asset form
    errors, _ = genome("nc", sources=TABLE % "CC BY-NC 4.0")
    check("an NC source is a violation", len(errors) == 1)
    check("the NC violation names the file, the licence and the reason",
          "SOURCES.md:3" in errors[0] and "CC BY-NC 4.0" in errors[0]
          and "non-commercial" in errors[0])

    # 3. share-alike: legal to use, fatal to a CC BY tree, so it must NOT pass
    errors, _ = genome("sa", leaf="leaf: n-t0-a\nlicence: CC BY-SA 4.0\n")
    check("a share-alike leaf is a violation", len(errors) == 1)
    check("the SA violation explains the relicensing",
          "share-alike" in errors[0] and "relicense" in errors[0])

    # 4. an engine nobody has classified must be classified, not waved through
    errors, _ = genome("unknown-engine", vo='{"engine": "bark-small", "lines": []}')
    check("an unknown VO engine is a violation", len(errors) == 1)
    check("the unknown-engine violation names engine and remedy",
          "bark-small" in errors[0] and "MODEL_LICENCES" in errors[0])

    # an f5 take kept in vo-archive is provenance (R6), not a shipped asset:
    # advisory only, and it must still be SAID out loud
    errors, advisories = genome("archived", archive_vo='{"engine": "f5-tts-v1-base", "lines": []}')
    check("an archived NC take does not fail CI", errors == [])
    check("but the archived NC take is reported", any("f5-tts" in a for a in advisories))

    def tree(name, files):
        """Scan a throwaway repo whose files are written at EXACTLY the paths
        given. genome() above builds one fixed shape; the coverage rules can
        only be tested by putting an asset where the real tree puts it —
        takes/clips/, a dir nobody hard-coded, an archive."""
        root = tmp / name
        for rel, body in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        return lg.scan(root)

    N = "genomes/g/nodes/n"
    SVD = "stabilityai/stable-video-diffusion-img2vid-xt"

    # ---- hole 1: THE PICTURE WAS UNCHECKED ------------------------------
    # v1 resolved only VO engines through the model table. A clip sidecar's
    # model was compared against a short advisory list and otherwise ignored,
    # so footage from any model shipped unchecked.
    errors, _ = tree("pic-nc", {f"{N}/clips/01-a.meta.yaml":
                                f"platform: kaggle-free-gpu\nmodel: 'still: Lykon/dreamshaper-8 "
                                f"(+IP-Adapter 0.35) | motion: {SVD}'\n"})
    check("an NC video model in a shipping sidecar is a violation", len(errors) == 1)
    check("the picture violation names the model and the NC reason",
          "stable-video-diffusion" in errors[0] and "non-commercial" in errors[0])
    # the compound field is the trap: 'cc-by-nc' was fixed by checking deny
    # first, but 'still: ALLOWED | motion: DENIED' needed the resolver to stop
    # returning one longest match. dreamshaper is allowlisted; SVD is not.
    check("a compound 'still: X | motion: Y' is judged by BOTH models",
          lg.classify(lg.engine_licence(f"still: Lykon/dreamshaper-8 | motion: {SVD}"))[0] == "deny")
    check("model_licences returns every model a field names",
          len(lg.model_licences(f"still: Lykon/dreamshaper-8 | motion: {SVD}")) >= 2)
    errors, _ = tree("pic-unknown", {f"{N}/clips/01-a.meta.yaml":
                                     "platform: kaggle-free-gpu\nmodel: 'motion: SomeCorp/nightreel-2'\n"})
    check("an unclassified video model is a violation, not a silent pass",
          len(errors) == 1 and "MODEL_LICENCES" in errors[0])
    # the picture's version of a deleted key: a sidecar that answers nothing
    errors, _ = tree("pic-empty", {f"{N}/clips/01-a.meta.yaml": "prompt: a mug falls\nseed: 7\n"})
    check("a clip sidecar with no model/platform at all is a violation", len(errors) == 1)
    errors, _ = tree("pic-orphan", {f"{N}/clips/01-a.mp4": "not really an mp4"})
    check("footage with no sidecar and no leaf record is a violation",
          len(errors) == 1 and "no provenance" in errors[0])
    # and no false positive on a slated beat: there is no asset to license
    errors, _ = tree("pic-slate", {f"{N}/leaves/n-t3-a.yaml":
                                   "leaf: n-t3-a\nsources:\n- beat: 1\n  clip: slate (no footage yet)\n"
                                   "  platform: none\n  model: none\n"})
    check("a slated beat needs no licence — there is no asset", errors == [])

    # ---- hole 2: ONE DELETED KEY DEFEATED BOTH LAYERS -------------------
    errors, advisories = tree("vo-gone", {f"{N}/clips/01-vo.json": '{"lines": []}'})
    check("a shipping VO manifest with 'engine' DELETED is a violation", len(errors) == 1)
    check("the deleted-key violation says absence is not a note",
          "no provenance" in errors[0] and "not a note" in errors[0])
    errors, advisories = tree("vo-gone-archived", {f"{N}/clips/vo-archive/01-vo.json": '{"lines": []}'})
    check("the same manifest in vo-archive/ is advisory (not served, not globbed)",
          errors == [] and len(advisories) == 1)
    # the third way to delete a field: keep it, point it at nothing
    errors, _ = tree("vo-pointer", {f"{N}/leaves/n-t3-a.yaml":
                                    "leaf: n-t3-a\nmodel: per-beat — see sources\n"})
    check("'see sources' with no sources is a violation, not a delegation",
          len(errors) == 1 and "points at nothing" in errors[0])
    errors, _ = tree("vo-pointer-ok", {f"{N}/leaves/n-t3-a.yaml":
                                       "leaf: n-t3-a\nmodel: per-beat — see sources\nsources:\n"
                                       "- beat: 1\n  clip: 01-a.mp4\n  platform: alibaba-model-studio\n"})
    check("...and the same pointer over real records still passes", errors == [])

    # ---- hole 3: SCAN COVERAGE WAS ONE HARD-CODED GLOB ------------------
    # <node>/clips/*-vo.json was the only VO path v1 walked, yet render_t3
    # accepts --clips <ANY dir> and build_site publishes takes/clips/ verbatim.
    NC_VO = '{"engine": "f5-tts-v1-base", "lines": []}'
    for i, (label, rel) in enumerate((("takes/clips", f"{N}/takes/clips/01-vo.json"),
                                      ("a dir nobody hard-coded", f"{N}/renders/01-vo.json"),
                                      ("a renamed manifest", f"{N}/clips/take-final.json"))):
        errors, _ = tree(f"cov-vo-{i}", {rel: NC_VO})
        check(f"an NC VO manifest in {label} is a violation", len(errors) == 1)
    errors, _ = tree("cov-takes-sidecar", {f"{N}/takes/clips/01-a.meta.yaml": "platform: pixverse-web\n"})
    check("a sidecar in takes/clips (build_site publishes it verbatim) is scanned",
          len(errors) == 1 and "pixverse" in errors[0])
    errors, advisories = tree("cov-archive", {f"{N}/clips/footage-archive/01-a.meta.yaml":
                                              "platform: pixverse-web\n"})
    check("only an explicit archive lowers scrutiny — and never to silence",
          errors == [] and any("pixverse" in a for a in advisories))
    # audio coverage from both sides: an unlisted file, and a cue with no row
    errors, _ = tree("cov-audio", {f"{N}/audio-sources/SOURCES.md": TABLE % "**CC0**",
                                   f"{N}/audio-sources/y.wav": "RIFF"})
    check("a recorded sound with no row in SOURCES.md is a violation",
          len(errors) == 1 and "no row" in errors[0])
    errors, _ = tree("cov-cue", {f"{N}/audio-sources/SOURCES.md": TABLE % "**CC0**",
                                 f"{N}/audio-sources/x.ogg": "OggS",
                                 f"{N}/clips/sound.yaml":
                                 f"events:\n  - {{beat: 1, sfx: thud, file: {N}/audio-sources/z.ogg}}\n"})
    check("a sound cue naming a file with no licence row is a violation",
          len(errors) == 1 and "z.ogg" in errors[0])

    # ---- hole 4: THE ADVISORY WAS JUSTIFIED ON A FALSE PREMISE ----------
    # v1 called SVD/LTX advisory because they were "already on disk in
    # superseded takes". They are not: 15 of 16 SVD sidecars are in
    # nodes/001-capability-inventory/clips/, the dir render_t3 assembles from.
    # Re-derived from the licences themselves, SVD is non-commercial and LTXV's
    # custom terms are unread — a violation and an unknown, not two advisories.
    check("SVD's weights licence is non-commercial",
          lg.classify(lg.MODEL_LICENCES["stable-video-diffusion"])[0] == "deny")
    check("LTXV's custom terms are unknown, which is a violation not a shrug",
          lg.classify(lg.MODEL_LICENCES["ltx-video"])[0] == "unknown")
    errors, advisories = tree("svd-ships", {f"{N}/clips/01-a.meta.yaml": f"model: {SVD}\n"})
    check("shipping SVD footage FAILS the gate, it is not warned about",
          len(errors) == 1 and advisories == [])
    check("no ADVISORY_MODELS escape hatch survives", not hasattr(lg, "ADVISORY_MODELS"))
    # the same downgrade in ToS form: a free tier that forbids commercial use
    check("a personal-use-only free tier is denied like any NC licence",
          lg.classify(lg.MODEL_LICENCES["pixverse"])[0] == "deny")

    # ---- hole 5: json GOT v1's NARROW TREATMENT WHILE yaml GOT THE SWEEP ----
    # scan_vo_manifest read exactly one key, data['engine']. So hole 1 survived
    # inside the other file format: a manifest could name a non-commercial
    # PICTURE model, or carry an NC licence key outright, and be waved through
    # because its VOICE engine was fine.
    errors, _ = tree("json-model", {f"{N}/clips/01-vo.json":
                                    '{"engine": "chatterbox-0.5B", "model": "PixVerse V6", "lines": []}'})
    check("an NC model beside a publish-safe engine in a manifest is a violation",
          len(errors) == 1 and "pixverse" in errors[0])
    errors, _ = tree("json-licence", {f"{N}/clips/01-vo.json":
                                      '{"engine": "chatterbox-0.5B", "licence": "CC BY-NC 4.0"}'})
    check("a licence key inside a json manifest is read like any other",
          len(errors) == 1 and "non-commercial" in errors[0])
    errors, _ = tree("json-nested", {f"{N}/clips/01-vo.json":
                                     '{"engine": "chatterbox-0.5B", "lines": '
                                     '[{"n": 1, "model": "fish-speech-1.5"}]}'})
    check("provenance nested inside a manifest's lines[] is swept too",
          len(errors) == 1 and "research-only" in errors[0])

    # ---- hole 6: A POINTER SILENCED THE MODEL STANDING NEXT TO IT ---------
    # POINTER matched as a fragment and returned before the model table was
    # consulted, so three appended words bought silence.
    errors, _ = tree("ptr-decorated", {f"{N}/clips/01-a.meta.yaml":
                                       f"platform: kaggle-free-gpu\nmodel: '{SVD} — see sources'\n"})
    check("'see sources' appended to an NC model does not silence it",
          len(errors) == 1 and "stable-video-diffusion" in errors[0])
    check("a pointer is honoured only when the value names no model",
          lg.model_licences("per-beat — see sources") == []
          and lg.model_licences(f"{SVD} — see sources") != [])

    # ---- hole 7: ONLY .mp4 WAS A PICTURE, AND NOTHING WAS A SOUND ---------
    # render_t3's find_audio muxes NN-*.{mp3,wav,m4a,aac,ogg} whether or not a
    # manifest sits beside them, and build_site copies takes/clips/ with
    # iterdir() — so the extension was never a filter on what ships. Not writing
    # the manifest was the cheapest deletion of all: there was no key to delete.
    errors, _ = tree("audio-orphan", {f"{N}/takes/clips/02-vo.mp3": "ID3"})
    check("a shipping VO mp3 with no manifest at all is a violation",
          len(errors) == 1 and "no provenance" in errors[0])
    check("the audio violation names the manifest it wants",
          "NN-vo.json" in errors[0])
    errors, _ = tree("audio-ok", {f"{N}/clips/02-vo.mp3": "ID3",
                                  f"{N}/clips/02-vo.json": '{"engine": "chatterbox-0.5B", "lines": []}'})
    check("...and the same mp3 beside its manifest passes", errors == [])
    errors, _ = tree("container-webm", {f"{N}/clips/01-a.webm": "webm",
                                        f"{N}/takes/clips/02-b.mov": "mov"})
    check("footage renamed .webm/.mov is still footage",
          len(errors) == 2 and all("no provenance" in e for e in errors))
    errors, advisories = tree("audio-archived", {f"{N}/clips/vo-archive/02-vo.mp3": "ID3"})
    check("an archived take is not a shipping asset", errors == [])

    # ---- hole 8: TWO EXTENSIONS WERE THE COVERAGE RULE --------------------
    # '*.yaml' and the literal name '*.meta.yaml' were hard-coded, so saving the
    # same sidecar as .yml escaped both the sweep and the must-declare rule.
    errors, _ = tree("yml-sidecar", {f"{N}/clips/01-a.meta.yml": "platform: pixverse-web\n"})
    check("a sidecar saved .yml is scanned like .yaml",
          len(errors) == 1 and "pixverse" in errors[0])
    errors, _ = tree("json-renamed-empty", {f"{N}/clips/take-final.json": '{"prompt": "a mug falls"}'})
    check("a manifest renamed take-final.json must still declare provenance",
          len(errors) == 1 and "not a note" in errors[0])
    errors, _ = tree("stem-mismatch", {f"{N}/clips/take-final.yml": "prompt: a mug falls\nseed: 7\n",
                                       f"{N}/clips/take-final.mp4": "mp4"})
    check("a record that is not a sidecar does not provenance the clip beside it",
          len(errors) == 1 and "no provenance" in errors[0])
    # hole 2 spelled as an ADDITION rather than a deletion: a bare leaf row
    check_named = {f"{N}/leaves/n-t3-a.yaml":
                   "leaf: n-t3-a\nsources:\n- beat: 1\n  clip: 07-take.mp4\n",
                   f"{N}/clips/07-take.mp4": "mp4"}
    errors, _ = tree("leaf-launder", check_named)
    check("a leaf row with no provenance of its own cannot launder a clip",
          len(errors) == 1 and "no provenance" in errors[0])
    check_named[f"{N}/leaves/n-t3-a.yaml"] += "  platform: alibaba-model-studio\n"
    errors, _ = tree("leaf-launder-ok", check_named)
    check("...and the same row with a real platform does provenance it", errors == [])

    # and the real tree, which is a RATCHET, not a pass/fail. The gate's first
    # full run (2026-08-01) found 46 violations, every one of them pre-existing
    # and every one in node 001 — debt this gate discovered, not debt this test
    # run created. Asserting `errors == []` would have left main red and, via
    # pages.yml, undeployable, which punishes the next honest commit rather than
    # the footage. So the COUNT is asserted instead: the classes stay printed in
    # full, one NEW violation fails the suite, and the number may only go down.
    # Never raise LICENCE_DEBT to make this green.
    from lint_genome import LICENCE_DEBT
    errors, _ = lg.scan(REPO)
    if errors:
        classes = {}
        for e in errors:
            where, _, msg = e.partition(": ")
            key = re.sub(r"'[^']*'", "'…'", msg)[:96]
            classes.setdefault(key, []).append(where)
        print(f"      live tree: {len(errors)} violation(s) in {len(classes)} class(es)"
              f" — pre-existing debt, ratchet {LICENCE_DEBT}")
        for key, wheres in sorted(classes.items(), key=lambda kv: -len(kv[1])):
            print(f"      × {len(wheres):2d}  {key}")
            print(f"            e.g. {wheres[0]}")
    check(f"the live tree adds nothing unpublishable (debt <= {LICENCE_DEBT})",
          len(errors) <= LICENCE_DEBT)
    if len(errors) < LICENCE_DEBT:
        print(f"      ✓ debt fell to {len(errors)} — lower LICENCE_DEBT to match")


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
    test_sync_shots_is_idempotent()
    test_kaggle_notebook_cells_parse()
    test_sd_prompt_fits_clip_and_keeps_the_action()
    test_footage_must_match_its_beat()
    test_displayable_action_is_the_trees_voice_only()
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
    test_marketplace_tools()
    test_approval_gate()
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
    with tempfile.TemporaryDirectory() as td:
        test_licence_gate(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_no_undefined_locals(Path(td))
        test_subprocess_reads_are_utf8(Path(td))
        test_queue_render_params_reach_the_child(Path(td))
        test_hosted_path_sends_our_negative(Path(td))
        test_antistatic_first_signal_wins(Path(td))
        test_vendored_licence_does_not_launder(Path(td))
    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all pipeline tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
