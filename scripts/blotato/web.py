"""Thin wrapper around OpenCLI for driving Blotato's website. Session name: blo.

  python scripts/blotato/web.py open https://my.blotato.com/videos
  python scripts/blotato/web.py state                # numbered refs for every control
  python scripts/blotato/web.py click <ref|css>
  python scripts/blotato/web.py type <ref> "text"
  python scripts/blotato/web.py fill <ref> "text"
  python scripts/blotato/web.py upload <ref> path
  python scripts/blotato/web.py shot name            # -> runs/web/<name>.png
  python scripts/blotato/web.py wait text "Done" [ms]
  python scripts/blotato/web.py eval "<js>"
  python scripts/blotato/web.py raw <any opencli browser args...>

Reads config/machine.json for the opencli binary and profile. Every call is logged to
runs/web/log.txt so a click path can be reconstructed into an adapter later.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CFG = json.loads((REPO / "config" / "machine.json").read_text(encoding="utf-8"))
OC = CFG["opencli_bin"]
SESSION = "blo"
LOG = REPO / "runs" / "web" / "log.txt"


def run(args: list[str], timeout: int = 120) -> str:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    cmd = [OC, "browser", SESSION, *args]
    env = dict(os.environ)
    node_dir = str(Path(CFG.get("node_dir", "C:/Users/david/tools/node")))
    env["PATH"] = node_dir + os.pathsep + env.get("PATH", "")
    if CFG.get("opencli_profile"):
        env["OPENCLI_PROFILE"] = CFG["opencli_profile"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, shell=OC.endswith(".cmd"))
    out = (p.stdout or "") + (p.stderr or "")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')} [{p.returncode}] {' '.join(args)[:200]}\n")
    if p.returncode not in (0, 66):
        out = f"[exit {p.returncode}] " + out
    return out.strip()


def main(argv: list[str]) -> None:
    if not argv:
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "shot":
        name = rest[0] if rest else time.strftime("%H%M%S")
        dest = REPO / "runs" / "web" / f"{name}.png"
        print(run(["screenshot", str(dest)]))
        print(dest)
    elif cmd == "wait":
        kind, value = rest[0], rest[1]
        ms = rest[2] if len(rest) > 2 else "60000"
        print(run(["wait", kind, value, "--timeout", ms], timeout=int(ms) // 1000 + 30))
    elif cmd == "raw":
        print(run(rest, timeout=300))
    else:
        print(run([cmd, *rest]))


if __name__ == "__main__":
    main(sys.argv[1:])
