#!/usr/bin/env python3
"""Compress a shot prompt to fit SD1.5's 77-token text encoder.

`shots.md` prompts are written for humans first — they open with the full style
bible so a reader (or a different model) knows exactly what the shot should look
like. That costs about 45 tokens before a single word of action, and CLIP stops
at 77. Measured on 2026-07-26 with the real tokenizer, all twenty of 001's
prompts run 113-145 tokens, and beat 1 is cut here:

    …a tiny mascot-simple banyan sapling — thin curved trunk, two oversized
    expressive leaves, no [CUT] face — trembles and shivers in a gust of wind,
    filling the lower half of the frame, alone in a vast green field…

So the renderer never saw the action, the framing, or the light — only style
words. That is very likely part of why the first renders came back as mush.

The fix keeps `shots.md` exactly as it is (it is documentation) and compresses at
generation time:

- a compact STYLE_TAG replaces the long style sentence — same instruction, ~14
  tokens instead of ~45
- the shot type is preserved, because framing is not decoration
- the trailing "No photorealism, no 3D render look… no text" is dropped, since
  every one of those terms is already in the renderer's negative prompt, so as a
  positive-prompt suffix it is pure waste — and being at the end, it was the part
  CLIP threw away anyway
- if the action is still too long, it is trimmed at a SENTENCE boundary from the
  end and the caller is told, so nothing is ever cut mid-phrase

    from sd_prompt import compress
    text, dropped = compress(shot["prompt"])
"""

import re

# Same instruction as the style bible's opening sentence, in a fraction of the
# tokens. Comma-separated tags are what SD1.5 was trained on; the prose version
# spends its budget on grammar the text encoder does not use.
# Style sits at the END so it modifies rather than becomes the subject (leading
# with it produced abstract lineart and no sapling). But trailing style is weakly
# weighted, and vanilla SD1.5 defaulted to watercolour painting, so the tag is
# front-loaded with the two words that matter most and repeated compactly.
# The trailing "masterpiece, best quality" are not decoration and not wishful: they are
# the booster tags Animagine XL 3.1 was explicitly trained with (its model card scores
# training captions on an aesthetic scale and expects them at inference). Omitting them
# on 2026-07-26 got the exact failure its card warns about — flat abstract shapes in a
# garish palette. `abstract` is correspondingly in the negative, notebook side.
STYLE_TAG = ("anime cel shading, flat colour, bold clean lineart, 2d animation still, "
             "pastel, masterpiece, best quality")

# The style preamble ends at the first sentence break after the palette phrase.
_STYLE_END = re.compile(r"(?:pastel[^.]*palette|gentle pastel[^.]*)\.\s*", re.I)
# Everything the negative prompt already covers, and which CLIP truncated anyway.
_TAIL = re.compile(
    r"\s*(?:No photorealism[^.]*\.|no 3d render look[^.]*\.|"
    r"9\s*:\s*16 vertical\s*,?\s*no text\s*\.?|no text\s*\.?)\s*$", re.I)
# "Vertical 9:16 extreme wide shot," -> "extreme wide shot"
_SHOT = re.compile(r"^vertical\s+9\s*:\s*16\s+([^,]+?)\s*,", re.I)

MAX_TOKENS = 77

# SD1.5 has a very strong "tree" prior, and 001 asks for a 15 cm two-leaf sprout.
# Adjectives do not beat a prior — a negative prompt does. But this cannot be
# global: the growth ladder wants a man-height tree by 007a, so excluding "mature
# tree" everywhere would break the finale. These terms are added ONLY when the
# beat's own text says the subject is small.
_SMALL = re.compile(r"\b(sapling|seedling|sprout|two[- ]leaf|tiny|15\s*cm|40\s*cm|"
                    r"knee-high|small plant)\b", re.I)
SCALE_NEGATIVES = ("mature tree, large tree, tall tree, thick trunk, full canopy, "
                   "forest, bush, shrubbery")


# "no buildings, no people, no path" in a POSITIVE prompt asks for buildings,
# people and a path: SD1.5 has no notion of negation, it just sees the nouns. Beat 2
# of 001 said exactly that and came back blank (2026-07-26). These clauses are
# pulled out of the positive prompt and appended to the negative one, which is the
# only place a "not" means anything.
_NEGATION = re.compile(r",?\s*\bno\s+([a-z][a-z\- ]{1,24}?)(?=,|\.|$)", re.I)


