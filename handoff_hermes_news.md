# Handoff: Stack Watch Telegram Notifications via Hermes Agent

**Date:** 2026-06-05
**Recipient Agent:** Hermes (Telegram Agent)
**Objective:** Automate sending daily Stack Watch summaries to the operator's Telegram chat.

---

## 1. Context & Task Overview
The Stack Watch pipeline runs daily to identify dev-tool releases, updates, and regressions.
- At **09:30**, AntiGravity runs the research, compiles the findings, translates them, and generates a pre-formatted Russian Telegram message file.
- **Your task (Hermes):** Detect the daily digest file, read its contents, and send them directly to the operator's Telegram chat. No parsing or translation is required on your end.

---

## 2. Input Source
Every day after 10:05, you can find the pre-formatted Telegram message file at:
- **Path:** `/Users/user/Projects/Research/processed/YYYY-MM-DD/telegram_digest_ru.md`

The file contains the complete, ready-to-send Telegram message in HTML format.

---

## 3. Execution Logic (How to run / poll)
Run a check daily at **10:05** (after the build has finished running):
1. Resolve today's date (`date '+%Y-%m-%d'`).
2. Check if `/Users/user/Projects/Research/processed/YYYY-MM-DD/telegram_digest_ru.md` exists.
3. If yes (and not sent yet), read the file and send the exact content to the operator's Telegram chat using Telegram HTML format.
