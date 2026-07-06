#!/usr/bin/env bash
# Create do-not-upload/ layout and migrate legacy local files from backend/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DNU="$ROOT/do-not-upload"

echo "Setting up do-not-upload/ at $DNU"

mkdir -p "$DNU"/{data,logs,env,storage/images,storage/videos,storage/audio,cache/optimized_images,cache/pytest,coverage}

touch "$DNU/data/.gitkeep"
touch "$DNU/logs/.gitkeep"
touch "$DNU/env/.gitkeep"
touch "$DNU/storage/.gitkeep"
touch "$DNU/cache/.gitkeep"
touch "$DNU/coverage/.gitkeep"

migrate() {
  local src="$1"
  local dest="$2"
  if [ -e "$src" ] && [ "$src" != "$dest" ]; then
    if [ -d "$src" ]; then
      shopt -s nullglob
      local files=("$src"/*)
      shopt -u nullglob
      if [ "${#files[@]}" -gt 0 ]; then
        echo "  migrate: $src/* -> $dest/"
        mv "$src"/* "$dest/" 2>/dev/null || true
      fi
    elif [ -f "$src" ]; then
      echo "  migrate: $src -> $dest"
      mv "$src" "$dest"
    fi
  fi
}

echo "Migrating legacy backend artifacts (if any)..."
migrate "$ROOT/backend/elder_company.db" "$DNU/data/elder_company.db"
migrate "$ROOT/backend/.env" "$DNU/env/.env"
migrate "$ROOT/backend/logs" "$DNU/logs"
migrate "$ROOT/backend/optimized_images" "$DNU/cache/optimized_images"
migrate "$ROOT/backend/test_storage/images" "$DNU/storage/images"
migrate "$ROOT/backend/test_storage/videos" "$DNU/storage/videos"
migrate "$ROOT/backend/test_storage/audio" "$DNU/storage/audio"

if [ ! -f "$DNU/env/.env" ]; then
  echo ""
  echo "Next step: copy backend/env.example to do-not-upload/env/.env and fill in your keys."
else
  echo ""
  echo "Found do-not-upload/env/.env"
fi

echo "Done."
