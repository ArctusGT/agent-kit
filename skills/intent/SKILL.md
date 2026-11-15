---
name: intent
description: Weigh a requested method against the objective behind it. Use when the Maintainer states an intent ("the intent is", "so that", "I don't want to have to"), or asks for work alongside the reason for it, before drafting a slice or starting the work.
---

The Maintainer gives two things: a **method** (do A, B and C) and an **intent**
(achieve D, optionally without E). The intent is the fixed point. The method is
a **premise**, the Maintainer's best guess at the time.

Where the intent itself is unclear, draw it out first: read
`.agents/skills/grilling/SKILL.md` and follow it.

Before drafting or building, hold each part of the method against the intent:

- **A cheaper route.** Something reaches D with less code, fewer moving parts or
  a smaller blast radius. Often the thing to avoid (E, or the W the Maintainer
  wants never to think about) is easier to remove at its source than to build
  around, and the extra part the method planned for disappears with it.
- **A conflict.** Two parts of the method work against each other, or one works
  against D.
- **An unmeasured premise.** One part depends on something nobody has observed.
  Name the cheapest proof that would settle it: a read-only probe, a prototype,
  one measurement.

Where one of these holds, say so in one short message before any work: the
premise, why it doesn't hold, and the alternative or the proof. Then wait.
Where none holds, proceed as asked and say nothing about it.

Prefer the shape that stays easy to change. A design hardens once its premises
have been proven, not before.
