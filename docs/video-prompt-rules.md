# Video prompt rules

Everything here is from a source or from a measured run on this account. Nothing is
taste. Written 2026-09-26 after four failed videos.

The failure has a name: **temporal drift** — the model loses track of a subject across
frames, so a bird that is fine at second 3 has a green crest at second 9 and no head at
second 21. It is the known hard problem of video diffusion, and everything below exists
to fight it.

## The rule I broke worst: never write "no"

> *"Describe nouns, never write 'no' or 'don't'. Language models bind the strongest
> signal to the noun. When you write 'no walls,' the token the model latches onto is
> still 'walls.'"* — [veo3ai.io](https://www.veo3ai.io/blog/veo-3-negative-prompts-guide-2026)

Every prompt I wrote ended with **"No music. No subtitles. No subtitles."** That does
not remove subtitles. It asks for them, twice.

Unwanted things go in the **Negative Prompt box**, which the Blotato generate panel has
and which I never once used, as plain nouns, 3–8 of them:

```
warping, morphing, melting, distortion, extra limbs, duplicated body parts,
floating objects, text, subtitles, watermark
```

Rules for that box: 3–8 terms, never 30. Never contradict the positive prompt. Never
negate something that was not going to appear anyway.

## Positive prompt order

Camera & lens → Subject → Action & physics → Setting → Lighting → Style → Audio.
Camera first: *"the model gives more weight to whatever you mention at the beginning"*
([eachlabs](https://www.eachlabs.ai/blog/structuring-veo-3-prompts-for-better-motion-control)).

One flowing paragraph. No headers, bullets or timecodes — those read as noise
(`docs/generation-types.md`).

## Motion: describe positions, not verbs

> *"Describe specific body positions at the start and end of the action rather than a
> description of movement."* — [higgsfield](https://higgsfield.ai/blog/how-to-avoid-distortions-ai-videos)

Bad: "the bird walks across the bridge flaring its wings to balance".
Good: "starts with both feet on the third slat, body low, wings folded; ends with both
feet on the seventh slat, head over the walnut, wings still folded."

Verbs alone give floaty, weightless motion. Positions give physics.

## What actually causes the melt

| Cause | Rule |
|---|---|
| Subject too small in frame | The animal fills **a third of the frame or more**. A wide architectural shot gives the model almost no subject to hold on to. |
| Complex articulated motion | Wings flaring, balancing on a swaying surface, is close to the worst case. Keep it to one simple body action. |
| Chaining too deep | Each clip generated from the previous clip's last frame is a copy of a copy. Error compounds. Go back to the original still every 2 clips. |
| Changing several things at once | *"Change one variable at a time between shots."* Setting, angle and lighting must not all move together. |
| Long clips | Identity drift climbs with duration. Prefer 4–6s over 8s for anything articulated. |
| Camera movement described loosely | Smooth single-direction moves only. No spins, no sudden direction changes. |

## Lock these word-for-word in every shot

- The subject sentence — never paraphrased
- The lighting sentence — *"describe light source, direction, quality and lens character
  identically in every prompt"*
- The camera sentence — same body, lens, height, angle

## Order of work

1. **Test the most complex shot first.** Not last. If the hard shot melts, nothing else
   matters and you have spent nothing on the easy ones.
2. Lock the world in a **still** (50 credits) before any video (400).
3. Generate, then **watch the output** frame by frame before sending it anywhere.

## Measured on this account

- Failures refund. A refused generation costs nothing, so re-rolling is free to try.
- 8s with audio 400 credits · 6s 300 · 4s 200. Silent is 35/sec instead of 50.
- A person described by gender ("a woman's hand… her hand") was refused; "a hand" passed.
- Real named people are refused by name and by photo — see
  `tests/generation/video/verdicts.md`.

## The ceiling, measured 2026-09-26

**Both reference videos are single continuous takes.** ffmpeg scene detection at a
sensitive threshold (0.08) finds **zero cuts** in either the parrot elevator
(`data/refs/9aaY`, 30s) or the football one (`data/refs/qp4GR`, 11.7s).

That is why they flow and why stitched clips never will. There is nothing to flow
between - the camera simply runs.

**Blotato cannot produce that.** The video generator offers four models
(`mochi-v1`, `veo3`, `veo3.1/fast`, `veo3.1/fast/image-to-video`,
`veo3.1/fast/first-last-frame-to-video`), a maximum duration of **8 seconds**, and **no
extend or continue** anywhere in the editor - searched the whole UI for extend,
continue, append, longer. Google's own docs say Veo 3.1 supports video extension;
Blotato does not expose it.

So a seamless 30-second take is off the table here. The options are:
1. Accept cuts and design for them - shots that are *meant* to be separate angles,
   rather than one action chopped up.
2. `first-last-frame-to-video` between generated keyframe stills. Seamless at the
   joins, still segments. Untested, 300 credits to find out.
3. A tool with extend, which breaks the Blotato-only rule and needs Drew.

**And the likeliest explanation for the reference is that it is not AI at all.** Thirty
unbroken seconds of a bird operating a wooden lift with consistent physics is beyond
any current single generation. A real homemade parrot elevator is a known viral clip,
and the channel is 29 days old with 70 uploads - a reposting operation. If that is
right, no prompt engineering was ever going to close the gap, which is worth knowing
before spending another day on it.
