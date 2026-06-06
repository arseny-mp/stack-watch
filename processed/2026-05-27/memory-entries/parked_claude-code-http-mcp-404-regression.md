---
name: parked-claude-code-http-mcp-404-regression
description: Claude Code v2.1.147+ may break POST-only HTTP MCP; re-test after fix release
metadata:
  type: project
---

Parking entry for Claude Code Streamable HTTP MCP regression identified 2026-05-27 via Stack Watch (Solo-source mode).

**Trigger to revisit:** A claude-code release after v2.1.150 ships with release notes or changelog mentioning MCP Streamable HTTP GET stream / 404 session handling, OR an HTTP MCP server in the stack fails tool listing after upgrade.

**Why parked:** Confirmed regression on v2.1.147–2.1.150 with spec-backed analysis, but the tracking issue closed without naming a fix version. Stdio MCP (primary Desktop Commander path) is unaffected; action is conditional on HTTP MCP usage.

**Source(s):** https://github.com/anthropics/claude-code/issues/62198 , https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http

**Touches:** Claude Code CLI, Desktop Commander
