#!/usr/bin/env python3
"""Turn a curation yaml into a kohya-shaped LoRA dataset: captions + manifest.

    python3 pipeline/lora/build_dataset.py jerry           # write captions + manifest
    python3 pipeline/lora/build_dataset.py jerry --check    # verify, write nothing

WHAT THIS DOES AND WHY IT IS A SCRIPT RATHER THAN 31 HAND-WRITTEN FILES.

Every frame in the set was rendered from a prompt that is ALREADY WRITTEN IN OUR
BOORU DIALECT and is stored verbatim in the frame's own `.yaml` sidecar
(`prompt:`, written by the renderer at draw time, §7.2). That prompt is a better
caption source than a tagger would be, for two reasons:

  - it is ground truth about what was ASKED, at the exact wording the founder
    ratified, rather than a model's guess about what was drawn; and
  - it is already comma-separated tags ending in the animagine booster tags, so
    the caption dialect matches the inference dialect for free. A caption
    written in prose while inference is written in tags trains a mapping we
    never use.

A tagger pass (`wd-eva02-large-tagger-v3` @ 0.35, research doc §4) is still the
right SECOND step and is named in the README -- it catches what the model drew
that nobody asked for, which on this dataset is not hypothetical: nine frames
came back wearing glasses. But the tagger needs onnxruntime on the box, and this
runs on the Mac for $0 today.

THE PRUNE RULE (research doc §4), which is the only interesting logic here:
tags naming a PERMANENT attribute are deleted so the trigger absorbs them; tags
naming a VARIABLE stay, so they stay promptable. Deleting `green skin, bald
head, patchwork cloak` is what makes `bnyjerry` alone reproduce them. Keeping
`crouching`, `wide shot`, `warm amber afternoon light` is what keeps us able to
steer pose, framing and light afterwards.

TRIGGER PLACEMENT. The identity run is replaced IN PLACE by the trigger and then
hoisted to the head of the tag string, because booru-trained models weight the
head of the caption most and every community guide puts the activation tag
first. Hoisting matters for the frames where the goblin is not the grammatical
subject (beat 16 opens on a leaf); without it those captions would bury the
trigger behind a foreground object and teach it weakly.

NO IMAGE IS COPIED OR MODIFIED. The frames stay where they are in farm-out/ and
the manifest addresses them by repo-relative path + sha256, so a frame that is
edited or re-rendered under the same name makes `--check` fail loudly instead of
silently changing what the LoRA trained on.
"""

import argparse
import hashlib
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LORA = os.path.join(REPO, "pipeline", "lora")


def _yaml():
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML required: python3 -m pip install pyyaml")
    return yaml


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_prompt(png):
    """The prompt the renderer recorded for this frame, or None.

    Sidecars are `<name>.yaml` beside `<name>.png`. Parsed with a regex rather
    than yaml.safe_load on purpose: several of these sidecars carry unquoted
    colons and bracket sequences inside `done_when:` prose that make
    safe_load raise, and at least one file in review/ is already known not to
    parse. The one key we need is machine-written and always quoted.
    """
    # TWO SIDECAR NAMES, AND THE SECOND IS NOT A TIDINESS ADDITION. The mac
    # plate path writes `<name>.yaml`; `controlnet_plate.py:472` writes
    # `<name>.png.meta.yaml`. Every box-rendered frame therefore looked to this
    # function like a frame with NO recorded prompt, and a frame with no prompt
    # is silently dropped from the dataset by the caller. That would have
    # excluded the entire reference-route set -- the only frames in the tree
    # that carry the tile's proportion -- from the LoRA, without an error.
    for side in (png[:-4] + ".yaml", png + ".meta.yaml"):
        if os.path.exists(side):
            break
    else:
        return None, None
    text = open(side, encoding="utf-8", errors="replace").read()
    m = re.search(r'^prompt:\s*"(.*?)"\s*$', text, re.M | re.S)
    prompt = m.group(1).strip() if m else None
    if prompt is None:
        # THE BLOCK-SCALAR FORM, which is what controlnet_plate.py writes:
        #     prompt: |-
        #       masterpiece, best quality, ...
        # Read the indented run and rejoin it, because a prompt folded across
        # lines is still one tag string and the prune patterns are written
        # against the single-line form.
        b = re.search(r'^prompt:\s*\|-?\s*\n((?:[ \t]+.*\n?)+)', text, re.M)
        if b:
            prompt = " ".join(l.strip() for l in b.group(1).splitlines()
                              if l.strip())
    s = re.search(r'^size:\s*"?([0-9]+x[0-9]+)', text, re.M)
    return prompt, (s.group(1) if s else None)


def tidy(text):
    """Repair the punctuation a deletion leaves behind."""
    text = re.sub(r"\s+", " ", text)
    # ", , " and "; , " left by removing a whole tag
    text = re.sub(r"(?:,\s*){2,}", ", ", text)
    text = re.sub(r";\s*,", ";", text)
    text = re.sub(r",\s*;", ";", text)
    # a clause that lost its subject: ", sitting" after "leaf fills the frame,"
    text = re.sub(r"^\s*[,;]\s*", "", text)
    text = re.sub(r"\s*[,;]\s*$", "", text)
    text = re.sub(r"\s+([,;.])", r"\1", text)
    return text.strip()


