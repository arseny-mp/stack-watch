---
name: parked-gemini-3-1-flash-image-ga
description: GA image models; preview ids shut down 2026-06-25 — grep configs before deadline
metadata:
  type: project
---

Parking entry for Gemini 3.1 Flash Image GA identified 2026-05-29 via Stack Watch (Solo-source mode).

**Trigger to revisit:** `rg 'gemini-3\.(1-flash-image|pro-image)-preview' ~/Projects` returns any hit, OR any Gemini/NotebookLM automation references image preview model ids, OR date reaches 2026-06-20 (5 days before shutdown).

**Why parked:** Image-generation GA is confirmed on Google Cloud and docs, but no evidence the operator stack actively calls preview image model ids in dev workflows. Migration is date-bound, not urgent today.

**Source(s):** https://cloud.google.com/blog/products/ai-machine-learning/nano-banana-2-and-nano-banana-pro-are-generally-available , https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image

**Touches:** Gemini