def _negated_nouns(text: str) -> list:
    return [m.group(1).strip() for m in _NEGATION.finditer(text)]


# Some beats ARE the thing the standard negative prompt forbids. Beat 3 of 001 is a
# terminal resolving a line of output — its entire subject is text on a screen — and
# it came back (2026-07-26) as abstract magenta shapes, because `text` sits in the
# renderer's standard negative AND shots.md's boilerplate "no text" (which means "no
# burned-in caption") got extracted into the negative on top of it. Forbidding the
# subject twice is a reliable way to not draw it. When the shot is a screen, `text`
# has to come OUT of the negative — the caption ban belongs to render_t3, which
# draws captions itself, not to the image model.
_TEXT_SUBJECT = re.compile(
    r"\b(terminal|console|screen|monitor|cursor|spinner|logs?|stack trace|"
    r"code|command line|prompt line|dashboard|readout|sign|label)\b", re.I)


# Animagine XL 3.1 is trained on Danbooru captions, where the presence and number of
# PEOPLE is declared by a count tag — `1boy`, `1girl`, `multiple boys` — before anything
# else in the caption. Prose alone leaves the human optional: beat 4 of 001 asks for "a
# hunched man at a desk tipping sideways out of his chair" and on 2026-07-27 rendered the
# desk, the chair and the flying papers with NOBODY IN THEM. The furniture was correct
# and the man simply was not there. 93 of the genome's 177 prompts open on a person, so
# this is not an edge case; it is over half the show.
_MALE = r"man|men|boy|boys|he|his|him|father|husband|king|lord|gentleman"
_FEMALE = r"woman|women|girl|girls|she|her|mother|wife|queen|lady"
# Goblins, magistrates and assessors are people for framing purposes but their gender is
# not stated in the scripts, and `1other` is a real Danbooru tag for exactly this case.
_OTHER = (r"goblin|goblins|farmer|magistrate|assessor|scavenger|keeper|villagers?|"
          r"guards?|stranger|figure|silhouette|person|people|crowd|someone|child|children")
_PLURAL = r"\b(men|women|boys|girls|goblins|guards|villagers|people|crowd|children)\b"
# Only tags I am confident exist in the Danbooru vocabulary. "two patrol guards" is 2, not
# a crowd, so an explicit number is used when the prompt gives one; anything vaguer falls
# back to the "multiple"/"crowd" forms rather than inventing "3others".
_NUMBER = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _tag_from_clause(first: str) -> str:
    """The count tag for a single leading clause. Kept separate from count_tag() because
    compress() needs it on a clause it has already parsed — going back through compress()
    to find the clause would recurse forever."""
    # A possessive is not the subject. Beat 7 of 006a is a close-up of a ledger page
    # "beneath a woman's thumb" — a woman is present, but the page is the shot, and
    # declaring `1girl` would put a whole woman in it. Same for beat 14 of 002b, a
    # close-up of "a small goblin's clawed fingers": the hands are the subject, and beat 1
    # of 001 proves a pair of hands renders correctly with no count tag at all.
    plural = bool(re.search(_PLURAL, first, re.I))
    first = re.sub(r"\b[\w-]+'s\b", "", first)
    n = next((v for w, v in _NUMBER.items() if re.search(rf"\b{w}\b", first, re.I)), None)
    for pat, one, two, many in ((_MALE, "1boy", "2boys", "multiple boys"),
                                (_FEMALE, "1girl", "2girls", "multiple girls"),
                                (_OTHER, "1other", "2others", "crowd")):
        if re.search(rf"\b({pat})\b", first, re.I):
            if not plural:
                return one
            return two if n == 2 else many
    return ""


