# Mem0 Python SDK v2.0.4 — delete_linked cascading delete
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Mem0
**Original URL:** https://github.com/mem0ai/mem0/releases/tag/v2.0.4
**Verify URL:** ok
**Date:** 2026-06-01
**Tags:** 
**Verification domains:** github.com, linkloot.io

## Summary
Mem0 Python SDK v2.0.4 (published 2026-05-27) adds a `delete_linked` parameter to `delete()` and async `delete()`. When set to `True`, deleting a memory also removes older superseded memories in the v3 `linked_memory_ids` chain transitively — the delete-side counterpart of `latest_only`.

## What changes
On a non-prod Mem0 project, test `memory.delete(memory_id, delete_linked=True)` when removing superseded chain-close facts. If behavior matches intent (no stale facts resurface), adopt in agent cleanup scripts that currently call plain `delete()`.

## Verification notes
Literal match confirmed on GitHub release page: "`delete()` and async `delete()` accept `delete_linked` (default `False`)". Cross-domain confirmation on linkloot.io (2026-05-29) independently describes the same API surface and default behavior.

## Calibration notes
Release is May 27 — outside strict 48h window but not previously logged in `_seen-urls.txt` (v2.0.3 was seen). Downgraded from do-now to experiment because production Mem0 stack needs a single-chain validation before policy change.
