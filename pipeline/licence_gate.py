#!/usr/bin/env python3
"""Licence gate — nothing ships that we cannot publish under CC BY.

The tree publishes CC BY 4.0. Two licence families are therefore fatal to an
episode rather than merely awkward:

  - NON-COMMERCIAL (CC BY-NC and relatives, and every "free tier, personal use
    only" ToS). A CC BY release is a standing offer to commercial reusers; one
    NC input makes that offer a lie for the whole episode and for every fork
    downstream of it.
  - SHARE-ALIKE (*-SA). Mixing SA material in relicenses the episode under SA,
    silently changing the terms every node beneath it inherited.

Plus research-only weights, no-derivatives material (a fork-per-beat tree
cannot accept ND), and — the case that actually bit us — anything whose terms
nobody has written down. **Unknown is a violation, not a pass**, for pictures
exactly as much as for voice.

Why this exists (2026-08-01): the steward was one command away from voicing a
whole episode with F5-TTS, whose checkpoints are CC BY-NC, and had already
downloaded fish/OpenAudio, which is research-only. Nothing unpublishable
reached canon, but only by luck — no code would have stopped it. Provenance was
being published faithfully (§7.2) and read by nobody.

Two principles, learned from the four holes an adversarial audit opened in v1
(all four fixed here, each with a test in pipeline/test_pipeline.py):

  1. **Anything that ships carries a licence this gate recognises.** v1 resolved
     only VO *engines* against the model table; a clip sidecar naming a video
     model — or naming nothing at all — passed in silence, so footage from any
     model could ship unchecked. Now every provenance key (engine, model,
     still_model, platform, provider …) resolves the same way, and a compound
     field is judged by EVERY model it names, not by whichever name happened to
     be longest ("still: dreamshaper | motion: stable-video-diffusion" read as
     dreamshaper and passed 16 times).
  2. **Absence is never safer than presence.** v1 downgraded a shipping VO
     manifest with the 'engine' key *deleted* to an advisory, which made
     deleting a key the cheapest way past the gate. Missing provenance on a
     shipping asset is now a violation — a deleted field, a renamed file and a
     moved directory all raise scrutiny, never lower it. Only an explicit
     archive location (below) lowers it, and never to silence.

A second audit (2026-08-01, after v2) found four more silent passes, all of
them the SAME two principles leaking out through a container or a spelling.
Each is fixed below and has a test:

  5. **json got v1's narrow treatment while yaml got the sweep.** scan_vo_manifest
     read one key — data['engine'] — so `{"engine": "chatterbox", "model":
     "pixverse v6"}` passed, and a `"licence": "CC BY-NC 4.0"` inside a manifest
     was never read at all. Hole 1 again, one file format later. Manifests now go
     through the same per-record sweep as leaves and sidecars (_scan_records).
  6. **A pointer silenced the model standing next to it.** POINTER matched as a
     FRAGMENT and returned before the model table was consulted, so appending
     'see sources' to any value bought silence: `model: stable-video-diffusion —
     see sources` passed. A pointer is now honoured only when the value names no
     model at all; if it names one, the name wins.
  7. **Only .mp4 counted as a picture and nothing counted as a sound.** Footage
     coverage globbed '*.mp4', and audio had no coverage at all beyond the
     SOURCES.md tables — yet render_t3 muxes NN-*.{mp3,wav,m4a,aac,ogg} and
     build_site copies takes/clips/ with iterdir(), i.e. whatever is in it. So a
     synthesized VO mp3 whose NN-vo.json was never written, or a clip renamed
     .webm, shipped with provenance written nowhere. Both containers are now
     walked (VIDEO_EXT / AUDIO_EXT).
  8. **Two extensions were the coverage rule.** '*.yaml' and the exact name
     '*.meta.yaml' were hard-coded, so a sidecar saved as .yml, or a manifest
     renamed take-final.json, escaped both the sweep and the must-declare-
     provenance rule. Coverage is by suffix FAMILY now (RECORD_EXT), and the
     must-declare rule keys off '.meta.' anywhere in the name — because renaming
     a file is hole 2 wearing a different hat.

What counts as SHIPPING is derived from the two programs that decide what
reaches an audience, not from one hard-coded glob (hole 3). Read 2026-08-01:

  pipeline/build_site.py main() copies into _site/, i.e. onto banyan.city:
    - leaves/<content> for every leaf whose content ends .html/.mp4 — whatever
      the leaf's status: a superseded leaf's mp4 is still served at a stable URL
    - <slug>-media/        ← nodes/<n>/stills/*.png
    - <slug>-media-takes/  ← nodes/<n>/takes/stills/*.png
    - <slug>-media-clips/  ← EVERY file in nodes/<n>/takes/clips/ (iterdir —
      note: not a glob, so the extension is irrelevant; whatever sits in that
      directory is on the website)
    - trials/<platform>/   ← pipeline/t3-trials/outputs/*/*.mp4
  pipeline/render_t3.py assembles an episode from --clips <ANY dir>, globbing
    NN-*.mp4 (find_clips), NN-*.{mp3,wav,m4a,aac,ogg} (find_audio, AUDIO_EXT),
    NN-vo.json and sound.yaml out of it. So every directory holding per-beat
    footage is one command away from a published episode — including
    takes/clips/, which the live 001-t3-d leaf assembles from.

Therefore: every record file (yaml / yml / json — RECORD_EXT) under genomes/
and under the trial gallery's outputs/, plus every moving-image and audio file
those two roots contain, judged as SHIPPING unless the path passes through an
archive directory (`archive/`, `archive-*/`, `*-archive/` — the repo's own
convention for superseded material kept under R6). Archived assets are
advisory, because they are not served and not globbed as per-beat footage — but
they are always named out loud, and promoting one back is a violation the
moment it moves.

Known gap, stated rather than hidden: still images carry no per-file
provenance anywhere in the tree (162 .png, 0 sidecars). Their model is recorded
once in each leaf's `still_model` and once as a constant in still_local.py, both
of which this gate reads — but a png dropped into stills/ by hand is invisible
to it. A stills manifest would close that; it does not exist yet, so .png is
deliberately absent from VIDEO_EXT / AUDIO_EXT below: the walk covers every
container it can hold to account, and this one gap is named here rather than
papered over with a rule that would fire 162 times and be muted on day one.

Used by pipeline/lint_genome.py (so CI fails on a violation). Runnable alone:
    python3 pipeline/licence_gate.py
"""

import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


def normalise(text) -> str:
    """Licence text is prose in the wild ('**CC BY 4.0** — credit Gravity
    Sound'), so every comparison happens on a normalised form: lowercase, each
    run of non-alphanumerics collapsed to a single '-'."""
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


# Checked FIRST and always. A deny family stays denied however the string is
# dressed up, so 'CC BY-NC 4.0' can never fall through to the CC BY allowance.
DENY = [
    (r"non-?commercial|\bnc\b|by-nc",
     "non-commercial — the tree publishes CC BY 4.0, which offers commercial "
     "reuse this asset forbids"),
    (r"share-?alike|by-sa|-sa\b|\bsa\b",
     "share-alike — it would relicense the whole episode and every fork "
     "downstream of it"),
    (r"research-only|research-use|academic-use|research-purposes|non-research",
     "research-only — not licensed for a published work"),
    (r"no-?deriv|by-nd|\bnd\b",
     "no-derivatives — a fork-per-beat tree is nothing but derivatives"),
    # the free-tier ToS family: legal to generate with, not legal to publish.
    # This is how a video service says NC without using the word (PixVerse,
    # Kling, Vidu — DECISIONS.md D8 research, 2026-07-19).
    (r"personal-use|personal-only|no-commercial-use|not-for-commercial",
     "personal-use only — a tree published under CC BY is not personal use"),
]

# Publish-safe identifiers. An allowlist, not a plausibility heuristic: a
# licence nobody has written down here is a licence nobody has read.
ALLOW = [
    (r"public-domain|\bpd\b|pd-mark|no-known-copyright", "public domain"),
    (r"\bcc0\b|creative-?commons-zero", "CC0"),
    (r"\bcc-?by(-\d+(-\d+)?)?\b", "CC BY"),        # bare attribution; -NC/-SA/-ND denied above
    (r"\bapache-2(-0)?\b", "Apache-2.0"),
    (r"\bmit\b", "MIT"),
    (r"\bbsd(-[23]-clause)?\b", "BSD"),
    # Weights licences that grant commercial use and claim nothing over the
    # OUTPUT. Their conditions (OpenRAIL's use restrictions, FAIPL's copyleft)
    # bind redistribution of the model; we never redistribute weights, we
    # publish frames. Both are on the allowlist because someone read them —
    # which is the only qualification this list has ever had.
    (r"openrail", "CreativeML OpenRAIL-M"),
    (r"\bfaipl\b", "Fair AI Public License 1.0-SD"),
    # A hosted service's terms, not a weights licence: the provider assigns the
    # customer commercial rights in the output. Every entry that uses this token
    # must say in its comment WHERE that grant is recorded — the token is a
    # citation, not a shrug, and the PixVerse entry below is what it looks like
    # when a provider does the opposite.
    (r"commercial-output-grant", "provider grant of commercial output rights"),
]

