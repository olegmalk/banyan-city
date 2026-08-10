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


class Args:
    """The attribute bag argparse would hand cmd_manifest / cmd_verify."""

    def __init__(self, **kw):
        self.__dict__.update({"genome": "sapling", "node": "n", "dir": None})
        self.__dict__.update(kw)


def fake_repo(td: Path, files: dict) -> Path:
    """A REPO root holding genomes/sapling/nodes/n/takes/ with `files` in it."""
    takes = td / "genomes" / "sapling" / "nodes" / "n" / "takes"
    takes.mkdir(parents=True)
    for rel, body in files.items():
        p = takes / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
    return takes


def test_an_empty_manifest_is_not_a_pass():
    """A manifest that lists nothing matched every directory and said PASS.

    `0/0 match` then `TAKES-VERIFY: PASS` is the whole failure: verify compared
    nothing and printed the sentence that means the copy is intact. A manifest
    truncated to its header, one built before the frames were copied, or one
    written against the wrong path all produce it — and this file is the only
    in-repo record that the gitignored frames ever existed, so nothing else
    would ever contradict it.
    """
    real_repo = tb.REPO
    with tempfile.TemporaryDirectory() as td:
        try:
            tb.REPO = Path(td)
            takes = fake_repo(Path(td), {"stills/01-a.png": b"pixels-a"})
            # a manifest with only its header — parse_manifest skips comments,
            # so `recorded` comes out empty
            (takes / tb.MANIFEST_NAME).write_text("# a header and nothing else\n")
            rc = tb.cmd_verify(Args())
            check("an empty manifest fails verify instead of passing it", rc != 0)

            # and the ordinary case still passes, so this is not just "always red"
            (takes / tb.MANIFEST_NAME).write_text(
                "\n".join(tb.manifest_lines(takes)) + "\n")
            check("a real manifest still verifies clean", tb.cmd_verify(Args()) == 0)
        finally:
            tb.REPO = real_repo


def test_manifesting_an_empty_corpus_is_refused():
    """Writing the empty manifest is the moment the green starts.

    `manifest` on a takes/ with no files wrote a header, printed
    "0 files, 0 bytes" and exited 0 — a backup that never ran, recorded as done.
    Refusing at write time means the passing verify above can never be created.
    """
    real_repo = tb.REPO
    with tempfile.TemporaryDirectory() as td:
        try:
            tb.REPO = Path(td)
            takes = fake_repo(Path(td), {})
            rc = tb.cmd_manifest(Args())
            check("manifesting an empty takes/ is refused", rc != 0)
            check("and no empty manifest is left behind",
                  not (takes / tb.MANIFEST_NAME).exists())

            (takes / "stills").mkdir()
            (takes / "stills" / "01-a.png").write_bytes(b"pixels-a")
            check("a real corpus still manifests", tb.cmd_manifest(Args()) == 0)
        finally:
            tb.REPO = real_repo


def main() -> int:
    for fn in [
        test_manifest_covers_every_file_but_itself,
        test_manifest_format_is_shasum_c_compatible,
        test_parse_manifest_ignores_comments_and_blanks,
        test_verify_detects_a_corrupted_copy,
        test_verify_detects_a_missing_file,
        test_an_empty_manifest_is_not_a_pass,
        test_manifesting_an_empty_corpus_is_refused,
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
