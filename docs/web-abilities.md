# Blotato website abilities (via OpenCLI) — mapped live 2026-09-19 on David's machine

Everything below was clicked through the real site in Chrome (profile `x8cb8fc2`, logged in as
kidquick360). Prices are the numbers the site showed next to the Generate button, and every paid
run was checked against the balance afterwards. **Spent: 315 credits** (11,310 → 10,995).

## The big picture
The website has the same template form as the API **plus a video editor**, and the editor is where
the extra abilities live. Everything paid happens inside an editor for one video, and the results
land on that video's timeline (and become "scene images" the picker can reuse).

Open the editor: `my.blotato.com/videos` → click a video **card** (not the pencil, that's rename)
→ `my.blotato.com/video-editor/<id>`. Left rail: **Text · Caption · Image · Shapes · Video · Audio**.

## Abilities, with results

| # | Ability | Where | Models / options | Price | Tested | Verdict |
|---|---------|-------|------------------|-------|--------|---------|
| W1 | **Words → picture** | Image → Generate | 17 models, same 13 as the API **plus 4 Edit models** | 1–50 | not run (API covers it) | — |
| W2 | **Picture + words → picture** (1 ref) | Image → Generate → pick an Edit model → Aspect Ratio + **Reference Images → Pick images** | `nano-banana/edit` 15 · `nano-banana-2/edit` 30 · `nano-banana-pro/edit` 50 · `seedream/v4.5/edit` 15 | 30 | ✅ logo → neon sign | Works. Logo re-drawn as a double neon tube: shape recognisable, not exact. |
| W3 | **Two pictures + words → picture** (style ref + likeness ref) | same panel, pick **up to 14** images from Scene Images or Upload | same Edit models | 30 | ✅ alley frame (style) + logo (likeness) → wooden sign in the alley | **Works, and the logo came out exact.** This is the workflow Drew wants. |
| W4 | **Picture → clip (animate)** | click a generated image → **Create Animated Image** → Animate tab | `framepack` 55 · `runway-gen3/turbo` 85 · `hunyuan` 135 · `luma-dream-machine` 170 · `minimax` 170 · `minimax/video-01-director` 170 · `kling 1.5 pro` 210 · `kling 1.6 pro` 210 · `veo2` 835 | 55 | ✅ Framepack on the neon logo | Works. 5 s, **480×848** (low res). Motion prompt box. |
| W5 | **Two pictures → clip (morph)** | Animate tab with **Kling 1.5 / 1.6: "End Image (Optional) → Pick an image"** | Kling 210 | not run | Exists. |
| W6 | **Words → clip, voice baked in** | Video → Generate | `mochi-v1` 135 · `veo3` 1,250 · `veo3.1/fast` · `veo3.1/fast/image-to-video` · `veo3.1/fast/first-last-frame-to-video` | Veo 3.1 Fast: **50/sec with audio, 35/sec without** (4 s = 200, 8 s = 400, 8 s silent = 280); options 4/6/8 s, 720p/1080p, Generate Audio switch, negative prompt | 200 | ✅ 4 s, audio on, 7-word spoken line | **Works.** Hand-drawn detective in a gaslit alley, mouth moving, real audio track (720×1280). The tutorial's method, on Blotato. |
| W7 | **Picture → clip with Veo** | Video → Generate → `veo3.1/fast/image-to-video` → Image → Pick | 200–400 | not run | Exists. Same audio option. |
| W8 | **First + last frame → clip with Veo** | Video → Generate → `veo3.1/fast/first-last-frame-to-video` → two picks | 200–400 | not run | Exists. Morph with sound. |
| W9 | **Stock library** | Image → Search / Video → Search | royalty-free images and videos | free | seen | Exists. |
| W10 | **Upload own file** | Image → Upload / Video → Upload / Audio (file only) | any image / video / audio | free | via picker | Works, but see the OpenCLI trap below. |
| W11 | **Captions** | Caption → Generate Captions | word-by-word, highlight colour | free | seen | Exists (the free API route already proved it). |
| W12 | **Text overlays** | Text | 12 title styles (Hormozi, Solid, Gradient, Highlight Box…) | free | seen | Exists. |
| W13 | **Voiceover** | only in the template form (20 voices), not in the editor's Audio tool | free | — | Audio tool is upload-only. |
| W14 | **Export / Download / Create Post** | editor top bar | — | free | seen | Exists. |

Not mapped yet: the AI image's **Settings** and **Style** tabs (tab clicks didn't register; likely
style presets), and what "Rerun" keeps vs. changes.

## What this decides
- **Two-reference images are real and cheap (30).** Style from one picture, identity from another,
  logo exact. Build the image skill's `from` move on the website, not the API's product template.
- **Baked-voice clips are real (200 per 4 s).** One paragraph in, a talking hand-drawn scene out.
  At 8 scenes that's 1,600 credits (~$9.60) for a 32-second Short — dearer than the 70-a-scene
  `video.story` route, so use it for hero scenes or when lip-sync matters.
- **Animate is cheap but low-res on Framepack** (480×848). Runway 85 or Hunyuan 135 next to test for
  a 9:16 that isn't soft.
- Generated images become **scene images**, so a locked character sheet can sit in a "library video"
  and be picked as a reference from any later generation in that video.

## OpenCLI driving notes (the traps that cost time today)
- `web.py` wraps it: `python scripts/blotato/web.py open|state|click|fill|eval|shot|raw …`.
- **Refs go stale fast** (the timeline re-renders). Prefer CSS selectors: `click "button[type=submit]"`,
  `click "[role=dialog] img[alt='Image 1']"`, `click "button[id$='-trigger-generate']"`.
- **Model pickers are native `<select>`s owned by React.** `select` and plain `.value=` don't stick.
  Set it through the prototype setter then dispatch `change`:
  `Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(sel,v); sel.dispatchEvent(new Event('change',{bubbles:true}))`.
  Same trick for textareas (`HTMLTextAreaElement`) with an `input` event.
- **`opencli upload` fails on the picker's native file input** ("fileChooserOpened not received").
  Workaround that works: host the file first (`client.upload_file` — free, no generation), then in
  `eval`: `fetch(url) → Blob → File → DataTransfer → input.files = dt.files → dispatch change`.
- Buttons by text: `eval "Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='Generate').click()"`.
  Scope to the active panel first (`[role=tabpanel][data-state=active]`) because several
  panels have a Generate button.
- Don't use `||` or `?.` inside `eval` strings from bash on Windows; the `.cmd` shim eats them.
- Results: image URLs in `img[src*=public_media]`, clips in `video[src*=public_media]`
  (`videogen2-anim-*` = animate, `videogen2-vid-*` = text-to-video, `videogen2-img-*` = images).
- Poll with `document.body.innerText.includes('Generating')`; Framepack ≈ 4–6 min, Veo ≈ 3 min.

## Files
- Results: `tests/generation/web/` (stills) and `runs/web/out/` (clips, git-ignored; sent to Discord).
- Screenshots of every step: `runs/web/*.png`; command log: `runs/web/log.txt`.
