# Stack Watch — learnings.md

This file captures direct feedback, classification corrections, and overrides from the operator. The Research Agent must read this file at the start of every daily run to avoid repeating previous classification errors.

---

## Active Rules & Exclusions

1. **Ollama Releases**:
   * Default verdict: `parking lot` (rather than `do now` or `experiment`) unless the release notes explicitly mention changes to embedding handling, performance improvements on GPU Linux hosts, or changes affecting **Mem0** integrations.
2. **Claude Code CLI**:
   * Critical bug fixes (e.g. timeout fixes, api thinking blocks fixes) should default to `do now` if they affect our CLI chains. Normal beta updates default to `experiment`.
3. **Mem0 Updates**:
   * Always verify if new parameters (like `delete_linked` or vector size adjustments) are backward-compatible before upgrading.
4. **General Tool Releases**:
   * Minor version bumps (e.g., vX.Y.Z -> vX.Y.Z+1) with no major features should be given a `skip` verdict with the reason "Minor patch release, no actionable features for current dev flow".
