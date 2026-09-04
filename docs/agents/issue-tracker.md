# Issue tracker

Issues and specs for this repo live as markdown files in `.issues/`.

## When a skill says "publish to the issue tracker"

Create a new file under `.issues/<effort>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Reference docs

- [TICKET-TEMPLATE.md](TICKET-TEMPLATE.md): what the tickets should look like
- [triage-lables.md](triage-labels.md): what labels we use for state roles 

## Issue Tracker Principles

### Use with skills

Based on Matt Pocock's original skills, by which followed the following build chain:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review
```

## Layout

- One feature per directory: `.issues/<effort>/`
- The spec is `.issues/<effort>/spec.md`
- Issues are one file per ticket at `.issues/<effort>/<NNN>-<slug>.md`
  - where `NNN` is append-only, non repeating number from `001`
  - never multiple issues combined into one ticket file

## Creating specs

Specs are created using a skill. Agents defer to the maintainer to invoke a skill to perform said action *NOT* create a spec themselves. Said skill should contain the shape of the spec itself, *NOT* this document.

## Creating tickets

- Tickets are *ALWAYS* created using a skill.
- The maintainer may invoke a skill to have a ticket drafted 
- Agents may invoke a skill to draft a ticket themselves
  - Agents do not waste time asking for permission when they think a ticket should be drafted
  - Agents **MUST** not duplicate acceptance criteria vaguely pre-existing in adjacent tickets/efforts
    - The Maintainer rejects any tickets that they deem a *DUPLICATE*; So should the Agent.
  - A *newly* drafted ticket devoid of acceptance criteria is automatically *REJECTED*
  - Agents *MUST* notify the Maintainer when they have drafted a ticket for review
  - The maintainer must *ACCEPT* or *REJECT* a ticket for it to be "raised"
  - **Staging is the acceptance.** A ticket the Maintainer has staged is accepted, and therefore raised. Nothing in the file records it, because `.agents/rules/the-index-is-the-maintainers.md` already makes staging the Maintainer's channel for "I have read this and I accept it", and git carries who staged it and when
    - A ticket left unstaged is undecided. Not rejected, not forgotten, and not the Agent's to revise or delete on its own
    - An Agent must therefore never ask whether a staged ticket is accepted, and never add an "accepted" marker to one
- Said skill should contain the method of drafting the ticket itself, but it *MUST* conform to the template shapes described in [TICKET-TEMPLATE.md](TICKET-TEMPLATE.md)
- Agents may check acceptance ticket criteria themselves whilst informing the Maintainer

## Staying on track

- The agent may present or maintain a scratchpad of acceptance criteria or specific human tasks it thinks the Maintainer is yet to address during the course of an individual chat. This is ephemeral, discarded at the end of a chat or the beginning of a new chat.

## Closing tickets

Closed tickets are retained only in git. The code base is representative of work done.

- Agents *MUST NOT* close tickets themselves
- Agents *MAY* set a ticket's Status to `ready-for-closure` once every acceptance criterion it can confirm is confirmed
  - This asks for review; it does not close anything. `ready-for-closure` means the Maintainer needs to review for closure
  - The agent says in a comment which criteria are unticked and why, so a criterion left unmet is distinguishable from one the hardware or the scope made moot
  - The Maintainer greps for the term to find tickets awaiting review, so an agent that finishes the work and leaves the Status alone hides it
- The maintainer may instruct an agent to close a ticket using `ready-for-closure` if it's acceptance criteria is confirmed to be completed
  - An agent should ensure work is committed before it delete the ticket file, and then commits
  - The effort directory and spec may remain unless the maintainer instructs the agent to remove it

## Comments

Comments and conversation history append to the bottom of the ticket under a `## Comments` heading

- Comments should start with the current date/timestamp included at the beginning or in the first line.
- Comments should be separated by a horizontal rule. Permission granted in advance to agents to fix comments with missing horizontal rules
