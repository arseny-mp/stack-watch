# GitHub MCP Server 1.1.2 — lockdown RepoAccessCache viewer isolation
**Verdict:** parking
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Git / GitHub
**Original URL:** https://github.com/github/github-mcp-server/releases/tag/v1.1.2
**Verify URL:** ok
**Date:** 2026-05-31
**Tags:** single-domain
**Verification domains:** github.com

## Summary
GitHub MCP Server 1.1.2 (2026-05-29) fixes lockdown mode in HTTP deployments: `RepoAccessCache` is now scoped per request so viewer identity is not reused across callers. Relevant only when running github-mcp-server with `--lockdown-mode` serving multiple users.

## What changes
If operating a shared HTTP github-mcp-server with lockdown enabled, upgrade to ≥1.1.2 immediately. Stdio single-user local MCP configs (typical Desktop Commander / Claude Code setup) are unaffected per merged PR impact notes.

## Verification notes
Literal match on release: "Lockdown mode: scope RepoAccessCache per request." PR #2571 and release tag confirm; security advisory GHSA-pjp5-fpmr-3349 referenced in PR but not independently fetched. No second-domain source located.

## Calibration notes
Stack does not document a multi-user HTTP github-mcp-server deployment; parked until that pattern is adopted. Single-domain → parking with low confidence.
