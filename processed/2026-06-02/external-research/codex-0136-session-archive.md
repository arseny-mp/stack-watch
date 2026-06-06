# Codex CLI 0.136.0 — session archive and Bedrock support
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Codex
**Original URL:** https://github.com/openai/codex/releases/tag/rust-v0.136.0
**Verify URL:** ok
**Date:** 2026-06-02
**Tags:** 
**Verification domains:** github.com, developers.openai.com, releasebot.io

## Summary
Codex CLI 0.136.0 shipped 2026-06-01 as a stable release. Sessions can now be archived via `/archive` in the TUI or `codex archive`/`codex unarchive` on the CLI; archived sessions are protected from resume/fork until restored. The release also adds Amazon Bedrock as a model provider and `codex app-server --stdio` for MCP app-server integrations.

## What changes
- Upgrade: `npm install -g @openai/codex@0.136.0` (~10 min).
- On one non-critical Codex session, test `/archive` then confirm the session cannot be resumed until `codex unarchive`.
- Document archive workflow if useful for separating stale review sessions from active chains.

## Verification notes
Literal match on GitHub release: "Sessions can now be archived from the TUI with `/archive` or from the CLI with `codex archive`/`codex unarchive`". Confirmed independently on developers.openai.com/codex/changelog (2026-06-01 entry) and releasebot.io OpenAI feed (0.136.0 summary).

## Calibration notes
Bedrock support skipped as actionable — not in current stack infra. Session archive is the primary experiment target.
