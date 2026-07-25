#!/usr/bin/env python3
"""Which stage directions reach the viewer, and for how long.

Pure text rules, no audio dependencies — `synth_vo.py` needs numpy and
soundfile, and these rules need to be testable in CI without them.

The tree has no mouth. Its answers ARE stage directions ("One leaf tilts."), so
those have to reach the screen and own a beat of silence the viewer reads.
Cycle 006 got that right and implemented it as a blocklist of camera words,
which is the wrong shape: the list held `close-up` but not `close on`, and said
nothing at all about scenery or about other characters' business, so it admitted
258 of the genome's 271 directions. Every admitted one took 3.6-4.5s of silent
track with a caption nobody speaks — "no sound for like 3 seconds straight
staring at the random ai animation" and "this is literally just the script being
put as dialogue", both founder, both traced back here.

So it is an allowlist, and the tree has to be the SUBJECT. Naming a leaf is not
enough: "He holds the fig up beside the bare branch it fell from" is the
goblin's business, and "The sun arcs overhead three times as one new leaf
unfurls from a bud" is a timelapse. Everything that does not survive is already
described to the renderer in `shots.md`, which is where it belongs.
"""

import re

ACTION_MAX_WORDS = 14   # stage directions this short can become on-screen beats
ACTION_MIN_HOLD = 1.4   # seconds a displayed gesture owns the track
ACTION_MAX_HOLD = 2.2   # past this a silent hold reads as a stalled video

TREE_PART = r"(leaf|leaves|branch|branches|crown|canopy|bough|frond)"
GESTURE = (r"(tilts?|tilting|dips?|nods?|curls?|shivers?|trembles?|lifts?|rises?|"
           r"drops?|holds?|stills?|straightens?|turns?|folds?|unfurls?|"
           r"twitch(?:es)?|angles?|leans?|draws? in)")
CAMERA_WORDS = (r"\b(camera|frame|framing|shot|close-?up|close on|wide|extreme|macro|"
                r"montage|cut to|we see|insert|pov|angle on|pull (?:in|out)|"
                r"push (?:in|out)|pan|zoom|underground|cross-?section)\b")
NOT_THE_TREE = (r"^(he|she|they|his|her|the (?:goblin|scavenger|farmer|magistrate|"
                r"assessor|pilgrim|stranger|man|guard\w*)|guard \d|the (?:sun|moon|"
                r"wind|sky|grass|light|water|field)|dawn|wind|moonlight|sunrise)\b")


def is_beat_pause(action_text: str) -> bool:
    """A bare 'Beat.' is a rest, not a line and not a caption — it becomes the
    next line's breath (cycle-001 defect 14: the render dropped it entirely)."""
    return bool(action_text) and action_text.strip().rstrip(".").lower() in ("beat", "a beat")


def displayable_action(action_text):
    """The tree's own gesture, or None."""
    t = action_text.strip()
    if not t or is_beat_pause(t):
        return None
    first = re.split(r"(?<=[.!?…])\s+", t)[0]
    if re.search(CAMERA_WORDS, first, re.I):
        return None  # production language, not story
    if len(first.split()) > ACTION_MAX_WORDS:
        return None  # a paragraph is camera direction
    if re.match(NOT_THE_TREE, first.strip(), re.I):
        return None  # someone else's business, or the weather
    if not re.search(TREE_PART, first, re.I):
        return None  # not the tree at all
    if not re.search(GESTURE, first, re.I):
        return None  # the tree is present but not answering
    return first


def action_hold(text: str) -> float:
    """Seconds a displayed gesture owns.

    Capped: the gesture is a beat of silence the viewer READS, and past a couple
    of seconds a silent hold stops reading as a pause and starts reading as the
    video having stalled (founder, 2026-07-23)."""
    return min(ACTION_MAX_HOLD, max(ACTION_MIN_HOLD, 0.28 * len(text.split()) + 0.6))
