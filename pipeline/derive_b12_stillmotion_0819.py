#!/usr/bin/env python3
r"""Derive pipeline/jobs/ep2-b12-stillmotion-0819.yaml FROM the growmotion recipe.

PARENT: pipeline/jobs/ep2-b01-growmotion-crf10-0819.yaml -- the LTX i2v recipe
that came back PASS and CUT-PREFERRED tonight ("f120 from init 15.2 vs 65.7;
luma ends 84.8 vs plate 85.1 where the original blooms to 148.4; monotone over 85
frames, 0 shrinks"). Everything a sampler reads is carried BY COPY: 121 frames at
704x1280, 24 fps, guidance 2.0, --distilled-sigmas, --two-stage, --image-crf 10,
--offload sequential, and cover_crop.py / stamp_sidecar.py byte-for-byte. The one
variable is the beat.

WHY BEAT 12 IS THE BEAT THIS RECIPE WANTS, AND IT IS NOT THE OBVIOUS ARGUMENT.
The ladder's own calibration says crf 10 is NOT a global win: on beat 18 -- a
macro whose whole content is fine high-frequency tremble -- a cleaner init gave
i2v less to push off from and the shot FROZE (interframe median 0.570 against
5.956; FAIL-FROZEN; the original still stands). Beat 12 is a macro too, so the
naive read is that this recipe is contraindicated here.

It is the opposite, for two reasons that both come from the beat rather than from
the recipe:

  1. THE APPROVED LINE ASKS FOR THE THING THAT FAILED BEAT 18. The founder
     approved beat 12's rewritten staging this morning (5d6eb792), and it reads
     "Tight on the sapling's two leaves, PERFECTLY STILL -- the scavenger
     crouched behind them, out of frame." On beat 18 near-stillness was a defect
     because the beat is a tremble. Here it is the instruction.
  2. BEAT 12'S ONE NAMED SHIPPING FAULT IS THE crf-33 SIGNATURE.
     done-definitions.yaml beats.'12' ships this beat WITH A FAULT NAMED: "the
     colour shifts warm-to-cool across the first second", also recorded as the
     reason the beat is UNFINISHED. That is what an abandoned init looks like --
     the same measurement class as beat 01's "luma ends 84.8 vs plate 85.1 where
     the crf-33 original blooms to 148.4" and beat 07's "background strip drift
     5.43 against 36.41, the crf-33 field visibly boils". So the beat's own
     recorded blemish is the defect this flag was measured to cause, and testing
     it costs one clip.

WHAT THIS RUNG IS NOT. It is not a one-variable A/B against the shipped take:
that clip carries a different prompt (a 1,400-character wording built to force a
leaf COUNT) and a different seed. The comparison this job is built for is
BEAT-INTERNAL and it is stated in the bar -- the same plate, at crf 10, judged on
whether the palette holds across the first second and whether the frame stays
still without dying.

A PLATE FAULT THAT IS NOT THIS JOB'S TO FIX, DECLARED UP FRONT. The plate under
this beat -- 12-related-r4-s2.png, which is the SHIPPED take's own init -- does
not carry the canon two cotyledons. Measured on it directly: four blade-sized
components with major axes 619/772/607/591 px and aspects 2.85/3.11/3.38, against
composite-init-pattern.md 8's pre-registered acceptable band of 1.6-2.6. They are
lance-shaped and there are more than two. i2v cannot fix that -- an init is frame
one -- so the count clause below is scored AGAINST THE PLATE and not against this
take, and beat 12's route to a real two-leaf frame is the composite instrument
that solved beats 15 and 19 tonight. Filing this take is worth doing anyway
because the colour fault is orthogonal and the shipped clip is already in the
cut; pretending the count was in play would be the dishonest part.

$0 to derive. No model, no network, no GPU.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PARENT = os.path.join(REPO, "pipeline", "jobs", "ep2-b01-growmotion-crf10-0819.yaml")
OUT = os.path.join(REPO, "pipeline", "jobs", "ep2-b12-stillmotion-0819.yaml")

PARENT_DIR = r"C:\banyan-farm\ep2-b01-growmotion-crf10-0819"
PARENT_OUT = r"C:\banyan-farm\ep2-b01-growmotion-crf10-0819-out"
CHILD_DIR = r"C:\banyan-farm\ep2-b12-stillmotion-0819"
CHILD_OUT = r"C:\banyan-farm\ep2-b12-stillmotion-0819-out"

PLATE_REPO_PATH = ("genomes/sapling/nodes/002b-first-citizen/takes/stills/"
                   "12-related-r4-s2.png")
PLATE_NAME = "12-related-r4-s2.png"
PLATE_SHA = "cc6bd5f0c0cc116d3cb6530a9bae81ac5b5593a683e4e80e20d6319e0cc0c074"
CLIP_NAME = "12-related-LTX-stillmotion-crf10-s20260819.mp4"
SEED = 20260819

REFUSE = re.compile(r"verdict|pick|sweep|plate_ack", re.I)

# THE APPROVED LINE, VERBATIM, AND IT LEADS THE PROMPT.
# node.md as rewritten 2026-08-17 and approved 2026-08-19 (5d6eb792, "all
# approved"). The recipe's own style tail is carried from the parent unchanged;
# what precedes it is his sentence and the two facts a locked near-still shot
# needs (nothing enters, the frame does not move).
APPROVED_LINE = ("Tight on the sapling's two leaves, perfectly still -- the "
                 "scavenger crouched behind them, out of frame.")
PROMPT = (
    APPROVED_LINE + " Static locked framing, the frame never moves and nothing "
    "enters it. The leaves hold their shape and their position; only the grass "
    "stirs, very slightly, in the air. Detailed cinematic anime, warm amber "
    "backlight, hazy out-of-focus grassy field, soft glowing light, masterpiece, "
    "best quality, very aesthetic.")

# The parent's camera-lock negative, carried, plus the terms this beat's own line
# forbids by name: anyone entering the frame, and the plant changing.
NEGATIVE = (
    "camera pan, camera tilt, zoom, dolly, push in, pull back, tripod, cut to "
    "another shot, scene change, different location, split screen, still image, "
    "freeze frame, goblin, creature, person, face, hands, figure entering frame, "
    "new leaf, extra leaf, growing leaf, wilting, leaves falling")

FETCH = '''#!/usr/bin/env python3
"""Fetch beat 12's plate off origin/main and refuse on a sha mismatch.

