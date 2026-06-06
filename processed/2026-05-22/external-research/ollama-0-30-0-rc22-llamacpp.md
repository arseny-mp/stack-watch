# Ollama v0.30.0-rc22 — llama.cpp architecture prerelease
**Verdict:** parking
**Confidence:** low
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Ollama, Mem0
**Original URL:** https://github.com/ollama/ollama/releases/tag/v0.30.0-rc22
**Verify URL:** ok
**Date:** 2026-05-22
**Tags:** single-source

## Summary
Ollama v0.30.0-rc22 is a pre-release that moves the runtime to direct llama.cpp with GGUF compatibility and MLX acceleration on Apple Silicon. Known issues exclude laguna-xs.2 and llama3.2-vision on this build.

## What changes
No change on the production Mem0/Ollama embedding host until GA. Track release notes for stable v0.30.0 and re-validate nomic-embed and other models the stack depends on.

## Cross-source notes
Single-source only.

## Calibration notes
Prerelease on inference layer that backs Mem0 embeddings → parking. Single-source; would remain parking even with cross-source agreement due to rc risk.
