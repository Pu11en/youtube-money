# AGENTS.md — youtube-money

A Sollo.ai-style faceless YouTube maker, driven from Discord AI sessions and
built on Drew's Blotato account. **This folder is the plugin:** every Discord
session (Claude, Codex or DSH) that starts here reads this file and the skills
in `.agents/skills/` (Claude sees them through `.claude/skills`, a symlink).

## Status (2026-09-19, evening)
- Research is done. Built so far: the image block scaffolding (written, still untested live).
- **This machine has everything: the Blotato key works here (12,420 credits) and OpenCLI v1.8.7 is
  installed with profile `ets3mbsm` connected.** There is no "wait for the other computer" step.
  OpenCLI is not on `PATH`; the binary is
  `/home/drewp/.local/share/opencli-tool/node_modules/.bin/opencli`. `opencli doctor` lies about the
  extension — trust `opencli profile list`.
- **The generation plumbing is the deliverable, not any one picture.** One front door
  (`scripts/blotato/generate.py`) + a data catalog (`scripts/blotato/techniques.json`); every skill
  calls it, no skill hardcodes a template id, and `--set key=value` overrides any input on the fly.
  Dry run by default, ceiling required, costs **measured** from the balance and written back into the
  catalog. How it works and how to move it to another computer: `docs/generation-plumbing.md`.
- **Route split:** one picture in (`image.from-image`) and upload work on the **API**; two pictures
  (style ref + likeness ref) and any named video model are **website via OpenCLI**.
- **Website abilities mapped and tested (2026-09-19, David's machine):** two-reference images
  (30, logo exact), Framepack animate (55), Veo 3.1 Fast text-to-video with baked voice (200 per
  4 s). Full catalog with click paths, prices and OpenCLI traps: `docs/web-abilities.md`.
  Driver: `scripts/blotato/web.py`.
- **The big finding (2026-09-19):** a picture **uploaded** into `video.story` is reproduced
  **pixel-perfect and costs nothing** — voice, synced captions and a slow zoom come free with it. A
  picture **generated** costs 70 a scene, and a **regenerated** logo comes back wrong. So: pay to
  make the right stills once, then assemble, narrate and caption for free.
- **Measured prices** (never guessed, all from the live balance): upload 0 · `video.story` 0 with
  uploaded media, ~70 per generated+animated scene · `image.from-image` 50 · `video.character` 400 a
  scene — **avoid it**, it holds a character but ignores the one you describe. Full results:
  `tests/generation/video/verdicts.md` and `tests/generation/images/logo-style-verdicts.md`.
- **Build on `video.story`.** A 30-second Short of 8 generated scenes is roughly 560 credits (~$3.40).
- **Two computers, one account.** The Blotato key and its credit pool are shared; the OpenCLI binary
  path and Chrome profile are per-machine and live in `config/machine.json` (git-ignored, example
  committed). Another agent pulls the repo, adds `.env` + `machine.json`, and continues.
- **Drew's direction: a toolbox of human-in-the-loop skills, not a fixed
  pipeline.** Each skill has one job, asks lettered questions, takes fixes in
  plain words, and reads a niche profile + a style profile so it's niche- and
  style-agnostic. Map and build order: `docs/skills-map.md`.
- **Current focus (2026-09-19): image and video generation only.** Scripts,
  narration and niche picking wait. The 7 generation types and their test
  matrix: `docs/generation-types.md`. Build and test here — both routes work on this machine.
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
- **A credit limit is a budget, not a green light.** Drew naming a number answers
  *how much*, not *whether now*. Before any paid call, both must be true: he said
  go, **and** every input he named is actually in hand. Learned the hard way on
  2026-09-19 — a ceiling was read as a trigger and 100 credits ran on invented
  prompts (`tests/generation/images/logo-style-verdicts.md`).
- **Never substitute your own taste for his reference.** If the style reference
  hasn't arrived, stop and ask. A reference is the starting point of a picture;
  inventing the scene yourself is the failure the prompt-kit rule below exists
  to prevent.
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
- `.agents/skills/blotato-image/` — the image skill (new / from / upload, dry-run,
  credit meter). `.agents/skills/blotato-web/` — the OpenCLI website route
  (unverified). Code in `scripts/blotato/`, tests in `tests/generation/images/`.
- `.agents/skills/youtubepro/` — research → insights → ideas → script → thumbnail,
  ported from AgriciDaniel/youtubepro as on-demand file tools. `research <topic>`
  is verified live (needs a free `YOUTUBE_API_KEY` in `.env`); the other four are
  written, paper-tested only. Read its `SKILL.md` first; only `thumbnail` can spend.
- `docs/setup-new-computer.md` — **start here on a new machine:** repo, key, and the OpenCLI +
  Blotato-logged-in Chrome setup, with the traps that already cost time.
  `docs/handoff-other-computer.md` is the older, narrower version of the same thing.
- On Windows the `.claude/skills` symlink checks out as a text file; read
  `.agents/skills/` directly.
- Reuse from elsewhere, don't copy: Blotato API runner and brand-safety rules in
  `../blotato-automations`, the free ffmpeg assembler in `../cinco-vid`.
