# Where an explanation belongs

**The running system, and the code and config that set it, are the account of
how things are. Prose describing them is a cache, and a cache with nothing to
invalidate it is how a claim outlives the thing it described.**

An explanation goes to the nearest home that can be checked, and no further:

| the material | where it goes |
|---|---|
| how something is | the system, the code, the config — read them |
| what a line is doing, where the code cannot show it alone | a comment on that line |
| how to use the code a directory holds, and the traps in using it | that directory's README |
| a finding, constraint or decision holding the system in a shape someone means to improve | the ticket that pursues the better outcome |
| a constraint no ticket can resolve | an ADR, once the Maintainer ratifies it |
| when a line changed, and who changed it | git, which answers without being asked |

Each rung sits further from what would falsify the claim than the one above it.
That is the whole ordering, and it runs one way: **material moves toward the
code, never away from it.**

## A README is for the technician

Two things, and the second is why anyone opens it twice:

- the commands for using the code and config that directory holds
- the traps the next technician or agent would otherwise fall into

A decision, a measurement, or a description of how the system is arranged
belongs on another rung. A reader wanting one of those gets a better answer
from the system.

## Finding what a ticket decided

Read the tickets, or ask the Maintainer. That is the discovery path, and it
needs no breadcrumb: a ticket is deleted when it closes, so a reference to one
dangles by design.

An ADR is the exception, because an ADR does not close. Cite it **by name, and
say nothing about what it holds** — a comment paraphrasing an ADR is a second
copy of the decision, free to drift from the first.

## Why this needs a rule

Every rule that moves an explanation is locally right, and the composition
carries it the wrong way. Design comes out of a comment. Reasoning longer than
a line comes off a host. A measurement leaves the document that collected it.
Each move is correct on its own, and each lands the material one rung further
from the code, in a place with more authority and less to contradict it.

What arrives at the top reads as documentation. An agent asked to change the
design then argues the README back at the Maintainer, having never established
that anyone authored the claim on purpose;
`a-raised-criterion-can-still-be-wrong.md` is what to do once it has got that
far, and this is how it does not.

The gradient was built when this kit kept provenance in the repository rather
than in git. Git carries provenance now, so the reason those rules pointed
outward is gone while the pointing remained.
