# Claude Code v2.1.153 — release-channel update fix
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.153
**Verify URL:** ok
**Date:** 2026-05-29
**Tags:**
**Verification domains:** github.com, saudishopper.com.sa

## Summary
Anthropic released Claude Code v2.1.153 on May 28, 2026. The release fixes `claude update` installing the latest npm version instead of the configured release channel — relevant for operators pinning stable vs nightly channels across CC CLI iTerm sessions.

## What changes
- Run `npm update -g @anthropic-ai/claude-code` and confirm `claude --version` reports 2.1.153.
- Run `claude doctor` to verify last update attempt and channel alignment.
- Estimated time: under 15 minutes per host.

## Verification notes
Literal `v2.1.153` and fix text "Fixed `claude update` installing the latest version instead of the configured release channel's version for npm installations" on GitHub release page. Second domain: https://saudishopper.com.sa/en/claude-code-update-2-1-153/ cites version 2.1.153 and May 28, 2026 publish date.

## Calibration notes
None. Small, verifiable channel fix with clear install path qualifies as do-now per rubric.
