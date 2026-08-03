#!/usr/bin/env python3
"""Motion takes on a farm machine — self-installing, heartbeat-observable.

The open render requests want TAKES, not more frames, and the founder asked
for a free video generator set up without anyone standing at the keyboard
(2026-07-30). So the video stack installs itself the way runpod_boot.sh
proved: a courier mark at every stage, so a silent or stuck machine is
visible from anywhere instead of looking like it is thinking.

Everything lands in ONE deletable folder (C:\\banyan-video on Windows,
~/banyan-video elsewhere) with its own venv — the stills worker stays pinned
to diffusers 0.29.2 for SDXL, and Wan needs a modern one.

Driven by farm_worker when a queue task carries `video: true`.
"""

import collections
import json
import os
import platform
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
IS_WIN = platform.system() == "Windows"
ROOT = Path("C:/banyan-video") if IS_WIN else Path.home() / "banyan-video"
VENV = ROOT / "venv"
PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python3")
# Blackwell (RTX 50-series) needs cu128 wheels; older builds do not know sm_120
TORCH_INDEX = "https://download.pytorch.org/whl/cu128"


# Two thresholds, because "slow" and "wedged" are different failures. A 480x832
# clip takes ~4 min and a first-run model download can precede the first clip.
STALL_MINUTES = 45          # SILENT this long = hung. Kill it.
# Printing but no finished clip this long = a real loop, or a model too slow to be
# usable. 180 lets AnimeGen's ~27B pair finish a clip (30m+ observed and still
# sampling on 2026-08-03) without letting a stuck progress bar burn a whole night.
NO_PROGRESS_MINUTES = 180

PROGRESS = re.compile(r"^\[(\d+)/(\d+)\]\s+wrote\s+(.+?)\s+in\s+(\S+)")


def _stream(cmd, courier, timeout, env):
    """Run cmd, heartbeating each finished clip instead of after all of them.

    `subprocess.run(capture_output=True)` buffers until exit, so a batch of 8
    clips sharing one model load — the whole point of batching, 44min down to
    11 — reported NOTHING for over an hour. The courier's promise is that "a
    silent machine is impossible", and for long batches it quietly was not:
    from outside, an hour of healthy sampling and a hung process look
    identical. wan_i2v already prints `[i/N] wrote <path> in <n>s` per clip;
    this just stops throwing those lines away until the end.

    Returns a CompletedProcess so callers (retry/transient logic) are unchanged.

    SECOND EFFECT, load-bearing, do not remove the mark() call thinking it is
    only logging: batch clips are written straight into `courier.out`, and
    Courier.mark() does `git add -A farm-out` + commit + push. So marking per
    clip also PUSHES each finished clip the moment it exists. Before this, a
    batch that hit its timeout lost every clip it had already rendered, because
    nothing was pushed until the task returned — three hours of finished work
    discarded by the last minute of it. Now a timeout keeps whatever finished.
    """
    out = []
    # BOUNDED. Now that stderr is drained live (see drain_err below), a tqdm bar
    # is a real line every redraw — Python's universal-newline mode turns each \r
    # into \n, verified — so a 3-hour render appends tens of thousands of near
    # identical lines. Callers only ever read the TAIL (`r.stderr[-2500:]`) and
    # scan for transient-error strings, and a failure lands at the END, so keeping
    # the last few thousand lines loses nothing and cannot grow without limit.
    err = collections.deque(maxlen=4000)
    deadline = time.time() + timeout if timeout else None
    # encoding= explicitly: errors="replace" keeps this from crashing on the
    # farm's cp1252 locale, but without it every non-ASCII byte the renderer
    # prints (the Chinese negative prompt, a progress bar's box characters)
    # lands in the log as mojibake — and the log is how we diagnose failures.
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace",
                         bufsize=1, env=env)

    # A HEARTBEAT THAT DOES NOT DEPEND ON THE CHILD SAYING ANYTHING.
    #
    # Per-clip marks made batch progress visible, but the phases that produce NO
    # stdout stayed invisible — and those are the long ones. A 30GB model download
    # writes its progress bars to stderr, so from outside, "downloading AnimeGen"
    # and "hung" looked identical for 65 minutes (2026-08-01), which is the third
    # time today we could not tell working from stuck. Elapsed time is knowable
    # without the child's cooperation, so publish that.
    alive = threading.Event()
    # STALL DETECTION, not just liveness. Overnight 2026-08-01: clip 1 of 5 landed
    # in 599s, then the batch produced nothing for EIGHT HOURS while faithfully
    # reporting "child still running" every five minutes. The watchdog proved the
    # process was breathing and said nothing about whether it was working — so a
    # hung render looked exactly like a slow one, all night, and four clips never
    # came. Liveness without progress is a comfort blanket.
    # TWO CLOCKS, because "no clip yet" and "not breathing" are different facts.
    #
    #   at    last FINISHED CLIP        -> progress
    #   said  last line of child output -> liveness
    #
    # The kill used to fire on `at` alone, i.e. "no clip in 45 minutes". That is
    # right for a hung process and WRONG for a legitimately slow one: AnimeGen
    # (27B, two A14B transformers, 25 steps without the distillation LoRAs) passed
    # 30 minutes on its first clip with the sampler running normally, and would
    # have been killed at 45 for being slow. ti2v-5b's 240s never came near it, so
    # nothing had tested the threshold before.
    #
    # Now: silence for STALL_MINUTES kills (a real hang says nothing at all),
    # while a child that is still printing is left alone until NO_PROGRESS_MINUTES
    # — long enough that a slow model finishes, short enough that an infinite
    # progress-bar loop does not run all night.
    progress = {"at": time.time(), "n": 0, "said": time.time()}

    def tick():
        n = 0
        while not alive.wait(300):          # every 5 minutes
            n += 5
            stalled = int(time.time() - progress["at"]) // 60
            silent = int(time.time() - progress["said"]) // 60
            msg = (f"VIDEO_ALIVE {n}m elapsed, {progress['n']} clip(s) done"
                   + (f", last output {silent}m ago" if silent >= 5 else ""))
            kill = silent >= STALL_MINUTES or stalled >= NO_PROGRESS_MINUTES
            if kill:
                why = (f"silent for {silent}m" if silent >= STALL_MINUTES
                       else f"no clip finished in {stalled}m despite output")
                msg = (f"VIDEO_STALLED {why} ({progress['n']} done) — "
                       f"killing it so the queue moves")
            if courier:
                try:
                    courier.mark(msg)
                except Exception:            # noqa: BLE001
                    pass                     # a heartbeat may never kill its subject
            if kill:
                try:
                    p.kill()
                except Exception:            # noqa: BLE001
                    pass
                return
    threading.Thread(target=tick, daemon=True).start()

    # DRAIN STDERR ON ITS OWN THREAD. Two reasons, and the second is worse than
    # the first.
    #
    # 1. tqdm — the sampler's progress bar, and HF's download bars — writes to
    #    STDERR. This function used to read stderr only after the stdout loop
    #    ENDED, i.e. after the child exited, so during a render the only stdout
    #    line was "[i/N] wrote ..." at the very end of each clip. A model slow
    #    enough to take longer than STALL_MINUTES for one clip therefore looked
    #    completely silent, and the liveness clock above would have killed it
    #    while its progress bar was ticking normally into an unread pipe.
    # 2. A PIPE THAT NOBODY READS FILLS AND BLOCKS THE WRITER. The OS buffer is
    #    ~64KB; a chatty sampler passes that, and then the child blocks forever on
    #    its next stderr write while we sit blocked on p.stdout waiting for output
    #    that can no longer come. That is a genuine deadlock, and from outside it
    #    is indistinguishable from a hang — which is exactly the shape of the
    #    "eight hours, no clips, still breathing" night on 2026-08-01.
    def drain_err():
        try:
            for eline in p.stderr:
                err.append(eline)
                progress["said"] = time.time()
                print(eline, end="", flush=True)
        except Exception:                    # noqa: BLE001
            pass                             # the pipe closing is not an error
    err_t = threading.Thread(target=drain_err, daemon=True)
    err_t.start()

    try:
        for line in p.stdout:
            out.append(line)
            # ECHO IT. Reading the child's stdout into a pipe means it stops
            # reaching the console, so a human watching the worker window saw
            # nothing at all for 76 minutes while a 30GB download ran — "is it
            # even running?" (founder, 2026-08-01). Capturing output for the
            # courier must not cost the person sitting in front of the machine
            # their only view of it.
            print(line, end="", flush=True)
            # ANY output is proof of life, even a progress bar we cannot parse.
            progress["said"] = time.time()
            m = PROGRESS.match(line.strip())
            if m:
                progress["at"] = time.time()
                progress["n"] = int(m.group(1))
            if m and courier:
                try:
                    courier.mark(f"VIDEO_CLIP {m.group(1)}/{m.group(2)} "
                                 f"{Path(m.group(3)).name} in {m.group(4)}")
                except Exception:            # noqa: BLE001
                    # a heartbeat must never be able to kill the render it is
                    # reporting on — the cp1252 lesson, five casualties deep
                    pass
            if deadline and time.time() > deadline:
                p.kill()
                raise subprocess.TimeoutExpired(cmd, timeout)
        # stderr is drained by drain_err() above, in real time — do NOT read it
        # here as well. Two readers on one pipe race and split lines between them.
        err_t.join(timeout=30)
        p.wait(timeout=60)
    finally:
        alive.set()
        for pipe in (p.stdout, p.stderr):
            try:
                pipe.close()
            except Exception:                # noqa: BLE001
                pass
        if p.poll() is None:
            p.kill()
    return subprocess.CompletedProcess(cmd, p.returncode, "".join(out),
                                       "".join(err))


