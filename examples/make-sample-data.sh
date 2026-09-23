#!/usr/bin/env bash
# Generates a small synthetic tree used by the DirStat_Skill demo.
# The generated files are gitignored; only this script and the produced
# examples/demo-audit bundle are committed.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

rm -rf sample-data
mkdir -p sample-data/cache sample-data/models sample-data/reports

head -c 300000 /dev/urandom > sample-data/cache/blob.bin
head -c 150000 /dev/urandom > sample-data/models/model.gguf
printf 'quarterly numbers\n' > sample-data/reports/q1.txt
printf 'notes\n' > sample-data/reports/notes.md

echo "sample-data created under $(pwd)/sample-data"
