# A comment explains a line; it does not carry the design

**A comment says why the line beside it is written the way it is. It never
states what the system guarantees, what another component does, or what the work
is trying to prove.**

Each of those has a home that can be checked, and a comment is not one:

| the claim | where it belongs |
|---|---|
| what the system guarantees | the spec or ticket that claims it, once |
| what the work is trying to prove | that ticket's criteria |
| what was observed to happen | with its subject, saying how it was taken |
| what another component does | nowhere: it is falsified by an edit its reader never sees |

> **The test: can this comment be made false by an edit in a different file?**
> Then it is a claim, not an explanation.
>
> **And: if the code beside it were deleted, would the comment be orphaned, or
> would it still stand?** One that still stands was never explaining that code.
> It was stating a rule, and it will be read as one.

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
- **A present-tense fact that the next reader will take as a rule for the future.**
  "Reads nothing back", "never blocks", "holds no state": each is true when written, 
  but nothing marks it as an observation rather than a constraint. Code changes and 
  the sentence doesn't, so the sentence becomes the constraint.
- **The same assertion in more than one file.** Correct it where it is owned,
  and delete the copies.
- **A measurement in a comment.** `a-measurement-belongs-with-its-subject.md`
  puts it where the thing that produced it lives, and never in a document that
  collects measurements.
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

It wins downstream too. A comment describing one file honestly becomes a line in
a ticket, and a criterion is harder to doubt than a comment —
`a-raised-criterion-can-still-be-wrong.md` is what to do once it has got that
far. This rule is how it does not.
