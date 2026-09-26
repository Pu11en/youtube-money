"""Send text and files to David's Discord thread.

David only ever sees Discord. A file written to this repo, saved to the Desktop, or
opened in a browser on this machine reaches him as nothing at all, so anything he is
meant to look at - a generated clip, a reference photo, a test result - has to go
through here.

    python scripts/send.py "message"
    python scripts/send.py "here is the clip" path/to/clip.mp4
    python scripts/send.py "" a.jpg b.jpg c.mp4

Uses DISCORD_WEBHOOK_URL from .env. Discord caps a webhook upload at 8 MB on a free
server and 2000 characters of text, so this splits text and sends files one per
request, reporting exactly what landed.
"""
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LIMIT_BYTES = 8 * 1024 * 1024
UA = "youtube-money-send/1.0"


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


HOOK = env("DISCORD_WEBHOOK_URL")


def _send(body, content_type):
    req = urllib.request.Request(
        HOOK, data=body,
        headers={"Content-Type": content_type, "User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.status


def send_text(text):
    """Split on blank lines to stay under Discord's 2000 character limit."""
    if not text.strip():
        return
    chunks, current = [], ""
    for block in text.split("\n\n"):
        if len(current) + len(block) + 2 > 1900:
            chunks.append(current.rstrip())
            current = ""
        current += block + "\n\n"
    if current.strip():
        chunks.append(current.rstrip())
    for chunk in chunks:
        status = _send(json.dumps({"content": chunk, "flags": 4}).encode(),
                       "application/json")
        print("text sent, HTTP", status)


def send_file(path, caption=""):
    """One multipart request per file. Discord rejects the whole request if any
    single part is oversized, so files never share a request."""
    if not os.path.exists(path):
        print("MISSING, not sent:", path)
        return False
    size = os.path.getsize(path)
    if size > LIMIT_BYTES:
        print("TOO BIG (%.1f MB), not sent: %s" % (size / 1048576.0, path))
        return False

    name = os.path.basename(path)
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    boundary = "----" + uuid.uuid4().hex
    bnd = ("--" + boundary).encode()

    parts = [bnd,
             b'Content-Disposition: form-data; name="payload_json"',
             b"Content-Type: application/json", b"",
             json.dumps({"content": caption, "flags": 4}).encode(),
             bnd,
             ('Content-Disposition: form-data; name="files[0]"; filename="%s"'
              % name).encode(),
             ("Content-Type: " + ctype).encode(), b"",
             open(path, "rb").read(),
             ("--" + boundary + "--").encode(), b""]
    body = b"\r\n".join(parts)

    try:
        status = _send(body, "multipart/form-data; boundary=" + boundary)
    except urllib.error.HTTPError as e:
        print("FAILED %s: HTTP %s %s" % (name, e.code,
                                         e.read().decode("utf-8", "replace")[:200]))
        return False
    print("sent %s (%.0f KB), HTTP %s" % (name, size / 1024.0, status))
    return True


if __name__ == "__main__":
    if not HOOK:
        raise SystemExit("No DISCORD_WEBHOOK_URL in .env")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    message, files = sys.argv[1], sys.argv[2:]
    if message.strip() and not files:
        send_text(message)
    elif files:
        send_text(message)
        for f in files:
            send_file(f)
