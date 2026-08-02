#!/usr/bin/env python3
"""Vet a model's licence before it goes anywhere near an episode.

    python3 pipeline/vet_model.py FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers
    python3 pipeline/vet_model.py --self-test

Answers one question — may we publish output from this model under CC BY 4.0? —
in three states, and shows its working so a human can disagree with it.

WHY THIS EXISTS. Between 2026-07-31 and 2026-08-02 this project lost roughly two
days to licence archaeology done by hand, and every wrong turn was one of a small
number of repeatable mistakes:

  - f5-tts: CC BY-NC. An evening of tuning an engine we may never ship.
  - PixVerse free tier: personal-use only, and already inside a published episode.
  - LTX: the GitHub LICENSE is Apache and covers CODE ONLY; the weights ship under
    a custom licence that differs BY CHECKPOINT.
  - HunyuanVideo: a territory clause excluding the EU, where we publish.
  - AnimeGen: 69GB load peak, parked on a number read off the wrong document.
  - "no LICENSE file in the weights repo = unverifiable" — a rule that disqualified
    OUR OWN base model, which is already in the published episode.

THE TEST THAT ACTUALLY WORKS is not "is there a file" but "does the grant reach
the output, and is it traceable to someone with standing to give it":

  CLEAR         a grant traceable to the AUTHORS (weights-repo tag agreeing with
                the authors' project repo, which carries real text), containing NO
                OUTPUT CLAUSE, and every declared base_model is itself CLEAR.
  HARD FAIL     a real, author-traceable grant whose conditions TRAVEL to the
                output or to relicensing: NC, share-alike, OpenRAIL use
                restrictions, territory limits, no-training-on-output.
  UNVERIFIABLE  no author-traceable grant. Absence of a grant is not permission.

Apache 2.0 and MIT are CLEAR because they are SILENT about output — they grant
rights in "the Work" and say nothing about what you generate by running it. That
silence is the reason, not any affirmative permission. LTXV arrives at the same
place from the opposite direction, disclaiming output rights explicitly in §5.

TRANSITIVE RESOLUTION, the rule that catches deliberate laundering:

    Effective licence is the intersection along the base_model chain, never the
    leaf tag. Nobody can grant rights they do not hold, so a leaf tag MORE
    permissive than any declared base is affirmative evidence of a defect.

Verified live on 2026-08-02: hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF and
Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF both declare `license: apache-2.0` while
declaring `base_model: quanhaol/Wan2.2-TI2V-5B-Turbo` — which is CC BY-NC-SA 4.0.
A GGUF is a pure transform of the weights: no new training, no independently
licensable contribution, so there is no theory under which the quantizer acquired
rights the source never granted.

THE COMPLEMENT OF THAT RULE, and the one that caught me out:

    A permissive base plus a permissive method does NOT imply a permissive
    finetune. Read every node on its own terms.

quanhaol sits on an Apache base (Wan2.2-TI2V-5B) and credits an Apache method
(Self-Forcing), and is itself CC BY-NC-SA — which Apache expressly permits, since a
finetuner owns copyright in their own contribution and may license it more
restrictively. The transitive rule above catches a leaf claiming MORE than its
upstream; this catches a middle claiming LESS. Both directions are needed.

AND THE MISTAKE THAT MADE THIS TOOL NECESSARY TWICE: it first read only metadata
TAGS, called quanhaol "unverifiable — might clear if the author publishes terms",
and its self-test PASSED 5/5 on that wrong expectation. A green test asserting a
false ground truth is worse than no test: it manufactured confidence in a verdict
that could have put NC+ShareAlike material into a CC BY 4.0 episode. The repo ships
LICENSE.md, 19151 bytes, standard CC BY-NC-SA — NC, ShareAlike and
non-sublicensable all present, verified in the raw text. Text beats tag, always.

CAVEAT THIS TOOL MUST CARRY, or the transitive rule misleads: `base_model` is
self-declared and often absent. FastWan declares NONE while naming its base in
card prose. An empty base_model therefore reads as "upstream UNRECORDED", never
as "no upstream" — otherwise the check silently passes exactly the repos with the
worst provenance hygiene.

TWO API FACTS, both learned by getting them wrong:
  - HTTP 401 means nonexistent-OR-private, and those are byte-identical. It does
    NOT mean gated: a gated repo returns 200 with `gated: "auto"` and public
    metadata. Check the field, not the status.
  - Never trust a summarised fetch for an existence claim. A summarising fetch
    invented a "Wan-AI/Wan2.2-TI2V-5B-Turbo" that raw JSON shows does not exist,
    and refused to reproduce LTXV's clauses verbatim. This tool talks to the JSON
    APIs directly for that reason.

Reports, never decides. Adding a model to licence_gate.MODEL_LICENCES stays a
human act — R4 territory, and the founder has been right about these calls more
often than the steward.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request

HF = "https://huggingface.co/api/models/"
GH = "https://api.github.com/repos/"

# Permissiveness ordering, for the transitive comparison. Higher = grants more.
# Deliberately coarse: we only need "is the leaf claiming more than its base".
RANK = {
    "unverifiable": 0,
    "hard-fail": 1,          # real grant, but conditions travel
    "clear": 2,              # silent on output, or explicitly disclaims it
}

# Author-traceable and SILENT ON OUTPUT -> clear.
CLEAR_TAGS = {"apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause", "cc0-1.0",
              "unlicense", "isc", "cc-by-4.0"}
# Real grants whose conditions reach the output or force relicensing.
TRAVELS = ("nc", "sa", "nd", "openrail", "rail", "research", "non-commercial",
           "community", "other", "llama", "gemma")


def get(url):
    """Raw JSON, with the status. Never a summarised fetch — see module docstring."""
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:                                    # noqa: BLE001
        return 0, {}


# Phrases that mean "this grant reaches beyond the weights". Matched against the
# LICENCE TEXT, not a metadata tag — see fetch_licence_text().
TRAVELLING_TEXT = [
    (r"NonCommercial purposes only", "NC — bars commercial use of the material"),
    (r"\bNonCommercial\b", "NC clause present"),
    (r"same License Elements", "ShareAlike — forces adaptations onto the same terms"),
    (r"non-?sublicensable", "non-sublicensable — we cannot pass rights downstream"),
    (r"outside the Territory", "territory limit"),
    (r"to improve any other AI model", "no-training-on-output"),
    (r"research purposes only|academic or research", "research-only"),
    (r"expressly and intelligibly disclaiming", "mandatory machine-generated notice"),
]


def fetch_licence_text(slug: str) -> tuple:
    """(filename, text) of the first licence file in a GitHub repo root, or (None, "").

    LIST THE CONTENTS, then fetch. Do not probe raw paths: LICENSE, LICENSE.txt,
    LICENSE.md, COPYING all occur, and a 404 on a guessed name proves nothing. This
    is exactly how quanhaol/Wan2.2-TI2V-5B-Turbo was reported for two days as having
    "no licence at any filename" when it ships a 19KB LICENSE.md containing CC
    BY-NC-SA 4.0.

    And note what GitHub's own field does NOT tell you: spdx_id "NOASSERTION" means
    the detector COULD NOT CLASSIFY the file — commonly for CC texts and .md names.
    It carries no information about whether a file exists.
    """
    st, listing = get(GH + slug + "/contents/")
    if st != 200 or not isinstance(listing, list):
        return None, ""
    for x in listing:
        n = x.get("name", "")
        if "LICEN" in n.upper() or "COPYING" in n.upper():
            u = (f"https://raw.githubusercontent.com/{slug}/"
                 f"{x.get('path', n)}")
            for branch in ("main", "master"):
                st2, txt = get_raw(f"https://raw.githubusercontent.com/{slug}/"
                                   f"{branch}/{x.get('path', n)}")
                if st2 == 200 and txt:
                    return n, txt
    return None, ""


def get_raw(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:                                    # noqa: BLE001
        return 0, ""


def classify_tag(tag: str) -> tuple:
    """(state, why) for a licence tag alone, before provenance is considered."""
    if not tag:
        return "unverifiable", "no licence field declared"
    t = str(tag).lower()
    if t in CLEAR_TAGS:
        return "clear", f"{tag} — grants rights in the Work, silent on output"
    for bad in TRAVELS:
        if bad in t:
            return "hard-fail", (f"{tag} — a real grant whose conditions travel to "
                                 f"the output or force relicensing")
    return "unverifiable", f"{tag} — not on the known-clear list; read the text"


def vet(repo: str, depth: int = 0, seen=None) -> dict:
    """One model, resolved transitively along declared base_model."""
    seen = seen or set()
    pad = "  " * depth
    if repo in seen:
        return {"repo": repo, "state": "clear", "why": "already resolved (cycle)"}
    seen.add(repo)

    status, d = get(HF + repo)
    if status == 401:
        return {"repo": repo, "state": "unverifiable",
                "why": "HTTP 401 — nonexistent or private (these are "
                       "indistinguishable; 401 is NOT the gated signal)"}
    if status != 200:
        return {"repo": repo, "state": "unverifiable",
                "why": f"HTTP {status} from the model API"}

    card = d.get("cardData") or {}
    tag = card.get("license")
    state, why = classify_tag(tag)

    # TEXT BEATS TAG. The tag is a self-declared string; the text is the grant.
    # quanhaol declares NO tag on HF while its GitHub repo ships CC BY-NC-SA — so
    # tag-only reading called it "unverifiable, might clear later" when it is in
    # fact a permanent hard fail. Also: a permissive base does NOT imply a
    # permissive finetune. Apache lets a finetuner license their own contribution
    # more restrictively, and this one did exactly that on top of an Apache base
    # and an Apache method. Every node gets read on its own terms.
    gh_slug = (card.get("repository") or "")
    if gh_slug.startswith("https://github.com/"):
        gh_slug = gh_slug[len("https://github.com/"):].strip("/")
    else:
        gh_slug = repo          # many model repos mirror the org/name on GitHub
    fname, text = fetch_licence_text(gh_slug)
    if text:
        hits = [why2 for pat, why2 in TRAVELLING_TEXT if re.search(pat, text, re.I)]
        out_text = {"licence_text_file": f"{gh_slug}/{fname} ({len(text)}B)"}
        if hits:
            state = "hard-fail"
            why = (f"licence TEXT at {gh_slug}/{fname} contains travelling "
                   f"conditions: {'; '.join(hits[:3])}")
        elif state == "unverifiable":
            state, why = "clear", (f"no tag, but the text at {gh_slug}/{fname} has "
                                   f"no output/travelling clause")
    else:
        out_text = {}
    out = {"repo": repo, "tag": tag, "state": state, "why": why, **out_text,
           "gated": d.get("gated"), "downloads": d.get("downloads"),
           "licence_files": [s["rfilename"] for s in d.get("siblings", [])
                             if "licen" in s["rfilename"].lower()]}

    # the authors' project repo is where the TEXT usually lives — the weights repo
    # commonly has none, including for the model we already publish from
    gh = card.get("repository") or ""
    if gh.startswith("https://github.com/"):
        slug = gh[len("https://github.com/"):].strip("/")
        gs, gd = get(GH + slug)
        if gs == 200:
            out["upstream"] = slug
            out["upstream_spdx"] = (gd.get("license") or {}).get("spdx_id")
            cs, cl = get(GH + slug + "/contents/")
            if cs == 200 and isinstance(cl, list):
                names = [x["name"] for x in cl]
                out["upstream_licence_files"] = [n for n in names
                                                 if "LICEN" in n.upper()]
                out["upstream_notice"] = "NOTICE" in names

    # ---- transitive: nobody grants what they do not hold --------------------
    bases = card.get("base_model") or []
    if isinstance(bases, str):
        bases = [bases]
    out["base_model"] = bases or None
    kids = [vet(b, depth + 1, seen) for b in bases[:3]]
    out["bases"] = kids
    if not bases:
        # NOT "no upstream" — unrecorded. FastWan declares none and names its base
        # in prose, so treating empty as clean would reward bad hygiene.
        out["base_note"] = ("base_model UNRECORDED — not the same as none. Check the "
                            "card prose for a stated base before trusting this.")
    for k in kids:
        if RANK[k["state"]] < RANK[out["state"]]:
            out["state"] = k["state"]
            out["why"] = (f"leaf claims '{tag}' but its base {k['repo']} is "
                          f"{k['state'].upper()} — a leaf more permissive than its "
                          f"base is evidence of a defect, not a pass")
    return out


def show(r, depth=0):
    pad = "  " * depth
    mark = {"clear": "CLEAR       ", "hard-fail": "HARD FAIL   ",
            "unverifiable": "UNVERIFIABLE"}[r["state"]]
    print(f"{pad}{mark} {r['repo']}")
    print(f"{pad}             {r['why']}")
    for k in ("tag", "gated", "downloads", "licence_files", "upstream",
              "upstream_spdx", "upstream_licence_files", "upstream_notice",
              "base_model", "base_note"):
        if r.get(k) not in (None, [], ""):
            print(f"{pad}             {k}: {r[k]}")
    for b in r.get("bases") or []:
        show(b, depth + 1)


CASES = [
    ("FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers", "clear"),
    ("Wan-AI/Wan2.2-TI2V-5B-Diffusers", "clear"),
    # CORRECTED 2026-08-02: this was asserted as "unverifiable" and the self-test
    # passed 5/5 on that wrong expectation — a green test encoding a false ground
    # truth, which is worse than no test. It ships LICENSE.md, 19151B, CC BY-NC-SA
    # 4.0: NC, ShareAlike and non-sublicensable, all verified in the raw text. Not
    # "no grant found, might clear" but a permanent hard fail. The NC limit bites on
    # our USE OF THE WEIGHTS, so we never have to reach the unsettled question of
    # whether generated video is Adapted Material.
    ("quanhaol/Wan2.2-TI2V-5B-Turbo", "hard-fail"),
    ("hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF", "hard-fail"),      # laundering an NC base
    ("stabilityai/stable-video-diffusion-img2vid-xt-1-1", "hard-fail"),
]


def self_test() -> int:
    bad = 0
    for repo, want in CASES:
        r = vet(repo)
        ok = r["state"] == want
        print(f"  {'ok  ' if ok else 'FAIL'} {repo[:52]:54s} "
              f"got {r['state']:12s} want {want}")
        if not ok:
            bad += 1
            print(f"       why: {r['why']}")
    print(f"\n  {len(CASES)-bad}/{len(CASES)} as expected")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", help="HF repo id, e.g. org/model")
    ap.add_argument("--self-test", action="store_true",
                    help="check the five known cases, one per verdict state")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.repo:
        ap.print_help()
        return 2
    r = vet(a.repo)
    show(r)
    print()
    print("  This tool REPORTS. Adding a model to licence_gate.MODEL_LICENCES is a")
    print("  human decision (R4) — and the founder has been right about these more")
    print("  often than the steward has.")
    return 0 if r["state"] == "clear" else 1


if __name__ == "__main__":
    sys.exit(main())
