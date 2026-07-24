"""Caption chunking shared by render_t3 (burn-in) and synth_vo (timing).

Whole VO lines burned in as 4-6-line paragraph blocks read as homework on a
phone (loop cycle 001, defects 8/11/12): captions are short phrase units.
Lives in its own module so the TTS venv can import it without pillow."""

import re

CAPTION_MAX_WORDS = 7
GAG_PAREN_WORDS = 3  # parentheticals longer than this are always direction
_PRONOUNS = {"he", "she", "they", "it", "we", "i"}
_STAGE_VERBS = {"looks", "looking", "writes", "writing", "consults",
                "consulting", "stands", "standing", "turns", "turning",
                "points", "pointing", "nods", "nodding", "gestures",
                "gesturing", "pauses", "pausing", "glances", "glancing",
                "paces", "pacing", "beat", "whisper", "whispering",
                "muttering", "emerging", "wounded"}


def _is_direction(inner: str) -> bool:
    """Stage direction vs beat-gag. Direction is pronoun- or verb-led
    ('he writes', 'writing', 'consulting clipboard') or long; gags are the
    world's timed responses as noun phrases ('no leaf', 'nothing',
    'aggressively nothing') and stay in the caption."""
    words = inner.lower().split()
    if not words:
        return False
    if len(words) > GAG_PAREN_WORDS:
        return True
    return (words[0] in _PRONOUNS or words[0] in _STAGE_VERBS
            or words[0].endswith("ing"))


def split_caption_display(text: str) -> tuple:
    """(speech, directions) for a caption chunk. Stage-direction
    parentheticals leaking out of the script read as nonsense when burned
    in as dialogue (founder wince, 2026-07-25: 'this is literally just the
    script being put as dialogue'). They come OUT of the caption and render
    in the action style instead; beat-gag parentheticals stay inline."""
    directions = []
    def pull(m):
        inner = m.group(0)[1:-1].strip()
        if _is_direction(inner):
            directions.append(inner)
            return " "
        return m.group(0)
    speech = re.sub(r"\([^)]+\)", pull, text)
    speech = re.sub(r"\s+", " ", speech)
    speech = re.sub(r"—\s*—", "—", speech)          # residue of '— (…) —'
    speech = re.sub(r"^[—\s,]+|[—\s,]+$", "", speech)
    return speech, directions


def caption_chunks(text: str, max_words: int = CAPTION_MAX_WORDS) -> list:
    """Split a line into caption units: on sentence ends, then clause marks,
    then a hard word cap, so each unit rasterizes to <=2 lines at caption
    size. Never loses or reorders a word."""
    # parenthetical groups are atomic: never split inside '(...)' — a cap
    # boundary mid-parenthetical wrapped stage direction across chunks
    text = re.sub(r"\([^)]+\)", lambda m: m.group(0).replace(" ", "\x01"), text)
    units = []
    for sent in re.split(r"(?<=[.!?…])\s+", text.strip()):
        if not sent.split():
            continue
        sent_units, buf = [], []
        # a mid-line em dash ends its clause but stays VISIBLE (it carries
        # tone): \x00 marks the split point after it
        for clause in re.split(r"(?<=[,;:])\s+|\x00",
                               re.sub(r"\s+—\s+", " —\x00", sent)):
            for word in clause.split():
                buf.append(word)
                if len(buf) == max_words:
                    sent_units.append(" ".join(buf))
                    buf = []
            # a clause end past half the cap is a natural caption break
            if len(buf) > max_words // 2:
                sent_units.append(" ".join(buf))
                buf = []
        if buf:
            sent_units.append(" ".join(buf))
        # fold a 1-2 word remnant into its predecessor — WITHIN this
        # sentence only. Folding across sentences cascades: a run of tiny
        # sentences ('Newhaven!' '(no leaf) Greenrest?' …) re-assembles
        # into the very text wall chunking exists to prevent.
        if (len(sent_units) >= 2 and len(sent_units[-1].split()) <= 2
                and len(sent_units[-2].split()) + len(sent_units[-1].split()) <= max_words + 2):
            orphan = sent_units.pop()
            sent_units[-1] += " " + orphan
        units.extend(sent_units)
    units = [u.replace("\x01", " ") for u in units]
    return units or [text.replace("\x01", " ").strip()]


def chunk_spans(text: str, w0: float, w1: float) -> list:
    """Chunk a (display-ready) line and time each unit inside the window
    [w0, w1], proportional to word count: (chunk, start, end) triples.
    A word-count ESTIMATE — synth_vo writes measured timings into the VO
    manifest, which render_t3 prefers whenever present."""
    chunks = caption_chunks(text)
    total = sum(len(c.split()) for c in chunks) or 1
    spans, t = [], w0
    for c in chunks:
        dt = (w1 - w0) * len(c.split()) / total
        spans.append((c, t, t + dt))
        t += dt
    return spans
