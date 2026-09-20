"""One website image generation, end to end, through OpenCLI.

  python scripts/blotato/web_image.py --editor <video-editor-id> --model nano-banana-2 \
      --ratio 9:16 --prompt "..." --out runs/x.png [--ref-index N ...] [--ref-file path ...] [--go]

- --ref-index N picks the Nth scene image (0-based) already in that video's picker.
- --ref-file uploads a local file into the picker (hosted first via the API upload, then injected).
- Any ref makes the call an Edit-model call; pass an edit model then (nano-banana-2/edit ...).
Prints the new image URL and saves the file. Dry run unless --go.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import client  # noqa: E402
from web import run as oc  # noqa: E402

REPO = client.REPO_ROOT

JS_SET_SELECT = ("(function(){var p=Array.from(document.querySelectorAll('[role=tabpanel]')).find(function(p){return p.getAttribute('data-state')==='active' && p.innerText.indexOf('Select Image Model')>=0});"
                 "var s=p.querySelectorAll('select')[%d];var setter=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set;"
                 "var v=Array.from(s.options).map(function(o){return o.value}).find(function(v){return v.indexOf('%s')>=0});setter.call(s,v);s.dispatchEvent(new Event('change',{bubbles:true}));return v})()")
JS_SET_PROMPT = ("(function(){var p=Array.from(document.querySelectorAll('[role=tabpanel]')).find(function(p){return p.getAttribute('data-state')==='active' && p.innerText.indexOf('Select Image Model')>=0});"
                 "var t=p.querySelector('textarea');var setter=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;setter.call(t,%s);t.dispatchEvent(new Event('input',{bubbles:true}));return t.value.length})()")
JS_CLICK_GENERATE = ("(function(){var p=Array.from(document.querySelectorAll('[role=tabpanel]')).find(function(p){return p.getAttribute('data-state')==='active' && p.innerText.indexOf('Select Image Model')>=0});"
                     "var b=Array.from(p.querySelectorAll('button')).find(function(b){return b.textContent.trim()==='Generate'});b.click();return 'clicked'})()")
JS_PRICE = "(function(){var m=document.body.innerText.match(/(\\d+) credits/);return m?m[1]:'?'})()"
JS_IMG_URLS = "Array.from(document.querySelectorAll('img')).map(function(i){return i.src}).filter(function(s){return s.indexOf('public_media')>=0}).join(' ')"
JS_GENERATING = "document.body.innerText.indexOf('Generating')>=0 ? 'yes' : 'no'"
JS_OPEN_PICKER = "(function(){var b=Array.from(document.querySelectorAll('button')).find(function(b){return b.textContent.indexOf('Pick images')>=0});b.click();return 'ok'})()"
JS_PICK_INDEX = "(function(){var d=document.querySelector('[role=dialog]');var imgs=d.querySelectorAll('img');imgs[%d].click();return d.innerText.match(/\\(\\d+\\/14\\)/)[0]})()"
JS_INJECT_FILE = ("(async function(){var r=await fetch('%s');var b=await r.blob();var f=new File([b],'%s',{type:'image/png'});var dt=new DataTransfer();dt.items.add(f);"
                  "var inp=document.querySelector('[role=dialog] input[type=file]');inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));return 'set'})()")
JS_PICKER_COUNT = "(function(){var d=document.querySelector('[role=dialog]');return d?d.innerText.match(/\\(\\d+\\/14\\)/)[0]:'closed'})()"


def ev(js: str) -> str:
    out = oc(["eval", js], timeout=120).strip()
    return out.splitlines()[-1] if out else ""


def open_image_generate(editor_id: str) -> None:
    oc(["open", f"https://my.blotato.com/video-editor/{editor_id}"])
    time.sleep(6)
    ev("(function(){var b=Array.from(document.querySelectorAll('button')).filter(function(b){return b.textContent.trim()==='Image'});b[b.length-1].click();return 'ok'})()")
    time.sleep(2)
    oc(["click", "button[id$='-trigger-generate']"])
    time.sleep(2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--editor", required=True)
    ap.add_argument("--model", default="nano-banana-2")
    ap.add_argument("--ratio", default="9:16")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref-index", type=int, action="append", default=[])
    ap.add_argument("--ref-file", action="append", default=[])
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()

    refs = bool(a.ref_index or a.ref_file)
    if refs and "/edit" not in a.model:
        a.model = a.model + "/edit"
    print(f"[{'GO' if a.go else 'DRY'}] model={a.model} ratio={a.ratio} refs={a.ref_index}+{[Path(f).name for f in a.ref_file]} out={a.out}")
    if not a.go:
        return

    open_image_generate(a.editor)
    before = set(ev(JS_IMG_URLS).split())
    print("model:", ev(JS_SET_SELECT % (0, a.model)))
    time.sleep(1)
    if refs:
        print("ratio:", ev(JS_SET_SELECT % (1, a.ratio)))
        ev(JS_OPEN_PICKER)
        time.sleep(2)
        for i in a.ref_index:
            print("pick", i, ev(JS_PICK_INDEX % i))
        for f in a.ref_file:
            url = client.upload_file(client.load_api_key(), f)
            oc(["click", "[role=dialog] button[id$='-trigger-upload']"])
            time.sleep(1)
            ev(JS_INJECT_FILE % (url, Path(f).name))
            time.sleep(6)
            print("upload", Path(f).name, ev(JS_PICKER_COUNT))
        oc(["keys", "Escape"])
        time.sleep(1)
    print("prompt chars:", ev(JS_SET_PROMPT % json.dumps(a.prompt)))
    print("price:", ev(JS_PRICE))
    ev(JS_CLICK_GENERATE)
    for _ in range(40):
        time.sleep(6)
        if ev(JS_GENERATING) == "no":
            break
    time.sleep(2)
    after = [u for u in ev(JS_IMG_URLS).split() if u not in before]
    new = [u for u in after if "videogen2-img" in u or u.endswith(".png") or u.endswith(".jpg")]
    if not new:
        print("no new image found; page urls:", after[:3])
        sys.exit(2)
    url = new[-1]
    dest = client.download(url, a.out)
    print("url:", url)
    print("saved:", dest)


if __name__ == "__main__":
    main()
