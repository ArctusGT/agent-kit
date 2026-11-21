## Sweep scratch and research

**Category:** enhancement
**Summary:** A SessionStart hook gives each session a `.scratch/<session-id>/` and sweeps stale scratch and research
**Status:** ready-for-closure

**Current behavior:**
Scratch work goes to the harness's scratchpad, outside the repo, so it loses
its repo context and nothing in the repo can clean it up. `.research/` grows
until someone tidies it by hand. Neither directory is ignored by every project
that links the kit.

**Desired behavior:**
A kit hook runs at SessionStart and, inside the project only:
- creates `.scratch/<session-id>/`, using the session id from the hook's input, and prints its path so it lands in the session's context
- removes each other folder under `.scratch/` that has nothing inside modified in the last 24 hours
- removes files under `.research/` not modified in 14 days, and any folders left empty
- prints what it removed
- never follows symlinks, and leaves a git-tracked file alone, reporting it
- never fails the session: on any error it reports and exits 0

When `link.sh` wires this hook, it also makes sure the project's `.gitignore`
lists `.scratch/` and `.research/`.

The kit's guidance points at the session's `.scratch/<session-id>/` wherever
it now says "the scratchpad": the Scripts section of AGENTS.md, `implement`'s
ledger and proof, and the inline-script hook's message. The research rule
mentions the 14-day sweep, and that alignment work is cheaper to redo than
stale findings are to trust.

**Key interfaces:**
- A new kit hook, with a "Wire it up" entry for SessionStart in its header
- `link.sh` hook wiring: the `.gitignore` lines
- The 24-hour and 14-day thresholds, as named constants in the hook's header

**Acceptance criteria:**
- [x] Given a seeded project, the hook creates the session's folder and prints its path
- [x] A `.scratch/` folder older than 24 hours is removed; the current session's folder and a recently touched one survive
- [x] A `.research/` file older than 14 days is removed; a newer one survives; emptied folders go
- [x] A symlink under either directory is not followed, and a tracked file is left alone and reported
- [x] The hook exits 0 when the project has neither directory, and when a removal fails
- [x] `--help` prints what it does, what it reads and that it deletes
- [x] Wiring it with `link.sh` adds both directories to `.gitignore` once, and running it again adds nothing
- [x] The kit's guidance names `.scratch/<session-id>/` in place of the scratchpad, as listed under Desired behavior
- [x] **Maintainer:** a new session in timelab shows its scratch path, and a scratch folder seeded as old is gone

**Out of scope:**
- Where `handoff` writes its document
- Configurable thresholds
