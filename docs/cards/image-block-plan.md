# Pulled the new work — here's where the picture-making stands

## ✅ What came down in the pull

**11 new commits** landed. Nothing was broken and nothing conflicted.

### What's now in the project
- **The picture-maker skeleton** — code that talks to Blotato to make a picture, with a credit meter that's supposed to stop it overspending. **Written but never actually run.**
- **A YouTube research tool** — types a topic, gets back the best-performing videos on it. This one is proven working live.
- **Seven kinds of "make something"** written down plainly: picture from words, picture from a reference picture, your own upload, clip from words, clip from a picture, clip that morphs between two pictures, and voice.
- **A map of twelve small skills** instead of one big assembly line, so you can run any step alone, in any order.
- **Picture maps of all six phases** of making a video, plus a one-page cheat sheet as a PDF.
- **A list of channels and videos David found** for reference.

## 🔑 The surprise: this computer can already spend

The handoff note said this machine had **no Blotato key**, so all the real testing had to wait for your other computer.

**That's wrong — there's a working key here.**

- Account: **kidquick360@gmail.com**, starter plan
- **12,420 credits sitting there** — roughly **$74** worth
- Blotato answers fine; it listed all 37 of its templates

So the picture tests **do not have to wait**. Only the parts that need a logged-in browser still do, because that browser tool isn't installed here.

## ⚠️ Three real problems I found before spending anything

### 1. A false alarm in the code
The code checks it can find the right Blotato template, and says it can't. **It actually can** — Blotato just spells the template's name differently than the code expects. One line to fix. Harmless, but it would scare the next session off.

### 2. Blotato hands back a video, not a picture
There's only one way in through the door: the "make a video" route. So a "picture" today is really a **one-slide slideshow rendered as a video file**. To get an actual picture you can look at, we grab the first frame out of it. The tool that does that is already installed here.

### 3. The "use my reference picture" move can't work yet
This is the important one. **The whole point** of reference pictures is keeping the same character's face across every scene of a video.

Blotato's API only offers **text-to-image** models — thirteen of them. None of the "edit this picture" models are reachable that way. I checked every one of the 37 templates.

**So that whole block of tests belongs on your other computer**, driving the Blotato website by hand — or it needs a template nobody's found yet.

## ⏳ What the plan actually is

**The goal:** you say "make a character sheet", a real picture lands in the Discord thread, and the credits it cost match what Blotato's billing screen says.

### Free first (no credits, zero risk)
- ⬜ Fix the false alarm
- ⬜ Make it save a real picture, not just a video
- ⬜ Replace the guessed prices with the thirteen models Blotato really offers
- ⬜ Write down the reference-picture answer so nobody re-checks it
- ⬜ Start a **true crime** channel profile with blanks the tests fill in
- ⬜ Run every test on a **zero-spend dry run** to shake out breakages

### Then the ones that cost money — each waits for a credit limit from you
- ⬜ Character sheet on the cheap model, then on the good one → pick the winner
- ⬜ A world, an item, a thumbnail with room for a headline
- ⬜ Upload one of your own pictures and confirm it comes back usable
- ⬜ Check the credit log against Blotato's real bill
- ⬜ Write the winning models into the channel profile so every later step inherits them

**Rough cost of the whole spending half: about 220 credits — a bit over a dollar.**

## ⬜ What I have not done

No credits spent. No code changed yet. No pushing to GitHub.

I wrote the plan down and stopped, because the next step is your call on how to run it.
