#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M_audit)"
RUN_DIR="$REPO_ROOT/outputs/$STAMP"
RAW_EXPORT="$RUN_DIR/ncdu-export.json"

mkdir -p "$RUN_DIR"
bash "$REPO_ROOT/scripts/dgx/verify_ncdu.sh"
ncdu -o "$RAW_EXPORT" -x /
PYTHONPATH="$REPO_ROOT/src" python3 -m disk_audit_dgx.cli summarize-export \
  --export "$RAW_EXPORT" \
  --output-dir "$RUN_DIR" \
  --config "$REPO_ROOT/config/defaults.json"
echo "run_dir=$RUN_DIR"
