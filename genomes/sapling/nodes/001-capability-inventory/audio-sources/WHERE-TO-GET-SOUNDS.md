# Where to get sound effects we can actually ship

Founder, 2026-08-03: *"can you find a proper online source for sound effects? non
copyrighted ones? shouldnt be so hard to find.."*

It is harder than it looks, and for one specific reason that has nothing to do with
money. Read that first, because it eliminates most of the internet's "free sound
effects" sites in one stroke.

## The reason most free libraries fail for us

Almost every royalty-free sound library licenses you to **use** a sound in a
production. Very few let you **redistribute the file itself**.

`banyan-city` does the second thing. The repo IS the product: `audio-sources/`
contains the actual `.ogg` and `.wav` files, committed, public, and downloadable by
anyone who clones. That is redistribution, and it is exactly what a
"use-in-your-project-but-don't-redistribute" licence forbids.

So the test is not "is it free?" It is:

1. **May we redistribute the original file?** (we commit it)
2. **May a reuser of our episode redistribute it too?** (we publish CC BY 4.0, which
   promises them that)
3. **Does it drag obligations onto the whole episode?** (share-alike does — excluded)

That leaves **CC0 / public domain**, and **CC BY** with credit. Same three-state logic
`vet_model.py` applies to model weights, for the same reason.

## Verified sources

Checked 2026-08-03 by reading the terms or querying the API, not from memory.

| source | licences | verified | notes |
|---|---|---|---|
| **Wikimedia Commons** | CC0, PD, CC BY, CC BY-SA | API queried; `Category:CC-Zero` and `Category:Audio files of sound effects` both reachable; a `filetype:audio` search returns real results | **What we already use.** Both current recordings came from here. Per-file licence is stated on the file page, which is what makes it quotable. |
| **Freesound** | CC0, CC BY, CC BY-NC | licence list read from their FAQ; filtered search URL returns HTTP 200 | Biggest catalogue of the three. **Must filter** — CC BY-NC is offered and is unusable for us. Their filter has a "Free Cultural Works approved" option, which is exactly CC0 + CC BY. |
| **`pipeline/sfx.py`** (ours) | n/a | in the repo | Synthesized with fixed seeds. No licence question at all and a re-render is bit-identical. Already carries the fan, wind, room hum and soil thumps. |

### Freesound, filtered to what we can use

```
https://freesound.org/search/?q=QUERY&f=license:"Creative Commons 0"
```

Swap `QUERY`. Check the licence on the file page before downloading anyway — the
filter is a convenience, not a guarantee, and the file page is the thing we can quote
in `SOURCES.md`.

## Deliberately not recommended

- **Pixabay** — their licence summary returned HTTP 403, so I could not read it. Its
  terms may well be fine; I will not recommend a licence I have not read. Same rule as
  the model gate.
- **BBC Sound Effects** — its RemArc licence is personal/educational only. Fails (1)
  and (2).
- **Sonniss GDC bundles, and commercial royalty-free libraries generally** — royalty
  free for USE in a production, typically forbidding redistribution of the source
  files. Fine for an ordinary video, wrong for a repo that publishes its assets.
- **Anything CC BY-SA** — share-alike would relicense the episode. This is why the
  fan and wind stay synthesized even though good recordings exist.
- **"No copyright" YouTube compilations** — the uploader usually has no right to
  grant anything. Unquotable, so unusable.

## Adding one

1. Get the file and note its **file page URL** and licence verbatim.
2. Add a row to `SOURCES.md` — file, what it is, source link, licence. If it is CC BY,
   name the creator; that credit reaches the episode automatically via
   `build_site.audio_credits()`.
3. Reference it from `clips/sound.yaml` with a `file:` key.
4. Run `python3 pipeline/lint_genome.py`. The gate fails on any shipping sound with no
   row in `SOURCES.md` — absence is a violation, not a note.

## What I actually tested, and what each one fails on

Three sources, real queries, licences checked per file. Recorded so nobody repeats it.

| source | open to us? | catalogue | verdict |
|---|---|---|---|
| **Freesound** | **NO** — see below | the right one: a real SFX library with a CC0 filter | **blocked. Needs a founder API token.** |
| **Wikimedia Commons** | yes, open API | 231 + 64 files in its two SFX categories, ~80 CC0/PD | thin. Zero hits for a computer fan spinning down; nothing for room tone. Full-text search is actively misleading — "footsteps" returns 2252 hits that are overwhelmingly **Wiktionary pronunciation files**, a person *saying* the word. |
| **archive.org** | yes, open API (`advancedsearch.php`) | huge — 4930 items for "fan" alone | **almost nothing declares a licence.** 0 of 30 "fan" results carried a `licenseurl`; no declared licence is UNVERIFIABLE, which our own gate calls a violation. The few free ones match on text, not sound — "footsteps" returns sermons titled *Following The Footsteps Of Christ*. |
| **Wiktionary / Lingua Libre** | yes | pronunciations only | wrong medium. Files are `LL-Q...-speaker-word.wav`: a human saying "gravel", not gravel. |

### Freesound: their terms, not our limitation

```
User-agent: *          Disallow: /search/   Disallow: /apiv2/
User-agent: ClaudeBot  Disallow: /
```

Search and the API are disallowed for every agent, and ClaudeBot is named with a
blanket disallow. The API requires a token; a token requires an account; account
creation is founder-reserved. Scraping a site that forbids it, in order to source
"properly licensed" audio, would defeat the point of this whole document.

**To unblock:** create a Freesound account, generate an API v2 token, and hand it
over. Their CC0 filter plus that token is the actual answer for fan spin-down, room
tone and soil footsteps — the three gaps `sfx.py` currently covers synthetically.

### Until then

`pipeline/sfx.py` is not a stopgap for these. Fixed seeds, no licence question, and a
re-render is bit-identical — which no downloaded file can claim. The two recordings
that ARE worth having (a real Model M keyboard, a real body thud) came from Commons
because those exist there. Fan hum and room tone do not.
