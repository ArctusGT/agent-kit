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
    ln -s AGENTS.md CLAUDE.md
    git add .gitmodules .agents AGENTS.md CLAUDE.md .claude docs/agents

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

## Where port 22 is blocked

Both `git@github.com:` forms above need outbound SSH on port 22, which campus
egress drops. GitHub answers on 443 as well. Either form below reaches it.

Inline, needing no configuration, which is why a machine that cannot be
configured uses it:

    git clone ssh://git@ssh.github.com:443/OWNER/REPO.git

The `ssh://` scheme is required. `git@ssh.github.com:443/OWNER/REPO.git` looks
equivalent and is not: in that form a colon starts a path, so `443/OWNER/REPO`
is read as a directory name.

A `~/.ssh/config` alias instead, which sets the port and key once and keeps
every remote short:

    Host github-<name>
        HostName ssh.github.com
        Port 443
        User git
        IdentityFile ~/.ssh/github-<name>
        IdentitiesOnly yes

Then `github-<name>:OWNER/REPO.git` is the whole URL, wherever one of the
commands above says `git@github.com:OWNER/REPO.git`.

`IdentitiesOnly yes` earns its place as soon as a second GitHub key exists.
Without it ssh offers every key the agent holds, in the agent's order, and
GitHub authenticates as whichever it recognises first — so a push can land as
the wrong identity and succeed.

Check a key before wiring anything to it:

    ssh -T -p 443 git@ssh.github.com

`Hi USERNAME!` is an account key and reaches every repository that account can
read. `Hi OWNER/REPO!` is a deploy key and reaches exactly one.

## Pulling kit changes into a project

    git submodule update --remote .agents
    .agents/bin/link.sh --list

`--list` after the update shows anything new the kit gained. Nothing links
itself; a new skill reaches the project only when named.

A skill is live as soon as it is linked. Claude Code picks it up through the
symlink without restarting the session, so there is nothing to reload after
`link.sh`.

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

`AGENTS.md` at the project root is a real file, because every project extends
it. `CLAUDE.md` beside it is a symlink to it, because Claude Code reads
`CLAUDE.md` and does not read `AGENTS.md` — measured on 2.1.238, where a root
`AGENTS.md` alone loaded nothing at all. The `@` import inside it is followed,
so the kit's preferences arrive through the symlink.

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

Three files are in play: the project's root `AGENTS.md`, the `CLAUDE.md` symlink
beside it, and the kit's `.agents/AGENTS.md` that the first one imports. Nothing
loads if the `CLAUDE.md` symlink is missing, and it fails silently.

Check it from the project root. A run that answers with the two Golden rules
bullets has the whole chain working:

    claude -p "Quote the two bullets under 'Golden rules' from your loaded instructions."

An agent that ignores a rule or cannot see a skill is almost always a dangling
symlink — the submodule is not checked out. `.agents/bin/link.sh --list` and
`ls -l .claude/rules` both show it.

Still stuck: ask the Maintainer rather than guessing at the layout.
