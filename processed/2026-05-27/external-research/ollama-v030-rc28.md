# Ollama v0.30.0-rc28 / rc27 — llama.cpp transition, MLX Apple Silicon, iGPU disable
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Ollama, macOS / Homebrew / npm
**Original URL:** https://github.com/ollama/ollama/releases/tag/v0.30.0-rc28
**Verify URL:** ok
**Date:** 2026-05-27
**Tags:** 
**Verification domains:** github.com, release.bar

## Summary
Ollama v0.30.0-rc27 transitions the runner backend to directly support llama.cpp instead of GGML and brings MLX acceleration for Apple Silicon inference. rc28 disables integrated GPUs (iGPUs) by default and introduces the `OLLAMA_IGPU_ENABLE` environment flag to control their enablement.

## What changes
- Upgrade/Install pre-release: `curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.30.0-rc28 sh`
- On systems where iGPU support is desired, define `OLLAMA_IGPU_ENABLE=true` in the environment before starting the Ollama server.
- Run tests on Apple Silicon to verify inference speed and CPU/GPU memory split under the new MLX-accelerated llama.cpp runner.

## Verification notes
Literal match of `v0.30.0-rc28`, `OLLAMA_IGPU_ENABLE`, `llama.cpp`, and `MLX` verified on the GitHub release page and the atom feed. Pre-release tracking verified independently on release.bar.

## Calibration notes
Ollama's llama.cpp/MLX migration is now actively rolling out in rc27 and rc28. This is highly relevant to our local runner setup, and since it is verified on multiple independent domains, it is promoted to the experiment verdict.
