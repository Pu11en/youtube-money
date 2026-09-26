"""Daily YouTube early-signal digest.

One list: videos that blew up in the last 2 days from channels nobody follows yet.
The point is the comparison, not the view count - a video that out-runs its own
channel got there on the idea, and an idea that works from zero can be copied.

Drew's settings (chosen 2026-09-26): max 2 days old, 250k+ views, under 200k subs.

Free YouTube Data API only. Hard cap is 100 search.list calls per day per project,
so QUERIES stays well under it, leaving room to re-run once if a run fails.

    python scripts/digest/daily.py            # print the digest
    python scripts/digest/daily.py --post     # print it and post it to Discord
"""
import argparse
import datetime
import json
import os
import re
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
    """One API call, with backoff. A 429 mentioning 'per day' is the daily search cap."""
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


def collect():
    after = (NOW - datetime.timedelta(hours=MAX_AGE_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in QUERIES:
        d = get("search", part="snippet", type="video", q=q, order="viewCount",
                publishedAfter=after, maxResults=25, regionCode="US",
                relevanceLanguage="en")
        ids += [i["id"]["videoId"] for i in d.get("items", [])]
        time.sleep(1)
    ids = list(dict.fromkeys(ids))

    videos = []
    for k in range(0, len(ids), 50):
        videos += get("videos", part="snippet,statistics,contentDetails",
                      id=",".join(ids[k:k + 50])).get("items", [])
    videos = [v for v in videos if english(v)]

    chans = list({v["snippet"]["channelId"] for v in videos})
    info = {}
    for k in range(0, len(chans), 50):
        for c in get("channels", part="snippet,statistics",
                     id=",".join(chans[k:k + 50])).get("items", []):
            info[c["id"]] = c

    rows = []
    for v in videos:
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
            url="https://youtu.be/" + v["id"], views=views, subs=subs,
            published=pub.strftime("%Y-%m-%d %H:%M"), age_h=round(age_h, 1),
            vph=int(views / age_h), ratio=round(views / subs, 1) if subs else 0,
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


def render(picked, scanned):
    lines = ["**YouTube early signals - %s**" % NOW.strftime("%b %d"),
             "Posted in the last 2 days, 250k+ views, channel under 200k subs. "
             "Scanned %d videos, %d passed." % (scanned, len(picked)), ""]
    if not picked:
        lines.append("Nothing cleared the bar today.")
    for n, r in enumerate(picked, 1):
        new = (", channel %dd old" % r["channel_age_days"]
               if r["channel_age_days"] < NEW_CHANNEL_DAYS else "")
        lines += ["**%d. %s**" % (n, r["title"][:80]),
                  "%s - %s subs%s" % (r["channel"], format(r["subs"], ","), new),
                  "%s views in %dh - %sx its subscriber count"
                  % (format(r["views"], ","), int(r["age_h"]), r["ratio"]),
                  "<%s>" % r["url"], ""]
    return "\n".join(lines)


def post(text):
    """Angle-bracketed URLs above keep Discord from expanding every link."""
    base, secret, thread = (env("CCDB_API_URL"), env("CCDB_API_SECRET"),
                            env("DISCORD_THREAD_ID"))
    if not (base and secret and thread):
        print("\n[not posted: CCDB_API_URL, CCDB_API_SECRET or DISCORD_THREAD_ID missing]")
        return
    body = json.dumps({"text": text, "from_thread": thread,
                       "mode": "queue", "hop": 0}).encode()
    req = urllib.request.Request(
        "%s/api/threads/%s/message" % (base, thread), data=body,
        headers={"Authorization": "Bearer " + secret,
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        print("\n[posted]", r.status)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="also send it to Discord")
    args = ap.parse_args()
    if not KEY:
        raise SystemExit("No YOUTUBE_API_KEY in .env or environment.")

    rows = collect()
    text = render(pick(rows), len(rows))
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
