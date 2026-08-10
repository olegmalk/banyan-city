#!/usr/bin/env python3
"""Manifest and verify a node's takes/ corpus — the durability half of the
takes/ ignore rule.

`.gitignore` keeps candidate media out of the tree on purpose: pick-of-N frames
are ~1.2 MB each and dozens per beat, and only the frame the founder picks is
promoted into git. The cost of that rule is that a clean `git status` over
takes/ means "ignored", not "safe" — the pixels live on one disk and git holds
no record that they ever existed.

This closes the gap without touching the ignore rule. The manifest is text, so
it is tracked, it is small, and it turns an off-repo copy into a *restorable*
one: filename, sha256 and size for every file the ignore rule hides, committed
beside the sidecars that describe them.

    python3 pipeline/takes_backup.py manifest sapling 002b-first-citizen
    python3 pipeline/takes_backup.py verify   sapling 002b-first-citizen
    python3 pipeline/takes_backup.py verify   sapling 002b-first-citizen \
        --dir /path/to/a/restored/copy

Restore procedure and the off-repo copy locations are in
`TAKES-DURABILITY.md`. Rebuild the manifest after any render round that
adds candidates, or `verify` starts reporting the new frames as missing.
"""

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST_NAME = "MANIFEST.sha256"

HEADER = """\
# sha256 manifest of {node}'s takes/ corpus — see TAKES-DURABILITY.md.
# Written by pipeline/takes_backup.py; the media itself is gitignored by
# design, so this file is the only in-repo record that these frames exist.
# Verify a copy anywhere:  shasum -a 256 -c {manifest}
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def corpus_files(takes_dir: Path) -> list[Path]:
    """Every regular file under takes/ except the manifest itself, sorted.

    Deliberately not filtered by extension: the manifest's job is to describe
    the whole directory as it stands, so a restored copy can be checked for
    completeness rather than only for the file types today's ignore rule
    happens to list.
    """
    return sorted(
        p
        for p in takes_dir.rglob("*")
        if p.is_file() and p.name != MANIFEST_NAME and not p.name.startswith(".")
    )


def manifest_lines(takes_dir: Path) -> list[str]:
    return [
        f"{sha256(p)}  {p.relative_to(takes_dir).as_posix()}"
        for p in corpus_files(takes_dir)
    ]


def parse_manifest(text: str) -> dict[str, str]:
    """path -> sha256, ignoring comments and blanks (shasum -c's own rules)."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        if rel:
            out[rel] = digest
    return out


def takes_dir_for(genome: str, node: str) -> Path:
    return REPO / "genomes" / genome / "nodes" / node / "takes"


def cmd_manifest(args) -> int:
    takes = takes_dir_for(args.genome, args.node)
    if not takes.is_dir():
        print(f"no takes/ under {takes}", file=sys.stderr)
        return 2
    lines = manifest_lines(takes)
    path = takes / MANIFEST_NAME
    path.write_text(
        HEADER.format(node=args.node, manifest=path.relative_to(REPO).as_posix())
        + "\n".join(lines)
        + "\n"
    )
    total = sum(p.stat().st_size for p in corpus_files(takes))
    print(f"{path.relative_to(REPO)}: {len(lines)} files, {total} bytes")
    return 0


def cmd_verify(args) -> int:
    takes = takes_dir_for(args.genome, args.node)
    path = takes / MANIFEST_NAME
    if not path.is_file():
        print(f"no manifest at {path} — run `manifest` first", file=sys.stderr)
        return 2
    recorded = parse_manifest(path.read_text())

    target = Path(args.dir).expanduser().resolve() if args.dir else takes
    if not target.is_dir():
        print(f"not a directory: {target}", file=sys.stderr)
        return 2
    present = {
        p.relative_to(target).as_posix(): p
        for p in corpus_files(target)
    }

    missing = sorted(set(recorded) - set(present))
    extra = sorted(set(present) - set(recorded))
    changed = sorted(
        rel
        for rel, digest in recorded.items()
        if rel in present and sha256(present[rel]) != digest
    )

    for rel in missing:
        print(f"MISSING  {rel}")
    for rel in changed:
        print(f"CHANGED  {rel}")
    for rel in extra:
        print(f"UNRECORDED  {rel}")

    ok = len(recorded) - len(missing) - len(changed)
    print(f"{target}: {ok}/{len(recorded)} match")
    if missing or changed:
        print("TAKES-VERIFY: FAIL")
        return 1
    # An unrecorded file is a stale manifest, not a lost frame: say so loudly
    # enough to get the manifest rebuilt, but do not fail a copy that is intact.
    if extra:
        print(f"TAKES-VERIFY: PASS (manifest stale — {len(extra)} unrecorded)")
    else:
        print("TAKES-VERIFY: PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("manifest", help="write takes/MANIFEST.sha256")
    m.add_argument("genome")
    m.add_argument("node")
    m.set_defaults(func=cmd_manifest)

    v = sub.add_parser("verify", help="check a copy against the manifest")
    v.add_argument("genome")
    v.add_argument("node")
    v.add_argument("--dir", help="verify this directory instead of takes/")
    v.set_defaults(func=cmd_verify)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
