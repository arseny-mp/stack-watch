Stack Watch 2026-06-03
Phase A (self-research): 8 candidates produced
Phase B (finalizer):
  Sources read: antigravity-self
  Total candidates: 8
  Findings after web verification: 3
  By verdict: do-now 1, experiment 2, parking 0, skip 5
  Confidence distribution: high 3, medium 0, low 0
  URLs verified: ok=3, mismatch=0, failed=0
  Cross-domain verification: confirmed_multi_domain=3, single_domain=0
Calibration applied:
  - Source-bias adjustments: 2 (Mem0 OpenCode skip; OpenClaw internal skip)
  - MultiAgentClaw strip: 0
  - do-now downgrade (single domain): 0
  - Touches trim: 1 (OTEL finding downgraded do-now→experiment due to opt-in telemetry)
Issues: Mem0 release tag cli-v0.2.8 returns 404; verified via cli-node-v0.2.8 tag instead. docs.mem0.ai/changelog fetch timed out; npmjs.com used for cross-domain on CLI finding.