No model, no GPU, no spend. C:\\\\banyan-farm\\\\plates-local -- where the 08-13
beat-12 jobs read this same file from -- NO LONGER EXISTS on this box (checked).
So the plate is fetched from the repo, which is better anyway: the sha asserted
here is verifiable by anyone who clones it, and a plate that has to travel by
hand is a plate whose provenance is a claim.
"""
import hashlib, os, sys, urllib.request

OUT = r"{child_dir}"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "{repo_path}")
UA = {{"User-Agent": "banyan-city-b12-stillmotion/1.0 (albert.numbro@gmail.com)"}}
WANT = "{sha}"

os.makedirs(OUT, exist_ok=True)
raw = urllib.request.urlopen(
    urllib.request.Request(RAW, headers=UA), timeout=120).read()
have = hashlib.sha256(raw).hexdigest()
if have != WANT:
    sys.exit("!! SHA MISMATCH for {name} -- refusing.\\n   want %s\\n   have %s"
             % (WANT, have))
with open(os.path.join(OUT, "{name}"), "wb") as fh:
    fh.write(raw)
print("fetched {name} %d bytes sha %s OK" % (len(raw), have), flush=True)
'''.format(child_dir=CHILD_DIR.replace("\\", "\\\\"), repo_path=PLATE_REPO_PATH,
           sha=PLATE_SHA, name=PLATE_NAME)


def swap(value):
    if isinstance(value, str):
        return (value.replace(PARENT_OUT, CHILD_OUT)
                     .replace(PARENT_DIR, CHILD_DIR)
                     .replace(PARENT_OUT.replace("\\", "/"), CHILD_OUT.replace("\\", "/"))
                     .replace(PARENT_DIR.replace("\\", "/"), CHILD_DIR.replace("\\", "/"))
                     .replace("ep2-b01-growmotion-crf10-0819", "ep2-b12-stillmotion-0819")
                     .replace("b01-nub-init-704x1280.png", "b12-init-704x1280.png")
                     .replace("01-cold-open-LTX-nubgrow-b-s20260826.mp4", CLIP_NAME)
                     .replace("bench-b01-nubgrow", "bench-b12-stillmotion")
                     .replace("b01-embeds.pt", "b12-embeds.pt")
                     .replace("b01-jobs-encode.json", "b12-jobs-encode.json")
                     .replace("b01-jobs-render.json", "b12-jobs-render.json")
                     .replace("b01-motion-prompt.txt", "b12-motion-prompt.txt")
                     .replace("b01-negative.txt", "b12-negative.txt")
                     .replace("THE GLOB CARRIES THE BEAT SLUG (01-cold-open)",
                              "THE GLOB CARRIES THE BEAT SLUG (12-related)"))
    if isinstance(value, list):
        return [swap(v) for v in value]
    return value


def main() -> int:
    local = os.path.join(REPO, PLATE_REPO_PATH)
    if not os.path.isfile(local):
        print("!! plate not found at %s" % local)
        return 2
    h = hashlib.sha256()
    with open(local, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != PLATE_SHA:
        print("!! PLATE SHA MISMATCH\n   want %s\n   have %s" % (PLATE_SHA, h.hexdigest()))
        return 3

    if os.path.isfile(OUT) and "--force" not in sys.argv:
        existing = yaml.safe_load(open(OUT, encoding="utf-8")) or {}
        scored = sorted(k for k in existing if REFUSE.search(k))
        if scored:
            print("!! %s already carries %s -- refusing to overwrite a SCORED "
                  "spec. Pass --force if that is genuinely what you want."
                  % (os.path.relpath(OUT, REPO), ", ".join(scored)))
            return 5

    parent = yaml.safe_load(open(PARENT, encoding="utf-8"))
    refused = sorted(k for k in parent if REFUSE.search(k))
    child = {k: swap(v) for k, v in parent.items() if k not in refused}

    # ---- payload: the two scripts byte-for-byte, the two prompt files new, the
    # ---- two jobs jsons rewritten, plus one fetch step the parent did not need.
    payload = {}
    carried = []
    for key, val in parent["payload"].items():
        base = key.rsplit("\\", 1)[-1]
        newkey = swap(key)
        if base == "cover_crop.py":
            payload[newkey] = val
            carried.append("cover_crop.py BYTE-FOR-BYTE, sha256 %s"
                           % hashlib.sha256(val.encode()).hexdigest()[:12])
        elif base == "stamp_sidecar.py":
            # NOT byte-for-byte, and it must not be. This script WRITES THE
            # CLIP'S PROVENANCE SIDECAR. Carried unchanged it would stamp
            # "appended by ep2-b01-growmotion-crf10-0819" and point the reader at
            # beat 01's bar -- a sidecar that names the wrong job is worse than no
            # sidecar, because 7.2 provenance is read as fact. So the id, the bar
            # path and the beat-01 description are all swapped, and the claim in
            # `derivation` says "carried with N substitutions" rather than
            # pretending to byte-identity.
            payload[newkey] = swap(val)
        elif base == "b01-motion-prompt.txt":
            payload[newkey] = PROMPT
        elif base == "b01-negative.txt":
            payload[newkey] = NEGATIVE
        else:
            payload[newkey] = swap(val)
    payload[CHILD_DIR + r"\fetch_plate.py"] = FETCH
    # stamp_sidecar.py names its own job id in the note it appends; swap() has
    # already rewritten the id, but the two sentences about beat 01's nub are
    # beat 01's. Replaced, and this is the only edit to a carried script.
    stamp_key = CHILD_DIR + r"\stamp_sidecar.py"
    before = payload[stamp_key]
    payload[stamp_key] = payload[stamp_key].replace(
        "This clip IS a candidate for the cut (the cold open), so is_show_content is",
        "This clip IS a candidate for the cut (beat 12), so is_show_content is").replace(
        "A CANDIDATE TAKE FOR THE EPISODE 2 COLD OPEN. It animates the",
        "A CANDIDATE TAKE FOR BEAT 12, RELATED. It animates the").replace(
        "founder's own 2026-08-13 route -- a small inpainted nub, grown by",
        "line he approved on 2026-08-19 -- tight on two leaves, perfectly").replace(
        "the motion prompt -- on the frame-1 plate that passed its bar 7 of",
        "still -- on the plate under the take this beat already ships, at").replace(
        "7 (ep2-b01-nubcomp-b-0818). Judged against the bar pre-registered",
        "--image-crf 10 instead of 33. Judged against the bar pre-registered")
    subs = sum(1 for a, b in zip(before.splitlines(), payload[stamp_key].splitlines())
               if a != b)
    carried.append("stamp_sidecar.py carried with %d line substitutions (the job id, "
                   "the bar path and beat 01's description -- a sidecar naming the "
                   "wrong job is a provenance defect, not a cosmetic one)" % subs)
    child["payload"] = payload

    # ---- steps: the parent's, with a fetch in front and the crop re-sourced.
    steps = []
    for step in parent["steps"]:
        s = {k: swap(v) for k, v in step.items()}
        if s["name"] == "crop":
            argv = list(s["argv"])
            argv[argv.index("--src") + 1] = CHILD_DIR + "\\" + PLATE_NAME
            argv[argv.index("--sha256") + 1] = PLATE_SHA
            s["argv"] = argv
        steps.append(s)
    steps.insert(0, {"name": "fetch",
                     "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                              CHILD_DIR + r"\fetch_plate.py"]})
    child["steps"] = steps
    child["artifacts"] = [CHILD_OUT + "\\" + CLIP_NAME,
                          CHILD_OUT + r"\b12-init-704x1280.png"]

    # ---- the beat.
    child["id"] = "ep2-b12-stillmotion-0819"
    child["task"] = "ep2-b12-stillmotion-0819"
    child["beat"] = 12
    child["sample"] = True
    child["max_attempts"] = 1
    child["owner"] = ("beat 12/15/20 lane, 2026-08-19 -- derived by "
                      "pipeline/derive_b12_stillmotion_0819.py")
    child["consumer"] = (
        "THE EP2 CUT. Beat 12 is not a slate -- it ships -- but done-definitions.yaml "
        "records it as SHIP WITH FAULT NAMED and UNFINISHED, on one fault: 'the colour "
        "shifts warm-to-cool across the first second'. That fault is the crf-33 "
        "signature this repo measured tonight on three other beats, and beat 12's newly "
        "approved line asks for near-stillness, which is the one thing crf 10 has been "
        "measured to over-deliver. One clip decides whether the cut can swap.")
    child["success"] = (
        "ONE 121-frame 704x1280 mp4 with its sidecar and the 704x1280 init it was "
        "conditioned on, published into courier-box. The bar is below and it was written "
        "before the pixels existed. THE BAR'S OWN FIRST CLAUSE IS THE PALETTE, because "
        "that is the fault this rung exists to test -- not the leaf count, which belongs "
        "to the plate and is declared as a plate fault in this spec.")
    child["why"] = (
        "The approved line asks for 'perfectly still', and this recipe's known cost is "
        "motion (-23% on beat 07's gesture, -90% on beat 18's tremble). On this beat "
        "that cost is the brief. Its known benefit is init fidelity, and this beat's "
        "only named shipping fault is a first-second colour shift, which is what an "
        "abandoned init looks like.")
    child["est_minutes"] = 8

    child["bar"] = {
        "the_approved_line_this_is_staged_TO": (
            "Verbatim, and it is the first sentence of the motion prompt: \"%s\" Approved "
            "by the founder on 2026-08-19 (5d6eb792), one of five restaged beats whose "
            "STEWARDSHIP.md 6 block came off the same day. beats.'12'.done_when, written "
            "2026-08-15, is the other half: 'tight on the sapling's TWO leaves against "
            "the sky; exactly two cotyledons and one bare side-branch, per the growth "
            "ladder; no bush, no crown; the goblin NOT in frame.'" % APPROVED_LINE),
        "M1_THE_PALETTE_HOLDS_ACROSS_THE_FIRST_SECOND": (
            "THE CLAUSE THIS RUNG EXISTS FOR. Mean hue and mean luminance of the whole "
            "frame at f000, f012 and f024, against the 704x1280 init the clip was "
            "conditioned on. PASS = the warm-to-cool swing the shipped take was shipped "
            "with is materially smaller here. Reported as numbers against the shipped "
            "clip measured the same way, so the comparison is on the same instrument."),
        "M2_NEAR_STILL_BUT_NOT_DEAD": (
            "The leaves hold position and shape; the grass stirs. MEASURED ON REGIONS, "
            "NOT ON THE FRAME, per the beat-19 lane's finding that a whole-frame "
            "interframe floor is the wrong instrument on a near-still beat (a perfect "
            "32px fall over a frozen background moves whole-frame interframe by 0.056 "
            "and would fail the floor). So: interframe median inside the leaf mask, and "
            "interframe median inside the grass band, reported separately. PASS = leaf "
            "band near zero AND grass band non-zero."),
        "M3_NOBODY_ENTERS_FRAME": (
            "no goblin, no hand, no face, no figure at any edge in any of the 121 "
            "frames. His own line puts the scavenger OUT OF FRAME, crouched behind the "
            "leaves, so a figure arriving is a fail even if it is beautiful."),
        "M4_CAMERA_LOCKED": (
            "no pan, tilt, dolly or zoom. Measured as a global fit on a high-contrast "
            "edge, and reported with the region-consistency check the beat-19 lane "
            "added: a shift that appears on a low-contrast band but not on a "
            "high-contrast one is the field re-inking, not a camera move, and filing a "
            "camera fault that does not exist is its own defect."),
        "M5_THE_PLANT_DOES_NOT_CHANGE": (
            "no leaf appears, disappears, wilts or grows across the 121 frames. This is "
            "the clause the b19 motion take failed hardest (two leaves -> four+, one fig "
            "-> two, upright stem -> runner, in 90 frames), and it is the clause a "
            "near-still beat is most likely to pass."),
        "THE_COUNT_IS_NOT_SCORED_AGAINST_THIS_TAKE": (
            "beats.'12'.done_when asks for EXACTLY TWO cotyledons and one bare "
            "side-branch. THE PLATE DOES NOT CARRY THAT and no i2v render can add it, "
            "because the init is frame one. Measured on the plate itself: four "
            "blade-sized components, major axes 619/772/607/591 px, aspects "
            "2.85/3.11/3.38 against composite-init-pattern.md 8's pre-registered 1.6-2.6 "
            "band -- lance-shaped, and more than two. It is recorded here as a PLATE "
            "FAULT with a named route (the composite instrument that solved beats 15 and "
            "19 tonight, which is a build and not a wording) and it is NOT charged to "
            "this take. Scoring it here would let a real colour result be buried under a "
            "fault the render could not have avoided."),
        "how_scored": (
            "Every one of the 121 frames opened, not sampled -- the beat-07 lane's "
            "standard tonight. Numbers are FILTERS; the verdict is the read."),
    }
    child["failure_predicted_in_advance"] = (
        "FAIL-DEAD IS THE MOST LIKELY OUTCOME AND IT IS NAMED SO THAT A PASS MEANS "
        "SOMETHING. Beat 18 is the closest beat in the repo to this one by shot class -- "
        "a macro whose content is fine high-frequency movement -- and at crf 10 it went "
        "from an interframe median of 5.956 to 0.570 and was scored FAIL-FROZEN. If that "
        "happens here the clip is a still image with a file extension, and 'perfectly "
        "still' does not mean 'a still': the line's own 'only the grass stirs' is what "
        "separates the two, which is why M2 measures the grass band separately rather "
        "than measuring the frame. If FAIL-DEAD fires, the lever is NOT another crf "
        "value -- it is this beat's own prompt, which currently asks for stillness with "
        "the whole of its first sentence, and the shipped take's crf-33 clip remains in "
        "the cut untouched meanwhile.")
    child["pre_registered_fail_modes"] = {
        "FAIL-DEAD": "no movement anywhere, grass included. Named as most likely.",
        "FAIL-PALETTE": ("the warm-to-cool shift survives at crf 10, i.e. the shipped "
                         "fault is not the flag's. A real and useful negative result: it "
                         "would move the cause to the prompt or the plate."),
        "FAIL-INTRUDER": "a goblin, hand, face or figure enters frame. His line forbids it.",
        "FAIL-PLANT-CHANGE": "a leaf appears, vanishes, wilts or grows.",
        "FAIL-CAMERA": "a real, region-consistent camera move.",
        "FAIL-BLOOM": ("luminance climbs across the clip the way beat 01's crf-33 take "
                       "did (85 -> 148.4). The flag is supposed to prevent this; if it "
                       "arrives anyway the finding is about the flag, not the beat."),
        "reporting_rule": ("every mode above is reported BY NAME whether or not it fired, "
                           "and the near-duplicate share is reported on the TRACKED "
                           "REGIONS rather than the frame, per the beat-19 finding."),
    }
    child["duration_and_the_assembler_trap"] = (
        "121 frames at 24 fps = 5.0417 s. render_t3.py:616 REVERSES any clip whose slot "
        "outruns it (dur > cdur + 0.05, cdur <= 16.0). The beat-19 lane found this with "
        "0.09 s of margin on a beat whose action is irreversible. Beat 12 is near-still, "
        "so a palindrome would be nearly invisible here -- which is worse, not better: "
        "it means nobody would catch it. Whoever assembles should check beat 12's slot "
        "length against 5.0417 s rather than assume.")
    child["script_authority"] = (
        "Node 002b-first-citizen, approved_by: founder, and beat 12's rewritten line "
        "approved by name on 2026-08-19 (5d6eb792) -- which is what makes rendering it "
        "legal at all. STEWARDSHIP.md 6 blocked footage from this beat's restaged line "
        "until he had read it; leaves/002b-t0-c.yaml carried 'approval_status: NOT YET "
        "READ BY HIM' for beats 12, 13, 15, 19 and 20, and that block is discharged. "
        "Rendering the OLD staging instead would have been the wrong way round it.")
    child["init_provenance"] = (
        "%s, sha256 %s, fetched from origin/main by fetch_plate.py and re-asserted before "
        "the crop. It is the SHIPPED beat-12 take's own init (ep2-b12-tightB-0813 crops "
        "the same file at the same sha), which is what makes the palette comparison a "
        "comparison. C:\\banyan-farm\\plates-local, where the 08-13 jobs read it from, no "
        "longer exists on the box -- checked, not assumed." % (PLATE_REPO_PATH, PLATE_SHA))
    child["derivation"] = {
        "parent": "pipeline/jobs/ep2-b01-growmotion-crf10-0819.yaml",
        "by": "pipeline/derive_b12_stillmotion_0819.py",
        "carried_byte_for_byte": carried,
        "keys_refused": ("REFUSED, not carried: %s. The parent carries an INHERITED pick "
                         "block that recommends a clip for a decision made before that "
                         "clip existed, plus two inherited sweep summaries -- exactly the "
                         "defect the ladder asked for a guard against."
                         % ", ".join(refused)) if refused else "none",
        "sampler_numbers_unchanged": ("121 frames, 704x1280, 24 fps, guidance 2.0, "
                                      "--distilled-sigmas, --two-stage, --image-crf 10, "
                                      "--offload sequential, --mode production"),
        "seed": SEED,
        "what_is_NOT_the_same": ("the init and its source, the two prompt files, the bar, "
                                 "the fail modes, one added fetch step, and four sentences "
                                 "inside stamp_sidecar.py's appended note."),
        "why_no_CLIP_token_count_here": (
            "pipeline/clip_token_count.py measured the beat-15 SDXL job and caught a "
            "negative at 85 of 77. It is NOT run on this job and that is deliberate: LTX "
            "conditions on a T5 encoder, not CLIP, so a 77-token CLIP ceiling is the "
            "wrong instrument and quoting it here would be a number that looks like "
            "evidence."),
    }

    # the render json needs this beat's seed and beat number
    for key in list(child["payload"]):
        if key.endswith("b12-jobs-render.json"):
            child["payload"][key] = (child["payload"][key]
                                     .replace('"beat": 1,', '"beat": 12,')
                                     .replace('"seed": 20260818,', '"seed": %d,' % SEED))
        if key.endswith("b12-jobs-encode.json"):
            child["payload"][key] = child["payload"][key].replace('"beat": 1,', '"beat": 12,')

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(child, fh, sort_keys=False, width=100,
                       default_flow_style=False, allow_unicode=False)

    print("parent  %s" % os.path.relpath(PARENT, REPO))
    print("child   %s" % os.path.relpath(OUT, REPO))
    print("keys refused: %s" % (", ".join(refused) or "none"))
    print("carried byte-for-byte: %s" % "; ".join(carried))
    print("plate %s sha OK" % PLATE_NAME)
    print("steps: %s" % ", ".join(s["name"] for s in child["steps"]))
    print("rc=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
