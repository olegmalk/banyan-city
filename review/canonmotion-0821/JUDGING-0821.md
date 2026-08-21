# canonmotion tranche — judging log, 2026-08-21
# Bar: M1 face drawn every frame · M2 identity holds · W1 wardrobe + waist
# boundary · W2 no cloak/hood · A1 action completes inside the slot · C1 locked
# frame · C2 one subject (two on b07).
# Judged by eye off SHEET-bNN.png at 1:1. No metric decided anything.

b13  PASS 6/7, A1 marginal.
  M1 pass  no dissolve anywhere in 105 frames. The prior wave's b13 s1 egged at
           f065; this one has brow, eyes, nose and mouth drawn at f104.
  M2 pass  same creature f000->f104. Ears large, lateral, pointed. Slit pupil
           visible whenever the lids are open.
  W1 pass  mandarin collar + frogging, shirt over dark shorts, waist boundary
           intact. No merge.
  W2 pass  no cloak, no hood, no patch.
  A1 MARGINAL  the head-tip starts ~f072 and is still travelling at f096, the
           last frame a 97-frame trim keeps. It resolves at ~f104, OUTSIDE the
           slot. done_when says "the head-tip completes" -- inside the slot it
           reads as begun, not completed.
  C1 pass  horizon and grass stationary.
  C2 pass  one figure.
  note     the eyes CLOSE from ~f048 and stay closed. Defensible for
           "exhaustion resolving into relief", but the canon eye -- the whole
           point of the founder's image -- is only legible for the first 2 s.

b08  PASS 7/7, with a legibility cost that is his call.
  M1 pass  AND THIS IS A CORRECTION TO MY OWN FIRST READ. A tight head crop
           made f055+ look like the green egg. A taller crop shows the features
           ARE drawn -- eyes, nose and blush sit as a foreshortened sliver at
           the bottom edge of the head. What fills the frame is the CROWN of a
           bowed bald skull, which is what a front camera sees when the beat is
           "he looks down at his own belly".
  M2 pass  cel shading and colour hold. Contrast the prior 121-frame b08 seed 1
           (review/motion-ageb-0821/08-inside-him-LTX-ep2-b08-tilemotion-s1-
           0821.mp4): there the head goes uniformly bright yellow-green with a
           specular highlight and NO features while sitting roughly upright.
           That was a real dissolve. This is not the same event.
  W1 pass  collar, frogging, olive shirt, dark shorts, pale cuffs, boots. The
           waist boundary survives the whole clip -- the b08 garment-merge
           fault did not recur.
  W2 pass  none.
  A1 pass  hands reach the belly by f048, head bowed by ~f057 -- completes
           EARLY, as the done_when asked, well inside the 97-frame trim.
  C1 pass  top-corner change 0.9; background grass identical f000 vs f104.
  C2 pass  one figure.
  cost     from ~f057 to the end, over half the clip is the top of his head.
           Reads as "looking down"; his face is small. TASTE, not defect.

b02  FAIL, C1 and A1. The pre-registered init/action conflict fired exactly.
  C1 FAIL  the frame does not hold. Between f024 and f048 the camera pulls back
           hard: he goes from filling the frame to a figure a few percent of
           its height, and by f104 he is a speck at the bottom right of a wide
           shot. Subject scale changes roughly 5x.
  A1 FAIL  no sprint, no skid, no dive. He drifts AWAY from camera.
  world    the location is replaced. f000 is tall grass; from f048 the frame is
           dominated by a large bare black tree against pale sky.
  M1/M2    features are drawn while he is large and are simply too small to
           score after f048. Not an identity finding -- a staging one.
  C2 pass  one goblin, plus the small creature at his boots that the plate
           sheet already discloses as a known b02 plate fault.
  CAUSE, and it was filed before the render: the action clause asks him to run
  INTO frame and drop behind "a thin sapling trunk". He is already in frame at
  f000 -- an init frame IS frame zero -- and the canon b02 plate contains NO
  trunk, because the beat's own stage direction is that he has not seen the
  sapling yet. Handed a prop that is in none of its pixels, LTX did not ignore
  the word: it BUILT the tree and pulled the camera back far enough to fit the
  run and the trunk into one shot. Naming a prop absent from the init is a
  re-staging instruction on this recipe, not a detail request.
  next rung is PLATE-SIDE: a b02 plate that already contains the sapling trunk,
  or an action that only uses what the plate holds. Not a reworded prompt.

