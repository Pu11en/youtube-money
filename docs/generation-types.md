# The generation types, dumbed down, and the tests for each

Scope for now (Drew, 2026-09-19): **only image and video generation.** Scripts, narration quality
and niche picking wait. The goal is a set of tested moves that any session can call in plain words.

Source for the techniques: the tutorial's own master prompt, "Stickman Explainer Engine v1.0"
(local copy in `research/style-cloner-sources/prompts/private/`, not in git), plus Blotato's model
list in `../blotato-automations/research/blotato-model-catalog.md`.

## Where generation happens in the six phases
- **Phase 2 Asset bible:** images only (character sheet, worlds, items).
- **Phase 4 Make:** images (one still per scene), then video (animate each still), then voice.
- **Phase 5 Finish:** images only (thumbnail, end screen). Combining clips isn't generation.
- Phases 1, 3 and 6 generate nothing.

## Route decided (2026-09-19, checked live)
- **I1 words -> picture: API.** The slideshow template `/base/v2/image-slideshow/5903b592-.../v1`
  offers 13 text-to-image models (flux schnell/dev/1.1-pro/1.1-pro-ultra, recraft-v3, ideogram-v2,
  photon, gpt-image-1, gpt-image-2, nano-banana, nano-banana-2, nano-banana-pro,
  seedream v4.5 text-to-image). It renders a one-slide video, so a `.png` needs a frame grab.
- **I2 picture + words -> picture: website via OpenCLI.** Confirmed by Drew. **No Edit model is
  reachable through the API** — all 37 templates were listed and checked; only the slideshow and
  the Instagram Carousel take an image model, and both enums are text-to-image only. So the `from`
  move is built on `blotato-web`, not on the template endpoint. Both routes run on this machine.
- **I3 own picture: API upload** (`POST /media`), no generation, free.

## The 7 types

### Images
| # | Type | You give | You get | Blotato route | Cost | Used for |
|---|------|----------|---------|---------------|------|----------|
| I1 | **Words → picture** | a description | a new picture | API, 17 models (Flux Schnell 1 → Nano Banana Pro 50) | 1–50 | character sheet, a world, an item, thumbnail, end screen, any scene still |
| I2 | **Picture + words → picture** | 1–3 reference pictures + a description | a new picture that keeps what the refs show | the **Edit** models (Nano Banana Edit 15, Seedream Edit 15, NB2 Edit 30, NB Pro Edit 50). Which API template exposes them, or website via OpenCLI: **to confirm** | 15–50 | every scene still with the same character / world / item |
| I3 | **Your own picture** | a file | the same file, hosted | API upload, no generation | 0 | a photo, logo or drawing you already have, as a scene still or a reference for I2 / V2 |

I2 has three flavours that are the same call with a different reference:
- **character ref** — keeps face, outfit, proportions; changes pose, place, light
- **world ref** — keeps palette, era, line style, mood; changes the subject
- **item ref** — keeps an object's shape and markings; changes where it sits
- and **mix** (character + world, or + item): 2 refs is the sweet spot, 3 the ceiling.

### Video
| # | Type | You give | You get | Blotato route | Cost | Used for |
|---|------|----------|---------|---------------|------|----------|
| V1 | **Words → clip** | a paragraph (character lock + action + background + line) | a 4–8 s clip, voice baked in if the model does sound | website only (Veo 3 / Veo 3.1 via OpenCLI); the API has no text-to-video | Veo 3.1 Fast ≈ 35–50 per second, Veo 3 1,250 per clip | the tutorial's method; hero scenes only at this price |
| V2 | **Picture → clip (animate)** | one still | that still moving for 4–8 s | API "animate" on a scene, or website: Framepack 55, Runway 85, Luma / MiniMax 170, Kling 210 | 55–210 | the normal scene clip: make the still with I2, then animate it |
| V3 | **Two pictures → clip (morph)** | a start still and an end still | a clip that travels from one to the other | website: Kling 1.6 (start + end), Veo 3.1 frames-to-video | 210+ | scene-to-scene continuity, transformations, the "match-cut" trick |
| V4 | **Voice** | the line + a voice name | audio for that line | API, 20 ElevenLabs voices | 0 | narration over V2 / V3 clips (V1 can bake it in instead) |

