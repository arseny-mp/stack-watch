# Ollama v0.30.0-rc31 — nomic-embed-text input lowercasing
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Ollama, Mem0
**Original URL:** https://github.com/ollama/ollama/releases/tag/v0.30.0-rc31
**Verify URL:** ok
**Date:** 2026-05-31
**Tags:** 
**Verification domains:** github.com, appselfhost.com

## Summary
Ollama pre-release v0.30.0-rc31 (published assets refreshed 2026-05-29) enforces lowercase input for `nomic-embed-text`, matching the model card. Our Mem0 stack uses Ollama for embeddings; upgrading without re-indexing can desynchronize vector search against existing pgvector rows.

## What changes
On a staging Mac host: `curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.30.0-rc31 sh`. Embed the same mixed-case test string on rc28 vs rc31 and diff cosine similarity. If production upgrade proceeds, schedule a Mem0 corpus re-embed before cutover.

## Verification notes
Literal match on GitHub release: "`nomic-embed-text` now converts inputs to lowercase per the model card where prior Ollama versions incorrectly preserved mixed case." Cross-confirmed on appselfhost.com (2026-05-29) describing the same breaking behavior change and re-indexing risk.

## Calibration notes
Pre-release only — do not bump production Ollama until stable v0.30.0 ships or staging test passes. rc28 already tracked in seen-urls; rc31 is the new candidate with explicit embed behavior note.
