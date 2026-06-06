# Claude Code v2.1.161 — MCP credential redaction fix
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Claude Code CLI
**Original URL:** https://github.com/anthropics/claude-code/releases/tag/v2.1.161
**Verify URL:** ok
**Date:** 2026-06-03
**Tags:** 
**Verification domains:** github.com, code.claude.com

## Summary
Claude Code v2.1.161 (published 2026-06-02) fixes a security regression where `claude mcp list`, `get`, and `add` printed secrets to the terminal — expanding `${VAR}` references and exposing credential headers and URL secrets in plaintext. The fix aligns with long-standing community reports (GitHub issue #30467) about MCP token exposure via `claude mcp get`.

## What changes
- Run `claude update` to install v2.1.161 (~5 min).
- Verify redaction: `claude mcp get <server-name>` should mask tokens instead of printing full values.
- Audit any scripts or coordinator logs that capture `claude mcp list/get` output; rotate MCP tokens if logs may contain pre-2.1.161 plaintext.

## Verification notes
Literal match on GitHub release: "Fixed `claude mcp` list/get/add printing secrets to the terminal: `${VAR}` references are no longer expanded, and credential headers and URL secrets are redacted." Cross-domain confirmation on code.claude.com/docs/en/changelog with identical v2.1.161 entry. Supporting context on github.com issue #30467 describing the pre-fix exposure pattern.

## Calibration notes
None. Direct security fix for daily Claude Code CLI MCP workflow.
