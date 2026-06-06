# HN report: Claude Code remote system-prompt injection
**Verdict:** parking
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI
**Original URL:** https://news.ycombinator.com/item?id=48259288
**Verify URL:** ok
**Date:** 2026-05-29
**Tags:** single-domain
**Verification domains:** news.ycombinator.com

## Summary
A May 2026 HN thread claims Claude Code v2.1.150+ pulls bootstrap data from `api.anthropic.com/api/claude_cli/bootstrap` and GrowthBook flag `tengu_heron_brook`, injecting remote strings into the system prompt. Commenters suggest `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` and `DISABLE_GROWTHBOOK=1`. No independent Anthropic documentation confirming `tengu_heron_brook` was found in this cycle.

## What changes
- Do not change production env until locally verified on installed binary (strings/grep for `heron_brook` after next upgrade).
- If verified: add mitigations to CC CLI launch profile and document in operator runbook.

## Verification notes
Literal `tengu_heron_brook`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, and v2.1.150 reference present on HN item 48259288. Single-domain only — no second independent source with the same technical claims in this scan.

## Calibration notes
Verdict capped at parking per solo-source cross-domain rule. Not skip — security-relevant if confirmed on next bisect.
