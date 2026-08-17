#!/usr/bin/env python3
"""Correct the FRAME COUNT in the seven ep2-bNN-cast-0817 specs.

WHAT WAS WRONG, and it was wrong from the moment the specs were filed --
not created by the box sampler sync an hour before this script was written,
only made audible by it.

`refs-guards-twoinfield-nos2-0815` is **3 distinct images poured into 4 slots**.
Hashed on the box 2026-08-17 (sha256, `Get-FileHash`):

    04-the-footnote-wave1-s0.png  26062B66DFCF9B22...  <-- s0 and s3 are the
    04-the-footnote-wave1-s1.png  725A2C1163971F85...      SAME BYTES
    04-the-footnote-wave1-s2.png  293AFE8187731764...
    04-the-footnote-wave1-s3.png  26062B66DFCF9B22...  <-- byte-identical to s0

The sampler enumerates exactly four slots (`{prefix}-s{i}.png`, i in 0..3) and
`dedup_cells()` drops a cell that would redraw a reference already drawn, so the
real grid is **3 cells x 4 seeds = 12 frames**, never 16. The `nos2` in the dir
name is the admission: slot s2 was dropped and the hole filled with a copy of s0.

THREE CORRECTIONS PER SPEC. All seven get all three.

1. THE COPY-OUT THRESHOLD. Each publish step ends
   `raise SystemExit(0 if len(pngs) >= 16 else 1)`. Post-sync twelve files land,
   so that exits 1. `>= 16` becomes `>= 12`, with a comment recording that 12 is
   `seeds x distinct-ref-sha256` and why it is hardcoded rather than derived: the
   derivation would have to mirror the sampler's slot enumeration, and the
   sampler is being edited by another lane this hour. The better fix stays
   available to whoever touches this next.

2. THE DECLARED `r3` ARTIFACT -- and THIS is the one that actually fails the job.
   The threshold above is on a step carrying `allow_fail: True`, so `box_runner`
   resets its rc to 0 (line 980) and the SystemExit alone cannot fail anything.
   What fails is the artifacts list: all seven declare
   `...-ipa-r3-w015-s0.png` as a sentinel, r3 is the deduplicated cell, surviving
   cells keep their original names, so post-sync that file is never written.
   `resolve_artifact()` wildcards only the beat SLUG (`05-*-ipa-r3-w015-s0.png`),
   which cannot rescue a missing ref index -- so the job lands
   `rc = RC_ARTIFACTS_MISSING` (92), `failed_step = artifact-check`, after the GPU
   has done all the work. Three sentinels for three cells is the correct
   declaration; the r3 line is removed.

3. THE PRE-REGISTERED DENOMINATOR. All seven read "scored by eye per frame across
   all 16, reported as N of 16", so a scorer would report 12/16 as though four
   frames had failed, or hunt for files that were never drawn. This is corrected
   ADDITIVELY: `success:` is left BYTE-IDENTICAL -- the superseded wording stays
   standing, which is the whole point -- and a new top-level
   `frame_count_correction_0817` key states the true count with its reason. What
   is scored does not change by one word. 12 was always the true frame count.

HOUSE PATTERN (same as `insert_b0708_figure_count_0817.py`): sha256 before and
after, a byte delta asserted against the exact payload, a backup per file, and a
PARSED-VARIANT DIFF proving which keys moved and that nothing else did. The trap
that pattern exists for: a lane's anchor once inserted 26 lines INSIDE a folded
scalar with a byte delta that matched perfectly and a sha that moved exactly as
predicted. Only the parsed diff caught it. A checksum landing where you expected
is not proof of a correct edit.

    python3 pipeline/insert_cast0817_frame_count_0817.py            # check only
    python3 pipeline/insert_cast0817_frame_count_0817.py --apply
"""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

JOBS = Path(__file__).resolve().parent / "jobs"
BEATS = ("05", "06", "07", "08", "09", "10", "11")

OLD_RAISE = "raise SystemExit(0 if len(pngs) >= 16 else 1)"
NEW_RAISE = (
    "# frame count is 12, not 16: 4 seeds x 3 DISTINCT reference sha256s. "
    "refs-guards-twoinfield-nos2-0815 holds 3 distinct images in 4 slots (s0 and "
    "s3 are the same bytes; hashed on the box 2026-08-17), and dedup_cells drops "
    "the cell that would redraw s0, so the grid is 3 cells x 4 seeds. Hardcoded "
    "rather than derived from seeds x distinct-ref-sha256 because deriving it "
    "means mirroring the sampler slot enumeration while another lane is editing "
    "the sampler; derive it when that settles.\\n"
    "raise SystemExit(0 if len(pngs) >= 12 else 1)"
)

