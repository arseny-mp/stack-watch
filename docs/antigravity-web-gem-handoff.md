# Handoff: Stack Watch Web-Gem Curation Workflow

**Date:** 2026-06-06  
**Author:** AntiGravity Agent  
**Audience:** External Developer Agents / Operators  
**Workspace Base:** `/Users/user/Projects/Stack Watch`  
**Status:** **FULLY ALIGNED WITH WEB-GEM CURATION POLICY**

---

## 1. Web-Gem Workflow Overview

Since the operator does not use or pay for the developer Google API key, the daily curation stage is processed through the **Google Gemini Web Gem** (custom chatbot instructions UI) rather than an automated script.

The daily operational lifecycle runs as follows:

```
[09:30] launchd runs run_poller_and_screening.sh
   │
   ├──> poll_feeds.py gathers release & HN candidates
   └──> ai_screening.py fails-open (retains all candidates as "keep" because key is empty)
        and outputs them to ~/Projects/Stack Watch/YYYY-MM-DD/feed_updates.json
   │
[User Action] Operator copies YYYY-MM-DD/feed_updates.json
   │
   ├──> Pastes updates list into Gemini Web Gem (Gem has _rubric.md & learnings.md knowledge)
   └──> Gem processes updates & outputs: summary.md, REPORT.md, findings files
   │
[User Action] Operator saves output files into daily drop folder YYYY-MM-DD/
   │
[10:00] launchd runs bridge-antigravity-research.sh
   │
   ├──> bridge checks folders, compiles rolling files and rollup
   ├──> generate_dashboard.py compiles static index.html
   └──> updates-news-deliver.sh triggers Telegram bot delivery
```

---

## 2. Daily Folder Structure Checklist

After manual curation via the Gemini Web Gem, the following files should be created and saved in `/Users/user/Projects/Stack Watch/YYYY-MM-DD/` before the bridge execution:

* **`summary.md`**: Standard daily summary containing verdict lists (Do now, Experiment, Parking, Unconfirmed, Skipped).
* **`REPORT.md`**: Curation log (Confidence rates, calibration decisions, issues encountered).
* **`log-additions.md`** *(Optional)*: Pipe-separated row(s) to append to the master log.
* **`memory-index-additions.txt`** *(Optional)*: Memory index entries for parked items.
* **`external-research/`** *(Optional)*: Directory containing individual `<slug>.md` markdown findings.
* **`memory-entries/`** *(Optional)*: Directory containing individual memory entries for Vector memory.

---

## 3. Automation Plist Diagnostics

Daily scheduler daemons are active on the local macOS host:

1. **`com.user.poll-feeds-research`** (`~/Library/LaunchAgents/com.user.poll-feeds-research.plist`)
   - **Trigger**: Daily at **09:30**.
   - **Action**: Runs polling and pre-filtering to populate the day's `feed_updates.json`.
2. **`com.user.bridge-antigravity-research`** (`~/Library/LaunchAgents/com.user.bridge-antigravity-research.plist`)
   - **Trigger**: Daily at **10:00**.
   - **Action**: Validates daily drop folder, regenerates `index.html` status panel, and delivers news to Telegram.
3. **`com.user.stack-watch-gateway`**
   - **Status**: **Decommissioned & Stopped** (unloaded from launchd) by operator request.

### Diagnostics Reference
- **Manually run ingestion**:
  `/Users/user/Projects/Stack\ Watch/scripts/run_poller_and_screening.sh`
- **Manually run bridge (e.g. for `2026-06-06`)**:
  `/Users/user/Projects/Stack\ Watch/scripts/bridge-antigravity-research.sh 2026-06-06`
- **Rebuild the premium dashboard `index.html`**:
  `python3 /Users/user/Projects/Stack\ Watch/scripts/generate_dashboard.py`
