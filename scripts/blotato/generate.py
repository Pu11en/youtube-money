"""The one front door for making anything on Blotato.

Every skill calls this. Nothing else should hardcode a template id: the catalog
lives in `techniques.json`, so adding a way to generate is a data edit, not a
code change.

Three promises, in order of how much they matter:

1. **Nothing spends by accident.** Dry run is the default. A ceiling is required.
   The live balance is checked before submitting, and what the run already spent
   is checked against the ceiling.
2. **Costs are measured, never guessed.** Blotato does not publish per-template
   prices, so every live run reads the balance before and after and writes the
   real delta into the ledger. Measured numbers get folded back into the catalog.
3. **Anything can be overridden on the fly.** `--set key=value` writes straight
   into the template inputs, so a one-off tweak never needs a code change.

    python3 scripts/blotato/generate.py list
    python3 scripts/blotato/generate.py show video.story
    python3 scripts/blotato/generate.py run image.from-image \
        --ref logo.png --scene "..." --run demo --limit 60          # dry run
    python3 scripts/blotato/generate.py run video.story \
        --scene-media logo.png --scene-script "One line." \
        --animate --voice Brian --ratio 9:16 --run demo --limit 400 --go

Portability: the Blotato key comes from `.env` or the environment, and the
OpenCLI binary and Chrome profile come from `config/machine.json` (git-ignored,
one per computer). Nothing machine-specific is committed, so another agent on
another computer pulls the repo, drops in its own `.env` and `machine.json`, and
continues from here.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

import client
import meter

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).resolve().parent / "techniques.json"
RUNS = REPO_ROOT / "runs"


# --------------------------------------------------------------------------- catalog

def load_catalog() -> list[dict]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))["techniques"]


def find(tid: str) -> dict:
    for t in load_catalog():
        if t["id"] == tid:
            return t
    known = ", ".join(t["id"] for t in load_catalog())
    raise SystemExit(f"no technique {tid!r}. Known: {known}")


def save_measured_cost(tid: str, credits: int) -> None:
    """Fold a measured price back into the catalog so the next session inherits it."""
    doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    for t in doc["techniques"]:
        if t["id"] == tid and t.get("cost_credits") is None and credits > 0:
            t["cost_credits"] = credits
            t["cost_source"] = f"measured {time.strftime('%Y-%m-%d')} from the live balance"
            CATALOG.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            print(f"catalog updated: {tid} costs {credits} credits")
            return


# --------------------------------------------------------------------------- inputs

def _media(key: str, ref: str, go: bool) -> str:
    """A ref is a URL already, or a local file that gets uploaded (free)."""
    if ref.startswith(("http://", "https://")):
        return ref
    path = Path(ref)
    if not path.exists():
        raise SystemExit(f"no such file for {key}: {ref}")
    if not go:
        return f"<would upload {path.name}>"
    return client.upload_file(key_api, path)


key_api = ""  # set in main(); _media needs it without threading it through every builder


def build_inputs(tech: dict, args, go: bool) -> dict:
    kind = tech.get("inputs_builder")

    if kind == "product_scene":
        if not (args.ref and args.scene):
            raise SystemExit("image.from-image needs --ref and --scene")
        if not 10 <= len(args.scene) <= 500:
            raise SystemExit(f"--scene must be 10-500 characters; yours is {len(args.scene)}")
        return {"productImage": _media("ref", args.ref, go), "sceneDescription": args.scene}

    if kind == "slideshow_one":
        if not args.prompt:
            raise SystemExit("image.from-text needs --prompt")
        return {
            "slides": [{"imageSource": args.prompt, "textOverlay": ""}],
            "aiImageModel": args.model or tech.get("default_model"),
            "aspectRatio": args.ratio or "9:16",
        }

    if kind == "story_video":
        media = args.scene_media or []
        scripts = args.scene_script or []
        prompts = args.scene_prompt or []
        if not (media or prompts):
            raise SystemExit("video.story needs --scene-media and/or --scene-prompt (repeat per scene)")
        sources = [_media("scene-media", m, go) for m in media] + list(prompts)
        if scripts and len(scripts) != len(sources):
            raise SystemExit(f"{len(sources)} scenes but {len(scripts)} --scene-script values; they must match")
        scenes = [{"mediaSource": s, "script": scripts[i] if scripts else ""} for i, s in enumerate(sources)]
        inputs = {
            "scenes": scenes,
            "enableVoiceover": bool(args.voice),
            "animateAiImages": bool(args.animate),
            "aspectRatio": args.ratio or "9:16",
            "trimToVoiceover": bool(args.voice),
        }
        if args.voice:
            inputs["voiceName"] = args.voice
        if args.model:
            inputs["aiImageModel"] = args.model
        return inputs

    if kind == "character_video":
        prompts = args.scene_prompt or []
        scripts = args.scene_script or []
        if not prompts:
            raise SystemExit("video.character needs --scene-prompt (repeat per scene)")
        if scripts and len(scripts) != len(prompts):
            raise SystemExit(f"{len(prompts)} scenes but {len(scripts)} --scene-script values; they must match")
        inputs = {
            "scenes": [{"description": p, "narration": scripts[i] if scripts else ""}
                       for i, p in enumerate(prompts)],
            "style": args.style or "realistic",
            "aspectRatio": args.ratio or "9:16",
        }
        if args.ref:
            inputs["characterDescription"] = _media("ref", args.ref, go)
        return inputs

    if kind == "combine":
        if not args.clip:
            raise SystemExit("video.combine needs --clip (repeat per clip)")
        return {
            "videoClips": [_media("clip", c, go) for c in args.clip],
            "aspectRatio": args.ratio or "9:16",
            "trimSilence": True,
        }

    raise SystemExit(f"technique {tech['id']!r} has no API builder - it is a {tech['route']} route. "
                     f"See {tech.get('notes', '')[:120]}")


def apply_overrides(inputs: dict, sets: list[str]) -> dict:
    """--set a.b=value writes anywhere in the inputs, so a one-off never needs code."""
    for item in sets or []:
        if "=" not in item:
            raise SystemExit(f"--set wants key=value, got {item!r}")
        path, raw = item.split("=", 1)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        node = inputs
        parts = path.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {}) if not p.isdigit() else node[int(p)]
        last = parts[-1]
        if last.isdigit():
            node[int(last)] = value
        else:
            node[last] = value
        print(f"override: {path} = {value!r}")
    return inputs


# --------------------------------------------------------------------------- output

def save_output(url: str, dest_stem: Path) -> Path:
    """Download, then name the file after what actually arrived, not what we hoped for."""
    tmp = dest_stem.with_suffix(".download")
    dest_stem.parent.mkdir(parents=True, exist_ok=True)
    client.download(url, tmp)
    head = tmp.read_bytes()[:12]
    if head[:3] == b"\xff\xd8\xff":
        ext = ".jpg"
    elif head[:8] == b"\x89PNG\r\n\x1a\n":
        ext = ".png"
    elif head[4:8] == b"ftyp":
        ext = ".mp4"
    elif head[:4] == b"RIFF":
        ext = ".webp"
    else:
        ext = Path(url.split("?")[0]).suffix or ".bin"
    final = dest_stem.with_suffix(ext)
    tmp.replace(final)
    return final


def probe(path: Path) -> str:
    if not shutil.which("ffprobe"):
        return ""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height,duration",
         "-of", "default=nw=1", str(path)],
        capture_output=True, text=True).stdout.strip().replace("\n", " ")
    return out


# --------------------------------------------------------------------------- run

def cmd_list(args) -> None:
    for t in load_catalog():
        cost = t["cost_credits"]
        cost_s = "free" if cost == 0 else (f"{cost} cr" if cost else "cost unknown")
        print(f"{t['id']:<24} {t['route']:<4} {t['reliability']:<9} {cost_s:<13} {t['name']}")


def cmd_show(args) -> None:
    print(json.dumps(find(args.technique), indent=2))


def cmd_run(args) -> None:
    global key_api
    tech = find(args.technique)
    go = args.go

    if tech["route"] == "web":
        raise SystemExit(
            f"{tech['id']} is a website technique, not an API one. Drive it with OpenCLI:\n"
            f"  {tech.get('notes', '')}")

    key_api = client.load_api_key() if go else ""
    inputs = apply_overrides(build_inputs(tech, args, go), args.set)

    print(f"technique: {tech['id']}  ({tech['name']})")
    print(f"reliability: {tech['reliability']} - {tech.get('notes', '')[:160]}")
    known = tech["cost_credits"]
    if known is None:
        print(f"expected cost: UNKNOWN - never measured. It will be measured from the balance, but "
              f"the ceiling CANNOT cap it (video.character turned out to be 800). Needs --unknown-cost-ok.")
    else:
        print(f"expected cost: {known} credits")
    print(f"run: {args.run} | ceiling: {args.limit} | already spent on this run: {meter.spent(args.run)}")
    print("inputs:", json.dumps(inputs, indent=2)[:1200])

    if not go:
        print("\nDRY RUN - nothing submitted, nothing spent. Add --go to submit.")
        return

    before = client.credits(key_api)["creditsRemaining"]
    if before < args.limit:
        raise SystemExit(f"refusing: balance {before} is below the {args.limit}-credit ceiling")
    already = meter.spent(args.run)
    if already >= args.limit:
        raise SystemExit(f"refusing: run {args.run!r} already spent {already} of its {args.limit}-credit ceiling")
    if known is not None and already + known > args.limit:
        raise SystemExit(f"refusing: {already} already spent + {known} for this call passes the {args.limit} ceiling")
    if known is None and not args.unknown_cost_ok:
        # Learned the hard way on 2026-09-19: video.character cost 800 credits on a run whose
        # ceiling was 900 and which had already spent 210. A ceiling cannot stop a call whose
        # price nobody knows, so an unpriced technique now needs saying so out loud.
        raise SystemExit(
            f"refusing: {tech['id']} has never been priced, so the {args.limit}-credit ceiling "
            f"cannot protect this call - it could cost more than the whole ceiling by itself.\n"
            f"Headroom left on this run: {args.limit - already}.\n"
            f"If Drew has agreed to find the price, re-run with --unknown-cost-ok.")

    created = client.create_from_template(key_api, template_id=tech["template_id"], inputs=inputs,
                                          render=True, title=f"{args.run}: {args.what}")
    item = created.get("item", created)
    cid = item.get("id")
    print("creation:", cid)
    meter.record(args.run, what=args.what, model=tech["id"], credits=0, status="submitted", creation_id=cid)

    item = client.wait_for(key_api, cid, timeout_s=args.timeout)
    status = item.get("status")
    after = client.credits(key_api)["creditsRemaining"]
    delta = before - after
    print(f"credits: {before} -> {after}  (measured cost: {delta})")

    urls = item.get("imageUrls") or ([item["mediaUrl"]] if item.get("mediaUrl") else [])
    if status in client.TERMINAL_OK and urls:
        dest = save_output(urls[0], RUNS / "out" / f"{args.run}-{args.what}")
        info = probe(dest)
        meter.record(args.run, what=args.what, model=tech["id"], credits=delta, status="charged",
                     creation_id=cid, note=str(dest))
        save_measured_cost(tech["id"], delta)
        print("saved:", dest, f"({info})" if info else "")
    else:
        meter.record(args.run, what=args.what, model=tech["id"], credits=delta,
                     status=f"failed:{status}", creation_id=cid,
                     note=json.dumps(item.get("error"))[:300])
        print("FAILED:", status, json.dumps(item)[:600])


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="every technique, its route, reliability and measured cost").set_defaults(fn=cmd_list)
    sh = sub.add_parser("show", help="the full catalog entry"); sh.add_argument("technique"); sh.set_defaults(fn=cmd_show)

    r = sub.add_parser("run", help="make something (dry run unless --go)")
    r.add_argument("technique")
    r.add_argument("--run", required=True, help="name of this block, shared by every call in it")
    r.add_argument("--limit", type=int, required=True, help="max credits this whole run may spend")
    r.add_argument("--what", default="out", help="short name for this call, used in the filename and ledger")
    r.add_argument("--go", action="store_true", help="actually spend")
    r.add_argument("--unknown-cost-ok", action="store_true",
                   help="allow a technique whose price has never been measured; a ceiling cannot "
                        "protect a call whose cost nobody knows yet")
    r.add_argument("--timeout", type=int, default=1800, help="seconds to wait for a render")
    r.add_argument("--ref", help="a reference picture: URL or local file")
    r.add_argument("--scene", help="scene description for image.from-image (10-500 chars)")
    r.add_argument("--prompt", help="text prompt for image.from-text")
    r.add_argument("--model", help="override the image model")
    r.add_argument("--ratio", help="16:9 | 1:1 | 4:5 | 9:16")
    r.add_argument("--style", help="video.character visual style")
    r.add_argument("--voice", help="voice name; also switches voiceover on")
    r.add_argument("--animate", action="store_true", help="turn stills into motion (video.story)")
    r.add_argument("--scene-media", action="append", help="a scene's own picture/video; repeat per scene")
    r.add_argument("--scene-prompt", action="append", help="a scene described in words; repeat per scene")
    r.add_argument("--scene-script", action="append", help="a scene's narration; repeat per scene")
    r.add_argument("--clip", action="append", help="a clip for video.combine; repeat")
    r.add_argument("--set", action="append", help="override any template input: --set key=value or --set a.b=value")
    r.set_defaults(fn=cmd_run)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