def motion_directions(node_dir: Path) -> dict:
    """{beat: the node's OWN per-beat motion direction}, from motion.yaml.

    This file has existed since 2026-07-29 — "Per-beat MOTION direction (what
    moves; the still owns composition). Edit here — a PR to this file is a
    motion-direction pitch." The shot board reads it. make_requests reads it. The
    RENDERER never did, so every clip we have made was animated from a motion
    prompt I generated instead, and mine were worse in every way that mattered:

      motion.yaml beat 1:  "the young man types rapidly, fingers moving over the
                            keys, slight shoulder movement, monitor glow flickers
                            gently, camera locked"
      what I sent:         "One mechanical keyboard, very fast — then it stops.
                            gentle drift; no new subjects, no scene change"

    Theirs describes the STILL WE HAVE, in motion terms, and ends "camera locked"
    — the exact anti-scene-change instruction I spent today trying to invent. Beat
    4's entry is "the limp hand stays motionless... one loose paper settles to the
    floor", which is the aftermath the still actually shows, rather than the mug
    drop I asked for and got.

    Preferred over the node.md action line, which describes what HAPPENS in the
    story and can therefore describe a moment the still has already passed.
    """
    f = node_dir / "motion.yaml"
    if not f.exists():
        return {}
    try:
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    except Exception:                                    # noqa: BLE001
        return {}
    return {int(k): str(v).strip()
            for k, v in (data.get("motion_prompts") or {}).items() if v}


BEAT_HEAD = re.compile(r"^\*\*(.+?)\s+—\s+\d+:\d\d–\d+:\d\d\*\*$", re.M)


