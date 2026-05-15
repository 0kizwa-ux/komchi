#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 start_room_draft_assistant.py
else
  python start_room_draft_assistant.py
fi
