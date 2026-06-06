# Claude Opus 4.8 GA — dynamic workflows and cheaper fast mode
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Cowork, Claude Code CLI, ChatGPT
**Original URL:** https://www.anthropic.com/news/claude-opus-4-8
**Verify URL:** ok
**Date:** 2026-05-29
**Tags:**
**Verification domains:** anthropic.com, platform.claude.com, venturebeat.com

## Summary
Anthropic released Claude Opus 4.8 on May 28, 2026. The model ships as `claude-opus-4-8` at unchanged standard API pricing ($5/$25 per MTok). Fast mode pricing dropped to $10/$50 per MTok. Claude Code gains a research-preview "dynamic workflows" mode for parallel subagents on very large tasks; claude.ai and Cowork gain effort controls.

## What changes
- In Claude Code: select Opus 4.8 / run `claude-opus-4-8` via API; try `/fast` on Max if latency-sensitive.
- On one Implementor chain: compare Opus 4.7 vs 4.8 on a known Reviewer-heavy task; record token/latency delta.
- If on Enterprise/Team/Max: read Anthropic dynamic-workflows post and test one bounded migration task before adopting for production chains.
- API integrators: note mid-conversation `role: "system"` messages and `effort` defaulting to `high` on Opus 4.8.

## Verification notes
Literal `claude-opus-4-8` and May 28, 2026 date confirmed on https://www.anthropic.com/news/claude-opus-4-8. Cross-confirmed on https://platform.claude.com/docs/en/release-notes/overview (May 28, 2026 section) and https://venturebeat.com/technology/anthropics-claude-opus-4-8-is-here-with-3x-cheaper-fast-mode-and-near-mythos-level-alignment.

## Calibration notes
Downgraded from do-now: model swap needs one-chain validation; dynamic workflows limited to Enterprise/Team/Max research preview per Anthropic post.
