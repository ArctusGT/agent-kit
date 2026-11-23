## Sync kit at session start

**Category:** enhancement
**Summary:** A SessionStart hook fast-forwards the kit when that is safe, and otherwise reports how far behind it is
**Status:** ready-for-agent
**blocked-by:** [intent-pipeline/002-prune-dangling-links]

**Current behavior:**
A project's kit stays at the commit its `.agents` submodule pins until someone
updates it by hand. Sessions run skills the kit has since changed or removed,
and never see new ones.

**Desired behavior:**
A kit hook runs at SessionStart. It fetches the kit's origin quietly, with a
short timeout. It fast-forwards the kit to `origin/main` only when all of the
following hold:

- the session is in the project's main checkout, not a worktree, and the project is on its default branch
- the kit is on `main`, with no uncommitted changes
- the project's `.agents` pointer has no uncommitted change, so it still matches the kit's commit
- the kit is behind `origin/main` and can fast-forward

After a fast-forward, the hook:
- runs `link.sh --prune` and prints what it removed
- commits `.agents` plus exactly the tracked links the prune removed, as "Bump kit to <short sha>", so the project's tree stays clean, and pushes nothing
- lists kit entries that are new and not linked in this project, without linking them

In every other case it prints one line, "kit is N behind origin/main: <reason>"
(or ahead, or diverged), and changes nothing. A failed fetch prints one line.
The hook always exits 0.

**Key interfaces:**
- A new kit hook, with a "Wire it up" entry for SessionStart in its header
- `link.sh --prune` (intent-pipeline/002)

**Acceptance criteria:**
- [x] In a throwaway project and kit with origin one commit ahead, and every condition met, the hook fast-forwards, makes one commit touching only `.agents` and the links it pruned, and pushes nothing
- [x] Each condition, broken on its own (worktree, project off its default branch, kit off main, dirty kit, dirty pointer, diverged), leaves both repos unchanged and prints its reason
- [x] A failed fetch prints one line and exits 0
- [x] After a fast-forward that removed a linked skill, the dangling link is pruned, reported, and removed in the bump commit
- [x] A new, unlinked kit entry is listed, not linked
- [x] `--help` prints what it does, what it reads, and that it commits
- [ ] **Maintainer:** after a kit push, a new session in timelab shows the bump commit; report whether that same session already sees the updated skills or only the next one does

**Out of scope:**
- Linking new kit entries automatically
- Pushing either repo
- Syncing a worktree's kit
