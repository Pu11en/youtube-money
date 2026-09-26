# Daily digest — YouTube early signals

One Discord message at **noon Central**, every day. Videos that blew up in the last
2 days from channels with no audience yet.

## Why this and not the trending page
The trending page ranks by total views, so it is always movie trailers and Taylor
Swift — things that were never early. This ranks by **views ÷ subscribers**. A
10,700-sub channel at 4.7M views did it on the idea, not on an audience, and an
idea that works from zero can be copied.

## Settings (Drew's, 2026-09-26)

| Rule | Value |
|---|---|
| Max age | 48 hours, hard |
| Min views | 250,000 |
| Max subscribers | 200,000 (or any size if the channel is under 90 days old) |
| Items | 10, one per channel |
| Language | English only |
| Never repeat | video ids remembered 30 days in `data/digest/seen.json` |
| No clip farms | titles crediting another account are dropped |
| Delivery | Discord webhook, noon Central |

## Commands

| Do this | Run |
|---|---|
| See it now | `python scripts/digest/daily.py` |
| See it and post it | `python scripts/digest/daily.py --post` |
| Charts only, no search calls | `python scripts/digest/daily.py --charts-only` |
| Check the schedule | `schtasks /Query /TN youtube-digest-noon` |
| Turn it off | `schtasks /Delete /TN youtube-digest-noon /F` |
| Read the last run | `data/digest/run.log` |
| Look up an item | `python scripts/digest/lookup.py D0926-3` |
| Look up a whole digest | `python scripts/digest/lookup.py D0926` |

Every run also saves `data/digest/digest-<date>.md` and `raw-<date>.json`.

## Item codes

Each digest is named after its date - `D0926` - and its items are `D0926-1`
through `D0926-10`, printed next to each title. Say a code and step two knows
exactly which video is meant, with no re-finding and no ambiguity about "the third
one."

Codes are written to `data/digest/index.json` only when a digest actually posts,
so a code never refers to something nobody saw. `lookup.py` resolves one, and
`--json` gives a later session the whole row to work from.

## The two limits that shaped it

- **100 `search.list` calls per project per day.** Separate from the 10,000-unit
  quota and not obvious until you hit it. This is why the default source is
  YouTube's own trending charts (`videos.list chart=mostPopular`), which cost
  1 unit each and no search calls.
- **More regions beat one region.** Measured the same minute on 2026-09-26: US
  alone saw 502 videos and 22 finds; every English chart worldwide saw 2,312 and
  93; US + Europe, which is what Drew chose, sees ~1,350 and ~60. Each extra chart
  costs 1 quota unit of 10,000. The best find that day, a 40-day-old channel at
  17.2M views, was invisible to the US chart.

  Current list: US, GB, IE, DE, FR, ES, IT, NL, SE, NO, DK, FI, PL, BE, AT, CH.
  Non-English charts stay in because an English video that charts in Sweden often
  never charts in the US, and the English filter drops the local-language rest.

## Why the sort does not matter

Tried four ways of ranking the same day's candidates - views over subs, views per
hour, a damped ratio, and a blend. The top five came out nearly identical every
time. With only ~60 candidates for 10 slots the good ones win under any formula,
so effort belongs in the pool, not the sort.

## What it still misses

Videos in their first hour or two, before any chart or search index catches them.
Keyword search (25 of the 100 daily calls, on by default) closes part of that gap
and found the best item of 2026-09-26 - a 352-sub channel at 4,021x - which no
chart carried. A second free API key in another Google Cloud project would double
the search budget.

## Files

- `scripts/digest/daily.py` — the digest
- `scripts/digest/run-noon.cmd` — what Task Scheduler runs
- `scripts/digest/lookup.py` — resolve an item code like `D0926-3`
- `scripts/digest/probe.py` — the exploration that produced the examples Drew
  picked the thresholds from
