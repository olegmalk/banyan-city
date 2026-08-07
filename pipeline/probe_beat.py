#!/usr/bin/env python3
"""Render ONE beat on a farm box from files on disk, never from a typed string.

`wan_i2v.py` takes --prompt and --negative as command-line STRINGS, and every
beat's negative carries Wan's Chinese anti-static terms (静态, 静止,
静止不动的画面). Those survive a python argv list; they do not reliably survive
being typed into a cp1252 cmd.exe over ssh, and a mangled negative is INVISIBLE
in the result — the clip renders, just without the terms whose effect was the
whole point of the run. So the two strings are read as utf-8 from files, whose
sha256 the operator can compare on both machines before firing.

Two other things this fixes, both of which have already cost us a record:

  --stage simple WRITES NO SIDECAR. Beat 11's f15 take had to be recovered from
  a commit whose blobs are gone from the branch tip to find out what seed made
  it, and beat 15's sidecar on 2026-08-06 was typed by hand off a log. A render
  that does not say what it was is a render we cannot compare against. This
  writes the §7.2 sidecar itself, from the values it actually passed.

  EVERY RECIPE FIELD IS EXPLICIT in build_cmd(). The bug this guards against is
  on record: --guidance was missing from one of wan_i2v's three call paths, so a
  cfg 3.0 test produced a file byte-identical to the cfg 5.0 baseline and "guidance
  did nothing" was nearly written down as a finding (video_task.py, 2026-08-03).

It does not import video_task, deliberately: that module imports yaml at module
scope for motion.yaml, and the video venv on a render box has torch and diffusers
in it, not pyyaml. This runs under the same interpreter as the render.

One beat, one process, one rc line. Nothing is pulled off the box until the rc
line prints — that is the contract, and it is why the last line is unconditional.
"""

import argparse
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

# THE SAME ENVIRONMENT video_task._run GIVES EVERY RENDER. A probe that skips it
# is not running the production recipe, whatever its flags say.
#
#   PYTHONIOENCODING / PYTHONUTF8  a single non-ASCII character in a success
#       message killed a 25-minute encode on a cp1252 console (2026-07-30), and
#       this path prints the Chinese negative back on purpose.
#   PYTORCH_CUDA_ALLOC_CONF        PyTorch's own advice from the OOM that killed
#       AnimeGen: 917 MiB reserved-but-unallocated while asking for 1.29 GiB.
#   HF_HUB_DISABLE_XET             the chunked transfer restarts a dropped
#       download from zero; the classic path resumes.
RENDER_ENV = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
              "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
              "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60"}


def build_cmd(python, wan, init, out, prompt, negative, seed, embeds,
              size="704x1280", steps=14, guidance=5.0, seconds=2.5,
              model="ti2v-5b", offload=True) -> list:
    """The full wan_i2v argv for one beat. PURE — unit-tested.

    --no-shake-neg is ALWAYS passed, for the same reason video_task passes it on
    every path: the per-beat shake decision is already made upstream and travels
    inside the negative string, and wan_i2v's own global copy would re-add the
    terms to a beat that was deliberately denied them.
    """
    cmd = [str(python), str(wan), "--stage", "simple",
           "--embeds", str(embeds),
           "--init", str(init), "--out", str(out),
           "--prompt", prompt, "--negative", negative,
           "--model", str(model), "--quantise", "none",
           "--size", str(size), "--steps", str(int(steps)),
           "--guidance", str(float(guidance)), "--seconds", str(float(seconds)),
           "--seed", str(int(seed))]
    if offload:
        cmd.append("--offload")
    return cmd + ["--no-shake-neg"]


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sidecar_text(model, licence, worker, beat, size, seconds, steps, guidance,
                 seed, task, init, init_sha, wall_s, prompt, negative,
                 offload=True) -> str:
    """The §7.2 provenance block for one probe clip. PURE — unit-tested.

    Same fields and same order as the sidecars video_task.write_sidecar leaves,
    plus the three a hand-written one keeps forgetting: which still conditioned
    it, that still's sha256, and how long it took.
    """
    def block(key, value):
        body = "\n".join("  " + ln for ln in str(value).splitlines())
        return f"{key}: |-\n{body}\n"

    return ("# Shot provenance (7.2) — written by probe_beat at render time\n"
            f"platform: local-gpu ({worker})\n"
            f"model: {model}\n"
            f"model_licence: {licence}\n"
            f"shot_beat: {beat}\n"
            f"size: {size}\n"
            f"seconds: {seconds}\n"
            f"steps: {steps}\n"
            f"guidance: {guidance}\n"
            f"offload: {'model_cpu_offload' if offload else 'none'}\n"
            f"quantise: none\n"
            f"seed: {seed}\n"
            f"task: {task}\n"
            f"init_still: {Path(init).name}\n"
            f"init_still_sha256: {init_sha}\n"
            f"wall_seconds: {wall_s}\n"
            "cost_usd: 0\n"
            + block("prompt", prompt)
            + block("negative", negative))


