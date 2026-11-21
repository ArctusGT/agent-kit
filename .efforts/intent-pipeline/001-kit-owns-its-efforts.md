## Kit owns its efforts

**Category:** enhancement
**Summary:** `new-slice` drafts into the kit's own `.efforts/` when run from inside the kit
**Status:** ready-for-agent

**Current behavior:**
`new-slice` always treats the directory holding the kit as the project, so a
slice about the kit, drafted from any project that links it, lands in that
project's tracker. Other projects using the kit never see it. The kit has no
`.efforts/` of its own, and `block-new-docs` only guards `.efforts/` at the
project root, so a hand-written slice under the kit goes unchecked.

**Desired behavior:**
Where `new-slice` runs from at or below the kit's own working tree, the kit is
the project: the slice is written under the kit's `.efforts/<effort>/` and
numbered against the kit's history. Run from the project root, nothing
changes. `block-new-docs` blocks a new slice file under the kit's `.efforts/`
the same way it blocks one under the project's, and names how to make it.

**Key interfaces:**
- `new-slice`: how it picks the project root
- `block-new-docs`: the path test for a new slice
- The effort tracker doc: where the kit's own work is tracked

**Acceptance criteria:**
- [ ] Run from inside the kit, `new-slice <effort> <slug>` writes under the kit's `.efforts/` and prints that path
- [ ] Numbering inside the kit counts the kit's files and history, not the project's
- [ ] Run from the project root, `new-slice` writes where it does today
- [ ] `block-new-docs` blocks writing a new `.efforts/<effort>/<name>.md` under the kit, with a message naming `new-slice` run from inside the kit
- [ ] `new-slice --help` states both cases
- [ ] The effort tracker doc says work on the kit is tracked in the kit's own `.efforts/`

**Out of scope:**
- Moving slices that already exist in any project
- `slice-view` reading the kit's tracker
