---
name: parked-github-mcp-112-lockdown-viewer-fix
description: GitHub MCP 1.1.2 lockdown viewer isolation — HTTP multi-user only
metadata:
  type: project
---

Parking entry for GitHub MCP Server 1.1.2 lockdown cache fix identified 2026-05-31 via Stack Watch (Solo-source mode).

**Trigger to revisit:** Stack deploys github-mcp-server in HTTP mode with `--lockdown-mode` serving more than one authenticated user, or security advisory GHSA-pjp5-fpmr-3349 is flagged in a dependency audit.

**Why parked:** Fix is scoped to multi-user HTTP lockdown deployments; our documented MCP usage is stdio/local. Confirmed only on github.com (single-domain).

**Source(s):** https://github.com/github/github-mcp-server/releases/tag/v1.1.2

**Touches:** Git / GitHub
