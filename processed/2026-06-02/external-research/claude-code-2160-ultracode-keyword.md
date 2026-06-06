# Claude Code v2.1.160 — ultracode keyword rename and acceptEdits hardening
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.160
**Verify URL:** ok
**Date:** 2026-06-02
**Tags:** 
**Verification domains:** github.com, code.claude.com

## Summary
Claude Code v2.1.160 (published 2026-06-02) renames the dynamic-workflow trigger keyword from `workflow` to `ultracode`. Typing "workflow" in a prompt no longer auto-triggers a dynamic workflow run; operators must use the `ultracode` keyword or `/effort ultracode`. The release also hardens acceptEdits mode with prompts before writing shell startup files and build-tool configs that grant code execution.

## What changes
- Run `claude update` to install v2.1.160 (~5 min).
- Search protocol docs and skills for instructions to type "workflow" as a dynamic-workflow trigger; replace with `ultracode` keyword or `/effort ultracode`.
- Update any coordinator briefings that reference the violet-highlighted "workflow" trigger word.

## Verification notes
Literal match confirmed on GitHub release page: "Renamed the dynamic-workflow trigger keyword from `workflow` to `ultracode`." Cross-domain confirmation on code.claude.com/docs/en/changelog with identical changelog entry for v2.1.160.

## Calibration notes
None. Directly touches active Claude Code CLI workflow used daily.
