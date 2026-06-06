# Claude Code v2.1.152 — autonomous code-review fixes, skills frontmatter
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, macOS / Homebrew / npm
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.152
**Verify URL:** ok
**Date:** 2026-05-27
**Tags:** 
**Verification domains:** registry.npmjs.org, aiweekly.co, reddit.com

## Summary
Claude Code v2.1.152 introduces `/code-review --fix` flag to autonomously apply code-review findings with false-positive filtering. It also expands the context window by ~4,566 tokens, and enables tool management via `disallowed-tools` frontmatter in skills and slash commands.

## What changes
- Upgrade: `npm install -g @anthropic-ai/claude-code@2.1.152`
- Test the new `/code-review --fix` functionality on a playground branch to evaluate precision.
- Audit skills configurations to determine if any benefit from specifying `disallowed-tools`.

## Verification notes
Verified the release version `2.1.152` on the npm registry. Key features (such as `/code-review --fix` and frontmatter `disallowed-tools` specifications) verified via aiweekly.co release logs, and context window expansions confirmed via developer discussions on reddit.com.

## Calibration notes
This is a major feature update for our primary terminal coding CLI. Promote to experiment verdict based on cross-domain verification.
