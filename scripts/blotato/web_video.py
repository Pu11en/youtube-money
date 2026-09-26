"""Drive Blotato's website video generator: text-to-video and image-to-video.

The API cannot reach the named video models at all - all 37 templates are template
based - so Veo only exists through the website. This is the adapter for it.

    python scripts/blotato/web_video.py probe
    python scripts/blotato/web_video.py t2v "prompt" --seconds 4
    python scripts/blotato/web_video.py i2v "prompt" --image path.jpg --seconds 4

Credits are the truth, not the page: charged-and-held is a success, charged-then-
refunded is a refusal. Every run prints the balance before and after.
"""
import argparse
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


web = _load("web", os.path.join(HERE, "web.py"))
client = _load("bclient", os.path.join(HERE, "client.py"))

EDITOR = "https://my.blotato.com/video-editor/c4adbeb7-a1c4-4d9a-855a-250ae721b398"
NOISE = ("Update available", "npm install", "[exit")


def ev(js, timeout=180):
    """Evaluate JS in the page and return the value, minus opencli's own chatter."""
    out = web.run(["eval", js], timeout=timeout)
    lines = [l for l in out.splitlines() if not any(n in l for n in NOISE)]
    return "\n".join(lines).strip()


def credits():
    return client.credits(client.load_api_key())["creditsRemaining"]


def open_generator(model):
    """Editor -> Video tool -> Generate -> pick the model. Idempotent."""
    web.run(["open", EDITOR], timeout=180)
    time.sleep(9)
    ev("(function(){var b=Array.from(document.querySelectorAll('button'))"
       ".filter(function(x){return x.textContent.trim()==='Video'});"
       "b[b.length-1].click();return 1})()")
    time.sleep(3)
    web.run(["click", "button[id$='-trigger-generate']"])
    time.sleep(4)
    got = ev("(function(){var s=document.querySelectorAll('select')[0];"
             "s.value=%s;s.dispatchEvent(new Event('change',{bubbles:true}));"
             "return s.value})()" % json.dumps(model))
    time.sleep(3)
    return got


def set_options(seconds, aspect="9:16"):
    return ev("(function(){var s=document.querySelectorAll('select');"
              "for(var i=0;i<s.length;i++){var v=Array.from(s[i].options)"
              ".map(function(o){return o.value});"
              "if(v.indexOf(%s)>=0){s[i].value=%s;s[i].dispatchEvent(new Event('change',{bubbles:true}));}"
              "if(v.indexOf(%s)>=0){s[i].value=%s;s[i].dispatchEvent(new Event('change',{bubbles:true}));}}"
              "return 'options set'})()"
              % (json.dumps(seconds), json.dumps(seconds),
                 json.dumps(aspect), json.dumps(aspect)))


def set_prompt(text):
    return ev("(function(){var t=Array.from(document.querySelectorAll('textarea'))"
              ".find(function(x){return (x.placeholder||'').indexOf('paste your prompt')>=0});"
              "if(!t)return 'no prompt box';"
              "var s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;"
              "s.call(t,%s);t.dispatchEvent(new Event('input',{bubbles:true}));"
              "return 'prompt '+t.value.length+' chars'})()" % json.dumps(text))


def price():
    return ev("(function(){var m=document.body.innerText.match(/(\\d[\\d,]*) credits/);"
              "return m?m[1]:'unknown'})()")


