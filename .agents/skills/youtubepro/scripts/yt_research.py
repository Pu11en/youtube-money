#!/usr/bin/env python3
"""Public YouTube Data API v3 research snapshot (ported from AgriciDaniel/youtubepro, Apache-2.0).

Three calls: search.list -> videos.list -> channels.list. Writes snapshot.json + snapshot.md.
Never zero-fills missing public fields. No paid provider is involved (API key is free, quota-limited).
"""
import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

BASE = "https://www.googleapis.com/youtube/v3"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def load_key():
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if key:
        return key
    for env_path in (os.path.join(ROOT, ".env"), os.path.join(os.path.expanduser("~"), ".youtube-money.env")):
        if os.path.exists(env_path):
            for line in open(env_path, encoding="utf-8"):
                if line.startswith("YOUTUBE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    return ""


def get_json(url, stage):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            reason = json.loads(body)["error"]["errors"][0]["reason"]
        except Exception:
            reason = body[:200]
        sys.exit(f"[{stage}] YouTube HTTP {e.code}: {reason}")


def iso_seconds(d):
    if not d:
        return None
    m = re.match(r"^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", d)
    if not m:
        return None
    days, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def opt_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def published_after(v):
    days = {"hour": 1 / 24, "today": 1, "week": 7, "month": 30, "year": 365}.get(v)
    if not days:
        return None
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat().replace("+00:00", "Z")


def fetch(query, max_results, order, published, duration, key):
    p = {"part": "snippet", "q": query, "type": "video", "maxResults": str(max_results), "key": key, "order": order}
    pa = published_after(published)
    if pa:
        p["publishedAfter"] = pa
    if duration != "any":
        p["videoDuration"] = duration
    search = get_json(f"{BASE}/search?{urllib.parse.urlencode(p)}", "search")
    ids = [i.get("id", {}).get("videoId") for i in search.get("items", [])]
    ids = [i for i in ids if i]
    warnings = []
    videos, channels = {}, {}
    if ids:
        vp = {"part": "snippet,statistics,contentDetails,status,topicDetails,paidProductPlacementDetails,liveStreamingDetails",
              "id": ",".join(ids), "key": key, "maxResults": "50"}
        vd = get_json(f"{BASE}/videos?{urllib.parse.urlencode(vp)}", "videoDetails")
        videos = {v["id"]: v for v in vd.get("items", [])}
        if len(videos) < len(ids):
            warnings.append(f"videoDetails returned {len(videos)}/{len(ids)} rows")
        cids = sorted({v["snippet"]["channelId"] for v in videos.values()})
        if cids:
            cp = {"part": "snippet,statistics,topicDetails,brandingSettings", "id": ",".join(cids), "key": key, "maxResults": "50"}
            cd = get_json(f"{BASE}/channels?{urllib.parse.urlencode(cp)}", "channels")
            channels = {c["id"]: c for c in cd.get("items", [])}
            if len(channels) < len(cids):
                warnings.append(f"channels returned {len(channels)}/{len(cids)} rows")
    rows = []
    for vid in ids:
        v = videos.get(vid)
        if not v:
            continue
        sn, st, cdet, status = v.get("snippet", {}), v.get("statistics", {}), v.get("contentDetails", {}), v.get("status", {})
        ch = channels.get(sn.get("channelId"), {})
        chs = ch.get("statistics", {})
        thumbs = sn.get("thumbnails", {})
        rows.append({
            "id": vid, "title": sn.get("title"), "channelId": sn.get("channelId"), "channelTitle": sn.get("channelTitle"),
            "publishedAt": sn.get("publishedAt"), "description": (sn.get("description") or "")[:320],
            "tags": (sn.get("tags") or [])[:12], "categoryId": sn.get("categoryId"),
            "language": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage"),
            "thumbnailUrl": (thumbs.get("high") or thumbs.get("default") or {}).get("url"),
            "duration": cdet.get("duration"), "durationSeconds": iso_seconds(cdet.get("duration")),
            "definition": cdet.get("definition"), "hasCaptions": cdet.get("caption") == "true",
            "viewCount": opt_int(st.get("viewCount")), "likeCount": opt_int(st.get("likeCount")),
            "commentCount": opt_int(st.get("commentCount")),
            "madeForKids": status.get("madeForKids"), "embeddable": status.get("embeddable"), "license": status.get("license"),
            "topicCategories": (v.get("topicDetails", {}).get("topicCategories") or [])[:8],
            "hasPaidProductPlacement": v.get("paidProductPlacementDetails", {}).get("hasPaidProductPlacement"),
            "liveBroadcastContent": sn.get("liveBroadcastContent"),
            "channel": {
                "subscriberCount": None if chs.get("hiddenSubscriberCount") else opt_int(chs.get("subscriberCount")),
                "videoCount": opt_int(chs.get("videoCount")), "viewCount": opt_int(chs.get("viewCount")),
                "country": ch.get("snippet", {}).get("country"), "publishedAt": ch.get("snippet", {}).get("publishedAt"),
                "description": (ch.get("snippet", {}).get("description") or "")[:240],
                "topicCategories": (ch.get("topicDetails", {}).get("topicCategories") or [])[:6],
            } if ch else None,
        })
    return {
        "provider": "youtube-data-api-v3", "query": query,
        "filters": {"order": order, "published": published, "duration": duration, "maxResults": max_results},
        "retrievedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "regionCode": search.get("regionCode"),
        "totalResultsApprox": opt_int(search.get("pageInfo", {}).get("totalResults")),
        "orderedVideoIds": ids, "warnings": warnings, "videos": rows,
    }


def analytics(snap, now=None):
    now = now or datetime.now(timezone.utc)
    vids = snap["videos"]
    views = [v["viewCount"] for v in vids if v["viewCount"] is not None]
    vpd, inter, reach, ages = [], [], [], []
    for v in vids:
        if v["publishedAt"]:
            age = max((now - datetime.fromisoformat(v["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 86400, 1)
            ages.append(age)
            if v["viewCount"] is not None:
                vpd.append((v["id"], v["viewCount"] / age))
        if None not in (v["viewCount"], v["likeCount"], v["commentCount"]) and v["viewCount"]:
            inter.append((v["likeCount"] + v["commentCount"]) / v["viewCount"])
        subs = (v.get("channel") or {}).get("subscriberCount")
        if subs and v["viewCount"] is not None:
            reach.append((v["id"], v["viewCount"] / subs))
    dur = Counter()
    for v in vids:
        s = v["durationSeconds"]
        dur["unknown" if s is None else "under4min" if s < 240 else "4to20min" if s <= 1200 else "over20min"] += 1
    rec = Counter()
    for a in ages:
        rec["7d" if a <= 7 else "30d" if a <= 30 else "1y" if a <= 365 else "older"] += 1
    tags = Counter(t.strip().lower() for v in vids for t in v["tags"])
    chan = Counter(v["channelTitle"] for v in vids)
    n = len(vids)
    cov = {k: sum(1 for v in vids if v.get(k) is not None) for k in ("viewCount", "likeCount", "commentCount", "durationSeconds", "language")}
    cov["tags"] = sum(1 for v in vids if v["tags"])
    cov["subscriberCount"] = sum(1 for v in vids if (v.get("channel") or {}).get("subscriberCount") is not None)

    def top(pairs):
        return [{"id": i, "value": round(x, 2)} for i, x in sorted(pairs, key=lambda p: -p[1])[:5]]

    return {
        "sampleSize": n,
        "views": {"median": statistics.median(views) if views else None,
                  "average": round(statistics.mean(views)) if views else None,
                  "max": max(views) if views else None, "rows": len(views)},
        "viewsPerDay": {"median": round(statistics.median([x for _, x in vpd]), 1) if vpd else None, "top": top(vpd),
                        "note": "age-normalized public proxy, not real-time velocity"},
        "visibleInteractionRate": {"median": round(statistics.median(inter), 4) if inter else None, "rows": len(inter),
                                   "note": "(likes+comments)/views on complete rows only; not engagement or satisfaction"},
        "reachVsSubscribers": {"top": top(reach), "note": "views / current rounded subscriber count; subs are today's, not at publish time"},
        "durationMix": dict(dur), "recencyMix": dict(rec),
        "recurringTags": [{"tag": t, "count": c} for t, c in tags.most_common(15) if c > 1],
        "channelConcentration": {"uniqueChannels": len(chan), "top": [{"channel": c, "videos": k} for c, k in chan.most_common(5)]},
        "coverage": {k: f"{c}/{n}" for k, c in cov.items()},
        "caveats": ["totalResultsApprox is not search volume", "one personalized, region-sensitive snapshot, not a trend",
                    "under4min is not necessarily a Short", "thumbnail pixels were not inspected",
                    "missing fields stay unavailable, never zero"],
    }


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "query"


def fmt(n):
    if n is None:
        return "n/a"
    return f"{n:,}" if isinstance(n, int) else f"{n:,.1f}"


def write_md(path, snap, an):
    L = [f"# Research snapshot: {snap['query']}", "",
         f"- snapshotId: `{snap['snapshotId']}`  retrieved: {snap['retrievedAt']}  region: {snap.get('regionCode') or 'n/a'}",
         f"- filters: {snap['filters']}  approx total matches: {fmt(snap['totalResultsApprox'])} (not search volume)",
         f"- sample: {an['sampleSize']} videos, {an['channelConcentration']['uniqueChannels']} channels; warnings: {snap['warnings'] or 'none'}",
         "", "## Deterministic analytics (observed)",
         f"- views: median {fmt(an['views']['median'])}, average {fmt(an['views']['average'])}, max {fmt(an['views']['max'])} ({an['views']['rows']} rows)",
         f"- views/day median {fmt(an['viewsPerDay']['median'])}; top: " + ", ".join(f"{t['id']}={t['value']}" for t in an['viewsPerDay']['top']),
         f"- visible interaction rate median {an['visibleInteractionRate']['median']} ({an['visibleInteractionRate']['rows']} complete rows)",
         "- reach vs subs top: " + ", ".join(f"{t['id']}={t['value']}x" for t in an['reachVsSubscribers']['top']),
         f"- duration mix: {an['durationMix']}   recency: {an['recencyMix']}",
         "- recurring tags: " + (", ".join(f"{t['tag']} ({t['count']})" for t in an['recurringTags']) or "none repeat"),
         "- top channels: " + ", ".join(f"{c['channel']} ({c['videos']})" for c in an['channelConcentration']['top']),
         f"- coverage: {an['coverage']}", "",
         "## Source videos (YouTube result order)", "",
         "| # | id | title | channel | published | dur(s) | views | likes | comments | subs |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for i, v in enumerate(snap["videos"], 1):
        subs = (v.get("channel") or {}).get("subscriberCount")
        title = (v["title"] or "").replace("|", "/")[:70]
        L.append(f"| {i} | {v['id']} | {title} | {(v['channelTitle'] or '')[:30]} | {(v['publishedAt'] or '')[:10]} | "
                 f"{fmt(v['durationSeconds'])} | {fmt(v['viewCount'])} | {fmt(v['likeCount'])} | {fmt(v['commentCount'])} | {fmt(subs)} |")
    L += ["", "## Caveats", *[f"- {c}" for c in an["caveats"]], ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def selftest_snapshot():
    now = datetime.now(timezone.utc)

    def mk(i, days, views, likes, comments, secs, subs, tags):
        return {
            "id": f"vid{i}", "title": f"Sample video {i}", "channelId": f"c{i % 3}", "channelTitle": f"Channel {i % 3}",
            "publishedAt": (now - timedelta(days=days)).isoformat().replace("+00:00", "Z"), "description": "", "tags": tags,
            "categoryId": "24", "language": "en", "thumbnailUrl": None, "duration": None, "durationSeconds": secs,
            "definition": "hd", "hasCaptions": False, "viewCount": views, "likeCount": likes, "commentCount": comments,
            "madeForKids": False, "embeddable": True, "license": "youtube", "topicCategories": [],
            "hasPaidProductPlacement": False, "liveBroadcastContent": "none",
            "channel": {"subscriberCount": subs, "videoCount": 10, "viewCount": 1000, "country": "US",
                        "publishedAt": None, "description": "", "topicCategories": []},
        }

    vids = [mk(1, 3, 120000, 5000, 300, 55, 20000, ["true crime", "shorts"]),
            mk(2, 40, 8000, None, 20, 700, 1000, ["true crime"]),
            mk(3, 400, 900000, 30000, 2000, 1500, None, ["documentary"]),
            mk(4, 10, None, None, None, None, 500, [])]
    return {"provider": "selftest", "query": "true crime shorts",
            "filters": {"order": "relevance", "published": "any", "duration": "any", "maxResults": 4},
            "retrievedAt": now.isoformat(), "regionCode": "US", "totalResultsApprox": 1000000,
            "orderedVideoIds": [v["id"] for v in vids], "warnings": [], "videos": vids}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("query", nargs="?")
    ap.add_argument("--max", type=int, default=25, help="1-50 videos (default 25)")
    ap.add_argument("--order", default="relevance", choices=["relevance", "date", "viewCount", "rating"])
    ap.add_argument("--published", default="any", choices=["any", "hour", "today", "week", "month", "year"])
    ap.add_argument("--duration", default="any", choices=["any", "short", "medium", "long"], help="short <4min, medium 4-20, long >20")
    ap.add_argument("--out", help="output folder (default channels/<channel>/research/<query-slug>)")
    ap.add_argument("--channel", default="scratch", help="channel name for the default output folder")
    ap.add_argument("--selftest", action="store_true", help="run on a built-in sample, no API key or network")
    a = ap.parse_args()
    if a.selftest:
        snap = selftest_snapshot()
    else:
        if not a.query:
            ap.error("query is required (or use --selftest)")
        key = load_key()
        if not key:
            sys.exit("YOUTUBE_API_KEY not set. Put it in the environment or in .env at the repo root (see SKILL.md, Setup).")
        snap = fetch(a.query.strip()[:200], max(1, min(50, a.max)), a.order, a.published, a.duration, key)
    ident = json.dumps([snap["query"], snap["filters"], snap["orderedVideoIds"], snap["retrievedAt"]])
    snap["snapshotId"] = hashlib.sha256(ident.encode()).hexdigest()[:16]
    an = analytics(snap)
    snap["analytics"] = an
    out = a.out or os.path.join(ROOT, "channels", a.channel, "research", slugify(snap["query"]))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=1)
    write_md(os.path.join(out, "snapshot.md"), snap, an)
    print(f"snapshot {snap['snapshotId']}: {an['sampleSize']} videos -> {out}")
    if snap["warnings"]:
        print("warnings:", "; ".join(snap["warnings"]))


if __name__ == "__main__":
    main()