KEY = "frame_count_correction_0817"


def add_top(beat: str) -> str:
    """The additive correction key. One line per scalar, no folded scalars."""
    return (
        "\n"
        "# --- correction filed 2026-08-17, additive: `success:` above is\n"
        "# --- UNCHANGED and its superseded denominator stays visible. -------\n"
        "%s:\n"
        "  true_frame_count: 12\n"
        "  grid: '3 cells x 4 seeds -- 3 DISTINCT reference sha256s in 4 slots'\n"
        "  denominator_to_report: 'N of 12'\n"
        "  denominator_superseded: 'N of 16 (see the success: key above, left standing verbatim)'\n"
        "  reason: 'refs-guards-twoinfield-nos2-0815 is 3 distinct images in 4"
        " slots -- s0 and s3 are byte-identical (26062B66DFCF9B22..., hashed on"
        " the box 2026-08-17). dedup_cells drops the cell that would redraw s0,"
        " so 12 frames are drawn, never 16. 12 WAS ALWAYS THE TRUE COUNT: the"
        " pre-sync renders of this beat wrote 16 files of which 4 were"
        " byte-copies of the other 12, so a scorer reporting N of 16 was"
        " counting duplicates as independent evidence.'\n"
        "  what_is_scored: 'UNCHANGED. Not one term of the bar is altered,"
        " loosened or removed -- only the denominator it is divided by, which was"
        " miscounted. Every condition in success: still applies per frame.'\n"
        "  also_corrected_in_this_spec: 'copy-out threshold >= 16 -> >= 12, and"
        " the declared artifact NN-*-ipa-r3-w015-s0.png removed: r3 is the"
        " deduplicated cell and is never written, which made box_runner retire"
        " the job rc 92 artifact-check after a full render. The threshold alone"
        " could not fail it -- that step is allow_fail: True.'\n"
        % KEY
    )


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def art_line(text: str, beat: str) -> str:
    """The one declared-artifact line naming the deduplicated r3 cell."""
    hits = [ln for ln in text.split("\n")
            if ln.startswith("- C:") and "-ipa-r3-w015-s0.png" in ln]
    if len(hits) != 1:
        sys.exit("!! beat %s: %d artifact lines name r3, expected 1. Refusing."
                 % (beat, len(hits)))
    return hits[0] + "\n"


def build(text: str, beat: str) -> tuple:
    """(new text, expected byte delta). Every anchor must match EXACTLY ONCE."""
    if text.count(OLD_RAISE) != 1:
        sys.exit("!! beat %s: `%s` matches %d times, expected 1. Refusing."
                 % (beat, OLD_RAISE, text.count(OLD_RAISE)))
    if KEY in text:
        sys.exit("!! beat %s: `%s` is ALREADY in the file. Refusing to "
                 "double-insert." % (beat, KEY))
    if "len(pngs) >= 12" in text:
        sys.exit("!! beat %s already carries the corrected threshold. Refusing."
                 % beat)
    if not text.endswith("\n"):
        sys.exit("!! beat %s does not end in a newline; refusing to append blind."
                 % beat)

    drop = art_line(text, beat)
    top = add_top(beat)

    out = text.replace(OLD_RAISE, NEW_RAISE, 1)
    out = out.replace(drop, "", 1)
    out = out + top

    delta = (len(NEW_RAISE.encode()) - len(OLD_RAISE.encode())
             - len(drop.encode()) + len(top.encode()))
    return out, delta, drop


