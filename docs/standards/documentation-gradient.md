# The documentation gradient

**The running system, and the code and config that set it, are the account of
how things are. Prose about them is a cache, and git holds the history.** An
explanation goes to the nearest home that can be checked, and no further.

## The ladder

| the material | where it goes |
|---|---|
| why a line is written the way it is, where the code cannot show it | a comment on that line |
| what a function is for and how it is used | a comment on the function |
| what a file is, where its name and place do not say | a file header of one or two lines |
| how to use a directory's code, and the traps in using it | that directory's README — `readme-shape.md` |
| what a change did, and what was measured to show it | the commit message |
| a value the repository sets | the source that sets it, once |
| what the system guarantees, what the work must prove, a constraint someone means to improve | the slice that pursues it, once |
| a constraint no slice can resolve | an ADR, once the Maintainer ratifies it, cited by name only |
| when a line changed, and who changed it | git, which answers without being asked |
| how something is, or a value the system still holds | nowhere: read it again, with the script or command that reads it |

Each rung sits further from what would falsify the claim than the one above it.
**Material moves toward the code, never away from it.**

## Comments

**Add a comment when:**
- A reader might wonder *why* the code is written this way
- A decision was made to *not* do something obvious — the absence needs explaining
- Something surprising is happening that could cause a future reader to pause
- There's a footgun or dangerous assumption that can't be eliminated by restructuring

**Remove a comment when:**
- It restates what the code already says clearly
- A rename or extraction has made it redundant

**Check for overflow.** After naming is complete, re-read the changed code as if
encountering it for the first time. What questions would a future reader have that
the identifiers don't answer? Common overflow: why this approach instead of an
obvious alternative, performance constraints that shaped the design, or a mental
model needed to reason about the code. Be wary of evaluating from your own
perspective — you already know the context from the conversation. The test is what
someone reading this code cold would wonder about.

**Place comments as close as possible to the code they describe.** A comment that
applies to one branch of an `if` belongs inside that branch, not above the whole
statement. Reference specific identifiers in comments where possible — this makes
the relationship between comment and code explicit and harder to accidentally break.

## Measurements

A measurement is what the running system, a host or a third-party binary was
observed to do. **It carries its method**, so the next reader can take it again
rather than trust it. Where the method is a script the repository ships, name
the script. A measurement that cannot be re-taken was never falsifiable,
whatever date it carries.

It goes with its subject, on the ladder above. A physical one-shot that nothing
can re-read goes in the slice holding the constraint, or an ADR once ratified.

**Never a ledger**: a build record, a measurement log, an as-built document. Its
subject is measurements rather than a thing, so every line is true when written
and nothing ever invalidates it. A reader then takes it over the system, and a
drifted value looks the same as a current one. Delete it and let git hold what
was there. The one exception is a prototype's findings under `.research/`,
written before there is a subject to hold them.

## Provenance is git's

When the repository changed, and who changed it, is git's answer. State the
fact and let git carry the date: *"moved here from the shared role"*, not
*"moved here 2026-08-31"*. **The test: can git answer it without being told what
to look for? Then the date is noise.**

A rule drops a count stale by the next run, an incident log, a narration of the
mistake that produced it. Where an incident makes a rule credible, one clause
names the failure.

### The exception: a copy that leaves git

An exported artefact (a PDF or HTML page published to a documentation host, a
printed sheet) is read where `git log` cannot run, so it carries a provenance
block derived from git, never typed by hand:

- **Version of the source, not the export**: the hash and date of the last
  commit touching the files it was rendered from, and a revision number
  counting those commits.
- **Who**: that commit's git author. Never the Agent.
- **Uncommitted sources render as a draft**: a DRAFT watermark, and
  *"uncommitted"* where the version would be.

The export is committed separately, and its commit message names the source
hash. A project adds its own fields (an approver, a review date) in its
`AGENTS.md`. The source behind the export carries no version line.

## Moving material between rungs

**A claim being moved is a claim being re-asserted.** A move feels like
formatting, so nothing fires the check that writing it the first time would
have.

- Read what the code does now, not what the text says it does.
- Check any value it quotes: a number in prose is a copy, and a copy drifts.
- Where two copies disagree, establish which is wrong before writing the
  survivor down.

A slice is deleted when it closes, so a reference to one dangles by design.
To find what a slice decided, read the slices or ask the Maintainer.

## Why

Every move away from the code is locally right and the composition is wrong:
design comes out of a comment into a header, a measurement into a log, a
decision into a README. Each lands one rung further from what would falsify it,
in a place with more authority and less to contradict it. What arrives reads as
documentation, and it **wins**: the next agent argues it back at the Maintainer
without establishing that anyone authored it on purpose.
`.agents/rules/a-raised-criterion-can-still-be-wrong.md` is what to do once it
has got that far.
