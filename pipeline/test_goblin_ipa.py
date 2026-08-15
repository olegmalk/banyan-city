#!/usr/bin/env python3
"""Guards on the IP-Adapter sampler's two measured lies.

MEASURED 2026-08-15, across 18 IP-Adapter jobs / 280 renders:

  1. 112 renders (40%) were EXACT BYTE-DUPLICATES of another render in the same
     job. Reference sets were built from fewer than four distinct pictures and
     poured into the harness's four fixed slots, so the GPU redrew the same
     conditioning under a second filename. The law held in all 17 measurable
     jobs: unique PNGs == seeds x DISTINCT reference sha256. Confirmed twice —
     repo-side hashing and the box's own render-time .sha256 manifests (560
     files, 0 mismatches) — so it is duplication at RENDER TIME, not in transfer.

  2. 248 of 280 sidecars (89%) said "CONSISTENCY MECHANISM on beat 04" in their
     header regardless of the beat drawn, because the string was a literal.
     goblin_ipa_beat.py renders other beats by rebinding the sampler's BEAT.
     The machine field `shot_beat` was correct in all 280 and stays the
     trustworthy one; the prose a human reads is what lied.

Pure functions, no torch, no GPU, no box. Run: python3 pipeline/test_goblin_ipa.py
"""

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

import goblin_ipa_sample as gis

FAILURES = []

A = "a" * 64
B = "b" * 64
C = "c" * 64
D = "d" * 64
FOUR_DISTINCT = [A, B, C, D]
TWO_DISTINCT = [A, A, B, B]


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def _wg():
    return SimpleNamespace(BASE="cagliostrolab/animagine-xl-3.1", LICENCE="Fair AI",
                           W=832, H=1216, STEPS=40, CFG=7.0, DROP_NEG="none")


def _row(beat):
    return {"warns": [], "beat": beat, "slug": "evidence", "kind": "goblin",
            "tag": "1girl", "pos_tok": 60, "neg_tok": 50, "extra_neg_tier": "b",
            "pos": "a green goblin", "neg": "blurry", "neg_anchor": None}


def _sidecar_text(beat, ref_name, **kw):
    """Write one sidecar into a temp dir and hand back its text."""
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "frame.png"
        gis.sidecar(png, seed=1234, row=_row(beat), secs=12.5, task="t",
                    harness_sha="h", drafts_sha="d", self_sha="s", wg=_wg(),
                    ref=Path(td) / ref_name, ref_sha=A, scale=0.6, **kw)
        return png.with_suffix(".yaml").read_text(encoding="utf-8")


# ---------------------------------------------------------------- FIX 1: dedup

def test_a_four_distinct_set_still_renders_every_cell():
    # b02-charref is the healthy shape: 4 distinct references x 4 seeds = 16
    # distinct PNGs. Deduplication must be invisible to it, cell for cell and
    # NAME for name — the surviving tuples are the originals, so every filename
    # already on disk stays what it was.
    kept, skipped, canon = gis.dedup_cells(gis.CELLS_WINDOW4, FOUR_DISTINCT)
    check("4 distinct: every window4 cell kept", kept == [tuple(c) for c in gis.CELLS_WINDOW4])
    check("4 distinct: nothing skipped", skipped == [])
    check("4 distinct: 4 cells x 4 seeds = 16 frames", len(kept) * 4 == 16)
    check("4 distinct: each slot is its own canonical", canon == [0, 1, 2, 3])
    kept_w, skipped_w, _ = gis.dedup_cells(gis.CELLS_WHOLE, FOUR_DISTINCT)
    check("4 distinct: arm 1's 6 cells all survive",
          len(kept_w) == 6 and skipped_w == [])


def test_a_two_distinct_set_renders_two_cells_not_four():
    # The measured case. Four slots, two pictures: 8 renders, not 16.
    kept, skipped, canon = gis.dedup_cells(gis.CELLS_WINDOW4, TWO_DISTINCT)
    check("2 distinct: 2 cells survive", len(kept) == 2)
    check("2 distinct: the survivors are the first slot of each group",
          [c[0] for c in kept] == [0, 2])
    check("2 distinct: 2 cells skipped", len(skipped) == 2)
    check("2 distinct: 2 cells x 4 seeds = 8 frames", len(kept) * 4 == 8)
    check("2 distinct: canonical map folds r1->r0 and r3->r2",
          canon == [0, 0, 2, 2])
    check("2 distinct: each skip names the cell it duplicates",
          skipped[0][1][0] == 0 and skipped[1][1][0] == 2)


