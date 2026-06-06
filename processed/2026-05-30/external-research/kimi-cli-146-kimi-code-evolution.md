# Kimi CLI 1.46.0 — evolution toward Kimi Code successor
**Verdict:** experiment
**Confidence:** medium
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Kimi Code CLI, Kimi Desktop
**Original URL:** https://github.com/MoonshotAI/kimi-cli/releases/tag/1.46.0
**Verify URL:** ok
**Date:** 2026-05-30
**Tags:** 
**Verification domains:** github.com, testingcatalog.net

## Summary
kimi-cli 1.46.0 (2026-05-29) ships docs announcing migration to the rebuilt TypeScript `@moonshot-ai/kimi-code` project, plus ACP session-history replay on load and graceful MCP shutdown. Moonshot is actively sunsetting the Python CLI in favor of kimi-code.

## What changes
Install `@moonshot-ai/kimi-code@latest` on a sandbox chain; run first-launch migration (skills copy from `~/.kimi/skills/`). Compare ACP resume latency and MCP teardown vs legacy `kimi-cli` before pointing Hermes ACP backend at the new binary.

## Verification notes
GitHub release 1.46.0 lists "docs: announce evolution to Kimi Code successor project" and "fix(acp): replay session history on load". testingcatalog.net independently reports the Python→TypeScript kimi-code rewrite with Claude Code–style architecture (May 2026).

## Calibration notes
Do not switch production Kimi ACP routing until one chain validates migration and ACP replay on macOS host.
