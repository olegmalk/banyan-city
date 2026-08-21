#!/usr/bin/env python3
r"""EMIT PLATE SPECS ON THE FOUNDER'S OWN GOBLIN -- the sample, then the wave.

    python3 pipeline/derive_jerry_canon_0821.py --sample          # beat 13, one frame
    python3 pipeline/derive_jerry_canon_0821.py --wave            # the other six
    python3 pipeline/derive_jerry_canon_0821.py --beat 4 --round r2 --emotion worried

Every value comes from `pipeline/jerry_canon_0821.py`, which is
`canon.yaml -> founder_ruling_2026_08_21` expressed as constants. Nothing is
typed twice and nothing here decides anything: this file is the wiring.

ONE SAMPLE BEFORE ANY BATCH (founder, 2026-08-03). `--wave` REFUSES to run until
the sample spec exists and has been judged -- see `_sample_judged`. The recipe
changed wholesale today (new reference image, new proportion, new eye, new
costume) and that is exactly the case the rule is written for.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard                    # noqa: E402
import derive_spec                           # noqa: E402
import jerry_canon_0821 as C                 # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-jerry-face-k6a-0821.yaml"
PARENT_DIR_TOKEN = "jerryface-k6a-0821"
NODE = "002b-first-citizen"
OWNER = "canon lane, 2026-08-21"
PY = r"C:\banyan-farm\venv\Scripts\python.exe"

BAR = """THE CANON BAR. Read at 1:1 against taste/refs/goblin-canon-founder-0821.png
-- THE FOUNDER'S OWN IMAGE -- and against nothing else. Tile B
(adult-b19-0819.jpg) is SUPERSEDED and is no longer the thing to match; a frame
that looks like the tile now FAILS.

  IDENTITY -- five clauses, and three of them invert a bar that stood this
  morning. Every number is measured off the founder's image.
  F1  EARS: LARGE, LATERAL, POINTED, projecting clear of the skull on both
      sides and dominating the silhouette. Measured target: ear span about 1.5x
      the skull width. SHORT LOW FLANGES NOW FAIL -- that was the tile's ear and
      it is struck. So does a bare skull with no ear read at all.
  F2  EYES: a large open almond with an off-white sclera AND A VISIBLE PUPIL --
      small, dark, a narrow VERTICAL slit. BLANK PUPIL-LESS EYES NOW FAIL. A
      round black anime pupil filling the eye also fails; the target is ~10% of
      the eye's width.
  F3  BALD, smooth unbroken dome, no hair, no hairline, no horns, no cowl.
  F4  SKIN: a muted desaturated grey-olive over the whole body, one tone. A
      saturated kelly green fails. A human complexion fails. Measured #7C806D.
  F5  NO AGE MODELLING: no brow furrows, no nasolabial folds, no jowls, no
      cheekbone shadow. The face is smooth. He is not an adult man.

  PROPORTION
  P1  ABOUT 2.7 HEADS TALL, head roughly 37% of the standing figure. This is the
      founder's own drawing and it is deliberately large-headed. A 5-heads
      figure fails; so does a head so large the body cannot act.
  P2  NOT A MASCOT. Round-bellied, squat, or super-deformed still fails -- the
      killed chibi design is still killed. Large head, ordinary child body.

  COSTUME -- new today, and the cloak is dead.
  W1  MANDARIN / BAND COLLAR SHIRT in muted sage, dark shorts above the knee,
      bare shins, dark ankle boots.
  W2  NO CLOAK, NO HOOD, NO COWL, NO PATCHES, NO STITCH LINES. A patchwork
      cloak is the single most likely regression: it was in the frozen positive
      until today and it is still in four script lines.

  THE BEAT
  B1  THE POSE IS THE ONE ASKED FOR.
  B2  THE WORLD IS PRESENT AT FRAME ONE -- this beat's own location, in focus
      enough to read. An empty studio background fails.
  B3  THE BEAT'S EMOTION IS LEGIBLE WITH THE CAPTION COVERED, judged against
      the stage direction recorded in this spec.

  PALETTE
  L1  MUTED, HIGH-KEY, LOW SATURATION, soft ink linework. The founder's image
      is watercolour-adjacent and its background is genuinely out of focus.

