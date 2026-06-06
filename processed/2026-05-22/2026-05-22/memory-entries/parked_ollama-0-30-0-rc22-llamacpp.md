---
name: parked-ollama-0-30-0-rc22-llamacpp
description: Ollama v0.30.0-rc22 llama.cpp prerelease — wait for GA before Mem0 host upgrade
metadata:
  type: project
---

Parking entry for Ollama v0.30.0-rc22 architecture shift identified 2026-05-22 via Stack Watch.

**Trigger to revisit:** Stable Ollama v0.30.0 (non-rc) is released and embedding models used by Mem0 (e.g. nomic-embed) pass a smoke add/search on a non-production host.

**Why parked:** Pre-release rebuilds inference around llama.cpp with known model gaps (laguna-xs.2, llama3.2-vision). The Mem0 stack depends on Ollama for embeddings; upgrading the production host on rc22 risks silent embedding regressions.

**Source(s):** antigravity-self — https://github.com/ollama/ollama/releases/tag/v0.30.0-rc22

**Touches:** Ollama, Mem0
