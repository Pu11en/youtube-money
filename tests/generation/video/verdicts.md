# Video tests

Run `vid-test`, 2026-09-19. Ceiling Drew set: **900 credits**. Route: `scripts/blotato/generate.py`.
Outputs in `runs/out/` (git-ignored).

## The headline, before the detail
**Uploading your own picture into a video costs nothing and keeps it perfect. Letting Blotato
generate the picture is where all the money goes.** That single fact reframes the whole pipeline.

---

## 00 — rejected for free: the voice name
First attempt used `--voice Brian`. Blotato returned **http 422** and listed the valid values: the
full label is required, `Brian (American, deep)`. **Nothing was charged** — the dry-run and ceiling
machinery did its job and the catalog now carries all 20 full strings.

## 01 — my own picture, animated, with a voice line
- Verdict: **PASS, and better than expected**
- Credits: **0** (12,320 → 12,320)
- Time: ~22 seconds
- Output: `vid-test-01-animate-logo.mp4`, **1080×1920**, 2.2 s, h264 + **aac audio**

What came back for nothing:
- **The logo is pixel-perfect.** Wide flat dome, full-width base, correct proportions — because it
  was **uploaded, not regenerated**. Compare `image.from-image`, which redrew the same mark twice for
  50 credits a go. *This is the answer to the likeness problem: don't let Blotato re-draw an asset
  you already have.*
- **Real voiceover**, a genuine AAC track from the ElevenLabs voice.
- **Word-by-word captions**, burned in, synced to the narration, with the spoken word highlighted
  yellow. Nobody asked for these; they come free with the template.
- **A slow Ken Burns push.** Note: `animateAiImages` did **nothing** here — it only applies to
  AI-generated images. The motion on an uploaded still is the built-in zoom, and it is free.
- `trimToVoiceover` cut the clip to the length of the line, 2.2 s for a 7-word sentence.

### What this means for the build
A video assembled entirely from pictures we already have — uploaded, not generated — appears to cost
**nothing but the pictures themselves**. Spend the credits on making the right stills once, then
assemble, narrate and caption for free.

## 02 — three scenes generated from words, animated, narrated
- Verdict: **pending**
- Credits: **210 charged within the first minute**, and it was still rendering after four.
- The shell call hit a 2-minute limit while the render continued server-side; recovered by polling
  the creation id from the ledger. **Lesson for every session: video renders run in the background
  with output to a log file, never inline.**
- This is the number that matters for costing a real Short: three generated-and-animated scenes.

## 03 — the same-face test (`video.character`)
- Verdict: not run yet

## 04 — combining clips (`video.combine`)
- Verdict: not run yet
