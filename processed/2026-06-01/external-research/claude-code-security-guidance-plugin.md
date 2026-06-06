# Claude Code security-guidance plugin — real-time vulnerability review
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://code.claude.com/docs/en/security-guidance
**Verify URL:** ok
**Date:** 2026-06-01
**Tags:** 
**Verification domains:** code.claude.com, helpnetsecurity.com

## Summary
Anthropic released a free security-guidance plugin for Claude Code that reviews code changes for vulnerabilities during the same session. It runs a fast pattern check on each edit, a model review at end-of-turn, and a deeper agentic review on commit or push. Install with `/plugin install security-guidance@claude-plugins-official` then `/reload-plugins`.

## What changes
In one CC CLI Implementor session: install the plugin, add project rules in `.claude/claude-security-guidance.md` if needed, and run a small code-touching chain to measure false-positive rate and latency. Requires Claude Code v2.1.144+ (~45 min experiment).

## Verification notes
Literal match on code.claude.com/docs/en/security-guidance: "Install the security-guidance plugin to have Claude review its own code changes for vulnerabilities and fix them in the same session." Cross-domain confirmation on helpnetsecurity.com (May 27) independently describes the three review stages and free availability on all plans.

## Calibration notes
Plugin announced May 25–27 window; not in `_seen-urls.txt`. Experiment rather than do-now because value depends on false-positive tolerance in existing Implementor chains.