# Model / engine / service name (normalised, matched as a fragment) → the
# licence its output ships under. The names are what the manifests actually
# write, e.g. 'chatterbox-0.5B', 'f5-tts-v1-base', 'alibaba-model-studio'.
# Values are kept short and token-like on purpose: DENY/ALLOW match them as
# text, so prose in a value can match by accident. Reasoning goes in comments.
MODEL_LICENCES = {
    # ---- voice engines -------------------------------------------------
    "chatterbox": "MIT",
    "kokoro": "Apache-2.0",
    "f5-tts": "CC-BY-NC-4.0",           # the near-miss: publish-safe it is NOT
    "openaudio": "research-only, non-commercial",
    "fish": "research-only, non-commercial",   # fish-speech == OpenAudio weights
    "voxcpm": "Apache-2.0",
    # Verified SEPARATELY from voxcpm (2026-08-01), against the cached model
    # card: "Apache-2.0 license, free for commercial use". Listed on its own
    # even though the substring 'voxcpm' already matched it — because that match
    # would have been an ACCIDENT. A new release inherits the licence of any
    # allowed model whose name is a prefix of its own, so a VoxCPM3 shipped
    # under non-commercial terms would be waved straight through. The matcher
    # is substring-based on purpose (it has to survive 'still: X | motion: Y'
    # provenance strings), so the safeguard is this table: add every new
    # version explicitly, after reading ITS licence, and never rely on the
    # prefix. The direction that bites is always allow-by-inheritance.
    #
    # THE SAFEGUARD IS NO LONGER DISCIPLINE (2026-08-08). Everything above still
    # describes the right practice, but the last three sentences described the
    # matcher of the day and it has been replaced: keys match whole TOKENS now,
    # and a version fused onto a key (`voxcpm3` for `voxcpm`) grades as a
    # variant, so an allowance does not reach it — `VoxCPM3` fails closed with
    # nobody having to remember this paragraph. Compound 'still: X | motion: Y'
    # strings still work, by identifier rather than by substring. Adding the
    # version explicitly is still the right move, and it is now what MAKES the
    # string resolve rather than what stops it going wrong: this key is why
    # `voxcpm2` answers for itself instead of falling to `voxcpm`'s doubt.
    "voxcpm2": "Apache-2.0",
    # CORRECTED 2026-08-02, twice. First recorded as "unverifiable, nothing to
    # read" — wrong: quanhaol/Wan2.2-TI2V-5B-Turbo ships LICENSE.md, 19151 bytes,
    # standard CC BY-NC-SA 4.0. Verified in the raw text: "for NonCommercial
    # purposes only", "non-sublicensable", and ShareAlike via "same License
    # Elements". GitHub's spdx_id says NOASSERTION, which means its detector could
    # not CLASSIFY the file — it says nothing about whether one exists, and reading
    # it as "no file" is how this hid for two days.
    # It is a permanent hard fail, not a maybe: the NC limit bites on our USE OF THE
    # WEIGHTS, so we never reach the unsettled question of whether generated video
    # is Adapted Material. Technically it was the ideal model — 4-step, CFG-free,
    # real i2v. Rejected on licence, not merit, and never worth revisiting.
    # Its GGUF mirrors (hum-ma, Kiijoku) declare apache-2.0 over this base: a leaf
    # cannot grant what its base withholds.
    "quanhaol": "CC-BY-NC-SA-4.0",
    # ---- video models whose licence was READ, 2026-08-01 -------------------
    # AnimeGen-I2V (aidealab): LICENSE file verified byte-identical to canonical
    # Apache-2.0 through all nine operative sections, front matter tags
    # `commercial-use`. An anime finetune of Wan 2.2 that force-prepends
    # "Japanese anime style" and negatives out 3d/cg/photo — it fails TOWARD
    # anime, which is the drift direction we want.
    # Undisclosed training data: not a licence problem (the LICENSE is clean) but
    # worth logging under §7.2 that we cannot say what it learned from.
    "animegen": "Apache-2.0",
    "aidealab": "Apache-2.0",
    # Deliberately ABSENT and not to be re-proposed without reading D13:
    #   ltx / lightricks  — weights ship under THREE licences by version; the 2B
    #                       is "academic or research purposes only, and explicitly
    #                       excludes commercialization", and the GitHub LICENSE
    #                       that looks like plain Apache-2.0 covers CODE ONLY.
    #   hunyuanvideo      — Tencent community licence §5(c) excludes the EU, UK
    #                       and South Korea from the permitted Territory. We would
    #                       breach it by publishing at all, before any downstream
    #                       question, since banyan.city is visible in the EU.
    # ---- open image / video weights ------------------------------------
    # v1 called this one an ADVISORY, on the premise that it was "already on
    # disk in superseded takes". That premise was false, and the audit proved
    # it: 15 of the 16 SVD sidecars are in nodes/001-capability-inventory/
    # clips/ — the live per-beat footage directory render_t3 assembles from —
    # and the 16th is in takes/clips/, which build_site publishes verbatim.
    # The advisory is withdrawn. SVD shipped (2023-11) under the Stability AI
    # Non-Commercial Research Community License; Stability later moved several
    # models onto a "Community License" that permits commercial use only BELOW a
    # revenue threshold. WHICH of the two governs these weights has not been
    # read off Stability's own page by anyone here — and it does not change the
    # verdict, which is why the value below is unchanged: under the first, the
    # footage is non-commercial outright; under the second, our CC BY 4.0
    # release would be offering every downstream reuser rights the cap does not
    # give us (the same defect as ltx-video, below). A revenue-capped grant
    # cannot back an uncapped offer. Someone must still read it and record which
    # one applies — as a fact, not as grounds for a lower threshold.
    "stable-video-diffusion": "Stability AI non-commercial research community licence",
    # NOW READ, end to end (2026-08-01), from the raw file rather than a
    # summariser: LTXV Open Weights License 0.X, dated 2025-04-15, which its own
    # header applies to "all LTXV model versions released since April 15, 2025".
    # Our takes are 2026-07 and load Lightricks/LTX-Video unpinned, so this is
    # the operative text.
    #   §5: "Licensor claims no rights in the Output you generate using the Model."
    #   §1.8: Output is "the results of operating a Model".
    #   §2: the $10,000,000 annual-revenue threshold decides who must buy a
    #       COMMERCIAL USE AGREEMENT for the Model. Every granted verb in §2
    #       takes "the Model" as its object; §3's redistribution conditions are
    #       likewise scoped to "the Model or Derivatives of the Model"; and §1.4
    #       defines Derivatives model-to-model only (weights/activations
    #       transferred into another model, distillation, synthetic training
    #       data). A rendered video is Output, not a Derivative.
    # So the cap gates the WEIGHTS, not the footage — which means the note above
    # about stable-video-diffusion ("a revenue-capped grant cannot back an
    # uncapped offer") does NOT transfer to this one: that argument holds where a
    # cap constrains output distribution, and here it constrains who may run the
    # model. We are at zero revenue either way.
    # STILL NOT FLIPPED TO ALLOW, deliberately. Nobody here is a lawyer, moving
    # an entry to allow is the direction that publishes things, and the two
    # affected files are unused trial takes of beat 1 — so waiting costs nothing
    # and the founder gets to make the call with the text in front of him (D13).
    # Attachment A(e) additionally forbids disseminating output "without
    # expressly and intelligibly disclaiming that the ... content is machine
    # generated" — an obligation on US, which the §7.2 sidecars already meet.
    # Terse, for the same reason as google-flow below: this value is classified,
    # not just printed. The reading lives in the comment above and in MODEL_NOTES.
    "ltx-video": "LTXV Open Weights Licence 0.X (read; founder sign-off pending)",
    # LTX-2/2.3 ARE NOT 0.X, and the bare 'lightricks' key was labelling them as
    # such. normalise("Lightricks/LTX-2.3-fp8") is "lightricks-ltx-2-3-fp8" — the
    # dot becomes a dash — so a 2.3 sidecar matched this catch-all and nothing
    # else, and got reported under the wrong document: 0.X is a different licence
    # from the LTX-2 Community License Agreement, which carries a 20-item use
    # schedule that 0.X does not have (D16). It failed SAFE — both are non-allow,
    # so the clip was refused either way — but a gate that refuses for the wrong
    # reason teaches the wrong fix to whoever reads the message.
    # So: 2.3 is explicit, and the catch-all no longer names a version it cannot
    # know. Same rule the voxcpm2 entry above exists to enforce — add every
    # version after reading ITS licence, never inherit by prefix.
    # The catch-all below deliberately keeps the IDENTICAL string to ltx-video
    # rather than a version-agnostic wording, and that is load-bearing, not lazy:
    # our archived LTX-Video takes match BOTH keys, and check_model reports one
    # violation per distinct LICENCE (dict.fromkeys over the values), not per key.
    # Giving the two keys different strings split every such asset into two
    # violations and pushed the debt ratchet 38 -> 40 — a reporting artifact, with
    # no new unpublishable thing in the tree. Raising the ceiling to absorb that
    # would be exactly the "loosen the ratchet" move the ratchet exists to stop.
    # So the nuance lives in MODEL_NOTES, which is printed and never classified —
    # the same split the google-flow comment above prescribes.
    #
    # ADDING THE KEY WAS NOT ENOUGH, which is the 2026-08-08 half of this entry.
    # model_licences() ordered its hits by KEY LENGTH, so on a string naming both
    # — `diffusers/LTX-2.3-Distilled-Diffusers (Lightricks LTX-2.3 distilled,
    # bf16)`, which is exactly what video_task writes — the 10-character catch-all
    # still outranked the 7-character version key, and engine_licence() handed
    # publishable() the 0.X document again. The specific entry existed, was
    # correct, and lost on spelling: the mislabel this comment was written to
    # prevent went on happening for three days underneath the fix for it.
    # Which key wins is DECLARED now, in SUPERSEDES_CATCH_ALL below, and no longer
    # inferred from how many letters a vendor's name happens to have.
    "ltx-2-3": "LTX-2 Community Licence Agreement (D16; watch-only, sign-off pending)",
    "lightricks": "LTXV Open Weights Licence 0.X (read; founder sign-off pending)",
    "dreamshaper": "CreativeML-OpenRAIL-M",      # SD1.5 derivative; outputs unrestricted
    # animagine: THE RECORD WAS STALE, AND IT WAS CLEARING EVERY STILL WE SHIP.
    #
    # This said "faipl-1.0-sd; outputs unrestricted", which was true of an earlier
    # version of the repo. cagliostrolab/animagine-xl-3.1's own card now reads:
    # "This model is licensed under the CreativeML Open RAIL++-M License… Note:
    # This license supersedes any previous community license tags (e.g., FAIPL)."
    # HF's tag agrees: openrail++. And this very file already lists r"openrail" as
    # a licence whose conditions travel — so the gate held two records that
    # contradicted each other, and the permissive one won on every asset.
    #
    # Read the actual text (SDXL LICENSE.md, 14105 bytes, sha256 19b6998b…):
    #   "Except as set forth herein, Licensor claims no rights in the Output You
    #    generate using the Model."          <- no ownership claim. Good.
    #   "No use of the output can contravene any provision as stated in the
    #    License."                          <- but its USE is bound to
    #                                          Attachment A's restrictions.
    # We publish CC BY 4.0, which offers reusers unrestricted use. We cannot
    # grant what we do not hold, and we cannot silently pass the restriction on.
    # Same shape as the google-flow finding in D13, and it lands on EVERY
    # approved still, because animagine drew all fifteen.
    #
    # Recorded as what it is rather than quietly allowed or quietly failed: the
    # founder decides whether to narrow our own offer (D13) or re-draw the stills
    # on a model whose grant we can pass on. Naming it here makes it visible in
    # the debt count instead of invisible behind a stale tag.
    "animagine": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
    "cagliostrolab": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
    "ip-adapter": "Apache-2.0",
    # Open Wan weights (Wan-AI/Wan2.x) are Apache-2.0. The hosted preview
    # models (wan2.5/2.6/2.7 via Model Studio) publish no weights, so what
    # actually licenses their output is the platform grant on the next line —
    # every record naming one also names its platform, and both are checked.
    "wan": "Apache-2.0",
    # ---- hosted services: the licence IS the provider's terms -----------
    # Alibaba Model Studio (Qwen/Wan API): terms assign generated content to
    # the user, and DECISIONS.md D8 (2026-07-19, adversarial web research)
    # recorded this route as "genuinely free, watermark-free, publishable".
    "alibaba-model-studio": "provider terms: commercial-output-grant",
    "fal-ai": "provider terms: commercial-output-grant",   # paid API, output to the customer
    "hailuo": "provider terms: commercial-output-grant",   # MiniMax via fal
    "minimax": "provider terms: commercial-output-grant",
    "claude": "provider terms: commercial-output-grant",   # Anthropic: output rights to the customer
    # The counter-example. DECISIONS.md D8: "Kling/Vidu/PixVerse free tiers are
    # license-blocked (personal-use-only ToS), not quality-blocked." The tree's
    # own research wrote this down and then five beats of the live 001-t3-d cut
    # were assembled from PixVerse takes anyway.
    "pixverse": "free-tier ToS: personal-use only, non-commercial",
    "kling": "free-tier ToS: personal-use only, non-commercial",
    "vidu": "free-tier ToS: personal-use only, non-commercial",
    # Veo via Google Flow. The terms ARE now read (2026-08-01) and "unread" was
    # the wrong reason — but the verdict does not move, for better reasons.
    # There is no Flow- or Labs-specific terms document: policies.google.com's
    # service-specific index lists Labs.google against only the main ToS and the
    # generative-AI use policy; labs.google/terms is a 404; the old
    # terms/generative-ai page has deferred to the main ToS since 2024-05-22. So
    # the governing text is the Google ToS, and in it:
    #   - Ownership is answered: "Some of our services allow you to generate
    #     original content. Google won't claim ownership over that content."
    #   - Commercial use is NEITHER granted NOR forbidden. The word "commercial"
    #     appears once in the whole document, defining "consumer". Silence.
    #   - But under "Don't abuse our services" two conditions attach to the
    #     OUTPUT: no "using AI-generated content from our services to develop
    #     machine learning models", and no "misleading others into thinking that
    #     generative AI content was created by a human". Flow also embeds a
    #     SynthID watermark that "should not be tampered with or removed".
    # CC BY 4.0 offers reusers "any purpose, even commercially" with no such
    # carve-outs — training explicitly included. We cannot pass through
    # conditions we were given, so we cannot honestly make the CC BY offer over
    # this footage. That is the real blocker, and it is a judgement about what we
    # warrant to reusers rather than missing text. Independently, all three trial
    # files record `watermark: true` (visible Flow sparkle, bottom-right), which
    # disqualifies them from published material on its own — which is what D8
    # actually meant by "trials only".
    # KEEP THESE VALUES TERSE AND NAME NO OTHER LICENCE. This value is fed to
    # classify(), which greps it for licence identifiers — so a first draft of
    # this entry that explained itself with the words "cannot pass through a
    # CC BY 4.0 offer" matched the CC-BY allow pattern and silently made six
    # Flow files publishable. An explanation became a verdict. The prose belongs
    # in MODEL_NOTES below, which is only ever printed; test_pipeline now asserts
    # every restricted entry still classifies non-allow.
    "google-flow": "Google ToS: output conditions we cannot pass on, plus watermark",
    "veo": "Google ToS: output conditions we cannot pass on, plus watermark",
    # ---- our own compute: the output is ours to publish ------------------
    # Rented or local GPUs make no claim on the output; the weights named in
    # the same record carry the licence, and they are checked separately.
    "kaggle": "CC-BY-4.0 (our own output)",
    "local-rtx5090": "CC-BY-4.0 (our own output)",
    # the generic form video_task.write_sidecar emits, e.g. "local-gpu (rtx5090)".
    # Added after a sidecar written by our OWN renderer was flagged unpublishable:
    # only the exact handle "local-rtx5090" was listed, so every clip from a new
    # machine — or from a writer that spells it differently — became a violation.
    # A rule that depends on one machine's nickname is not a rule.
    "local-gpu": "CC-BY-4.0 (our own output)",
    # synth_vo writes "local-mps (pipeline/synth_vo.py, synth_vo v3)" — the Apple
    # card is our own compute exactly as the 5090 is, and it was missing here for
    # the same reason "local-gpu" once was: the list had grown one machine
    # nickname at a time. Caught 2026-08-08, when the first two Chatterbox takes
    # copied into cuts/checklist/ for the founder's ear check pushed licence debt
    # 25 -> 27 and failed the build. The voice engine's own licence is NOT being
    # waved through with this: chatterbox-0.5B is on the voice-engine list above
    # as MIT, it rides the `model` key of the same sidecar, and the gate reads
    # every provenance key independently — so an unread engine on our own card
    # still fails, which is the only property that makes this entry safe.
    "local-mps": "CC-BY-4.0 (our own output)",
    "local-deterministic": "CC-BY-4.0 (our own output)",
    "post-motion": "CC-BY-4.0 (our own output)",     # post_motion.py: code, not a model
    "render-t2": "CC-BY-4.0 (our own output)",
    "render-t3": "CC-BY-4.0 (our own output)",
    "sfx-py": "CC-BY-4.0 (our own output)",
}

