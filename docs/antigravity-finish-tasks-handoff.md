# Handoff: Finish Stack Watch wiring (AntiGravity-side tasks)

**Date:** 2026-06-05  
**Audience:** AntiGravity (research producer + poller + bridge owner)  
**Status:** **FULLY LIVE AND OPERATIONAL** (All wiring completed, tested, and active)

---

## 1. Wiring Status & Completed Tasks

All remaining implementation gaps listed in previous handoffs have been successfully resolved and verified:

| Capability | Status | Notes |
|---|---|---|
| **Delivery bot (format, retry, immediate, weekly)** | ✅ **LIVE** | Retry-backoff and formatting active. |
| **Bridge daily copy + weekly rollup** | ✅ **LIVE** | Automates weekly digest and daily staging. |
| **Poller `poll_feeds.py` exists** | ✅ **LIVE** | Refined for direct daily folder writing. |
| **Poller scheduled @ 09:30** | ✅ **LIVE** | Active via launchd agent `com.user.poll-feeds-research`. |
| **Poller output path** | ✅ **LIVE** | Writes directly to daily drop zone `~/Projects/Stack Watch/YYYY-MM-DD/`. |
| **Breaking-marker → immediate alert** | ✅ **LIVE** | Bridge immediately triggers delivery bot on `breaking-marker`. |
| **Orphan-drop cleanup (3-day)** | ✅ **LIVE** | Automates pruning of stale directories and logs alerts. |
| **Data Boundary Constraints** | ✅ **LIVE** | Added hard privacy constraints in `_rubric.md`. |

---

## 2. Completed Tasks Breakdown

### Task 1 — Schedule the poller (`com.user.poll-feeds-research`)
* **Launchd Agent Created**: Created `/Users/user/Library/LaunchAgents/com.user.poll-feeds-research.plist`.
* **Schedule**: Runs daily at **09:30** (before the research agent runs).
* **Launchd Status**: Loaded and active. Verified via `launchctl list | grep poll-feeds` and tested via `launchctl kickstart`.

### Task 2 — Fix the poller output path (`processed/` collision)
* **Script Modification**: [poll_feeds.py](file:///Users/user/Projects/Stack%20Watch/scripts/poll_feeds.py) now creates and writes its results directly to `~/Projects/Stack Watch/YYYY-MM-DD/feed_updates.json`.
* **Rubric Instructions**: Updated [_rubric.md](file:///Users/user/Projects/Stack%20Watch/_rubric.md) to instruct the research agent to read `feed_updates.json` directly from the daily directory, eliminating `processed/` collision.

### Task 3 — Wire breaking-marker → immediate alert
* **Rubric update**: Rubric instructs the research agent to write `breaking-marker` in the daily directory `~/Projects/Stack Watch/YYYY-MM-DD/breaking-marker` if a `breaking/security` severity finding is added.
* **Bridge update**: [bridge-antigravity-research.sh](file:///Users/user/Projects/Stack%20Watch/scripts/bridge-antigravity-research.sh) detects this marker and immediately triggers `updates-news-deliver.sh` with the `--immediate` flag.

### Task 4 — Data boundary & privacy constraints
* **Rubric update**: Explicitly updated [_rubric.md](file:///Users/user/Projects/Stack%20Watch/_rubric.md) Section 9 to enforce the data boundary constraint:
  - **Allowed reads:** Public online sources via poller script, and the `/Users/user/Projects/Stack Watch/` folder only.
  - **Forbidden:** Accessing other `~/Projects/*` folders, local project repositories, or local private files outside of the designated research directory.

### Task 5 — Orphan-drop cleanup
* **Bridge update**: The bridge script scans and deletes folders under `~/Projects/Stack Watch/` older than 3 days that lack `REPORT.md` or `.bridged` markers, printing an `[ALERT]` message to the logs.

---

## 3. Verification & Operation Checklist

1. **Verify Poller Schedule**:
   ```bash
   launchctl list | grep poll-feeds
   # Expected output: com.user.poll-feeds-research
   ```
2. **Review Poller Outputs**:
   Confirm that `feed_updates.json` is generated directly under the daily drop zone:
   `ls -la ~/Projects/Stack Watch/$(date '+%Y-%m-%d')/feed_updates.json`
3. **Check Logs**:
   * Poller: `~/Library/Logs/poll-feeds-research.stdout.log`
   * Bridge: `~/Library/Logs/bridge-antigravity-research.log`
