# The shape of a README

**Every README in this repository, without exception. Commands first,
explanation after, and never the complete story.**

## The order

1. **Who the document is for.** One or two sentences.
2. **The exact commands, end to end**, from logging in to reading the result.
   Nothing between them the reader does not type.
3. **The explainers**, below the commands, and only for what the commands did
   not make obvious.
4. **How each file in the directory is used**: parameters, common errors, and
   troubleshooting an agent or a search would not reach.

**Never open with principles the reader has not arrived at yet.** The Agent
knows the subject and the reader does not, so an explainer placed above the
thing it explains is read by nobody.

## What to leave out

**If an agent holding this file, or a search, answers it easily, leave it out.**

A gloss on a command runs two words to one short sentence, and only where the
command is not self-evident. Anything longer is an explainer and belongs below.

A README never needs to be the whole story. It needs enough to make sense,
enough for an agent to close the gaps, and a line telling the reader to ask when
still lost. Written for someone with no background in the subject, and not a
paste from an agent.

## Say which context is which

Text is the worst form of communication. Anything that can be read two ways will
be, so the context is stated where it changes rather than left to the reader.

- **One word does one job.** A term carrying several meanings is several silent
  changes of context wearing one label. Name the specific thing instead.
- **Plain word first, formal term in quotes after it**, once per file, so the
  reader can look the formal one up and does not need to: prerequisite, or
  "prereq" ("edge"); rewrite ("re-flow").
- **Every acronym and document code is expanded where it is first raised.** This
  one binds every document, not only a README. Expand it in the prose at first
  use: a glossary table alone does not discharge it, because a reader arriving
  mid-document never sees the top. Where a file carries many codes, write both,
  and say in the table that the prose expands them too.
- **Where one short form carries two meanings in the same file, spell the rarer
  one out in full every time.** A table entry saying which meaning is intended
  is not enough; the collision is met at the point of use.

## Why this needs a rule

A README can read as authoritative and be unusable, and the author cannot tell.
The Agent reads all of it happily, having no task to lose track of. The reader
following it has one.

An unexpanded acronym is worse than jargon, because it reads as a citation. The
Agent has just read the source and the reader has not, so a code that is
transparent while drafting is opaque a week later to everyone including the
Agent that wrote it. The cost is asymmetric: expanding is a few words, and
omitting it costs the reader the document.

The collision is the half that survives review. One reference file used a
two-letter short form for a numbered principle throughout, and for intellectual
property in a single paragraph quoted from another source. Both were correct,
neither was signposted, and nothing in the file could reveal the switch.