# A VENDOR CATCH-ALL IS THE LICENCE OF LAST RESORT FOR THAT VENDOR. Version-specific
# key → the catch-all key it supersedes: when one provenance string matches both, the
# version is the answer and the catch-all is dropped (model_licences below).
#
# Needed because the keys are matched as SUBSTRINGS of one normalised string, so a
# sidecar naming the vendor AND the version legitimately matches both, and something
# has to decide which document gets cited. Until 2026-08-08 that something was
# len(name), which is a fact about spelling and not about licences — see the ltx-2-3
# entry for the three days it cost.
#
# THE ENTRY IS WRITTEN BESIDE THE VERSION, not as a member list on the catch-all, and
# the direction is the point: adding `ltx-3` tomorrow means writing its licence and
# its supersession in the same file at the same moment. A catch-all that enumerated
# its own family would go stale the first time someone added a version and did not
# think to come back up here — the voxcpm2 comment's rule ("add every new version
# explicitly, never inherit by prefix") pointed the other way.
#
# NOT "a catch-all defers to whatever else matched", which is the tempting one-liner
# and is an allow-by-inheritance hole: `Lightricks/LTX-9 on local-gpu` matches
# `lightricks` and `local-gpu`, and dropping the catch-all because SOMETHING else
# matched would leave only our own compute — an unread Lightricks model waved through
# as publishable. Deferral is only ever to a version whose licence someone read,
# which is precisely what an entry in this table certifies.
SUPERSEDES_CATCH_ALL = {
    "ltx-video": "lightricks",
    "ltx-2-3": "lightricks",
}
CATCH_ALLS = frozenset(SUPERSEDES_CATCH_ALL.values())

