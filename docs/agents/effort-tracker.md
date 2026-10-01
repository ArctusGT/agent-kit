# Effort tracker

Efforts and specs for this repo live as markdown files in `.efforts/`. An
effort is a directory; each file in it is one slice of that effort.

An effort is not an issue. An issue is correspondence with someone outside the
repo, held by the forge and never cloned with it. A slice may name the issue it
answers; the issue never lives in `.efforts/`.

## When a skill says "publish to the effort tracker"

Create a new file under `.efforts/<effort>/` (creating the directory if needed).

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

- Maintainer or Agents may draft slices but must always do so using a skill.
  - Agents do not waste time asking for permission when they think a slice should be drafted
  - Slices **MUST** not duplicate acceptance criteria vaguely pre-existing in adjacent slices/efforts
    - Pre-existing slices may be enhanced, merged or contributed to after their initial creation with new requirements.
  - Only the maintainer stages a drafted slice.
    - A slice the Maintainer has staged is accepted, and therefore raised. Git carries who staged it and when.
    - A slice left unstaged is undecided. Not rejected, not forgotten, and not the Agent's to revise or delete on its own
- Said skill should contain the method of drafting the slice itself, but it *MUST* conform to the template shapes described in [SLICE-TEMPLATE.md](SLICE-TEMPLATE.md)
- Agents may mark acceptance criteria as "done" themselves whilst informing the Maintainer
  - Agents may question the Maintainer if it believes acceptance criteria is unfulfilled or accidentally marked "done".

## Staying on track

- The agent may present or maintain a scratchpad of acceptance criteria or specific human tasks it thinks the Maintainer is yet to address during the course of an individual chat. This is ephemeral, discarded at the end of a chat or the beginning of a new chat.

## Closing slices

Closed slices are retained only in git. The code base is representative of work done.

- Agents *MUST NOT* close slices themselves
- Agents *MAY* set a slice's Status to `ready-for-closure` once every acceptance criterion it can confirm is confirmed
  - This asks for review; it does not close anything. `ready-for-closure` means the Maintainer needs to review for closure.
  - Agents should remind the maintainer when slices are `ready-for-closure`.
  - The Maintainer greps for the term to find slices awaiting review, so an agent that finishes the work and leaves the Status alone hides it
- The maintainer may instruct an agent to close a slice using `ready-for-closure` if it's acceptance criteria is confirmed to be completed
  - An agent should ensure work is committed before it delete the slice file, and then commits
  - The effort directory and spec may remain unless the maintainer instructs the agent to remove it

## Comments

Comments append to the bottom of the slice under a `## Comments` heading

- Comments should start with the current date/timestamp included at the beginning or in the first line.
- Comments should be separated by a horizontal rule. Permission granted in advance to agents to fix comments with missing horizontal rules
