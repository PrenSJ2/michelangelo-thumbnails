#!/usr/bin/env bash
# Minimal Michelangelo invocation.
set -euo pipefail

michelangelo generate \
  --background "$1" \
  --title "${2:-LAUNCH DAY}" \
  --accent-color "${3:-#FF3B30}" \
  --output ./michelangelo-basic.png

echo "Wrote ./michelangelo-basic.png"
