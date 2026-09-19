#!/usr/bin/env bash
set -euo pipefail

if command -v ncdu >/dev/null 2>&1; then
  echo "ncdu already installed"
  exit 0
fi

if ! sudo -n true >/dev/null 2>&1; then
  echo "ERROR: sudo password required; installation must be performed with operator input" >&2
  exit 4
fi

sudo apt-get update
sudo apt-get install -y ncdu
