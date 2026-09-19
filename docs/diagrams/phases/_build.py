"""Writes the six per-phase archify workflow sources. Run: python _build.py"""
import json, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
W = 128


def node(id, lane, col, type, label, sub, tag=None, width=W):
    n = {"id": id, "lane": lane, "col": col, "width": width, "type": type, "label": label, "sublabel": sub}
    if tag:
        n["tag"] = tag
    return n


def edge(a, b, label=None, variant=None):
    e = {"from": a, "to": b}
    if label:
        e["label"] = label
    if variant:
        e["variant"] = variant
    return e


lanes = [{"id": "drew", "label": "Drew decides"}, {"id": "skill", "label": "Skill does the work"}, {"id": "blotato", "label": "Blotato / OpenCLI"}]
lanes_free = [{"id": "drew", "label": "Drew decides"}, {"id": "skill", "label": "Skill does the work"}, {"id": "files", "label": "Saved files"}]

diagrams = {}

diagrams["01-new-niche"] = {
    "title": "Phase 1: New niche (free, by talking)",
    "lanes": lanes_free,
    "phases": [{"id": "a", "label": "Figure it out", "fromCol": 0, "toCol": 3}, {"id": "b", "label": "Write it down", "fromCol": 4, "toCol": 5, "variant": "emphasis"}],
    "main": ["idea", "niche", "angle", "who", "look", "refs", "card", "ok", "profiles"],
    "nodes": [
        node("idea", "drew", 0, "frontend", "Vague idea", "or none at all"),
        node("niche", "skill", 0, "backend", "Narrow the niche", "5 options, risky ones flagged", "analytics plugin later"),
        node("angle", "skill", 1, "backend", "Find the angle", "what makes it different"),
        node("who", "drew", 1, "security", "Pick", "viewer, mood, Shorts"),
        node("look", "skill", 2, "backend", "Choose the look", "stickman, painted, photo-real"),
        node("refs", "drew", 3, "security", "Pick", "2-5 channels to learn from"),
        node("card", "skill", 4, "backend", "One-page card", "everything in one place"),
        node("ok", "drew", 4, "security", "OK", "or a fix in plain words"),
        node("profiles", "files", 5, "database", "niche.md + style.md", "the two profiles"),
    ],
    "edges": [
        edge("idea", "niche", "what you like", "emphasis"),
        edge("niche", "angle", "picked niche", "emphasis"),
        edge("angle", "who", "questions", "emphasis"),
        edge("who", "look", "answers", "emphasis"),
        edge("look", "refs", "samples", "emphasis"),
        edge("refs", "card", "channels kept", "emphasis"),
        edge("card", "ok", "shows", "emphasis"),
        edge("ok", "profiles", "saves", "emphasis"),
    ],
    "cards": [
        {"dot": "emerald", "title": "Decided here", "items": ["Niche and angle", "Viewer, mood, format (Shorts first)", "Look, voice or silent, reference channels", "How it makes money"]},
        {"dot": "amber", "title": "Rules", "items": ["No finance, health, legal or political AI channels (YouTube will not pay)", "Every question is a lettered pick with a recommendation first", "Skipped as a skill for now: done by talking until the analytics plugin exists"]},
        {"dot": "cyan", "title": "Hands over", "items": ["niche.md: topic, audience, mood, money", "style.md: look, ratio, clip length, words per scene, voice, captions, music", "Read by every other skill", "Edit later reopens any single item"]},
    ]}

