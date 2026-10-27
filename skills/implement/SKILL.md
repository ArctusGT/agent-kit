---
name: implement
description: "Implement, commit and review a slice or spec. Use when the user or a briefing agent asks for a slice or spec to be implemented."
---

A slice is implemented by two kinds of agent. The session the Maintainer talks to hands it off and checks the work; a sub-agent implements it. No agent reviews its own code with `code-review`, and the session reads reports, never the diff or a review's working material.

## The session handing a slice off

When the Maintainer says to implement a `ready-for-agent` slice:

1. Make the worktree named after the slice, passing `<effort>/<NNN-slug>` as its `name`, and start a sub-agent in it that runs this skill's part for the sub-agent. Starting waits on the Maintainer's word; a slice being raised is not it.
2. When the sub-agent reports, start a separate sub-agent to run /code-review on the slice's commits, and wait for its report. Never run the review yourself.
3. If the report has findings, send them to the implementing sub-agent with SendMessage, which resumes it with its context, and it fixes each or names it in the slice. Then start a new `code-review` sub-agent. Repeat until a run leaves nothing to fix.
4. Tell the implementing sub-agent to set the Status in its last commit.
5. Report to the Maintainer: what was committed, each review's findings, and what waits on the Maintainer. Landing and closing wait on the Maintainer's word.

## The sub-agent working a slice

Implement the work described in the spec or slice, then put it through three reviews before reporting back.

1. **Implement.** Work in the worktree named after the slice (`<effort>/<NNN-slug>`, branch `worktree-<effort>/<NNN-slug>`), so the worktree and the slice name each other. Use /tdd where possible, at pre-agreed seams. Run typechecking and single test files regularly.
2. **Commit once per acceptance criterion.** When a criterion is confirmed, tick it in the slice and commit the tick with the work that met it, using /commit-messages. Run the full test suite before the last commit.
3. **Review, one pass at a time.** Each pass reads the code the previous pass's fixes left, so they run in this order and never in parallel. For each, start a sub-agent on this slice's commits and wait for its report. Fix and commit each pass's findings as step 4 says before starting the next:
   1. /structural-review: does the code's shape match the domain?
   2. /method-review: is each method as clear as it could be?
   3. /hierarchical-documentation: names and comments. It edits in place; read its changes before committing them, and use its commit-message notes.
4. **Fix within the slice.** Fix each finding, from these reviews and from the `code-review` findings the session sends, inside the slice's scope and commit the fix. A finding beyond it, such as a reframing that reaches past what the slice asked for, is named in the slice for the Maintainer instead. Done when every finding is one or the other.
5. **Stop before `code-review`.** After the third review, report to the session what was committed and each review's findings, and stop. Do not set a Status yet. The session runs `code-review` in a separate sub-agent and sends its findings; fix them as step 4 says.
6. **Set the Status.** When the session says a `code-review` run left nothing to fix, set the slice's Status for what it waits on, in the last commit:
   - **A criterion waits on the Maintainer** (a converge, a live observation): `ready-for-human`. The reviews have already run; the tracker's closing rules say why a live check ticked later needs no second one.
   - **Every criterion is ticked**: `ready-for-closure`. Closing it waits on the Maintainer's word in the conversation.

   Then report to the session what was committed and anything left for the Maintainer.
