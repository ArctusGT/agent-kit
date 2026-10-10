---
name: implement
description: "Implement, commit and review a slice or spec. Use when the user or a briefing agent asks for a slice or spec to be implemented."
---

Implement the work described in the spec or slice, then review it before reporting back.

1. **Implement.** Use /tdd where possible, at pre-agreed seams. Run typechecking and single test files regularly.
2. **Commit once per acceptance criterion.** When a criterion is confirmed, tick it in the slice and commit the tick with the work that met it. Run the full test suite before the last commit.
3. **Review.** Run /code-review on this slice's commits, and wait for both reviewers to report.
4. **Fix.** Fix each finding and commit the fix, or name it in the slice for the Maintainer. Done when every finding is one or the other.
5. **Report back.** Once every criterion you can confirm is ticked, set the slice's Status to `ready-for-closure` in the last commit. Then report what was committed and anything left for the Maintainer.
