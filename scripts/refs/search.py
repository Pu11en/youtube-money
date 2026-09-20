"""Visual Search Picker: scene narration -> keyword sets -> 20 reference candidates -> Drew picks one.

  python scripts/refs/search.py find --video attila-no-grave --scene 1 \
      --q "hun warrior alone steppe sunset illustration" --q "..." --q "..."
  python scripts/refs/search.py pick --video attila-no-grave --scene 1 --n 7 [--why "..."]
  python scripts/refs/search.py show --video attila-no-grave --scene 1

Sources (all free, zero Blotato credits): Pinterest through OpenCLI (Chrome logged in), Wikimedia
Commons API, Openverse API. Links only are stored; nothing is downloaded.
`find` prints Discord-ready messages: 4 blocks of 5, each item = number, title, source, why, image link.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CFG = json.loads((REPO / "config" / "machine.json").read_text(encoding="utf-8"))
UA = "youtube-money/0.1 (reference search)"
STOP = set("a an the of in on at to for with and or his her their its into over under by from is are was were be this that these those it he she they we you".split())


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"user-agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def pinterest(q: str, limit: int = 10) -> list[dict]:
    env = dict(os.environ)
    env["PATH"] = str(CFG.get("node_dir", "C:/Users/david/tools/node")) + os.pathsep + env.get("PATH", "")
    if CFG.get("opencli_profile"):
        env["OPENCLI_PROFILE"] = CFG["opencli_profile"]
    cmd = [CFG["opencli_bin"], "pinterest", "search-pins", q, "-f", "json", "--limit", str(min(limit, 10))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env, shell=CFG["opencli_bin"].endswith(".cmd"))
        start = p.stdout.find("[")
        rows = json.loads(p.stdout[start:]) if start >= 0 else []
    except Exception as e:  # noqa: BLE001
        print(f"  pinterest failed for {q!r}: {e}")
        return []
    out = []
    for r in rows:
        if not r.get("imageUrl"):
            continue
        out.append({"source": "pinterest", "title": (r.get("title") or r.get("description") or "").strip()[:80] or "(untitled pin)",
                    "page": r.get("url"), "image": r["imageUrl"], "board": r.get("board", ""), "by": r.get("pinner", ""),
                    "licence": "third-party (Pinterest) - reference only, ask before using as a generation input", "query": q})
    return out


def wikimedia(q: str, limit: int = 10) -> list[dict]:
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 800, "format": "json"})
    try:
        pages = _get(u).get("query", {}).get("pages", {})
    except Exception as e:  # noqa: BLE001
        print(f"  wikimedia failed for {q!r}: {e}")
        return []
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("thumburl"):
            continue
        meta = ii.get("extmetadata", {})
        out.append({"source": "wikimedia", "title": p["title"].replace("File:", "")[:80], "page": ii.get("descriptionurl"),
                    "image": ii["thumburl"], "board": "", "by": meta.get("Artist", {}).get("value", "")[:40],
                    "licence": meta.get("LicenseShortName", {}).get("value", "see page"), "query": q})
    return out


def openverse(q: str, limit: int = 10) -> list[dict]:
    u = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "page_size": limit})
    try:
        rows = _get(u).get("results", [])
    except Exception as e:  # noqa: BLE001
        print(f"  openverse failed for {q!r}: {e}")
        return []
    return [{"source": "openverse", "title": (r.get("title") or "")[:80], "page": r.get("foreign_landing_url"),
             "image": r.get("thumbnail") or r.get("url"), "board": r.get("source", ""), "by": r.get("creator", ""),
             "licence": f"CC {r.get('license', '').upper()}", "query": q} for r in rows if r.get("url")]


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def rank(cands: list[dict], queries: list[str], narration: str) -> list[dict]:
    want = set()
    for q in queries + [narration]:
        want |= words(q)
    seen, out = set(), []
    for c in cands:
        key = c["image"].split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        text = words(" ".join([c["title"], c.get("board", ""), c.get("query", "")]))
        c["score"] = len(text & want) + (2 if c["source"] == "pinterest" else 0) + (1 if c["title"] != "(untitled pin)" else 0)
        c["why"] = "matches: " + ", ".join(sorted(text & want)[:4]) if text & want else "found under: " + c["query"]
        out.append(c)
    out.sort(key=lambda c: -c["score"])
    return out


def discord_blocks(cands: list[dict]) -> list[str]:
    blocks = []
    for i in range(0, len(cands), 5):
        lines = []
        for n, c in enumerate(cands[i:i + 5], start=i + 1):
            lines.append(f"**{n}. {c['title']}** — {c['source']} · {c['why']}\n{c['image']}")
        blocks.append("\n".join(lines))
    return blocks


def cmd_find(a) -> None:
    out_dir = REPO / "videos" / a.video / "refs"
    out_dir.mkdir(parents=True, exist_ok=True)
    cands = []
    for q in a.q:
        print(f"searching: {q}")
        cands += pinterest(q, 10)
        cands += wikimedia(q, 6)
        cands += openverse(q, 6)
        time.sleep(1)
    ranked = rank(cands, a.q, a.narration or "")[: a.limit]
    path = out_dir / f"scene-{a.scene:02d}.candidates.json"
    path.write_text(json.dumps({"video": a.video, "scene": a.scene, "narration": a.narration, "queries": a.q,
                                "candidates": ranked, "at": time.strftime("%Y-%m-%d %H:%M")}, indent=2), encoding="utf-8")
    print(f"{len(cands)} found, {len(ranked)} kept -> {path}\n")
    for b in discord_blocks(ranked):
        print(b)
        print("-----")


def cmd_pick(a) -> None:
    out_dir = REPO / "videos" / a.video / "refs"
    data = json.loads((out_dir / f"scene-{a.scene:02d}.candidates.json").read_text(encoding="utf-8"))
    c = data["candidates"][a.n - 1]
    c["picked_at"] = time.strftime("%Y-%m-%d %H:%M")
    if a.why:
        c["drew_note"] = a.why
    (out_dir / f"scene-{a.scene:02d}.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
    print(f"scene {a.scene} reference = #{a.n} {c['title']} ({c['source']})\n{c['image']}\nsaved -> {out_dir / f'scene-{a.scene:02d}.json'}")


def cmd_show(a) -> None:
    p = REPO / "videos" / a.video / "refs" / f"scene-{a.scene:02d}.json"
    print(p.read_text(encoding="utf-8") if p.exists() else "no pick yet")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find"); f.add_argument("--video", required=True); f.add_argument("--scene", type=int, required=True)
    f.add_argument("--q", action="append", required=True, help="keyword set; repeat 3 times"); f.add_argument("--narration", default="")
    f.add_argument("--limit", type=int, default=20); f.set_defaults(fn=cmd_find)
    p = sub.add_parser("pick"); p.add_argument("--video", required=True); p.add_argument("--scene", type=int, required=True)
    p.add_argument("--n", type=int, required=True); p.add_argument("--why", default=""); p.set_defaults(fn=cmd_pick)
    s = sub.add_parser("show"); s.add_argument("--video", required=True); s.add_argument("--scene", type=int, required=True); s.set_defaults(fn=cmd_show)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
