# Claude Code v2.1.146 — /code-review rename
**Verdict:** experiment
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.146
**Verify URL:** ok
**Date:** 2026-05-22
**Tags:** single-source

## Summary
Claude Code v2.1.146 shipped 2026-05-21. `/simplify` is renamed to `/code-review` with optional effort levels; paginated MCP `resources/list` and `tools/list` no longer drop items after page 1.

## What changes
Upgrade Claude Code to v2.1.146 (`claude update` or reinstall bundle). Replace `/simplify` usage with `/code-review`. Re-smoke any MCP integrations that rely on paginated tool lists.

## Cross-source notes
Single-source (antigravity-self). No cross-source confirmation today.

## Calibration notes
Single-source ceiling: experiment max.
