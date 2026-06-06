# ChatGPT Dreaming V3 memory architecture
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** ChatGPT
**Original URL:** https://openai.com/index/chatgpt-memory-dreaming/
**Verify URL:** ok
**Date:** 2026-06-05
**Tags:** 
**Verification domains:** openai.com, 9to5mac.com

## Summary
OpenAI launched a significantly more capable dreaming-based memory architecture for ChatGPT on June 4, 2026. The system auto-synthesizes memories in the background, exposes them via a reviewable memory summary page, and rolls out first to Plus/Pro users in the US with roughly doubled memory capacity.

## What changes
Open ChatGPT → Settings → Memory → review the memory summary page. Audit coordinator-relevant facts (stack preferences, workflow constraints) for staleness or contradictions introduced by automatic dreaming synthesis. Optionally revert to legacy saved memories via Settings → Memory → Saved memories if auto-updates cause drift.

## Verification notes
Literal match confirmed on openai.com/index/chatgpt-memory-dreaming/: "June 4, 2026", "memory summary page", "dreaming". Cross-confirmed on 9to5mac.com/2026/06/04/openai-says-chatgpts-memory-feature-is-getting-smarter-and-coming-to-free-users/ citing "doubling the capacity for memory storage" and June 4 rollout to Plus/Pro US users.

## Calibration notes
Actionable for ChatGPT Plus/Pro coordinator layer. Not a code change — workflow audit only. Downgraded from do-now because rollout is US-only initially and value requires observing memory summary behavior over several sessions.
