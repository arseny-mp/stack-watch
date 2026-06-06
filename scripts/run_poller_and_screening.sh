#!/usr/bin/env bash
# run_poller_and_screening.sh
# Chains poll_feeds.py and ai_screening.py sequentially.
# Runs daily at 09:30 via launchd.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "=== poller execution start ==="
python3 scripts/poll_feeds.py
echo "=== screening execution start ==="
python3 scripts/ai_screening.py
echo "=== completed successfully ==="