# KEYS WHOSE ALLOWANCE MAY TRAVEL TO A NAME THE TABLE HAS NOT SEEN, each with the
# reason it is not the hazard the rest of this section exists to stop. Every other
# allow key covers ONE set of weights and covers nothing else: see _match_grade.
#
# The test of membership is not "we trust this vendor", it is: **does the document
# that grants us the output attach to something broader than one checkpoint?**
#   - our own compute and our own code: the grant is that WE made it. A new machine
#     nickname or a renamed script is not a new licensor. This list is why
#     `local-gpu (a-box-we-buy-in-october)` does not have to be added to the table
#     the day the box arrives — the mistake the "local-rtx5090" entry above records.
#   - a hosted service: the licence IS the provider's terms, and those terms cover
#     whatever the service serves. `claude-fable-5` and a model Anthropic ships next
#     year land on the same document; the model name is not what was read.
# A WEIGHTS licence never qualifies on that test, which is why `chatterbox`,
# `kokoro`, `voxcpm`, `dreamshaper`, `animegen` and `ip-adapter` are absent: a
# finetune of them is a different set of weights under a licence nobody has read,
# and that is precisely the string that must fail closed.
ALLOW_INHERITS = {
    # ---- our own compute / our own code ----
    "kaggle": "our own compute; the notebook's weights are a separate key",
    "local-rtx5090": "our own compute",
    "local-gpu": "our own compute, any machine nickname",
    "local-mps": "our own compute",
    "local-deterministic": "our own code path, no model at all",
    "post-motion": "our own code (post_motion.py)",
    "render-t2": "our own code (render_t2.py)",
    "render-t3": "our own code (render_t3.py)",
    "sfx-py": "our own code (sfx.py)",
    # ---- hosted services: the terms cover the service, not one checkpoint ----
    "alibaba-model-studio": "provider terms cover every model the API serves (D8)",
    "fal-ai": "provider terms cover every model the API serves",
    "hailuo": "provider terms (MiniMax via fal) cover the service's models",
    "minimax": "provider terms cover the service's models",
    "claude": "Anthropic's terms cover whatever model they serve",
    # ---- THE UNCOMFORTABLE ONE, listed with its discomfort ----
    # `wan` is the only WEIGHTS key here and it does not pass the test above on its
    # own merits. It is here because the tree's wan records are 100-odd sidecars
    # naming hosted preview versions — wan2.5/2.6/2.7, wan2.x-t2v-plus, wan-api —
    # whose weights were never published, so the entry above already says out loud
    # that what licenses their output is the PLATFORM grant in the same record, not
    # this key. Strict matching would refuse every one of them for the wrong reason
    # (an unread model) when the right reading is recorded one line away.
    # The tightening that retires this line is per-version keys — `wan2-2` for the
    # Apache-2.0 open weights, the platform grant for each hosted preview — which
    # is a classification job with a founder-visible outcome, not a matcher fix.
    # Until then: a wan release whose licence differs from Apache-2.0 gets its own
    # key the day it is used, and this line is the reason nothing will warn you.
    "wan": "hosted wan previews are licensed by the platform grant beside them "
           "(see the wan entry); per-version keys are the tightening",
}

# What a demoted allow becomes: a licence classify() must read as UNKNOWN, so the
# string fails closed and says why. Deliberately NOT the empty string and NOT a
# silent drop — a dropped hit is invisible the moment the same record also names
# our own GPU, and "no hits" would then read as "nothing to check". The finding has
# to be POSITIVE to survive standing next to an allow.
UNINHERITED = ("unread variant of {name} — one set of weights was read and this "
               "is not it")
# Substring that identifies such a value without re-deriving it (used for ordering
# and by the tests). Any wording change must keep this token present.
UNINHERITED_MARK = "unread variant of "

# Models with NO LICENCE TEXT ANYWHERE — a different state from "nobody has read
# it yet", and the difference is worth encoding because it changes what to DO.
#
# LTX-Video sat in this gate as "unread". Someone read it, in about twenty minutes,
# and it cleared. quanhaol/Wan2.2-TI2V-5B-Turbo has no text at any URL: both
# LICENSE paths 404 and GitHub reports NOASSERTION. Reading is not a task that can
# be completed. Filing both as "unread" sends the next person to look for a
# document that does not exist.
#
# So: "unread" means GO READ IT (cheap, and it may clear). "UNCLEARABLE" means the
# only routes are the author publishing terms, or replacing the asset.
UNCLEARABLE = {}   # nothing currently sits here; see quanhaol below for why

# Apache-2.0 AND OUR OUTPUT, stated once so it stops being re-derived:
# Apache 2.0 has no output clause at all. It grants rights in "the Work" — the
# weights and code — and is SILENT on what you generate by running it. That
# silence, not any affirmative grant, is why apache-2.0 weights place no condition
# on our CC BY 4.0 offer. (LTXV reaches the same place the other way, by explicit
# disclaimer in §5: "Licensor claims no rights in the Output".)
# Verified 2026-08-02: neither Wan-Video/Wan2.2 nor hao-ai-lab/FastVideo ships a
# NOTICE file, so Apache §4(d)'s attribution requirement — which is conditional on
# the distributed Work containing one — never triggers. Nothing travels into an
# episode.

# Remedy appended to a violation when the fix is specific enough to name.
MODEL_NOTES = {
    "quanhaol": " — UNCLEARABLE, not merely unread: there is no licence text at any "
                "URL to read. Do not spend time looking. Either the author "
                "publishes terms or the asset is replaced.",
    "pixverse": " — if the take was made on a PAID PixVerse plan, record the plan "
                "in the sidecar (the free tier is personal-use only); otherwise "
                "re-shoot the beat on a publish-safe route",
    "stable-video-diffusion": " — re-render the beat (render_local.py / Kaggle Wan) "
                             "or move the take to clips/footage-archive/",
    # the terms have been read; what is left is not research but a decision
    "google-flow": " — terms read 2026-08-01: Google claims no ownership of the "
                   "output and never forbids commercial use, but two conditions "
                   "attach to it (no using the output to train ML models, no "
                   "passing it off as human-made) plus 'keep SynthID intact' — "
                   "and our own release grants reusers those very freedoms, so we "
                   "cannot honestly pass the restrictions on. The three files "
                   "also carry a visible Flow watermark, which disqualifies them "
                   "on its own. Move them off the published surface, or record a "
                   "founder decision narrowing what we offer reusers (D13)",
    "ltx-video": " — the licence is read and says the cap gates the weights, not "
                 "the footage; awaiting founder sign-off before this becomes an "
                 "allow (D13)",
    # THE LAST-RESORT NOTE NOW, not the winning one (2026-08-08). It used to print
    # for our archived LTX-Video takes because 'lightricks' was the longer key;
    # SUPERSEDES_CATCH_ALL drops it on any string that also names a version we have
    # read, so what reaches this line is a Lightricks model matching NO version key.
    # The 0.X reading is still the right thing to say — 0.X is what applies to
    # anything Lightricks released from 2025-04-15 that we have not separately
    # classified — but the remedy is now the unlisted version, so it says so.
    "lightricks": " — the licence is read and says the cap gates the weights, not "
                  "the footage; awaiting founder sign-off before this becomes an "
                  "allow (D13). If the value names an LTX version this table does "
                  "not list, that version is what you are looking at and 0.X may "
                  "not be its document: read ITS licence, add it beside 'ltx-2-3', "
                  "and register the supersession in SUPERSEDES_CATCH_ALL",
    "ltx-2-3": " — LTX-2 Community License read end to end (D16): commercial use "
               "free below $10M revenue and no rights claimed in output, so the "
               "reuse side is clear under watch-only. What binds US: AI-disclosure "
               "per surface, never train on the output, and item 20 — LTX must "
               "never power a contributor-facing generation service. Awaiting "
               "founder sign-off on the screened sample before this becomes an "
               "allow",
}

# Values that DECLARE no third-party model, matched on the WHOLE value (never
# as a fragment — 'none' inside a longer string means nothing). A slate, a
# title card or a code-only render is our own work under LICENSE-CONTENT.md.
SENTINELS = {"none", "n-a", "na", "null", "no-model", "code"}
# Values that point at provenance recorded elsewhere in the same file. The
# records they point at are each checked on their own, so following the pointer
# would only double-report.
POINTER = re.compile(r"see-sources|see-below|see-shots-md|per-beat")

# Licence-bearing keys, at any depth of a leaf or sidecar.
LICENCE_KEYS = {"licence", "license", "licence_spdx", "license_spdx", "rights"}
# Keys naming a synthesis engine, which we resolve through MODEL_LICENCES.
ENGINE_KEYS = {"engine", "voice_engine", "vo_engine", "tts_engine"}
# Keys naming the model or the service that made an asset — the PICTURE side of
# the gate, checked exactly like an engine (hole 1).
MODEL_KEYS = {"model", "still_model", "motion_model", "video_model", "image_model",
              "base_model", "motion_module",
              # A CORRECTION IS JUDGED LIKE THE FIELD IT CORRECTS (2026-08-08).
              # Render-time provenance is never rewritten — a wrong value is
              # annotated with a dated `corrections:` block instead, so the
              # record keeps the evidence that it was ever wrong. That
              # convention hands the gate a second place a model name can live,
              # and a place it did not read would be the cheapest route past it:
              # write `model: none`, correct it to something unpublishable
              # underneath, ship. Hole 2's shape exactly ("absence is never
              # safer than presence"), spelled as an append instead of a delete.
              "corrected_model", "corrected_still_model"}
PLATFORM_KEYS = {"platform", "provider", "service", "vendor",
                 "corrected_platform"}          # same rule as corrected_model above
PROVENANCE_KEYS = ENGINE_KEYS | MODEL_KEYS | PLATFORM_KEYS
# Keys that name the asset a record is about, for the error message.
ASSET_KEYS = ("clip", "file", "audio", "still", "content", "leaf")

# What ships, by container — never by one extension (hole 7/8). build_site
# copies takes/clips/ with iterdir(), so the extension is not its business;
# render_t3 globs NN-*.mp4 for picture and AUDIO_EXT for sound. A clip saved
# .webm and a VO saved .wav are as published as an .mp4, so they are walked the
# same way.
VIDEO_EXT = {".mp4", ".webm", ".mov", ".mkv", ".m4v", ".gif"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus",
             # added 2026-08-03 while making scan_audio_sources extension-based;
             # these are containers a contributor could plausibly drop in
             ".aiff", ".aif", ".wma"}
