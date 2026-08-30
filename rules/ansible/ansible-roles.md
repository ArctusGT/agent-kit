# A role exists because something asks for it

**Demand pushes supply. A role directory is created in the same commit as the
reference that needs it, and removed in the same commit as the last reference
that did.**

A reference means one of: an entry in a `*_roles` list, a play's `roles:`
block, or an `include_role`/`import_role` name. Nothing else counts — a role
named only in a comment, a doc, or a plan is unreferenced.

## Never

- **Never write a role ahead of demand.** Not "ready for when the host exists",
  not "scaffolded while the context is fresh". Write it when a list needs it.
- **Never leave a role behind after its last reference goes.** Removing the
  entry from a `*_roles` list and keeping the directory is the failure this
  rule exists to prevent.

## Removing one

The removal commit is the whole record — git is the provenance, so write it as
one. It must carry:

- what the role deployed, and to which hosts
- anything it leaves on those hosts that the deletion does not clean up
- every table or document listing roles, which outlives the directory and
  which no audit reports

Settle live residue before or with the deletion. Once the role is gone nothing
in the repository knows what it put on a host.

## Finding one

Reconcile supply against demand: list the role directories, list the
references, and diff them. An orphan is not discoverable by reading the role —
it is obvious the moment the two lists are compared.

## Why this needs a rule

An unreferenced role is not inert. It keeps making claims that nothing
re-checks, and any ledger of what is deployed records them as though they were
still true — including claims about hosts the role has not run on for weeks.
