#!/usr/bin/env bash
# Claude Code SessionStart hook. Gives the session a working folder at
# .scratch/<session-id>/ in the project and prints its path into the session's
# context, then sweeps stale material. DELETES FILES, inside the project only:
#   - each other folder under .scratch/ with nothing inside modified in the
#     last 24 hours
#   - files under .research/ not modified in 14 days, then any folders left empty
# Prints what it removed. Never follows a symlink (a stale link is removed
# itself, its target is not touched), and leaves a git-tracked file alone,
# reporting it. Never fails the session: on any error it says so and exits 0.
#
# Reads the hook's JSON from stdin (session_id, cwd). The project is
# $CLAUDE_PROJECT_DIR, else the JSON's cwd, else the current directory.
# Needs jq and git. Takes no arguments; --help prints this header.
#
# Wire it up in the project's .claude/settings.json:
#   "SessionStart": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/sweep-scratch.sh" }] }]
#
# link.sh also makes sure the project's .gitignore lists .scratch/ and .research/.
SCRATCH_MAX_AGE_HOURS=24
RESEARCH_MAX_AGE_DAYS=14

if [ "${1:-}" = "--help" ]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 0
fi

set -uo pipefail

# Remove every untracked file or link under $1 that is older than $2 minutes
# (0 removes all), reporting tracked ones, then folders left empty below $1.
# Symlinks are matched as links by find -P and never entered.
sweep_files() {
  local dir=$1 minutes=$2 f
  while IFS= read -r -d '' f; do
    if git -C "$PROJECT" ls-files --error-unmatch -- "${f#"$PROJECT"/}" >/dev/null 2>&1; then
      echo "sweep-scratch: kept tracked file ${f#"$PROJECT"/}"
    elif rm -f -- "$f"; then
      echo "sweep-scratch: removed ${f#"$PROJECT"/}"
    else
      echo "sweep-scratch: could not remove ${f#"$PROJECT"/}"
    fi
  done < <(find -P "$dir" \( -type f -o -type l \) -mmin +"$minutes" -print0)
  find -P "$dir" -mindepth 1 -depth -type d -empty -delete 2>/dev/null
}

main() {
  command -v jq >/dev/null || { echo "sweep-scratch: needs jq, skipped"; return; }
  local input session cwd d
  input=$(cat)
  session=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
  cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
  PROJECT=${CLAUDE_PROJECT_DIR:-${cwd:-$PWD}}
  cd "$PROJECT" 2>/dev/null || { echo "sweep-scratch: no project directory, skipped"; return; }
  PROJECT=$(pwd -P)

  case $session in
    ''|*/*|.|..) echo "sweep-scratch: no usable session id, skipped"; return ;;
  esac
  [ -L .scratch ] && { echo "sweep-scratch: .scratch is a symlink, skipped"; return; }
  mkdir -p ".scratch/$session" && echo "Scratch folder for this session: $PROJECT/.scratch/$session"

  # A folder is stale when nothing in it, itself included, is newer than the limit.
  for d in .scratch/*/; do
    d=${d%/}
    [ -d "$d" ] && [ ! -L "$d" ] && [ "$d" != ".scratch/$session" ] || continue
    [ -z "$(find -P "$d" -mmin -$((SCRATCH_MAX_AGE_HOURS * 60)) -print -quit)" ] || continue
    sweep_files "$PROJECT/$d" 0
    rmdir "$d" 2>/dev/null && echo "sweep-scratch: removed $d/"
  done

  if [ -d .research ] && [ ! -L .research ]; then
    sweep_files "$PROJECT/.research" $((RESEARCH_MAX_AGE_DAYS * 24 * 60))
  fi
}

main
exit 0