# Files that carry provenance, by suffix family rather than by exact name: a
# sidecar saved .yml and a manifest renamed take-final.json are still records,
# and renaming one must not exempt it (hole 8).
RECORD_EXT = {".yaml", ".yml", ".json"}


def classify(licence) -> tuple:
    """(verdict, why) for one licence string. verdict ∈ allow|deny|unknown.

    Deny is checked before allow so a compound identifier is judged by its
    worst clause, and an unrecognised string is 'unknown' — never 'probably
    fine'."""
    if licence is None or not str(licence).strip():
        return "unknown", "no licence recorded"
    norm = normalise(licence)
    for pattern, why in DENY:
        if re.search(pattern, norm):
            return "deny", why
    for pattern, name in ALLOW:
        if re.search(pattern, norm):
            return "allow", name
    return "unknown", ("not on the publish-safe allowlist — classify it in "
                       "pipeline/licence_gate.py or replace the asset")


# ---------------------------------------------------------------------------
# HOW A KEY IN THE TABLE ABOVE MATCHES A PROVENANCE STRING. Rewritten 2026-08-08;
# until then a key matched as a bare SUBSTRING of the whole normalised value, which
# is two holes pointing opposite ways:
#
#   * SUFFIX. `fastwan` contains `wan`, so model_licences("fastwan") answered
#     Apache-2.0 — a document read for a different model, about a model in no
#     table, with nothing said out loud. It was RIGHT (db26f7b went and read
#     FastVideo's LICENSE: Apache-2.0), and that is exactly why it survived: the
#     accident agreed with the truth once, so nothing looked wrong.
#   * FINETUNE. `Lykon/dreamshaper-8-anything` contains `dreamshaper`, so every
#     LoRA, merge and finetune of a listed base inherited the base's allowance.
#
# The morning's SUPERSEDES_CATCH_ALL fix covered ONE family in ONE direction (a
# vendor catch-all losing to a version key we had read). This is the general rule,
# and it rests on the asymmetry the voxcpm2 entry named and then left to
# discipline: THE DIRECTION THAT BITES IS ALWAYS ALLOW-BY-INHERITANCE. A
# restriction that reaches one model too many refuses something publishable —
# noisy, and it fails safe. An allowance that reaches one model too many publishes
# something we hold no right to publish, and the debt count says 25 all the while.
#
# So matching is deliberately NOT symmetrical:
#
#   deny / unknown licences → honoured at ANY match. An NC base's finetune is NC.
#   allow licences          → honoured only where the key NAMES an identifier
#                             rather than merely occurring inside one; otherwise
#                             the hit is DEMOTED to UNINHERITED and reported.
#
# An identifier no key matches is unknown, which was already a violation. Nothing
# below can turn a string this table has never seen into a pass — that is the one
# property to preserve if any of this is ever rewritten again.
#
# A provenance string is prose with identifiers in it, so the identifier is the
# unit: `Wan-AI/Wan2.2-TI2V-5B`, `local-gpu`, `post_motion.py`. Hyphens, dots and
# underscores bind INSIDE a name; whitespace, slashes, pipes, commas, colons and
# brackets separate one name from the next and from the prose around it. That one
# distinction is why `kokoro-82M via kokoro-onnx (local neural TTS)` reads as
# several identifiers — so `via` is not held against `kokoro` — while
# `dreamshaper-8-anything` reads as exactly one, and `anything` is.
IDENT_SEP = re.compile(r"[\s/|,;:()\[\]{}<>+&*=\"'`]|—|–|→")
# Tokens that describe HOW the same weights were packaged rather than naming other
# weights: a parameter count (82M, 0.5B), a precision or quantisation (fp8, bf16,
# q4), a container (onnx, gguf, safetensors, diffusers), a date, a resolution.
# Everything with a digit in it qualifies, plus this short word list. Words that
# name DIFFERENT weights — distilled, turbo, plus, base, instruct, preview, xl —
# are deliberately absent: those are the strings that must fail closed.
DECORATION_WORDS = frozenset({"onnx", "gguf", "safetensors", "diffusers",
                              "ckpt", "pt", "pth", "bin", "py"})
# exact      — the key consumed every identifier it touched, and nothing else.
# decorated  — leftovers, all of them packaging (above): the same weights.
# variant    — a leftover word the table never read, or a version fused onto the
#              key (`wan2` for `wan`, `voxcpm3` for `voxcpm`). Different weights.
GRADE_RANK = {"exact": 0, "decorated": 1, "variant": 2}


def identifiers(text) -> list:
    """The identifiers a provenance string names, each normalised."""
    return [n for n in (normalise(c) for c in IDENT_SEP.split(str(text))) if n]


def _decoration(token: str) -> bool:
    """Packaging, not another model — see DECORATION_WORDS."""
    return any(c.isdigit() for c in token) or token in DECORATION_WORDS


def _match_grades(key: str, tokens: list, run_of: list) -> dict:
    """{identifier(s) touched → grade} for every way `key` matches here.

    A key matches a run of WHOLE tokens (so `wan` no longer matches inside
    `fastwan`), and its last token may absorb a fused numeric suffix (`wan2`) —
    which is graded as a version, the weakest grade, because a version bump is
    exactly how a licence changes. Leftover tokens are counted only in the
    identifiers the match actually touched: prose two words away is not evidence
    about the model, and the identifier it sits in is.

    Keyed by the touched identifiers rather than reduced to one grade, because
    WHICH identifier a hit is about is what lets a specific key answer for it
    (model_licences below). A multi-token key may legitimately span consecutive
    identifiers — `alibaba-model-studio` against 'Alibaba Model Studio API' —
    so the key of this dict is a tuple, not an index."""
    kt = key.split("-")
    grades = {}
    for start in range(len(tokens) - len(kt) + 1):
        fused = False
        for offset, want in enumerate(kt):
            got = tokens[start + offset]
            if got == want:
                continue
            if offset == len(kt) - 1 and got.startswith(want) and got[len(want):].isdigit():
                fused = True
                continue
            break
        else:
            span = range(start, start + len(kt))
            touched = tuple(dict.fromkeys(run_of[i] for i in span))
            leftover = [t for i, t in enumerate(tokens)
                        if run_of[i] in touched and i not in span]
            grade = ("variant" if fused or not all(map(_decoration, leftover))
                     else "decorated" if leftover else "exact")
            if GRADE_RANK[grade] < GRADE_RANK.get(grades.get(touched), 9):
                grades[touched] = grade
    return grades


def model_licences(text) -> list:
    """EVERY classified model named in a provenance string, as (name, licence).

    One field routinely names two models — 'still: dreamshaper-8 | motion:
    stable-video-diffusion-img2vid-xt' — and v1's resolver returned the single
    longest match, so sixteen shipping sidecars were judged by their still
    model and their non-commercial motion model was never looked at. A record
    ships only if every model it names is publish-safe.

    LENGTH DECIDES NOTHING ABOUT WHICH DOCUMENT A MODEL IS JUDGED UNDER
    (2026-08-08). A vendor catch-all whose version-specific key also matched is
    dropped here per SUPERSEDES_CATCH_ALL, and any catch-all that survives sorts
    last — so `Lightricks/LTX-2.3` is answered by the LTX-2 Community Licence and
    not by whichever key spells its vendor with more letters. Length still breaks
    ties between unrelated keys, where it decides nothing that matters.

    AN ALLOWANCE NEVER TRAVELS TO A NAME NOBODY READ (also 2026-08-08, the other
    half of the same queue entry). A key whose licence classifies `allow` and
    which only matched a VARIANT of itself is returned under UNINHERITED instead
    of under its own licence, unless it is declared in ALLOW_INHERITS. The name
    is still returned, so the report can say what the string resembles — the
    demotion changes the verdict, never the evidence. Restrictions keep
    travelling in the other direction, on purpose (see the section comment)."""
    tokens, run_of = [], []
    for i, ident in enumerate(identifiers(text)):
        for tok in ident.split("-"):
            tokens.append(tok)
            run_of.append(i)
    graded = {}
    for name in MODEL_LICENCES:
        grades = _match_grades(name, tokens, run_of)
        if grades:
            graded[name] = grades
    # THE MOST SPECIFIC KEY ANSWERS FOR AN IDENTIFIER. `voxcpm2` is in this table
    # because someone read ITS card, and it names the string `voxcpm2` outright,
    # while `voxcpm` reaches the same string only as a fused version — so the
    # reading wins and the base key has nothing to say about it. Without this,
    # adding a version key would make the string WORSE than before it was added
    # (read licence + inherited doubt), which is the opposite of the incentive
    # every "add every new version explicitly" comment in this file is asking for.
    #
    # Deliberately NOT the tempting "a base key defers to whatever else matched" —
    # the hole SUPERSEDES_CATCH_ALL's comment names. Deferral is to a key that
    # matched THE SAME IDENTIFIER at exact or decorated grade, i.e. one whose
    # licence is about these very weights. `Lykon/dreamshaper-8-anything on
    # local-gpu (rtx5090)` still fails: our own GPU is a different identifier and
    # answers for nothing but itself.
    answered = {run for grades in graded.values()
                for runs, grade in grades.items() if grade != "variant"
                for run in runs}
    superseded = {SUPERSEDES_CATCH_ALL[n] for n in graded if n in SUPERSEDES_CATCH_ALL}
    hits = []
    for name, grades in graded.items():
        if name in superseded:
            continue
        licence = MODEL_LICENCES[name]
        if (min(GRADE_RANK[g] for g in grades.values()) == GRADE_RANK["variant"]
                and name not in ALLOW_INHERITS
                and classify(licence)[0] == "allow"):
            # every occurrence is a variant (that is what the min says). If a key
            # that DID name the identifier covers all of them, this one is silent;
            # otherwise it fails closed and says which reading it is not.
            if all(any(run in answered for run in runs) for runs in grades):
                continue
            licence = UNINHERITED.format(name=name)
        hits.append((name, licence))
    # A demoted hit sorts after the licences somebody actually read, so
    # engine_licence() cites a real document when the string names one and only
    # falls back to "we have not read this" when it does not.
    hits.sort(key=lambda h: (h[0] in CATCH_ALLS, UNINHERITED_MARK in h[1], -len(h[0])))
    return hits