def beat_actions(node_md: Path) -> dict:
    """{beat number: the script's own line about what HAPPENS in it}.

    The two files say different things and we were only reading one. shots.md
    describes how a beat LOOKS (composition, for drawing the still). node.md
    describes what HAPPENS in it — "One mechanical keyboard, very fast", "The
    spinner resolves", "the frame tips sideways". That second one is a motion
    brief, written by the author, sitting unused.

    Instead we sent every beat the same sentence: "gentle drift; only what would
    really move here". So the model had to invent what moves, and on beat 2 —
    a man at a keyboard at 3am — it decided he pulls his hoodie up and down.
    Founder: "wan just made him pull his hoodie up and down. he didnt type at
    all." Of course: nothing ever told it he was typing.

    Nothing invented here either. The beat's own prose, minus the parts that are
    not about motion: the VO lines (they are audio), the terminal code fences
    (they are burned in as overlays by render_t3, not animated), and stage
    directions in caps like BLACK or SMASH TO BLACK.
    """
    text = node_md.read_text(encoding="utf-8")
    parts = BEAT_HEAD.split(text)[1:]
    out = {}
    for i in range(0, len(parts) - 1, 2):
        num = i // 2 + 1
        body = parts[i + 1]
        keep = []
        for line in body.split("\n"):
            s = line.strip()
            if not s or s.startswith((">", "```", "**")):
                continue           # VO line, code fence, or the next heading
            if s in ("SMASH TO BLACK.", "BLACK."):
                continue
            if re.match(r"^[A-Z][A-Z\s.✓✗$]+$", s):
                continue           # a terminal-panel line, not an action
            keep.append(s)
            if len(" ".join(keep)) > 220:
                break
        action = " ".join(keep).strip()
        action = re.sub(r"`[^`]*`", "", action)          # inline code
        # terminal-panel text leaks in when it shares a line with prose
        action = re.sub(r"[✓✗]\s*\S.*?(?=$|\.)", "", action)
        # a lighting cue, not a motion: "BLACK." tells the model to render darkness
        action = re.sub(r"\b(BLACK|SMASH TO BLACK)\b\.?", "", action)
        action = re.sub(r"\*([^*]*)\*", r"\1", action)   # emphasis markers
        action = re.sub(r"\s*,\s*(?=,)", "", action)
        action = re.sub(r"[,:]\s*(?=[,.])", "", action)
        action = re.sub(r"\s+", " ", action).strip(" ,.:")
        if action:
            out[num] = action
    return out


# Wan's official anti-stillness terms. Applied PER BEAT, never globally — see
# antistatic_for().
ANTI_STATIC = "静态, 静止, 静止不动的画面, frozen frame, still image, no motion"

# A direction that describes stillness. Beats like "the leaf holds almost perfectly
# still" or "a beat of stillness" must NOT be told to avoid being static.
# "settles" and "quivers" were in this list and are MOVEMENT words — a leaf that
# "lifts and settles" is moving. That misfiled beat 9 as wanting stillness, which is
# the exact beat the founder reported as "literally not moving, not one pixel", so
# the classifier would have made it worse. Stillness words only.
WANTS_STILL = re.compile(r"\b(still|stillness|motionless|barely|nearly still|"
                         r"very slightly|perfectly still|holds almost)\b", re.I)
# A direction that asks for real movement, where Wan's usual failure — freezing —
# is the thing to suppress.
# EXTENDED 2026-08-03 with the amplitude register the founder approved ("do this
# kinda thing"). The original list was written when directions said "drifts" and
# "stirs"; his chosen variant says "hammer", "flying", "drive hard", "jump",
# "slamming", "thrashes". None of those matched, so five rewritten beats silently
# lost their anti-static terms — the classifier did not recognise the strongest
# motion language in the file as motion at all. Caught by the tests, not by eye.
#
# Also -ING forms throughout: the old list had "pulses" but not "pulsing", "rapidly"
# but not "rapid". A vocabulary that only matches one inflection will keep doing
# this every time a direction is reworded.
WANTS_MOVE = re.compile(r"\b(whip\w*|shak\w*|sweep\w*|tip\w*|rapid\w*|fast|"
                        r"increasingly|puls\w*|arc\w*|unfurl\w*|scroll\w*|drift\w*|"
                        r"lift\w*|settl\w*|quiver\w*|strain\w*|flex\w*|trembl\w*|"
                        r"stir\w*|turning|hammer\w*|fly\w*|flies|driv\w*|jump\w*|"
                        r"scatter\w*|slam\w*|thrash\w*|strob\w*|jolt\w*|lash\w*|"
                        r"clench\w*|grip\w*|shudder\w*|snap\w*|skitter\w*|burst\w*|"
                        r"rac\w*|swing\w*|spin\w*|stream\w*|slid\w*|roll\w*|"
                        r"tumbl\w*|surge\w*|blink\w*|curl\w*)\b", re.I)


def antistatic_for(direction: str) -> str:
    """Wan's anti-stillness terms, but only for beats that should actually move.

    Founder, 2026-08-02: "no static at all forces it to move even when not needed,
    creating shaking." Exactly so, and it explains both failures at once — a blanket
    setting cannot be right for fifteen beats that disagree about motion:

      WITH the terms on every beat: beats meant to be nearly still (4 "the limp hand
      stays motionless", 8 "holds almost perfectly still") were forbidden from
      stillness, so they shook.
      WITHOUT them on any beat: beats that need real movement risk Wan's usual
      failure, a frozen output — which is what beat 9 did.

    So it is decided per beat, from the direction the author already wrote. Stillness
    language in the direction means no anti-static suppression; movement language
    means keep it.

    WHEN A DIRECTION SAYS BOTH, THE ONE THAT COMES FIRST WINS. This used to say
    "the still reading wins — an over-still clip is a usable plate, a shaking one
    is not", and that was wrong in a way the founder caught by eye on 2026-08-03:
    "wan 2.2 basically doesnt move at all, literally."

    Why it failed: the steward rewrote beat 1's direction as "his hands type fast
    over the mechanical keyboard and then stop abruptly, HANDS GOING STILL, monitor
    glow flickers gently". WANTS_STILL matched the bare word "still" — describing
    the END STATE of a motion — and suppressed the anti-static terms, so a beat
    whose whole job is typing was told nothing about needing to move. Beat 12 had
    the same shape ("strains and quivers... everything else still") and measured the
    lowest motion of all fifteen. Both were the steward's own wording defeating the
    steward's own logic.

    Position is the honest discriminator because these directions are written
    subject-first: "his hands type FAST ... going still" opens with motion and ends
    still, while "the leaf holds almost perfectly STILL, dust motes settle" opens
    with stillness and merely mentions a drift. First signal = the subject.
    """
    d = direction or ""
    ms, mv = WANTS_STILL.search(d), WANTS_MOVE.search(d)
    if ms and mv:
        return "" if ms.start() < mv.start() else ANTI_STATIC
    if ms:
        return ""
    return ANTI_STATIC if mv else ""


