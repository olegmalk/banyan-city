# Node 002a — The Broken Channel

**Tree:** Sapling · **Parent:** [001 — Capability Inventory](../001-capability-inventory/node.md) · **Trunk:** undecided · **Status:** hot
**This file is a T0 leaf** (`002a-t0-b`, molt successor per SCRIPT-SPEC.md).
**Format:** 9:16 vertical · 60–90s · VO-driven

---

## State change (R1)

Three at once: the sapling performs his **first act on the world**
(rerouting water through a cracked channel); the farmer's field state
flips (dust → mud); and the world reveals it is **not inert** — the
system acknowledges his change.

## Hook (R5)

The system *responds* to him. Not a mood, a mechanism: he pushed a fix,
and something under the field pushed back an acknowledgment. The
question a viewer can state: *what is the system that just answered —
and what does it want with him?*

---

## Script

**COLD OPEN — 0:00–0:05**

Macro shot: a small young banyan tree at the edge of a field of
grey dust, trembling in a dry wind.

> **VO (dry, tired, engineer):** I died an engineer and woke up a tree. Two capabilities: sense, and grow. Today, a production incident found me anyway.

**THE FARMER — 0:05–0:22**

A FARMER (50s, sun-cracked, kind eyes gone flat) trudges into frame,
drops to his knees in the grey dust two paces from the sapling. He picks
up a handful of dirt. It runs out of his fist like ash.

> **FARMER (to the sky, hoarse):** Three seasons! Three seasons I've prayed, and you send the rain to Marn's field and the rot to mine! What do you *want* from me?!

> **VO:** He's cursing the gods. Classic misattribution. In my experience, when one house floods and the neighbor's burns, it's not theology. It's *plumbing.*

**THE DIAGNOSIS — 0:22–0:42**

The view dives underground: a glowing root-map of the field — the water
table, and cutting across it, an old irrigation channel rendered as a
bright conduit. Halfway along it: a crack. Water hemorrhages sideways,
flooding a low field on one side while the channel runs dry into the
farmer's field on the other.

> **VO:** There it is. Cracked channel, thirty meters west. Upstream: Marn's field, drowning. Downstream: this poor guy, desert. It's not a drought. It's a *routing bug*. Water takes the cheapest path — ask any incident review.

```
ROOT CAUSE: channel breach, sector W
IMPACT:     field A flooded / field B starved
FIX:        reroute. owner: me. eta: …oh no.
```

**THE FIX — 0:42–1:08**

Timelapse, the episode's centerpiece: one root grows west through dark
soil, day-strobe overhead. The cost shows — the sapling's young leaves
yellow at the edges as everything he has goes into one direction.

> **VO:** Growth budget: all of it. Cancel the new leaves. Cancel the height. One root, thirty meters, toward the crack. My deploy speed is measured in seasons, and I'm the only engineer in the region.

The root arrives at the breach, wedges into the crack, and *drinks* the
leak — wicking the overflow along its own length back toward the dry
field. A thin dark thread of moisture creeps through the grey dust like
ink.

The FARMER, days later in the timelapse, stops mid-curse. Kneels.
Presses his palm flat into the dirt. It's *damp*. He looks around — no
rain, no clouds — nothing but a scrappy little sapling he could swear
was smaller last week.

> **FARMER (whisper):** …Marn? You seeing this?

**THE RESPONSE / HOOK — 1:08–1:25**

Underground view. The moisture thread flows steady. The sapling settles,
spent.

> **VO:** Patch deployed. Fields rebalancing. And nobody will ever know it was—

The channel *pulses* — not the water, the **channel itself**: a slow
wave of light runs the conduit's full length, passes *through* his root
at the breach, and the flow adjusts — precisely, deliberately — matching
the exact draw of his fix.

> **VO (very quiet):** …That wasn't physics. Physics doesn't *acknowledge receipt*.

The pulse comes again. Brighter. Aimed at him.

SMASH TO BLACK.

```
200 OK
```

---

## Provenance

Molt successor script (`t0-b`), steward-written (model: claude-fable-5)
to `SCRIPT-SPEC.md` from `leaves/002a-seed.md` (verbatim founding text)
and committed node 001. Predecessor archived as `leaves/002a-t0-a.md`
(molted 2026-07-25, sap event 002); the molt adds the R7 cold open and
removes the serial-viewing recap — the diagnosis/fix/response spine
survives whole.

## Siblings

[002b — The First Citizen](../002b-first-citizen/node.md) · [002c — ADMIN(?)](../002c-admin-wireframe/node.md)

## Anticipated grafts (§9)

The overlay in 002c can explain *what* pulsed through the channel; the
scavenger of 002b can wander into this irrigation story. Reconvergence
is a designed payoff.

## Taste-rule notes

- **R7:** cold open re-grounds premise and names both capabilities in
  5s; each beat causes the next (curse → diagnosis → fix → response);
  hook question statable.
- **R1:** field state flips, farmer's belief flips, world reveals
  responsiveness.
- **R2:** no villain — the "antagonist" is a cracked pipe and a system
  nobody maintained.
- **R3:** the comedy is the deflation of cosmic despair into plumbing.
- **R5:** hook is a genuine state change — the world has a control
  plane, and it just noticed him.
