# Auto-run 2026-09-19: "Genghis Khan's grave has never been found"

Drew said "just go". One session did every step with no human picks in between.

| Step | Tool | Cost | Time |
|---|---|---|---|
| Research 3 niches, 25 Shorts each | youtubepro `research` (YouTube Data API) | 0 | ~1 min |
| Pick niche + idea from the numbers | session | 0 | — |
| 8-scene script, 6-7 words a line | session (tutorial rules) | 0 | — |
| Character sheet | website, nano-banana-2 | 30 | ~1 min |
| 8 scene stills, sheet + scene 1 as references | website, nano-banana-2/edit via `web_image.py` | 240 | ~12 min |
| Assemble: stills + Brian voice + captions, 9:16 | `video.story` (API), uploaded media | **0** | ~3 min |
| **Total** | | **270** (~$1.62) | ~20 min |

Result: `final-v1.mp4`, 1080x1920, 19.7 s, voice + word-highlight captions, one consistent
character across all 8 scenes (see `stills/contact.png`).

What is NOT done (the honest gaps for the fully automatic path):
- Facts are the popular legends, not sourced; no fact check ran.
- Nothing graded the script; 8 lines came out at ~20 s (Shorts sweet spot is 30-60 s).
- Captions sit centre and cover the character in some scenes (`captionPosition` should be top or bottom).
- No music, no thumbnail, no end screen, no title/description.
- No Drew gates ran (by request); nothing was posted.
- No lip-sync (Veo baked-voice would be 200 a scene); the free route gives zoom + voiceover.