# Wan 2.2 is a general video model — the founder's read after screening six takes:
# "wan 2.2 is still pretty good, the problem is its not made for anime style"
# (2026-08-01). Its training is dominated by live action, so left alone it pulls
# every frame toward photography no matter how anime the still it was handed.
#
# The proper fix is an anime-trained model (AnimeGen-I2V, parked on VRAM). This is
# the cheap one available today: say the style out loud in the POSITIVE and put
# photography in the NEGATIVE. Costs nothing, and until now we had nowhere to put
# a negative at all — every "no photorealism" clause was sitting in the positive
# prompt asking for the opposite.
STYLE = ("2D anime, hand-drawn cel animation, flat cel shading, clean ink "
         "linework, anime key art")
# The founder's actual complaint, stated where it acts: Wan likes to cut to a
# second, more photographic shot partway through a clip. These terms took our
# measured scene-change drift from 40.2 to 8.8.
#
# ITS OWN CONSTANT so the hosted API path can import the identical string.
# generate_shots was sending NO negative prompt at all to Model Studio, which is
# why the one engine with nothing suppressing a cut was the one that produced a
# cut ("wan 2.7 has the second scene for like half a second at the end", founder,
# 2026-08-03). Two copies of a list is how they drift; one constant is how they
# cannot.
ANTI_SCENE = ("scene change, shot change, cut to another angle, second scene, "
              "new camera angle, different location, split screen, montage")
# Shake suppression, applied PER BEAT rather than to everything.
#
# Added blanket on 2026-08-02 to fix "these all have a pattern of like, shaking
# alot, strangly". It worked — camera translation went to 0.00px on all fifteen
# beats. But it also damped the motion we want: on 2026-08-03 an A/B on beat 1
# (same seed, same steps, typing-only direction) measured frame-to-frame movement
# of 0.19 with these terms and 0.62 without — 3.3x — and the founder's verdict on
# the pair was "B is better overall", B being without.
#
# Both of his notes are true at once, which is why this cannot be a global switch:
#   "no static at all forces it to move even when not needed, creating shaking"
#   "needs more movement, hands barely move"
# So it follows the same per-beat signal as antistatic_for, inverted: a beat asking
# for stillness gets shake suppression, a beat asking for motion does not.
SHAKE_NEG = ("camera shake, handheld camera, jitter, wobble, unstable camera, "
             "vibrating, trembling camera, rolling shutter")
# THE STYLE NEGATIVE HAD TWO MOTION SUPPRESSORS HIDING IN IT.
#
# This list exists to keep the picture from drifting photoreal. But a negative
# prompt does not know why a term is there, only that the term is unwanted:
#
#   "motion blur"  — fast hands PRODUCE motion blur. Asking for fast typing while
#                    forbidding its visual signature leaves the model one cheap way
#                    to satisfy both: do not move. Added 2026-08-01 as an
#                    anti-photoreal term, when the complaint was style, not motion.
#   "film still"   — meant as "not a live-action film frame". But the token *still*
#                    is in it, and nothing guarantees the encoder reads the two
#                    words as one concept. This is the same trap as WANTS_STILL
#                    matching "hands going still" earlier today.
#
# Both moved to ANTI_PHOTO_STRICT, applied only where they cannot cost us motion:
# beats whose direction asks for stillness. This is the third time a term added for
# picture quality turned out to act on motion (the first was Wan's own anti-static
# defaults, the second our shake suppression, whose removal was the ONE change that
# has moved the needle: 0.19 -> 0.62).
# MEASURED AND REVERTED, 2026-08-03. I moved "motion blur" and "film still" off
# motion beats on the reasoning that fast hands PRODUCE motion blur, so forbidding
# it while asking for speed leaves the model one cheap way out: do not move. Good
# reasoning, wrong answer — beat 1 measured 0.63 with them gone against 0.62 with
# them, i.e. nothing. So they are motion-NEUTRAL, and keeping them on every beat is
# free while removing them would weaken the anti-photoreal guard for no gain.
#
# What DID work is in the row below it: the shake terms (0.19 -> 0.62) and dropping
# "camera locked" plus amplitude language (0.62 -> 1.18).
ANTI_STYLE = ("photorealistic, photograph, live action, film still, 3D render, "
              "CGI, octane, realistic skin texture, depth of field bokeh, "
              "motion blur, " + ANTI_SCENE)
# Wan's negative field cap as we use it. Kept as a name so the truncation warning
# and the value cannot drift apart.
#
# RAISED 460 -> 900, with the arithmetic rather than a shrug.
#
# 460 CHARACTERS was a proxy for a TOKEN limit and never a measured one. Wan 2.2's
# text encoder is UMT5-XXL, whose usual maximum sequence is 512 TOKENS. Our longest
# negative is ~523 chars — mostly English at roughly 4 chars per token, plus a
# Chinese quality list at 1 token per character — which estimates to ~146 tokens.
# The old cap was throwing away terms at under a third of the real budget: a still
# beat lost "second scene, new camera angle, different location, split screen,
# montage", i.e. five of the eight anti-scene-change terms, on every render.
#
# Two things make raising it safe rather than hopeful:
#   - the tokenizer prints its OWN truncation warning if a prompt really is too
#     long, and stderr is drained live as of this morning, so overflow is now
#     observable instead of silent
#   - this function's own warning prints anything IT drops
# 900 leaves headroom under the estimate without pretending to know the exact
# figure. If the tokenizer ever complains, that number is the thing to lower.
NEG_MAX = 900


# SDXL prompt furniture that means nothing to a video model and eats its attention
QUALITY_SPAM = re.compile(
    r"\b(masterpiece|best quality|very aesthetic|newest|highly detailed|detailed|"
    r"cinematic lighting|9:16 vertical|no text)\b[,.\s]*", re.I)
# "No person, no figure, no cloak" — negatives written as PROSE inside what we
# hand over as the POSITIVE prompt
NEGATIVE_PROSE = re.compile(r"\bno\s+[a-z0-9][^,.]*(?:[,.]|$)", re.I)


