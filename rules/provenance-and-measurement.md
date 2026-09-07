# Provenance is git's; a measurement carries its method

Every line this repository holds, and the same test for each: a rule, a README, a
ticket, a comment in a task file.

**A line's provenance is when the repository changed, and who changed it.** Git
answers that exactly, so state the fact and let git carry the date — *"moved here
from the shared role"*, not *"moved here 2026-08-31"*.

**A measurement is what the running system, a host, or a third-party binary was
observed to do.** It carries how it was taken, so that the next reader can take
it again rather than trust it. Written in the commit that made the change, git
supplies the date; written anywhere else, it goes with its subject and never
into a document that collects measurements —
`a-measurement-belongs-with-its-subject.md`.

> **The test: can git answer it without being told what to look for?** Then the
> date is noise.

`ansible-roles.md` uses the word in this sense already — *"git is the
provenance"*. `docs/adr/0001` uses **provenance marker** for something else, where
a glossary term was first resolved; that is a different object, not a competing
definition, and neither is in `CONTEXT.md`.

## What a rule drops on top of that

A count stale by the next run, an incident log, a narration of the mistake that
produced it. Where an incident is what makes a rule credible, one clause carries
it: name the failure, not the story.

## Why this needs a rule

Both kinds look like rigour at the moment of writing, and only one of them is.
A date is cheap and always plausible, so nothing rejects it, and the difference
does not surface until the provenance note has gone stale beside a measurement
that is still the only line worth reading.

**It fails in the opposite direction too, which is why this does not simply ban
dates.** An undated measurement cannot be told from a guess. The method is what
answers that rather than the date: a measurement saying how it was taken can be
taken again, and one that cannot be re-taken was never falsifiable whatever it
was stamped with. Where the method is a script the repository ships, name the
script.

The trap is that the writer cannot feel the difference. Recording *"moved here"*
and recording *"measured 10.011s"* are the same act from the inside, and only one
has a second copy in git.

`roles/host_baseline/tasks/chrony.yml` acquired provenance dates alongside its
measurements, and git already held every one of the provenance ones.
