#!/usr/bin/env bash
# Claude Code PreToolUse hook for Write. Blocks creating a new slice or a new
# README.md inside the project, and names the generator that makes one from
# the kit's template. Editing a file that already exists is never blocked.
#
# A slice is any .efforts/<effort>/<name>.md, in the project or in the kit's
# own .efforts/ under it. Paths outside the project are left alone.
#
# Reads the hook's JSON from stdin and changes nothing. Exit 0 lets the write
# go ahead; exit 2 blocks it and hands stderr back to the Agent.
#
# Wire it up in the project's .claude/settings.json:
#   "PreToolUse": [{ "matcher": "Write", "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/block-new-docs.sh" }] }]
#
# Needs jq. Takes no arguments; --help prints this header.
set -euo pipefail

if [ "${1:-}" = "--help" ]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 0
fi

path=$(jq -r '.tool_input.file_path // empty')
project=$(cd "${CLAUDE_PROJECT_DIR:-$PWD}" && pwd -P)

[ -e "$path" ] && exit 0

# The path with symlinks resolved, so /tmp and /private/tmp compare equal.
# The file does not exist yet, so resolve its nearest existing ancestor.
physical() {
  local dir=$1 rest=""
  until [ -d "$dir" ]; do
    rest="/${dir##*/}$rest"
    dir=$(dirname "$dir")
  done
  echo "$(cd "$dir" && pwd -P)$rest"
}
path=$(physical "$(dirname "$path")")/${path##*/}

case "$path" in "$project"/*) ;; *) exit 0 ;; esac
relative=${path#"$project"/}

# A generator's path from the project root: bare when the kit is the project.
generator() {
  local kit
  kit=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
  if [ "$kit" = "$(cd "$project" && pwd -P)" ]; then
    echo "bin/$1"
  else
    echo ".agents/bin/$1"
  fi
}

if [[ $relative =~ ^\.efforts/[^/]+/[^/]+\.md$ ]]; then
  echo "Blocked: new slices come from the template. Run $(generator new-slice) <effort> <slug>, then edit the file it prints." >&2
  exit 2
fi

# From the project root the bare generator would write into the project, so
# this message says to run it from inside the kit.
if [[ $relative =~ ^\.agents/\.efforts/[^/]+/[^/]+\.md$ ]]; then
  echo "Blocked: new slices about the kit come from the template. From inside .agents, run bin/new-slice <effort> <slug>, then edit the file it prints." >&2
  exit 2
fi

if [ "${relative##*/}" = README.md ]; then
  echo "Blocked: new READMEs come from the template. Run $(generator new-readme) <dir>, then edit the file it prints." >&2
  exit 2
fi

exit 0
