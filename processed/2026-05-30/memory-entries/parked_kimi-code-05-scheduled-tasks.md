---
name: parked-kimi-code-05-scheduled-tasks
description: Kimi Code 0.5.0 native cron scheduled tasks — revisit after kimi-code migration
metadata:
  type: project
---

Parking entry for Kimi Code in-CLI scheduled tasks identified 2026-05-30 via Stack Watch (Solo-source mode).

**Trigger to revisit:** Kimi Code migration experiment (kimi-cli-146) completes GREEN on sandbox chain AND operator wants to replace one external launchd reminder with in-agent cron.

**Why parked:** Feature confirmed only on github.com/MoonshotAI/kimi-code release notes (single-domain). Stack still runs legacy kimi-cli for ACP; adopting scheduled tasks requires kimi-code install first. Overlaps conceptually with "Nightly Mem0 consolidation" parking lot but does not meet that trigger yet.

**Source(s):** https://github.com/MoonshotAI/kimi-code/releases/tag/@moonshot-ai/kimi-code@0.5.0

**Touches:** Kimi Code CLI
