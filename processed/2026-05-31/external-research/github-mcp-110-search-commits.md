# GitHub MCP Server 1.1.0 — search_commits and issue-field tools
**Verdict:** parking
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Git / GitHub, Desktop Commander
**Original URL:** https://github.com/github/github-mcp-server/releases/tag/v1.1.0
**Verify URL:** ok
**Date:** 2026-05-31
**Tags:** single-domain
**Verification domains:** github.com

## Summary
GitHub MCP Server 1.1.0 (2026-05-28) ships `search_commits` for GitHub commit search syntax, GHAS alert pagination, smaller project-item payloads, and issue-field read/write behind `remote_mcp_issue_fields`. The stack's seen-urls still reference v1.0.5 only.

## What changes
When upgrading github-mcp-server past 1.0.5, add `search_commits` to release-audit agent prompts (e.g., `repo:owner/name fix regression committer-date:>=2026-05-01`). Enable issue-field tools only if Insiders Mode or `remote_mcp_issue_fields` flag is required.

## Verification notes
Literal match on release page: "A new `search_commits` tool has been added, allowing agents to search commits directly using GitHub search syntax." No independent second-domain confirmation found; github.com/awesome-copilot references are same domain.

## Calibration notes
Published May 28 — slightly outside strict 48h window but not yet in seen-urls (only v1.0.5 logged). Verdict capped at parking due to single-domain confirmation.
