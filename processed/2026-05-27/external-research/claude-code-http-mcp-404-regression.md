# Claude Code — HTTP MCP GET 404 treated as session expiry (v2.1.147+)
**Verdict:** parking
**Confidence:** medium
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI, Desktop Commander
**Original URL:** https://github.com/anthropics/claude-code/issues/62198
**Verify URL:** ok
**Date:** 2026-05-27
**Tags:** 
**Verification domains:** github.com, modelcontextprotocol.io

## Summary
A regression from Claude Code v2.1.147 through v2.1.150 misinterprets HTTP 404 on the optional MCP Streamable HTTP GET listening stream as session expiry, tears down the transport, and leaves POST-only HTTP MCP servers unreachable in interactive sessions. The MCP spec treats the GET stream as optional (servers without SSE should return 405); session-expiry 404 handling applies to POST requests carrying `Mcp-Session-Id`. Issue opened 2026-05-25, closed 2026-05-27 without a linked fix release in the thread.

## What changes
- Inventory HTTP-type MCP servers in `~/.claude.json` (remote gateways, streamable HTTP bridges).
- If tools vanish after upgrade: compare behavior on v2.1.146 vs current build, or temporarily switch affected servers to stdio transport.
- Revisit when a claude-code release after 2.1.150 documents streamable-HTTP GET/404 handling fix.

## Verification notes
Literal strings `v2.1.147`, `MCP session expired (server returned 404)`, and version matrix through `2.1.150` found on the GitHub issue page. MCP Streamable HTTP spec section confirms: "The client MAY issue an HTTP GET" and servers without SSE "MUST return HTTP 405 Method Not Allowed" — supporting that GET 404 is not the session-expiry signal described in session-management clause 4.

## Calibration notes
Issue closed by automation; fix version not stated — capped at `parking` with explicit re-test trigger rather than `experiment` or `do-now`. Stdio MCP (Desktop Commander default) unaffected; relevance is HTTP/streamable MCP integrations only.
