---
name: visual-picker
description: Turn a scene's narration into 3 keyword sets, search Pinterest (via OpenCLI), Wikimedia Commons and Openverse, and show Drew 20 reference candidates with previews in Discord so he picks one per scene. Free, zero Blotato credits, links only. Use when Drew says "find references", "visual search", "pinterest", "show me options for scene N", or a scene needs a direction image before it is generated.
---

# visual-picker

One job: **narration in → 20 reference pictures in the thread → Drew picks one → saved to the scene.**
Nothing is downloaded; the pick is a link + a note. Zero credits.

## Run it
1. Read the scene: its spoken line, its role (hook / why / decision / price / result / ending), and the
   channel bible look (`channels/<channel>/bible.md`).
2. Write **3 keyword sets**, each 5–8 words, each a different angle:
   - **subject** — who/what is in frame (e.g. `hun warrior alone endless steppe sunset illustration`)
   - **composition** — the shot idea (e.g. `lone rider silhouette vast plain dusk graphic novel vertical`)
   - **mood/theme** — the feeling or the metaphor (e.g. `empty grassland horizon unmarked grave concept art moody`)
   Show the three sets in one line each **before** searching only if Drew asked to see them; otherwise search.
3. Search:
   ```
   python scripts/refs/search.py find --video <slug> --scene <n> --narration "<line>" --q "<set1>" --q "<set2>" --q "<set3>"
   ```
   It prints 4 Discord-ready blocks of 5 (number, title, source, why, image link). **Paste all four
   blocks into the reply as-is** — Discord previews the image links. Then ask one question:
   "Which one, 1–20? Or say what's off (darker / no people / closer) and I search again."
4. Refine = search again with changed words. Free; repeat until Drew picks.
5. Pick:
   ```
   python scripts/refs/search.py pick --video <slug> --scene <n> --n <k> --why "<Drew's words>"
   ```
   Saves `videos/<slug>/refs/scene-NN.json` and post the picked image link back with
   **"Scene N reference locked"**. Add the link to the scene's row in `videos/<slug>/card.md`.

## Using the pick as a generation input
- **Wikimedia / Openverse** results are CC or public domain: fine to pass to Blotato as a reference.
- **Pinterest** pins are someone's work: it is a *direction* reference for the prompt (composition, light,
  palette). Passing the pixels into Blotato as an Edit reference needs Drew's OK for that pick.
  Either way the generated still is ours; the pin is never stored or reused as an asset.

## Machine needs
- Pinterest search runs through OpenCLI's `pinterest search-pins` and needs the bridged Chrome to be
  logged into Pinterest (it is on David's machine). If it isn't, the script says so and the other two
  sources still return results.
- Wikimedia and Openverse need nothing.
