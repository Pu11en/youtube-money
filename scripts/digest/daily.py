"""Daily YouTube early-signal digest.

One list: videos that blew up in the last 2 days from channels nobody follows yet.
The point is the comparison, not the view count - a video that out-runs its own
channel got there on the idea, and an idea that works from zero can be copied.

Drew's settings (chosen 2026-09-26): max 2 days old, 250k+ views, under 200k subs,
10 items, noon Chicago.

Two ways in, both free:
  trending charts (default) - 12 categories x 16 regions (US + Europe), ~192
                              quota units of the 10,000 a day, ~1,300 English
                              videos. No search calls at all.
  --wide                    - adds 25 keyword searches for videos too new to have
                              reached any chart. Costs 25 of the 100 search calls
                              allowed per project per day, a separate limit that
                              is very easy to hit.

    python scripts/digest/daily.py            # print the digest
    python scripts/digest/daily.py --post     # print it and post it to Discord
    python scripts/digest/daily.py --wide     # cast a wider net, costs search calls
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
API = "https://www.googleapis.com/youtube/v3/"
NOW = datetime.datetime.now(datetime.UTC)

MAX_AGE_HOURS = 48
MIN_VIEWS = 250_000
MAX_SUBS = 200_000
NEW_CHANNEL_DAYS = 90     # a young channel qualifies even if it passed MAX_SUBS
TOP = 10

# Travel (19) and Education (27) have no trending chart and answer 404.
CATEGORIES = {1: "Film & Animation", 2: "Autos", 10: "Music", 15: "Pets & Animals",
              17: "Sports", 20: "Gaming", 22: "People & Blogs", 23: "Comedy",
              24: "Entertainment", 25: "News", 26: "Howto & Style",
              28: "Science & Tech"}

# US and Europe (Drew, 2026-09-26). Non-English charts still earn their place: an
# English video that charts in Sweden or the Netherlands often never charts in the
# US, and the English filter downstream throws away the local-language rest.
REGIONS = ["US", "GB", "IE", "DE", "FR", "ES", "IT", "NL", "SE", "NO", "DK",
           "FI", "PL", "BE", "AT", "CH"]

# Generic on purpose. We want movement anywhere, not inside a chosen niche.
QUERIES = ["story", "explained", "how", "why", "insane", "crazy", "first time",
           "review", "reaction", "challenge", "documentary", "day in my life",
           "worst", "best", "i tried", "caught on camera", "ranking", "asmr",
           "restore", "build", "cooking", "history", "animals", "money", "prank"]


def env(name):
    v = os.environ.get(name)
    if v:
        return v
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"')
    return ""


KEY = env("YOUTUBE_API_KEY")


def get(path, **params):
    """One API call. A 429 mentioning 'per day' is the daily search cap, not a blip."""
    params["key"] = KEY
    url = API + path + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if "per day" in body:
                raise SystemExit("Out of searches for today. Resets at 07:00 UTC.")
            if e.code == 404:                       # category with no chart
                return {"items": []}
            if e.code not in (429, 500, 503) or attempt == 3:
                raise SystemExit("YouTube API %s: %s" % (e.code, body[:300]))
            time.sleep(3 * (attempt + 1))


def english(video):
    lang = (video["snippet"].get("defaultAudioLanguage")
            or video["snippet"].get("defaultLanguage") or "")
    if lang:
        return lang.lower().startswith("en")
    title = video["snippet"]["title"]
    return len(re.sub(r"[\x00-\x7f]", "", title)) <= len(title) * 0.1


def from_trending():
    """YouTube's own per-category charts, per region. Never touches search quota."""
    found = {}
    for region in REGIONS:
        for cid, name in CATEGORIES.items():
            d = get("videos", part="snippet,statistics", chart="mostPopular",
                    regionCode=region, videoCategoryId=cid, maxResults=50)
            for item in d.get("items", []):
                found.setdefault(item["id"], (item, "%s/%s" % (region, name)))
            time.sleep(0.2)
    return found