def caption_for(prompt, spec):
    """Apply rewrite + prune, insert the trigger in place, hoist it to the head."""
    trigger = spec["trigger"]
    out = prompt

    # Rewrites first: they narrow phrases the prune list would otherwise miss
    # (`both green clawed hands` -> `both hands`), and doing them after prune
    # would leave orphaned adjectives.
    for src, dst in (spec.get("rewrite") or {}).items():
        out = re.sub(re.escape(src), dst, out, flags=re.I)

    # Prune: replace the FIRST identity run with the trigger, delete any others.
    placed = False
    for phrase in spec.get("prune") or []:
        pat = re.compile(re.escape(phrase), re.I)
        while pat.search(out):
            out = pat.sub(trigger if not placed else "", out, count=1)
            placed = True

    out = tidy(out)
    if not placed:
        # The curation yaml promised this frame carries the canon wording. If it
        # does not, the caption would silently train the trigger on nothing.
        return None

    # Hoist the trigger to the head of the tag string.
    #
    # The in-place substitution can land the trigger INSIDE a longer tag, when
    # the deleted identity run was followed by more of the same clause: beat
    # 17's `...bald head, dusty patchwork cloak draped over his knees` becomes
    # `bnyjerry draped over his knees`. Prepending a second trigger there gave
    # a caption with the token twice, which trains it on the pose clause as
    # well as the character. So strip a LEADING trigger off any tag first and
    # keep whatever remains as its own tag -- `draped over his knees` is a
    # variable worth keeping promptable -- then put exactly one trigger at the
    # head, where booru-trained models weight it most.
    tags = []
    for t in out.split(","):
        t = t.strip()
        if not t:
            continue
        m = re.match(r"^%s\b[\s]*(.*)$" % re.escape(trigger), t, re.I)
        if m:
            t = m.group(1).strip()
            if not t:
                continue
        tags.append(t)
    return ", ".join([trigger] + tags)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject", help="jerry -- reads pipeline/lora/dataset-<subject>.yaml")
    ap.add_argument("--check", action="store_true",
                    help="verify shas and captions against the committed manifest; write nothing")
    args = ap.parse_args()

    yaml = _yaml()
    spec_path = os.path.join(LORA, "dataset-%s.yaml" % args.subject)
    if not os.path.exists(spec_path):
        sys.exit("no such curation file: %s" % spec_path)
    spec = yaml.safe_load(open(spec_path, encoding="utf-8"))

    out_dir = os.path.join(LORA, "captions", args.subject)
    man_path = os.path.join(LORA, "manifest-%s.yaml" % args.subject)

    rows, problems = [], []
    for entry in spec["include"]:
        rel = entry["path"]
        png = os.path.join(REPO, rel)
        if not os.path.exists(png):
            problems.append("MISSING: %s" % rel)
            continue
        prompt, size = sidecar_prompt(png)
        if not prompt:
            problems.append("NO SIDECAR PROMPT: %s" % rel)
            continue
        if spec["canon_wording"].split(",")[0].strip().lower() not in prompt.lower():
            problems.append("PROMPT LACKS CANON WORDING: %s" % rel)
            continue
        cap = caption_for(prompt, spec)
        if not cap:
            problems.append("PRUNE MATCHED NOTHING: %s" % rel)
            continue
        stem = "%s__%s" % (os.path.basename(os.path.dirname(rel)),
                           os.path.basename(rel)[:-4])
        rows.append({
            "image": rel,
            "caption_file": "pipeline/lora/captions/%s/%s.txt" % (args.subject, stem),
            "caption": cap,
            "sha256": sha256(png),
            "size": size or "unknown",
            "tier": entry.get("tier", "B"),
            "tracked": os.system("cd %s && git ls-files --error-unmatch %s >/dev/null 2>&1"
                                 % (REPO, rel)) == 0,
        })

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  " + p)

    if args.check:
        if not os.path.exists(man_path):
            sys.exit("no manifest to check against: %s" % man_path)
        old = yaml.safe_load(open(man_path, encoding="utf-8"))
        drift = []
        by_img = {r["image"]: r for r in rows}
        for o in old["frames"]:
            n = by_img.get(o["image"])
            if not n:
                drift.append("GONE FROM SET: %s" % o["image"])
            elif n["sha256"] != o["sha256"]:
                drift.append("SHA CHANGED: %s" % o["image"])
            elif n["caption"] != o["caption"]:
                drift.append("CAPTION CHANGED: %s" % o["image"])
        for d in drift:
            print("  " + d)
        print("CHECK: %s  frames=%d drift=%d problems=%d"
              % ("FAIL" if (drift or problems) else "PASS", len(rows), len(drift), len(problems)))
        return 1 if (drift or problems) else 0

    os.makedirs(out_dir, exist_ok=True)
    for r in rows:
        with open(os.path.join(REPO, r["caption_file"]), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(r["caption"] + "\n")

    untracked = [r["image"] for r in rows if not r["tracked"]]
    header = (
        "# GENERATED by pipeline/lora/build_dataset.py -- do not hand-edit.\n"
        "# Curation and its reasons live in pipeline/lora/dataset-%s.yaml.\n"
        "# Re-verify with:  python3 pipeline/lora/build_dataset.py %s --check\n"
        "#\n"
        "# `tracked: false` means the frame is on this Mac but NOT in git, so a\n"
        "# `git pull` on the box will not produce it. Those must be committed or\n"
        "# shipped before the training job can run.\n"
        % (args.subject, args.subject))
    doc = {
        "subject": spec["subject"],
        "character": spec["character"],
        "trigger": spec["trigger"],
        "base_model": spec["base_model"],
        "count": len(rows),
        "tier_a": sum(1 for r in rows if r["tier"] == "A"),
        "untracked": untracked,
        "frames": rows,
    }
    with open(man_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header)
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100)

    print("wrote %d captions -> %s" % (len(rows), out_dir))
    print("wrote manifest -> %s" % man_path)
    print("tier A=%d B=%d, untracked=%d"
          % (doc["tier_a"], len(rows) - doc["tier_a"], len(untracked)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
