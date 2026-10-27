---
name: implement
description: "Implement, commit and review a slice or spec. Use when the Maintainer asks for a slice or spec to be implemented."
---

A slice is implemented by two kinds of agent: the session the Maintainer talks to, and its sub-agents. The session hands the slice off and checks the work; a sub-agent implements it, and a new sub-agent runs each review pass. The *sub-agent* that wrote the code never runs `code-review` on it, and the session reads reports, never the diff or a review's working material.

### The workflow
```txt
Implement with a sub-agent -> Review passes, each in a new sub-agent -> Repeat in rounds -> Set the Status -> Land -> Close on the Maintainer's word
```

## The session handing a slice off

When the Maintainer says to implement a `ready-for-agent` slice:

1. Make the worktree named after the slice, `<effort>/<NNN-slug>` (where the project has a WorktreeCreate hook, the hook makes it), and start a sub-agent that runs the sub-agent section of this skill, giving it the worktree's path to work in by absolute path. Worktree isolation takes no name, so the sub-agent does not make the worktree.
2. When the sub-agent reports passes 1–3 done, start a new sub-agent to run /code-review on the slice's commits, and wait for its report. Never run a review yourself. Record every pass's findings in the ledger (see `Passes`).
3. If the report has findings, send them to the implementing sub-agent with SendMessage, which resumes it with its context. Wait for its report that the fixes are committed, then start the next round or end them, as `Rounds` says.
4. When the rounds end, tell the implementing sub-agent to set the Status, and wait for its report that it is committed.
5. Land the slice's branch, as `Landing` says.
6. Report to the Maintainer: what was committed and landed, each round's findings, and what waits on the Maintainer. Closing waits on the Maintainer's word.
7. Name any other `ready-for-agent` slices that could run next, each with its own sub-agent: beside this one where they touch different files, after it where they touch the same ones.

When the implementing sub-agent hands up a question, ask it as `Ask the Maintainer` says and send the answer back with SendMessage.

## The sub-agent working a slice

Implement the work described in the spec or slice, then put it through review passes 1–3 before reporting back.

1. **Implement.** Work in the worktree named after the slice (`<effort>/<NNN-slug>`, branch `worktree-<effort>/<NNN-slug>`), so the worktree and the slice name each other. Use /tdd where possible, at pre-agreed seams. Run typechecking and single test files regularly.
2. **Prove it.** Get proof for every change you made. See `Proof`.
3. **Commit once per acceptance criterion.** When a criterion is confirmed, tick it in the slice and commit the tick with the work that met it, using /commit-messages. Run the full test suite before the last commit.
4. **Run passes 1–3**, as `Passes` says, fixing each pass's findings as `Rounds` says before starting the next.
5. **Stop before `code-review`.** Report to the session what was committed and each pass's findings, and stop, with no Status set. The session runs `code-review` and sends its findings: fix them, commit, and report again.
6. **Set the Status** when the session says the rounds have ended, as `Landing` says, and report that it is committed.

Where you cannot continue alone, hand the question to the session in your report and stop until it answers. See `Ask the Maintainer`.

## Review

Fix what each finding names, and nothing more. Push back on a finding that reaches past the slice.

### Passes

Each pass reads the code the previous pass's fixes left, so they run in this order and never in parallel, each in a new sub-agent on this slice's commits:

1. /structural-review: does the code's shape match the domain?
2. /method-review: is each method as clear as it could be?
3. /hierarchical-documentation: names and comments. It edits in place; read its changes before committing them, and use its commit-message notes.
4. /code-review: the spec, the repo's standards, and stale READMEs. The session starts this one, never the implementing sub-agent.

The session keeps a ledger of the findings in its scratchpad: id, pass, round, outcome, and usage where a report gives it. It records what the reports say, never a guess.

### Rounds

A round is one `code-review` run; passes 1–3 run once, before round 1. Round 1 reads the slice's whole diff; later rounds read only the code changed since and the findings still open.

- **Fix within the slice.** Fix each finding inside the slice's scope and commit the fix. A finding beyond it, such as a reframing that reaches past what the slice asked for, is named in the slice for the Maintainer instead. A round is done when every finding is one or the other.
- Another round runs only when the last one fixed more than nitpicks. A nitpick is a wording, comment, doc or format fix that changes no behaviour; declined nitpicks need no round either.
- Stop at 3 rounds. Go to 5 only while a finding about security, permissions, auth, data loss, or state and concurrency stays open with evidence, or when the Maintainer asks.
- A finding still open when the rounds stop is named in the slice for the Maintainer.

## Landing

1. **Set the Status.** The implementing sub-agent sets the slice's Status for what it waits on, in the last commit, whose message ends `Reviewed in <N> rounds, by <model>`, naming the model the passes ran on:
   - **A criterion waits on the Maintainer** (a converge, a live observation): `ready-for-human`. The rounds have already run, and a live check the Maintainer ticks afterwards needs no second one.
   - **Every criterion is ticked**: `ready-for-closure`. Closing it waits on the Maintainer's word in the conversation.
2. **Land.** The session lands the slice's branch with `bin/land` from the project's main checkout, without asking. A branch at `ready-for-human` lands too, so the Maintainer's check runs on main.

## Proof

Proof is evidence you observed yourself in this session: command output, a reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same reproduction pass.
- Run any checks the repo's CI runs.
- Add one focused test that fails without the fix, where the behaviour has none and the repo has a test setup.
- For UI and runtime behaviour, run the app, code or service and look at the change. Green mocked tests do not prove the user experience works. Put screenshots in the scratchpad.

A change you cannot prove is one you are not confident in: `Ask the Maintainer`.

## Ask the Maintainer

A question in a normal message goes unseen, and the thread looks done. The implementing sub-agent hands its question to the session in its report and stops; the session asks it with the harness's question tool, `AskUserQuestion` in Claude Code, so the thread shows that it is waiting.

- Put all the context in the question: what blocks the work, and the options with the recommendation first.

Ask only when the work cannot continue alone:
- A change cannot be proven.
- `bin/land` refuses, for a cause outside the slice.
- The next step deletes data, touches production, or changes things outside the repo.
- The goal is ambiguous in a way that changes the result.
- Another slice makes this one obsolete.

Decide everything else with sensible defaults, and list those decisions in the report.
