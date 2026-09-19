# Prompt: thumbnail (ported from youtubepro `buildThumbnailPrompt` + `buildThumbnailSuggestionsPrompt`, Apache-2.0)

Two parts. Part 1 is free (the session writes it). Part 2 spends Blotato credits and is
**dry-run by default**: print the image prompt and the estimated cost, then wait for Drew's
"go" with a credit limit.

## Part 1 - five text options (free)
Generate exactly five short text options for the thumbnail of `videos/<slug>/idea.md`:
- 2-5 words, 40 chars or fewer; complement the title and promise instead of repeating them.
- Plain, specific, phone-readable. Normal title casing unless a name/acronym needs caps.
- No invented results, proof, urgency, secrets, danger, exclusivity, money or transformation.
Ask: **A-E** pick one · **F** no text · or your own words.

## Part 2 - the image prompt (Blotato image tool, or a named model through OpenCLI)
Ask first (skip anything already answered by `{{style.*}}`):
- Style: **A** photoreal · **B** illustrated · **C** cinematic-dark · **D** clean-flat · **E** the style profile's look
- Composition: **A** single subject centre · **B** subject left, text right · **C** split screen
- Lighting / colour scheme: one line each, or "use the style profile"
- Ratio: 16:9 (long) · 9:16 (Short cover)

Then compose one paragraph, no bullets:
```
Create one original <ratio> YouTube thumbnail that truthfully packages this video.
Video topic: "<title>". Viewer promise: "<honestPromise>". Thumbnail concept: "<thumbnailConcept>".
Creator direction: "<fix words, if any>".
Visual direction: style <style>; composition <composition>; camera <angle>; lighting <lighting>;
colour scheme <scheme>. <If channels/<name>/character.png exists: use the locked character reference as the subject.>
Text: render only "<chosen text>" in the <position> area, clear of faces and key objects,
heavy readable sans-serif, mobile-legible, exact spelling.  |  or: render no words, letters, logos or watermarks.
Integrity: match the promise without unsupported claims, fake proof, deceptive before/after or
false urgency; one obvious focal point and a hierarchy that reads on a phone; do not imitate a
named creator or reproduce another thumbnail; one polished image.
```
Save the prompt + chosen text to `videos/<slug>/thumbnail.md`. On "go, limit N credits":
generate one image on Blotato, append the spend to `videos/<slug>/credits.log`, post it, ask
**A** keep · **B** variation ("<direction>") · **C** redo with a fix. The kept image is
`videos/<slug>/thumbnail.png`.
