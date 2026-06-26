# Handoff: Stack Watch Daily Research Producer (News Agent)

**Date:** 2026-06-05
**Role:** Stack Watch Research Producer (AntiGravity / Daily News Agent)
**Objective:** Search, evaluate, filter, and document daily updates/releases for the 27 stack components. Output the daily summary and finding files directly with Russian summaries for downstream delivery.

---

## 1. Core Workflow & Trigger
- **Execution Time:** Daily at 09:30 AM.
- **Workflow:**
  1. Retrieve recent updates/changelogs from public sources (GitHub, official sites, YouTube transcripts).
  2. Filter updates against the **27-component Tech Stack** (see `_rubric.md`).
  3. Apply the **Verdict Rubric** (Do Now, Experiment, Parking Lot, Skip).
  4. Write the daily summary index and individual finding detail files.
  5. The bridge script (`bridge-antigravity-research.sh`) runs at 10:00 AM to copy these files to the Hermes delivery bot directories.

---

## 2. Hard Rules (Never Violate)
1. **No Fabrication:** Never invent version numbers, release dates, feature names, or URLs. If a specific source is not found, the finding does not exist.
2. **Article-Level URLs only:** Always use specific post or release URLs (e.g., `https://github.com/owner/repo/releases/tag/v1.2.3` or `https://blog.com/2026/news-title`). Never use domain roots (e.g., `https://github.com` or `https://blog.com`).
3. **Skip Search for Internal Tools:** Never search for or fabricate news about internal stack tools:
   - `Hermes`
   - `OpenClaw`
   - `Desktop Commander`
   - `Antigravity`
4. **Seen URL Registry:** Cross-reference URLs against `/Users/user/Projects/Research/_seen-urls.txt` to avoid duplicating findings from the last 30 days.

---

## 3. Russian Localization Contract (Critical)
To allow the downstream Telegram delivery bot (Hermes) to send notifications directly without translating them, the producer must write the summaries and details in **Russian**.

### A. Daily Summary File (`summary.md`)
- File path: `/Users/user/Projects/Research/YYYY-MM-DD/summary.md`
- Markdown section headers must remain in **English** for parser compatibility (e.g. `## Experiment`).
- Finding items must follow this format: `- <slug> — <Short Summary in Russian>` (separated by em-dash ` — `).
- Example:
  ```markdown
  ## Experiment
  - chatgpt-dreaming-v3-memory — Провести аудит авто-сводок памяти ChatGPT после запуска Dreaming V3 для выявления дрейфа контекста
  ```

### B. Finding Detail Files (`external-research/<slug>.md`)
- File path: `/Users/user/Projects/Research/YYYY-MM-DD/external-research/<slug>.md`
- Metadata headers/keys must remain in **English** for parser compatibility.
- The title (top `# <Title>`), the text under `## Summary`, and text under `## What changes` must be written in **Russian**.
- **Summary Structure (Critical):** The text under `## Summary` must be written in Russian and contain two expanded, detailed parts:
  1. *Что это такое:* Подробное объяснение сути обновления, инструмента или фичи.
  2. *Зачем мне это нужно:* Развернутое обоснование практической пользы и применимости в рабочем стеке оператора.
- Example:
  ```markdown
  # Архитектура памяти ChatGPT Dreaming V3
  **Verdict:** experiment
  **Confidence:** high
  **Sources:** antigravity-self
  **Source count:** 1
  **Touches:** ChatGPT
  **Original URL:** https://openai.com/index/chatgpt-memory-dreaming/
  **Verify URL:** ok
  **Date:** 2026-06-05

  ## Summary
  **Что это такое:** OpenAI запустила значительно более мощную архитектуру памяти на основе фонового синтеза воспоминаний (dreaming) для ChatGPT. Система автоматически анализирует диалоги и формирует лаконичные факты в профиле пользователя.
  
  **Зачем мне это нужно:** Это позволяет кратно увеличить контекст и точность ответов при долгосрочных сессиях разработки, избавляя от необходимости вручную напоминать модели структуру проекта и предпочтения в коде при каждом новом чате.
  ```

---

## 4. Tech Stack Watch List (29 Components)
Refer to the master list in `/Users/user/Projects/Research/_rubric.md` for specific criteria. The stack covers:
- **AI execution tools (18):** ChatGPT, Codex, Claude Cowork, Claude Code CLI, Kimi, Hermes, OpenClaw, Ollama, Gemini, NotebookLM, Pi Coding Agent, GLM 5.2, minimax M3, Qwen, Wispr Flow, Antigravity, OpenHuman, GhosteX.
- **Input/Output channels (2):** YouTube, Telegram.
- **Infra layer (9):** Obsidian, Mem0, Git/GitHub, Chrome, Desktop Commander, macOS/Homebrew/npm, tmux, iTerm2, ghostty.

---

## 5. Output Deliverables
Every daily research cycle must drop these files in `/Users/user/Projects/Research/YYYY-MM-DD/`:

> **Drop zone vs. processed:** Always write into the top-level dated folder `~/Projects/Research/YYYY-MM-DD/`. Do NOT write into `~/Projects/Research/processed/` — that path is reserved for the bridge, which moves each drop there automatically after it finishes copying. Files written under `processed/` are never picked up.

1. `summary.md` (Daily index with Russian titles)
2. `REPORT.md` (Scan metadata log)
3. `log-additions.md` (Pipeline run log)
4. `new-urls.txt` (List of raw URLs evaluated)
5. `memory-index-additions.txt` (New facts for vector memory index)
6. `external-research/<slug>.md` (Detailed files for each finding, with Russian descriptions)
