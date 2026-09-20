# Setting up the computer we'll actually work on

Written 2026-09-19, after the API side was proven here. This is the whole job: clone the repo, get
the Blotato key in, and get **OpenCLI talking to a Chrome that is logged into Blotato on that
machine**. The last part is the only fiddly bit, so most of this page is about it.

**Say this to the session over there:**
> "Read AGENTS.md and docs/setup-new-computer.md. Get me to `generate.py list` working and
> `opencli profile list` showing a connected profile. Spend nothing."

---

## 1. The repo (2 minutes)

```bash
git clone https://github.com/Pu11en/youtube-money.git
cd youtube-money
python3 --version     # 3.9+; the scripts are standard library only, no pip install
ffmpeg -version       # needed to inspect and crop video; install if missing
```

## 2. The Blotato key (2 minutes)

**The Blotato account is the same everywhere** — `kidquick360@gmail.com`. Same key, same credit pool.

```bash
cp .env.example .env
# put the key in BLOTATO_API_KEY. .env is git-ignored; never commit it.
python3 scripts/blotato/image.py doctor
```

That is free and must print `key ok`, the credit balance, and the template list. Then:

```bash
python3 scripts/blotato/generate.py list
```

which shows every technique with its measured price. If both work, **the whole API half is done** —
that is most of the pipeline, including free videos from uploaded pictures.

> ⚠️ **One shared wallet.** Both computers draw from the same balance. Before a session spends,
> check the live number rather than a remembered one, and agree a ceiling per machine.

## 3. OpenCLI + a Blotato-logged-in Chrome (the fiddly part)

### How it actually works
OpenCLI **does not launch or log into Chrome**. It talks to a **Browser Bridge extension** running
inside a Chrome you already have open, through a local daemon on port `19825`. So the requirement is
not "install OpenCLI" — it is **"a Chrome window, logged into Blotato, with the extension loaded"**.

### Install the tool
```bash
mkdir -p ~/.local/share/opencli-tool && cd ~/.local/share/opencli-tool
npm install @jackwener/opencli
export OC=~/.local/share/opencli-tool/node_modules/.bin/opencli
$OC --version      # 1.8.7 is what the working machine runs
```

> ⚠️ **It will not be on your `PATH`.** `which opencli` returning nothing does **not** mean it is
> missing — that exact confusion already cost this project time. Always call it through `$OC`, or add
> the bin directory to `PATH`.

### Install the extension into the right Chrome profile
1. Download the extension from https://github.com/jackwener/opencli/releases
2. In the Chrome profile you use for Blotato, open `chrome://extensions/`
3. Turn on **Developer Mode** (top right)
4. **Load unpacked** → select the extension folder
5. **Log into Blotato in that same profile** and leave `my.blotato.com` open

### Confirm it
```bash
$OC profile list
```
You want a line like `ets3mbsm — connected v1.0.24`. The profile name will be **different on your
machine, and that is fine** — it is just whichever Chrome profile is logged in.

> ⚠️ **`$OC doctor` lies.** On the working machine it reports `Extension: not connected` while
> `profile list` shows it connected and commands work. **Trust `profile list`.** Do not reinstall the
> extension because `doctor` complained.

### Record the machine's own settings
```bash
cp config/machine.example.json config/machine.json
```
Set `opencli_bin` to your path and `opencli_profile` to your profile name. This file is git-ignored —
**it is the only thing that differs between the two computers.** Everything else is shared.

### Two more traps
- OpenCLI drives **the active tab**. On the working machine it drifted back to another page twice
  mid-task. Keep Blotato in **its own window**, and re-`open` the URL before each step.
- Known issue #672: connecting with several Chrome profiles open can fail. Close the others.

## 4. Prove it end to end (free)

```bash
export OC=~/.local/share/opencli-tool/node_modules/.bin/opencli
$OC browser blo open https://my.blotato.com
$OC browser blo state          # numbered [N] refs for every control on the page
$OC browser blo screenshot runs/web/hello.png
$OC browser blo close
```
If `state` lists the Blotato sidebar (Inbox, Automations, Published, Videos, Settings), you are in.

## 5. What the other computer is actually for

The API half is already proven and works anywhere. **The website route is the reason that machine
matters**, because two things only exist there:

- **`image.from-two-images`** — a Pinterest-style reference to depart from *plus* a logo or character
  held exactly. No API template accepts two images. This is the workflow Drew actually wants.
- **`video.named-model`** — picking Kling, Veo or Runway by name. The API never exposes the video model.

First job over there, free, before any credits: open the Blotato image maker, list every model in the
picker, find whether an **Edit** model exists and whether it takes an uploaded reference, screenshot
each step into `runs/web/`, and write the click path into `.agents/skills/blotato-web/SKILL.md`.

## 6. Read these before starting

- `AGENTS.md` — the rules, including the two that were learned expensively: **a credit limit is a
  budget, not a green light**, and **never substitute your own taste for Drew's reference**.
- `docs/generation-plumbing.md` — the one front door every skill calls.
- `tests/generation/video/verdicts.md` — the measured prices and the big finding: **an uploaded
  picture goes into a video free and pixel-perfect, while a generated one costs 70 a scene and a
  regenerated logo comes back wrong.**
- `tests/generation/images/logo-style-verdicts.md` — why the API cannot hold a likeness.

## 7. Working habits that are not obvious
- **Video renders outlast a shell.** A render took 12 minutes while the calling shell died at 2.
  Run them with `nohup ... > runs/<name>.log 2>&1 &` and poll the log. If a call is lost, the
  creation id is in `runs/credits.log` and can be polled on its own.
- **Prices are measured, never guessed**, and a newly measured price is written back into
  `scripts/blotato/techniques.json` automatically — commit that file so the other machine inherits it.
- **Never-priced techniques refuse to run** unless given `--unknown-cost-ok`. That guard exists
  because an unpriced call cost 800 credits on a 900 ceiling that had already spent 210.

## Windows notes (David's machine, done 2026-09-19)
- No admin: Node is portable at `C:/Users/david/tools/node`, ffmpeg at `C:/Users/david/tools/ffmpeg/bin`. Prepend both to `PATH` in a session.
- OpenCLI: `C:/Users/david/.local/share/opencli-tool/node_modules/.bin/opencli.cmd`. `profile list` says "Daemon is not running" until `doctor` has run once after Chrome opened; run `doctor` first.
- The bridge extension lives in Chrome's **Default** profile here (id `ildkmabpimmkaediidaifkhjpohdnifk`); bridge profile id `x8cb8fc2`. Blotato is logged in as kidquick360.
- All of this is in `config/machine.json` (git-ignored).