def engine_licence(engine) -> str:
    """The licence that decides an engine's verdict, or None if we have never
    classified it. None is a failure upstream, not a default-allow. When a
    string names several models, the first non-allow licence decides — the same
    worst-clause rule classify() applies within one identifier."""
    hits = model_licences(engine)
    if not hits:
        return None
    for _, licence in hits:
        if classify(licence)[0] != "allow":
            return licence
    return hits[0][1]


def is_candidate(path: Path, root: Path = REPO) -> bool:
    """Evaluation media under a `takes/` subtree — shot but not yet chosen.

    A THIRD tier between shipping and archived, added 2026-08-07. Archive means
    "was canon, superseded"; candidate means "may never be canon at all". Both
    are decided by directory name only, for the reason is_archived() gives: a
    directory is a DECLARATION, whereas a filename or a missing field is a way
    of hiding something.

    Why it earns its own tier rather than counting as debt. The ratchet in
    lint_genome asserts one thing — that publishable-asset liability never
    quietly grows — and it does that by counting violations. Candidates break
    the count without breaking the invariant: the founder picks one frame out of
    four, so a single approved still arrives with three siblings that exist only
    to be rejected, and each writes its own honest sidecar. On 2026-08-07 that
    put 40 records into one node's takes/stills/ in a single wave and pushed the
    debt from 38 to 78 — 40 new lines of report about ONE unresolved question
    (D15: animagine-xl-3.1 is CreativeML Open RAIL++-M, whose use restrictions
    travel, and it drew every frame in the tree). Not one new KIND of liability;
    the same open decision, multiplied by the number of frames a wave happens to
    shoot. A ratchet that ratchets on batch size is a ratchet nobody can hold.

    THIS IS SCOPING, NOT SUPPRESSION, and the difference is load-bearing:
      - candidates are still classified, by exactly the same rules;
      - they are still REPORTED, on their own line in lint output, so D15's
        surface area stays visible and countable instead of vanishing;
      - they do not enter the debt total;
      - and the moment one is PROMOTED — copied into the node's own stills/ or
        clips/, named by a leaf, assembled into an episode — it is canon and the
        full gate applies with nothing softened. Same rule as an archive: moving
        the file is what changes the verdict.

    WHAT MAKES THE EXEMPTION HONEST is that the publish path enforces it, and
    takes/ IS a publish path — this must not be read as "takes/ never ships".
    Both directories build_site copies out of a takes/ subtree run every file
    through publishable() first: takes/clips/ since the PixVerse leak, and
    takes/stills/ as of today (build_site.py, same commit as this comment — it
    was a bare glob+copy until now, the one published surface on the site with
    no licence question asked). A non-allow candidate is withheld and named in
    WITHHELD.md. That gate, not this tier, is what keeps an unpublishable frame
    off banyan.city. If a surface ever starts publishing out of takes/ without
    calling publishable(), this exemption becomes a hole the day that code
    lands, so the two belong in the same review.

    THE TIER THEREFORE COVERS EXACTLY WHAT publishable() CATCHES, and no more:
    a record that NAMES a model whose licence classifies non-allow. Everything
    else the gate can find in a takes/ file stays canon debt — an empty
    provenance value, a model in no table, a pointer to nothing, a sidecar
    declaring no provenance at all, a clip with no record beside it. In every
    one of those, engine_licence() returns None, publishable() reads None as
    `continue`, and the file is copied to the website. Exempting the findings
    the publish gate waves through would invert the incentive the whole gate
    rests on: writing an honest sidecar would cost a candidate line, and writing
    nothing would cost nothing. The unreadable record must never be the cheap
    one — that is hole 2 ("absence is never safer than presence"), and it would
    have come straight back in through this door.
    """
    try:
        parts = path.relative_to(root).parts[:-1]
    except ValueError:
        parts = path.parts[:-1]
    return "takes" in parts


def is_archived(path: Path, root: Path = REPO) -> bool:
    """Superseded material, kept for provenance (R6).

    Decided by directory name only — the repo's own convention (clips/
    vo-archive, clips/footage-archive, clips/archive-t2v-realistic,
    takes/archive) — and by nothing else. Not by a filename, not by a leaf's
    status, not by a missing field: those are all ways of hiding an asset, and
    an archive is a way of declaring one. Archived assets are advisory because
    build_site copies none of these directories and render_t3 globs none of
    them; the moment a file moves out, it is judged as shipping."""
    try:
        parts = path.relative_to(root).parts[:-1]
    except ValueError:
        parts = path.parts[:-1]
    return any(p == "archive" or p.startswith("archive-") or p.endswith("-archive")
               for p in parts)


def records(obj):
    """Yield one dict of scalars per record in a nested yaml/json structure.

    v1 flattened everything into bare (key, value) pairs, which was enough to
    find a licence but not enough to name the asset it belonged to — 'key
    platform' does not say which beat of which episode. Provenance is written
    per record (a beat's clip, platform, model and cost live in one dict), so
    the gate reads it per record. A scalar list under a key is kept with the
    record, because 'licence: [CC0, MIT]' is two licences, not none."""
    if isinstance(obj, dict):
        scalars = {}
        for k, v in obj.items():
            key = str(k).strip().lower()
            if isinstance(v, dict):
                yield from records(v)
            elif isinstance(v, list):
                if any(isinstance(i, (dict, list)) for i in v):
                    yield from records(v)
                else:
                    scalars[key] = v
            else:
                scalars[key] = v
        yield scalars
    elif isinstance(obj, list):
        for item in obj:
            yield from records(item)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


# The pipeline writes sidecars under TWO names and always has:
#
#   <stem>.meta.yaml        09-whoami.meta.yaml   — render_t3, intake_take, and
#                           the 126 records tracked under genomes/ and cuts/
#   <full name>.meta.yaml   09-whoami.mp4.meta.yaml — hold_still.py:243 and
#                           video_task.write_sidecar (video_task.py:923)
#
# Readers pinned to the stem shape simply do not see the other one, and an
# asset whose record they cannot see reads as an asset with no provenance at
# all — the loudest possible verdict on the most carefully written file. That
# is a bug in the READER. Fixing it by renaming the files instead would break
# every reader pinned to the full-name shape, starting with the two held-still
# detectors (render_t3.py:545, check_invention.py:207) that match on the file
# they were handed, and it would throw away the git trail on each record.
#
# The pattern is build_shotboard.py:240-241's, which got this right first: try
# the exact name, fall back, and treat "neither exists" as no record rather
# than as an error. Most specific first — a sidecar naming the container it
# sits beside outranks one naming only the stem, so a `.POST.mp4` can never
# inherit the base take's receipt while claiming to be its own.
META_EXT = (".meta.yaml", ".meta.yml")
# `.json` is the VO manifest shape (NN-vo.json beside NN-vo.mp3) and belongs
# ONLY to callers that walk sound as well as picture — i.e. the gate. A picture
# reader that accepted it would one day adopt an unrelated export sitting in the
# same directory as a clip's recipe, so those callers pass META_EXT explicitly.
RECORD_SIDECAR_EXT = META_EXT + (".json",)


def sidecar_for(asset: Path, exts=RECORD_SIDECAR_EXT) -> Path | None:
    """The record beside an asset that says what made it, or None.

    Both naming conventions, and by default the three extensions the pipeline
    writes: `.meta.yaml`, the same saved `.meta.yml`, and `NN-vo.json` beside
    `NN-vo.mp3` (synth_vo). Never inherits a NEIGHBOUR's record — both
    candidates are built from this asset's own name, so renaming a take away
    from its sidecar still loses its provenance rather than borrowing the
    next take's.
    """
    for ext in exts:
        for cand in (asset.with_name(asset.name + ext),    # 09-x.mp4.meta.yaml
                     asset.with_name(asset.stem + ext)):   # 09-x.meta.yaml
            if cand.exists():
                return cand
    return None


