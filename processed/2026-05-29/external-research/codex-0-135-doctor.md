# Codex CLI 0.135.0 — richer codex doctor diagnostics
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Codex
**Original URL:** https://github.com/openai/codex/releases/tag/rust-v0.135.0
**Verify URL:** ok
**Date:** 2026-05-29
**Tags:**
**Verification domains:** github.com, developers.openai.com

## Summary
OpenAI shipped Codex CLI 0.135.0 on May 28, 2026. The headline operational change is expanded `codex doctor` output covering environment, Git, terminal, app-server, and thread inventory — useful before debugging MCP or remote-control failures on the stack.

## What changes
- Upgrade: `npm install -g @openai/codex@0.135.0`
- Baseline capture: `codex doctor > ~/Projects/Research/_scratch/codex-doctor-2026-05-29.txt` (or `--summary` for support tickets)
- Optional: exercise `/permissions` named profiles if using Codex sandbox profiles alongside Desktop Commander MCP

## Verification notes
Literal string `0.135.0` and "`codex doctor` now reports richer environment, Git, terminal, app-server, and thread inventory diagnostics" found on the GitHub release page. Cross-confirmed on https://developers.openai.com/codex/changelog under "Codex CLI 0.135.0" dated 2026-05-28.

## Calibration notes
Experiment not do-now: upgrade is low risk but doctor baseline should run once before treating output as regression reference.
