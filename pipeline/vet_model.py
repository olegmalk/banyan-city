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
rights the source never granted. (Since 2026-08-03 those two are refused one step
earlier, by the rule that a tag with no readable text behind it is not a grant at
all — so they report UNVERIFIABLE, which is stricter. See CASES.)

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
import time
import urllib.error
import urllib.request
from pathlib import Path

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


def fetch_hf_licence_text(repo: str, siblings) -> tuple:
    """(filename, text) of a licence file in the HF WEIGHTS REPO itself.

    This was the hole. fetch_licence_text() reads GitHub only, and the sibling
    list was collected for DISPLAY but never read — so aidealab/AnimeGen-I2V,
    which ships a plain `LICENSE` on Hugging Face and has no GitHub mirror, had
    no text found at all. The weights repo is the most authoritative place a
    licence can live: it travels with the very files we load.

    ROOT ONLY, and that is the other half of the same lesson. Taking the first
    file whose name contains "LICEN" anywhere in the tree reads a VENDORED
    third-party licence as the repo's own grant. Both directions of that error
    are live on Hugging Face today, found 2026-08-04 while the audit in
    `pipeline/research/models-licence.md` was being recorded:

      - `IndexTeam/Index-anisora` — its only licence file is
        `reward/weights/bert-base-uncased/LICENSE`. BERT's Apache text was
        holding a CLEAR verdict on a repo that also ships the CogVideoX-based
        5B line, which is the exact laundering the audit flags.
      - `Kijai/WanVideo_comfy` — its only licence file is
        `LoRAs/Ditto/ditto_LICENSE.txt`, CC BY-NC-SA, so a 1.8M-download repo
        hard-failed for a reason with nothing to do with the weights in it.
        Right answer, wrong evidence, and it would have moved the day Ditto did.

    A licence three directories down governs what sits beside it, not what we
    load. No root file means no text found here, which fails closed.
    """
    for s in siblings or []:
        n = s.get("rfilename", "")
        if "/" in n:                            # vendored, not this repo's grant
            continue
        if "LICEN" in n.upper() or "COPYING" in n.upper():
            st, txt = get_raw(f"https://huggingface.co/{repo}/raw/main/{n}")
            if st == 200 and txt:
                return n, txt
    return None, ""


# Which vendored text covers which repos — EXACT SLUGS, mirroring the table in
# licences/README.md ("Wan 2.2 (TI2V-5B, I2V-A14B, Diffusers variants)").
#
# Written as an explicit list because the first version matched on filename
# resemblance: it split "Wan2.2-Lightning" on "-", took the stem "Wan2.2", found
# that inside "Wan2.2-LICENSE.txt", and applied Wan-AI's sha256-verified Apache
# text to lightx2v's LoRA weights — a different org entirely. That is licence
# LAUNDERING, and it manufactures permission rather than merely missing it, which
# is the more dangerous direction. Introduced and caught the same hour,
# 2026-08-03. Permission does not travel by names looking alike.
#
# Anything not listed here gets no vendored text and is judged on what can
# actually be read. Fails closed.
VENDORED_COVERS = {
    "Wan2.2-LICENSE.txt": (
        "wan-ai/wan2.2-ti2v-5b",
        "wan-ai/wan2.2-ti2v-5b-diffusers",
        "wan-ai/wan2.2-i2v-a14b",
        "wan-ai/wan2.2-i2v-a14b-diffusers",
        "wan-ai/wan2.2-t2v-a14b",
        "wan-ai/wan2.2-t2v-a14b-diffusers",
    ),
    # Added 2026-08-07 by the T5 licence check, and note WHICH slug it is. The
    # FastWan weights repo declares apache-2.0 with no LICENSE file and no
    # `repository` field, so the GitHub fallback below tries
    # "FastVideo/FastWan2.2-…" and never reaches hao-ai-lab/FastVideo, which
    # does ship the real text. That is a paper-trail hole, not a licence
    # problem, and this directory is the remedy the docstring already named.
    #
    # ONE slug, deliberately. The recipe in ACTION-PLAN T5 downloads the LoRA
    # from DeepBeepMeep/Wan2.2, and Kijai/WanVideo_comfy holds a byte-identical
    # copy — neither is listed and neither may be. They are 130- and 233-file
    # grab-bags spanning many origins, so covering a REPO with one work's text
    # is the same laundering the Wan2.2-Lightning near-miss above was: a
    # vendored licence covers a WORK, and the work here is FastVideo's.
    "FastVideo-FastWan-LICENSE.txt": (
        "fastvideo/fastwan2.2-ti2v-5b-fullattn-diffusers",
    ),
}