def test_four_copies_of_one_picture_are_one_render_per_seed():
    kept, skipped, _ = gis.dedup_cells(gis.CELLS_WINDOW4, [A, A, A, A])
    check("1 distinct: one cell survives", len(kept) == 1 and kept[0][0] == 0)
    check("1 distinct: three cells skipped", len(skipped) == 3)


def test_dedup_folds_only_the_reference_never_the_knob():
    # Arm 1 sweeps scale on r0: (0, 0.6), (0, 0.4), (0, 0.8). Those are three
    # DIFFERENT renders of the same picture and must all survive even when all
    # four slots hold identical bytes — the reference is the duplicate, the
    # configuration is not.
    kept, skipped, _ = gis.dedup_cells(gis.CELLS_WHOLE, [A, A, A, A])
    check("identical slots: the 0.4/0.8 sweep survives",
          [tuple(c) for c in kept] == [(0, 0.6), (0, 0.4), (0, 0.8)])
    check("identical slots: only the three r1/r2/r3 twins are dropped",
          len(skipped) == 3)
    # And arm 7 varies scale inside a fixed window on one reference.
    kept_s, skipped_s, _ = gis.dedup_cells(gis.CELLS_WINDOW_SCALE, [A, A, A, A])
    check("identical slots: a window arm's two scales both survive",
          len(kept_s) == 2 and skipped_s == [])
    # Arm 3 varies the WINDOW on one reference: four cells, four renders.
    kept_w, skipped_w, _ = gis.dedup_cells(gis.CELLS_WINDOW, [A, A, A, A])
    check("identical slots: a window sweep is four distinct renders",
          len(kept_w) == 4 and skipped_w == [])


def test_the_run_says_out_loud_that_it_deduplicated():
    # Silently rendering 8 where the arm asked for 16 would be its own kind of
    # lie. If someone asks for four references and provides two, the run says so.
    _, skipped, _ = gis.dedup_cells(gis.CELLS_WINDOW4, TWO_DISTINCT)
    txt = "\n".join(gis.dedup_report(TWO_DISTINCT, skipped, 4))
    check("report: shouts that the set is not 4 distinct",
          "NOT 4 DISTINCT" in txt and "2 distinct of 4 slots" in txt)
    check("report: names the byte-identical slot pairs",
          "r0, r1" in txt and "r2, r3" in txt and "BYTE-IDENTICAL" in txt)
    check("report: names every skipped cell", txt.count("SKIPPED cell") == 2)
    check("report: states the renders not spent", "8 renders NOT spent" in txt)


def test_a_healthy_set_is_reported_as_checked_not_as_silence():
    txt = "\n".join(gis.dedup_report(FOUR_DISTINCT, [], 4))
    check("healthy report: states 4 distinct of 4",
          "4 distinct of 4 slots" in txt and "nothing deduplicated" in txt)
    check("healthy report: does not shout", "!!" not in txt)


def test_slots_are_grouped_by_bytes_and_not_by_name():
    check("grouping: two pairs", gis.dup_groups(TWO_DISTINCT) == [[0, 1], [2, 3]])
    check("grouping: all distinct is four singletons",
          gis.dup_groups(FOUR_DISTINCT) == [[0], [1], [2], [3]])
    check("grouping: a non-adjacent duplicate is still one group",
          gis.dup_groups([A, B, A, B]) == [[0, 2], [1, 3]])
    kept, skipped, _ = gis.dedup_cells(gis.CELLS_WINDOW4, [A, B, A, B])
    check("non-adjacent duplicates dedup to the first two cells",
          [c[0] for c in kept] == [0, 1] and len(skipped) == 2)


# --------------------------------------------------- FIX 2: the header's beat

