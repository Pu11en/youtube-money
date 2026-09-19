# The plumbing is built — here's the video test menu

## ✅ What I built (free, no credits)

**One front door for making anything.** Every skill calls the same thing, and no skill knows or cares which Blotato template does the work.

### Why that matters for what you described
You wanted it **flexible and changeable on the fly**. So:

- **Adding a new way to generate is a list edit**, not a code change. Anyone can add one.
- **Any setting can be overridden for one single run** without touching code — swap the model, the ratio, the voice, anything, just for that shot.
- Each entry carries **what it costs, how reliable it's proven to be, and what's wrong with it** — so nobody rediscovers the logo problem the hard way.

### Three safety rules baked in
- ⬜ **Nothing spends unless you say go.** Dry run is the default, always.
- ✅ **Costs get measured, never guessed.** Blotato publishes no prices, so it reads your balance before and after and **saves the real number** — the next session and the other computer inherit it automatically.
- ✅ **It refuses to cross your ceiling**, and checks your live balance first.

I also fixed the file bug — outputs are now named after **what actually arrived**, not what we hoped for.

## 🔌 The other computer can now pick this up

Everything travels in the repo except **two files per machine**:

- **The Blotato key.** Same account everywhere. ⚠️ **The credits are one shared pool** — two computers generating at once spend from the same balance, so each needs its own ceiling.
- **The OpenCLI settings.** The browser path and Chrome profile **are different on each computer, and that's expected.** Only that difference is kept local; everything else is shared.

The handoff also warns about the two traps that already cost me time: OpenCLI isn't on the normal search path, and its health check lies about the browser being disconnected.

## 🎬 What I found for video

The big discovery: **one template does almost everything.**

Each scene can take **either your own uploaded picture or a written description**, and the same call adds motion, voice and captions. That single template covers:

- ⬜ Turning **your picture into a moving clip**
- ⬜ Turning **words into a clip**
- ⬜ **Narration** in 20 voices
- ⬜ **Captions** burned in

There's a second one worth more than all of it: a **talking video that takes a character photo** and promises to keep that same character across up to 100 scenes. **If it honours the photo, that's the cheap answer to the same-face problem** that the image route just failed.

**What the API will never do:** let you name a specific video model like Kling or Veo. That stays a browser job.

## ⏳ The test I want to run, and what it costs

**Every video price is unknown.** Nobody has run one. You said use a fair amount on the hard, unreliable stuff — agreed, that's where the answers are.

### My proposal: a 900-credit ceiling
That's **about $5.40**, and it leaves you over 11,000 credits.

Four tests, cheapest and most informative first:

- ⬜ **1. Your logo, animated, with a voice line.** One scene. The simplest possible video, and it prices the backbone.
- ⬜ **2. Three scenes from words, animated, narrated, captioned.** The real shape of a Short — and it shows whether cost scales per scene.
- ⬜ **3. The same-face test.** A character photo through the talking-video template, two scenes. **This is the one that matters most.**
- ⬜ **4. Joining clips together** with music and captions — documented as free, so we confirm whether it really is.

**I stop and report after each one**, so if test 1 comes back at 600 credits I stop rather than blowing the ceiling.

### ⚠️ One honest warning
Video is where the real money goes. Image shots were 30 cents. **A video with motion could plausibly be several dollars each** — I genuinely don't know yet, which is exactly why test 1 is one scene.

## ⬜ Where things stand

**Nothing spent since the logo test. Balance 12,320. Nothing pushed to GitHub.**

The plumbing is committed and the tests are loaded — waiting on your go.
