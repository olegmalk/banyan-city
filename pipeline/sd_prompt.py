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
STYLE_TAG = "anime cel shading, flat colour, bold clean lineart, 2d animation still, pastel"

# The style preamble ends at the first sentence break after the palette phrase.
_STYLE_END = re.compile(r"(?:pastel[^.]*palette|gentle pastel[^.]*)\.\s*", re.I)
# Everything the negative prompt already covers, and which CLIP truncated anyway.
_TAIL = re.compile(
    r"\s*(?:No photorealism[^.]*\.|no 3d render look[^.]*\.|"
    r"9\s*:\s*16 vertical\s*,?\s*no text\s*\.?|no text\s*\.?)\s*$", re.I)
# "Vertical 9:16 extreme wide shot," -> "extreme wide shot"
_SHOT = re.compile(r"^vertical\s+9\s*:\s*16\s+([^,]+?)\s*,", re.I)

MAX_TOKENS = 77


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

    # SUBJECT FIRST, style last. CLIP weights early tokens most heavily, so the
    # opening of the prompt becomes the composition. Leading with the style tag —
    # which I did to protect it from truncation, before compression made truncation
    # moot — got exactly what it asked for on 2026-07-26: "bold lineart, pastel,
    # soft watercolor background" drawn literally as cream squiggles on a green
    # wash, contrast 153 and no sapling anywhere in it. Vivid, and meaningless.
    tail = f", {STYLE_TAG}"
    head = f"{shot}. " if shot else ""
    dropped = []
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", action) if s.strip()]

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

    out = (head + " ".join(sentences)).strip()
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
