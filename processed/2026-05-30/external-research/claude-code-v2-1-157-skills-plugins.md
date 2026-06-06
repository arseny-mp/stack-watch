# Claude Code v2.1.157 — local skills plugins and workflow keyword control
**Verdict:** experiment
**Confidence:** medium
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.157
**Verify URL:** ok
**Date:** 2026-05-30
**Tags:** 
**Verification domains:** github.com, code.claude.com

## Summary
Claude Code v2.1.157 adds marketplace-free plugin loading from `.claude/skills`, a `claude plugin init` scaffold command, and a `/config` setting to disable accidental dynamic-workflow triggers from the word "workflow" in prompts.

## What changes
On one repo, run `claude plugin init <name>` under `.claude/skills/` and verify the skill loads without a marketplace entry. If workflow keyword false-positives appear, toggle "Workflow keyword trigger" off in `/config`.

## Verification notes
Literal matches on GitHub release: "Plugins in `.claude/skills` directories are now automatically loaded, no marketplace required" and "Added a \"Workflow keyword trigger\" setting in /config". code.claude.com/docs/en/changelog lists the same v2.1.157 bullet points.

## Calibration notes
None. Feature is additive; experiment on one chain before changing org-wide skill packaging.
