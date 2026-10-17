#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ASSET_DIR="${1:-NarrationBuild/v1}"
TAG="narration-zh-v1"
test -d "$ASSET_DIR"
python3 scripts/generate_narration.py --output "$ASSET_DIR"
if gh release view "$TAG" >/dev/null 2>&1; then
  :
else
  gh release create "$TAG" --title "史迹明清朗读 v1" --notes "史迹 0.83 明清长读的豆包语音音频。"
fi

assets=("$ASSET_DIR"/*.mp3)
test "${#assets[@]}" -gt 0
for ((offset=0; offset<${#assets[@]}; offset+=50)); do
  batch=("${assets[@]:offset:50}")
  for attempt in 1 2 3; do
    if gh release upload "$TAG" "${batch[@]}" --clobber; then
      break
    fi
    if [ "$attempt" -eq 3 ]; then
      exit 1
    fi
    sleep $((attempt * 3))
  done
done

remote_count="$(gh release view "$TAG" --json assets --jq '.assets | length')"
if [ "$remote_count" -ne "${#assets[@]}" ]; then
  echo "Expected ${#assets[@]} release assets, found $remote_count" >&2
  exit 1
fi
python3 scripts/generate_narration.py --output "$ASSET_DIR" --published