diagrams["02-asset-bible"] = {
    "title": "Phase 2: Asset bible",
    "lanes": lanes,
    "phases": [{"id": "a", "label": "Describe", "fromCol": 0, "toCol": 1}, {"id": "b", "label": "Generate + pick", "fromCol": 2, "toCol": 3, "variant": "emphasis"}, {"id": "c", "label": "Lock + reuse", "fromCol": 4, "toCol": 5}],
    "main": ["need", "sheet", "gen", "pick", "lock", "library"],
    "nodes": [
        node("need", "drew", 0, "frontend", "Say what you need", "a detective, 1890s London"),
        node("own", "drew", 1, "frontend", "Or give a picture", "your own reference"),
        node("sheet", "skill", 1, "backend", "Sheet prompt", "front, side, faces, plain"),
        node("gen", "blotato", 2, "cloud", "Make 2 variants", "Nano Banana 2, 30 credits each", "credits"),
        node("pick", "drew", 3, "security", "Pick A or B", "or: redo, less shadow"),
        node("lock", "skill", 4, "backend", "Lock it", "name it: detective"),
        node("more", "blotato", 4, "cloud", "Worlds + items", "same way, from the sheet", "credits"),
        node("library", "skill", 5, "database", "assets/", "characters, worlds, items"),
    ],
    "edges": [
        edge("need", "sheet", "words", "emphasis"),
        edge("own", "sheet", "picture", "dashed"),
        edge("sheet", "gen", "prompt + cost", "emphasis"),
        edge("gen", "pick", "2 pictures", "emphasis"),
        edge("pick", "lock", "the winner", "emphasis"),
        edge("lock", "more", "as reference"),
        edge("lock", "library", "saves", "emphasis"),
        edge("more", "library", "saves"),
    ],
    "cards": [
        {"dot": "emerald", "title": "Three kinds of reference", "items": ["Character: keeps face, outfit, proportions", "World: keeps palette, era, line style, mood", "Item: keeps an object's shape and markings"]},
        {"dot": "amber", "title": "What to expect", "items": ["Identity and style hold well; tiny details drift", "Every run is a fresh roll: look, keep, or redo", "2 references per image is best, 3 the ceiling"]},
        {"dot": "cyan", "title": "Blotato routes", "items": ["Text to image: API, any of 17 models", "From a reference: the Edit models, 15-50 credits", "Which template exposes Edit: confirm with the live list"]},
    ]}

diagrams["03-story"] = {
    "title": "Phase 3: Story (free: ideas, facts, script, grade)",
    "lanes": lanes_free,
    "phases": [{"id": "a", "label": "Idea", "fromCol": 0, "toCol": 1}, {"id": "b", "label": "Facts", "fromCol": 2, "toCol": 2}, {"id": "c", "label": "Script", "fromCol": 3, "toCol": 5, "variant": "emphasis"}],
    "main": ["ideas", "pickidea", "facts", "dropfacts", "script", "grade", "fix", "gate", "files"],
    "nodes": [
        node("ideas", "skill", 0, "backend", "10 ideas", "title, promise, wrong belief"),
        node("pickidea", "drew", 1, "security", "More, or a number", "pick one"),
        node("facts", "skill", 2, "backend", "Sourced facts", "free Blotato research + web"),
        node("dropfacts", "drew", 2, "security", "Drop 4 and 9", "or OK"),
        node("script", "skill", 3, "backend", "Scene-cut script", "6-7 words per 4-second clip"),
        node("grade", "skill", 4, "backend", "Grader", "8 checks, Shorts ruler", "7 is good"),
        node("fix", "drew", 4, "security", "Shorter, creepier", "fix in plain words"),
        node("gate", "drew", 5, "security", "Gate 1", "OK + credit limit"),
        node("files", "files", 5, "database", "videos/<slug>/", "idea, facts, script, OK"),
    ],
    "edges": [
        edge("ideas", "pickidea", "lettered list", "emphasis"),
        edge("pickidea", "facts", "chosen idea", "emphasis"),
        edge("facts", "dropfacts", "numbered, each with a link", "emphasis"),
        edge("dropfacts", "script", "approved facts", "emphasis"),
        edge("script", "grade", "draft", "emphasis"),
        edge("grade", "fix", "score + top 3 fixes", "emphasis"),
        edge("fix", "gate", "final script", "emphasis"),
        edge("gate", "files", "saves with the exact script", "emphasis"),
    ],
    "cards": [
        {"dot": "emerald", "title": "Where the words come from", "items": ["Ideas open on the viewer's wrong belief (Veritasium)", "Facts: anything without a source is barred", "Script written in passes: structure, spoken draft, specifics, strip AI tone"]},
        {"dot": "amber", "title": "The Shorts ruler", "items": ["Hook in 2 seconds, title confirmed fast", "One twist, ending on the reveal", "Beats linked by but / therefore, never and-then", "Originality: not interchangeable with the competitor's video"]},
        {"dot": "cyan", "title": "Honest gap", "items": ["No grader is proven against real retention data yet", "It catches bad scripts; it cannot promise a hit", "The analytics plugin will teach it later"]},
    ]}

