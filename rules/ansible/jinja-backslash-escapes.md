# A backslash escape in a Jinja expression is not reliable

**Never depend on a backslash escape inside a Jinja expression in a playbook or a
template. Write the construct that needs none.**

A YAML folded scalar (`>-`) does not process escapes, and what reaches Python is
not what the expression looks like it says. The pattern still compiles. It simply
matches nothing.

## Substitutions

| instead of | write | why |
|---|---|---|
| `\.` | `[.]` | character class, no escape |
| `\$` | `[$]` | same |
| `\s` | a literal space | the input's whitespace is known |
| `split('\n')` | `regex_findall('(?m)^...')` | `(?m)` anchors per line with no newline literal |

Each expresses the intent without a backslash. Where a new case appears, find
the construct that needs no escape rather than escaping harder.

## Why this is worse than a normal bug

It fails **silently and inverted**. The expression evaluates, produces an empty
list or an unsplit string, and the surrounding logic then reports a confident
wrong answer: a healthy fleet described as broken, or a filter that quietly
filters nothing. A regex that substitutes nothing leaves the placeholder it was
meant to replace, and the query built from it runs against a literal.

## The check that catches it

**Evaluate the expression against real input before trusting it**, on localhost
with the actual captured output.

Reading the code does not catch this; reading it is exactly what makes it look
correct. Only running it against real input distinguishes a pattern that matches
from one that compiles.