def test_the_sidecar_header_names_the_beat_that_was_drawn():
    txt = _sidecar_text(20, "20-evidence-wave1-s0.png")
    check("beat 20 sidecar says beat 20 in its header",
          "CONSISTENCY MECHANISM on beat 20" in txt)
    check("beat 20 sidecar never says beat 04", "beat 04" not in txt)
    check("beat 20 sidecar's machine field is still shot_beat: 20",
          "shot_beat: 20" in txt)
    four = _sidecar_text(4, "04-the-footnote-wave1-s0.png")
    check("beat 4 sidecar still says beat 04",
          "CONSISTENCY MECHANISM on beat 04" in four and "shot_beat: 4" in four)


def test_a_reference_filename_that_claims_another_beat_is_marked_unreliable():
    # The slot names are held fixed while the beat varies, so the name on a
    # beat-20 frame is a beat-04 name. That is allowed; recording it as though
    # it identified the picture is not.
    txt = _sidecar_text(20, "04-the-footnote-wave1-s2.png")
    check("cross-beat name marked unreliable",
          "ip_adapter_reference_name_reliable: false" in txt)
    check("cross-beat note points at the hash instead",
          "ip_adapter_reference_sha256, never by this name" in txt)
    check("cross-beat note says which beat this actually is",
          "claims a different beat than 20" in txt)
    check("the bytes are still identified", f"ip_adapter_reference_sha256: {A}" in txt)
    same = _sidecar_text(4, "04-the-footnote-wave1-s2.png")
    check("a matching name is marked reliable",
          "ip_adapter_reference_name_reliable: true" in same)
    anon = _sidecar_text(4, "charref-s2.png")
    check("a name that claims no beat is marked unknown, not true",
          "ip_adapter_reference_name_reliable: unknown" in anon)


def test_ref_name_reliability_is_decided_by_the_prefix():
    check("04- name on beat 4 is reliable",
          gis.ref_name_reliable("04-the-footnote-wave1-s0.png", 4) is True)
    check("04- name on beat 20 is not",
          gis.ref_name_reliable("04-the-footnote-wave1-s0.png", 20) is False)
    check("a prefixless name claims nothing",
          gis.ref_name_reliable("charref-s0.png", 4) is None)
    check("a one-digit prefix claims nothing",
          gis.ref_name_reliable("4-x-s0.png", 4) is None)


def test_the_sidecar_records_which_slots_shared_bytes():
    dup = _sidecar_text(20, "04-the-footnote-wave1-s0.png",
                        ref_slot=0, dup_slots=(1,), n_slots=4, n_distinct=2)
    check("duplicate slots are named on the frame",
          "ip_adapter_reference_duplicate_slots: [r1]" in dup)
    check("the frame says it was rendered once, not once per slot",
          "rendered ONCE, not once per slot" in dup)
    check("the frame carries the distinct count", "reference_set_distinct: 2 of 4" in dup)
    check("the frame carries its slot", "ip_adapter_reference_slot: r0" in dup)
    clean = _sidecar_text(4, "04-the-footnote-wave1-s0.png",
                          ref_slot=0, dup_slots=(), n_slots=4, n_distinct=4)
    check("a healthy frame states it had no twin",
          "ip_adapter_reference_duplicate_slots: none" in clean)
    check("a healthy frame states 4 of 4", "reference_set_distinct: 4 of 4" in clean)


def main():
    print("goblin_ipa_sample — dedup + sidecar honesty\n")

    # DO NOT RENDER THE SAME REFERENCE TWICE.
    test_a_four_distinct_set_still_renders_every_cell()
    test_a_two_distinct_set_renders_two_cells_not_four()
    test_four_copies_of_one_picture_are_one_render_per_seed()
    test_dedup_folds_only_the_reference_never_the_knob()
    test_the_run_says_out_loud_that_it_deduplicated()
    test_a_healthy_set_is_reported_as_checked_not_as_silence()
    test_slots_are_grouped_by_bytes_and_not_by_name()

    # AND THE SIDECAR MUST NAME THE BEAT IT ACTUALLY DREW.
    test_the_sidecar_header_names_the_beat_that_was_drawn()
    test_a_reference_filename_that_claims_another_beat_is_marked_unreliable()
    test_ref_name_reliability_is_decided_by_the_prefix()
    test_the_sidecar_records_which_slots_shared_bytes()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all goblin ipa tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
