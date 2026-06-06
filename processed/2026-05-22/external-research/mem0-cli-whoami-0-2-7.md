# mem0-cli v0.2.7 — whoami and agent-rush
**Verdict:** experiment
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Mem0
**Original URL:** https://github.com/mem0ai/mem0/releases/tag/cli-v0.2.7
**Verify URL:** ok
**Date:** 2026-05-22
**Tags:** single-source

## Summary
mem0-cli v0.2.7 (2026-05-20) adds `mem0 whoami` to print the active agent `default_user_id` from local config and introduces `mem0 agent-rush` with a persisted PII acknowledgement in `~/.mem0/config.json`.

## What changes
Upgrade mem0-cli to v0.2.7 on the Mem0 operator host. Run `mem0 whoami` once to confirm identity wiring. Ignore `agent-rush` unless the operator joins the AGENTRUSH game.

## Cross-source notes
Single-source only today.

## Calibration notes
Single-source ceiling: experiment. AGENTRUSH game commands treated as optional; whoami is the actionable hook for the Mem0 stack.
