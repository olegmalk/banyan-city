#!/usr/bin/env python3
"""Thumbnails for /queue's gallery — because the real frames are 860 KB each.

The founder, 2026-08-14, on the first /queue: *"i expected you to be able to
scroll, see images and prompts and these details all with a nice interface."*
A gallery is the right answer and it has one hard constraint nobody would guess
from the markup: **the artifacts are full-resolution PNGs, median 862 KB**, and
there are 348 of them behind the newest-first grid. Pointing `<img>` at the
originals makes a page that costs 300 MB to scroll — on his phone, on cellular.
`loading="lazy"` does not save that; it only spreads it over the scroll.

So this writes a 512 px JPEG for every image the page can show, and the page
prefers it with an `onerror` fall back to the original bytes. Same picture,
~4% of the bytes, and a missing thumb degrades to a slow card rather than a
hole.

WHERE THEY LIVE, and why not here. Media is never committed to `main` and never
copied into `_site/` (SITE.md). The originals already live on
`farm-results-rtx5090`; the thumbs go on their own branch, `site-thumbs`, for
one reason — **the box pushes to the results branch on its own schedule** and a
laptop pushing 20 MB of derived files into that same branch is a push war
waiting to happen (it has happened here before). A branch only this script
writes cannot collide with the courier.

    python3 pipeline/queue_thumbs.py            # write JPEGs to a scratch dir
    python3 pipeline/queue_thumbs.py --push     # ...and publish them

`--push` works in a throwaway clone under the system temp dir, never in this
working tree: several lanes share this checkout and `git checkout --orphan`
here would yank the branch out from under them.

Re-run it after `queue_history.py` adds jobs. Nothing breaks if you forget —
the new cards simply load their full-size originals.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HISTORY = REPO / "pipeline" / "measured" / "queue-history.json"

SOURCE_REF = "origin/farm-results-rtx5090"
THUMB_BRANCH = "site-thumbs"

# 512 px long edge: sharp on a 3x phone at the card size the grid uses, and
# still a legible strip thumbnail in the lightbox. q72 because these are flat
# anime cels — the ringing that would show on a photograph does not show here.
MAX_EDGE = 512
QUALITY = 72


def wanted(data: dict) -> list[str]:
    """Every artifact path the gallery can put on screen as a picture.

    Both the outputs and the init frames: the lightbox shows the frame a render
    started from next to what it produced, and that comparison is the whole
    reason the founder asked for the page.
    """
    seen: dict[str, None] = {}
    for job in data.get("jobs") or []:
        if not isinstance(job, dict):
            continue
        for out in job.get("outputs") or []:
            if out.get("kind") == "image" and out.get("path"):
                seen[str(out["path"])] = None
        init = job.get("init") or {}
        if init.get("path"):
            seen[str(init["path"])] = None
        ref = job.get("reference") or {}
        if ref.get("path"):
            seen[str(ref["path"])] = None
    return list(seen)


def thumb_rel(path: str) -> str:
    """`farm-out/x/y.png` → `farm-out/x/y.jpg`, the same shape on the thumb
    branch. Mirroring the path rather than hashing it means a thumb belongs to
    an artifact and not to a job id — a re-run history that picks a different
    frame for a card still finds the right file."""
    p = str(path).replace("\\", "/").lstrip("/")
    return p.rsplit(".", 1)[0] + ".jpg" if "." in p.rsplit("/", 1)[-1] else p + ".jpg"


def read_blobs(paths: list[str], ref: str = SOURCE_REF):
    """Stream the artifact bytes straight out of the object store.

    `git cat-file --batch` in one process: the results branch is already
    fetched, so this never touches the network and never checks the branch out.
    Yields `(path, bytes | None)` — None for an artifact the branch does not
    carry, which is a fact the caller reports rather than an error.
    """
    proc = subprocess.Popen(
        ["git", "-C", str(REPO), "cat-file", "--batch"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for path in paths:
            proc.stdin.write(f"{ref}:{path}\n".encode())
            proc.stdin.flush()
            header = proc.stdout.readline().decode("utf-8", "replace").strip()
            if header.endswith(("missing", "ambiguous")) or " " not in header:
                yield path, None
                continue
            size = int(header.rsplit(" ", 1)[-1])
            body = proc.stdout.read(size)
            proc.stdout.read(1)                      # the trailing newline
            yield path, body
    finally:
        try:
            proc.stdin.close()
        except OSError:
            pass
        proc.wait()


def shrink(raw: bytes) -> bytes | None:
    """One artifact → one JPEG, or None if the bytes are not a picture we can
    read. A corrupt frame on the branch must cost one card its thumbnail, not
    the whole run."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception:
        return None
    img = img.convert("RGB")
    img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return buf.getvalue()


