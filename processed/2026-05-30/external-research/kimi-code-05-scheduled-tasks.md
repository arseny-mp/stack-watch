# Kimi Code 0.5.0 — native scheduled tasks and auto permission mode
**Verdict:** parking
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Kimi Code CLI
**Original URL:** https://github.com/MoonshotAI/kimi-code/releases/tag/@moonshot-ai/kimi-code@0.5.0
**Verify URL:** ok
**Date:** 2026-05-30
**Tags:** single-domain
**Verification domains:** github.com

## Summary
Kimi Code 0.5.0 (2026-05-28) introduces cron-style scheduled tasks inside the CLI (5-field cron syntax) and a `/auto` command with `--auto` flag for permission auto-approval. Could reduce external launchd glue for low-risk agent reminders.

## What changes
No immediate change. Revisit after Kimi Code migration experiment succeeds: test one cron reminder (e.g., daily stack-health grep) via in-CLI scheduler instead of external launchd.

## Verification notes
Literal match on GitHub release: "Add scheduled tasks" with cron examples and "Add `/auto` slash command and `--auto` CLI flag for auto permission mode." No independent second-domain source found documenting scheduled tasks specifically; moonshotai.github.io getting-started docs do not mention scheduling yet.

## Calibration notes
Downgraded to parking + single-domain because only github.com/MoonshotAI/kimi-code confirms the feature. Relates to existing "Nightly Mem0 consolidation" parking lot but does not fire that trigger until Kimi Code is adopted.
