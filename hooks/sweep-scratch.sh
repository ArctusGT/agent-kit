#!/usr/bin/env bash
# Claude Code SessionStart hook. Gives the session a working folder at
# .scratch/<session-id>/ in the project and prints its path into the session's
# context, then sweeps stale material. DELETES FILES, inside the project only:
#   - each other folder under .scratch/ with nothing inside modified in the
#     last 24 hours
#   - files under .research/ not modified in 14 days, then every empty folder
# Prints what it removed. Never follows a symlink (a stale link is removed
# itself, its target is not touched), and leaves a git-tracked file alone,
# reporting it. Never fails the session: on any error it says so and exits 0.
#
# Reads the hook's JSON from stdin (session_id, cwd). The project is
# $CLAUDE_PROJECT_DIR, else the JSON's cwd, else the current directory.
# Needs jq and git. Takes no arguments; -h or --help prints this header, and any
# other argument is refused without sweeping.
#
# A directory holding a .git (a nested repo) is left alone whole and reported.
#
# Wire it up in the project's .claude/settings.json:
#   "SessionStart": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/sweep-scratch.sh" }] }]
#
# link.sh also makes sure the project's .gitignore lists .scratch/ and .research/.
SCRATCH_MAX_AGE_HOURS=24
RESEARCH_MAX_AGE_DAYS=14

case "${1:-}" in
  -h|--help) awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"; exit 0 ;;
  '') ;;
  *) echo "sweep-scratch: takes no arguments (see --help), nothing swept"; exit 0 ;;
esac

set -uo pipefail

REPOS=()

# True when $1 is inside one of the nested repos found by find_repos.
in_repo() {
  local r
  for r in ${REPOS[@]+"${REPOS[@]}"}; do
    case $1 in "$r"|"$r"/*) return 0 ;; esac
  done
  return 1
}

# Fill REPOS with each directory under $1, $1 included, that holds a .git, and
# report it. The sweep never touches a repo's files or folders.
find_repos() {
  local g
  REPOS=()
  while IFS= read -r -d '' g; do
    REPOS+=("${g%/.git}")
    echo "sweep-scratch: kept nested git repo ${g%/.git}"
  done < <(find -P "$1" -name .git -print0)
}

# Remove the untracked files and links under relative path $1, reporting
# tracked ones, then every empty folder below $1. An optional $2 limits it to
# those older than that many minutes. A git answer other than "tracked" (0)
# or "not tracked" (1) is a git failure: the file is left alone.
# Symlinks are matched as links by find -P and never entered.
sweep_files() {
  local dir=$1 age=() f
  [ -n "${2:-}" ] && age=(-mmin +"$2")
  find_repos "$dir"
  # ${age[@]+...} expands to nothing for an empty array; a bare "${age[@]}" is
  # an unbound variable under set -u in macOS's bash 3.2.
  while IFS= read -r -d '' f; do
    in_repo "$f" && continue
    git ls-files --error-unmatch -- "$f" >/dev/null 2>&1
    case $? in
      0) echo "sweep-scratch: kept tracked file $f" ;;
      1) if rm -f -- "$f"; then echo "sweep-scratch: removed $f"; else echo "sweep-scratch: could not remove $f"; fi ;;
      *) echo "sweep-scratch: git failed on $f, left alone" ;;
    esac
  done < <(find -P "$dir" \( -type f -o -type l \) ${age[@]+"${age[@]}"} -print0)
  # Deepest first, so a folder emptied by its children's removal goes too.
  while IFS= read -r -d '' f; do
    in_repo "$f" && continue
    [ -z "$(ls -A "$f")" ] || continue
    if rmdir -- "$f"; then echo "sweep-scratch: removed $f/"; else echo "sweep-scratch: could not remove $f/"; fi
  done < <(find -P "$dir" -mindepth 1 -depth -type d -print0)
}

# Give the session its folder, then sweep each other folder under .scratch/
# that is stale: nothing in it, itself included, newer than the limit.
sweep_scratch() {
  local session=$1 scratch_dir
  case $session in
    ''|*/*|.|..) echo "sweep-scratch: no usable session id, .scratch skipped"; return ;;
  esac
  [ -L .scratch ] && { echo "sweep-scratch: .scratch is a symlink, skipped"; return; }
  mkdir -p ".scratch/$session" && echo "Scratch folder for this session: $PROJECT/.scratch/$session"

  for scratch_dir in .scratch/*/; do
    scratch_dir=${scratch_dir%/}
    [ -d "$scratch_dir" ] && [ ! -L "$scratch_dir" ] && [ "$scratch_dir" != ".scratch/$session" ] || continue
    [ -z "$(find -P "$scratch_dir" -mmin -$((SCRATCH_MAX_AGE_HOURS * 60)) -print -quit)" ] || continue
    sweep_files "$scratch_dir"
    rmdir "$scratch_dir" 2>/dev/null && echo "sweep-scratch: removed $scratch_dir/"
  done
}

sweep_research() {
  [ -d .research ] && [ ! -L .research ] || return 0
  sweep_files .research $((RESEARCH_MAX_AGE_DAYS * 24 * 60))
}

main() {
  command -v jq >/dev/null || { echo "sweep-scratch: needs jq, skipped"; return; }
  local input cwd
  input=$(cat)
  cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
  PROJECT=${CLAUDE_PROJECT_DIR:-${cwd:-$PWD}}
  cd "$PROJECT" 2>/dev/null || { echo "sweep-scratch: no project directory, skipped"; return; }
  PROJECT=$(pwd -P)

  sweep_scratch "$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)"
  sweep_research
}

main
exit 0
