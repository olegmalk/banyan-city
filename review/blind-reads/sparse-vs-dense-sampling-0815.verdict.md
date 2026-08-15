# sparse-vs-dense-sampling-0815 — verbatim blind reader verdict

Recorded 2026-08-15. This is the cold reader's own report, copied unaltered — the
agent that wrote it WAS the reader, so this is first-hand, not a summary of one.
It had no project context, was told not to seek any, and was NOT told that the two
sets might be the same clip or what the experiment was testing.

Machine-readable summary, hashes, caveats and reproduction:
`review/blind-reads/sparse-vs-dense-sampling-0815.yaml`.

**What the sets were, which the reader did not know:**
SET ONE = the same 97-frame clip sampled every ~6th frame (the retired instrument).
SET TWO = the same clip again, as consecutive frames plus a whole-clip overview.

**The line this whole record exists for** is at the very end, under COMPARISON.

---

## The prompt the reader was given, verbatim

```
You are a COLD READER. You have NO context about any project and you must not seek any — do not read repository files, documentation, prompts, specs, or anything describing what these images are or what they were made for. Looking any of that up destroys the entire value of this report. You stand in for a stranger who is shown some frames and asked what happens.

You will look at TWO sets of frames, already generated and sitting on disk. **They may be from the same video or from different videos — you are not being told which, and you must not assume either way.** Judge each set on its own, in order, and only compare them at the very end.

SET ONE: `/private/tmp/claude-501/-Users-artovonkugler-banyan-city/51fa0eeb-78a4-44dd-a095-f8105ba56a73/scratchpad/read-control-oldstyle/`
SET TWO: `/private/tmp/claude-501/-Users-artovonkugler-banyan-city/51fa0eeb-78a4-44dd-a095-f8105ba56a73/scratchpad/read-control/`

Look at every image file in each directory with the Read tool. If a directory is empty or unreadable, say so plainly and move on — do not substitute anything else.

For EACH set, in its own section, answer:

**A. Describe what the frames show**, in order. Be concrete and physical.

**B. Is the movement CONTINUOUS or does it STEP?** This is the central question, so be precise. Does each frame follow smoothly from the one before it, or is there a point where the picture jumps — where two neighbouring frames do not look like consecutive moments of the same movement? If there is a jump, say between which frames and what changes across it.

**C. Over roughly how many frames does the main movement happen?** Give a number or a range, and say which frames you counted.

**D. Name the action in one sentence**, as you would to a friend. If you cannot name one, say so outright.

**E. Is anything about the framing or composition a problem?** For example: is the subject's face visible throughout, or does it become hidden? Does the shot end on something hard to read?

**F. Would a viewer think something happened, or that the video was broken or paused?**

THEN, at the very end, a short comparison:
- Do the two sets show the SAME movement, or different movements? Say what makes you think so.
- If your answers to question B differed between the two sets — one continuous, one stepping — say so explicitly and say which is which. **This is the single most important line in your report.**
- If one set gave you a clearer basis for answering than the other, say which and why.

Be blunt and concrete. Do not soften, do not hedge to be agreeable, and do not try to make the two sets agree if they don't. If you cannot tell something from what you were given, say that rather than guessing. Report only what you see.
```

---

## The verdict, verbatim

Both directories readable. Set one contains one file (`sheet.png`, a 16-frame contact sheet labelled "frame 1"–"frame 16"). Set two contains five files: `overview.png` (16 tiles labelled 000–096, sparsely sampled) plus `strip-01`–`strip-04` (consecutive frames 022–041, 042–061, 062–081, 082–086).

---

## SET ONE — `read-control-oldstyle/sheet.png`

**A. What the frames show**

A small child-sized figure with a large bald pale-tan head, long pointed ears, and grey-green shirt and trousers, standing in a sunlit grass field. Camera is roughly frontal, slightly above eye level.

