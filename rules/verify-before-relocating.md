# Verify a comment before moving it

**A comment being moved is a claim being republished. Check it against the code
first.**

Relocating existing text into a README, a rule or an issue feels like a formatting
change. It is not — it re-asserts every statement in it, in a place with more
authority than the comment had, and usually further from the code that would
contradict it.

Before writing a moved claim anywhere:

- **Read what the code does now**, not what the comment says it does.
- **Check the value**, if the comment quotes one. A number written out in text is
  a copy, and a copy is a thing that drifts.
- **When two copies disagree, at least one is wrong.** Find out which before
  writing the surviving one down.

**A claim repeated identically in four files is not thereby verified.** It is one
unverified claim with four copies, and the repetition reads as corroboration.

## Why this needs a rule

It fails invisibly and in the wrong direction. A stale comment misleads one
reader at one site; the same text in a README misleads everyone, carries the
weight of documentation, and is no longer next to the code that disproves it.

Contradiction between two copies is the only cheap signal. Where several copies
agree there is nothing to notice, so the check has to happen before the copy is
made rather than after.
