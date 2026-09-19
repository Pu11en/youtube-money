# Plan: get one real picture out of Blotato, on this computer

Written 2026-09-19 after pulling the 11 new commits (image scaffolding, youtubepro, phase maps).

## The goal in one line
Turn the untested image scaffolding into **two proven moves on one machine**: Drew says "make a
character sheet" and the API makes it; Drew says "the same detective in the alley" and the website
route makes it with the sheet as the reference. A real `.png` lands in the thread both times, and
the credits spent match Blotato's billing screen.

## What changed since the handoff was written
The handoff assumed this machine had no Blotato key and no OpenCLI. **Both assumptions are wrong.**
There is no "other computer" step left — this is the computer.

- Key works here: account `kidquick360@gmail.com`, plan `starter`, **12,420 credits** (~$74).
- `image.py doctor` runs clean, 37 templates pulled.
- **OpenCLI v1.8.7 is installed here** at
  `/home/drewp/.local/share/opencli-tool/node_modules/.bin/opencli` — not on `PATH`, which is why
  `which opencli` finds nothing. Export it as `$OC` or add it to `PATH`.
- **The Browser Bridge is live:** `opencli profile list` shows `ets3mbsm — connected v1.0.24`, and
  `my.blotato.com` is logged in. (`opencli doctor` reported the extension as missing while
  `profile list` showed it connected — trust `profile list`.)
- Verified by driving it: the Blotato **video editor has an `Image` tool** in its left rail
  (Text / Caption / Image / Shapes / Video / Audio). The click path in `blotato-web` starts there.
- Caution: the session attaches to the **active tab**, and it drifted back to `/agent` twice mid-run.
  Park Blotato in its own window, or re-`open` the URL before every step.

## Three real blockers found by reading the live template list

1. **False "template not found" warning.** `image.py` stores the bare UUID
   `5903b592-…`; the live API returns it as `/base/v2/image-slideshow/5903b592-…/v1`. The
   template is fine, the comparison is wrong. One-line fix.
2. **The API returns a video, not a picture.** The only generation endpoint the client has is
   `/videos/from-templates`. An "image" today is a one-slide slideshow rendered to mp4. To get a
   `.png` we pull frame one with ffmpeg (installed here).
3. **Image-to-image is a website job, not an API job — and that is fine.** The slideshow
   template's `aiImageModel` enum is text-to-image only (flux ×4, recraft, ideogram, photon,
   gpt-image-1/2, nano-banana, nano-banana-2, nano-banana-pro, seedream v4.5 text-to-image).
   No `nano-banana/edit`, no `seedream/edit`; the Instagram Carousel template is the same.
   **Drew confirmed (2026-09-19): Blotato does image-to-image on the website, through OpenCLI.**
   So I2 is not blocked and is not missing — it is simply built on the `blotato-web` route
   instead of the API one, and it runs on this machine. The `from` move in `blotato-image`
   should call the web route, not the template endpoint.

## The tasks

Check: `python3 -c "import json,py_compile;[py_compile.compile(f,doraise=True) for f in ['scripts/blotato/client.py','scripts/blotato/image.py','scripts/blotato/meter.py']];json.load(open('tests/generation/images/cases.json'));print('OK')"`

Try: `python3 scripts/blotato/image.py doctor`

### Free tasks (no credits, safe to run any time)
- [ ] Fix the template-id comparison so `doctor` matches the full path form and stops warning; print the matched template's live input names.
- [ ] Make `image.py` write a real `.png`: after a creation finishes, download the mp4 and pull frame 1 with ffmpeg into `runs/tests/images/<case>.png`; keep the mp4 beside it.
- [ ] Replace the guessed model/price table in `image.py` and `meter.py` with the 13 models the live template actually offers, and mark any price we have not confirmed as unknown rather than guessing.
- [ ] Write the settled routing into `docs/generation-types.md` and `AGENTS.md`: text-to-picture (I1) and upload (I3) go through the API, picture-to-picture (I2) goes through the website with OpenCLI. Record the 37 template ids already checked so nobody re-checks them.
- [ ] Put the OpenCLI path where sessions will find it: note the binary path in `blotato-web/SKILL.md` and drop the `$OC` export into `.env.example`, so no future session concludes OpenCLI is missing.
- [ ] Walk the website image-to-image path by hand with OpenCLI, spending nothing: video editor → `Image` tool → list every model in the picker, find the reference/upload control, screenshot each step into `runs/web/`. Write the exact click path into `blotato-web/SKILL.md`.
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

### The I2 block, on the website route (runs here — nothing is blocked)
Each of these needs a credit limit from Drew first, same gate as the API ones.
- [ ] I2-01 character reference → a new pose. This is the one that decides everything: if the face holds, the whole same-character pipeline is real.
- [ ] I2-02 the same character in a second scene. Note honestly what drifted between 01 and 02.
- [ ] I2-03 world reference → new subject, and I2-04 item reference → new place.
- [ ] I2-05 mix of two references (character + world) — the sweet spot the master prompt recommends.
- [ ] Once the path works twice by hand, write it as an OpenCLI adapter (`opencli browser init blotato/<command>`) so the `from` move runs as one command instead of a click script.

## How to try it
1. Run `python3 scripts/blotato/image.py doctor`. It should print `key ok`, the credit balance, and **no warning**.
2. Run the I1-01 dry run. It should name the model, the cost and the limit left, and spend nothing.
3. After the first real run, open `runs/tests/images/` — there should be a `.png` you can look at, not only an mp4.
