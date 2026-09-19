---
name: blotato-image
description: Make pictures on Blotato from Discord in plain words: a new picture from a description (I1), a picture from 1-3 reference pictures plus words (I2), or upload Drew's own picture (I3). Dry-run first, credit limit per run, one result at a time for Drew to keep, redo or fix. Use when Drew says "make", "generate", "draw", "picture", "image", "character sheet", "thumbnail", "world", "item", "redo", "variations", or names a saved asset.
---

# blotato-image

One job: turn what Drew says into one picture on Blotato, show it, and file it. Never batch-spend.

## The three moves
| Move | Drew says | What runs |
|---|---|---|
| **new** (I1) | "make a character sheet: a Victorian detective…", "a thumbnail for…" | `image.py new --prompt … --model … --ratio …` |
| **from** (I2) | "the detective in the alley with the lantern", "same world, inside the police station" | look up the named refs in `channels/<channel>/assets/`, then `image.py from --ref … --prompt …` |
| **upload** (I3) | attaches a picture: "use this as the character" | `image.py upload <file>` → save under `assets/` with a name |
Plus **redo** ("redo, less shadow") = same move again with the prompt changed, and **variations** ("3 takes") = same call 3 times, each shown.

## Every run, in this order
1. **Read the profile** if a channel is named: `channels/<channel>/style.md` gives the look sentence, default models, ratio. No channel → ask which, or use the test defaults (Shorts 9:16, `flux-schnell` for tests, `nano-banana-2` for keepers, `fal-ai/nano-banana/edit` for refs).
2. **Write the prompt** from the style rules in `docs/generation-types.md`: the character lock sentence word-for-word, the prop palette, flat style words, and a negative tail (no text, no watermark, no extra limbs, no other characters). Show Drew the prompt in 2–3 lines, not the whole thing.
3. **Dry run**: run the command without `--go`. Tell Drew: model, cost, run name, limit left.
4. **Ask**: "Spend N credits? (A) yes (B) cheaper model (C) change the prompt (D) skip". Only on A, rerun with `--go`.
5. **Show the picture** (post the file in the thread) and ask: "(A) keep (B) redo with a fix (C) 2 more takes (D) drop".
6. **File it**: keepers go to `channels/<channel>/assets/{characters,worlds,items,thumbnails}/<name>.png` with a one-line card in `assets/index.md` (name, what it is, model, the prompt used). Tests go to `runs/tests/images/` and the verdict to `tests/generation/images/verdicts.md`.
7. **Offer to save the fix**: if Drew changed a model, ratio or style words, ask once "save that for the channel?" → edit `style.md`.

## Credit rules (hard)
- Nothing spends without `--run` and `--limit`, both said by Drew in the thread. The meter (`scripts/blotato/meter.py`) stops any call that would pass the limit or the live balance.
- One picture per call. `variations` = 3 calls, 3 dry-run lines, one yes.
- Reference images through the API are **unproven** (see `docs/generation-types.md`). If a `from` result ignores the reference, say so plainly and offer the website route (`blotato-web` skill) instead of retrying blind.

## Setup on a new computer
- `python scripts/blotato/image.py doctor` — needs `BLOTATO_API_KEY` in `.env`. Prints the key check, the balance, and saves the live template list to `runs/templates.json`. Read the "Slideshow template live inputs" it prints; if a field name differs from `image.py`, fix `image.py` first.
- Test block: `python scripts/blotato/image.py test I1-01 --limit 5` then `--go`. Cases in `tests/generation/images/cases.json`.

## What it never does
- Spend without the dry-run + yes. Post anywhere. Use any generator but Blotato. Put text inside a generated picture (headlines are added at combine time).
