## To spec

**Category:** enhancement
**Summary:** A `to-spec` skill writes the accepted intent into an effort's spec, the baseline a build follows
**Status:** ready-for-agent
**blocked-by:** [intent-pipeline/001-kit-owns-its-efforts, intent-pipeline/003-intent-aligns-before-a-spec]

**Current behavior:**
The effort tracker says specs are made by a skill that the Maintainer invokes,
and that the skill owns the spec's shape. No such skill exists. `to-slices`
and `implement` both accept a spec, but nothing produces one.

**Desired behavior:**
`to-spec` is invoked by the Maintainer, never by the model, after `intent` has
been accepted. Its shape is adapted from upstream `to-spec`
(https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md).
It reads the accepted intent from the conversation and writes one spec per
effort, `.efforts/<effort>/spec.md`, made from a kit template by a generator.

The spec holds:
- the objectives, each stated so it can be checked
- the unwanteds and what is out of scope
- the accepted premises, each with its proof
- the nice-to-haves, marked as such
- the behaviour to build

It states that it is the baseline: a build follows it, and it changes only
through a new `intent` run (realignment), which rewrites it in place. Git
keeps the earlier versions. Any `.research/` finding promoted into the spec is
removed from `.research/`.

**Key interfaces:**
- `to-spec` skill, `disable-model-invocation: true`
- A spec template in the kit's templates, and a `new-spec <effort>` generator beside `new-slice`, using the same project-or-kit root rule
- `block-new-docs`: a new `spec.md` under `.efforts/` is blocked with a message naming `new-spec`
- The effort tracker's "Creating specs" section names `to-spec`

**Acceptance criteria:**
- [ ] `to-spec` exists, cannot be invoked by the model, and holds the spec's shape
- [ ] `new-spec <effort>` writes `.efforts/<effort>/spec.md` from the template and prints the path; `--help` answers
- [ ] `new-slice` numbering ignores `spec.md`
- [ ] `block-new-docs` blocks a hand-written new `spec.md` and names `new-spec`
- [ ] The spec template has a section for each item listed under Desired behavior, plus the baseline statement
- [ ] `to-spec` removes promoted findings from `.research/`
- [ ] The effort tracker's "Creating specs" section names `to-spec`

**Out of scope:**
- Changing how `to-slices` reads a spec, or adding validation ladders to slices
- Slimming `implement`'s per-slice rounds, or a spec-wide `code-review`
