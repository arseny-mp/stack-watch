# Stack Watch — Combined Improvement Roadmap

**Date:** 2026-06-05
**Scope:** End-to-end news system — Producer (AntiGravity), Bridge (`bridge-antigravity-research.sh`), Delivery bot (`updates-news-deliver.sh`).
**Origin:** Merge of two reviews — Claude (reliability + architecture-fit) and AntiGravity (sources + interactivity). Conflicts resolved in favour of the live architecture.

## How to read this

Each item is tagged:

- **Layer** — where the change lives: `Producer` (AntiGravity research), `Bridge` (copy step), `Bot` (delivery script), `Ops` (cron/launchd/monitoring).
- **Effort** — S / M / L.
- **Risk** — Low / Med / High (operational or security risk of the change itself).
- **From** — Claude / AntiGravity / Both.

Phases are ordered by leverage (value ÷ cost), not by the order either review proposed. Notably this **reverses AntiGravity's suggested starting point**: inline buttons are the heaviest, riskiest change, not the entry point.

---

## Resolved design decisions (apply across all phases)

1. **Severity is a separate axis from verdict.** The producer's verdict rubric (`do-now / experiment / parking / skip`) answers *what to do*. A new **severity tag** (`breaking/security`, `performance`, `integration`, `minor`) answers *how urgent*. They must not be conflated — "Do now" ≠ "emergency". AntiGravity's priority categories become the severity tag.
2. **Discovery ≠ verification.** New feed/aggregator sources (HN, Reddit, MCP registry) are for *noticing* a topic only. Every finding's `Original URL` and facts are still confirmed on the primary source with cross-domain validation. This preserves the existing "no fabrication / article-level URL" rules.
3. **Detail-on-demand without interactivity.** AntiGravity's `[ℹ️ Подробнее]` button is delivered as a `sendDocument` attachment of `external-research/<slug>.md` (same mechanism as the existing kanban-md delivery) — 80% of the value, zero new long-running services.
4. **Interactivity is a separate, final project.** Inline buttons require a live `gateway-updates` (currently intentionally NOT bootstrapped) and turn a stateless cron script into a stateful service. Deferred to Phase 6, and the remote command-execution button is dropped.

---

## Phase 0 — Reliability & quick wins (do first)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 0.1 | **Delivery retry + failure alert.** `curl` send currently fires once; the success-marker is only written on 200, and cron runs once/day → a transient Telegram error = a silently lost day. Add 3 retries w/ backoff; on final failure, alert a second channel/log. | Bot | S | Low | Claude |
| 0.2 | **Russian section headers** (`Внедрить сейчас / Эксперименты / Отложено`). | Bot | S | Low | Claude | 
| 0.3 | **Orphan-drop cleanup + alert.** Bridge logs skip a stale `2026-05-28` drop daily (`REPORT.md missing`); incomplete drops accumulate in `~/Projects/Research/`. Add a sweep/alert for drops older than N days. | Bridge/Ops | S | Low | Claude |
| 0.4 | **Fix or remove OpenClaw notify.** Bridge logged `Failed to send OpenClaw notification` (2026-06-04). Decide if it's a live path; fix or delete. | Bridge/Ops | S | Low | Claude |

> **0.1 and 0.2 are already DONE** (script updates-news-deliver.sh patched 2026-06-05, retry-backoff implemented, Russian headers active, dry-run verified). Listed for completeness.

---

## Phase 1 — Sources: recall + anti-hallucination (Producer)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 1.1 | **RSS/Atom GitHub Releases as the primary feed layer.** e.g. `https://github.com/ollama/ollama/releases.atom`, Claude Code, Codex, tmux, Mem0. Dated, article-level URLs by construction → kills hallucination risk and raises coverage. Agent shifts from discovery to evaluation. | Producer | M | Low | Both |
| 1.2 | **Official changelog / API RSS** for big providers (Anthropic API changelog, OpenAI, Moonshot/Kimi). Prefer RSS over scraping tables (brittle). | Producer | M | Low | AntiGravity |
| 1.3 | **Discovery layer (verify on primary!):** HN API by stack keywords, `r/LocalLLaMA` (Ollama/Qwen/GLM benchmarks), and **MCP Registry** (`modelcontextprotocol/servers`, `mcp-server` tag) — high value given Desktop Commander / Claude Desktop. Hermes already has an `mcp-registry` tool to lean on. | Producer | M | Med | AntiGravity |
| 1.4 | **Freshness hard-gate + semantic dedup.** Require `Original URL` → 200 and date within N days; dedup by `(component + version)` on top of `_seen-urls.txt` (URL-only dedup misses the same release under two URLs). Keep cross-domain validation. | Producer | M | Low | Claude |

