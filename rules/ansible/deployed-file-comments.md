# Comments on a managed host

**A file on a host carries exactly one kind of comment: the ownership banner.
Nothing else. Documentation lives in this repository.**

Two forms, and no third:

| what Ansible owns | form |
|---|---|
| the whole file (`template`, `copy`) | banner at top **and** tail |
| a fragment of someone else's file | `blockinfile` with `marker_begin` / `marker_end` |

The banner text is `ansible_managed`, set once in `ansible.cfg`. Templates
render it with `{{ ansible_managed | comment }}` at both ends, so the wording is
single-sourced and cannot drift between files. Keep it static; a banner
carrying a timestamp or a run id churns every managed file on every converge.

## Where the reasoning goes instead

`{# ... #}`. A Jinja comment is stripped at render, so it stays in the
template and never reaches the host. Converting a `#` line to `{# #}` loses
nothing and is the fix for almost every existing case.

Anything longer than a couple of lines belongs in the repository's
documentation, cited by a stable key from the file that would otherwise have
carried it. The document holding the note carries a line at its top saying what
the keys are.

## Never

**Do not write a comment onto a host with `lineinfile` or `replace`.** A
fragment marked by `blockinfile` can be removed later by `state: absent`; a
line poked into a stock file cannot be found again except by the string
itself.

## Why this needs a rule

A comment written onto a host is a copy of repository knowledge that nothing
regenerates, nothing checks, and no audit can see. It rots in place, and it
rots on hardware rather than in git, so the usual recovery, reading the
history, does not reach it.

The trap is that the instinct is usually right and the medium is wrong: a
comment written onto a host **to correct a misleading comment** reproduces the
defect one layer down.
