---
name: parked-github-mcp-110-search-commits
description: GitHub MCP 1.1.0 search_commits — revisit when bumping past v1.0.5
metadata:
  type: project
---

Parking entry for GitHub MCP Server 1.1.0 commit search tooling identified 2026-05-31 via Stack Watch (Solo-source mode).

**Trigger to revisit:** Operator upgrades local or remote github-mcp-server configuration from v1.0.5 to ≥1.1.0, or a chain needs cross-repo commit search without raw `gh` CLI.

**Why parked:** Feature confirmed on github.com release notes only (single-domain). Current seen-urls pin v1.0.5; no production MCP config documents github-mcp-server yet. Value is plausible for release forensics but unproven in our workflows.

**Source(s):** https://github.com/github/github-mcp-server/releases/tag/v1.1.0

**Touches:** Git / GitHub, Desktop Commander