diagrams["04-make"] = {
    "title": "Phase 4: Make (scenes to clips, one at a time)",
    "lanes": lanes,
    "phases": [{"id": "a", "label": "Plan scenes", "fromCol": 0, "toCol": 1}, {"id": "b", "label": "Pictures", "fromCol": 2, "toCol": 3, "variant": "emphasis"}, {"id": "c", "label": "Motion + voice", "fromCol": 4, "toCol": 5, "variant": "emphasis"}],
    "main": ["scenes", "okscenes", "meter", "stills", "review", "chain", "clips", "voice", "done"],
    "nodes": [
        node("scenes", "skill", 0, "backend", "Scene prompts", "one paragraph each"),
        node("okscenes", "drew", 1, "security", "OK, or your beats", "scene 3 in the alley"),
        node("meter", "skill", 2, "security", "Credit meter", "limit checked every call"),
        node("stills", "blotato", 2, "cloud", "Scene images", "refs by name", "credits"),
        node("review", "drew", 3, "security", "Keep / redo / fix", "one scene at a time"),
        node("chain", "skill", 3, "backend", "Chain", "kept scene is next ref"),
        node("clips", "blotato", 4, "cloud", "Animate", "Framepack 55, Kling 210, Veo", "credits"),
        node("voice", "blotato", 5, "cloud", "Voice per scene", "20 voices, free"),
        node("done", "skill", 5, "database", "clips/scene-NN.mp4", "+ credits.log"),
    ],
    "edges": [
        edge("scenes", "okscenes", "list", "emphasis"),
        edge("okscenes", "meter", "approved scenes", "emphasis"),
        edge("meter", "stills", "allows", "emphasis"),
        edge("stills", "review", "each image", "emphasis"),
        edge("review", "chain", "kept", "emphasis"),
        edge("chain", "clips", "stills in order", "emphasis"),
        edge("review", "stills", "redo with a fix", "dashed"),
        edge("clips", "voice", "clip + line", "emphasis"),
        edge("voice", "done", "saves", "emphasis"),
    ],
    "cards": [
        {"dot": "emerald", "title": "Natural-language moves", "items": ["The detective in the alley with the lantern: picks refs by name", "Redo 4, darker: regenerates only scene 4", "Save that for the channel: writes the fix into style.md"]},
        {"dot": "amber", "title": "Credits", "items": ["Image 15-50, Framepack 55, Kling 210, Veo 3.1 Fast about 35-50 per second", "Meter stops before the call that would pass the limit", "Dry-run mode prints what it would spend"]},
        {"dot": "cyan", "title": "Two routes", "items": ["API: still + voice, then animate (video-with-voice template, never run live yet)", "OpenCLI website: pick Veo or Kling, reference image, sound in the clip", "Frame chaining (Kling 1.6 start + end image) for continuity"]},
    ]}