def attach_image(local_path):
    """Put a local file into the picker.

    The dialog has tabs Scene Images | Upload | Close. Clicking the Upload tab is not
    enough on its own - the file input is mounted lazily - so this hosts the file
    first, then injects a real File into whatever input appears.
    """
    url = client.upload_file(client.load_api_key(), local_path)
    print("hosted:", url)

    ev("(function(){var b=Array.from(document.querySelectorAll('button'))"
       ".find(function(x){return x.textContent.indexOf('Pick an image')>=0});"
       "if(b)b.click();return 'picker'})()")
    time.sleep(5)

    ev("(function(){var d=document.querySelector('[role=dialog]');if(!d)return 0;"
       "var t=Array.from(d.querySelectorAll('[role=tab],button'))"
       ".find(function(x){return x.textContent.trim()==='Upload'});"
       "if(t){t.click();['pointerdown','mousedown','mouseup','click'].forEach(function(e){"
       "t.dispatchEvent(new MouseEvent(e,{bubbles:true}))});}return 1})()")
    time.sleep(4)

    inputs = ev("(function(){return document.querySelectorAll('input[type=file]').length})()")
    print("file inputs after Upload tab:", inputs)
    if inputs == "0":
        # Nothing to inject into: the dropzone mounts its input only on a real pointer
        # event over the drop area. Try the area itself before giving up.
        ev("(function(){var d=document.querySelector('[role=dialog]');if(!d)return 0;"
           "var z=d.querySelector('[class*=border-dash],[class*=dropzone],[class*=cursor-pointer]');"
           "if(z){['pointerover','pointerdown','mousedown','mouseup','click'].forEach(function(e){"
           "z.dispatchEvent(new MouseEvent(e,{bubbles:true}))});}return 1})()")
        time.sleep(3)
        inputs = ev("(function(){return document.querySelectorAll('input[type=file]').length})()")
        print("file inputs after poking the dropzone:", inputs)

    if inputs == "0":
        return False

    name = os.path.basename(local_path)
    ev("(async function(){var r=await fetch(%s);var b=await r.blob();"
       "var f=new File([b],%s,{type:b.type||'image/jpeg'});"
       "var dt=new DataTransfer();dt.items.add(f);"
       "var i=document.querySelector('input[type=file]');i.files=dt.files;"
       "i.dispatchEvent(new Event('change',{bubbles:true}));return 'injected'})()"
       % (json.dumps(url), json.dumps(name)))
    time.sleep(10)

    ev("(function(){var d=document.querySelector('[role=dialog]');if(!d)return 0;"
       "var c=Array.from(d.querySelectorAll('button'))"
       ".find(function(x){return x.textContent.trim()==='Close'});if(c)c.click();return 1})()")
    time.sleep(2)

    still = ev("(function(){return document.body.innerText.indexOf('Pick an image')>=0"
               "?'not attached':'attached'})()")
    print("attach result:", still)
    return still == "attached"


def generate_and_wait(minutes=10):
    before = credits()
    print("credits before:", before)
    ev("(function(){var b=Array.from(document.querySelectorAll('button'))"
       ".filter(function(x){var t=x.textContent.trim();return t==='Generate'||t==='Retry'});"
       "b[b.length-1].click();return 'generate'})()")
    time.sleep(20)
    charged = credits()
    print("credits after click:", charged, "(spend %d)" % (before - charged))
    if charged == before:
        print("nothing was charged - the click did not submit")
        return None, before

    for _ in range(minutes * 6):
        time.sleep(10)
        now = credits()
        if now >= before:
            print("REFUSED - credits refunded to", now)
            return None, now
        urls = ev("(function(){return Array.from(document.querySelectorAll('video'))"
                  ".map(function(v){return v.currentSrc||v.src||''}).join(' ')})()")
        fresh = [u for u in urls.split() if "videogen2-vid" in u]
        if fresh:
            return fresh[-1], now
    print("timed out waiting")
    return None, credits()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["probe", "t2v", "i2v"])
    ap.add_argument("prompt", nargs="?", default="")
    ap.add_argument("--image")
    ap.add_argument("--seconds", default="4s")
    ap.add_argument("--out", default="tests/generation/video/out.mp4")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    model = ("fal-ai/veo3.1/fast/image-to-video" if a.mode == "i2v"
             else "fal-ai/veo3.1/fast")
    print("model:", open_generator(model))

    if a.mode == "probe":
        print(ev("(function(){var d=document.querySelector('[role=dialog]');"
                 "return document.body.innerText.replace(/\\n+/g,' | ').slice(0,600)})()"))
        sys.exit(0)

    if a.mode == "i2v":
        if not a.image or not attach_image(a.image):
            raise SystemExit("ABORT: no reference image attached. Nothing spent.")

    print(set_options(a.seconds))
    print(set_prompt(a.prompt))
    print("price shown:", price())

    url, after = generate_and_wait()
    print("credits now:", after)
    if not url:
        raise SystemExit(2)
    dest = client.download(url, os.path.join(ROOT, a.out))
    print("saved:", dest)
