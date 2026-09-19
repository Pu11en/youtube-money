# The generation plumbing

One front door for making anything on Blotato, so every skill calls the same thing and no skill
hardcodes a template id. Built 2026-09-19.

## The idea
A skill should say *what* it wants, never *how* Blotato does it. The how lives in two files:

- **`scripts/blotato/techniques.json`** — the catalog. One entry per way of generating, each with its
  route, template id, what it takes, its **measured** cost, how reliable it has proven to be, and the
  known issues. Adding a technique is a data edit; no Python changes.
- **`scripts/blotato/generate.py`** — the runner. Reads the catalog, builds the inputs, refuses to
  overspend, measures what was actually charged, and names the saved file after what really arrived.

```bash
python3 scripts/blotato/generate.py list            # every technique, cost, reliability
python3 scripts/blotato/generate.py show video.story
python3 scripts/blotato/generate.py run <id> --run <block> --limit <n> [--go]
```

## The three guarantees
1. **Dry run is the default.** `--go` is the only way to spend. A `--limit` is always required. Before
   submitting it checks the live balance, what this run already spent, and — when the price is known —
   whether this call would cross the ceiling.
2. **Costs are measured, never guessed.** Blotato publishes no per-template price. Each live run reads
   the balance before and after and writes the real delta to `runs/credits.log`. The first time a
   technique's price is measured it is **written back into the catalog**, so the next session and the
   next computer inherit it.
3. **Anything is overridable on the fly.** `--set key=value` (and `--set a.b.0=value`) writes directly
   into the template inputs. A one-off experiment never needs a code change.

## What's in the catalog today
| id | route | takes | reliability |
|---|---|---|---|
| `media.upload` | api | a local file | **proven**, free |
| `image.from-image` | api | 1 picture + words | **partial** — 50 cr, great stylist, redraws logos |
| `image.from-text` | api | words | unproven |
| `video.story` | api | scenes (uploaded media *or* prompts) + voice + animate | unproven — **the backbone** |
| `video.character` | api | scenes + a character reference picture | unproven — **the same-face question** |
| `video.combine` | api | clips + music + captions | unproven, documented free |
| `image.from-two-images` | web | style ref + likeness ref | unproven — the workflow Drew wants |
| `video.named-model` | web | Kling / Veo / Runway by name | unproven |

Web-route techniques refuse to run through the API front door and print what to do instead, rather
than silently doing something weaker.

## Moving to another computer
Everything is in git except two files, one per machine:

- **`.env`** — `BLOTATO_API_KEY`. The **Blotato account is the same everywhere** and the credit pool is
  shared, so two computers generating at once draw from one balance. Agree a ceiling per machine.
- **`config/machine.json`** — copy from `config/machine.example.json`. The OpenCLI binary path and the
  Chrome profile logged into Blotato. **These differ per computer and are meant to.**

To pick up where this left off:
```bash
git pull
cp .env.example .env               # add the Blotato key
cp config/machine.example.json config/machine.json   # fix the OpenCLI path + profile
python3 scripts/blotato/image.py doctor              # free: key, balance, templates
python3 scripts/blotato/generate.py list             # what is proven and what is not
```

Two traps worth knowing before you debug them yourself:
- OpenCLI is usually **not on `PATH`**; `which opencli` finding nothing does not mean it is missing.
- `opencli doctor` reports the browser extension as missing even when it is connected. Trust
  `opencli profile list`.

## What is still unknown
Every video technique's price and reliability. Nothing in the video column has been run live yet, and
the API never lets you name a video model — that is why the web route exists in the catalog. The
`video.character` entry is the highest-value unknown: if it honours an image reference, it is the
cheap answer to keeping one face across a whole video.
