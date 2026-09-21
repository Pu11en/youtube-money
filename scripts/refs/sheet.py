"""Contact sheet of the 20 candidates: one numbered grid image, hosted on Blotato media (free) so
Discord shows it inline. Thumbnails are fetched into memory only; nothing is kept on disk except
the grid itself under runs/ (git-ignored).

  python scripts/refs/sheet.py --video attila-no-grave --scene 1
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "blotato"))
import client  # noqa: E402

CELL_W, CELL_H, COLS = 300, 420, 5
UA = "youtube-money/0.1 (contact sheet)"


def fetch(url: str) -> Image.Image | None:
    try:
        req = urllib.request.Request(url, headers={"user-agent": UA, "referer": "https://www.pinterest.com/"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGB")
    except Exception:  # noqa: BLE001
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--scene", type=int, required=True)
    a = ap.parse_args()
    data = json.loads((REPO / "videos" / a.video / "refs" / f"scene-{a.scene:02d}.candidates.json").read_text(encoding="utf-8"))
    cands = data["candidates"]
    rows = (len(cands) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL_W, rows * CELL_H), (18, 18, 18))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 44)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
    for i, c in enumerate(cands):
        x, y = (i % COLS) * CELL_W, (i // COLS) * CELL_H
        im = fetch(c["image"])
        if im is not None:
            im.thumbnail((CELL_W - 12, CELL_H - 12))
            sheet.paste(im, (x + (CELL_W - im.width) // 2, y + (CELL_H - im.height) // 2))
        else:
            draw.text((x + 20, y + CELL_H // 2), "no preview", fill=(160, 160, 160), font=font)
        n = str(i + 1)
        draw.rectangle([x + 6, y + 6, x + 6 + 34 + 24 * len(n), y + 62], fill=(255, 210, 0))
        draw.text((x + 16, y + 8), n, fill=(0, 0, 0), font=font)
    out = REPO / "runs" / "refs" / f"{a.video}-scene-{a.scene:02d}-sheet.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=85)
    url = client.upload_file(client.load_api_key(), out)
    print(url)


if __name__ == "__main__":
    main()
