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
                "build_shotboard.py", "site_theme.py", "licence_gate.py"]
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

    ok, errs = case("cuts/review-assets", dict(good, model="Lightricks/LTX-2.3-Distilled"))
    check("D16's LTX is still refused inside the gallery", not ok and errs == 1)

    ok, errs = case("cuts/review-assets", dict(good, model="someone/never-heard-of-it-v9"))
    check("an unclassified model is still refused inside the gallery",
          not ok and errs == 1)

    # The compound string is the one that has bitten before: judging a value by
    # its softest ingredient is hole 1, and an exemption re-opens it if the
    # publish path stops at the first licence it can excuse.
    ok, errs = case("cuts/review-assets", dict(
        good, model="still: cagliostrolab/animagine-xl-3.1 | motion: Lightricks/LTX-2.3"))
    check("animagine beside LTX in one value loses on the LTX clause",
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
          [n for n, _ in lg.model_licences(LTX23)] == ["ltx-2-3"])
    check("...so the document cited is the LTX-2 Community Licence (D16)",
          "LTX-2 Community Licence" in (lg.engine_licence(LTX23) or ""))
    check("...and not the LTXV Open Weights 0.X the catch-all names",
          "0.X" not in (lg.engine_licence(LTX23) or ""))
    check("...while the refusal itself is unchanged — it was never the defect",
          lg.classify(lg.engine_licence(LTX23))[0] != "allow")
    errors, _ = tree("ltx23-document", {f"{N}/clips/01-a.meta.yaml":
                                        f"platform: local-gpu (rtx5090)\nmodel: {LTX23}\n"})
    check("the gate reports that sidecar once, under D16",
          len(errors) == 1 and "D16" in errors[0] and "0.X" not in errors[0])
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
    check("the source is GitHub's public deployments list", m["api"].startswith(
        "https://api.github.com/repos/olegmlkvorg/banyan-city/deployments?"))
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

    # NOT A VITAL. The vitals row promises four numbers a reader can check
    # against the repo; this one is fetched live and can be absent, and quietly
    # sitting it beside them would weaken the promise the row makes.
    check("the meter is its own tile, not a fifth repo-checkable vital",
          'class="infra rise"' in src and '<div class="vital"><b>{pct}%' in src)


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
    test_queue_promoter_gate_beats_everything()
    test_queue_promotion_is_one_atomic_move()
    test_argparse_declares_every_flag_it_reads()
    test_child_verdict_names_a_corpse()
    test_a_busy_card_refuses_the_render()
    with tempfile.TemporaryDirectory() as td:
        test_giveup_needs_no_fail_line(Path(td))
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
    with tempfile.TemporaryDirectory() as td:
        test_the_conditioning_plate_is_the_episode_crop(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_no_render_path_stretches_a_mismatched_still(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_dispatch_never_hands_a_renderer_a_raw_still(Path(td))
    test_vercel_build_guard_covers_every_site_input()
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
        test_the_nested_init_frame_dialect_resolves_like_the_flat_one(Path(td))
    test_every_served_cut_posters_the_frame_its_record_names()
    test_the_infra_meter_never_prints_a_number_the_page_did_not_measure()
    # A HAND-RUN THAT BORROWS A QUEUE ID CLAIMS IT — pure: no git, no network.
    test_a_hand_claim_writes_lines_every_reader_already_parses()
    test_a_hand_claim_reads_the_verdict_off_the_exit_code()
    test_a_hand_claim_refuses_an_id_nobody_filed()
    # A CONCATENATION MUST NOT LAUNDER ITS INPUTS — own temp dir each: these
    # rewrite and delete source clips under a manifest that names them.
    with tempfile.TemporaryDirectory() as td:
        test_a_cut_holding_one_refused_ingredient_does_not_publish(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_cut_whose_manifest_no_longer_describes_its_inputs_does_not_publish(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_a_cut_whose_ingredients_all_pass_publishes_unchanged(Path(td))
    # REGIONAL IP-ADAPTER GEOMETRY (memo §3.3) — pure: PIL only, no torch.
    test_a_region_mask_conditions_its_box_and_nothing_else()
    test_a_box_that_names_no_region_is_refused_not_rounded()
    test_the_reference_crop_keeps_only_the_subject()
    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all pipeline tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
