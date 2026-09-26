"""Probe three ways of finding early-stage YouTube movement.

Not the digest yet. This exists to produce real examples so Drew can pick a style.
Free YouTube Data API only. Each search.list costs 100 quota units of the free 10,000/day.
"""
import datetime, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

KEY = os.environ.get("YOUTUBE_API_KEY") or ""
if not KEY:
    env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    for line in open(os.path.abspath(env), encoding="utf-8"):
        if line.startswith("YOUTUBE_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')

NOW = datetime.datetime.now(datetime.UTC)
API = "https://www.googleapis.com/youtube/v3/"

# Deliberately generic: we want movement anywhere, not inside a chosen niche.
QUERIES = ["story", "explained", "how", "why", "insane", "crazy", "first time",
           "review", "reaction", "challenge", "documentary", "day in my life",
           "worst", "best", "i tried", "caught on camera", "ranking", "tier list",
           "asmr", "restore", "build", "cooking", "workout", "history", "space",
           "animals", "money", "car", "prank", "tutorial"]


def get(path, **params):
    """One API call, with backoff. YouTube answers 429 if searches come too fast."""
    params["key"] = KEY
    url = API + path + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def english(video):
    lang = (video["snippet"].get("defaultAudioLanguage")
            or video["snippet"].get("defaultLanguage") or "")
    if lang:
        return lang.lower().startswith("en")
    title = video["snippet"]["title"]
    return len(re.sub(r"[\x00-\x7f]", "", title)) <= len(title) * 0.1


def collect(hours, queries):
    """Search each query for videos published in the last `hours`, then enrich."""
    after = (NOW - datetime.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in queries:
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
        pub = datetime.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
        age_h = max((NOW - pub).total_seconds() / 3600, 0.5)
        born = datetime.datetime.fromisoformat(
            ch["snippet"]["publishedAt"].replace("Z", "+00:00"))
        rows.append(dict(
            title=v["snippet"]["title"], channel=v["snippet"]["channelTitle"],
            url="https://youtu.be/" + v["id"], views=views, subs=subs,
            published=pub.strftime("%Y-%m-%d %H:%M"), age_h=round(age_h, 1),
            vph=int(views / age_h), ratio=round(views / subs, 1) if subs else 0,
            channel_age_days=(NOW - born).days))
    return rows


def one_per_channel(rows, top):
    """Cap each channel at one entry, or a single prolific uploader eats the list."""
    seen, out = set(), []
    for r in rows:
        if r["channel"] in seen:
            continue
        seen.add(r["channel"])
        out.append(r)
        if len(out) == top:
            break
    return out


def show(label, why, rows, cols):
    """Markdown with the link on the title, so Discord renders it clickable."""
    print(chr(10) + "## " + label)
    print(why + chr(10))
    for n, r in enumerate(rows, 1):
        title = r["title"].replace("[", "(").replace("]", ")")[:70]
        print(f"{n}. **[{title}]({r['url']})**")
        print(f"   {r['channel']} - {r['subs']:,} subs - posted {r['published'][:10]}")
        print(f"   {cols(r)}")


if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 72
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rows = collect(hours, QUERIES)
    print(f"searched {len(QUERIES)} generic queries, last {hours}h -> "
          f"{len(rows)} English videos with a known channel")

    a = one_per_channel(sorted([r for r in rows if r["subs"] < 100_000], key=lambda r: -r["ratio"]), top)
    show("STYLE A - small channel, big numbers",
         "The video out-ran its own subscriber count. No audience handed it these views.",
         a, lambda r: f"{r['views']:,} views vs {r['subs']:,} subs  =  {r['ratio']}x its channel")

    b = one_per_channel(sorted([r for r in rows if r["age_h"] <= 48 and r["subs"] < 250_000],
               key=lambda r: -r["vph"]), top)
    show("STYLE B - fastest right now",
         "Posted in the last 2 days and climbing hardest per hour. Catches things mid-rise.",
         b, lambda r: f"{r['vph']:,} views/hour  ({r['views']:,} views in {r['age_h']}h)")

    c = one_per_channel(sorted([r for r in rows if r["channel_age_days"] < 365],
               key=lambda r: -r["views"]), top)
    show("STYLE C - brand new channels",
         "The channel itself is under a year old and already pulling views.",
         c, lambda r: f"{r['views']:,} views  (channel is {r['channel_age_days']} days old)")
