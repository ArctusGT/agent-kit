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
- [triage-labels.md](triage-labels.md): what labels we use for state roles 

## Effort Tracker Principles

### Use with skills

Based on Matt Pocock's original skills, by which followed the following build chain:

```txt
grill-with-docs → to-spec → to-slices → implement
```

`implement` owns how a slice is worked: who implements it, the review passes and rounds, setting the Status, and landing. This document covers making, raising and closing slices.

## Layout

- One effort per directory: `.efforts/<effort>/`
- The spec is `.efforts/<effort>/spec.md`
- Slices are one file per slice at `.efforts/<effort>/<NNN>-<slug>.md`
  - where `NNN` is append-only, non repeating number from `001`
  - never multiple slices combined into one file
- Name a worktree working a slice after it, `<effort>/<NNN-slug>`: its path under the worktrees directory mirrors the slice's under `.efforts`, and its branch is `worktree-<effort>/<NNN-slug>`. This is the link between a slice and the worktree working it. Nothing enforces it; a worktree with any other name is made as before.

## Creating specs

Specs are created using a skill. Agents defer to the maintainer to invoke a skill to perform said action *NOT* create a spec themselves. Said skill should contain the shape of the spec itself, *NOT* this document.

## Creating slices

### Drafting

Said skill should contain the method of drafting the slice itself, but it *MUST* conform to the template shapes described in [SLICE-TEMPLATE.md](SLICE-TEMPLATE.md)

- Agents draft slices, always using a skill. The Maintainer edits a slice only to show how something should read, as a baseline for the Agent to revise from.
- Agents do not waste time asking for permission when they think a slice should be drafted
- Slices **MUST** not duplicate acceptance criteria vaguely pre-existing in adjacent slices/efforts
  - Pre-existing slices may be enhanced, merged or contributed to after their initial creation with new requirements.
  - A rework of a raised slice, any change to its scope or criteria, is left uncommitted like a draft and holds only once the Maintainer says to raise it. Ticking a criterion or setting a Status is not a rework.
- A drafted slice is a file left uncommitted in whichever checkout the Agent is working in, a worktree included, for the Maintainer to read.
- A worktree a slice is drafted in branches from the local default branch, not the remote's, so it sees every slice already raised.

### Committing

- Work on a slice starts only once it is raised, through `implement`.
  - An uncommitted draft, or the uncommitted part of a rework, is not implemented.
- A slice is raised when the Maintainer says so in the conversation.
  - The Agent commits the draft as written, and the commit message names the instruction.
- A committed slice lands on the default branch straight away.
  - A slice left uncommitted is undecided or forgotten, not rejected. It is not the Agent's to revise or delete on its own; the Agent reminds the Maintainer it exists and suggests an action.
- The Agent cherry-picks that one commit onto it in the main checkout, never the whole branch, so unreviewed work on the branch stays behind. A session isolated to a worktree cannot reach the main checkout, so the Agent leaves the worktree, keeping it, to commit the slice there.

### Staying on track

- The agent may present or maintain a scratchpad of acceptance criteria or specific human tasks it thinks the Maintainer is yet to address during the course of an individual chat. This is ephemeral, discarded at the end of a chat or the beginning of a new chat.
- Agents may tick unmarked acceptance criteria themselves whilst informing the Maintainer; a criterion marked `**Maintainer:**` is ticked only once the Maintainer reports it met.
- Agents may question the Maintainer if it believes acceptance criteria is unfulfilled or accidentally marked "done".

## Closing slices

Closed slices are retained only in git. The code base is representative of work done.

- The Status is `ready-for-human` while a criterion marked `**Maintainer:**` is unticked (see [SLICE-TEMPLATE.md](SLICE-TEMPLATE.md)), and `ready-for-closure` once every criterion is ticked. `implement` says how the slice is reviewed before either is set, and when the branch lands.
- When the Maintainer reports a `**Maintainer:**` criterion met, the Agent ticks it on main and, once every criterion is ticked, sets `ready-for-closure`.
- **The Maintainer's word to close a `ready-for-closure` slice is the confirmation to close it**
  - Agents remind the Maintainer which slices are waiting.
  - The Agent deletes the file and commits the deletion, with the commit message naming the instruction.
  - The closing commit is the record, since git is the only place the slice survives: what the slice delivered, and anything named in it for the Maintainer that is still open.
- A worktree's branch has already landed by then, so the slice is closed on main.
- The effort directory and spec may remain unless the maintainer instructs the agent to remove it

## Comments

Comments append to the bottom of the slice under a `## Comments` heading

- Each comment is committed on its own, so the commit dates it; the comment itself carries no date.
- Comments should be separated by a horizontal rule. Permission granted in advance to agents to fix comments with missing horizontal rules
