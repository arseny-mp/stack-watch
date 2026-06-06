# Stack Watch — 2026-05-29

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 8
**New findings:** 5
**By verdict:** do-now 1, experiment 2, parking 2, skip 0
**Cross-Domain Validation rate:** 60% (3/5 findings verified on 2+ independent domains)

## Do now (high confidence)
- claude-code-2-1-153 — npm update to 2.1.153 fixes release-channel `claude update` behavior

## Experiment
- claude-opus-4-8 — GA model `claude-opus-4-8`, cheaper fast mode, dynamic workflows preview in Claude Code
- codex-0-135-doctor — Upgrade to 0.135.0 and capture `codex doctor` baseline for support debugging

## Parking
- gemini-3-1-flash-image-ga — Revisit when grep finds `*-image-preview` model ids before 2026-06-25 shutdown
- hn-claude-code-remote-prompt — Revisit after local binary bisect confirms remote prompt injection; env-var mitigations unverified by Anthropic docs

## Unconfirmed / Single Domain (low confidence)
- hn-claude-code-remote-prompt — Found only on news.ycombinator.com; verdict restricted to parking — remote bootstrap / GrowthBook injection allegation

## Skipped
- claude-code-2-1-152 — URL in `_seen-urls.txt`
- ollama-v0-30-0-rc27-rc28 — URLs in `_seen-urls.txt`
- mem0-v2-0-3 — Published 2026-05-26, outside 48h window
- kimi-cli-1-44-0 — Latest release 2026-05-14, no May 27–29 tag
- desktop-commander-0-2-41 — Latest release 2026-05-14
- openclaw-hermes — Internal tools; search skipped per HARD RULE 3
