---
name: clone-video
description: Take one YouTube link (or a digest code like D0926-2) and produce ONE finished video that copies that video beat for beat with different subjects. Use when David says "clone this", "same video but with X", "copy this trend", or pastes a link and names a swap.
---

# clone-video

**David says one thing: `clone <link>` plus what to swap. Everything else is this
skill's job.**

Written 2026-09-26 after a session burned hours and delivered a 4-second test clip of
two men sitting on chairs when the ask was an 11-second three-beat video. The test was
mistaken for the deliverable. This file exists so that cannot happen twice.

## The contract

**One finished mp4. Same length, same beats, same look, different subjects. Delivered
as a clickable link in the Discord reply.**

Not a clip. Not a sample. Not a still. Not a description of what a video would be.
A test that proves a capability is never the deliverable - it is a step, and the step
is finished when the whole video exists.

## Before spending anything: restate the finish line

First reply, one short paragraph, before any work:

> You'll get: one <N>-second vertical video. <Beat 1>, <Beat 2>, <Beat 3>. Same <set>,
> same <look>, with <the swap> instead of <the original subjects>. Roughly <N> credits.

Then **one** question, lettered, and wait. This single step would have caught the
2026-09-26 failure in its first minute.

## Steps

1. **Get the reference.** `python -m yt_dlp -f "bv*+ba/b" -o "data/refs/<id>/source.%(ext)s" <url>`
   Merge with ffmpeg (`config/machine.json` -> `ffmpeg`). Never work from the thumbnail.
2. **Watch it.** `ffmpeg -i source.mp4 -vf fps=1 frame-%02d.jpg`, then Read several
   frames - beginning, middle, end. Note the real duration, the aspect, and the cut
   points.
3. **Write the beat sheet.** One row per beat: what is on screen, what moves, what the
   camera does, how long. An 8-second cap per Veo clip means most videos are 2-4 clips.
   Save to `videos/<slug>/beats.md`.
4. **Lock the cast and the set.** Generate the opening frame once as an image, then
   start every clip from it (`veo3.1/fast/image-to-video`, or
   `veo3.1/fast/first-last-frame-to-video` for a beat that must end somewhere exact).
   Text-to-video alone gives a different face and a different room every clip - this is
   the single biggest cause of a clone that does not look like the original.
5. **Generate each beat.** `scripts/blotato/web_video.py`. It aborts before spending if
   a reference image fails to attach.
6. **Stitch.** ffmpeg concat to one mp4, matched to the original's length.
7. **Deliver.** `python scripts/send.py "the clone" videos/<slug>/final.mp4` and paste
   the printed link into the reply.
8. **Check it against the original** and say so honestly - see below.

## Done means all of these

Report this list in the final reply, every line marked, no line skipped:

- [ ] Same number of beats, in the same order
- [ ] Length within ~2 seconds of the original
- [ ] Same aspect ratio
- [ ] Same setting, same props, same lighting
- [ ] The same characters in every beat, not a new face per clip
- [ ] The payoff actually happens on screen
- [ ] One file, stitched, not a folder of clips
- [ ] Delivered as a link David can click

If a line cannot be ticked, say which and why, in the reply. Never quietly ship a
partial clone and describe it as done.

## Known walls

- **Real people are blocked.** Naming a celebrity is refused, and feeding a photo of one
  is refused too. Proven four ways on 2026-09-26, see
  `tests/generation/video/verdicts.md`. Do not re-litigate it; design the swap around it.
- **Credits are the truth, not the page.** Charged-and-held is a success, charged-then-
  refunded is a refusal. Refusals cost nothing, so prompt iteration is free.
- **Veo caps at 8 seconds**, 4/6/8 only, 9:16 available, 50 credits/sec with audio and
  35 without.

## Cost to expect

~200 credits per 4-second beat with audio. A 12-second three-beat clone is ~600 credits,
about $3.60. Say the number in the restatement, before starting.
