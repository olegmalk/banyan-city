#!/usr/bin/env python3
r"""Check, on a Mac farm worker, that its model weights are actually intact.

This exists because of 2026-08-15/16. macbook1 (the fastest machine in the
fleet, an M1 Max) and macbook3 rendered SDXL as PURE NOISE, deterministically
and silently, for days. Both produced a byte-identical noise PNG. The cause
was not MPS, not the torch version and not RAM -- all five Macs run the same
torch build (git cf30153c) and all five have 32 GiB. The cause was the UNet:

    blobs/c1e43f5fa892e1c54c99fc7caebf9c3426910ea5a730861ff89dead23b9f260e
    macbook1: sha256 813587173c50...  87.7% of the file is all-zero
    macbook3: sha256 28a83ca78be0...  92.6% of the file is all-zero
    macbook2: sha256 c1e43f5fa892...  intact
    (the weights were rsync'd machine-to-machine, farm-six-macs.md step 7)

**Every proxy passed.** The file's `stat` size was byte-exact, the file count
was right, the manifest compared equal -- a lane checked exactly that and
concluded "weights verified byte-identical, 33 files, 25 symlinks, 6940 MB".
The bytes were wrong anyway, because a file can carry its full length and
still be mostly holes. Only reading the content can see that, so that is what
this does and the only thing it trusts.

The check is cheap and needs no network: huggingface_hub names an LFS blob
after the sha256 of its own content, so the expected digest is the filename.
    https://github.com/huggingface/hub-docs/blob/main/docs/hub/local-cache.md
    "Git LFS files: named by their SHA-256 hash (64 hexadecimal characters)."

Nor does a clean `rsync` exit prove anything: rsync's post-transfer whole-file
check is an MD4 accumulated over the bytes as they stream past, never a re-read
of what landed on disk (rsync(1), --checksum). A write that is dropped after
the digest saw it is invisible to it.

    python3 pipeline/mac_preflight.py                  # audit the HF cache
    python3 pipeline/mac_preflight.py --canary         # + a real 8-step render

Exits 0 and prints `verdict: READY`, or nonzero with `verdict: BLOCKED` and
the reason. Import `weights_ok()` to refuse work before spending GPU time.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import platform
import socket
import subprocess
import sys

CHUNK = 8 << 20
MIB = 1 << 20
# Below this, a blob is a config/tokenizer file: cheap to be wrong about and
# not what silently zeroes a render. The weights are the ones worth reading.
MIN_AUDIT_BYTES = 1 << 20

# A final-step SDXL latent sits near unit scale once the sampler has done its
# job -- measured 1.02 on a healthy machine. A UNet whose weights are zeroed
# predicts ~no noise, so the latent never contracts from its initial sigma
# (SDXL's init_noise_sigma is ~14.6) and measured 17.03 on both broken ones.
# Anything above this is not a bad picture, it is not a picture.
LATENT_STD_CEILING = 5.0


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_content_addressed(name: str) -> bool:
    """True for a blob whose filename IS its sha256 -- 64 lowercase hex.

    A 40-hex name is a git SHA-1 blob hash (`sha1("blob <len>\\0" + content)`),
    which is NOT a plain digest of the content and must not be compared with
    one. Skipping those is deliberate; flagging them would be a false alarm on
    every small git-tracked file in the cache.
    """
    return len(name) == 64 and all(c in "0123456789abcdef" for c in name)


def digest_and_zero_census(path: str, chunk: int = CHUNK) -> dict:
    """Read the whole file: its sha256, and how much of it is all-zero.

    The zero census is the diagnosis, not the verdict -- it says *how* a file
    is wrong (holes from a broken transfer) where the digest only says *that*
    it is. Counted in whole MiB regions; a trained UNet has no such region.
    """
    h = hashlib.sha256()
    zero_mib = total_mib = read = 0
    with open(path, "rb") as fh:
        carry = b""
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
            read += len(b)
            data = carry + b
            whole = len(data) // MIB
            for i in range(whole):
                total_mib += 1
                if not any(data[i * MIB:(i + 1) * MIB]):
                    zero_mib += 1
            carry = data[whole * MIB:]
        if carry:
            total_mib += 1
            if not any(carry):
                zero_mib += 1
    return {"sha256": h.hexdigest(), "bytes_read": read,
            "zero_mib": zero_mib, "total_mib": total_mib}


def classify_blob(name: str, path: str) -> dict:
    """Verdict for one blob, decided ONLY by what reading it returns."""
    st = os.stat(path)
    out = {
        "size": st.st_size,
        # Physical bytes are recorded because they are how this defect looks
        # from the outside, but they are never the verdict: APFS compression
        # makes an intact file look small and a `du` under-report already sent
        # one lane chasing a stalled download that had finished.
        "physical_bytes": st.st_blocks * 512,
    }
    out.update(digest_and_zero_census(path))
    out["expected"] = name
    ok = out["sha256"] == name
    out["state"] = "ok" if ok else "CORRUPT"
    if not ok:
        pct = 100.0 * out["zero_mib"] / max(out["total_mib"], 1)
        out["why"] = ("content sha256 %s != blob name; %.1f%% of the file is "
                      "all-zero (%d of %d MiB). Size and file count cannot see "
                      "this." % (out["sha256"][:16] + "...", pct,
                                 out["zero_mib"], out["total_mib"]))
    return out


def hub_root(explicit: str = "") -> str:
    if explicit:
        return explicit
    hf_home = os.environ.get("HF_HOME") or os.path.join(
        os.path.expanduser("~"), ".cache", "huggingface")
    return os.path.join(hf_home, "hub")


def audit_cache(root: str, min_bytes: int = MIN_AUDIT_BYTES) -> dict:
    """Every content-addressed blob in a HF cache, checked by content."""
    blobs, corrupt = {}, []
    if not os.path.isdir(root):
        return {"root": root, "present": False, "blobs": {}, "corrupt": [],
                "checked": 0}
    for dirpath, _dirs, files in os.walk(root):
        if os.path.basename(dirpath) != "blobs":
            continue
        for name in sorted(files):
            if not is_content_addressed(name):
                continue
            path = os.path.join(dirpath, name)
            if not os.path.isfile(path) or os.path.getsize(path) < min_bytes:
                continue
            info = classify_blob(name, path)
            # the repo the blob belongs to, so a report names something a human
            # can act on rather than 64 hex characters
            info["repo"] = os.path.basename(os.path.dirname(dirpath))
            blobs[name] = info
            if info["state"] != "ok":
                corrupt.append("%s: %s" % (info["repo"], info["why"]))
    return {"root": root, "present": True, "blobs": blobs, "corrupt": corrupt,
            "checked": len(blobs)}


def weights_ok(root: str = "", min_bytes: int = MIN_AUDIT_BYTES) -> tuple:
    """(ok, [reasons]) -- the one call a renderer needs before it spends time."""
    rep = audit_cache(hub_root(root), min_bytes)
    if not rep["present"]:
        return False, ["no huggingface cache at %s" % rep["root"]]
    if not rep["checked"]:
        return False, ["no model weights found under %s -- nothing to render "
                       "with" % rep["root"]]
    return (not rep["corrupt"]), list(rep["corrupt"])


def latent_is_degenerate(std: float, ceiling: float = LATENT_STD_CEILING) -> bool:
    """True when a finished latent never contracted -- i.e. the output is noise.

    Catches the whole class, not just this cause: a torch/macOS MPS
    correctness regression would present the same way and hash checks would
    pass. cf. pytorch/pytorch#141471, a diffusion model rendering "nothing but
    noise" purely from a torch minor-version bump, labelled
    `module: correctness (silent)`.
    """
    return not (std == std) or std > ceiling  # NaN is degenerate too


def sysctl(key: str) -> str:
    try:
        return subprocess.run(["sysctl", "-n", key], capture_output=True,
                              text=True, encoding="utf-8",
                              timeout=10).stdout.strip()
    except Exception:
        return "?"


def machine_report() -> dict:
    rep = {"host": socket.gethostname(), "platform": platform.platform(),
           "python": sys.version.split()[0]}
    if sys.platform == "darwin":
        rep["chip"] = sysctl("machdep.cpu.brand_string")
        try:
            rep["ram_gib"] = round(int(sysctl("hw.memsize")) / 1024 ** 3, 1)
        except ValueError:
            rep["ram_gib"] = None
        try:
            rep["macos"] = subprocess.run(
                ["sw_vers", "-productVersion"], capture_output=True, text=True, encoding="utf-8",
                timeout=10).stdout.strip()
        except Exception:
            rep["macos"] = "?"
    try:
        import torch
        rep["torch"] = torch.__version__
        rep["torch_git"] = getattr(torch.version, "git_version", "?")
        rep["mps"] = bool(getattr(torch.backends, "mps", None)
                          and torch.backends.mps.is_available())
    except Exception as exc:
        rep["torch"] = "MISSING: %s" % exc
        rep["mps"] = False
    return rep


def run_canary(steps: int = 8, width: int = 832, height: int = 1216,
               model: str = "cagliostrolab--animagine-xl-3.1") -> dict:
    """One short real render; report the final latent's scale.

    ONE SAMPLE BEFORE ANY BATCH, one level down: this is the smallest render
    that can tell a working machine from one that will hand back noise for
    every seed of every beat.
    """
    out = {"steps": steps, "size": "%dx%d" % (width, height)}
    try:
        import torch
        from diffusers import StableDiffusionXLPipeline
    except Exception as exc:
        out["state"] = "SKIPPED"
        out["why"] = "no torch/diffusers here (%s)" % exc
        return out
    repo = model.replace("--", "/", 1) if "--" in model else model
    dev = "mps" if (getattr(torch.backends, "mps", None)
                    and torch.backends.mps.is_available()) else "cpu"
    pipe = StableDiffusionXLPipeline.from_pretrained(
        repo, torch_dtype=torch.float32, use_safetensors=True)
    pipe.to(dev)
    seen = {}

    def cb(_pipe, step, _t, kw):
        lat = kw["latents"].detach().to("cpu", torch.float32)
        seen["std"] = float(lat.std())
        seen["nan"] = int(torch.isnan(lat).sum())
        return kw

    g = torch.Generator(device="cpu").manual_seed(20260719)
    pipe(prompt="a goblin seated in grass, cinematic lighting, masterpiece",
         num_inference_steps=steps, guidance_scale=7.5, width=width,
         height=height, generator=g, callback_on_step_end=cb,
         callback_on_step_end_tensor_inputs=["latents"])
    std = seen.get("std", float("nan"))
    out["device"] = dev
    out["final_latent_std"] = round(std, 4)
    out["latent_nan"] = seen.get("nan", -1)
    bad = latent_is_degenerate(std)
    out["state"] = "NOISE" if bad else "ok"
    if bad:
        out["why"] = ("final latent std %.3f > %.1f -- the sampler never "
                      "contracted, so this machine renders noise" %
                      (std, LATENT_STD_CEILING))
    return out


def as_yaml(data, indent=0) -> str:
    """Minimal YAML writer -- a render venv is not a data venv."""
    pad = "  " * indent
    if isinstance(data, dict):
        if not data:
            return pad + "{}\n"
        out = ""
        for k, v in data.items():
            if isinstance(v, (dict, list)) and v:
                out += "%s%s:\n%s" % (pad, k, as_yaml(v, indent + 1))
            else:
                out += "%s%s: %s\n" % (pad, k, scalar(v))
        return out
    if isinstance(data, list):
        if not data:
            return pad + "[]\n"
        out = ""
        for v in data:
            if isinstance(v, (dict, list)) and v:
                body = as_yaml(v, indent + 1).splitlines()
                out += "%s- %s\n" % (pad, body[0].strip())
                out += "".join(line + "\n" for line in body[1:])
            else:
                out += "%s- %s\n" % (pad, scalar(v))
        return out
    return pad + scalar(data) + "\n"


def scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or any(c in s for c in ":#'\"\n") or s.strip() != s:
        import json
        return json.dumps(s)
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Mac farm worker preflight: are this machine's weights real?")
    ap.add_argument("--hub", default="", help="HF hub dir (default: $HF_HOME/hub)")
    ap.add_argument("--canary", action="store_true",
                    help="also run one short render and check it is not noise")
    ap.add_argument("--canary-steps", type=int, default=8)
    ap.add_argument("--out", default="", help="also write the report here")
    ap.add_argument("--min-bytes", type=int, default=MIN_AUDIT_BYTES)
    a = ap.parse_args(argv)

    report = {"generated_at": utcnow()}
    report["machine"] = machine_report()
    problems = []

    cache = audit_cache(hub_root(a.hub), a.min_bytes)
    report["weights"] = {
        "root": cache["root"],
        "blobs_checked": cache["checked"],
        "blobs_corrupt": len(cache["corrupt"]),
        "detail": {k: {"repo": v["repo"], "state": v["state"],
                       "size": v["size"], "physical_bytes": v["physical_bytes"],
                       "zero_mib": v["zero_mib"], "total_mib": v["total_mib"],
                       "sha256": v["sha256"]}
                   for k, v in cache["blobs"].items()},
    }
    if not cache["present"]:
        problems.append("no huggingface cache at %s" % cache["root"])
    elif not cache["checked"]:
        problems.append("no model weights under %s -- nothing to render with"
                        % cache["root"])
    problems.extend(cache["corrupt"])

    if a.canary:
        can = run_canary(steps=a.canary_steps)
        report["canary"] = can
        if can["state"] == "NOISE":
            problems.append("canary: %s" % can["why"])

    report["problems"] = problems
    report["verdict"] = "READY" if not problems else "BLOCKED"
    text = as_yaml(report)
    sys.stdout.write(text)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