A frame failing ANY of F1-F5, P1-P2 or W2 is REJECTED and is not a candidate.
Near-misses are what made the 31-frame LoRA set untrainable."""


def _fresh(beat, rnd, sample):
    stage = C.WAVE[beat][3]
    what = ("THE ONE SAMPLE FOR THE WHOLE CANON RECIPE" if sample
            else "BEAT %02d OF THE CANON PATCH WAVE" % beat)
    return {
        "owner": OWNER,
        "consumer": (
            ("THE JUDGEMENT THAT RELEASES THE CANON WAVE, and nothing else "
             "renders until it is made. On this one frame depend six more "
             "plates, seven motion tranches and the swap into "
             "review/ep2-ship-0821. If it fails, the round-2 variable is named "
             "in `round_2_lever` and the wave waits."
             ) if sample else
            ("The canon patch wave's plate for beat %02d. A pass here becomes a "
             "plate CANDIDATE; the pick is a separate judgement, the motion "
             "re-derive is a separate spec, and review/ep2-ship-0821 is NOT "
             "touched by this job." % beat)),
        "success": (
            "ONE 832x1216 png at seed %d on the CANON recipe, scored at 1:1 "
            "against taste/refs/goblin-canon-founder-0821.png on the bar in "
            "`bar`. Beat %02d's own emotion (B3) is scored against the stage "
            "direction in this spec, not against a general impression."
            % (C.SEED, beat)),
        "why": (
            "%s, ROUND %s.\n\n%s\n\n"
            "THE RECIPE CHANGED WHOLESALE AT 16:54 TODAY. The founder supplied "
            "a picture -- taste/refs/goblin-canon-founder-0821.png, commit %s -- "
            "with \"dude, this is how the goblin should look\", and it "
            "contradicts tile B on the ears, the eyes, the proportion, the skin "
            "and the clothes. Every frame rendered before it is the wrong "
            "character. They are kept as evidence, not deleted.\n\n"
            "WHAT MOVED, all of it measured and all of it in canon.yaml "
            "`founder_ruling_2026_08_21`: head_frac 0.190 -> 0.370 (2.71 heads); "
            "the IP-Adapter reference re-cropped off the founder's image on a "
            "square canvas; `blank eyes` struck and `slit pupils` in its place; "
            "`pointy ears` moved from the NEGATIVE to the POSITIVE; the "
            "patchwork cloak replaced by the drawn costume; the head mask "
            "re-derived from the skeleton because k6a's box would sit inside "
            "this head's forehead."
            % (what, rnd, stage, C.CANON_COMMIT)),
    }


# ROUND TWO'S BASELINE NEGATIVE, added to every rung after the sample. The two
# hard fails on ep2-b13-canon-s1-0821 were a SECOND FLOATING HEAD and orange
# irises; `2boys` was already in the negative and did not touch the head,
# because a second head is not a second character and the tag for a character
# does not name it.
NEG_R2 = ("extra head, disembodied head, multiple heads, floating head, "
          "orange eyes, glowing eyes, red eyes, saturated, high contrast")


def _strip_terms(where, clause, terms):
    """Delete named comma terms from a clause, refusing a term that is absent.

    SUBTRACTION IS A LEVER THIS DERIVER DID NOT HAVE and the round-nine order
    needs it: the founder's eye is an off-white field with a tiny pupil, and
    the words `slit pupils` / `constricted pupils` in the positive and
    `blank eyes` / `no pupils` in the negative are all pushing AWAY from it.
    `--pos-add` cannot un-say a word. A silent no-op would be the dangerous
    failure -- a rung recorded as "eye words removed" whose frame still had
    them -- so a term that is not in the clause is a hard stop, not a warning.
    """
    if not terms:
        return clause
    parts = [t.strip() for t in clause.split(",")]
    for term in [t.strip() for t in terms.split("|") if t.strip()]:
        if term not in parts:
            raise SystemExit("!! %s: cannot strip %r -- it is not a term in "
                             "%r" % (where, term, clause))
        parts.remove(term)
    return ", ".join(parts)


def emit(beat, rnd="p1", emotion=None, sample=False, priority=6, force=False,
         extra_keys=None, neg_add=None, ip_scale=None, ip_ref=None,
         pos_add=None, pose_override=None, pose_words_override=None,
         control_scale=None, seed=None, pos_strip=None, neg_strip=None):
    if beat not in C.WAVE:
        raise SystemExit("!! beat %r is not in the wave" % beat)
    pose, pose_words, default_emotion, stage = C.WAVE[beat]
    pose = pose_override or pose
    pose_words = pose_words_override or pose_words
    emotion = emotion or default_emotion
    stem = C.SKELETONS[pose]
    mask = C.head_box(pose)
    prompt = C.prompt_for(pose_words, emotion)
    if pos_add:
        # Inserted into the IDENTITY half, before the emotion and the pose, so
        # the pose and location stay at the tail where CLIP-77 protects them.
        prompt = prompt.replace(C.IDENTITY, C.IDENTITY + ", " + pos_add, 1)
    negative = C.NEGATIVE + ((", " + neg_add) if neg_add else "")
    prompt = _strip_terms("%s prompt" % beat, prompt, pos_strip)
    negative = _strip_terms("%s negative" % beat, negative, neg_strip)
    ip_scale = ip_scale or C.IP_SCALE
    control_scale = control_scale or C.CONTROL_SCALE
    seed = seed or C.SEED
    ip_ref = ip_ref or C.IP_REF
    ip_ref_sha = C.REF_SHA[ip_ref]

    new_id = "ep2-b%02d-canon-%s-0821" % (beat, rnd)
    job_dir = "b%02dcanon-%s-0821" % (beat, rnd)

    # CLIP-77, MEASURED PER SPEC, not trusted from the module's selftest. A
    # caller may pass an --emotion the cross-product never covered.
    n_pos = _clip77("%s prompt" % new_id, prompt)
    n_neg = _clip77("%s negative" % new_id, negative)

    extra = {
        "ip_adapter": dict(C.ip_adapter_block(pose),
                           ref="%s/%s.png" % (C.ASSET_DIR, ip_ref),
                           ref_sha256=ip_ref_sha, scale=ip_scale),
        "stage_direction": stage,
        "bar": BAR,
        "word_side_strips": (
            "positive -%s ; negative -%s" % (pos_strip or "nothing",
                                             neg_strip or "nothing")),
        "the_one_variable": (
            "THE BEAT -- its skeleton pose (%s) at head_frac %.3f, its pose "
            "words, its emotion (`%s`) and the mask that skeleton implies. The "
            "recipe, the reference and the proportion are the sample's and are "
            "identical across the wave, so a frame that misses is attributable "
            "to the beat." % (pose, C.HEAD_FRAC, emotion)),
        "the_rung_this_is_one_variable_from": (
            "NOTHING -- this is not a rung. The reference image changed, so "
            "holding one variable would be theatre. It is a wholesale recipe "
            "change and it is being run the way the rule says: ONE SAMPLE "
            "(beat %02d) judged at 1:1 before anything is scaled."
            % C.SAMPLE_BEAT),
        "one_sample_rule": (
            "ONE FRAME, AND IT IS BEAT %02d, for the two reasons the age-B wave "
            "spent its sample there: it is the frame the founder pointed at "
            "when he said the goblin reads as an adult, and it was the best "
            "pass of the adult wave's round one, so a break here is "
            "attributable to the new recipe and not to a marginal beat. "
            "NOTHING SCALES OFF IT UNTIL IT IS JUDGED BY EYE AT 1:1."
            % C.SAMPLE_BEAT),
        "round_2_lever": (
            "NAMED BEFORE THE RENDER so round two is a decision and not a "
            "brainstorm, in the order they will be reached for:\n"
            "  1. SKIN GOES HUMAN -> put `pale skin, grey skin` back in the "
            "negative. They were struck today and it is the weakest of the "
            "strikes.\n"
            "  2. PUPIL COMES BACK TOO LARGE -> add `constricted pupils` to the "
            "positive. It was drafted in and cut by the CLIP-77 budget; there "
            "are 3 spare tokens.\n"
            "  3. FIGURE COMES BACK TOO TALL -> drop `child, chibi` from the "
            "negative. They are kept under protest and are in tension with a "
            "2.71-head brief.\n"
            "  4. EARS COME BACK SMALL -> raise IP_SCALE from 0.7, or rebuild "
            "the reference at head-frac 0.25 (already on disk, sha in the "
            "module). The ear is geometry the adapter carries, not a word.\n"
            "One at a time, in that order, and each is one spec."),
        "clip77_measured_not_estimated": (
            "positive %d of 77, negative %d of 77, counted with "
            "animagine-xl-3.1's OWN vocab by pipeline/clip_token_count.py. The "
            "first draft of the identity clause measured 84-90 and the tail it "
            "was dropping was THE POSE AND THE LOCATION on all seven beats."
            % (n_pos, n_neg)),
        "supersedes": (
            "ep2-b%02d-ageb-{p1,r2}-0821 on the DESIGN axis. Those frames are "
            "the wrong character as of 16:54 today and are kept as evidence. "
            "This job does not delete or re-file them." % beat),
        "post_ship_patch": (
            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. A plate here is a "
            "candidate; a candidate becomes a pick, a pick becomes a motion "
            "spec, and only a passing motion take is swapped -- four "
            "judgements, none of them this job's."),
        "founder_ruling_verbatim": "dude, this is how the goblin should look",
    }
    if beat == 7:
        extra["guard_absence_warning"] = (
            "BEAT 07 IS THE CONFISCATION AND THIS PLATE HAS NO GUARD IN IT ON "
            "PURPOSE -- it is the goblin's plate and the guards are a separate "
            "cast with their own approved sheet. CARRIED FORWARD FROM THE "
            "FALLBACK LANE'S 14-CLIP RECORD: b07's MOTION drew no guard on "
            "either seed, so the confiscation action was simply absent from the "
            "clip. That is the prompt-summons law -- a subject that is not "
            "PLACED in the wording is not drawn. When this plate's motion spec "
            "is written it MUST name the guard as a placed subject in frame, or "
            "beat 07 will come back empty a third time.")
    extra.update(extra_keys or {})

    overrides = {
        "argv:--control": "pipeline/control/%s.png" % stem,
        "argv:--control-sha256": C.SKELETON_SHA[stem],
        "argv:--ip-ref": "pipeline/control/%s.png" % ip_ref,
        "argv:--ip-ref-sha256": ip_ref_sha,
        "argv:--ip-mask": mask,
        "argv:--ip-scale": ip_scale,
        "argv:--repo-commit": C.ASSET_COMMIT,
        "argv:--scale": control_scale,
        "argv:--seed": str(seed),
        "payload:prompt.txt": prompt,
        "payload:negative.txt": negative,
        "key:beat": int(beat),
        "key:node": NODE,
        "key:priority": priority,
        "key:est_minutes": 4,
        "key:sample": bool(sample),
    }
    child = derive_spec.derive(
        src=PARENT, new_id=new_id, fresh=_fresh(beat, rnd, sample),
        overrides=overrides, retoken=[(PARENT_DIR_TOKEN, job_dir)],
        extra=extra, by="pipeline/derive_jerry_canon_0821.py")

    child["steps"][0] = {"name": "stage",
                         "argv": [PY, "-c",
                                  C.stage_step(job_dir, stem, ip_ref)]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [PY, "-c",
                                   C.publish_step(job_dir, new_id,
                                                  stem, ip_ref)]}
    child["artifacts"] = [r"C:\banyan-farm\%s\out\%s-%s.png"
                          % (job_dir, new_id, C.ARM)]

    # ---- every flag the frame is conditioned on, asserted on the EMITTED argv.
    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    for flag, want in (("--control", "pipeline/control/%s.png" % stem),
                       ("--control-sha256", C.SKELETON_SHA[stem]),
                       ("--ip-ref", "pipeline/control/%s.png" % ip_ref),
                       ("--ip-ref-sha256", ip_ref_sha),
                       ("--ip-mask", mask),
                       ("--ip-scale", ip_scale),
                       ("--ip-weight", C.IP_WEIGHT),
                       ("--scale", control_scale),
                       ("--seed", str(seed)),
                       ("--arm", C.ARM),
                       ("--task", new_id)):
        if argv.count(flag) != 1:
            raise SystemExit("!! %s: %s appears %d times"
                             % (new_id, flag, argv.count(flag)))
        got = argv[argv.index(flag) + 1]
        if got != want:
            raise SystemExit("!! %s: %s is %r, want %r"
                             % (new_id, flag, got, want))

    joined = repr({k: v for k, v in child.items() if k != "derivation"})
    if PARENT_DIR_TOKEN in joined:
        raise SystemExit("!! %s still names the parent job dir" % new_id)
    if C.IP_WEIGHT_SHA not in joined:
        raise SystemExit("!! %s does not record the adapter digest" % new_id)
    # THE FIVE STRUCK TAGS MAY NOT COME BACK IN THE POSITIVE. Every one of them
    # was in the frozen k6a string this morning, so the failure mode is a
    # copy-paste, not a decision, and a guard is the only thing that catches it.
    pay = child["payload"][r"C:\banyan-farm\%s\prompt.txt" % job_dir]
    for dead in ("blank eyes", "thick eyebrows", "patchwork", "cloak",
                 "adult", "half-closed eyes",
                 # ADDED 2026-08-22, and they were REQUIRED here this morning.
                 # Both name the pupil; on animagine both draw a large rendered
                 # iris, which is the eye the founder vetoed the whole w2 sweep
                 # for. r12d reaches his eye with `eyebags, jitome` and no pupil
                 # word at all, so these two may not come back by copy-paste.
                 "slit pupils", "constricted pupils"):
        if dead in pay:
            raise SystemExit("!! %s: struck tag %r is back in the positive "
                             "-- the founder's image has none of it" % (new_id,
                                                                        dead))
    # ...and the ones that MUST be there, for the same reason inverted.
    #
    # `slit pupils` LEFT THIS LIST ON 2026-08-22 AND IT WAS THE FOUNDER WHO
    # TOOK IT OUT. It was required here because his image plainly shows a tiny
    # dark pupil on an off-white field and the tag is booru's nearest name for
    # that. It is not: on animagine `slit pupils` draws a LARGE iris with a
    # slit through it, and a large iris is exactly the thing he vetoed the
    # whole w2 sweep for ("that aint my goblin"). A required tag that produces
    # the vetoed frame is not a guard, it is the defect with a test around it.
    # The eye now comes off the adapter (see the sq65 note in jerry_canon_0821)
    # and round nine's rungs strip the word side to zero so the two stop
    # competing. `pointy ears` and `mandarin collar` stay required: both are
    # silhouette, both survived every round, and neither is contested.
    for live in ("pointy ears", "mandarin collar", "eyebags", "jitome"):
        if live not in pay:
            raise SystemExit("!! %s: %r is not in the positive" % (new_id, live))
    if pose_words not in pay:
        raise SystemExit("!! %s: the pose and location are not in the positive"
                         % new_id)

    out = "pipeline/jobs/%s.yaml" % new_id
    derive_spec.write(child, out, force=force)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out),
        must_hold=(C.DRIVER, stem + ".png", ip_ref + ".png"))
    print("wrote %s\n   skel=%-26s mask=%-19s clip77=%d/%d\n   +  %s"
          % (out, stem, mask, n_pos, n_neg, pay))
    return out


def _clip77(label, text):
    import clip_token_count as clip
    c = clip.Clip()
    n = c.count(text)[0] + clip.SPECIALS
    if n > clip.CEILING:
        raise SystemExit("!! %s is %d of %d -- the tail would be DROPPED and "
                         "the tail is the pose and the location" % (label, n,
                                                                    clip.CEILING))
    return n


def _sample_judged():
    """The wave is gated on a verdict key existing on the sample's spec."""
    import yaml
    p = os.path.join(REPO, "pipeline/jobs/ep2-b%02d-canon-s1-0821.yaml"
                     % C.SAMPLE_BEAT)
    if not os.path.isfile(p):
        return False, "the sample spec %s does not exist yet" % os.path.basename(p)
    with open(p, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    key = [k for k in spec if k.startswith("verdict")]
    if not key:
        return False, ("%s carries no `verdict*` key -- the sample has not been "
                       "judged by eye at 1:1, and ONE SAMPLE BEFORE ANY BATCH "
                       "means the batch waits" % os.path.basename(p))
    return True, "judged: %s" % key[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--wave", action="store_true")
    ap.add_argument("--beat", type=int)
    ap.add_argument("--round", default="p1")
    ap.add_argument("--emotion")
    ap.add_argument("--neg-add", help="appended to the negative")
    ap.add_argument("--pos-add", help="appended to the IDENTITY clause")
    ap.add_argument("--pos-strip", help="pipe-separated terms DELETED from the "
                                        "positive; absent term = hard stop")
    ap.add_argument("--neg-strip", help="pipe-separated terms DELETED from the "
                                        "negative; absent term = hard stop")
    ap.add_argument("--ip-scale")
    ap.add_argument("--ip-ref")
    ap.add_argument("--pose", help="skeleton pose override (a rung lever)")
    ap.add_argument("--pose-words", help="pose+location clause override")
    ap.add_argument("--control-scale", help="ControlNet scale (a rung lever)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--commit", help="the asset commit to pin as --repo-commit")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if a.commit:
        C.ASSET_COMMIT = a.commit
    if not C.ASSET_COMMIT:
        raise SystemExit("!! pass --commit <sha> -- the spec pins the commit "
                         "the assets are fetched from and there is no default")

    if a.sample:
        return 0 if emit(C.SAMPLE_BEAT, rnd="s1", sample=True, priority=9,
                         force=a.force) else 1
    if a.wave:
        ok, msg = _sample_judged()
        if not ok:
            raise SystemExit("!! REFUSING THE WAVE: %s" % msg)
        print("sample gate: %s" % msg)
        for beat in sorted(b for b in C.WAVE if b != C.SAMPLE_BEAT):
            emit(beat, rnd=a.round, force=a.force)
        return 0
    if a.beat:
        emit(a.beat, rnd=a.round, emotion=a.emotion, force=a.force,
             neg_add=a.neg_add, pos_add=a.pos_add, ip_scale=a.ip_scale,
             ip_ref=a.ip_ref, pose_override=a.pose,
             pose_words_override=a.pose_words,
             control_scale=a.control_scale, seed=a.seed,
             pos_strip=a.pos_strip, neg_strip=a.neg_strip)
        return 0
    ap.error("pass --sample, --wave or --beat N")


if __name__ == "__main__":
    sys.exit(main())
