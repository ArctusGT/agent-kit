---
name: commit-messages
description: >-
  Write git commit messages in a narrative, reasoning-focused style. Use when creating
  commits, drafting commit messages, or when the user asks for help writing
  a commit message.
---

# Commit Messages

Write commit messages that tell the story of *why* a change was made, not
just what changed. The reader should come away understanding the context,
the decision, and the trade-offs.

## Subject Line

Format: `Imperative verb phrase`. A slice the commit works on is named in
the body as `<effort>/<NNN>` (e.g. `agent-tooling/002`), never in the
subject.

- **Imperative mood**: "Add", "Fix", "Remove", "Prevent", "Handle" --
  never past tense.
- **No conventional-commits prefixes**: No `feat:`, `fix:`, `chore:`.
- **50 chars max** Drop words the context already implies --
  e.g. "Add NOT NULL on" beats "Add NOT NULL constraint on" because
  "NOT NULL" already means constraint.

Examples:
- `Show contact subscriptions in CSV`
- `Fix flaky cypress test`
- `Remove unused field from API payload`

## Body

Separate from subject with a blank line. Wrap at 72 characters. Use
backticks for code references (class names, method names, constants)
in the body.

### Narrative Arc

Follow this structure (skip sections that aren't relevant for small
changes):

1. **Context / current state**: What the world looks like before this
   change. Ground the reader.
2. **Problem or motivation**: What's wrong, missing, or desired. Name
   the specific concept or mechanism behind the problem rather than
   describing it loosely. "Not enforced at the DB level" is better
   than "the database didn't match" because it tells the reader
   exactly what kind of gap exists. Go further and name the
   real-world trigger -- the actors, behaviors, or patterns that made
   this change necessary *now*. "Customers hit this on every page
   reload" is stronger than "the cache can go stale" because it
   names who's affected and why it's urgent.
3. **Solution**: The approach or strategy, not a play-by-play of the
   diff. Describe the *shape* of the change rather than enumerating
   files or functions. Use "This commit..." to demarcate from
   background.
4. **Design reasoning**: Why this approach. State constraints or
   principles, discuss alternatives considered. Connect facts to the
   specific concerns they address -- "the table is small" is an
   assertion; "the table is small enough that the lock will be
   near-instant" is reasoning. The reader shouldn't have to infer
   why a fact matters.
5. **Scope boundaries**: What's explicitly *not* included. Use phrases
   like "out of scope for this change" or "a follow-up will..."
6. **Incidental discoveries**: Anything found along the way. "While
   digging into this, the work turned up..."
7. **Future work**: What should happen next, if anything.
8. **Living with this change**: When a change introduces a new
   constraint, convention, or tool, include practical guidance for
   developers who'll encounter it. What should they do when it
   gets in their way? When is it appropriate to override or work
   around it? This is distinct from future work -- it's a playbook
   for coexisting with the change.

### Voice and Tone

- **Impersonal**: the Agent writes the message and the Maintainer is the
  git author, so "I" would put the Agent's reasoning in the Maintainer's
  mouth. Write "This commit...", "X was considered", or name the actor:
  "the Maintainer chose", "the Agent measured".
- **Conversational but precise**: Reads like explaining the change to a
  colleague over coffee, not like formal documentation.
- **Length tracks reasoning, not diff size**: A complex redesign gets
  section headers, diagrams, and benchmarks. But a subtle one-line
  bug fix that took days to hunt down can also warrant a page-long
  explanation tracing the investigation. Write as much as the
  *reasoning* demands, regardless of how many lines changed.

### Enrichment (use when relevant)

- **Section headers**: For long messages, use markdown-style headers
  (`Performance`, `Security`, `Notable choices`, etc.) with underlines
  or blank-line separation.
- **Cross-references**: Cite commit SHAs, slice references, or
  documentation URLs. The reader should be able to trace anything.
  Only reference durable artifacts — planning documents, conversation
  context, and internal phase labels (e.g. "Phase 1") don't survive
  into git history.
