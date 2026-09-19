# AGENTS.md — youtube-money

A Sollo.ai-style faceless YouTube maker, driven from Discord AI sessions and
built on Drew's Blotato account. **This folder is the plugin:** every Discord
session (Claude, Codex or DSH) that starts here reads this file and the skills
in `.agents/skills/` (Claude sees them through `.claude/skills`, a symlink).

## Status (2026-09-19)
- Research is done; nothing is built yet.
- **Drew's direction: a toolbox of human-in-the-loop skills, not a fixed
  pipeline.** Each skill has one job, asks lettered questions, takes fixes in
  plain words, and reads a niche profile + a style profile so it's niche- and
  style-agnostic. Map and build order: `docs/skills-map.md`.
- **Current focus (2026-09-19): image and video generation only.** Scripts,
  narration and niche picking wait. The 7 generation types and their test
  matrix: `docs/generation-types.md`. Build here, test on Drew's other computer
  (the one with OpenCLI), then add OpenCLI here.
- First niche for the no-credit paper run: true crime.
- Prompts start from proven sources in `research/style-cloner-sources/`
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
- `research/sollo-video-exact-flow.md` — reference only (we don't use Sollo): the
  exact 10-step flow from their Short and 12-min tutorial transcripts.
- `docs/skills-map.md` — **the spec:** the 12 skills, the two profiles, how a
  session builds or improves a skill, and the build order.
- `docs/video-flow.md` — one example recipe for a video (15 steps). Reference,
  not the rulebook.
- `docs/generation-types.md` — the 7 image/video generation types, what the
  master prompt teaches about prompting, and the test plan.
- `docs/diagrams/phases/` — archify maps: overview + one per phase (JSON, HTML, PNG).
- `references/youtube/` — the library of channels and videos David/Drew find.
  Storage only; add rows when asked, fetch transcripts only when asked.
- `.agents/skills/` — one skill per flow (to be built).
- Reuse from elsewhere, don't copy: Blotato API runner and brand-safety rules in
  `../blotato-automations`, the free ffmpeg assembler in `../cinco-vid`.
