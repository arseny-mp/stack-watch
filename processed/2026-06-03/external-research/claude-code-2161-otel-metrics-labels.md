# Claude Code v2.1.161 — OTEL resource attributes on metric labels
**Verdict:** experiment
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
Claude Code v2.1.161 adds `OTEL_RESOURCE_ATTRIBUTES` values as labels on metric datapoints, closing a gap where resource attributes appeared on log events but not on metrics (reported in GitHub issue #16537). Operators running OTEL telemetry can now slice usage metrics by custom dimensions such as team, repo, or cost center.

## What changes
- After upgrading to v2.1.161, add to `~/.claude/settings.json` env block if telemetry is enabled:
  `OTEL_RESOURCE_ATTRIBUTES="team.id=platform,cost_center=eng-123"` (no spaces in values per OTEL spec).
- Confirm in metrics backend that new labels appear on datapoints after one session (~15 min experiment).
- See code.claude.com/docs/en/monitoring-usage for formatting rules and Bedrock/Vertex identity patterns.

## Verification notes
Literal match on GitHub release: "`OTEL_RESOURCE_ATTRIBUTES` values are now included as labels on metric datapoints, so you can slice usage metrics by custom dimensions like team or repo." Cross-domain confirmation on code.claude.com/docs/en/monitoring-usage documenting `OTEL_RESOURCE_ATTRIBUTES` usage for team identification. Prior bug context on github.com issue #16537.

## Calibration notes
Downgraded from do-now to experiment because OTEL telemetry is opt-in and value must be validated in the operator's metrics backend before protocol-wide adoption.
