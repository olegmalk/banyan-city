# Loop cycle 013 — the night the farm learned to make video

**Opened:** 2026-07-30 night · **Closed:** pending founder screen
**Source:** founder's v7d notes + "find a completely free but high quality ai
video generator you can setup yourself", "why arent we using fish audio?",
"i still feel like this episode 1 remake can be hard to understand"

## The cut (v7e → v7f)

- **The fall is air-then-floor.** v7d's lone thump read late and thin; now a
  whoosh rises through the drop and a long, heavy `fall_impact` lands exactly
  on the cut to his last sight (the take has no impact frame — the cut IS the
  event). Placed against measured beat offsets, not by feel.
- **The "random weird wind" was the noise bed** running under every scene.
  It is now darker, quieter, and confined to the OUTDOOR world: silent from
  the cold open, breathing in with the sky.
- **"Huh. Blue." plays over the sky**, not black. The founder was right that
  naming the colour over a black frame wastes the line.
- **Speaker tags off for one-voice episodes.** Every caption read "THE TREE:"
  from the first frame — three independent cold readers took it for a
  captioning bug AND it spoiled the reincarnation ~40s early. Two-word fix,
  biggest comprehension win of the night.
- Drafted four replacements for the hospital-ceiling joke (clouds break the
  gag) — text only; the line is the author's call (R4).

## Cold reads: the answer to "is this hard to understand?"

Three naive readers (a phone viewer given only frames+captions, a script-only
story editor, a measurement-driven pacing editor) agreed:
1. **The death does not read.** Guesses: "he knocked his coffee over", "he
   fell asleep". Everything downstream depends on knowing he died.
2. **The middle drags**: 26–58s is static plates carrying four-word lines,
   including 12s of announcing an inventory that hasn't started. "Cold, on a
   phone, I would have swiped at 30 seconds."
3. **Nobody has a name** in 110 seconds.
Both (1) and (2) need script edits — logged for the founder, not taken.

## Free video generation: built, unattended

Four research lenses (web-sourced) then implemented as a farm task so the
Windows machine installed everything itself — no human at that keyboard.

- **Wan 2.2 TI2V-5B**, Apache 2.0 (clean for CC BY), native 704x1280 = our
  9:16, one ~10GB model where the 14B swaps two 8.5GB experts per stage.
- **Index-AniSora V3.2** is the find for the incoming 5090: Bilibili's
  Apache-2.0 Wan2.2 finetune trained on 10M+ ANIME clips, 8-step distilled.
- Open weights genuinely stop at Wan 2.2; "Wan 2.5/2.7 open source" pages are
  impersonators. Macs are out: a comparable M1 Max needed 82 min for 2s.

**Five one-clip canaries, four real bugs** (each would have eaten the night
if 15 clips had been queued up front):
1. `0xC0000005` access violation = RAM exhaustion (11GB text encoder +
   transformer + VAE in 16GB) → `--stage encode` writes embeddings and EXITS,
   the only reliable way to hand memory back on Windows.
2. Worker restarted only on `farm_worker.py` changes, so a new script ran
   against the old imported caller → fingerprint every `pipeline/*.py`.
3. cp1252, third casualty on that machine: a finished 25-minute encode died
   printing `encoded → path` → ASCII prints + utf-8 child env.
4. `enable_vae_tiling` absent on this pipeline in diffusers 0.39 → try the
   pipeline helper, then the VAE's own, then continue without.

## Voice

- **F5-TTS is the answer**: clones our own takes, **4.7s per line** on the
  M1 Pro — a whole episode is a coffee break. Samples delivered.
- **fish/OpenAudio**: two of three walls cleared (found the commit whose model
  class matches the checkpoint's config; pulled the 3.6GB weights), stopped at
  a pydantic schema bug in their own code. Parked with the exact diagnosis.

## Lesson

Canary-per-change is what made a blind remote install survivable: every one of
the four bugs was invisible from here except through the courier heartbeats,
and each cost one clip instead of one night. And when a machine "isn't
working", check whether the work has a consumer before inventing some.
