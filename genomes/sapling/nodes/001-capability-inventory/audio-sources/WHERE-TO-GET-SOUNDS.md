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
