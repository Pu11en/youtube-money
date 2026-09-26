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
SKIP_REPOSTS = True       # drop clip farms re-uploading someone else's video

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


class SearchCapReached(Exception):
    """The 100 search.list calls per project per day are gone until 07:00 UTC."""


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
                raise SearchCapReached()
            if e.code == 404:                       # category with no chart
                return {"items": []}
            if e.code not in (429, 500, 503) or attempt == 3:
                raise SystemExit("YouTube API %s: %s" % (e.code, body[:300]))
            time.sleep(3 * (attempt + 1))


ACCENTS = set("¡¿áéíóúüñàèìòùâêîôûäöëïçãõåæøœßığşþ")

# Short, high-frequency words that are near-proof of a non-English title. Kept to
# words that are not also English ("no", "son", "die", "van" would all misfire).
FOREIGN_WORDS = re.compile(
    r"\b(und|oder|nicht|ist|das|ich|du|wir|sie|mit|auf|für|von|zu|wie|"
    r"que|para|por|con|los|las|una|uno|del|muy|más|pero|todo|esta|este|"
    r"les|dans|pour|avec|sur|est|sont|tout|cette|mais|plus|"
    r"nel|della|sono|questo|come|anche|perché|"
    r"het|een|niet|voor|maar|ook|"
    r"och|inte|för|att|"
    r"bir|ile|nie|jest|jak)\b", re.I)


def english(video):
    """Language field when the uploader set one, otherwise prove it from the title.

    The old version only counted non-ASCII characters, so a Spanish title written
    in plain letters walked straight through. Measured 2026-09-26: 1 of 54.
    """
    lang = (video["snippet"].get("defaultAudioLanguage")
            or video["snippet"].get("defaultLanguage") or "")
    if lang:
        return lang.lower().startswith("en")

    title = video["snippet"]["title"]
    if any(c in ACCENTS for c in title.lower()):
        return False
    if FOREIGN_WORDS.search(title):
        return False
    # Nothing latin-alphabet left to judge (Cyrillic, Hindi, Korean, Arabic...).
    letters = re.sub(r"[^A-Za-z]", "", title)
    return len(letters) >= 6


# A title crediting another account is a clip farm re-uploading someone else's
# video, not a channel with an idea of its own. Measured 2026-09-26: 4 of 54
# candidates, two of which had reached the top ten.
REPOST = re.compile(r"(@\w|\bcredit|\bcr\s*:|\bYT\s*:|\bvia\s+@)", re.I)


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
    """Keyword searches, for videos the trending charts never picked up.

    Running out of search calls mid-way is normal, not fatal: keep whatever ids
    came back and let the charts carry the rest of the run.
    """
    after = (NOW - datetime.timedelta(hours=MAX_AGE_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in QUERIES:
        try:
            d = get("search", part="snippet", type="video", q=q, order="viewCount",
                    publishedAfter=after, maxResults=25, regionCode="US",
                    relevanceLanguage="en")
        except SearchCapReached:
            print("[search cap reached after %d queries, charts only from here]"
                  % QUERIES.index(q))
            break
        ids += [i["id"]["videoId"] for i in d.get("items", [])]
        time.sleep(1)
    ids = list(dict.fromkeys(ids))
    if not ids:
        return {}

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
            vid=vid, title=v["snippet"]["title"],
            channel=v["snippet"]["channelTitle"],
            source=source, url="https://youtu.be/" + vid, views=views, subs=subs,
            published=pub.strftime("%Y-%m-%d %H:%M"), age_h=round(age_h, 1),
            ratio=round(views / subs, 1) if subs else 0,
            channel_age_days=(NOW - born).days))
    return rows


SEEN_PATH = os.path.join(ROOT, "data", "digest", "seen.json")
SEEN_DAYS = 30            # long enough that nothing can come back around


