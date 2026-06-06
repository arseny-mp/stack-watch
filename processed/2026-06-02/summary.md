# Stack Watch — 2026-06-02

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 8
**New findings:** 3
**By verdict:** do-now 2, experiment 1, parking 0, skip 5
**Cross-Domain Validation rate:** 100% (3/3 findings verified on 2+ independent domains)

## Do now (high confidence)
- claude-code-2160-ultracode-keyword — v2.1.160 renames dynamic-workflow trigger from `workflow` to `ultracode`; update protocol docs and run `claude update`
- gemini-20-shutdown-june1 — Gemini 2.0 Flash model IDs dead since June 1; audit configs and migrate to gemini-3.1-flash-lite or gemini-3.5-flash

## Experiment
- codex-0136-session-archive — Codex 0.136.0 adds `/archive` and `codex archive`; upgrade and test on one stale session

## Parking
_(none)_

## Unconfirmed / Single Domain (low confidence)
_(none)_

## Skipped
- claude-code-2159-internal — v2.1.159 has no user-facing changes
- chatgpt-jobs-june1 — Out of scope (job search); URL dedup in _seen-urls.txt
- gemini-interactions-api-june8 — Already parked/dedup from prior cycle
- mem0-v204-delete-linked — Processed 2026-06-01; URL dedup
- openclaw-hermes — Internal tools; search skipped per rubric
