#!/usr/bin/env python3
"""Derive a fixed motion job from a -lw job, renaming EVERY inherited token.

Why this exists. The -lw wave was derived by copying a parent job and editing
only the id, the crop --src and the prompt. Everything else kept the parent's
names, so nineteen jobs wrote their init to `b13-init-704x1280.png`, published
an mp4 called `13-remake-LTX-0813.mp4`, and copied it into a directory named
for the id MINUS its date suffix. None of that changed a single pixel -- the
srcs were right and every output was distinct -- but it makes an artifact
unreadable from its own filename, and the id-minus-suffix dst is the exact
prefix shape that has published a twin into its sibling's directory four
times. A name that lies is a defect even when the bytes are correct.

So this deriver rewrites the tokens as a set: bench jsonl, output mp4, init
png, payload prefix, job id, and the publish dst -- which here is the FULL id,
never a prefix of it. Order matters and is enforced below: the longest and most
specific token goes first, because `b13-` is a substring of both
`b13-init-704x1280.png` and `bench-b13-remake.jsonl`.

It edits the raw YAML text rather than a parsed tree on purpose. The payload
carries JSON with Windows paths inside double-escaped strings; round-tripping
that through a YAML dumper reflows it into a different-but-equivalent file and
the diff stops being readable. Every token replaced is plain ASCII with no
quoting significance, so text is the safe surface. The result is parsed at the
end and refused if it does not load.
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BRANCH = "origin/farm-results-rtx5090"
BOX_FARM_OUT = "C:\\banyan-farm\\courier-box\\farm-out"


def blob_sha(path: str) -> str:
    """sha256 of a file as it exists on the results branch.

    The box crops from its own courier-box copy, which is the same bytes the
    courier pushed -- so the branch is a legitimate place to read the hash the
    crop step will assert. If they ever disagree the crop refuses, which is the
    behaviour we want: a mismatch means the box copy is not what we scored.
    """
    out = subprocess.run(["git", "show", f"{BRANCH}:{path}"], cwd=REPO,
                         capture_output=True)
    if out.returncode != 0 or not out.stdout:
        sys.exit(f"!! not on {BRANCH}: {path}")
    return hashlib.sha256(out.stdout).hexdigest()


def tokens(text: str) -> dict:
    """The inherited names in a -lw job, read off the job instead of guessed."""
    t = {}
    m = re.search(r"bench-[A-Za-z0-9_-]+\.jsonl", text)
    t["bench"] = m.group(0) if m else ""
    m = re.search(r"\d\d-[A-Za-z0-9-]+-LTX-[A-Za-z0-9-]+\.mp4", text)
    t["mp4"] = m.group(0) if m else ""
    m = re.search(r"b\d\d-init-\d+x\d+\.png", text)
    t["png"] = m.group(0) if m else ""
    m = re.search(r"(b\d\d)-motion-prompt\.txt", text)
    t["prefix"] = m.group(1) + "-" if m else ""
    m = re.search(r"^id:\s*(\S+)\s*$", text, re.M)
    t["id"] = m.group(1) if m else ""
    return t


def derive(src_yaml: Path, new_id: str, beat: int, slug: str, tag: str,
           prompt: str = "", plate: str = "", seed: int = 0) -> str:
    text = src_yaml.read_text(encoding="utf-8")
    old = tokens(text)
    for k in ("bench", "mp4", "png", "prefix", "id"):
        if not old[k]:
            sys.exit(f"!! could not find the {k} token in {src_yaml.name}")

    bb = f"b{beat:02d}"
    new = {
        "bench": f"bench-{bb}-{tag}.jsonl",
        "mp4": f"{beat:02d}-{slug}-LTX-{tag}.mp4",
        "png": f"{bb}-init-704x1280.png",
        "prefix": f"{bb}-",
        "id": new_id,
    }
    # Longest first: b13- lives inside b13-init-...png and bench-b13-....jsonl.
    for k in ("bench", "mp4", "png", "prefix", "id"):
        text = text.replace(old[k], new[k])
    # The dst was the id minus its date suffix; whatever survives the id
    # replacement is that prefix, and it becomes the full id.
    stale_dst = re.sub(r"-\d{4}$", "", old["id"])
    if stale_dst != old["id"]:
        text = text.replace(stale_dst, new_id)

    if plate:
        # Exact-string swap, not a pattern. The crop argv is a YAML block
        # sequence, so a regex whose \s* can cross a newline happily eats the
        # "- " item marker off the following line and produces a file that no
        # longer parses. The old values are read from the parsed source, which
        # is unambiguous, and replaced literally.
        old_argv = [s for s in yaml.safe_load(src_yaml.read_text(encoding="utf-8"))["steps"]
                    if s.get("name") == "crop"][0]["argv"]
        old_src = old_argv[old_argv.index("--src") + 1]
        old_sha = old_argv[old_argv.index("--sha256") + 1]
        win = BOX_FARM_OUT + "\\" + plate.split("farm-out/", 1)[1].replace("/", "\\")
        text = text.replace(old_src, win).replace(old_sha, blob_sha(plate))
    if prompt:
        style = ("2D anime, hand-drawn cel animation, flat cel shading, clean ink linework, "
                 "anime key art, cinematic lighting, detailed, newest, masterpiece, "
                 "best quality, very aesthetic.")
        text = re.sub(rf"({bb}-motion-prompt\.txt: ).*",
                      lambda m: m.group(1) + f"'{prompt} {style}'", text, count=1)
    if seed:
        text = re.sub(r'\\"seed\\": \d+', f'\\\\"seed\\\\": {seed}', text)

    doc = yaml.safe_load(text)          # refuse anything that will not parse
    if doc.get("id") != new_id:
        sys.exit(f"!! id did not take: {doc.get('id')}")
    leftover = [k for k in ("b13-", "b05-init", "13-remake", "06-the-clipboard-LTX")
                if k in text and not k.startswith(f"b{beat:02d}")]
    if leftover:
        sys.exit(f"!! inherited tokens survived in {new_id}: {leftover}")
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--beat", type=int, required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--prompt", default="")
    ap.add_argument("--plate", default="", help="path on the results branch")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    text = derive(Path(a.src), a.id, a.beat, a.slug, a.tag, a.prompt, a.plate, a.seed)
    out = REPO / "pipeline" / "jobs" / f"{a.id}.yaml"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