def _vendored_licence(repo: str):
    """(filename, text) from our own `licences/` archive, or None.

    Text we already fetched, read and sha256-verified against the canonical
    licence, committed so the reading survives the upstream repo being edited or
    deleted (every Wan 2.2 weights repo ships no LICENSE and the card's link
    404s — see licences/README.md).
    """
    d = Path(__file__).resolve().parent.parent / "licences"
    if not d.is_dir():
        return None
    slug = repo.strip().lower()
    for fname, covered in VENDORED_COVERS.items():
        if slug not in covered:
            continue
        f = d / fname
        if not f.is_file():
            return None
        try:
            return f.name, f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
    return None


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
    # WEIGHTS REPO FIRST — it is where the licence travels with the files we
    # actually load; then the authors' project repo, which is where Wan and many
    # others keep theirs.
    fname, text = fetch_hf_licence_text(repo, d.get("siblings"))
    if text:
        gh_slug = repo          # name the source honestly in the output below
    else:
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
        # A TAG WITH NOTHING BEHIND IT IS NOT A GRANT.
        #
        # classify_tag() calls "apache-2.0" clear, and the text logic above only
        # ever UPGRADES unverifiable->clear or downgrades to hard-fail. So a repo
        # declaring apache-2.0 in HF metadata while shipping no licence file
        # anywhere — weights repo, project repo, or our own archive — came back
        # CLEAR. That is the exact state this module's own docstring calls
        # unquotable, and that wan_i2v refuses to render with: found on
        # 2026-08-03 for lightx2v/Wan2.2-Lightning and Wan2.2-Distill-Loras,
        # both 'apache-2.0', both zero licence files. The tool contradicted the
        # rule it exists to enforce.
        #
        # `licences/` is a legitimate third source: text we fetched, read and
        # sha256-verified against the canonical licence, committed so the reading
        # survives the upstream repo changing. Wan2.2 itself is in there, and its
        # HF repo ships no licence file — so without this the fix would condemn
        # the model the tree already publishes from.
        vend = _vendored_licence(repo)
        if vend:
            fname2, text2 = vend
            hits2 = [w for pat, w in TRAVELLING_TEXT if re.search(pat, text2, re.I)]
            if hits2:
                state = "hard-fail"
                why = (f"vendored licence {fname2} contains travelling "
                       f"conditions: {'; '.join(hits2[:3])}")
            else:
                out_text = {"licence_text_file": f"licences/{fname2} "
                                                 f"({len(text2)}B, vendored+verified)"}
        elif state == "clear":
            state = "unverifiable"
            why = (f"tag says {tag!r} but NO licence text exists to quote — not in "
                   f"the weights repo, not at {gh_slug}, not in licences/. A "
                   f"self-declared tag is a claim, not a grant we can pass on")
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
    # CORRECTED 2026-08-04, and it is the same staleness as hum-ma below, found the
    # same way: this said "clear", and the 2026-08-03 no-text-behind-a-tag rule had
    # been returning "unverifiable" ever since without anyone re-running the live
    # self-test. Verified against the file at HEAD before touching it, so the
    # regression belongs to that rule, not to the root-only fix above.
    # FastWan's apache-2.0 was a tag with nothing quotable behind it: no LICENSE in
    # the weights repo, and its card declares no `repository`, so the GitHub
    # fallback tries `FastVideo/FastWan…` and never reaches hao-ai-lab/FastVideo,
    # which does ship a real Apache-2.0. The fix, if we ever want to render on it,
    # is to vendor that verified text into `licences/` the way Wan 2.2 already is —
    # never to loosen the rule.
    #
    # MOVED unverifiable -> clear 2026-08-07, and it is the fix above being taken,
    # not the rule being relaxed. The T5 licence check read
    # hao-ai-lab/FastVideo's LICENSE (10757B, operative sections 1-9
    # whitespace-identical to canonical Apache-2.0) and vendored it, so the text
    # now EXISTS to quote and the no-text-behind-a-tag rule is satisfied rather
    # than bypassed. Delete licences/FastVideo-FastWan-LICENSE.txt and this
    # returns to "unverifiable" on the next run, which is the property that makes
    # the change honest. Evidence: pipeline/research/models-licence.md, the
    # FastWan section.
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
    ("stabilityai/stable-video-diffusion-img2vid-xt-1-1", "hard-fail"),

    # ---- the Turbo chain, every link (models-licence.md, 2026-08-04) ---------
    #
    # The audit walked all four mirrors of the 4-step distill and UPHELD this
    # tool's refusal at each. All four are in here rather than one, because the
    # chain is the lesson: Apache-2.0 base -> CC BY-NC-SA 4.0 distill ->
    # unlicensed fp16 repack -> GGUFs declaring apache-2.0 again, with no act of
    # relicensing anywhere in between and by parties who never held the right.
    # And name the pull, because it is the strongest in the audit: these GGUFs
    # run in 4GB at 4 steps and the card recommends exactly our 704x1280.
    #
    # THE EXPECTED STATE MOVED, AND THE OLD ONE HAD GONE STALE. hum-ma was
    # recorded here as "hard-fail — laundering an NC base", verified live
    # 2026-08-02. The rule added 2026-08-03 — a tag with no readable text behind
    # it is a claim, not a grant — now fires first, so both GGUFs come back
    # UNVERIFIABLE and this self-test had been failing unnoticed since. Nothing
    # loosened: unverifiable is RANK 0, stricter than hard-fail, and main() exits
    # 1 on both. But note what the state cannot say. A leaf with no readable
    # licence is already at the bottom of RANK, so the transitive rule can never
    # worsen it to hard-fail — read the printed base chain, not the leaf's word.
    # It is quanhaol's NC + ShareAlike that makes these permanent, not the
    # missing file, and no upload by anyone downstream can cure it.
    ("hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF", "unverifiable"),
    # a verbatim clone of hum-ma's card, Civitai links and all — the same error
    # copied, not independent corroboration of its apache-2.0 claim
    ("Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF", "unverifiable"),
    # declares nothing at all, and is STRICTLY WORSE than the distill it
    # redistributes: the weights stay under BY-NC-SA, and because §3(a) obliges a
    # redistributor to pass the licence on, we get no grant from this one either
    ("yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers", "unverifiable"),
    # the fp16 repack both GGUFs were actually converted from
    # (`Wan22-Turbo/Wan2_2-TI2V-5B-Turbo_fp16.safetensors`), itself unlicensed.
    # Until the root-only fix above it hard-failed on a Ditto LoRA's licence.
    ("Kijai/WanVideo_comfy", "unverifiable"),

    # ---- laundering the same audit flagged elsewhere ------------------------
    #
    # One repo id, four model generations, and a repo id cannot express the
    # split. V2/V3/V3.1/V3.2 are Wan-based and Bilibili's Apache-2.0 grant over
    # them is sound — V3.2 is the audit's top 12GB pick. The `V1` / `5B` /
    # `5B_RL` folders declare that same apache-2.0 over a **CogVideoX-5B** base,
    # whose own licence is revocable, registration-gated for commercial use and
    # carries a field-of-use clause. So UNVERIFIABLE here is not doubt about
    # V3.2; it is this tool saying it cannot answer at repo granularity, which is
    # the honest answer. Bilibili's grant is prose in a GitHub README the HF card
    # does not link, so there is no text to quote either.
    ("IndexTeam/Index-anisora", "unverifiable"),
    # the CogVideoX-based 5B line relabelled into diffusers: apache-2.0 tag, no
    # text anywhere, base_model pointing back at the mixed repo above
    ("Disty0/Index-anisora-5B-diffusers", "unverifiable"),
    # THE MOST LIKELY ACCIDENTAL ADOPTION IN THE AUDIT, and it is here for that
    # reason. "FramePack is Apache-2.0 and runs in 6GB" is true of
    # `lllyasviel/FramePack`, the CODE. These are the WEIGHTS: no licence tag, no
    # LICENSE file, no base_model declared, and the `_HY` suffix over a
    # HunyuanVideo base whose Territory clause excludes the EU, UK and South
    # Korea — where we publish. A permissive repo licence read as though it
    # covered the weights is the textbook pattern, and the 6GB figure is exactly
    # what makes someone reach for it.
    ("lllyasviel/FramePackI2V_HY", "unverifiable"),
]


