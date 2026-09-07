# A raised criterion can still be wrong

**When a criterion cannot be met without inventing machinery, doubt the
criterion before building the machinery. Bring the Maintainer the doubt, not the
workaround.**

A ticket brief is authoritative about **scope** — what is being asked for, and
what is out of bounds. It is not authoritative about **truth**. A criterion is
someone's best statement of a requirement at the time they wrote it, and the
Agent implementing it usually learns more about the system than the person who
wrote it knew.

## The tell

**You are designing a mechanism whose only purpose is to satisfy a sentence.**
Nothing in the running system wants it, no consumer is waiting for it, and it
would not exist if the line were phrased differently.

At that moment, stop and trace the criterion:

- **To the human decision behind it.** A Maintainer weighed something and chose.
  That stands until they change it.
- **Or to a claim.** A comment, a header, an earlier ticket's wording, an
  Agent's own summary. A claim is a hypothesis wearing an imperative voice, and
  it does not bind anything.

Where it traces to a claim, say so in one line and propose the correction.
Where it traces to a decision, build it.

## What makes this hard to see

A criterion widens as it is copied, and each widening reads as the same
requirement. An observation that one function is not called becomes "reads
nothing back", which becomes "has no inbound path at all". Every step is a fair
paraphrase of the last and the end is unrecognisable from the start.

So trace to the **origin**, not to the previous restatement. `git log -S` on the
phrase finds it faster than reading forward from the ticket.

## Never

- **Never build around a criterion you have not traced.** The workaround
  outlives the misunderstanding and nothing later re-examines it.
- **Never quietly drop one either.** Both silent compliance and silent
  deviation hide the same thing: that the criterion was never checked.
- **Never treat your own drafted criterion as settled** because the Maintainer
  accepted it. They accepted the scope; they were relying on the draft being
  right about the system.

## Why this needs a rule

Everything in the tracker pushes one way. A brief is "the authoritative
specification", a ticket without criteria is rejected outright, and staging
makes a raised ticket carry the Maintainer's authority. All of that is correct
for scope, and all of it reads as correct for truth.

`solicited-work.md` warns that a ticket invents the shape it describes — but
only before the ticket is written. Afterwards there is nothing that licenses
doubt, so the Agent's only legal move is to satisfy the sentence, and it will
build whatever that takes.

The failure looks like diligence from both ends. The Agent is honouring the
brief, the Maintainer sees the brief honoured, and the machinery nobody wanted
is the only evidence either of them gets.
