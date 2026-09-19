# Handoff: continuing on Drew's computer (the one with OpenCLI + the Blotato key)

Written 2026-09-19 on David's computer. Everything here was built without a Blotato key, so the
first job over there is to prove the image path is reliable, one test at a time.

## What to say to the session over there
> "Read AGENTS.md and docs/handoff-other-computer.md. We're continuing the image tests. Limit for
> the I1 block is ___ credits."

## Setup (5 minutes)
1. `git clone https://github.com/Pu11en/youtube-money.git` (or `git pull` if it's there).
   Also clone `Pu11en/blotato-automations` beside it if you want the older Blotato notes.
2. Copy `.env.example` to `.env` and put the Blotato API key in it. `.env` is git-ignored.
3. `python scripts/blotato/image.py doctor` — free. It must print `key ok`, the credit balance, and
   the live inputs of the slideshow template. **If a field name differs from what `image.py` sends
   (`slides[].imageSource`, `slides[].textOverlay`, `aiImageModel`, `aspectRatio`), fix `image.py` first.**
4. Check OpenCLI: `opencli doctor`, then `opencli profile list` with the Blotato Chrome open. If it
   doesn't connect, install the Browser Bridge extension in that profile (see `.agents/skills/blotato-web/SKILL.md`).

## The image tests (Drew sets a limit per block)
- Cases: `tests/generation/images/cases.json`. Verdicts go in `tests/generation/images/verdicts.md`.
- Each case: dry run → Drew says yes → `--go` → the session posts the picture in the thread → Drew
  says pass/fail/redo → verdict written.
  ```
  python scripts/blotato/image.py test I1-01 --limit 5
  python scripts/blotato/image.py test I1-01 --limit 5 --go
  ```
- Order: I1-01..05 (about 141 credits total at list price), then I2-01..05 (75), then I3-01 (15).
- **The question the I2 block answers:** does the API honour a reference picture with an Edit model?
  If I2-01 comes back ignoring the sheet, stop the I2 block on the API and do the free website check
  in `blotato-web` first; then run I2-01 by hand on the website with the same prompt and compare.

## What "reliable" means before we move to video
- I1: three of the four keeper models tried, one picked as the default sheet model, one as the default
  scene model, written into a first `channels/true-crime/style.md`.
- I2: a `from` move that works on at least one route (API or website) for character, world and item
  refs, with the drift noted honestly.
- I3: an upload comes back as a public URL and can be used as a reference.
- The credit ledger (`runs/credits.log`) matches the app's billing screen for the day.

## Then
- Video tests (V1–V4) get their own `cases.json`; the plan is in `docs/generation-types.md`.
- Commit locally after each block; push only when Drew says so.
