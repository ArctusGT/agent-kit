#!/usr/bin/env bash
# Claude Code hook (SessionStart, UserPromptSubmit, Stop, SessionEnd) that notes
# when a session is active and logs its blocks of time to the repo's timesheet
# ticket as the repo's bot. The work is hooks/agent_time.py, which --help
# explains in full: the per-repo setting, the token file, what it logs where.
#
# Silent where the repo has no .agent-time.json or no token. Never blocks and
# always exits 0; the forge is only ever spoken to by a detached child.
#
# Wire it up in the project's .claude/settings.json:
#   "SessionStart": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/agent-time.sh" }] }],
#   "UserPromptSubmit": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/agent-time.sh" }] }],
#   "Stop": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/agent-time.sh" }] }],
#   "SessionEnd": [{ "hooks": [{ "type": "command",
#     "command": "\"$CLAUDE_PROJECT_DIR\"/.agents/hooks/agent-time.sh" }] }]
#
# Takes no arguments; --help prints this header.
if [ "${1:-}" = "--help" ]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 0
fi
python3 -I "$(dirname "$0")/agent_time.py" hook 2>/dev/null
exit 0
