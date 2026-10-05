# The Agent commits its own work; the rest of the index is the Maintainer's

**The Agent stages and commits its own work as it goes, without waiting for
the Maintainer to stage it. Whatever else is in the index belongs to the
Maintainer and is never touched.**

## The default loop

1. **The Agent finishes one small fix and verifies it.**
2. **The Agent commits it by explicit path:**

       git add <path>
       git commit -F <message-file> -- <path> <path>

   One path at a time on `git add`, never a glob and never a directory. The
   message is written after the diff of those paths has been read, and
   describes exactly them.
3. **The Agent says in the chat what it committed**, by commit and by file.
   The Maintainer reviews in the log and asks for a revert where it is wrong.

## Slices stay with the Maintainer

- **The Agent never stages or commits a new slice.** Drafting one is allowed
  (`docs/agents/effort-tracker.md`); a staged slice is an accepted one, and
  accepting is the Maintainer's.
- **The Agent deletes a slice only when the Maintainer says to.** Closing is
  the Maintainer's call. The deletion is `rm` and a commit by path, in a
  commit of its own.
- Ticking a criterion and setting `ready-for-closure` go in the commit with
  the work they describe.

## Never

- **`git add -A`, `git add .`, or a bare directory.** Each sweeps up whatever
  the Maintainer was part-way through.
- **`git reset`, `git stash`, `git checkout -- <path>`, `git restore`.** All
  discard state that is not the Agent's.
- **A bare `git commit`.** It takes the whole index, including anything the
  Maintainer staged. Name the paths.
- **A commit holding a file the Agent did not change in this task.** Where a
  path already had the Maintainer's edits in it, the Agent asks first.

## Why this needs a rule

Review moved from the index to the log: the Maintainer reads what was
committed rather than staging what is accepted. The protections on the
index stay, because the failure they prevent is silent either way. A commit
that swept up somebody else's half-reviewed work applies cleanly, and
nothing in its message says so.