def from_search():
    """Keyword searches, for videos the trending charts never picked up."""
    after = (NOW - datetime.timedelta(hours=MAX_AGE_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in QUERIES:
        d = get("search", part="snippet", type="video", q=q, order="viewCount",
                publishedAfter=after, maxResults=25, regionCode="US",
                relevanceLanguage="en")
        ids += [i["id"]["videoId"] for i in d.get("items", [])]
        time.sleep(1)
    ids = list(dict.fromkeys(ids))

    found = {}
    for k in range(0, len(ids), 50):
        for item in get("videos", part="snippet,statistics",
                        id=",".join(ids[k:k + 50])).get("items", []):
            found[item["id"]] = (item, "search")
    return found


def enrich(found):
    """Attach channel size and age, which is the whole basis of the comparison."""
    videos = {k: v for k, v in found.items() if english(v[0])}
    chans = sorted({v["snippet"]["channelId"] for v, _ in videos.values()})
    info = {}
    for k in range(0, len(chans), 50):
        for c in get("channels", part="snippet,statistics",
                     id=",".join(chans[k:k + 50])).get("items", []):
            info[c["id"]] = c

    rows = []
    for vid, (v, source) in videos.items():
        ch = info.get(v["snippet"]["channelId"])
        if not ch:
            continue
        subs = int(ch["statistics"].get("subscriberCount") or 0)
        views = int(v["statistics"].get("viewCount") or 0)
        pub = datetime.datetime.fromisoformat(
            v["snippet"]["publishedAt"].replace("Z", "+00:00"))
        born = datetime.datetime.fromisoformat(
            ch["snippet"]["publishedAt"].replace("Z", "+00:00"))
        age_h = max((NOW - pub).total_seconds() / 3600, 0.5)
        rows.append(dict(
            title=v["snippet"]["title"], channel=v["snippet"]["channelTitle"],
            source=source, url="https://youtu.be/" + vid, views=views, subs=subs,
            published=pub.strftime("%Y-%m-%d %H:%M"), age_h=round(age_h, 1),
            ratio=round(views / subs, 1) if subs else 0,
            channel_age_days=(NOW - born).days))
    return rows


def pick(rows):
    keep = [r for r in rows
            if r["age_h"] <= MAX_AGE_HOURS
            and r["views"] >= MIN_VIEWS
            and (r["subs"] < MAX_SUBS or r["channel_age_days"] < NEW_CHANNEL_DAYS)]
    keep.sort(key=lambda r: -r["ratio"])
    seen, out = set(), []
    for r in keep:                       # one per channel, or one uploader eats the list
        if r["channel"] in seen:
            continue
        seen.add(r["channel"])
        out.append(r)
        if len(out) == TOP:
            break
    return out


def render(picked, scanned, passed):
    local = NOW.astimezone()
    lines = ["**YouTube early signals - %s**" % local.strftime("%a %b %d"),
             "Blew up in the last 2 days from a channel with no audience yet.",
             "Scanned %d videos, %d cleared the bar, top %d by how far each beat "
             "its own channel." % (scanned, passed, len(picked)), ""]
    if not picked:
        lines.append("Nothing cleared the bar today.")
    for n, r in enumerate(picked, 1):
        young = (" - channel only %dd old" % r["channel_age_days"]
                 if r["channel_age_days"] < NEW_CHANNEL_DAYS else "")
        lines += ["**%d. %s**" % (n, r["title"][:80]),
                  "%s - %s subs%s" % (r["channel"], format(r["subs"], ","), young),
                  "%s views in %dh - **%sx its subscriber count**"
                  % (format(r["views"], ","), int(r["age_h"]), r["ratio"]),
                  "<%s>" % r["url"], ""]
    return "\n".join(lines)


def post(text):
    """Send to the Discord webhook in .env, split to stay under Discord's 2000 chars.

    flags=4 is SUPPRESS_EMBEDS: with the angle brackets it guarantees no link
    previews, so ten finds stay ten lines instead of ten video cards.
    """
    hook = env("DISCORD_WEBHOOK_URL")
    if not hook:
        print("[not posted: DISCORD_WEBHOOK_URL missing from .env]")
        return

    para = "\n\n"
    chunks, current = [], ""
    for block in text.split(para):
        if len(current) + len(block) + 2 > 1900:
            chunks.append(current.rstrip())
            current = ""
        current += block + para
    if current.strip():
        chunks.append(current.rstrip())

    for n, chunk in enumerate(chunks, 1):
        body = json.dumps({"content": chunk, "flags": 4}).encode()
        req = urllib.request.Request(
            hook, data=body,
            headers={"Content-Type": "application/json",
                     # Discord's edge answers 403 to Python's default User-Agent.
                     "User-Agent": "youtube-money-digest/1.0"})
        with urllib.request.urlopen(req) as r:
            print("[posted %d/%d] HTTP %s" % (n, len(chunks), r.status))
        time.sleep(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="also send it to Discord")
    ap.add_argument("--wide", action="store_true",
                    help="add 25 keyword searches (uses the 100/day search cap)")
    args = ap.parse_args()
    if not KEY:
        raise SystemExit("No YOUTUBE_API_KEY in .env or environment.")

    # Under Task Scheduler stdout is a log file in cp1252, and one emoji in one
    # video title is enough to kill the run before it posts anything.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    found = from_trending()
    if args.wide:
        found.update(from_search())
    rows = enrich(found)
    passed = [r for r in rows if r["age_h"] <= MAX_AGE_HOURS
              and r["views"] >= MIN_VIEWS
              and (r["subs"] < MAX_SUBS or r["channel_age_days"] < NEW_CHANNEL_DAYS)]
    text = render(pick(rows), len(rows), len(passed))
    print(text)

    outdir = os.path.join(ROOT, "data", "digest")
    os.makedirs(outdir, exist_ok=True)
    stamp = NOW.strftime("%Y-%m-%d")
    with open(os.path.join(outdir, "raw-%s.json" % stamp), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    with open(os.path.join(outdir, "digest-%s.md" % stamp), "w", encoding="utf-8") as f:
        f.write(text)

    if args.post:
        post(text)
