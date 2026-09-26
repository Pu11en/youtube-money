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
- Verdict: **PASS, and the best value on the menu**
- Credits: **210** (12,320 → 12,110) = **70 credits per animated scene**, $0.42 each
- Time: about 12 minutes to render
- Output: `vid-test-02-three-scenes-animated.mp4`, 1080×1920, **12.1 s**, h264 + aac

Genuinely broadcast-looking: a rain-slicked street under a streetlight, real reflections, real
depth. Narration in Callum, word-by-word captions with the spoken word highlighted, and each still
has actual motion (frames half a second apart differ inside one scene). Three scenes, three lines,
one call.

- **The working price of a Short:** roughly **70 credits per scene, ~4 s of finished video each**.
  A 30-second Short of 8 scenes lands near 560 credits — about **$3.40**.
- Defect: the generated stills come back wide and get **letterboxed** into the 9:16 frame, so there
  are black bars top and bottom despite asking for 9:16. Worth a crop step or a prompt that asks
  for a vertical composition.
- Process lesson: the shell call died at 2 minutes while the render kept going server-side. Video
  renders **must** run in the background writing to a log file, and the creation id is recoverable
  from `runs/credits.log` if a call is lost.

## 03 — the same-face test (`video.character`)
- Verdict: **holds a character, ignores the one you asked for, and costs far too much**
- Credits: **800** (12,110 → 11,310) = **400 per scene**, $4.80 for 16 seconds
- Output: `vid-test-03-same-face.mp4`, 1080×1920, 16 s, 2 scenes

What it got right:
- **Consistency is real.** The same young man appears in both scenes — same face, same green hood,
  same brown leather strap, same compass medallion, same fingerless gloves, indoors and outdoors.
  The template's headline promise is true.

What it got wrong:
- **It ignored the character I described.** I asked for a weathered male detective in his fifties,
  grey stubble, brown overcoat. It produced a man in his twenties in what looks like fantasy
  adventuring gear, and then held *that* consistently across both scenes. Consistent, but not yours.
- **Gibberish text**: a box in scene two is labelled "EYSCIIVE VEESE". Confirms the standing rule —
  never let a model write text inside a frame.
- **5.7× the price of `video.story`** per scene (400 vs 70) for a worse match to the brief.

**Decision: do not build on `video.character`.** It is the wrong answer to the same-face problem.
The cheap and exact answer is the one test 01 found: **make or supply the character still once, then
feed it in as uploaded media**, where it is reproduced perfectly and costs nothing to animate.

## 04 — combining clips (`video.combine`)
- Verdict: not run. The run hit its ceiling first (see below).

---

## ⚠️ The ceiling was breached, and why
Drew set **900**. The run spent **1,010** — over by 110.

The hole: a ceiling cannot stop a call whose price nobody knows. `video.character` had never been
priced, so the pre-flight check compared only what the run had *already* spent (210) against 900,
passed it, and the single call then cost 800.

**Fixed the same day.** `generate.py` now refuses any never-priced technique unless it is run with
`--unknown-cost-ok`, and prints the headroom left so the decision is deliberate. Verified: an
unpriced technique on a fresh run now refuses.

## The costs we now know, measured not guessed
| technique | credits | per what |
|---|---|---|
| `media.upload` | 0 | any file |
| `video.story`, uploaded picture | 0 | per scene, including voice and captions |
| `video.story`, generated + animated scene | 70 | per scene (~4 s) |
| `image.from-image` | 50 | per picture |
| `video.character` | 400 | per scene |

## What this block decided
- **Build the pipeline on `video.story`.** It does words-to-scene, picture-to-scene, motion, voice
  and captions in one call, and it is the cheapest thing that works.
- **Never let Blotato regenerate an asset that must stay exact.** Upload it. Free and perfect.
- **Skip `video.character`.** Consistent but uncontrollable and six times the price.
- Still unknown: `video.combine` (documented free), `image.from-text`, and both website routes.

## 2026-09-26 — Can Veo make the celebrity-swap trend? (D0926-2)

Reference: https://youtu.be/qp4GR-dd8dc — FunBall, 36.9k subs, 18.4M views in 39h.
Two footballers on chairs in a parking garage, rope tied to each chair, a third rides
off on a scooter, one chair gets yanked out. 11.7 s, 608x1080.

Route: website via OpenCLI, video-editor → Video tool → Generate.
Models offered: `fal-ai/mochi-v1`, `fal-ai/veo3`, `fal-ai/veo3.1/fast`,
`fal-ai/veo3.1/fast/image-to-video`, `fal-ai/veo3.1/fast/first-last-frame-to-video`.
Controls: aspect 16:9 / 1:1 / 9:16 · duration 4s / 6s / 8s · 720p / 1080p ·
Generate Audio switch · negative prompt.

| Test | Prompt | Result | Credits |
|---|---|---|---|
| T1 | same scene, **named** "Cristiano Ronaldo and Lionel Messi" | **refused** — `ValidationError: Unprocessable Entity` | 200 charged, **refunded** |
| T2 | identical scene, **"two young men in football kits"** | **worked** — 4 s, 720x1280 | 200 |

| T3 | same scene, **named** "Patrick Mahomes and Travis Kelce" | **refused**, twice | 400 charged, **all 400 refunded** |

**Naming a real person is refused, whatever the sport.** The block is on the name,
not the scene or the niche: T2 changed nothing but the two names and went straight
through, and T3 swapped soccer names for NFL names and hit the same wall. Tested
across two sports so this is a rule, not a one-off.

Credits are the reliable signal here, not the page: charged then fully refunded
means the run failed. The browser read-back is flaky over long waits.

**Failed generations are refunded.** 8,689 → 8,489 → 8,689 → 8,489. Testing prompts
that get rejected costs nothing, so there is no reason to guess cautiously.

**T2 quality:** the set is right first time — parking garage, fluorescent strip
lights, two chairs, blue rope tied to the chair legs, both men laughing, correct
symmetrical wide framing. This is real generated motion, not a still with a zoom.

Prompt lessons from T2:
- "football kits" gave American football shoulder pads. Say **soccer jersey**.
- Two people described once came out as near-twins. **Describe each person separately**
  or the model reuses one face.

Still open: `veo3.1/fast/image-to-video` (W7, never run) — feeding a photo instead of
a name. That is the likely method behind the reference video and the next test.

Files: `tests/generation/video/celeb-test/control-no-names.mp4` + extracted frames.

### Image-to-video is reachable but not yet drivable (2026-09-26)

`fal-ai/veo3.1/fast/image-to-video` selects fine and prices at 300 credits for 6 s.
Attaching the reference image is the blocker:

- The video picker dialog has tabs `Scene Images | Upload | Close`. Its Upload tab
  renders **no `input[type=file]`** at all, so the blob-injection trick that works for
  the image generator's Reference Images picker (`web_image.py`, `JS_INJECT_FILE`) has
  nothing to inject into. Those are two different dialogs.
- `client.upload_file` puts the file in the same `public_media` bucket the picker reads
  from, but the picker lists only registered scene images, so an API upload never
  appears there.
- The API cannot do this at all: all 37 templates are template-based (story video,
  slideshows, combine-clips). No raw image-to-video. Website is the only route.

Next person: the job is a real adapter for that dialog, not another poke. Worth checking
whether the Upload tab lazily mounts its input on a pointer event rather than a click,
and whether a scene image can be created from an arbitrary URL.

**Not blocked by this:** text-to-video with described characters works today and is
proven (T2). Only recognisable real faces need this path.
