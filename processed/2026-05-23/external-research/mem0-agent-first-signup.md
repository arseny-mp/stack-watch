# Mem0 Agent-First signup — mem0 init --agent --json
**Verdict:** experiment
**Confidence:** low
**Sources:** cursor-agent-self
**Source count:** 1
**Touches:** Mem0
**Original URL:** https://mem0.ai/blog/introducing-agentmode-mem0-signup-without-a-human-in-the-loop
**Verify URL:** ok
**Date:** 2026-05-23
**Tags:** single-source

## Summary
Mem0 introduced Agent-First signup on 2026-05-21: coding agents can provision Mem0 API access via `mem0 init --agent --json` without human email verification, returning api_key, default_user_id, mcp_url, and claim_command in a JSON envelope. Humans claim the shadow account later with `mem0 init --email <addr>`.

## What changes
On one isolated test agent (not production Mem0 project): run `mem0 init --agent --json`, confirm envelope fields, run smoke `mem0 add` / `mem0 search` with returned default_user_id. Document claim flow before enabling on Hermes/OpenClaw automation paths. Requires mem0 CLI (`npm install -g @mem0/cli` or pip mem0ai).

## Cross-source notes
Single-source (cursor-agent-self only). Distinct from mem0-cli v0.2.7 (already seen 2026-05-22).

## Calibration notes
HARD RULE 4: single-source → experiment. Literal verify ok: blog contains `mem0 init --agent --json` and May 21, 2026 date. Operator must review shadow-account isolation before production adoption; AGENTRUSH game mentioned in blog is optional skip unless operator opts in.
