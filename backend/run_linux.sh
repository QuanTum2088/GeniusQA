#!/usr/bin/env bash
# Start N-Tester backend (Fast-style thin launcher)
set -e
cd "$(dirname "$0")"
if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python main.py
fi
exec python main.py