def video_prompt(motion: str, still_prompt: str, no_anchor=False) -> tuple:
    """(positive, extra_negative) for animating an ALREADY APPROVED frame.

    We were handing the video model the STILL-GENERATION prompt — a full
    instruction for drawing the scene from scratch, complete with SDXL quality
    tags and negatives written as prose. An image-to-video model reads that as
    "draw this", not "move this", and obliges: beat 12's prompt says "a single
    thin green plant stem bent into a tense arc", so Wan drew one IN ADDITION to
    the stem already in the frame, entering from the right. The founder spotted it
    as "a stick poking the sapling" (2026-08-01). Beat 15 similarly re-lit the
    scene from "rings of warm orange light" instead of moving anything.

    So: strip the quality furniture, move the "No X" prose into the real negative
    prompt where it belongs, and put MOTION first with the scene reduced to a
    short anchor — enough for the model to know what it is looking at, not enough
    to invite a redraw.

    Nothing is invented here; the beat's own words are reused, just sorted into
    the field that acts on them.
    """
    still_prompt = still_prompt or ""
    # BOTH inputs get the treatment, not just the scene description. The motion
    # string carried "no new subjects, no scene change" straight into the POSITIVE
    # prompt — so every render was being asked for new subjects and a scene change,
    # in the same breath as being told not to. Founder on beat 1: "it makes an
    # additional realistic looking scene". It was told to.
    # This is the second time the same mistake shipped: fixed for still_prompt on
    # 2026-08-01, left in place here because the motion string looked like prose
    # rather than a prompt. Any text that reaches the model goes through this.
    motion = motion or ""
    negatives = [m.group(0).strip(" ,.")
                 for src in (motion, still_prompt)
                 for m in NEGATIVE_PROSE.finditer(src)]
    motion = re.sub(r"\s*;?\s*$", "", NEGATIVE_PROSE.sub("", motion)).strip(" ,.;")
    scene = NEGATIVE_PROSE.sub("", still_prompt)
    scene = QUALITY_SPAM.sub("", scene)
    scene = re.sub(r"\s*,\s*,+", ",", scene)
    scene = re.sub(r"\s+", " ", scene).strip(" ,.")
    # a short anchor only — the frame already carries the composition
    words = scene.split()
    anchor = " ".join(words[:22]) + ("…" if len(words) > 22 else "")
    # ANCHOR SUPPRESSION, for the motion investigation.
    #
    # Measured on beat 1: frame-to-frame motion is pinned at 0.62 whether we send
    # 61 frames or 121, and whether guidance is 5.0 or 3.0. Neither parameter moves
    # it, so the constraint is upstream of both. Counting the prompt: 15 words of
    # style, 19 of motion, then 25 describing a STATIC composition — the largest
    # block, and the LAST thing the text encoder reads. It is also redundant, since
    # the init image already IS that composition. Telling a video model in detail
    # what a still frame looks like is a plausible way to get a still frame.
    #
    # Untested, hence a flag rather than a deletion: the anchor was added because
    # early clips drifted off-subject, and dropping it may bring that back.
    if no_anchor:
        anchor = ""
    positive = f"{STYLE}. {motion}. Subject already in frame: {anchor}." if anchor \
        else f"{STYLE}. {motion}"
    extra_neg = ", ".join(n[3:].strip() for n in negatives if len(n) > 3)
    anti = antistatic_for(motion)
    # anti applied  => this beat wants motion  => do NOT suppress shake
    # anti suppressed => this beat wants stillness => DO suppress shake
    # a beat that wants motion gets neither shake suppression nor the two
    # motion-suppressing photo terms; a beat that wants stillness gets both
    strict = "" if anti else SHAKE_NEG
    # ORDER IS SURVIVAL. The negative is capped, and a plain [:460] cuts mid-word:
    # adding ANTI_PHOTO_STRICT pushed a still beat to exactly 460 and the tail
    # arrived as "fil". So the PER-BEAT decisions — the ones being tuned, the ones
    # whose presence or absence we are measuring — go FIRST, and the general style
    # list, which is the same on every clip, goes last where losing its tail costs
    # least. Then cut on a comma so no term is ever half-sent.
    parts = [x for x in (extra_neg, anti, strict, ANTI_STYLE) if x]
    # DEDUPE, first-occurrence order. The pieces overlap by construction: the task
    # suffix carries "no new subjects, no scene change", which video_prompt strips
    # into extra_neg, and ANTI_SCENE says "scene change" again. A still beat came to
    # 480 chars against a 460 cap and lost "split screen, montage" — to duplicates.
    # Repeating a term does not strengthen it; it just spends the budget.
    seen, uniq = set(), []
    for term in (t.strip() for t in ", ".join(parts).split(",")):
        k = term.lower()
        if term and k not in seen:
            seen.add(k)
            uniq.append(term)
    neg = ", ".join(uniq)
    if len(neg) > NEG_MAX:
        cut = neg[:NEG_MAX].rsplit(",", 1)[0]
        print(f"!! negative prompt truncated {len(neg)} -> {len(cut)} chars; "
              f"dropped: {neg[len(cut):].strip(', ')[:120]}", flush=True)
        neg = cut
    return positive[:700], neg


MODEL_LICENCE = {
    "ti2v-5b":  ("Wan-AI/Wan2.2-TI2V-5B-Diffusers", "Apache-2.0"),
    "animegen": ("aidealab/AnimeGen-I2V", "Apache-2.0"),
}


def _yaml_block(key: str, value: str) -> str:
    """A literal block scalar — safe for prompts containing quotes, colons, commas.

    Prompts hold ": " and "…" and Chinese negatives; any inline form would need
    escaping rules we would get wrong once and then not notice.
    """
    if not value:
        return f"{key}: ''\n"
    body = "\n".join("  " + ln for ln in str(value).splitlines())
    return f"{key}: |-\n{body}\n"


