"""Blotato image block: words -> picture (I1), picture + words -> picture (I2), upload (I3).

Dry-run is the default: every command prints what it would send and what it would
cost. Add --go to spend credits. Every paid call needs --run <name> and --limit <n>.

  python scripts/blotato/image.py doctor
  python scripts/blotato/image.py upload path/to/ref.png
  python scripts/blotato/image.py new  --prompt "..." --model flux-schnell --ratio 9:16 --out runs/x.png --run t1 --limit 50 [--go]
  python scripts/blotato/image.py from --ref URL|path --prompt "..." --model fal-ai/nano-banana/edit --out ... --run t1 --limit 50 [--go]
  python scripts/blotato/image.py test I1-01 --limit 50 [--go]
  python scripts/blotato/image.py status <creation-id>

Template used: "Image Slideshow with Text Overlays" (one slide, no text) -> item.imageUrls[0].
Field names come from the public docs; `doctor` saves the live inputs to runs/templates.json
so a session can correct them if Blotato changed something.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import client  # noqa: E402
import meter  # noqa: E402

REPO_ROOT = client.REPO_ROOT
SLIDESHOW_TEMPLATE = "5903b592-1255-43b4-b9ac-f8ed7cbf6a5f"
RATIOS = ("9:16", "16:9", "1:1", "4:5")
CASES = REPO_ROOT / "tests" / "generation" / "images" / "cases.json"


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2)[:4000])


def cmd_doctor(args) -> None:
    key = client.load_api_key()
    who = client.me(key)
    print("key ok:", json.dumps(who)[:200])
    bal = client.credits(key)
    print("credits:", json.dumps(bal)[:300])
    tpl = client.templates(key)
    out = REPO_ROOT / "runs" / "templates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tpl, indent=2), encoding="utf-8")
    items = tpl.get("items") or tpl.get("templates") or (tpl if isinstance(tpl, list) else [])
    print(f"templates: {len(items)} saved to {out}")
    print("\nTemplates that take an image or an image model:")
    for t in items:
        text = json.dumps(t.get("inputs", {})).lower()
        if "image" in text or "model" in text:
            print(f"- {t.get('id')}  {t.get('name')}")
    hit = [t for t in items if t.get("id") == SLIDESHOW_TEMPLATE]
    print("\nSlideshow template live inputs:" if hit else "\nWARNING: slideshow template id not in the live list; pick another from runs/templates.json")
    if hit:
        _print_json(hit[0].get("inputs"))
    edit = "edit" in json.dumps(items).lower()
    print("\nEdit models mentioned in any template inputs:", "yes" if edit else "no (reference-image editing may be web-only)")


def cmd_upload(args) -> None:
    key = client.load_api_key()
    url = client.upload_file(key, args.path)
    print(url)


def _resolve_ref(key: str, ref: str, go: bool) -> str:
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref
    p = Path(ref)
    if not p.exists():
        raise SystemExit(f"reference not found: {ref}")
    if not go:
        return f"<would upload {p}>"
    return client.upload_file(key, p)


def _generate(*, key: str, run: str, limit: int, model: str, ratio: str, prompt: str, refs: list[str],
              out: Path, go: bool, what: str) -> None:
    cost = meter.price(model)
    slide = {"imageSource": refs[0] if refs else prompt, "textOverlay": ""}
    inputs = {"slides": [slide], "aiImageModel": model, "aspectRatio": ratio}
    body = {"templateId": SLIDESHOW_TEMPLATE, "inputs": inputs, "render": True, "title": f"{run}: {what}"}
    if refs:
        body["prompt"] = prompt
        if len(refs) > 1:
            body["prompt"] += " Additional reference images: " + ", ".join(refs[1:])
    print(f"[{'GO' if go else 'DRY RUN'}] {what}  model={model}  cost={cost}  run={run}  limit={limit}")
    _print_json(body)
    if not go:
        print("Add --go to spend credits.")
        return
    bal = client.credits(key)
    balance = bal.get("credits") or bal.get("balance") or bal.get("item", {}).get("credits")
    meter.allow(run, limit, cost, int(balance) if isinstance(balance, (int, float)) else None)
    created = client.create_from_template(key, template_id=SLIDESHOW_TEMPLATE, inputs=inputs,
                                          prompt=body.get("prompt"), title=body["title"])
    item = created.get("item", created)
    cid = item.get("id")
    print("creation:", cid)
    meter.record(run, what=what, model=model, credits=cost, status="submitted", creation_id=cid)
    item = client.wait_for(key, cid)
    status = item.get("status")
    urls = item.get("imageUrls") or ([item["mediaUrl"]] if item.get("mediaUrl") else [])
    if status in client.TERMINAL_OK and urls:
        dest = client.download(urls[0], out)
        meter.record(run, what=what, model=model, credits=cost, status="charged", creation_id=cid, note=str(dest))
        print("saved:", dest)
    else:
        meter.record(run, what=what, model=model, credits=0, status=f"failed:{status}", creation_id=cid,
                     note=json.dumps(item.get("error"))[:200])
        print("FAILED:", status, json.dumps(item)[:500])


def cmd_new(args) -> None:
    key = client.load_api_key() if args.go else ""
    _generate(key=key, run=args.run, limit=args.limit, model=args.model, ratio=args.ratio, prompt=args.prompt,
              refs=[], out=Path(args.out), go=args.go, what="new")


def cmd_from(args) -> None:
    key = client.load_api_key() if args.go else ""
    refs = [_resolve_ref(key, r, args.go) for r in args.ref]
    _generate(key=key, run=args.run, limit=args.limit, model=args.model, ratio=args.ratio, prompt=args.prompt,
              refs=refs, out=Path(args.out), go=args.go, what="from")


def cmd_status(args) -> None:
    key = client.load_api_key()
    _print_json(client.creation(key, args.id))


def cmd_test(args) -> None:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    case = next((c for c in cases if c["id"] == args.case), None)
    if not case:
        raise SystemExit(f"no case {args.case}; known: {', '.join(c['id'] for c in cases)}")
    key = client.load_api_key() if args.go else ""
    out = REPO_ROOT / "runs" / "tests" / "images" / f"{case['id']}.png"
    refs = [_resolve_ref(key, r, args.go) for r in case.get("refs", [])]
    print(f"== {case['id']}: {case['name']}\n   pass looks like: {case['pass']}")
    _generate(key=key, run=args.run or case["id"], limit=args.limit, model=case.get("model", meter.CHEAP_TEST_MODEL),
              ratio=case.get("ratio", "9:16"), prompt=case["prompt"], refs=refs, out=out, go=args.go, what=case["id"])
    if args.go:
        print(f"Now write the verdict in tests/generation/images/verdicts.md under {case['id']}.")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    u = sub.add_parser("upload"); u.add_argument("path"); u.set_defaults(fn=cmd_upload)
    s = sub.add_parser("status"); s.add_argument("id"); s.set_defaults(fn=cmd_status)

    def paid(sp):
        sp.add_argument("--run", required=True, help="name of this test block / video")
        sp.add_argument("--limit", type=int, required=True, help="max credits this run may spend")
        sp.add_argument("--go", action="store_true", help="actually spend credits (default: dry run)")

    n = sub.add_parser("new"); n.add_argument("--prompt", required=True); n.add_argument("--model", default=meter.CHEAP_TEST_MODEL)
    n.add_argument("--ratio", default="9:16", choices=RATIOS); n.add_argument("--out", required=True); paid(n); n.set_defaults(fn=cmd_new)

    f = sub.add_parser("from"); f.add_argument("--ref", action="append", required=True, help="URL or local file; repeat for 2-3 refs")
    f.add_argument("--prompt", required=True); f.add_argument("--model", default=meter.EDIT_MODEL)
    f.add_argument("--ratio", default="9:16", choices=RATIOS); f.add_argument("--out", required=True); paid(f); f.set_defaults(fn=cmd_from)

    t = sub.add_parser("test"); t.add_argument("case"); t.add_argument("--run", default=None)
    t.add_argument("--limit", type=int, required=True); t.add_argument("--go", action="store_true"); t.set_defaults(fn=cmd_test)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
