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
