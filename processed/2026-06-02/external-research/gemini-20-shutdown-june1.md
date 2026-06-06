# Gemini 2.0 Flash models shut down — migrate model IDs now
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Gemini, NotebookLM
**Original URL:** https://therouter.ai/news/gemini-2-flash-deprecation-june-2026-migration/
**Verify URL:** ok
**Date:** 2026-06-02
**Tags:** 
**Verification domains:** therouter.ai, ai.google.dev

## Summary
Google shut down all Gemini 2.0 Flash model IDs effective June 1, 2026: gemini-2.0-flash, gemini-2.0-flash-001, gemini-2.0-flash-lite, and gemini-2.0-flash-lite-001. Any API call using these IDs now returns errors. Official replacement guidance points to gemini-3.5-flash or gemini-3.1-flash-lite.

## What changes
- Grep all product repos, env files, and Gemini-bridge scripts for `gemini-2.0-flash` and `gemini-2.0-flash-lite` strings (~30 min audit).
- Replace pinned IDs with `gemini-3.1-flash-lite` (cost-optimized) or `gemini-3.5-flash` (quality) per workload.
- Re-test Chrome→Gemini→NotebookLM pipeline if any step references 2.0 Flash models.

## Verification notes
Secondary source therouter.ai confirms June 1, 2026 hard shutdown for all four model IDs. Cross-domain primary confirmation on ai.google.dev/gemini-api/docs/changelog June 1 entry: "The following Gemini 2.0 models are now shut down" with identical model ID list.

## Calibration notes
None. Hard production breakage if any config still references retired IDs.
