# Plan: get one real picture out of Blotato, on this computer

Written 2026-09-19 after pulling the 11 new commits (image scaffolding, youtubepro, phase maps).

## The goal in one line
Turn the untested image scaffolding into a **proven move**: Drew says "make a character sheet",
a real `.png` lands in the thread, the credits spent match Blotato's billing screen — and the
reference-picture question (I2) is answered yes or no with evidence, not a guess.

## What changed since the handoff was written
The handoff assumed no Blotato key on this machine. There is one.

- Key works here: account `kidquick360@gmail.com`, plan `starter`, **12,420 credits** (~$74).
- `image.py doctor` runs clean, 37 templates pulled.
- OpenCLI is **not** installed here, so the website route still belongs to the other computer.

## Three real blockers found by reading the live template list

1. **False "template not found" warning.** `image.py` stores the bare UUID
   `5903b592-…`; the live API returns it as `/base/v2/image-slideshow/5903b592-…/v1`. The
   template is fine, the comparison is wrong. One-line fix.
2. **The API returns a video, not a picture.** The only generation endpoint the client has is
   `/videos/from-templates`. An "image" today is a one-slide slideshow rendered to mp4. To get a
   `.png` we pull frame one with ffmpeg (installed here).
3. **No Edit model is reachable through the API.** The slideshow template's `aiImageModel` enum
   is text-to-image only (flux ×4, recraft, ideogram, photon, gpt-image-1/2, nano-banana,
   nano-banana-2, nano-banana-pro, seedream v4.5 text-to-image). No `nano-banana/edit`, no
   `seedream/edit`. The Instagram Carousel template is the same. **So the whole I2 block
   (picture + words → picture) cannot run on the API as written.** It is a website/OpenCLI job,
   or it needs a Blotato template we have not found yet.

## The tasks

Check: `python3 -c "import json,py_compile;[py_compile.compile(f,doraise=True) for f in ['scripts/blotato/client.py','scripts/blotato/image.py','scripts/blotato/meter.py']];json.load(open('tests/generation/images/cases.json'));print('OK')"`

Try: `python3 scripts/blotato/image.py doctor`

### Free tasks (no credits, safe to run any time)
- [ ] Fix the template-id comparison so `doctor` matches the full path form and stops warning; print the matched template's live input names.
- [ ] Make `image.py` write a real `.png`: after a creation finishes, download the mp4 and pull frame 1 with ffmpeg into `runs/tests/images/<case>.png`; keep the mp4 beside it.
- [ ] Replace the guessed model/price table in `image.py` and `meter.py` with the 13 models the live template actually offers, and mark any price we have not confirmed as unknown rather than guessing.
- [ ] Re-scan all 37 live templates for any input that takes a reference image plus a prompt; write the answer (found / not found, with the template ids checked) into `docs/generation-types.md` so nobody re-checks it.
- [ ] Write the `channels/true-crime/` starter profile pair (`niche.md`, `style.md`) with empty default-model slots the tests will fill.
- [ ] Dry-run every I1 case end to end with `--limit 0` so the whole path is exercised with zero spend, and fix anything that breaks before real money moves.

### Spending tasks (each needs Drew's limit, said in the thread, before it runs)
- [ ] I1-01 character sheet on the cheapest model. Post the picture, write the verdict, log the credits.
- [ ] I1-02 character sheet on a quality model. Post, verdict, credits. Pick the default sheet model.
- [ ] I1-03 world and I1-04 item. Post, verdicts, credits. Pick the default scene model.
- [ ] I1-05 thumbnail with empty space for a headline. Post, verdict, credits.
- [ ] I3-01 upload Drew's own picture, confirm it comes back as a usable public URL. Post, verdict.
- [ ] Reconcile `runs/credits.log` against Blotato's billing screen for the day; write the gap, if any, into the verdicts file.
- [ ] Write the winning models and ratio into `channels/true-crime/style.md` so every later skill inherits them.

### Blocked here, belongs to the OpenCLI computer
- [ ] The whole I2 block (character ref, world ref, item ref, mix of two). Run by hand on the Blotato website first to confirm the Edit models exist there, then decide whether a skill can drive it.

## How to try it
1. Run `python3 scripts/blotato/image.py doctor`. It should print `key ok`, the credit balance, and **no warning**.
2. Run the I1-01 dry run. It should name the model, the cost and the limit left, and spend nothing.
3. After the first real run, open `runs/tests/images/` — there should be a `.png` you can look at, not only an mp4.
