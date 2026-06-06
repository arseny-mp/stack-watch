# Stack Watch — 2026-05-27

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 10
**New findings:** 4
**By verdict:** do-now 0, experiment 3, parking 1, skip 6
**Cross-Domain Validation rate:** 100% (4/4 findings verified on 2+ independent domains)

## Do now (high confidence)

_(none)_

## Experiment

- codex-cli-0134-profile-mcp — Upgrade to Codex CLI 0.134.0; audit profile v1 config migration and re-test MCP servers.
- claude-code-v21152 — Upgrade to Claude Code 2.1.152; test autonomous /code-review --fix on standard project directories.
- ollama-v030-rc28 — Test Ollama v0.30.0-rc28; verify llama.cpp support & Apple Silicon MLX acceleration options.

## Parking

- claude-code-http-mcp-404-regression — Revisit after next claude-code release documents HTTP MCP GET/404 fix; until then audit POST-only HTTP MCP gateways on v2.1.147+.

## Unconfirmed / Single Domain (low confidence)

_(none)_

## Skipped

- gemini-interactions-default-may26 — URL in seen-urls; no in-stack Interactions API client.
- ollama-v030-rc23 — seen-urls; prerelease outside 48h freshness.
- mem0-cli-v027 — seen-urls; release 2026-05-20.
- claude-code-v21150 — seen-urls; no new release since 2026-05-23.
- kimi-cli-144 — release 2026-05-14, outside 48h.
- desktop-commander-v0241 — release 2026-05-14, outside 48h.
