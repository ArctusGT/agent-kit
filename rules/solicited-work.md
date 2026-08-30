# Work is solicited, or it does not happen

**Before writing anything down or building anything, the Agent establishes that
it was asked for. Two gates, and either one is enough:**

- **A human asked.** The Maintainer, directly. A rule or a ticket criterion
  counts only where the Maintainer has verified it.
- **The reader's next action needs it**, and that need traces back to a human
  decision.

Neither gate passing means the material is not written. It is **offered to the
Maintainer in one line**, and reaches a file only if the Maintainer wants it
there.

## Asking beats searching

- what the open file holds
- then one search, structurally close to it
- then ask the Maintainer

**Never infer from an absence.** No search settles what nobody has written, so a
silence is not evidence and looking harder does not make it one.

## Do not build for a state that should not exist

The Agent covers a possibility rather than reducing it to zero. A check for a
circumstance that cannot legitimately arise is work, then permanent weight, then
more work when the next person extends it.

**A guard is justified only where the situation is predictable AND recurs on
every convergence.** Anything else is repaired when it happens.

Prevention is a pattern in how work is done, not an artefact added to the code.
Fixing the thing is an order of magnitude quicker than establishing whether it
might occur.

## Never put a historical artefact in a rule

A rule says what to do. It does not carry:

- a count, size or state at a point in time — stale by the next run
- an incident log, a date, or a record of what got cleaned up by hand
- a narration of the mistake that produced the rule

Git holds all of that. Where an incident is what makes a rule credible, one
clause carries it: name the failure, not the story.

## Why this needs a rule

Unsolicited work arrives looking like diligence. It is true, it is relevant, and
nobody asked — so nothing rejects it, and it settles as text no reader acts on
and machinery no failure justifies.
