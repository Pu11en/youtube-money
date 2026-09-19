---
name: blotato-web
description: Drive Blotato's website in Drew's logged-in Chrome with OpenCLI for what the API can't do: pick an exact image or video model, use an uploaded picture as a reference with an Edit model, animate an uploaded photo, or read the in-app prompts. Use when the blotato-image or video skill says "web route", or Drew says "on the website", "with OpenCLI", "Kling", "Veo", "edit model".
---

# blotato-web (OpenCLI route)

Status 2026-09-19 evening: **OpenCLI is set up on THIS machine and the bridge is live.** The click
path itself is still unverified; everything below about attaching is now confirmed working.

**Run it like this** (the binary is not on `PATH`, so `which opencli` finds nothing):
```
export OC=/home/drewp/.local/share/opencli-tool/node_modules/.bin/opencli
$OC profile list        # ets3mbsm - connected v1.0.24
```
`$OC doctor` reports the extension as missing even when it is connected. **Trust `profile list`.**
The session drives the **active tab** and drifted back to `/agent` twice during a check, so re-`open`
the URL before each step, or keep Blotato in its own window.

Verified so far: `my.blotato.com` is logged in, and the video editor's left rail has
**Text / Caption / Image / Shapes / Video / Audio** - the `Image` tool is where the click path starts.
This route owns **image-to-image (I2)**: no API template exposes an Edit model, and Drew confirmed
the website does it.

## How OpenCLI actually attaches (verified from its docs, v1.8.8)
- It does not launch Chrome. It talks to the **Browser Bridge extension** inside the Chrome that's
  already open, through a local daemon on `localhost:19825`.
- So the Chrome profile logged into Blotato (`ets3mbsm`) must have the extension installed, and that
  Chrome must be open. Then:
  ```
  opencli doctor
  opencli profile list            # shows the connected profile(s)
  opencli profile use <name>      # or --profile / OPENCLI_PROFILE
  ```
- Sessions are named. Everything below uses session `blo`:
  ```
  opencli browser blo open https://my.blotato.com/videos
  opencli browser blo state                 # numbered [N] refs for every control
  opencli browser blo click <ref|css>
  opencli browser blo type <ref> "text"     # fill <ref> "text" to replace
  opencli browser blo select <ref> <option>
  opencli browser blo upload <ref> C:\path\file.png
  opencli browser blo wait text "Done" --timeout 600000
  opencli browser blo screenshot runs/web/step.png
  opencli browser blo get url|text|value <ref>
  opencli browser blo close
  ```
  Add `-f json` for machine output; non-interactive; exit 69 = bridge down, 75 = timeout.
- Saved command sets ("adapters") are hand-written JS at `~/.opencli/clis/blotato/<command>.js`,
  scaffolded with `opencli browser init blotato/<command>`, checked with `opencli browser verify`.
  Write one only after the click path below has been done by hand twice and worked both times.

## First thing to check on Drew's computer (free, no credits)
Goal: find where the **Edit** image models live in the app and whether they take an uploaded picture.
1. `open https://my.blotato.com` → `state` → screenshot. Find "Photo / Video" or "AI Images".
2. Open the image maker. `state` again. List every model in the model picker: expect Realistic
   (Recraft), Best for Text (Nano Banana 2), Creative (Flux) and, hopefully, the **Edit** models
   (Nano Banana Edit, Nano Banana 2 Edit, Nano Banana Pro Edit, Seedream 4.5 Edit).
3. If an Edit model exists: pick it and look for an **upload / reference image** control. Screenshot.
4. In the video editor (Videos → New → a template → "Need more customization" → Image Source →
   Upload Image): confirm the upload control and the "Create Animated Image" button and its model
   list (Framepack, Kling 1.5 Pro, Kling 1.6 with end image, Veo…).
5. Write what was found into `docs/generation-types.md` under "Blotato route" for I2 and V2/V3, with
   screenshots in `runs/web/` (not in git) and the click path in this file.

## Spending rule (same as the API)
Before any click that generates: say the model, the cost from the credit table, the run name and the
limit left; get "A" from Drew; only then click. Log it with `scripts/blotato/meter.py` (`record`) so
one ledger covers both routes. Screenshot before and after every generation click.

## Known risks
- Website changes break click paths; keep the API for everything the API can do.
- OpenCLI issue #672: connecting with several Chrome profiles open can fail; close other profiles.
