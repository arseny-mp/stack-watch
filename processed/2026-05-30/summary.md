# Stack Watch — 2026-05-30

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 9
**New findings:** 4
**By verdict:** do-now 1, experiment 2, parking 1, skip 1
**Cross-Domain Validation rate:** 75% (3/4 findings verified on 2+ independent domains)

## Do now (high confidence)
- claude-code-v2-1-156-opus-thinking-fix — Upgrade Claude Code to ≥2.1.156 before Opus 4.8 chains to avoid thinking-block API 400 wedging.

## Experiment
- claude-code-v2-1-157-skills-plugins — Try marketplace-free `.claude/skills` plugins and workflow keyword toggle on one chain.
- kimi-cli-146-kimi-code-evolution — Pilot `@moonshot-ai/kimi-code` migration and ACP replay before switching production Kimi backend.

## Parking
- kimi-code-05-scheduled-tasks — Revisit native cron scheduling after Kimi Code migration experiment passes.

## Unconfirmed / Single Domain (low confidence)
- kimi-code-05-scheduled-tasks — Found only on github.com/MoonshotAI/kimi-code; verdict restricted to parking — in-CLI scheduled tasks with 5-field cron syntax.

## Skipped
- claude-code-v2-1-158-bedrock-auto-mode — Bedrock/Vertex/Foundry auto mode opt-in; stack uses Anthropic API directly.
- v2-1-154-dynamic-workflows — Duplicate topic; anthropic.com Opus 4.8 URL already in seen-urls (2026-05-29 cycle).
- codex-0-135-0 — URL in seen-urls.txt.
- mem0-v2-0-4 — Published May 27, outside 48h window.
- ollama / desktop-commander — No releases in lookback window.
- openclaw / hermes — Internal tools; search skipped per rubric.
