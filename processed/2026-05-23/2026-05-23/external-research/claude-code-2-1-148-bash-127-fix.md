# Claude Code v2.1.148 — Bash exit 127 regression hotfix
**Verdict:** experiment
**Confidence:** low
**Sources:** cursor-agent-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.148
**Verify URL:** ok
**Date:** 2026-05-23
**Tags:** single-source

## Summary
Claude Code v2.1.148 (2026-05-22) is a hotfix for users where the Bash tool returned exit code 127 on every command — a regression introduced in v2.1.147.

## What changes
Check installed version on operator machines running Claude Code. If on v2.1.147 and Bash commands uniformly return 127, upgrade to v2.1.148+ immediately. Otherwise include v2.1.148 in the next routine CLI update batch (superseded by v2.1.149 if upgrading straight to latest).

## Cross-source notes
Single-source (cursor-agent-self only).

## Calibration notes
HARD RULE 4: single-source → experiment. Literal verify ok: release notes state exit code 127 and regression in 2.1.147. Prioritize upgrade path to v2.1.149 which includes this fix plus additional changes.
