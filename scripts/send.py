"""Put a file in front of David.

He is on Discord and nowhere else, and three delivery paths were tried on 2026-09-26:

1. **A public link - the one that works.** Upload to Blotato's public bucket (free,
   0 credits) and print the URL. He clicks it in the thread and Discord plays the mp4
   inline. Immediate, works mid-session, no size limit worth worrying about.
2. The harness attachment list - works, but only delivers when the session ends.
   Queued as a backup so nothing is lost if he never clicks.
3. The Discord webhook - **does not reach him.** It belongs to a different channel
   than his thread, and Discord answers `Unknown Channel` to `?thread_id=`. Everything
   sent that way went somewhere he cannot see. Do not use it for him.

    python scripts/send.py "what this is" clip.mp4 photo.jpg

Prints the links to paste into the reply. Text alone just prints - say it yourself.
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


def queue(path):
    """The real delivery path. The webhook belongs to a different channel than
    David's thread - Discord answers 'Unknown Channel' to thread_id - so files reach
    him through the harness attachment list, which the bot posts when the session
    ends. Verified 2026-09-26 after everything sent by webhook went to a channel he
    could not see."""
    thread = env("DISCORD_THREAD_ID")
    if not thread:
        print("no DISCORD_THREAD_ID; cannot queue", path)
        return False
    listing = os.path.join(ROOT, ".ccdb-attachments-" + thread)
    full = os.path.abspath(path)
    if not os.path.exists(full):
        print("MISSING, not queued:", path)
        return False
    already = []
    if os.path.exists(listing):
        already = [l.strip() for l in open(listing, encoding="utf-8")]
    if full in already:
        print("already queued:", os.path.basename(full))
        return True
    with open(listing, "a", encoding="utf-8") as f:
        f.write(full + "\n")
    print("queued for delivery at session end:", os.path.basename(full))
    return True


def publish(path):
    """Host it publicly and return a URL he can click. Uploads are free."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "bclient", os.path.join(ROOT, "scripts", "blotato", "client.py"))
    client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client)
    return client.upload_file(client.load_api_key(), path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    message, files = sys.argv[1], sys.argv[2:]
    if message.strip():
        print(message)
        print()
    for f in files:
        if not os.path.exists(f):
            print("MISSING:", f)
            continue
        queue(f)                      # backup path, arrives at session end
        print("  LINK:", publish(f))  # primary path, works right now