class Gate:
    """Collects violations (errors) and advisories over one repo."""

    def __init__(self, repo: Path = REPO):
        self.repo = repo
        self.errors = []
        self._advisories = []      # (message, where) — collapsed by run()
        self.candidates = []       # takes/ — reported, never counted (is_candidate)
        self._reported = set()     # (where, licence) already named — see check_provenance

    def tier_of(self, path: Path) -> str:
        """"canon" | "candidate" | "archived" — which of the three the file is.

        Archive is checked FIRST: `takes/archive/` is both, and an archived take
        is the more specific statement (it was shot, considered and set aside),
        so it keeps the advisory treatment it has always had rather than being
        re-labelled a live candidate."""
        if is_archived(path, self.repo):
            return "archived"
        if is_candidate(path, self.repo):
            return "candidate"
        return "canon"

    def err(self, where: str, msg: str) -> None:
        line = f"{where}: {msg} (licence gate)"
        if line not in self.errors:          # one asset, one violation
            self.errors.append(line)

    def advise(self, where: str, msg: str) -> None:
        """Advisories are collapsed by message before printing. One archived
        F5-TTS take is worth reading about; forty identical lines are worth
        scrolling past, which is how a real warning gets missed."""
        self._advisories.append((msg, where))

    def candidate(self, where: str, msg: str) -> None:
        """A takes/ record's problem: classified and printed, never counted."""
        line = f"{where}: {msg} (licence gate)"
        if line not in self.candidates:
            self.candidates.append(line)

    def report(self, where: str, msg: str, tier: str = "canon") -> None:
        """Route one finding by tier. Nothing is ever silent — the three
        differ in whether they FAIL, not in whether they are said out loud.

        canon      → violation, counted against the debt ratchet
        candidate  → reported on its own line, not counted (see is_candidate)
        archived   → advisory, collapsed by message

        `tier` was a `shipping: bool` until 2026-08-07. A boolean could only
        ever say fails / does-not-fail, so the day a third tier appeared the
        choice was to call candidates shipping (and let one 40-frame wave move
        the ratchet by 40) or to call them archived (and bury a live question in
        a list that exists to be scrolled past). Neither is true of them."""
        if tier == "candidate":
            self.candidate(where, f"{msg} — a takes/ candidate, so it is not "
                                  "counted against the debt ratchet; publishing "
                                  "it is blocked by publishable(), and promoting "
                                  "it into stills/ or clips/ makes this fatal")
        elif tier == "archived":
            self.advise(where, f"{msg} — archived, so it does not fail CI, but "
                               "promoting it back into an episode would")
        else:
            self.err(where, msg)

    def check_licence(self, where: str, licence, what: str) -> None:
        """An explicit licence key is a fact about the file, wherever the file
        lives, so this stays an error even in an archive (v1 behaved this way
        and nothing here weakens it)."""
        verdict, why = classify(licence)
        if verdict == "deny":
            self.err(where, f"licence '{licence}' on {what} cannot ship: {why}")
        elif verdict == "unknown":
            self.err(where, f"licence '{licence}' on {what} is unclassified: {why}")

    def check_provenance(self, where: str, value, what: str, tier: str = "canon") -> None:
        """A model / engine / platform name → whether what it made can ship.

        The one path for voice AND picture (hole 1). Absent or unrecognised
        provenance on a shipping asset is a violation, not a note (hole 2)."""
        # THE CANDIDATE TIER APPLIES TO EXACTLY ONE OUTCOME: a model that IS
        # named and DOES classify non-allow. That is the only finding
        # build_site.publishable() acts on, so it is the only one whose
        # exemption is backed by anything.
        #
        # Everything else below — an empty value, a name in no table, a pointer
        # to nothing — makes engine_licence() return None, and publishable()
        # reads None as `continue` and copies the file to the website. Those
        # findings therefore stay CANON debt wherever the file lives, because
        # the alternative is a rule that charges you for honest provenance and
        # refunds you for vague provenance. The gate must never make the
        # unreadable record the cheap one.
        blocked = tier if tier != "candidate" else "canon"
        norm = normalise(value)
        if not norm:
            self.report(where, f"{what} is empty — an asset with no provenance has no "
                               "licence, and no licence cannot ship", blocked)
            return
        # The model table is consulted FIRST, before either escape (hole 6).
        # v2 matched POINTER as a fragment and returned, so 'stable-video-
        # diffusion — see sources' bought silence by appending three words: a
        # pointer beside a name is not a delegation, it is a decoration. A value
        # that names a model is judged by that model, whatever else it says.
        hits = model_licences(value)
        if not hits:
            if POINTER.search(norm):
                return                    # provenance recorded per record below
            if norm in SENTINELS:
                return                    # declares no external model: our own work
            self.report(where, f"{what} '{value}' matches nothing in "
                               "licence_gate.MODEL_LICENCES — an unclassified model is "
                               "not a safe model; add it there with the licence you "
                               "actually read, or replace the asset", blocked)
            return
        # One violation per asset per licence, not per matched name and not per
        # key: a sidecar that says `platform: pixverse-web` and `model: PixVerse
        # V6` has one problem, and printing it twice is how a 7-line report
        # becomes a 20-line one nobody finishes reading.
        for licence in dict.fromkeys(l for _, l in hits):
            verdict, why = classify(licence)
            if verdict == "allow":
                continue
            names = [n for n, l in hits if l == licence]
            note = next((MODEL_NOTES[n] for n in names if n in MODEL_NOTES), "")
            if (where, licence) in self._reported:
                continue
            self._reported.add((where, licence))
            self.report(where, f"{what} '{value}' is made with {'/'.join(names)} "
                               f"({licence}), which cannot ship: {why}{note}", tier)

    def check_engine(self, where: str, engine, what: str, tier: str = "canon") -> None:
        """Voice engines, kept as its own name because that is what the VO path
        calls; the check itself is the shared one."""
        self.check_provenance(where, engine, what, tier)

    def scan_record_file(self, path: Path, tier: str = "canon") -> None:
        """One record file — leaf, clip sidecar, VO manifest, voices.yaml,
        sound.yaml, whatever a future step writes — parsed and swept.

        Both formats land in the same sweep on purpose (hole 5). Unparseable is
        an error and never a skip, in an archive too: a file nobody can read is
        a licence nobody can verify."""
        where = _rel(path)
        text = path.read_text(errors="replace")
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                self.err(where, f"unparseable VO manifest, engine cannot be verified ({e})")
                return
        else:
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as e:
                self.err(where, "unparseable yaml, licence cannot be verified "
                                f"({e.__class__.__name__})")
                return
        self._scan_records(path, data, tier)

    def describes_asset(self, path: Path) -> bool:
        """Files whose ONLY job is to say what made a shipping asset: a clip
        sidecar (`<clip>.meta.yaml`) and a VO manifest (`NN-vo.json`). Such a
        file that declares no provenance answers the one question it exists to
        answer, so its emptiness is a violation (below).

        Tested by suffix FAMILY, never by an exact name: `.meta.yml` is a
        sidecar and `take-final.json` is a manifest, and v2's
        `endswith('.meta.yaml')` let both walk past (hole 8). Every json under
        the scanned roots is a manifest in practice — the tree has 336 and all
        336 are VO."""
        return ".meta." in path.name or path.suffix.lower() == ".json"

    def _scan_records(self, path: Path, data, tier: str = "canon") -> None:
        """The one sweep over a parsed record file, whatever its format.

        v2 ran this over yaml and gave json a single `data['engine']` lookup —
        which is exactly hole 1 (the picture is unchecked) one file format
        later: a manifest saying `engine: chatterbox, model: pixverse v6`, or
        carrying an NC `licence` key, passed in silence (hole 5). Leaves,
        sidecars and manifests are all read the same way now."""
        where = _rel(path)
        recs = list(records(data))
        # A sidecar or manifest exists to answer "what made this and under what
        # licence". One that declares no model, engine or platform answers
        # nothing — and it would otherwise satisfy scan_media, which only looks
        # for the record's existence. Absence is a violation, not a note: a
        # deleted 'engine' key must not be cheaper than a wrong one.
        # No `tier == "canon" and …` guard on the condition: report() decides
        # error vs candidate vs advisory, and a record that says nothing is
        # worth naming out loud in all three. v2 guarded the sidecar rule this
        # way and the archive went silent, which is the one thing a lower tier
        # must never buy.
        if self.describes_asset(path) \
                and not any(k in PROVENANCE_KEYS for r in recs for k in r):
            fix = ("backfill the engine of record or re-synth (pipeline/synth_vo.py "
                   "writes it)" if path.suffix.lower() == ".json"
                   else "record the platform and model that made the footage beside it")
            self.report(where, "declares no engine, model or platform — a shipping asset "
                               f"with no provenance is a violation, not a note; {fix}",
                        tier if tier != "candidate" else "canon")
        # 'model: per-beat — see sources' delegates provenance to the records
        # underneath it, and check_provenance honours that. If the file has no
        # record naming a model, the delegation points at nothing — which is a
        # deleted field wearing a pointer's clothes.
        prov = [(k, r[k]) for r in recs for k in PROVENANCE_KEYS if r.get(k)]
        if any(POINTER.search(normalise(v)) for _, v in prov) \
                and not any(model_licences(v) for _, v in prov):
            self.report(where, "provenance says 'see sources' but no record in this file "
                               "names a model or service — the pointer points at nothing",
                        tier if tier != "candidate" else "canon")
        for rec in recs:
            asset = next((str(rec[k]) for k in ASSET_KEYS if rec.get(k)), "")
            label = f"{where} [{asset[:60]}]" if asset else where
            # a slated beat has no footage, so it has nothing to license; its
            # 'platform: none / model: none' is an honest statement of that.
            slate = asset.lower().startswith("slate")
            for key, value in rec.items():
                for v in (value if isinstance(value, list) else [value]):
                    if key in LICENCE_KEYS:
                        self.check_licence(label, v, f"key '{key}'")
                    elif key in PROVENANCE_KEYS and not slate:
                        kind = "engine" if key in ENGINE_KEYS else "model/service"
                        self.check_provenance(label, v, f"{kind} (key '{key}')", tier)

    def scan_sources_md(self, path: Path) -> set:
        """A node's audio-sources/SOURCES.md licence table. The licence column
        is found from the nearest header row; rows in a continuation table with
        no header of its own fall back to the last cell (which is how that file
        actually grew). Returns the filenames the table covers."""
        where = _rel(path)
        col = None
        listed = set()
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            heads = [normalise(c) for c in cells]
            if any(h in ("licence", "license") for h in heads):
                col = next(i for i, h in enumerate(heads) if h in ("licence", "license"))
                continue
            if all(set(c) <= set("-: ") for c in cells):
                continue                      # markdown separator row
            idx = col if col is not None and col < len(cells) else len(cells) - 1
            self.check_licence(f"{where}:{lineno}", cells[idx],
                               f"'{cells[0]}'" if cells else "table row")
            if cells:
                listed.add(cells[0].strip("`* "))
        return listed

    def scan_audio_sources(self, path: Path) -> None:
        """The table AND its coverage. Every recorded sound in the directory
        ships (render_t3 muxes them via clips/sound.yaml), so a file with no row
        is an unlicensed shipping asset — dropping a new .wav in beside the
        others, or deleting its row, must not buy silence."""
        listed = self.scan_sources_md(path)
        where = _rel(path)
        for f in sorted(path.parent.iterdir()):
            if f.is_dir() or f.name.startswith("."):
                continue
            # AUDIO ONLY. This used to skip SOURCES.md by name and treat every other
            # file in the directory as a recorded sound, so adding
            # WHERE-TO-GET-SOUNDS.md — documentation about which licences are usable —
            # was reported as an unlicensed shipping asset (2026-08-03). Documentation
            # next to the assets it documents is the right place for it; the gate has
            # to know the difference. Extension-based, so a .wav renamed .mov is still
            # caught, and a note is not.
            if f.suffix.lower() not in AUDIO_EXT:
                continue
            if f.name not in listed:
                self.err(_rel(f), f"recorded sound ships with no row in {where} — "
                                  "its licence is written down nowhere")

    def scan_sound_cues(self, path: Path) -> None:
        """clips/sound.yaml names recorded files by path; each must resolve to a
        row in its node's SOURCES.md. A cue pointing at an unlisted file is the
        same hole from the other side."""
        where = _rel(path)
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError:
            return                            # scan_record_file already reported it
        for rec in records(data):
            ref = rec.get("file")
            if not ref:
                continue
            target = (self.repo / str(ref))
            table = target.parent / "SOURCES.md"
            if not target.exists():
                self.err(where, f"sound cue names '{ref}', which does not exist — "
                                "its licence cannot be verified")
            elif not table.exists() or target.name not in self.scan_sources_md(table):
                self.err(where, f"sound cue names '{ref}' with no row in "
                                f"{_rel(table)} — a shipping sound with no licence")

    def sidecar_of(self, asset: Path) -> Path | None:
        """The record beside an asset that says what made it, or None."""
        return sidecar_for(asset)

    def scan_media(self, root: Path, named: set) -> None:
        """Every shipping picture and sound whose licence is written down
        NOWHERE: no sidecar beside it, no SOURCES.md row, no leaf record naming
        it. Renaming a clip so the sidecar no longer matches must not make it
        invisible (a .POST.mp4 next to a .meta.yaml for a different take looks
        provenanced and is not).

        v2 walked '*.mp4' and nothing else (hole 7), which left two ways to ship
        with no provenance at all: save the clip as .webm (build_site copies
        takes/clips/ by iterdir, so the extension is not a filter), or write the
        VO mp3 and never write its NN-vo.json (render_t3's find_audio muxes
        NN-*.mp3 whether a manifest exists or not). Both are walked now — a
        deleted manifest is hole 2, and a renamed container is hole 8."""
        for asset in sorted(root.rglob("*")):
            ext = asset.suffix.lower()
            if not asset.is_file() or ext not in (VIDEO_EXT | AUDIO_EXT):
                continue
            if is_archived(asset, self.repo) or asset.parent.name == "leaves":
                continue                      # leaves/*.mp4 = the episode; its leaf yaml is the record
            if (asset.parent / "SOURCES.md").exists():
                continue                      # scan_audio_sources owns that directory's coverage
            if self.sidecar_of(asset) or asset.name in named:
                continue
            kind = "footage" if ext in VIDEO_EXT else "audio"
            beside = ("no .meta.yaml sidecar" if ext in VIDEO_EXT
                      else "no NN-vo.json manifest, no .meta.yaml sidecar, no SOURCES.md row")
            # STAYS A HARD ERROR IN takes/ TOO — deliberately not routed through
            # report(). The candidate tier is only ever as honest as the publish
            # gate behind it, and publishable() returns True for a file with no
            # sidecar ("unprovenanced is the gate's finding, not the build's").
            # So an unprovenanced take in takes/clips/ is not withheld from
            # banyan.city — it is copied onto it. Exempting the one class of
            # asset the publish gate waves through is how a scoping rule becomes
            # a laundering rule: write no record and pay nothing.
            self.err(_rel(asset), f"{kind} ships with no provenance: {beside} "
                                  "and no leaf record names it, so nothing "
                                  "says what made it or under what licence")

    def assets_named_by_leaves(self, genomes: Path) -> set:
        """Asset filenames a leaf's sources[] names — the other place a shipping
        clip's or VO take's provenance legitimately lives (render_t3 writes it
        there: `clip:` + `audio:` beside `platform:` / `voice_engine:`).

        A row only counts if it carries provenance ITSELF. Otherwise adding a
        bare `clip: 07-take.mp4` line to a leaf would launder a file the gate
        would otherwise have caught — hole 2 again, spelled as an addition
        instead of a deletion."""
        named = set()
        for leaf in sorted(genomes.glob("*/nodes/*/leaves/*.y*ml")):
            try:
                data = yaml.safe_load(leaf.read_text())
            except yaml.YAMLError:
                continue
            for rec in records(data):
                if not any(rec.get(k) for k in PROVENANCE_KEYS):
                    continue
                for key in ("clip", "audio"):
                    for tok in re.split(r"[+\s]+", str(rec.get(key, ""))):
                        if Path(tok).suffix.lower() in (VIDEO_EXT | AUDIO_EXT):
                            named.add(tok)
        return named

    def collapse(self) -> list:
        """One line per distinct advisory, with a count and a couple of
        examples, in first-seen order."""
        groups = {}
        for msg, where in self._advisories:
            groups.setdefault(msg, []).append(where)
        out = []
        for msg, wheres in groups.items():
            if len(wheres) == 1:
                out.append(f"{wheres[0]}: {msg}")
            else:
                out.append(f"{len(wheres)} files: {msg} "
                           f"(e.g. {', '.join(wheres[:2])})")
        return out

    def run(self) -> tuple:
        genomes = self.repo / "genomes"
        # The three roots build_site publishes out of: the tree itself, the
        # trial gallery (outputs/*/*.mp4 → /trials/<platform>/), and the working
        # cuts (cuts/**.mp4 → /review/, added 2026-08-07 with D17). Everything
        # below is derived from these, so a new node, a new clips dir or a new
        # record format is covered the day it appears — no per-shape glob left
        # to fall out of date (hole 3). A published surface that the gate does
        # not walk is the whole hole this list exists to close, so a directory
        # gets added here in the same commit that starts publishing out of it.
        roots = [genomes] + [d for d in (self.repo / "pipeline" / "t3-trials" / "outputs",
                                         self.repo / "cuts")
                             if d.is_dir()]
        for root in roots:
            # 1. every record file, any format, anywhere: leaves, clip sidecars,
            #    VO manifests under clips/ or takes/clips/ or a dir someone
            #    passes to render_t3 --clips tomorrow, voices.yaml, sound.yaml.
            for f in sorted(root.rglob("*")):
                if f.is_file() and f.suffix.lower() in RECORD_EXT:
                    self.scan_record_file(f, tier=self.tier_of(f))
            # 2. every shipping picture and sound with no provenance anywhere.
            #    Leaf rows are a legitimate place for it, so they are collected
            #    first — from the tree only; a trial clip's record is its sidecar.
            self.scan_media(root, self.assets_named_by_leaves(genomes)
                            if root == genomes else set())
        # 3. the recorded-audio tables, and every file they should cover
        for md in sorted(genomes.glob("*/nodes/*/audio-sources/SOURCES.md")):
            self.scan_audio_sources(md)
        # 4. sound-design cues that name a recorded file
        for f in sorted(genomes.glob("*/nodes/*/clips/sound.yaml")):
            self.scan_sound_cues(f)
        return self.errors, self.collapse(), self.candidates


