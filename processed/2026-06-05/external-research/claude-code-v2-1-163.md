# Claude Code v2.1.163 stability release
**Verdict:** experiment
**Confidence:** high
**Sources:** client-env
**Source count:** 1
**Touches:** Claude Code CLI
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.163
**Verify URL:** ok
**Date:** 2026-06-05
**Tags:** 
**Verification domains:** github.com

## Summary
Anthropic released Claude Code v2.1.163 on June 4, 2026. This release introduces `requiredMinimumVersion` and `requiredMaximumVersion` managed settings, the `/plugin list` command to display installed plugins with filters, and a markdown copy shortcut `c` in `/btw`. It also fixes background command hangs under `claude -p`, key errors, and terminal alignment bugs.

## What changes
Run `npm update -g @anthropic-ai/claude-code` to upgrade to v2.1.163. Test the new `/plugin list` command and try the `c` shortcut inside `/btw` to verify markdown copying functionality.

## Verification notes
Literal match confirmed on github.com/anthropics/claude-code/releases/tag/v2.1.163: "requiredMinimumVersion", "/plugin list", "c to copy", and "claude -p hangs".

## Calibration notes
Actionable upgrade for our primary command line executor. Downgraded to experiment because it is a single-source finding from the GitHub releases page, which has not been cross-validated by other sources yet (single-source ceiling heuristic).
