#!/usr/bin/env python3
r"""002b — the goblin window mechanism on a beat that is NOT beat 04.

2026-08-10. A WRAPPER over `goblin_ipa_sample.py`, holding no sampler code of
its own: the arms, the timestep window, the sidecars and the seed arithmetic are
that file's and stay there, because two copies of a sampler drift and the
sidecars would stop meaning the same thing.

THE VERDICT THIS ANSWERS TO. Roman, 2026-08-10 ~15:00: "the goblin needs abit
more regeneration." Nothing here picks, ranks or promotes a frame, and nothing
here decides what the goblin looks like — that is R4's.

WHAT IS ALREADY MEASURED, so this does not re-ask it. On beat 04 the 15% window
gets the green back (green_share 0.455 against the tags-only baseline's 0.492
and 0.012 when the reference owns all forty steps, a1dcd32), it holds across
eight seeds, and the second knob has now been swept too: at a fixed 15% window,
raising the adapter scale drains the colour again (0.455 at 0.6 -> 0.404 at 0.8
-> 0.209 at 1.0, job ep2-b04-goblin-ipa-wscale). Time and strength are both
mapped. What NOBODY has tested is the axis the fourteen staged wave beats
actually depend on.

THE UNTESTED AXIS IS THE BEAT. Every cell ever drawn used beat 04's prompt AND
beat 04's own frames as the reference — a face filling the frame, conditioned on
four other faces filling the frame at the same composition. "One creature across
seeds" measured that way is partly a statement about a fixed composition. The
question the fourteen staged beats ask is a different one: does a beat-04
reference carry the SAME creature into a beat that is framed nothing like it —
a full-body sprint, a medium shot talking upward, a hand-level close-up? If it
does not, the wave cannot be rendered off this mechanism whatever the beat-04
numbers say, and telling the founder "this gives you one goblin" would be a
claim the evidence never supported.

WHAT THIS RUNS. The recipe is unchanged and unpicked-at: arm `window4`, the 15%
window at scale 0.6 across all four beat-04 references, four seeds each. Only
the BEAT changes — the draft prompt comes from `wave-drafts.yaml` for the named
beat, the references stay beat 04's, and the seed arithmetic (`SEED + beat +
i*1000`) makes this beat's seeds distinct from beat 04's by construction. This
is a proven recipe applied to a new condition, one sample per beat.

THE READ IS BY EYE AND IT IS A COMPARISON: this beat's sixteen frames beside the
beat-04 frames drawn from the same reference. Is it the same creature — same
face, same build, same skin — or the beat-04 goblin only when the composition
is beat 04's? `green_share` may be run for the colour half; it says nothing
about identity. The DINOv2 identity metric is NOT run and no number here may
answer the identity question: it failed twice on this beat family (724b616,
93356b1), calling four visibly different faces one creature. Where a number and
the picture disagree, the picture wins.

ZERO PROMPT TOKENS ADDED — the founder's "nothing complex" is untouched.

$0, local GPU, nothing published, shots.md untouched.

Usage:
    python goblin_ipa_beat.py --beat 2 --harness <dir> --root <repo>
        --refs <dir> --out <dir> --arm window4 --task <id>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Beats whose draft carries the character being conditioned. A beat without
# that character in it cannot answer an identity question about them, so it is
# refused rather than rendered. 8 and 13 joined the goblin list when their
# blocks gained the slot (2026-08-11/12); the guard list exists because the
# founder's consistency mandate (2026-08-12, "you need to create proper
# character consistency") covers the guards too — the reference is whatever
# --refs holds, no longer only beat 04's goblin frames.
GOBLIN_BEATS = (2, 3, 4, 8, 13, 14, 15, 17, 19, 20)
GUARD_BEATS = (5, 6, 7, 8, 9, 10, 11)
# THE FIG IS NOT A CHARACTER, and this list is the admission that the gate above
# was written as if every reference depicted a person. It does not: the fig is a
# frozen OBJECT with its own canon (deep purple-violet, green at the neck, matte)
# and, since 2026-08-14, its own licence-clean reference. The rationale of the
# guard still applies unchanged — a beat with no fig in it cannot answer whether
# the fig holds — so the list is the beats where a fig is actually in frame.
FIG_BEATS = (1, 18, 19, 20)
BEAT_LISTS = {"goblin": GOBLIN_BEATS, "guard": GUARD_BEATS, "fig": FIG_BEATS}


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--beat", type=int, required=True,
                    help="the beat to draw, from wave-drafts.yaml. The "
                         "REFERENCES stay beat 04's — that is the test.")
    ap.add_argument("--sampler-dir", default=None,
                    help="directory holding goblin_ipa_sample.py; defaults to "
                         "this file's own directory")
    ap.add_argument("--character", choices=tuple(BEAT_LISTS),
                    default="goblin",
                    help="what the reference in --refs depicts; gates which "
                         "beats may be conditioned. `fig` is an OBJECT rather "
                         "than a character and its beats are where a fig is in "
                         "frame.")
    known, rest = ap.parse_known_args()

    allowed = BEAT_LISTS[known.character]
    if known.beat not in allowed:
        print(f"!! beat {known.beat} is not one of the {known.character} "
              f"beats {allowed} — its draft has no {known.character}, so "
              f"nothing it drew could answer whether they hold. Refusing.",
              flush=True)
        return 30

    sampler_dir = Path(known.sampler_dir or Path(__file__).resolve().parent)
    if not (sampler_dir / "goblin_ipa_sample.py").is_file():
        print(f"!! no goblin_ipa_sample.py under {sampler_dir} — this file "
              f"renders nothing on its own and will not improvise a sampler.",
              flush=True)
        return 31
    sys.path.insert(0, str(sampler_dir))
    import goblin_ipa_sample as gis                                  # noqa: E402

    # The sampler reads BEAT as a module global inside main(): it selects the
    # draft, seeds the arithmetic and names every output file and sidecar. The
    # reference filenames are beat 04's and are deliberately NOT touched.
    gis.BEAT = known.beat
    sys.argv = [sys.argv[0]] + rest
    print(f"== goblin window mechanism on BEAT {known.beat:02d}, references "
          f"held at beat 04. Recipe unchanged; the beat is the variable.",
          flush=True)
    return gis.main()


if __name__ == "__main__":
    sys.exit(main())