def scan(repo: Path = REPO) -> tuple:
    """(errors, advisories) for a repo. Errors are publish-blocking.

    KEPT AT TWO VALUES on purpose (2026-08-07). Candidates arrived as a third
    bucket, and widening this tuple would have rewritten 35 unpack sites in
    test_pipeline alone — a diff where the real change is invisible among the
    mechanical ones, and every one of those sites a chance to silently swallow
    the new element by unpacking it into `_`. Callers that only ask "does this
    tree ship" still get exactly that answer; scan_all() is for callers that
    must also account for what is merely being considered."""
    errors, advisories, _candidates = scan_all(repo)
    return errors, advisories


def scan_all(repo: Path = REPO) -> tuple:
    """(errors, advisories, candidates) — the whole picture.

    Errors are publish-blocking and counted against the debt ratchet.
    Candidates are takes/ records naming a model whose licence does not clear:
    printed every run so the tree's open licence questions stay countable, and
    never added to the total, because build_site.publishable() is what keeps
    them off the website. See is_candidate for the full reasoning and for the
    one thing that must stay true for this split to be honest."""
    return Gate(repo).run()


def main() -> int:
    errors, advisories, candidates = scan_all()
    for a in advisories:
        print(f"  ⚠ {a}")
    if candidates:
        print(f"  ⊙ {len(candidates)} takes/ candidate(s) not publishable as-is "
              f"(not counted — see licence_gate.is_candidate):")
        for c in candidates:
            print(f"    - {c}")
    if errors:
        print(f"✗ licence gate: {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✓ licence gate clear — 0 violations, {len(advisories)} advisory(ies), "
          f"{len(candidates)} candidate(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
