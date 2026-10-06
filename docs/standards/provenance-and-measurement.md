# Provenance is git's; a measurement carries its method

Every line this repository holds, and the same test for each: a rule, a README, a
slice, a comment in a task file.

**A line's provenance is when the repository changed, and who changed it.** Git
answers that exactly, so state the fact and let git carry the date — *"moved here
from the shared role"*, not *"moved here 2026-08-31"*.

**A measurement is what the running system, a host, or a third-party binary was
observed to do.** It carries how it was taken, so that the next reader can take
it again rather than trust it. Written in the commit that made the change, git
supplies the date; written anywhere else, it goes with its subject and never
into a document that collects measurements —
`.agents/rules/a-measurement-belongs-with-its-subject.md`.

> **The test: can git answer it without being told what to look for?** Then the
> date is noise.

## The exception: a copy that leaves git

**An exported artefact is read where git cannot answer, so it carries its own
provenance.** An exported artefact is a rendered file meant to be read outside
the repository: a PDF or HTML page published to SharePoint or any
documentation host, or a printed sheet. A reader holding one cannot run
`git log`, and two printed copies look equally current.

Every exported artefact carries a provenance block, derived from git and never
typed by hand:

- **Version: the source, not the export.** The hash of the last commit that
  touched the files it was rendered from, that commit's date, and a revision
  number counting the commits that touched them. The export cannot carry its
  own hash, because the hash only exists once the export is committed.
- **Who: the git author of that source commit.** Never the Agent's name, and
  never *"<agent> on behalf of"*. The Agent is not a git author, so this holds
  without anyone checking it.
- **Uncommitted sources render as a draft.** A DRAFT watermark, and
  *"uncommitted"* where the version would be. Nothing without a real hash goes
  on a wall or a host.

The export is committed separately from its sources, and the export commit's
message names the source hash it was rendered from.

A project adds its own fields to the block — an approver, a location, a review
date — in its `AGENTS.md`. This rule names none.

Everything else in the repository keeps git as its only provenance. The
exception covers the exported copy, not the source it came from: the markdown
behind a PDF carries no version line.

`.agents/rules/ansible/ansible-roles.md` uses the word in this sense already — *"git is the
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
