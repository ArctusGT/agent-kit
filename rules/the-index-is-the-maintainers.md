# The index is the Maintainer's

**The Agent never stages. The Maintainer reviews drafted work and stages what
they accept, so what is staged is what has been agreed to and nothing else.**

An Agent that stages its own work commits the Maintainer's review state along
with it, under a message describing neither.

## The default loop

1. **The Agent drafts and stops.** It says what it changed and why, in the chat.
   It does not commit.
2. **The Maintainer reviews and stages** what they accept — in lazygit, or
   however they like.
3. **The Agent reads the staged set, then commits it.**

       git diff --cached --name-only
       git commit -F <message-file>

   The message describes exactly the staged set. Where the staged set is not
   what the Agent expected, it says so and stops rather than writing a message
   that covers the difference.
4. **The Agent then asks about what is still unstaged.** An unstaged change has
   not been agreed to. It is not forgotten, not rejected, and not the Agent's to
   revert or re-edit.

## Where the Maintainer asks the Agent to carry work through

Some work is handed over whole — build it, verify it, commit as you go. There
the Agent commits by explicit path and still stages nothing:

    git commit -F <message-file> -- <path> <path>

That form takes the working tree at those paths and ignores the index
completely, so a Maintainer reviewing in parallel is never disturbed.

## Never

- **`git add -A`, `git add .`, or a bare directory** — each sweeps up whatever
  the Maintainer was part-way through deciding about.
- **`git reset`, `git stash`, `git checkout -- <path>`, `git restore`** — all
  discard staged state, and none of it is the Agent's.
- **A commit whose message was written before its contents were read.** The
  staged set is established first; the message is written to fit it.

The one carve-out: a file the Agent has just created is untracked, and
`git commit -- <path>` cannot reach it. `git add <that exact path>` is
permitted — named in full, one path at a time, never a glob and never a
directory.

## Why this needs a rule

Staging is the Maintainer's only channel for "I have read this and I accept
it", and it is silent. Nothing in a commit announces that half of it was
somebody else's in-progress review, and the diff still applies cleanly, so the
usual signals — a conflict, a failing check, a broken build — all stay quiet.

It is found later, by reading a commit message that does not mention what the
commit contains.
