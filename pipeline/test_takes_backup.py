#!/usr/bin/env python3
"""Tests for pipeline/takes_backup.py — the takes/ durability manifest.

Pure filesystem, no network and no box: builds a tiny takes/ tree in a temp
dir and drives the same functions the real corpus uses. The regressions that
matter here are silent ones — a manifest that quietly omits a file, or a
verify that passes on a corrupted copy — because both look like success and
both are only discovered when someone actually needs the backup.

Run: python3 pipeline/test_takes_backup.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import takes_backup as tb

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def make_takes(root: Path) -> Path:
    takes = root / "takes"
    (takes / "stills").mkdir(parents=True)
    (takes / "stills" / "01-a.png").write_bytes(b"pixels-a")
    (takes / "stills" / "01-a.png.meta.yaml").write_text("model: test\n")
    (takes / "stills" / "02-b.png").write_bytes(b"pixels-b")
    (takes / ".DS_Store").write_bytes(b"junk")
    return takes


def test_manifest_covers_every_file_but_itself():
    with tempfile.TemporaryDirectory() as td:
        takes = make_takes(Path(td))
        lines = tb.manifest_lines(takes)
        (takes / tb.MANIFEST_NAME).write_text("\n".join(lines) + "\n")
        paths = set(tb.parse_manifest("\n".join(lines)))
        check(
            "manifest lists media and sidecars alike",
            paths
            == {"stills/01-a.png", "stills/01-a.png.meta.yaml", "stills/02-b.png"},
        )
        check(
            "manifest excludes itself and dotfiles",
            tb.MANIFEST_NAME not in "".join(lines) and ".DS_Store" not in "".join(lines),
        )


def test_manifest_format_is_shasum_c_compatible():
    with tempfile.TemporaryDirectory() as td:
        takes = make_takes(Path(td))
        line = tb.manifest_lines(takes)[0]
        digest, sep, rel = line.partition("  ")
        check("two-space separator", sep == "  ")
        check("lowercase hex digest of length 64", len(digest) == 64 and digest.islower())
        check("path is relative to takes/", not rel.startswith("/"))


def test_parse_manifest_ignores_comments_and_blanks():
    parsed = tb.parse_manifest("# header\n\nabc  stills/x.png\n# trailing\n")
    check("comments and blanks skipped", parsed == {"stills/x.png": "abc"})


def test_verify_detects_a_corrupted_copy():
    with tempfile.TemporaryDirectory() as td:
        takes = make_takes(Path(td))
        before = tb.parse_manifest("\n".join(tb.manifest_lines(takes)))
        (takes / "stills" / "02-b.png").write_bytes(b"pixels-CORRUPT")
        after = tb.parse_manifest("\n".join(tb.manifest_lines(takes)))
        check(
            "a one-byte change moves the digest",
            before["stills/02-b.png"] != after["stills/02-b.png"],
        )
        check("untouched files keep their digest", before["stills/01-a.png"] == after["stills/01-a.png"])


def test_verify_detects_a_missing_file():
    with tempfile.TemporaryDirectory() as td:
        takes = make_takes(Path(td))
        recorded = tb.parse_manifest("\n".join(tb.manifest_lines(takes)))
        (takes / "stills" / "02-b.png").unlink()
        present = {
            p.relative_to(takes).as_posix() for p in tb.corpus_files(takes)
        }
        check("deletion shows up as missing", set(recorded) - present == {"stills/02-b.png"})


def main() -> int:
    for fn in [
        test_manifest_covers_every_file_but_itself,
        test_manifest_format_is_shasum_c_compatible,
        test_parse_manifest_ignores_comments_and_blanks,
        test_verify_detects_a_corrupted_copy,
        test_verify_detects_a_missing_file,
    ]:
        print(fn.__name__)
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: " + ", ".join(FAILURES))
        return 1
    print("all takes_backup tests pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
