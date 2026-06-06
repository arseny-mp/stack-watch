# Stack Watch — 2026-05-31

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 7
**New findings:** 3
**By verdict:** do-now 0, experiment 1, parking 2, skip 4
**Cross-Domain Validation rate:** 33% (1/3 findings verified on 2+ independent domains)

## Do now (high confidence)
- (none)

## Experiment
- ollama-v030-rc31-nomic-embed-lowercase — Stage rc31 and diff nomic-embed-text vectors before any production Ollama bump affecting Mem0 embeddings.

## Parking
- github-mcp-110-search-commits — Revisit when upgrading github-mcp-server past v1.0.5 for commit-search audit workflows.
- github-mcp-112-lockdown-viewer-fix — Revisit if deploying shared HTTP github-mcp-server with lockdown mode enabled.

## Unconfirmed / Single Domain (low confidence)
- github-mcp-110-search-commits — Found only on github.com; verdict restricted to parking — search_commits and issue-field tooling in v1.1.0.
- github-mcp-112-lockdown-viewer-fix — Found only on github.com; verdict restricted to parking — per-request RepoAccessCache isolation fix.

## Skipped
- kimi-code-0-6-0 — URL in `_seen-urls.txt`.
- claude-code-v2-1-158 — URL in `_seen-urls.txt`.
- codex-0-136-0-alpha-1 — Pre-release tag with no actionable changelog body.
- mem0-v2-0-4 — Published May 27, outside 48h window.
- notebooklm-drive-auto-sync — Official post May 26, outside 48h window.
- openclaw / hermes — Internal tools; search skipped per rubric.
