#!/usr/bin/env bash
# Scan git-tracked files for common personal-info patterns before publishing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FAIL=0

check_pattern() {
  local label="$1"
  local pattern="$2"
  local matches
  matches="$(git grep -n -E "$pattern" -- . 2>/dev/null || true)"
  if [ -n "$matches" ]; then
    echo "FAIL: $label"
    echo "$matches" | head -20
    [ "$(echo "$matches" | wc -l | tr -d ' ')" -gt 20 ] && echo "... (truncated)"
    FAIL=1
  else
    echo "OK:   $label"
  fi
}

echo "Personal-info scan (git-tracked files only)"
echo "==========================================="

check_pattern "Personal name in copyright" 'Copyright 202[0-9] (Qingyuan|chaos)[^A-Za-z]'
check_pattern "Home path (/Users/chaos)" '/Users/chaos'
check_pattern "Private email domain" 'chaos\.h@|@gmicloud\.'
check_pattern "OpenAI-style API keys" 'sk-[A-Za-z0-9]{20,}'
if git ls-files --error-unmatch .env do-not-upload/env/.env 2>/dev/null; then
  echo "FAIL: Committed secret .env file"
  git ls-files .env do-not-upload/env/.env 2>/dev/null
  FAIL=1
else
  echo "OK:   No committed .env files"
fi

echo ""
echo "Local-only (should stay gitignored):"
for path in do-not-upload/env/.env do-not-upload/logs/app.log do-not-upload/data/elder_company.db; do
  if [ -e "$path" ]; then
    echo "  present: $path (not scanned for git — verify .gitignore)"
  fi
done

echo ""
echo "Git commit author (visible after push):"
git log -1 --format='  %an <%ae>'

echo ""
if [ "$FAIL" -ne 0 ]; then
  echo "Fix the issues above before pushing to GitHub."
  exit 1
fi

echo "No personal-info patterns found in tracked files."
echo "Note: older git commits may still contain author name/email in history."