def write_sidecar(clip, vmodel, task, beat, seconds, steps, size,
                  prompt=None, negative=None):
    """A §7.2 provenance sidecar beside every generated clip.

    Video clips have been landing on the courier branch as bare mp4s, with the
    model recorded nowhere — licence_gate then flags them as "footage ships with
    no provenance", and it is right to. The renderer is the only thing that knows
    what it just ran, so it is the only thing that can say so honestly.

    Licence is written from a table keyed on the SHORT name, not guessed from the
    repo id: an unrecognised model gets "UNVERIFIED" rather than a hopeful
    Apache-2.0, because a wrong allow is the direction that publishes things.
    """
    repo, lic = MODEL_LICENCE.get(vmodel, (vmodel, "UNVERIFIED — licence not read"))
    Path(str(clip) + ".meta.yaml").write_text(
        "# Shot provenance (7.2) — written by video_task at render time\n"
        # "local-gpu (<worker>)" not "local-<worker>": the gate classifies on the
        # generic "local-gpu" prefix, so this form is recognised on ANY machine
        # while still naming which one rendered it. Spelling it "local-dads-msi"
        # made every clip from a new handle an unclassified violation — the fix for
        # one machine's nickname must not depend on another's.
        f"platform: local-gpu ({task.get('worker', 'unknown')})\n"
        f"model: {repo}\n"
        f"model_licence: {lic}\n"
        f"shot_beat: {beat}\n"
        f"size: {size}\n"
        f"seconds: {seconds}\n"
        f"steps: {steps}\n"
        f"guidance: {task.get('guidance', 5.0)}\n"
        f"seed: {int(task.get('seed_base', 20260731)) + beat}\n"
        f"task: {task.get('id')}\n"
        "cost_usd: 0\n"
        # THE PROMPT IS PROVENANCE. CLAUDE.md §7.2 says every render publishes
        # "model, prompt, cost" and this file published two of the three. On
        # 2026-08-02 the founder said beat 2 had "no typing"; the clip was
        # correct for the prompt it was given, but the prompt was nowhere on
        # disk, so telling a bad direction from a bad model meant reconstructing
        # the string by re-running the pipeline. Anyone auditing the tree had no
        # way at all. Record what was actually asked for.
        + _yaml_block("prompt", prompt or "")
        + _yaml_block("negative", negative or ""), encoding="utf-8")


def _run(cmd, courier, stage, timeout=None, retry=False):
    # utf-8 on the child's stdout: Windows consoles default to cp1252, and a
    # single non-ASCII character in a SUCCESS message killed a 25-minute
    # encode with UnicodeEncodeError (2026-07-30, canary 3)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
           # PyTorch's own advice, printed in the OOM that killed AnimeGen on
           # 2026-08-03: "If reserved but unallocated memory is large try setting
           # PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True to avoid
           # fragmentation." That OOM had 917 MiB reserved-but-unallocated while
           # asking for 1.29 GiB — the exact shape this setting addresses. It
           # grows one allocation instead of hunting for a contiguous block, so it
           # costs nothing when memory is plentiful.
           "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
           # HF's newer chunked (xet/CAS) transfer dropped the 10GB model
           # download 23 minutes in on the 5090 (2026-07-31). The classic path
           # resumes; the chunked one restarts.
           "HF_HUB_DISABLE_XET": "1",
           "HF_HUB_DOWNLOAD_TIMEOUT": "60"}
    attempts = 3 if retry else 1
    for attempt in range(1, attempts + 1):
        r = _stream(cmd, courier, timeout, env)
        if courier:
            courier.say(f"$ {' '.join(str(c) for c in cmd[:6])}…\n{(r.stdout or '')[-1500:]}"
                        f"{(r.stderr or '')[-2500:]}")
        if not r.returncode:
            return r
        # a dropped download is not a broken pipeline: say so and try again,
        # because the next attempt resumes from the bytes already on disk
        transient = any(s in (r.stderr or "") for s in
                        ("CAS Client", "error sending request", "Connection",
                         "Read timed out", "IncompleteRead", "ConnectionError"))
        if attempt < attempts and transient:
            if courier:
                courier.mark(f"VIDEO_RETRY {stage} (attempt {attempt} hit a "
                             f"network drop, resuming)")
            continue
        raise RuntimeError(f"{stage} failed (exit {r.returncode})")
    return r


def ensure_stack(courier) -> None:
    """Create the video venv and its deps, marking every stage."""
    ROOT.mkdir(parents=True, exist_ok=True)
    if not PY.exists():
        courier.mark("VIDEO_VENV_CREATING")
        _run([sys.executable, "-m", "venv", str(VENV)], courier, "venv", timeout=600)
    courier.mark("VIDEO_VENV_OK")

    probe = _run([str(PY), "-c", "import torch,diffusers;print(torch.__version__,"
                 "diffusers.__version__,torch.cuda.is_available())"],
                 None, "probe") if _have(PY, "torch") else None
    if probe is None:
        courier.mark("VIDEO_DEPS_INSTALLING")
        pip = [str(PY), "-m", "pip", "install", "-q", "--retries", "30",
               "--timeout", "120"]     # their router kills long streams
        if IS_WIN:
            _run(pip + ["torch", "--index-url", TORCH_INDEX], courier,
                 "torch cu128", timeout=5400)
        else:
            _run(pip + ["torch"], courier, "torch", timeout=5400)
        _run(pip + ["diffusers>=0.35", "transformers", "accelerate", "safetensors",
                    "ftfy", "imageio", "imageio-ffmpeg", "pillow", "huggingface_hub"],
             courier, "diffusers stack", timeout=5400)
        probe = _run([str(PY), "-c", "import torch,diffusers;print(torch.__version__,"
                     "diffusers.__version__,torch.cuda.is_available())"],
                     courier, "probe")
    courier.mark(f"VIDEO_DEPS_OK {probe.stdout.strip()}")

    # TOP-UP, outside the first-run block. The install above runs only when torch
    # is absent, so a machine set up before a package was needed never gets it —
    # and finds out at the END of a 30GB model download. peft is exactly that: it
    # arrived with AnimeGen's LoRAs, long after the 5090's venv was built. Cheap
    # to check (pip is a no-op when satisfied), and it fails here rather than an
    # hour in.
    for mod, spec in (("peft", "peft"),):
        if not _have(PY, mod):
            courier.mark(f"VIDEO_DEPS_TOPUP {spec}")
            _run([str(PY), "-m", "pip", "install", "-q", "--retries", "30",
                  "--timeout", "120", spec], courier, f"install {spec}", timeout=1800)


