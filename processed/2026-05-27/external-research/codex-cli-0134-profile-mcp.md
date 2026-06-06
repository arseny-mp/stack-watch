# Codex CLI 0.134.0 — profile v2, MCP OAuth, thread search
**Verdict:** experiment
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** Codex, Git / GitHub, macOS / Homebrew / npm
**Original URL:** https://github.com/openai/codex/releases/tag/rust-v0.134.0
**Verify URL:** ok
**Date:** 2026-05-27
**Tags:** 
**Verification domains:** developers.openai.com, github.com, releasebot.io

## Summary
OpenAI shipped stable Codex CLI 0.134.0 on 2026-05-26. The release adds local conversation history search, makes `--profile` the primary permission-profile selector with legacy profile v1 configs rejected, improves MCP setup (per-server environments, OAuth for streamable HTTP), and allows parallel execution of read-only MCP tools that advertise `readOnlyHint`.

## What changes
- Upgrade: `npm install -g @openai/codex@0.134.0` (or `brew upgrade --cask codex` if using Homebrew cask).
- Before first run: grep `~/.codex/config.toml` for legacy profile v1 keys; follow migration links in CLI errors if upgrade fails.
- After upgrade: smoke-test one chain with Desktop Commander / other MCP servers; confirm `codex mcp` OAuth servers still connect.
- Estimated time: 30–45 minutes including regression on one repo.

## Verification notes
Literal `0.134.0` and feature bullets verified on https://developers.openai.com/codex/changelog (section dated 2026-05-26) and https://github.com/openai/codex/releases/tag/rust-v0.134.0. Third-party mirror at releasebot.io lists the same version date and feature summary.

## Calibration notes
Prior cycle skipped 0.134.0-alpha assets as changelog-empty; stable tag now has full release notes — promoted from skip to experiment. Not `do-now` because profile v1 rejection may break existing configs until migrated.
