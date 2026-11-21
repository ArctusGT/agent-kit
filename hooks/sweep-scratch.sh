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

# Remove the untracked files and links under relative path $1, reporting
# tracked ones, then folders left empty below $1. An optional $2 limits it to
# those older than that many minutes. A git answer other than "tracked" (0)
# or "not tracked" (1) is a git failure: the file is left alone.
# Symlinks are matched as links by find -P and never entered.
sweep_files() {
  local dir=$1 age=() f
  [ -n "${2:-}" ] && age=(-mmin +"$2")
  while IFS= read -r -d '' f; do
    git ls-files --error-unmatch -- "$f" >/dev/null 2>&1
    case $? in
      0) echo "sweep-scratch: kept tracked file $f" ;;
      1) if rm -f -- "$f"; then echo "sweep-scratch: removed $f"; else echo "sweep-scratch: could not remove $f"; fi ;;
      *) echo "sweep-scratch: git failed on $f, left alone" ;;
    esac
  done < <(find -P "$dir" \( -type f -o -type l \) "${age[@]}" -print0)
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
    sweep_files "$d"
    rmdir "$d" 2>/dev/null && echo "sweep-scratch: removed $d/"
  done

  if [ -d .research ] && [ ! -L .research ]; then
    sweep_files .research $((RESEARCH_MAX_AGE_DAYS * 24 * 60))
  fi
}

main
exit 0
