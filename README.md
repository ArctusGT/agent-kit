# agent-kit

Rules, skills and issue-tracker conventions shared across the Maintainer's
projects. It is consumed as a git submodule at `.agents/`, and each project
picks which entries it wants.

## Adding it to a project

On the workstation, from the project root. Replace `<you>` with the GitHub
account.

    git submodule add git@github.com:<you>/agent-kit.git .agents
    .agents/bin/link.sh --list
    .agents/bin/link.sh --all
    cp .agents/AGENTS.md.template AGENTS.md
    git add .gitmodules .agents AGENTS.md .claude docs/agents

`--list` prints every entry and whether the project has it. `--all` links the
generic rules, all skills, all commands and the issue-tracker docs; the Ansible
rules are left out and asked for by name:

    .agents/bin/link.sh --group ansible

Then edit `AGENTS.md` — the first line imports the shared preferences, the rest
is this project's.

## Cloning a project that already uses it

    git clone --recurse-submodules git@github.com:<you>/<project>.git

Without `--recurse-submodules` the symlinks dangle and no rule or skill loads.
On an existing clone:

    git submodule update --init .agents

## Pulling kit changes into a project

    git submodule update --remote .agents
    .agents/bin/link.sh --list

`--list` after the update shows anything new the kit gained. Nothing links
itself; a new skill reaches the project only when named.

## Pushing a kit change from inside a project

Edits made in `.agents/` are edits to this repository.

    cd .agents
    git add <path>
    git commit
    git push
    cd ..
    git add .agents

The last line records the new kit commit in the project. Other projects pick it
up with `git submodule update --remote`.

## Shared or project-specific

A **symlink** under `.claude/` points into the kit and is shared. A **real
file** at the same path is this project's own and `link.sh` leaves it alone —
it reports `local override` and moves on. That is the whole mechanism: to stop
sharing a rule, replace the symlink with a copy.

`git status` distinguishes them, so what is shared is visible without reading
anything.

## Why the entries are linked one at a time

`.claude/skills` stays a real directory holding a mix of symlinks and real
directories. Symlinking the whole of `.claude/skills` at the kit would leave a
project-specific skill nowhere to live.

## Why `.claude/` still exists

Claude Code discovers skills, commands and rules under `.claude/` only. `.agents/`
is where the files live; `.claude/` is how the agent finds them.

`AGENTS.md` is a real file rather than a symlink because every project extends
it, and because `@` import is native — no symlink to break on a checkout that
does not support them.

## The files

| path | what it is |
|---|---|
| `AGENTS.md` | The Maintainer's preferences: voice, planning, commands, comments. Reaches an agent through the `@.agents/AGENTS.md` line at the top of the project's own root `AGENTS.md`. Never linked into `.claude/`. |
| `bin/link.sh` | The linker. Run from the project root, not from `.agents/`. Refuses to run if the kit is not inside the project. Re-running is safe — it re-points symlinks and never touches a real file. |
| `AGENTS.md.template` | Starting point for a project's `AGENTS.md`. Copied, not linked. |
| `rules/*.md` | Generic rules. Land at `.claude/rules/<name>.md`. |
| `rules/ansible/*.md` | Ansible rules. Land in the same flat `.claude/rules/`, so a name must not collide with a generic rule. |
| `skills/<name>/` | One skill per directory, `SKILL.md` plus its references. `agents/openai.yaml` is the Codex counterpart and travels with it. |
| `commands/*.md` | Slash commands. Land at `.claude/commands/<name>.md`. |
| `docs/agents/*.md` | Issue-tracker conventions the skills read by path. Land at `docs/agents/` in the project, not under `.claude/`, because that is where the skills look. |

`docs/agents/triage-labels.md` is written to be overridden: the right-hand
column is per-tracker. Replace the symlink with a real file to change it.

## When something does not load

Two files are named `AGENTS.md`: the project's at the root, and the kit's at
`.agents/AGENTS.md`. The root one imports the kit one. Confirm the import took
by asking a fresh agent to quote a line from the shared preferences — a failed
import loads nothing and says nothing.

An agent that ignores a rule or cannot see a skill is almost always a dangling
symlink — the submodule is not checked out. `.agents/bin/link.sh --list` and
`ls -l .claude/rules` both show it.

Still stuck: ask the Maintainer rather than guessing at the layout.
