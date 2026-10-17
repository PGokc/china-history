#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ASSET_DIR="${1:-NarrationBuild/v1}"
BUCKET="shiji-history-assets"
PREFIX="narration/v1/"
test -d "$ASSET_DIR"
python3 scripts/generate_narration.py --output "$ASSET_DIR"
assets=("$ASSET_DIR"/*.mp3)
test "${#assets[@]}" -gt 0
tosutil cp "$ASSET_DIR" "tos://$BUCKET/$PREFIX" \
  -r -flat -u -vchecksum -j=16 -nfj=16 -include='*.mp3' \
  -acl=public-read -contentType=audio/mpeg \
  '-cacheControl=public,max-age=31536000,immutable' -re=cn-shanghai
remote_count="$(tosutil ls "tos://$BUCKET/$PREFIX" -re=cn-shanghai 2>/dev/null | grep -c '\.mp3$')"
if [ "$remote_count" -ne "${#assets[@]}" ]; then
  echo "Expected ${#assets[@]} narration assets, found $remote_count" >&2
  exit 1
fi
python3 scripts/generate_narration.py --output "$ASSET_DIR" --published
