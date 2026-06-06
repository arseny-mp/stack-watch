# Stack Watch — 2026-06-05

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 8
**New findings:** 4
**By verdict:** do-now 0, experiment 2, parking 2, skip 4
**Cross-Domain Validation rate:** 75% (3/4 findings verified on 2+ independent domains)

## Do now (high confidence)

_(none)_

## Experiment
- chatgpt-dreaming-v3-memory — Audit ChatGPT memory summary after Dreaming V3 rollout (June 4) for coordinator context drift
- claude-code-v2-1-163 — Test new managed settings, plugin list filters, btw shortcut, and CLI hang fixes in Claude Code CLI v2.1.163

## Parking
- codex-sites-role-plugins — Revisit when workspace tier includes Codex Sites preview or GitHub-relevant role plugin ships
- ollama-v030-nvidia-driver-570 — Revisit before upgrading Ollama past 0.29 on GPU Linux hosts running Mem0 embeddings

## Unconfirmed / Single Domain (low confidence)

_(none)_

## Skipped
- ollama-v0-30-5 — macOS Apple Silicon host is unaffected by Pascal driver issue, and we do not use gemma4:12b or Windows Hermes install
- gemini-interactions-api-june8 — Interactions API not used in current Gemini web / NotebookLM workflows
- claude-code-v2-1-162 — URL already in `_seen-urls.txt` (dedup)
- mem0-openclaw-v1-0-12 — Internal OpenClaw tool + URL already seen
