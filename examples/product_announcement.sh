#!/usr/bin/env bash
# Product-launch poster with logo, badge, and footer text.
set -euo pipefail

BG="${1:?background image required}"
LOGO="${2:?logo image required}"
BADGE="${3:?badge image required}"

michelangelo generate \
  --background "$BG" \
  --title "Introducing the V2" \
  --accent-color "#0A84FF" \
  --first-circle-image "$BADGE" \
  --second-circle-text "NEW" \
  --show-logo --logo-image "$LOGO" --logo-position bottom \
  --show-additional-text --additional-text-content "Available now" \
  --output ./michelangelo-launch.png

echo "Wrote ./michelangelo-launch.png"