# Keyed on --model, so the sidecar names the artifact rather than guessing it.
# Same table as video_task.MODEL_LICENCE for the models a probe can reach; an
# unknown model gets UNVERIFIED, because a wrong allow is the direction that
# publishes things.
LICENCES = {"ti2v-5b": ("Wan-AI/Wan2.2-TI2V-5B-Diffusers", "Apache-2.0")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--python", required=True, help="the video venv's interpreter")
    ap.add_argument("--wan", required=True, help="path to wan_i2v.py")
    ap.add_argument("--init", required=True, help="the conditioning still")
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--negative-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--beat", type=int, required=True)
    ap.add_argument("--task", default="probe")
    ap.add_argument("--worker", default="unknown")
    ap.add_argument("--embeds", default="", help="scratch path; unused by --stage simple")
    ap.add_argument("--size", default="704x1280")
    ap.add_argument("--steps", type=int, default=14)
    ap.add_argument("--guidance", type=float, default=5.0)
    ap.add_argument("--seconds", type=float, default=2.5)
    ap.add_argument("--model", default="ti2v-5b")
    ap.add_argument("--no-offload", action="store_true")
    a = ap.parse_args()

    # this process prints the negative back, CJK and all, into a redirected
    # stdout whose default encoding on Windows is cp1252 — reconfigure before
    # the first print rather than trusting the caller to have set PYTHONUTF8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip()
    negative = Path(a.negative_file).read_text(encoding="utf-8").strip()
    init_sha = sha256(a.init)
    embeds = a.embeds or str(Path(a.out).with_suffix(".unused.pt"))
    cmd = build_cmd(a.python, a.wan, a.init, a.out, prompt, negative, a.seed,
                    embeds, size=a.size, steps=a.steps, guidance=a.guidance,
                    seconds=a.seconds, model=a.model, offload=not a.no_offload)

    # Say what is about to run, INCLUDING the two strings — read back from the
    # files, so the log proves what reached the model rather than what we meant
    # to send. Byte counts as well as text: mojibake and truncation both show up
    # as a length that does not match the Mac's.
    print(f"PROBE_INIT {a.init} sha256={init_sha}", flush=True)
    print(f"PROBE_PROMPT {len(prompt)} chars: {prompt}", flush=True)
    print(f"PROBE_NEGATIVE {len(negative)} chars: {negative}", flush=True)
    # the two long strings are already printed in full above, so the command line
    # shows where they came from instead — DROPPING them would leave a bare
    # `--prompt` with no value, i.e. a logged command that could not have run
    shown = [f"<{Path(a.prompt_file).name}>" if c == prompt else
             f"<{Path(a.negative_file).name}>" if c == negative else c for c in cmd]
    print("PROBE_CMD " + " ".join(shown), flush=True)

    t0 = time.time()
    rc = subprocess.run(cmd, env={**os.environ, **RENDER_ENV}).returncode
    wall = int(time.time() - t0)
    out = Path(a.out)
    size_b = out.stat().st_size if out.exists() else 0

    if rc == 0 and size_b > 10_000:
        model, licence = LICENCES.get(a.model, (a.model, "UNVERIFIED — licence not read"))
        Path(str(out) + ".meta.yaml").write_text(
            sidecar_text(model, licence, a.worker, a.beat, a.size, a.seconds,
                         f"{a.steps} (UniPC flow_shift=5.0)", a.guidance, a.seed,
                         a.task, a.init, init_sha, wall, prompt, negative,
                         offload=not a.no_offload),
            encoding="utf-8")
        print(f"PROBE_SIDECAR {out.name}.meta.yaml", flush=True)

    # THE RC LINE. Unconditional, last, and machine-readable: the operator pulls
    # nothing off this box until it appears, so it must survive every path out of
    # here including a render that produced no file.
    print(f"PROBE_RC rc={rc} out={a.out} bytes={size_b} wall_s={wall}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
