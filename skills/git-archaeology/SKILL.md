---
name: git-archaeology
description: Recover from git history why something in the repository is the way it is, where a file came from, what a deleted document said, or what a closed ticket recorded. Use when the code, its comments and its nearest README do not explain it; when the Maintainer names a thing by description rather than by a word that appears in the tree; or when a file-scoped git log came back thin.
---

# Git archaeology

The question this answers: *if this is not explained by the code, by a comment,
or by a README next to it, what am I looking for in `.git`?*

Where the issue tracker closes a ticket by deleting its file, and a document's
content migrates as the repository is reorganised, the answer is routinely in
history: in a commit message, in a file that no longer exists, or in a ticket
that was deleted whole. This repo's `docs/agents/issue-tracker.md` says what
closure does to a ticket here. Every one of those is reachable, and none of them
is reachable by the reflex.

## The reflex, and what it actually measures

`git log --follow -- <path>` answers *"which commits edited these bytes"*. That
is a different question from *"where did this come from"*, and it returns a
confident, incomplete answer to the second.

Measured 2026-09-01, in the project this skill was written for, on
`files/job-templates/camera-trap/classify.py`: the file-scoped log returns two
commits, and the one that introduced the file says
*"the camera-trap template is new and original code"*. True, and it omits the
whole provenance. The four commits carrying it wrote into `docs/Cluster.md`,
which no longer exists, so no query scoped to `classify.py` can reach them.

**Search the history, not the path.** The pathspec is the last filter to add,
never the first.

## Steps

1. **Fit the description to a file before searching for the description.** The
   Maintainer names things by what they do, and the tree often has no such word.
   *"The AddaxAI runner"* is `classify.py`; `runner` appears nowhere near it. Say
   which file fits the description and confirm it, so the question becomes
   answerable rather than absent.

2. **Harvest keys from that file.** Read it and collect the strings nothing else
   in the world shares: third-party project names, model and artifact filenames,
   version identifiers, a named decoy, an unusual constant. A key that survives
   in the working tree is an entry point into history; the more specific, the
   fewer false hits.

3. **Search with no pathspec, across every ref.** Both forms, because they find
   different things — messages, then content:

       git log --all --oneline -i --grep=<term>
       git log --all --oneline -S '<string>'

   `--grep` reaches reasoning that was never in a file. `-S` reaches text that
   was in one and was removed.

4. **Read the bodies in ancestry order, forward.** A commit message is a claim
   with a date, and the next commit may correct it. Reading newest-first inverts
   a correction into the position that was overturned:

       git log --reverse --date=short --pretty=format:'%h %ad %s' <old>..<new>

5. **Recover what was deleted, by name.** A deleted file's last content is one
   command away once a commit that touched it is known:

       git log --diff-filter=D --name-only --oneline -- '<glob>'
       git show <sha>^:<path>

6. **Put the sha beside the claim.** Every recovered fact cites the commit it
   came from, so the next reader can re-read the source rather than trust the
   summary. Where two commits disagree, name both and say which is later.

Done when every claim reported carries a sha, and the search has been run for
each key harvested in step 2 rather than only the first that hit.

## What makes a key work

The best keys are the ones a human would never choose to write twice: an
upstream filename, a checkpoint name, a vendor's module path. The worst are
words the repository uses for several unrelated things — a search for `runner`
returns a task runner, a CI runner and a batch-loader comment, none of them the
subject.

**A key absent from the tree is the normal case, not a dead end.** The
load-bearing noun of an answer is often the thing that was removed, or the thing
that was never written down. It reaches the same commits through `--grep`, so
harvest candidate keys from what the recovered commits say and search again.

## Why this needs a skill

Both failures are silent and both look like a finished search.

The file-scoped log **succeeds**. It returns commits, one of them plausibly
answers the question, and nothing indicates that the commits holding the answer
were filtered out by the pathspec.

And a question phrased by description **looks unanswerable**. Grepping the tree
for the Maintainer's word returns nothing or returns noise, and *"there is
nothing like that in this source"* is the natural reply — while the thing exists
under another name and its history is intact.
