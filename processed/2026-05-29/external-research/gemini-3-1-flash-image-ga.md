# Gemini 3.1 Flash Image GA — migrate off preview before June 25
**Verdict:** parking
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Gemini
**Original URL:** https://cloud.google.com/blog/products/ai-machine-learning/nano-banana-2-and-nano-banana-pro-are-generally-available
**Verify URL:** ok
**Date:** 2026-05-29
**Tags:**
**Verification domains:** cloud.google.com, docs.cloud.google.com

## Summary
Google announced GA for Nano Banana 2 (`gemini-3.1-flash-image`) and Nano Banana Pro (`gemini-3-pro-image`) on May 28–29, 2026. Preview ids shut down June 25, 2026. Video-to-image input is exclusive to Flash Image. Primary stack use is Gemini web + NotebookLM bridge — image models matter only if configs reference preview ids.

## What changes
- Grep stack configs for `gemini-3.1-flash-image-preview` or `gemini-3-pro-image-preview`.
- Replace with `gemini-3.1-flash-image` / `gemini-3-pro-image` before 2026-06-25.
- No action if no image-model references exist.

## Verification notes
Literal `gemini-3.1-flash-image` and GA wording on Google Cloud blog (May 28–29, 2026). Cross-confirmed on https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image (Release date: May 28, 2026; Model ID `gemini-3.1-flash-image`). Changelog entry on ai.google.dev also lists May 28 GA and June 25 preview shutdown (used for claim only; changelog URL is in seen-urls for dedup of repeat processing, not as primary source).

## Calibration notes
Parked: no evidence our 19-component dev workflow actively uses image-generation model ids today. Trigger makes revisit concrete.
