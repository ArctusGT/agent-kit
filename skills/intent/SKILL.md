---
name: intent
description: Align on the intent before a spec or a build. Use when the Maintainer states an intent ("the intent is ..."), when the objective, what to avoid or a premise is unclear, or when asked to "grill me".
---

The Maintainer gives two things: a **method** (do A, B and C) and an **intent**
(achieve D, optionally without E). The intent is the fixed point. The method is
a **premise**, the Maintainer's best guess at the time.

This skill ends with an intent the Maintainer has accepted, ready for a spec.
Where the objective is already checkable, nothing to avoid is missing, and no
weighing turns anything up, skip the rounds: proceed as asked and say nothing.

## Weigh the method

Hold each part of the method against the intent:

- **A cheaper route.** Something reaches D with less code, fewer moving parts or
  a smaller blast radius. Often the thing to avoid (E, or anything the
  Maintainer wants never to think about) is easier to remove at its source than to build
  around, and the extra part the method planned for disappears with it.
- **A conflict.** Two parts of the method work against each other, or one works
  against D.
- **An unmeasured premise.** One part depends on something nobody has observed.
  Name the cheapest proof that would settle it.

Say what holds in the next round: the premise, why it doesn't hold, and the
alternative or the proof. Prefer the shape that stays easy to change: a design
hardens once its premises have been proven, not before.

## Rounds

The **frontier** is every question you can ask _now_ without guessing at answers
you haven't heard yet. Ask the whole frontier in one round, then wait for the
answers. Each round's answers reshape what is left: recompute the frontier. A
question whose answer depends on another question still open in this round
belongs to a _later_ round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Ask through a **scenario**: give an example of the behaviour that would follow
from an answer and let the question fall out of it, rather than putting the
abstract question directly. An abstract question arrives carrying your framing,
and the Maintainer answers inside it, including when the answer they need is
outside it. So open broadly and narrow late: leave a particular in play until a
later round, or until running the thing makes it obvious, because settling one
early for a tidy frontier closes an option the Maintainer would have taken once
they had seen it work. Save the sharp explicit question for what blocks
progress.

**Surface assumptions both ways.** In the first round, list the premises you hear
the Maintainer resting on beside your own reading of the request, side by side,
so a mismatch shows before any question is answered.

**Facts are your job.** When a frontier question needs a fact from the
environment (filesystem, tools, etc.), dispatch a sub-agent to find it, and
never ask the Maintainer for what you could look up. A running exploration is an
unsettled prerequisite: only the questions downstream of it wait, so ask the
rest of the frontier now.

### Gaps

The Maintainer may say they don't know. Close that gap yourself rather than
asking again, taking the first branch that fits:

- **Confident:** state what you know, mark it `confident`, and say what would
  confirm it, so the Maintainer can check it instead of taking it on trust.
- **A quick check settles it:** offer a read-only probe, a test in the
  session's scratch space, or a web lookup. Ask before going online. Run the
  check once the Maintainer says yes, and report what it showed.
- **Nothing can be known until something exists:** read
  `.agents/skills/prototype/SKILL.md` and follow it, then resume from what the
  prototype showed.

A finding worth keeping across sessions goes to `.research/` only with the
Maintainer's agreement. Offer it in one line, and write it with the method that
produced it.

### Sort what you learn

Keep four lists, each item marked **solicited** (the Maintainer said or
confirmed it) or **unsolicited** (you inferred it):

- **Objectives**, the outcomes the work must achieve.
- **Nice-to-haves**, wanted if cheap.
- **Unspoken wants**, what the Maintainer would expect without saying it.
- **Unwanteds**, what must not happen.

Offer an unsolicited item in one line and leave it out until the Maintainer
confirms it.

Once a term or decision settles that belongs in the glossary or an ADR, read
`.agents/skills/domain-modeling/SKILL.md` and follow it to record it.

## Stop

Stop asking when the objectives can be checked, the unwanteds are named, and
each premise is either confirmed or paired with its proof. A question still open
then is not a failure: name it beside its proof.

Present the sorted intent for the Maintainer to accept, and offer `to-spec` in
one line.

## Realignment

When the intent changes mid-build, stop the build and run this skill again with
the current spec as the starting point. The result is a new spec baseline. The
spec stays untouched while the build is in flight.
