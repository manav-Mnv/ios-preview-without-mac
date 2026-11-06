#!/bin/bash
# Runs the app in an iPhone and an iPad simulator, in light and dark mode,
# and saves screenshots (plus a short video) into results/.
set -uo pipefail
OUT=results
mkdir -p "$OUT"
WAIT="${PREVIEW_WAIT:-8}"

APP=$(find .preview/build/dd/Build/Products -type d -name "*.app" -path "*iphonesimulator*" | head -1)
[ -z "$APP" ] && { echo "Built app not found"; exit 1; }

pick() { # newest available iOS simulator whose name contains $1
  xcrun simctl list devices available -j | python3 -c '
import json, sys
want = sys.argv[1]
devices = json.load(sys.stdin)["devices"]
found = [d for rt, ds in sorted(devices.items()) if "iOS" in rt for d in ds if want in d["name"]]
print(found[-1]["udid"] if found else "")' "$1"
}

launch_and_shoot() { # udid  file  [launch args...]
  local U=$1 F=$2; shift 2
  xcrun simctl terminate "$U" "$BUNDLE_ID" >/dev/null 2>&1 || true
  xcrun simctl launch "$U" "$BUNDLE_ID" "$@" >/dev/null 2>&1
  sleep "$WAIT"
  xcrun simctl io "$U" screenshot "$OUT/$F.png" >/dev/null 2>&1 && echo "  saved $F.png"
}

run_device() { # prefix  name-hint  fallback-hint
  local P=$1 U; U=$(pick "$2"); [ -z "$U" ] && U=$(pick "$3")
  [ -z "$U" ] && { echo "No $3 simulator available"; return; }
  echo "$P: $(xcrun simctl list devices | grep "$U" | head -1 | sed -E 's/ \(.*//; s/^ +//')" | tee -a "$OUT/devices.txt"
  xcrun simctl boot "$U" >/dev/null 2>&1 || true
  xcrun simctl bootstatus "$U" -b >/dev/null
  xcrun simctl status_bar "$U" override --time "9:41" --batteryLevel 100 --cellularBars 4 >/dev/null 2>&1 || true
  xcrun simctl install "$U" "$APP"

  xcrun simctl ui "$U" appearance light >/dev/null 2>&1 || true
  if [ "$P" = "iphone" ]; then
    # A short video of the app starting up.
    xcrun simctl io "$U" recordVideo --codec=h264 --force "$OUT/iphone-launch.mp4" >/dev/null 2>&1 &
    local REC=$!
    sleep 1
    launch_and_shoot "$U" "$P-light"
    kill -INT "$REC" 2>/dev/null; wait "$REC" 2>/dev/null || true
  else
    launch_and_shoot "$U" "$P-light"
  fi

  xcrun simctl ui "$U" appearance dark >/dev/null 2>&1 || true
  launch_and_shoot "$U" "$P-dark"
  xcrun simctl ui "$U" appearance light >/dev/null 2>&1 || true

  # Optional extra screens from screens.txt:   name | launch arguments
  if [ -f screens.txt ]; then
    while IFS='|' read -r NAME ARGS; do
      NAME=$(echo "$NAME" | xargs); ARGS=$(echo "${ARGS:-}" | xargs)
      [ -z "$NAME" ] && continue
      case "$NAME" in \#*) continue;; esac
      SAFE=$(echo "$NAME" | tr -c 'A-Za-z0-9-' '-' | sed 's/-*$//')
      # shellcheck disable=SC2086
      launch_and_shoot "$U" "$P-screen-$SAFE" $ARGS
    done < screens.txt
  fi

  # Did the app crash?
  find ~/Library/Logs/DiagnosticReports -name "*.ips" -newer "$APP" 2>/dev/null | while read -r R; do
    grep -q "\"$BUNDLE_ID\"" "$R" 2>/dev/null && cp "$R" "$OUT/$P-crash-$(basename "$R")"
  done
  xcrun simctl shutdown "$U" >/dev/null 2>&1 || true
}

run_device iphone "iPhone 17 Pro" "iPhone"
run_device ipad "iPad Pro 13" "iPad"
ls -la "$OUT"
