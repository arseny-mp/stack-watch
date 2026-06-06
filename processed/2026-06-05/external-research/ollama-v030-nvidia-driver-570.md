# Ollama v0.30 requires NVIDIA driver 570+ on Pascal GPUs
**Verdict:** parking
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Ollama, Mem0
**Original URL:** https://github.com/ollama/ollama/issues/16415
**Verify URL:** ok
**Date:** 2026-06-05
**Tags:** 
**Verification domains:** github.com/ollama/ollama (issues), github.com/ollama/ollama (docs/gpu.mdx)

## Summary
A June 2, 2026 GitHub issue documents severe performance regression after upgrading Ollama from v0.24 to v0.30 on multi-GPU Pascal hardware. Root cause: NVIDIA driver 535 was below the v0.30 CUDA runtime requirement of driver 570 or newer; Ollama fell back to Vulkan with ~5× slower inference until driver upgrade to 570.211.01.

## What changes
Before upgrading Ollama past 0.29 on any GPU Linux host used for Mem0 embeddings: run `nvidia-smi` and confirm driver ≥570. Check Ollama logs for `NVIDIA driver too old` / `required_driver="570 or newer"` before blaming model or hardware regression.

## Verification notes
Literal match on issue #16415: `required_driver="570 or newer"`, `version 0.30.0`, created 2026-06-02. Cross-confirmed in official docs/gpu.mdx: "Nvidia GPUs with compute capability 5.0 through 6.2 require driver version 570 or newer."

## Calibration notes
Relevant to Mem0 stack only on GPU Linux inference hosts. macOS Apple Silicon unaffected. Parked pending next Ollama upgrade decision on production Linux.
