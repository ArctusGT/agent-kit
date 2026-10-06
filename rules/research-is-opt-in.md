# Research is read when asked, and not otherwise

**`.research/` at a project root holds the Maintainer's working material:
prototypes, findings, measurements taken before anything is decided. The Agent
does not read, search, cite or write there unless the Maintainer asks, by name,
in the current conversation.**

The directory is gitignored. It exists in one working copy, and nothing in it
has been reviewed.

## What asking covers

- **The request names the directory or a file in it.** "Read the n8n findings"
  covers the findings file. It does not cover the rest of `.research/`.
- **Permission lasts for the task that asked.** A later task in the same
  session starts without it.
- **Writing is the same.** Being asked to write a findings file is not being
  asked to tidy the directory around it.

## Searches leave it out

The Grep tool and `git grep` skip it already, because both honour
`.gitignore`. `grep -R` and `find -L` do not, so exclude it by hand:

    grep -R --exclude-dir=.research <pattern> .
    find -L . -path ./.research -prune -o <test> -print

A hit inside `.research/` from a search nobody asked to include is not
evidence. Discard it rather than reasoning from it.

## Nothing outside points in

No slice, README, comment or commit message cites a path under `.research/`.
The directory is untracked, so a reference to it dangles in every other clone
and in the history.

**Material leaves only when the Maintainer promotes it**, into a slice, the
code or the config. A claim being moved is a claim being re-asserted, so check
it against the running system on the way out —
`.agents/docs/standards/where-an-explanation-belongs.md`.

## Inside, a findings document is allowed

`a-measurement-belongs-with-its-subject.md` bans a document whose subject is
measurements. `.research/` is the exception, because a prototype's findings
exist before there is a subject for them to belong to: no role, no slice, no
config yet.

What still holds inside: every measurement carries its method, so it can be
taken again (`.agents/docs/standards/provenance-and-measurement.md`). A findings file with no method
is a list of guesses.

## Why this needs a rule

Unreviewed material read without being asked becomes a source. It is
prototype-grade and written before any decision, and it reads as authoritative
anyway, so it gets argued back at the Maintainer the way a stale README does.
It also breaks every other clone of the project, which cannot see it.
