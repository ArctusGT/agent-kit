#!/usr/bin/env bash
# Claude Code SessionStart hook. Fetches the kit's origin and, when that is
# safe, fast-forwards the kit to origin/main. CHANGES THE PROJECT'S GIT
# HISTORY: after a fast-forward it commits .agents, plus the tracked links that
# link.sh --prune removed and nothing else, as "Bump kit to <short sha>", so the
# project's tree stays clean. The commit runs the project's own commit hooks
# and signing, unbounded. It pushes nothing, in either repo. If the commit
# fails it unstages its own paths and says so.
#
# It fast-forwards only when all of these hold; otherwise it prints one line,
# "kit is N behind origin/main: <reason>" (or ahead, or diverged), and changes
# nothing:
#   - the session is in the project's main checkout, not a worktree, and the
#     project is on its default branch (origin/HEAD, else main)
#   - the kit is on main with no uncommitted changes
#   - the project's .agents pointer has no uncommitted change
#   - the kit is behind origin/main and can fast-forward
# Nothing is printed when the kit already matches origin/main. A failed or
# slow fetch prints one line and stops. It always exits 0.
#
# After a fast-forward it runs link.sh --prune, prints what that removed, and
# commits those removals with the bump. It then lists the kit entries that are
# new and not linked here, without linking them.
#
# Reads the hook's JSON from stdin (cwd) only when CLAUDE_PROJECT_DIR is unset.
# The project is $CLAUDE_PROJECT_DIR, else the JSON's cwd (needs jq), else the
# current directory, and must be a repo root, else it is skipped. Needs git.
# KIT_SYNC_FETCH_TIMEOUT sets the fetch limit in whole seconds (default 5; any
# other value gives the default). Takes no arguments; -h or --help prints this header, and
# any other argument is refused without acting.
#
# Wire it up in the project's .claude/settings.json:
#   "SessionStart": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/sync-kit.sh" }] }]
#
FETCH_TIMEOUT=${KIT_SYNC_FETCH_TIMEOUT:-5}
KIT=.agents
case $FETCH_TIMEOUT in ''|*[!0-9]*) FETCH_TIMEOUT=5 ;; esac

case "${1:-}" in
  -h|--help) awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"; exit 0 ;;
  '') ;;
  *) echo "sync-kit: takes no arguments (see --help), nothing done"; exit 0 ;;
esac

# No -e: every failure below is reported as one line, and the hook exits 0.
set -uo pipefail

say() { echo "sync-kit: $*"; }

# git fetch for the kit, stopped after FETCH_TIMEOUT seconds. macOS has no
# timeout(1), so poll the fetch rather than leave a watchdog behind holding
# the hook's output open.
fetch_kit() {
  local pid ticks=0
  GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=$FETCH_TIMEOUT" \
    git -C "$KIT" fetch --quiet origin >/dev/null 2>&1 &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$ticks" -ge $((FETCH_TIMEOUT * 10)) ]; then
      kill "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      return 1
    fi
    sleep 0.1
    ticks=$((ticks + 1))
  done
  wait "$pid"
}

