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
| Max age | 48 hours |
| Min views | 250,000 |
| Max subscribers | 200,000 (or any size if the channel is under 90 days old) |
| Items | 10, one per channel |
| Language | English |
| Delivery | Discord webhook, noon Central |

## Commands

| Do this | Run |
|---|---|
| See it now | `python scripts/digest/daily.py` |
| See it and post it | `python scripts/digest/daily.py --post` |
| Wider net (spends search calls) | `python scripts/digest/daily.py --wide` |
| Check the schedule | `schtasks /Query /TN youtube-digest-noon` |
| Turn it off | `schtasks /Delete /TN youtube-digest-noon /F` |
| Read the last run | `data/digest/run.log` |

Every run also saves `data/digest/digest-<date>.md` and `raw-<date>.json`.

## The two limits that shaped it

- **100 `search.list` calls per project per day.** Separate from the 10,000-unit
  quota and not obvious until you hit it. This is why the default source is
  YouTube's own trending charts (`videos.list chart=mostPopular`), which cost
  1 unit each and no search calls.
- **12 regions beat 1.** Measured the same minute: US alone saw 502 videos and 22
  finds; twelve English charts saw 2,312 and 93. Cost of the difference is 144
  units of 10,000. The best find that day, a 40-day-old channel at 17.2M views,
  was invisible to the US chart.

## What it still misses

Videos in their first few hours, before any chart picks them up. `--wide` adds
keyword search for those, at 25 of the 100 daily search calls. A second free API
key in another Google Cloud project would double that budget.

## Files

- `scripts/digest/daily.py` — the digest
- `scripts/digest/run-noon.cmd` — what Task Scheduler runs
- `scripts/digest/probe.py` — the exploration that produced the examples Drew
  picked the thresholds from