def load_seen():
    """Video ids already sent, so a 47-hour-old video is never shown twice.

    Without this the digest repeats itself: measured 2026-09-26, 38 of the 54
    candidates were over 24h old and so were already eligible the day before.
    """
    if not os.path.exists(SEEN_PATH):
        return {}
    with open(SEEN_PATH, encoding="utf-8") as f:
        seen = json.load(f)
    cutoff = (NOW - datetime.timedelta(days=SEEN_DAYS)).strftime("%Y-%m-%d")
    return {vid: day for vid, day in seen.items() if day >= cutoff}


def save_seen(seen, picked):
    today = NOW.strftime("%Y-%m-%d")
    for r in picked:
        seen[r["vid"]] = today
    os.makedirs(os.path.dirname(SEEN_PATH), exist_ok=True)
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=1)


def eligible(rows, seen):
    return [r for r in rows
            if r["age_h"] <= MAX_AGE_HOURS
            and r["views"] >= MIN_VIEWS
            and (r["subs"] < MAX_SUBS or r["channel_age_days"] < NEW_CHANNEL_DAYS)
            and r["vid"] not in seen
            and not (SKIP_REPOSTS and REPOST.search(r["title"]))]


def pick(rows, seen):
    keep = eligible(rows, seen)
    keep.sort(key=lambda r: -r["ratio"])
    used, out = set(), []
    for r in keep:                       # one per channel, or one uploader eats the list
        if r["channel"] in used:
            continue
        used.add(r["channel"])
        out.append(r)
        if len(out) == TOP:
            break
    return out


INDEX_PATH = os.path.join(ROOT, "data", "digest", "index.json")


def digest_name():
    """Short handle for today's digest, e.g. D0926. Items are D0926-1 .. D0926-10."""
    return NOW.astimezone().strftime("D%m%d")


def save_index(picked):
    """One rolling file keyed by item id, so a later session can look up 'D0926-3'
    without knowing which day's file to open or what the numbers meant."""
    index = {}
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, encoding="utf-8") as f:
            index = json.load(f)
    name = digest_name()
    for n, r in enumerate(picked, 1):
        entry = dict(r)
        entry["digest"] = name
        entry["posted"] = NOW.astimezone().strftime("%Y-%m-%d %H:%M %Z")
        index["%s-%d" % (name, n)] = entry
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)


def render(picked, scanned, passed):
    local = NOW.astimezone()
    name = digest_name()
    lines = ["**YouTube early signals - %s - %s**"
             % (name, local.strftime("%a %b %d")),
             "Blew up in the last 2 days from a channel with no audience yet.",
             "Scanned %d videos, %d cleared the bar, top %d by how far each beat "
             "its own channel." % (scanned, passed, len(picked)),
             "Call an item out by its code, e.g. `%s-3`." % name, ""]
    if not picked:
        lines.append("Nothing cleared the bar today.")
    for n, r in enumerate(picked, 1):
        young = (" - channel only %dd old" % r["channel_age_days"]
                 if r["channel_age_days"] < NEW_CHANNEL_DAYS else "")
        lines += ["**`%s-%d`  %s**" % (name, n, r["title"][:80]),
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
    ap.add_argument("--charts-only", action="store_true",
                    help="skip the keyword searches, trending charts alone")
    args = ap.parse_args()
    if not KEY:
        raise SystemExit("No YOUTUBE_API_KEY in .env or environment.")

    # Under Task Scheduler stdout is a log file in cp1252, and one emoji in one
    # video title is enough to kill the run before it posts anything.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    found = from_trending()
    if not args.charts_only:
        # The charts only carry what is already surfacing. Search reaches the ones
        # still on the way up, and 25 calls leaves 75 of the daily 100 spare.
        found.update(from_search())
    rows = enrich(found)
    seen = load_seen()
    picked = pick(rows, seen)
    text = render(picked, len(rows), len(eligible(rows, seen)))
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
        # Only what actually went out is remembered, so a failed post does not
        # silently burn ten finds or hand out codes for items nobody saw.
        save_seen(seen, picked)
        save_index(picked)
