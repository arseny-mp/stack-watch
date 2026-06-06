# Stack Watch — 2026-06-01

**Sources processed:** antigravity-self (Solo-source mode)
**Candidates considered (across all sources):** 9
**New findings:** 4
**By verdict:** do-now 2, experiment 2, parking 0, skip 5
**Cross-Domain Validation rate:** 100% (4/4 findings verified on 2+ independent domains)

## Do now (high confidence)
- chatgpt-gpt45-o3-retirement — GPT-4.5 leaves ChatGPT June 27; audit coordinator model selections before deadline
- notebooklm-gemini-chats-block-sharing — Do not Gemini-chat a notebook that must stay shareable; delete Gemini chats to restore sharing

## Experiment
- mem0-v204-delete-linked — Test delete_linked=True on non-prod Mem0 cleanup to prevent superseded facts resurfacing
- claude-code-security-guidance-plugin — Install security-guidance plugin in one CC CLI chain; measure false-positive rate

## Parking

## Unconfirmed / Single Domain (low confidence)

## Skipped
- gemini-interactions-june8-sunset — Already in _seen-urls.txt
- claude-code-v2157-v2158 — URLs already in _seen-urls.txt (dedup)
- codex-0136-alpha2 — Pre-release with no actionable changelog body
- openclaw-hermes-internal — Internal operator tools; search skipped per rubric
- notebooklm-sharing-secondary — Secondary journalism; folded into official Gemini-chat sharing finding
