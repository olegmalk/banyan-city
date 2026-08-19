#!/usr/bin/env python3
"""Fast, dependency-light tests for the render pipeline's parsing logic.

No ffmpeg, no chromium, no network — pure functions only, so this runs in CI
next to lint_genome.py. Catches the silent-corruption regressions: a broken
beat-timing regex or clip-naming rule would mis-time or drop episode footage
without any error. Run: python3 pipeline/test_pipeline.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_t2 as t2
import render_t3 as t3
import hold_still as hs
import hold_period as hp
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

    # `text` leaves the negative only for a beat that names the WORDS it wants drawn.
    # A screen NOUN used to be enough, on the reading that beat 3 of 001 "is a terminal
    # resolving a line of output, its subject IS text on a screen". Beat 3 was the only
    # beat in the genome that rule fired on, and on 2026-08-07 all four of its wave
    # candidates came back with gibberish glyphs and anime-girl wallpaper — nothing was
    # left fighting the junk. Screens in this show are abstract glow (beat 1's "one
    # glowing monitor with code", drawn with `text` negated, since 2026-07-27).
    from sd_prompt import beat_negative, suppressed_negatives
    check("naming the actual words un-negates 'text'",
          "text" in suppressed_negatives('Vertical 9:16 close shot. A weathered wooden '
                                         'sign reading "OPEN" beside a dirt road. No text.'))
    check("...capitalised after a reading verb counts too",
          "text" in suppressed_negatives("Vertical 9:16 close shot. A brass plaque that "
                                         "reads NORTH GATE, lantern light. No text."))
    check("a terminal that shows no named words keeps its 'text' protection",
          suppressed_negatives("Vertical 9:16 close shot. A terminal spinner "
                               "resolving into a finished line. No text.") == [])
    # the two live shapes this must not fire on: a person reading, and a person writing
    check("a person reading aloud is not an ask for glyphs",
          suppressed_negatives("Vertical 9:16 medium shot. A robed magistrate reads "
                               "aloud from an open ledger. No text.") == [])
    check("nor is a person writing", suppressed_negatives(
        "Vertical 9:16 close shot. A grey-robed man stops writing mid-stroke, quill "
        "lifted, and looks up. No text.") == [])
    # and the beat this was all for: 001 beat 3, as shots.md carries it
    BEAT3 = next(s["prompt"] for s in parse_shots(
        (REPO / "genomes/sapling/nodes/001-capability-inventory/shots.md").read_text())
        if s["num"] == 3)
    NEG3 = ("photorealistic, 3d render, abstract, text, watermark, signature, "
            "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
            "realistic skin texture")
    check("001 beat 3 keeps 'text' in its negative",
          "text" in beat_negative(NEG3, BEAT3, warn=lambda m: None).split(", "))
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


def test_negative_prompt_cannot_overflow_in_silence():
    """The negative prompt gets the same 77 tokens, and nothing was watching it.

    diffusers warns when a POSITIVE prompt is truncated and says nothing when a
    negative one is, so every still this project has drawn with a long negative
    lost its tail without a word. Measured 2026-08-06 with the real tokenizer: 7
    of the genome's 177 beats are over — 001 beat 7 at 115 tokens, half of it
    thrown away, and 002b beat 1 at 82. On 002b beat 1 the lost words were
    duplicates, which is the only reason nobody noticed for a month.

    Everything here runs on an injected counter, so it needs no tokenizer and
    means the same thing in CI as it does on a render box.
    """
    import re as _re

    sys.path.insert(0, str(REPO / "pipeline"))
    import sd_prompt
    from generate_shots import parse_shots

    fit = getattr(sd_prompt, "fit_negative", None)
    fit_beat = getattr(sd_prompt, "beat_negative", None)
    check("sd_prompt exposes fit_negative()", fit is not None)
    check("sd_prompt exposes beat_negative()", fit_beat is not None)
    if fit is None or fit_beat is None:
        return

    # one token per word, one per comma — exact for this test's made-up terms
    def n(t):
        return len(_re.findall(r"[A-Za-z0-9']+", t)) + t.count(",")

    # 1. under budget: byte-identical and silent. This is the guard on the fix
    # itself — a negative that already fits must reach the model unchanged, or
    # the repair becomes a look change to every frame in the genome.
    said = []
    short = "photorealistic, 3d render, text"
    check("a negative that fits comes back byte-identical",
          fit(short, limit=77, warn=said.append, count=n) == short)
    check("a negative that fits says nothing", said == [])

    # 2. over budget: brought under the limit, and LOUD about it
    house = ", ".join(f"h{i}" for i in range(30))
    said = []
    out = fit(house, beat=", ".join(f"b{i}" for i in range(10)),
              limit=20, warn=said.append, count=n)
    check("an over-budget negative is brought under the limit", n(out) <= 20)
    check("dropping a term is announced", len(said) == 1 and "DROPPED" in said[0])
    check("the announcement names what it dropped", "h29" in said[0])
    # the beat's own terms are why the beat looks like itself; the house list is
    # the same on every frame, so it is the one that gets sacrificed
    check("beat-specific terms outlive the house list", "b9" in out)
    check("the house list is what gets spent", "h29" not in out)

    # 3. duplicates go before anything real does — 002b beat 1's overflow was
    # entirely "text" and "photorealism" arriving twice
    said = []
    out = fit("text, watermark", beat="text", limit=4, warn=said.append, count=n)
    check("a repeated term is removed before a unique one", out.count("text") == 1)
    check("deduplication is announced", "deduplicated" in said[0])
    check("deduplication keeps the unique terms", "watermark" in out)

    # asking for a term twice must not be how you lose it: the surviving copy
    # sits at the house copy's POSITION but carries the beat's PROTECTION, so
    # spending the house list cannot take it (001 beat 7's "no text" did exactly
    # this before the two were separated)
    out = fit("keepme, h1, h2, h3, h4", beat="keepme, b1",
              limit=5, warn=lambda m: None, count=n)
    check("a term the beat also asked for survives the house list being spent",
          "keepme" in out)
    check("the house terms it outranks are gone", "h4" not in out)

    # 4. the real genome, every beat: fits, and whatever already fitted is
    # untouched down to the byte
    NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
           "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
           "realistic skin texture")

    def as_it_was(prompt):
        """The assembly all three renderers used before fit_negative existed."""
        neg = NEG
        for term in sd_prompt.suppressed_negatives(prompt):
            neg = neg.replace(term + ", ", "")
        extra = sd_prompt.extra_negatives(prompt)
        return f"{neg}, {extra}" if extra else neg

    over, changed, worst = [], [], 0
    for node in sorted((REPO / "genomes/sapling/nodes").iterdir()):
        f = node / "shots.md"
        if not f.exists():
            continue
        for s in parse_shots(f.read_text()):
            was = as_it_was(s["prompt"])
            now = fit_beat(NEG, s["prompt"], warn=lambda m: None, count=n)
            worst = max(worst, n(now))
            if n(now) > 77:
                over.append(f"{node.name} beat {s['num']}")
            if n(was) <= 77 and now != was:
                changed.append(f"{node.name} beat {s['num']}")
    check(f"every beat's negative fits (worst {worst})", not over)
    check(f"no beat that already fitted is altered ({len(changed)} were)", not changed)


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
    # WAS: every motion prompt must contain "camera locked". That encoded a belief
    # which turned out to be false, and the test was enforcing it against evidence.
    #
    # Measured 2026-08-03: in image-to-video the INIT FRAME locks the framing, not
    # the phrase. Camera translation stayed at 0.00-0.02px on every variant with
    # "camera locked" removed, against 4.83px on the clip the founder called
    # "aggressively moving". Meanwhile the phrase cost real subject motion — median
    # frame-to-frame went 0.62 -> 0.79 when it came out, and the share of
    # barely-moving frames fell.
    #
    # So the phrase is now kept only where stillness IS the direction (beats 4, 6, 8
    # — the limp hand, the too-blue sky, "the trembling stops"), where it costs
    # nothing and reinforces the intent. Asserting it everywhere would have blocked
    # the founder's own call ("this is actually the best overall, do this kinda
    # thing"). A test may enforce an invariant; it may not outvote a measurement.
    STILL_BEATS = (4, 6, 8)
    check("the deliberately-still beats still lock the camera",
          all("camera locked" in mp[n] for n in STILL_BEATS))
    check("every beat has a direction with some substance",
          all(len(v.split()) >= 8 for v in mp.values()))
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


def test_held_still_is_never_reversed(tmp: Path):
    """Founder, 2026-08-07: "for all of the images that have no animation and
    only zooming, first of all, do not do ping pong." No delivered cut ever hit
    this path — v30 and v31 sized their held clips to their slots — so the test
    guards a latent one: a held clip left at the 2.5s default lands in beat 14's
    13s slot, and the palindrome would answer it by reversing the push. It is
    stretched instead; real footage still gets the palindrome, which is what
    keeps ITS loop seams motion-continuous."""
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

    clip = tmp / "14-worth-staying-in.mp4"
    clip.write_bytes(b"v")
    beat = {"slug": "TEST — 0:00–0:13", "items": []}
    orig_run, orig_vd = t3.subprocess.run, t3.video_duration
    t3.subprocess.run, t3.video_duration = fake_run, lambda f: 2.5
    try:
        t3.render_beat(beat, 14, 13.0, [clip], tmp)          # no sidecar yet
        as_footage = " ".join(" ".join(c) for c in calls)
        calls.clear()
        Path(str(clip) + ".meta.yaml").write_text(
            "model: none — held still + code push-in, no video model ran\n")
        t3.render_beat(beat, 14, 13.0, [clip], tmp)
        as_held = " ".join(" ".join(c) for c in calls)
    finally:
        t3.subprocess.run, t3.video_duration = orig_run, orig_vd
    check("unmarked footage still gets the palindrome", "reverse" in as_footage)
    check("a held still is never reversed", "reverse" not in as_held)
    check("a held still is stretched to its slot", "setpts" in as_held)


def test_held_zoom_is_monotonic_and_moderate():
    """The founder's two conditions on a zoom-only shot, as arithmetic.

    ONE DIRECTION, WHOLE CLIP — asserted over the real beat lengths of episode
    1's held beats, not a convenient one. That half is fixed and has never
    moved: "do not do ping pong" (2026-08-07).

    THE AMOUNT IS THE HALF THAT MOVED, and this test was rewritten when it did.
    It used to bound the RATE and let the total fall out at 2-4%, on the
    reasoning that the held beats run 2.6s to 13.0s so a fixed total drifts the
    short one five times faster. The founder screened that and refused the
    scheme, not just the setting: "zoom speed ladder is just overdoing it.
    simply make the zoom speed moderate." So what is pinned here is now the
    TOTAL, identical on every beat, and the rate is whatever falls out —
    the exact inverse of what this function asserted eight hours earlier.

    Four settings have been screened (6% invisible, 18% too much, 2-4% too
    slow, 12% moderate). A later session with a metric does not get to move it:
    a number agreeing with itself is not a screening.
    """
    ep1_held = [2.583, 3.5, 6.637, 10.524, 12.992]        # beats 5, 4, 7, 10, 14
    for secs in ep1_held + [0.5, 1.0, 60.0]:
        n = max(2, int(24 * secs))
        zs = hs.scale_series(secs, n)
        check(f"{secs}s: scale series never reverses",
              all(b <= a for a, b in zip(zs, zs[1:])))
        check(f"{secs}s: pushes IN and lands on the approved frame",
              zs[0] > zs[-1] and abs(zs[-1] - 1.0) < 1e-9)
        # LINEAR, so the move never creeps up and never parks — both curves that
        # did one of those were rejected by name (see hold_still.EASE_EXP)
        steps = [a - b for a, b in zip(zs, zs[1:])]
        check(f"{secs}s: every frame advances by the same amount",
              max(steps) - min(steps) < 1e-9)
    for secs in ep1_held + [0.5, 60.0]:
        total = hs.zoom_total(secs)
        check(f"{secs}s: travel is the one moderate total, {total * 100:.0f}%",
              abs(total - hs.ZOOM_TOTAL) < 1e-12)
    check("a 2.6s beat and a 13.0s beat are given the SAME move — no ladder",
          hs.zoom_total(2.583) == hs.zoom_total(12.992))
    check(f"and that total is 12%, the screened setting ({hs.ZOOM_TOTAL})",
          abs(hs.ZOOM_TOTAL - 0.12) < 1e-12)
    check("an explicit per-beat override is still honoured",
          hs.zoom_total(6.0, 0.01) == 0.01)


def test_held_sidecar_is_readable_by_every_tool_that_reads_it(tmp: Path):
    """hold_still wrote an honest record that the publish gate could not read.

    THREE tools read this one file and they want different things from the same
    two lines, which is why the strings are pinned by a test and not by a
    comment alone:

      licence_gate    classifies `platform` and `model`. SENTINELS is matched on
                      the WHOLE value (licence_gate.py:466), so the old
                      "none — held still + code push-in, no video model ran" read
                      as an unclassified MODEL NAME — and the one clip in the
                      tree we can prove no model touched was the one the gate
                      refused. "local-cpu (ffmpeg)" resolved to no route at all.
      render_t3       substring-matches "model: none" (render_t3.py:545). A miss
                      means the clip is treated as footage and PING-PONGED —
                      the computed push-in run backwards, which the founder
                      ruled out on 2026-08-07.
      check_invention skips held clips on the same substring
                      (check_invention.py:207). A miss means every held clip is
                      scored for invented content: four confident false
                      positives on the first run.

    A BARE "none" is the only value satisfying all three — appending to it
    breaks the gate, renaming the key breaks the other two — so the explanation
    lives on `note`, which nothing classifies.
    """
    import yaml

    import licence_gate as lg

    clip = tmp / "03-deploy-succeeded.mp4"
    clip.write_bytes(b"v")
    # The still has to EXIST now: sidecar() hashes the bytes it was handed
    # (2026-08-09). A real call always has them — it just fed the file to ffmpeg
    # — and this test was passing a path nothing had ever written.
    still = tmp / "03-deploy-succeeded.png"
    still.write_bytes(b"the deploy-succeeded frame")
    hs.sidecar(clip, still, 3, 2.5, zoom_total_used=0.03)
    text = Path(str(clip) + ".meta.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    check("held platform resolves to our own licence, not to nothing",
          lg.model_licences(data["platform"])
          == [("local-deterministic", "CC-BY-4.0 (our own output)")])
    check("held model is a BARE sentinel",
          lg.normalise(data["model"]) in lg.SENTINELS)
    check("the explanation survives, off the classified key",
          "no video model ran" in str(data.get("note", "")))
    check("render_t3 still reads the clip as held", t3.held_still([clip]))
    check("check_invention's literal is the one hold_still writes",
          '"model: none" in meta.read_text'
          in (REPO / "pipeline" / "check_invention.py").read_text(encoding="utf-8")
          and "model: none" in text)

    # BOTH NAMING CONVENTIONS, from the reader's side. hold_still and
    # video_task write `<name>.mp4.meta.yaml`; render_t3 and 126 tracked records
    # use `<stem>.meta.yaml`. A reader pinned to one shape reports the other as
    # an asset with NO provenance — the loudest verdict on the most careful file.
    check("the full-name shape is found", lg.sidecar_for(clip) is not None)
    stem_only = tmp / "04-stem.mp4"
    stem_only.write_bytes(b"v")
    (tmp / "04-stem.meta.yaml").write_text("model: none\n", encoding="utf-8")
    check("the stem shape is still found", lg.sidecar_for(stem_only) is not None)
    check("an asset with neither has no record, and says so",
          lg.sidecar_for(tmp / "05-nothing.mp4") is None)
    # a VO manifest is a record; a picture reader must not adopt one as a recipe
    (tmp / "06-vo.mp3").write_bytes(b"a")
    (tmp / "06-vo.json").write_text("{}", encoding="utf-8")
    check("the gate sees a VO manifest", lg.sidecar_for(tmp / "06-vo.mp3") is not None)
    check("a picture reader scoped to META_EXT does not",
          lg.sidecar_for(tmp / "06-vo.mp3", lg.META_EXT) is None)

    # THE BARE SHAPE, third naming convention and the one that cost us four
    # stills (2026-08-11). The box's older still harnesses wrote their §7.2
    # record as `<stem>.yaml` with no `.meta` infix — a real render-time
    # receipt that the reader could not see, so a file with perfectly good
    # provenance read as having none and the fail-closed gate would withhold
    # it. Picture callers scoped to META_EXT must see it too: it is a still's
    # record, and they are the ones who read stills.
    bare = tmp / "07-the-footnote-s0.png"
    bare.write_bytes(b"p")
    (tmp / "07-the-footnote-s0.yaml").write_text(
        "platform: local-gpu (rtx5090)\nmodel: cagliostrolab/animagine-xl-3.1\n",
        encoding="utf-8")
    check("the bare stem shape is found", lg.sidecar_for(bare) is not None)
    check("and by a picture reader scoped to META_EXT",
          lg.sidecar_for(bare, lg.META_EXT) is not None)
    check("a json-only caller still gets no yaml",
          lg.sidecar_for(bare, (".json",)) is None)

    # AND THE COLLISION THAT SHAPE OPENS. `<stem>.yaml` is a name anything can
    # have, and every one of the 82 node leaves already has it beside the mp4
    # it describes. A leaf is a document the gate walks on its own, not a
    # sidecar; adopting one here would have re-tiered 32 published clips on a
    # lookup change meant to find four stills. Same for any neighbour yaml that
    # never says what made the file — it cannot answer the gate, so letting it
    # in would only cost us the honest "no record" finding.
    leafish = tmp / "08-t3-a.mp4"
    leafish.write_bytes(b"v")
    (tmp / "08-t3-a.yaml").write_text(
        "leaf: 08-t3-a\ntier: T3\ncontent: 08-t3-a.mp4\nmodel: per-beat\n",
        encoding="utf-8")
    check("a leaf sitting beside its own mp4 is not adopted as its sidecar",
          lg.sidecar_for(leafish) is None)
    silent = tmp / "09-notes.png"
    silent.write_bytes(b"p")
    (tmp / "09-notes.yaml").write_text("title: crop notes\nby: steward\n",
                                       encoding="utf-8")
    check("a same-stem yaml naming no engine is not a record",
          lg.sidecar_for(silent) is None)
    # Most specific still wins, exactly as it does between the two .meta shapes.
    (tmp / "09-notes.meta.yaml").write_text("model: none\n", encoding="utf-8")
    check("an explicit .meta.yaml outranks a bare neighbour",
          lg.sidecar_for(silent) == tmp / "09-notes.meta.yaml")

    # END TO END, through the real gate, in a root it actually walks: the clip
    # is only clean if the record classifies AND the reader can find it.
    root = tmp / "repo"
    (root / "genomes").mkdir(parents=True)
    (root / "cuts").mkdir(parents=True)
    (root / "cuts" / clip.name).write_bytes(b"v")
    (root / "cuts" / (clip.name + ".meta.yaml")).write_text(text, encoding="utf-8")
    errors, _ = lg.scan(root)
    check("a held still passes the licence gate end to end", errors == [])


def test_every_sidecar_reader_finds_both_shapes(tmp: Path):
    """The last three readers pinned to one of the two naming conventions.

    The tree has always written records under two names — `06-x.meta.yaml`
    (render_t3, intake_take, 126 tracked records) and `06-x.mp4.meta.yaml`
    (hold_still, video_task, the farm worker, and every writer added since).
    Neither is wrong, so the fix is always in the READER: renaming files would
    break the held-still detectors and throw away each record's git trail.
    lg.sidecar_for tries both; build_site took it at four call sites and
    publishable() at a fifth. These are the rest, and each one costs something
    different when it misses:

      shot board      the crowd-facing surface — a take plays with no engine
                      credit and no "exact settings used" link, which is §7.2
                      unmet in public rather than in a log.
      render_t3       clip_provenance's {} is not a GAP in the episode leaf, it
                      is a wrong answer in it: beat_provenance turns the miss
                      into a published claim that no model rendered the beat.
      build_comparison  the inverse pinning, full-name only — a stem-shape
                      record reads as "no sidecar, numbers blank", a row of gap
                      marks over a render that measured itself.

    WIDENING, NOT SWAPPING, is the whole assertion here: every case below checks
    the shape the reader already handled as well as the one it could not see.
    """
    import build_comparison as bc
    import build_shotboard as bsb

    REC = ("platform: local-gpu\nmodel: Wan2.2-TI2V-5B\n"
           "contributed_by: someone\ncost_usd: 0\n")
    full = tmp / "01-the-keyboard.HAILUO.mp4"
    full.write_bytes(b"v")
    (tmp / "01-the-keyboard.HAILUO.mp4.meta.yaml").write_text(REC, encoding="utf-8")
    stem = tmp / "02-the-keyboard.HAILUO.mp4"
    stem.write_bytes(b"v")
    (tmp / "02-the-keyboard.HAILUO.meta.yaml").write_text(REC, encoding="utf-8")
    bare = tmp / "03-nobody-filed-one.HAILUO.mp4"
    bare.write_bytes(b"v")

    # THE SHOT BOARD, both the credit line and the receipt link beside it.
    check("the board reads a full-name record",
          bsb.take_meta(full).get("contributed_by") == "someone")
    check("...and still reads the stem shape",
          bsb.take_meta(stem).get("contributed_by") == "someone")
    check("a take with no record says nothing rather than guessing",
          bsb.take_meta(bare) == {})
    check("the board links the full-name receipt",
          "01-the-keyboard.HAILUO.mp4.meta.yaml"
          in bsb.take_cell(full, "media", "", False))
    check("...and the stem-shape one",
          "02-the-keyboard.HAILUO.meta.yaml"
          in bsb.take_cell(stem, "media", "", False))
    check("and offers no receipt at all over a 404",
          "exact settings used" not in bsb.take_cell(bare, "media", "", False))

    # RENDER_T3, at the level the leaf is actually written from.
    check("the leaf credits a full-name record",
          t3.beat_provenance([full])["model"] == "Wan2.2-TI2V-5B")
    check("...and a stem-shape one",
          t3.beat_provenance([stem])["model"] == "Wan2.2-TI2V-5B")
    check("a clip with no record is the only one that reads as 'none'",
          t3.beat_provenance([bare])["model"] == "none")
    # held_still is the same lookup one function over; the full-name direction is
    # pinned end to end in test_held_sidecar_is_readable_by_every_tool_that_reads_it
    held = tmp / "04-held.mp4"
    held.write_bytes(b"v")
    (tmp / "04-held.meta.yaml").write_text("model: none\n", encoding="utf-8")
    check("a held clip filed under the stem shape is still never reversed",
          t3.held_still([held]))

    # THE COMPARISON PAGE — the inverse, so the stem shape is the new one here.
    check("the comparison page reads a stem-shape record",
          (bc.load_sidecar(stem) or {}).get("model") == "Wan2.2-TI2V-5B")
    check("...and still reads the shape it was written for",
          (bc.load_sidecar(full) or {}).get("model") == "Wan2.2-TI2V-5B")
    check("no record stays None — a blank recipe would print as measured",
          bc.load_sidecar(bare) is None)

    # check_invention exposes no helper — its skip is inline in the sweep — so it
    # is pinned on the source, the way its "model: none" literal already is.
    check("check_invention locates held records with the tolerant reader",
          "lg.sidecar_for(p, lg.META_EXT)"
          in (REPO / "pipeline" / "check_invention.py").read_text(encoding="utf-8"))


def test_farm_still_sidecar_records_what_actually_ran(tmp: Path):
    """The farm worker's VIDEO path writes provenance; its STILLS path wrote none.

    video_task.write_sidecar exists because clips were landing on the courier
    branch as bare mp4s with the model recorded nowhere. The frames beside them
    were landing exactly the same way and nobody noticed for a week, because a
    still looks self-explanatory in a way a clip does not. It is not: a bake-off
    task can name ANY open model in `model:`, so the one fact you cannot recover
    from a png on farm-results-<name> is which model drew it.

    Four things this pins, each of which was unrecoverable:
      1. the model ACTUALLY LOADED — task['model'] when the task overrides the
         house model, the house model when it does not. Recording the default
         while a bake-off ran would be worse than recording nothing.
      2. the POST-FIT prompt. sd_prompt.compress() rewrites the shot text to fit
         CLIP's 77 tokens and the model sees the compressed string; shots.md is
         not a record of what was asked for. §7.2 names prompt explicitly.
      3. the licence, resolved THROUGH licence_gate — so the record can never
         disagree with the tool that will later judge it, and an unclassified
         model reads UNVERIFIED instead of a hopeful allow.
      4. seed, size, steps, task id, $0.
    """
    import yaml

    import farm_worker as fw
    import licence_gate as lg
    from sd_prompt import compress

    long_shot = ("a wide low-angle shot of a young sapling in a server room, "
                 "cold blue rack light behind it: cables on the floor, dust in "
                 "the air, one warm desk lamp off to the left, detailed "
                 "cinematic anime, 9:16, the whole frame held very still")
    ptext, _ = compress(long_shot)
    task = {"id": "r42", "worker": "dads-msi", "seeds": 4, "steps": 40}

    text = fw.still_sidecar("cagliostrolab/animagine-xl-3.1", task, 7, 21007,
                            "832x1216", 40, ptext, "photorealistic, 3d render")
    d = yaml.safe_load(text)
    check("the still sidecar is valid yaml", isinstance(d, dict))
    check("platform is the generic local-gpu form the gate classifies",
          lg.model_licences(d["platform"]) and d["platform"].startswith("local-gpu"))
    check("the model that drew it is named", d["model"] == "cagliostrolab/animagine-xl-3.1")
    check("its licence is the gate's own verdict, not a guess",
          d["model_licence"] == lg.engine_licence("cagliostrolab/animagine-xl-3.1"))
    check("the seed is recorded", d["seed"] == 21007)
    check("and which of the batch's seeds it was", d["seeds_in_batch"] == 4)
    for k, v in (("shot_beat", 7), ("size", "832x1216"), ("steps", 40),
                 ("task", "r42"), ("cost_usd", 0)):
        check(f"{k} is recorded", d[k] == v)
    check("the POST-FIT prompt is recorded, not the shots.md text",
          d["prompt"] == ptext and d["prompt"] != long_shot)
    check("the negative is recorded too", d["negative"] == "photorealistic, 3d render")
    check("a txt2img frame claims no img2img settings",
          "strength" not in d and "init" not in d)

    # WHICH BOX RENDERED IT, and the two answers that are not it. 2026-08-08.
    #
    # `002b-b01-5b.mp4` reached the founder's morning checklist saying
    # `platform: local-gpu (MSI)` over a log reporting a 25.7GB card. Nothing
    # guessed: platform.node() returns "MSI" on BOTH Windows boxes, so the
    # sidecar faithfully recorded a value that cannot separate a 24GiB 5090 from
    # a 12GB 5070 Ti. The other wrong answer is the task's `worker:` field, which
    # is a ROUTING constraint whose legal values include the wildcard `any` — a
    # clip is not rendered by "any". video_task.worker_id() asks the card.
    import video_task as V
    check("the card names itself, and the handle rides along",
          V.worker_id({"worker": "rtx5090"}, gpu="NVIDIA GeForce RTX 5090 Laptop GPU")
          == "NVIDIA GeForce RTX 5090 Laptop GPU @ rtx5090")
    check("two boxes sharing a hostname are told apart by the card",
          V.worker_id({"worker": "MSI"}, gpu="NVIDIA GeForce RTX 5090 Laptop GPU")
          != V.worker_id({"worker": "MSI"}, gpu="NVIDIA GeForce RTX 5070 Ti Laptop GPU"))
    check("the routing wildcard never becomes a machine",
          "any" not in V.worker_id({"worker": "any"}, gpu="RTX 5090"))
    check("...nor does the old 'unknown' placeholder",
          "unknown" not in V.worker_id({"worker": "unknown"}, gpu="RTX 5090"))
    check("with no card to ask, an explicitly named box is still honoured",
          V.worker_id({"worker": "rtx5090"}, gpu="") == "rtx5090")
    check("and the platform stays the generic form the licence gate classifies",
          lg.model_licences(f"local-gpu ({V.worker_id({}, gpu='RTX 5090')})"))
    # the sidecar farm_worker writes goes through the same function, so a still
    # and a clip from one night cannot disagree about which machine made them
    still_task = dict(task, worker="rtx5090")
    check("the still sidecar's platform routes through the same worker_id",
          yaml.safe_load(fw.still_sidecar("cagliostrolab/animagine-xl-3.1",
                                          still_task, 7, 1, "8x8", 4, "p", "n"))["platform"]
          == f"local-gpu ({V.worker_id(still_task)})")

    # A BAKE-OFF NAMES ITS OWN MODEL. Recording the house default while another
    # model rendered is the one failure worse than recording nothing at all.
    other = fw.still_sidecar("stabilityai/sdxl-turbo", dict(task, model="x"), 7,
                             1, "832x1216", 4, "p", "n")
    od = yaml.safe_load(other)
    check("a bake-off's model is what gets written",
          od["model"] == "stabilityai/sdxl-turbo")
    check("an unclassified model is UNVERIFIED, never a hopeful allow",
          od["model_licence"].startswith("UNVERIFIED"))

    # A prompt full of colons, quotes and em-dashes is the normal case here, and
    # an inline scalar would need escaping rules we would get wrong once.
    nasty = 'a shot: "quoted", with — dashes, and a trailing colon:'
    nd = yaml.safe_load(fw.still_sidecar("m", task, 1, 1, "8x8", 1, nasty, ""))
    check("a prompt with colons and quotes survives the round trip",
          nd["prompt"] == nasty)

    img2img = yaml.safe_load(fw.still_sidecar(
        "m", task, 1, 1, "8x8", 1, "p", "n",
        init="genomes/sapling/nodes/001-capability-inventory/stills/07-x.png",
        strength=0.45))
    check("an img2img frame records what it was drawn from", img2img["strength"] == 0.45
          and img2img["init"].endswith("07-x.png"))

    # THE RECORD MUST BE FINDABLE, and under the convention the readers use.
    png = tmp / "r42-07-zero-0-moving-parts-s0.png"
    png.write_bytes(b"p")
    Path(str(png) + ".meta.yaml").write_text(text, encoding="utf-8")
    check("licence_gate finds the still's record beside it",
          lg.sidecar_for(png) == Path(str(png) + ".meta.yaml"))

    # WRITTEN PER IMAGE, INSIDE THE LOOP — not after the batch. The courier
    # branch's whole point is that a machine which dies mid-run is still
    # readable, and a sidecar pass at the end of the batch loses every frame the
    # run did finish. This is the regression the test exists for: the stills path
    # shipped for a week with no sidecar call in it at all.
    src = (REPO / "pipeline" / "farm_worker.py").read_text(encoding="utf-8")
    loop = src.split("for k in range(int(task.get(\"seeds\", 4))):")[1].split("\ndef ")[0]
    check("the stills loop writes a sidecar for every frame it saves",
          "still_sidecar(" in loop and loop.index("img.save(") < loop.index("still_sidecar("))


def test_bench_sidecar_names_the_beat_or_omits_it(tmp: Path):
    """A bench clip records the beat it IS — and records nothing when nobody said.

    review/ep2-b01/wan5b-b01.mp4 reached the founder's morning checklist saying
    `shot_beat: 0` over the COLD OPEN, and so did cuts/checklist/002b-b01-5b.mp4.
    Nothing guessed: wan_i2v's two bench write_sidecar calls passed beat=0 as a
    LITERAL, a throughput measurement having no beat to give. Honest for a bench
    row, wrong the moment the clip is screened as a beat — and it is the field
    build_shotboard and the review page key off to place a clip under its beat, so
    both files needed a hand-written correction block for a fact the renderer
    could have been told (queue id wan-bench-sidecar-beat-1786190640).

    Three things, and the last is the one a --beat flag can newly break:
      1. a beat that IS known is published
      2. an unknown beat is ABSENT, not 0. A placeholder 0 is indistinguishable
         from a real beat to every reader; an absent field reads as "not
         recorded", which is true. Same drop-a-None convention as _yaml_map.
      3. the published SEED does not move. write_sidecar publishes seed_base +
         beat, so a caller that names a beat and hands over the seed itself would
         record a draw that never happened.
    """
    import ast as A
    import yaml

    import video_task as V
    import wan_i2v as W

    def side(beat, seed=20260806):
        clip = tmp / f"bench-b{beat}.mp4"
        clip.write_bytes(b"v")
        V.write_sidecar(clip, "ti2v-5b",
                        {"worker": "rtx5090", "guidance": 5.0,
                         "seed_base": W.sidecar_seed_base(seed, beat),
                         "id": "b01-wan5b-6s/production/b1/s20260806"},
                        beat=beat, seconds=6.042, steps=14, size="704x1280")
        text = Path(str(clip) + ".meta.yaml").read_text(encoding="utf-8")
        return text, yaml.safe_load(text)

    text, d = side(1)
    check("a bench sidecar publishes the beat it was given", d["shot_beat"] == 1)
    check("and still the seed that was actually drawn, not seed+beat",
          d["seed"] == 20260806)

    text, d = side(None)
    check("an unknown beat is an ABSENT field, not a guessed 0",
          "shot_beat" not in text and "shot_beat" not in d)
    check("and it is not a null either — nothing was recorded as nothing",
          "shot_beat" not in yaml.safe_load(text))
    check("an unknown beat moves no seed", d["seed"] == 20260806)
    check("the rest of the record is unchanged by the missing field",
          d["size"] == "704x1280" and d["steps"] == 14 and d["cost_usd"] == 0)

    # WHOSE BEAT WINS. A jobs file is N different beats; one CLI number is not
    # right for all of them, and the old defect one size up would be a sweep where
    # every clip claims beat 1.
    check("a --jobs entry's own beat beats the command line",
          W.bench_beat(3, {"beat": 7}) == 7)
    check("the command line covers a job that names none",
          W.bench_beat(3, {"init": "x.png"}) == 3)
    check("nobody saying is None, on either path",
          W.bench_beat(None) is None and W.bench_beat(None, {"init": "x"}) is None)
    check("a beat someone typed is honoured verbatim, 0 included",
          W.bench_beat(0) == 0 and W.bench_beat("11", None) == 11)
    check("the seed base is the seed minus the beat, and unmoved when unknown",
          W.sidecar_seed_base(20260806, 6) == 20260800
          and W.sidecar_seed_base(20260806, None) == 20260806)

    # STRUCTURAL, because the two call sites live in a stage function that needs
    # torch and diffusers and cannot run here — the same reason the flag tests in
    # this file are AST. What is pinned is that neither one hard-codes the beat
    # again, and that both compensate the seed they publish.
    src = (REPO / "pipeline" / "wan_i2v.py").read_text(encoding="utf-8")
    calls = [n for n in A.walk(A.parse(src))
             if isinstance(n, A.Call) and isinstance(n.func, A.Attribute)
             and n.func.attr == "write_sidecar"]
    check(f"both wan bench sidecar call sites found (got {len(calls)})",
          len(calls) == 2)
    hard = [A.unparse(k.value) for c in calls for k in c.keywords
            if k.arg == "beat" and isinstance(k.value, A.Constant)]
    for h in hard:
        print(f"      x  a bench call site passes beat={h} as a literal")
    check("neither bench call site hard-codes the beat", not hard)
    bases = [n for n in A.walk(A.parse(src)) if isinstance(n, A.Call)
             and isinstance(n.func, A.Name) and n.func.id == "sidecar_seed_base"]
    check("and both hand over a base that compensates for it", len(bases) == 2)


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


def _argparse_gaps(src: str, filename: str = "<src>"):
    """Attributes read off a parsed-args namespace that no add_argument declares.

    PURE, and AST-only on purpose: wan_i2v and ltx_i2v both reach for torch and
    diffusers, neither of which exists on this machine or in CI, so the module is
    parsed and never imported.

    Returns (namespace variable names, [(attr, first line that reads it), ...]).

    Three things count as declaring an attribute, because all three really do put
    one on the namespace: an `add_argument` (resolved by argparse's own dest rule
    — explicit `dest=`, else the first long option, else the first short one, with
    dashes to underscores), a `set_defaults(x=...)`, and a plain `a.x = ...`
    assignment. `getattr(a, "x", default)` is deliberately NOT counted as a read:
    it carries its own default and cannot raise, which is exactly why wan_i2v uses
    that form in the helpers a non-batch caller can reach.
    """
    import ast

    tree = ast.parse(src, filename=filename)

    # 1. The namespace: whatever `<x> = <parser>.parse_args()` binds. Matched by
    #    NAME across the whole module, because the parse happens in main() and
    #    every read happens in a stage function that took it as a parameter — both
    #    renderers call it `a`, and that convention is the thing being checked.
    ns = set()
    for n in ast.walk(tree):
        if (isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Attribute)
                and n.value.func.attr in ("parse_args", "parse_known_args")):
            for t in n.targets:
                for el in (t.elts if isinstance(t, ast.Tuple) else [t]):
                    if isinstance(el, ast.Name):
                        ns.add(el.id)

    declared = set()
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)):
            continue
        if n.func.attr == "set_defaults":
            declared |= {kw.arg for kw in n.keywords if kw.arg}
            continue
        if n.func.attr != "add_argument":
            continue
        dest = next((kw.value.value for kw in n.keywords if kw.arg == "dest"
                     and isinstance(kw.value, ast.Constant)), None)
        flags = [x.value for x in n.args
                 if isinstance(x, ast.Constant) and isinstance(x.value, str)]
        if dest is None and flags:
            longs = [f for f in flags if f.startswith("--")]
            dest = (longs[0][2:] if longs else flags[0].lstrip("-")).replace("-", "_")
        if dest:
            declared.add(dest)

    # 2. An assignment onto the namespace defines it as surely as a flag does —
    #    `a.model = MODELS.get(a.model, a.model)` is real, and calling it missing
    #    would be a false alarm.
    for n in ast.walk(tree):
        if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id in ns and isinstance(n.ctx, ast.Store)):
            declared.add(n.attr)

    missing = {}
    for n in ast.walk(tree):
        if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id in ns and isinstance(n.ctx, ast.Load)
                and n.attr not in declared):
            missing.setdefault(n.attr, n.lineno)
    return ns, sorted(missing.items(), key=lambda kv: kv[1])


def test_argparse_declares_every_flag_it_reads():
    """Every flag a renderer READS must be one its own parser DECLARES.

    The regression this exists for shipped on 2026-08-04 in fab4632: the --batch
    BODY landed in ltx_i2v.py — embeds expansion, per-slot generators, the
    stage-1 batch-shape assertion — and the four argparse lines that declare
    --batch/--mode/--bench-jsonl/--bench-label did not. `batch = max(1,
    int(a.batch))` then raised AttributeError on EVERY `--stage render`, at the
    defaults, before a weight was read. The LTX renderer could not render at all
    for a day.

    Nothing here could have caught it. py_compile passes — it is valid syntax.
    test_no_undefined_locals passes — `a` is defined, it is the ATTRIBUTE that is
    not. And no test touched either renderer's CLI, which is the actual gap: the
    box they run on is not this machine, so the first thing that executes them is
    a paid, hour-long render on a GPU nobody is sitting at.

    Verified by running it against `git show fab4632:pipeline/ltx_i2v.py`, where
    it reports `a.batch` at line 401 and fails. A test you have not seen fail is
    not a test.

    `xplat_fidelity.py` is not a renderer and joined this list on 2026-08-05 for
    the same structural reason: it was promoted out of `bench-platform/` into a
    tool other people will call, and it runs on measurement artifacts that take
    ffmpeg minutes to reach — so a namespace typo there also surfaces late rather
    than at parse time. Any pipeline script that binds `parse_args()` belongs
    here; the check costs one AST walk.
    """
    for name in ("wan_i2v.py", "ltx_i2v.py", "xplat_fidelity.py"):
        src = (REPO / "pipeline" / name).read_text(encoding="utf-8")
        ns, missing = _argparse_gaps(src, name)
        check(f"{name} binds a parsed-args namespace this test can follow", bool(ns))
        for attr, line in missing:
            print(f"      x  {name}:{line} reads a.{attr} — no add_argument "
                  f"declares --{attr.replace('_', '-')}")
        check(f"{name} declares every flag it reads", not missing)


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


def test_probe_beat_sends_the_files_and_the_whole_recipe(tmp: Path):
    """A one-beat probe must pass every sampling parameter, and pass the two
    strings it READ rather than any it re-derived.

    Same invariant as the test above, on the third renderer entry point. It is
    here because the probe path is the one used for single-beat re-renders — the
    runs whose whole purpose is that ONE input changed — and a recipe field that
    silently reverts to a default turns "only the negative changed" into a claim
    nobody can check afterwards.

    The utf-8 half is the other reason: the negative carries Wan's Chinese
    anti-static terms, and the run is fired over a cp1252 console. If the string
    that reaches argv is not byte-for-byte the file's, the clip still renders and
    the corruption is invisible in the output.
    """
    import re

    sys.path.insert(0, str(REPO / "pipeline"))
    import probe_beat as pb

    neg = "splitting leaf, 静态, 静止不动的画面, frozen frame"
    cmd = pb.build_cmd("py", "wan.py", "in.png", "out.mp4", "2D anime. x", neg,
                       20260816, "e.pt", steps=14, guidance=5.0, seconds=2.5)
    check("probe passes the negative byte-for-byte", neg in cmd)
    check("probe passes the seed it was given", "20260816" in cmd)

    flags = {c[2:] for c in cmd if c.startswith("--")}
    SAMPLING = {"seconds", "steps", "size", "guidance", "model", "quantise", "seed"}
    missing = sorted(SAMPLING - flags)
    for m in missing:
        print(f"      x  probe omits --{m}")
    check("the probe path passes every sampling parameter", not missing)
    check("the probe path suppresses wan_i2v's global shake terms",
          "no-shake-neg" in flags)

    wan_src = (REPO / "pipeline" / "wan_i2v.py").read_text(encoding="utf-8")
    known = set(re.findall(r'add_argument\("--([a-z-]+)"', wan_src))
    unknown = sorted(flags - known)
    for u in unknown:
        print(f"      x  --{u} is sent but wan_i2v does not define it")
    check("the probe sends no flag the renderer does not accept", not unknown)

    # the recipe is not only flags: video_task hands every render an environment,
    # and each variable in it is there because its absence once cost a run
    vt_src = (REPO / "pipeline" / "video_task.py").read_text(encoding="utf-8")
    vt_env = set(re.findall(r'"(PYTHON[A-Z0-9_]*|PYTORCH_[A-Z0-9_]*|HF_HUB_[A-Z0-9_]*)":',
                            vt_src))
    missing_env = sorted(vt_env - set(pb.RENDER_ENV))
    for m in missing_env:
        print(f"      x  the probe does not set {m}")
    check(f"the probe hands the render video_task's environment ({len(vt_env)} vars)",
          vt_env and not missing_env)

    # the sidecar is the other half: --stage simple writes none, which is why
    # beat 11's seed had to be dug out of a commit whose blobs are gone
    side = pb.sidecar_text("Wan-AI/Wan2.2-TI2V-5B-Diffusers", "Apache-2.0",
                           "rtx5090", 11, "704x1280", 2.5, "14", 5.0, 20260816,
                           "t", "11-grow.png", "abc", 200, "pos", neg)
    check("the probe sidecar records the seed", "seed: 20260816" in side)
    check("the probe sidecar records the negative verbatim", "静止不动的画面" in side)
    check("the probe sidecar records which still conditioned it",
          "init_still: 11-grow.png" in side)


def test_ltx_frames_are_the_nearest_8n_plus_1():
    """The queue speaks seconds; LTX's CLI takes frames, and only 8n+1 ones.

    A translation with rounding in it is exactly the kind of thing that looks
    obviously right and is off by a third of a second on every clip in an episode.
    Two failure directions matter:

      FLOOR instead of nearest. 4s at 24fps is 96 frames and the candidates are 89
      and 97. Flooring gives 89 — 3.71s of clip for a beat the shot board timed at
      4.0 — and render_t3 would then either stretch it or slate the gap, neither of
      which anyone would trace back to a rounding rule.

      A COUNT THAT IS NOT 8n+1. LTX refuses it (ltx_i2v prints "requires frames
      divisible by 8 plus 1" and exits 2), which is the harmless direction, but it
      would refuse AFTER the queue had marked the task running.

    The 2.7s -> 65 row is the load-bearing one: 65 frames is the recipe the founder
    screened on 2026-08-06, so a task written in seconds must land on it exactly or
    the queue cannot reproduce the approved look at all.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import video_task as V

    check("2.7s at 24fps is the screened 65 frames", V.ltx_frames_for(2.7) == 65)
    check("4s at 24fps rounds UP to 97, not down to 89", V.ltx_frames_for(4) == 97)
    check("3s at 24fps -> 73", V.ltx_frames_for(3.0) == 73)
    check("5s at 24fps -> 121", V.ltx_frames_for(5.0) == 121)
    check("a non-24 fps is honoured", V.ltx_frames_for(4, fps=12) == 49)
    bad = [s for s in (0.1, 0.5, 1, 1.7, 2, 2.5, 2.667, 2.7, 3, 3.3, 4, 4.5, 5, 6, 8)
           if (V.ltx_frames_for(s) - 1) % 8 or V.ltx_frames_for(s) < 9]
    for s in bad:
        print(f"      x  {s}s -> {V.ltx_frames_for(s)} frames, not a valid 8n+1")
    check("every duration maps to a legal 8n+1 count of at least 9", not bad)
    # nearest, checked as a property rather than as a table: no legal count is
    # closer to the request than the one returned
    off = []
    for s in (0.4, 1.3, 2.2, 3.9, 4.4, 7.1):
        want = s * 24
        got = V.ltx_frames_for(s)
        better = [f for f in range(9, 400, 8) if abs(f - want) < abs(got - want)]
        if better:
            off.append(f"{s}s -> {got}, but {better[0]} is nearer {want}")
    for o in off:
        print(f"      x  {o}")
    check("no legal frame count is nearer the request than the one chosen", not off)


def test_ltx_dispatch_routes_by_video_model(tmp: Path):
    """`video_model: ltx*` must reach ltx_i2v.py, and everything else wan_i2v.py.

    Until 2026-08-07 video_task hardcoded the renderer in all three of its sampling
    paths — `wan = str(REPO/"pipeline"/"wan_i2v.py")` and the same literal in the
    batch call — so an LTX task was not a slow path, it was no path: `video_model`
    only ever selected a key inside wan_i2v.MODELS, and LTX is deliberately not in
    that dict (different pipeline, different licence document).

    Both halves are asserted, and the second is the one that protects existing work:
    an LTX task must NOT reach wan_i2v, and a Wan task must NOT reach ltx_i2v. The
    dispatch is three lines above code that fifteen episodes have already been
    rendered through, and a routing change that leaks is a change to all of them.

    Run against real machinery — node 001's shot board and a real still — with only
    the two child-process boundaries stubbed, because the thing under test is which
    argv gets built, not whether a GPU is present.
    """
    import json

    sys.path.insert(0, str(REPO / "pipeline"))
    import video_task as V

    from PIL import Image

    node = REPO / "genomes/sapling/nodes/001-capability-inventory"
    stills = tmp / "stills"
    stills.mkdir()
    # A REAL IMAGE AT THE REAL CANON SIZE, not the eight PNG magic bytes this
    # fixture used until 2026-08-08. Dispatch now prepares an aspect-correct
    # conditioning plate before either renderer is called (conditioning_plate),
    # so a still that cannot be opened is a beat that gets SKIPPED — and a
    # fixture that skips every beat answers the routing question by accident,
    # from the "no clips produced" path, whichever renderer was picked.
    Image.new("RGB", (832, 1216), (40, 60, 45)).save(stills / "01-keyboard.png")
    work = tmp / "node"
    work.mkdir()
    for f in ("shots.md", "node.md"):
        (work / f).write_text((node / f).read_text(encoding="utf-8"), encoding="utf-8")
    (work / "stills").symlink_to(stills)

    class Courier:
        def __init__(self):
            self.out = tmp / "farm-out"
            self.out.mkdir(exist_ok=True)
            self.marks, self.said = [], []

        def mark(self, m):
            self.marks.append(m)

        def say(self, m):
            self.said.append(m)

    seen = []
    real = (V._run, V.gpu_vram_gb, V.ensure_stack)
    V.gpu_vram_gb = lambda: 24.0            # a big card, so the Wan batch path runs
    V.ensure_stack = lambda courier: None   # no venv on this machine, and none needed

    def fake_run(cmd, courier, stage, timeout=None, retry=False):
        seen.append([str(c) for c in cmd])
        # the child would have written the clip; write something clip-sized so the
        # caller's own "did a clip appear" check reaches its success branch and the
        # routing question is answered by a run that SUCCEEDED, not by an exception
        for i, c in enumerate(cmd):
            if c == "--out":
                Path(cmd[i + 1]).write_bytes(b"0" * 20_000)
            if c == "--jobs":
                for j in json.loads(Path(cmd[i + 1]).read_text(encoding="utf-8")):
                    if isinstance(j, dict) and j.get("out"):
                        Path(j["out"]).write_bytes(b"0" * 20_000)
        return None
    V._run = fake_run
    try:
        for vmodel, script, other in (
                ("ltx23-distilled-fp8", "ltx_i2v.py", "wan_i2v.py"),
                ("ti2v-5b", "wan_i2v.py", "ltx_i2v.py")):
            seen.clear()
            V.run({"id": f"t-{vmodel}", "beats": "1", "video_model": vmodel,
                   "seconds": 2.7, "worker": "rtx5090"}, Courier(), work)
            joined = " ".join(" ".join(c) for c in seen)
            check(f"{vmodel} reaches {script}", script in joined)
            check(f"{vmodel} never reaches {other}", other not in joined)
    finally:
        V._run, V.gpu_vram_gb, V.ensure_stack = real

    # THE WHOLE RECIPE, not just the script name. Same invariant the Wan test above
    # enforces on its three call sites: a parameter the queue may set and the child
    # silently defaults is how "guidance did nothing" got written down as a finding.
    task = {"id": "ep1", "video_model": "ltx23-distilled-fp8", "worker": "rtx5090",
            "seed_base": 20260731}
    argv = V.ltx_argv("py", "ltx_i2v.py", task, "j.json", stage="render",
                      size="704x1280", seconds=2.7)
    got = " ".join(argv)
    for want in ("--size 704x1280", "--frames 65", "--guidance 1.0",
                 "--image-crf 33", "--offload model", "--two-stage",
                 "--distilled-sigmas", "--fp8-layerwise", "--task ep1",
                 "--worker rtx5090"):
        check(f"the screened recipe carries {want}", want in got)
    # the CFG-1 default is the LTX one, not this file's Wan-shaped 5.0
    check("guidance defaults to the distilled 1.0, not wan's 5.0",
          "--guidance 5.0" not in got)
    # bf16 has no cast, so the resident mode would OOM: it must get sequential
    bf16 = " ".join(V.ltx_argv("py", "l.py", {**task, "video_model": "ltx23-distilled"},
                               "j.json", stage="render", size="704x1280", seconds=2.7))
    check("the un-cast bf16 model gets --offload sequential",
          "--offload sequential" in bf16 and "--fp8-layerwise" not in bf16)
    # --steps means nothing under --two-stage (the sigma lists set the counts), and
    # a queue default of 30 in the log is a number nothing executed
    check("--steps is not sent on the two-stage path", "--steps" not in got)
    single = V.ltx_argv("py", "l.py", {**task, "two_stage": False}, "j.json",
                        stage="render", size="704x1280", seconds=2.7)
    check("--steps IS sent on the single-stage path", "--steps 8" in " ".join(single))
    check("the encode stage takes only the jobs file",
          V.ltx_argv("py", "l.py", task, "j.json", stage="encode", size="704x1280",
                     seconds=2.7) == ["py", "l.py", "--stage", "encode",
                                      "--jobs", "j.json"])
    # an ltx name the dispatch cannot honour must fail HERE, with a sentence, not an
    # hour later inside diffusers: ltx23-fp8 is the archived single-file checkpoint
    try:
        V.ltx_argv("py", "l.py", {"video_model": "ltx23-fp8"}, "j.json",
                   stage="render", size="704x1280", seconds=2.7)
        check("an unsupported ltx model is refused at dispatch", False)
    except ValueError:
        check("an unsupported ltx model is refused at dispatch", True)

    # every flag the dispatch sends must be one ltx_i2v's parser declares — the LTX
    # half of the same check test_queue_render_params_reach_the_child makes for wan
    import re as _re
    known = set(_re.findall(r'add_argument\("--([a-z0-9-]+)"',
                            (REPO / "pipeline" / "ltx_i2v.py").read_text(encoding="utf-8")))
    sent = {c[2:] for c in argv + single if c.startswith("--")}
    unknown = sorted(sent - known)
    for u in unknown:
        print(f"      x  --{u} is sent but ltx_i2v does not define it")
    check("no flag is sent that ltx_i2v does not accept", not unknown)


def test_ltx_jobs_list_is_one_beat_per_entry(tmp: Path):
    """The jobs file is the whole contract between two processes and fifteen beats.

    Everything that makes an episode an episode rather than fifteen unrelated
    renders passes through this list: which still conditions which beat, which
    seed, which prompt, and which embeds file the render stage should expect the
    encode stage to have written. It is read twice, in two processes, and the
    second read happens after ~4 minutes of model loading — so a malformed entry
    must raise at the top of the run, not a third of the way into it.

    The recipe is deliberately NOT per-beat: one model load is one recipe, and a
    jobs file that could vary --size or --offload per entry would be asking for a
    reload it cannot have.
    """
    import argparse
    import json

    sys.path.insert(0, str(REPO / "pipeline"))
    import ltx_i2v as L

    (tmp / "p1.txt").write_text("2D anime. the sapling leans", encoding="utf-8")
    # the negative carries Wan-era Chinese anti-static terms; the point of putting
    # prompts in FILES is that these bytes survive a cp1252 console
    (tmp / "n1.txt").write_text("静态, 静止不动的画面, frozen frame", encoding="utf-8")
    spec = [{"beat": 1, "embeds": str(tmp / "e1.pt"), "prompt_file": str(tmp / "p1.txt"),
             "negative_file": str(tmp / "n1.txt"), "init": str(tmp / "01.png"),
             "out": str(tmp / "o1.mp4"), "seed": 20260732},
            {"beat": 2, "embeds": str(tmp / "e2.pt"), "prompt_file": str(tmp / "p1.txt"),
             "negative_file": str(tmp / "n1.txt"), "init": str(tmp / "02.png"),
             "out": str(tmp / "o2.mp4"), "seed": 20260733}]
    jf = tmp / "jobs.json"
    jf.write_text(json.dumps(spec), encoding="utf-8")

    base = dict(jobs=str(jf), beat=99, seed=1, init="", out="", prompt="",
                negative="", embeds="", size="704x1280", offload="model",
                two_stage=True)
    jobs = L._jobs_for(argparse.Namespace(**base), "render")
    check("one namespace per entry", len(jobs) == 2)
    check("each beat carries its own seed", [j.seed for j in jobs] == [20260732, 20260733])
    check("each beat carries its own beat number", [j.beat for j in jobs] == [1, 2])
    check("each beat carries its own embeds path",
          [Path(j.embeds).name for j in jobs] == ["e1.pt", "e2.pt"])
    check("the prompt is read from the file, not the json",
          jobs[0].prompt == "2D anime. the sapling leans")
    check("the negative survives as bytes, not as mojibake",
          "静止不动的画面" in jobs[0].negative)
    check("the recipe is shared, not per-beat",
          all(j.size == "704x1280" and j.offload == "model" for j in jobs))

    check("no --jobs means exactly the namespace it was handed",
          L._jobs_for(argparse.Namespace(jobs=""), "render") == [
              argparse.Namespace(jobs="")])

    def raises(spec_, stage, why):
        p = tmp / "bad.json"
        p.write_text(json.dumps(spec_), encoding="utf-8")
        try:
            L._jobs_for(argparse.Namespace(**{**base, "jobs": str(p)}), stage)
            check(why, False)
        except ValueError:
            check(why, True)

    raises([{"beat": 1, "prompt_file": str(tmp / "p1.txt")}], "encode",
           "an entry with no embeds path is refused")
    raises([{"beat": 1, "embeds": str(tmp / "e1.pt")}], "encode",
           "an entry with no prompt file is refused")
    raises([{"beat": 1, "embeds": str(tmp / "e1.pt"), "init": str(tmp / "01.png")}],
           "render", "an entry with no output path is refused")
    raises([], "render", "an empty jobs list is refused")
    raises([{"beat": 1, "embeds": str(tmp / "e1.pt"), "init": str(tmp / "01.png"),
             "out": str(tmp / "same.mp4")},
            {"beat": 2, "embeds": str(tmp / "e2.pt"), "init": str(tmp / "02.png"),
             "out": str(tmp / "same.mp4")}], "render",
           "two beats writing the same file is refused")


def test_sidecar_only_calls_the_negative_inert_when_it_is():
    """The "changed no pixel" caveat must be FALSE-proof, not unconditional.

    THE DEFECT, live from the guidance flag's arrival until 2026-08-16:
    `_render_one` appended "[unused: guidance 1.0 ... changed no pixel]" to every
    sidecar whose negative was non-empty, whatever guidance had actually been. Our
    beat specs pass `--guidance 2.0`, so the sidecars of the renders whose negative
    genuinely DID bite all published a line saying it had not. Sidecar text only —
    it never touched a pixel — but a provenance line that is wrong is worse than an
    absent one, because the next lane reads it as a measurement rather than as a
    note. The 2026-08-15 CFG lane found it and left it alone because another lane
    held the file.

    The truth condition is upstream's, not ours: diffusers' LTX2 pipeline sets
    `do_classifier_free_guidance = (guidance_scale > 1.0) or (audio_guidance_scale
    > 1.0)` and audio defaults to the video scale, so the uncond pass — the only
    thing that ever reads the negative embeddings — runs for every guidance ABOVE
    1.0 and for none at or below it.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import ltx_i2v as L

    NEG = "camera pan, zoom, still image, freeze frame"
    INERT = "changed no pixel"

    at2 = L.sidecar_negative(NEG, 2.0)
    check("guidance 2.0 does NOT claim the negative was unused", INERT not in at2)
    check("guidance 2.0 records the negative verbatim", at2 == NEG)
    check("guidance 1.5 does NOT claim the negative was unused",
          INERT not in L.sidecar_negative(NEG, 1.5))
    # The boundary itself: 1.0 is NOT > 1.0, so CFG is off and the caveat is true.
    at1 = L.sidecar_negative(NEG, 1.0)
    check("guidance 1.0 does say the negative was unused", INERT in at1)
    check("guidance 1.0 still records the negative itself", at1.startswith(NEG))
    check("guidance 0 says the negative was unused",
          INERT in L.sidecar_negative(NEG, 0.0))
    # A run given no negative gets no caveat about one, at any guidance.
    check("an empty negative stays empty at 1.0", L.sidecar_negative("", 1.0) == "")
    check("an empty negative stays empty at 2.0", L.sidecar_negative("", 2.0) == "")
    # argparse hands guidance through as a float, but a jobs-built namespace or a
    # hand-written test can carry the string; the caveat must not flip on the type.
    check("a string guidance is read as a number",
          INERT not in L.sidecar_negative(NEG, "2.0"))

    # And the unconditional form must not come back: no literal caveat text may
    # sit anywhere in the file except inside sidecar_negative itself.
    src = (REPO / "pipeline" / "ltx_i2v.py").read_text(encoding="utf-8")
    fn = src.split("def sidecar_negative", 1)[1].split("\ndef ", 1)[0]
    check("the caveat text lives in exactly one function",
          src.count("changed no pixel]") == fn.count("changed no pixel]") == 1)


def test_the_conditioning_plate_is_the_episode_crop(tmp: Path):
    """The crop that frames a video plate must be the crop that frames the cut.

    THE DEFECT, hash-verified 2026-08-08: every canon still is 832x1216 (aspect
    0.684) and every clip is rendered at 704x1280 (0.550), and both renderers
    closed that gap with a two-argument resize — wan_i2v.py:541 and :713 called
    `Image.resize((w, h))` outright, ltx_i2v handed the raw PIL image to a
    preprocessor that does the same. 0.684/0.550 = 1.2440, so every clip came out
    24.4% vertically stretched and nothing said so, because a stretched frame is a
    valid frame and no metric in this repo measures aspect.

    THE POLICY IS BORROWED, NOT CHOSEN. render_t3 has fitted every delivered
    episode to 9:16 with `force_original_aspect_ratio=increase` + `crop=W:H`
    since T3 existed — scale to cover, then take the middle. That framing is
    founder-approved by having been screened; picking a different one for the
    plates would mean conditioning the model on a composition the episode then
    re-crops. The first assertion below reads that filter string back out of
    render_t3, so if the episode's policy ever moves, THIS test is what says the
    plate policy has silently stopped matching it.

    The pixel fingerprint is the part that cannot be argued with: the plate must
    equal crop-then-resample of the source, byte for byte, and must NOT equal the
    naive stretch. Sizes and aspect ratios alone would pass a plate cropped from
    the wrong side.
    """
    from PIL import Image

    sys.path.insert(0, str(REPO / "pipeline"))
    import plate_prep as pp

    # 1. THE POLICY THIS MATCHES, read from the file that ships the episodes.
    graph = (REPO / "pipeline" / "render_t3.py").read_text(encoding="utf-8")
    check("ep1's fit is still scale-to-cover plus centre crop",
          "force_original_aspect_ratio=increase" in graph
          and f"crop={{WIDTH}}:{{HEIGHT}}" in graph)
    check("ep1 does not letterbox its footage",
          "force_original_aspect_ratio=decrease" not in graph)

    # 2. THE ARITHMETIC, both directions and the no-op.
    check("832x1216 into 704x1280 crops WIDTH, centred",
          pp.cover_crop_box(832, 1216, 704, 1280) == (81, 0, 750, 1216))
    check("the kept window is 669 wide — 163px out, 81 left and 82 right",
          (750 - 81, 832 - 669) == (669, 163))
    check("704x1280 into 832x1216 crops HEIGHT, centred",
          pp.cover_crop_box(704, 1280, 832, 1216) == (0, 125, 704, 1154))
    check("an exactly on-aspect source is not cropped",
          pp.cover_crop_box(704, 1280, 704, 1280) is None)
    check("one pixel of disagreement is rounding, not framing",
          pp.cover_crop_box(703, 1280, 704, 1280) is None)
    check("four pixels is framing, and is cropped",
          pp.cover_crop_box(700, 1280, 704, 1280) == (0, 3, 700, 1276))
    check("a half-scale source of the same shape is left alone",
          pp.cover_crop_box(416, 608, 832, 1216) is None)
    check("the note says the numbers, in ascii, for a cp1252 console",
          "163px of width (81 left, 82 right)" in pp.crop_note(832, 1216, 704, 1280)
          and pp.crop_note(832, 1216, 704, 1280).isascii())

    # 3. THE PIXELS. An asymmetric source, so a crop taken from the wrong side or
    # a left/right flip fails instead of looking plausible.
    src = Image.new("RGB", (832, 1216))
    src.putdata([(x % 256, y % 256, (x * 3 + y * 7) % 256)
                 for y in range(1216) for x in range(832)])
    still = tmp / "01-canon.png"
    src.save(still)

    plate, rec = pp.prepare_plate(still, "704x1280", tmp / "plates", tag="01")
    got = Image.open(plate).convert("RGB")
    check("the plate is exactly the target size", got.size == (704, 1280))
    check("the plate's aspect is 0.55, not the still's 0.684",
          abs(got.size[0] / got.size[1] - 0.55) < 1e-9)
    want = src.crop((81, 0, 750, 1216)).resize((704, 1280), Image.LANCZOS)
    check("the plate IS the centre crop of the source, pixel for pixel",
          got.tobytes() == want.tobytes())
    stretched = src.resize((704, 1280), Image.LANCZOS)
    check("and is not the stretch the renderers used to do",
          got.tobytes() != stretched.tobytes())

    # 4. THE RECORD. It names the durable half (the still, by repo-relative path
    # and sha) as well as the derived half, because the plate dir gets deleted.
    check("the record names the source still, not just the plate",
          rec["path"].endswith("01-canon.png")
          and rec["sha256"] == pp.sha256_file(still))
    check("the record measures both frames",
          (rec["source_wxh"], rec["plate_wxh"]) == ("832x1216", "704x1280"))
    check("the record says what was cropped and by which policy",
          rec["crop_policy"].startswith("cover-centre")
          and "163px of width" in rec["crop_policy"])
    check("the record hashes the bytes the model actually saw",
          rec["plate_sha256"] == pp.sha256_file(plate))

    # 4b. THE SEPARATOR, which is the whole portability of that repo-relative
    # pointer. The clips are rendered on the Windows box and the sidecars are read
    # here, and `genomes\sapling\...` does not raise on posix — a backslash is a
    # legal filename character, so the pointer just quietly names nothing. Asserted
    # through a PureWindowsPath because that is the only way this Mac can see the
    # bug at all: the local Path flavour never produces a backslash to strip.
    from pathlib import PureWindowsPath
    win = PureWindowsPath(r"genomes\sapling\nodes\002b-first-citizen\stills"
                          r"\01-cold-open.png")
    check("a windows repo-relative path is published with forward slashes",
          pp.posix(win)
          == "genomes/sapling/nodes/002b-first-citizen/stills/01-cold-open.png")
    check("a windows absolute path keeps its drive and loses its backslashes",
          pp.posix(PureWindowsPath(r"C:\banyan-farm\b01\01-704x1280.png"))
          == "C:/banyan-farm/b01/01-704x1280.png")
    check("nothing this platform can produce carries a backslash either",
          "\\" not in rec["path"] and "\\" not in pp.rel_to_repo(still))

    # AND THE CALL SITE, structurally, because the behaviour above cannot pin it
    # from here: `Path("a\\b")` on posix is one segment named `a\b`, so the local
    # flavour has no separator to convert and rel_to_repo would pass every
    # assertion this machine can make even after a revert to `str()`. Both of its
    # exits — the repo-relative one and the absolute fallback — must go through
    # posix(), and CI runs on linux, so only the AST notices if one stops.
    import ast

    pp_src = (REPO / "pipeline" / "plate_prep.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(pp_src, "plate_prep.py"))
              if isinstance(n, ast.FunctionDef) and n.name == "rel_to_repo")
    exits = [n.value for n in ast.walk(fn) if isinstance(n, ast.Return)]
    check(f"both of rel_to_repo's {len(exits)} exits are converted, not str()'d",
          len(exits) == 2
          and all(isinstance(e, ast.Call) and getattr(e.func, "id", "") == "posix"
                  for e in exits))

    # 5. AN ALREADY-CORRECT PLATE IS STILL RESAMPLED TO SIZE. Right aspect, wrong
    # scale is the same class of silent wrongness one step smaller.
    half = tmp / "half.png"
    Image.new("RGB", (352, 640), (9, 9, 9)).save(half)
    p2, r2 = pp.prepare_plate(half, "704x1280", tmp / "plates", tag="02")
    check("an on-aspect but undersized still is scaled, not passed through",
          Image.open(p2).size == (704, 1280) and "no crop" in r2["crop_policy"])


def _asymmetric(w: int, h: int):
    """A picture with no symmetry in either axis. Cheap — blocks, not a gradient.

    Every assertion below compares one crop against another, and a picture that
    is symmetric passes when the crop is taken from the wrong side or the image
    comes back mirrored. The stripes are deliberately different widths so a
    left/right flip changes the bytes, and the top band so a vertical one does.
    """
    from PIL import Image

    img = Image.new("RGB", (w, h), (20, 30, 40))
    img.paste((220, 40, 40), (0, 0, max(1, w // 8), h))            # fat left edge
    img.paste((40, 200, 90), (w - max(1, w // 20), 0, w, h))       # thin right edge
    img.paste((250, 240, 60), (0, 0, w, max(1, h // 12)))          # top band only
    img.paste((90, 60, 220), (w // 3, h // 2, w // 3 + max(1, w // 10),
                              h // 2 + max(1, h // 6)))            # off-centre mark
    return img


def test_no_render_path_stretches_a_mismatched_still(tmp: Path):
    """The held beats were stretched too, and for four days nothing measured it.

    THE PLATE FIX MISSED A RENDERER. 9009870 put `plate_prep`'s cover-centre
    policy in front of wan_i2v and the queue, on the reasoning that those are
    what turn a still into video. `hold_still.py` also turns a still into video —
    it just does it with arithmetic instead of a model — and it had the identical
    line, `src.resize((int(W * over), int(H * over)))`, two arguments and no
    aspect term. Every held beat in v30, v31 and v32 is 24.4% tall (42.6dB
    against the approved still on beat 14), which makes the held clips the WORST
    case rather than an afterthought: a held still's entire claim is that it is
    exactly the frame the founder approved, and it was the one clip in the tree
    guaranteed not to be. `farm_worker.py:490` had it a third time on its img2img
    init.

    So this test is deliberately not about one function. It sweeps every source
    shape the tree can hand a renderer — the canon 832x1216, an already-correct
    704x1280, a landscape frame, an over-tall one and a square — across BOTH
    surviving pixel paths, because the bug was never that one crop was wrong. It
    was that no test anywhere asserted an output aspect, so three call sites
    could each be written the obvious wrong way and all three stay silent.

    What is NOT re-asserted here: the direction, the amount and the curve of the
    push-in. Those are the founder's, they live in
    test_held_zoom_is_monotonic_and_moderate, and this fix moved none of them —
    but the monotonicity has to be re-checked in PIXELS, because a crop box that
    rounds badly can reverse a move whose float scales never did.
    """
    from PIL import Image

    sys.path.insert(0, str(REPO / "pipeline"))
    import plate_prep as pp

    W, H = hs.W, hs.H
    check("the held beats target the same bucket the plates do", (W, H) == (704, 1280))

    # THE SWEEP. Both directions of mismatch, plus the no-op, on both paths.
    shapes = [(832, 1216, "the canon still, every frame in the tree"),
              (704, 1280, "already on-aspect — must not be re-cropped"),
              (1920, 1080, "a landscape frame, which loses WIDTH not height"),
              (512, 1600, "over-tall, the direction that loses HEIGHT"),
              (1000, 1000, "square")]
    zs = hs.scale_series(12.992, 24 * 13)          # beat 14's real length
    for sw, sh, why in shapes:
        # --- the held path ---
        boxes = hs.zoom_windows(sw, sh, zs)
        check(f"{sw}x{sh} held: a window per frame ({why})", len(boxes) == len(zs))
        worst = max(abs((r - l) / (b - t) - W / H) for l, t, r, b in boxes)
        check(f"{sw}x{sh} held: every window is on the 0.55 target aspect "
              f"(worst {worst:.5f})", worst <= pp.ASPECT_EPS)
        check(f"{sw}x{sh} held: no window escapes the source",
              all(0 <= l < r <= sw and 0 <= t < b <= sh for l, t, r, b in boxes))
        # THE WIDEST WINDOW IS THE PLATE. Not merely on-aspect — the same box,
        # so a held beat and a rendered beat cut from one still open on one
        # composition instead of two that are each defensible on their own.
        check(f"{sw}x{sh} held: frame 0 IS the conditioning plate's crop",
              boxes[0] == (pp.cover_crop_box(sw, sh, W, H) or (0, 0, sw, sh)))
        widths = [r - l for l, _, r, _ in boxes]
        check(f"{sw}x{sh} held: the push-in never reverses in PIXELS",
              all(b <= a for a, b in zip(widths, widths[1:])))
        check(f"{sw}x{sh} held: and it does travel, by 1 + ZOOM_TOTAL",
              abs(widths[0] / widths[-1] - (1 + hs.ZOOM_TOTAL)) < 0.005)
        # ONE CENTRE FOR THE WHOLE SHOT. Rounding each window independently made
        # this alternate by half a pixel — a shimmer under a move whose only
        # content is that it is smooth. See hold_still._same_parity.
        check(f"{sw}x{sh} held: the zoom origin never moves, not by half a pixel",
              len({(l + r, t + b) for l, t, r, b in boxes}) == 1)

        # --- the plate path, same shapes, same rule ---
        fitted, info = pp.fit_cover(_asymmetric(sw, sh), W, H)
        check(f"{sw}x{sh} plate: comes out exactly {W}x{H}", fitted.size == (W, H))
        check(f"{sw}x{sh} plate: the record says which pixels went",
              str(sw) in info["crop_note"] and info["crop_note"].isascii())

    # THE PIXELS, on the shape that actually exists in the tree. Sizes and
    # aspects alone would pass a crop taken from the wrong side.
    src = _asymmetric(832, 1216)
    want = src.crop((81, 0, 750, 1216)).resize((W, H), Image.LANCZOS)
    frames = list(hs.zoom_frames(src, zs))
    check("a held frame is exactly the clip size", frames[0].size == (W, H))
    check("the first held frame IS the plate, pixel for pixel",
          frames[0].tobytes() == want.tobytes()
          and want.tobytes() == pp.fit_cover(src, W, H)[0].tobytes())
    stretched = src.resize((W, H), Image.LANCZOS)
    check("and is NOT the stretch every held beat in v30-v32 carries",
          frames[0].tobytes() != stretched.tobytes())
    check("the last frame is tighter than the first, and still not the stretch",
          frames[-1].tobytes() not in (frames[0].tobytes(), stretched.tobytes()))

    # NO OVERSAMPLED INTERMEDIATE. The geometrically-correct-but-soft variant
    # (fit to 704x1280, blow up 1.14x, crop back down) is a real alternative that
    # a later session could reach for; it upscales 1.2x and every frame inherits
    # the blur. Frame 0 must be the single-resample cut, not that one.
    soft = (pp.fit_cover(src, W, H)[0]
            .resize((int(W * 1.14), int(H * 1.14)), Image.LANCZOS)
            .crop((7, 8, 7 + W, 8 + H)))
    check("frames are cut from the native still, not from an upscaled buffer",
          frames[0].tobytes() != soft.tobytes())

    # THE RECORD, because an unrecorded framing is how this survived a whole
    # pipeline audit: `init: <path>` names a file, not a crop.
    import yaml
    clip = tmp / "14-worth-staying-in.mp4"
    clip.write_bytes(b"v")
    note = pp.crop_note(832, 1216, W, H) + "; and then some (a: colon, in it)"
    # The still must EXIST: sidecar() hashes the bytes it was handed as of
    # 2026-08-09, which is the only defence a held clip has on a fresh clone. A
    # real call always has the file — it just fed it to ffmpeg.
    still = tmp / "14-worth-staying-in.png"
    src.save(still)
    hs.sidecar(clip, still, 14, 12.99, zoom_total_used=0.12, framing=note)
    text = Path(str(clip) + ".meta.yaml").read_text(encoding="utf-8")
    d = yaml.safe_load(text)
    check("the held sidecar records which pixels the frame kept",
          "163px of width" in d["framing"] and d["framing"] == note)
    check("a framing note full of colons does not break the yaml",
          isinstance(d, dict) and d["shot_beat"] == 14)
    # the three substring readers this file's docstring pins, still readable.
    # `none` is a yaml STRING, not a null — the sentinel readers match the raw
    # text and licence_gate normalises the value, so both forms are asserted.
    check("and the bare sentinel render_t3 and check_invention match survives",
          "model: none\n" in text and d["model"] == "none")
    # AND THE PATH THAT APPLIED NO POLICY CLAIMS NONE. --frozen still letterboxes
    # (a separate, unscreened question — see hold.__doc__), so it returns "" and
    # the key must be absent rather than present and empty: an empty `framing:`
    # would read as "measured, nothing cropped", which is a different claim.
    frz = tmp / "14-frozen.mp4"
    frz.write_bytes(b"v")
    hs.sidecar(frz, still, 14, 12.99, frozen=True)
    frz_text = Path(str(frz) + ".meta.yaml").read_text(encoding="utf-8")
    check("a frozen hold claims no framing it did not apply",
          "framing:" not in frz_text
          and "framing" not in (yaml.safe_load(frz_text) or {}))

    # THE THIRD CALL SITE. farm_worker imports torch and diffusers, so it cannot
    # be exercised here and the fix is asserted structurally instead — by AST,
    # not by substring, because the comment recording what the line USED to say
    # contains the very string a substring check would look for, and a test that
    # a comment can satisfy is worse than no test.
    #
    # The invariant is delegation: render_task may open an image, but every
    # decision about its shape belongs to plate_prep. A resize of its own is the
    # bug by definition, whatever arguments it is given.
    import ast

    fw_src = (REPO / "pipeline" / "farm_worker.py").read_text(encoding="utf-8")
    render_task = next(n for n in ast.walk(ast.parse(fw_src, "farm_worker.py"))
                       if isinstance(n, ast.FunctionDef) and n.name == "render_task")
    resizes = [n.lineno for n in ast.walk(render_task)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "resize"]
    check("the farm worker's img2img init goes through the shared policy",
          "plate_prep.fit_cover(" in fw_src)
    check(f"and render_task reshapes nothing itself (found {resizes})", not resizes)
    check("the held path reaches the same helper, not its own arithmetic",
          "plate_prep.cover_crop_box("
          in (REPO / "pipeline" / "hold_still.py").read_text(encoding="utf-8"))


def test_dispatch_never_hands_a_renderer_a_raw_still(tmp: Path):
    """Both renderers must be conditioned on a plate, and the sidecar must say so.

    This is the half of the aspect fix that ltx_i2v.py cannot carry. That file
    hands `--init` straight to a preprocessor that resizes to --size without
    looking at aspect, and it is parked — so the only place LTX's stretch can be
    fixed from is upstream, by making sure the corrupt input never arrives. Every
    dispatch path is asserted because this file's history is a list of parameters
    that reached two of its three sampling paths and not the third.

    THE PROVENANCE HALF IS NOT A GARNISH. An i2v clip is at least as much its
    conditioning image as its prompt, and until today no sidecar named the still
    at all — so a clip rendered from a REVOKED still, or from the pre-regrade
    revision of a redrawn one, was indistinguishable on disk from a correct one.
    The sha is what makes that answerable; two revisions of a still share a name
    and a size.
    """
    import json

    import yaml
    from PIL import Image

    sys.path.insert(0, str(REPO / "pipeline"))
    import licence_gate as lg
    import video_task as V

    node = REPO / "genomes/sapling/nodes/001-capability-inventory"
    work = tmp / "node"
    (work / "stills").mkdir(parents=True)
    for f in ("shots.md", "node.md"):
        (work / f).write_text((node / f).read_text(encoding="utf-8"), encoding="utf-8")
    canon = {}
    for beat, shade in ((1, (200, 40, 40)), (2, (40, 40, 200))):
        p = work / "stills" / f"{beat:02d}-canon.png"
        im = Image.new("RGB", (832, 1216), shade)
        # a bright stripe down one side: a crop taken from an edge instead of the
        # centre keeps it, and the plate's mean colour then gives the game away
        im.paste((255, 255, 0), (0, 0, 40, 1216))
        im.save(p)
        canon[beat] = p
    # the REVOKED sibling must stay unread — it is the file whose accidental use
    # the sha in the record exists to make detectable
    Image.new("RGB", (832, 1216), (0, 0, 0)).save(
        work / "stills" / "01-canon-REVOKED-old.png")

    class Courier:
        def __init__(self):
            self.out = tmp / "farm-out"
            self.out.mkdir(exist_ok=True)
            self.marks, self.said = [], []

        def mark(self, m):
            self.marks.append(m)

        def say(self, m):
            self.said.append(m)

    # Collected INSIDE the stub, not read back afterwards: the Wan batch path
    # unlinks its jobs file the moment the child returns, and the LTX path hands
    # the same file to two stages, so an after-the-fact sweep of argv would find
    # one path missing and the other doubled.
    inits = []
    real = (V._run, V.gpu_vram_gb, V.ensure_stack)
    V.gpu_vram_gb = lambda: 24.0
    V.ensure_stack = lambda courier: None

    def fake_run(cmd, courier, stage, timeout=None, retry=False):
        cmd = [str(c) for c in cmd]
        for i, c in enumerate(cmd):
            if c == "--init":
                inits.append(Path(cmd[i + 1]))
            if c == "--out":
                Path(cmd[i + 1]).write_bytes(b"0" * 20_000)
            if c == "--jobs":
                for j in json.loads(Path(cmd[i + 1]).read_text(encoding="utf-8")):
                    if not isinstance(j, dict):
                        continue
                    if j.get("init"):
                        inits.append(Path(j["init"]))
                    if j.get("out"):
                        Path(j["out"]).write_bytes(b"0" * 20_000)
        return None
    V._run = fake_run

    try:
        # THREE PATHS, all three exercised: LTX's jobs file, Wan's batch jobs file
        # (>1 beat on a big card) and Wan's single-beat argv (1 beat).
        for label, task in (
                ("ltx", {"id": "p-ltx", "beats": "1,2", "seconds": 2.7,
                         "video_model": "ltx23-distilled-fp8", "worker": "rtx5090"}),
                ("wan-batch", {"id": "p-wanb", "beats": "1,2", "seconds": 4,
                               "video_model": "ti2v-5b", "worker": "rtx5090"}),
                ("wan-single", {"id": "p-wans", "beats": "1", "seconds": 4,
                                "video_model": "ti2v-5b", "worker": "rtx5090"})):
            inits.clear()
            courier = Courier()
            V.run(dict(task), courier, work)
            # LTX hands one jobs file to encode AND to render, so the same plate
            # legitimately appears twice; what must be true is that each beat has
            # one and only one distinct conditioning frame.
            plates = sorted({p.resolve() for p in inits})
            check(f"{label}: every beat got a conditioning frame",
                  len(plates) == len(str(task["beats"]).split(",")))
            check(f"{label}: no renderer was handed the raw canon still",
                  not any(p in {q.resolve() for q in canon.values()} for p in plates))
            check(f"{label}: every conditioning frame is already 704x1280",
                  all(Image.open(p).size == (704, 1280) for p in plates))
            check(f"{label}: the plates live outside the courier's push folder",
                  not any(courier.out.resolve() in p.parents for p in plates))

            clips = sorted(courier.out.glob(f"{task['id']}-*.mp4"))
            metas = [yaml.safe_load((c.parent / (c.name + ".meta.yaml"))
                                    .read_text(encoding="utf-8")) for c in clips]
            check(f"{label}: every clip's sidecar records its init frame",
                  clips and all(isinstance(m.get("init_frame"), dict) for m in metas))
            frames = [m["init_frame"] for m in metas]
            check(f"{label}: the record names the still, not the plate, as source",
                  all(f["path"].endswith("-canon.png")
                      and "REVOKED" not in f["path"] for f in frames))
            check(f"{label}: the record carries the still's own sha256",
                  {f["sha256"] for f in frames}
                  <= {V.plate_prep.sha256_file(p) for p in canon.values()})
            check(f"{label}: the record states the crop, source and plate sizes",
                  all(f["source_wxh"] == "832x1216" and f["plate_wxh"] == "704x1280"
                      and "163px of width" in f["crop_policy"] for f in frames))
    finally:
        V._run, V.gpu_vram_gb, V.ensure_stack = real

    # A RENDERER'S OWN SIDECAR IS ADDED TO, NEVER REWRITTEN. ltx_i2v writes the
    # offload mode, the quantisation and the measured throughput; those are the
    # only record of them, and the queue's thinner version would delete them.
    clip = tmp / "own.mp4"
    clip.write_bytes(b"0" * 20_000)
    side = tmp / "own.mp4.meta.yaml"
    side.write_text("model: Lightricks/LTX-Video\nthroughput_s_video_per_s_wall: 0.42\n",
                    encoding="utf-8")
    rec = {"path": "genomes/sapling/nodes/n/stills/01-x.png", "sha256": "ab" * 32,
           "source_wxh": "832x1216", "plate_wxh": "704x1280",
           "crop_policy": V.plate_prep.crop_note(832, 1216, 704, 1280)}
    check("the queue appends its init_frame to the renderer's record",
          V.append_init_frame(clip, rec) is True)
    got = yaml.safe_load(side.read_text(encoding="utf-8"))
    check("and the renderer's own measurements survive it",
          got["throughput_s_video_per_s_wall"] == 0.42
          and got["model"] == "Lightricks/LTX-Video")
    check("the appended block round-trips through yaml",
          got["init_frame"]["sha256"] == "ab" * 32
          and got["init_frame"]["crop_policy"].startswith("cover-centre"))
    check("a second append is a no-op, not a duplicate block",
          V.append_init_frame(clip, rec) is False
          and side.read_text(encoding="utf-8").count("init_frame:") == 1)

    # THE READERS TOLERATE THE NEW KEY, verified the way `corrections:` was: the
    # gate walks every nested dict as its own record, so a block of five scalars
    # with no model, platform or licence in it must read as "nothing to judge"
    # and must not turn a clean clip into a violation. `path` is deliberately not
    # one of the gate's ASSET_KEYS — naming it `still:` would have.
    root = tmp / "gate"
    n = root / "genomes/g/nodes/n/clips"
    n.mkdir(parents=True)
    body = ("platform: local-gpu (rtx5090)\nmodel: Wan-AI/Wan2.2-TI2V-5B-Diffusers\n"
            "model_licence: Apache-2.0\ncost_usd: 0\n")
    (n / "01-a.mp4").write_bytes(b"0" * 100)
    (n / "01-a.mp4.meta.yaml").write_text(body, encoding="utf-8")
    before, _ = lg.scan(root)
    (n / "01-a.mp4.meta.yaml").write_text(
        body + V._yaml_map("init_frame", rec), encoding="utf-8")
    after, _ = lg.scan(root)
    check("licence_gate reads a sidecar the same with init_frame as without",
          before == after == [])


def test_vercel_build_guard_covers_every_site_input():
    """The Vercel build guard must still name every input build_site.py reads.

    `pipeline/vercel-ignore-build.sh` decides whether a push is worth a build by
    diffing a hand-written list of site inputs. Two ways that list rots, both
    silent, both expensive in opposite directions: a guarded path gets renamed
    (the guard stops covering it, and a real site change stops publishing), or a
    builder grows a new input nobody added (same). This test reads the inputs
    back out of the builders and fails if one escapes the list — which is the
    only reason the list is allowed to be strict. The overspend it descends from
    was >$100 of build hours in under a month, so the guard staying honest is
    worth a test.
    """
    import json
    import re

    cfg = json.loads((REPO / "vercel.json").read_text())

    # (a) the config points at a script that exists, and the branch rules deny
    #     the courier branches while still letting main publish.
    guard = REPO / "pipeline" / "vercel-ignore-build.sh"
    check("vercel.json ignoreCommand names the guard script",
          "vercel-ignore-build.sh" in (cfg.get("ignoreCommand") or ""))
    check("the guard script exists", guard.is_file())
    enabled = (cfg.get("git") or {}).get("deploymentEnabled") or {}
    check("git.deploymentEnabled denies farm-results-*",
          enabled.get("farm-results-*") is False)
    check("git.deploymentEnabled denies everything by default",
          enabled.get("**") is False and enabled.get("*") is False)
    check("git.deploymentEnabled still allows main", enabled.get("main") is True)

    # (b) every path the guard lists is a real path today.
    body = guard.read_text()
    block = body.split("SITE_INPUTS=(", 1)[1].split("\n)", 1)[0]
    listed = [ln.strip() for ln in block.splitlines()
              if ln.strip() and not ln.strip().startswith("#")]
    missing = [p for p in listed if not (REPO / p).exists()]
    if missing:
        print(f"      guard lists paths that no longer exist: {missing}")
    check("every path in the build guard exists", not missing)

    # (c) every repo file the builders read is under one of those paths. The
    #     builders name their inputs as `REPO / "..."` literals and as sibling
    #     module imports; both are enumerable without importing anything.
    builders = ["build_site.py", "build_status.py", "build_sim.py",
                "build_shotboard.py", "build_pulse.py", "site_theme.py",
                "licence_gate.py"]
    seen, queue = set(), list(builders)
    # Seed the expected set with the builders themselves: build_site delegates to
    # build_status/build_sim/build_shotboard from *inside* main(), so the
    # top-level-import rule below would never see them, and dropping one from the
    # guard would have gone unnoticed. (It did, the first time this test ran.)
    reads = {f"pipeline/{b}" for b in builders}
    while queue:
        name = queue.pop()
        if name in seen or not (REPO / "pipeline" / name).is_file():
            continue
        seen.add(name)
        src = (REPO / "pipeline" / name).read_text()
        # Sibling pipeline modules are build inputs — but only the ones imported
        # at module scope (column 0). An indented `from video_task import ...`
        # is a lazy import inside a paid-render code path that build_site never
        # executes; following those walked the test into the whole render
        # pipeline and would have made every ltx_i2v.py tweak rebuild the site.
        for mod in re.findall(r"^(?:import (\w+)|from (\w+) import)", src, re.M):
            dep = (mod[0] or mod[1]) + ".py"
            if (REPO / "pipeline" / dep).is_file():
                reads.add(f"pipeline/{dep}")
                queue.append(dep)
        # REPO / "a" / "b"  and  REPO / "a/b"
        for chain in re.findall(r'REPO / "([^"]+)"((?: / "[^"]+")*)', src):
            parts = [chain[0]] + re.findall(r'"([^"]+)"', chain[1])
            reads.add("/".join(parts))

    # Named exclusions, each with the reason it is not a site input. A path that
    # reaches this test without being listed in the guard OR named here is a new
    # input nobody thought about, and that is the failure worth having.
    not_inputs = {
        "_site":                 "the output directory, not an input",
        "pipeline":              "sys.path.insert, not a file read",
        "pipeline/budget.yaml":  "generate_shots.load_caps() reads it on the PAID "
                                 "render path only; build_status imports just "
                                 "parse_shots, so no build ever opens it",
    }
    uncovered = sorted(
        r for r in reads
        if r not in not_inputs
        and not any(r == p or r.startswith(p + "/") for p in listed))
    if uncovered:
        print(f"      builder inputs the guard does not cover: {uncovered}")
    check("the build guard covers every builder input", not uncovered)


def test_links_resolve_against_the_url_a_page_is_served_at(tmp: Path):
    """A page's relative links resolve against its URL, not its directory.

    THE BREAK, 2026-08-09. The founder opened banyan.city/review and said
    "images are broken". Nothing was missing: every file was in `_site` at the
    path the page named, and `check_links` swept 70 pages green. The URL was
    wrong. `vercel.json` sets `cleanUrls: true` with `trailingSlash: false`, so
    `_site/review/index.html` is served at **`/review`** — and `/review/`
    308-redirects to it, so there is no directory-shaped version of that URL.
    A page at `/review` has base `/`, which makes `review-assets/x.jpg` mean
    `/review-assets/x.jpg`. 119 references across three pages 404'd: every
    image, every clip, every poster and every provenance link on /review, all
    six trial videos on /trials, and /lab's three sub-page links.

    The gate resolved each href against the page's directory ON DISK, so it was
    asking a question the browser never asks and could not have caught any of
    it. It models the served URL now. This test pins the two rules that make
    that true, because they are invisible in the output when they are right:

      1. `<dir>/index.html` is served one level UP from where it sits. Every
         other page is served where it sits.
      2. resolution is root-clamped, like a browser: `../index.html` from
         `/review` is `/index.html`, not an escape from the site. Path
         arithmetic calls that an escape and would fail the correct nav links
         while passing the broken media ones.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import build_site as bs

    # Pinned against BOTH host settings rather than against whatever vercel.json
    # says today: a config agent is free to turn trailingSlash on, and a test
    # that silently re-pointed at the new answer would stop testing anything.
    import json as _json
    real = bs._trailing_slash
    bs._trailing_slash = lambda: False
    try:
        check("a subdirectory index is served from its parent",
              bs.served_base("review/index.html") == "")
        check("...and so is the trials page", bs.served_base("trials/index.html") == "")
        check("the root index is served from the root",
              bs.served_base("index.html") == "")
        check("a named page keeps its own directory",
              bs.served_base("watch/season.html") == "watch")
        check("...including a node's shot board",
              bs.served_base("sapling/001-x-shots.html") == "sapling")
        bs._trailing_slash = lambda: True
        check("turn trailingSlash on and the base moves back down a level",
              bs.served_base("review/index.html") == "review")
        check("...while a named page is unaffected by the setting",
              bs.served_base("watch/season.html") == "watch")
    finally:
        bs._trailing_slash = real
    cfg = _json.loads((REPO / "vercel.json").read_text(encoding="utf-8"))
    check("and the live rule is READ from vercel.json, never assumed",
          bs._trailing_slash() == bool(cfg.get("trailingSlash", False)))

    check("the break: a relative asset on /review points at the site root",
          bs.resolve_url("", "review-assets/x.jpg") == "review-assets/x.jpg")
    check("the fix: a root-absolute reference lands where the file is",
          bs.resolve_url("", "/review/review-assets/x.jpg")
          == "review/review-assets/x.jpg")
    check("`..` is clamped at the root the way a browser clamps it",
          bs.resolve_url("", "../index.html") == "index.html")
    check("...and still walks up one real level when there is one",
          bs.resolve_url("watch", "../index.html") == "index.html")
    check("a page in a directory resolves its siblings",
          bs.resolve_url("sapling", "001-x-shots.html") == "sapling/001-x-shots.html")

    # And the gate itself must FAIL on the real shape of the bug rather than
    # only reporting it prettily. Built as files, because check_links sweeps
    # _site rather than taking HTML as an argument.
    out = tmp / "_site"
    (out / "review").mkdir(parents=True)
    (out / "review" / "review-assets").mkdir()
    (out / "review" / "review-assets" / "x.jpg").write_bytes(b"\xff\xd8\xff")
    (out / "index.html").write_text("<a href='review/index.html'>r</a>")
    old, bs.OUT = bs.OUT, out
    try:
        (out / "review" / "index.html").write_text(
            '<img src="review-assets/x.jpg"><a href="../index.html">up</a>')
        broken = bs.check_links(["index.html"])
        check("the gate fails on a relative asset under a subdirectory index",
              any("review-assets/x.jpg" in b for b in broken))
        check("...and does not fail on the nav link beside it",
              not any("index.html\"" in b or "../index.html" in b for b in broken))

        (out / "review" / "index.html").write_text(
            '<img src="/review/review-assets/x.jpg"><a href="../index.html">up</a>')
        check("the gate passes once the reference is root-absolute",
              bs.check_links(["index.html"]) == [])
    finally:
        bs.OUT = old


def test_review_page_publishes_nothing_unprovenanced():
    """Every file the review area serves must exist, carry a record, and clear
    the licence gate — checked against `cuts/cuts.yaml`, not against the build.

    WHY A TEST AND NOT JUST THE GATE. `build_site.publishable()` returns True
    for a file with NO sidecar at all, on purpose and correctly: an
    unprovenanced asset is the licence gate's finding to report, not the site
    build's to silently suppress. That is the right call for the shot board,
    where withholding a take would hide the crowd's own evidence. It is the
    wrong call HERE. The review area exists because the author screens working
    cuts on a phone (D17), and a cut published with no record of what made it is
    exactly the debt §7.2 exists to prevent — the loophole is real and was found
    open: `review/beat-11-grow.mp4` is in three cuts and has no sidecar anywhere,
    which is why the morning checklist points at v32 for that take instead of
    republishing it bare.

    So this closes the gap for one directory rather than changing the gate for
    every directory. Three things, on the real yaml:
      1. every named asset exists — a checklist item promising a clip that is
         not in the repo reads to the author as a thing he failed to find
      2. every named asset has a `.meta.yaml` beside it, under either of the two
         naming conventions the pipeline writes
      3. every named asset passes publishable(), so a licence that does not
         grant what CC BY 4.0 offers cannot reach the open web through here
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import yaml
    import build_site as bs
    import licence_gate as lg

    cuts_dir = REPO / "cuts"
    cfg = yaml.safe_load((cuts_dir / "cuts.yaml").read_text(encoding="utf-8")) or {}

    named: list[str] = []
    for cut in cfg.get("cuts") or []:
        named.append(str(cut["file"]))
    for grp in cfg.get("comparisons") or []:
        for p in grp.get("items") or []:
            named += [str(p["left"]), str(p["right"])]
            if (p.get("footnote") or {}).get("file"):
                named.append(str(p["footnote"]["file"]))
    # The checklist's three media slots. `audio:` is narration, judged by ear;
    # `sheets:` is a contact sheet of candidate frames. Both publish exactly
    # like a clip and are gated exactly like one.
    for it in (cfg.get("checklist") or {}).get("items") or []:
        for slot in ("clips", "sheets", "audio"):
            named += [str(x["file"]) for x in (it.get(slot) or [])]

    check("cuts.yaml names at least one asset", bool(named))
    missing = [n for n in named if not (cuts_dir / n).exists()]
    check(f"every asset named in cuts.yaml exists ({len(named)} named)", not missing)
    if missing:
        print("      missing:", ", ".join(missing[:6]))

    present = [n for n in named if (cuts_dir / n).exists()]
    bare = [n for n in present if not lg.sidecar_for(cuts_dir / n, lg.META_EXT)]
    check("every published asset carries a provenance record", not bare)
    if bare:
        print("      no sidecar:", ", ".join(bare[:6]))

    # The licence is classified off the record this test FOUND, not by calling
    # publishable().
    #
    # This was once a workaround and is now belt-and-braces, and the note is
    # kept because the reason it was written matters. publishable() used to look
    # its sidecar up by stem only (`f.with_suffix('.meta.yaml')`), so a
    # full-name record — `beat-05-HELD-moderate.mp4.meta.yaml`, which is what
    # hold_still and video_task write, and which every clip on the checklist
    # is — was invisible to it and it returned "publishable, no sidecar" for a
    # fully documented file. Calling it here would have asserted nothing while
    # looking like it asserted everything: green because the gate never read the
    # file, not because the licence cleared.
    # FIXED 2026-08-07 — publishable() now routes through lg.sidecar_for() and
    # sees both shapes (test_licence_gate pins it). Reading the record directly
    # is kept anyway: this test's job is that the PUBLISHED SET is clean, and it
    # should keep answering that question on its own evidence rather than
    # inheriting whatever the gate currently believes.
    #
    # ONE CLASS OF ASSET CLEARS WITHOUT AN `allow` LICENCE, and it is a founder
    # decision rather than an exception this test grew (2026-08-09). The
    # candidate frames are drawn by animagine-xl-3.1, whose OpenRAIL++ use
    # restrictions travel; he authorised them onto /review — "not like theres any
    # reason to hide it" — and they publish under an offer narrowed to those very
    # restrictions instead of under the site's CC BY 4.0. Granting only what we
    # hold is what makes them publishable, so they are not a hole in this
    # assertion; they are a second way of satisfying it, and it is spelled out
    # here rather than waved through by loosening the check above.
    blocked, narrowed = [], []
    for n in present:
        side = lg.sidecar_for(cuts_dir / n, lg.META_EXT)
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            continue
        cleared = lg.review_narrowed(cuts_dir / n, data)
        for key, value in data.items():
            if key.lower() not in lg.PROVENANCE_KEYS:
                continue
            hits = lg.model_licences(value)
            for licence in dict.fromkeys(l for _m, l in hits):
                if lg.classify(licence)[0] == "allow":
                    continue
                names = [m for m, l in hits if l == licence]
                if cleared and lg.narrowed_model(names):
                    narrowed.append(n)
                    continue
                blocked.append(f"{n} ({key})")
    check("every published asset's own record clears the licence gate", not blocked)
    if blocked:
        print("      withheld:", ", ".join(blocked[:6]))

    # The narrowed set is not allowed to quietly spread. Every member must be in
    # the one directory he named, and the page must say on its face what those
    # images are served under — a licence recorded only in a sidecar nobody opens
    # is a licence recorded nowhere.
    stray = [n for n in set(narrowed) if not n.startswith("review-assets/")]
    check("nothing outside the review gallery publishes on the narrowed offer", not stray)
    if stray:
        print("      stray:", ", ".join(stray[:6]))
    if narrowed:
        gallery = {str(s["file"]) for it in (cfg.get("checklist") or {}).get("items") or []
                   for s in (it.get("sheets") or [])}
        check("every narrowed asset is shown as a sheet, where the licence line prints",
              set(narrowed) <= gallery)


def test_the_review_gallery_clears_on_three_conditions_and_nothing_less(tmp: Path):
    """D15's visibility half, and the three things that have to be true for it.

    THE DECISION. The founder, 2026-08-09: *"put the images from my computer onto
    there please, not like theres any reason to hide it."* That put the candidate
    frames on /review. It did NOT resolve D15 — animagine-xl-3.1 is CreativeML
    Open RAIL++-M, its use restrictions travel to the output, and what the tree
    offers reusers is his call and still open. So the frames publish under an
    offer narrowed to those restrictions rather than under CC BY 4.0, and
    narrowing is what makes them genuinely publishable: we grant nothing we do
    not hold.

    WHY THIS TEST EXISTS RATHER THAN A COMMENT. An exemption in a licence gate is
    the most dangerous shape of code in this repo — every hole the 2026-08-01
    audits found was something that looked like a reasonable special case. This
    one is narrow by construction and each condition closes a different route:

      1. the DIRECTORY he named — `cuts/review-assets/`. A frame that moves out
         is judged with nothing softened, same rule as promoting an archived take.
      2. the RECORD declares the offer (`published_under:`). Without this,
         copying a refused file into the right directory would clear it, and
         writing nothing would be cheaper than writing the truth — hole 2
         ("absence is never safer than presence") in a new hat.
      3. the MODEL is one he authorised. **D16's LTX clips stay refused**: that
         sign-off is a separate open question and it is still his. A model in no
         table stays refused too, because a licence nobody has read cannot be
         narrowed to terms nobody has read.

    And the two halves must agree. licence_gate reports and build_site publishes;
    if they disagreed about which files these are, lint would print a clean tree
    while the build shipped something else. Both ask review_narrowed().
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import yaml
    import build_site as bs
    import licence_gate as lg

    good = {"platform": "local-gpu (rtx5090)",
            "model": "cagliostrolab/animagine-xl-3.1",
            "published_under": "CreativeML Open RAIL++-M use restrictions, not CC BY 4.0"}

    def case(where: str, rec: dict):
        """(publishable, gate_errors) for one record in one directory."""
        root = tmp / where.replace("/", "_")
        d = root / where
        d.mkdir(parents=True, exist_ok=True)
        img = d / f"{len(list(root.rglob('*.jpg')))}.jpg"
        img.write_bytes(b"\xff\xd8\xff\xdb" + b"0" * 64)
        (img.parent / (img.name + ".meta.yaml")).write_text(yaml.safe_dump(rec))
        g = lg.Gate(root)
        side = img.parent / (img.name + ".meta.yaml")
        g.scan_record_file(side, tier=g.tier_of(side))
        # publishable() resolves the gallery by path, so it is asked about the
        # real repo-relative shape rather than the temp root.
        return bs.publishable(img)[0], len(g.errors)

    ok, errs = case("cuts/review-assets", dict(good))
    check("all three conditions: it publishes and is not debt", ok and errs == 0)

    ok, errs = case("cuts/review-assets", {k: v for k, v in good.items()
                                           if k != "published_under"})
    check("no `published_under:` line: refused, and counted", not ok and errs == 1)

    ok, errs = case("cuts/checklist", dict(good))
    check("right record, wrong directory: refused, and counted", not ok and errs == 1)

    # D16 RESOLVED 2026-08-11 (Roman: "i dont see a reason we cant put ltx clips on
    # the site, so sure"), so this case flipped — and the way it flipped is the
    # thing worth pinning. LTX-2.3 does not join FOUNDER_NARROWED and does not use
    # this exemption at all: it is an ALLOW in MODEL_LICENCES, so it publishes on
    # its own licence, with or without a `published_under:` line. The narrowing
    # stayed exactly as narrow as it was; one model stopped needing it.
    ok, errs = case("cuts/review-assets", dict(good, model="Lightricks/LTX-2.3-Distilled"))
    check("D16's LTX publishes in the gallery, on its own licence", ok and errs == 0)
    ok, errs = case("cuts/review-assets",
                    {k: v for k, v in dict(good, model="Lightricks/LTX-2.3-Distilled").items()
                     if k != "published_under"})
    check("...and it does not need the narrowing to do it", ok and errs == 0)
    # the vendor's OTHER document did not move with it — D13 is still open
    ok, errs = case("cuts/review-assets", dict(good, model="Lightricks/LTX-Video"))
    check("LTXV Open Weights 0.X is still refused inside the gallery",
          not ok and errs == 1)

    ok, errs = case("cuts/review-assets", dict(good, model="someone/never-heard-of-it-v9"))
    check("an unclassified model is still refused inside the gallery",
          not ok and errs == 1)

    # The compound string is the one that has bitten before: judging a value by
    # its softest ingredient is hole 1, and an exemption re-opens it if the
    # publish path stops at the first licence it can excuse.
    # (Was written with LTX-2.3 as the unexcused half; D16 cleared that model on
    # 2026-08-11, so the property is re-pinned with LTXV Open Weights 0.X, which is
    # still open under D13. The property under test never changed — only which
    # licence is the one that must not be excused away.)
    ok, errs = case("cuts/review-assets", dict(
        good, model="still: cagliostrolab/animagine-xl-3.1 | motion: Lightricks/LTX-Video"))
    check("animagine beside LTXV 0.X in one value loses on the 0.X clause",
          not ok and errs == 1)

    check("the authorised list names only the D15 model",
          set(lg.FOUNDER_NARROWED) == {"animagine", "cagliostrolab"})
    check("every authorised entry cites the decision that authorised it",
          all("founder" in v and "2026-08-09" in v
              for v in lg.FOUNDER_NARROWED.values()))


def test_review_queue_comes_before_the_record(tmp: Path):
    """What is still his to do renders ABOVE everything already decided.

    The founder, 2026-08-09: *"why is banyan.city/review so big and long? its
    hard to find what to do"*. He is fourteen and screens in five-minute passes
    on a phone, and the page had reached fifty thousand pixels of scroll with
    seven open asks scattered through a week of settled ones. The fix was a
    presentation split — `state: open` first as tight cards, everything else
    folded below — and this test pins the three properties of that split that
    are easy to break by accident while editing the renderer:

      1. AN OPEN ITEM IS ABOVE THE RECORD AND A SETTLED ONE IS BELOW IT. The
         only thing deciding which half an item lands in is its `state`.
      2. NOTHING IS DELETED BY FOLDING. A settled item's body, the page's own
         `why:` and the note that came with the checklist all still print — one
         fold down. "Shorter" must never be implemented as "gone".
      3. THE NUMBER IS `n:`, NOT THE POSITION IN THE LIST. He answers by number
         ("item 12: yes"). Splitting one list into two renumbers everything if
         the loop index is used, so item 12 would silently become item 02 the
         first time an item settled — and his answer would land on the wrong
         thing. The count line is checked with it, because a page that opens by
         claiming a number has to have counted.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import build_site as bs

    cuts = tmp / "cuts"
    cuts.mkdir(parents=True)
    (cuts / "cuts.yaml").write_text("""
page:
  title: "Working cuts"
  eyebrow: "UNLISTED"
  why: "WHY-PROSE-the-page-explains-itself"
checklist:
  title: "the note that came with the list"
  intro: "INTRO-PROSE-that-is-not-an-ask"
  items:
    - n: 4
      ask: "A thing you already answered"
      state: settled
      chip: "CONFIRM"
      body: "SETTLED-BODY-kept-word-for-word"
    - n: 12
      ask: "A thing that is yours to answer"
      state: open
      chip: "SCREEN"
      body: |-
        > `review/somewhere/a-cut.mp4`

        OPEN-BODY-the-argument-behind-the-ask
provenance: "receipts"
""", encoding="utf-8")

    keep_cuts, keep_out = bs.CUTS, bs.OUT
    bs.CUTS, bs.OUT = cuts, tmp / "site"
    try:
        page = bs.render_review()
    finally:
        bs.CUTS, bs.OUT = keep_cuts, keep_out

    def at(needle):
        return page.find(needle)

    record = at('id="record"')
    check("the record section exists", record > 0)
    check("the open item is above the record", 0 < at('id="item-12"') < record)
    check("the settled item is below the record", at('id="item-04"') > record)
    check("the settled item is folded", '<details' in page[at('id="item-04"') - 60:at('id="item-04"')])

    check("nothing folded is deleted — the settled body still prints",
          at("SETTLED-BODY-kept-word-for-word") > record)
    check("the page's own why: survives, behind a fold",
          at("WHY-PROSE-the-page-explains-itself") > record)
    check("the checklist note survives, behind a fold",
          at("INTRO-PROSE-that-is-not-an-ask") > record)

    # The ask stays on the card; the argument goes one fold down, in that order.
    check("the open item's argument is folded under its ask",
          at("A thing that is yours to answer")
          < at("Why we are asking") < at("OPEN-BODY-the-argument-behind-the-ask"))
    check("the card lifts the item's own path as its where-line",
          'class="where"' in page and at("review/somewhere/a-cut.mp4") < at("Why we are asking"))

    check("the number is n:, not the loop index", '<span class="n">12</span>' in page)
    check("no item was renumbered by the split", '<span class="n">02</span>' not in page)
    check("the count line counts the open items", "1 thing needs you" in page)
    check("the count line estimates off the chip (SCREEN = 3 min)",
          "about 3 minutes" in page)


def test_checklist_does_not_reask_a_closed_question():
    """An item on the morning checklist must be open THIS MORNING.

    On 2026-08-07 the author refused v32 with an itemised list. Overnight, two
    of the items on that list were answered by him directly, in the hours
    between the screening and the build: the push-in rate — *"zoom speed ladder
    is just overdoing it. simply make the zoom speed moderate"* — and the
    approach for beats 7 to 9 — *"alright, shot progression"*. Both had finished
    media waiting to be shown to him, a four-rung speed ladder in particular,
    and both were dropped from the checklist rather than published.

    The failure mode this guards is subtle and expensive: the evidence for a
    closed question is usually the most polished thing in the tree, because
    someone just spent an evening making it. Putting it in front of him reads as
    diligence and is actually a request to decide something he has decided —
    with, in the zoom's case, the exact artifact he called "overdoing it".

    Held here rather than in prose because the checklist is edited by whoever is
    on shift, and the two closed questions are precisely the ones whose media is
    sitting on disk looking useful.
    """
    import yaml
    cfg = yaml.safe_load((REPO / "cuts" / "cuts.yaml").read_text(encoding="utf-8")) or {}
    items = (cfg.get("checklist") or {}).get("items") or []
    check("the checklist has items", bool(items))

    # The four rungs are real files and stay unpublished; naming one under a
    # media slot is the mistake, not mentioning the ladder in prose (item 01
    # explains why it is absent, which is the honest thing to do).
    slots = [str(x["file"]) for it in items for slot in ("clips", "sheets", "audio")
             for x in (it.get(slot) or [])]
    ladder = [s for s in slots if "zoom-ladder" in s or "zoom-0p6" in s
              or "zoom-1p5" in s or "zoom-2p5" in s or "zoom-4p0" in s]
    check("no checklist item publishes a rung of the refused speed ladder", not ladder)

    asks = " ".join(str(it.get("ask", "")).lower() for it in items)
    check("no item asks him to pick a zoom speed",
          not ("pick" in asks and "speed" in asks and "zoom" in asks))
    check("no item asks him to pick an approach for 7/8/9",
          "pick an approach" not in asks)

    # The beat-7 trap: he named beat 7 twice — once for draining the colour and
    # once as the first of three identical shots — so ONE replacement frame has
    # to satisfy both notes. Beat 7 therefore belongs to the progression item
    # alone; a separate "beat 7 colour" item would collect two answers for one
    # frame and the second would arrive too late to shoot.
    six = next((it for it in items if "six frames" in str(it.get("ask", "")).lower()), None)
    check("the six-frame item exists", six is not None)
    if six:
        body = str(six.get("body", ""))
        check("beat 7 is not listed among the individually-picked frames",
              "**Beat 7" not in body and "Beat 7 —" not in body)
    prog = next((it for it in items if "7, 8 and 9" in str(it.get("ask", ""))), None)
    check("the progression item exists", prog is not None)
    if prog:
        check("the progression item says its pick also settles the grey note",
              "grey" in str(prog.get("body", "")).lower())


def test_beat11_direction_is_the_founders_revert(tmp: Path):
    """Beat 11's "mitosis" was never there, and the fix for it made the beat worse.

    This test replaces test_beat11_negatives_name_the_mitosis, which held the
    opposite and was right for about eight hours. The founder, screening v32 on
    2026-08-07: "beat 11 actually became worse when we wrongly fixed 'mitosis'
    which was never there, so you should revert it." Two rulings in one sentence
    — the defect was not a defect, and the eight anti-leaf-count terms authored
    against it cost the beat something visible — and both are R4's.

    WHY A TEST AND NOT JUST A REVERT. Everything that argued for those terms is
    still true and still on the record: the f15 take really does show a third
    shape at the apex around frame 20, the frame table in STATE.md 2026-08-07
    really was counted, and the 2.36 median really was the episode's highest. A
    reader who finds that evidence and re-adds the terms will believe they are
    fixing a regression. They are not. Measurement does not outvote the author on
    a taste call; that is the same order as "a metric agreeing with me is not a
    sample" (CLAUDE.md).

    What this holds, on the real genome rather than a fixture:
      1. the direction is the pre-fix sentence, exactly
      2. not one of the eight terms is anywhere in either prompt
      3. anti-static still applies, so the revert did not freeze the beat
      4. BEAT 9 IS NOT REVERTED WITH IT. He corrected the beat number himself
         ("i was talking about BEAT 9"), that re-render was screened and kept,
         and a tidying sweep across "both leaf beats" would undo it.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import video_task as vt
    from generate_shots import parse_shots

    node = REPO / "genomes/sapling/nodes/001-capability-inventory"
    direction = vt.motion_directions(node).get(11, "")
    shot = {s["num"]: s for s in parse_shots((node / "shots.md").read_text(encoding="utf-8"))}[11]
    pos, neg = vt.video_prompt(f"{direction}. no new subjects, no scene change",
                               shot["prompt"], no_anchor=True, beat=11)

    PRE_FIX = ("the new leaf unfurls in a fast sweep and springs upright, dew drops "
               "shaking loose and running off, the light swinging across it")
    check("beat 11's direction is the founder's pre-fix text", direction == PRE_FIX)

    REVERTED = ("splitting leaf", "dividing leaf", "duplicate leaves",
                "extra leaves appearing", "second sprout", "leaf multiplying",
                "changing leaf count", "morphing silhouette")
    present = [w for w in REVERTED if w in neg or w in pos]
    for w in present:
        print(f"      x  beat 11 says '{w}' again — the founder reverted that")
    check("the leaf-count terms are gone from beat 11", not present)
    check(f"beat 11's negative still fits ({len(neg)}/{vt.NEG_MAX} chars)",
          len(neg) <= vt.NEG_MAX)
    check("beat 11 is still forbidden to freeze", "frozen frame" in neg)

    # The revert is beat 11's alone. Beat 9's terms were screened and kept.
    b9 = vt.motion_directions(node).get(9, "")
    check("beat 9 keeps the growth terms the founder did ask for",
          "no growing stem" in b9 and "no extra stem nodes" in b9)


def test_beat09_negatives_forbid_the_growth(tmp: Path):
    """Beat 9's plant does not divide a leaf — it grows a whole new tier of them.

    Counted off the f15 take at frames 0/12/24/36/48/60: the sprout starts as one
    node of leaves low in the grass and ends on a lengthened stem carrying a
    SECOND node, roughly four leaf shapes becoming seven. Beat 11's leaf splits
    and re-fuses; beat 9's plant simply grows — which is beat 11's own line
    ("Latency: three days. Throughput: one leaf") happening two beats early.

    Nothing in the beat asks for it. node.md gives WHOAMI no action at all, only
    "Terminal text types itself over the shot", and shots.md draws "a tiny
    two-leaf green sprout ... quiet empty composition". So growth here is not an
    overshoot to bound, it is invention to forbid outright, and this test holds
    the two halves of that fix:

      1. the COUNT terms, as on beat 11, plus the ones beat 11 never needed —
         a stem that lengthens and grows extra nodes
      2. the direction no longer asks a leaf to leave. The f15 positive said
         "one leaf spinning as it falls"; no negative outvotes an instruction
         (video_prompt: "It was told to"), so the clause had to go from the
         prompt, not be argued with from the negative.

    The still path is deliberately untouched — shots.md is not edited here, and
    09-whoami.png is the founder's canon.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import video_task as vt
    from generate_shots import parse_shots

    node = REPO / "genomes/sapling/nodes/001-capability-inventory"
    direction = vt.motion_directions(node).get(9, "")
    shot = {s["num"]: s for s in parse_shots((node / "shots.md").read_text(encoding="utf-8"))}[9]
    pos, neg = vt.video_prompt(f"{direction}. no new subjects, no scene change",
                               shot["prompt"], no_anchor=True, beat=9)

    WANTED = ("splitting leaf", "dividing leaf", "duplicate leaves",
              "extra leaves appearing", "new leaves growing", "second sprout",
              "leaf multiplying", "changing leaf count", "morphing silhouette",
              "growing stem", "extra stem nodes", "branching stem",
              "timelapse growth", "leaf detaching", "falling leaf")
    absent = [w for w in WANTED if w not in neg]
    for w in absent:
        print(f"      x  beat 9's negative no longer says '{w}'")
    check("beat 9 forbids the plant growing", not absent)
    check("none of it leaked into the positive prompt",
          not any(w in pos for w in WANTED))
    check("the growth terms lead the negative", neg.startswith("splitting leaf"))
    check(f"beat 9's negative still fits ({len(neg)}/{vt.NEG_MAX} chars)",
          len(neg) <= vt.NEG_MAX)
    check("beat 9 is still forbidden to freeze", "frozen frame" in neg)
    # The half a negative cannot do. Both spellings, so restoring either fails.
    check("the direction no longer asks a leaf to fall",
          "spinning as it falls" not in pos and "falls" not in pos)


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


def test_last_beat_action_stops_at_the_beat_list(tmp: Path):
    """The final beat must not be animated with the node's `## Provenance` section.

    BEAT_HEAD.split bounds every beat by the NEXT beat's heading — except the
    last one, whose body runs to end of file and swallows whatever follows the
    beat list. On every node in this tree that is `## Provenance`, so the closing
    beat of all 16 nodes was handing the text encoder "## Provenance
    Shot-granular successor (), steward-written (model: claude-fable-5)" as part
    of its motion brief. Found 2026-08-09 preparing episode 2 beat 21, whose
    direction came back with the provenance line welded onto "the leaf tilts and
    holds".

    Skipping the heading is not enough and that is the point of the test: a
    `continue` drops the `##` line and keeps reading the prose underneath it. The
    beat has to END there.
    """
    import video_task as vt

    node = tmp / "node.md"
    node.write_text(
        "**Open — 0:00–0:05**\n\nThe cursor blinks in an empty terminal.\n\n"
        "**Close — 0:05–0:10**\n\nThe leaf tilts once and holds.\n\n"
        "---\n\n## Provenance\n\nSteward-written (model: claude-fable-5) to the\n"
        "shared spec, and this sentence must never reach a text encoder.\n",
        encoding="utf-8")
    acts = vt.beat_actions(node)
    check("last beat keeps its own action",
          acts.get(2) == "The leaf tilts once and holds")
    check("last beat drops the provenance section",
          "Provenance" not in acts.get(2, "") and "claude" not in acts.get(2, ""))
    check("earlier beats are untouched",
          acts.get(1) == "The cursor blinks in an empty terminal.".rstrip("."))

    # A heading with no rule before it is the 001 shape, and must also terminate.
    node.write_text(
        "**Only — 0:00–0:05**\n\nUnderground, the thump is closer now.\n\n"
        "## Provenance\n\nSteward-written (model: claude-fable-5).\n",
        encoding="utf-8")
    check("a bare heading ends the beat too",
          "Provenance" not in vt.beat_actions(node).get(1, ""))

    # and the live genome must agree, on every node, not just the two we render
    dirty = []
    for nd in sorted((REPO / "genomes/sapling/nodes").glob("*/node.md")):
        acts = vt.beat_actions(nd)
        if not acts:
            continue
        tail = acts[max(acts)]
        if "Provenance" in tail or "Lineage notes" in tail or "claude-fable" in tail:
            dirty.append(nd.parent.name)
    check(f"no live node's last beat carries a section heading ({len(dirty)} dirty)",
          not dirty)


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


def test_nested_licence_does_not_launder(tmp: Path):
    """A licence file three directories down is not the repo's grant either.

    Same failure as `_vendored_licence` matching on filename resemblance, one
    layer out: `fetch_hf_licence_text` took the first sibling whose name
    contained "LICEN" anywhere in the tree. Both directions of that error were
    live on Hugging Face on 2026-08-04, found while recording
    `pipeline/research/models-licence.md`:

      - `IndexTeam/Index-anisora` ships exactly one licence file,
        `reward/weights/bert-base-uncased/LICENSE`, and BERT's Apache text was
        holding a CLEAR verdict over a repo that also carries the
        CogVideoX-based 5B line.
      - `Kijai/WanVideo_comfy` ships exactly one, `LoRAs/Ditto/ditto_LICENSE.txt`,
        CC BY-NC-SA, so it hard-failed for a reason unrelated to its weights.

    Offline: with only nested siblings the fetch must not happen at all, which
    is also what makes it testable in CI.
    """
    import vet_model as vm

    fetched = []

    def stub(url):
        fetched.append(url)
        return 200, "Apache License\nVersion 2.0, January 2004\n"

    real, vm.get_raw = vm.get_raw, stub
    try:
        for repo, nested in (("IndexTeam/Index-anisora",
                              "reward/weights/bert-base-uncased/LICENSE"),
                             ("Kijai/WanVideo_comfy",
                              "LoRAs/Ditto/ditto_LICENSE.txt")):
            got = vm.fetch_hf_licence_text(repo, [{"rfilename": "config.json"},
                                                  {"rfilename": nested}])
            check(f"nested licence is not {repo.split('/')[1]}'s grant",
                  got == (None, ""))
        check("a nested licence is never even fetched", not fetched)
        # and a root file must still be read, or aidealab/AnimeGen-I2V — the one
        # anime model that does ship a real LICENSE — loses it
        name, text = vm.fetch_hf_licence_text(
            "aidealab/AnimeGen-I2V",
            [{"rfilename": "config.json"}, {"rfilename": "LICENSE"}])
        check("a root LICENSE is still read", name == "LICENSE" and "Apache" in text)
    finally:
        vm.get_raw = real

    # The audited chain must stay recorded, and no link of it may read as clear.
    # CASES is checked live by `--self-test` (network, so not here); this asserts
    # only that the record has not lost an entry or gained a permissive one.
    blocked = ("quanhaol/Wan2.2-TI2V-5B-Turbo",
               "hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF",
               "Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF",
               "yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers",
               "Kijai/WanVideo_comfy",
               "IndexTeam/Index-anisora",
               "Disty0/Index-anisora-5B-diffusers",
               "lllyasviel/FramePackI2V_HY")
    recorded = dict(vm.CASES)
    check("no repo is recorded twice in CASES", len(recorded) == len(vm.CASES))
    check("every expected state is one the tool can return",
          all(want in vm.RANK for _, want in vm.CASES))
    check("every repo the audit blocked is still recorded",
          not [r for r in blocked if r not in recorded])
    check("and no blocked repo is recorded as clear",
          all(recorded.get(r) != "clear" for r in blocked))


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
    # ONE check() FOR N OFFENDERS IS A MASK, and it caught its own author.
    # 2026-08-17: a lane adding tests in this file introduced a NEW offender, and
    # because the whole rule was a single check(), the suite's failure tally stayed
    # at 1 — identical to the one pre-existing offender it already had. The new
    # violation was invisible in the count and visible only in these printed
    # lines, which nobody diffs. Same shape as the guard whose call site was
    # unwired and still passed 42 of 47 checks: the tally has to MOVE when a new
    # thing breaks, or the tally is not a measurement. So each offender is its own
    # named assertion, and the aggregate stays as the floor for the empty case.
    for b in bad:
        check(f"a text-mode subprocess read names its encoding: {b}", False)
    check("every text-mode subprocess read names its encoding", not bad)
    # and the file that actually broke must be readable as UTF-8, not as cp1252
    raw = (REPO / "pipeline" / "farm-queue.yaml").read_bytes()
    try:
        raw.decode("utf-8")
        ok = True
    except UnicodeDecodeError:
        ok = False
    check("the farm queue is valid UTF-8", ok)


def test_a_heartbeat_commits_only_the_heartbeat(tmp: Path):
    """The courier's five-minute commit must not sweep up the whole index.

    `Courier.mark()` scoped its `git add` to farm-out/ and then ran a BARE
    `git commit`, which writes everything staged. The checkout on a farm box is
    shared — a human at the machine, a hand-run diagnostic, another script — so
    anything anyone had staged got committed under the message "hb: <stage>" and
    force-pushed to a courier branch that nobody reads for content. Their work,
    filed under our label, on a timer.

    Asserted END TO END rather than by reading the source, because the property
    that matters is git's and not ours: `git commit -- <path>` commits the
    working tree at that path and leaves the rest of the index alone. If that
    ever stopped being true the fix would be silently useless, and a source
    check would still pass.
    """
    import subprocess

    import farm_worker as fw

    repo, origin = tmp / "box-checkout", tmp / "origin.git"
    repo.mkdir()

    def sh(*a):
        return subprocess.run(a, cwd=repo, check=True, capture_output=True,
                              text=True, encoding="utf-8")

    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    sh("git", "init", "-q", "-b", "main")
    sh("git", "config", "user.email", "t@t")
    sh("git", "config", "user.name", "t")
    sh("git", "remote", "add", "origin", str(origin))
    (repo / "README.md").write_text("x\n")
    sh("git", "add", "README.md")
    sh("git", "commit", "-qm", "init")

    # somebody else's work, staged in the shared checkout and not theirs to lose
    (repo / "half-finished.py").write_text("# mid-edit, deliberately staged\n")
    sh("git", "add", "half-finished.py")

    was = fw.REPO
    try:
        fw.REPO = repo
        fw.Courier("testbox").mark("STARTED task=t1")
    finally:
        fw.REPO = was

    committed = sh("git", "show", "--name-only", "--format=", "HEAD").stdout.split()
    staged = sh("git", "diff", "--cached", "--name-only").stdout.split()
    check("the heartbeat itself is committed",
          any(f.startswith("farm-out/") for f in committed))
    check("the other process's staged file is NOT in the heartbeat commit",
          "half-finished.py" not in committed)
    check("...and it is still staged, exactly as they left it",
          "half-finished.py" in staged)


def test_a_busy_card_refuses_the_render():
    """A pre-flight that prints and proceeds is a log line, not a check.

    On 2026-08-07 at 23:09:43 wan_i2v printed "9.7GB of 26GB VRAM is ALREADY IN
    USE before we load anything — another render is probably running" into a
    detached run on the 5090, then loaded the model anyway; at 23:10:31 the
    process died rc=-1073741819 (0xC0000005) with nothing written. The same task
    ran clean the next morning on a free card. The diagnosis was right, printed,
    and unactionable — nobody was standing in front of that terminal.

    The two readings that define the line are both from that one log, which is
    why they are asserted here rather than left as a tuned constant: a clean run
    on the same card ends with "freed between clips: 2.0/26GB still held", so
    residue is normal and must not stop the farm.
    """
    import wan_i2v as W

    check("the collision that crashed would now abort", W.busy_is_fatal(9.7, 26))
    check("the residue a clean run leaves behind would not",
          not W.busy_is_fatal(2.0, 26))
    check("...nor would a little more of it", not W.busy_is_fatal(2.1, 26))
    # the same fraction on the smaller box, where an absolute GB line would either
    # never fire or fire on everything
    check("half of the 12GB box is a collision there too", W.busy_is_fatal(6.0, 12))
    check("and its own residue still is not", not W.busy_is_fatal(2.0, 12))
    check("no card, no verdict", not W.busy_is_fatal(0, 0))
    # the escape hatch has to exist, or the check just breaks the diagnostic that
    # found the contention in the first place
    src = (REPO / "pipeline" / "wan_i2v.py").read_text(encoding="utf-8")
    check("there is a documented way to share the card on purpose",
          "--force-shared-gpu" in src and "BANYAN_ALLOW_SHARED_GPU" in src)
    check("busy has its own exit code, distinct from bad arguments",
          W.RC_GPU_BUSY not in (0, 1, 2))


def test_attempts_survive_a_dead_host():
    """A crash that kills the OS must still spend an attempt.

    The guard used to count `FAIL task=<id>` lines, which only exist if the worker
    SURVIVES the failure. On 2026-08-04 an AnimeGen task crashed its render child
    at 0xC0000005 and then bluescreened the host, so the heartbeat holds one
    STARTED line and nothing else — recorded attempts: zero, forever. A restarted
    worker would re-run the task that took the machine down, every time, and each
    crash would erase the evidence that should have stopped it (DIAG-20260804.md).
    """
    from farm_worker import MAX_ATTEMPTS, heartbeat_attempts

    # the real thing, copied from farm-results-rtx5090's heartbeat.txt
    diag = ("07:12:18Z STARTED task=bench-animegen-b01-1785827400 beats=1 on cuda\n"
            "07:12:22Z VIDEO_VENV_OK\n"
            "07:12:47Z VIDEO_RENDERING beat=01 on animegen (single-process)\n"
            "07:27:56Z VIDEO_ALIVE 15m elapsed, 0 clip(s) done, last output 14m ago\n")
    done, attempts = heartbeat_attempts(diag)
    check("a host-killing crash counts as one attempt (0 before this fix)",
          attempts.get("bench-animegen-b01-1785827400") == 1)
    check("...and one attempt is not yet a giveup",
          attempts["bench-animegen-b01-1785827400"] < MAX_ATTEMPTS)

    # restarted into the same task: two starts, still no FAIL line anywhere
    done, attempts = heartbeat_attempts(diag + diag)
    check("twice through the bluescreen reaches MAX_ATTEMPTS",
          attempts["bench-animegen-b01-1785827400"] >= MAX_ATTEMPTS)
    check("a task that only ever crashed the box is not 'done'", not done)

    # DONE EXCLUDES. Two completed runs of the same id must never read as attempts
    # to give up on — the worker skips them either way, but the courier message
    # would accuse a task that worked.
    ok = ("16:08:52Z STARTED task=faceneg-b01-1785819600 beats=1 on cuda\n"
          "16:13:01Z DONE task=faceneg-b01-1785819600\n") * 2
    done, attempts = heartbeat_attempts(ok)
    check("DONE marks the task done however many starts it took",
          done == {"faceneg-b01-1785819600"})

    # A CONSOLE INTERRUPT IS STILL NOT AN ATTEMPT. The task loop marks INTERRUPTED
    # precisely so a Ctrl+C or a closed window costs nothing; counting its START
    # back in would undo the 2026-08-02 and 2026-08-03 lessons.
    interrupted = ("STARTED task=t1 beats=1 on cuda\n"
                   "INTERRUPTED task=t1 (console interrupt, not counted as an attempt)\n"
                   "STARTED task=t1 beats=1 on cuda\n"
                   "FAIL task=t1\n")
    done, attempts = heartbeat_attempts(interrupted)
    check("an interrupted start costs no attempt", attempts["t1"] == 1)

    # older histories carry FAIL lines without this fix's reading of STARTED
    done, attempts = heartbeat_attempts("FAIL task=old\nFAIL task=old\n")
    check("a legacy FAIL-only history still counts its failures",
          attempts["old"] == 2)

    # RE-QUEUES ARE UNAFFECTED because ids carry an epoch stamp (queue_keeper
    # writes f"{slug}-msi-{stamp}"), so the same work queued again is a new id.
    done, attempts = heartbeat_attempts(diag + diag)
    check("a re-queue under a fresh id starts from zero",
          "bench-animegen-b01-1785900000" not in attempts)


def test_giveup_needs_no_fail_line(tmp: Path):
    """finished_tasks() reads the above off disk and refuses the task."""
    from farm_worker import MAX_ATTEMPTS, finished_tasks

    class Stub:
        out = tmp
    (tmp / "heartbeat.txt").write_text(
        "STARTED task=killer beats=1 on cuda\n"
        "STARTED task=killer beats=1 on cuda\n"
        "STARTED task=fine beats=1 on cuda\n"
        "DONE task=fine\n"
        "STARTED task=once beats=1 on cuda\n", encoding="utf-8")
    # fetch is stubbed to an EMPTY ledger, not left to its default: the default
    # talks to origin, and this suite promises no network in CI.
    skip, gave_up = finished_tasks(Stub(), fetch=lambda: "")
    check("a task started MAX_ATTEMPTS times with no DONE is skipped",
          "killer" in skip and gave_up.get("killer") == MAX_ATTEMPTS)
    check("a completed task is skipped but not accused",
          "fine" in skip and "fine" not in gave_up)
    check("a task with one start left is still runnable",
          "once" not in skip and "once" not in gave_up)


def test_a_hand_ledger_done_stops_a_worker_that_never_ran_it(tmp: Path):
    """finished_tasks() unions the shared farm-results-* ledgers into done.

    A hand-run that borrows a queue id MUST claim it (farm-queue.yaml's 2026-08-08
    ruling), and claim_task publishes those lines to `farm-results-hand`. Until
    this, finished_tasks() opened exactly one file on one disk — so every
    hand-completed id was invisible to every worker and its entry kept reading as
    unstarted. On 2026-08-09 all five entries in `tasks:` were hand-runs on queue
    ids, so a worker revived on the 5090 would have re-rendered the finished ones.

    Three calls this pins, because each is a way the fix could be wrong:
      1. a hand DONE stops the worker exactly like its own DONE;
      2. a hand STARTED or FAIL costs this machine NOTHING — another lane's
         attempts must not be able to exhaust a task's retries here;
      3. a failed read falls back to the local file and NEVER to an empty done
         set, which is the thing that would re-render everything.
    """
    from farm_worker import MAX_ATTEMPTS, finished_tasks

    class Stub:
        out = tmp
    (tmp / "heartbeat.txt").write_text(
        "10:00:00Z STARTED task=mine beats=1 on cuda\n"
        "10:04:00Z DONE task=mine\n"
        "10:05:00Z STARTED task=twice beats=1 on cuda\n"
        "10:09:00Z STARTED task=twice beats=1 on cuda\n", encoding="utf-8")
    hand = ("17:27:06Z STARTED task=ep2-b13-r8-goblin-1786292421 by-hand\n"
            "17:43:29Z DONE task=ep2-b13-r8-goblin-1786292421 by-hand rc=0 4 stills\n"
            "16:16:47Z STARTED task=002b-b12-promptfix-0809 by-hand\n"
            "18:00:00Z FAIL task=002b-b12-promptfix-0809 by-hand\n"
            "18:10:00Z STARTED task=002b-b12-promptfix-0809 by-hand\n"
            "18:20:00Z FAIL task=002b-b12-promptfix-0809 by-hand\n"
            "18:30:00Z STARTED task=002b-b12-promptfix-0809 by-hand\n")

    skip, gave_up = finished_tasks(Stub(), fetch=lambda: hand)
    check("a hand DONE stops a worker that never ran the task",
          "ep2-b13-r8-goblin-1786292421" in skip)
    check("...and it is not accused of having failed",
          "ep2-b13-r8-goblin-1786292421" not in gave_up)
    check("another lane's STARTED and FAIL spend none of THIS worker's attempts",
          "002b-b12-promptfix-0809" not in skip
          and "002b-b12-promptfix-0809" not in gave_up)
    check("this machine's own ledger still counts its own attempts",
          gave_up.get("twice") == MAX_ATTEMPTS and "mine" in skip)

    # A LOCAL GIVEUP THAT SOMEONE ELSE FINISHED IS NOT A GIVEUP. `twice` is two
    # starts with no DONE here; a hand DONE for it means the work exists, so the
    # worker skips it without printing the "fix the cause" accusation.
    skip, gave_up = finished_tasks(Stub(), fetch=lambda: "19:00:00Z DONE task=twice\n")
    check("a hand DONE clears a local giveup instead of accusing it",
          "twice" in skip and "twice" not in gave_up)

    # 3. THE FAILED READ. None is "could not read", and the fallback is the local
    # file — never an empty done set, which is what re-renders everything.
    skip, gave_up = finished_tasks(Stub(), fetch=lambda: None)
    check("an unreadable ledger falls back to the local file, not to empty",
          "mine" in skip and gave_up.get("twice") == MAX_ATTEMPTS)
    check("...and an id only the hand ledger knew about is simply unknown again",
          "ep2-b13-r8-goblin-1786292421" not in skip)

    def boom():
        raise OSError("git not on PATH")
    skip, gave_up = finished_tasks(Stub(), fetch=boom)
    check("a ledger read that RAISES cannot take the worker down with it",
          "mine" in skip)

    # THE SECOND CALL, recorded where it is enforced: every farm-results-* branch,
    # not the hand ledger alone, so a re-imaged box recovers its own history the
    # way queue_promoter.fetch_heartbeats already reads it.
    src = (REPO / "pipeline" / "farm_worker.py").read_text(encoding="utf-8")
    check("the shared read globs every farm-results-* branch, not just hand",
          "refs/heads/farm-results-*:refs/remotes/origin/farm-results-*" in src)
    check("a fetch failure with no readable ref returns None, not an empty ledger",
          'return "" if fetched else None' in src)


def test_child_verdict_names_a_corpse():
    """VIDEO_ALIVE reported a dead render child for fourteen minutes.

    2026-08-04: the child died at 0xC0000005 fifty-six seconds in, and the parent
    kept heartbeating "alive, last output 14m ago" because it was blocked reading
    the pipes of a process Windows Error Reporting was holding open. Then the box
    bluescreened, so the 45-minute stall watchdog never fired at all. Asking
    `poll()` directly is the cheap check that turns that into a named failure
    (DIAG-20260804.md).
    """
    import video_task as vt

    check("a running child that has just spoken is alive",
          vt.child_verdict(None, 0, 0) == ("alive", ""))
    check("an exited child is dead, by exit code, not by inference",
          vt.child_verdict(3221225477, 5, 5)
          == ("dead", "child exited code=3221225477"))
    check("dead outranks stalled — the exit code is the better answer",
          vt.child_verdict(1, 50, 50)[0] == "dead")
    # THE GRACE MINUTE. A healthy child prints "[i/N] wrote ..." immediately before
    # exiting, so its silence is milliseconds; failing a successful render because
    # the tick landed mid-drain would be a worse bug than the one being fixed.
    check("a fresh clean exit mid-drain is not slandered",
          vt.child_verdict(0, 0, 0) == ("alive", ""))
    # the existing watchdog is the backstop, wording unchanged
    check("silence still stalls at STALL_MINUTES",
          vt.child_verdict(None, vt.STALL_MINUTES, 0)
          == ("stalled", f"silent for {vt.STALL_MINUTES}m"))
    check("output without clips still stalls at NO_PROGRESS_MINUTES",
          vt.child_verdict(None, 0, vt.NO_PROGRESS_MINUTES)
          == ("stalled", f"no clip finished in {vt.NO_PROGRESS_MINUTES}m "
                         f"despite output"))
    # HONEST LIMIT, recorded so nobody credits this with more than it does: while
    # the crash dumper has the child suspended, the process has NOT exited and
    # poll() still returns None. On the 2026-08-04 timeline this verdict arrives
    # when WER lets go, not at minute five. It removes up to ~44 minutes of false
    # VIDEO_ALIVE; it does not detect a frozen child.
    check("a child frozen under a crash dumper still reads as alive (known gap)",
          vt.child_verdict(None, 14, 15) == ("alive", ""))


def test_animegen_casts_before_the_second_expert(tmp: Path):
    """Load `hi`, cast `hi`, then load `lo` — one bf16 expert at a time.

    Both A14B transformers used to be loaded in bf16 and cast to fp8 only
    afterwards, so the peak held two ~32 GiB experts: ~64 GiB of host RAM against
    31.4 GB physical on the rtx5090 laptop, i.e. ~33 GB of hard paging, which is
    the diagnosis for the 0xC0000005 this path has died at three times
    (DIAG-20260804.md). Static check because the fix cannot be exercised here — it
    needs the weights and a CUDA card.
    """
    import ast

    src = (REPO / "pipeline" / "wan_i2v.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "load_animegen")
    lines = src.splitlines()
    # where each expert is loaded, and where the fp8 cast of the first one happens
    load_hi = load_lo = cast = None
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            text = "".join(lines[n.lineno - 1:n.end_lineno])
            if 'subfolder="transformer"' in text:
                load_hi = n.lineno
            elif 'subfolder="transformer_2"' in text:
                load_lo = n.lineno
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "cast_fp8" and cast is None):
            cast = n.lineno
    check("load_animegen still loads both experts",
          load_hi is not None and load_lo is not None)
    check("the first expert is cast to fp8 BEFORE the second is loaded",
          cast is not None and load_hi < cast < load_lo)
    # and the reason the LoRA path keeps the old order is written down, not lost:
    # peft would build the adapters in the base layer's dtype, i.e. fp8.
    check("the with-LoRA exception names peft and its dtype",
          "peft" in src and "float8_e4m3fn dtype error" in src)
    check("the fix cites the diagnosis it comes from",
          src.count("DIAG-20260804.md") >= 1)


def test_queue_backlog_is_invisible_to_workers():
    """The `backlog:` key must be a planning list only. Every worker ever shipped
    reads `.get("tasks", [])` off origin/main (farm_worker.py:115) and nothing
    else, including checkouts too old to know the key exists — that invisibility
    is the whole reason planned work can live in the queue file at all. If a
    worker ever learns to read backlog:, gated work starts rendering itself."""
    import yaml as _y

    src = (REPO / "pipeline" / "farm_worker.py").read_text(encoding="utf-8")
    check("the worker still reads only tasks: out of the queue",
          '.get("tasks", [])' in src)
    check("the worker never mentions backlog at all", "backlog" not in src)

    # the read path itself, on a file that carries both lists
    text = ("tasks:\n"
            "- id: old-style-1785000000\n"
            "  worker: msi\n"
            "  node: 001-capability-inventory\n"
            "  beats: '1'\n"
            "backlog:\n"
            "- id: planned-1786000000\n"
            "  runner: farm\n"
            "  gate: founder\n")
    seen = (_y.safe_load(text) or {}).get("tasks", []) or []
    check("an old-style task with no new fields still parses",
          [t["id"] for t in seen] == ["old-style-1785000000"])
    check("nothing from backlog: reaches the worker's task list",
          all("planned" not in t["id"] for t in seen))

    # and an empty tasks: list must not read as a broken queue
    empty = (_y.safe_load("tasks:\nbacklog:\n- id: x\n") or {}).get("tasks", []) or []
    check("an empty tasks: is an empty list, not a crash", empty == [])

    # the real file, parsed, is the thing the workers will actually see
    live = _y.safe_load((REPO / "pipeline" / "farm-queue.yaml").read_text(
        encoding="utf-8")) or {}
    check("the live queue still parses and carries both keys",
          "tasks" in live and "backlog" in live)
    ids = [e.get("id") for e in (live.get("backlog") or [])]
    check("every backlog entry has an id", all(ids) and len(ids) == len(set(ids)))
    check("every backlog entry says why it exists",
          all(e.get("why") for e in (live.get("backlog") or [])))
    check("every gated backlog entry names what specifically",
          all(e.get("gate_ref") for e in (live.get("backlog") or []) if e.get("gate")))


def test_a_revived_worker_cannot_choke_on_the_tasks_list():
    """Every `tasks:` entry a worker would SELECT must be one it can RUN.

    On 2026-08-09 all five entries in tasks: were hand-lane rounds carrying
    `worker: rtx5090` and no `node:` — and render_task subscripts `node`
    directly (farm_worker.py:512 video, :534 stills). So the founder's morning
    login on the 5090 would have had the worker pick up each one, raise
    KeyError('node') before loading a model, and write `FAIL task=<id>` to its
    heartbeat for renders that a hand lane had already finished. Two ledgers
    disagreeing about one id, and neither wrong about itself.

    The fix in the file is `worker: hand` — a handle no machine is ever started
    under — and the fix here is that prose cannot be the enforcement. The check
    reuses queue_promoter.promotable(), which is the same structural test the
    promoter already applies before it puts anything IN this list; running it on
    what is already in the list closes the door hand-editing opens.

    Two halves, because either alone is passable by accident:
      1. `hand` really is unselectable — it is in no capability table, so no
         worker can be started as `--name hand` and match it;
      2. the guard can actually fail — a node-less entry aimed at a real machine
         is rejected, so a green run means the queue is clean, not that the
         check is vacuous.
    """
    import yaml as _y

    from queue_promoter import CAPS, PREFERENCE, promotable

    live = _y.safe_load((REPO / "pipeline" / "farm-queue.yaml").read_text(
        encoding="utf-8")) or {}
    # WAS `len(tasks) > 0`, CHANGED 2026-08-18, and the reason matters because
    # loosening an anti-vacuity guard is exactly the edit that should be argued
    # for rather than made. The guard's job is "this test is looking at
    # something", i.e. catch a file that stopped parsing or a key that got
    # renamed — NOT "there is work queued". On 2026-08-18 the last five entries
    # in tasks: were retired (all five finished 2026-08-09, all five with DONE
    # lines on farm-results-hand the promoter cannot read), and an empty queue is
    # a legitimate, already-tested state: farm_worker.py:143 is null-safe on it
    # and the test above at `tasks:\nbacklog:` asserts that shape on purpose. A
    # green farm should not have to keep a dead entry alive to satisfy a test.
    #
    # So the guard now checks the thing it was protecting: the file parsed and
    # the key is still there. Vacuity of the per-entry loop below is covered by
    # part 2, which feeds promotable() two entries that MUST be rejected — that
    # is what makes a green run mean "the queue is clean" rather than "the check
    # did nothing", and it runs whether tasks: holds five entries or none.
    check("the queue file parses and still has a tasks: key to look at",
          "tasks" in live)
    tasks = live.get("tasks") or []

    # SELECTION IS THE WORKER'S RULE, COPIED EXACTLY: farm_worker.py:680 reads
    # `task.get("worker", "any") not in ("any", a.name)` and skips on true. So an
    # entry is selectable iff its worker is "any" or a handle a machine runs under.
    handles = set(CAPS) | set(PREFERENCE)
    selectable = [e for e in tasks
                  if str(e.get("worker", "any")).strip() in {"any"} | handles]
    for e in selectable:
        why = promotable(e)
        check(f"a worker could actually run {e.get('id')} ({why or 'shaped'})",
              why is None)

    check("`hand` is not a machine handle, so `worker: hand` is never selected",
          "hand" not in handles)
    check("the worker's selection rule is still the one this test copies",
          'task.get("worker", "any") not in ("any", a.name)'
          in (REPO / "pipeline" / "farm_worker.py").read_text(encoding="utf-8"))

    # 2. the guard bites. These are the two shapes that actually reached the file.
    check("a node-less entry aimed at a real machine is rejected",
          promotable({"id": "x", "worker": "rtx5090", "beats": 1})
          == "farm entry names no node")
    check("...and so is one with a node but nothing to render",
          promotable({"id": "x", "worker": "rtx5090", "node": "001-capability-inventory"})
          == "farm entry names neither beats nor a prompt")
    check("a prompt counts instead of beats — that is the worker-shaped round",
          promotable({"id": "x", "worker": "rtx5090",
                      "node": "001-capability-inventory",
                      "slug": "sense", "prompt": "a sprout, no person"}) is None)


def test_queue_promoter_gate_beats_everything():
    """A gate blocks regardless of `after`, and the promoter cannot clear one.

    This is the rule that keeps founder, code and hardware gates human-owned: a
    promoter that could decide a gate was satisfied would be deciding that the
    founder had looked, or that Smart App Control was off, on its own evidence.
    Clearing a gate is a person deleting the key in a commit."""
    from queue_promoter import parse_done, plan, resolve_worker

    # CR-only heartbeats are what the 5090 actually writes; a splitlines() reader
    # sees one line and finds nothing.
    check("DONE ids parse out of a CR-terminated heartbeat",
          parse_done("02:59:53Z DONE task=faceneg-b01-1785819600\r"
                     "03:10:00Z FAIL task=other\r")
          == {"faceneg-b01-1785819600"})

    farm = {"runner": "farm", "node": "001-capability-inventory", "beats": "1"}
    q = {"tasks": [], "backlog": [
        dict(farm, id="ready", worker="msi", after=["done-a", "done-b"]),
        dict(farm, id="half", worker="msi", after=["done-a", "never"]),
        dict(farm, id="gated", worker="msi", after=["done-a", "done-b"],
             gate="founder", gate_ref="pending-founder:v6-verdict"),
        dict(farm, id="gated-no-deps", worker="msi", gate="hardware",
             gate_ref="the box is unreachable"),
    ]}
    p = plan(q, {"done-a", "done-b"})
    check("an entry whose after-ids are all DONE is promoted",
          p["promote"] == ["ready"])
    check("one unmet after-id is enough to hold an entry",
          any(i == "half" and "never" in w for i, w in p["waiting"]))
    check("a gate blocks an entry whose after-ids are ALL satisfied",
          any(i == "gated" and w.startswith("gate:founder") for i, w in p["waiting"]))
    check("a gate blocks an entry with no dependencies at all",
          any(i == "gated-no-deps" and w.startswith("gate:hardware")
              for i, w in p["waiting"]))
    check("the promoter never reports a gated entry as runnable by hand",
          not any(i in ("gated", "gated-no-deps") for i, _ in p["by_hand"]))

    # window is advisory: machine work is scheduled by dependencies, not hours
    p2 = plan({"tasks": [], "backlog": [
        dict(farm, id="night", worker="msi", window="overnight"),
        dict(farm, id="day", worker="msi", window="day")]}, set())
    check("window never delays a promotion", sorted(p2["promote"]) == ["day", "night"])

    # manual work is never put in a worker's inbox
    p3 = plan({"tasks": [], "backlog": [
        {"id": "byhand", "runner": "manual", "worker": "m1pro", "cmd": "bash x.sh"}]},
        set())
    check("a manual entry is reported, never promoted",
          not p3["promote"] and p3["by_hand"] == [("byhand", "bash x.sh")])

    # nothing goes into tasks: that a worker could not run
    p4 = plan({"tasks": [], "backlog": [
        {"id": "nonode", "runner": "farm", "worker": "msi", "beats": "1"},
        {"id": "nobeats", "runner": "farm", "worker": "msi", "node": "001-x"},
        {"id": "nowho", "runner": "farm", "node": "001-x", "beats": "1"},
        {"id": "impossible", "runner": "farm", "node": "001-x", "beats": "1",
         "needs": ["mps", "vram20"]}]}, set())
    check("a farm entry with no node is refused, not queued", not p4["promote"])
    check("all four malformed entries are reported with a reason",
          len(p4["waiting"]) == 4 and all("not queue-shaped" in w
                                          for _, w in p4["waiting"]))

    # worker is filled from needs, and stays a plain string (farm_worker:488
    # compares it by equality, so a list would never match any machine)
    w, why = resolve_worker({"needs": ["mps"]})
    check("needs [mps] resolves to the Mac", w == "m1pro" and "needs" in why)
    w, _ = resolve_worker({"needs": ["cuda", "vram20"]})
    check("needs [cuda, vram20] resolves to the 26GB box", w == "rtx5090")
    w, _ = resolve_worker({"worker": "msi", "needs": ["cuda", "vram20"]})
    check("an explicit worker always wins over needs", w == "msi")
    w, _ = resolve_worker({"worker": ["msi", "rtx5090"]})
    check("a list worker is refused rather than written", w is None)


def test_queue_promotion_is_one_atomic_move():
    """A promotion moves the dict from one list to the other in a single write,
    so the two lists can never disagree — and everything it does not touch comes
    out byte-identical, because the comments in this file are the record of why
    each parked job stays parked."""
    import yaml as _y
    from queue_promoter import blocks, plan, rewrite, verify

    text = (
        "tasks:\n"
        "# a parked job, and ninety lines of why it must stay parked\n"
        "# - id: parked\n"
        "#   worker: rtx5090\n"
        "- id: finished-1785819600\n"
        "  worker: rtx5090\n"
        "  node: 001-capability-inventory\n"
        "  beats: '1'\n"
        "\n"
        "backlog:\n"
        "\n"
        "# the reason this entry exists, which must travel with it\n"
        "- id: moves-1786000000\n"
        "  runner: farm\n"
        "  needs: [mps]\n"
        "  node: 001-capability-inventory\n"
        "  beats: '7'\n"
        "  why: >-\n"
        "    a consumer, named\n"
        "\n"
        "- id: stays-1786000001\n"
        "  runner: farm\n"
        "  worker: msi\n"
        "  node: 001-capability-inventory\n"
        "  beats: '2'\n"
        "  gate: hardware\n"
        "  gate_ref: the box is unreachable\n")

    q = _y.safe_load(text)
    p = plan(q, {"finished-1785819600"})
    check("a task with a DONE heartbeat line is retired",
          p["retire"] == ["finished-1785819600"])
    check("a FAIL-only task would not be retired (only DONE was matched)",
          plan(q, set())["retire"] == [])

    new = rewrite(text, p["retire"], p["promote"], p["assign"], "2026-08-07")
    verify(text, new, p["retire"], p["promote"])       # raises SystemExit if not
    after = _y.safe_load(new)
    t_ids = [e["id"] for e in (after.get("tasks") or [])]
    b_ids = [e["id"] for e in (after.get("backlog") or [])]
    check("the promoted entry is in tasks: exactly once", t_ids == ["moves-1786000000"])
    check("...and is gone from backlog: in the same write",
          b_ids == ["stays-1786000001"])
    check("no entry is ever in both lists", not (set(t_ids) & set(b_ids)))
    check("the retired task is in neither list",
          "finished-1785819600" not in t_ids + b_ids)
    check("worker was filled in from needs on the way across",
          after["tasks"][0]["worker"] == "m1pro")
    check("the promoted entry is otherwise unchanged",
          after["tasks"][0]["beats"] == "7" and after["tasks"][0]["why"].strip()
          == "a consumer, named")
    check("the gated entry survives untouched",
          after["backlog"][0]["gate"] == "hardware")

    # the comments, which is the half yaml.safe_dump cannot do
    check("the parked job's reasoning is still in the file",
          "ninety lines of why it must stay parked" in new
          and "#   worker: rtx5090" in new)
    check("the moved entry's own comment moved with it",
          new.index("the reason this entry exists")
          < new.index("- id: moves-1786000000") < new.index("backlog:"))
    check("the promotion says where it came from",
          "promoted from backlog 2026-08-07" in new)

    # a second run has nothing left to do — safe on a timer
    p2 = plan(_y.safe_load(new), {"finished-1785819600"})
    check("re-running promotes nothing and retires nothing",
          not p2["promote"] and not p2["retire"])

    # the block walk must not swallow a comment block it merely sits under
    pre, bl, tail = blocks(["# park line one",
                            "# park line two",
                            "",
                            "# mine",
                            "- id: a",
                            "  worker: msi"])
    check("a blank line stops a block reaching back into the park above it",
          len(bl) == 1 and bl[0] == ["# mine", "- id: a", "  worker: msi"]
          and pre == ["# park line one", "# park line two", ""])
    # and with no blank line at all, the run is region preamble and stays put
    pre2, bl2, _ = blocks(["# park with no blank under it",
                           "# - id: parked",
                           "- id: a",
                           "  worker: msi"])
    check("a comment run touching the top of the region is never carried off",
          bl2 == [["- id: a", "  worker: msi"]] and len(pre2) == 2)


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
    # "ltx-2-3" joined this list on 2026-08-05, when MODEL_LICENCE gained an
    # fp8 key whose model string resolves to it and to nothing else. It is the
    # licence the LTX candidate actually ships under, it was already in the
    # table, and it was the one LTX key with no tripwire on it — so a future
    # reword of its value into an explanation could have flipped a watch-only
    # candidate to publishable in silence, which is the precise failure the
    # comment above describes.
    # IT LEFT THIS LIST ON 2026-08-11, because D16 is resolved and the flip is now
    # a founder decision rather than an accident: Roman, "i dont see a reason we
    # cant put ltx clips on the site, so sure." The tripwire does not disappear
    # with it — it turns over, below — because an allow value has the same defect
    # in mirror image: a reworded explanation could make it stop matching, or make
    # it match on a pattern that was never about this document.
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
    # THE OTHER HALF OF THE SAME TRIPWIRE, for the entry that moved. D16's
    # allowance has to come from the LTX-2 document being NAMED, not from some
    # other identifier drifting into the value: the founder cleared LTX-2.3, and a
    # value that cleared because it happened to contain "MIT" or "CC BY" would be
    # the google-flow failure running forwards instead of backwards.
    for name in ("ltx-2-3", "ltx-2-3-distilled"):
        value = lg.MODEL_LICENCES[name]
        check(f"{name} is publishable — D16 resolved 2026-08-11",
              lg.classify(value)[0] == "allow")
        check(f"...and {name} clears on the LTX-2 document, not another licence",
              lg.classify(value)[1] == "LTX-2 Community License Agreement")
    # the allowance is about the document, so it must not reach the vendor: LTXV
    # Open Weights 0.X is D13's question and is still the founder's.
    check("the LTX-2 allow pattern does not clear the LTXV 0.X catch-all",
          lg.classify(lg.MODEL_LICENCES["lightricks"])[0] != "allow")

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

    def tree3(name, files):
        """tree(), but keeping the candidates bucket scan() drops (2026-08-07).
        A takes/ finding is still a finding; it is just counted elsewhere."""
        root = tmp / name
        for rel, body in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        return lg.scan_all(root)

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
    # accepts --clips <ANY dir> and build_site publishes takes/clips/ too.
    # These assert COVERAGE — that the sweep SEES a record wherever it sits.
    # Which bucket it lands in is the tier's business and is asserted further
    # down; takes/ became a candidate rather than an error on 2026-08-07, so
    # 'is seen' is counted as errors + candidates here. Reading it out of
    # `errors` alone would have made this test quietly stop testing coverage
    # the day the tier landed, while still passing for the other two paths.
    NC_VO = '{"engine": "f5-tts-v1-base", "lines": []}'
    for i, (label, rel) in enumerate((("takes/clips", f"{N}/takes/clips/01-vo.json"),
                                      ("a dir nobody hard-coded", f"{N}/renders/01-vo.json"),
                                      ("a renamed manifest", f"{N}/clips/take-final.json"))):
        errors, _, cands = tree3(f"cov-vo-{i}", {rel: NC_VO})
        check(f"an NC VO manifest in {label} is seen", len(errors) + len(cands) == 1)
    errors, _, cands = tree3("cov-takes-sidecar",
                             {f"{N}/takes/clips/01-a.meta.yaml": "platform: pixverse-web\n"})
    errors = errors + cands
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

    # ---- THE RIGHT REFUSAL FOR THE WRONG REASON: a vendor catch-all outranked
    # the version key that exists to beat it. 2026-08-08.
    #
    # The keys are matched as substrings of one normalised string, so a sidecar
    # naming both the vendor and the version matches both keys — and
    # model_licences ordered its hits by len(name), so the 10-character
    # `lightricks` catch-all (LTXV Open Weights 0.X) beat the 7-character
    # `ltx-2-3` (LTX-2 Community Licence, a different document with a 20-item use
    # schedule 0.X does not have). The clip was refused either way, which is why
    # it survived three days: the verdict was right and only the citation was
    # wrong. A gate that refuses for the wrong reason sends the next person to
    # read the wrong licence.
    #
    # The string below is verbatim from review/ep2-b01/ltx-b01.mp4.meta.yaml —
    # video_task.MODEL_LICENCE["ltx23-distilled"], what our own renderer writes —
    # rather than a shortened stand-in, because the bug was in how the two keys
    # collide inside a REAL provenance value.
    LTX23 = "diffusers/LTX-2.3-Distilled-Diffusers (Lightricks LTX-2.3 distilled, bf16)"
    check("a real LTX-2.3 sidecar string resolves to the version, not the vendor",
          "lightricks" not in [n for n, _ in lg.model_licences(LTX23)])
    check("...so the document cited is the LTX-2 Community License (D16)",
          "LTX-2 Community License" in (lg.engine_licence(LTX23) or ""))
    check("...and not the LTXV Open Weights 0.X the catch-all names",
          "0.X" not in (lg.engine_licence(LTX23) or ""))
    # WHICH DOCUMENT IT IS was always the point of this block; the verdict on that
    # document was a separate question and it has now been answered. D16 RESOLVED
    # 2026-08-11 — Roman: "i dont see a reason we cant put ltx clips on the site,
    # so sure." So the line that used to read "the refusal itself is unchanged"
    # asserts the founder's answer instead, and it asserts it here, against the
    # real sidecar string, rather than only against the table entry.
    check("...and that document is now an allow — D16, founder 2026-08-11",
          lg.classify(lg.engine_licence(LTX23))[0] == "allow")
    errors, _ = tree("ltx23-document", {f"{N}/clips/01-a.meta.yaml":
                                        f"platform: local-gpu (rtx5090)\nmodel: {LTX23}\n"})
    check("a real LTX-2.3 sidecar is no longer debt", errors == [])
    # THE SPELLING MUST NOT DECIDE IT. The same render whose value omits the bare
    # `LTX-2.3` identifier — what video_task writes when it names only the
    # checkpoint — grades as a variant of `ltx-2-3` and was demoted to UNINHERITED,
    # i.e. refused on a spelling while its twin published. `ltx-2-3-distilled` is
    # in the table for this, and it is the read-the-version rule, not an inheritance.
    BARE = "diffusers/LTX-2.3-Distilled-Diffusers"
    check("the distilled checkpoint named alone clears on the same document",
          lg.classify(lg.engine_licence(BARE))[0] == "allow"
          and "LTX-2 Community License" in lg.engine_licence(BARE))
    # and the fail-closed direction is untouched: an LTX-2.3 SOMETHING nobody read
    # is a variant, is demoted, and is refused — the allowance covers checkpoints,
    # never the version number.
    UNREAD_23 = "Lightricks/LTX-2.3-Turbo-Unread"
    check("an unread LTX-2.3 variant is still refused",
          lg.classify(lg.engine_licence(UNREAD_23))[0] != "allow")
    check("...and it says which reading it is not",
          lg.UNINHERITED_MARK in (lg.engine_licence(UNREAD_23) or ""))
    # THE OTHER DIRECTION, and the reason the catch-all is dropped only for a
    # version we have READ rather than for anything else that matched. "Defer to
    # whatever else is in the string" would clear an unlisted Lightricks model the
    # moment its sidecar also named our own GPU — allow-by-inheritance, the one
    # direction that publishes things (the voxcpm2 entry's rule).
    UNLISTED = "Lightricks/LTX-9-preview on local-gpu (rtx5090)"
    check("an LTX version in no table still falls to the vendor catch-all",
          lg.classify(lg.engine_licence(UNLISTED))[0] != "allow")
    check("...and our own compute standing beside it does not clear it",
          "lightricks" in [n for n, _ in lg.model_licences(UNLISTED)])
    # and the archived 0.X takes keep their own document: supersession is
    # per-version, so ltx-video answers for LTX-Video exactly as it always did
    check("an LTX-Video string is still judged under LTXV Open Weights 0.X",
          "0.X" in (lg.engine_licence("Lightricks/LTX-Video") or ""))
    check("every SUPERSEDES_CATCH_ALL key is a model this table has classified",
          all(k in lg.MODEL_LICENCES and v in lg.MODEL_LICENCES
              for k, v in lg.SUPERSEDES_CATCH_ALL.items()))

    # ---- AN ALLOWANCE MUST NEVER TRAVEL TO A NAME NOBODY READ. 2026-08-08, the
    # other half of the same queue entry as the block above.
    #
    # Keys were matched as substrings of the whole normalised value, which leaks
    # in two directions, and the morning's fix only closed one of them:
    #   * SUFFIX — `fastwan` contains `wan`, so the gate answered Apache-2.0 for
    #     a model in no table, having read nothing. It was RIGHT (FastVideo's
    #     LICENSE is Apache-2.0, read separately in db26f7b), and that is why it
    #     lived: the accident agreed with the truth once, so nothing looked odd.
    #   * FINETUNE — `Lykon/dreamshaper-8-anything` contains `dreamshaper`, so
    #     every LoRA, merge and finetune of a listed base cleared on its base's
    #     licence.
    # Both are now graded per IDENTIFIER (licence_gate._match_grade): an allow is
    # honoured where the key NAMES the identifier, and a variant of it is demoted
    # to UNINHERITED unless declared in ALLOW_INHERITS.
    check("a suffix is not a match — fastwan inherits nothing from wan",
          lg.model_licences("fastwan") == [] and lg.engine_licence("fastwan") is None)
    check("...so an unlisted model containing a known key fails CLOSED",
          lg.classify(lg.engine_licence("fastwan") or "")[0] == "unknown")
    FINETUNE = "Lykon/dreamshaper-8-anything"
    check("a finetune of an allowed base does not inherit the base's allowance",
          lg.classify(lg.engine_licence(FINETUNE))[0] != "allow")
    check("...and the report still names what it resembles, so the reading is findable",
          [n for n, _ in lg.model_licences(FINETUNE)] == ["dreamshaper"])
    check("...while the base itself is untouched — the real sidecar string still clears",
          lg.engine_licence("Lykon/dreamshaper-8") == "CreativeML-OpenRAIL-M")
    # the version direction the voxcpm2 entry documented in 2026-08-01 and then
    # left to discipline ("add every new version explicitly, never rely on the
    # prefix"). A fused numeric suffix is now a version, and a version is
    # different weights: enforced, not remembered.
    check("a version fused onto an allowed key is a different model",
          lg.classify(lg.engine_licence("VoxCPM3"))[0] != "allow")
    check("...while the two versions somebody DID read still resolve",
          lg.engine_licence("VoxCPM-0.5B") == "Apache-2.0"
          and lg.engine_licence("voxcpm2") == "Apache-2.0")
    # A DEMOTION MUST SURVIVE STANDING NEXT TO AN ALLOW. Dropping the hit instead
    # of demoting it would go silent the moment the same sidecar also named our own
    # GPU — "no hits" reads as "nothing to check", which is how the record with the
    # least provenance becomes the cheapest (hole 2).
    errors, _ = tree("finetune-inherit", {f"{N}/clips/01-a.meta.yaml":
                                          f"platform: local-gpu (rtx5090)\nmodel: {FINETUNE}\n"})
    check("an unread finetune is a violation even beside our own compute",
          len(errors) == 1 and "dreamshaper" in errors[0])
    check("every UNINHERITED value classifies non-allow, whatever the model is called",
          all(lg.classify(lg.UNINHERITED.format(name=n))[0] != "allow"
              for n in lg.MODEL_LICENCES))
    check("UNINHERITED_MARK still identifies its own wording",
          lg.UNINHERITED_MARK in lg.UNINHERITED.format(name="x"))
    # a withheld asset's reason lands on a public page, and build_site strips
    # everything after an em dash as internal bookkeeping. So the wording keeps
    # the part a stranger can act on ("unread variant of dreamshaper") in front
    # of the dash and the explanation behind it — same convention as the
    # MODEL_LICENCES values with '(read; founder sign-off pending)' tails.
    import build_site as _bs_lic
    check("the public form of a demoted licence is a readable name, not a paragraph",
          _bs_lic.public_licence(lg.UNINHERITED.format(name="dreamshaper"))
          == "unread variant of dreamshaper")
    check("every ALLOW_INHERITS key is in the table and its licence really is an allow",
          all(k in lg.MODEL_LICENCES
              and lg.classify(lg.MODEL_LICENCES[k])[0] == "allow"
              and isinstance(why, str) and why
              for k, why in lg.ALLOW_INHERITS.items()))
    # THE STRINGS THE TREE ACTUALLY WRITES, verbatim, because the risk in a
    # matcher rewrite is not the hazard it closes — it is the 385 chatterbox
    # sidecars, the 245 local-gpu ones and the 235 animagine ones it must leave
    # exactly as they were. Each of these is a real value out of a real record;
    # a licence-gate change that reclassifies a shipped asset moves the ratchet,
    # and the ratchet is the only thing asserting nothing new became unpublishable.
    UNCHANGED = {
        # cuts/**/*-vo.json and genomes/**/clips/*.meta.yaml
        "chatterbox-0.5B": "MIT",
        "chatterbox-0.5B (per-line emotional direction)": "MIT",
        "kokoro-onnx (kokoro-82M)": "Apache-2.0",
        # a parameter count, a machine nickname, a script name and a path are all
        # packaging — none of them is another model
        "local-gpu (rtx5090)": "CC-BY-4.0 (our own output)",
        "local-gpu (MSI)": "CC-BY-4.0 (our own output)",
        "local-mps (pipeline/synth_vo.py, synth_vo v3)": "CC-BY-4.0 (our own output)",
        "local-deterministic (pipeline/hold_still.py, render_t3.py, ffmpeg)":
            "CC-BY-4.0 (our own output)",
        "local deterministic (post_motion.py)": "CC-BY-4.0 (our own output)",
        "kaggle-free-gpu": "CC-BY-4.0 (our own output)",
        # a key spanning three whitespace-separated words still matches — and the
        # platform grant is what this value has always resolved to, which is also
        # the honest answer: the wan entry says the hosted previews publish no
        # weights, so Model Studio's terms are the document, not Apache-2.0
        "wan2.7-t2v (Alibaba Model Studio API)": "provider terms: commercial-output-grant",
        "fal-ai/minimax/hailuo-2.3/standard/image-to-video":
            "provider terms: commercial-output-grant",
        "claude-fable-5": "provider terms: commercial-output-grant",
        # and every restricted one stays restricted, judged by its worst clause
        "cagliostrolab/animagine-xl-3.1": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
        "f5-tts-v1-base": "CC-BY-NC-4.0",
        "PixVerse V6": "free-tier ToS: personal-use only, non-commercial",
        "Veo 3.1 (Google Flow free tier)":
            "Google ToS: output conditions we cannot pass on, plus watermark",
    }
    wrong = {v: lg.engine_licence(v) for v, want in UNCHANGED.items()
             if lg.engine_licence(v) != want}
    check(f"the {len(UNCHANGED)} real provenance strings in the tree resolve "
          f"exactly as before{'' if not wrong else f' — got {wrong}'}", not wrong)
    SVD_PAIR = ("still: Lykon/dreamshaper-8 (+IP-Adapter 0.35) | "
                "motion: stabilityai/stable-video-diffusion-img2vid-xt")
    check("the 16 compound SVD sidecars still name all three of their models",
          {n for n, _ in lg.model_licences(SVD_PAIR)}
          == {"dreamshaper", "ip-adapter", "stable-video-diffusion"})
    check("...and are still refused on the motion model",
          "non-commercial" in lg.classify(lg.engine_licence(SVD_PAIR))[1])

    # ---- the CANDIDATE tier: takes/ is scoped out of the ratchet, not hidden --
    # 2026-08-07. A candidate-stills wave wrote 40 honest sidecars into one
    # node's takes/stills/ in a single night and took the debt 38 -> 78, forty
    # lines all restating one open decision (D15: animagine-xl-3.1 is CreativeML
    # Open RAIL++-M). The ratchet counts violations, so it was tracking how many
    # frames a batch happened to shoot rather than how much liability the tree
    # carries. Frames shot to be chosen between are not canon and must not move
    # a canon count — but they must never go quiet either, which is what these
    # assertions pin.
    RAIL = "model: cagliostrolab/animagine-xl-3.1\n"
    # the SAME sidecar, moved between two directories — the only difference
    canon_errs, _, canon_cands = tree3(
        "cand-canon", {f"{N}/stills/06-blue.png.meta.yaml": RAIL})
    take_errs, _, take_cands = tree3(
        "cand-takes", {f"{N}/takes/stills/06-blue.png.meta.yaml": RAIL})
    check("a RAIL-licenced sidecar in canon stills/ is counted debt",
          len(canon_errs) == 1 and "animagine" in canon_errs[0] and canon_cands == [])
    check("...and the identical sidecar under takes/ raises debt by nothing",
          take_errs == [])
    check("...but it IS still classified and reported as a candidate",
          len(take_cands) == 1 and "animagine" in take_cands[0])
    check("the candidate line says why it is not counted, not merely that it is not",
          "not counted against the debt ratchet" in take_cands[0]
          and "promoting it" in take_cands[0])
    # promotion is what changes the verdict — the same rule an archive follows
    promoted, _, _ = tree3("cand-promoted",
                           {f"{N}/clips/06-blue.mp4.meta.yaml": RAIL})
    check("promoting a candidate into clips/ makes it fatal again",
          len(promoted) == 1)
    # takes/archive/ is both; archived is the more specific statement and wins
    arch_e, arch_a, arch_c = tree3("cand-archived",
                                   {f"{N}/takes/archive/06-blue.png.meta.yaml": RAIL})
    check("an archived take under takes/ stays an advisory, not a candidate",
          arch_e == [] and arch_c == [] and len(arch_a) == 1)

    # THE EXEMPTION STOPS EXACTLY WHERE publishable() STOPS. Everything below
    # leaves engine_licence() returning None, which publishable() treats as
    # `continue` — so build_site copies the file to the website. If takes/ let
    # these off too, writing a vague record would be cheaper than writing an
    # honest one, and hole 2 would be back in through a new door.
    vague, _, vague_c = tree3("cand-unclassified",
                              {f"{N}/takes/stills/07-x.png.meta.yaml":
                               "model: some-model-nobody-classified\n"})
    check("an UNCLASSIFIED model under takes/ is still hard debt",
          len(vague) == 1 and vague_c == [])
    silent, _, silent_c = tree3("cand-silent",
                                {f"{N}/takes/stills/07-x.png.meta.yaml":
                                 "prompt: a mug falls\nseed: 7\n"})
    check("a takes/ sidecar declaring no provenance at all is still hard debt",
          len(silent) == 1 and "not a note" in silent[0] and silent_c == [])
    bare, _, bare_c = tree3("cand-bare", {f"{N}/takes/clips/02-b.mp4": "mp4"})
    check("a takes/ clip with no record beside it is still hard debt",
          len(bare) == 1 and "no provenance" in bare[0] and bare_c == [])
    # and the founder's switch must not be narrowed by any of the above
    check("scan() keeps its two-value contract for callers that only ask 'ships?'",
          len(lg.scan(tmp / "cand-takes")) == 2)

    # ---- the publish gate this scoping RESTS ON must be able to read ---------
    # takes/ is exempt from the debt count only because publishable() withholds
    # an unpublishable candidate from the site. That premise was false until
    # 2026-08-07: publishable() looked its sidecar up with f.with_suffix(), which
    # REPLACES the final extension instead of appending, so it could only ever
    # build `06-blue.meta.yaml` and never `06-blue.png.meta.yaml` — the shape
    # hold_still, video_task and the farm's stills all write. A missing sidecar
    # takes publishable()'s "unprovenanced is the gate's finding" branch and
    # returns True, so the newer naming convention did not merely go unchecked:
    # writing a correct record was the thing that made the frame publishable.
    # The fifth stem-only reader of the five, and the only one on the gate.
    import build_site as _bs
    stills_dir = tmp / "pub-gate"
    stills_dir.mkdir(parents=True, exist_ok=True)
    frame = stills_dir / "06-blue.png"
    frame.write_bytes(b"png")
    check("a frame with no record at all is the gate's finding, not the build's",
          _bs.publishable(frame) == (True, ""))
    (stills_dir / "06-blue.png.meta.yaml").write_text(RAIL)
    ok, why = _bs.publishable(frame)
    check("a FULL-NAME sidecar carrying a withheld licence blocks publication",
          ok is False and "RAIL" in why)
    # the older stem shape must keep working — this is a widening, not a swap
    frame2 = stills_dir / "07-green.png"
    frame2.write_bytes(b"png")
    (stills_dir / "07-green.meta.yaml").write_text(RAIL)
    check("...and the stem-shape sidecar still blocks it too",
          _bs.publishable(frame2)[0] is False)
    # a full-name sidecar naming a CLEARED model must still publish, or the fix
    # would just be a blanket refusal wearing a reader's clothes
    frame3 = stills_dir / "08-ok.png"
    frame3.write_bytes(b"png")
    (stills_dir / "08-ok.png.meta.yaml").write_text("model: aidealab/AnimeGen-I2V\n")
    check("a full-name sidecar naming an Apache-2.0 model still publishes",
          _bs.publishable(frame3) == (True, ""))

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


def _tiny_git_repo(tmp: Path) -> Path:
    """A real repository, because the thing under test is git's own answer.

    Faking `git ls-files` would test the mock. The bug being closed here was a
    disagreement between what one disk holds and what the repository holds, and
    only a repository can be asked that.
    """
    import subprocess
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(tmp)] + cmd, check=True,
                       capture_output=True)
    return tmp


def _commit_all(tmp: Path) -> None:
    import subprocess
    subprocess.run(["git", "-C", str(tmp), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "commit", "-q", "-m", "x"],
                   check=True, capture_output=True)


def test_the_board_links_only_frames_the_deploy_has(tmp: Path):
    """A candidate frame that is not in the tree gets no link on the site.

    THE FAILURE (2026-08-08, diagnosed three times in one day as a broken site).
    Candidate frames are gitignored on purpose — `takes/**/*.png`, ~1 MB each,
    dozens per beat — so they live on the box that drew them and nowhere else.
    `variant_cells` listed every PNG it could see on disk, which on that box
    meant 164 <a href>s into 002b frames the repository does not carry.
    `check_links` failed the build over them, correctly. CI, having none of the
    files, emitted no such links and stayed green. Same commit, exit 1 here and
    exit 0 there, and the difference read as "the site is broken locally".

    So the assertion is the invariant, not the symptom: what the board links is
    a function of the repository, which is the thing every box shares.
    """
    import build_shotboard as bsb

    repo = _tiny_git_repo(tmp)
    (repo / ".gitignore").write_text("takes/**/*.png\n")
    stills = repo / "takes" / "stills"
    stills.mkdir(parents=True)
    kept, ignored = stills / "01-a.png", stills / "01-b.png"
    for p in (kept, ignored):
        p.write_bytes(b"pixels")
    # `kept` is committed over the ignore rule the way 001's takes/ archive is —
    # ignoring never untracks, and a tracked file ships.
    import subprocess
    subprocess.run(["git", "-C", str(repo), "add", "-f", str(kept)],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", str(repo / ".gitignore")],
                   check=True, capture_output=True)
    _commit_all(repo)

    thumb = bsb.still_thumb
    bsb.still_thumb = lambda *a, **k: ""      # no ffmpeg, no writes into _site
    try:
        site = bsb.variant_cells(stills, 1, rel="m", genome="g")
        local = bsb.variant_cells(stills, 1, rel="", genome="g")
    finally:
        bsb.still_thumb = thumb

    check("site board links the frame the tree carries", "m-takes/01-a.png" in site)
    check("site board does NOT link the ignored frame", "01-b.png" not in site)
    # The local review board is the reason those uncommitted frames exist: beats
    # get judged on it before anything is committed. It must keep showing both.
    check("standalone board still shows both candidates",
          local.count("<figure") == 2 and "data:image" in local)
    check("standalone board emits no site-relative hrefs", "-takes/" not in local)


def test_a_frame_the_tree_carries_but_the_licence_blocks_is_named_not_linked(tmp: Path):
    """publishable() decides pictures the way it already decided clips.

    `take_cell` has always drawn a "not published here" panel for a motion take
    whose licence forbids redistribution, because the build never copies that
    file and a <video> pointing at it would be a dead player. `variant_cells`
    linked candidate stills with no licence question asked at all, so a tracked
    frame that publishable() refuses would be an <a href> to a file the build
    deliberately did not copy — a 404 for the visitor and a red build for us,
    this time on CI too. In the tree AND publishable are two conditions and both
    have to hold before a link is emitted.
    """
    import build_shotboard as bsb

    repo = _tiny_git_repo(tmp)
    stills = repo / "takes" / "stills"
    stills.mkdir(parents=True)
    (stills / "01-a.png").write_bytes(b"pixels")
    # The real shape of 001's withheld frames: a render record naming a model
    # whose licence carries use restrictions CC BY 4.0 cannot pass on.
    (stills / "01-a.png.meta.yaml").write_text(
        "model: cagliostrolab/animagine-xl-3.1\n")
    _commit_all(repo)

    thumb = bsb.still_thumb
    bsb.still_thumb = lambda *a, **k: ""
    try:
        site = bsb.variant_cells(stills, 1, rel="m", genome="g")
    finally:
        bsb.still_thumb = thumb

    check("a licence-blocked frame is listed", "<figure" in site)
    check("a licence-blocked frame is not linked", "m-takes/01-a.png" not in site)
    check("and the page says why", "not published here" in site
          and "CreativeML" in site)


def test_no_git_never_silently_empties_the_board(tmp: Path):
    """"git cannot answer" must not read as "the tree is empty".

    in_the_tree() is the one gate that can remove content from the site, so its
    failure mode matters more than its success. A tarball export, a build box
    with no git binary, a directory outside any repository: all three return
    nothing from `ls-files`, and treating that as "nothing is tracked" would
    publish a shot board with every take stripped out of it and no error
    anywhere. Absence of an answer falls back to what the disk holds, which is
    exactly what every build did before this gate existed.
    """
    import build_site as bs

    plain = tmp / "not-a-repo"
    plain.mkdir()
    files = [plain / "01-a.png", plain / "01-b.png"]
    for p in files:
        p.write_bytes(b"pixels")
    check("outside a repo, every file is kept", bs.in_the_tree(files) == files)

    repo = tmp / "repo"
    repo.mkdir()
    _tiny_git_repo(repo)
    stills = repo / "takes"
    stills.mkdir()
    empty = [stills / "01-c.png"]
    empty[0].write_bytes(b"pixels")
    # A real repo that tracks nothing here IS an answer, and it is obeyed.
    check("inside a repo, an untracked file is dropped", bs.in_the_tree(empty) == [])


# ====================================================================== #
# A POSTER IS A PROMISE ABOUT PIXELS — review-poster-names-stale-still-1786197251
#
# The defect, in one sentence: a review-page clip's poster was resolved by the
# FILENAME its record gives, so promoting a new canon still under an existing
# name re-postered every older clip drawn from the old pixels, and the page
# showed a tall sapling over footage of bare soil. It was invisible locally
# because `poster()` only reaches the still fallback when ffmpeg is missing —
# which is the Vercel build image, i.e. only the deployed page lied, only on the
# surface the founder actually screens from.
#
# These pin `build_site.still_from_record()` (which pixels does this clip hold)
# and `build_site.poster_still()` (what a record naming no still at all gets).
# Both are pure: they read files, no ffmpeg, no page build.
# ====================================================================== #


def _stills_dir(root: Path, node: str, files: dict) -> Path:
    """One node's stills/, the shape still_dirs() hands the resolver."""
    d = root / node / "stills"
    d.mkdir(parents=True)
    for name, data in files.items():
        (d / name).write_bytes(data)
    return d


def test_a_promoted_still_does_not_reposter_an_older_clip(tmp: Path):
    """THE REGRESSION TEST THE QUEUE ENTRY ASKED FOR, as the tree really does it.

    R6 keeps a retired frame in place under a `-REVOKED-<why>` name, so after a
    promotion the canon filename holds NEW pixels and the old ones are still on
    disk beside it. Identical bytes are the identical picture, so the clip's true
    frame is findable — and a resolver that goes by name shows the wrong one.
    """
    import hashlib

    import build_site as bs

    OLD, NEW = b"bare soil, beat 15 as shot", b"tall sapling, promoted later"
    old_sha, new_sha = hashlib.sha256(OLD).hexdigest(), hashlib.sha256(NEW).hexdigest()
    d = _stills_dir(tmp, "001-x", {"15-coming.png": NEW,
                                   "15-coming-REVOKED-underground.png": OLD})
    clip = tmp / "beat-15-animated.mp4"
    clip.write_bytes(b"an mp4")

    got, why = bs.still_from_record(
        {"init_still": "15-coming.png", "init_still_sha256": old_sha}, clip, [d])
    check("a clip drawn from the old pixels posters the OLD file, not the promoted name",
          got is not None and got.name == "15-coming-REVOKED-underground.png")
    check("...silently, with no warning, because this is a correct answer and not a repair",
          why == "")
    check("...and the bytes handed back are the bytes the record names",
          got is not None and bs.bytes_sha256(got) == old_sha)

    # The same shape of record, on a clip drawn AFTER the promotion.
    got2, why2 = bs.still_from_record(
        {"init_still": "15-coming.png", "init_still_sha256": new_sha}, clip, [d])
    check("a clip drawn from the pixels the name still holds posters the name itself",
          got2 is not None and got2.name == "15-coming.png" and why2 == "")
    # `source_still` is what hold_still.py writes; `init_still` is the renderers'.
    got3, _ = bs.still_from_record(
        {"source_still": "15-coming.png", "source_still_sha256": old_sha}, clip, [d])
    check("both record dialects are read — hold_still's source_still resolves too",
          got3 is not None and got3.name == "15-coming-REVOKED-underground.png")


def test_a_record_we_cannot_honour_gets_no_poster_at_all(tmp: Path):
    """No poster beats a wrong poster, and "no record" is not "cannot honour".

    Four refusals and one sentinel. The sentinel matters as much as the
    refusals: `(None, "")` means the record claims nothing, so the caller stays
    free to fall back, while `(None, why)` means the record made a claim we
    could not verify and the caller must show nothing.
    """
    import hashlib

    import build_site as bs

    d = _stills_dir(tmp, "001-x", {"12-undefined.png": b"cracked grey"})
    clip = tmp / "beat-12-animated.mp4"
    clip.write_bytes(b"an mp4")

    gone = hashlib.sha256(b"pixels nobody kept").hexdigest()
    got, why = bs.still_from_record(
        {"init_still": "12-undefined.png", "init_still_sha256": gone}, clip, [d])
    check("a recorded hash no file on disk has → no poster", got is None)
    check("...and the warning names the clip and the hash, so it is findable",
          clip.name in why and gone[:12] in why)

    got, why = bs.still_from_record({"init_still": "99-not-here.png"}, clip, [d])
    check("a named still in no node's stills/ → no poster, with a reason",
          got is None and "no node" in why)

    d2 = _stills_dir(tmp, "002b-y", {"12-undefined.png": b"a different picture"})
    got, why = bs.still_from_record({"init_still": "12-undefined.png"}, clip, [d, d2])
    check("one name, two nodes, no hash → refuse rather than pick one",
          got is None and "2 nodes" in why)

    got, why = bs.still_from_record({}, clip, [d])
    check("a record that names no still returns the free-to-fall-back sentinel",
          got is None and why == "")


def test_a_hashless_name_that_changed_hands_is_refused(tmp: Path):
    """The only evidence available when a record carries no hash: file age.

    Stated in still_from_record's docstring and repeated here because the limit
    is the point — mtime is a property of the checkout, so this rule catches a
    stranded clip on a working copy and cannot fire on a fresh clone. It is the
    reason the published cuts' records were backfilled with measured hashes.
    """
    import os

    import build_site as bs

    d = _stills_dir(tmp, "001-x", {"07-zero.png": b"grayened, promoted later"})
    still = d / "07-zero.png"
    clip = tmp / "beat-07-zoom-gentle.mp4"
    clip.write_bytes(b"an mp4")
    born = clip.stat().st_mtime

    os.utime(still, (born + bs.STILL_MTIME_SLACK + 60,) * 2)
    got, why = bs.still_from_record({"source_still": "07-zero.png"}, clip, [d])
    check("no hash, and the file under that name is newer than the clip → refuse",
          got is None and "re-promoted" in why)

    os.utime(still, (born - 60,) * 2)
    got, why = bs.still_from_record({"source_still": "07-zero.png"}, clip, [d])
    check("no hash, and the name is no newer than the clip → trust the name",
          got is not None and got.name == "07-zero.png" and why == "")

    # Clock skew and a fresh checkout must not read as a promotion.
    os.utime(still, (born + bs.STILL_MTIME_SLACK - 30,) * 2)
    got, _ = bs.still_from_record({"source_still": "07-zero.png"}, clip, [d])
    check("...and a few minutes of skew is slack, not evidence", got is not None)


def test_a_shot_that_records_no_still_gets_no_poster(tmp: Path):
    """An assembly may borrow the node's still. A single shot may not.

    The live case, 2026-08-08: `checklist/002b-b01-5b.mp4` is an EPISODE 2
    beat-1 render whose record names no still, and the old blanket fallback gave
    it episode 1's `09-whoami.png` — another beat of another episode — as its
    poster wherever ffmpeg is absent, which is the deploy.
    """
    import build_site as bs

    d = _stills_dir(tmp, "001-x", {"09-whoami.png": b"a beat 9 frame"})
    node_still = d / "09-whoami.png"

    shot = tmp / "002b-b01-5b.mp4"
    shot.write_bytes(b"an mp4")
    got, why = bs.poster_still({"shot_beat": 1, "model": "Wan-AI/Wan2.2-TI2V-5B"},
                               shot, [d], node_still)
    check("a one-shot record naming no still gets no poster, not another beat's frame",
          got is None and "names no still at all" in why and shot.name in why)

    film = tmp / "ep1-v32-gentleholds.mp4"
    film.write_bytes(b"an mp4")
    got, why = bs.poster_still({"model": "per-beat — see sources",
                                "sources": [{"part": "animated beats"}]},
                               film, [d], node_still)
    check("a whole-episode assembly still shows the node's approved still",
          got == node_still and why == "")

    # poster_still must not soften a refusal still_from_record already made.
    got, why = bs.poster_still({"init_still": "nope.png"}, film, [d], node_still)
    check("an unhonourable record is refused even for an assembly",
          got is None and why != "")


def test_a_held_clip_records_the_bytes_it_was_handed(tmp: Path):
    """hold_still writes the hash, so a held beat is defended on Vercel too.

    `source_still: <name>` was the only frame reference this tool wrote, and the
    resolver's one other defence — "the file under that name is newer than the
    clip" — CANNOT FIRE ON THE DEPLOY, because a fresh clone stamps every file
    with the checkout time. So every held clip ever made was right on a laptop
    and undefended on banyan.city, which is the only surface the founder screens
    from. Measured off the bytes the function was handed, never looked up by name
    afterwards: looking it up later is the failure being closed.
    """
    import hashlib

    import yaml

    import build_site as bs

    PIXELS = b"beat 14 as it was drawn: bare soil, low horizon"
    stills = _stills_dir(tmp, "001-x", {"14-worth-staying-in.png": PIXELS})
    clip = tmp / "beat-14-HELD-gentle.mp4"
    clip.write_bytes(b"a computed push-in")
    hs.sidecar(clip, stills / "14-worth-staying-in.png", 14, 2.5, zoom_total_used=0.12)
    data = yaml.safe_load(Path(str(clip) + ".meta.yaml").read_text(encoding="utf-8"))

    check("the held sidecar records the sha256 of exactly those bytes",
          data.get("source_still_sha256") == hashlib.sha256(PIXELS).hexdigest())
    check("...beside the name, which is kept for a reader",
          data.get("source_still") == "14-worth-staying-in.png")
    # The three classifier-input lines are untouched — pinned again here because
    # this edit landed in the same function and hold_still's own comments say
    # what each one breaks.
    check("the classifier lines above it are unchanged",
          data["platform"] == "local-deterministic (pipeline/hold_still.py, ffmpeg)"
          and data["model"] == "none"
          and str(data["model_licence"]).startswith("n/a — inherits the still's licence"))
    # False boilerplate removed: this tool holds whatever frame it is handed, and
    # several of those are provisional picks the founder has not seen. Approval
    # is the T0 leaf's word (§6), not this file's to assert.
    check("the prompt no longer claims an approval nobody gave",
          "the chosen still is held" in str(data["prompt"])
          and "approved" not in str(data["prompt"]))

    # AND THE POINT OF THE HASH: the canon filename is re-promoted onto different
    # pixels, R6 keeps the old frame in place under a -REVOKED- name, and this
    # clip still posters the frame it actually holds.
    (stills / "14-worth-staying-in-REVOKED-too-tall.png").write_bytes(PIXELS)
    (stills / "14-worth-staying-in.png").write_bytes(b"a redraw promoted later")
    got, why = bs.still_from_record(data, clip, [stills])
    check("after a re-promotion the held clip posters its own pixels, not the name",
          got is not None and got.name == "14-worth-staying-in-REVOKED-too-tall.png"
          and why == "")
    check("...and those really are the bytes the sidecar recorded",
          got is not None and bs.bytes_sha256(got) == data["source_still_sha256"])


def test_a_held_pick_the_founder_has_not_seen_says_so_in_its_own_record(tmp: Path):
    """The PROVISIONAL label is written by the tool or it is not written.

    Beat 06 was the only beat in episode 1 with no approved frame — he refused
    r3 ("women, too many clouds") and r4 ("its getting worse") — so v34 holds a
    STEWARD PICK there, `b06-r5-s2`, out of `takes/stills/`. v33 did the same
    thing and carried the same three lines, and they were appended to the
    sidecar BY HAND after hold_still had written it. That is the defect f7de075
    named one directory over: the label lives outside the tool, so it survives
    exactly as long as somebody remembers it.

    Two halves and they cannot come apart, because one call writes both: a
    BANNER a person sees at the top of the file, and `provisional: true` for
    anything that decides what may be published. Plus the frame's PATH — a pick
    in `takes/stills/` is not findable by name in the canon directories, so a
    bare `source_still:` names pixels no resolver can reach.
    """
    import yaml

    takes = tmp / "takes" / "stills"
    takes.mkdir(parents=True)
    frame = takes / "06-too-blue-r5-s2.png"
    frame.write_bytes(b"low cloud, mostly blue, nobody in it")
    clip = tmp / "06-too-blue.mp4"
    clip.write_bytes(b"a computed push-in")

    hs.sidecar(clip, frame, 6, 4.87, zoom_total_used=0.12,
               provisional_reason="PROVISIONAL PICK b06-r5-s2 (conf 0.55)")
    text = Path(str(clip) + ".meta.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    check("a provisional hold says PROVISIONAL before anything else in the file",
          text.lstrip().startswith("# ====") and "PROVISIONAL" in text.split("\n")[1])
    check("...and says it again where a gate can read it",
          data.get("provisional") is True
          and "b06-r5-s2" in str(data.get("provisional_reason")))
    check("the frame's directory is on the record, not just its name",
          str(data.get("source_still_path")).endswith(
              "takes/stills/06-too-blue-r5-s2.png")
          and data.get("source_still") == "06-too-blue-r5-s2.png")
    # THE BANNER IS A COMMENT AND THE CLASSIFIER LINES ARE UNMOVED. Putting six
    # lines above `platform:` is exactly the sort of edit that takes licence_gate
    # down with it — SENTINELS matches `model:` on the whole value, render_t3
    # substring-matches "model: none" to decide whether to ping-pong the clip.
    check("the three classifier lines survive the banner",
          data["platform"] == "local-deterministic (pipeline/hold_still.py, ffmpeg)"
          and data["model"] == "none"
          and "model: none" in text)

    # AND THE DEFAULT IS SILENT: a canon hold must not grow a provisional stamp,
    # or the word stops meaning anything on the clips that carry it.
    plain = tmp / "10-sense.mp4"
    plain.write_bytes(b"another push-in")
    hs.sidecar(plain, frame, 10, 2.5, zoom_total_used=0.12)
    ptext = Path(str(plain) + ".meta.yaml").read_text(encoding="utf-8")
    check("a hold with no reason given carries no provisional stamp at all",
          "PROVISIONAL" not in ptext
          and yaml.safe_load(ptext).get("provisional") is None)


def test_the_nested_init_frame_dialect_resolves_like_the_flat_one(tmp: Path):
    """Episode 2's cold open was blank while its own record held the answer.

    video_task's LTX/Wan renders write the frame as a NESTED mapping —
    `init_frame: {path:, sha256:, plate_sha256:, …}` — and the resolver read only
    the flat dialects, so it saw a record naming no still at all while two lines
    down the same record carried sha256 7cc22aa1…, which is a frame on disk.
    Two traps, and both are in here: the path is written with WINDOWS separators
    (and a backslash is a legal posix filename character, so Path().name returns
    the whole string instead of raising), and `plate_sha256` is the 704x1280
    cover-crop fed to the model, which exists nowhere the resolver looks —
    recording it would produce a refusal instead of a poster.
    """
    import hashlib

    import build_site as bs

    PIXELS = b"01-cold-open as episode 2 was filmed from it"
    sha = hashlib.sha256(PIXELS).hexdigest()
    plate = hashlib.sha256(b"the 704x1280 cover crop, which is nowhere").hexdigest()
    d = _stills_dir(tmp, "002b-first-citizen", {"01-cold-open.png": PIXELS})
    clip = tmp / "wan5b-b01-v2.mp4"
    clip.write_bytes(b"an mp4")

    nested = {"init_frame": {
        "path": r"genomes\sapling\nodes\002b-first-citizen\stills\01-cold-open.png",
        "sha256": sha, "plate_wxh": "704x1280",
        "plate_path": r"C:\banyan-farm\b01\01-704x1280.png", "plate_sha256": plate}}
    flat = {"init_still": "01-cold-open.png", "init_still_sha256": sha}
    check("the nested dialect resolves to the same still the flat one does",
          bs.still_from_record(nested, clip, [d]) == bs.still_from_record(flat, clip, [d]))
    check("...and that is the frame, not a blank",
          bs.still_from_record(nested, clip, [d])[0].name == "01-cold-open.png")
    check("the Windows path is read as a basename, not swallowed whole",
          bs.record_still_claim(nested)[0] == "01-cold-open.png")
    check("plate_sha256 is never mistaken for the frame",
          bs.record_still_claim(nested)[1] == sha)
    # Proof that reading the plate hash would have COST something rather than
    # being merely untidy: those bytes are in no stills/ dir, so it refuses.
    only_plate = {"init_frame": {"path": "01-cold-open.png", "sha256": plate}}
    check("...which matters, because the plate hash resolves to nothing at all",
          bs.still_from_record(only_plate, clip, [d])[0] is None)

    # A CORRECTION OUTRANKS THE RENDER-TIME FIELD, which is how a frame recovered
    # out of git history reaches the resolver without rewriting what the renderer
    # wrote. Same convention licence_gate reads as corrected_model.
    (d / "01-cold-open-REVOKED-too-tall.png").write_bytes(PIXELS)
    (d / "01-cold-open.png").write_bytes(b"a redraw promoted onto the same name")
    corrected = {"corrections": [{"date": "2026-08-09", "field": "init_still",
                                  "corrected_init_still": "01-cold-open-REVOKED-too-tall.png",
                                  "corrected_init_still_sha256": sha}]}
    got, why = bs.still_from_record(corrected, clip, [d])
    check("a backfilled correction resolves the poster it names",
          got is not None and got.name == "01-cold-open-REVOKED-too-tall.png" and why == "")

    # THE LIVE CLIP THE BACKFILL WAS WRITTEN FOR. Episode 2 beat 1 is the next
    # thing the founder screens after episode 1, and it must poster the frame it
    # holds rather than whatever owns the name `01-cold-open.png` today.
    import yaml

    import licence_gate as lg
    served = REPO / "cuts" / "checklist" / "002b-b01-5b.mp4"
    side = lg.sidecar_for(served, lg.META_EXT)
    rec = yaml.safe_load(side.read_text(encoding="utf-8"))
    got, why = bs.still_from_record(rec, served, bs.still_dirs())
    check("the served episode-2 cold open is no longer a blank player",
          got is not None and why == "")
    check("...and it posters the frame it was filmed from, by bytes",
          got is not None and bs.bytes_sha256(got).startswith("7cc22aa1"))
    check("...which is the RETIRED file, not whatever holds the canon name now",
          got is not None and "REVOKED" in got.name)


def test_every_served_cut_posters_the_frame_its_record_names():
    """The live review surface, on the real tree — not a fixture.

    The invariant, for every clip `cuts/cuts.yaml` actually serves: if its
    record states the hash of the still it was drawn from, the poster the build
    resolves holds EXACTLY those bytes. That is the whole fix, asserted against
    the files the founder will screen rather than against a mock, and it stays
    true across any future promotion — which is what makes it worth running
    forever rather than once.
    """
    import yaml

    import build_site as bs
    import licence_gate as lg

    cfg = yaml.safe_load((bs.CUTS / "cuts.yaml").read_text(encoding="utf-8")) or {}
    named: list[str] = [str(c["file"]) for c in (cfg.get("cuts") or [])]
    for grp in cfg.get("comparisons") or []:
        for p in grp.get("items") or []:
            named += [str(p["left"]), str(p["right"])]
            if (p.get("footnote") or {}).get("file"):
                named.append(str(p["footnote"]["file"]))
    for it in (cfg.get("checklist") or {}).get("items") or []:
        named += [str(x["file"]) for x in (it.get("clips") or [])]

    dirs = bs.still_dirs()
    check(f"the resolver can see every node's stills/ ({len(dirs)} dirs)", len(dirs) >= 1)

    hashed, wrong, stale_name, blank = 0, [], 0, []
    for rel in sorted(set(named)):
        src = bs.CUTS / rel
        if not src.exists() or src.suffix.lower() not in lg.VIDEO_EXT:
            continue
        side = lg.sidecar_for(src, lg.META_EXT)
        if not side:
            continue                      # a different test's finding, not this one's
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            continue
        want = str(data.get("init_still_sha256")
                   or data.get("source_still_sha256") or "").strip().lower()
        got, why = bs.still_from_record(data, src, dirs)
        if want:
            hashed += 1
            if got is None or bs.bytes_sha256(got) != want:
                wrong.append(rel)
            elif got.name != str(data.get("init_still") or data.get("source_still") or ""):
                stale_name += 1           # the name changed hands; bytes found it anyway
        elif why:
            blank.append(rel)

    check(f"at least one served cut records the hash of its still ({hashed} do)", hashed >= 1)
    check(f"every one of those {hashed} posters those exact bytes"
          + ("" if not wrong else f" — WRONG: {', '.join(wrong)}"), not wrong)
    # Not an assertion about the number, which any promotion or backfill moves —
    # printed so a reviewer can see the renamed-bytes path is live traffic and
    # not a hypothetical the tests invented.
    print(f"      · {stale_name} served cut(s) postered from a file that no longer "
          f"holds the name their record gives")
    if blank:
        print(f"      · {len(blank)} served cut(s) get NO poster (record cannot be "
              f"honoured): {', '.join(sorted(blank)[:6])}")


def test_the_infra_meter_never_prints_a_number_the_page_did_not_measure():
    """D18's monitoring line: a meter, and an honest one.

    Over $100 of build time in under a month, because every courier heartbeat
    triggered a full rebuild — and the first anyone knew was the invoice, because
    nothing in this repo reported it. The allowlist stopped the spending; this is
    the half that makes it legible.

    THE FAILURE MODE OF A METER IS NOT BEING WRONG, IT IS BEING REASSURING. So
    the page ships with no count in it at all — not zero, not the last one seen —
    and the browser either measures one or the tile says in words that it could
    not. These pin that contract, plus the two mechanical things that would break
    it silently: a variable the script reads and build() forgets to emit, and a
    source that stops being free.
    """
    import re

    import build_sim as bs
    import build_status as d

    m = d.infra_meter()
    src = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")

    check("the tile's copy carries every string it can need, including failure",
          all(str(m.get(k, "")).strip()
              for k in ("api", "title", "counting", "unavailable",
                        "unit_one", "unit_many", "note")))
    # The number slot ships holding `counting`, and neither that string nor the
    # failure string may contain a digit — a "0" or a "—" in there would read as
    # a measurement. The unit strings do carry the window ("last 24 hours"),
    # which is a label on the question and not an answer to it.
    check("the number slot ships with no digit in it at all",
          not any(ch.isdigit() for ch in m["counting"] + m["unavailable"]))
    check("...and the slot the server renders is that placeholder",
          f'id="infra-n">{{_e(meter["counting"])}}' in src)
    check("an unavailable number is said in words, not shown as 0 or a dash",
          "not put a number on it" in m["unavailable"])

    # $0 AND PUBLIC. The moment this needs a token or a paid plan it is not a
    # source this project may use — the whole entry exists because a meter cost
    # money to read. environment=Production is filtered server-side because two
    # thirds of this repo's deployments are the free github-pages mirror.
    # Owner-derived, not owner-spelled. The repo changed hands on 2026-08-10 and
    # this assertion was one of the things pinning the old name in place; a test
    # that has to be edited by hand at every move is a test that will be edited
    # wrongly. What matters here is the HOST and the ENDPOINT — the two things
    # that make the meter free and public — so those are what get named.
    import repo_slug
    check("the source is GitHub's public deployments list", m["api"].startswith(
        f"{repo_slug.API_URL}/deployments?"))
    check("...on api.github.com, which needs no account to read",
          m["api"].startswith("https://api.github.com/repos/"))
    check("...filtered to the builds that are actually billed",
          "environment=Production" in m["api"])
    check("...and carries no token, key or secret of any kind",
          not any(w in m["api"].lower() for w in ("token", "access_token", "key=", "auth")))

    # EVERY IDENTIFIER THE SCRIPT READS MUST BE EMITTED. This is the bug that
    # nearly shipped: INFRA_HOURS was read by the fetch and defined nowhere, and
    # an undefined global in a .catch()-wrapped promise fails SILENTLY into the
    # "unavailable" branch — a meter that says GitHub did not answer when GitHub
    # answered fine. No browser here, so it is checked structurally.
    used = set(re.findall(r"\bINFRA_[A-Z_]+\b", bs.INFRA_JS))
    block = re.search(r"var INFRA_API =.*?;", src, re.S)
    emitted = set(re.findall(r"\bINFRA_[A-Z_]+\b", block.group(0) if block else ""))
    check(f"every INFRA_* the script reads is emitted by build() ({len(used)} of them)",
          bool(used) and used <= emitted)
    check("...and nothing is emitted that the script never reads",
          not (emitted - used))
    check("the script is wired into the page it is written for",
          "{INFRA_JS}" in src and 'id="infra-n"' in src and 'id="infra-u"' in src)

    # NOT A VITAL. The meter is fetched live and can be absent, so it must
    # never dress as a repo-checkable number. The four-tile vitals row it once
    # sat beside died in the 2026-08-11 revamp (its numbers moved into the
    # grove and the glance strip), so the assertion is now the row's absence:
    # if a vitals row ever comes back, this test asks the question again.
    check("the meter is its own tile, and no vitals row exists to absorb it",
          'class="infra rise"' in src and '<div class="vital">' not in src)


# ====================================================================== #
# A HAND-RUN THAT BORROWS A QUEUE ID CLAIMS IT
# — queue-id-borrowed-by-hand-run-1786190580, the lead's ruling of 2026-08-08
#
# `002b-b01-video-5b-1786089900` asked for seconds 2.5; the clip carrying that
# id in its sidecar is 4.71s and no `DONE task=` line for it exists anywhere. The
# render was hand-run with the queue entry's id and a different recipe, so the
# promoter could not retire the entry and it read as unstarted while its output
# was already on the review page. The ruling: a hand-run carrying a queue id MUST
# write the STARTED/DONE lines. claim_task.py is what makes that the short path.
#
# These pin the parts that break silently: the LINE FORMAT (every reader keys on
# `task=(\S+)`, and a line the readers cannot parse is worse than no line), the
# exit-code mapping, and the refusal to claim an id nobody filed.
# ====================================================================== #


def test_a_hand_claim_writes_lines_every_reader_already_parses():
    """The line format is the contract, and its two readers are the test.

    farm_worker.heartbeat_attempts() decides whether a task is retried and
    queue_promoter.parse_done() decides whether it is retired. A helper that
    writes a line neither of them keys on would be worse than writing nothing:
    it would look like a claim in the log and count for nothing anywhere.
    """
    import claim_task as ct
    import farm_worker as fw
    import queue_promoter as qp

    tid = "002b-b01-video-5b-1786089900"
    started = ct.heartbeat_line("started", tid, note="hand-run, ltx_i2v")
    done = ct.heartbeat_line("done", tid)

    check("a hand STARTED line is stamped and marks the id",
          started.split()[1] == "STARTED" and f"task={tid}" in started)
    check("a note follows the id and never joins it — \\S+ would swallow it",
          f"task={tid} " in started and started.rstrip().endswith("ltx_i2v"))

    log = "\n".join([started, done]) + "\n"
    done_ids, attempts = fw.heartbeat_attempts(log)
    check("the worker's own reader sees the task as done", done_ids == {tid})
    # The DONE set is what excludes a finished task from being picked up again
    # (finished_tasks reads it); the attempt count just records honestly that one
    # run happened. Both come off the same two lines.
    check("...and the same lines record exactly one run of it", attempts.get(tid) == 1)
    check("the promoter's DONE reader retires on the same line", qp.parse_done(log) == {tid})

    # INTERRUPTED subtracts a start, exactly as it does for the worker — a Ctrl+C
    # in a hand-run must not spend an attempt either.
    stopped = "\n".join([ct.heartbeat_line("started", tid),
                         ct.heartbeat_line("interrupted", tid)]) + "\n"
    check("an interrupted hand-run costs no attempt",
          fw.heartbeat_attempts(stopped)[1].get(tid, 0) == 0)
    failed = "\n".join([ct.heartbeat_line("started", tid),
                        ct.heartbeat_line("fail", tid, note="OOM")]) + "\n"
    check("a failed hand-run counts as one attempt, like the worker's",
          fw.heartbeat_attempts(failed)[1].get(tid) == 1)

    # The append log is never rewritten: two starts are two attempts, and a
    # helper that de-duplicated them would hand a crash loop a fresh budget.
    twice = ct.append_line(ct.append_line("", ct.heartbeat_line("started", tid)),
                           ct.heartbeat_line("started", tid))
    check("two claims of the same id are two attempts, not one",
          fw.heartbeat_attempts(twice)[1].get(tid) == 2)
    check("append_line repairs a heartbeat that lost its final newline",
          ct.append_line("07:00:00Z STARTED task=x", "07:01:00Z DONE task=x")
          == "07:00:00Z STARTED task=x\n07:01:00Z DONE task=x\n")

    # --at: the hour the work FINISHED, for a claim written after the fact. The
    # log is the record, so a mark typed at 14:00 for a job that ended at 09:00
    # should say 09:00 — the alternative is losing the hour or burying it in
    # free text, which is what the 2026-08-09 catch-up lines had to do.
    import time as _time

    def _refuses(fn):
        try:
            fn()
        except BaseException:
            return True
        return False

    at = ct.clock_at("09:00:00Z")
    late = ct.heartbeat_line("done", tid, clock=at)
    check("--at stamps the hour the work finished, not the hour it was typed",
          late.startswith("09:00:00Z DONE"))
    check("...and the readers key on the mark exactly as they do for a live one",
          fw.heartbeat_attempts(ct.append_line("", late))[0] == {tid}
          and qp.parse_done(ct.append_line("", late)) == {tid})
    check("a trailing Z is optional and a bare clock means the same instant",
          ct.clock_at("09:00:00") == at)

    # THE GUARD THAT MATTERS: today only. An earlier day cannot be expressed, so
    # a yesterday completion cannot be typed into today's count. 40f6ca4 is the
    # live example — 21:08 UTC on 2026-08-08, which reads as the 9th in a +04:00
    # git log, and stamping it would have put yesterday's work in "finished today".
    check("--at can only ever land on today, so no wrong-day claim is typeable",
          _time.strftime("%Y-%m-%d", _time.gmtime(at))
          == _time.strftime("%Y-%m-%d", _time.gmtime()))
    check("a clock that is not a clock is refused rather than guessed",
          _refuses(lambda: ct.clock_at("yesterday")))

    # And it cannot ride the wrapper form, which writes DONE from an exit code
    # that has not happened yet — there is no past hour to carry.
    check("--at is refused with `-- <cmd>`, which claims work not yet run",
          _refuses(lambda: ct.main(["some-id", "--at", "09:00:00Z", "--", "true"])))


def test_a_hand_claim_reads_the_verdict_off_the_exit_code():
    """DONE is written from the exit code, never from intent.

    That is the whole reason the wrapper form exists: the STARTED line and the
    DONE line cannot be forgotten separately from the run, and a crash cannot
    leave a bare STARTED behind — which is the state that made the 5090's
    bluescreened AnimeGen task look brand new forever.
    """
    import claim_task as ct
    check("exit 0 is DONE", ct.stage_for(0) == "done")
    check("a non-zero exit is FAIL, not DONE", ct.stage_for(1) == "fail")
    check("SIGINT is INTERRUPTED — a Ctrl+C is not a failed render",
          ct.stage_for(130) == "interrupted" and ct.stage_for(-2) == "interrupted")
    check("every stage the CLI offers is one the readers key on",
          set(ct.STAGES) == {"started", "done", "fail", "interrupted"})

    # The `--` split is done by hand because argparse.REMAINDER swallows every
    # flag after the first positional: `claim_task.py <id> started --note x`
    # parsed `--note x` as a command to run and then rejected the whole call.
    own, cmd = ct.split_command(["t1", "started", "--note", "x"])
    check("our own flags stay ours when there is no command",
          own == ["t1", "started", "--note", "x"] and cmd == [])
    own, cmd = ct.split_command(["t1", "--no-push", "--", "python3", "-c", "print(1)"])
    check("everything after the first bare -- is the wrapped command",
          own == ["t1", "--no-push"] and cmd == ["python3", "-c", "print(1)"])
    own, cmd = ct.split_command(["t1", "--", "sh", "-c", "a -- b"])
    check("...and a second -- inside the command is the command's business",
          cmd == ["sh", "-c", "a -- b"])


def test_a_hand_claim_refuses_an_id_nobody_filed():
    """The other half of the ruling: do not claim what was never queued.

    `DONE task=<id>` means "that queue entry ran". A line for an id in no list
    retires nothing and tells the next reader an entry exists when none does —
    the same untruth as a borrowed id, pointed the other way.
    """
    import claim_task as ct

    text = (
        "tasks:\n"
        "- id: real-farm-task-1786000000\n"
        "  worker: rtx5090\n"
        "backlog:\n"
        "- id: real-manual-task-1786000001\n"
        "  runner: manual\n"
        "  why: a person runs this one\n")
    check("an id in tasks: is claimable",
          (ct.queue_entry(text, "real-farm-task-1786000000") or {}).get("worker") == "rtx5090")
    # backlog too: a `runner: manual` entry never leaves backlog, and manual
    # entries are exactly the ones a person runs by hand.
    check("an id in backlog: is claimable, because manual work never leaves it",
          (ct.queue_entry(text, "real-manual-task-1786000001") or {}).get("runner") == "manual")
    check("an id in neither list is not a task", ct.queue_entry(text, "invented-1786000002") is None)

    # And the live file — two thousand lines of comment-heavy YAML, which is the
    # thing worth exercising — parses, and answers for the ids actually in it.
    # THOSE IDS ARE READ OUT OF THE FILE, never written in here: a literal id
    # pins this test to one piece of work, and every piece of work eventually
    # retires. This line named `composite-provenance-manifest-1786218000` and
    # failed the hour that entry was done — a test breaking on success, which
    # teaches the next reader to distrust it rather than the change.
    import yaml

    live = (REPO / "pipeline" / "farm-queue.yaml").read_text(encoding="utf-8")
    doc = yaml.safe_load(live) or {}
    live_ids = [e["id"] for key in ("tasks", "backlog")
                for e in (doc.get(key) or [])
                if isinstance(e, dict) and e.get("id")]
    check("the live queue still holds entries to claim", bool(live_ids))
    check("the real queue parses and answers for every real id",
          all(ct.queue_entry(live, i) is not None for i in live_ids))
    check("the real queue does not answer for an invented id",
          ct.queue_entry(live, "no-such-task-0000000000") is None)

    # The claim branch is NOT a worker's: Courier force-pushes farm-results-<name>
    # from the box's own disk, so a line written to one would be erased by the
    # machine it borrowed. And the status page must not grow a building for it.
    import build_sim as bs
    check("hand claims land on their own branch, which no worker force-pushes",
          ct.HAND_BRANCH == "farm-results-hand")
    check("...and the town does not publish it as a machine that is never on",
          ct.HAND_BRANCH.split("farm-results-")[-1] in bs.NOT_A_MACHINE)
    check("...while the real machines all still have buildings",
          not (set(bs.MACHINES) & bs.NOT_A_MACHINE))


def test_a_job_run_by_hand_reaches_the_status_counters():
    """No building on the street, and counted all the same.

    NOT_A_MACHINE was only ever meant to be about the TILE — its own comment
    said "read_machines() drops these; nothing else about them changes" — but
    the finished/done/in-flight counters (today finished_recent(),
    task_ids_done() and live_now()) each walked the machine list, so a job a
    person ran and claimed could not appear as finished, could not stop its own
    queue entry from publishing as runnable, and could not read as in flight
    while it ran. Both halves are pinned here.
    """
    import datetime
    import build_sim as bs
    import claim_task as ct

    now = datetime.datetime(2026, 8, 9, 18, 0, tzinfo=datetime.timezone.utc)
    tid = "a-hand-task-1786000000"
    # BUILT BY claim_task ITSELF, not typed as a literal here: the page reads
    # these off the commit SUBJECT, and claim_task's subject carries a leading
    # clock that farm_worker's does not. A literal would let the two files drift
    # apart and still pass — which is exactly how the second half of this bug
    # would have survived the first.
    started = ct.heartbeat_line("started", tid, clock=0)
    done = ct.heartbeat_line("done", tid, clock=0)
    check("the mark is read through claim_task's leading clock and without it",
          bs.hb_mark(done) == "DONE" == bs.hb_mark("DONE task=x"))

    hand = {"key": "hand", "branch": "farm-results-hand", "ledger": True,
            "name": bs.LEDGERS["hand"],
            "history": [(now - datetime.timedelta(minutes=5), done),
                        (now - datetime.timedelta(minutes=9), started)]}
    box = {"key": "rtx5090", "name": "the big render house", "history":
           [(now - datetime.timedelta(hours=3), "DONE task=a-box-task-1786000001")]}

    fin = bs.finished_recent([box, hand], now)
    check("a job finished by hand is in the last day's finished list",
          [who for _w, who, t, _n in fin if t == tid] == ["run by hand"])
    check("...beside the machine's, not instead of it", len(fin) == 2)
    check("...and its queue entry stops publishing itself as runnable",
          tid in bs.task_ids_done([box, hand]))

    open_hand = {**hand, "history": hand["history"][1:]}   # STARTED, no DONE yet
    r = bs.live_now([box, open_hand], now)
    check("a hand-run in progress reads as in flight, not as queued",
          [(who, t) for _w, who, t in r] == [(bs.LEDGERS["hand"], tid)])
    check("...and stops reading as in flight the moment its DONE lands",
          bs.live_now([box, hand], now) == [])
    stale = {**open_hand, "history":
             [(now - datetime.timedelta(hours=2), started)]}
    check("...and a STARTED older than the freshness cutoff is not 'now'",
          bs.live_now([stale], now) == [])
    check("yesterday's hand work has left the rolling day",
          bs.finished_recent([{**hand, "history":
                               [(now - datetime.timedelta(days=1), done)]}], now) == [])
    check("and the ledger still gets no building on the street",
          "hand" in bs.NOT_A_MACHINE and "hand" not in bs.MACHINES)


def test_a_retired_id_still_says_what_the_job_was():
    """A finished row names the job in a stranger's words — never a log token.

    The promoter retires an entry the instant its DONE line appears, so the ids
    most sure to have no queue entry left are the ones whose work most surely
    shipped. The old fallbacks printed either the raw id or the runner's own
    note — and the note is written for the person clearing the gate, which is
    how taste-ledger record numbers and REVOKED filenames reached the public
    page (the founder's screenshot, 2026-08-11). done_story() now takes the id
    and translates it; the note still rides the counter for any reader that
    needs the evidence trail, but no display path prints it.
    """
    import claim_task as ct
    import build_sim as bs

    tid = "composite-provenance-manifest-1786218000"
    note = "backfilled 2026-08-09 by status-audit; ran and completed 11:04:00Z, evidence 39224e5"
    # Built by claim_task, for the same reason the test above does it: the note
    # has to survive the exact format that writer produces, not a literal here.
    line = ct.heartbeat_line("done", tid, note=note, clock=0)
    check("the note is read back whole, past the clock, mark, id and by-hand",
          bs.hb_note(line) == note)
    check("a worker line that carries no note answers with no note",
          bs.hb_note("DONE task=a-box-task-1786000001") == "")
    check("...and neither reading disturbs the mark or the id",
          bs.hb_mark(line) == "DONE" and f"task={tid}" in line)

    # The id families the studio actually mints, translated — and the epoch
    # token never survives into any of them.
    check("a scene id translates into the scene it was for",
          bs.tid_words("ep2-b05-warmfield-0811-1786470001")
          == "a fresh frame for episode 2, scene 05")
    check("...and the 00Nx node spelling reads as the same episode",
          bs.tid_words("002b-b12-promptfix-0809")
          == "a fresh frame for episode 2, scene 12")
    check("a motion id reads as a moving take, not a frame",
          bs.tid_words("001-b06-i2v-ltx-1786000001")
          == "a moving take for episode 1, scene 06")
    check("an id nobody can translate stays a generic sentence, not a token",
          bs.tid_words(tid) == "a studio job")

    check("a retired id is translated, never printed raw",
          bs.done_story(None, tid) == bs.tid_words(tid))
    # A render-shaped queue entry is the better answer and keeps winning.
    task = {"id": tid, "video": True, "video_model": "ti2v-5b", "seconds": 3.0}
    check("a queue entry that still exists is still what the row reports",
          bs.done_story(task, tid) == bs.task_story(task)[0])
    check("...but a non-render entry does not — task_story would call a lock "
          "release 'frames for world scenery'",
          bs.done_story({"id": tid, "runner": "manual"}, tid) == bs.tid_words(tid))

    import datetime
    now = datetime.datetime(2026, 8, 9, 16, 30, tzinfo=datetime.timezone.utc)
    hand = {"name": bs.LEDGERS["hand"],
            "history": [(now - datetime.timedelta(hours=4), line)]}
    check("and the note still travels out of the counter for whoever needs it",
          [n for _w, _who, _t, n in bs.finished_recent([hand], now)] == [note])


def test_an_age_counts_from_the_line_not_from_the_push():
    """A check-in is as old as its own stamp, not as old as its commit.

    heartbeat_history dated every entry by commit time, which is when a line
    reached GitHub. Courier pushes a box's log on a cycle and a person pushes a
    hand claim whenever they get to it, so the commit always trails the event by
    an unknown amount — and the page's footer promises the opposite, that every
    age counts from the moment its own datum was recorded. The line's own clock
    IS that moment wherever a writer stamps one.
    """
    import datetime
    import build_sim as bs

    commit = datetime.datetime(2026, 8, 9, 12, 30, 0, tzinfo=datetime.timezone.utc)
    check("a line pushed half an hour late is aged from when it was written",
          bs.line_time("12:00:00Z DONE task=x by-hand", commit)
          == commit.replace(hour=12, minute=0, second=0))
    # farm_worker commits `hb: {stage}` and keeps the clock in the file, so its
    # subjects have no stamp to prefer and must fall through untouched.
    check("a line with no clock of its own keeps its commit time",
          bs.line_time("DONE task=x", commit) == commit)
    check("...and so does one whose clock is not a time",
          bs.line_time("99:99:99Z DONE task=x", commit) == commit)
    check("no commit date, nothing to date a clock against",
          bs.line_time("12:00:00Z DONE task=x", None) is None)

    # WRITTEN BEFORE MIDNIGHT, PUSHED AFTER. The commit supplies the day, so a
    # stamp landing after its own commit can only be the previous one — a line
    # cannot be committed before it is written.
    after_midnight = datetime.datetime(2026, 8, 9, 0, 10, 0, tzinfo=datetime.timezone.utc)
    check("a line pushed past midnight belongs to the day it was written",
          bs.line_time("23:50:00Z DONE task=x by-hand", after_midnight)
          == datetime.datetime(2026, 8, 8, 23, 50, tzinfo=datetime.timezone.utc))
    check("...while a second of clock skew is skew, not a whole day back",
          bs.line_time("00:10:01Z DONE task=x by-hand", after_midnight).day == 9)

    # And the consequence that matters: the rolling day is measured from the
    # line's OWN clock, so a job pushed late ages from when it was written —
    # and leaves the window when its own stamp is a day old, not its commit's.
    now = datetime.datetime(2026, 8, 9, 6, 0, tzinfo=datetime.timezone.utc)
    line = "23:50:00Z DONE task=x by-hand"
    hand = {"name": bs.LEDGERS["hand"],
            "history": [(bs.line_time(line, after_midnight), line)]}
    check("a line pushed late is aged from when it was written",
          [w for w, *_ in bs.finished_recent([hand], now)]
          == [datetime.datetime(2026, 8, 8, 23, 50, tzinfo=datetime.timezone.utc)])
    check("...and it leaves the rolling day on its own clock, not the push's",
          bs.finished_recent([hand], now + datetime.timedelta(hours=18)) == [])


def test_a_rate_limited_build_can_still_see_hand_work():
    """The API-down fallback names the ledgers, not the machines alone.

    farm_branches is the single door every branch reader goes through, so a
    fallback listing MACHINES only did not just cost the hand ledger a tile it
    never had: read_ledgers returned nothing, "Finished today" printed 0 on a
    day people had finished work, and their retired queue entries re-opened as
    runnable. That is the invisible-buildings bug one heading over — a zero that
    actually means "we could not ask".
    """
    import build_sim as bs

    real_api = bs._api
    try:
        bs._api = lambda *a, **k: None          # GitHub rate-limited us
        fallback = bs.farm_branches()
    finally:
        bs._api = real_api

    check("the fallback still names every machine",
          all(f"farm-results-{k}" in fallback for k in bs.MACHINES))
    check("and it names the ledgers, which it used to drop",
          all(f"farm-results-{k}" in fallback for k in bs.LEDGERS))
    check("nothing else is invented", len(fallback) == len(bs.MACHINES) + len(bs.LEDGERS))
    # The ledger is in the branch list and still not a building: read_machines
    # drops it on NOT_A_MACHINE, which is the only thing that exclusion was for.
    check("...and the ledger branch is still not a machine",
          [b for b in fallback if b.split("farm-results-")[-1] in bs.NOT_A_MACHINE]
          == ["farm-results-hand"])


def test_a_log_it_could_not_read_is_not_a_day_with_no_work():
    """"Nothing finished" and "we could not find out" must not print the same.

    The zero-state sentence asserted an empty day off a read that may never have
    happened: rate-limit the branch list and every counter on the work list goes
    quiet, with the most reassuring possible wording. That is the infra meter's
    lesson one heading over — where a failed read prints NO number rather than a
    stale or invented one — so the same contract applies here.

    The other half is that a 404 is not a failure. A ledger branch exists only
    once somebody has claimed a task by hand; on a day nobody has, asking for it
    correctly answers "there is nothing there", and that is knowledge, not an
    outage. farm-results-hand was deleted on 2026-08-09 (4924a29) and the page
    must read that as a quiet true zero, not as a fault.
    """
    import build_sim as bs

    saved = list(bs.FETCH_ERRORS)
    try:
        bs.FETCH_ERRORS[:] = []
        check("a build with every read intact knows what it knows",
              bs.logs_unread() == [])

        bs.FETCH_ERRORS[:] = [(bs.BRANCH_LIST_LABEL, "GitHub is rate-limiting this build")]
        check("a rate-limited branch list is an unread log, not an empty day",
              bs.logs_unread() == ["the branch list"])

        bs.FETCH_ERRORS[:] = [(bs.log_label("farm-results-hand"), "GitHub answered HTTP 500")]
        check("...and so is one branch's own log failing",
              bs.logs_unread() == ["farm-results-hand"])
        # The label is built in one place precisely so this match cannot rot.
        check("the failure the page prints is the one logs_unread looks for",
              bs.log_label("farm-results-msi") == "the check-in dates for farm-results-msi")
    finally:
        bs.FETCH_ERRORS[:] = saved

    # A 404 the caller said it could live with is an ANSWER: empty list, and
    # nothing added to the page's list of faults.
    import urllib.error
    saved = list(bs.FETCH_ERRORS)
    real_fetch = bs.urllib.request.urlopen
    try:
        bs.FETCH_ERRORS[:] = []

        def gone(*a, **k):
            raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)
        bs.urllib.request.urlopen = gone
        check("a ledger branch that does not exist reads as empty, not as broken",
              bs.branch_log("farm-results-hand", absent_ok=True) == [])
        check("...and posts no fault about a branch nobody promised was there",
              bs.FETCH_ERRORS == [] and bs.logs_unread() == [])

        def limited(*a, **k):
            raise urllib.error.HTTPError("u", 429, "Too Many Requests", {}, None)
        bs.urllib.request.urlopen = limited
        check("a rate limit is still a fault even where absence is tolerated",
              bs.branch_log("farm-results-hand", absent_ok=True) == []
              and bs.logs_unread() == ["farm-results-hand"])
    finally:
        bs.urllib.request.urlopen = real_fetch
        bs.FETCH_ERRORS[:] = saved


def test_the_queue_is_reported_in_time_and_never_guessed():
    """"i should be able to see how long the queue is in time as well" — Roman,
    2026-08-12.

    Two things have to stay true of that number. It is DERIVED at build time
    from the counts the supervisor measured, so a tick that rewrites
    ready/running and leaves the median alone still moves the estimate instead
    of printing a total nobody recomputed — the reason the estimate is not a
    stored field beside the counts. And it is never invented: with no snapshot,
    or a snapshot carrying no measured median, the page says which of the two
    is missing rather than showing a plausible figure. That second half is the
    infra meter's contract, arriving at its third place on this page.
    """
    import datetime
    import build_sim as bs

    snap = {"measured_at": "2026-08-12 12:42Z", "ready": 3, "running": 1,
            "queued_kinds": {"ltx": 3, "still": 1},
            "kind_medians": {"ltx": 5.0, "still": 1.0},
            "kind_median_fallback": 3.0,
            "median_from": "the 248 jobs the box finished"}
    eta = bs.box_queue_eta(snap)
    check("three motion takes and a stills batch is sixteen minutes of work",
          eta["jobs"] == 4 and eta["est_minutes"] == 16
          and eta["basis"] == "kinds")

    # WHY PER KIND AT ALL: the same four jobs the other way round is a
    # different afternoon, and one pooled median cannot tell them apart.
    flipped = bs.box_queue_eta({**snap, "queued_kinds": {"ltx": 1, "still": 3}})
    check("...and the same four jobs of the other kinds is not the same wait",
          flipped["est_minutes"] == 8)

    # THE STALENESS THE SHAPE EXISTS TO PREVENT: the tick moves the counts and
    # nothing else, and the time moves with them.
    ticked = bs.box_queue_eta({**snap, "ready": 8, "queued_kinds": None,
                               "measured_at": "2026-08-12 13:10Z"})
    check("a tick that only moves the counts moves the estimate with them",
          ticked["est_minutes"] == 27 and ticked["basis"] == "rough")
    check("...and a fallback estimate is labelled as the rough thing it is",
          "rough" in bs.queue_time_basis(ticked))

    # A MIX THAT DOES NOT ACCOUNT FOR EVERY JOB is a reading of a queue that
    # has moved since. Falling back beats reporting a total for three of four.
    partial = bs.box_queue_eta({**snap, "queued_kinds": {"ltx": 3}})
    check("a kind mix that does not add up to the count is not trusted",
          partial["basis"] == "rough" and partial["est_minutes"] == 12)

    check("no medians measured at all, no time claimed",
          bs.box_queue_eta({**snap, "kind_medians": None,
                            "kind_median_fallback": None})["est_minutes"] is None)
    check("...and its words are empty, so no caller can print a bare number",
          bs.queue_time_words(bs.box_queue_eta(
              {**snap, "kind_medians": {}, "kind_median_fallback": 0})) == "")
    check("an unreadable snapshot is not a queue of length zero",
          bs.box_queue_eta({}) is None and bs.box_queue_eta(None) is None)
    check("an empty queue is a real zero and is allowed to say so",
          bs.queue_time_words(bs.box_queue_eta({**snap, "ready": 0, "running": 0,
                                                "queued_kinds": {}}))
          == "nothing queued")

    # The shipped snapshot must satisfy the reader it was written for.
    live = bs.box_queue_eta(bs.read_box_queue())
    check("the snapshot in the repo parses into an estimate or an honest gap",
          live is None or live["est_minutes"] is None
          or live["est_minutes"] >= 0)

    # THE HEADLINE, which moved on 2026-08-14. The founder asked for the queue
    # at the top of the page, so the summary strip's queue cell became the same
    # sentence twice and the cell was removed — its number and its two ids now
    # head the queue's own section. The three facts below are unchanged and are
    # checked at the number's new address: a time when one can be estimated,
    # "not read" when no snapshot could be read, and the count with no time at
    # all when nothing has been measured to multiply it by.
    now = datetime.datetime(2026, 8, 12, 13, 0, tzinfo=datetime.timezone.utc)
    view = {"fin": [], "live": [], "unread": [], "last_activity": None,
            "by_id": {}, "hero": {"number": 1, "watch": "/watch"},
            "tot": {"final": 15, "total": 15}, "ep2": None, "inbox": [],
            "boxq": eta}
    head = bs.queue_head_html(eta)
    check("the queue's headline answers it in time, not only in jobs",
          "~16 min" in head)
    check("...and it keeps the ids LIVE_JS rewrites",
          'id="q-tile-n"' in head and 'id="q-tile-l"' in head)
    blind = bs.queue_head_html(None)
    check("...and with no snapshot to read it says so and prints no time",
          "not read" in blind and "of work queued" not in blind)
    timeless = bs.queue_head_html(
        bs.box_queue_eta({**snap, "kind_medians": {},
                          "kind_median_fallback": 0}))
    check("...and with counts but nothing measured it still shows the counts",
          "no job times have been measured" in timeless
          and "of work queued" not in timeless)
    # And the strip must not have kept a copy: one fact printed twice, a few
    # hundred pixels apart, is the complaint that moved it.
    check("the summary strip no longer prints the queue a second time",
          "of work queued" not in bs.summary_strip(view, now))


# ====================================================================== #
# A CONCATENATION MUST NOT LAUNDER WHAT WENT INTO IT
# — composite-provenance-manifest-1786218000
#
# publishable() read a file's OWN sidecar and nothing else, so the moment N
# clips were muxed into one mp4 the gate saw one new file with one clean record
# and no way to ask what was inside it. On 2026-08-09 that cleared two cuts whose
# footage and stills are refused one directory down (D16 LTX-2, D15 animagine);
# both were plugged by hand-written composite sidecars, and a hand-plug is
# per-cut — the next assembly re-opens the hole.
#
# render_t3 now writes `ingredients:` (one row per muxed file: path, sha256 as
# muxed, verdict at assembly time) and composite_publishable() walks it. These
# three pin the three answers that matter: refused stays refused through a
# concat, a manifest that no longer describes the file it names is a refusal,
# and a clean cut is untouched.
# ====================================================================== #


def _cut_with_ingredients(tmp: Path, rows: list) -> Path:
    """A cut mp4 plus the assembly sidecar render_t3 writes beside it."""
    import yaml as _y
    cut = tmp / "ep1-v34.mp4"
    cut.write_bytes(b"a concatenated episode")
    (tmp / (cut.name + ".meta.yaml")).write_text(_y.safe_dump(
        {"platform": "local-deterministic (pipeline/hold_still.py, render_t3.py, ffmpeg)",
         "model": "none", "cost_usd": 0.0, "ingredients": rows}, sort_keys=False))
    return cut


def _clip(tmp: Path, name: str, body: bytes, model: str) -> tuple:
    """A source clip and its own sidecar. Returns (path, sha256)."""
    import hashlib

    import yaml as _y
    p = tmp / name
    p.write_bytes(body)
    (tmp / (name + ".meta.yaml")).write_text(_y.safe_dump(
        {"platform": "local-gpu (rtx5090)", "model": model, "cost_usd": 0}, sort_keys=False))
    return p, hashlib.sha256(body).hexdigest()


def test_a_cut_holding_one_refused_ingredient_does_not_publish(tmp: Path):
    """One bad clip out of three withholds the whole cut, and says which one.

    The cut's own record is spotless — this is the laundering case exactly: an
    assembly whose top line is honest and whose insides are not. The reason
    string has to name the ingredient, because "this episode is withheld" with no
    path in it is a message nobody can act on.
    """
    import build_site as bs

    good, good_sha = _clip(tmp, "01-a.mp4", b"wan footage", "Wan-AI/Wan2.2-TI2V-5B-Diffusers")
    bad, bad_sha = _clip(tmp, "13-b.mp4", b"pixverse footage", "PixVerse V6")
    check("the clean ingredient publishes on its own", bs.publishable(good) == (True, ""))
    check("the refused ingredient does not publish on its own", bs.publishable(bad)[0] is False)

    cut = _cut_with_ingredients(tmp, [
        {"beat": 1, "kind": "clip", "path": good.name, "sha256": good_sha, "publishable": True},
        {"beat": 13, "kind": "clip", "path": bad.name, "sha256": bad_sha, "publishable": False,
         "why": bs.publishable(bad)[1]},
    ])
    ok, why = bs.publishable(cut)
    check("a cut containing one refused clip is withheld", ok is False)
    check("...and the reason names the clip, not just the cut", "13-b.mp4" in why)

    # The row's recorded verdict is not the only defence: a manifest that claims
    # every ingredient passed is still re-asked, so a licence reclassified after
    # assembly is caught on the next build rather than never.
    lying = _cut_with_ingredients(tmp, [
        {"beat": 13, "kind": "clip", "path": bad.name, "sha256": bad_sha, "publishable": True},
    ])
    check("a manifest claiming a refused clip passed is overruled by re-asking",
          bs.publishable(lying)[0] is False)


def test_a_cut_whose_manifest_no_longer_describes_its_inputs_does_not_publish(tmp: Path):
    """Changed bytes, a deleted file and a row with no hash are all refusals.

    Three absences, one rule: an ingredient we cannot resolve is a REFUSAL and
    never a pass — the same way lint reads a missing record. A manifest is a
    claim about a file nobody can look inside, so a claim that cannot be checked
    must buy the cut nothing; otherwise deleting a row is the cheapest way past
    the gate.
    """
    import build_site as bs

    clip, sha = _clip(tmp, "01-a.mp4", b"the bytes that were muxed", "Wan-AI/Wan2.2-TI2V-5B-Diffusers")
    row = {"beat": 1, "kind": "clip", "path": clip.name, "sha256": sha, "publishable": True}
    cut = _cut_with_ingredients(tmp, [dict(row)])
    check("the cut publishes while the manifest still describes the file", bs.publishable(cut) == (True, ""))

    clip.write_bytes(b"different footage under the same name")
    ok, why = bs.publishable(cut)
    check("a source file that changed since the cut was made withholds the cut", ok is False)
    check("...and the reason says the record no longer describes the contents",
          "changed" in why and clip.name in why)

    clip.unlink()
    ok, why = bs.publishable(cut)
    check("a source file the repo no longer carries withholds the cut", ok is False)
    check("...and says so rather than passing on an unresolvable row", "no longer carries" in why)

    # An ingredient with no hash cannot be checked against anything.
    nohash = tmp / "nohash"
    nohash.mkdir()
    _clip(nohash, "01-a.mp4", b"the bytes that were muxed", "Wan-AI/Wan2.2-TI2V-5B-Diffusers")
    unhashed = _cut_with_ingredients(
        nohash, [{"beat": 1, "kind": "clip", "path": "01-a.mp4", "publishable": True}])
    check("a row naming a file with no hash is unverifiable, so withheld",
          bs.publishable(unhashed)[0] is False)

    # And an ingredient with no record beside it: unprovenanced is a pass for a
    # standalone take (the gate's finding, not the build's) and a REFUSAL inside
    # a cut, because the manifest promised the cut could be audited.
    bare = tmp / "bare"
    bare.mkdir()
    import hashlib
    raw = bare / "02-c.mp4"
    raw.write_bytes(b"no sidecar anywhere")
    check("a clip with no record publishes on its own", bs.publishable(raw) == (True, ""))
    cut2 = _cut_with_ingredients(bare, [
        {"beat": 2, "kind": "clip", "path": raw.name,
         "sha256": hashlib.sha256(b"no sidecar anywhere").hexdigest(), "publishable": True}])
    check("...and withholds the cut it is muxed into", bs.publishable(cut2)[0] is False)


def test_a_cut_whose_ingredients_all_pass_publishes_unchanged(tmp: Path):
    """The regression guard on the other side: this must not withhold everything.

    A gate that refuses a clean cut is as broken as one that clears a dirty one,
    and it fails in the direction nobody notices until the review page is empty.
    Also pins the no-manifest case: every cut assembled before today has no
    `ingredients:` block at all, and those keep answering exactly as they did.
    """
    import build_site as bs

    a, a_sha = _clip(tmp, "01-a.mp4", b"wan beat one", "Wan-AI/Wan2.2-TI2V-5B-Diffusers")
    b, b_sha = _clip(tmp, "02-b.mp4", b"a held still push-in", "none")
    cut = _cut_with_ingredients(tmp, [
        {"beat": 1, "kind": "clip", "path": a.name, "sha256": a_sha, "publishable": True},
        {"beat": 2, "kind": "clip", "path": b.name, "sha256": b_sha, "publishable": True},
    ])
    check("a cut whose every ingredient passes publishes, with no warning",
          bs.publishable(cut) == (True, ""))

    plain = tmp / "old-cut.mp4"
    plain.write_bytes(b"assembled before manifests existed")
    (tmp / "old-cut.mp4.meta.yaml").write_text(
        "platform: local-deterministic (pipeline/hold_still.py, render_t3.py, ffmpeg)\n"
        "model: none\ncost_usd: 0\n")
    check("a cut with no ingredients block is judged exactly as it was before",
          bs.publishable(plain) == (True, ""))

    # render_t3 writes the platform line VERBATIM from the licence table; if that
    # string ever stops resolving to an allow, every cut we assemble goes unknown.
    import licence_gate as lg
    import render_t3 as _t3
    check("the assembly platform line render_t3 writes is a classified allow",
          lg.classify(lg.engine_licence(_t3.ASSEMBLY_PLATFORM))[0] == "allow")


def test_a_steward_pick_stays_labelled_after_it_is_concatenated(tmp: Path):
    """`publishable` is the licence's word and says nothing about whether he
    has SEEN the frame — so the manifest has to carry both.

    v34 beat 06 is the case: the founder refused r3 and r4, r5 finally drew
    nobody, and the cut holds the steward's own pick out of `takes/`. That clip
    is perfectly licensed — local ffmpeg over a frame we already own — so its
    row reads `publishable: true`, and it sat there indistinguishable from the
    fourteen frames he chose himself. Nothing in the manifest said which beat
    was a guess. The clip's sidecar knew (hold_still writes `provisional: true`
    on it); the concatenation dropped the fact, which is the same laundering
    `ingredient_row` was written to stop, one field over.

    THE FLAG IS COPIED, NEVER INTERPRETED, and that is asserted here too. Twelve
    of v34's clips inherit `provisional:` from v33's hand-written labels, where
    it meant four different things — so a row carries the ingredient's own word
    and the head is a pointer at the rows, not a taste verdict derived from them.
    """
    import yaml as _y

    import render_t3 as t3

    seen, _ = _clip(tmp, "14-worth-staying-in.mp4", b"his own pick, held", "none")
    guess, _ = _clip(tmp, "06-too-blue.mp4", b"a steward pick, held", "none")
    # hold_still's stamp, as it writes it
    side = tmp / "06-too-blue.mp4.meta.yaml"
    rec = _y.safe_load(side.read_text())
    rec["provisional"] = True
    rec["provisional_reason"] = "PROVISIONAL PICK b06-r5-s2 (conf 0.55) — NOT canon"
    side.write_text(_y.safe_dump(rec, sort_keys=False))

    rows = [t3.ingredient_row(seen, 14, "clip"), t3.ingredient_row(guess, 6, "clip")]
    check("an ingredient whose record says nothing carries no provisional mark",
          rows[0].get("provisional") is None)
    check("an ingredient that marks itself provisional says so in the manifest",
          rows[1].get("provisional") is True)
    check("...and the licence verdict is untouched by it — they are two questions",
          rows[0]["publishable"] is True and rows[1]["publishable"] is True)

    out = tmp / "ep1-v34-PROVISIONAL.mp4"
    out.write_bytes(b"the assembled cut")
    side = t3.assembly_sidecar(out, "001", "", 0.0, 15, [], rows, 90.1, [])
    head = _y.safe_load(side.read_text(encoding="utf-8"))
    check("the cut's head points at the flagged beats instead of hiding them",
          head.get("provisional") is True and head.get("provisional_beats") == [6])

    # AND A CUT WITH NOTHING FLAGGED MUST NOT GROW THE FIELD — a warning printed
    # on every cut is a warning nobody reads.
    clean = tmp / "ep1-v35.mp4"
    clean.write_bytes(b"a cut of ratified frames")
    cside = t3.assembly_sidecar(clean, "001", "", 0.0, 15, [], [rows[0]], 90.1, [])
    chead = _y.safe_load(cside.read_text(encoding="utf-8"))
    check("a cut whose ingredients flag nothing says nothing about provisionality",
          "provisional" not in chead and "provisional_beats" not in chead)


# ====================================================================== #
# A HELD SHOT IS ONLY AS PUBLISHABLE AS THE FRAME IT HOLDS
# — canon-promotion-provenance-1786320000
#
# `ingredients:` closed the concatenation door and left the picture door open.
# render_t3 lists what it MUXED — clips and audio — so a held beat's clip is a
# row and the PNG hold_still drew it out of is not. Eleven of v34's fifteen
# beats are held, every one of them says `model: none` honestly (no video model
# ran), and on 2026-08-09 `publishable()` therefore cleared the whole cut while
# `takes/stills/06-too-blue-r5-s2.png` — inside it — answered
# `(False, 'CreativeML Open RAIL++-M')` when asked by name.
#
# The second half is worse and is what these pin: a canon promotion is a COPY
# into `stills/`, the copy carries no sidecar, and publishable() reads
# unprovenanced as permitted — so promoting a frame is what strips the record
# that would have refused it. The bytes are the way back: the take is still in
# the tree under its own name with its own record, and identical bytes are the
# identical picture.
# ====================================================================== #


def _frame(d: Path, name: str, body: bytes, model) -> tuple:
    """A PNG and (optionally) the render-time sidecar beside it."""
    import hashlib

    import yaml as _y
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_bytes(body)
    if model is not None:
        (d / (name + ".meta.yaml")).write_text(_y.safe_dump(
            {"platform": "local-gpu (rtx5090)", "model": model,
             "seed": 20263722, "cost_usd": 0}, sort_keys=False))
    return p, hashlib.sha256(body).hexdigest()


def _held(tmp: Path, name: str, frame_rel: str, frame_sha: str) -> Path:
    """A hold_still clip: no video model ran, and the frame is the whole shot."""
    import yaml as _y
    p = tmp / name
    p.write_bytes(b"one still, pushed in on")
    (tmp / (name + ".meta.yaml")).write_text(_y.safe_dump(
        {"platform": "local-deterministic (pipeline/hold_still.py, ffmpeg)",
         "model": "none",
         "model_licence": "n/a — inherits the still's licence, see stills/README.md",
         "source_still": Path(frame_rel).name,
         "source_still_path": frame_rel,
         "source_still_sha256": frame_sha, "cost_usd": 0}, sort_keys=False))
    return p


def test_a_held_shot_is_only_as_publishable_as_the_frame_it_holds(tmp: Path):
    """`model: none` is the truth and it is not the answer.

    Held clips are the majority of every recent cut, so the direction that
    matters is asserted both ways: a clip drawn from a refused frame is
    withheld and says WHICH frame, and a clip that names no frame at all is
    untouched — a gate that withholds everything is as broken as one that
    withholds nothing.
    """
    import build_site as bs

    takes = tmp / "takes" / "stills"
    frame, sha = _frame(takes, "06-too-blue-r5-s2.png",
                        b"an animagine frame", "cagliostrolab/animagine-xl-3.1")
    check("the frame does not publish on its own", bs.publishable(frame)[0] is False)

    saved_still, saved_frame = bs._STILL_DIRS, bs._FRAME_DIRS
    try:
        # The record's path is repo-relative on the real tree; here the tree is
        # the temp dir, so the resolver is pointed at it and nothing else.
        bs._STILL_DIRS, bs._FRAME_DIRS = [], [takes]
        held = _held(tmp, "06-too-blue.mp4", "takes/stills/06-too-blue-r5-s2.png", sha)
        ok, why = bs.publishable(held)
        check("a held shot drawn from a refused frame is withheld", ok is False)
        check("...and the reason names the frame and its licence",
              "06-too-blue-r5-s2.png" in why and "RAIL++" in why)

        plain, _ = _clip(tmp, "02-b.mp4", b"a slate", "none")
        check("a clip that names no frame is unaffected", bs.publishable(plain) == (True, ""))

        # A frame the record can name but the tree cannot produce is a refusal,
        # not a shrug: the claim is about bytes nobody holds.
        gone = _held(tmp, "07-x.mp4", "takes/stills/07-never-existed.png", "f" * 64)
        check("a frame claim no file in the tree can satisfy withholds the shot",
              bs.publishable(gone)[0] is False)
    finally:
        bs._STILL_DIRS, bs._FRAME_DIRS = saved_still, saved_frame


def test_a_canon_promotion_cannot_strip_the_record_that_refuses_it(tmp: Path):
    """The promoted copy has no sidecar; the take it was copied from does.

    This is the hole in one test. `cp takes/stills/03-...-r4-s3.png
    stills/03-deploy-succeeded.png` is the whole of a canon promotion, and the
    copy arrives unprovenanced — which publishable() reads as permitted. Asked
    through the bytes instead of through the name, the take's own record is
    still there and still says animagine.

    THE SECOND HALF IS THE DELIBERATE LIMIT, and it is pinned so that nobody
    "fixes" it by accident: when NO copy of those bytes carries a record, the
    frame is counted and reported, not refused. Twenty-two of the thirty frames
    in `stills/` are older than `takes/stills/` and answer that way, and
    refusing them would empty the founder's review page over an absence the
    licence gate already reports. stills/README.md's promotion sidecar is what
    retires that list; this test asserts the count exists in the meantime.
    """
    import build_site as bs
    import licence_gate as lg

    stills, takes = tmp / "stills", tmp / "takes" / "stills"
    take, sha = _frame(takes, "03-deploy-succeeded-r4-s3.png",
                       b"the frame he picked", "cagliostrolab/animagine-xl-3.1")
    promoted, _ = _frame(stills, "03-deploy-succeeded.png", take.read_bytes(), None)
    saved_still, saved_frame, saved_warn = bs._STILL_DIRS, bs._FRAME_DIRS, list(bs.FRAME_WARNINGS)
    try:
        bs._STILL_DIRS, bs._FRAME_DIRS = [stills], [stills, takes]
        bs.FRAME_WARNINGS.clear()
        check("the promoted copy carries no record of its own",
              lg.sidecar_for(promoted, lg.RECORD_SIDECAR_EXT) is None)
        check("...so asked on its own it still reads as permitted",
              bs.publishable(promoted) == (True, ""))

        held = _held(tmp, "03-deploy-succeeded.mp4", "stills/03-deploy-succeeded.png", sha)
        ok, why = bs.publishable(held)
        check("a shot held on a promoted frame is refused through the take's record",
              ok is False and "RAIL++" in why)
        check("...and the reason names the take, which is where the record lives",
              "03-deploy-succeeded-r4-s3.png" in why)
        check("nothing was counted as unprovenanced — the record was found",
              bs.FRAME_WARNINGS == [])

        # Now the frame nobody kept a take of: same promotion, no twin anywhere.
        orphan, osha = _frame(stills, "04-the-fall.png", b"a 2026-07-27 approval", None)
        held2 = _held(tmp, "04-the-fall.mp4", "stills/04-the-fall.png", osha)
        check("a frame with no record anywhere does not withhold the shot",
              bs.publishable(held2) == (True, ""))
        check("...it is counted and named instead, so the absence is visible",
              len(bs.FRAME_WARNINGS) == 1 and "04-the-fall.png" in bs.FRAME_WARNINGS[0])
    finally:
        bs._STILL_DIRS, bs._FRAME_DIRS = saved_still, saved_frame
        bs.FRAME_WARNINGS[:] = saved_warn


def _promo_tree(tmp: Path, take_record: str, body: bytes = b"the frame he picked"):
    """A one-node tree promote_still can run inside, and the take to promote.

    promote_still and build_site both resolve everything from their module-level
    REPO, so the tree has to be shaped like the real one — genome, node, shots.md
    for the canon slug, and takes/stills/ beside the canon stills/ — rather than
    passed in as arguments.
    """
    node = tmp / "genomes" / "sapling" / "nodes" / "001-x"
    (node / "stills").mkdir(parents=True, exist_ok=True)
    takes = node / "takes" / "stills"
    takes.mkdir(parents=True, exist_ok=True)
    (node / "shots.md").write_text(
        "# Shots\n\n## Beat 14 — WORTH STAYING IN\n\n```\na sapling\n```\n",
        encoding="utf-8")
    take = takes / "14-worth-staying-in-r4-s3.png"
    take.write_bytes(b"\x89PNG\r\n\x1a\n" + body)
    (takes / (take.name + ".meta.yaml")).write_text(take_record, encoding="utf-8")
    return node, take, takes


def _at_repo(tmp: Path):
    """Point build_site and promote_still at `tmp` — restore with the callable."""
    import build_site as bs
    import promote_still as ps
    saved = (bs.REPO, ps.REPO, bs._STILL_DIRS, bs._FRAME_DIRS)
    bs.REPO, ps.REPO = tmp, tmp
    bs._STILL_DIRS, bs._FRAME_DIRS = [], []

    def restore():
        bs.REPO, ps.REPO, bs._STILL_DIRS, bs._FRAME_DIRS = saved
    return restore


def test_a_promotion_records_the_weights_and_not_the_machine(tmp: Path):
    """`platform:` is written first in every sidecar, and it resolves.

    The first draft of promote_still took the first provenance key licence_gate
    could resolve, which on the real `03-deploy-succeeded-fix-s0` record is
    `platform: local-gpu (rtx5090)` → `CC-BY-4.0 (our own output)`. It would have
    stamped our own licence on an animagine frame and cleared it, in the one file
    written to do the opposite. The weights win over the machine that ran them.
    """
    import build_site as bs
    import promote_still as ps

    node, take, _ = _promo_tree(tmp, (
        "platform: local-gpu (rtx5090)\n"
        "model: cagliostrolab/animagine-xl-3.1\n"
        "model_licence: CreativeML Open RAIL++-M (use restrictions travel; D15)\n"
        "seed: 20260722\n"))
    restore = _at_repo(tmp)
    try:
        import yaml as _y
        dest = ps.promote(node, 14, take, "b14-r4-s3", "founder", False)
        written = _y.safe_load((dest.parent / (dest.name + ".meta.yaml"))
                               .read_text(encoding="utf-8"))
        check("the canon record names the weights",
              written.get("model") == "cagliostrolab/animagine-xl-3.1")
        check("...and keeps the platform too, rather than choosing between them",
              written.get("platform") == "local-gpu (rtx5090)")
        bs._STILL_DIRS, bs._FRAME_DIRS = [], []
        ok, why = bs.publishable(dest)
        check("an honest promotion REFUSES the frame it documents",
              ok is False and "RAIL++" in why)
        check("the record says whose pick it was, in his words",
              written.get("approved_by") == "founder"
              and written.get("his_address") == "b14-r4-s3")
        check("the take stays where recorded_twin can still reach it", take.is_file())
    finally:
        restore()


def test_a_promoted_composite_carries_the_frame_it_was_drawn_from(tmp: Path):
    """A partial record is worse than none, because it switches off the twin.

    `recorded_twin()` is consulted only when the promoted frame has NO sidecar
    (build_site.py:803). So a promotion sidecar naming just the take's own model
    answers in the twin's place while knowing less than it: measured on this
    exact shape, the bare `cp` was refused as a source frame and the partial
    sidecar CLEARED. The composite reference has to travel with the pixels.
    """
    import build_site as bs
    import promote_still as ps

    node, take, takes = _promo_tree(tmp, "")
    src = takes / "src-animagine.png"
    src.write_bytes(b"\x89PNG\r\n\x1a\nANIMAGINE-SOURCE")
    (takes / (src.name + ".meta.yaml")).write_text(
        "model: cagliostrolab/animagine-xl-3.1\n", encoding="utf-8")
    import hashlib
    (takes / (take.name + ".meta.yaml")).write_text(
        "platform: local-gpu (rtx5090)\n"
        "model: wan\n"
        "model_licence: Apache-2.0\n"
        "source_still_path: genomes/sapling/nodes/001-x/takes/stills/src-animagine.png\n"
        f"source_still_sha256: {hashlib.sha256(src.read_bytes()).hexdigest()}\n",
        encoding="utf-8")

    restore = _at_repo(tmp)
    try:
        import yaml as _y
        check("the composite take is refused on the frame underneath it",
              bs.publishable(take)[0] is False)
        dest = ps.promote(node, 14, take, "b14-r4-s3", "founder", False)
        written = _y.safe_load((dest.parent / (dest.name + ".meta.yaml"))
                               .read_text(encoding="utf-8"))
        check("the frame reference travelled into canon",
              "source_still_path" in written and "source_still_sha256" in written)
        check("...and so did the take's own model", written.get("model") == "wan")
        bs._STILL_DIRS, bs._FRAME_DIRS = [], []
        ok, why = bs.publishable(dest)
        check("the canon copy is refused for the same reason the take was",
              ok is False and "RAIL++" in why)
        # The door the bare `cp` left open: asked as some clip's source frame.
        rec = {"source_still_path":
               "genomes/sapling/nodes/001-x/stills/" + dest.name,
               "source_still_sha256":
               hashlib.sha256(dest.read_bytes()).hexdigest()}
        bs._STILL_DIRS, bs._FRAME_DIRS = [], []
        ok2, _ = bs.frame_publishable(rec, node / "clips" / "14.mp4", frozenset())
        check("...and refused again when a clip reaches it as a source frame",
              ok2 is False)
    finally:
        restore()


def test_a_promotion_that_would_launder_a_licence_writes_nothing(tmp: Path):
    """CARRY is a list and a list goes stale, so the guarantee is measured.

    `init_image` is already a fourth frame-reference dialect that build_site
    cannot read, found by reading render_b01r8 rather than by anything failing —
    the next one will arrive the same way. Simulated here by taking two keys out
    of CARRY: the promotion must refuse, name the dropped fields, and leave
    neither the PNG nor a sidecar behind. A half-written promotion on disk is the
    bare `cp` again, reached by a longer route.
    """
    import build_site as bs
    import promote_still as ps

    node, take, takes = _promo_tree(tmp, "")
    src = takes / "src-animagine.png"
    src.write_bytes(b"\x89PNG\r\n\x1a\nANIMAGINE-SOURCE")
    (takes / (src.name + ".meta.yaml")).write_text(
        "model: cagliostrolab/animagine-xl-3.1\n", encoding="utf-8")
    import hashlib
    (takes / (take.name + ".meta.yaml")).write_text(
        "model: wan\n"
        "source_still_path: genomes/sapling/nodes/001-x/takes/stills/src-animagine.png\n"
        f"source_still_sha256: {hashlib.sha256(src.read_bytes()).hexdigest()}\n",
        encoding="utf-8")

    restore = _at_repo(tmp)
    saved_carry = ps.CARRY
    ps.CARRY = saved_carry - {"source_still_path", "source_still_sha256"}
    try:
        refused = ""
        try:
            ps.promote(node, 14, take, "b14-r4-s3", "founder", False)
        except SystemExit as e:
            refused = str(e)
        check("a promotion more publishable than its take is refused",
              "REFUSED" in refused and "MORE publishable" in refused)
        check("...and the refusal names the exact fields that went missing",
              "`source_still_path:`" in refused
              and "`source_still_sha256:`" in refused)
        dest = node / "stills" / "14-worth-staying-in.png"
        check("no canon frame is left on disk", not dest.exists())
        check("...and no half-written record either",
              not (dest.parent / (dest.name + ".meta.yaml")).exists())
    finally:
        ps.CARRY = saved_carry
        restore()


def test_a_take_the_tree_cannot_account_for_is_refused_by_name(tmp: Path):
    """Three silent shapes, three refusals, each naming its own field.

    "Not allowed" sends whoever hit it to read the source; naming the field sends
    them to the record. The pointer case earns its own branch because it LOOKS
    like diligence: a value that resolves to no model is read by publishable() as
    no licence question at all, so a sidecar written to account for a frame would
    be the thing that clears it.
    """
    import promote_still as ps

    restore = _at_repo(tmp)
    try:
        def why(record, body):
            node, take, takes = _promo_tree(tmp, record, body)
            if record == "":
                (takes / (take.name + ".meta.yaml")).unlink()
            try:
                ps.promote(node, 14, take, "b14-r4-s3", "founder", True)
            except SystemExit as e:
                return str(e)
            return ""

        bare = why("", b"no record at all")
        check("a take with no record cannot be promoted",
              "no provenance record" in bare and ".meta.yaml" in bare)
        blank = why("platform: local-gpu (rtx5090)\nseed: 3\n", b"no model key")
        check("a record that names no model refuses on the missing field",
              "missing field: `model:`" in blank)
        ptr = why("model: see-below\n", b"a pointer")
        check("a pointer is refused for pointing, not for being unknown",
              "points instead of naming" in ptr)
        unknown = why("model: some-new-checkpoint\n", b"unclassified")
        check("an unclassified model is refused before it reaches canon",
              "MODEL_LICENCES" in unknown)
    finally:
        restore()


def test_a_canon_name_is_freed_by_recording_the_refusal(tmp: Path):
    """Revocations stack; the canon name is not a slot to overwrite.

    The bytes are the only thing separating the frame that was refused from the
    one replacing it, so clobbering the name destroys the record of the refusal
    and does it silently.
    """
    import promote_still as ps

    node, take, _ = _promo_tree(tmp, "model: cagliostrolab/animagine-xl-3.1\n")
    restore = _at_repo(tmp)
    try:
        dest = ps.promote(node, 14, take, "b14-r4-s3", "founder", False)
        again = ""
        try:
            ps.promote(node, 14, take, "b14-r4-s4", "founder", False)
        except SystemExit as e:
            again = str(e)
        check("promoting onto an occupied canon name is refused",
              "already exists" in again)
        check("...and the refusal prescribes the -REVOKED- rename",
              "REVOKED" in again)
        check("the frame that was there is untouched", dest.is_file())
    finally:
        restore()


def test_the_live_v34_cut_is_refused_by_the_frames_inside_it():
    """The measured case, on the real tree, and it must stay refused.

    `review/provisional-v34/ep1-v34-PROVISIONAL.mp4` is the cut the gate cleared
    on 2026-08-09 with eleven animagine frames in it. The answer this asserts is
    the licence one — not "unrecorded", not "missing" — because the fix is a
    founder decision (D15) and a refusal that named the wrong reason would send
    whoever reads it to re-record a sidecar instead.

    It flips to publishable the day D15 is settled, and this test is meant to
    fail then: that is a founder decision landing, not a regression.
    """
    import build_site as bs

    cut = REPO / "review" / "provisional-v34" / "ep1-v34-PROVISIONAL.mp4"
    if not cut.exists():
        return                              # provisional cuts are not tracked
    ok, why = bs.publishable(cut)
    check("v34 is not publishable — its frames are refused one directory down",
          ok is False)
    check("...and the reason it gives is the licence, not a missing record",
          "RAIL++" in why)


def test_a_region_mask_conditions_its_box_and_nothing_else():
    """A masked IP-Adapter is only regional if the mask really has an outside.

    `render_b13r7.py` routes the goblin reference into one box and leaves the
    plant to the text prompt, which scores 4/4 and must not be disturbed. Every
    way that goes silently wrong is geometric: a box that rounds away to nothing
    conditions no pixels, a box covering the frame conditions all of them, and
    either one still renders four frames and writes four sidecars.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import regional_ip as rip

    W, H = 832, 1216
    box = (0.25, 0.5, 0.75, 1.0)
    m = rip.region_mask(W, H, box, feather=0)
    px = m.load()
    check("region mask is one channel at frame size",
          m.mode == "L" and m.size == (W, H))
    check("inside the box conditions at full strength", px[W // 2, 900] == 255)
    check("outside the box conditions not at all",
          px[10, 10] == 0 and px[W - 10, 100] == 0 and px[10, 900] == 0)
    check("the box lands on the pixels its fractions name",
          rip.box_to_pixels(box, W, H) == (208, 608, 624, 1216))

    # A feather softens the silhouette edge; too much of one turns a region into
    # the whole frame, which is the failure that would look like it worked.
    soft = rip.region_mask(W, H, box, feather=24).load()
    check("a feathered mask still conditions its centre fully",
          soft[W // 2, 900] > 250)
    check("a feathered mask still leaves the far corner unconditioned",
          soft[5, 5] == 0)
    check("the feather is confined to the edge it softens",
          0 < soft[208, 900] < 255)

    check("coverage is reported as the fraction it is",
          abs(rip.coverage(box) - 0.25) < 1e-9)
    check("the free margins the plant needs are reported",
          rip.side_bands(box) == (0.25, 0.25, 0.5, 0.0))
    check("a whole-frame box reports no margin, so a guard can refuse it",
          rip.coverage((0.0, 0.0, 1.0, 1.0)) == 1.0
          and rip.side_bands((0.0, 0.0, 1.0, 1.0)) == (0.0, 0.0, 0.0, 0.0))


def test_a_box_that_names_no_region_is_refused_not_rounded():
    """Bad geometry must stop the render, not quietly become some other box."""
    sys.path.insert(0, str(REPO / "pipeline"))
    import regional_ip as rip

    def raises(fn):
        try:
            fn()
        except ValueError:
            return True
        return False

    check("an inverted box is refused", raises(lambda: rip.validate_box((0.8, 0.1, 0.2, 0.9))))
    check("a zero-area box is refused", raises(lambda: rip.validate_box((0.5, 0.1, 0.5, 0.9))))
    check("an edge outside the frame is refused",
          raises(lambda: rip.validate_box((-0.1, 0.0, 0.5, 0.5))))
    check("a box with the wrong number of edges is refused",
          raises(lambda: rip.validate_box((0.1, 0.2, 0.3))))
    check("a non-numeric edge is refused", raises(lambda: rip.parse_box("0.1,0.2,x,0.4")))
    check("a negative feather is refused",
          raises(lambda: rip.region_mask(64, 64, (0.1, 0.1, 0.9, 0.9), feather=-1)))
    check("a well-formed string parses to the box it names",
          rip.parse_box(" 0.18, 0.02 ,0.88,0.78 ") == (0.18, 0.02, 0.88, 0.78))

    # A box thinner than a pixel must still condition a pixel rather than
    # collapse to an empty crop that PIL would hand back as a 0-wide image.
    x0, y0, x1, y1 = rip.box_to_pixels((0.5, 0.5, 0.5001, 0.5001), 100, 100)
    check("a sub-pixel box never rounds away to nothing", x1 > x0 and y1 > y0)


def test_the_reference_crop_keeps_only_the_subject():
    """CLIP encodes the whole reference, so what is in it is what transfers.

    The r6 s2 frame carries three seedlings of its own; handing it in whole
    would push plant evidence into the character's region — the fusion r6 just
    cleared. Cropping to the subject is what makes the conditioning about the
    goblin.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import regional_ip as rip
    from PIL import Image

    src = Image.new("RGB", (832, 1216), (10, 20, 10))
    src.paste(Image.new("RGB", (200, 300), (240, 30, 30)), (300, 400))
    crop = rip.crop_reference(src, (0.16, 0.06, 0.90, 0.88))
    check("the crop is the pixel box of the fractions it was given",
          crop.size == (616, 997))
    check("subject pixels survive the crop", crop.getpixel((300 - 133 + 10, 400 - 73 + 10)) == (240, 30, 30))
    check("a full-frame crop returns the frame unchanged",
          rip.crop_reference(src, (0.0, 0.0, 1.0, 1.0)).size == src.size)
    check("the box describes itself for the sidecar",
          "53% of frame" in rip.describe((0.18, 0.02, 0.88, 0.78)))


# ── check_invention against its first labelled set ───────────────────────────
# These run in CI because check_invention.py's numpy import moved inside its
# measuring functions and eval_invention.py's statistics are pure python. The
# gate's RULE — the part that decides — was previously the one piece of the
# pipeline no test could execute, which is how it stayed 0-for-3 with every test
# green.

def test_nine_clips_cannot_license_a_threshold_however_cleanly_they_split():
    """The arithmetic that stops the next session shipping a fitted rule.

    Three positives among nine give 84 labelings, so a metric that separates the
    set perfectly earns an exact two-sided p of 2/84 and no better. This is not a
    modelling choice or a convention — it is the number of ways the labels could
    have fallen, and it is why 'it separates perfectly!' is not a result here.
    """
    import math
    sys.path.insert(0, str(REPO / "pipeline"))
    import eval_invention as ev

    pos, neg = [0.9, 0.8, 0.7], [0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    check("a perfect separator scores AUC 1.0", ev.auc(pos, neg) == 1.0)
    check("its exact two-sided p is 2/84 and not smaller",
          abs(ev.exact_p(pos, neg) - 2.0 / 84.0) < 1e-12)
    check("the best p this set can produce still fails after the correction "
          "for the metrics actually tried",
          ev.exact_p(pos, neg) * ev.K >= 0.05)
    # The honest exit: say what n would settle it. Twelve clips with five
    # invented is the first place a perfect separator clears alpha at this K.
    need = ev.sample_size_needed(ev.K)
    check("the harness names the sample size that would settle it",
          need is not None and need[0] > 9)
    check("that n is the SMALLEST one that clears the bar, not a round number",
          2.0 / math.comb(need[0], need[1]) * ev.K < 0.05
          and all(2.0 / math.comb(n, max(1, round(n * 0.4))) * ev.K >= 0.05
                  for n in range(4, need[0])))


def test_a_metric_that_points_the_wrong_way_is_not_a_separator():
    """`monotonic` splits the labelled set cleanly — backwards. A harness that
    scores separation on |AUC - 0.5| alone would rank it as a find; the direction
    has to be declared up front and checked, or a contradicted hypothesis reads
    as a confirmed one."""
    sys.path.insert(0, str(REPO / "pipeline"))
    import eval_invention as ev

    pos, neg = [0.1, 0.2, 0.3], [0.7, 0.8, 0.9]
    perfect, gap, _ = ev.separation(pos, neg, hi_is_positive=True)
    check("a backwards split is not reported as separated", perfect is False)
    check("and its gap is negative rather than absolute", gap < 0)
    check("declaring the other direction finds the same split",
          ev.separation(pos, neg, hi_is_positive=False)[0] is True)
    check("every candidate declares a direction before it is scored",
          all(isinstance(h, bool) for _, h, _ in ev.CANDIDATES))
    check("K is the number of candidates tried, not a constant someone typed",
          ev.K == len(ev.CANDIDATES))
    names = [n for n, _, _ in ev.CANDIDATES]
    check("no candidate is counted twice", len(names) == len(set(names)))


def test_leave_one_out_catches_the_threshold_that_only_fits_what_it_saw():
    """In-sample separation and LOO disagree exactly where it matters.

    These are the pair_moving_frac numbers: perfect in-sample, and the invented
    clip nearest the boundary is misclassified the moment the threshold is not
    allowed to see it. A harness reporting only 'separates perfectly' would hide
    that.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    import eval_invention as ev

    vals = [0.7986, 0.4861, 0.4306, 0.3333, 0.3542, 0.3889, 0.3611, 0.3333, 0.3333]
    labels = [True, True, True, False, False, False, False, False, False]
    check("the set is perfectly separated in sample",
          ev.separation([v for v, l in zip(vals, labels) if l],
                        [v for v, l in zip(vals, labels) if not l], True)[0])
    corr, tot, errs = ev.loo_threshold_accuracy(vals, labels, True)
    check("leave-one-out still misses the boundary clip", corr == tot - 1)
    check("and it names which one", errs and errs[0][0] == 2)


def test_the_labelled_set_is_internally_consistent():
    """A fixture that disagrees with itself is not ground truth. The clips are
    untracked by gate G5, so these fields are the whole of what a future reader
    gets."""
    import re
    import yaml
    fx = yaml.safe_load(
        (REPO / "pipeline" / "invention-labelled-set.yaml").read_text(encoding="utf-8"))
    clips = fx["clips"]
    inv = [c for c in clips if c["label"] == "invented"]
    cln = [c for c in clips if c["label"] == "clean"]
    check("the header's counts match the clips", len(inv) == fx["positives"]
          and len(cln) == fx["negatives"])
    check("every clip is labelled invented or clean",
          len(inv) + len(cln) == len(clips))
    check("every clip carries a full sha256",
          all(re.fullmatch(r"[0-9a-f]{64}", c["sha256"]) for c in clips))
    check("no clip is listed twice", len({c["path"] for c in clips}) == len(clips))
    check("every clip says why it is labelled the way it is",
          all(len(c.get("evidence", "")) > 40 for c in clips))
    check("every clip names the render batch it came from",
          all(c.get("set") for c in clips))
    oos = [c for c in clips if "held_out_from" in c]
    check("the header's out-of-sample count matches the clips",
          len(oos) == fx["out_of_sample"])
    # THE INVARIANT, not a count. A clip is out-of-sample when it came from a
    # DIFFERENT batch than the one it is held out from — which is the only thing
    # that makes it out-of-sample, and is checkable. The previous form asserted
    # "exactly one, and it is not beat 16", which was a fact about the b12 clip
    # rather than a rule, and would have rejected a later beat-16 batch that is
    # every bit as out-of-sample as b12 was.
    check("out-of-sample means the clip postdates a DIFFERENT batch",
          all(c["held_out_from"] != c["set"] for c in oos))
    check("and every in-sample clip belongs to the batch that was frozen",
          all(c["set"] == fx["set_id"] for c in clips if "held_out_from" not in c))


def test_the_committed_measurements_cover_every_candidate_and_every_clip():
    """The json is the record. If a candidate metric is added and nothing is
    re-measured, evaluate() silently skips it and the report shrinks without
    saying so — which would quietly lower K and make the correction look kinder
    than it is."""
    import json
    import yaml
    sys.path.insert(0, str(REPO / "pipeline"))
    import eval_invention as ev

    fx = yaml.safe_load(
        (REPO / "pipeline" / "invention-labelled-set.yaml").read_text(encoding="utf-8"))
    data = json.loads(
        (REPO / "pipeline" / "invention-labelled-set.measured.json").read_text(
            encoding="utf-8"))
    by_sha = {c["sha256"]: c for c in data["clips"]}
    check("every labelled clip has measurements on the record",
          all(c["sha256"] in by_sha for c in fx["clips"]))
    check("the measurements agree with the fixture's labels",
          all(by_sha[c["sha256"]]["label"] == c["label"] for c in fx["clips"]))
    wanted = {n for n, _, _ in ev.CANDIDATES}
    check("every candidate metric is measured on every clip",
          all(wanted <= set(c["metrics"]) for c in data["clips"]))
    check("the record carries the K its numbers were corrected with",
          data["K"] == ev.K)


def test_the_detector_states_its_measured_recall_and_states_it_correctly():
    """The gate's printed warning has to match what the gate actually does.

    This runs check_invention's real verdict() over the committed measurements
    and compares the recall it gets with the recall the warning claims. If
    someone repairs the rule, this fails and says so — the point is not to freeze
    0-of-3, it is to make the tool's claim about itself un-driftable.
    """
    import json
    import re
    sys.path.insert(0, str(REPO / "pipeline"))
    import check_invention as ci

    data = json.loads(
        (REPO / "pipeline" / "invention-labelled-set.measured.json").read_text(
            encoding="utf-8"))
    inv = [c for c in data["clips"] if c["label"] == "invented"]
    caught = sum(1 for c in inv if ci.verdict(c["metrics"])[0])
    m = re.search(r"is (\d+) OF (\d+)", ci.UNVALIDATED)
    check("the warning states a recall", m is not None)
    check(f"and it is the recall verdict() actually gets ({caught} of {len(inv)})",
          m is not None and int(m.group(1)) == caught
          and int(m.group(2)) == len(inv))
    check("the warning is printed on every run, not only on a flag",
          "print(UNVALIDATED)" in
          (REPO / "pipeline" / "check_invention.py").read_text(encoding="utf-8"))
    check("it points at the labels and the harness by path",
          "invention-labelled-set.yaml" in ci.UNVALIDATED
          and "eval_invention.py" in ci.UNVALIDATED)
    check("the files it points at exist",
          (REPO / "pipeline" / "invention-labelled-set.yaml").exists()
          and (REPO / "pipeline" / "eval_invention.py").exists())


def test_the_metric_that_cleared_the_correction_still_misses_what_it_never_saw():
    """`peak` clears the family-wise correction AND its boundary does not
    transfer. Both halves, because shipping the first without the second is the
    exact mistake this whole group of tests exists to prevent.

    On 2026-08-09 the set was grown to twelve for a pre-registered reason: n = 12
    with 5 invented is the smallest set at which a perfect separator earns a
    corrected p under 0.05, and `peak` duly earned 0.038. It is the first metric
    ever to clear here. But the three clips that took the set to twelve postdate
    both the candidate list and the leaderboard, so the boundary drawn on the
    eight original drift clips is a real prediction about them — and it calls
    both new invented clips clean (0.7477 and 0.7458 against a 0.7674 boundary).
    The perfect separation is perfect only after the threshold slides down.

    A future session reaching for `peak > 0.74` finds this measured rather than
    re-deriving it, which is the same service the churn note performs for churn.
    """
    import json
    sys.path.insert(0, str(REPO / "pipeline"))
    import eval_invention as ev

    data = json.loads(
        (REPO / "pipeline" / "invention-labelled-set.measured.json").read_text(
            encoding="utf-8"))
    rows = [{"name": c["name"], "label": c["label"],
             "out_of_sample": c["out_of_sample"], "metrics": c["metrics"]}
            for c in data["clips"]]
    res = {r["metric"]: r for r in ev.evaluate(rows)}
    peak = res["peak"]
    check("peak separates every labelled clip", peak["perfect"])
    check("and it clears the family-wise correction", peak["p_bonferroni"] < 0.05)
    check("it is the only candidate that does",
          sum(1 for r in res.values() if r["p_bonferroni"] < 0.05) == 1)
    # The half that stops it shipping.
    check("and its in-sample boundary still misses the clips it never saw",
          peak["out_of_sample_ok"] is False)
    check("the gate does not act on peak alone anyway",
          "m[\"peak\"] > 0.18" in
          (REPO / "pipeline" / "check_invention.py").read_text(encoding="utf-8"))


def test_striking_the_backwards_conjunct_would_flag_everything():
    """Why the obvious fix was not shipped, kept as an executable fact.

    `monotonic` runs backwards on the labelled set, so deleting it looks like
    free recall. It is not: on six-second LTX output the surviving conjuncts are
    true of every clip, and the gate goes from silent to flagging all twelve. A
    future session reaching for that edit finds the measurement here instead of
    re-deriving it.
    """
    import json
    sys.path.insert(0, str(REPO / "pipeline"))
    import check_invention as ci

    data = json.loads(
        (REPO / "pipeline" / "invention-labelled-set.measured.json").read_text(
            encoding="utf-8"))
    def no_mono(m):
        return bool((m["return_ratio"] > 0.88 and m["peak"] > 0.18)
                    or m["area_ratio"] > 1.30 or m["spread_ratio"] > 1.25)

    clean = [c for c in data["clips"] if c["label"] == "clean"]
    inv = [c for c in data["clips"] if c["label"] == "invented"]
    check("without the conjunct the rule catches all five",
          all(no_mono(c["metrics"]) for c in inv))
    check("and also flags every clean clip, which is not a detector",
          all(no_mono(c["metrics"]) for c in clean))
    check("the shipped rule is quiet on the same clean clips",
          not any(ci.verdict(c["metrics"])[0] for c in clean))
    check("peak > 0.18 is doing no work on this engine",
          all(c["metrics"]["peak"] > 0.18 for c in data["clips"]))


def test_an_agent_run_cannot_put_candidates_on_the_founders_screen():
    """`still_local.py` opened every still it drew, unconditionally.

    Correct for the loop it was written for — dad's 2026-07-27 directive is that
    the founder is sitting there and the picture appears — and wrong for every
    other caller. An agent rendering an unratified candidate had no way to use
    this Mac without throwing that candidate onto whatever screen was attached.
    r6 avoided it only by rendering on the 5090.

    So the default is asserted here too, not just the guard: a regression that
    silenced the founder's own loop would be the opposite mistake.
    """
    sys.path.insert(0, str(REPO / "pipeline"))
    from still_local import NO_OPEN_ENV, should_open

    check("the founder's interactive loop still opens its stills",
          should_open(True, {}))
    check("--no-open stops it", not should_open(False, {}))
    check("the env guard stops it without the flag",
          not should_open(True, {NO_OPEN_ENV: "1"}))
    for val in ("true", "YES", "On", " 1 "):
        check(f"the env guard reads {val!r} as set",
              not should_open(True, {NO_OPEN_ENV: val}))
    check("an empty env var is not a guard",
          should_open(True, {NO_OPEN_ENV: ""}))
    check("an unrelated value is not a guard",
          should_open(True, {NO_OPEN_ENV: "0"}))
    # The flag is the stronger statement: an explicit --no-open is not undone by
    # the environment saying nothing.
    check("--no-open wins over an unset env var",
          not should_open(False, {NO_OPEN_ENV: "0"}))


def test_a_review_page_the_build_never_copied_cannot_pass_the_gate(tmp: Path):
    """A page in the repo and not on the site is a FAILURE, not a quiet absence.

    2026-08-10: `review/approvals/index.html` was written, committed and asked
    for by name, and the URL 404'd. build_site.py published no such route, exit
    0; its link check passed; qa_local swept every route and passed. All three
    only ever read `_site/`, and a page that was never copied there is not a
    broken route — it is nothing at all. So the gate has to start from the repo,
    and the builder has to have a rule that picks the page up.
    """
    import build_site as bsite
    import qa_local as qa

    (tmp / "review" / "approvals").mkdir(parents=True)
    (tmp / "review" / "approvals" / "index.html").write_text("<h1>yes</h1>")
    (tmp / "review" / "v34-motion").mkdir()          # scratch: clips, no page
    (tmp / "review" / "v34-motion" / "b01.mp4").write_bytes(b"x")
    (tmp / "review" / ".cache").mkdir()
    (tmp / "review" / ".cache" / "index.html").write_text("<h1>no</h1>")

    found = [d.name for d in bsite.review_page_dirs(tmp / "review")]
    check("a review dir carrying index.html is a page", found == ["approvals"])
    check("a scratch dir of clips is not a page", "v34-motion" not in found)
    check("a dot-directory is not a page", ".cache" not in found)

    # The publisher stamps noindex; the review area is reachable, never
    # advertised (D17), and a hand-authored page does not pass through page().
    stamped = bsite.unlisted_html("<h1>yes</h1>")
    check("an unstamped page is published noindex", bsite.NOINDEX_META in stamped)
    check("...and keeps every word it had", "<h1>yes</h1>" in stamped)
    inhead = bsite.unlisted_html("<html><head><title>t</title></head><body>b</body>")
    check("the stamp lands inside <head> when there is one",
          inhead.index(bsite.NOINDEX_META) < inhead.index("<title>"))
    deliberate = '<head><meta name="robots" content="noindex, follow"></head>'
    check("a robots value the author chose is left alone",
          bsite.unlisted_html(deliberate) == deliberate)

    # The gate. `site` holds no review/ at all — the exact 2026-08-10 state.
    (tmp / "_site").mkdir()
    gaps = qa.unpublished_review_pages(repo=str(tmp), site=str(tmp / "_site"),
                                       is_tracked=lambda rel: True)
    check("a tracked page missing from _site fails, named",
          gaps == [("review/approvals/index.html", "unpublished")])

    untracked = qa.unpublished_review_pages(repo=str(tmp), site=str(tmp / "_site"),
                                            is_tracked=lambda rel: False)
    check("and an uncommitted one fails for the other reason",
          untracked == [("review/approvals/index.html", "untracked")])
    check("both reasons carry a remedy the reader can run",
          all(r in qa.REVIEW_GAP_REMEDY for _, r in gaps + untracked))

    built = tmp / "_site" / "review" / "approvals"
    built.mkdir(parents=True)
    (built / "index.html").write_text("<h1>yes</h1>")
    check("a page the build published is not a gap",
          qa.unpublished_review_pages(repo=str(tmp), site=str(tmp / "_site"),
                                      is_tracked=lambda rel: True) == [])

    # And the live page itself, so the rule cannot pass on a fixture while the
    # one page this was written for stops matching it.
    if (REPO / "review" / "approvals" / "index.html").exists():
        check("the real approvals page is one the builder publishes",
              "approvals" in [d.name for d in bsite.review_page_dirs()])


def test_the_repo_owner_is_read_from_the_platform_that_is_building():
    """The trap the 2026-08-10 owner change set, pinned so it cannot be reset.

    `build_site.py` used to read `GITHUB_REPOSITORY` with a hardcoded default.
    GitHub Actions sets that variable; VERCEL DOES NOT — it sets
    `VERCEL_GIT_REPO_OWNER` / `VERCEL_GIT_REPO_SLUG`. banyan.city builds on
    Vercel and the free mirror builds on Actions, so when the repo moved the
    mirror silently corrected itself while production kept publishing the old
    owner: two surfaces disagreeing, neither erroring, nothing to notice.

    So the contract is about PRECEDENCE, not about a name. Whichever platform
    is running the build gets to answer, and no builder is allowed to keep its
    own copy of the answer.
    """
    import os
    import re

    import repo_slug

    env = {"BANYAN_GH_REPO": "", "GITHUB_REPOSITORY": "",
           "VERCEL_GIT_REPO_OWNER": "", "VERCEL_GIT_REPO_SLUG": ""}
    saved = {k: os.environ.get(k) for k in env}

    def with_env(**kw):
        for k in env:
            os.environ.pop(k, None)
        for k, v in kw.items():
            os.environ[k] = v
        return repo_slug.gh_repo()

    try:
        check("Vercel's variables are read at all — the whole bug in one line",
              with_env(VERCEL_GIT_REPO_OWNER="someone",
                       VERCEL_GIT_REPO_SLUG="banyan-city") == "someone/banyan-city")
        check("Actions' variable still wins where both exist, so a fork stays a fork",
              with_env(GITHUB_REPOSITORY="forker/banyan-city",
                       VERCEL_GIT_REPO_OWNER="someone",
                       VERCEL_GIT_REPO_SLUG="banyan-city") == "forker/banyan-city")
        check("an explicit override outranks both",
              with_env(BANYAN_GH_REPO="me/mine",
                       GITHUB_REPOSITORY="forker/banyan-city") == "me/mine")
        # A half-set pair is the shape a partial platform migration takes, and
        # "owner/" is a URL that 404s rather than a build that fails loudly.
        check("half of Vercel's pair is not an answer",
              with_env(VERCEL_GIT_REPO_OWNER="someone") != "someone/")
        check("and neither is a slug with no owner in it",
              "/" in with_env(GITHUB_REPOSITORY="no-slash-here"))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    # NO BUILDER KEEPS ITS OWN COPY. This is the half that stops the sweep from
    # having to happen again: eight files each held the literal last time, and
    # every one of them was written by copying the file next door. The retired
    # owner is the thing being banned — a live URL naming `olegmlkvorg` is a
    # link that survives today only on a GitHub redirect that one accidental
    # repo creation at the old name would delete.
    # A `#` comment is exempt on purpose: the move left annotations behind that
    # are worth keeping ("this URL used to be X, it 404s now"), and REPO-MOVE.md's
    # rule for historical records is annotate, never erase. What is banned is the
    # old name reaching a URL the code actually builds or fetches.
    retired = re.compile(r"olegmlkvorg")
    stale = []
    for py in sorted((REPO / "pipeline").rglob("*.py")):
        if py.name in ("repo_slug.py", "test_pipeline.py"):
            continue
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if retired.search(line) and not line.lstrip().startswith("#"):
                stale.append(f"{py.name}:{i}")
    for s in stale:
        print(f"      x  {s} still names the retired owner in live code")
    check("no pipeline module names the retired owner outside a comment", not stale)

    # And the builders that publish links get theirs from the one place, so a
    # future move is a one-file edit rather than an archaeology exercise.
    for mod in ("build_site", "build_sim", "build_pulse", "build_shotboard",
                "build_status", "harvest_sap", "render_t1", "ops_board"):
        src = (REPO / "pipeline" / f"{mod}.py").read_text(encoding="utf-8")
        check(f"{mod}.py asks repo_slug rather than spelling the owner",
              "import repo_slug" in src)


def test_the_courier_and_the_telemetry_daemon_own_different_branches():
    """The push war, pinned shut.

    Until 2026-08-11 `pipeline/telemetry.py` and the courier in `box_runner.py`
    both wrote `farm-results-rtx5090`. The courier force-pushes from a tree with
    no telemetry.json, so every heartbeat deleted the vitals; the daemon watched
    the tip and re-published within the minute; each republish was another chance
    for the courier's next push to lose the race. On the night of 2026-08-10 the
    courier lost about ten in a row and render claims stalled some twenty minutes.

    Nothing about that is fixable by retry tuning, so the fix was to give each
    writer a branch. This test exists so nobody can quietly point them back at one.
    """
    import re

    import telemetry

    courier_src = (REPO / "pipeline" / "box_runner.py").read_text(encoding="utf-8")
    m = re.search(r'^COURIER_BRANCH\s*=\s*"([^"]+)"', courier_src, re.M)
    check("the courier still declares the branch it owns", m is not None)
    if m:
        check("the telemetry daemon does not publish to the courier's branch",
              telemetry.BRANCH != m.group(1))
        check("the branch telemetry left behind is the one the courier kept",
              telemetry.LEGACY_BRANCH == m.group(1))
    check("telemetry publishes to a branch named for what it carries",
          telemetry.BRANCH == "farm-telemetry-rtx5090")


def test_a_plate_that_rendered_is_not_a_plate_that_failed():
    """The beat slug, and the six plates it cost us.

    2026-08-14: six scene-plate specs were cloned from a template whose filename
    stem predated the beat SLUG the samplers write. `05-the-patrol-ipa-r0-w015-s0.png`
    landed on disk; `05-ipa-r0-w015-s0.png` was what the spec declared. Every step
    exited 0, thirty-two files published, and the runner retired all six FAILED on
    rc 92 — the same rc a crashed render gets. Beats 05, 09 and 11 sat unused for a
    day, and the wave that followed animated costume identity cards for six beats
    because the real plates read as lost.

    Two things are pinned here. The declared name resolves through the missing
    slug when exactly one file can be meant, and a job where NOTHING landed is a
    different rc from a job where some of it did — because "published nothing" is
    fixed by re-publishing in seconds and "render crashed" by re-rendering in
    ninety minutes, and the queue used to spell them identically.
    """
    import tempfile

    import box_runner as br

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "05-the-patrol-ipa-r0-w015-s0.png").write_bytes(b"x")
        declared = str(d / "05-ipa-r0-w015-s0.png")
        got, note = br.resolve_artifact(declared)
        check("the slugless declared name resolves to the file on disk",
              got == str(d / "05-the-patrol-ipa-r0-w015-s0.png"))
        check("and it says the spec is still wrong",
              bool(note) and "FIX THE SPEC" in note)

        exact = str(d / "05-the-patrol-ipa-r0-w015-s0.png")
        check("an exact match resolves with nothing to report",
              br.resolve_artifact(exact) == (exact, None))

        # Two slugged candidates for one declared name: guessing which frame the
        # job meant is the silent substitution the check exists to prevent.
        (d / "05-the-sprint-ipa-r0-w015-s0.png").write_bytes(b"x")
        got2, note2 = br.resolve_artifact(declared)
        check("two candidates resolve to neither", got2 is None)
        check("and the ambiguity is named", bool(note2) and "ambiguous" in note2)

        missing = str(d / "05-nothing-like-this.png")
        check("a name nothing on disk can satisfy stays missing",
              br.resolve_artifact(missing) == (None, None))

        present, absent, notes = br.resolve_artifacts(
            [exact, str(d / "05-gone-s9.png")])
        check("resolve_artifacts keeps the found and the absent apart",
              present == [exact] and absent == [str(d / "05-gone-s9.png")])
        check("and reports no slug note when there was no slug rescue",
              notes == [])

        listing = br.neighbours_of([str(d / "05-gone-s9.png")])
        check("the listing answers 'then what DID it write?'",
              len(listing) == 1 and "05-the-patrol-ipa-r0-w015-s0.png" in listing[0])

    check("published-nothing has an rc of its own",
          br.RC_PUBLISHED_NOTHING != br.RC_ARTIFACTS_MISSING)
    src = (REPO / "pipeline" / "box_runner.py").read_text(encoding="utf-8")
    check("the runner still distinguishes the two in execute()",
          "failed_step = \"publish-empty\"" in src
          and "rc = RC_PUBLISHED_NOTHING" in src)
    check("and it says so out loud rather than only in an rc",
          "PUBLISHED NOTHING" in src)
    check("a partial landing is still the old artifact-check failure",
          "rc = RC_ARTIFACTS_MISSING" in src)


def test_the_scene_plate_specs_declare_the_names_the_sampler_writes():
    """The same defect, checked where it is actually authored.

    The runner now tolerates a slugless declaration, but tolerating it is not
    the same as it being right: the resolver refuses the moment two frames could
    be meant. Every spec that names a `<beat>-...` png under a sampler out-dir
    must carry the beat slug, so no clone re-introduces this.
    """
    import re as _re

    import yaml

    # A sampler frame is `<beat>-<slug>-<wave1|ipa>-...`. If the marker follows
    # the beat number directly, the slug was dropped and the name matches nothing.
    slugless = _re.compile(r"^\d{2}-(wave\d|ipa)\b")
    bad = []
    for spec in sorted((REPO / "pipeline" / "jobs").glob("*.yaml")):
        if spec.name == "index.yaml":
            continue
        try:
            doc = yaml.safe_load(spec.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        arts = doc.get("artifacts")
        for art in (arts if isinstance(arts, list) else []):
            name = str(art).replace("\\", "/").rsplit("/", 1)[-1]
            if slugless.match(name):
                bad.append(spec.name + " -> " + name)
    check("no job spec declares a sampler frame without its beat slug",
          not bad)
    if bad:
        print("      " + "; ".join(bad[:6]))


def test_every_reader_falls_back_to_where_the_vitals_used_to_be():
    """A reader pointed at the new branch alone would go blind on the old data.

    The box's scheduled task is re-enabled by hand, so between deploying this and
    someone restarting the daemon the freshest sample is still only in the old
    place. A page that answered "not heard from" through that window would be
    reporting our own deploy sequence as a dead machine, which is exactly the
    class of claim the status page is not allowed to make.
    """
    import build_pulse
    import build_sim
    import pulse_series
    import telemetry

    check("build_sim maps a machine's courier branch to its vitals branch",
          build_sim.telemetry_branch("farm-results-rtx5090") == telemetry.BRANCH)
    check("that mapping is per-machine, not a special case for the 5090",
          build_sim.telemetry_branch("farm-results-msi") == "farm-telemetry-msi")
    check("the pulse cache reads the new branch first",
          pulse_series.TELEMETRY_BRANCH == telemetry.BRANCH)
    check("the pulse cache still knows the old one",
          pulse_series.TELEMETRY_BRANCH_LEGACY == telemetry.LEGACY_BRANCH)
    check("the pulse page's live tail asks the new branch",
          telemetry.BRANCH in build_pulse.TELEMETRY_URL)
    check("the pulse page's live tail keeps the old URL as its fallback",
          telemetry.LEGACY_BRANCH in build_pulse.TELEMETRY_URL_LEGACY)


def test_a_rev_parse_that_failed_is_not_a_sha():
    """Handed a name it cannot resolve, `git rev-parse` echoes the NAME to stdout
    and reports the failure only in its exit code.

    This is not a hypothetical. `publish()` walks back over its own commits to
    find what to rebuild on, and on a branch only it writes that walk asks for the
    parent of the root commit every single cycle. Reading stdout alone took the
    literal string "<sha>^" for a parent — a perfectly truthy value — and every
    publish after the very first one died in ls-tree. Caught 2026-08-11 by running
    the thing four times against a scratch remote instead of once.
    """
    import types

    import telemetry

    failed = types.SimpleNamespace(returncode=128, stdout="deadbeef^\n", stderr="fatal:")
    check("a failed rev-parse yields no sha, whatever it printed",
          telemetry.rev(failed) == "")
    ok = types.SimpleNamespace(returncode=0, stdout="deadbeef\n", stderr="")
    check("a successful one yields the sha", telemetry.rev(ok) == "deadbeef")


def test_the_box_publishes_its_own_queue_and_never_a_zero_it_did_not_measure():
    """The freshness fix, pinned at the point where it can rot silently.

    Roman, 2026-08-13: "why is the banyan.city/status only updating when i
    freaking remind you about it??" The queue tile printed
    measured/box-queue.yaml, which changes only when a session hand-commits it,
    so the page was exactly as fresh as the last nag. The box now publishes its
    queue in its five-minute telemetry pulse and the reader's browser draws it.

    What must not rot: a reading that FAILED must never come back as a queue that
    is EMPTY. Those two are one keystroke apart in every direction here — a
    missing directory, an unreadable job file, a listdir that raised — and they
    render as opposite claims: "the box is idle, nothing is waiting" versus "we
    could not see". The first is the lie the whole status page is arranged
    against.
    """
    import json as _json
    import os
    import tempfile
    import time

    import box_job_minutes
    import telemetry

    # The medians the page multiplies live counts by were measured PER KIND by
    # box_job_minutes. If the two tables drift, a live count gets multiplied by
    # the median of something else and the page prints a confident wrong hour.
    check("the box's queue kinds are box_job_minutes' kinds, exactly",
          list(telemetry.QUEUE_KINDS) == [tuple(k) for k in box_job_minutes.KINDS])

    def job(*argv):
        return _json.dumps({"steps": [{"argv": list(argv)}]})

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for sub in ("ready", "running", "done", "failed"):
            (root / sub).mkdir()
        now = time.time()
        (root / "ready" / "job-a.json").write_text(job("py", "ltx_i2v.py"))
        (root / "ready" / "job-b.json").write_text(job("py", "render_wave_sample.py"))
        (root / "running" / "job-r.json").write_text(job("py", "ltx_i2v.py"))
        lg = root / "running" / "job-r.log"
        lg.write_text("rendering")
        os.utime(lg, (now - 120, now - 120))
        (root / "failed" / "job-x.json").write_text("{}")
        (root / "done" / "job-d.json").write_text("{}")
        (root / "heartbeats.jsonl").write_text(
            '{"event":"runner_up","ts":"2026-08-13T08:00:00Z"}\n'
            '{"event":"job_start","job":"job-r","ts":"2026-08-13T09:00:00Z"}\n')

        # THE LOCK IS NOT A BARE PID. box_runner writes "<pid> <utc> boot=<n>";
        # reading it with int() over the whole file raises, and the first cut of
        # this reported "runner unknown" about a box that was rendering at the
        # time — caught only by running it against the real machine.
        # boot_id() answers 0 off the box (it reads /proc/stat, and this suite
        # runs on a Mac), and 0 means "cannot tell", which correctly disables the
        # boot comparison. Pin it so the Windows logic is actually exercised
        # here rather than skipped on every machine that runs the tests.
        real_boot = telemetry.boot_id
        telemetry.boot_id = lambda: 1786500000
        try:
            (root / "runner.lock").write_text(
                "%d 2026-08-13T09:39:02Z boot=1786500000\n" % os.getpid())
            check("a live runner is seen through the real lock format",
                  telemetry.runner_alive(root) is True)
            (root / "runner.lock").write_text(
                "%d 2026-08-13T09:39:02Z boot=1786000000\n" % os.getpid())
            check("a lock from before this boot is stale however alive its pid looks",
                  telemetry.runner_alive(root) is False)
            (root / "runner.lock").write_text("not a pid at all\n")
            check("an unreadable lock is unknown, never a claim either way",
                  telemetry.runner_alive(root) is None)
            (root / "runner.lock").unlink()
            check("no lock file at all is unknown too, not a dead runner",
                  telemetry.runner_alive(root) is None)
            # A pid nobody is running is genuinely gone; a pid we merely may not
            # query is NOT, and collapsing the two put "NOTHING IS DRAINING IT"
            # on the page while the box was mid-render (2026-08-13).
            check("a pid that does not exist reads as gone",
                  telemetry.process_state(999999) is False)
            check("our own pid reads as alive", telemetry.process_state(os.getpid()) is True)
            check("a live runner whose pid we cannot query is never reported dead",
                  telemetry.process_state(1) is not False)
        finally:
            telemetry.boot_id = real_boot
        # Written with the REAL boot id, for the queue_sample() check below. The
        # pinned value must not outlive the block: boot_id reads /proc/stat, which
        # a Linux CI runner HAS and a Mac does not, so a lock left stamped with a
        # made-up boot passes here and fails there. It did exactly that.
        (root / "runner.lock").write_text(
            "%d 2026-08-13T09:39:02Z boot=%d\n" % (os.getpid(), telemetry.boot_id()))

        q = telemetry.queue_sample(root=root, now=now)
        check("the runner's liveness rides along with the counts",
              q["runner_alive"] is True)
        check("it counts what is waiting", q["ready"] == 2)
        check("it counts what is rendering", q["running"] == 1)
        check("a corpse in failed/ is counted, not hidden", q["failed"] == 1)
        check("it names the running job", q["running_job"] == "job-r")
        check("the running job's log age is the liveness signal, in seconds",
              118 <= q["running_log_age_sec"] <= 122)
        check("the kind mix accounts for every queued job",
              q["kinds"] == {"ltx": 2, "still": 1})
        check("the last heartbeat comes back as an event", q["last_event"] == "job_start")
        check("its stamp is parsed as UTC, not as box-local time",
              q["last_event_at"] == 1786611600)

        # A job file it cannot read means the MIX is incomplete. A partial mix
        # would price the queue as though the unreadable jobs were not in it, so
        # the whole mix goes rather than the page quoting a short hour.
        (root / "ready" / "job-c.json").write_text("{ this is not json")
        q2 = telemetry.queue_sample(root=root, now=now)
        check("one unreadable job suppresses the whole kind mix", "kinds" not in q2)
        check("but the counts it could take are still published", q2["ready"] == 3)

    # THE REFUSAL. No queue directory is not an empty queue.
    with tempfile.TemporaryDirectory() as td:
        gone = telemetry.queue_sample(root=Path(td) / "not-there", now=time.time())
        check("a missing queue directory reports an error", bool(gone.get("error")))
        for k in ("ready", "running", "done_today", "failed"):
            check(f"and does not invent {k}", k not in gone)

    # distil() stays pure and omits what it was not handed — an old published
    # file has no queue block and every reader has to survive that.
    rows = [{"ts": int(time.time()), "gpu_util": 12.0, "gpu_power_w": 40.5}]
    bare = telemetry.distil(rows, gpu="x")
    check("no queue block unless one was sampled", "queue" not in bare)
    check("no power block unless one was sampled", "power" not in bare)
    check("the newest power draw rides along for the tile",
          bare.get("gpu_power_w") == 40.5)
    blank = telemetry.distil(rows, power={"ac": None, "battery_pct": None,
                                          "battery_minutes": None})
    check("an all-unknown power reading is not published as a reading",
          "power" not in blank)


def test_the_box_publishes_what_it_is_making_and_what_it_just_made():
    """The dropdown's data (Roman, 2026-08-13: "you should make it so you can see
    exactly what is being generated on the status page and see the images when
    its generated").

    THE PUBLISHED PATH CANNOT BE GUESSED FROM THE JOB. A job's `artifacts` records
    where the render WROTE the file, and the publish step's destination is a
    string inside an inline python step — on this box the task
    `ep2-b15-seedC-0813` published into a directory called `ep2-b15-seedB`. So the
    courier directory is listed and what is there is reported; anything derived
    from the task name would be a confident 404 in the reader's browser.
    """
    import json as _json
    import os
    import tempfile
    import time

    import telemetry

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "courier-box" / "farm-out"
        now = time.time()
        d1 = out / "ep2-b05twin-wave-0813"
        d1.mkdir(parents=True)
        (d1 / "05-the-patrol.mp4").write_bytes(b"v" * 4000)
        (d1 / "b05-init-704x1280.png").write_bytes(b"i" * 900)
        (d1 / "05-the-patrol.mp4.meta.yaml").write_text("m")
        (d1 / "job.sha256").write_text("s")
        (d1 / "half-copied.png").write_bytes(b"")
        (out / "box").mkdir(parents=True)
        (out / "box" / "a-log-tail.png").write_bytes(b"n" * 10)
        os.utime(d1 / "05-the-patrol.mp4", (now - 60, now - 60))
        os.utime(d1 / "b05-init-704x1280.png", (now - 70, now - 70))

        r = telemetry.results_sample(out=out, now=now)
        names = [i["name"] for i in r["items"]]
        check("the newest published file comes first", names[0] == "05-the-patrol.mp4")
        check("its path is the one the branch will serve",
              r["items"][0]["path"] ==
              "farm-out/ep2-b05twin-wave-0813/05-the-patrol.mp4")
        # The still is stamped BEFORE the clip — copy2 keeps source mtimes, so
        # the gap is however long the render took (measured 5-7 min on the box).
        check("a video is paired with the still beside it, so the strip shows a picture",
              r["items"][0].get("poster") ==
              "farm-out/ep2-b05twin-wave-0813/b05-init-704x1280.png")
        # These directories get reused between rounds, so an image that is merely
        # in the same folder can be a leftover from a previous take — and a
        # poster is read as a frame OF the clip beneath it.
        d2 = out / "reused-dir"
        d2.mkdir()
        (d2 / "new-take.mp4").write_bytes(b"v" * 100)
        (d2 / "last-rounds-frame.png").write_bytes(b"i" * 100)
        os.utime(d2 / "new-take.mp4", (now - 30, now - 30))
        os.utime(d2 / "last-rounds-frame.png", (now - 90000, now - 90000))
        stale = telemetry.results_sample(out=out, now=now)
        take = [i for i in stale["items"] if i["name"] == "new-take.mp4"][0]
        check("a clip is not postered with a frame from a previous round",
              "poster" not in take)

        check("sidecars and checksums are not results",
              not any(n.endswith((".yaml", ".sha256")) for n in names))
        check("a zero-byte file is a copy in progress, not a result",
              "half-copied.png" not in names)
        check("the courier's own text drop is not a result",
              "a-log-tail.png" not in names)
        # The still is the clip's poster, so it is not ALSO a tile of its own —
        # otherwise the strip shows each result twice.
        check("a still used as a poster is not repeated as its own tile",
              "b05-init-704x1280.png" not in names)
        check("it names the branch the paths are relative to",
              r["branch"] == telemetry.COURIER_BRANCH)

    # Nothing published is a fact, and it is not an empty success.
    with tempfile.TemporaryDirectory() as td:
        gone = telemetry.results_sample(out=Path(td) / "nope", now=time.time())
        check("an absent courier directory says so", bool(gone.get("error")))
        check("and offers no items to render", "items" not in gone)

    # The running job's own record, for the "what is on the card" line.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "running").mkdir()
        spec = {"task": "ep2-b05twin-wave-0813", "node": "002b-first-citizen",
                "beat": 5, "attempts": 1, "started_at": "2026-08-13T10:18:14Z",
                "steps": [{"argv": ["py", "ltx_i2v.py", "--stage", "render"]}],
                "artifacts": ["C:\\banyan-farm\\ep2-b05\\05-the-patrol.mp4"]}
        (root / "running" / "j.json").write_text(_json.dumps(spec))
        cur = telemetry.current_job(root, "j")
        check("the card's work is named by beat and node",
              cur["beat"] == 5 and cur["node"] == "002b-first-citizen")
        check("its start is a unix stamp the browser can age",
              cur["started_at"] == 1786616294)
        check("its kind is classified so the page can price it", cur["kind"] == "ltx")
        # A windows path through os.path.basename on a posix box comes back WHOLE,
        # and this string goes on a public page.
        check("what it is making is a filename, never somebody's directory tree",
              cur["makes"] == ["05-the-patrol.mp4"])
        check("a job record that will not parse yields nothing, not a broken line",
              telemetry.current_job(root, "missing") == {})


def test_the_depth_series_leaves_a_gap_where_it_could_not_look():
    """The rolling queue depth the status page draws a sparkline from.

    A CHART INTERPOLATES, which makes this the easiest place in the file to tell
    a lie by accident. One 0 written while the queue directory was unreadable
    draws a clean dip to empty across the whole outage — a picture of an idle box
    on a night it was fully loaded. A failed reading is therefore not recorded at
    all and the gap stays a gap; a queue that really is empty is a measurement and
    is recorded as the zero it is.

    It lives on disk rather than in the daemon, because the daemon is restarted by
    hand whenever telemetry.py changes — four times on the afternoon this was
    written — and a 24-hour series held in memory would almost never be 24 hours.
    """
    import json
    import tempfile
    import time

    import telemetry

    with tempfile.TemporaryDirectory() as td:
        csv = Path(td) / "queue-depth.csv"
        now = time.time()
        for depth, back in ((2, 900), (5, 600), (3, 300)):
            telemetry.depth_history({"ready": depth - 1, "running": 1},
                                    now=now - back, record=True, path=csv)
        check("each publish adds one point",
              [d for _t, d in telemetry.depth_history({}, now=now, path=csv)] == [2, 5, 3])

        telemetry.depth_history({"error": "the queue directory is not there"},
                                now=now - 120, record=True, path=csv)
        check("a reading that FAILED is a gap, never a dip to zero",
              len(telemetry.depth_history({}, now=now, path=csv)) == 3)

        telemetry.depth_history({"ready": 0, "running": 0}, now=now - 60,
                                record=True, path=csv)
        series = telemetry.depth_history({}, now=now, path=csv)
        check("a queue that really is empty is measured, and is a zero",
              len(series) == 4 and series[-1][1] == 0)

        before = len(series)
        telemetry.depth_history({"ready": 9, "running": 1}, now=now,
                                record=False, path=csv)
        check("a read-only rebuild cannot stamp points into the history",
              len(telemetry.depth_history({}, now=now, path=csv)) == before)

        # It survives the restart that loses an in-memory series.
        check("the history is read back off disk, not held in the process",
              len(telemetry.depth_history({}, now=now, path=csv)) == before)

        with csv.open("w", encoding="utf-8") as fh:
            for i in range(400):
                fh.write("%d,%d\n" % (int(now - 400 * 300 + i * 300), i % 7))
            fh.write("%d,99\n" % int(now - 90000))
            fh.write("this line is torn\n")
        series = telemetry.depth_history({}, now=now, record=False, path=csv)
        check("the series is capped at a day of five-minute publishes",
              len(series) <= telemetry.DEPTH_MAX_POINTS)
        check("nothing older than the window survives",
              all(t >= now - 86400 for t, _d in series))
        check("a row torn by a kill mid-write is skipped, not fatal",
              all(isinstance(d, int) for _t, d in series))

    # THE SHAPE IS A CONTRACT NOW. build_sim's sparkline (status-charts lane,
    # 6f327a20) draws straight off this array, and it hardens itself by filtering
    # element-wise and re-sorting rather than trusting the publisher — which is
    # right for a file a browser fetches off a branch, and is no reason for the
    # publisher to start emitting something else. Anything that reaches the wire
    # is a pair of ints, depth never negative, epochs strictly ascending.
    with tempfile.TemporaryDirectory() as td:
        csv = Path(td) / "queue-depth.csv"
        now = time.time()
        for depth, back in ((3, 1200), (0, 900), (7, 600), (1, 300)):
            telemetry.depth_history({"ready": depth, "running": 0},
                                    now=now - back, record=True, path=csv)
        series = telemetry.depth_history({}, now=now, path=csv)
        check("every point is a pair",
              all(isinstance(p, list) and len(p) == 2 for p in series))
        check("both halves are whole numbers, never floats or strings",
              all(isinstance(t, int) and isinstance(d, int) for t, d in series))
        check("a depth is never negative", all(d >= 0 for _t, d in series))
        check("epochs are strictly ascending, so a chart need not sort",
              all(series[i][0] < series[i + 1][0] for i in range(len(series) - 1)))
        check("and it survives a JSON round trip unchanged",
              json.loads(json.dumps(series)) == series)

    # queue_block is what the publish paths send, and the field is OPTIONAL —
    # every reader already survives the whole queue block being absent.
    import inspect
    src = inspect.getsource(telemetry.queue_block)
    check("the series rides along inside the queue block", "depth_series" in src)
    check("and is left out entirely when there is no history yet",
          "if series:" in src)


def test_the_dropdown_will_not_render_whatever_a_filename_says():
    """Every string in the dropdown was written by a machine on the render box —
    job ids, node names, and the filenames a render chose for its own output.

    Two rules hold that safe and both live in LIVE_JS: values reach the DOM
    through textContent, and a media path becomes a URL only after matching one
    shape. A filename is an attacker-controllable string the moment anything
    off-box can queue a job, and "the render named its mp4 that" is a poor reason
    to have shipped script into the page.
    """
    import build_sim

    js = build_sim.LIVE_JS
    check("the dropdown validates a path before it becomes a URL", "safePath" in js)
    check("and anchors it to the published directory", "^farm-out" in js)
    check("and refuses anything that climbs out of it", 'indexOf("..")' in js)
    # `.innerHTML`, not the bare word: the rule is written down in a comment two
    # lines above the code that follows it, and a test that cannot tell the
    # comment from an assignment fails on its own documentation.
    check("the dropdown never assigns innerHTML", ".innerHTML" not in js)
    check("videos are not downloaded until asked", 'preload", "none"' in js)
    check("images load only as they are needed", 'loading", "lazy"' in js)
    # An unpushed frame must say so rather than showing a broken image.
    check("a frame the courier has not pushed explains itself",
          "not on the branch yet" in js)

    src = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")
    check("the fold is emitted collapsed", '<details class="peek"' in src)
    for el in ("q-peek", "q-peek-body"):
        check(f"the builder emits {el}", f'id="{el}"' in src)
        check(f"LIVE_JS looks up {el}", f'"{el}"' in js)


def test_the_queue_is_a_picture_and_the_picture_cannot_lie():
    """The queue section became blocks on 2026-08-14 ("can you make the queue
    more visuals and less text?"), and a picture can tell every lie a sentence
    can while being much harder to check.

    Four of them, and each has a rule here:

      1. A STRIP SHORTER THAN THE COUNT BESIDE IT. The box publishes counts by
         kind, and a mix that does not add up is ordinary — a reading of a queue
         that moved while it was being read. Blocks for the jobs the mix does
         not account for are drawn in the neutral colour rather than left out,
         because a five-block strip under the numeral 8 is a wrong picture.
      2. AN IDLE CARD DRAWN OVER A READING NOBODY TOOK. "Empty" and "not read"
         are different states and only one of them may show the idle block.
      3. A BEAT NUMBER ON A WAITING BLOCK. Only the running job has a record;
         inventing a beat for a waiting one is the page making up the fact it
         exists to report.
      4. AMBER IN THE STRIP. The colour law is --leaf for the machine's work and
         --sap for what is waiting on the author. Everything in this queue waits
         on a card, so an amber block would say the opposite of what is true.
    """
    import re as _re

    import build_sim as bs

    # 1. the mix that does not add up
    blocks, hidden, counts = bs.queue_blocks({"ltx": 3}, ready=5, running=2)
    check("every job gets a block, even the ones the mix cannot name",
          len(blocks) == 7 and hidden == 0)
    check("...and the ones it cannot name are drawn as unknown, not as ltx",
          counts.get(None) == 4 and counts.get("ltx") == 3)
    over = bs.queue_blocks({"ltx": 99}, ready=1, running=1)[0]
    check("...and a mix that over-counts is trimmed to the measured count",
          len(over) == 2)

    # the running job leads, wears its own kind, and is the only one marked
    lead, _h, _c = bs.queue_blocks({"ltx": 1, "still": 3}, ready=3, running=1,
                                   running_kind="ltx")
    check("the running job is the first block and carries its own kind",
          lead[0]["running"] and lead[0]["kind"] == "ltx")
    check("...and it is the only block marked as running",
          sum(1 for b in lead if b["running"]) == 1)

    # 3. what a block is allowed to say
    check("a waiting block names a kind and never a beat",
          bs.queue_block_words({"kind": "ltx", "running": False})
          == "waiting — a motion take")
    check("...and a kind the snapshot never named says exactly that",
          "does not name the kind" in bs.queue_block_words({"kind": None}))

    # 2. empty is a state; unread is a different one
    idle = bs.queue_strip_html([])
    check("an empty queue draws the idle block, not a bare zero",
          "card idle" in idle and "qstrip" in idle)
    check("...and LIVE_JS will not draw it over a report with no queue block",
          "if (!wrap || !q) return;" in bs.LIVE_JS)

    # 4. the colour law, in the CSS and in the classes
    qcss = bs.SIM_CSS[bs.SIM_CSS.index(".qstrip {"):bs.SIM_CSS.index(".qspark {")]
    check("no block, swatch or bar in the queue picture is amber",
          "--sap" not in qcss)
    # `var(--alarm, #e2564d)` is the page's one deliberate literal and predates
    # this section: --alarm is not defined in site_theme.py, so the fallback is
    # the colour rather than a spare. Everything else must be a token.
    check("...and every colour it does use is a theme token",
          not _re.search(r"#[0-9a-fA-F]{3,8}\b",
                         _re.sub(r"var\(--alarm,[^)]*\)", "", qcss)))

    # the progress-ish bar is never called progress
    js = bs.LIVE_JS
    check("the running job's bar is labelled an estimate, never a completion",
          "an estimate, not progress" in js
          and "a measurement of how far through it is" in js)
    check("...and it is drawn as SVG, like every other picture on this page",
          '"qnow-svg"' in js and "createElementNS" in js)

    # the strip and its key are built, not spliced
    check("the redrawn strip never assigns innerHTML", ".innerHTML" not in js)
    src = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")
    # The strip and its key take their ids from a default argument rather than a
    # literal, so this checks the default — rename it and the JS stops finding
    # the element, silently, which is the failure the tile taught us about.
    check("the builder's strip and key keep the ids LIVE_JS looks up",
          'sid: str = "q-strip"' in src and 'lid: str = "q-legend"' in src)
    for el in ("q-now", "q-chips"):
        check(f"the builder emits {el}", f'id="{el}"' in src)
    for el in ("q-strip", "q-legend", "q-now", "q-chips"):
        check(f"...and LIVE_JS looks up {el}", f'"{el}"' in js)
    # One vocabulary, sent over rather than retyped: two spellings of "a motion
    # take" is exactly the drift this page keeps being bitten by.
    check("the strip's words are shipped to the browser, not written twice",
          "QKIND_ONE = {json.dumps(QUEUE_KIND_ONE)}" in src)


def test_the_queue_leads_the_page_and_says_so_once():
    """Roman, 2026-08-14: "shouldnt the queue be at the top?"

    Two things can quietly undo that. The queue can drift back down the page as
    sections are added above it, and the summary strip can regrow a queue cell —
    the same number a few hundred pixels from the section itself, which is the
    duplicated information he keeps asking us to stop printing.
    """
    import build_sim as bs

    src = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")
    body = src[src.index("<body>"):]
    for name, marker in (("the queue", "{live_queue}"),
                         ("the glance strip", "{strip}"),
                         ("what waits on the author", 'id="waiting"'),
                         ("the episode cards", "{eta_section}"),
                         ("the work list", "{production}")):
        check(f"the page body places {name}", marker in body)
    order = [body.index(m) for m in ("{live_queue}", "{strip}", 'id="waiting"',
                                     "{eta_section}", "{production}")]
    check("the queue is the first section on the page, above the glance strip",
          order == sorted(order))
    check("the work list points at the queue rather than repeating it",
          'href="#queue"' in src)


def test_the_status_page_can_actually_find_the_numbers_it_rewrites():
    """The live queue tile is a contract between a builder and a string of JS,
    and nothing but this test holds the two ends together.

    build_sim bakes `id="q-tile-n"`, `id="q-count"` and friends into the HTML;
    LIVE_JS looks those ids up and rewrites them. Rename one — the sort of thing
    a tidy-up does without a second thought — and there is no error anywhere:
    getElementById returns null, the JS quietly does nothing, and the page goes
    back to printing a hand-committed number from hours ago. Which is the exact
    bug this was written to fix, restored in silence.
    """
    import build_sim

    js = build_sim.LIVE_JS
    for el in ("q-tile-n", "q-tile-l", "q-count", "q-notice"):
        check(f"LIVE_JS looks up {el}", f'"{el}"' in js)

    src = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")
    for el in ("q-tile-n", "q-tile-l", "q-count", "q-notice"):
        check(f"the builder emits an element with id {el}",
              f'id="{el}"' in src)

    # It must read the branch telemetry actually publishes to, with the same
    # legacy fallback every other reader carries.
    import telemetry
    check("the tile fetches the box's telemetry branch",
          telemetry.BRANCH in build_sim.BOX_TEL_URL)
    check("and falls back to where the vitals used to live",
          telemetry.LEGACY_BRANCH in build_sim.BOX_TEL_URL_LEGACY)
    check("it reads the file telemetry.py actually publishes",
          build_sim.BOX_TEL_URL.endswith("/" + telemetry.PUBLISH_PATH))
    check("the tile's constants reach the page",
          "BOX_TEL =" in src and "BOX_MEDIAN_FALLBACK =" in src)

    # Ages must be computed against the READER's clock. The committing laptop's
    # clock drifted a full day in August; a stamp taken from the build would have
    # had the page reporting tomorrow's queue as though it were now.
    check("the live queue ages its reading off the fetched file's own stamp",
          "Date.now() / 1000 - q.at" in js)
    # And a dead fetch keeps the baked numbers rather than blanking the tile.
    check("a failed live read says so and keeps the built-in numbers",
          "Live refresh unavailable" in js and "BOX_BAKED" in js)


# ---------------------------------------------------------------------------
# THE STATUS PAGE'S CHARTS (pipeline/charts.py), added 2026-08-13 with them.
#
# Roman asked for charts that make the page easier to understand. A chart is a
# claim made in geometry, and geometry fails silently — a bar drawn from the
# wrong field, or a series that changes colour between two bars, looks exactly
# as convincing as a correct one. These pin the claims the pictures make that a
# reader cannot check by eye, plus the refusals.
# ---------------------------------------------------------------------------

def _fake_progress():
    """Two episodes, one of which has a beat nobody has scored."""
    return [
        {"number": 1, "title": "One", "total_beats": 4, "beats": [
            {"n": 1, "state": "done", "note": "he passed it"},
            {"n": 2, "state": "candidate-awaiting-founder", "note": ""},
            {"n": 3, "state": "fix-known", "note": ""}]},          # beat 4 absent
        {"number": 2, "title": "Two", "total_beats": 2, "beats": [
            {"n": 1, "state": "blocked-decision", "note": ""},
            {"n": 2, "state": "never-rendered", "note": ""}]},
    ]


def test_every_beat_gets_exactly_one_leaf_and_an_unscored_one_shows_as_missing():
    """The canopy's denominator is the episode's beat count, not its file rows.

    THE FAILURE THIS FORBIDS: episode 1 has four beats and three lines in the
    states file. Drawing three leaves would make the picture agree with the
    file and disagree with the show — and it would agree by SHRINKING, so an
    episode nobody had scored would render as a small, tidy, fully-green tree.
    The unscored beat gets a hollow leaf and is counted as unknown.
    """
    import charts

    svg, summary = charts.sapling_svg(_fake_progress(),
                                      {1: "b1.html", 2: "b2.html"})
    check("one leaf per beat of every episode, six in all",
          svg.count('<path class="lf ') == 6)
    ep1 = next(s for s in summary if s["number"] == 1)
    check("the beat with no line in the file is drawn, and drawn as missing",
          ep1["counts"]["unk"] == 1 and "lf-unk" in svg)
    check("...and the episode's own total is what the canopy counts against",
          ep1["total"] == 4 and sum(ep1["counts"].values()) == 4)
    check("the two states the card owns share one shade, as the ETA bar has "
          "always merged them",
          ep1["counts"]["mach"] == 1
          and next(s for s in summary if s["number"] == 2)["counts"]["mach"] == 1)
    check("a leaf links to its own beat on its own episode's board",
          'href="b1.html#beat-01"' in svg and 'href="b2.html#beat-02"' in svg)
    check("...and carries the reason on file where there is one",
          "he passed it" in svg)
    check("no episodes, no tree — never an empty picture of a healthy show",
          charts.sapling_html([], {}) == "" and charts.sapling_svg([], {})[0] == "")

    # THE LABEL CARRIES BOTH OF HIS CLOCKS, ALWAYS. Roman read the old form —
    # "EP 2 · 0/21 passed" — as zero progress on an episode holding eighteen
    # rendered takes, nine of them scored as waiting on his look. "Passed"
    # counts only what HE has passed, so one number could answer only one of
    # his two questions and the label showed the emptier one. Dropping the look
    # clock when it reads zero would put the bug straight back for the episode
    # where the queue is the interesting fact, which is why both lines are
    # asserted on the episode that has neither.
    # Read out of the label ELEMENT, not out of the whole picture: every done
    # beat's tooltip says "passed by you" too, and a substring search over the
    # svg would pass on a tooltip while the label said nothing.
    import re as _re

    epl = _re.findall(r'<text class="epl".*?</text>', svg)
    check("an episode's label carries the queue clock and the passed clock, "
          "queue first",
          len(epl) == 2 and "EP 1 · 1 for your look" in epl[0]
          and "1 passed by you" in epl[0]
          and epl[0].index("for your look") < epl[0].index("passed by you"))
    check("...and both lines are drawn even at zero, so neither clock can hide",
          "EP 2 · 0 for your look" in svg and "0 passed by you" in svg)
    check("...and no episode label still reads as a bare N/M passed",
          "/4 passed<" not in svg and "/2 passed<" not in svg)


def test_the_beat_states_are_grouped_by_whose_clock_they_are_on():
    """The bar and the tree stack green-then-amber, and both read one table.

    This is a legibility fix pinned as a fact. In pipeline order the two dark
    shades (leaf-deep, sap-deep) were adjacent segments, and they are ΔE 11.1
    apart for a normal-vision reader — below where colour alone can carry a
    difference. Grouped by clock they are never neighbours, and the bar reads
    as one green block and one amber block, which is the argument the colour is
    there to make. Reordering STATE_ORDER back would silently undo it.
    """
    import build_sim as bs
    import charts

    order = list(charts.STATE_ORDER)
    check("the machine's two states come first, then the author's two",
          order == ["done", "mach", "look", "gate"])
    check("...so the two dark shades are never neighbours in the bar",
          abs(order.index("mach") - order.index("gate")) > 1)
    check("build_sim's ETA bar reads that order rather than keeping its own",
          "charts.STATE_ORDER" in
          (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8"))

    row = {"total": 6, "counted": 6, "machine_minutes": 60, "thin": False,
           "sample": 5, "conditional_minutes": 0, "conditional_beats": 0,
           "decisions": [], "number": 9, "title": "T", "node": "n",
           "review_url": "", "measured_at": "", "decisions_untagged": 0,
           "ready": 1, "awaiting_founder": 2, "needs_render": 2,
           "per_beat_minutes": 30.0, "rounds": {}, "window": "",
           "states_read_from": "",
           "counts": {"done": 1, "candidate-awaiting-founder": 2,
                      "fix-known": 1, "blocked-decision": 1,
                      "never-rendered": 1}}
    card = bs._eta_card(row, lambda m: f"{m} min")
    check("and the bar it draws puts them in that order too",
          card.index("b-done") < card.index("b-mach") < card.index("b-look")
          < card.index("b-gate"))


def test_a_kind_keeps_its_shade_on_a_day_the_other_kinds_are_missing():
    """Colour follows the series, never its position in one bar.

    THE BUG THIS CAUGHT, before it shipped: the stack numbered its shades by
    index within each bar, so on a day with no still frames the "everything
    else" slab slid from the third step to the second — the same series drawn
    as two different greens in two neighbouring bars. A reader who learns
    "faintest is the tail" has to keep being right about it.
    """
    import charts

    doc = {"kinds": ["ltx", "still", "other"], "measured_at": "2026-08-13",
           "days": [
               # No ties: ltx is the biggest by machine time, still is
               # second, other is the tail — and day one has no still frames
               # at all, which is the case that used to repaint the tail.
               {"date": "2026-08-10", "jobs": 2, "failed": 0, "minutes": 130,
                "partial": False, "by_kind": {"ltx": 100, "other": 30}},
               {"date": "2026-08-11", "jobs": 3, "failed": 0, "minutes": 210,
                "partial": False,
                "by_kind": {"ltx": 100, "still": 80, "other": 30}}]}
    out = charts.work_days_html(doc)
    bars = out.split('<g class="wkbar">')[1:]
    check("the day missing a kind still draws its tail in the tail's shade",
          "w3" in bars[0] and "w2" not in bars[0])
    check("...and the day with every kind draws the same tail the same way",
          "w3" in bars[1] and "w2" in bars[1])
    check("the biggest kind by machine time is the one at the foot",
          bars[1].index("w1") < bars[1].index("w2"))


def test_a_bar_is_as_tall_as_its_minutes_and_a_part_day_says_so():
    """Height is the measured minutes against a whole-hour ceiling.

    And the newest day is nearly always half-finished, so it is labelled rather
    than left to read as the day the farm stopped.
    """
    import re

    import charts

    doc = {"kinds": ["ltx"], "measured_at": "2026-08-13", "days": [
        {"date": "2026-08-10", "jobs": 4, "failed": 0, "minutes": 120,
         "partial": False, "by_kind": {"ltx": 120}},
        {"date": "2026-08-11", "jobs": 2, "failed": 1, "minutes": 60,
         "partial": True, "by_kind": {"ltx": 60}}]}
    out = charts.work_days_html(doc)
    plot = charts.WORK_BASE - charts.WORK_PLOT_TOP
    # Every bar's top comes off its rounded data-end: "...V<top>a<r> <r>...".
    tops = [float(v) for v in re.findall(r"V(\d+\.\d+)a", out)]
    check("a two-hour day against a two-hour ceiling reaches the top gridline",
          len(tops) == 2
          and abs(tops[0] - (charts.WORK_PLOT_TOP + charts.BAR_R)) < 0.01)
    check("the half-day bar is drawn exactly half as tall",
          abs((tops[1] - tops[0]) - plot / 2) < 0.01)
    check("a day still running is labelled, not published as a collapse",
          "so far" in out)
    check("the hours are said in hours, and short days stay in minutes",
          charts._hrs(533) == "8.9 h" and charts._hrs(45) == "45 min"
          and charts._hrs(1200) == "20 h")
    check("no days, no chart — an unread file is never an idle farm",
          charts.work_days_html({}) == ""
          and charts.work_days_html({"days": []}) == "")


def test_the_charts_fetch_nothing_and_claim_nothing_they_cannot_read():
    """No external request, no literal colour, and a table view for every chart.

    The published site's CSP allows no CDN, no font host and no script host, so
    a chart library or a webfont would not fail loudly — it would render a blank
    rectangle on the founder's phone. And every colour comes from a theme custom
    property, which is the only reason the pictures follow a reader's light/dark
    setting at all; one hex literal in here is a colour that does not know which
    theme it is in, and it would break in one mode only.
    """
    import re as _re

    import charts

    src = (REPO / "pipeline" / "charts.py").read_text(encoding="utf-8")
    check("the chart module reaches for nothing off this machine",
          not _re.search(r"https?://", charts.CHART_CSS)
          and "@import" not in charts.CHART_CSS
          and "urllib" not in src and "requests" not in src)
    check("every colour in the chart CSS is a theme token, never a hex literal",
          not _re.search(r"#[0-9a-fA-F]{3,8}\b", charts.CHART_CSS))

    tree = charts.sapling_html(_fake_progress(), {1: "b.html", 2: "c.html"})
    work = charts.work_days_html(
        {"kinds": ["ltx"], "measured_at": "x", "days": [
            {"date": "2026-08-10", "jobs": 1, "failed": 0, "minutes": 30,
             "partial": False, "by_kind": {"ltx": 30}}]})
    for name, out in (("the tree", tree), ("the work chart", work)):
        check(f"{name} carries a table view of the same numbers",
              "<table" in out and "</table>" in out)
        check(f"...and {name} keeps a legend, so identity is never colour alone",
              "-key" in out)
        check(f"...and {name} has an aria-label carrying the whole finding",
              'role="img"' in out and 'aria-label="' in out)
    check("the work chart names the date it was measured",
          "Measured" in work)


def _fake_cut(prev_takes=("b1-old.mp4",), why_lies=False):
    """A two-beat cut manifest: beat 1 has footage, beat 2 is a slate."""
    return {"dir": "ep2-demo-0999", "manifest": "picks-0999.yaml",
            "prev": "ep2-demo-0998", "prev_takes": set(prev_takes),
            "said_footage": 1, "said_slates": 1,
            "beats": [
                {"n": 1, "slug": "COLD OPEN", "take": "b1-new.mp4",
                 "why": "carry-forward" if why_lies else "new"},
                {"n": 2, "slug": "THE SPRINT", "take": "", "why": "slate"}]}


def test_the_episode_now_strip_counts_the_cut_and_never_its_own_source():
    """Every number on the strip is a join of two files, computed at build.

    Roman, 2026-08-19: *"hows the progress with episode 2? ... its not projected
    very well."* The strip that answers him is one line per fact, and the whole
    design constraint is that no fact is typed into build_sim.py: five ep2 demo
    cuts were assembled in five days, so a hand-written "17 of 21" is correct
    until the next assembly and wrong for as long as nobody notices.

    THE FOUR THINGS PINNED HERE, each of which was a real defect or a near one:

    1. THE COUNTS FOLLOW THE FILES. Change the fixture, the sentence changes.
    2. `why: new` IS NOT TRUSTED FOR WHAT IS NEW. picks-0819.yaml defines `new`
       as "not in the 2026-08-18 cut" and also copies every unre-read row from
       picks-0818 verbatim — so beats 01 and 14 carried `new` from the cut before
       the one they were new in, and the first draft of this strip published "4
       of them new" about a cut whose own header says two clips were swapped.
       Newness is a diff of take FILENAMES against the previous manifest, which
       cannot be stale in that way.
    3. A SLATE THAT HOLDS A PASSING TAKE IS ITS OWN FACT. It is the one thing
       neither file knows alone: the tree says beat 07 is amber, the manifest
       says beat 07 is a hole, and the join says the two are the same beat and
       the gap between them is a SWAP, not a render.
    4. IT FAILS TO NOTHING. It sits under a heading about progress, so a strip
       drawn off a failed read would read as an episode with no footage.
    """
    import re as _re

    import build_sim as bs

    # Beat 2 is the SLATE in the fixture cut and is deliberately `fix-known`
    # here, so the swap line below has a negative case to be silent in.
    prog = [{"number": 2, "title": "Two", "total_beats": 3, "beats": [
        {"n": 1, "state": "candidate-awaiting-founder", "note": ""},
        {"n": 2, "state": "fix-known", "note": ""},
        {"n": 3, "state": "blocked-decision", "note": ""}]}]
    out = bs.ep2_now_html(_fake_cut(), prog)
    check("the footage count is the manifest's rows, over the episode's beats",
          "<b>1 of 3 beats</b>" in out)
    check("the slate is named, not just counted",
          "<b>1 still a slate</b>" in out and "02 THE SPRINT" in out)
    check("the takes-waiting count is the measured states, not the cut",
          "<b>1 beat holds a take waiting for your look</b>" in out)
    check("...and it agrees with itself in the plural too",
          "<b>2 beats hold takes waiting for your look</b>" in bs.ep2_now_html(
              _fake_cut(), [{**prog[0], "beats": [
                  {"n": 1, "state": "candidate-awaiting-founder", "note": ""},
                  {"n": 2, "state": "candidate-awaiting-founder", "note": ""}]}]))
    check("a call only he can make is counted apart from a take he can look at",
          "waiting on a call only you can make</b> (03)" in out)
    check("nothing is claimed passed until a beat says done",
          "<b>0 beats passed.</b>" in out)
    check("the newest cut is a link the reader can open",
          'href="review/ep2-demo-0999"' in out)

    # (1) the numbers move with the file, which is the whole claim
    two = bs.ep2_now_html(_fake_cut(), [{**prog[0], "total_beats": 9}])
    check("changing the episode's beat count changes the printed denominator",
          "<b>1 of 9 beats</b>" in two)

    # (2) newness is measured, and a lying label cannot move it
    check("a take absent from the previous manifest reads as new",
          "not in ep2-demo-0998" in out and "01 COLD OPEN" in out)
    check("...and it still reads as new when the row's own `why` says otherwise",
          "not in ep2-demo-0998" in bs.ep2_now_html(
              _fake_cut(why_lies=True), prog))
    check("...and a take the previous cut already had is not called new",
          "not in ep2-demo-0998" not in bs.ep2_now_html(
              _fake_cut(prev_takes=("b1-new.mp4",)), prog))
    check("a first-ever cut claims nothing about a predecessor it has none of",
          "the cut before it" not in bs.ep2_now_html(
              {**_fake_cut(), "prev": "", "prev_takes": set()}, prog))

    # (3) the join's own finding
    swap = bs.ep2_now_html(_fake_cut(), [{**prog[0], "beats": [
        {"n": 1, "state": "fix-known", "note": ""},
        {"n": 2, "state": "candidate-awaiting-founder", "note": ""}]}])
    check("a slate holding a passing take is called a swap, not a render",
          "is a slate in that cut" in swap and "not a render" in swap)
    check("...and a slate with no passing take makes no such claim",
          "is a slate in that cut" not in out)

    # (4) fails to nothing, both ways round
    check("no cut manifest, no strip", bs.ep2_now_html({}, prog) == "")
    check("no measured states, no strip", bs.ep2_now_html(_fake_cut(), []) == "")
    check("an episode absent from the states file draws nothing",
          bs.ep2_now_html(_fake_cut(), [{"number": 7, "beats": [
              {"n": 1, "state": "done", "note": ""}]}]) == "")

    # The manifest's own totals are a cross-check and never the source, and a
    # disagreement is printed rather than resolved silently in our favour.
    lying = {**_fake_cut(), "said_footage": 19}
    check("a manifest that disagrees with its own rows says so on the page",
          "manifest disagrees with itself" in bs.ep2_now_html(lying, prog)
          and "states 19 footage beats and lists 1" in bs.ep2_now_html(lying, prog))
    check("...and stays quiet when the header and the rows agree",
          "disagrees with itself" not in out)

    # Same three guarantees every chart on this page carries.
    check("the strip carries a table view of the same join",
          "<table" in out and "In the newest cut" in out)
    check("...and an aria-label a screen reader gets the finding from",
          'aria-label="Episode 2 right now' in out)
    # Whichever CSS block holds it — the strip's rules live beside the ETA
    # card's, and which constant that is has moved once already.
    css = next((c for c in (bs.STRIP_CSS, bs.SIM_CSS) if ".ep2now" in c), "")
    check("the strip's CSS is actually shipped in the page's style tag",
          bool(css) and ".fk.f-unk" in css)
    check("...and its colours are theme tokens, never hex literals",
          not _re.search(r"#[0-9a-fA-F]{3,8}\b",
                         css[css.index(".ep2now"):css.index(".fk.f-unk")]))
    check("...and it uses the palette charts.py defines, not a private one",
          all(("var(--%s)" % t) in css for t in
              ("leaf", "leaf-deep", "sap", "sap-deep")))
    check("...and it reads the same states file the tree and the cards do",
          "episode-progress.yaml" in out)


def test_the_latest_cut_manifest_is_found_by_name_and_shape_checked():
    """Newest by DIRECTORY NAME, and nothing trusted about what is inside it.

    Mtime would pick a cut at random on the machine that builds the site: a
    deploy checkout's mtimes are all "whenever git wrote them", in whatever
    order the clone happened to walk. The names are `ep2-demo-MMDD` and sorting
    them is the only ordering that survives a fresh clone.
    """
    import pathlib as _pl
    import shutil as _sh
    import tempfile as _tf

    import build_sim as bs

    root = _tf.mkdtemp()
    rev = _pl.Path(root) / "review"
    def write(name, body):
        d = rev / name / "sources"
        d.mkdir(parents=True, exist_ok=True)
        (d / ("picks-%s.yaml" % name.rsplit("-", 1)[-1])).write_text(
            body, encoding="utf-8")

    write("ep2-demo-0801", "beats:\n- beat: 1\n  slug: A\n  take: old.mp4\n"
                           "  why: new\n")
    write("ep2-demo-0902", "beats:\n- beat: 1\n  slug: A\n  take: new.mp4\n"
                           "  why: new\n- beat: 2\n  take: null\n  why: slate\n")
    # Touched LAST and named FIRST — mtime order and name order disagree.
    (rev / "ep2-demo-0801" / "sources" / "picks-0801.yaml").touch()

    cut = bs.read_latest_cut(repo=_pl.Path(root))
    check("the newest cut is the highest-numbered name, not the newest file",
          cut.get("dir") == "ep2-demo-0902")
    check("...and the one before it is the previous name",
          cut.get("prev") == "ep2-demo-0801"
          and cut.get("prev_takes") == {"old.mp4"})
    check("a null take is carried as a slate rather than dropped",
          [b["take"] for b in cut["beats"]] == ["new.mp4", ""])

    write("ep2-demo-0903", "beats: not a list\n")
    check("a manifest of the wrong shape is skipped, not half-read",
          bs.read_latest_cut(repo=_pl.Path(root)).get("dir") == "ep2-demo-0902")
    write("ep2-demo-0904", "beats:\n- beat: not a number\n  take: x.mp4\n")
    check("a row with no readable beat number is dropped, and an empty "
          "manifest falls through to the last good one",
          bs.read_latest_cut(repo=_pl.Path(root)).get("dir") == "ep2-demo-0902")
    check("no review directory at all is {} and never a half-built dict",
          bs.read_latest_cut(repo=_pl.Path(_tf.mkdtemp())) == {})
    _sh.rmtree(root, ignore_errors=True)


def test_the_queue_depth_line_refuses_to_cross_a_gap_it_did_not_measure():
    """The sparkline's four refusals, each pinned because each is invisible.

    A chart is a claim in geometry and geometry fails quietly. These four are
    the ways this one could lie while still looking like a chart:

      1. CROSSING A GAP. A failed reading is never written to depth_series —
         no point at all, rather than a zero — because a zero recorded while
         the queue directory was unreadable draws a clean dip to empty across
         an outage: a picture of an idle box on a night it was full. The series
         is therefore cut into runs and each is its own path.
      2. SLOPING BETWEEN SAMPLES. A reading is the depth until the next one
         replaces it. Sloping would draw jobs arriving one at a time when eight
         landed at once, so the path steps (H then V) and never diagonals.
      3. DRAWING AN ABSENCE. The field is optional — an old publish, a box with
         no history, a missing queue block — and a flat line at zero is a
         claim. Absent means words.
      4. IMPLYING "NOW". The box publishes every five minutes and raw's CDN
         holds each copy for five more, so the newest point can be ten minutes
         old. Age comes off the point's own epoch against the READER's clock,
         never off the build stamp.
    """
    import build_sim as bs

    js = bs.LIVE_JS
    check("a break is declared at more than two and a half publish intervals",
          "DEPTH_GAP = 750" in js and "DEPTH_GAP" in js)
    check("...and the series is cut into runs on it, not drawn as one line",
          "depthRuns" in js and "runs.push(cur)" in js)
    check("the line steps and never slopes between two readings",
          '"H" + x.toFixed(1) + "V" + y.toFixed(1)' in js)
    check("a missing series is words, never an empty chart",
          "not publishing queue history yet" in js)
    check("...and so is a series too short to have a shape",
          "DEPTH_MIN_POINTS = 4" in js
          and "make a shape worth drawing" in js)
    check("a queue that was empty at every reading is not called 'never more "
          "than one'",
          "empty every time it looked" in js)
    check("the newest reading is aged against the reader's own clock",
          "Date.now() / 1000 - lastP[0]" in js)
    check("...and the page says how far behind the box that can be",
          "ten minutes behind the box" in js)
    check("the chart is built with createElementNS, never innerHTML",
          "createElementNS" in js)
    check("a stretched sparkline keeps an even stroke",
          "non-scaling-stroke" in bs.SIM_CSS)
    check("the drawn line carries an aria-label of the same sentence",
          'svg.setAttribute("aria-label", note.textContent)' in js)

    src = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")
    for el in ("q-spark", "q-spark-note"):
        check(f"the builder emits {el}", f'id="{el}"' in src)
        check(f"...and LIVE_JS looks up {el}", f'"{el}"' in js)
    check("the baked copy says the history is not built into the page",
          "not built into this page" in src)
    # It must run BEFORE the count checks throw, or a box publishing vitals
    # with no queue block would leave the chart showing the no-JS sentence
    # forever instead of its own honest one.
    check("the depth chart is drawn before the tile's count checks can throw",
          js.index("drawDepth(q);") < js.index("carries no counts"))


# ---------------------------------------------------------------------------
# A RENDER HE WAS NEVER SHOWN IS A RENDER THAT DID NOT HAPPEN.
#
# Four times in three days he reported work as undone that had in fact
# rendered — the guard sheets, the sapling-reveal frames, beat 02's rerun,
# beat 12's plate. box_enqueue already refuses a job with no `consumer:`;
# nothing ever checked the promise was kept. pipeline/unpaged.py is that check
# and these are its edges. Pure logic: no git, no disk, no clock.

from datetime import datetime, timezone


def _sidecar(jid, present=(), steps=(), finished="2026-08-14T09:00:00Z", rc=0):
    return {"id": jid, "rc": rc, "finished_at": finished,
            "artifacts_present": list(present),
            "steps": [{"argv": list(a)} for a in steps]}


def test_a_render_that_reached_a_page_is_not_an_unpaged_render():
    import unpaged
    now = datetime(2026, 8, 14, 21, 0, tzinfo=timezone.utc)
    job = _sidecar("ep2-guard-sheet-a-0814-1786707392",
                   present=[r"C:\out\06-the-clipboard-s0.png"])
    page = unpaged.tokens_of(
        '<h2 id="e-guards">Guards</h2>'
        '<img src="/review/ep2-picks/06-the-clipboard-s0.png">')
    r = unpaged.audit([job], {"ep2-guard-sheet-a-0814": "Roman picks one"},
                      page, now)
    check("a frame the review page links is paged, not flagged",
          not r["unpaged"] and len(r["paged"]) == 1)
    check("and it records HOW it was found, so the claim is checkable",
          r["paged"][0]["shown_as"] == "file 06-the-clipboard-s0.png")

    # The real-world case: a contact sheet BAKES the frames, so no filename
    # survives onto the page and the only thread back is the publish directory.
    baked = _sidecar("ep2-b02-idfix-0812-1786500000",
                     present=[r"C:\out\02-s0.png"],
                     steps=[["python", "-c",
                             'dst = "C:/banyan-farm/courier-box/farm-out/ep2-b02-idfix"']])
    sheet = unpaged.tokens_of('<img src="/review/sheets/wave2-b02.jpg">'
                              "<p>round ep2-b02-idfix, four seeds</p>")
    r = unpaged.audit([baked], {"ep2-b02-idfix-0812": "Roman's next look"},
                      sheet, now)
    check("a sheet that names the round credits the round it baked",
          not r["unpaged"] and r["paged"][0]["shown_as"] == "publish ep2-b02-idfix")


def test_a_render_no_page_names_is_the_number_this_exists_to_report():
    import unpaged
    now = datetime(2026, 8, 14, 21, 0, tzinfo=timezone.utc)
    job = _sidecar("ep1-b05-sapling-reveal-0811-1786400000",
                   present=[r"C:\out\05-reveal-s0.png"],
                   finished="2026-08-11T15:55:00Z")
    r = unpaged.audit([job], {"ep1-b05-sapling-reveal-0811": "Roman's next look"},
                      unpaged.tokens_of("<p>nothing to do with it</p>"), now)
    check("frames on disk that no page names are flagged",
          [x["task"] for x in r["unpaged"]] == ["ep1-b05-sapling-reveal-0811"])
    check("and the age is what makes it a complaint rather than a note",
          round(r["unpaged"][0]["age_hours"]) == 77)

    # THE NEAR MISS THAT MATTERS. Round names are hyphenated and one is
    # routinely a prefix of the next; substring matching would credit the round
    # he DID see for the one he did not.
    occl = _sidecar("ep2-b02-goblin-occl-0811-1786440000",
                    present=[r"C:\out\02-s0.png"],
                    steps=[["python", "-c",
                            'dst="C:/x/courier-box/farm-out/ep2-b02-goblin-occl"']])
    bright = unpaged.tokens_of("<p>see ep2-b02-goblin-occlbright</p>")
    r = unpaged.audit([occl], {"ep2-b02-goblin-occl-0811": "Roman's next look"},
                      bright, now)
    check("a longer round name does not page the shorter one inside it",
          len(r["unpaged"]) == 1)


def test_a_render_that_produced_nothing_is_a_failed_render_not_an_unpaged_one():
    import unpaged
    now = datetime(2026, 8, 14, 21, 0, tzinfo=timezone.utc)
    empty = unpaged.tokens_of("")
    consumers = {"ep2-b09-wave-0814": "Roman's next look"}

    died = _sidecar("ep2-b09-wave-0814-1786700000", present=[], rc=92)
    r = unpaged.audit([died], consumers, empty, now)
    check("a job whose artifacts never appeared is not counted here",
          not r["unpaged"] and not r["paged"])

    # Same discipline one step further in: a job that made only its provenance
    # sidecars made nothing anybody can look at.
    yaml_only = _sidecar("ep2-b09-wave-0814-1786700001",
                         present=[r"C:\out\09-s0.yaml", r"C:\out\bench.jsonl"])
    check("yaml and jsonl are records, not something to show him",
          not unpaged.audit([yaml_only], consumers, empty, now)["unpaged"])

    # And one that is still going: no finished_at at all.
    running = {"id": "ep2-b09-wave-0814-1786700002", "steps": [],
               "artifacts_present": [r"C:\out\09-s0.png"]}
    check("a job still running is not yet a broken promise",
          not unpaged.audit([running], consumers, empty, now)["unpaged"])


def test_the_count_is_promises_to_him_and_not_every_render_on_the_farm():
    import unpaged
    now = datetime(2026, 8, 14, 21, 0, tzinfo=timezone.utc)
    empty = unpaged.tokens_of("")
    art = [r"C:\out\x-s0.png"]

    rows = unpaged.audit(
        [_sidecar("a-0814-1786400000", present=art),
         _sidecar("b-0814-1786400000", present=art),
         _sidecar("c-0814-1786400000", present=art)],
        {"a-0814": "Roman picks one of the four",
         "b-0814": "the v35 screening cut, which cannot take a stretched ingredient"},
        empty, now)
    check("a job whose consumer names him is the promise being audited",
          [x["task"] for x in rows["unpaged"]] == ["a-0814"])
    check("a job feeding another artifact is an ingredient, not his backlog",
          [x["task"] for x in rows["ingredient"]] == ["b-0814"])
    check("a job whose spec is gone is reported apart — no promise to read",
          [x["task"] for x in rows["no_spec"]] == ["c-0814"])

    # `R4` means "his call, eventually" in a consumer sentence, not "his screen
    # now". Reading it as him put eleven v34 plate twins in the count.
    twin = _sidecar("ep1-b03-v34-plate-twin-r3-1786300000", present=art)
    r = unpaged.audit([twin],
                      {"ep1-b03-v34-plate-twin-r3":
                       "the v35 screening cut. Which ROUND the cut uses is R4's open call"},
                      empty, now)
    check("R4 in a consumer is the taste rule, not a promise of a look",
          not r["unpaged"] and len(r["ingredient"]) == 1)

    # In flight: finished minutes ago, still the firing lane's to page.
    fresh = _sidecar("d-0814-1786400000", present=art,
                     finished="2026-08-14T20:30:00Z")
    r = unpaged.audit([fresh], {"d-0814": "Roman picks one"}, empty, now)
    check("a wave that landed half an hour ago is in flight, not a failure",
          not r["unpaged"] and len(r["in_flight"]) == 1)


def test_one_round_asked_twice_is_one_unshown_picture():
    import unpaged
    now = datetime(2026, 8, 14, 21, 0, tzinfo=timezone.utc)
    runs = [_sidecar("ep2-b05-x-0814-1786400000", present=[r"C:\out\a.png"],
                     finished="2026-08-14T09:00:00Z"),
            _sidecar("ep2-b05-x-0814-1786410000", present=[r"C:\out\b.png"],
                     finished="2026-08-14T12:00:00Z")]
    r = unpaged.audit(runs, {"ep2-b05-x-0814": "Roman picks one"},
                      unpaged.tokens_of(""), now)
    check("two runs of one round are one row, not two",
          len(r["unpaged"]) == 1 and r["unpaged"][0]["runs"] == 2)
    check("and the age is the NEWEST run's — the round is that fresh",
          r["unpaged"][0]["age_hours"] == 9.0)
    check("a page naming EITHER run has shown this round's pictures",
          not unpaged.audit(runs, {"ep2-b05-x-0814": "Roman picks one"},
                            unpaged.tokens_of("<img src='a.png'>"), now)["unpaged"])


def test_a_tree_that_cannot_see_the_farm_branch_says_so_instead_of_zero():
    import unpaged
    # CI and the deploy box clone main alone. A green "0 unpaged" there would be
    # a claim made out of an absent branch, and this warning runs in build_site.
    check("no sidecars anywhere is not the same as nothing unpaged",
          unpaged.warn_line({"measurable": False, "unpaged": []}) == "")
    check("nothing unpaged is silence too — a build log is not a scoreboard",
          unpaged.warn_line({"measurable": True, "unpaged": []}) == "")
    line = unpaged.warn_line({"measurable": True, "unpaged": [
        {"task": "ep2-guard-sheet-a-r2-0814", "age_hours": 4.6, "artifacts": 4}]})
    check("and one unpaged render names itself in the build log",
          "ep2-guard-sheet-a-r2-0814" in line and "1 finished render " in line)


def test_the_queue_page_prints_the_prompt_that_made_the_frame():
    """The founder, 2026-08-14: "i cant keep blindly saying these videos are low
    quality... we need to see a history of the queue, what has been generated,
    what image reference did it use, what was the prompt".

    His second verdict, the same day, is why the page is now a gallery: *"looks
    like you were pretty lazy with the queue history.. i expected you to be able
    to scroll, see images and prompts and these details all with a nice
    interface, more visuals."*

    So the load-bearing claim of /queue is that THE PROMPT IS SHIPPED IN FULL —
    not a link out to it, not a truncation with an ellipsis as the only copy,
    not a summary. What changed with the gallery is WHERE: the baked HTML holds
    the grid, a thumbnail and one prompt line per card, and the untruncated
    prompts, negatives and recipes ride in `queue-data.json` and
    `queue-detail.json`, which the page fetches. That is the whole reason the
    page went from 2.8 MB to a fifth of it. This test therefore checks each fact
    on the surface that actually carries it, because "in the page's own bytes"
    was a claim about the old fold layout and not about the founder's ask.
    """
    import build_queue as bq

    hist = {
        "_meta": {"measured_at": "2026-08-14T16:56:46Z",
                  "source_commit": "33f0f42eccc6f89732e3c1c1a2a7a4cf0933b178"},
        "jobs": [{
            "id": "ep2-b18-figlit-0814-1786724010",
            "beat": 18, "node": "002b-first-citizen", "kind": "still-ipa",
            "rc": 0, "failed_step": None, "attempts": 1,
            "started_at": "2026-08-14T16:22:05Z",
            "finished_at": "2026-08-14T16:24:58Z", "duration_s": 173,
            "prompt": "a fig lit from the side so its purple skin reads",
            "negative": "backlit silhouette, black shape against bright sky",
            "prompt_source": "artifact sidecar",
            "init": {"path": "farm-out/ep2-b18/init.png"},
            "outputs": [{"path": "farm-out/ep2-b18/18-the-decision-r0.png",
                         "name": "18-the-decision-r0.png",
                         "bytes": 1233830, "kind": "image"},
                        {"path": "farm-out/ep2-b18/18-the-decision-r0.mp4",
                         "name": "18-the-decision-r0.mp4",
                         "bytes": 2200000, "kind": "video"}],
            "recipe": {"model": "flux", "steps": 28},
        }],
        "upcoming": [],
    }
    out = bq.render(hist)

    # THE GRID IS THE PAGE, and it is in the baked bytes — so the gallery is
    # there with JavaScript off and is greppable in the built file.
    check("the render is a card you can see, not a row you must open",
          '<button type="button" class="qc' in out and "beat 18" in out)
    check("the card carries a readable line of the prompt",
          "a fig lit from the side so its purple skin reads" in out)

    # Media is REFERENCED, never copied: the frames live on the courier branch
    # and the page must point at exactly that branch on the raw CDN. The card
    # asks the thumb branch first and keeps the original as the fallback, so a
    # frame the thumbnailer missed costs one slow card and never a hole.
    check("the card's picture comes from the thumb branch",
          f'src="{bq.thumb_url("farm-out/ep2-b18/18-the-decision-r0.png")}"' in out)
    check("with the full-size original on the same card as the fallback",
          f'{bq.RESULTS_BASE}/farm-out/ep2-b18/18-the-decision-r0.png' in out)
    check("the media base is the raw CDN, not a path inside _site",
          "raw.githubusercontent.com" in bq.RESULTS_BASE
          and "raw.githubusercontent.com" in bq.THUMB_BASE
          and bq.RESULTS_BASE in out)

    # THE FULL TEXT IS SHIPPED, in the payloads the page fetches. Untruncated:
    # the card's line may be cut on a word boundary, the payload's never is.
    idx = bq.index_payload(hist)
    det = bq.detail_payload(hist)["jobs"]["ep2-b18-figlit-0814-1786724010"]
    check("the index ships the positive prompt whole, for the search box",
          idx["jobs"][0]["prompt"] == "a fig lit from the side so its purple skin reads")
    check("the opened record ships the negative too — the half he cannot see otherwise",
          det["negative"] == "backlit silhouette, black shape against bright sky")
    check("they are separate fields, so neither can be mistaken for the other",
          det["prompt"] != det["negative"])
    check("and the page labels both where it prints them",
          "Positive prompt" in bq.LIVE_JS and "Negative prompt" in bq.LIVE_JS)
    check("the init frame travels with the record, on the box's own branch",
          det["init"]["path"] == "farm-out/ep2-b18/init.png"
          and bq.art_url(det["init"]["path"]).startswith(bq.RESULTS_BASE))
    check("and so does every output it made",
          [a["path"] for a in det["outputs"]]
          == ["farm-out/ep2-b18/18-the-decision-r0.png",
              "farm-out/ep2-b18/18-the-decision-r0.mp4"])
    check("a long prompt is cut only on the card, never in the payload",
          bq.snippet("x " * 200).endswith("…") and len(bq.snippet("x " * 200)) <= 90)

    # A page holding 1,700 artifacts must cost nothing until it is scrolled to.
    check("images are lazy", 'loading="lazy"' in out)
    # A job that produced only a clip gets a <video> card, and that one must not
    # pull the file down to show a poster frame.
    clip_only = {"id": "v1", "beat": 4, "kind": "motion", "rc": 0,
                 "finished_at": "2026-08-14T16:24:58Z", "duration_s": 173,
                 "outputs": [{"path": "farm-out/v/04.mp4", "name": "04.mp4",
                              "kind": "video"}]}
    check("video downloads nothing until asked", 'preload="none"' in bq.card_html(clip_only, 0))
    # The line he scans on the grid: which beat, what kind, when, how many files.
    check("the card's own line carries beat, kind, clock and file count",
          "beat 18" in out and "2 files" in out)


def test_a_prompt_nobody_recorded_says_so_instead_of_looking_empty():
    """The dangerous failure of this page is not a missing prompt — it is a
    missing prompt that renders as an empty box, because an empty box reads as
    "the render had no negative prompt" and that is a different, false fact.

    A prompt the generator could not recover is named, with the reason it gave.
    Never reconstructed: the 77-token fit happened on the box's tokenizer and a
    recomputation can differ exactly where it would matter.
    """
    import build_queue as bq

    lost = {"id": "old-job-1", "beat": 3, "kind": "motion", "rc": 0,
            "finished_at": "2026-08-01T09:00:00Z", "duration_s": 400,
            "prompt": None, "negative": None,
            "prompt_source": "no artifact sidecar was written for this run",
            "outputs": [{"path": "farm-out/old/03.mp4", "name": "03.mp4",
                         "kind": "video"}]}
    out = bq.render({"_meta": {}, "jobs": [lost], "upcoming": []})
    check("an unrecoverable prompt prints the honest marker",
          bq.NO_PROMPT in out)
    check("and the card is marked as a gap, not left looking blank",
          'class="p gap"' in out)
    check("nothing was invented in its place",
          "a slow push" not in out and "prompt: </p><p></p>" not in out)

    # The gap and its reason travel in the index row, so the grid can print the
    # honest marker on first paint without a second fetch and without inventing
    # a cause. A row carrying `prompt` and a row carrying `prompt_gap` are the
    # two different facts, and no row may carry both.
    row = bq.index_row(lost)
    check("the row states the gap rather than shipping an empty prompt",
          row["prompt_gap"] == "no artifact sidecar was written for this run"
          and "prompt" not in row)
    check("and the opened record does not invent a prompt either",
          "prompt" not in bq.detail_row(lost))
    check("a gap with no recorded cause still refuses to imply one",
          bq.index_row(dict(lost, prompt_source=None))["prompt_gap"]
          == "no reason recorded")

    # The opposite case must stay distinguishable: a run that really carried a
    # positive and really carried no negative is a different fact from a run
    # that recorded neither, and the record is what the page reads to tell them
    # apart. (Careful if you ever assert these markers by substring: NO_NEGATIVE
    # ENDS WITH NO_PROMPT — "NEGATIVE PROMPT NOT RECORDED" contains "PROMPT NOT
    # RECORDED" — so a bare `NO_PROMPT in x` is true whenever the negative
    # marker is present. Asserting on the record's keys cannot make that mistake.)
    half = dict(lost, prompt="a slow push in on the sprout",
                prompt_source="artifact sidecar")
    hrow, hdet = bq.index_row(half), bq.detail_row(half)
    check("a recovered positive is shipped whole and opens no gap",
          hrow["prompt"] == "a slow push in on the sprout" and "prompt_gap" not in hrow)
    check("and the missing half is missing, not empty",
          hdet["prompt"] == "a slow push in on the sprout" and "negative" not in hdet)
    check("the marker for that missing half is its own words",
          bq.NO_NEGATIVE.startswith("NEGATIVE") and bq.NO_NEGATIVE != bq.NO_PROMPT)
    # The opened record is drawn in the browser, so the markers must reach it as
    # constants rather than as strings retyped in the JS — two copies of a
    # promise are one copy away from disagreeing.
    check("the record view prints the markers from the module's own constants",
          "NO_PROMPT" in bq.LIVE_JS and "NO_NEGATIVE" in bq.LIVE_JS)

    # A history file that cannot be read at all must degrade to a sentence, not
    # to a fabricated empty page and not to a build crash — several lanes share
    # this tree and one of them can be mid-write.
    empty = bq.render(None)
    check("an unreadable history says so rather than showing an empty queue",
          "queue-history.json" in empty and "queue_history.py" in empty)


def test_the_queue_gallery_can_be_narrowed_to_one_beat_and_opened_full_size():
    """The founder's ask has a second half the first gallery did not answer:
    *"scroll, see images and prompts and these details all with a nice
    interface"* — and he reviews on a phone. Two things that needs and did not
    have:

    ONE BEAT AT A TIME. He does not browse 573 renders, he asks "what has beat 13
    ever looked like". Typing `b13` into the search box worked by accident; a
    control that says so did not exist. It is a <select> and not a row of 21
    chips because 21 chips is four rows of a sticky bar on a phone, which is the
    whole screen.

    FULL SIZE WITHOUT LEAVING. Every picture on this page is a 512 px preview or
    a fitted copy, so "is that a fig or a smear" could only be settled by
    following a link to raw.githubusercontent.com — a cold page load away from
    the gallery that loses the scroll position and the filters, and on a phone a
    one-way trip.
    """
    import build_queue as bq

    def job(i, beat, kind="still"):
        return {"id": "j%d" % i, "beat": beat, "kind": kind, "rc": 0,
                "finished_at": "2026-08-14T16:24:58Z", "duration_s": 10,
                "prompt": "p", "prompt_source": "artifact sidecar",
                "outputs": [{"path": "farm-out/d%d/f.png" % i, "kind": "image"}]}

    hist = {"_meta": {}, "upcoming": [],
            "jobs": [job(1, 13), job(2, 13), job(3, 4), job(4, None)]}
    out = bq.render(hist)

    # The beat control is built from the beats that are actually there, and
    # carries the count, so choosing is informed before it is chosen.
    check("the bar offers a beat filter", 'id="q-beat"' in out)
    check("built from the beats present, not a hardcoded 1..21",
          'value="13">beat 13 — 2 renders' in out
          and 'value="4">beat 04 — 1 render<' in out)
    check("and it counts the beats it is offering", "all 2 beats" in out)
    # A run whose beat nobody recorded is its own answer, not beat 0 and not
    # hidden: it gets an option, so it stays reachable.
    check("a run with no recorded beat is selectable rather than lost",
          'value="none">no beat recorded — 1 render' in out)
    check("the filter reads the beat off the card the page already stamped",
          'data-b="13"' in out and 'data-b=""' in out)
    check("and the script knows that option by the same name",
          'state.beat === "none"' in bq.LIVE_JS
          and "state.beat" in bq.LIVE_JS)
    # The count line must call itself filtered when only the beat is set, or a
    # narrowed grid reads as the whole history.
    check("a beat-only filter still reports itself as a filter",
          'state.beat !== ""' in bq.LIVE_JS)

    # The lens: full-resolution bytes over the record, never a navigation away.
    check("the page ships a lens", 'id="q-lens"' in out and 'class="qlens"' in out)
    check("it is closed until asked for", '<div class="qlens" id="q-lens" hidden>' in out)
    check("the output, the init frame and the reference all open in it",
          bq.LIVE_JS.count("zoomable(") >= 4)
    check("the lens shows the full-size file, not the 512 px preview",
          "var url = artUrl(path);" in bq.LIVE_JS)
    # Ten beats ship a clip called 13-remake-LTX-0813.mp4 and thirteen carry an
    # init called b13-init-704x1280.png, so a caption naming the file names
    # nothing. The directory is the identifier.
    check("and captions the whole path, because the filename is not an identifier",
          "lensCap.textContent = path;" in bq.LIVE_JS)
    check("escape closes the lens before the record underneath it",
          "if (lens && !lens.hidden)" in bq.LIVE_JS)
    check("the raw file is still one tap away for anyone who wants the bytes",
          'id="q-lens-raw"' in out)

    # THE GALLERY MUST NOT BE BURIED. Measured at 390 px before this changed: the
    # 54 unrun job cards ran 34,500 px and put the first finished render 43
    # screens down, on the page he opens to look at renders. Folded on a narrow
    # viewport it is 2.7 screens. Both sections still exist and both are still
    # reachable — he asked for the coming work too.
    up = bq.render({"_meta": {}, "jobs": [job(1, 13)],
                    "upcoming": [{"id": "u1", "beat": 3, "kind": "still",
                                  "state": "held", "hold_reason": "needs a call"},
                                 {"id": "u2", "beat": 4, "kind": "still",
                                  "state": "authored"}]})
    check("the unrun list is foldable", 'class="qupwrap"' in up and "<summary>" in up)
    check("and ships OPEN, so a reader with no JavaScript is shown everything",
          '<details class="qupwrap" id="q-up" open>' in up)
    check("the script folds it only where the screen cannot afford it",
          "window.innerWidth < 760" in bq.LIVE_JS)
    check("the summary states the count while folded, so nothing is concealed",
          "2 jobs authored and not yet run" in up
          and "1 held on you, 1 runnable" in up)
    check("every upcoming card is still in the page, not dropped",
          up.count('class="qup ') == 2)
    check("and following the jump link opens it rather than landing on a fold",
          "openUpcoming" in bq.LIVE_JS and 'href="#upcoming"' in up)
    check("the jump bar reaches the gallery, the coming work and the live block",
          'class="qjump"' in up and 'href="#finished"' in up and 'href="#now"' in up)


def test_the_queue_never_claims_to_have_checked_the_results_branch():
    """The marker on a picture-less tile used to read "NO ARTIFACT ON THE
    BRANCH", and the page's own explainer expanded that to "the run reported an
    outcome and the branch carries no file under its name".

    THE BUILDER NEVER READS THE BRANCH. It reads one thing, the `outputs` list
    in queue-history.json. Measured 2026-08-15: all 222 tiles carrying the
    marker also carry no `artifacts_dir`, and at least 25 of them have frames
    sitting on farm-results-rtx5090 in a directory named after the job — the
    history file simply never linked them. So the old marker stated, on 25
    tiles, a fact that was false, and blamed the render for a gap in the
    generator.

    The fix is the wording, not a guessed path: a tile that showed a frame this
    page INFERRED rather than read would put every other frame on the page in
    doubt, which is a worse page than one with 222 honest holes in it.
    """
    import build_queue as bq

    check("the marker claims the record, which is what the builder read",
          "RECORD" in bq.NO_ARTIFACT.upper())
    check("and no longer claims a branch it never opened",
          "BRANCH" not in bq.NO_ARTIFACT.upper())

    blank = {"id": "b1", "beat": 7, "kind": "motion", "rc": 0,
             "finished_at": "2026-08-14T16:24:58Z", "duration_s": 10,
             "prompt": "p", "prompt_source": "artifact sidecar", "outputs": []}
    out = bq.render({"_meta": {}, "upcoming": [], "jobs": [blank]})
    check("a run with no recorded output still says so on its tile",
          bq.NO_ARTIFACT in out)
    check("the tile is not left blank, which would read as a render that failed",
          'class="none"' in out)
    check("the explainer names the generator as where the gap has to be fixed",
          "queue_history.py" in out)
    check("and states that the page cannot check the branch itself",
          "never reads the results branch" in out)
    # The honest markers are a set, and a redesign that tidied one away would be
    # the exact failure this page exists to avoid.
    check("every marker still reaches the browser as a constant, not a retyping",
          "NO_ARTIFACT" in bq.LIVE_JS and "NO_PROMPT" in bq.LIVE_JS
          and "NO_NEGATIVE" in bq.LIVE_JS)


def test_the_queue_page_is_actually_published_and_actually_swept():
    """A page that exists only when someone runs its builder by hand is a page
    the founder will find as a 404 (this one already was, once). The wiring is
    three lines in three files and every one of them is a silent failure.
    """
    site = (REPO / "pipeline" / "build_site.py").read_text(encoding="utf-8")
    check("build_site.py runs the queue builder, so a deploy emits the page",
          "from build_queue import build" in site)

    qa = (REPO / "pipeline" / "qa_local.py").read_text(encoding="utf-8")
    check("the screening gate runs that builder too",
          "build_queue.py" in qa)
    check("and /queue is content-checked, not merely counted as a route",
          '"/queue"' in qa)

    import json as _json
    vercel = _json.loads((REPO / "vercel.json").read_text(encoding="utf-8"))
    sources = [h.get("source", "") for h in vercel.get("headers", [])]
    check("/queue is in the no-cache block with the other live pages",
          any("queue" in s and "status" in s for s in sources))

    sim = (REPO / "pipeline" / "build_sim.py").read_text(encoding="utf-8")
    check("/status points at the full history from its queue section",
          "queue.html" in sim and "full history" in sim)


# ---------------------------------------------------------------------------
# THE PICTURE A MOTION JOB STARTS FROM MUST BE A PLACE.
#
# 2026-08-14: nineteen motion renders went out and six animated a COSTUME
# IDENTITY CARD — one figure on flat blank paper, no location, no second
# character — because the wave sent each beat to "its newest good job" and for
# the guards that job was the identity pick. Two of the six scored at the top of
# the wave on frame-difference: a card breathing measures exactly like a shot,
# so nothing downstream could catch it. The check that catches it was written
# and validated by the motion-wave lane in review/ep2-picks/plate_check.py and
# promoted into pipeline/box_enqueue.py so it cannot be forgotten.
# ---------------------------------------------------------------------------


def _plate_png(kind: str) -> bytes:
    """A 704x1280 png that is either a place or a figure on blank paper."""
    import io
    import random

    from PIL import Image

    W, H = 704, 1280
    if kind == "card":
        im = Image.new("L", (W, H), 236)                     # pale blank paper
        im.paste(40, (W // 3, H // 3, 2 * W // 3, 2 * H // 3))   # centred figure
    else:
        # Texture out to the edges, which is what a drawn place has.
        im = Image.frombytes("L", (W, H), random.Random(20260814).randbytes(W * H))
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def _motion_spec(src: str, **extra) -> dict:
    spec = {
        "id": "ep2-b09-probe-0815",
        "consumer": "this test",
        "steps": [
            {"name": "crop", "argv": ["python.exe", "cover_crop.py", "--src", src,
                                      "--out", "init.png", "--size", "704x1280"]},
            {"name": "render", "argv": ["python.exe",
                                        "C:\\banyan-farm\\banyan-city\\pipeline\\ltx_i2v.py",
                                        "--stage", "render", "--jobs", "jobs.json"]},
        ],
    }
    spec.update(extra)
    return spec


FARM_SRC = ("C:\\banyan-farm\\courier-box\\farm-out\\ep2-b09-guardpick-0814\\"
            "09-the-pause-ipa-r0-w015-s0.png")


def test_only_a_motion_job_is_asked_what_its_picture_is():
    """The scoping is the point, not a convenience.

    A figure on blank paper is the CORRECT output for the stills lane's identity
    work — charref sheets, costume picks, turnarounds all want exactly the
    picture this refuses. A blanket gate on the shared queue would refuse
    legitimate work from another lane, so only i2v jobs are checked, decided the
    way box_job_minutes.py decides: off the steps' argv, never off the job id,
    because ids drift into nicknames while argv is what runs.
    """
    import box_enqueue as be
    import box_job_minutes as bjm

    def never(_path):
        raise AssertionError("a non-motion job must not even fetch a plate")

    card = _motion_spec(FARM_SRC)
    stills = {"id": "ep2-b01-figleaf-0814", "steps": [
        {"argv": ["python.exe", "cover_crop.py", "--src", FARM_SRC, "--out", "x.png"]},
        {"argv": ["python.exe", "goblin_ipa_beat.py", "--beat", "1"]}]}
    check("a job whose argv runs ltx_i2v animates", be.job_animates(card))
    check("a charref job does not, even naming the same picture",
          not be.job_animates(stills))
    check("and so it is never gated", be.plate_problems(stills, fetch=never) == [])
    check("which is the same classification box_job_minutes makes",
          bjm.job_kind(card) == "ltx" and bjm.job_kind(stills) == "charref")

    nickname = _motion_spec(FARM_SRC, id="a-perfectly-innocent-name")
    check("the id has no vote — a nicknamed motion job is still checked",
          be.job_animates(nickname))

    no_src = {"id": "x", "steps": [{"argv": ["python.exe", "ltx_i2v.py", "--stage",
                                             "render", "--jobs", "j.json"]}]}
    check("a motion job that crops nothing names no picture to measure",
          be.crop_src(no_src) is None and be.plate_problems(no_src, fetch=never) == [])


def test_a_motion_job_starting_from_a_costume_card_is_refused():
    """Flat border → refuse; textured border → pass; could not look → REFUSE.

    The third is half the guard's value and the easiest thing to lose in a move:
    "I could not check" must never exit zero. Two of the nineteen landed there,
    and one of those two was cropping the WRONG BEAT'S plate.
    """
    import box_enqueue as be

    card, scene = _plate_png("card"), _plate_png("scene")
    check("a figure on blank paper measures as blank",
          be.measure_plate(card) >= be.PLATE_FLAT_MAX)
    check("a picture with texture to its edges does not",
          be.measure_plate(scene) < be.PLATE_FLAT_MAX)

    refused = be.plate_problems(_motion_spec(FARM_SRC), fetch=lambda p: card)
    check("the card is refused", len(refused) == 1)
    said = refused[0] if refused else ""
    check("and the refusal names the picture, not just the verdict",
          "09-the-pause-ipa-r0-w015-s0.png" in said)
    check("prints what it measured against what it required",
          "0.62" in said and "flatness" in said.lower())
    check("says plainly that it looks like a card rather than a scene",
          "CHARACTER CARD" in said and "not a scene" in said)
    check("and says what to DO about it",
          "real scene plate" in said and "plate_ack" in said)

    check("the scene passes",
          be.plate_problems(_motion_spec(FARM_SRC), fetch=lambda p: scene) == [])

    # Could not look. Both shapes: nothing came back, and bytes that are not an
    # image. Neither may read as "fine".
    unfetchable = be.plate_problems(_motion_spec(FARM_SRC), fetch=lambda p: None)
    check("a plate that could not be fetched is REFUSED, not waved through",
          len(unfetchable) == 1 and "NOT checked" in unfetchable[0])
    local = _motion_spec("C:\\banyan-farm\\plates-local\\12-related-r4-s2.png")
    check("a --src off the results branch is unfetchable by definition",
          be.results_branch_path(local["steps"][0]["argv"][3]) is None)
    check("and is refused rather than skipped — this is the b12/b21 case",
          len(be.plate_problems(local, fetch=lambda p: None)) == 1)
    check("bytes that are not an image are refused too",
          len(be.plate_problems(_motion_spec(FARM_SRC),
                                fetch=lambda p: b"not a png")) == 1)

    # Waivable per job, never globally, and the waiver has to name itself.
    check("a deliberate macro can be acknowledged in the spec",
          be.plate_problems(_motion_spec(FARM_SRC, plate_ack="card: a macro of the fruit"),
                            fetch=lambda p: card) == [])
    check("an unfetchable plate can be acknowledged separately",
          be.plate_problems(_motion_spec(FARM_SRC, plate_ack="unfetchable: hand-staged"),
                            fetch=lambda p: None) == [])
    check("and the card waiver does not silently cover the unseen case",
          len(be.plate_problems(_motion_spec(FARM_SRC, plate_ack="card: a macro"),
                                fetch=lambda p: None)) == 1)


def test_the_plate_check_actually_runs_on_the_shared_enqueue_path():
    """A guard defined and never called is the lane-local script we started with.

    Also pins the two numbers whoever meets a borderline plate will need, and
    the statistic that was tried and rejected — a later reader with a foggy
    night plate in front of them cannot re-derive either from the code.
    """
    import box_enqueue as be

    real = be.fetch_results_blob
    be.fetch_results_blob = lambda p: _plate_png("card")
    try:
        spec = _motion_spec(FARM_SRC, node="002b-first-citizen")
        problems = be.gate_checks(spec, be.to_job(spec))
    finally:
        be.fetch_results_blob = real
    check("gate_checks refuses a card alongside the gate and approval checks",
          any("CHARACTER CARD" in p for p in problems))

    src = (REPO / "pipeline" / "box_enqueue.py").read_text(encoding="utf-8")
    check("the tightest legitimate scene is recorded with its number",
          "0.489" in src and "beat 21" in src)
    check("and why border stdev was rejected as the statistic",
          "33.0" in src and "44.0" in src)

    # The threshold was measured off the wave that broke. If the lane-local
    # original is still here, the promoted copy must not have drifted from it.
    origin = REPO / "review" / "ep2-picks" / "plate_check.py"
    if origin.exists():
        ns = {}
        exec(compile("\n".join(l for l in origin.read_text(encoding="utf-8").splitlines()
                               if l.startswith(("FLAT_MAX", "BAND", "TOL", "SIZE"))),
                     str(origin), "exec"), ns)
        check("threshold, band, tolerance and crop size match the original",
              (ns["FLAT_MAX"], ns["BAND"], ns["TOL"], ns["SIZE"])
              == (be.PLATE_FLAT_MAX, be.PLATE_BAND, be.PLATE_TOL, be.PLATE_SIZE))


# ---------------------------------------------------------------------------
# AND THE SAME WAVE CAUGHT BY ITS ARGUMENT RATHER THAN ITS PIXELS.
#
# The flatness check above measures the picture, and on 2026-08-15 two lanes
# established that the picture is not enough: the classes interleave, a tight
# portrait card reads 0.236 and a legitimate night field reads 0.489, so no cut
# point separates them. Grouped instead by the reference SET of the job that
# produced each plate, the split is clean — refs-charref-guards-r5-0812 (18 of
# 24 flagged), refs-guards-chosen-0814 (20 of 24) and refs-goblin-frozen-0812
# (63 of 84) against refs-guards-twoinfield-0813 (0 of 28, max 0.462) and
# refs-goblin-approved-0814 (0 of 48). b09's plates flip from >=0.94 to <=0.09
# on the same beat and the same prompt when only the refs change; b06 and b10 do
# the same. So box_enqueue traces a motion job's --src back to the job that
# published it and reads THAT job's --refs.
#
# BOTH GUARDS STAY, and these tests hold both: refs is exact but is a denylist a
# new set walks past, flatness is fuzzy but sees blank paper from any source.
# ---------------------------------------------------------------------------


def _producer_spec(*refs) -> dict:
    """A plate-generation spec that names `refs` on both its steps."""
    argv = ["python.exe", "goblin_ipa_beat.py", "--beat", "9"]
    for r in refs:
        argv += ["--refs", "C:\\banyan-farm\\wave-goblin-prep\\" + r]
    return {"id": "ep2-b09-guardpick-0814",
            "steps": [{"name": "dry", "argv": argv + ["--dry"]},
                      {"name": "sample", "argv": list(argv)}]}


def test_a_motion_jobs_plate_is_traced_back_to_the_job_that_drew_it():
    """Resolution is the whole mechanism: no --refs rides on the motion job.

    farm-out/<job-id>/<file> is written by the producing job's publish step under
    its own id, so the --src path is the one link back to the arguments the
    picture was drawn with. If that link breaks the check is blind, which is why
    a broken link is a refusal further down rather than a shrug.
    """
    import box_enqueue as be

    check("the --src names the job that published it",
          be.producing_job_id(FARM_SRC) == "ep2-b09-guardpick-0814")
    check("a --src that is not from farm-out has no producer to name",
          be.producing_job_id("C:\\banyan-farm\\plates-local\\12-related-r4-s2.png")
          is None)
    check("nor does a farm-out path with no job directory in it",
          be.producing_job_id("C:\\banyan-farm\\courier-box\\farm-out\\loose.png") is None)

    check("refs are read off every step, not just the first, and deduped by use",
          be.spec_refs(_producer_spec("refs-guards-chosen-0814"))
          == ["refs-guards-chosen-0814"] * 2)
    check("and are compared as basenames, not as box paths",
          be.spec_refs(_producer_spec("refs-a", "refs-b"))[:2] == ["refs-a", "refs-b"])
    check("a producer that named no reference set yields none",
          be.spec_refs({"steps": [{"argv": ["python.exe", "x.py"]}]}) == [])

    # The producer is looked up on disk, so the real specs must still resolve.
    real = be.producer_spec_path("ep2-b09-guardpick-0814")
    check("the real b09 guardpick spec resolves in pipeline/jobs",
          real is not None and real.endswith("ep2-b09-guardpick-0814.yaml"))
    check("and it is one of the sets the evidence condemns",
          any(r in be.CARD_REFS_DENYLIST for r in be.spec_refs(be.load_spec(real))))
    check("a directory nobody ever published resolves to nothing",
          be.producer_spec_path("ep2-b11-idfix-that-never-ran") is None)

    # AND THE HALF THAT WAS WRONG UNTIL 2026-08-16. This test used to assert
    # that ep2-b01-final055-r3 "has no spec on this machine". It has one --
    # ep2-b01-final055-r3-0812.yaml, which says in its own publish step that it
    # writes farm-out/ep2-b01-final055-r3. The directory simply does not carry
    # the date. 274 of the 645 published directories were refused this way.
    check("the name lookup alone still cannot see a dropped date suffix",
          be.producer_spec_path("ep2-b01-final055-r3") is None)
    found, why = be.resolve_producer("ep2-b01-final055-r3")
    check("but the spec that declares the directory is found, and it is real",
          why is None and found is not None
          and found.endswith("ep2-b01-final055-r3-0812.yaml"))
    check("a directory no spec declares is still unresolved, with a reason",
          be.resolve_producer("ep2-b11-idfix-that-never-ran")[0] is None)


def test_a_plate_drawn_from_a_card_reference_set_is_refused():
    """Denylisted refs → refuse; a clean set → pass; unresolvable → REFUSE.

    The third is the same law the plate check learned: "I could not check" must
    never exit zero. It is also not hypothetical — farm-out/b06-r6r7-recovered
    is a real published directory that no spec in the repo claims, and
    farm-out/ep2-b15-seedB is a real one that TWO specs write into.
    """
    import box_enqueue as be

    def producer(refs):
        return lambda _path: _producer_spec(refs)

    refused = be.refs_problems(_motion_spec(FARM_SRC),
                               load=producer("refs-guards-chosen-0814"))
    check("a plate drawn from a card reference set is refused", len(refused) == 1)
    said = refused[0] if refused else ""
    check("and the refusal names the set and the job that used it",
          "refs-guards-chosen-0814" in said and "ep2-b09-guardpick-0814" in said)
    check("and the picture, so a reader can go and look at it",
          "09-the-pause-ipa-r0-w015-s0.png" in said)
    check("says what is wrong with those sets in plain words",
          "COSTUME CARD" in said and "blank paper" in said)
    check("and says what to DO about it",
          "scene reference set" in said and "plate_ack" in said)

    # THE LOAD-BEARING HONESTY. A denylist cannot see a set nobody listed, and
    # the refusal has to say so — the flatness pass line was rewritten this week
    # for implying more than it had established.
    check("the refusal admits it is a denylist, not a detector",
          "DENYLIST" in said.upper() and "slip straight past" in said)
    check("and admits a producer that named no refs passes too",
          "named no refs" in said)

    check("a plate drawn from a scene reference set passes",
          be.refs_problems(_motion_spec(FARM_SRC),
                           load=producer("refs-guards-twoinfield-0813")) == [])
    check("so does a producer that named no reference set at all",
          be.refs_problems(_motion_spec(FARM_SRC),
                           load=lambda p: {"steps": [{"argv": ["x.py"]}]}) == [])

    # A NAME PATTERN WOULD NOT DO THIS, which is why the list is explicit: the
    # worst set by hit rate and the cleanest set share every word in their names
    # but one, and neither carries a `charref` tell.
    check("the two sets a pattern would confuse land on opposite verdicts",
          "refs-guards-chosen-0814" in be.CARD_REFS_DENYLIST
          and "refs-guards-twoinfield-0813" not in be.CARD_REFS_DENYLIST)

    # Could not resolve the producer. Two shapes: no job id in the path, and a
    # job id with no spec. Neither may read as "fine".
    local = _motion_spec("C:\\banyan-farm\\plates-local\\12-related-r4-s2.png")
    unresolved = be.refs_problems(local, load=producer("refs-guards-chosen-0814"))
    check("a --src with no traceable producer is REFUSED, not waved through",
          len(unresolved) == 1 and "NOT checked" in unresolved[0])
    absent = be.refs_problems(
        _motion_spec("C:\\banyan-farm\\courier-box\\farm-out\\b06-r6r7-recovered\\"
                     "06-r6-s0.png"))
    check("and so is a farm-out directory no spec in the repo claims — a real one",
          len(absent) == 1 and "b06-r6r7-recovered" in absent[0])

    # THE THIRD SHAPE, and the one a `<dir>-DATE` name rule would have got
    # confidently wrong: two specs publishing into ONE directory. Real —
    # ep2-b15-seedC-0813 published into farm-out/ep2-b15-seedB. Which job drew
    # a given plate there is not knowable from the path, so it is refused
    # rather than attributed to whichever name sorts first.
    tied = be.refs_problems(
        _motion_spec("C:\\banyan-farm\\courier-box\\farm-out\\ep2-b15-seedB\\"
                     "15-s0.png"))
    check("a directory two specs publish into is refused, not attributed",
          len(tied) == 1 and "2 specs publish into" in tied[0])
    check("and both candidates are named so a person can settle it",
          len(tied) == 1 and "ep2-b15-seedB-0812.yaml" in tied[0]
          and "ep2-b15-seedC-0813.yaml" in tied[0])

    def unreadable(_path):
        raise ValueError("mapping values are not allowed here")

    broken = be.refs_problems(_motion_spec(FARM_SRC), load=unreadable)
    check("a producer spec that will not parse is a REFUSAL, not a traceback",
          len(broken) == 1 and "NOT checked" in broken[0]
          and "could not be read" in broken[0])

    # Waivable per job, never globally, and — as with card/unfetchable — each
    # waiver names the one thing it waives.
    check("a card set can be acknowledged in the spec",
          be.refs_problems(_motion_spec(FARM_SRC, plate_ack="refs: b21 seed is a field"),
                           load=producer("refs-guards-chosen-0814")) == [])
    check("an unresolvable producer can be acknowledged on its own",
          be.refs_problems(_motion_spec(
              "C:\\banyan-farm\\plates-local\\12-related-r4-s2.png",
              plate_ack="unresolved: hand-staged, refs read by the lane")) == [])
    check("and the refs waiver does not silently cover the untraceable case",
          len(be.refs_problems(_motion_spec(
              "C:\\banyan-farm\\plates-local\\12-related-r4-s2.png",
              plate_ack="refs: this set is fine"))) == 1)

    # Scope, same as the plate check: card refs are the POINT of identity work.
    stills = {"id": "ep2-b01-figleaf-0814", "steps": [
        {"argv": ["python.exe", "cover_crop.py", "--src", FARM_SRC, "--out", "x.png"]},
        {"argv": ["python.exe", "goblin_ipa_beat.py", "--beat", "1"]}]}
    check("a charref job is never asked, even off a denylisted producer",
          be.refs_problems(stills, load=producer("refs-guards-chosen-0814")) == [])


def test_the_refs_check_runs_on_the_shared_enqueue_path_beside_the_flatness_one():
    """Both guards, both wired, neither standing in for the other.

    A job can honestly trip both — a plates-local --src is unfetchable AND
    untraceable — and one `plate_ack:` has to be able to say both things, or the
    jobs that need a waiver most cannot get one.
    """
    import box_enqueue as be

    real_fetch, real_load = be.fetch_results_blob, be.load_spec
    be.fetch_results_blob = lambda p: _plate_png("scene")   # flatness says fine
    be.load_spec = lambda p: _producer_spec("refs-guards-chosen-0814")
    try:
        spec = _motion_spec(FARM_SRC, node="002b-first-citizen")
        problems = be.gate_checks(spec, be.to_job(spec))
    finally:
        be.fetch_results_blob, be.load_spec = real_fetch, real_load
    check("gate_checks refuses on the refs even when the border looks textured",
          any("COSTUME CARD" in p for p in problems))

    # And the complement in the other direction: the flatness block is NOT
    # weakened by having a second guard beside it. A card from an unlisted set
    # is still caught by the pixels alone.
    be.fetch_results_blob = lambda p: _plate_png("card")
    be.load_spec = lambda p: _producer_spec("refs-nobody-has-listed-yet-0899")
    try:
        spec = _motion_spec(FARM_SRC, node="002b-first-citizen")
        problems = be.gate_checks(spec, be.to_job(spec))
    finally:
        be.fetch_results_blob, be.load_spec = real_fetch, real_load
    check("an unlisted card set slips the denylist and the pixels catch it",
          any("CHARACTER CARD" in p for p in problems))

    # One job, two honest refusals, and a waiver that can name both.
    both = be.plate_problems(local := _motion_spec(
        "C:\\banyan-farm\\plates-local\\12-related-r4-s2.png"), fetch=lambda p: None)
    both += be.refs_problems(local)
    check("a plates-local src is refused twice, once per reason", len(both) == 2)
    cleared = _motion_spec("C:\\banyan-farm\\plates-local\\12-related-r4-s2.png",
                           plate_ack=["unfetchable: hand-staged by the lane",
                                      "unresolved: refs read by hand"])
    check("and a list of acknowledgements can waive both",
          be.plate_problems(cleared, fetch=lambda p: None) == []
          and be.refs_problems(cleared) == [])
    check("a single-string ack still reads exactly as it always did",
          be.acked(_motion_spec(FARM_SRC, plate_ack="card: a macro"), "card")
          == "card: a macro")

    # The denylist is a named constant, not a literal buried in a function, so
    # that adding a set is an edit to a list a reader can find.
    src = (REPO / "pipeline" / "box_enqueue.py").read_text(encoding="utf-8")
    check("the denylist is a module-level named constant",
          "\nCARD_REFS_DENYLIST = (" in src)
    check("the evidence table that justifies each entry is recorded with it",
          "refs-guards-twoinfield-0813" in src and "0 of 28" in src)
    check("and the reason a name pattern was rejected", "no `charref` tell" in src)


# ==============================================================================
# A METRIC THAT CANNOT SEE A THREE-FRAME HOLD MUST NEVER BE THE ONE WE READ.
#
# `cadence` — louder index parity mean over quieter index parity mean — reported
# 1.06x, documented as "every frame is new", on a clip that holds every picture
# for three frames. It is a parity-2 detector: every ODD hold period aliases to
# exactly 1.00x by construction. These tests pin the aliasing table so the old
# number can never quietly come back, and pin the replacement — autocorrelation
# of the per-pair difference series, where the peak lag IS the hold period — on
# the same synthetic series the research used.
# Evidence: pipeline/research/ltx23-motion-source.md §4.1-4.2 (commit dfa87c27).
# ==============================================================================

def _comb(period, n=90, loud=8.0, quiet=0.3):
    """One loud pair every `period`: a clip holding each picture `period` frames."""
    return [loud if i % period == 0 else quiet for i in range(n)]


def test_the_retired_parity_ratio_is_blind_to_odd_holds():
    # The exact table from the research, reproduced as code. If any of these
    # numbers move, somebody has changed the retired function and it is only
    # kept so this test can exist.
    for period, expected in ((2, 26.67), (3, 1.00), (4, 14.12), (5, 1.00), (6, 9.56)):
        got = hp.legacy_parity_ratio(_comb(period))
        check("retired cadence on a period-%d hold reads %.2fx" % (period, expected),
              abs(got - expected) < 0.01)
    check("retired cadence is EXACTLY 1.00 on period 3 — the blindness",
          abs(hp.legacy_parity_ratio(_comb(3)) - 1.0) < 1e-9)
    check("retired cadence is EXACTLY 1.00 on period 5 — the blindness",
          abs(hp.legacy_parity_ratio(_comb(5)) - 1.0) < 1e-9)


def test_the_hold_period_is_the_peak_lag_for_every_period():
    for period in (2, 3, 4, 5, 6):
        r = hp.hold_period(_comb(period))
        check("a period-%d hold is read as period %d" % (period, period),
              r["period"] == period)
        check("and read strongly (%d)" % period, r["strength"] >= 0.9)
    # The two the old metric could not see at all.
    check("period 3 — invisible to the retired ratio — is caught at lag 3",
          hp.hold_period(_comb(3))["lags"][3] > 0.9)
    check("period 5 — invisible to the retired ratio — is caught at lag 5",
          hp.hold_period(_comb(5))["lags"][5] > 0.9)


def test_a_hold_shows_a_comb_and_not_just_a_peak():
    # A real period-3 hold anti-correlates at 1, 2, 4, 5 (-0.42 measured on
    # 0815-b13-AFTER). A lone peak with no trough around it is a different
    # animal, and the lag table is printed so a human can tell them apart.
    lags = hp.hold_period(_comb(3))["lags"]
    check("period 3 anti-correlates at the non-multiple lags",
          all(lags[k] < 0 for k in (1, 2, 4, 5)))
    check("and correlates again at its own harmonic", lags[6] > 0.9)
    check("but the harmonic never outranks the fundamental", lags[3] > lags[6])


def test_the_fundamental_wins_over_its_harmonic():
    # The period a human counts by opening frames is 3, never 6.
    check("a period-3 hold is reported as 3 and not 6",
          hp.hold_period(_comb(3))["period"] == 3)
    check("a period-2 hold is reported as 2 and not 4",
          hp.hold_period(_comb(2))["period"] == 2)


def test_it_reports_a_period_a_human_can_check_not_a_bare_score():
    r = hp.hold_period(_comb(3, n=96), fps=24.0)
    check("it reports how many distinct pictures the frames carry",
          r["distinct_pictures"] is not None and 31 <= r["distinct_pictures"] <= 33)
    check("it reports the effective frame rate a viewer experiences",
          abs(r["effective_fps"] - 8.0) < 0.01)
    check("and the reading names the period in words",
          "holds every 3 frames" in r["reading"])


def test_it_refuses_to_call_aperiodic_motion_a_hold():
    # Smooth, non-repeating motion: no peak lag. This must NOT read as a hold,
    # and equally must not be reported as a pass — the reading says so itself.
    ramp = [1.0 + 0.05 * i for i in range(90)]
    r = hp.hold_period(ramp)
    check("a smooth ramp is not a hold", r["period"] == 1)
    check("and the reading refuses to be read as approval",
          "NOT a claim" in r["reading"] and "motion is good" in r["reading"])
    check("a lag-1 peak is named as smooth variation, not as a period-1 hold",
          "peak is lag 1" in r["reading"])
    # Noise with no structure at all: below the floor, and it says the lag.
    import random
    random.seed(7)
    noise = [5.0 + random.random() for _ in range(90)]
    r = hp.hold_period(noise)
    check("structureless noise is not a hold either", r["period"] == 1)
    check("and it names the lag it looked at", "best lag" in r["reading"])


def test_a_long_period_is_not_reported_as_a_frame_hold():
    # ep2-b13-lw read period 11 and 0815-b04 read period 12 on 2026-08-15.
    # Eleven frames is half a second — a pulse, not a picture being held — and
    # a lane would have quoted "effective 2 fps" straight into a verdict.
    r = hp.hold_period(_comb(10, n=120))
    check("a 10-frame period is flagged as a pulse, not a frame hold",
          "PULSE OR SCENE RHYTHM" in r["reading"])
    r3 = hp.hold_period(_comb(3))
    check("and a real 3-frame hold carries no such caveat",
          "PULSE OR SCENE RHYTHM" not in r3["reading"])


def test_a_peak_at_the_edge_of_the_range_is_not_called_a_maximum():
    # A peak at max_lag has nothing above it to be higher than, so it has not
    # been shown to be the peak. Say so rather than report it as one.
    r = hp.hold_period(_comb(12, n=140), max_lag=12)
    check("a peak at the edge of the lag range says it is unconfirmed",
          "edge of the lag range" in r["reading"])
    check("and a peak inside the range does not",
          "edge of the lag range" not in hp.hold_period(_comb(3))["reading"])


def test_a_clip_that_never_changed_a_pixel_is_the_loudest_finding():
    r = hp.hold_period([0.0] * 90)
    check("a constant difference series has no period", r["period"] is None)
    check("and says FROZEN SOLID rather than falling through to 'no hold'",
          "FROZEN SOLID" in r["reading"])


def test_it_says_too_short_instead_of_guessing():
    r = hp.hold_period(_comb(3, n=10))
    check("ten pairs is too short to claim a period", r["period"] is None)
    check("and it says so", "too short" in r["reading"])


def test_the_metric_is_labelled_a_filter_everywhere_it_is_printed():
    # The rule that does not change: a metric errs in both directions and is a
    # filter, never a verdict. If it is ever printed without saying so, a lane
    # will quote it as one — which is how a 15-beat batch shipped frozen.
    for rel in ("pipeline/hold_period.py", "pipeline/coldread_frames.py",
                "review/ep2-picks/cadence_check.py"):
        src = (REPO / rel).read_text(encoding="utf-8")
        check("%s says the cold read decides" % rel,
              "cold read decides" in src or "COLD READ DECIDES" in src.upper())
        check("%s carries the aliasing table so nobody reinstates cadence" % rel,
              "1.00x" in src and "odd" in src.lower())


def test_stg_off_adds_no_argument_at_all():
    # THE PROMISE THIS PINS: a job that does not ask for STG must render exactly
    # what it rendered before the flag existed. The way that is guaranteed is
    # that "off" is an EMPTY DICT and not `stg_scale=0.0` — nothing is added to
    # the kwargs, so `pipe()` is called with the identical arguments and the
    # identical defaults. If someone ever "tidies" this into always passing a
    # zero, the call changes for every existing job and this test says so.
    import ltx_i2v
    for off in (0.0, 0, None, "", -1.0):
        check("stg_kwargs(%r, '') is empty — nothing is passed" % (off,),
              ltx_i2v.stg_kwargs(off, "") == {})
    check("stg_kwargs off ignores blocks entirely",
          ltx_i2v.stg_kwargs(0.0, "28") == {})


def test_stg_on_passes_exactly_the_two_upstream_arguments():
    # The names are the installed pipeline's, read off
    # LTX2ImageToVideoPipeline.__call__ (stg_scale line 883,
    # spatio_temporal_guidance_blocks line 890 in diffusers 0.39.0 on the box).
    # A misspelling here would be swallowed by **kwargs-shaped call sites and
    # render a silent control arm labelled as an STG one.
    import ltx_i2v
    got = ltx_i2v.stg_kwargs(1.0, "28")
    check("STG on passes exactly two keys, both upstream's names",
          set(got) == {"stg_scale", "spatio_temporal_guidance_blocks"})
    check("STG scale is a float", got["stg_scale"] == 1.0)
    check("STG blocks is a list of ints", got["spatio_temporal_guidance_blocks"] == [28])
    check("comma-separated blocks parse",
          ltx_i2v.stg_kwargs(2, "11,25,35")["spatio_temporal_guidance_blocks"]
          == [11, 25, 35])
    check("space-separated blocks parse",
          ltx_i2v.stg_kwargs(2, "11 25")["spatio_temporal_guidance_blocks"] == [11, 25])


def test_stg_without_blocks_is_refused_before_any_weight_loads():
    # Upstream refuses the same combination in check_inputs — but only after the
    # transformer is resident, i.e. ~90s and a full model load into a traceback.
    # Refusing in the pure helper means the CLI can refuse at parse time.
    import ltx_i2v
    try:
        ltx_i2v.stg_kwargs(1.0, "")
        check("stg_scale>0 without blocks is refused", False)
    except ValueError as exc:
        check("stg_scale>0 without blocks is refused", True)
        check("the refusal names the recommended block for LTX-2.3",
              "28" in str(exc))


def test_the_stg_flags_default_to_off_on_the_command_line():
    # argparse defaults are half the promise; the other half is that the render
    # path reads them through stg_kwargs. Both are checked in the source rather
    # than by running a render, because running one needs a 5090.
    src = (REPO / "pipeline" / "ltx_i2v.py").read_text(encoding="utf-8")
    check("--stg-scale defaults to 0.0",
          '"--stg-scale", type=float, default=0.0' in src)
    check("--stg-blocks defaults to empty", '"--stg-blocks", default=""' in src)
    check("the render path adds STG only through stg_kwargs",
          "stg = stg_kwargs(getattr(a" in src and "if stg:\n        common.update(stg)" in src)
    # The two pipe() call sites take the recipe through **common. If STG were
    # ever written as a literal keyword on one of them the two stages of the
    # two-stage recipe could silently disagree, so there must be exactly one
    # place STG enters the kwargs and it must be the update above.
    check("STG enters the kwargs in exactly one place",
          src.count("common.update(stg)") == 1)
    check("the sidecar records STG and omits it when off",
          '"stg": ("scale %g blocks %s"' in src)


def _fake_hf_cache(root, repo, blobs):
    """Build a huggingface-shaped cache. `blobs` maps blob NAME -> bytes.

    The name is what the hub would have called the file (the sha256 of the
    content it served); the bytes are what actually landed on this disk. The
    two disagreeing IS the defect, so the fixture has to be able to express it.
    """
    d = root / ("models--" + repo.replace("/", "--")) / "blobs"
    d.mkdir(parents=True, exist_ok=True)
    for name, content in blobs.items():
        (d / name).write_bytes(content)
    return d


def _sha(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def test_a_weight_file_is_judged_by_its_content_and_not_its_length(td):
    # THE DEFECT, exactly as it was on macbook1 and macbook3 on 2026-08-15:
    # a 5.1 GB UNet with the right byte length whose content was 88%/93%
    # zeros, because an rsync left holes in it. SDXL rendered pure noise,
    # deterministically, and nothing anywhere errored.
    import mac_preflight as mp
    good = b"weights!" * 4096                      # 32 KiB of real content
    name = _sha(good)
    holed = b"weights!" * 512 + b"\0" * (len(good) - 4096)   # same length, holes

    root = Path(td) / "hub"
    _fake_hf_cache(root, "cagliostrolab/animagine-xl-3.1", {name: good})
    ok, why = mp.weights_ok(str(root), min_bytes=1)
    check("an intact blob passes", ok and why == [])

    # same path, same name, same LENGTH — only the bytes differ
    _fake_hf_cache(root, "cagliostrolab/animagine-xl-3.1", {name: holed})
    ok, why = mp.weights_ok(str(root), min_bytes=1)
    check("a holed blob of the correct length is CAUGHT", not ok)
    check("the refusal names the repo, not just a hash",
          any("animagine" in w for w in why))
    check("the refusal says how much of the file is nothing",
          any("all-zero" in w for w in why))


def test_the_checks_that_passed_this_defect_still_pass_it(td):
    # A lane checked "33 files, 25 symlinks, 6940 MB" and concluded the weights
    # were byte-identical. This pins WHY that was blind: on the good and the
    # holed tree, file count and total size are identical to the byte. If
    # someone ever replaces the content check with a cheaper one, this fails.
    import mac_preflight as mp
    good = b"weights!" * 4096
    name = _sha(good)
    holed = b"weights!" * 512 + b"\0" * (len(good) - 4096)

    a, b = Path(td) / "a", Path(td) / "b"
    da = _fake_hf_cache(a, "x/y", {name: good})
    db = _fake_hf_cache(b, "x/y", {name: holed})
    manifest = lambda d: sorted((p.name, p.stat().st_size) for p in d.iterdir())
    check("file count and size are IDENTICAL across good and broken",
          manifest(da) == manifest(db))
    check("...and the content check separates them anyway",
          mp.weights_ok(str(a), min_bytes=1)[0]
          and not mp.weights_ok(str(b), min_bytes=1)[0])


def test_an_empty_or_missing_cache_is_not_a_pass(td):
    # "No corrupt blobs" is trivially true of a machine with no weights at all.
    # macbook5 is in exactly that state, and a guard that green-lights it would
    # hand it work it cannot start.
    import mac_preflight as mp
    ok, why = mp.weights_ok(str(Path(td) / "nope"), min_bytes=1)
    check("a missing cache BLOCKS rather than passing empty", not ok)
    empty = Path(td) / "empty"
    empty.mkdir()
    ok, why = mp.weights_ok(str(empty), min_bytes=1)
    check("a cache with no weights BLOCKS", not ok)
    check("and says nothing is there to render with",
          any("nothing to render" in w or "no model weights" in w for w in why))


def test_only_content_addressed_blobs_are_compared_to_their_names(td):
    # A 40-hex blob is a git SHA-1 (`sha1("blob <len>\0" + content)`), NOT a
    # digest of the content — comparing it with sha256 would flag every small
    # git-tracked file in the cache and train everyone to ignore the guard.
    import mac_preflight as mp
    check("64 hex is content-addressed", mp.is_content_addressed("a" * 64))
    check("40 hex (git sha1) is skipped", not mp.is_content_addressed("a" * 40))
    check("a non-hex name is skipped", not mp.is_content_addressed("z" * 64))
    check("uppercase is not the hub's form", not mp.is_content_addressed("A" * 64))

    root = Path(td) / "hub"
    good = b"weights!" * 4096
    _fake_hf_cache(root, "x/y", {_sha(good): good, "b" * 40: b"config" * 1000})
    ok, why = mp.weights_ok(str(root), min_bytes=1)
    check("a git-sha1 blob beside a good one raises no false alarm", ok)


def test_a_latent_that_never_contracted_is_reported_as_noise():
    # Measured 2026-08-16 on the real defect: healthy final latent std 1.02 on
    # macbook2, 17.03 on macbook1 and macbook3 — which decoded to a
    # byte-identical noise PNG on both. The band has ~5x margin either way.
    # This is the check that would also catch a cause hashes cannot see, e.g.
    # pytorch/pytorch#141471, a diffusion model rendering "nothing but noise"
    # from a torch version bump alone.
    import mac_preflight as mp
    check("a healthy final latent passes", not mp.latent_is_degenerate(1.02))
    check("the measured broken value is caught", mp.latent_is_degenerate(17.03))
    check("SDXL's initial sigma is caught (never contracted)",
          mp.latent_is_degenerate(14.6))
    check("NaN latents are degenerate too",
          mp.latent_is_degenerate(float("nan")))
    check("the ceiling sits between the two measured values",
          1.02 < mp.LATENT_STD_CEILING < 17.03)


def test_the_worker_refuses_before_it_loads_a_model():
    # Placement is the whole value: checking after from_pretrained means the
    # machine has already claimed the task. Checking at startup means it never
    # claims one. Both call sites are pinned here because a future edit that
    # moves the guard below the load would restore the silent-noise behaviour
    # with every test still green.
    src = (REPO / "pipeline" / "farm_worker.py").read_text(encoding="utf-8")
    check("the worker checks weights at startup, before claiming work",
          "require_intact_weights(courier)\n" in src)
    check("the guard runs BEFORE from_pretrained, not after",
          src.index("require_intact_weights(courier)\n    pipe = cls.from_pretrained")
          < src.index("pipe.to(device)"))
    check("the refusal is marked to the branch, not only printed",
          "courier.blame(msg)" in src)
    check("refusing raises rather than returning a usable pipe",
          "raise SystemExit(msg)" in src)


def test_a_corrected_gate_never_reaches_the_queue_page_uncorrected():
    # THE FAILURE, 2026-08-16. gate-evidence.yaml never erases a superseded
    # line: it leaves it standing and writes a dated `gate_CORRECTION_MMDD`
    # sibling beside it. queue_history.py read `gate` alone, so six rows saying
    # "GATED - guard cast unapproved (his call)" were copied into
    # queue-history.json and rendered on /queue (build_queue.py reads
    # det.verdict.gate) — a block the founder lifted the same day. The reader
    # must carry the correction, because the JSON is machine-written and a
    # hand-edit would be overwritten by the next run.
    import queue_history as qh
    plain = {"beat": "02", "gate": "ships under the two-round rule"}
    check("an uncorrected gate is passed through untouched",
          qh.gate_text(plain) == "ships under the two-round rule")
    corrected = {"beat": "05",
                 "gate": "GATED - guard cast unapproved (his call)",
                 "gate_CORRECTION_0816": "the cast stands as drawn"}
    out = qh.gate_text(corrected)
    check("the superseded text is still there, not erased",
          out.startswith("GATED - guard cast unapproved (his call)"))
    check("and it is marked superseded", "SUPERSEDED" in out)
    check("pointing at the key that holds the correction",
          "gate_CORRECTION_0816" in out)
    check("a missing gate stays missing rather than becoming a string",
          qh.gate_text({"beat": "03"}) is None)
    # A lowercase or undated sibling is NOT a correction: the convention is a
    # dated, shouted key, and a loose match would silently mute real gates.
    check("an undated sibling does not mute the gate",
          qh.gate_text({"beat": "06", "gate": "GATED - x",
                        "gate_note": "y"}) == "GATED - x")
    # The live file must actually carry the six corrections, or this reader is
    # correct and the record is still wrong.
    import yaml
    ge = yaml.safe_load(
        (REPO / "review" / "ep2-picks" / "gate-evidence.yaml").read_text(encoding="utf-8"))
    stale = [str(b["beat"]) for b in ge["beats"]
             if "guard cast unapproved" in str(b.get("gate") or "")
             and not any(str(k).startswith("gate_") and str(k) != "gate"
                         for k in b)]
    check("no guard-cast row is left without its dated correction", not stale)


def test_a_lifted_block_and_a_wrong_success_bar_cannot_reach_the_ledger():
    # THE SAME FAILURE AS ABOVE, TWICE MORE, FOUND 2026-08-16. A decision moves
    # and the records that act on it do not. gate_text() fixed one field; this
    # covers the general reader and the two other fields it now protects.
    #
    #   (a) episode-progress.yaml was measured 2026-08-14 09:40Z and holds
    #       twelve goblin beats at `blocked-decision -- goblin beat, character
    #       gate`. He opened that gate at 2026-08-14T11:09:07Z ("seed s0 is the
    #       goblin") and all twelve have animated since. queue_history copies
    #       `state` into every job row, so 248 rows carried the dead block --
    #       beat 20's printed it beside `gate: "rendering now (2 jobs)"`.
    #   (b) the ALL-21 WAVE was authored by copying one spec, so 28 of its 32
    #       specs carried BEAT 02's `consumer`/`why`/`success`. The recorded
    #       bar for the beat-20 clip read "a goblin sprints in, skids and dives
    #       behind a sapling" -- beat 02's action, not beat 20's. That prose
    #       reached the ledger's `purpose` block for all 28 runs.
    import queue_history as qh
    check("an uncorrected field is passed through untouched",
          qh.carry_correction({"state": "fix-known"}, "state", "f.yaml")
          == "fix-known")
    check("a missing field stays missing rather than becoming a string",
          qh.carry_correction({}, "state", "f.yaml") is None)
    st = qh.carry_correction(
        {"state": "blocked-decision",
         "state_CORRECTION_0816": "the gate is open"}, "state", "ep.yaml")
    check("the superseded state is still there, not erased",
          st.startswith("blocked-decision"))
    check("and the state is marked superseded", "SUPERSEDED" in st)
    check("naming the key and the file that hold the correction",
          "state_CORRECTION_0816" in st and "ep.yaml" in st)
    check("an undated sibling does not mute a state",
          qh.carry_correction({"state": "blocked-decision",
                               "state_note": "x"}, "state", "f") ==
          "blocked-decision")
    # A gate is a yes/no, so a pointer suffices. A SUCCESS LINE IS THE BAR
    # SOMEONE JUDGES A CLIP AGAINST, so the replacement has to travel with the
    # row -- a pointer to another file is what let 28 clips be read against the
    # wrong beat in the first place.
    sc = qh.carry_correction(
        {"success": "a goblin sprints in, skids and dives",
         "success_CORRECTION_0816": "BOTH HANDS to the fruit, then the look UP"},
        "success", "spec.yaml", include_text=True)
    check("a corrected success line carries its replacement inline, not a pointer",
          "BOTH HANDS to the fruit" in sc)
    check("and still shows the superseded bar it replaces",
          sc.startswith("a goblin sprints in, skids and dives"))
    # gate_text keeps its own behaviour: pointer only, no inlined text.
    check("a gate still points rather than inlining",
          "the cast stands as drawn" not in
          qh.gate_text({"gate": "GATED", "gate_CORRECTION_0816":
                        "the cast stands as drawn"}))
    # The live files must actually carry the corrections, or this reader is
    # right and the record is still wrong.
    import yaml
    ep = yaml.safe_load((REPO / "pipeline" / "measured" /
                         "episode-progress.yaml").read_text(encoding="utf-8"))
    ep2 = [e for e in ep["episodes"] if e.get("number") == 2][0]
    stale = [b["n"] for b in ep2["beats"]
             if "character gate" in str(b.get("note") or "")
             and not qh.correction_keys(b, "state")]
    check("no goblin beat is left asserting the character gate uncorrected",
          not stale)
    # THE CENSUS OF THE TWELVE, REWRITTEN 2026-08-19 AND NOT DELETED. This asked
    # for twelve `state_CORRECTION_*` siblings, which was the right check for as
    # long as the twelve rows still held their 08-14 states. All 21 ep2 rows have
    # since been REMEASURED, and a correction of a state that no longer exists
    # has nothing to correct — worse, `carry_correction` would stamp the NEW
    # state SUPERSEDED and republish the retracted reading into /queue, which is
    # the exact failure this test was written to stop, running backwards. So the
    # invariant is asserted one level up, where it survives a remeasure: each of
    # the twelve is either corrected in place OR its old reading is preserved
    # where the remeasure put it, and the twelve are still accounted for one by
    # one. Silently dropping any of them still fails.
    twelve = [2, 3, 4, 7, 8, 13, 14, 15, 16, 17, 19, 20]
    before = (ep.get("remeasured_0819") or {}).get("states_before") or {}
    kept = [n for n in twelve
            if any(b["n"] == n and (qh.correction_keys(b, "state")
                                    or str(before.get(n) or "") == "blocked-decision")
                   for b in ep2["beats"])]
    check("all twelve of them are still accounted for — corrected in place, or "
          "remeasured with the reading they replaced kept on the record",
          sorted(kept) == twelve)
    import episode_eta as _eta
    check("...and no remeasured row pretends the old reading was never made",
          len(before) == len(ep2["beats"])
          and all(str((b.get("remeasured_0819") or {}).get("previous_state") or "")
                  in set(_eta.STATES) for b in ep2["beats"]))
    # And the 28 wave specs: every one that is not beat 02 must carry its own
    # bar, and the four that ARE beat 02 must be left alone.
    # Select on the byte-identical header LINE, not on the phrase anywhere in
    # the file. Grepping for "ALL-21 WAVE" picked up 34 files the moment this
    # audit's own correction prose mentioned the wave by name in two beat-16
    # specs — a selector contaminated by the thing it selects for. The first
    # line is the actual identity: all 32 carry it byte for byte.
    jobs = REPO / "pipeline" / "jobs"
    header = ("# 2026-08-14. ALL-21 WAVE, authored and NOT enqueued. "
              "It fires the moment he approves the plates.\n")
    wave = [p for p in sorted(jobs.glob("*.yaml"))
            if p.read_text(encoding="utf-8").startswith(header)]
    check("the wave is still the thirty-two specs this audit counted",
          len(wave) == 32)
    wrong = []
    for p in wave:
        spec = yaml.safe_load(p.read_text(encoding="utf-8"))
        beat02 = int(spec["beat"]) == 2
        corrected = bool(qh.correction_keys(spec, "success"))
        if beat02 == corrected:      # b02 corrected, or non-b02 left stale
            wrong.append(p.name)
    check("every non-beat-02 wave spec carries its own success bar, and the "
          "four real beat-02 specs are untouched", not wrong)
    # THE WAVE WAS NOT THE BLAST RADIUS. The handover reported 28 of 32; the
    # ledger rebuild proved beat 02's prose had been pasted well past the wave
    # — 80 specs carry it and only 13 are beat 02, including beats (16) that
    # were never in the wave at all. Guard the real population, so the next
    # paste of this line is caught wherever it lands.
    SPRINT = "sprints in, skids and dives behind a sapling"
    # SIX specs are staged for deletion by another lane and are deliberately
    # left alone; drop them from the population rather than from the rule.
    # THE LIST MUST BE ALL SIX, NOT THE FOUR A LOCAL `ls` SHOWS. Four of them
    # (b14/b15) were also recreated untracked, so they exist on disk; the two
    # b17 ones are staged-deleted AND gone from the working tree while still
    # tracked in HEAD. A local run therefore never sees them and passes, and CI
    # checks out HEAD, sees them, and fails — which is exactly what happened on
    # commit 4f68cdfd. Existence on disk is a proxy; the committed tree is the
    # fact.
    staged_deleted = {"ep2-b14-s49-0815.yaml", "ep2-b14-s49B-0815.yaml",
                      "ep2-b15-s49-0815.yaml", "ep2-b15-s49B-0815.yaml",
                      "ep2-b17-s49-0815.yaml", "ep2-b17-s49B-0815.yaml"}
    stale_bar = []
    for p in sorted(jobs.rglob("*.yaml")):
        if p.name in staged_deleted:
            continue
        raw = p.read_text(encoding="utf-8")
        if SPRINT not in raw:
            continue
        try:
            spec = yaml.safe_load(raw)
        except Exception:
            continue
        if not isinstance(spec, dict) or int(spec.get("beat") or -1) == 2:
            continue
        if SPRINT in str(spec.get("success") or "") \
                and not qh.correction_keys(spec, "success"):
            stale_bar.append(p.name)
    check("no non-beat-02 spec anywhere in pipeline/jobs still records beat "
          "02's sprint as its own success bar", not stale_bar)


def main():
    import tempfile
    test_a_stale_harness_cannot_render_a_killed_wording()
    test_a_job_cannot_be_filed_with_outputs_nobody_can_find()
    test_a_finished_job_cannot_be_filed_with_nothing_to_carry_it_home()
    test_a_newer_mirror_alone_is_not_a_stuck_deploy()
    test_a_resolved_call_can_never_render_as_waiting_on_the_author()
    test_beat_duration_from_timecode()
    test_beat_duration_fallback()
    with tempfile.TemporaryDirectory() as td:
        test_find_clip_naming(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_find_audio_naming(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_pingpong_loop_seams(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_held_still_is_never_reversed(Path(td))
    test_held_zoom_is_monotonic_and_moderate()
    with tempfile.TemporaryDirectory() as td:
        test_held_sidecar_is_readable_by_every_tool_that_reads_it(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_every_sidecar_reader_finds_both_shapes(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_farm_still_sidecar_records_what_actually_ran(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_bench_sidecar_names_the_beat_or_omits_it(Path(td))
    test_wrap_never_drops_words()
    test_caption_chunks()
    test_sync_shots_is_idempotent()
    test_kaggle_notebook_cells_parse()
    test_sd_prompt_fits_clip_and_keeps_the_action()
    test_negative_prompt_cannot_overflow_in_silence()
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
    test_attempts_survive_a_dead_host()
    test_queue_backlog_is_invisible_to_workers()
    test_a_revived_worker_cannot_choke_on_the_tasks_list()
    test_queue_promoter_gate_beats_everything()
    test_queue_promotion_is_one_atomic_move()
    test_argparse_declares_every_flag_it_reads()
    test_child_verdict_names_a_corpse()
    test_a_busy_card_refuses_the_render()
    with tempfile.TemporaryDirectory() as td:
        test_giveup_needs_no_fail_line(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_hand_ledger_done_stops_a_worker_that_never_ran_it(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_animegen_casts_before_the_second_expert(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_licence_gate(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_no_undefined_locals(Path(td))
        test_subprocess_reads_are_utf8(Path(td))
        test_a_heartbeat_commits_only_the_heartbeat(Path(td))
        test_queue_render_params_reach_the_child(Path(td))
        test_probe_beat_sends_the_files_and_the_whole_recipe(Path(td))
    test_ltx_frames_are_the_nearest_8n_plus_1()
    with tempfile.TemporaryDirectory() as td:
        test_ltx_dispatch_routes_by_video_model(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_ltx_jobs_list_is_one_beat_per_entry(Path(td))
    test_sidecar_only_calls_the_negative_inert_when_it_is()
    with tempfile.TemporaryDirectory() as td:
        test_the_conditioning_plate_is_the_episode_crop(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_no_render_path_stretches_a_mismatched_still(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_dispatch_never_hands_a_renderer_a_raw_still(Path(td))
    test_vercel_build_guard_covers_every_site_input()
    with tempfile.TemporaryDirectory() as td:
        test_links_resolve_against_the_url_a_page_is_served_at(Path(td))
    test_review_page_publishes_nothing_unprovenanced()
    with tempfile.TemporaryDirectory() as td:
        test_the_review_gallery_clears_on_three_conditions_and_nothing_less(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_review_queue_comes_before_the_record(Path(td))
    test_checklist_does_not_reask_a_closed_question()
    with tempfile.TemporaryDirectory() as td:
        test_beat11_direction_is_the_founders_revert(Path(td))
        test_beat09_negatives_forbid_the_growth(Path(td))
        test_hosted_path_sends_our_negative(Path(td))
        test_antistatic_first_signal_wins(Path(td))
        test_last_beat_action_stops_at_the_beat_list(Path(td))
        test_vendored_licence_does_not_launder(Path(td))
        test_nested_licence_does_not_launder(Path(td))
    # Own temp dir each: these build real git repositories, and a repo inside a
    # repo would answer for the wrong tree.
    with tempfile.TemporaryDirectory() as td:
        test_the_board_links_only_frames_the_deploy_has(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_frame_the_tree_carries_but_the_licence_blocks_is_named_not_linked(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_no_git_never_silently_empties_the_board(Path(td))
    # POSTERS BY BYTES — review-poster-names-stale-still-1786197251. Own temp dir
    # each: these write stills/ trees and then move file mtimes around in them.
    with tempfile.TemporaryDirectory() as td:
        test_a_promoted_still_does_not_reposter_an_older_clip(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_record_we_cannot_honour_gets_no_poster_at_all(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_hashless_name_that_changed_hands_is_refused(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_shot_that_records_no_still_gets_no_poster(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_held_clip_records_the_bytes_it_was_handed(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_held_pick_the_founder_has_not_seen_says_so_in_its_own_record(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_the_nested_init_frame_dialect_resolves_like_the_flat_one(Path(td))
    test_every_served_cut_posters_the_frame_its_record_names()
    test_the_infra_meter_never_prints_a_number_the_page_did_not_measure()
    # A HAND-RUN THAT BORROWS A QUEUE ID CLAIMS IT — pure: no git, no network.
    test_a_hand_claim_writes_lines_every_reader_already_parses()
    test_a_hand_claim_reads_the_verdict_off_the_exit_code()
    test_a_hand_claim_refuses_an_id_nobody_filed()
    test_a_job_run_by_hand_reaches_the_status_counters()
    # WHAT THE WORK LIST SAYS WHEN IT DOES NOT KNOW — pure: urlopen is stubbed.
    test_a_retired_id_still_says_what_the_job_was()
    test_an_age_counts_from_the_line_not_from_the_push()
    test_a_rate_limited_build_can_still_see_hand_work()
    test_a_log_it_could_not_read_is_not_a_day_with_no_work()
    test_the_queue_is_reported_in_time_and_never_guessed()
    # A CONCATENATION MUST NOT LAUNDER ITS INPUTS — own temp dir each: these
    # rewrite and delete source clips under a manifest that names them.
    with tempfile.TemporaryDirectory() as td:
        test_a_cut_holding_one_refused_ingredient_does_not_publish(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_cut_whose_manifest_no_longer_describes_its_inputs_does_not_publish(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_cut_whose_ingredients_all_pass_publishes_unchanged(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_steward_pick_stays_labelled_after_it_is_concatenated(Path(td))
    # ...AND A HELD SHOT IS ONLY AS PUBLISHABLE AS THE FRAME IT HOLDS.
    with tempfile.TemporaryDirectory() as td:
        test_a_held_shot_is_only_as_publishable_as_the_frame_it_holds(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_canon_promotion_cannot_strip_the_record_that_refuses_it(Path(td))
    # ...AND THE PROMOTION ITSELF CARRIES THE RECORD OR DOES NOT HAPPEN. Own temp
    # dir each: promote_still and build_site are pointed at the tree as their
    # REPO, so two trees in one directory would answer for each other.
    with tempfile.TemporaryDirectory() as td:
        test_a_promotion_records_the_weights_and_not_the_machine(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_promoted_composite_carries_the_frame_it_was_drawn_from(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_promotion_that_would_launder_a_licence_writes_nothing(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_take_the_tree_cannot_account_for_is_refused_by_name(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_canon_name_is_freed_by_recording_the_refusal(Path(td))
    test_the_live_v34_cut_is_refused_by_the_frames_inside_it()
    # REGIONAL IP-ADAPTER GEOMETRY (memo §3.3) — pure: PIL only, no torch.
    test_a_region_mask_conditions_its_box_and_nothing_else()
    test_a_box_that_names_no_region_is_refused_not_rounded()
    test_the_reference_crop_keeps_only_the_subject()
    # CHECK_INVENTION AGAINST GROUND TRUTH — pure: the clips are untracked, so
    # these read the committed measurements and run the real verdict() on them.
    test_nine_clips_cannot_license_a_threshold_however_cleanly_they_split()
    test_a_metric_that_points_the_wrong_way_is_not_a_separator()
    test_leave_one_out_catches_the_threshold_that_only_fits_what_it_saw()
    test_the_labelled_set_is_internally_consistent()
    test_the_committed_measurements_cover_every_candidate_and_every_clip()
    test_the_detector_states_its_measured_recall_and_states_it_correctly()
    test_the_metric_that_cleared_the_correction_still_misses_what_it_never_saw()
    test_striking_the_backwards_conjunct_would_flag_everything()
    # THE MAC'S RENDER LOOP MUST NOT PUBLISH TO HIS SCREEN BY ACCIDENT.
    test_an_agent_run_cannot_put_candidates_on_the_founders_screen()
    # A PAGE HE WAS PROMISED MUST REACH THE SITE, AND ITS ABSENCE MUST BE LOUD.
    with tempfile.TemporaryDirectory() as td:
        test_a_review_page_the_build_never_copied_cannot_pass_the_gate(Path(td))
    # THE MIRROR AND PRODUCTION MUST NAME THE SAME OWNER.
    test_the_repo_owner_is_read_from_the_platform_that_is_building()
    # TWO WRITERS MUST NEVER SHARE ONE BRANCH AGAIN.
    test_the_courier_and_the_telemetry_daemon_own_different_branches()
    # A RENDER THAT LANDED MUST NEVER READ AS A RENDER THAT CRASHED.
    test_a_plate_that_rendered_is_not_a_plate_that_failed()
    test_the_scene_plate_specs_declare_the_names_the_sampler_writes()
    test_every_reader_falls_back_to_where_the_vitals_used_to_be()
    test_a_rev_parse_that_failed_is_not_a_sha()
    # THE STATUS PAGE MUST GO STALE ON ITS OWN, NOT ON A REMINDER.
    test_the_box_publishes_its_own_queue_and_never_a_zero_it_did_not_measure()
    test_the_queue_is_a_picture_and_the_picture_cannot_lie()
    test_the_queue_leads_the_page_and_says_so_once()
    test_the_status_page_can_actually_find_the_numbers_it_rewrites()
    # AND HE MUST BE ABLE TO SEE WHAT IT IS MAKING.
    test_the_box_publishes_what_it_is_making_and_what_it_just_made()
    test_the_dropdown_will_not_render_whatever_a_filename_says()
    test_the_depth_series_leaves_a_gap_where_it_could_not_look()

    test_every_beat_gets_exactly_one_leaf_and_an_unscored_one_shows_as_missing()
    test_the_beat_states_are_grouped_by_whose_clock_they_are_on()
    test_a_kind_keeps_its_shade_on_a_day_the_other_kinds_are_missing()
    test_a_bar_is_as_tall_as_its_minutes_and_a_part_day_says_so()
    test_the_charts_fetch_nothing_and_claim_nothing_they_cannot_read()
    test_the_episode_now_strip_counts_the_cut_and_never_its_own_source()
    test_the_latest_cut_manifest_is_found_by_name_and_shape_checked()
    test_the_queue_depth_line_refuses_to_cross_a_gap_it_did_not_measure()

    # AND WORK HE WAS NEVER SHOWN MUST BE A NUMBER SOMEBODY READS.
    test_a_render_that_reached_a_page_is_not_an_unpaged_render()
    test_a_render_no_page_names_is_the_number_this_exists_to_report()
    test_a_render_that_produced_nothing_is_a_failed_render_not_an_unpaged_one()
    test_the_count_is_promises_to_him_and_not_every_render_on_the_farm()
    test_one_round_asked_twice_is_one_unshown_picture()
    test_a_tree_that_cannot_see_the_farm_branch_says_so_instead_of_zero()

    # AND HE MUST BE ABLE TO READ THE PROMPT THAT MADE THE FRAME HE IS JUDGING.
    test_the_queue_page_prints_the_prompt_that_made_the_frame()
    test_a_prompt_nobody_recorded_says_so_instead_of_looking_empty()
    test_the_queue_gallery_can_be_narrowed_to_one_beat_and_opened_full_size()
    test_the_queue_never_claims_to_have_checked_the_results_branch()
    test_the_queue_page_is_actually_published_and_actually_swept()

    # AND A MOTION JOB MUST START FROM A PLACE, NOT FROM A COSTUME CARD.
    test_only_a_motion_job_is_asked_what_its_picture_is()
    test_a_motion_job_starting_from_a_costume_card_is_refused()
    test_the_plate_check_actually_runs_on_the_shared_enqueue_path()
    test_a_motion_jobs_plate_is_traced_back_to_the_job_that_drew_it()
    test_a_plate_drawn_from_a_card_reference_set_is_refused()
    test_the_refs_check_runs_on_the_shared_enqueue_path_beside_the_flatness_one()

    # AND A METRIC THAT CANNOT SEE A THREE-FRAME HOLD MUST NEVER BE READ AGAIN.
    test_the_retired_parity_ratio_is_blind_to_odd_holds()
    test_the_hold_period_is_the_peak_lag_for_every_period()
    test_a_hold_shows_a_comb_and_not_just_a_peak()
    test_the_fundamental_wins_over_its_harmonic()
    test_it_reports_a_period_a_human_can_check_not_a_bare_score()
    test_it_refuses_to_call_aperiodic_motion_a_hold()
    test_a_long_period_is_not_reported_as_a_frame_hold()
    test_a_peak_at_the_edge_of_the_range_is_not_called_a_maximum()
    test_a_clip_that_never_changed_a_pixel_is_the_loudest_finding()
    test_it_says_too_short_instead_of_guessing()
    test_the_metric_is_labelled_a_filter_everywhere_it_is_printed()
    # AND THE ONE MOTION LEVER A MAINTAINER NAMED MUST BE OFF UNLESS ASKED FOR.
    test_stg_off_adds_no_argument_at_all()
    test_stg_on_passes_exactly_the_two_upstream_arguments()
    test_stg_without_blocks_is_refused_before_any_weight_loads()
    test_the_stg_flags_default_to_off_on_the_command_line()
    with tempfile.TemporaryDirectory() as td:
        test_a_weight_file_is_judged_by_its_content_and_not_its_length(td)
    with tempfile.TemporaryDirectory() as td:
        test_the_checks_that_passed_this_defect_still_pass_it(td)
    with tempfile.TemporaryDirectory() as td:
        test_an_empty_or_missing_cache_is_not_a_pass(td)
    with tempfile.TemporaryDirectory() as td:
        test_only_content_addressed_blobs_are_compared_to_their_names(td)
    test_a_latent_that_never_contracted_is_reported_as_noise()
    test_the_worker_refuses_before_it_loads_a_model()

    # AND A DECISION THAT MOVED MUST REACH THE THING THAT ACTUALLY RUNS.
    with tempfile.TemporaryDirectory() as td:
        test_an_approval_filed_only_in_the_inbox_is_the_failure_it_names(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_dated_correction_beside_the_superseded_text_is_accepted(td)
    with tempfile.TemporaryDirectory() as td:
        test_an_unresolved_decision_is_not_a_finding(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_stale_block_inside_a_list_row_is_found_too(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_correction_written_into_the_row_clears_it(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_plate_prompt_that_contradicts_the_cast_is_caught(td)
    with tempfile.TemporaryDirectory() as td:
        test_the_same_word_is_canon_for_the_goblin_and_stays_silent(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_known_contradiction_named_in_a_record_does_not_fail_the_build(td)
    with tempfile.TemporaryDirectory() as td:
        test_an_acknowledgement_no_record_backs_is_itself_a_failure(td)
    with tempfile.TemporaryDirectory() as td:
        test_an_acknowledgement_that_matches_nothing_must_be_pruned(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_canon_no_render_has_ever_used_is_reported(td)
    with tempfile.TemporaryDirectory() as td:
        test_one_render_carrying_the_canon_clears_it(td)
    with tempfile.TemporaryDirectory() as td:
        test_no_render_evidence_at_all_is_an_abstention_not_a_pass(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_canon_no_draft_carries_cannot_be_called_unrendered(td)
    with tempfile.TemporaryDirectory() as td:
        test_prompts_that_contradict_each_other_are_caught_with_no_canon_at_all(td)
    with tempfile.TemporaryDirectory() as td:
        test_one_reading_only_is_not_a_contradiction(td)
    with tempfile.TemporaryDirectory() as td:
        test_writing_the_canon_down_is_what_silences_the_axis(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_banned_term_in_a_negative_block_is_not_an_assertion_of_it(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_prompt_that_lives_only_in_a_job_payload_is_read(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_negative_payload_file_is_never_read_as_a_request(td)
    with tempfile.TemporaryDirectory() as td:
        test_posture_words_are_not_read_as_height_claims(td)
    with tempfile.TemporaryDirectory() as td:
        test_an_empty_corpus_is_not_a_clean_repo(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_register_whose_evidence_vanished_fails_on_itself(td)
    with tempfile.TemporaryDirectory() as td:
        test_the_register_is_verified_by_content_and_not_by_the_file_existing(td)
    with tempfile.TemporaryDirectory() as td:
        test_no_register_at_all_is_an_abstention(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_resolved_decision_no_subject_covers_is_named_not_ignored(td)
    test_it_reads_the_real_repo_corpora_and_not_an_empty_set()
    with tempfile.TemporaryDirectory() as td:
        test_a_spec_the_ledger_records_as_run_is_history_not_pending(td)
    with tempfile.TemporaryDirectory() as td:
        test_the_same_spec_unfired_is_reported(td)
    with tempfile.TemporaryDirectory() as td:
        test_a_pruned_farm_out_no_longer_manufactures_unrun(td)
    with tempfile.TemporaryDirectory() as td:
        test_without_a_ledger_it_abstains_instead_of_guessing(td)
    with tempfile.TemporaryDirectory() as td:
        test_an_acknowledgement_for_a_fired_receipt_is_surplus_not_stale(td)
    test_the_real_ledger_is_read_and_is_not_empty()
    for _t in (test_one_beats_bar_recorded_on_another_beats_spec_fails,
               test_a_cross_beat_bar_no_entry_rules_on_is_review_and_never_fail,
               test_a_bar_the_register_calls_shared_is_silent,
               test_an_entry_that_rules_neither_way_abstains_instead_of_passing,
               test_a_dated_correction_sibling_takes_the_spec_out_of_the_group,
               test_a_bars_entry_no_spec_carries_any_more_is_stale_and_fails,
               test_an_excused_spec_is_quiet_while_its_record_still_backs_it,
               test_an_excuse_the_record_no_longer_carries_stops_excusing,
               test_the_bar_rule_reaches_the_real_exit_code_and_not_just_the_function,
               test_a_second_card_carrying_one_ruling_counts_as_covered,
               test_without_also_records_the_second_card_is_reported_uncovered,
               test_an_evidence_string_alive_only_inside_a_strike_fails,
               test_the_live_prose_that_replaced_it_still_passes,
               test_a_blockquote_is_not_a_corpse,
               test_a_strike_spanning_several_quoted_lines_is_removed_whole,
               test_removing_a_strike_cannot_join_words_across_the_gap,
               test_unbalanced_strike_markers_abstain_rather_than_guess,
               test_a_string_that_is_simply_gone_keeps_the_older_message,
               test_the_struck_evidence_gate_reaches_the_real_exit_code):
        with tempfile.TemporaryDirectory() as td:
            _t(td)
    test_the_real_register_has_no_assertion_living_on_dead_text()
    test_a_corrected_gate_never_reaches_the_queue_page_uncorrected()
    test_a_lifted_block_and_a_wrong_success_bar_cannot_reach_the_ledger()
    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all pipeline tests passed")
    return 0



# ══════════════════════════════════════════════════════════════════════════════
# AND A DECISION THAT MOVED MUST REACH THE THING THAT ACTUALLY RUNS.
#
# Five separate multi-day losses in two days, all the same shape: the canon moved
# and the artifact that runs did not. Every test below is a SYNTHETIC
# RECONSTRUCTION of one of them — the check has to fire on the repo as it was on
# the day, and go quiet on the repo as it was after the fix. A check that has only
# ever been run against already-corrected files has proved nothing.
# ══════════════════════════════════════════════════════════════════════════════

import check_canon_drift as ccd


def _fixture(td, *, inbox=None, register=None, drafts=None, records=None,
             sidecars=None, jobs=None, ran=None, ledger=True):
    """Write the smallest tree check_canon_drift can read. Returns the root.

    `ran` lists task names the run ledger records as fired; `ledger=False` writes
    no ledger at all, which must make the checker abstain rather than treat every
    spec as pending.
    """
    root = Path(td)
    if ledger:
        (root / "pipeline" / "measured").mkdir(parents=True, exist_ok=True)
        (root / "pipeline" / "measured" / "queue-history.json").write_text(
            json.dumps({"jobs": [{"task": t, "spec_file": f"pipeline/jobs/{t}.yaml", "rc": "0"}
                                 for t in (ran or [])]}), encoding="utf-8")
    (root / "review").mkdir(parents=True, exist_ok=True)
    (root / "pipeline").mkdir(parents=True, exist_ok=True)
    (root / "review" / "inbox.yaml").write_text(inbox or "[]\n", encoding="utf-8")
    (root / "pipeline" / "canon.yaml").write_text(register or "subjects: []\n", encoding="utf-8")
    if drafts is not None:
        (root / "pipeline" / "wave-drafts.yaml").write_text(drafts, encoding="utf-8")
    for name, body in (records or {}).items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    for name, body in (sidecars or {}).items():
        p = root / "farm-out" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    for name, body in (jobs or {}).items():
        p = root / "pipeline" / "jobs" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return root


def _fails(findings, rule=None):
    return [f for f in findings
            if f.level == ccd.FAIL and (rule is None or f.rule == rule)]


# --- INSTANCE 1: the guard cast --------------------------------------------
# 2026-08-14/15 the founder cast both guards. The approval reached
# review/inbox.yaml and nowhere else, and four beats stayed blocked for a day.

_INBOX_GUARDS_RESOLVED = """
- what: THE TWO GUARDS ARE ALREADY YOURS
  url: /review/ep2-picks/sheets/guard-cast-0816.jpg
  resolved:
    date: '2026-08-16'
    verdict: THE CAST STANDS AS DRAWN. guard A and guard B exactly as drawn.
"""

_REG_GUARD_CAST = """
records:
  structured: [records/done-definitions.yaml]
  prose: []
subjects:
- id: ep2-guard-cast
  kind: founder_decision
  resolved_by:
    card_url_contains: sheets/guard-cast-0816.jpg
    verdict_matches: THE CAST STANDS AS DRAWN
  evidence:
    file: review/inbox.yaml
    contains: THE CAST STANDS AS DRAWN
  open_phrases:
  - animat\\w* guard beats off an unapproved cast
  - guard cast unapproved
  negation_cues:
  - CORRECTION
  - no longer
"""

_RECORD_STILL_BLOCKED = """
guards:
  rule: Do not cast them and do not animate guard beats off an unapproved cast.
"""

_RECORD_CORRECTED = _RECORD_STILL_BLOCKED + """
guards_CORRECTION_0816: >-
  CORRECTION, 2026-08-16. The rule above is left standing; the cast is approved.
"""


def test_an_approval_filed_only_in_the_inbox_is_the_failure_it_names(td):
    root = _fixture(td, inbox=_INBOX_GUARDS_RESOLVED, register=_REG_GUARD_CAST,
                    records={"records/done-definitions.yaml": _RECORD_STILL_BLOCKED})
    f = _fails(ccd.run(root), "resolved_but_open")
    check("a record still calling a resolved decision open FAILS", len(f) == 1)
    check("the finding names the record and the key path",
          bool(f) and f[0].where.endswith("done-definitions.yaml:guards.rule"))
    check("the finding prints the date the founder actually answered",
          bool(f) and "2026-08-16" in f[0].detail)


def test_a_dated_correction_beside_the_superseded_text_is_accepted(td):
    root = _fixture(td, inbox=_INBOX_GUARDS_RESOLVED, register=_REG_GUARD_CAST,
                    records={"records/done-definitions.yaml": _RECORD_CORRECTED})
    check("superseded text under a dated *_CORRECTION_MMDD sibling is quiet",
          _fails(ccd.run(root), "resolved_but_open") == [])


def test_an_unresolved_decision_is_not_a_finding(td):
    root = _fixture(td, inbox="- what: THE TWO GUARDS\n  url: /review/ep2-picks/sheets/guard-cast-0816.jpg\n",
                    register=_REG_GUARD_CAST,
                    records={"records/done-definitions.yaml": _RECORD_STILL_BLOCKED})
    out = ccd.run(root)
    check("a record blocking on a still-OPEN question is correct, not a fault",
          _fails(out, "resolved_but_open") == [])
    check("and the checker says why it abstained rather than passing silently",
          any(f.level == ccd.UNKNOWN and "still open" in f.detail for f in out))


# --- INSTANCE 4: the six gate-evidence rows --------------------------------
# Found 2026-08-16 in review/ep2-picks/gate-evidence.yaml: six list rows reading
# `gate: GATED - guard cast unapproved (his call)` for beats 05/06/07/09/10/11,
# with no correction in the file. The FOURTH record asserting the same stale
# block, found by the fourth separate lane — which is the argument for a check
# and not a habit. This one lives in a LIST, not under a mapping key.

_GATE_EVIDENCE_STALE = """
beats:
- beat: '05'
  gate: GATED - guard cast unapproved (his call)
- beat: '06'
  gate: GATED - guard cast unapproved (his call)
- beat: '08'
  gate: ships under the two-round rule
"""

_GATE_EVIDENCE_FIXED = """
beats:
- beat: '05'
  gate: GATED - guard cast unapproved (his call)
  gate_CORRECTION_0816: 'CORRECTION, 2026-08-16: cast approved, gate discharged.'
- beat: '06'
  gate: GATED - guard cast unapproved (his call)
  gate_CORRECTION_0816: 'CORRECTION, 2026-08-16: cast approved, gate discharged.'
"""


def test_a_stale_block_inside_a_list_row_is_found_too(td):
    root = _fixture(td, inbox=_INBOX_GUARDS_RESOLVED, register=_REG_GUARD_CAST,
                    records={"records/done-definitions.yaml": _GATE_EVIDENCE_STALE})
    f = _fails(ccd.run(root), "resolved_but_open")
    check("both stale list rows are reported, the passing row is not", len(f) == 2)
    check("the finding locates the row by index, not just the file",
          bool(f) and "beats.[0].gate" in f[0].where)


def test_a_correction_written_into_the_row_clears_it(td):
    root = _fixture(td, inbox=_INBOX_GUARDS_RESOLVED, register=_REG_GUARD_CAST,
                    records={"records/done-definitions.yaml": _GATE_EVIDENCE_FIXED})
    check("a dated correction inside the row silences it",
          _fails(ccd.run(root), "resolved_but_open") == [])


# --- INSTANCE 2: `bald` ----------------------------------------------------
# The sheets moved off bald on 08-12; 22 guard-beat prompts still ask for it, and
# beat 11's "identity collapse — the bald scalp fills in with dark hair" was the
# render drifting TOWARD the approved cast, filed as a defect.
#
# THE DISCRIMINATOR THIS FIXTURE EXISTS FOR: `bald` is CANON for the goblin (272
# rendered prompts) and the DEFECT for the guards (84). No word-level rule can
# tell those apart. The goblin draft below must stay silent.

_DRAFTS_BALD = """
beats:
  11:
    kind: guard
    authored_b11_idfix: >-
      2boys, two round bald guard men in plain brown tunics walk away from camera
  20:
    kind: goblin
    authored_b20_idfix_r2: >-
      A small goblin boy, green skin, bald head, patchwork cloak, raises a ripe fig
"""

_REG_GUARD_HAIR = """
records: {structured: [], prose: []}
subjects:
- id: ep2-guard-hair
  kind: prompt_canon
  since: '2026-08-12'
  evidence: {file: pipeline/wave-drafts.yaml, contains: 'two round bald guard men'}
  scope:
    beats: [11]
    prompt_mentions: \\bguards?\\b
  forbids: ['\\bbald\\b']
"""

_REG_GUARD_HAIR_ACK = _REG_GUARD_HAIR + """
  acknowledged:
    recorded_in: records/known.yaml
    recorded_contains: guards_CORRECTION_0816
    variants: [authored_b11_idfix]
"""


def test_a_plate_prompt_that_contradicts_the_cast_is_caught(td):
    root = _fixture(td, register=_REG_GUARD_HAIR, drafts=_DRAFTS_BALD)
    f = _fails(ccd.run(root), "prompt_contradicts_canon")
    check("a guard plate still asking for bald FAILS", len(f) == 1)
    check("it names the beat and the variant that would be sent",
          bool(f) and "b11:authored_b11_idfix" in f[0].where)


def test_the_same_word_is_canon_for_the_goblin_and_stays_silent(td):
    root = _fixture(td, register=_REG_GUARD_HAIR, drafts=_DRAFTS_BALD)
    hits = [f for f in ccd.run(root) if "b20" in f.where]
    check("`bald` on the goblin beat is canon and is NOT reported", hits == [])


def test_a_known_contradiction_named_in_a_record_does_not_fail_the_build(td):
    root = _fixture(td, register=_REG_GUARD_HAIR_ACK, drafts=_DRAFTS_BALD,
                    records={"records/known.yaml": "guards_CORRECTION_0816: recorded 2026-08-16\n"})
    out = ccd.run(root)
    check("an acknowledged historical draft is ACK, not FAIL",
          _fails(out, "prompt_contradicts_canon") == []
          and any(f.level == ccd.ACK for f in out))


def test_an_acknowledgement_no_record_backs_is_itself_a_failure(td):
    root = _fixture(td, register=_REG_GUARD_HAIR_ACK, drafts=_DRAFTS_BALD,
                    records={"records/known.yaml": "something_else: nothing to do with it\n"})
    check("a suppression list no record backs FAILS instead of silencing",
          len(_fails(ccd.run(root), "acknowledgement_unrecorded")) == 1)


def test_an_acknowledgement_that_matches_nothing_must_be_pruned(td):
    reg = _REG_GUARD_HAIR + """
  acknowledged:
    recorded_in: records/known.yaml
    recorded_contains: guards_CORRECTION_0816
    variants: [authored_b11_idfix, authored_a_variant_that_no_longer_exists]
"""
    root = _fixture(td, register=reg, drafts=_DRAFTS_BALD,
                    records={"records/known.yaml": "guards_CORRECTION_0816: recorded\n"})
    check("a stale acknowledgement FAILS so the list prunes itself",
          len(_fails(ccd.run(root), "stale_acknowledgement")) == 1)


# --- INSTANCE 3: purple ----------------------------------------------------
# The purple canon landed 08-13/14 into three beat-20 drafts. NO render ever
# produced a frame from any of them, so the 08-15 colour sheet asked the founder
# to rule on 08-12 frames whose prompt contains no colour word at all. He rejected
# a colour the beat was never asked for.

_DRAFTS_PURPLE = """
beats:
  20:
    kind: goblin
    authored_b20_plate: >-
      A small goblin boy, green skin, raises a deep purple-violet fig in both hands
    authored_b20_idfix_r2: >-
      A small goblin boy, green skin, raises a ripe fig in both hands like evidence
"""

_SIDECAR_OLD = """platform: local-gpu (rtx5090)
shot_beat: 20
draft_variant: authored_b20_idfix_r2
prompt: >-
  A small goblin boy, green skin, raises a ripe fig in both hands like evidence
"""

_SIDECAR_PURPLE = """platform: local-gpu (rtx5090)
shot_beat: 20
draft_variant: authored_b20_plate
prompt: >-
  A small goblin boy, green skin, raises a deep purple-violet fig in both hands
"""

_REG_PURPLE = """
records: {structured: [], prose: []}
subjects:
- id: ep2-fig-purple
  kind: prompt_canon
  since: '2026-08-13'
  evidence: {file: pipeline/wave-drafts.yaml, contains: 'deep purple-violet fig'}
  scope: {beats: [20], prompt_mentions: '\\bfigs?\\b'}
  requires_any: [purple]
  must_have_run: true
"""


def test_a_canon_no_render_has_ever_used_is_reported(td):
    root = _fixture(td, register=_REG_PURPLE, drafts=_DRAFTS_PURPLE,
                    sidecars={"ep2-b20-idfix-r2/20-evidence-s0.yaml": _SIDECAR_OLD})
    f = _fails(ccd.run(root), "canon_never_ran")
    check("a canon in the drafts and in zero rendered prompts FAILS", len(f) == 1)
    check("it says how many frames were drawn without it",
          bool(f) and "ZERO of the 1 rendered prompts" in f[0].detail)


def test_one_render_carrying_the_canon_clears_it(td):
    root = _fixture(td, register=_REG_PURPLE, drafts=_DRAFTS_PURPLE,
                    sidecars={"ep2-b20-idfix-r2/20-evidence-s0.yaml": _SIDECAR_OLD,
                              "ep2-b20-plate-0814/20-evidence-s0.yaml": _SIDECAR_PURPLE})
    check("one frame actually rendered from the canon silences it",
          _fails(ccd.run(root), "canon_never_ran") == [])


def test_no_render_evidence_at_all_is_an_abstention_not_a_pass(td):
    root = _fixture(td, register=_REG_PURPLE, drafts=_DRAFTS_PURPLE)
    out = ccd.run(root)
    check("with no sidecars to read it says CANNOT TELL, never 'clean'",
          _fails(out, "canon_never_ran") == []
          and any(f.level == ccd.UNKNOWN and f.rule == "canon_never_ran" for f in out))


def test_a_canon_no_draft_carries_cannot_be_called_unrendered(td):
    drafts = _DRAFTS_PURPLE.replace("deep purple-violet fig", "ripe fig")
    root = _fixture(td, register=_REG_PURPLE, drafts=drafts,
                    sidecars={"a/20-s0.yaml": _SIDECAR_OLD})
    out = ccd.run(root)
    check("'never written' is distinguished from 'never rendered'",
          any(f.level == ccd.UNKNOWN and "never written" in f.detail for f in out))


# --- THE FIFTH SHAPE: an attribute nothing ever defined --------------------
# The sapling is in twelve of twenty-one beats and never had a canonical
# description, so twelve beats improvised one in opposite directions. This is
# instance 2's shape with no canon to contradict.

_DRAFTS_SAPLING = """
beats:
  1:
    kind: guard
    authored_b01_figref: >-
      A tiny sapling, two oversized wide oval cotyledon leaves, in a grassy field
    authored_b01_figleaf: >-
      A tiny sapling in a sunlit grassy field, deeply lobed fig leaves with five fingers
"""

_REG_AXIS = """
records: {structured: [], prose: []}
subjects: []
axes:
- id: sapling-leaf-shape
  must_be_pinned: true
  scope: {prompt_mentions: '\\bsapling\\b'}
  values:
    wide-oval-cotyledon: ['\\boval\\b', '\\bcotyledon']
    deeply-lobed-fig: ['\\blobed\\b', 'five fingers']
"""


def test_prompts_that_contradict_each_other_are_caught_with_no_canon_at_all(td):
    root = _fixture(td, register=_REG_AXIS, drafts=_DRAFTS_SAPLING)
    f = _fails(ccd.run(root), "attribute_unpinned")
    check("an attribute two prompts describe oppositely FAILS", len(f) == 1)
    check("and it names the beat carrying BOTH readings",
          bool(f) and "b01 carry BOTH" in f[0].detail)


def test_one_reading_only_is_not_a_contradiction(td):
    drafts = _DRAFTS_SAPLING.replace(
        "deeply lobed fig leaves with five fingers", "wide oval cotyledon leaves")
    root = _fixture(td, register=_REG_AXIS, drafts=drafts)
    out = ccd.run(root)
    check("agreement is not reported as disagreement",
          _fails(out, "attribute_unpinned") == [])
    check("and a single asserted value is an abstention, not proof of a canon",
          any(f.level == ccd.UNKNOWN and f.rule == "attribute_unpinned" for f in out))


def test_writing_the_canon_down_is_what_silences_the_axis(td):
    reg = _REG_AXIS.replace("subjects: []", """subjects:
- id: sapling-leaves
  kind: prompt_canon
  since: '2026-08-16'
  pins_axis: sapling-leaf-shape
  evidence: {file: pipeline/wave-drafts.yaml, contains: 'wide oval cotyledon leaves'}
""")
    root = _fixture(td, register=reg, drafts=_DRAFTS_SAPLING)
    check("pinning the attribute in the register clears the axis",
          _fails(ccd.run(root), "attribute_unpinned") == [])


def test_a_banned_term_in_a_negative_block_is_not_an_assertion_of_it(td):
    drafts = """
beats:
  1:
    kind: goblin
    authored_b01_x: >-
      A tiny sapling with deeply lobed fig leaves. No oval leaves, no cotyledon leaves.
"""
    root = _fixture(td, register=_REG_AXIS, drafts=drafts)
    check("`no oval leaves` asserts the opposite and is not counted as a clash",
          _fails(ccd.run(root), "attribute_unpinned") == [])


# --- THE BLIND SPOT: prompts that live in job payloads ---------------------
# The first cut read wave-drafts.yaml and `--variant` argv only. Both of
# 2026-08-16's headline violations live in job-spec `payload:` prompt text and
# were invisible: `TALLER THAN HE IS` in six beat-15 specs, `ONE SINGLE ROUND
# GREEN FIG` in three — neither phrase is in wave-drafts.yaml at all.

_JOB_WITH_PAYLOAD = """id: ep2-b15-leafB-0813
beat: 15
payload:
  C:\\banyan-farm\\x\\b15-motion-prompt.txt: 'A SINGLE SMALL SAPLING STANDS BESIDE HIM, one slender stem with two big leaves, taller than he is.'
  C:\\banyan-farm\\x\\b15-negative.txt: 'pointed leaves, lance-shaped leaves, taller than he is'
"""

_REG_HEIGHT = """
records: {structured: [], prose: []}
subjects: []
axes:
- id: sapling-height
  must_be_pinned: true
  scope: {prompt_mentions: '\\bsapling\\b'}
  values:
    above-the-goblin: ['taller than he is']
    below-the-goblin: ['no taller than', 'knee[- ]high']
"""


def test_a_prompt_that_lives_only_in_a_job_payload_is_read(td):
    # `ran=[]` — the ledger exists and does not list this spec, so it is pending.
    drafts = """
beats:
  12:
    kind: guard
    authored_b12_scene: >-
      A tiny sapling no taller than the grass in an open field
"""
    root = _fixture(td, register=_REG_HEIGHT, drafts=drafts, jobs={"j.yaml": _JOB_WITH_PAYLOAD})
    f = _fails(ccd.run(root), "attribute_unpinned")
    check("a payload-only prompt is compared against the canon", len(f) == 1)
    check("and the finding names the spec and the payload file it came from",
          bool(f) and "jobs/j:b15-motion-prompt.txt" in f[0].detail)


def test_a_negative_payload_file_is_never_read_as_a_request(td):
    job = _JOB_WITH_PAYLOAD.replace(
        "one slender stem with two big leaves, taller than he is.", "one slender stem.")
    root = _fixture(td, register=_REG_HEIGHT, drafts="beats:\n", jobs={"j.yaml": job})
    prompts = ccd.read_job_payload_prompts(str(Path(td)))
    check("only the prompt file is taken from the payload", len(prompts) == 1)
    check("the negative file's banned terms are not read as assertions",
          all("lance-shaped" not in p for _, _, p in prompts))


def test_posture_words_are_not_read_as_height_claims(td):
    # `standing tall` is in 17 prompts and is POSTURE. The sapling lane's own
    # judgement: forbidding it would fire seventeen times for no defect.
    drafts = """
beats:
  15:
    kind: goblin
    authored_b15_idfix: >-
      a tiny sapling standing tall beside him, its two oversized leaves above him
"""
    root = _fixture(td, register=_REG_HEIGHT, drafts=drafts)
    check("`standing tall` is not counted as a height assertion",
          _fails(ccd.run(root), "attribute_unpinned") == [])


# --- AND THE FAILURE MODE THAT PASSED A WEIGHTS MANIFEST FULL OF HOLES -----

def test_an_empty_corpus_is_not_a_clean_repo(td):
    # A register that still asserts a canon, and a prompt corpus that has gone
    # empty underneath it. The one answer that must never come back is "clean":
    # the weights manifest that passed blobs full of holes did exactly that.
    root = _fixture(td, register=_REG_PURPLE, drafts="beats:\n")
    out = ccd.run(root)
    check("an empty corpus never reports all-clear", out != [])
    check("it fails on the register's own evidence rather than on nothing",
          len(_fails(out, "register_evidence_missing")) == 1)
    check("and it abstains on the rule it can no longer evaluate",
          any(f.level == ccd.UNKNOWN and f.rule == "canon_never_ran" for f in out))


def test_a_register_whose_evidence_vanished_fails_on_itself(td):
    root = _fixture(td, register=_REG_PURPLE,
                    drafts="beats:\n  20:\n    kind: goblin\n    authored: >-\n      a ripe fig\n")
    f = _fails(ccd.run(root), "register_evidence_missing")
    check("a register asserting a canon its own source no longer carries FAILS",
          len(f) == 1)


def test_the_register_is_verified_by_content_and_not_by_the_file_existing(td):
    root = _fixture(td, register=_REG_PURPLE, drafts=_DRAFTS_PURPLE,
                    sidecars={"a/20-s0.yaml": _SIDECAR_PURPLE})
    check("evidence present in the named file passes",
          _fails(ccd.run(root), "register_evidence_missing") == [])


def test_no_register_at_all_is_an_abstention(td):
    root = Path(td)
    (root / "review").mkdir(parents=True, exist_ok=True)
    (root / "review" / "inbox.yaml").write_text("[]\n", encoding="utf-8")
    out = ccd.run(root)
    check("a missing register says so rather than passing",
          _fails(out) == [] and any(f.rule == "register" for f in out))


def test_a_resolved_decision_no_subject_covers_is_named_not_ignored(td):
    root = _fixture(td, inbox=_INBOX_GUARDS_RESOLVED, register="subjects: []\n")
    out = ccd.run(root)
    check("the register's own blind spots are reported as CANNOT TELL",
          any(f.rule == "unregistered_decision" and f.level == ccd.UNKNOWN for f in out))


def test_it_reads_the_real_repo_corpora_and_not_an_empty_set():
    # The lesson of the weights manifest that passed files full of holes, and of
    # the status payload that reported `ready: 0` against a real 3: a check that
    # silently reads nothing reports a clean repo. These are content floors.
    # FLOORS ARE SET AGAINST WHAT IS TRACKED, not against this laptop. The first
    # cut asserted 400+ render sidecars and went red in CI, because 456 of the 509
    # sidecars here live in an UNTRACKED farm-out/ and a checkout sees 53. That is
    # the same defect the floors exist to catch, one level up.
    drafts = ccd.read_draft_variants((REPO / "pipeline" / "wave-drafts.yaml").read_text())
    payloads = ccd.read_job_payload_prompts(str(REPO))
    sidecars = ccd.read_run_evidence(str(REPO))
    ledger = ccd.read_ledger_prompts(str(REPO))
    check("wave-drafts yields the authored prompt corpus", len(drafts) > 150)
    check("job payloads yield a prompt corpus of their own", len(payloads) > 300)
    check("tracked render sidecars under review/ are found", len(sidecars) > 40)
    # 331 of the ledger's 573 rows carry a prompt; the rest are runs whose prompt
    # was never recorded, and the floor is set under the real number, not the
    # row count, so it measures what the reader actually returns.
    check("the tracked ledger supplies the render evidence CI can actually see",
          len(ledger) > 250)
    check("render evidence is the union of both, so neither alone decides",
          len(sidecars + ledger) > len(ledger))
    check("every prompt read is non-empty text",
          all(p.strip() for _, _, p in drafts + payloads)
          and all(p.strip() for _, _, _, p in ledger))


# --- AND THE CHECK MUST KNOW WHAT HAS ACTUALLY RUN -------------------------
# Both false-positive rounds this check has had came from guessing run status off
# the filesystem: farm-out/ alone missed sidecars under review/, and farm-out IS
# PRUNED, so age alone manufactured "unrun" for two specs sitting in the ledger at
# rc=0. pipeline/measured/queue-history.json is the authority.

_JOB_FIRED = """id: ep2-b18-old-0812
beat: 18
payload:
  C:\\x\\b18-motion-prompt.txt: 'A tiny sapling with ONE SINGLE ROUND GREEN FIG hanging from it.'
steps:
- name: sample
  argv:
  - python
  - --variant
  - authored_b18_old
"""

_REG_GREEN = """
records: {structured: [], prose: []}
subjects:
- id: fig-not-green
  kind: prompt_canon
  since: '2026-08-13'
  evidence: {file: pipeline/jobs/ep2-b18-old-0812.yaml, contains: 'ONE SINGLE ROUND GREEN FIG'}
  scope: {beats: [18], prompt_mentions: '\\bfigs?\\b'}
  forbids: ['green fig']
"""


def test_a_spec_the_ledger_records_as_run_is_history_not_pending(td):
    root = _fixture(td, register=_REG_GREEN, drafts="beats:\n",
                    jobs={"ep2-b18-old-0812.yaml": _JOB_FIRED},
                    ran=["ep2-b18-old-0812"])
    out = ccd.run(root)
    check("a fired receipt is not re-reported as a canon violation",
          _fails(out, "prompt_contradicts_canon") == [])
    check("and it is not reported as an unrun job either",
          _fails(out, "unrun_job_against_canon") == [])


def test_the_same_spec_unfired_is_reported(td):
    root = _fixture(td, register=_REG_GREEN, drafts="beats:\n",
                    jobs={"ep2-b18-old-0812.yaml": _JOB_FIRED}, ran=[])
    f = _fails(ccd.run(root))
    check("a spec the ledger has never seen IS compared against canon", len(f) >= 1)
    check("and the violation names the payload prompt",
          any("b18-motion-prompt.txt" in x.detail or "b18-motion-prompt.txt" in x.where
              for x in f))


def test_a_pruned_farm_out_no_longer_manufactures_unrun(td):
    # The exact 2026-08-16 defect: ep2-b18-plantneg-0812 and ep2-b18-refresh-0811
    # were FAILed as un-fired because farm-out had been pruned, while both sit in
    # the ledger at rc=0.
    root = _fixture(td, register=_REG_GREEN, drafts="beats:\n",
                    jobs={"ep2-b18-old-0812.yaml": _JOB_FIRED},
                    ran=["ep2-b18-old-0812"])
    check("no farm-out directory at all, and the ledger still settles it",
          not (Path(td) / "farm-out").exists()
          and _fails(ccd.run(root), "unrun_job_against_canon") == [])


def test_without_a_ledger_it_abstains_instead_of_guessing(td):
    root = _fixture(td, register=_REG_GREEN, drafts="beats:\n",
                    jobs={"ep2-b18-old-0812.yaml": _JOB_FIRED}, ledger=False)
    out = ccd.run(root)
    check("with no run ledger it judges no payload at all",
          _fails(out, "prompt_contradicts_canon") == [])
    check("and it says so, naming how many prompts it declined to judge",
          any(f.rule == "run_status" and f.level == ccd.UNKNOWN for f in out))


def test_an_acknowledgement_for_a_fired_receipt_is_surplus_not_stale(td):
    reg = _REG_GREEN + """
  acknowledged:
    recorded_in: records/known.yaml
    recorded_contains: noted_0816
    variants: ['jobs/ep2-b18-old-0812:b18-motion-prompt.txt']
"""
    root = _fixture(td, register=reg, drafts="beats:\n",
                    jobs={"ep2-b18-old-0812.yaml": _JOB_FIRED}, ran=["ep2-b18-old-0812"],
                    records={"records/known.yaml": "noted_0816: recorded\n"})
    out = ccd.run(root)
    check("a suppression whose prompt has fired is ACK surplus, not a FAIL",
          _fails(out, "stale_acknowledgement") == []
          and any(f.rule == "acknowledgement_no_longer_needed" for f in out))


def test_the_real_ledger_is_read_and_is_not_empty():
    tasks, specs, ok = ccd.read_run_ledger(str(REPO))
    check("the run ledger parses", ok)
    check("it carries the real completed-run population", len(tasks) > 200)
    check("the two specs that were wrongly called un-fired are in it",
          {"ep2-b18-plantneg-0812", "ep2-b18-refresh-0811"} <= (tasks | specs))


# --- INSTANCE 5: one beat's judging bar recorded on another beat's spec -----
# THE LOSS, 2026-08-14/16. The ALL-21 wave was authored by copying one spec and
# the paste went past the wave: 80 specs carried beat 02's `success` line and 13
# of them are beat 02. queue_history.py copies `success` into the ledger's
# `purpose`, so 352 rows published "a LEAN ADULT goblin sprints in…" as the bar
# for clips of beats that do no such thing, and /queue showed it.
#
# rule_bar_serves_two_beats and `also_records:` LANDED UNTESTED in 6bb283f3 —
# recovered whole from a lane that died on 2026-08-15 before it could write
# these. Rules 1-4 are mutation-proofed and this rule was not, which put it
# outside the only thing that keeps this file honest. Each assertion below was
# run against a deliberately broken copy of check_canon_drift.py and observed
# to go RED; the breakage each one catches is named beside it.
_BAR = "a LEAN ADULT goblin sprints in, skids and dives behind a sapling"

_SPECS_TWO_BEATS = {
    "ep2-b02-sprint-0814.yaml": f"beat: 2\nsuccess: {_BAR}\n",
    "ep2-b16-fig-0814.yaml": f"beat: 16\nsuccess: {_BAR}\n",
}

_REG_BAR_OWNED = f"""
records:
  structured: []
  prose: []
subjects: []
bar_fields: [success]
bars:
- id: ep2-b02-sprint-bar
  field: success
  contains: {_BAR}
  owned_by_beat: 2
"""

_REG_BAR_ACK = _REG_BAR_OWNED + """  acknowledged:
    specs: [ep2-b16-fig-0814]
    recorded_in: records/known.yaml
    recorded_contains: beat 16 keeps the paste until it re-renders
"""


def test_one_beats_bar_recorded_on_another_beats_spec_fails(td):
    # RED when: the FAIL branch is removed, or the call site at run() is unwired.
    root = _fixture(td, register=_REG_BAR_OWNED, jobs=_SPECS_TWO_BEATS)
    f = _fails(ccd.run(root), "bar_serves_two_beats")
    check("a spec carrying another beat's recorded bar FAILS", len(f) == 1)
    check("and it is the NON-owner spec that is named — the owner's is correct",
          bool(f) and f[0].where == "pipeline/jobs/ep2-b16-fig-0814.yaml")
    check("the finding says which beat the bar belongs to",
          bool(f) and "beat 2's bar" in f[0].detail)


def test_a_cross_beat_bar_no_entry_rules_on_is_review_and_never_fail(td):
    # RED when: the REVIEW branch is promoted to FAIL. 13 groups on this repo
    # span beats and only ONE is the defect; failing all 13 is 8% precision, the
    # cry-wolf shape that got the runner watchdog switched off.
    root = _fixture(td, register="records:\n  structured: []\n  prose: []\nsubjects: []\n",
                    jobs=_SPECS_TWO_BEATS)
    out = ccd.run(root)
    check("an unadjudicated collision is never a FAIL",
          _fails(out, "bar_serves_two_beats") == [])
    check("but it is reported at REVIEW, so the register can rule on it",
          any(f.level == ccd.REVIEW and f.rule == "bar_serves_two_beats" for f in out))


def test_a_bar_the_register_calls_shared_is_silent(td):
    # RED when: `shared: true` stops short-circuiting. A wave has ONE bar across
    # twenty beats when it is written wave-wide on purpose.
    reg = _REG_BAR_OWNED.replace("  owned_by_beat: 2\n", "  shared: true\n")
    root = _fixture(td, register=reg, jobs=_SPECS_TWO_BEATS)
    check("a deliberately wave-wide bar produces no finding of any level",
          [f for f in ccd.run(root) if f.rule == "bar_serves_two_beats"] == [])


def test_an_entry_that_rules_neither_way_abstains_instead_of_passing(td):
    # RED when: a bars entry with no verdict falls through silently.
    reg = _REG_BAR_OWNED.replace("  owned_by_beat: 2\n", "")
    root = _fixture(td, register=reg, jobs=_SPECS_TWO_BEATS)
    out = ccd.run(root)
    check("an entry with neither owned_by_beat nor shared is CANNOT TELL, not a pass",
          _fails(out, "bar_serves_two_beats") == []
          and any(f.level == ccd.UNKNOWN and f.rule == "bar_serves_two_beats" for f in out))


def test_a_dated_correction_sibling_takes_the_spec_out_of_the_group(td):
    # RED when: _bar_groups stops consulting correction_sibling. A spec that has
    # already written its own dated correction must not be failed for it again.
    jobs = dict(_SPECS_TWO_BEATS)
    jobs["ep2-b16-fig-0814.yaml"] += (
        "success_CORRECTION_0817: >-\n"
        "  CORRECTION, 2026-08-17. beat 16 is the fig; the line above is beat 02's bar.\n")
    root = _fixture(td, register=_REG_BAR_OWNED, jobs=jobs)
    check("a spec that records its own dated correction is quiet",
          _fails(ccd.run(root), "bar_serves_two_beats") == [])


def test_a_bars_entry_no_spec_carries_any_more_is_stale_and_fails(td):
    # RED when: the trailing matched_entries sweep is dropped. A register that
    # cannot go stale is the whole point — this is the fourth stale-record loss.
    reg = _REG_BAR_OWNED.replace(_BAR, "a bar no spec in this repo has ever carried")
    root = _fixture(td, register=reg, jobs=_SPECS_TWO_BEATS)
    check("an entry asserting a collision that no longer exists FAILS on itself",
          len(_fails(ccd.run(root), "stale_bar_entry")) == 1)


def test_an_excused_spec_is_quiet_while_its_record_still_backs_it(td):
    root = _fixture(td, register=_REG_BAR_ACK, jobs=_SPECS_TWO_BEATS,
                    records={"records/known.yaml":
                             "note: beat 16 keeps the paste until it re-renders\n"})
    out = ccd.run(root)
    check("a spec on the acknowledged list is not failed while the record stands",
          _fails(out, "bar_serves_two_beats") == []
          and _fails(out, "acknowledgement_unrecorded") == [])


def test_an_excuse_the_record_no_longer_carries_stops_excusing(td):
    # RED when: ack_live is not consulted, i.e. the suppression list is trusted
    # without the record that is supposed to justify it.
    root = _fixture(td, register=_REG_BAR_ACK, jobs=_SPECS_TWO_BEATS,
                    records={"records/known.yaml": "note: nothing about beat 16 any more\n"})
    out = ccd.run(root)
    check("an unbacked suppression list FAILS on itself",
          len(_fails(out, "acknowledgement_unrecorded")) == 1)
    check("and the spec it was excusing is failed again",
          len(_fails(out, "bar_serves_two_beats")) == 1)


def test_the_bar_rule_reaches_the_real_exit_code_and_not_just_the_function(td):
    """The unwired-call-site trap, made un-passable.

    Proved today on another lane: a guard function written PERFECTLY whose call
    site was never wired still passed 42 of 47 checks — only the few that ran the
    real thing end to end and demanded the real exit code caught it. And
    check_canon_drift.py itself has been found running green while checking
    nothing. Every other assertion here calls ccd.run() directly; this one runs
    the file the way CI and a human run it, argv in, stdout and exit code out, so
    deleting `findings += rule_bar_serves_two_beats(root, reg)` from run() turns
    THIS red with the function itself untouched.
    """
    import subprocess
    root = _fixture(td, register=_REG_BAR_OWNED, jobs=_SPECS_TWO_BEATS)
    r = subprocess.run([sys.executable, str(REPO / "pipeline" / "check_canon_drift.py"),
                        "--root", str(root)], capture_output=True, text=True,
                       encoding="utf-8")
    check("the real entry point EXITS 1 on a bar recorded against the wrong beat",
          r.returncode == 1)
    check("the counted banner is what says so, not a stray log line",
          "CANON-DRIFT: fail=1 " in r.stdout)
    check("stdout names the rule and the offending spec",
          "bar_serves_two_beats" in r.stdout and "ep2-b16-fig-0814.yaml" in r.stdout)


# --- AND ONE RULING RECORDED ON TWO CARDS IS COVERED, NOT UNCOVERED --------
# `also_records:` is coverage bookkeeping only, never adjudication: _card_resolution
# must identify exactly ONE card or it abstains, so the second card carrying the
# same ruling would sit on the uncovered list forever without this.

_INBOX_TWO_CARDS_ONE_RULING = """
- what: WHICH SEED IS THE GOBLIN
  url: /review/ep2-picks/sheets/seed-picker-0816.jpg
  resolved:
    date: '2026-08-16'
    verdict: seed s0 is the goblin
- what: THE PLATES CARD ASKS THE SAME THING IN OLDER WORDS
  url: /review/ep2-picks/sheets/plates-0812.jpg
  resolved:
    date: '2026-08-16'
    verdict: seed s0 is the goblin
"""

_REG_ALSO_RECORDS = """
records:
  structured: []
  prose: []
subjects:
- id: ep2-seed-is-goblin
  kind: founder_decision
  resolved_by:
    card_url_contains: sheets/seed-picker-0816.jpg
    verdict_matches: seed s0 is the goblin
  also_records:
  - card_url_contains: sheets/plates-0812.jpg
  evidence:
    file: review/inbox.yaml
    contains: seed s0 is the goblin
"""


# --- AND AN ASSERTION MUST NOT BE SATISFIED BY PROSE MARKED DEAD -----------
# THE HOLE, measured 2026-08-17. House style §6 keeps superseded prose VISIBLE
# FOREVER, struck with `~~`, because the provenance is the point. So a
# `contains:` assertion pointed at prose that is later superseded keeps passing
# on the struck-through corpse of its own claim — indefinitely.
# `sapling-cotyledon-shape` asserted 'The working canon is ROUND/OVAL
# COTYLEDONS', superseded 2026-08-17 and STILL PHYSICALLY PRESENT at
# THE-SAPLING.md:81 inside the struck block. Measured on the real repo with the
# real string: pre-fix `fail=1`, post-fix `fail=2`. It matters because the same
# pattern guards ep2-fig-purple — the founder's canon-wide retroactive purple
# ruling — so the instrument meant to catch a drift back to red could not.
#
# AND ONLY `~~` MEANS DEAD. Stripping `>`-quoted blocks as well (the written
# proposal) turns `sapling-height` red FALSELY: its evidence lives inside a
# blockquote, and in this repo `>` is a QUOTATION, usually the founder's own
# words — the most alive text there is. test_a_blockquote_is_not_a_corpse pins
# that so nobody "fixes" it back.


def _ev_reg(needle, file="doc.md"):
    return ("records:\n  structured: []\n  prose: []\n"
            "subjects:\n- id: sapling-struck-probe\n  kind: prompt_canon\n"
            "  since: '2026-08-17'\n  evidence:\n"
            f"    file: {file}\n    contains: '{needle}'\n")


_DOC_SUPERSEDED = """
## 2.2 The leaves

**The canon is ORDINARY LEAVES.** A plain, unremarkable leaf, 2026-08-17.

> ~~**The working canon is ROUND/OVAL COTYLEDONS.** He did not say this. He
> said two leaves, and the steward inferred the shape from the count on
> 2026-08-16. Kept visible per house style; do not apply it.~~
"""


def test_an_evidence_string_alive_only_inside_a_strike_fails(td):
    # RED when: live_prose() stops being applied. THE case that was passing.
    root = _fixture(td, register=_ev_reg("The working canon is ROUND/OVAL COTYLEDONS"),
                    records={"doc.md": _DOC_SUPERSEDED})
    f = _fails(ccd.run(root), "register_evidence_missing")
    check("an assertion satisfied ONLY by struck-through text FAILS", len(f) == 1)
    check("and the file still physically contains it — that is the whole point",
          "The working canon is ROUND/OVAL COTYLEDONS" in _DOC_SUPERSEDED)
    check("the finding says the text is struck, not merely absent",
          bool(f) and "struck" in f[0].detail.lower())


def test_the_live_prose_that_replaced_it_still_passes(td):
    # RED when: live_prose() strips too much and eats live text.
    root = _fixture(td, register=_ev_reg("The canon is ORDINARY LEAVES"),
                    records={"doc.md": _DOC_SUPERSEDED})
    check("the live claim in the same file satisfies the gate",
          _fails(ccd.run(root), "register_evidence_missing") == [])


def test_a_blockquote_is_not_a_corpse(td):
    """`>` marks a QUOTATION — usually the founder — not superseded text.

    The written proposal was to skip `~~`-struck AND `>`-quoted prose. Measured
    over all 8 real subjects, the quoted half turns `sapling-height` red falsely:
    it asserts `about 40 cm, always shorter than he`, which lives in a blockquote.
    Failing an entry whose canon is current is the cry-wolf shape that gets
    instruments switched off — installed inside the honesty checker itself.
    """
    doc = "## Height\n\n> He said: about 40 cm, always shorter than he is.\n"
    root = _fixture(td, register=_ev_reg("about 40 cm, always shorter than he"),
                    records={"doc.md": doc})
    check("a founder quote in a blockquote is LIVE canon and passes",
          _fails(ccd.run(root), "register_evidence_missing") == [])


def test_a_strike_spanning_several_quoted_lines_is_removed_whole(td):
    # RED when: the span regex loses re.S. The real strike in THE-SAPLING.md
    # wraps over four `>` continuation lines, so a line-at-a-time strip misses it.
    doc = "start\n\n> ~~**DEAD CLAIM HEADER.** and the reason it died,\n> which runs on\n> for three more lines.~~\n\nend\n"
    root = _fixture(td, register=_ev_reg("which runs on for three more lines"),
                    records={"doc.md": doc})
    f = _fails(ccd.run(root), "register_evidence_missing")
    check("a multi-line struck span is dead all the way through", len(f) == 1)


def test_removing_a_strike_cannot_join_words_across_the_gap(td):
    # RED when: struck spans are replaced with "" instead of a space, so
    # `al~~junk~~pha` would start satisfying an assertion for `alpha`.
    root = _fixture(td, register=_ev_reg("alpha"),
                    records={"doc.md": "the word is al~~junk~~pha here\n"})
    check("stripping a strike must not manufacture a word that was never written",
          len(_fails(ccd.run(root), "register_evidence_missing")) == 1)


def test_unbalanced_strike_markers_abstain_rather_than_guess(td):
    # RED when: an odd `~~` count is silently treated as clean prose.
    root = _fixture(td, register=_ev_reg("The canon is ORDINARY LEAVES"),
                    records={"doc.md": "**The canon is ORDINARY LEAVES.** and a stray ~~ marker\n"})
    out = ccd.run(root)
    check("an odd number of `~~` is reported, not guessed at",
          any(f.rule == "register_evidence_unstruckable" and f.level == ccd.UNKNOWN
              for f in out))
    check("and it is an abstention — a malformed file is not a FAIL",
          _fails(out, "register_evidence_unstruckable") == [])


def test_a_string_that_is_simply_gone_keeps_the_older_message(td):
    # RED when: every miss is reported as struck, which would misdiagnose the
    # ordinary stale-string case the gate was built for.
    root = _fixture(td, register=_ev_reg("a claim nobody ever wrote down"),
                    records={"doc.md": _DOC_SUPERSEDED})
    f = _fails(ccd.run(root), "register_evidence_missing")
    check("a string that was never there is 'no longer in the file'", len(f) == 1)
    check("and is NOT blamed on a strike it has nothing to do with",
          bool(f) and "struck" not in f[0].detail.lower())


def test_the_struck_evidence_gate_reaches_the_real_exit_code(td):
    """Same unwired-call-site trap, same answer: run the real thing.

    check_register_freshness could be perfect and unreferenced at run()'s call
    site and every assertion above would still pass. This one runs the file by
    argv and demands the exit code, so deleting `findings +=
    check_register_freshness(root, reg)` turns it red with the function untouched.
    """
    import subprocess
    root = _fixture(td, register=_ev_reg("The working canon is ROUND/OVAL COTYLEDONS"),
                    records={"doc.md": _DOC_SUPERSEDED})
    r = subprocess.run([sys.executable, str(REPO / "pipeline" / "check_canon_drift.py"),
                        "--root", str(root)], capture_output=True, text=True,
                       encoding="utf-8")
    check("the real entry point EXITS 1 on an assertion backed only by dead text",
          r.returncode == 1)
    check("the counted banner reports it as a failure",
          "CANON-DRIFT: fail=1 " in r.stdout)
    check("stdout names the rule and the struck diagnosis",
          "register_evidence_missing" in r.stdout and "struck" in r.stdout.lower())


def test_the_real_register_has_no_assertion_living_on_dead_text():
    """The floor on the real repo: no subject may be green on a corpse.

    Run against pipeline/canon.yaml itself, because the synthetic fixtures above
    prove the mechanism and this proves the REPO. When this goes red, a canon
    moved and its register entry is still pointing at the struck-through text of
    the claim it replaced — repoint `contains:`, never un-strike the prose.
    """
    # `or {}` so a missing register fails this check LOUDLY on the count below
    # rather than crashing with AttributeError and reading as an error, not a red.
    reg = ccd.load_register(str(REPO))[0] or {}
    subjects = [s for s in reg.get("subjects", []) if (s.get("evidence") or {}).get("contains")]
    check("every subject in the register carries an evidence string", len(subjects) >= 8)
    corpses = []
    for s in subjects:
        p = REPO / s["evidence"]["file"]
        if not p.exists():
            continue
        raw = p.read_text(errors="replace")
        n = ccd._flat(s["evidence"]["contains"])
        if n in ccd._flat(raw) and n not in ccd._flat(ccd.live_prose(raw)):
            corpses.append(s["id"])
    check(f"no live subject is satisfied only by struck text (found: {corpses})",
          corpses == [])


def test_a_second_card_carrying_one_ruling_counts_as_covered(td):
    root = _fixture(td, inbox=_INBOX_TWO_CARDS_ONE_RULING, register=_REG_ALSO_RECORDS)
    out = ccd.run(root)
    check("neither card is left on the register's uncovered list",
          [f for f in out if f.rule == "unregistered_decision"] == [])
    check("and bookkeeping adjudicates nothing — it cannot manufacture a FAIL",
          _fails(out) == [])


def test_without_also_records_the_second_card_is_reported_uncovered(td):
    # THE MUTATION, built in: delete the field and the same fixture must go loud.
    # An assertion that passes with the mechanism removed is not testing it.
    reg = _REG_ALSO_RECORDS.replace(
        "  also_records:\n  - card_url_contains: sheets/plates-0812.jpg\n", "")
    root = _fixture(td, inbox=_INBOX_TWO_CARDS_ONE_RULING, register=reg)
    u = [f for f in ccd.run(root) if f.rule == "unregistered_decision"]
    check("with the field gone the same decision is reported uncovered",
          len(u) == 1 and "OLDER WORDS" in u[0].detail)
    check("and it is an abstention, never a pass and never a FAIL",
          bool(u) and u[0].level == ccd.UNKNOWN)



# ---------------------------------------------------------------------------
# THE HARNESS DRAFTS GUARD. 2026-08-16.
#
# Reconstructs the exact failure that was found and not caught: a job whose
# --harness names a directory whose wave-drafts.yaml is NOT ours, rendering a
# beat-19 key whose wording the founder killed on 2026-08-15 and which
# done-definitions.yaml now makes disqualifying ("a take where the fruit
# touches him fails this beat now"). Six copies of that file existed on the
# card; the hashes below are the real ones, measured 2026-08-16.
#
# The renderer had been WRITING drafts_sha256 into every sidecar since the file
# was authored (goblin_ipa_sample.py:636). Nothing read it. So this is not a
# test of new plumbing; it is a test that a number we already record is finally
# compared to something.
# ---------------------------------------------------------------------------

_OURS = "dd644905c2ebee4648b6bf7ba675dbfe622d826d0ca9f09a294217254d125246"
_STALE = "0017402c4aa09427410ca0f633a2cbef12409f2d460a85bc3c6d2cbac99af4e2"


def _b19_spec(harness, **extra):
    """A beat-19 job in the shape ep2-b18-scale-0816 actually had.

    Both steps name the harness, because both steps of a real goblin spec do
    and because the dry step is where the refusal is cheapest.
    """
    spec = {"id": "ep2-b19-guardtest", "node": "002b-first-citizen",
            "consumer": "the harness drafts guard's own regression test",
            "steps": [{"name": "dry",
                       "argv": ["python.exe", "goblin_ipa_beat.py", "--beat", "19",
                                "--harness", harness,
                                "--draft-key", "authored_b19_adult", "--dry"]},
                      {"name": "sample",
                       "argv": ["python.exe", "goblin_ipa_beat.py", "--beat", "19",
                                "--harness", harness,
                                "--draft-key", "authored_b19_adult"]}]}
    spec.update(extra)
    return spec


def test_a_stale_harness_cannot_render_a_killed_wording():
    sys.path.insert(0, str(REPO / "pipeline"))
    import box_enqueue as bq

    stale = _b19_spec(r"C:\banyan-farm\wave-scale-0816")
    probs = bq.harness_drafts_problems(stale, repo_sha=_OURS,
                                       box_sha=lambda p: _STALE)
    check("a beat-19 job on a stale harness is REFUSED",
          len(probs) == 1 and "STALE DRAFTS" in probs[0])
    check("the refusal prints both hashes, so it can be acted on without a box",
          _STALE in probs[0] and _OURS in probs[0])
    check("the refusal NAMES THE FIX -- a guard with no remedy gets disabled",
          "--sync-drafts" in probs[0] and "drafts_ack" in probs[0])

    ours = _b19_spec(r"C:\banyan-farm\wave-goblin-prep")
    check("the same job on the matching harness passes",
          bq.harness_drafts_problems(ours, repo_sha=_OURS,
                                     box_sha=lambda p: _OURS) == [])

    # Two steps, one harness: the refusal must be one line, not one per step.
    check("a harness named twice is refused once, not twice",
          len(bq.harness_drafts_problems(stale, repo_sha=_OURS,
                                         box_sha=lambda p: _STALE)) == 1)

    # "Could not look" is not "fine" -- the same rule plate_problems keeps.
    check("an unreadable drafts file is a refusal, not a pass",
          any("cannot be identified" in p for p in
              bq.harness_drafts_problems(stale, repo_sha=_OURS,
                                         box_sha=lambda p: "")))

    # Deliberate forks have to stay possible, or the guard blocks real work and
    # gets removed. The waiver names what it waives, like every other in the file.
    waived = _b19_spec(r"C:\banyan-farm\wave-scale-0816",
                       drafts_ack="a forked scale wording under test on purpose")
    check("an explicit drafts_ack waives the drift",
          bq.harness_drafts_problems(waived, repo_sha=_OURS,
                                     box_sha=lambda p: _STALE) == [])
    check("but the ack does NOT excuse an unreadable file",
          bq.harness_drafts_problems(waived, repo_sha=_OURS,
                                     box_sha=lambda p: "") != [])

    # The path is read off argv, not off the id -- the house rule everywhere in
    # box_enqueue. A spec whose two steps disagree renders its preflight against
    # one wording and its picture against another.
    split = _b19_spec(r"C:\banyan-farm\wave-goblin-prep")
    split["steps"][1]["argv"][5] = r"C:\banyan-farm\wave-scale-0816"
    check("a spec that changes harness between its steps is caught",
          len(bq.harness_drafts_problems(
              split, repo_sha=_OURS,
              box_sha=lambda p: _OURS if "goblin-prep" in p else _STALE)) == 1)

    check("the guard runs inside gate_checks, not only when called by hand",
          "harness_drafts_problems" in
          (REPO / "pipeline" / "box_enqueue.py").read_text(encoding="utf-8")
          .split("def gate_checks")[1].split("\ndef ")[0])


def test_a_job_cannot_be_filed_with_outputs_nobody_can_find():
    """Six jobs rendered perfectly into C:\\Windows\\System32 and the card idled 11h.

    2026-08-17. A relative `--out` sent every frame to the runner service's
    working directory; the artifacts list was carried from another spec; and the
    publish step -- whose paths use forward slashes -- was left reading the
    SOURCE job's directory, so it copied that job's frames out under this job's
    name and exited 0. Nothing in box_enqueue objected, because every check
    there asked whether a job was ALLOWED to run and none asked whether anyone
    could find what it made.
    """
    import box_enqueue as bq
    absout = r"C:\banyan-farm\jobdir\frame.png"
    ok = {"steps": [{"name": "s1", "argv": ["py.exe", "x.py", "--out", absout]}],
          "artifacts": [absout]}
    check("a spec whose outputs are absolute and declared is filed",
          bq.output_path_problems(ok) == [])

    relative = {"steps": [{"name": "s1", "argv": ["py.exe", "x.py", "--out", "frame.png"]}],
                "artifacts": []}
    check("a RELATIVE --out is refused (this is the System32 bug)",
          any("NOT an absolute path" in p for p in bq.output_path_problems(relative)))

    foreign = {"steps": [{"name": "s1", "argv": ["py.exe", "x.py", "--out", absout]}],
               "artifacts": [r"C:\banyan-farm\jobdir\someone-elses-frame.png"]}
    check("an artifact no step produces is refused",
          any("never named by any step" in p for p in bq.output_path_problems(foreign)))

    publish_elsewhere = {
        "steps": [{"name": "s1", "argv": ["py.exe", "x.py", "--out", absout]},
                  {"name": "publish", "argv":
                   ["py.exe", "-c", "src = 'C:/banyan-farm/OTHERJOB'\nprint(src)\n"]}],
        "artifacts": [absout]}
    check("a publish step reading a directory this job never writes is refused",
          any("no step in this job writes" in p
              for p in bq.output_path_problems(publish_elsewhere)))

    same_dir_fwd = {
        "steps": [{"name": "s1", "argv": ["py.exe", "x.py", "--out", absout]},
                  {"name": "publish", "argv":
                   ["py.exe", "-c", "src = 'C:/banyan-farm/jobdir'\nprint(src)\n"]}],
        "artifacts": [absout]}
    check("the same directory spelled with forward slashes is accepted",
          bq.output_path_problems(same_dir_fwd) == [])

    check("the guard runs inside gate_checks, not only when called by hand",
          "output_path_problems" in
          (REPO / "pipeline" / "box_enqueue.py").read_text(encoding="utf-8")
          .split("def gate_checks")[1].split("\ndef ")[0])


def test_a_finished_job_cannot_be_filed_with_nothing_to_carry_it_home():
    """ep2-cnet-probe-0817 rendered all four arms and was invisible for two days.

    2026-08-17 12:39-12:41Z: it ran, it succeeded, and it PASSED its own bar by
    28x. Nobody knew until 2026-08-19, because the spec declared artifacts under
    its own working directory and no step copied them into
    C:\\banyan-farm\\courier-box\\farm-out -- the only path by which a box result
    reaches this tree. Two later documents state as fact that the job never
    fired. output_path_problems passed it, because it only asks whether the
    declared artifacts are NAMED by a step. Named is not delivered.
    """
    import box_enqueue as bq
    out = r"C:\banyan-farm\jobdir\frame.png"
    step = {"name": "s1", "argv": ["py.exe", "x.py", "--out", out]}

    stranded = {"steps": [step], "artifacts": [out]}
    probs = bq.courier_problems(stranded)
    check("a job whose artifacts nothing couriers off the box is refused",
          any("nothing will carry them off the box" in p for p in probs))
    check("the refusal names the incident that cost two days",
          any("ep2-cnet-probe-0817" in p for p in probs))

    published = {
        "steps": [step,
                  {"name": "publish", "argv":
                   ["py.exe", "-c",
                    'import shutil\n'
                    'dst = "C:/banyan-farm/courier-box/farm-out/jobdir"\n'
                    'shutil.copy2("C:/banyan-farm/jobdir/frame.png", dst)\n']}],
        "artifacts": [out]}
    check("the same job WITH a publish step into farm-out is filed",
          bq.courier_problems(published) == [])

    # The forward-slash spelling is the one every real publish step uses, and
    # the backslash spelling is what `artifacts:` uses -- both must resolve.
    backslashed = {
        "steps": [step,
                  {"name": "publish", "argv":
                   ["py.exe", "-c",
                    'import shutil\n'
                    'shutil.copy2(src, r"C:\\banyan-farm\\courier-box\\farm-out\\j")\n']}],
        "artifacts": [out]}
    check("a publish step spelled with backslashes is accepted too",
          bq.courier_problems(backslashed) == [])

    direct = {"steps": [{"name": "s1", "argv":
                         ["py.exe", "x.py", "--out",
                          r"C:\banyan-farm\courier-box\farm-out\j\frame.png"]}],
              "artifacts": [r"C:\banyan-farm\courier-box\farm-out\j\frame.png"]}
    check("a job that writes STRAIGHT into farm-out needs no publish step",
          bq.courier_problems(direct) == [])

    # MENTIONING the path is not couriering it. This is the shape of the bug:
    # a spec can talk about farm-out in its own text and still move nothing.
    mentions_only = {
        "steps": [step,
                  {"name": "note", "argv":
                   ["py.exe", "-c",
                    'print("results go to C:/banyan-farm/courier-box/farm-out later")\n']}],
        "artifacts": [out]}
    check("merely NAMING farm-out without copying anything is still refused",
          any("nothing will carry them off the box" in p
              for p in bq.courier_problems(mentions_only)))

    check("a job that declares no artifacts strands nothing and is not refused",
          bq.courier_problems({"steps": [step], "artifacts": []}) == [])

    check("the guard runs inside gate_checks, not only when called by hand",
          "courier_problems" in
          (REPO / "pipeline" / "box_enqueue.py").read_text(encoding="utf-8")
          .split("def gate_checks")[1].split("\ndef ")[0])


def test_a_resolved_call_can_never_render_as_waiting_on_the_author():
    """The founder screenshotted /status four times over one defect.

    "Waiting on the author" was fed by `pipeline/pending-founder.yaml` — retired
    2026-08-14, in its own `retired:` block, every one of its four entries
    carrying a `resolved:` verdict. The reader filtered on nothing, so the page
    aged four answered calls off their own `since:` dates (7, 7, 12 and 20 days)
    while the strip immediately above them, reading the live board, said 2. Among
    the four: an episode-1 frame pick he closed with "we have already published
    it dude, we are done", and a script read he abolished outright.

    Both halves are asserted, because either alone would let it come back. The
    READER (`build_status.inbox()`) must read the canonical board and drop what
    carries `resolved:`. The RENDERER (`waiting_html`) must refuse a resolved
    entry from ANY supplier — the stale four reached the page through a supplier
    that did no filtering, so the invariant has to live in the section rather
    than in one of its sources.

    The last two checks are run against the REAL board, because a unit test on
    synthetic data cannot see the drift that actually shipped: the page's own
    count and the page's own list read from the same file, and if they ever
    disagree again one of them has stopped reading it.
    """
    import datetime
    import tempfile

    import yaml

    import build_sim as bs
    import build_status as bd

    now = datetime.datetime(2026, 8, 19, tzinfo=datetime.timezone.utc)
    board = [
        {"what": "AN OPEN TASTE CALL. Second half of the same question.",
         "url": "/review/ep2-guards-0818", "since": "2026-08-17", "group": "taste"},
        {"what": "Choose the last drawing in episode 1 - scene 6.",
         "url": "/review/cuts.html#item-10", "since": "2026-08-07",
         "resolved": {"date": "2026-08-13",
                      "verdict": "we have already published it dude, we are done"}},
    ]

    with tempfile.TemporaryDirectory() as td:
        real = bd.REPO
        try:
            bd.REPO = Path(td)
            (Path(td) / "review").mkdir()
            (Path(td) / "review/inbox.yaml").write_text(
                yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
            cards = bd.inbox()
            check("the reader takes its entries from review/inbox.yaml",
                  len(cards) == 1)
            check("an entry with a resolved: key is not handed to the page",
                  all(not c.get("resolved") for c in cards)
                  and "episode 1" not in repr(cards))
            check("the age is measured from the card's own since:",
                  bs.waiting_words(cards[0]["since"], now) == "waiting 2 days")
            src = (REPO / "pipeline" / "build_status.py").read_text(encoding="utf-8")
            # The path as a code literal, not as prose: the docstring above
            # inbox() names the retired file on purpose, to say why it is gone.
            check("the retired snapshot file is not read by any code path",
                  'pending-founder.yaml"' not in src
                  and 'review/inbox.yaml"' in src)
        finally:
            bd.REPO = real

    # The renderer refuses it a second time, whoever hands it in. These are
    # page-shaped rows carrying a `resolved:` key — the exact thing the retired
    # reader handed over, title and all, and the page printed it.
    rows = [
        {"title": "AN OPEN TASTE CALL", "detail": "the guards read adolescent",
         "since": "2026-08-17"},
        {"title": "Choose the last drawing in episode 1 - scene 6",
         "detail": "the one shot you have never passed", "since": "2026-08-07",
         "resolved": {"date": "2026-08-13",
                      "verdict": "we have already published it dude, we are done"}},
    ]
    html = bs.waiting_html(rows, [], now)
    check("the section renders the open call", "AN OPEN TASTE CALL" in html)
    check("the section cannot render a resolved call",
          "last drawing in episode 1" not in html)
    check("and it is dropped, not merely hidden — one row, not two",
          html.count("<li>") == 1)
    check("a list of nothing but resolved calls reads as nothing waiting",
          "Nothing waiting" in bs.waiting_html([rows[1]], [], now))
    check("a resolved call cannot age off its own since: either",
          "waiting 12 days" not in html)

    live = bd.inbox()
    check("every call on the real page is open",
          all(not c.get("resolved") for c in live))
    check("the page's count and the page's list read the same file",
          len(live) == bs.review_inbox_open())


def test_a_newer_mirror_alone_is_not_a_stuck_deploy():
    """The gate said STUCK on a healthy deploy for as long as work was held.

    banyan.city built 95 seconds after the last PUSHED commit -- working
    perfectly -- while 185 commits sat unpushed on the laptop. qa_local measured
    lag against local HEAD, called it an 8.5h stuck deploy, and cited the Pages
    mirror as corroboration. But `pages.yml` reruns on a */30 cron from the same
    commit, so a newer mirror is the normal state of any day without a push.

    Both directions are asserted here, because the fix is only worth having if
    the check can still go red on the real failure it was written for.
    """
    import qa_local as q
    H = 3600
    check("a newer mirror with a CURRENT primary is the cron, not a stuck deploy",
          not q.mirror_says_stuck(drift_s=11 * H, primary_lag_s=0, fail_s=3 * H))
    check("a newer mirror AND a primary behind what was pushed is still STUCK",
          q.mirror_says_stuck(drift_s=11 * H, primary_lag_s=5 * H, fail_s=3 * H))
    check("a behind primary with no mirror drift does not fire this check",
          not q.mirror_says_stuck(drift_s=0, primary_lag_s=5 * H, fail_s=3 * H))
    check("both must clear the threshold, not merely be positive",
          not q.mirror_says_stuck(drift_s=4 * H, primary_lag_s=1 * H, fail_s=3 * H))
    check("lag is measured against origin/main, not HEAD",
          "origin/main" in (REPO / "pipeline" / "qa_local.py")
          .read_text(encoding="utf-8").split("def origin_commit_epoch")[1][:400])


if __name__ == "__main__":
    sys.exit(main())
