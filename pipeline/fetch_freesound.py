#!/usr/bin/env python3
"""Fetch CC0-only sound effects from Freesound, with provenance, via the official API.

    export FREESOUND_TOKEN=...           # from https://freesound.org/apiv2/apply/
    python3 pipeline/fetch_freesound.py "computer fan" --want 5
    python3 pipeline/fetch_freesound.py "room tone" --want 3 --download 12345

WHY THE API AND NOT THE WEBSITE. Freesound's robots.txt disallows /search/ and
/apiv2/ for every agent and names ClaudeBot with a blanket disallow:

    User-agent: *          Disallow: /search/   Disallow: /apiv2/
    User-agent: ClaudeBot  Disallow: /

robots.txt governs CRAWLERS. An authenticated API client acting on the account
holder's own token is not a crawler — it is the documented, sanctioned way in, which
is why they issue tokens at all. Scraping the HTML search page would violate the
directive; using the API with the founder's key does not. Do not "fall back" to
scraping if the token is missing. Fail and say so.

CC0 ONLY BY DEFAULT, and that is not fussiness. This repo commits its audio files —
audio-sources/ is public and cloneable — and publishes CC BY 4.0, which promises
reusers they may redistribute too. So the test is "may we redistribute the file, and
may they?", which excludes:
  - CC BY-NC, which Freesound offers and which would make our commercial-reuse offer
    a lie for the whole episode
  - anything -SA, which would relicense the episode
CC BY is acceptable WITH credit (see SOURCES.md), but CC0 is preferred so a fork
inherits no obligation it has to track. Pass --allow-by to include CC BY.

Every download prints a ready-made SOURCES.md row. The licence gate fails on any
shipping sound with no row, so the row is not paperwork — it is the thing that lets
the sound ship.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
API = "https://freesound.org/apiv2"
UA = {"User-Agent": "banyan-city/1.0 (https://banyan.city; +authenticated API client)"}

# Freesound's exact licence strings, from their FAQ (read 2026-08-03). Their filter
# also offers a "Free Cultural Works approved" grouping, which is these two.
CC0 = "Creative Commons 0"
CC_BY = "Attribution"


def token() -> str:
    t = os.environ.get("FREESOUND_TOKEN", "").strip()
    if not t:
        sys.exit("FREESOUND_TOKEN is not set.\n"
                 "  Get one at https://freesound.org/apiv2/apply/ (founder's account —\n"
                 "  account creation and credentials are founder-reserved), then:\n"
                 "    export FREESOUND_TOKEN=...\n"
                 "  Do NOT scrape the website instead: their robots.txt forbids it.")
    return t


def get(path: str, **params):
    params["token"] = token()
    url = f"{API}{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=45) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        if e.code == 401:
            sys.exit(f"HTTP 401 — the token was rejected. Check it is the API key from\n"
                     f"  /apiv2/apply/ and not a Client id. Body: {body}")
        sys.exit(f"HTTP {e.code} from {path}: {body}")


def search(query: str, want: int, allow_by: bool, sort: str = "score"):
    """Licence-filtered search. Filtering SERVER-SIDE matters: it is the difference
    between reading a catalogue and downloading something unusable and deleting it."""
    lics = [CC0] + ([CC_BY] if allow_by else [])
    f = " OR ".join(f'license:"{l}"' for l in lics)
    d = get("/search/text/", query=query, filter=f"({f})",
            fields="id,name,license,duration,filesize,username,previews,url",
            page_size=min(want, 50), sort=sort)
    return d.get("results", []), d.get("count", 0)


def short_licence(lic: str) -> str:
    """The API returns a licence URL, the search FILTER takes a name.

    Both forms are handled because they arrive from different places: the filter
    string in search() must say 'Creative Commons 0', while every result carries
    'http://creativecommons.org/publicdomain/zero/1.0/'. The first version of this
    only matched the name, so a SOURCES.md row would have been written with a bare
    URL in the licence column — and that column is what the gate reads.
    """
    l = (lic or "").lower()
    if "/zero/" in l or "creative commons 0" in l:
        return "CC0"
    if "/publicdomain/" in l:
        return "Public domain"
    if "/licenses/by-nc" in l or "noncommercial" in l:
        return "CC BY-NC"          # refused downstream
    if "/licenses/by-sa" in l or "sharealike" in l:
        return "CC BY-SA"          # refused downstream
    if "/licenses/by/" in l or l.strip() == "attribution":
        return "CC BY 4.0"
    return lic or "UNKNOWN"


def sources_row(s: dict, fname: str) -> str:
    short = short_licence(s["license"])
    credit = "" if short == "CC0" else f" — credit {s['username']}"
    return (f"| `{fname}` | {s['name'][:48]} ({s['duration']:.1f}s) | "
            f"[{s['name'][:40]}]({s['url']}) by {s['username']} | "
            f"**{short}**{credit} |")


def download_preview(s: dict, dest: Path) -> Path | None:
    """The hq preview: 128kbps mp3, served without OAuth2.

    Originals need the full OAuth2 browser flow. For sound effects sitting at
    -20 LUFS under dialogue a 128k preview is not the limiting factor; if a hero
    sound ever needs the original, that is when to do the OAuth dance.
    """
    url = (s.get("previews") or {}).get("preview-hq-mp3")
    if not url:
        print(f"    no hq preview for {s['id']}")
        return None
    req = urllib.request.Request(url, headers={**UA, "Authorization": f"Token {token()}"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        print(f"    preview download failed ({e.code}) for {s['id']}")
        return None
    dest.write_bytes(data)
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--want", type=int, default=8)
    ap.add_argument("--sort", default="score",
                    choices=["score", "downloads_desc", "rating_desc", "duration_asc"],
                    help="score = relevance (default). downloads_desc surfaces popular "
                         "sounds that merely mention the words — 'computer fan' returned "
                         "Crashing Starship and Journey To The Interweb.")
    ap.add_argument("--allow-by", action="store_true",
                    help="include CC BY as well as CC0 (needs credit in SOURCES.md)")
    ap.add_argument("--download", type=int, default=0, metavar="ID",
                    help="download this sound id's hq preview into audio-sources/")
    ap.add_argument("--node", default="001-capability-inventory")
    ap.add_argument("--slug", default="", help="filename stem for the download")
    a = ap.parse_args()

    if a.download:
        d = get(f"/sounds/{a.download}/",
                fields="id,name,license,duration,filesize,username,previews,url")
        lic = short_licence(d["license"])
        if lic in ("CC BY-NC", "CC BY-SA", "UNKNOWN"):
            sys.exit(f"REFUSED: {a.download} is {lic}. NC would make our commercial-reuse "
                     f"offer a lie; -SA would relicense the episode.")
        stem = a.slug or f"freesound-{d['id']}"
        suffix = "cc0" if lic in ("CC0", "Public domain") else "ccby"
        out = (REPO / "genomes/sapling/nodes" / a.node / "audio-sources"
               / f"{stem}-{suffix}.mp3")
        got = download_preview(d, out)
        if got:
            print(f"  saved {got.relative_to(REPO)}  ({got.stat().st_size // 1024}KB)")
            print(f"\n  ADD THIS ROW to audio-sources/SOURCES.md — the gate fails without it:\n")
            print(f"  {sources_row(d, got.name)}")
        return 0

    results, count = search(a.query, a.want, a.allow_by, a.sort)
    lics = "CC0" + (" + CC BY" if a.allow_by else "")
    print(f"  {a.query!r} — {count} results under {lics}\n")
    if not results:
        print("  nothing. Try a broader query; Freesound tags are user-supplied.")
        return 0
    print(f"  {'id':>9}  {'dur':>6}  {'licence':<26} name")
    for s in results:
        short = short_licence(s["license"])
        print(f"  {s['id']:>9}  {s['duration']:>5.1f}s  {short:<26} {s['name'][:44]}")
    print(f"\n  then: python3 pipeline/fetch_freesound.py '{a.query}' "
          f"--download <id> --slug <name>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
