# Claude Code v2.1.149 — /usage breakdown and sandbox fixes
**Verdict:** experiment
**Confidence:** low
**Sources:** cursor-agent-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.149
**Verify URL:** ok
**Date:** 2026-05-23
**Tags:** single-source

## Summary
Claude Code v2.1.149 shipped 2026-05-22 with a per-category `/usage` breakdown (skills, subagents, plugins, per-MCP-server cost), keyboard navigation in `/diff`, GFM task-list checkbox rendering, and a batch of permission and sandbox hardening fixes.

## What changes
Upgrade Claude Code CLI to v2.1.149 on the operator Mac (`claude --version` → 2.1.149). Run `/usage` once after upgrade to see which categories drive limits. If PowerShell or large `find` trees are in daily workflows, smoke-test one session after upgrade because this release fixes several permission-parser and macOS vnode issues.

## Cross-source notes
Single-source (cursor-agent-self only). Workspace Agent and Gemini Gem digests for 2026-05-23 were not present on the bus.

## Calibration notes
HARD RULE 4: single-source ceiling → experiment (not do-now). Literal verify ok: release page contains `/usage` now shows a per-category breakdown and v2.1.149 tag.
