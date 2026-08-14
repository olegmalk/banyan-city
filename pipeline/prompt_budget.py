#!/usr/bin/env python3
"""Refuse to encode a prompt the text encoder would silently truncate.

WHAT THIS PREVENTS, and why it needs its own file.

Every video pipeline we call tokenizes with
`padding="max_length", max_length=max_sequence_length, truncation=True`.
Truncation there is COMPLETELY SILENT. Most diffusers pipelines keep an
`untruncated_ids` copy, diff it against the truncated one and log a
`removed_text` warning; LTX2's `encode_prompt` in diffusers 0.39.0 does
neither. Measured on the box 2026-08-14: a 2,601-token prompt came back as
exactly 1024 tokens with ZERO python warnings, ZERO stderr and ZERO stdout.
There is no channel on which we would be told. The prompt would simply stop
mid-sentence, the clip would render, the sidecar would publish the full text
we thought we sent, and the only evidence would be a shot that does not match
its own prompt.

HEADROOM AS MEASURED, so the next person knows whether this is theoretical:

  * LTX (`ltx_i2v.py`) — default limit 1024. 871 prompt files on the box, max
    684 tokens; 73 committed job specs, max 297. Worst case is 67% of budget,
    so this has never fired and is NOT a live defect. It is a number with no
    check next to it, which is how the other two silent failures found the
    same week got in.
  * Wan (`wan_i2v.py`) — default limit **226**, and several episode-1 prompts
    run 207-297 tokens. Wan is dormant (no job spec references it since the
    2026-07-27 pilot) so nothing has been lost, but reviving it with
    present-day prompt lengths WOULD silently drop text. This is the exposed
    path.

THE LIMIT IS READ, NEVER WRITTEN. `effective_max_sequence_length` pulls the
default straight out of `inspect.signature(pipe.encode_prompt)`. Hardcoding
1024 and 226 would mean a diffusers bump that changed either default moved
the cliff while our guard went on checking the old edge — the guard would
still pass and the truncation would still be silent, which is strictly worse
than no guard because it reads as covered. Reading the signature also makes
the check correct for free if we ever start passing `max_sequence_length=`
ourselves: pass that value as `explicit` and it wins, exactly as it would at
the call.

Pure stdlib on purpose — no torch, no diffusers, no transformers import — so
it loads inside the box's render venvs and is testable anywhere.
"""

import inspect

__all__ = ["PromptTooLong", "effective_max_sequence_length", "count_tokens",
           "check_prompt_budget"]


class PromptTooLong(RuntimeError):
    """The prompt does not fit and the encoder would have dropped the rest."""


def effective_max_sequence_length(encode_prompt, explicit=None) -> int:
    """The token limit THIS call will actually apply.

    `explicit` is whatever the caller passes as `max_sequence_length=`; when it
    is None the pipeline falls back to its signature default and so do we. The
    value is never written down in our source — see the module docstring.

    Raises if the number cannot be determined. That is deliberate: an unknown
    limit is precisely the state this module exists to end, and the failure is
    deterministic (it fires on the first encode after a diffusers bump removes
    or retypes the parameter, not at random), so it surfaces the change instead
    of hiding it behind a guard that silently stopped checking.
    """
    if explicit is not None:
        return int(explicit)
    try:
        params = inspect.signature(encode_prompt).parameters
    except (TypeError, ValueError) as e:      # C-implemented or unintrospectable
        raise PromptTooLong(
            f"cannot read max_sequence_length from {encode_prompt!r}: {e}. "
            "Refusing to encode: without the limit this call applies there is "
            "no way to tell a prompt that fits from one that is silently cut.")
    p = params.get("max_sequence_length")
    if p is None or p.default is inspect.Parameter.empty or not isinstance(
            p.default, int) or isinstance(p.default, bool):
        raise PromptTooLong(
            f"{getattr(encode_prompt, '__qualname__', encode_prompt)} has no "
            "integer default for max_sequence_length "
            f"(got {None if p is None else p.default!r}). The installed "
            "diffusers changed this signature; the truncation limit must be "
            "read from it, so update the caller to pass the value explicitly "
            "rather than guessing.")
    return int(p.default)


def count_tokens(tokenizer, text: str) -> int:
    """Tokens in `text` with truncation and padding OFF.

    Same tokenizer object the pipeline is about to hand the prompt to, so the
    count is the one the pipeline will produce and not an approximation from a
    different vocabulary. This is the `untruncated_ids` half of the comparison
    the other diffusers pipelines make and LTX2's does not.

    A LOWER BOUND, not an upper one: if a pipeline wraps the prompt in a chat
    template before tokenizing, the real count is this plus the template's few
    tokens. So the guard can pass a prompt that sits within a handful of tokens
    of the limit. It cannot do the reverse — anything it refuses really would
    have been cut — and at 684 of 1024 the margin is not where we live.
    """
    enc = tokenizer(text, padding=False, truncation=False,
                    add_special_tokens=True)
    ids = enc["input_ids"] if hasattr(enc, "__getitem__") else enc.input_ids
    if ids and isinstance(ids[0], (list, tuple)):   # batched shape
        ids = ids[0]
    return len(ids)


def check_prompt_budget(encode_prompt, tokenizer, texts, explicit=None,
                        job: str = "") -> int:
    """Refuse — loudly — if any text would be truncated. Returns the limit.

    `texts` is an iterable of (label, text) pairs; label names the file or the
    field so the error says WHICH prompt, not just that one was too long. Empty
    texts are skipped: an unused negative is not a defect.

    Refuses rather than trimming, and rather than warning. A warning inside a
    200-line render log is how this stays invisible for nine rounds of
    experiments, which is exactly what happened to the still-image encoder that
    threw away 80 of 157 tokens without erroring.
    """
    limit = effective_max_sequence_length(encode_prompt, explicit)
    over = []
    for label, text in texts:
        if not text:
            continue
        n = count_tokens(tokenizer, text)
        if n > limit:
            over.append((label, n))
    if over:
        where = f" [{job}]" if job else ""
        lines = [f"PROMPT TOO LONG{where}: the text encoder would DROP the "
                 f"overflow with no warning on any channel."]
        for label, n in over:
            lines.append(f"  {label}: {n} tokens > limit {limit} "
                         f"({n - limit} tokens of text would be LOST)")
        lines.append("Nothing was encoded. Shorten the prompt, or pass an "
                     "explicit max_sequence_length the model actually supports "
                     "— do not raise this guard's number on its own.")
        raise PromptTooLong("\n".join(lines))
    return limit
