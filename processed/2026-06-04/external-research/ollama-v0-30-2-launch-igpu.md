# Ollama v0.30.2 — launch integrations and Radeon 8060S iGPU
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Ollama, Codex
**Original URL:** https://github.com/ollama/ollama/releases/tag/v0.30.2
**Verify URL:** ok
**Date:** 2026-06-04
**Tags:** 
**Verification domains:** github.com, shipfeed.fyi

## Summary
Ollama v0.30.2 (2026-06-03) expands `ollama launch` with Cline CLI auto-install, Qwen Code integration, Radeon 8060S iGPU enabled by default, and isolated Codex launch configuration — relevant for local inference backend and Codex-via-Ollama paths.

## What changes
Upgrade Ollama to v0.30.2 or later (v0.30.4 is current stable). If using `ollama launch` with Codex, re-test launch after the `isolate Codex launch configuration` change. AMD APU users with Radeon 8060S get iGPU acceleration without manual discovery overrides.

## Verification notes
GitHub release tag `v0.30.2` contains literal bullets `discover: allow Radeon 8060S iGPU by default` and `launch: isolate Codex launch configuration`. shipfeed.fyi storyline confirms Ollama v0.30.2 with identical changelog bullets from an independent domain.

## Calibration notes
Cline CLI and Qwen Code are out-of-stack tools; trimmed actionable scope to Ollama upgrade, Radeon iGPU default, and Codex launch isolation only. Rejected AppSelfHost v0.30.1-rc0 article (tag 404 on GitHub).
