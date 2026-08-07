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
import hold_still as hs
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
    hs.sidecar(clip, tmp / "03-deploy-succeeded.png", 3, 2.5, zoom_total_used=0.03)
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

    node = REPO / "genomes/sapling/nodes/001-capability-inventory"
    stills = tmp / "stills"
    stills.mkdir()
    (stills / "01-keyboard.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
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
    blocked = []
    for n in present:
        side = lg.sidecar_for(cuts_dir / n, lg.META_EXT)
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            continue
        for key, value in data.items():
            if key.lower() not in lg.PROVENANCE_KEYS:
                continue
            licence = lg.engine_licence(value)
            if licence and lg.classify(licence)[0] != "allow":
                blocked.append(f"{n} ({key})")
    check("every published asset's own record clears the licence gate", not blocked)
    if blocked:
        print("      withheld:", ", ".join(blocked[:6]))


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
    skip, gave_up = finished_tasks(Stub())
    check("a task started MAX_ATTEMPTS times with no DONE is skipped",
          "killer" in skip and gave_up.get("killer") == MAX_ATTEMPTS)
    check("a completed task is skipped but not accused",
          "fine" in skip and "fine" not in gave_up)
    check("a task with one start left is still runnable",
          "once" not in skip and "once" not in gave_up)


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
    RESTRICTED = ("pixverse", "kling", "vidu", "stable-video-diffusion",
                  "f5-tts", "openaudio", "fish", "google-flow", "veo",
                  "ltx-video", "lightricks", "ltx-2-3")
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
    with tempfile.TemporaryDirectory() as td:
        test_held_still_is_never_reversed(Path(td))
    test_held_zoom_is_monotonic_and_moderate()
    with tempfile.TemporaryDirectory() as td:
        test_held_sidecar_is_readable_by_every_tool_that_reads_it(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_every_sidecar_reader_finds_both_shapes(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_farm_still_sidecar_records_what_actually_ran(Path(td))
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
    test_queue_promoter_gate_beats_everything()
    test_queue_promotion_is_one_atomic_move()
    test_argparse_declares_every_flag_it_reads()
    test_child_verdict_names_a_corpse()
    with tempfile.TemporaryDirectory() as td:
        test_giveup_needs_no_fail_line(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_animegen_casts_before_the_second_expert(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_licence_gate(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_no_undefined_locals(Path(td))
        test_subprocess_reads_are_utf8(Path(td))
        test_queue_render_params_reach_the_child(Path(td))
        test_probe_beat_sends_the_files_and_the_whole_recipe(Path(td))
    test_ltx_frames_are_the_nearest_8n_plus_1()
    with tempfile.TemporaryDirectory() as td:
        test_ltx_dispatch_routes_by_video_model(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_ltx_jobs_list_is_one_beat_per_entry(Path(td))
    test_review_page_publishes_nothing_unprovenanced()
    test_checklist_does_not_reask_a_closed_question()
    with tempfile.TemporaryDirectory() as td:
        test_beat11_direction_is_the_founders_revert(Path(td))
        test_beat09_negatives_forbid_the_growth(Path(td))
        test_hosted_path_sends_our_negative(Path(td))
        test_antistatic_first_signal_wins(Path(td))
        test_vendored_licence_does_not_launder(Path(td))
        test_nested_licence_does_not_launder(Path(td))
    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all pipeline tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