# The first reason the kit must not be fast-forwarded, or nothing.
blocker() {
  local gitdir common branch default kit_branch
  gitdir=$(cd "$(git rev-parse --git-dir)" && pwd -P)
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
  [ "$gitdir" = "$common" ] || { echo "the session is in a worktree"; return; }

  branch=$(git symbolic-ref --short -q HEAD || true)
  default=$(git symbolic-ref --short -q refs/remotes/origin/HEAD 2>/dev/null || true)
  default=${default#origin/}
  default=${default:-main}
  [ "$branch" = "$default" ] || { echo "the project is on ${branch:-a detached HEAD}, not $default"; return; }

  kit_branch=$(git -C "$KIT" symbolic-ref --short -q HEAD || true)
  [ "$kit_branch" = main ] || { echo "the kit is on ${kit_branch:-a detached HEAD}, not main"; return; }

  [ -z "$(git -C "$KIT" status --porcelain)" ] || { echo "the kit has uncommitted changes"; return; }
  git ls-files --stage -- "$KIT" | grep -q '^160000 ' ||
    { echo "the project's $KIT is not a submodule"; return; }
  # The project records the kit as a gitlink. --ignore-submodules=dirty keeps
  # the kit's own working tree out of this, leaving a moved pointer or a
  # staged change.
  [ -z "$(git status --porcelain --ignore-submodules=dirty -- "$KIT")" ] ||
    { echo "the project's $KIT pointer is not at the kit's commit, or has a staged change"; return; }
}

# Entries of link.sh --list as "<group>:<name> <state>", one per line, the
# group keeping its colon, leaving out the "gone" section. A state of "-"
# means the entry is not linked in this project.
kit_entries() {
  "$KIT/bin/link.sh" --list 2>/dev/null |
    awk '/^[a-z]+:$/ {g=$1; next} g != "gone:" && /^  / {n=$1; $1=""; sub(/^ +/, ""); print g n, $0}'
}

# Print the entries that are in $2 but not $1 and are not linked, as
# "<group> <name>". Both are kit_entries output, taken before and after the
# fast-forward.
report_new_unlinked() {
  local entries_before=$1 entries_after=$2 new_unlinked
  new_unlinked=$(awk 'NR==FNR {seen[$1]; next} $2 == "-" && !($1 in seen) {print $1}' \
    <(printf '%s\n' "$entries_before") <(printf '%s\n' "$entries_after"))
  [ -n "$new_unlinked" ] || return 0
  say "new in the kit and not linked here (link with $KIT/bin/link.sh <name>):"
  printf '%s\n' "$new_unlinked" | sed 's/^/  /; s/:/ /'
}

# Fast-forward the kit, prune, and commit the bump with the links the prune
# removed, then report. A failed commit unstages the paths this staged.
sync_kit() {
  local entries_before entries_after sha pruned link
  local paths=("$KIT")
  entries_before=$(kit_entries)
  git -C "$KIT" merge --ff-only --quiet origin/main >/dev/null 2>&1 || { say "fast-forward failed, kit left as it was"; return; }
  sha=$(git -C "$KIT" rev-parse --short HEAD)

  pruned=$("$KIT/bin/link.sh" --prune 2>&1 | grep -v '^nothing to prune$' || true)
  # Only a tracked link can go in the commit; an untracked one is just gone.
  for link in $(printf '%s\n' "$pruned" | awk '$1 == "x" {print $2}'); do
    [ -n "$(git ls-files -- "$link")" ] && paths+=("$link")
  done

  if git add -- "${paths[@]}" >/dev/null 2>&1 &&
     git commit --quiet -m "Bump kit to $sha" -- "${paths[@]}" >/dev/null 2>&1; then
    say "kit fast-forwarded to $sha, committed as \"Bump kit to $sha\" with ${#paths[@]} path(s)"
  else
    git restore --staged -- "${paths[@]}" >/dev/null 2>&1
    say "kit moved to $sha but the bump commit failed, its paths are unstaged"
  fi
  [ -z "$pruned" ] || { say "pruned:"; printf '%s\n' "$pruned"; }

  entries_after=$(kit_entries)
  report_new_unlinked "$entries_before" "$entries_after"
}

main() {
  local input cwd behind ahead reason
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    PROJECT=$CLAUDE_PROJECT_DIR
  else
    cwd=
    if [ ! -t 0 ] && command -v jq >/dev/null; then
      input=$(cat)
      cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
    fi
    PROJECT=${cwd:-$PWD}
  fi
  cd "$PROJECT" 2>/dev/null || { say "no project directory, skipped"; return; }
  PROJECT=$(pwd -P)

  command -v git >/dev/null || { say "needs git, skipped"; return; }
  [ "$(git rev-parse --show-toplevel 2>/dev/null)" = "$PROJECT" ] ||
    { say "$PROJECT is not a repo root, skipped"; return; }
  [ -e "$KIT/.git" ] || { say "no kit at $KIT, skipped"; return; }

  fetch_kit || { say "could not fetch the kit's origin (limit ${FETCH_TIMEOUT}s), kit left as it was"; return; }

  behind=$(git -C "$KIT" rev-list --count HEAD..origin/main 2>/dev/null) || { say "kit has no origin/main, skipped"; return; }
  ahead=$(git -C "$KIT" rev-list --count origin/main..HEAD)
  [ "$behind" -gt 0 ] || [ "$ahead" -gt 0 ] || return 0  # matches origin/main: silent

  reason=$(blocker)
  if [ -n "$reason" ]; then
    if [ "$behind" -gt 0 ]; then say "kit is $behind behind origin/main: $reason"
    else say "kit is $ahead ahead of origin/main: $reason"; fi
    return
  fi
  if [ "$ahead" -gt 0 ]; then
    if [ "$behind" -gt 0 ]; then say "kit is $behind behind origin/main: diverged, with $ahead of its own"
    else say "kit is $ahead ahead of origin/main: nothing to pull"; fi
    return
  fi
  sync_kit
}

main
exit 0
