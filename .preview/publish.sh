#!/bin/bash
# Replaces the preview-results branch with the latest screenshots and report.
set -euo pipefail
mkdir -p results

cd results
git init -q -b preview-results
git config user.name "github-actions"
git config user.email "actions@github.com"
git add -A
git commit -qm "Preview for ${GITHUB_SHA::7}"
git push -fq "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" preview-results
echo "Results: https://github.com/${GITHUB_REPOSITORY}/tree/preview-results"
