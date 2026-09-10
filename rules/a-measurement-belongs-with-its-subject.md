# A measurement belongs with its subject

**A measurement is written where the thing that produced it lives. Never into a
document that collects measurements.**

The subject is still running, and that is what separates a measurement from
every other claim: it can be taken again. A document holding one is a cache of
live state with no invalidation, and the system it describes will never tell it
that it has gone wrong.

## Where one goes

| what was measured | where it is written |
|---|---|
| a value the system still holds | nowhere — read it again, with the script that reads it |
| a value the repository sets | the source that sets it, once |
| why a value was chosen | a comment on the line that sets it, where the code cannot show it alone |
| what a change did, and what that measured | the commit message for the change |
| a physical one-shot nothing can re-read | the ticket that holds the constraint, or an ADR once it is ratified |

Which rung each of those is, and why the ordering runs toward the code rather
than away from it, is `where-an-explanation-belongs.md`.

**Git holds a measurement and dates it without being asked.** The commit that
made a change carries what was measured, its n and its method, and git supplies
who and when. `provenance-and-measurement.md` covers what to write beside a
measurement; it is the method, so the next reader can take it again.

## Never a ledger

**A build record, a measurement log, an as-built document, a page of
observations: none of these.** The name varies and the shape does not — a
document whose subject is measurements rather than a thing.

The tell is that its contents read as a history of the work rather than a
description of anything. A reader wanting a value gets it faster from the system.

- **Never a criterion demanding one.** "Recorded in the build record" is a
  criterion to doubt before it is satisfied —
  `a-raised-criterion-can-still-be-wrong.md`.
- **Never migrate one into READMEs to rescue it.** That republishes every claim
  in it at once, which is `verify-before-relocating.md` at document scale.
  Delete it, and let git hold what was there.

## Why this needs a rule

**It fails by accumulating correctness.** Every line is true when written, every
line carries its date, and every line satisfies whichever rule sent it there. So
nothing rejects any of it, and there is no moment at which the document is wrong
enough to notice.

It then outranks its subject. Prose is easier to read than a running system, so
it gets read instead, and a value that has drifted is indistinguishable from one
that has not: both are dated, both are plausible, and the drifted one is the one
nobody re-took.

Its copies defeat single-sourcing wherever single-sourcing exists. A firmware
README declined to repeat its toolchain pin so that the two could not disagree,
and the build record one directory away carried it twice. A driver scanned for
its display's address at every boot so that nothing would carry a guess, and the
build record became the only place in the repository stating the address.