def parsed_diff(before, after, beat: str, drop: str) -> None:
    """Prove exactly which keys moved. The byte count cannot see an
    indentation slip that swallows a neighbouring block; this can."""
    added = set(after) - set(before)
    removed = set(before) - set(after)
    if removed:
        sys.exit("!! beat %s: a top-level key disappeared: %s"
                 % (beat, sorted(removed)))
    if added != {KEY}:
        sys.exit("!! beat %s: unexpected top-level additions: %s"
                 % (beat, sorted(added)))

    # Every top-level key except the two we deliberately touch must be
    # byte-identical -- `success:` above all, since leaving the superseded
    # denominator standing is the entire point of an additive correction.
    for k in before:
        if k in ("artifacts", "steps"):
            continue
        if before[k] != after[k]:
            sys.exit("!! beat %s: top-level %r changed and must not have."
                     % (beat, k))
    if before["success"] != after["success"]:
        sys.exit("!! beat %s: success: was modified. Refusing." % beat)

    # artifacts: exactly the r3 sentinel gone, order of the rest preserved.
    want = [a for a in before["artifacts"] if "-ipa-r3-w015-s0.png" not in a]
    gone = [a for a in before["artifacts"] if "-ipa-r3-w015-s0.png" in a]
    if len(gone) != 1:
        sys.exit("!! beat %s: %d parsed artifacts name r3." % (beat, len(gone)))
    if after["artifacts"] != want:
        sys.exit("!! beat %s: artifacts list is not the original minus r3."
                 % beat)

    # steps: same count, same keys, and the ONLY textual difference anywhere in
    # any step is the one raise-line swap.
    if len(before["steps"]) != len(after["steps"]):
        sys.exit("!! beat %s: step count changed." % beat)
    swapped = 0
    for i, (b, a) in enumerate(zip(before["steps"], after["steps"])):
        if set(b) != set(a):
            sys.exit("!! beat %s: step %d keys changed." % (beat, i))
        for k in b:
            if b[k] == a[k]:
                continue
            if k != "argv":
                sys.exit("!! beat %s: step %d key %r changed." % (beat, i, k))
            if len(b[k]) != len(a[k]):
                sys.exit("!! beat %s: step %d argv length changed." % (beat, i))
            for j, (bv, av) in enumerate(zip(b[k], a[k])):
                if bv == av:
                    continue
                # The embedded script: assert the swap and NOTHING else.
                expect = bv.replace(OLD_RAISE, NEW_RAISE.replace("\\n", "\n"), 1)
                if av != expect:
                    sys.exit("!! beat %s: step %d argv[%d] differs by more than "
                             "the raise-line swap. Refusing." % (beat, i, j))
                swapped += 1
    if swapped != 1:
        sys.exit("!! beat %s: %d argv entries changed, expected exactly 1."
                 % (beat, swapped))

    print("   beat %s parsed diff OK: +%s, artifacts 4->3 (r3 only), "
          "1 argv swap, success: byte-identical" % (beat, KEY))
    print("   beat %s dropped sentinel: %s" % (beat, drop.strip()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--beats", default=",".join(BEATS))
    a = ap.parse_args()

    import yaml  # noqa: E402

    beats = [b for b in a.beats.split(",") if b]
    rc = 0
    for beat in beats:
        target = JOBS / ("ep2-b%s-cast-0817.yaml" % beat)
        before_txt = target.read_text()
        before = yaml.safe_load(before_txt)
        after_txt, exp, drop = build(before_txt, beat)
        delta = len(after_txt.encode()) - len(before_txt.encode())

        print("\n=== ep2-b%s-cast-0817 ===" % beat)
        print("   sha256 before   %s" % sha(target))
        print("   bytes  before   %d" % len(before_txt.encode()))
        print("   byte delta      %+d   (expected %+d)" % (delta, exp))
        if delta != exp:
            sys.exit("!! beat %s: byte delta != payload. Something other than "
                     "the three intended edits happened." % beat)

        after = yaml.safe_load(after_txt)
        parsed_diff(before, after, beat, drop)

        pub = [s for s in after["steps"] if "len(pngs) >=" in str(s.get("argv"))]
        if len(pub) != 1 or "len(pngs) >= 12" not in str(pub[0]["argv"]):
            sys.exit("!! beat %s: corrected threshold not present after build."
                     % beat)
        if after[KEY]["true_frame_count"] != 12:
            sys.exit("!! beat %s: correction key does not say 12." % beat)

        if not a.apply:
            print("   --check only: nothing written.")
            continue

        backup = target.with_suffix(".yaml.bak-castframecount-0817")
        shutil.copy2(target, backup)
        target.write_text(after_txt)
        print("   backup          %s" % backup.name)
        print("   sha256 after    %s" % sha(target))
        print("   bytes  after    %d" % len(target.read_bytes()))
    if not a.apply:
        print("\nRe-run with --apply to write.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
