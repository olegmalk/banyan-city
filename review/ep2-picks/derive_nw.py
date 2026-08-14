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
           prompt: str = "", plate: str = "", seed: int = 0, frames: int = 0) -> str:
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
    # Order is load-bearing twice over. bench/mp4/png come before "prefix"
    # because b13- lives inside b13-init-...png and bench-b13-....jsonl. And
    # "id" must come before "prefix" too: when the parent was itself derived,
    # its id CONTAINS its beat prefix -- ep2-b05-nw-0815 holds "b05-" -- so
    # swapping the prefix first rewrites the id out from under the id swap and
    # the job silently comes out named for the wrong beat. It failed loudly
    # here only because the parse check compares the id afterwards.
    for k in ("bench", "mp4", "png", "id", "prefix"):
        text = text.replace(old[k], new[k])
    # The dst was the id minus its date suffix; whatever survives the id
    # replacement is that prefix, and it becomes the full id.
    # Only for parents whose dst really was the id-minus-date PREFIX. Jobs this
    # script already produced use the FULL id as their dst, and for those the
    # stale prefix is also a prefix of the NEW id -- so replacing it a second
    # time rewrites the id inside itself and yields ep2-b06-scnbB-0815B-0815.
    stale_dst = re.sub(r"-\d{4}$", "", old["id"])
    if stale_dst != old["id"] and not new_id.startswith(stale_dst):
        text = text.replace(stale_dst, new_id)

    # The beat NUMBER, which is metadata rather than conditioning and so was
    # silently inherited: three jobs went out recording beat 5 while cropping
    # beat 6, 7 and 9's plates. The render would have been correct and the
    # provenance a lie, which is the same defect class as the inherited
    # filenames this whole script exists to stop.
    text, n = re.subn(r"^beat:\s*\d+\s*$", f"beat: {beat}", text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"!! expected one beat field, replaced {n}")

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
        # The token loop above has ALREADY rewritten the text, and a parent's
        # plate path can contain its beat prefix -- ep2-b05-scene-0814 holds
        # "b05-". So the string to search for is the source's path AFTER the
        # same substitutions, not as it appears in the source file. Skipping
        # this made the swap silently miss: the job kept a mangled path built
        # from the new beat's directory and the old beat's filename, and only
        # plate_check.py noticed, by failing to fetch it.
        for k in ("bench", "mp4", "png", "id", "prefix"):
            old_src = old_src.replace(old[k], new[k])
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
    if frames:
        # Anchored to the flag, never to the bare number: "97" also appears in
        # seeds, sha prefixes and est_minutes, and a loose replace would hit
        # them. LTX wants 8n+1.
        if (frames - 1) % 8:
            sys.exit(f"!! frames must be 8n+1, got {frames}")
        text, n = re.subn(r"(--frames\n\s+- )'?\d+'?", lambda m: m.group(1) + f"'{frames}'", text)
        if n != 1:
            sys.exit(f"!! expected one --frames value, replaced {n}")

    doc = yaml.safe_load(text)          # refuse anything that will not parse
    if doc.get("id") != new_id:
        sys.exit(f"!! id did not take: {doc.get('id')}")
    # Check the tokens THIS derivation actually replaced, not a hardcoded list.
    # The hardcoded version false-fired on beat 6: its correct new filename is
    # 06-the-clipboard-LTX-scn.mp4, which contains the very token the list was
    # watching for. A guard that fails on a correct output teaches people to
    # bypass guards.
    leftover = [old[k] for k in ("bench", "mp4", "png", "id", "prefix")
                if old[k] != new[k] and old[k] in text]
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
    ap.add_argument("--frames", type=int, default=0, help="LTX frame count, 8n+1")
    a = ap.parse_args()

    text = derive(Path(a.src), a.id, a.beat, a.slug, a.tag, a.prompt, a.plate, a.seed,
                  a.frames)
    out = REPO / "pipeline" / "jobs" / f"{a.id}.yaml"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
