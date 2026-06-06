---
name: parked-ollama-v030-nvidia-driver-570
description: Ollama v0.30 needs NVIDIA driver ≥570 on Pascal — check before GPU host upgrade
metadata:
  type: project
---

Parking entry for Ollama v0.30 NVIDIA driver requirement identified 2026-06-05 via Stack Watch (Solo-source mode).

**Trigger to revisit:** Before upgrading Ollama past 0.29 on any GPU Linux host used for Mem0 embeddings or local inference.

**Why parked:** Issue #16415 (June 2, 2026) shows v0.30 silently falls back from CUDA to slow Vulkan when driver <570, causing ~5× inference regression. Official docs/gpu.mdx confirms Pascal GPUs (compute 5.0–6.2) need driver 570+. macOS Apple Silicon unaffected.

**Source(s):** https://github.com/ollama/ollama/issues/16415, https://github.com/ollama/ollama/blob/main/docs/gpu.mdx

**Touches:** Ollama, Mem0