- **Existing conventions**: When the change follows an existing
  codebase pattern, name it ("following the pattern used by similar
  validation rules"). This orients the reader without requiring
  them to read other files.
- **Principles/constraints**: Before describing a solution, state the
  constraints that guided it as a numbered list.
- **Alternatives considered**: "X was considered, but it broke
  constraint Y. Z holds all of them."
- **Code snippets / payload shapes**: Include when they clarify the
  change (JSON shapes, SQL, small code examples).
- **Mermaid diagrams**: For complex control flow, show before/after as
  flowcharts or state diagrams.
- **Performance data**: Include benchmarks or query plan comparisons
  when the change has performance implications.
- **Security implications**: Call out security improvements even when
  they're a side effect.
- **Deployment safety**: Note whether the change is safe to deploy at
  any time, requires ordering, or is behind a feature flag. "This
  change was written to be safe to deploy any time."
- **Verification**: Describe how the change was confirmed to work, with
  the method, so it can be taken again: "Verified by...", "Reproduced with..."
- **ENV variables**: When introducing new environment variables, list
  them explicitly.
- **State combinatorics**: For UI work, document the space of possible
  states (e.g. with TypeScript ADTs or a count of combinations).

### Recurring Phrases and Conventions

These signal phrases appear naturally and serve specific roles:

- "This commit..." -- demarcates what the diff does vs. background.
- "Note that..." -- adds caveats the reader should be aware of.
- "While digging into this, the work turned up..." -- incidental findings.
- "out of scope for this change" -- explicit scope boundary.
- "The refactoring budget for this change is spent" -- scope discipline.
- "This is purely a refactor" or "pure refactor (ish)" -- declares no
  behavior change, sometimes with noted small exceptions.
- "A follow-up will..." -- promises future work without blocking now.
- "Longer-term, this probably wants..." -- non-blocking future vision.

## Examples

### Small fix

```
Fix ExampleService class typo

The ExampleService API had a typo, found while browsing the code. A
constant was written as `Inte::ExampleService` rather than
`Integrations::ExampleService`.
```

### Bug fix

```
Fix flaky contact search spec

The contact search spec can flake when generated names for the "match" and
"non-match" contacts happen to overlap. This hard-codes the names for this
specific test and removes generated names from the factory.
```

### Feature with design reasoning

```
Show contact subscriptions in CSV

The CSV export shows no subscription data for archived contacts, because
the association it uses returns only active contacts. The export should
show all subscriptions associated with the contact that are accessible to
the user.

Three principles had to hold:

1. Permission logic stays in the permission layer
2. No N+1: subscription data must be batch-loadable
3. Serializer is active/archived-contact agnostic

Several solutions were considered, and each broke one or more of these
constraints. The one that held all three works
like this:

- DB view aggregates subscription IDs as an array on each
  record. This is structural, no permission logic applied.
- Permission layer filters by tenant ID.
- Manual pre-loading of subscription IDs avoids N+1
```

### Refactor with before/after

```
Refactor session service

In the spirit of "make the change easy, then make the easy change",
this commit re-structures the entire tree of services into a form that
better suits the changes that follow it.

Pure refactor (ish)
-------------------

This is mostly a pure refactor, with a couple small exceptions...

[... sections with mermaid diagrams showing before/after flow ...]
```

### Incremental Rollout Pattern

For risky or large changes, commit messages document a deliberate
incremental strategy:

1. Add nullable column / feature-flagged code (safe to deploy anytime)
2. Backfill existing data or enable flag
3. Make column non-nullable / remove flag (only after step 2 is done)

Each commit explains where it sits in the sequence: "Now that the
existing API keys are cleaned up, it is safe to add the stricter
constraints everywhere."

### Incident Chain Narrative

When fixing bugs introduced by earlier commits, tell the chain story:

```
abc12345 started moving away from archived records. Then def67890
tried to rein it back in, but that is subject to
the default scope again. This commit adds thorough testing to ensure
the query neither *over* selects nor *under* selects records to delete.
```

## Anti-Patterns

- "Updated files" or "Various fixes" -- say what actually changed.
- Starting the body with what the commit does rather than why.
- Hiding who decided ("it was decided") -- name the actor ("the Maintainer chose") or the reason.
- Explaining what the diff shows -- the reader can see the diff. Explain
  the *reasoning* behind it.
- Including coordination notes for the current team ("go talk to X
  about the credentials", "we need to follow up in Slack") -- commit
  messages are for future readers, not present-day task management.
- Adding `feat:` / `fix:` prefixes.

## Workflow

When asked to commit:

1. Read the diff carefully.
2. Identify the *story*: what was the state before, what changed, why.
3. Draft subject line in imperative mood.
4. Write body following the narrative arc.
5. Add enrichment (cross-refs, diagrams, benchmarks) where it helps.
6. Verify line wrapping at 72 characters.
