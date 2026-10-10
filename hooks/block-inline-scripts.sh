#!/usr/bin/env bash
# Claude Code PreToolUse hook for Bash. Blocks a shell or Python interpreter
# given -c with a multi-line script, and points the Agent at the rule
# under "Scripts" in .agents/AGENTS.md.
#
# Reads the hook's JSON from stdin and changes nothing. Exit 0 lets the
# command run; exit 2 blocks it and hands stderr back to the Agent.
#
# Wire it up in the project's .claude/settings.json:
#   "PreToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/block-inline-scripts.sh" }] }]
#
# Needs jq. Takes no arguments; --help prints this header.
set -euo pipefail

if [ "${1:-}" = "--help" ]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 0
fi

cmd=$(jq -r '.tool_input.command // empty')

# An interpreter, any flags, then -c (alone or ending a flag group like -lc).
interp='(^|[[:space:];&|(])(python[0-9.]*|bash|sh|zsh)([[:space:]]+-[A-Za-z]+)*[[:space:]]+-[A-Za-z]*c[[:space:]]'

if [[ $cmd =~ $interp ]]; then
  script=${cmd#*"${BASH_REMATCH[0]}"}
  if [[ $script == *$'\n'* ]]; then
    echo "Blocked: a multi-line script passed with -c. Write it to the scratchpad and run the file (AGENTS.md, \"Scripts\")." >&2
    exit 2
  fi
fi

exit 0
