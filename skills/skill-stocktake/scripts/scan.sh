#!/usr/bin/env bash
# scan.sh — Phase 1 inventory for /skill-stocktake.
#
# Usage: scan.sh [project_root]
#   project_root defaults to $PWD. Scans ~/.claude/skills plus
#   {project_root}/.claude/skills if it exists.
#
# Output:
#   1. "Scanning:" summary — which roots were found, with file counts
#   2. One tab-separated row per skill file:
#        path <TAB> mtime_utc <TAB> name <TAB> description
#
# Portability: POSIX-sh constructs only. Works in Git Bash on Windows,
# macOS (BSD userland), and Linux. No `date -d`, no GNU-only stat flags.

set -eu

project_root="${1:-$PWD}"
global_dir="$HOME/.claude/skills"
project_dir="$project_root/.claude/skills"
# Avoid double-scanning when run from $HOME
[ "$project_dir" = "$global_dir" ] && project_dir=""

# File mtime as UTC ISO-8601. Try GNU `date -r FILE` first; fall back to
# BSD/macOS `stat -f %m` (epoch) piped back through `date -u -r EPOCH`.
mtime_utc() {
  date -u -r "$1" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null && return 0
  date -u -r "$(stat -f %m "$1" 2>/dev/null)" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null && return 0
  echo "unknown"
}

# Extract a top-level frontmatter field ($2) from a skill file ($1).
fm_field() {
  awk -v key="$2" '
    NR == 1 { if ($0 ~ /^---[ \t]*$/) { infm = 1; next } else { exit } }
    infm && /^---[ \t]*$/ { exit }
    infm && index($0, key ":") == 1 {
      val = substr($0, length(key) + 2)
      gsub(/^[ \t]+|[ \t]+$/, "", val)
      sub(/^"/, "", val); sub(/"$/, "", val)
      print val
      exit
    }
  ' "$1"
}

echo "Scanning:"
files=""
for dir in "$global_dir" "$project_dir"; do
  [ -n "$dir" ] || continue
  if [ -d "$dir" ]; then
    found=$(find "$dir" -name SKILL.md -type f 2>/dev/null | sort)
    count=$(printf '%s\n' "$found" | grep -c . || true)
    printf '  \342\234\223 %s  (%s files)\n' "$dir" "$count"
    files="$files$found
"
  else
    printf '  \342\234\227 %s  (not found)\n' "$dir"
  fi
done
echo

printf 'path\tmtime_utc\tname\tdescription\n'
printf '%s\n' "$files" | grep . | while IFS= read -r f; do
  printf '%s\t%s\t%s\t%s\n' \
    "$f" "$(mtime_utc "$f")" \
    "$(fm_field "$f" name)" "$(fm_field "$f" description)"
done
