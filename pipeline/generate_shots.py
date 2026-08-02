#!/usr/bin/env python3
"""Shot generator — programmatic footage for a node's shot list, PRD §7.4.

Reads a node's `shots.md` (one generation prompt per beat), calls a video-gen
provider for every beat that doesn't have a clip yet, polls to completion,
downloads the result, and writes `NN-slug.mp4` + `NN-slug.meta.yaml` into a
clips dir — exactly the layout `render_t3.py --clips` assembles. This replaces
pasting prompts into platform websites: the manual path was for the free-tier
bake-off (see pipeline/t3-trials/); production renders are API-driven.

Providers (adapter per vendor; pick with --provider):
  kling   official agent CLI (`@klingai/cli-global`) — already OAuth'd on this
          machine; draws on paid agent credits (kling.ai membership-agent).
  veo     Google Gemini API (Veo) — needs GEMINI_API_KEY.
  fal     fal.ai aggregator (Kling/Seedance/Hailuo/…) — needs FAL_KEY;
          model chosen with --model.
  wan     Alibaba Cloud Model Studio / DashScope intl (wan2.7-t2v) — needs
          DASHSCOPE_API_KEY (Singapore workspace). Native 9:16, 2-15s,
          watermark off by default. New-account free quota may cover runs
          (pipeline/t3-trials/free-routes.md); pass --quota-covered (with
          --yes, founder attesting) to record such runs at $0 in the ledger
          while printing the list-price estimate.

Every clip's meta.yaml records platform, model, verbatim prompt, cost estimate,
and date (§7.2 — publish everything). Costs are estimates until the vendor bill
lands; the ledger reconciles.

Usage:
    python3 pipeline/generate_shots.py sapling 001 --provider kling --clips-dir /tmp/ep001
    python3 pipeline/generate_shots.py sapling 001 --provider veo --beats 03,05
    python3 pipeline/generate_shots.py sapling 001 --provider fal --model kling-video/v2.5-turbo/pro
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DURATION = 10  # seconds per shot; beats are fitted by render_t3 anyway

# ------------------------------------------------------------ spend control --
# Conservative $/second estimates (verified 2026-07-18 against official pages;
# unknown models estimate at the highest known rate rather than optimistically).
PRICE_PER_SEC = [
    ("veo3.1/fast", 0.15), ("veo3.1", 0.40),
    ("veo-3.1-fast", 0.10), ("veo-3.1-lite", 0.05), ("veo-3.1", 0.40),
    ("kling-video/v3/turbo", 0.112), ("kling-video/v3", 0.126),
    ("kling-video-v3", 0.112), ("kling-video-v2_5", 0.084),
    ("hailuo-2.3", 0.056), ("seedance-2.0", 0.3034),
    ("wan2.7", 0.10), ("wan2.6", 0.15), ("wan", 0.05),
]
FALLBACK_PRICE = 0.40  # unknown model → assume the most expensive known rate
SPEND_LEDGER = REPO / "ledger" / "render-spend.csv"


def price_per_sec(model: str) -> float:
    m = (model or "").lower()
    for frag, p in PRICE_PER_SEC:
        if frag in m:
            return p
    return FALLBACK_PRICE


def budget() -> dict:
    return yaml.safe_load((REPO / "pipeline" / "budget.yaml").read_text())


def spent_total() -> float:
    if not SPEND_LEDGER.exists():
        return 0.0
    rows = SPEND_LEDGER.read_text().strip().splitlines()[1:]
    return round(sum(float(r.split(",")[5]) for r in rows if r.strip()), 2)


def log_spend(node: str, beat: int, provider: str, model: str, est: float, note: str = "") -> None:
    if not SPEND_LEDGER.exists():
        SPEND_LEDGER.write_text("date,node,beat,provider,model,est_usd,note\n")
    with open(SPEND_LEDGER, "a") as f:
        f.write(f"{date.today().isoformat()},{node},{beat:02d},{provider},{model},{est:.2f},{note}\n")


# ---------------------------------------------------------------- shot list --

def parse_shots(shots_md: str) -> list:
    """`## Beat NN — TITLE ... ```prompt``` ` → [{num, slug, prompt, done}]

    Each prompt fence is bound to ITS beat's section (never read past the next
    `## Beat` heading — a missing fence must not swallow the next beat's prompt
    and send the wrong prompt to a paid API). Openers with an info string
    (```text) are accepted. A beat without a fence is skipped with a loud
    warning rather than silently."""
    shots = []
    heads = list(re.finditer(r"^## Beat (\d+) — ([^\n]*?)(✅[^\n]*|⬜[^\n]*)?$", shots_md, re.M))
    for i, h in enumerate(heads):
        num, title, status = int(h.group(1)), h.group(2).strip(), (h.group(3) or "")
        body_end = heads[i + 1].start() if i + 1 < len(heads) else len(shots_md)
        fence = re.search(r"^```[^\n]*\n(.*?)^```\s*$",
                          shots_md[h.end():body_end], re.M | re.S)
        if not fence:
            print(f"WARNING: shots.md beat {num:02d} ({title}) has no ``` prompt fence "
                  f"— beat SKIPPED, write the prompt before generating", file=sys.stderr)
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", title.split("(")[0].lower()).strip("-")
        shots.append({"num": num, "slug": slug or f"beat{num}",
                      "prompt": " ".join(fence.group(1).split()),
                      "done": "✅" in status})
    return shots


# ---------------------------------------------------------------- providers --

def gen_kling(prompt: str, model: str, dur: int) -> tuple:
    """Official agent CLI (OAuth'd; paid agent credits). Returns (url, meta)."""
    model = model or "kling-video-v2_5"
    r = subprocess.run(
        ["kling", "text_to_video", "--model", model, "--duration", str(dur),
         "--aspect_ratio", "9:16", "--resolution", "720p", "--enable_audio", "false",
         "--poll", "600", prompt],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=700)
    out = r.stdout + r.stderr
    if "Insufficient credits" in out:
        raise SystemExit("kling: agent credit balance is empty — top up at "
                         "https://kling.ai/h5-app/membership-agent (founder action)")
    urls = re.findall(r"https?://[^\s\"']+\.mp4[^\s\"']*", out)
    if not urls:
        raise RuntimeError(f"kling: no video URL in output:\n{out[-800:]}")
    return urls[-1], {"platform": "kling", "model": model, "cost_note": "agent credits; see kling.ai billing"}


def gen_veo(prompt: str, model: str, dur: int) -> tuple:
    """Google Gemini API — Veo long-running generation. Needs GEMINI_API_KEY.
    Veo natively supports 4/6/8s only (verified 2026-07: ai.google.dev/gemini-api/docs/veo);
    render_t3 clone-pads short clips to the beat length, so 8s is the right ask."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("veo: set GEMINI_API_KEY (aistudio.google.com/apikey)")
    dur = max(4, min(8, dur if dur in (4, 6, 8) else 8))
    model = model or "veo-3.1-fast-generate-preview"  # $0.10/s 720p — the value tier
    base = "https://generativelanguage.googleapis.com/v1beta"
    req = urllib.request.Request(
        f"{base}/models/{model}:predictLongRunning",
        data=json.dumps({
            "instances": [{"prompt": prompt}],
            "parameters": {"aspectRatio": "9:16", "durationSeconds": dur},
        }).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        op = json.load(r)["name"]
    for _ in range(120):  # poll up to ~10 min
        time.sleep(5)
        pr = urllib.request.Request(f"{base}/{op}", headers={"x-goog-api-key": key})
        with urllib.request.urlopen(pr) as r:
            st = json.load(r)
        if st.get("done"):
            if "error" in st:
                raise RuntimeError(f"veo: {st['error']}")
            resp = st.get("response", {}).get("generateVideoResponse", {})
            vids = resp.get("generatedSamples") or []
            if not vids:
                raise RuntimeError(
                    "veo: generation finished but returned no video — prompt likely "
                    "blocked by Google's RAI safety filter; rewrite the prompt "
                    f"(response: {json.dumps(resp)[:300]})")
            return vids[0]["video"]["uri"] + f"&key={key}", {
                "platform": "google-veo-api", "model": model,
                "cost_note": "per-second API billing; see ai.google.dev/pricing"}
    raise RuntimeError("veo: generation timed out")


def gen_fal(prompt: str, model: str, dur: int, image: Path | None = None) -> tuple:
    """fal.ai aggregator queue API. Needs FAL_KEY; --model picks the hosted model.

    With `image` (a founder-approved still), the call is IMAGE-to-video: the
    approved pixels are the shot, the API only moves them — same contract as
    the free engines, so a paid take competes on the board like any other.
    The still travels as a data URI (fal accepts them; no third-party hosting
    of unpublished frames).
    """
    key = os.environ.get("FAL_KEY")
    if not key:
        raise SystemExit("fal: set FAL_KEY (fal.ai/dashboard/keys)")
    # verified fal endpoints + $/10s 720p 9:16 (2026-07-18, fal model pages):
    #   fal-ai/kling-video/v3/turbo/standard/text-to-video   $1.12 (native audio)
    #   fal-ai/minimax/hailuo-2.3/standard/text-to-video     $0.56
    #   bytedance/seedance-2.0/text-to-video                 $3.03 (w/audio)
    #   fal-ai/veo3.1/fast                                   $1.20 per 8s (no visible watermark)
    model = model or "fal-ai/kling-video/v3/turbo/standard/text-to-video"
    if "/" not in model.split("/")[0] and not model.startswith(("fal-ai/", "bytedance/")):
        model = f"fal-ai/{model}"
    # payload shapes verified against fal endpoint schemas 2026-07-18:
    #   kling v3:  duration "3".."15" (string), aspect_ratio, generate_audio
    #   veo3.1:    duration "4s"/"6s"/"8s", resolution, generate_audio
    # generate_audio=false everywhere — the T3 post pipeline owns sound.
    payload = {"prompt": prompt, "aspect_ratio": "9:16", "generate_audio": False}
    if image is not None:
        import base64
        b64 = base64.b64encode(image.read_bytes()).decode()
        payload["image_url"] = f"data:image/png;base64,{b64}"
        if "text-to-video" in model:
            model = model.replace("text-to-video", "image-to-video")
    if "veo" in model:
        payload["duration"] = f"{dur if dur in (4, 6, 8) else 8}s"
        payload["resolution"] = "720p"
    else:
        payload["duration"] = str(dur)
    req = urllib.request.Request(
        f"https://queue.fal.run/{model}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        sub = json.load(r)
    status_url, resp_url = sub["status_url"], sub["response_url"]
    for _ in range(120):
        time.sleep(5)
        sr = urllib.request.Request(status_url, headers={"Authorization": f"Key {key}"})
        with urllib.request.urlopen(sr) as r:
            st = json.load(r)
        if st["status"] == "COMPLETED":
            rr = urllib.request.Request(resp_url, headers={"Authorization": f"Key {key}"})
            with urllib.request.urlopen(rr) as r:
                res = json.load(r)
            url = (res.get("video") or {}).get("url") or res["videos"][0]["url"]
            return url, {"platform": "fal.ai", "model": model,
                         "cost_note": "per-run billing; see fal.ai model page"}
        if st["status"] in ("FAILED", "ERROR"):
            raise RuntimeError(f"fal: {st}")
    raise RuntimeError("fal: generation timed out")


def gen_wan(prompt: str, model: str, dur: int, image: Path | None = None) -> tuple:
    """Alibaba Cloud Model Studio (DashScope intl) — wan2.x text-to-video.
    Needs DASHSCOPE_API_KEY (Singapore-region workspace; the new-account free
    quota covers video — see pipeline/t3-trials/free-routes.md).

    Schema verified 2026-07-19 against the official API reference
    (alibabacloud.com/help/en/model-studio/text-to-video-api-reference):
    async create (X-DashScope-Async: enable) + 15s task polling; duration
    2-15s integer; ratio 9:16 native; watermark defaults false — left off.
    720P chosen over the 1080P default to stretch quota. Result URLs expire
    in 24h — downloaded immediately by the caller. Workspace-scoped hosts
    (https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com) go via the
    DASHSCOPE_BASE_URL env override."""
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        raise SystemExit("wan: set DASHSCOPE_API_KEY (Model Studio console, Singapore region)")
    base = os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com").rstrip("/")
    model = model or "wan2.7-t2v"
    img_url = None
    if image is not None:
        # DashScope i2v takes a URL; approved stills are PUBLIC on the site by
        # design (the board), so the canonical copy is its own hosting. Verify it
        # serves before spending.
        rel = image.resolve().relative_to((REPO / "genomes").resolve())
        genome, _, node_name = rel.parts[0], rel.parts[1], rel.parts[2]
        img_url = f"https://banyan.city/{genome}/{node_name}-media/{image.name}"
        chk = urllib.request.Request(img_url, method="HEAD")
        with urllib.request.urlopen(chk) as r:
            assert r.status == 200
        if "-t2v" in model:
            model = model.replace("-t2v", "-i2v")
    req = urllib.request.Request(
        f"{base}/api/v1/services/aigc/video-generation/video-synthesis",
        data=json.dumps({
            "model": model,
            # wan2.7 renamed the i2v image field: "Field required: input.media"
            # (verified the hard way, 2026-07-28, $0 billed on the failed task)
            # wan2.7 i2v schema (Model Studio image-to-video API reference, verified
            # 2026-07-28): media = list of {type, url}; the still is the first frame.
            "input": ({"prompt": prompt,
                       "media": [{"type": "first_frame", "url": img_url}]}
                      if img_url else {"prompt": prompt}),
            "parameters": {"resolution": "720P", "ratio": "9:16",
                           "duration": max(2, min(15, dur)),
                           "prompt_extend": True, "watermark": False},
        }).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "X-DashScope-Async": "enable"})
    with urllib.request.urlopen(req) as r:
        task_id = json.load(r)["output"]["task_id"]
    for _ in range(60):  # docs: 1-5 min typical; poll 15s up to 15 min
        time.sleep(15)
        pr = urllib.request.Request(f"{base}/api/v1/tasks/{task_id}",
                                    headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(pr) as r:
            st = json.load(r)["output"]
        if st["task_status"] == "SUCCEEDED":
            return st["video_url"], {
                "platform": "alibaba-model-studio", "model": model,
                "cost_note": "free new-account quota while it lasts, then ~$0.10/s; see console billing"}
        if st["task_status"] in ("FAILED", "CANCELED", "UNKNOWN"):
            raise RuntimeError(f"wan: task {st['task_status']}: {st}")
    raise RuntimeError("wan: generation timed out")


PROVIDERS = {"kling": gen_kling, "veo": gen_veo, "fal": gen_fal, "wan": gen_wan}


def effective_duration(provider: str, model: str, dur: int) -> int:
    """Seconds the provider will actually generate and bill — mirrors the
    clamps inside each adapter (veo and fal-hosted veo: 4/6/8s only, else 8s;
    wan: 2-15s) so the budget gate estimates the real API cost, not the raw
    --duration ask."""
    if provider == "veo" or (provider == "fal" and "veo" in (model or "").lower()):
        return dur if dur in (4, 6, 8) else 8
    if provider == "wan":
        return max(2, min(15, dur))
    return dur


# --------------------------------------------------------------------- main --

def download(url: str, dest: Path) -> None:
    """Fetch to a .part temp then rename — a crash mid-download must never
    leave a truncated NN-*.mp4 that the resume check counts as a finished clip."""
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
            f.write(r.read())
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("genome")
    p.add_argument("node")
    p.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    p.add_argument("--model", default=None, help="provider-specific model override")
    p.add_argument("--beats", default=None, help="comma list, e.g. 03,05 (default: all beats without a clip)")
    p.add_argument("--clips-dir", type=Path, default=None,
                   help="where clips land (default: <node>/clips/)")
    p.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    p.add_argument("--from-stills", action="store_true",
                   help="image-to-video from the node's founder-APPROVED stills "
                        "(nodes/<node>/stills/NN-slug.png); refuses beats with no "
                        "approved still — approval binds pixels (fal provider only)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true",
                   help="REQUIRED to spend: confirms the printed estimate. No flag, no API call.")
    p.add_argument("--quota-covered", action="store_true",
                   help="wan only: founder attests this run is covered by the provider free quota: "
                        "ledger records $0.00 (with the list-price noted) and the money caps "
                        "don't count it. Still requires --yes. Do NOT pass once quota is exhausted.")
    args = p.parse_args()

    # STEWARDSHIP §6: narrative approval precedes media. This tool was one of the
    # three that made 8.7 GPU-hours of media from unread scripts on 2026-07-25 and
    # still had no gate on 2026-07-27 (principles audit, finding #1). One gate, one
    # implementation: render_local.approved().
    from render_local import approved as _approved
    _ok, _detail = _approved(args.genome, args.node)
    if not _ok:
        raise SystemExit(f"{args.node} is NOT approved — {_detail}\n"
                         "STEWARDSHIP.md §6: no PAID footage from an unread script.")

    if args.quota_covered and args.provider != "wan":
        p.error("--quota-covered applies only to --provider wan — the sole provider "
                "with a free quota (pipeline/t3-trials/free-routes.md)")

    genome_dir = REPO / "genomes" / args.genome
    lineage = yaml.safe_load((genome_dir / "lineage.yaml").read_text())
    node = next(n for n in lineage["nodes"] if n["id"] == args.node)
    node_dir = genome_dir / "nodes" / node["slug"]
    shots_file = node_dir / "shots.md"
    if not shots_file.exists():
        raise SystemExit(f"{node['id']}: no shots.md — write the per-beat prompt list first")

    clips_dir = args.clips_dir or (node_dir / "clips")
    clips_dir.mkdir(parents=True, exist_ok=True)
    shots = parse_shots(shots_file.read_text())
    wanted = ({int(b) for b in args.beats.split(",")} if args.beats else None)

    todo = []
    for s in shots:
        if wanted is not None and s["num"] not in wanted:
            continue
        existing = [c for c in clips_dir.glob(f"{s['num']:02d}-*.mp4") if c.stat().st_size > 0]
        if existing and wanted is None:
            continue  # already have footage (0-byte stubs don't count); explicit --beats regenerates
        todo.append(s)
    if not todo:
        print("nothing to generate — every requested beat already has a clip")
        return 0

    # ---- budget gate: estimate → print → require --yes → enforce caps ------
    rate = price_per_sec(args.model or {"kling": "kling-video-v2_5", "veo": "veo-3.1-fast",
                                        "fal": "kling-video/v3/turbo", "wan": "wan2.7-t2v"}[args.provider])
    eff_dur = effective_duration(args.provider, args.model, args.duration)
    est_run = round(len(todo) * eff_dur * rate, 2)
    caps, prior = budget(), spent_total()
    quota_note = " · QUOTA-COVERED (founder-attested: bills $0, list-price shown)" if args.quota_covered else ""
    print(f"{node['id']}: {len(todo)} shot(s) via {args.provider}"
          + (f" [{args.model}]" if args.model else "")
          + f" — estimated cost ${est_run:.2f} (${rate:.3f}/s x {eff_dur}s effective x {len(todo)})"
          f" · spent so far ${prior:.2f} · caps: ${caps['hard_cap_per_run_usd']:.2f}/run,"
          f" ${caps['hard_cap_total_usd']:.2f} lifetime{quota_note}")
    if args.dry_run:
        for s in todo:
            print(f"  would generate beat {s['num']:02d} ({s['slug']}): {s['prompt'][:70]}…")
        return 0
    est_for_caps = 0.0 if args.quota_covered else est_run
    if est_for_caps > caps["hard_cap_per_run_usd"]:
        raise SystemExit(f"REFUSED: run estimate ${est_run:.2f} exceeds per-run cap "
                         f"${caps['hard_cap_per_run_usd']:.2f} (pipeline/budget.yaml)")
    if prior + est_for_caps > caps["hard_cap_total_usd"]:
        raise SystemExit(f"REFUSED: ${prior:.2f} spent + ${est_run:.2f} would exceed lifetime cap "
                         f"${caps['hard_cap_total_usd']:.2f} (pipeline/budget.yaml)")
    if not args.yes:
        raise SystemExit("REFUSED: spending requires the explicit --yes flag "
                         "(this run would cost ~$%.2f%s). No flag, no spend."
                         % (est_run, " list-price; quota-covered" if args.quota_covered else ""))

    gen = PROVIDERS[args.provider]
    for s in todo:
        print(f"  beat {s['num']:02d} ({s['slug']}) … ", end="", flush=True)
        _img = None
        if args.from_stills:
            _img = node_dir / "stills" / f"{s['num']:02d}-{s['slug']}.png"
            if not _img.exists():
                raise SystemExit(f"beat {s['num']:02d}: no APPROVED still — the paid "
                                 "rail only animates founder-approved pixels.")
        try:
            url, meta = (gen(s["prompt"], args.model, args.duration, image=_img)
                         if args.from_stills else
                         gen(s["prompt"], args.model, args.duration))
        except RuntimeError as e:
            raise SystemExit(f"\nbeat {s['num']:02d} ({s['slug']}): {e}") from e
        beat_est = round(eff_dur * rate, 2)
        if args.quota_covered:
            log_spend(node["id"], s["num"], args.provider, meta.get("model", args.model or ""),
                      0.0, f"provider free quota (list-price ${beat_est:.2f})")
        else:
            log_spend(node["id"], s["num"], args.provider, meta.get("model", args.model or ""), beat_est)
        dest = clips_dir / f"{s['num']:02d}-{s['slug']}.mp4"
        download(url, dest)
        dest.with_suffix(".meta.yaml").write_text(
            "# Shot provenance (§7.2)\n" + yaml.safe_dump({
                **meta, "shot_beat": s["num"], "prompt": s["prompt"],
                "duration_s": args.duration, "aspect": "9:16",
                "date": date.today().isoformat(),
            }, sort_keys=False, allow_unicode=True))
        print(f"✓ {dest.name} ({dest.stat().st_size // 1024}KB)")

    print(f"\nnext: python3 pipeline/render_t3.py {args.genome} {args.node} "
          f"--clips {clips_dir} --out /tmp/{args.node}-episode.mp4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