def self_test() -> int:
    # A RATE-LIMITED RUN LIES, AND IN THE MOST DANGEROUS WORDING THERE IS.
    # Unauthenticated api.github.com allows 60 requests/hour per IP and each case
    # spends roughly two walking its base chain, so the list below no longer fits
    # in one budget alongside ordinary use. When the limit is hit, get() returns
    # status 0, fetch_licence_text() finds nothing, and quanhaol — whose CC
    # BY-NC-SA text exists ONLY on GitHub — comes back "unverifiable: no licence
    # field declared". That is the precise sentence this tool exists to stop
    # anyone believing, and it cost two days once already. Hit live on 2026-08-04
    # by the run that added the Turbo-chain cases. So check the budget before
    # spending it: /rate_limit does not itself count against the budget.
    st, rl = get("https://api.github.com/rate_limit")
    left = ((rl.get("resources") or {}).get("core") or {}).get("remaining")
    need = 2 * len(CASES)
    if st == 200 and isinstance(left, int) and left < need:
        mins = max(0, int((((rl["resources"]["core"].get("reset") or 0)
                            - time.time()) // 60)))
        print(f"  NOT RUN — {left} unauthenticated GitHub requests left of 60/hour "
              f"and this needs ~{need}. Rate-limited, a hard fail degrades to "
              f"'no licence field declared', which is worse than no answer. "
              f"Reset in ~{mins} min.")
        return 2
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
                    help="check every recorded case live (needs network)")
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
