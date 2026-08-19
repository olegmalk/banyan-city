#!/usr/bin/env python3
r"""Count a prompt in REAL CLIP BPE tokens, offline, against animagine's own files.

WHY THIS EXISTS, AND IT CAUGHT ONE THE HOUR IT WAS WRITTEN.
composite-init-pattern.md 4 records the failure this guards: animagine's prompt
budget is 77 CLIP tokens and "beat 06/08's negative measured EXACTLY 77/77 and
any word added silently drops the tail". Nothing warns you. The clipped words are
the LAST ones, and every spec in this repo front-loads its defect terms precisely
because of that -- which only works if the count is known.

Specs have been claiming headroom by counting WORDS ("26 terms / 38 words,
comfortably under"). Words are not tokens: `ep2-b15-sapcomp-0819`'s first negative
was 29 comma-terms and measured 85 of 77, so eight tokens off its tail would have
been dropped in silence. It was trimmed to 71 with this tool before the spec was
filed, and the tool's control is the parent job whose negative it measures at 71
against that spec's own recorded claim of comfortable headroom.

NO transformers, NO torch, NO network. It implements CLIPTokenizer directly over
`vocab.json` and `merges.txt` from the model already in this machine's HF cache,
so it runs anywhere the model is present and costs nothing.

    python3 pipeline/clip_token_count.py --spec pipeline/jobs/<job>.yaml
    python3 pipeline/clip_token_count.py --text "a tiny sapling, two leaves"
    python3 pipeline/clip_token_count.py --file prompt.txt

Exit code is 1 if anything measured is over the ceiling, so it can gate a filer.
"""

from __future__ import annotations

import argparse
import functools
import glob
import json
import os
import re
import sys

CEILING = 77          # CLIP's context length, special tokens included
SPECIALS = 2          # <|startoftext|> and <|endoftext|>
CACHE_GLOB = (
    "~/.cache/huggingface/hub/models--cagliostrolab--animagine-xl-3.1/"
    "snapshots/*/tokenizer")

# CLIP's own pre-tokenizer pattern, with its unicode classes narrowed to the
# ASCII this repo's prompts are written in (every spec here is ASCII by policy --
# PYTHONUTF8 is set on the box for path safety, not for prompt text).
PAT = re.compile(r"<\|startoftext\|>|<\|endoftext\|>|'s|'t|'re|'ve|'m|'ll|'d"
                 r"|[a-zA-Z]+|[0-9]|[^\sa-zA-Z0-9]+", re.I)


def _tokenizer_dir() -> str:
    hits = sorted(glob.glob(os.path.expanduser(CACHE_GLOB)))
    if not hits:
        sys.exit("!! no animagine-xl-3.1 tokenizer in the HF cache. This tool "
                 "reads the MODEL'S OWN vocab and refuses to guess with another.")
    return hits[-1]


class Clip:
    def __init__(self):
        d = _tokenizer_dir()
        self.vocab = json.load(open(os.path.join(d, "vocab.json"), encoding="utf-8"))
        lines = open(os.path.join(d, "merges.txt"), encoding="utf-8").read().splitlines()
        merges = [tuple(l.split()) for l in lines[1:] if l.strip()]
        self.ranks = {m: i for i, m in enumerate(merges)}
        self.dir = d

    @functools.lru_cache(maxsize=None)
    def _bpe(self, token: str):
        word = tuple(list(token[:-1]) + [token[-1] + "</w>"])
        while len(word) > 1:
            rank, i = min((self.ranks.get((word[j], word[j + 1]), 1 << 30), j)
                          for j in range(len(word) - 1))
            if rank == (1 << 30):
                break
            word = word[:i] + (word[i] + word[i + 1],) + word[i + 2:]
        return list(word)

    def count(self, text: str):
        text = re.sub(r"\s+", " ", text.strip().lower())
        toks = []
        for piece in PAT.findall(text):
            toks.extend(self._bpe(piece))
        unknown = [t for t in toks if t not in self.vocab]
        return len(toks), unknown


def report(clip: Clip, label: str, text: str) -> bool:
    n, unknown = clip.count(text)
    total = n + SPECIALS
    state = "OK" if total <= CEILING else "OVER -- THE TAIL WILL BE DROPPED"
    print("%-14s %3d BPE + %d special = %3d of %d   %s"
          % (label, n, SPECIALS, total, CEILING, state))
    if unknown:
        print("%-14s unknown to this vocab: %s" % ("", unknown))
    if total > CEILING:
        # Name the words that fall off, because "it is over" is less useful than
        # "these are the terms you are about to lose".
        kept, seen = [], 0
        for piece in re.split(r"(,\s*)", text):
            seen += clip.count(piece)[0]
            if seen + SPECIALS <= CEILING:
                kept.append(piece)
        dropped = text[len("".join(kept)):].strip().lstrip(",").strip()
        print("%-14s DROPPED FROM THE TAIL: %s" % ("", dropped or "(mid-term)"))
    return total <= CEILING


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", help="a pipeline/jobs yaml; measures every "
                                   "prompt.txt / negative.txt in its payload")
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--text", action="append", default=[])
    a = ap.parse_args()
    if not (a.spec or a.file or a.text):
        ap.error("give --spec, --file or --text")

    clip = Clip()
    print("tokenizer: %s" % clip.dir)
    ok = True
    if a.spec:
        import yaml
        spec = yaml.safe_load(open(a.spec, encoding="utf-8"))
        payload = spec.get("payload") or {}
        found = False
        for key, text in payload.items():
            base = key.replace("\\", "/").rsplit("/", 1)[-1]
            if base in ("prompt.txt", "negative.txt"):
                ok &= report(clip, base, text)
                found = True
        if not found:
            print("no prompt.txt/negative.txt in this spec's payload")
    for path in a.file:
        ok &= report(clip, os.path.basename(path),
                     open(path, encoding="utf-8").read())
    for i, text in enumerate(a.text):
        ok &= report(clip, "--text[%d]" % i, text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