- Frames 1–7: the figure stands facing camera, hands clasped together in front of the chest, face neutral, looking straight at us. Across these seven frames essentially nothing changes except a very slight widening of view and slight drop of the hands by frame 7. Frame 1 is washed out at the top by a bright flare.
- Frame 8: abruptly a different picture — the camera is now well above the figure looking down, and the figure is bent forward from the waist, hands lowered together toward the grass, face tilted up at the lens.
- Frames 9–11: the figure keeps folding forward and down. By 10 the face is angled down so only the eyes are barely visible; by 11 the crown of the head is toward the camera and the face is essentially gone. The soles/legs of the figure appear at the top of frame, meaning it is now doubled over almost head-to-ground.
- Frames 12–16: a held pose — the huge pale dome of the crown fills the lower-centre of the frame, two legs stick up behind it, two hands rest in the grass at the bottom. These five frames are near-identical; only the grass blades and a couple of floating specks shift slightly.

**B. Continuous or stepping? — It STEPS.**

Judged on this sheet alone, the movement does not read as continuous. Specific breaks:

- **Frames 7 → 8 is the big one.** Frame 7 is a figure standing upright, shot from the front at near eye level, hands at chest. Frame 8 is a figure bent double, shot from clearly above, hands near the ground, at a different scale and camera pitch. These do not read as two consecutive moments — a large amount of movement is missing between them.
- **Frames 9 → 10** jumps again: the face goes from visible-and-tilted to fully hidden, and the legs suddenly appear at the top of frame.
- **Frames 10 → 11** and **11 → 12** each also skip a visible chunk of the fold.
- Frames 1–7 and 12–16 are, by contrast, effectively frozen.

So the sheet reads as: freeze, freeze, freeze, freeze, freeze, freeze, freeze, **lurch, lurch, lurch, lurch, lurch**, freeze, freeze, freeze, freeze, freeze.

**C. How many frames does the movement occupy?**

About 5 of the 16 — frames 7/8 through 12. Frames 1–7 are static standing; frames 12–16 are a static held pose.

**D. Name the action**

The little goblin-kid bends all the way forward and puts his hands down into the grass — as if kneeling down to touch or pick something (or collapsing forward).

**E. Framing / composition problems — yes, serious ones.**

- The face is visible for frames 1–9 and then gone. From frame 11 onward the only thing we see of the head is a huge, featureless, pale flesh-coloured dome. It occupies a third of the frame.
- The shot ends there and holds for five frames. The final image is genuinely hard to read: a big beige oval with two shoes above it. I had to work to reconstruct that I was looking at the top of a bowed head, and I am not fully certain the figure is not simply lying face-down.
- The proportions at the end make the character read as a blob rather than a person.

**F. Would a viewer think something happened, or that it was broken?**

Something happened, but the delivery would read as broken or dropped-frame. A viewer would perceive a still image, then a sudden snap to a different shot, then another still image. The suspicion would be a stutter or a cut, not a movement.

---

## SET TWO — `read-control/` (overview + consecutive strips)

**A. What the frames show**

Same character and same field. Reading the consecutive strips:

- **022–038** (strip-01, rows 1–3 and most of 4): the figure stands facing camera, hands clasped at the chest. Over these ~17 frames almost nothing moves — the framing widens very slowly and the figure's hands and shoulders drift by a few pixels. The blinking/eye state is static.
- **039–041**: the hands unclasp and drop from chest height to belly height, palms turning over; the head begins to tip forward; the camera starts pitching up/over.
- **042–046**: the figure squats/leans forward, hands coming down toward the grass, camera continuing to rise above him. His head tilts progressively.
- **047–051**: he goes further down; hands reach into the grass at the bottom of frame; the face begins to angle away from us.
- **052–056**: the fold continues; at 054–056 the soles of both shoes come into view at the top of frame — he is now bent almost double.
- **057–061**: the crown of the head rotates fully toward camera, the face disappears entirely, the pose settles: head down in the grass, legs up behind, hands flat in the grass in front.
- **062–086** (strips 03 and 04): held. Twenty-five frames of the same doubled-over pose. What changes is small: the camera creeps very slightly, individual grass blades sway, a couple of pale specks drift. The figure itself does not move.
- The overview (000–096) confirms 000–038 is the standing hold and 062–096 the bowed hold; the entire movement lives in the middle.

