#!/usr/bin/env bash
# Claude Code PreToolUse hook for Write. Blocks creating a new slice or a new
# README.md inside the project, and names the generator that makes one from
# the kit's template. Editing a file that already exists is never blocked.
#
# A slice is any .efforts/<effort>/<name>.md except spec.md, which to-spec
# writes from its own template. Paths outside the project are left alone.
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
project=${CLAUDE_PROJECT_DIR:-$PWD}

[ -e "$path" ] && exit 0
case "$path" in "$project"/*) ;; *) exit 0 ;; esac
relative=${path#"$project"/}

if [[ $relative =~ ^\.efforts/[^/]+/[^/]+\.md$ && ${relative##*/} != spec.md ]]; then
  echo "Blocked: new slices come from the template. Run .agents/bin/new-slice <effort> <slug>, then edit the file it prints." >&2
  exit 2
fi

if [ "${relative##*/}" = README.md ]; then
  echo "Blocked: new READMEs come from the template. Run .agents/bin/new-readme <dir>, then edit the file it prints." >&2
  exit 2
fi

exit 0
