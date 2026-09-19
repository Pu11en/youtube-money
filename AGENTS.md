# AGENTS.md — youtube-money

A Sollo.ai-style faceless YouTube maker, driven from Discord AI sessions and
built on Drew's Blotato account. **This folder is the plugin:** every Discord
session (Claude, Codex or DSH) that starts here reads this file and the skills
in `.agents/skills/` (Claude sees them through `.claude/skills`, a symlink).

## Status (2026-09-18)
- Research is done; nothing is built yet.
- First build target: the **style cloner → script writer → script grader**,
  started from proven sources in `research/style-cloner-sources/`
  (`SUMMARY.md` first), never from invented prompts.

## Hard rules
- **Paid services: Blotato only.** Never Kie.ai, HeyGen, Apify, OpenAI/Perplexity
  API keys, Bright Data or any other outside generator — take template prompt
  text only. Blotato's API/MCP does templates; for a specific video model
  (Kling, Veo…) or animating an uploaded photo, drive Blotato's website with
  OpenCLI (Chrome profile `ets3mbsm`).
- **No credits spent** until Drew approves the script and a credit limit for
  that video. **Nothing posts** until Drew has watched it and said OK.
- **Copy structure, never wording.** YouTube's "inauthentic content" policy
  demonetizes interchangeable, mass-produced videos (see
  `research/style-cloner-sources/creators.md`).
- GitHub is always last: commit locally; push only after Drew's OK.

## Map
- `research/` — Sollo analysis, Blotato mapping, YouTube workflow, sources list
  (`youtube-money-sources.md`), and the proven prompt kit.
- `docs/diagrams/` — archify maps of the planned pipeline (JSON source + HTML + PNG).
- `.agents/skills/` — one skill per flow (to be built).
- Reuse from elsewhere, don't copy: Blotato API runner and brand-safety rules in
  `../blotato-automations`, the free ffmpeg assembler in `../cinco-vid`.
