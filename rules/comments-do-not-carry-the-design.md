# A comment explains a line; it does not carry the design

**A comment says why the line beside it is written the way it is. It never
states what the system guarantees, what another component does, or what the work
is trying to prove.**

Each of those has a home that can be checked, and a comment is not one:

| the claim | where it belongs |
|---|---|
| what the system guarantees | the spec or ticket that claims it, once |
| what the work is trying to prove | that ticket's criteria |
| what was observed to happen | the build record, carrying its date |
| what another component does | nowhere: it is falsified by an edit its reader never sees |

> **The test: can this comment be made false by an edit in a different file?**
> Then it is a claim, not an explanation.

## What it looks like when it goes wrong

A hypothesis in a spec, correctly framed there as the thing nothing yet tests,
restated as an invariant in a file header. The header then reads as a
requirement rather than a guess, so the next agent defends it instead of
changing it, and every file repeating it makes it harder to question.
`verify-before-relocating.md` covers the copying: repetition is not
corroboration.

**A file header says what the file is.** One or two lines. It does not say what
the design is for.

## Never

- **A design property in a file header.** Not what the system proves, not what
  another component cannot see, not what the prototype exists to test.
- **The same assertion in more than one file.** Correct it where it is owned,
  and delete the copies.
- **A measurement in a comment.** `provenance-and-measurement.md` puts it in the
  build record with its date and how it was taken.
- **A comment written to correct a misleading comment.** Delete the wrong one.

`ansible/deployed-file-comments.md` is this rule for a file written onto a host,
where the copy cannot be reached by reading git history at all.

## Why this needs a rule

It reads as rigour and nothing rejects it. An imperative sentence in a header is
indistinguishable from a requirement, and it outlives everyone who knew it was a
guess.

The failure is not that such a comment goes stale. It is that it **wins**: an
agent asked to change the design argues the header back at the Maintainer,
having never established that anything authored it on purpose.
