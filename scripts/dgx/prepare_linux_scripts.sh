#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for script in \
  "$REPO_ROOT/scripts/dgx/verify_ncdu.sh" \
  "$REPO_ROOT/scripts/dgx/install_ncdu.sh" \
  "$REPO_ROOT/scripts/dgx/run_audit.sh" \
  "$REPO_ROOT/scripts/dgx/prepare_linux_scripts.sh"
do
  sed -i 's/\r$//' "$script"
  chmod +x "$script"
done

echo "prepared_linux_scripts=yes"
