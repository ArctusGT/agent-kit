#!/usr/bin/env bash
# Symlink kit entries into a project. Run from the project root.
#
#   .agents/bin/link.sh --list
#   .agents/bin/link.sh tdd grilling code-review
#   .agents/bin/link.sh --all
#   .agents/bin/link.sh --group ansible
#
# A real file already at the target is a deliberate local override: it is
# reported and left alone. A symlink is re-pointed, so re-running is safe.
set -euo pipefail

KIT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT=$(pwd)

case "$KIT" in
  "$PROJECT"/*) REL_KIT=${KIT#"$PROJECT"/} ;;
  *) echo "link.sh: the kit must live inside the project. Run this from the project root." >&2; exit 1 ;;
esac

# name -> "<path under the kit>|<path under the project>"
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
    *) echo "link.sh: no group '$1'. Groups: rules ansible skills commands docs" >&2; exit 1 ;;
  esac
}

link_one() {
  local pair src dst dir depth prefix
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
    done ;;
  --all)
    for g in rules skills commands docs; do
      for n in $(group_names "$g"); do link_one "$n"; done
    done ;;
  --group)
    [ $# -ge 2 ] || { echo "link.sh --group <rules|ansible|skills|commands|docs>" >&2; exit 1; }
    for n in $(group_names "$2"); do link_one "$n"; done ;;
  *)
    for n in "$@"; do link_one "$n"; done ;;
esac