---

## Phase 2 — Metadata for prioritization & grouping (Producer)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 2.1 | **Severity tag per finding** in `external-research/<slug>.md` (`breaking/security` 🚨, `performance` ⚡, `integration` 🧩, `minor`). Orthogonal to verdict. Drives routing (Phase 4) and flags (Phase 3). | Producer | M | Low | Both |
| 2.2 | **Populate `Tags:` + component→layer mapping.** `**Tags:**` is currently empty. Map the 27 components to 3 layers via existing `Touches`: 🤖 AI Agents & LLMs, 💻 Local Dev Environment, 🗄️ System Memory & CLI. No new data needed. | Producer | S | Low | Both |

---

## Phase 3 — Delivery formatting & grouping (Bot)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 3.1 | **Chunk under Telegram's 4096-char limit.** Currently unhandled → a busy day's message truncates. Prerequisite for any richer output below. | Bot | M | Low | Claude |
| 3.2 | **TL;DR header.** Surface the `By verdict: do-now N, experiment N…` line (already in `summary.md`) as a one-line summary in the Telegram header. | Bot | S | Low | Claude |
| 3.3 | **Two-level grouping + severity flags.** Group by verdict × thematic layer (from 2.2); prefix items with severity emoji (2.1); collapse `minor` items into a terse low-priority block (dry facts, no breakdown). | Bot | M | Low | Both |
| 3.4 | **"Подробнее" via `sendDocument`.** Attach `external-research/<slug>.md` instead of an inline button (see resolved decision #3). | Bot | M | Low | Both |

---

## Phase 4 — Severity routing / dual-channel (Bot + Producer)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 4.1 | **Breaking/security → immediate alert; rest → daily digest.** Keyed on the **severity tag** (2.1), NOT on verdict. Producer writes a `breaking`-marker when a `breaking/security` finding lands mid-run; a lightweight trigger fires the bot at once, bypassing the 10:05 cadence. Normal findings still batch into the daily digest. | Bot + Producer | M | Med | Both |

---

## Phase 5 — Weekly rollup (Bot/Bridge)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 5.1 | **Friday "week in review."** The bridge already builds `daily-digest-rolling.txt` (7-day) and component-rolling files for NotebookLM. Reuse them to emit a weekly per-component summary; complements the daily flow. | Bridge + Bot | M | Low | Claude |

---

## Phase 6 — Interactivity (biggest, last, optional)

| # | Item | Layer | Effort | Risk | From |
|---|------|-------|--------|------|------|
| 6.1 | **Inline buttons (`callback_query`).** Requires bringing a live `gateway-updates` online (currently a deliberate non-goal — the job is `no_agent`/script) and adds state + a Telegram-token-isolation concern vs. chief-of-staff. Scope to read-only actions: `[ℹ️ Подробнее]` (if not already covered by 3.4) and `[🅿️ В архив]` (mark slug seen). | Bot + Ops | L | High | Both |
| 6.2 | **DROPPED: `[🧪 Запустить тест]`.** Remote-triggering `brew`/`npm` upgrades + smoke-tests from a chat button is a system-mutation-from-messenger risk. Do not implement, or gate behind a hard out-of-band confirmation. | — | — | High | AntiGravity (rejected) |

---

## One-line sequencing

**0.1 retry+alert → 1.1 GitHub feeds → 1.4 freshness/dedup → 2.1 severity + 2.2 tags → 3.1 chunking → 3.2–3.4 grouping/detail → 4.1 dual-channel → 5.1 weekly → 6.x interactivity (only if still wanted).**

Highest leverage for least cost: **0.1** (stops silent day-loss) and **1.1** (fixes coverage + hallucination at the root). Everything visual (Phase 3+) sits behind **3.1 chunking**, and anything interactive (Phase 6) is a separate project, not a quick win.