**B. Continuous or stepping? — CONTINUOUS.**

Where I have consecutive frames, every frame follows smoothly from the one before it. I looked specifically for a break and did not find one:

- 038 → 039 → 040 → 041: the hands open and lower in even increments, the head tips a few degrees per frame.
- 044 → 045 → 046: the fastest part of the move — the head pitch changes most per frame here — but still each pair reads as consecutive moments of one gesture, not a jump.
- 052 → 056: the shoes rise into frame gradually, one appearing before the other.
- 057 → 061: the head rotation onto its crown is smooth.

The only thing that could be mistaken for a defect is the opposite problem: **long stretches where consecutive frames are indistinguishable** — 022–038 and 062–086. Those are holds, not jumps.

**C. How many frames does the movement occupy?**

Roughly **22–24 frames: 038 through 061**. Counted from strip-01 (038–041), strip-02 (042–061). Before 038 and after 061 there is no body movement. Against a clip that runs to at least 096, that means the action fills roughly a quarter of the running time and the rest is two static bookends — about 38 frames of standing still at the head and about 35 frames of held pose at the tail.

**D. Name the action**

He unclasps his hands, bends all the way forward, and reaches down into the grass, ending curled over with his head to the ground.

**E. Framing / composition problems — yes, the same ones, and now I can date them.**

- The face is legible up to about frame 051. From 057 onward it is gone for the rest of the clip — 30+ frames of nothing but the back/top of a bald head.
- The camera pitches up as he bends, which makes it worse: instead of following him down and keeping the face, it goes over the top of him.
- The final image the clip rests on for 25 straight frames is the least readable image in the whole set: a large beige dome with two shoe soles above it and two disembodied hands below it. Frames 082–086 are exactly that, unchanged.
- The 17-frame static opening is also a composition problem in its own right — the clip spends its first stretch on a portrait that isn't doing anything.

**F. Would a viewer think something happened, or that it was broken?**

Something happened — the movement itself, seen at full frame rate, would play as one clean fluid fold. But the front and back holds are long enough that a viewer could reasonably think the player was paused at the start and paused again at the end. The last quarter in particular, sitting on an unreadable shape without motion, is the kind of thing people scrub past thinking the video froze.

---

## COMPARISON

**Same movement, or different?** The **same movement, and almost certainly the same video.** Set one's 16 frames map one-for-one onto set two's 16 overview tiles: frame 1 has the identical top-of-frame white flare as tile 000, frames 5 and 6 match tiles 032 and 038, frame 8 matches 045, and frames 12–16 match 070/077/083/090/096 pose for pose, down to the grass detail. Set one is that sparse sampling and nothing else; set two is that same sparse sampling *plus* four strips of consecutive frames.

**Did my answer to B differ? YES, and this is the important line: SET ONE reads as STEPPING; SET TWO reads as CONTINUOUS.** Set one is the stepper — it appears to jump hard between frame 7 and frame 8 and again around 9–12. Set two is the continuous one. And set two explains set one: the strips contain the intermediate frames (039–056) that the contact sheet skips over, and those intermediates are smooth. **The stepping I saw in set one is an artifact of how thinly it was sampled, not something in the movement.** If I had only been given set one, I would have wrongly reported a broken or dropped-frame clip.

**Which gave a clearer basis?** **Set two, by a wide margin.** Consecutive frames are the only thing that can answer "does this step?" — a sheet sampling every 6th frame cannot distinguish a genuine jump-cut from a fast move, and in this case it actively misled me. Set two also let me measure the movement's duration (22–24 frames) and, just as usefully, measure the dead air around it (~38 frames before, ~35 after), which set one could only hint at. Set one's one advantage is that the whole clip fits on one page; but for the question asked, it is the wrong instrument.

One finding that survives both sets and is not a sampling artifact: **the clip loses the character's face partway through and then holds on an unreadable shape for its entire final quarter.**
