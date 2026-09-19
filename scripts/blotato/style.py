"""Style an existing picture: one reference image in, one new picture out.

This is the only *image-in, image-out* route Blotato's API has. It runs the
`Product Scene Placement` template (`productImage` + `sceneDescription`), which is
the single template out of all 37 that takes a real image input and generates a
new picture from it.

Known limitation, found live on 2026-09-08 by the `image-taste` project and
re-stated here so nobody forgets: **this template regenerates the reference, it
does not preserve its exact pixels.** Colour and edges shift. Treat every output
as a reinterpretation, not a faithful copy, and judge likeness by eye.

Cost is not published per template, so this script does not guess: it reads the
credit balance before and after and reports the measured delta. Drew sets a
ceiling; nothing is submitted without one.

    python3 scripts/blotato/style.py --ref <url-or-file> --scene "..." \
        --run logo-style --limit 60            # dry run, spends nothing
    python3 scripts/blotato/style.py ... --go  # spends, up to the ceiling
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import client
import meter

TEMPLATE = "f524614b-ba01-448c-967a-ce518c52a700"  # Product Scene Placement
TEMPLATE_NAME = "Product Scene Placement"
SCENE_MIN, SCENE_MAX = 10, 500
REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve_ref(key: str, ref: str, go: bool) -> str:
    """A ref is either already a URL, or a local file that needs uploading (free)."""
    if ref.startswith(("http://", "https://")):
        return ref
    path = Path(ref)
    if not path.exists():
        raise SystemExit(f"no such reference file: {ref}")
    if not go:
        return f"<would upload {path.name}>"
    return client.upload_file(key, path)


def run_one(*, key: str, run: str, limit: int, ref: str, scene: str, out: Path, go: bool, what: str) -> None:
    if not SCENE_MIN <= len(scene) <= SCENE_MAX:
        raise SystemExit(f"scene must be {SCENE_MIN}-{SCENE_MAX} characters; yours is {len(scene)}")

    ref_url = _resolve_ref(key, ref, go)
    print(f"template: {TEMPLATE_NAME}")
    print(f"reference: {ref_url}")
    print(f"scene ({len(scene)} chars): {scene}")
    print(f"run: {run} | ceiling: {limit} credits | already spent on this run: {meter.spent(run)}")

    if not go:
        print("\nDRY RUN — nothing submitted, nothing spent.")
        print("Cost per call is not published for this template; the real number is measured "
              "from the balance on the first live run.")
        print("Add --go to submit.")
        return

    before = client.credits(key)["creditsRemaining"]
    if before < limit:
        raise SystemExit(f"refusing to submit: balance {before} is below the {limit}-credit ceiling")
    if meter.spent(run) >= limit:
        raise SystemExit(f"refusing to submit: run {run!r} already spent its {limit}-credit ceiling")

    body_inputs = {"productImage": ref_url, "sceneDescription": scene}
    created = client.create_from_template(key, template_id=TEMPLATE, inputs=body_inputs,
                                          render=True, title=f"{run}: {what}")
    item = created.get("item", created)
    cid = item.get("id")
    print("creation:", cid)
    meter.record(run, what=what, model=TEMPLATE_NAME, credits=0, status="submitted", creation_id=cid)

    item = client.wait_for(key, cid)
    status = item.get("status")
    urls = item.get("imageUrls") or ([item["mediaUrl"]] if item.get("mediaUrl") else [])
    after = client.credits(key)["creditsRemaining"]
    delta = before - after
    print(f"credits: {before} -> {after}  (measured cost: {delta})")

    if status in client.TERMINAL_OK and urls:
        out.parent.mkdir(parents=True, exist_ok=True)
        dest = client.download(urls[0], out)
        meter.record(run, what=what, model=TEMPLATE_NAME, credits=delta, status="charged",
                     creation_id=cid, note=str(dest))
        print("saved:", dest)
    else:
        meter.record(run, what=what, model=TEMPLATE_NAME, credits=delta,
                     status=f"failed:{status}", creation_id=cid,
                     note=json.dumps(item.get("error"))[:200])
        print("FAILED:", status, json.dumps(item)[:500])


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ref", required=True, help="the picture to style: a URL or a local file")
    p.add_argument("--scene", required=True, help=f"{SCENE_MIN}-{SCENE_MAX} characters describing the new picture")
    p.add_argument("--out", default=None, help="where to save (default runs/tests/style/<run>-<what>.png)")
    p.add_argument("--what", default="style", help="short name for this shot, used in the ledger and filename")
    p.add_argument("--run", required=True, help="name of this block, e.g. logo-style")
    p.add_argument("--limit", type=int, required=True, help="max credits this run may spend")
    p.add_argument("--go", action="store_true", help="actually spend (default: dry run)")
    args = p.parse_args(argv)

    key = client.load_api_key() if args.go else ""
    out = Path(args.out) if args.out else REPO_ROOT / "runs" / "tests" / "style" / f"{args.run}-{args.what}.png"
    run_one(key=key, run=args.run, limit=args.limit, ref=args.ref, scene=args.scene,
            out=out, go=args.go, what=args.what)


if __name__ == "__main__":
    main()
