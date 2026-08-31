# Running a playbook without the Maintainer

**The Agent may run a playbook itself when it is read-only AND vault-free. Both
conditions, checked every time. Everything else is the Maintainer's.**

## Read-only

No task may change a host. The play uses query modules only: `uri` with a GET,
`command`/`shell` whose command merely reads, `find`, `stat`, `slurp`,
`include_vars`, `set_fact`, `debug`, `assert`, plus fact gathering.

- **`changed_when: false` does not make a task read-only.** It is a reporting
  flag. The module decides, and for `command` the ARGUMENT decides: the module
  name is identical whether the statement is a `SELECT` or a `DROP`.
- **`become: true` is fine.** A socket table, a firewall list and a database
  schema all need privilege, and privilege is orthogonal to whether anything
  gets written.

## Vault-free

No `vars_files` under `vault/`, and no `vault_*` variable referenced anywhere in
the play.

Read-only does not imply vault-free. `playbooks/audit.yml` changes nothing and
is still the Maintainer's, because it loads `vault/proxmox.yml`.

## The invocation

`ansible.cfg` names a vault password script and it runs on every invocation from
the repo root, so a locked vault fails a vault-free play, and fails
`--syntax-check` with it. Only `vault/*` holds ciphertext, so a play that loads
none of it decrypts nothing and any password satisfies startup. Write a dummy
password file in the scratchpad and point at it:

    ANSIBLE_VAULT_PASSWORD_FILE=<scratchpad>/dummy-vault-pass ansible-playbook <play>

Run from the repo root; `ansible.cfg` is read from cwd only, and without it
there is no inventory to target. A vault-BEARING play run this way fails at
decryption rather than proceeding, which is what makes the dummy safe rather
than a way around the lock.

## Still the Maintainer's

- Anything that converges, **including `--check`**. It still connects, and not
  every module implements it faithfully.
- Ad-hoc `ansible -m` against real hosts. Same reasoning as scripts being
  files: an inline command cannot be reviewed before it runs, and is gone
  afterwards.

## Unchanged by this

The result is read from `logs/ansible.log`, which is credential-bearing. A
one-off probe lives in the scratchpad; anything committed goes in `playbooks/`.

## Why this needs a rule

Both conditions fail quietly, in opposite directions.

Vault-freeness cannot be established by reading the play, because the password
script runs regardless of what the play loads, so the check that looks
sufficient passes a play that will die on startup. And read-only-ness is
invisible at the module level: `command` says nothing about whether its argument
writes.
