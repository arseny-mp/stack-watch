# ChatGPT retiring GPT-4.5 and OpenAI o3 from consumer UI
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** ChatGPT
**Original URL:** https://help.openai.com/en/articles/9624314-model-release-notes
**Verify URL:** ok
**Date:** 2026-06-01
**Tags:** 
**Verification domains:** help.openai.com, androidauthority.com

## Summary
OpenAI announced May 28, 2026 that GPT-4.5 will be retired from ChatGPT on June 27, 2026 following a 30-day sunset period, and OpenAI o3 will be retired on August 26, 2026 following a 90-day sunset period. Both remain available to paid users via model settings until their dates. Changes apply to ChatGPT only; API is unaffected.

## What changes
Before June 27, audit ChatGPT Plus/Pro coordinator sessions for any explicit GPT-4.5 or o3 model selection in custom GPTs or saved prompts. Migrate those workflows to GPT-5.5 Instant/Thinking defaults. Document the June 27 and August 26 cutoffs in operator notes (~30 min).

## Verification notes
Literal match on help.openai.com Model Release Notes: "GPT-4.5 will be retired from ChatGPT on June 27, 2026" and "OpenAI o3 will be retired from ChatGPT on August 26, 2026". Cross-domain confirmation on androidauthority.com (May 28 coverage) cites the same dates and ChatGPT-only scope.

## Calibration notes
Announcement is May 28 — within 7-day rubric lookback. Action urgency elevated because June 27 is 26 days away and ChatGPT is the coordinator layer in the stack.
