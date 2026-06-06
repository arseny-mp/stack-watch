# Claude Code v2.1.156 — Opus 4.8 thinking-block fix
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.156
**Verify URL:** ok
**Date:** 2026-05-30
**Tags:** 
**Verification domains:** github.com, code.claude.com, saudishopper.com.sa

## Summary
Claude Code v2.1.156 (published 2026-05-29) fixes a regression where Opus 4.8 sessions mutated thinking blocks between API turns, producing unrecoverable HTTP 400 errors. Anyone running Opus 4.8 on the CLI should upgrade before the next long chain.

## What changes
Run `npm update -g @anthropic-ai/claude-code` and confirm `claude --version` reports ≥2.1.156. If a session is already wedged, `/compact` or `/clear` remains the recovery path until upgraded.

## Verification notes
Literal match on GitHub release: "Fixed an issue when using Opus 4.8 where thinking blocks were modified, leading to API errors." Cross-confirmed on code.claude.com/docs/en/changelog with the same wording and on saudishopper.com.sa summarizing v2.1.156 as the Opus 4.8 API error fix.

## Calibration notes
None. Direct bugfix with clear target file (global npm install) and sub-5-minute apply time.
