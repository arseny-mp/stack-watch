# Claude Code v2.1.162 — agents/MCP/WebFetch fixes
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, Claude Cowork
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.162
**Verify URL:** ok
**Date:** 2026-06-04
**Tags:** 
**Verification domains:** github.com, code.claude.com

## Summary
Claude Code v2.1.162 shipped 2026-06-03 with background-agent observability (`waitingFor` in `claude agents --json`), restored Grep/Glob when listed in `--tools`, and multiple MCP/WebFetch permission fixes relevant to MCP-heavy workflows.

## What changes
Run `claude update` to reach v2.1.162. If any MCP server uses `timeout` below 1000ms in config, verify behavior after the fix (sub-1000ms values are now ignored). Review explicit `WebFetch(domain:...)` rules if relying on deny/ask overrides for preapproved domains.

## Verification notes
Primary URL contains literal title `v2.1.162` and bullet `Fixed MCP per-server timeout config values below 1000 ms`. Cross-domain confirmed on code.claude.com/docs/en/changelog with matching changelog bullets including `waitingFor` and MCP timeout fix text.

## Calibration notes
Downgraded from do-now: upgrade is low-risk but value depends on whether operator hits the specific MCP timeout or WebFetch edge cases; experiment on one chain first.
