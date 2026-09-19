"""Credit meter: every paid call goes through `allow()` first and `record()` after.

Ledger: <repo>/runs/credits.log (git-ignored), one JSON line per call.
A limit is per run ("this test block may spend 200"), set by Drew in Discord.
Model prices are Blotato's public table (2026-09-08 snapshot); the live balance
from /credits is the final word, and the app's billing screen beats both.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "runs" / "credits.log"

IMAGE_MODELS = {
    "flux-schnell": 1,
    "luma/photon": 10,
    "flux-dev": 10,
    "flux-1.1-pro": 15,
    "recraft-v3": 15,
    "fal-ai/nano-banana": 15,
    "fal-ai/nano-banana/edit": 15,
    "fal-ai/bytedance/seedream/v4.5/text-to-image": 15,
    "fal-ai/bytedance/seedream/v4.5/edit": 15,
    "flux-1.1-pro-ultra": 20,
    "openai/gpt-image-1": 25,
    "ideogram-v2": 30,
    "nano-banana-2": 30,
    "nano-banana-2/edit": 30,
    "nano-banana-pro": 50,
    "nano-banana-pro/edit": 50,
}

CHEAP_TEST_MODEL = "flux-schnell"
QUALITY_MODEL = "nano-banana-2"
EDIT_MODEL = "fal-ai/nano-banana/edit"


def price(model: str, count: int = 1) -> int:
    if model not in IMAGE_MODELS:
        raise SystemExit(f"unknown image model {model!r}; known: {', '.join(IMAGE_MODELS)}")
    return IMAGE_MODELS[model] * count


def spent(run: str) -> int:
    if not LEDGER.exists():
        return 0
    total = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("run") == run and row.get("status") == "charged":
            total += int(row.get("credits", 0))
    return total


def allow(run: str, limit: int, cost: int, balance: int | None = None) -> None:
    """Raise if this call would pass the run limit or the live balance."""
    used = spent(run)
    if used + cost > limit:
        raise SystemExit(f"STOP: run {run!r} has spent {used} of {limit}; this call costs {cost}. Raise the limit or skip.")
    if balance is not None and cost > balance:
        raise SystemExit(f"STOP: Blotato balance is {balance}, this call costs {cost}.")


def record(run: str, *, what: str, model: str, credits: int, status: str, creation_id: str = "", note: str = "") -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "run": run, "what": what, "model": model,
           "credits": credits, "status": status, "creation_id": creation_id, "note": note}
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
