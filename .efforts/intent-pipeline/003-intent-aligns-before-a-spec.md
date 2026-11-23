## Intent aligns before a spec

**Category:** enhancement
**Summary:** `intent` becomes the alignment phase, absorbing `grilling` and replacing `grill-with-docs`
**Status:** ready-for-agent
**blocked-by:** [intent-pipeline/002-prune-dangling-links]

**Current behavior:**
Alignment is spread over three skills. `intent` weighs a requested method
against its objective and hands off to `grilling` when the objective is
unclear. `grilling` asks rounds of questions. `grill-with-docs` is `grilling`
plus `domain-modeling`. None of them fills a gap in the Maintainer's
understanding from what the Agent already knows, offers a quick check in place
of a question, or sorts what is learned into what must be done and what must
not happen.

**Desired behavior:**
`intent` is the one skill for the alignment phase. It ends with an intent the
Maintainer has accepted, ready for a spec. In rounds, it:

- **Keeps `grilling`'s round format:** the frontier, numbered questions each
  with a recommended answer, asking through scenarios, facts found by the
  Agent and never asked of the Maintainer.
- **Surfaces assumptions both ways:** the Maintainer's premises and the
  Agent's own reading of the request, side by side, so a mismatch shows.
- **Fills gaps only where confident:** the Agent supplies what it knows with
  high confidence, marked as such, together with what would confirm it.
  Anything less confident becomes a check, not a claim.
- **Offers quick checks:** where a probe, a test in the session's scratch
  space or a web lookup settles a question faster than discussing it, the
  Agent offers it. Going online is asked first.
- **Sorts what it learns:** into objectives, nice-to-haves, unspoken wants and
  unwanteds, each marked solicited or unsolicited. An unsolicited item is
  offered in one line, never adopted.
- **Keeps the method weighing:** a cheaper route, a conflict, an unmeasured
  premise.
- **Has a prototype escape hatch:** where the Maintainer cannot know an answer
  until something exists, it hands off to `prototype` and resumes from what
  that showed.
- **Keeps findings only with agreement:** a finding worth keeping across
  sessions goes to `.research/` only when the Maintainer agrees.

It stops when the objectives can be checked, the unwanteds are named, and each
premise is either confirmed or paired with its proof. It then presents the
sorted intent for the Maintainer to accept, and offers `to-spec` in one line.

**Realignment:** once a build is under way it follows the spec as written.
When the intent changes mid-build, the Agent stops the build and runs `intent`
again with the current spec as its starting point. The result is a new spec
baseline. The spec is never edited while the build is in flight.

`grilling` and `grill-with-docs` are removed. Every reference in the kit
points at `intent` instead. `domain-modeling` stays a separate skill.

**Key interfaces:**
- `intent` skill: its description must trigger where `grilling`'s did, including "grill me"
- The skills and docs that currently send the reader to `grilling`: `triage`, `improve-codebase-architecture`, the domain doc, `link.sh`'s usage example

**Acceptance criteria:**
- [x] `intent` covers every behaviour listed under Desired behavior
- [x] `intent`'s description triggers on an unclear objective, on a stated intent, and on a request to be grilled
- [x] `grilling` and `grill-with-docs` no longer exist in the kit
- [x] `grep -R -E 'grilling|grill-with-docs'` over the kit, excluding `.git` and `.efforts`, finds nothing that names a skill
- [x] `intent` names `.agents/skills/prototype/SKILL.md` for the escape hatch and offers `to-spec` at the end
- [ ] **Maintainer:** in a real session, `intent` on a fresh request shows the four-way sort, at least one gap-fill marked as confident, and at least one offered quick check

**Out of scope:**
- The `to-spec` skill (intent-pipeline/004)
- Validation ladders in `to-slices`, and slimming `implement`'s per-slice rounds
- The `.scratch/` convention (intent-pipeline/005); `intent` refers to "the session's scratch space"
