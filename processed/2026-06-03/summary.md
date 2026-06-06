# Stack Watch — 2026-06-03

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 8
**New findings:** 3
**By verdict:** do-now 1, experiment 2, parking 0, skip 5
**Cross-Domain Validation rate:** 100% (3/3 findings verified on 2+ independent domains)

## Do now (high confidence)
- claude-code-2161-mcp-secrets-redaction — Upgrade to v2.1.161; MCP list/get/add no longer prints credential secrets

## Experiment
- claude-code-2161-otel-metrics-labels — Set OTEL_RESOURCE_ATTRIBUTES in settings.json if OTEL metrics export is active
- mem0-cli-v028-security-cves — npm update -g @mem0/cli if globally installed

## Parking

## Unconfirmed / Single Domain (low confidence)

## Skipped
- mem0-opencode-v012 — OpenCode not in 19-component stack
- mem0-openclaw-v1012 — OpenClaw is operator-internal; skip per rubric
- chatgpt-active-sessions — URL already in _seen-urls.txt (dedup)
- codex-0136-session-archive — URL already in _seen-urls.txt; processed 2026-06-02
- gemini-20-shutdown-june1 — Changelog URL already in _seen-urls.txt; processed 2026-06-02