Not generation, but part of every test: **combine** (clips in order + music + captions → one file), API
"Combine Clips" (free) or the Cinco Vid ffmpeg assembler.

## What the master prompt teaches about prompting (structure we keep)
- **Character lock:** one sentence describing the character, repeated word-for-word in every prompt,
  never paraphrased. Same idea for a **voice lock** when voice is baked in.
- **Video prompts are one flowing paragraph.** No headers, bullets, labels or timecodes; those read as
  noise and cause glitches. Image prompts may be structured.
- **Prop palette:** name every object in frame and say nothing else appears, so the model doesn't invent props.
- **Simple motion only:** walk, stop, turn, gesture, point, shrug. Complex motion renders badly.
- **Match-cut handoff:** the last half-second of a scene matches the first half-second of the next
  (same shape, pose or object). Skip on the final scene.
- **Negative prompt on every generation**, woven into prose for video: no warping, morphing, flicker,
  extra limbs, duplicate characters, on-screen text, watermarks, logos, background music.
- **No text inside any generated image or clip.** Headlines and captions get added when combining.
- **Reference sheet as a style reference, never as the first frame.** (On Blotato this is exactly the
  open question: V2 uses a first frame; a true style reference needs the website's Veo/ingredients.)
- **Audio-safe words:** mallet not hammer, peg not nail, burst of light not explosion.
- **Timing rule for baked voice:** 6–7 words per 4-second clip, counted; a cut-off line is a word-count
  problem, not a prompt problem.
- **Thumbnails:** 5 compositions (trio, close reaction, before/after split, character vs scale, object with
  reaction), all with empty space for a headline; end screen likewise.

## The test plan (run on Drew's computer, OpenCLI logged in; small credit limit per block)
Each test: one prompt, one output, a one-line verdict, credits spent. Save under
`tests/generation/<type>/<nn>-<name>/` with the prompt, the result file and `verdict.md`.

| Block | Tests | Pass looks like | Credits (est.) |
|---|---|---|---|
| **I1 words → picture** | character sheet (cheap model vs Nano Banana 2); a world; an item; a thumbnail with empty space | sheet has the rows it asked for; no text, no extra limbs; the style reads as one look | ~100 |
| **I2 picture + words** | character ref → 3 new poses/places; world ref → new subject; item ref → new place; mix of 2; mix of 3; **and** the same test through the API template if one exposes Edit | face/outfit unchanged across the 3; palette held; item shape held; 3-ref mix still coherent | ~200 |
| **I3 own picture** | upload a drawing, use it as I2 ref; upload a photo, animate with V2 | file is used as-is; animation keeps the subject recognisable | ~60 |
| **V1 words → clip** | one 4 s Veo 3.1 Fast clip with baked voice, 7-word line; same prompt with a bullet-list version to see the glitch claim | line finishes before the clip ends; character matches the lock; bullets version worse | ~300 |
| **V2 picture → clip** | same still through Framepack, Kling 1.5, Runway; plus API "animate" on a scene | motion simple and clean; no warping; pick the cheapest that passes | ~400 |
| **V3 morph** | Kling 1.6 start + end from two I2 stills of the same character | travels cleanly; character stays the same through the middle | ~210 |
| **V4 voice** | 3 voices on the same line; laid over a V2 clip in combine | timing fits a 4 s clip; captions line up | 0 |
| **Combine** | 3 clips + music + captions through Combine Clips; the same through Cinco Vid | one file, no gaps, captions readable, music under the voice | 0 |

Rough total: about 1,300 credits for the whole matrix, roughly one $29 pack. Drew sets the limit
per block before it runs; nothing runs without it.

## After the tests
Each type that passes becomes a **move** the image/video skill understands in plain words —
"make the detective in the alley" (I2 character ref), "animate scene 4 with Kling" (V2),
"morph scene 4 into scene 5" (V3), "voice this in Brian" (V4) — with its default model and cost
written into `style.md` so it's the same on every channel until Drew changes it.
