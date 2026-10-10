---
name: implement
description: "Implement, commit and review a slice or spec. Use when the user or a briefing agent asks for a slice or spec to be implemented."
---

Implement the work described in the spec or slice, then put it through four reviews before reporting back.

1. **Implement.** Use /tdd where possible, at pre-agreed seams. Run typechecking and single test files regularly.
2. **Commit once per acceptance criterion.** When a criterion is confirmed, tick it in the slice and commit the tick with the work that met it, using /commit-messages. Run the full test suite before the last commit.
3. **Review, one pass at a time.** Each pass reads the code the previous pass's fixes left, so they run in this order and never in parallel. For each of the first three, start a sub-agent on this slice's commits and wait for its report; run the fourth yourself, since it starts its own sub-agents. Fix and commit before starting the next:
   1. /structural-review: does the code's shape match the domain?
   2. /method-review: is each method as clear as it could be?
   3. /hierarchical-documentation: names and comments. It edits in place; read its changes before committing them, and use its commit-message notes.
   4. /code-review: the spec, the repo's standards, and stale READMEs.
4. **Fix within the slice.** Fix each finding inside the slice's scope and commit the fix. A finding beyond it, such as a reframing that reaches past what the slice asked for, is named in the slice for the Maintainer instead. Done when every finding is one or the other.
5. **Report back.** Once every criterion you can confirm is ticked, set the slice's Status to `ready-for-closure` in the last commit. Then report what was committed and anything left for the Maintainer.
