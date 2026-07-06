#!/usr/bin/env bash
# Fail if any top-level project folder exceeds MAX_FILES (git-tracked and on-disk).
set -euo pipefail

MAX_FILES="${MAX_FILES:-99}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAILED=0

count_disk_files() {
  local dir="$1"
  find "$dir" -type f \
    ! -path '*/node_modules/*' \
    ! -path '*/__pycache__/*' \
    ! -path '*/.pytest_cache/*' \
    ! -path '*/.git/*' \
    ! -path '*/htmlcov/*' \
    ! -path '*/.vite/*' \
    ! -path '*/dist/*' \
    2>/dev/null | wc -l | tr -d ' '
}

echo "Checking top-level folders (max ${MAX_FILES} files each)..."
echo ""

for dir in "$ROOT"/*/; do
  name="$(basename "$dir")"
  git_count="$(git -C "$ROOT" ls-files "$name" 2>/dev/null | wc -l | tr -d ' ')"
  disk_count="$(count_disk_files "$dir")"
  over_git=0
  over_disk=0

  [ "$git_count" -gt "$MAX_FILES" ] && over_git=1
  [ "$disk_count" -gt "$MAX_FILES" ] && over_disk=1

  if [ "$over_git" -eq 1 ] || [ "$over_disk" -eq 1 ]; then
    echo "FAIL: $name (git=$git_count, disk=$disk_count, limit=$MAX_FILES)"
    FAILED=1
  else
    echo "OK:   $name (git=$git_count, disk=$disk_count)"
  fi
done

echo ""
if [ "$FAILED" -ne 0 ]; then
  echo "One or more folders exceed the limit. Split large folders or move generated files to do-not-upload/."
  exit 1
fi

echo "All top-level folders are within the ${MAX_FILES}-file limit."
