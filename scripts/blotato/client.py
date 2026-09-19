"""Blotato HTTP client, standard library only.

Base URL and endpoints follow https://help.blotato.com/api/llm (checked 2026-09-19).
The API key is read from the BLOTATO_API_KEY environment variable or a `.env`
file at the repo root; it is never written to disk by this code.
"""
from __future__ import annotations

import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

BASE_URL = "https://backend.blotato.com/v2"
API_KEY_HEADER = "blotato-api-key"
USER_AGENT = "youtube-money/0.1"
REPO_ROOT = Path(__file__).resolve().parents[2]

TERMINAL_OK = {"done"}
TERMINAL_FAIL = {"creation-from-template-failed", "insufficient-credits", "failed"}


class BlotatoError(RuntimeError):
    def __init__(self, status: int, body: Any):
        super().__init__(f"blotato http {status}: {json.dumps(body)[:500]}")
        self.status = status
        self.body = body


def load_api_key() -> str:
    key = os.environ.get("BLOTATO_API_KEY", "").strip()
    if not key:
        env = REPO_ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("BLOTATO_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("No BLOTATO_API_KEY. Put it in the environment or in <repo>/.env (see .env.example).")
    return key


def _request(method: str, path: str, *, api_key: str, body: Optional[dict] = None, timeout: float = 60) -> dict:
    data = None
    headers = {API_KEY_HEADER: api_key, "user-agent": USER_AGENT, "accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["content-type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw.decode("utf-8", errors="replace")
        raise BlotatoError(e.code, payload) from None
    return json.loads(raw) if raw else {}


def me(api_key: str) -> dict:
    return _request("GET", "/users/me", api_key=api_key)


def credits(api_key: str) -> dict:
    return _request("GET", "/credits", api_key=api_key)


def templates(api_key: str) -> dict:
    return _request("GET", "/videos/templates?fields=id,name,description,inputs", api_key=api_key)


def upload_url(api_key: str, public_url: str) -> dict:
    return _request("POST", "/media", api_key=api_key, body={"url": public_url})


def upload_file(api_key: str, path: str | Path) -> str:
    """Presigned upload of a local file. Returns the public URL Blotato hosts it at."""
    path = Path(path)
    presign = _request("POST", "/media/uploads", api_key=api_key, body={"filename": path.name})
    put_url = presign.get("presignedUrl") or presign.get("uploadUrl")
    public = presign.get("publicUrl") or presign.get("url")
    if not put_url or not public:
        raise RuntimeError(f"unexpected presign response: {json.dumps(presign)[:300]}")
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    req = urllib.request.Request(put_url, data=path.read_bytes(), method="PUT",
                                 headers={"content-type": content_type, "user-agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as resp:
        resp.read()
    return public


def create_from_template(api_key: str, *, template_id: str, inputs: dict, prompt: Optional[str] = None,
                         title: Optional[str] = None, render: bool = True) -> dict:
    body: dict = {"templateId": template_id, "inputs": inputs, "render": render}
    if prompt:
        body["prompt"] = prompt
    if title:
        body["title"] = title
    return _request("POST", "/videos/from-templates", api_key=api_key, body=body)


def creation(api_key: str, creation_id: str) -> dict:
    return _request("GET", f"/videos/creations/{creation_id}", api_key=api_key)


def wait_for(api_key: str, creation_id: str, *, timeout_s: int = 900, every_s: int = 10, log=print) -> dict:
    start = time.time()
    last = None
    while time.time() - start < timeout_s:
        item = creation(api_key, creation_id)
        item = item.get("item", item)
        status = item.get("status")
        if status != last:
            log(f"  status: {status}")
            last = status
        if status in TERMINAL_OK or status in TERMINAL_FAIL or item.get("error"):
            return item
        time.sleep(every_s)
    raise TimeoutError(f"creation {creation_id} still {last} after {timeout_s}s")


def download(url: str, dest: str | Path) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"user-agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as resp:
        dest.write_bytes(resp.read())
    return dest
