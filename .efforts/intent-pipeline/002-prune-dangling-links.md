## Prune dangling links

**Category:** enhancement
**Summary:** `link.sh` removes links to kit entries that no longer exist
**Status:** ready-for-agent

**Current behavior:**
`link.sh` makes and re-points symlinks from a project into the kit, but never
removes one. When the kit deletes a skill, rule, command or doc, every project
that linked it keeps a dangling symlink. A provider may still list it, and
`find`/`grep` without `-L` hide it.

**Desired behavior:**
`link.sh --prune` removes every symlink in the directories `link.sh` links
into (rules, skills, commands, agent docs) whose target points into the kit
and no longer exists. It prints each removal. Real files are left alone, as
local overrides always are, and so are links pointing anywhere other than the
kit. `--list` shows a dangling link as gone, so the problem is visible before
anything is pruned.

**Key interfaces:**
- `link.sh --prune`: new mode
- `link.sh --list`: a state for a dangling link

**Acceptance criteria:**
- [x] In a throwaway project linking a kit entry that is then removed, `--prune` removes that link and prints it
- [x] A real file at a link target and a symlink pointing outside the kit both survive `--prune`
- [x] A second `--prune` run removes nothing and says so
- [x] `--list` shows a dangling link with a distinct state
- [x] `link.sh --help` describes `--prune`

**Out of scope:**
- Linking newly added kit entries automatically
- Un-wiring hooks from `.claude/settings.json`