diagrams["05-finish"] = {
    "title": "Phase 5: Finish (combine, cover, watch)",
    "lanes": lanes,
    "phases": [{"id": "a", "label": "Combine", "fromCol": 0, "toCol": 2, "variant": "emphasis"}, {"id": "b", "label": "Cover", "fromCol": 3, "toCol": 4}, {"id": "c", "label": "Gate 2", "fromCol": 5, "toCol": 5, "variant": "security"}],
    "main": ["order", "mood", "combine", "check", "thumb", "pickthumb", "watch"],
    "nodes": [
        node("order", "skill", 0, "backend", "Order + gaps", "in order, cut dead air"),
        node("mood", "drew", 1, "security", "Music mood", "+ caption style"),
        node("combine", "blotato", 1, "cloud", "Combine Clips", "music, fades, captions", "free"),
        node("check", "skill", 2, "backend", "Check the file", "length, sync, captions"),
        node("fallback", "blotato", 2, "backend", "Cinco Vid", "free ffmpeg backup", "if stitch fails"),
        node("thumb", "skill", 3, "backend", "5 thumbnail ideas", "in words, room for text"),
        node("pickthumb", "drew", 4, "security", "Pick one", "A to E"),
        node("render", "blotato", 4, "cloud", "Make thumbnail", "+ end screen", "credits"),
        node("watch", "drew", 5, "security", "Watch it", "post it, or fix scene 14"),
    ],
    "edges": [
        edge("order", "mood", "asks", "emphasis"),
        edge("mood", "combine", "choices", "emphasis"),
        edge("combine", "check", "final.mp4", "emphasis"),
        edge("combine", "fallback", "fails", "dashed"),
        edge("check", "thumb", "video OK", "emphasis"),
        edge("thumb", "pickthumb", "lettered list", "emphasis"),
        edge("pickthumb", "render", "the pick"),
        edge("pickthumb", "watch", "video + cover", "emphasis"),
    ],
    "cards": [
        {"dot": "emerald", "title": "From the tutorial", "items": ["Cut gaps between clips or speed up slightly", "Background music matching the mood, volume low, fade in and out", "Captions in a storytelling style, placed off the action"]},
        {"dot": "amber", "title": "Fixes", "items": ["Scene 14 looks wrong: re-renders only that scene, then combines again", "Never the whole video", "Title + description come from the script"]},
        {"dot": "cyan", "title": "Done when", "items": ["final.mp4, thumbnail.png, title and description saved", "Drew's OK saved against the exact file he watched", "Combine Clips has never been run live: first real test"]},
    ]}

diagrams["06-publish-learn"] = {
    "title": "Phase 6: Publish and learn",
    "lanes": lanes,
    "phases": [{"id": "a", "label": "Post", "fromCol": 0, "toCol": 1, "variant": "emphasis"}, {"id": "b", "label": "Wait", "fromCol": 2, "toCol": 3, "variant": "dashed"}, {"id": "c", "label": "Learn", "fromCol": 4, "toCol": 5}],
    "main": ["when", "post", "link", "numbers", "compare", "lessons", "next"],
    "nodes": [
        node("when", "drew", 0, "security", "Post it, or a time", "schedule"),
        node("post", "blotato", 1, "external", "Post to YouTube", "title, text, cover", "free"),
        node("link", "skill", 2, "database", "youtube.md", "the link, saved"),
        node("numbers", "drew", 3, "frontend", "Paste the numbers", "views, watch time, drop-off"),
        node("compare", "skill", 4, "backend", "Compare to the plan", "hook? slow beat? ending?"),
        node("lessons", "skill", 5, "database", "1-3 lessons", "into niche.md, style.md, assets"),
        node("next", "drew", 5, "frontend", "Next video", "starts smarter"),
    ],
    "edges": [
        edge("when", "post", "go", "emphasis"),
        edge("post", "link", "saves", "emphasis"),
        edge("link", "numbers", "days later", "emphasis"),
        edge("numbers", "compare", "pasted in", "emphasis"),
        edge("compare", "lessons", "writes", "emphasis"),
        edge("lessons", "next", "read by every skill", "emphasis"),
    ],
    "cards": [
        {"dot": "emerald", "title": "Now", "items": ["Blotato posts or schedules; nothing posts before Gate 2", "Blotato cannot read YouTube numbers, so Drew pastes them from Studio", "Lessons are short and dated"]},
        {"dot": "amber", "title": "Later: analytics plugin", "items": ["Pulls the numbers itself", "Feeds Phase 1 (niche picking) and Phase 3 (the grader)", "Separate plugin, planned by Drew"]},
        {"dot": "cyan", "title": "Also from Sollo", "items": ["Why it flopped check: this is it (Phase 6)", "Digital-product builder: skipped for now"]},
    ]}

for name, d in diagrams.items():
    out = {"schema_version": 2, "diagram_type": "workflow",
           "meta": {"title": d["title"], "output": name + ".html", "quality_profile": "showcase"},
           "lanes": d["lanes"], "phases": d["phases"], "mainPath": d["main"], "nodes": d["nodes"], "edges": d["edges"], "cards": d["cards"]}
    json.dump(out, open(name + ".workflow.json", "w"), indent=2)
print("written", list(diagrams))