def generate(out_dir: Path, paths: list[str], skip_existing: bool = True) -> dict:
    made = missing = skipped = unreadable = 0
    total = 0
    todo = []
    for p in paths:
        dest = out_dir / thumb_rel(p)
        if skip_existing and dest.is_file():
            skipped += 1
            total += dest.stat().st_size
            continue
        todo.append(p)
    for path, raw in read_blobs(todo):
        if raw is None:
            missing += 1
            continue
        jpeg = shrink(raw)
        if jpeg is None:
            unreadable += 1
            continue
        dest = out_dir / thumb_rel(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(jpeg)
        made += 1
        total += len(jpeg)
        if made % 100 == 0:
            print(f"  … {made} thumbs, {total / 1e6:.1f} MB", flush=True)
    return {"made": made, "skipped": skipped, "missing": missing,
            "unreadable": unreadable, "bytes": total}


def publish(src_dir: Path) -> str:
    """Put the JPEGs on `site-thumbs`, from a repository that is not this one.

    A fresh `git init` and not a clone. The first attempt cloned this repo and
    branched orphan off it, which does two bad things: banyan-city is a shallow
    checkout, so `--local` is ignored and the clone copies 1.7 GB of objects to
    move 27 MB of JPEGs, and `checkout --orphan` after `clone --no-checkout`
    lands main's whole working tree in the index — the push carried 4,160 files
    that were not thumbnails. An empty repository can only contain what is put
    in it.
    """
    with tempfile.TemporaryDirectory(prefix="banyan-thumbs-") as tmp:
        work = Path(tmp) / "repo"
        work.mkdir(parents=True)
        run = lambda *a: subprocess.run(  # noqa: E731
            ["git", "-C", str(work), *a], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode(
                "utf-8", "replace")
        origin = subprocess.run(
            ["git", "-C", str(REPO), "remote", "get-url", "origin"],
            check=True, stdout=subprocess.PIPE).stdout.decode().strip()
        run("init", "--quiet")
        run("symbolic-ref", "HEAD", f"refs/heads/{THUMB_BRANCH}")
        run("remote", "add", "origin", origin)
        subprocess.run(["cp", "-R", f"{src_dir}/.", str(work)], check=True)
        (work / "README.md").write_text(
            "# site-thumbs\n\n512 px JPEG thumbnails of the render artifacts on "
            "`farm-results-rtx5090`, written by `pipeline/queue_thumbs.py` and "
            "read by /queue's gallery over the raw CDN. Derived files only — "
            "every original lives on the results branch, and a thumbnail that "
            "is missing here costs a card its fast preview and nothing else.\n",
            encoding="utf-8")
        run("add", "-A")
        run("-c", "user.name=banyan-thumbs", "-c", "user.email=thumbs@banyan.city",
            "commit", "-m", "512px thumbnails for /queue's gallery")
        run("push", "--force", "origin", f"{THUMB_BRANCH}:{THUMB_BRANCH}")
        return run("rev-parse", "HEAD").strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="where the JPEGs go")
    ap.add_argument("--push", action="store_true",
                    help=f"publish them to the {THUMB_BRANCH} branch")
    ap.add_argument("--limit", type=int, default=0, help="first N only, for a sample")
    args = ap.parse_args(argv)

    out = Path(args.out) if args.out else Path(tempfile.gettempdir()) / "banyan-queue-thumbs"
    out.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(HISTORY.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"cannot read {HISTORY}: {exc}", file=sys.stderr)
        return 1
    paths = wanted(data)
    if args.limit:
        paths = paths[:args.limit]
    print(f"{len(paths)} artifacts to thumbnail → {out}")
    got = generate(out, paths)
    print(f"✓ {got['made']} written, {got['skipped']} already there, "
          f"{got['missing']} not on {SOURCE_REF}, {got['unreadable']} unreadable "
          f"— {got['bytes'] / 1e6:.1f} MB")
    if args.push:
        head = publish(out)
        print(f"✓ pushed {THUMB_BRANCH} at {head[:9]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
