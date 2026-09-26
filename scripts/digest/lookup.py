"""Look up a digest item by its code, so step two never has to re-find anything.

    python scripts/digest/lookup.py D0926-3      # one item
    python scripts/digest/lookup.py D0926        # the whole digest
    python scripts/digest/lookup.py              # every code on record
    python scripts/digest/lookup.py D0926-3 --json

Codes are handed out by daily.py when a digest posts and live in
data/digest/index.json.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", ".."))
INDEX_PATH = os.path.join(ROOT, "data", "digest", "index.json")


def load():
    if not os.path.exists(INDEX_PATH):
        raise SystemExit("No digest has posted yet, so there are no codes. "
                         "Run: python scripts/digest/daily.py --post")
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


def show(code, r):
    print("%s  %s" % (code, r["title"]))
    print("   channel  %s (%s subs, %d days old)"
          % (r["channel"], format(r["subs"], ","), r["channel_age_days"]))
    print("   numbers  %s views in %dh, %sx its subscriber count"
          % (format(r["views"], ","), int(r["age_h"]), r["ratio"]))
    print("   posted   %s, found in %s" % (r["published"], r.get("source", "?")))
    print("   url      %s" % r["url"])
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    index = load()
    want = args[0].upper().strip() if args else ""

    hits = {c: r for c, r in index.items()
            if not want or c == want or c.startswith(want + "-")}
    if not hits:
        raise SystemExit("No item called %r. On record: %s"
                         % (want, ", ".join(sorted(index)[-10:])))

    if as_json:
        print(json.dumps(hits if len(hits) > 1 else list(hits.values())[0], indent=1))
    else:
        for code in sorted(hits, key=lambda c: (c.split("-")[0],
                                                int(c.split("-")[1]))):
            show(code, hits[code])
