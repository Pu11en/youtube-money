# Skills map: the toolbox, not a conveyor belt

## What we learned from the tutorial (Jacksons AI, "Stickman animation with free AI")
- One **master prompt** turns the chatbot into a production assistant. It never runs on its own: at every step it **asks a question, offers lettered choices, and waits**.
- The questions it asks, in order: source document or none → voiceover or silent → **niche** (comedy, motivational, action story, explainer, horror, suspense, true-life story, listicle, countdown, mixed) → **ratio** (9:16 Short or 16:9 long) → **length** (30s to 10 min) → **idea** (type "more" for a fresh batch, then a number) → **script cut into scenes of 6–7 words** so the voice fits a 4-second clip → **character** (yours or the default) → character sheet made and locked as the reference picture → **visual beats** (yours or the AI's) → one paragraph prompt per scene, no bullet points → **clips made one at a time**, reviewed, and only the bad ones redone → clips numbered and joined → "next" gives an **end screen + 5 thumbnail prompts** that leave empty space for text → editing: cut gaps, quiet background music with fades, captions, export.
- What makes it feel flexible: the same engine makes a horror Short or a 10-minute true-life video because **niche, ratio, length and look are answers, not code**. Every step is small enough to redo alone.
- What it does badly: the whole video lives in one chat, so nothing is saved, nothing learns, and switching tools means starting over. We fix that with files and profiles.

## Our version: skills that take orders, not a line that runs itself
### The three rules that keep it dynamic
1. **Profiles hold the niche and the style, skills hold the method.** A skill never knows it's making true crime or stickman. It reads two small files: a **niche profile** (topic, audience, mood, what the channel is about) and a **style profile** (look, character sheet, ratio, clip length, words per scene, caption style, music mood, voice). Swap the profiles and the same skills make a different channel.
2. **Every skill asks before it acts, and takes fixes in plain words.** Each run starts with its lettered questions (like the master prompt) and ends with "ok" or a fix such as "darker", "shorter", "less dramatic". A fix changes that run right away. Then the skill asks once: "save this for the whole channel?" If you say yes, it goes into the profile, so the next run starts smarter.
3. **Every skill has one job and one saved file.** You can run any skill on its own, in any order, in any session. Nothing depends on the step before it beyond "does the file it needs exist?" Credits are only spent by three skills, and each checks your limit before every call.

### The skills (12)
| # | Skill | Job in one line | Asks you | Saves | Spends credits? |
|---|-------|-----------------|----------|-------|-----------------|
| 1 | **setup** | Build or edit a niche profile and a style profile | niche, who watches, Short or long, length, voice or silent, look, character or default | `channels/<name>/niche.md`, `style.md` | no |
| 2 | **competitors** | List rival channels' breakout videos (far above their normal views) | which channels, keep which outliers | `channels/<name>/outliers.md` | no |
| 3 | **style-dna** | Measure how the picked videos are built: hook, pacing, question/answer rhythm, ending. Numbers only, never their words | ok / "less dramatic" | `channels/<name>/style-dna.md` | no |
| 4 | **ideas** | 10 ideas that fit the profiles, each with a title, promise and the viewer's wrong belief | "more", or a number | `videos/<slug>/idea.md` | no |
| 5 | **facts** | Surprising, checkable facts with a source link each; unsourced ones are marked and barred | drop / ok | `videos/<slug>/facts.md` | no (Blotato research is free) |
| 6 | **script** | Script cut into scenes sized to the clip length (6–7 words per 4-second clip; longer beats for long-form), then graded on the 8 proven checks | longer / shorter / ok / a fix | `videos/<slug>/script.md` + grade | no |
| 7 | **character** | Character-sheet prompt from the style profile or your own; makes it on Blotato, you pick one, it's locked as the reference picture | yours or default, A/B pick | `channels/<name>/character.png` + prompt | yes, tiny (1–2 images) |
| 8 | **scenes** | One paragraph prompt per scene (no bullets), each starting with the locked style sentence and the character reference | your beats or its beats | `videos/<slug>/scenes.md` | no |
| 9 | **render** | Make clips one at a time on Blotato (image, or video via the API template, or a named model like Kling/Veo through OpenCLI), post each for review, redo only the ones you reject; voice per scene if voiceover is on | ok / redo 4 / "too dark" | `videos/<slug>/clips/scene-NN.mp4`, `credits.log` | **yes**, with a limit you set first |
| 10 | **assemble** | Join clips in order, cut gaps, quiet music with fade in/out, captions in the profile's style, export | music mood, caption style | `videos/<slug>/final.mp4` | no (Blotato stitch or the free Cinco Vid assembler) |
| 11 | **thumbnail** | End-screen prompt + 5 thumbnail ideas that leave room for text; makes the one you pick | A–E | `videos/<slug>/thumbnail.png`, title, description | yes, tiny |
| 12 | **post-learn** | Post or schedule through Blotato after you've watched it; later, paste your YouTube numbers and it writes 1–3 lessons into the profiles | post / schedule at… ; results | `videos/<slug>/youtube.md`, lessons in the profiles | no |

Plus **status**: reads the files and tells you what each video has and needs. Not a skill with a job, just a reader.

### How a video actually goes (one example, not the rule)
- You: "new channel, true crime, Shorts." → **setup** asks its questions → profiles saved.
- You: "ideas" → pick D → "script" → "shorter" → ok → "character" → pick B → "scenes" → ok → "render, limit 300 credits" → review each clip, redo two → "assemble" → "thumbnail" → pick C → watch → "post it".
- Next time you could skip **character** (it's locked), run **script** twice with two ideas, or run **render** alone on a scenes file from last week. Nothing breaks because each skill only asks "do I have the file I need?".

## How sessions build a skill (so any session can add or improve one)
Each skill is one folder in `.agents/skills/<name>/` with:
- `SKILL.md`: the job in one line, the questions it asks (with lettered choices), the file it needs, the file it saves, its "done when" check, and the fixes it understands in plain words.
- `prompts/`: the prompt pieces, with `{{niche.*}}` and `{{style.*}}` holes filled from the profiles. Built from the proven kit in `research/style-cloner-sources/`, never invented.
- `examples/`: one real input and output from a paper run, so the next session sees what good looks like.
- `LEARNINGS.md`: what fixes you asked for and what got saved to a profile, dated. This is how the skill improves with use.

**Build rule:** a skill is done when it runs once end to end on the true-crime paper run with no credits (skills 7, 9 and 11 get a dry-run mode that prints what it *would* spend). Only then does it get its first real Blotato call, with a limit.

**Suggested build order** (free first, credits last): setup → ideas → script → scenes → competitors → style-dna → facts → character → render (dry run) → assemble → thumbnail → post-learn → status.

## Where each tool lives
- **Blotato API** (works from any computer with the key): research, images, scene-video template, voices, stitching, posting.
- **OpenCLI on Drew's other computer** (Chrome profile `ets3mbsm`, logged into Blotato): picking a specific video model (Kling, Veo, Runway…), animating an uploaded photo, reading Blotato's in-app prompts. `render` calls it only when the style profile names a specific model; otherwise it uses the API.
- **Cinco Vid assembler** (free, local ffmpeg): the fallback for `assemble` if Blotato's stitch fails or a video is longer than one stitch allows.