def gpu_vram_gb() -> float:
    """Total VRAM on device 0, asked of the video venv (this process has no torch)."""
    r = subprocess.run([str(PY), "-c", "import torch;print(torch.cuda.get_device_properties(0)"
                        ".total_memory/1e9 if torch.cuda.is_available() else 0)"],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    try:
        return float((r.stdout or "0").strip())
    except ValueError:
        return 0.0


def _have(py: Path, mod: str) -> bool:
    return subprocess.run([str(py), "-c", f"import {mod}"],
                          capture_output=True).returncode == 0


def prefetch(task: dict, courier) -> None:
    """Download named weights into the video venv's cache, nothing more.

    Downloading is the safe half of trying a new model: it takes bandwidth, not
    judgement, so it can happen overnight while the install decision waits for
    a human. Heartbeats mark each repo so a stalled transfer is visible.
    """
    ensure_stack(courier)
    for spec in task.get("prefetch") or []:
        repo = str(spec["repo"])
        pats = spec.get("patterns") or None
        courier.mark(f"PREFETCH_START {repo}")
        code = (
            "import os\n"
            "os.environ['HF_HUB_DISABLE_XET']='1'\n"
            "os.environ['HF_HUB_DOWNLOAD_TIMEOUT']='60'\n"
            "from huggingface_hub import snapshot_download\n"
            f"p=snapshot_download({repo!r}, allow_patterns={pats!r})\n"
            "print('DOWNLOADED', p)\n")
        _run([str(PY), "-c", code], courier, f"prefetch {repo}",
             timeout=21600, retry=True)
        courier.mark(f"PREFETCH_OK {repo}")


def run(task: dict, courier, node_dir: Path) -> None:
    """One video task: N beats animated from their APPROVED stills.

    `beats` names the beats; each beat's still is the conditioning frame, and
    its shot-board prompt (already founder-approved text) drives the motion.
    """
    from generate_shots import parse_shots

    if task.get("prefetch"):
        return prefetch(task, courier)
    ensure_stack(courier)
    # utf-8 pinned: Windows' cp1252 mangles the em-dash in "## Beat NN —"
    # and parse_shots then finds nothing (the msi's first-light failure)
    directed = motion_directions(node_dir)          # the node's own motion briefs
    actions = beat_actions(node_dir / "node.md")     # fallback: the story action
    shots = {s["num"]: s
             for s in parse_shots((node_dir / "shots.md").read_text(encoding="utf-8"))}
    stills = node_dir / "stills"
    beats = [int(b) for b in str(task.get("beats", "")).split(",") if b.strip()]
    size = task.get("size", "704x1280")
    seconds = float(task.get("seconds", 4))
    steps = int(task.get("steps", 30))

    # BATCH on a big card: build the whole job list, then load the model once.
    # Per-clip processes spent ~10 of every 11 minutes reloading 10GB from disk.
    if gpu_vram_gb() >= 20 and len(beats) > 1:
        jobs, outs = [], []
        for num in beats:
            s = shots.get(num)
            init = next((q for q in stills.glob(f"{num:02d}-*.png")
                         if "REVOKED" not in q.name), None)
            if not s or not init:
                courier.say(f"beat {num}: no shot or no approved still - skipped")
                continue
            motion = task.get("motion") or ("subtle continuous motion, gentle camera "
                                            "drift, living scene")
            o = courier.out / f"{task.get('id')}-{num:02d}-{s['slug']}.mp4"
            act = directed.get(num) or actions.get(num)
            pos, neg = video_prompt(f"{act}. {motion}" if act else motion,
                                    s["prompt"],
                                    no_anchor=bool(task.get("no_anchor")))
            jobs.append({"init": str(init), "out": str(o), "prompt": pos,
                         "negative": neg,
                         "seed": int(task.get("seed_base", 20260731)) + num})
            # carry the prompt to the sidecar — see write_sidecar on why
            outs.append((num, o, pos, neg))
        if jobs:
            jf = ROOT / f"jobs-{task.get('id')}.json"
            jf.write_text(json.dumps(jobs), encoding="utf-8")
            vmodel = str(task.get("video_model", "ti2v-5b"))
            courier.mark(f"VIDEO_RENDERING batch of {len(jobs)} on {vmodel} "
                         f"(one model load)")
            _run([str(PY), str(REPO / "pipeline" / "wan_i2v.py"), "--stage", "simple",
                  "--embeds", str(ROOT / "unused.pt"), "--jobs", str(jf),
                  "--seconds", str(seconds), "--steps", str(steps), "--size", size,
                  "--model", vmodel,
                  "--quantise", str(task.get("quantise", "none")),
                  "--guidance", str(task.get("guidance", 5.0))]
                 + (["--offload"] if task.get("offload") else [])
                 # no_lora is what makes an AnimeGen run PUBLISHABLE. The
                 # Lightning 4-step LoRAs (lightx2v/Wan2.2-Lightning) declare
                 # apache-2.0 in HF metadata and ship NO LICENSE FILE, so our own
                 # gate calls them unknown — a violation, not a note. Without
                 # this flag a queue task could only run AnimeGen *with* them,
                 # i.e. could only produce footage we are not allowed to ship.
                 + (["--no-lora"] if task.get("no_lora") else [])
                 # ALWAYS. The per-beat decision is made in video_prompt() above
                 # and travels in the negative string; wan_i2v's own global copy
                 # would re-add the terms to every beat and undo it.
                 + ["--no-shake-neg"],
                 courier, f"batch {task.get('id')}", timeout=14400, retry=True)
            jf.unlink(missing_ok=True)
            made = 0
            for num, o, pos, neg in outs:
                if o.exists() and o.stat().st_size > 10_000:
                    made += 1
                    write_sidecar(o, vmodel, task, num, seconds, steps, size,
                                  prompt=pos, negative=neg)
                    courier.mark(f"VIDEO_CLIP_OK beat={num:02d} {o.stat().st_size//1024}KB")
                else:
                    courier.mark(f"VIDEO_CLIP_EMPTY beat={num:02d}")
            courier.say(f"video task {task.get('id')}: {made}/{len(outs)} clips")
            if not made:
                raise RuntimeError("no clips produced")
            return

    made = 0
    for num in beats:
        s = shots.get(num)
        if not s:
            courier.say(f"beat {num}: not in shots.md — skipped")
            continue
        init = next((p for p in stills.glob(f"{num:02d}-*.png")
                     if "REVOKED" not in p.name), None)
        if not init:
            courier.say(f"beat {num}: no approved still — skipped")
            continue
        # motion-first wording: the still already IS the composition, so the
        # prompt's job is what MOVES (cycle-001 lesson: front-loaded stillness
        # makes models hold the frame)
        motion = task.get("motion") or "subtle continuous motion, gentle camera drift, living scene"
        # SAME treatment as the batch path. This branch was still concatenating the
        # whole still-generation prompt — the bug that made Wan draw a second plant
        # stem into beat 12 ("a stick poking the sapling"). One code path fixed and
        # the other not is worse than neither, because the difference is invisible
        # in the queue: a task with ONE beat took this branch and a task with two
        # took the other, silently rendering on the default model with the old
        # prompt. Caught when a one-clip AnimeGen canary logged "beat=01
        # (single-process)" and rendered plain Wan (2026-08-01).
        # motion_override lets a canary try a different DIRECTION without editing
        # motion.yaml — the genome is the author's, and a test should not rewrite it
        act = task.get("motion_override") or directed.get(num) or actions.get(num)
        prompt, neg = video_prompt(f"{act}. {motion}" if act else motion,
                                   s["prompt"],
                                   no_anchor=bool(task.get("no_anchor")))
        vmodel = str(task.get("video_model", "ti2v-5b"))
        out = courier.out / f"{task.get('id')}-{num:02d}-{s['slug']}.mp4"
        emb = ROOT / f"embeds-{num:02d}.pt"
        wan = str(REPO / "pipeline" / "wan_i2v.py")
        # two processes: holding the 11GB text encoder AND the transformer in
        # one process killed the 16GB machine with an access violation
        # (0xC0000005). Encoding in a process that then EXITS is the only
        # reliable way to give that memory back on Windows.
        big = gpu_vram_gb() >= 20
        if big:
            # one process, the library's own pipeline class and encoding: the
            # split-process shortcuts are a 16GB workaround and one of them
            # was bypassing the image conditioning (first 5090 clip, garbage)
            courier.mark(f"VIDEO_RENDERING beat={num:02d} on {vmodel} "
                         f"(single-process)")
            _run([str(PY), wan, "--stage", "simple", "--embeds", str(emb),
                  "--prompt", prompt, "--init", str(init), "--out", str(out),
                  "--negative", neg,
                  "--model", vmodel,
                  "--quantise", str(task.get("quantise", "none")),
                  "--seconds", str(seconds), "--steps", str(steps), "--size", size,
                  # --guidance WAS MISSING HERE. The batch path passed it and this
                  # one did not, so every single-beat render — which is every clip
                  # in the episode and every canary — silently used wan_i2v's
                  # default 5.0 no matter what the queue said. Caught 2026-08-03
                  # when a cfg 3.0 test produced a file BYTE-IDENTICAL to the cfg
                  # 5.0 baseline (same sha256). That is not a result, it is a flag
                  # that never arrived, and I had already written "guidance did
                  # nothing" into a commit message on the strength of it.
                  "--guidance", str(task.get("guidance", 5.0)),
                  "--seed", str(int(task.get("seed_base", 20260731)) + num)]
                 + (["--offload"] if task.get("offload") else [])
                 # no_lora is what makes an AnimeGen run PUBLISHABLE. The
                 # Lightning 4-step LoRAs (lightx2v/Wan2.2-Lightning) declare
                 # apache-2.0 in HF metadata and ship NO LICENSE FILE, so our own
                 # gate calls them unknown — a violation, not a note. Without
                 # this flag a queue task could only run AnimeGen *with* them,
                 # i.e. could only produce footage we are not allowed to ship.
                 + (["--no-lora"] if task.get("no_lora") else [])
                 # ALWAYS. The per-beat decision is made in video_prompt() above
                 # and travels in the negative string; wan_i2v's own global copy
                 # would re-add the terms to every beat and undo it.
                 + ["--no-shake-neg"],
                 courier, f"beat {num}", timeout=7200, retry=True)
        else:
            courier.mark(f"VIDEO_ENCODING beat={num:02d}")
            _run([str(PY), wan, "--stage", "encode", "--embeds", str(emb),
                  "--prompt", prompt], courier, f"encode {num}", timeout=3600, retry=True)
            courier.mark(f"VIDEO_RENDERING beat={num:02d}")
            # THE THIRD sampling path, and it was missing --guidance, --model and
            # --quantise while the other two had them. Three paths that sample must
            # honour the same parameters or a queue value means different things
            # depending on which one runs — that divergence is exactly how
            # "guidance did nothing" got written down as a finding.
            _run([str(PY), wan, "--stage", "render", "--embeds", str(emb),
                  "--init", str(init), "--out", str(out),
                  "--model", vmodel,
                  "--quantise", str(task.get("quantise", "none")),
                  "--guidance", str(task.get("guidance", 5.0)),
                  "--seconds", str(seconds), "--steps", str(steps), "--size", size,
                  "--seed", str(int(task.get("seed_base", 20260731)) + num)],
                 courier, f"beat {num}", timeout=7200, retry=True)
        emb.unlink(missing_ok=True)
        if out.exists() and out.stat().st_size > 10_000:
            made += 1
            write_sidecar(out, vmodel, task, num, seconds, steps, size,
                          prompt=prompt, negative=neg)
            courier.mark(f"VIDEO_CLIP_OK beat={num:02d} "
                         f"{out.stat().st_size // 1024}KB")
        else:
            courier.mark(f"VIDEO_CLIP_EMPTY beat={num:02d}")
    courier.say(f"video task {task.get('id')}: {made}/{len(beats)} clips")
    if not made:
        raise RuntimeError("no clips produced")
