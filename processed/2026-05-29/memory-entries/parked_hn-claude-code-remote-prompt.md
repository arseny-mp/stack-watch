---
name: parked-hn-claude-code-remote-prompt
description: HN alleges remote system-prompt injection in CC 2.1.150+ — verify before env mitigations
metadata:
  type: project
---

Parking entry for Claude Code remote prompt injection report identified 2026-05-29 via Stack Watch (Solo-source mode).

**Trigger to revisit:** After any Claude Code upgrade past 2.1.150, run local strings check for `heron_brook` on the installed binary, OR Anthropic publishes official docs/changelog addressing bootstrap/GrowthBook injection, OR operator observes unexpected system-prompt drift in CC CLI sessions.

**Why parked:** HN thread documents plausible mitigations (`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, `DISABLE_GROWTHBOOK=1`) but this cycle found no second independent domain confirming `tengu_heron_brook`. Applying env changes without local verification risks breaking legitimate bootstrap features.

**Source(s):** https://news.ycombinator.com/item?id=48259288

**Touches:** Claude Code CLI
