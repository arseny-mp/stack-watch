# Mem0 Node CLI v0.2.8 — transitive dependency CVE remediation
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Mem0, npm, macOS / Homebrew / npm
**Original URL:** https://github.com/mem0ai/mem0/releases/tag/cli-node-v0.2.8
**Verify URL:** ok
**Date:** 2026-06-03
**Tags:** 
**Verification domains:** github.com, npmjs.com

## Summary
Mem0 Node CLI v0.2.8 (published 2026-06-01) is a security-only release pinning transitive dependencies via pnpm overrides to remediate multiple high-severity CVEs, including `@modelcontextprotocol/sdk` → ^1.25.4 (CVE-2025-66414, CVE-2026-0621), `jws`, `langsmith`, `tar-fs`, and others. Relevant if the operator machine runs `@mem0/cli` for Mem0 stack maintenance or agent-rush workflows.

## What changes
- Check install: `mem0 version` or `npm list -g @mem0/cli`.
- If present and below 0.2.8: `npm update -g @mem0/cli` (~5 min).
- Record result in one chain-close Mem0 fact if upgrade applied.

## Verification notes
Literal match on GitHub release tag cli-node-v0.2.8 listing CVE remediations including `@modelcontextprotocol/sdk` → ^1.25.4. Cross-domain confirmation on npmjs.com/package/@mem0/cli showing "0.2.8 · Published Jun 1, 2026".

## Calibration notes
Experiment not do-now because primary Mem0 deployment uses self-hosted postgres+pgvector+Python SDK; Node CLI may not be installed on operator machines. Upgrade only if `@mem0/cli` is confirmed present.