b03  FAIL, M2 and C1. Same root cause as b02.
  M1 pass  features stay drawn the whole 105 frames -- eyes, nose and mouth are
           legible even at f104. No dissolve.
  M2 FAIL  a curved pointed horn / topknot grows out of the crown of a BALD
           canon head from about f072 and is still there at f104. The canon
           goblin is bald with no crest; this is a new appendage, not a
           lighting read.
  W1 ~     collar and shirt hold while he is large; by f096 he is small enough
           that the waist boundary cannot be scored honestly. Not called.
  W2 pass  no cloak, no hood.
  A1 FAIL  "crouches low behind the thin trunk and holds still, eyes flicking
           sideways" -- THERE IS NO TRUNK IN FRAME AT ANY POINT. He does sink
           lower, so the pre-registered freeze risk did NOT fire; what fired
           instead was the b02 fault.
  C1 FAIL  the camera pulls back from ~f072; subject height roughly halves by
           f104. Quieter than b02 but the frame does not hold.
  C2 pass  one figure.
  THE PATTERN, and it is now two for two: b02 and b03 are the two beats whose
  action names a "thin sapling trunk", and NEITHER PLATE CONTAINS ONE -- the
  plate sheet already discloses that for b03 ("beat 03 has no trunk to hide
  behind"). Both re-staged: both pulled the camera back, and b02 built the tree
  outright. On this recipe a prop named in the prompt but absent from the init
  is read as an instruction to RE-STAGE THE SHOT. The fix is plate-side.

b04  PASS 6/7, A1 marginal -- and it is the most encouraging clip in the wave.
  M1 pass  features drawn all 105 frames. No dissolve.
  M2 pass  bald, large lateral pointed ears, off-white eyes with slit pupils,
           green skin, all held f000 -> f104.
  W1 pass  mandarin collar + frogging, olive shirt, dark shorts, laced boots,
           waist boundary present throughout.
  W2 pass  none.
  A1 MARGINAL, but on the right side of the line. THERE IS AN OUT-AND-BACK:
           he leans out and across from ~f024, is fully extended f048-f072,
           and is back upright by f096 -- INSIDE the 97-frame trim, so the
           pull-back, which is the joke, lands in the slot. This is the motion
           the beat needs and it is the motion TWO PLATE ROUNDS FAILED TO DRAW,
           so the "ask the motion model for the lean" bet paid. What it is not
           is a peek: with no trunk in frame there is nothing to lean out from
           or hide behind, so it reads as a stumble-and-recover.
  C1 pass  frame holds. Top-corner change 1.9; background grass stationary and
           subject scale constant -- notably NOT the b02/b03 pull-back, even
           though this beat's prop is also missing.
  C2 pass  one figure.
  note     b04 names no prop in its action clause ("leans out sideways from
           behind the trunk" is in the beat, but the clause the model got is
           dominated by the body verbs). It is the one missing-prop beat that
           did not re-stage, which is consistent with the b02/b03 reading: it
           is NAMING the absent prop that moves the camera, not missing it.

b07  FAIL on the beat -- but the pre-registered prediction was WRONG, and that
     is the most useful thing in the tranche.
  THE GUARD ARRIVED. I filed "I expect no guard" and named a two-figure plate
  as the next rung. From f024 a tall armoured guard in a helmet stands at the
  right, facing him, and he is there for the rest of the clip. Both prior
  seeds at 121 frames drew NO guard at all. So i2v DID place a second figure
  from wording alone on an init that contains one -- what changed is that the
  wording placed BOTH figures before asking anything of either, AND the four
  second-figure terms (second face, second goblin, two goblins, crowd) were
  struck from the negative. A prompt cannot summon what its own negative
  removes; with the negative fixed, it summoned.
  A1 FAIL, but the failure MOVED. The point happens -- the guard's arm comes up
     f072 and is fully extended and aimed by f096. THE GOBLIN IS GONE BY f096.
     f096 and f104 are the guard pointing at empty grass. The beat is
     "Guard 1 points at the scavenger"; there is no scavenger at the moment of
     the point.
  C2 FAIL  two figures f024-f072, then one -- and it is the wrong one.
  C1 FAIL  the camera pulls back between f000 and f024 to fit the second figure
     in. Same re-staging as b02 and b03, same cause: something named in the
     prompt is not in the init, so the shot is rebuilt to accommodate it.
  M1/M2 pass while he is present -- bald, lateral pointed ears, off-white eyes
     with slit pupils, green skin, no drift toward a human face.
  W1/W2 pass while present.
  next rung is now a TWO-FIGURE PLATE for a different reason than I filed: not
  because wording cannot summon the guard -- it can -- but because a plate with
  both figures already staged removes the re-stage AND gives the goblin a
  reason to still be there at the end.

b20  FAIL, A1 -- the same failure as the take it was meant to replace.
  A1 FAIL  HE NEVER LOOKS UP. The done_when is "the LOOK UP completes -- the
           outgoing take never did it", and this take does not do it either.
           A branch enters at the top right from ~f048 and he never turns to
           it; his head and eyes stay level at the camera for all 105 frames.
  freeze   the pre-registered end-state-plate risk FIRED HERE. Between f000 and
           f104 the pose barely changes. This is close to a still with a
           runtime, which is a mistake this tree has shipped before.
  M1 pass  features drawn all 105 frames.
  M2 pass  bald, large lateral pointed ears, off-white sclera with vertical
           slit pupils, green skin. Clean identity, arguably the cleanest face
           in the wave.
  W1 pass  collar, frogging, olive shirt, pale sleeves, dark shorts, boots,
           waist boundary intact.
  W2 pass  none.
  C1 MARGINAL  slight pull-back: he shrinks a little and the branch arrives.
           Much quieter than b02/b03 but the frame is not locked.
  C2 pass  one figure.
  canon    the fruit is YELLOW-GREEN. Canon has the fig PURPLE. The outgoing
           take had it RED, so this is the same fault in a new colour, carried
           by the plate rather than introduced by the motion.

================================================================================
ROUND 2 — the plate-fix wave, 2026-08-21
================================================================================
# THE LAW ROUND 1 MEASURED: a prompt naming an object ABSENT from the init makes
# the model build the object and pull the camera back to fit it. Round 1 failed
# on exactly the four beats whose prompts named something the plate lacked (02
# and 03 the trunk, 20 the branch, 07 the guard) and passed on the three that
# asked only for motion the plate had a body for (04, 08, 13).
#
# ROUND 2 CHANGED ONE THING: the init. b02/b03/b20 got the scripted object
# composited onto the same canon w2 plate and drawn in by a 0.30 masked i2i
# (pipeline/derive_ep2_sapnat_0821.py); b07 got a two-figure openpose plate
# (pipeline/derive_b07_twofig_0821.py). Every sampler number is round 1's.
# Motion re-filed by pipeline/file_canonmotion_r2_0821.py.
#
# Clips + plates: branch farm-results-rtx5090, farm-out/ep2-bNN-*-r2-0821/.
# Rebuild any sheet with:
#   ffmpeg -i <clip>.mp4 -vf "select=eq(n\,F)" -vframes 1 fNNN.png   (F = 0 24 48 72 96 104)
#   python3 pipeline/compare_sheet.py OUT.png "<title>" "f000"=f000.png ...

THE PLATES (all four rc=0; judged before any motion was filed)
  b02 sapnat  PASS  trunk drawn in, not moved, he untouched
  b03 sapnat  PASS  ditto — and the stem crosses his chest, which is the joke
  b20 sapnat  PASS  branch beside him AND the fig recoloured to canon purple
  b07 twofig  FAIL after 2 rounds — see below. No motion filed off it.
  measured on landing: mean |delta| INSIDE the drawn region 10.2–14.2 (really
  redrawn), OUTSIDE it 0.024–0.055 (the goblin untouched), plant centroid moved
  0.1–5.4 px on 832x1216 (it did not move).

b02  3/4 — R3 FAIL. THE CAMERA HELD.
  R1 pass  no pull-back at all. Round 1 ended with him "a speck at bottom right
           of a wide shot dominated by a large bare tree that is in no plate";
           none of that happens. Three constant-scale references hold in every
           frame — the small green critter at bottom centre, the sapling's stem
           and leaves, the grass-blade stroke width.
  R2 pass  the sapling is there for 105 frames and NO tree is ever built.
  R3 FAIL  no sprint and no skid. He drifts back and left, is behind the stem
           around f060, and bends over by f096. Timing is inside the slot; the
           SHAPE of the move is wrong.
  R4 pass  features every frame, collar + frogging hold, no new appendage.
  metric   eye-separation is DISQUALIFIED on this beat — he leaves centre, so
           from ~f048 it measures grass, not eyes (left/right dark-pixel split
           goes 6081/7910 at f000 to 3060/12790 at f096). Do not quote it here.

b03  2/4 — R1 MARGINAL, R3 FAIL. THE HORN IS GONE, THE COVER EXISTS.
  R1 MARGINAL  still recedes, by half as much. Eye separation (valid here — he
           stays centred and fully in frame): 339.7 px f000 → 246.9 px f104,
           monotonic, 73%. Round 1 was "his height roughly halves", ~50%.
  R2 pass  trunk present all 105 frames, no tree. Round 1 drew no trunk at all,
           so "the beat's cover does not exist" is fixed.
  R3 FAIL  the pre-registered "still with a runtime" fired. No crouch, no
           sideways eye flick; the only event is his eyes closing from ~f096.
  R4 pass  AND THE ROUND-1 HORN IS GONE — nothing grows from the crown.

b20  3/4 — R3 FAIL. BOTH PLATE-CARRIED FAULTS CLEARED.
  R1 pass  scale constant, frame locked. Round 1 was "slight pull-back".
  R2 pass  NO rogue branch enters. The composited sapling stands at frame right
           at his eye line for the whole clip.
  fig      PASS — PURPLE in every frame. Round 1 had it yellow-green, the
           outgoing take red. Recolour survived naturalize AND motion.
  R3 FAIL  the LIFT now happens (fig from lap at f000 to chin height by f048,
           both hands) — that is new, and the freeze risk did NOT fire. But he
           still NEVER LOOKS UP: head level, eyes on camera, all 105 frames.
  R4 pass  clean.

b07  PLATE FAILS AFTER TWO ROUNDS. NO MOTION FILED.
  R1  guard PASS and emphatic — five heads, full plate, helmeted, a head and a
      half taller: the founder's "dumb grown men" in pixels. No adapter leak.
      Goblin FAILS on the eyes: large round green eyes, not canon slit pupils.
      Suspected the IP mask; DREW IT ON THE OUTPUT and the box is correct — it
      holds the whole skull, both ears and the face. Killed that hypothesis for
      one composite instead of a round of GPU.
  R2  the eye clause WORKED — narrow vertical slit pupils on off-white sclera,
      and a better collar. But it regressed three ways: palette went warm (blue
      sky, gold armour), a hard-edged rectangular IP-MASK HALO appeared around
      the goblin, and the guard's pointing hand came back as GREEN GOBLIN SKIN
      aimed upward. All three trace to one mistake — this lane dropped `muted
      color` and `boots` to buy eye tokens, arguing round 1 proved them not
      load-bearing. Round 1 proved the opposite: they came back correct BECAUSE
      those terms were there. The halo is the palette split drawing the mask
      boundary, not a mask fault.
  ROUND 3 (founder's call): keep the eye clause verbatim, restore `muted color`
      and `boots`, buy the ~5 tokens from the GUARD clause — openpose already
      carries his pose and stature — or raise ip-scale instead of spending
      positive tokens.

WHAT THE WAVE NOW KNOWS, AND IT IS TWO LEVERS AND NOT ONE
  THE PLATE FIXES THE CAMERA. Every camera/invention fault round 1 blamed on a
  missing object cleared or halved when the object was composited in, with all
  sampler numbers held: b02 pull-back gone, b20 pull-back gone and the rogue
  branch gone, b03 halved, and the invented tree never appears again.
  THE PLATE DOES NOT BUY THE ACTION. All three still fail R3, each differently
  — b02 has the wrong shape of move, b03 has almost none, b20 does the lift but
  not the look. Beats asking for travel hold their frame; beats asking for
  stillness still drift. That is an action-wording / motion-strength question,
  a different lever, and it is NOT opened here: two rounds is the budget.
  NOTHING IN review/ep2-ship-0821 WAS TOUCHED. No cut moved. No swaps.

--------------------------------------------------------------------------------
b07 ROUND 3 — muted color + boots restored, tokens taken from the guard clause
--------------------------------------------------------------------------------
  K1 slit pupils  PASS  off-white sclera, narrow vertical slit pupils at 1:1.
  K2 collar       PASS  mandarin collar + frog closure, eyebags.
  P1 palette      PASS  muted sage back; blue sky / gold trim gone.
  P2 no halo      PASS  THE PRE-REGISTERED TEST CAME TRUE. R2's rectangle was
                        claimed to be a palette split across the mask boundary,
                        not a mask fault; restoring `muted color` with the mask
                        BYTE-IDENTICAL removed it. The IP mask is exonerated a
                        third time and ip-scale is not implicated by the halo.
  P3 guard hand   PASS  armoured gauntlet again, aimed down at him.
  P4 boots        PASS  dark boots, not sandals.
  G3/G4 guard     FAIL  the degenerate this spec named in advance: "unhelmeted
                        → the budget is the cause". He is unhelmeted AND his
                        head is a bare green goblin skull with pointed ears.
                        Stature and plate armour survived (openpose carries
                        those); the helmet and his species did not survive his
                        wording losing `city`, `in a helmet`, `facing him`.

THE THREE ROUNDS AS ONE RESULT — A TOKEN BUDGET, NOT A WORDING PROBLEM
  attribute            R1     R2     R3
  goblin slit pupils   FAIL   PASS   PASS
  muted palette        PASS   FAIL   PASS
  no mask halo         PASS   FAIL   PASS
  guard hand armoured  PASS   FAIL   PASS
  boots                PASS   FAIL   PASS
  guard helmeted human PASS   PASS   FAIL
  Every attribute has been achieved in some round and never all in one. Each
  round was a zero-sum reallocation of the same 77 CLIP tokens. The positive
  prompt provably cannot carry the founder's canon goblin identity in WORDS and
  enough guard description to keep him a helmeted human, on this checkpoint.

  NEXT LEVER (not opened — three rounds authorised, three spent): stop paying
  for the goblin's identity in tokens. The IP-Adapter reference already carries
  his face and the mask is verified correct three times over. Delete `white
  eyes, slit pupils, constricted pupils, eyebags, thin eyebrows` (~12 tokens)
  and raise ip-scale to compensate, freeing the whole budget for the guard.
  That is a RECIPE change, so it is one sample and its own question.

  BEAT 07 STANDING STATE: no plate passes on both figures; NO MOTION SPEC HAS
  BEEN FILED off any of the three rounds. R1 is the only round with a correct
  guard, R3 the only round with a correct goblin.
