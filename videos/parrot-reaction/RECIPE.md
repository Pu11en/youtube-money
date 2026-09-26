# I Told My Cockatoo To Say Please

The first video from this project that held together for its whole length. Kept as the
working reference for how a shot is built, not because the video itself is finished.

Watch: `final.mp4` · 30.1s · 720x1280 · 1,850 credits total (~$11)

## The cut

| # | 6s | On screen | Voice |
|---|---|---|---|
| 1 | crest flat → fans open, head tilts, beak opens | *"Do you want a treat?"* |
| 2 | crest half up, stares dead at lens, does not move | *"Say please."* |
| 3 | head turns fully away — the snub | *"Come on. Please?"* |
| 4 | head snaps back, crest thrown fully open, loud squawk | *"Okay, no treat then."* |
| 5 | leans in close to the lens, says *please* | laughing: *"There it is."* |

Shot 4 is the payoff and the thumbnail frame.

## How it was made

1. **One still first** (`set.png`, nano-banana-pro, 50 credits). Close portrait, bird
   filling the frame. Everything downstream starts here.
2. **Every shot animates that same still** with `veo3.1/fast/image-to-video`, 6s.
   Not chained off each other - chaining is a copy of a copy and the error compounds.
3. Camera, subject, setting, lighting and style sentences are **identical, word for
   word, in all five prompts**. Only the action and the line of dialogue change.
4. Action written as **start position → end position**, never as a verb.
5. Negative box on every call: `warping, morphing, melting, distortion, extra limbs,
   duplicated body parts, floating objects, text, subtitles, watermark`.
6. Stitched with ffmpeg concat, `dynaudnorm` so the five audio beds match.

Full reasoning for each rule: `docs/video-prompt-rules.md`.

## Why this shot type survives when the others melted

It is a head and a crest. No walking, no wings, no swaying surface, no invented
contraption. Every earlier attempt asked for articulated motion on an unstable object
and deformed within 20 seconds. The crest does all the acting and the model renders it
beautifully.

It is also the format that works on the channel being studied: their two biggest videos
(4.7M and 4.1M) are reaction close-ups with no props at all, while the elevator - the
one with the build - is third.

## Known flaws, unfixed

- **Shot 3's crest turns yellow.** The yellow blade artifact shows up whenever the crest
  is caught mid-transition. Fix: start that shot from a still with the crest already
  down, so it never has to interpolate.
- **Every shot is take 1.** Nothing was re-rolled. Refused generations refund, so
  re-rolling only costs when it succeeds - 2-3 takes per shot and keep the best is what
  a real pass would do.
- Drew's note: still not the *feeling* of the reference. What he wants is the bird
  trying out its toys - a thing was built for it, and we watch it use it.
