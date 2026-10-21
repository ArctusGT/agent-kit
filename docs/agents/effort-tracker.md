# Effort tracker

Efforts and specs for this repo live as markdown files in `.efforts/`. An
effort is a directory; each file in it is one slice of that effort.

An effort is not an issue. An issue is correspondence with someone outside the
repo, held by the forge and never cloned with it. A slice may name the issue it
answers, in one header line under `**Status:**`, as
`**ticket:** <group>/<project>#<n>`; the issue never lives in `.efforts/`.

## When a skill says "publish to the effort tracker"

For a slice, run `.agents/bin/new-slice <effort> <slug>` and fill in the file it
prints. For the spec, write `.efforts/<effort>/spec.md` directly.

## When a skill says "fetch the relevant slice"

Read the file at the referenced path. The user will normally pass the path or the slice number directly.

## Reference docs

- [SLICE-TEMPLATE.md](SLICE-TEMPLATE.md): what the slices should look like
- [triage-lables.md](triage-labels.md): what labels we use for state roles 

## Effort Tracker Principles

### Use with skills

Based on Matt Pocock's original skills, by which followed the following build chain:

```txt
grill-with-docs → to-spec → to-slices → implement → code-review
```

## Layout

- One effort per directory: `.efforts/<effort>/`
- The spec is `.efforts/<effort>/spec.md`
- Slices are one file per slice at `.efforts/<effort>/<NNN>-<slug>.md`
  - where `NNN` is append-only, non repeating number from `001`
  - never multiple slices combined into one file

## Creating specs

Specs are created using a skill. Agents defer to the maintainer to invoke a skill to perform said action *NOT* create a spec themselves. Said skill should contain the shape of the spec itself, *NOT* this document.

## Creating slices

- Agents draft slices, always using a skill. The Maintainer edits a slice only to show how something should read, as a baseline for the Agent to revise from.
  - Agents do not waste time asking for permission when they think a slice should be drafted
  - Slices **MUST** not duplicate acceptance criteria vaguely pre-existing in adjacent slices/efforts
    - Pre-existing slices may be enhanced, merged or contributed to after their initial creation with new requirements.
  - A drafted slice is a file left unstaged and uncommitted in whichever checkout the Agent is working in, a worktree included: ready for the Maintainer to stage there as the confirmation to commit it. A worktree a slice is drafted in branches from the local default branch, not the remote's, so it sees every slice already raised.
  - A committed slice lands on the default branch straight away. The Agent cherry-picks that one commit onto it in the main checkout, never the whole branch, so unreviewed work on the branch stays behind. A session isolated to a worktree cannot reach the main checkout, so the Agent leaves the worktree, keeping it, to land the slice.
  - Only the maintainer stages a drafted slice.
    - A slice the Maintainer has staged is accepted, and therefore raised. Git carries who staged it and when.
    - The Agent commits a staged slice as it was staged, without being asked. At the start of a turn it checks `git diff --cached --name-only -- .efforts/`; a staged slice at `ready-for-closure` is closed instead (below).
    - A slice left unstaged is undecided. Not rejected, not forgotten, and not the Agent's to revise or delete on its own
- Said skill should contain the method of drafting the slice itself, but it *MUST* conform to the template shapes described in [SLICE-TEMPLATE.md](SLICE-TEMPLATE.md)
- Agents may mark acceptance criteria as "done" themselves whilst informing the Maintainer
  - Agents may question the Maintainer if it believes acceptance criteria is unfulfilled or accidentally marked "done".

## Staying on track

- The agent may present or maintain a scratchpad of acceptance criteria or specific human tasks it thinks the Maintainer is yet to address during the course of an individual chat. This is ephemeral, discarded at the end of a chat or the beginning of a new chat.

## Closing slices

Closed slices are retained only in git. The code base is representative of work done.

- Agents close a slice only on the Maintainer's confirmation
- While a criterion waits on the Maintainer, such as a converge or a live observation, the slice's Status is `ready-for-human`
- Once every acceptance criterion is ticked, Agents set the Status to `ready-for-closure` and leave the slice **unstaged and uncommitted**
  - Before setting it, the Agent runs the `code-review` skill on the commits that did the slice's work, and fixes what it finds or names it in the slice for the Maintainer.
  - The Maintainer reviews it in the working tree, where every slice awaiting closure shows as one unstaged change. Agents remind the Maintainer which ones are waiting.
- **Staging a `ready-for-closure` slice is the Maintainer's confirmation to close it**
  - The Agent commits the slice as staged, then deletes the file and commits the deletion, with no further instruction. Both commits land on the default branch the way a raised slice does.
  - The closing commit is the record, since git is the only place the slice survives: what the slice delivered, and anything named in it for the Maintainer that is still open.
  - The effort directory and spec may remain unless the maintainer instructs the agent to remove it

## Comments

Comments append to the bottom of the slice under a `## Comments` heading

- Comments should start with the current date/timestamp included at the beginning or in the first line.
- Comments should be separated by a horizontal rule. Permission granted in advance to agents to fix comments with missing horizontal rules
