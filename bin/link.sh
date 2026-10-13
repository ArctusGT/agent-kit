#!/usr/bin/env bash
# Symlink kit entries into a project. Run from the project root.
#
#   .agents/bin/link.sh --list
#   .agents/bin/link.sh tdd grilling code-review
#   .agents/bin/link.sh --all
#   .agents/bin/link.sh --group ansible
#   .agents/bin/link.sh --group hooks
#
# A real file already at the target is a deliberate local override: it is
# reported and left alone. A symlink is re-pointed, so re-running is safe.
#
# Hooks are not symlinked. Each hook's header carries its "Wire it up" entry,
# which is merged into the project's .claude/settings.json; an event that
# already runs the hook's command is left alone. Wiring a hook needs jq.
# --all wires every hook along with the rest.
set -euo pipefail

if [ "${1:-}" = "--help" ]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 0
fi

KIT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT=$(pwd)

case "$KIT" in
  "$PROJECT"/*) REL_KIT=${KIT#"$PROJECT"/} ;;
  *) echo "link.sh: the kit must live inside the project. Run this from the project root." >&2; exit 1 ;;
esac

# name -> "<path under the kit>|<path under the project>"
#
# Two things the table below decides rather than records. Generic and ansible
# rules both land in one flat .claude/rules/, so an ansible rule must not take
# a generic rule's name. And docs/agents lands outside .claude/ because the
# skills that read those files look for them at that project path.
locate() {
  local n=$1
  for p in "rules/$n.md|.claude/rules/$n.md" \
           "rules/ansible/$n.md|.claude/rules/$n.md" \
           "skills/$n|.claude/skills/$n" \
           "commands/$n.md|.claude/commands/$n.md" \
           "docs/agents/$n.md|docs/agents/$n.md"; do
    [ -e "$KIT/${p%%|*}" ] && { printf '%s\n' "$p"; return 0; }
  done
  return 1
}

group_names() {
  case $1 in
    rules)    ls "$KIT"/rules/*.md | xargs -n1 basename | sed 's/\.md$//' ;;
    ansible)  ls "$KIT"/rules/ansible/*.md | xargs -n1 basename | sed 's/\.md$//' ;;
    skills)   ls -d "$KIT"/skills/*/ | xargs -n1 basename ;;
    commands) ls "$KIT"/commands/*.md | xargs -n1 basename | sed 's/\.md$//' ;;
    docs)     ls "$KIT"/docs/agents/*.md | xargs -n1 basename | sed 's/\.md$//' ;;
    hooks)    ls "$KIT"/hooks/*.sh | xargs -n1 basename | sed 's/\.sh$//' ;;
    *) echo "link.sh: no group '$1'. Groups: rules ansible skills commands docs hooks" >&2; exit 1 ;;
  esac
}

SETTINGS=.claude/settings.json

# The hook's "Wire it up" lines as one JSON object, with the kit path in its
# command made to match where this project keeps the kit.
hook_entry() {
  awk '/^# Wire it up/ {f=1; next} f && /^#[[:space:]]*$/ {exit} f {sub(/^# ?/, ""); print}' "$1" \
    | sed "s#/\\.agents/hooks/#/$REL_KIT/hooks/#" \
    | { printf '{'; cat; printf '}'; } | jq -c .
}

hook_command() { hook_entry "$KIT/hooks/$1.sh" | jq -r '[.[][].hooks[].command][0]'; }

hook_wired() {
  [ -f "$SETTINGS" ] &&
    jq -e --arg c "$(hook_command "$1")" '[.hooks[]?[]?.hooks[]?.command] | index($c)' "$SETTINGS" >/dev/null
}

wire_hook() {
  local n=$1 entry tmp
  command -v jq >/dev/null || { echo "  !  $n — wiring a hook needs jq"; return; }
  if hook_wired "$n"; then echo "  =  $SETTINGS — $n already wired"; return; fi
  entry=$(hook_entry "$KIT/hooks/$n.sh")
  mkdir -p "$(dirname "$SETTINGS")"
  [ -e "$SETTINGS" ] || echo '{}' > "$SETTINGS"
  tmp=$(mktemp)
  jq --argjson e "$entry" \
    'reduce ($e | to_entries[]) as $x (.; .hooks[$x.key] += $x.value)' "$SETTINGS" > "$tmp"
  mv "$tmp" "$SETTINGS"
  echo "  ->  $SETTINGS — $n"
}

link_one() {
  local pair src dst dir depth prefix
  [ -f "$KIT/hooks/$1.sh" ] && { wire_hook "$1"; return; }
  pair=$(locate "$1") || { echo "  ?  $1 — not in the kit"; return; }
  src=${pair%%|*}; dst=${pair##*|}
  dir=$(dirname "$dst")
  mkdir -p "$dir"
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "  =  $dst — local override, left alone"
    return
  fi
  depth=$(printf '%s' "$dir" | tr -cd '/' | wc -c); depth=$((depth + 1))
  prefix=$(for _ in $(seq "$depth"); do printf '../'; done)
  ln -sfn "$prefix$REL_KIT/$src" "$dst"
  echo "  ->  $dst"
}

case "${1:---list}" in
  --list)
    for g in rules ansible skills commands docs; do
      echo "$g:"
      for n in $(group_names "$g"); do
        pair=$(locate "$n"); dst=${pair##*|}
        if [ -L "$dst" ]; then state="linked"
        elif [ -e "$dst" ]; then state="local override"
        else state="-"; fi
        printf '  %-34s %s\n' "$n" "$state"
      done
    done
    echo "hooks:"
    for n in $(group_names hooks); do
      if ! command -v jq >/dev/null; then state="? (needs jq)"
      elif hook_wired "$n"; then state="wired"
      else state="-"; fi
      printf '  %-34s %s\n' "$n" "$state"
    done ;;
  --all)
    for g in rules skills commands docs hooks; do
      for n in $(group_names "$g"); do link_one "$n"; done
    done ;;
  --group)
    [ $# -ge 2 ] || { echo "link.sh --group <rules|ansible|skills|commands|docs|hooks>" >&2; exit 1; }
    for n in $(group_names "$2"); do link_one "$n"; done ;;
  *)
    for n in "$@"; do link_one "$n"; done ;;
esac
