#!/bin/bash
# Builds the generated project for the iOS Simulator and saves the errors in plain text.
set -uo pipefail
mkdir -p results
cd .preview/build || exit 1

xcodebuild -project App.xcodeproj -scheme App \
  -sdk iphonesimulator -configuration Debug \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath dd CODE_SIGNING_ALLOWED=NO build \
  > ../../results/build.log 2>&1
status=$?

# Keep only the useful lines, with paths shortened to your own files.
grep -E "error:" ../../results/build.log | sed -E 's|^.*/AppSources/||' | sort -u > ../../results/errors.txt || true
grep -E "warning:" ../../results/build.log | grep "/AppSources/" | sed -E 's|^.*/AppSources/||' | sort -u | head -40 > ../../results/warnings.txt || true

if [ $status -eq 0 ]; then
  echo "Build succeeded."
else
  echo "Build failed. Errors:"
  cat ../../results/errors.txt
fi
exit $status
