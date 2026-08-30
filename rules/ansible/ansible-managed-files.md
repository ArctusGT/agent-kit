# Writing a managed file from a task

**Use `ansible.builtin.template` with a `.j2`, not `copy:` with `content:`.**

`ansible_managed` is supplied by the template action plugin. It is not a fact
and not a play var, so `{{ ansible_managed | comment }}` inside a `copy:`
content block fails at runtime:

    Error while resolving value for 'content': 'ansible_managed' is undefined

`copy: content:` is fine only for a literal with no `ansible_managed` header
and no template variables.

## Why this needs a rule

It fails late. Everything upstream converges, then the play dies on the file
write — so the feedback arrives after a long successful run and reads like a
variable-scoping problem rather than a module choice.
