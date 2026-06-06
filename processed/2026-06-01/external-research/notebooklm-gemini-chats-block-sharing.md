# NotebookLM — Gemini chats block notebook sharing
**Verdict:** do-now
**Confidence:** high
**Sources:** antigravity-self
**Source count:** 1
**Touches:** NotebookLM, Gemini
**Original URL:** https://support.google.com/notebooklm/answer/17003757?hl=en
**Verify URL:** ok
**Date:** 2026-06-01
**Tags:** 
**Verification domains:** support.google.com, makeuseof.com

## Summary
Google's official NotebookLM help documents that notebooks containing Gemini chats are private and cannot be shared. When you chat with a notebook in Gemini, those conversations appear as read-only sources in NotebookLM under "Chats from Gemini" and disable the sharing function until the Gemini chat history is deleted.

## What changes
Add an explicit guardrail to the Chrome→Gemini→NotebookLM research pipeline: if a notebook must remain shareable (public link or collaborator access), do not initiate Gemini chats against that notebook. To restore sharing, delete the Gemini chat threads from Gemini Apps (~15 min to document and verify on one test notebook).

## Verification notes
Literal match on support.google.com: "Additionally, notebooks that contain Gemini chats are private and cannot be shared." Cross-domain confirmation on makeuseof.com describes the bidirectional Gemini↔NotebookLM sync and notes sharing risks when Gemini chats become notebook sources.

## Calibration notes
Secondary May 31 blazetrends coverage treated as background only; verdict anchored on official Google help, not journalism. Relevant to existing NotebookLM research pipeline experiment (partial, on-demand).
