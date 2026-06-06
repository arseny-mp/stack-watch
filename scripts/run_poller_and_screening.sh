#!/usr/bin/env bash
# run_poller_and_screening.sh
# Chains poll_feeds.py and ai_screening.py sequentially.
# Runs daily at 09:30 via launchd.

set -euo pipefail

cd "/Users/user/Projects/Stack Watch"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "=== poller execution start ==="
python3 scripts/poll_feeds.py
echo "=== screening execution start ==="
python3 scripts/ai_screening.py
echo "=== completed successfully ==="