def count_tag(prompt: str) -> str:
    """The Danbooru count tag for this beat's subject, or "" if nobody is in it.

    Scoped to the first clause for the same reason as suppressed_negatives: "a hunched
    silhouette faintly reflected" in beat 2 is lighting, not a character, and declaring
    `1boy` there would put a man in a shot that is meant to be an empty terminal.

    Reads the tag off compress()'s output rather than re-deriving it from the raw prompt,
    so the two can never disagree — an earlier version re-parsed the compressed text and
    reported zero tags genome-wide, because the text it scanned already began with
    "1boy, " and a word boundary does not split "1boy".
    """
    m = re.match(r"(1boy|1girl|1other|2boys|2girls|2others|"
                 r"multiple boys|multiple girls|crowd),", compress(prompt)[0])
    return m.group(1) if m else ""


def suppressed_negatives(prompt: str) -> list:
    """Standard negative terms this beat's SUBJECT needs removed to be drawable.

    Scoped to the FIRST CLAUSE, because a passing mention is not a subject: beats 1 and
    4 of 001 say "faint monitor glow on his knuckles" and "cold monitor light" — the
    monitor is lighting, not the shot. Un-negating `text` for those would only invite
    the model to scribble gibberish signage into a shot that never asked for any.
    """
    body = re.sub(r"^[a-z ]*shot of ", "", compress(prompt)[0], flags=re.I)
    return ["text"] if _TEXT_SUBJECT.search(body.split(",")[0]) else []


def extra_negatives(prompt: str) -> str:
    """Negative terms this beat needs on top of the renderer's standard ones."""
    parts = []
    if _SMALL.search(prompt):
        parts.append(SCALE_NEGATIVES)
    parts += _negated_nouns(prompt)
    blocked = set(suppressed_negatives(prompt))
    return ", ".join(p for p in parts if p.lower() not in blocked)


_TOKENIZER = None
_TOKENIZER_TRIED = False


def _clip_tokenizer():
    """The real CLIP tokenizer if it is importable, else None.

    It always is where this matters: diffusers depends on transformers, so any
    environment that can render can also count exactly. The estimate below is
    only for callers that just want to inspect prompts.
    """
    global _TOKENIZER, _TOKENIZER_TRIED
    if not _TOKENIZER_TRIED:
        _TOKENIZER_TRIED = True
        try:
            from transformers import CLIPTokenizer
            _TOKENIZER = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        except Exception:
            _TOKENIZER = None
    return _TOKENIZER


def _token_estimate(text: str) -> int:
    """Token count: exact when the tokenizer is available, else approximate.

    The approximation is calibrated, not guessed. An earlier version counted every
    punctuation mark and doubled long words "to be safe", overestimated a 55-token
    prompt as over 77, and therefore dropped every action sentence — leaving the
    renderer nothing but style tags, which is strictly worse than the truncation it
    was meant to prevent. Being pessimistic about a budget is not free when the
    penalty for "too long" is deleting the content.
    """
    tok = _clip_tokenizer()
    if tok is not None:
        return len(tok(text)["input_ids"])
    words = len(re.findall(r"[A-Za-z']+", text))
    marks = len(re.findall(r"[^\sA-Za-z]", text))
    return int(words * 1.35 + marks * 0.5) + 2


