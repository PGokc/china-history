#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DEVICE_ID="${1:-BFAE7DAB-A945-5450-BAE0-4D76FB7B3E45}"
python3 scripts/validate_content.py
BUILD_LOG=build-device.log
BUILD_STAGE=$(mktemp -d /private/tmp/shiji-build.XXXXXX)
trap 'rm -rf "$BUILD_STAGE"' EXIT
cp -R App Tests MingJi.xcodeproj "$BUILD_STAGE/"
APP="$BUILD_STAGE/build-device/Build/Products/Debug-iphoneos/MingJi.app"
ENTITLEMENTS="$BUILD_STAGE/build-device/Build/Intermediates.noindex/MingJi.build/Debug-iphoneos/MingJi.build/MingJi.app.xcent"
if ! (cd "$BUILD_STAGE" && xcodebuild -project MingJi.xcodeproj -scheme MingJi -configuration Debug -destination "id=$DEVICE_ID" -derivedDataPath build-device -allowProvisioningUpdates build) > "$BUILD_LOG" 2>&1; then
  # Xcode can select the first certificate embedded in a managed profile even
  # when that certificate has no private key on this Mac. The product and its
  # generated entitlements are already complete at that point; the isolated
  # signing pass below can safely use the explicitly selected local identity.
  if grep -q 'no identity found' "$BUILD_LOG" && test -d "$APP" && test -f "$ENTITLEMENTS" && test -f "$APP/embedded.mobileprovision"; then
    echo "Xcode automatic signing selected an unavailable identity; continuing with the local signing identity."
  # Documents file-provider metadata can be reattached during the build.
  # Recover only this known packaging failure; preserve all other failures.
  elif ! grep -q 'resource fork, Finder information, or similar detritus not allowed' "$BUILD_LOG"; then
    tail -60 "$BUILD_LOG"
    exit 1
  elif grep -q 'error:' "$BUILD_LOG"; then
    tail -60 "$BUILD_LOG"
    exit 1
  fi
fi
# Signing in Documents races its FileProvider metadata updates. Use an isolated,
# disposable system staging directory; all project sources stay in this repo.
SIGN_STAGE=$(mktemp -d /private/tmp/shiji-sign.XXXXXX)
trap 'rm -rf "$BUILD_STAGE" "$SIGN_STAGE"' EXIT
ditto --norsrc --noextattr --noqtn "$APP" "$SIGN_STAGE/MingJi.app"
SIGNED_APP="$SIGN_STAGE/MingJi.app"
IDENTITY="${MING_SIGN_IDENTITY:-Apple Development: xianchao huang (JQY2N9R999)}"
for lib in "$SIGNED_APP"/*.dylib; do
  test -f "$lib" || continue
  codesign --force --sign "$IDENTITY" --timestamp=none "$lib"
done
codesign --force --sign "$IDENTITY" --entitlements "$ENTITLEMENTS" --timestamp=none --generate-entitlement-der "$SIGNED_APP"
codesign --verify --deep --strict --verbose=2 "$SIGNED_APP" 2>&1 | tee sign-verification.log
xcrun devicectl device install app --device "$DEVICE_ID" "$SIGNED_APP" | tee install-device.log
xcrun devicectl device process launch --device "$DEVICE_ID" com.huangxianchao.mingji | tee launch-device.log