def compress(prompt: str) -> tuple:
    """(compressed_prompt, list_of_dropped_sentences)."""
    text = " ".join(prompt.split())
    shot = ""
    m = _SHOT.search(text)
    if m:
        shot = m.group(1).strip()
        # "Vertical 9:16 shot," carries no framing information; ", shot," in the
        # tail is noise the model has to spend attention on
        if shot.lower() in ("shot", "shots"):
            shot = ""
    m = _STYLE_END.search(text)
    action = text[m.end():] if m else text

    # The style preamble comes in two shapes. Molted shot lists use the documented
    # long form ending in "gentle pastel palette."; older branch-node prompts are
    # prose that just opens with a shot-type sentence ("Vertical 9:16 shot, dusk.")
    # and may mention pastel late, which made the match above swallow the entire
    # action. If what survived is a small fraction of the original, the match was
    # in the wrong place: fall back to dropping only the FIRST sentence.
    if len(action) < len(text) * 0.35:
        first_break = re.search(r"(?<=[.!?])\s+", text)
        action = text[first_break.end():] if first_break else text

    for _ in range(2):   # the tail sometimes arrives as two sentences
        action = _TAIL.sub("", action).strip()
    # negations move to the negative prompt (see _NEGATION above)
    action = _NEGATION.sub("", action).strip().rstrip(",")

    # SUBJECT FIRST, style last. CLIP weights early tokens most heavily, so the
    # opening of the prompt becomes the composition. Leading with the style tag —
    # which I did to protect it from truncation, before compression made truncation
    # moot — got exactly what it asked for on 2026-07-26: "bold lineart, pastel,
    # soft watercolor background" drawn literally as cream squiggles on a green
    # wash, contrast 153 and no sapling anywhere in it. Vivid, and meaningless.
    # ORDER: subject, then framing, then style. Whatever leads becomes the
    # composition — leading with STYLE_TAG produced abstract lineart and no
    # sapling; leading with "macro shot." produced an extreme close-up of leaves
    # and no sapling either. The subject is the only thing that should be first.
    # FRAMING LEADS, but as the head of the subject's own noun phrase — "Medium shot
    # of a hunched man tipping out of his chair", not "Medium shot." then the subject.
    # As a trailing tag (", medium shot" at the end, where this used to be) framing has
    # almost no weight: on 2026-07-26 all four SDXL test beats came back as extreme
    # macro crops regardless of what they asked for, including a "medium shot" of a man
    # that rendered as a close-up of a chair. The earlier failure that pushed framing to
    # the end was a standalone leading SENTENCE ("macro shot.") which left the subject
    # stranded in third position; folding it into the phrase keeps the subject noun at
    # token 3-4, where it still governs the composition.
    tail = f", {STYLE_TAG}"
    # `head` is threaded through every token estimate below, so the framing prefix is
    # counted against the 77-token budget rather than pushing the prompt over it after
    # the fitting loop has already run.
    head = f"{shot[0].upper() + shot[1:]} of " if shot else ""
    dropped = []
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", action) if s.strip()]

    # The Danbooru count tag goes ahead of even the framing: it declares WHETHER there is
    # a person at all, which is prior to how they are framed. Two or three tokens, and
    # it is the difference between a man tipping out of his chair and an empty chair.
    if sentences:
        tag = _tag_from_clause(sentences[0].split(",")[0])
        if tag:
            # these prompts are read by humans in the provenance leaves, so keep the
            # capitalisation sane once the tag owns the front of the line
            head = f"{tag}, " + (head[0].lower() + head[1:] if head else "")

    # Drop trailing sentences until it fits — but NEVER below one. Style words
    # with no action is the failure this whole module exists to prevent, so the
    # first sentence is not negotiable.
    while len(sentences) > 1 and _token_estimate(head + " ".join(sentences) + tail) > MAX_TOKENS:
        dropped.append(sentences.pop())

    # If that one sentence is still too long (12 of the genome's 182 prompts open
    # with a 60+ token sentence), trim it at COMMA boundaries from the end. The
    # subject and verb live at the front of these sentences and the trailing
    # clauses are lighting and mood, so this loses the least — and it still never
    # cuts mid-phrase, which is exactly what CLIP's own truncation does.
    if sentences and _token_estimate(head + sentences[0] + tail) > MAX_TOKENS:
        clauses = [c.strip() for c in sentences[0].split(",") if c.strip()]
        while len(clauses) > 1 and _token_estimate(head + ", ".join(clauses) + tail) > MAX_TOKENS:
            dropped.append(clauses.pop())
        sentences[0] = ", ".join(clauses)
        if not sentences[0].endswith((".", "!", "?")):
            sentences[0] += "."

    body = " ".join(sentences).strip()
    if head and body:
        body = body[0].lower() + body[1:]
    out = (head + body).strip()
    if out.endswith("."):
        out = out[:-1]
    out = (out + tail).strip()
    return out, list(reversed(dropped))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_shots import parse_shots

    node = sys.argv[1] if len(sys.argv) > 1 else "001-capability-inventory"
    p = Path(__file__).resolve().parent.parent / "genomes/sapling/nodes" / node / "shots.md"
    for s in parse_shots(p.read_text()):
        text, dropped = compress(s["prompt"])
        print(f"\nbeat {s['num']:02d} {s['slug']}  ~{_token_estimate(text)} tokens")
        print(f"  {text}")
        if dropped:
            print(f"  DROPPED (too long): {' '.join(dropped)[:160]}")
