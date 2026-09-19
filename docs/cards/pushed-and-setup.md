# Pushed to GitHub — and here's the other computer's setup

## ✅ It's on the repo

**9 commits pushed** to `Pu11en/youtube-money`. Working tree clean, nothing left behind.

### I checked for leaks before pushing
- **Your Blotato key is not in there.** Scanned every tracked file — the only match was code reading the setting's *name*, not the key itself.
- **Not uploaded:** your key file, the machine-specific settings, everything in the outputs folder, and the private transcripts.

### What's now on GitHub
- The generation plumbing — one front door plus the price catalog
- **Every measured price**, so the other computer starts knowing what things cost
- The two test write-ups, including the mistakes
- The rules, including the two learned expensively today
- The setup guide for the new machine

## 🖥️ The setup guide, and the one hard part

Most of it is quick. **The only fiddly bit is OpenCLI**, so here's the thing to understand before starting:

### OpenCLI does not log into Blotato for you
It **doesn't open Chrome and it doesn't sign in.** It talks to a small extension running inside a Chrome you already have open.

So the real requirement isn't "install OpenCLI" — it's:

> **A Chrome window, already signed into Blotato, with the bridge extension loaded.**

### The four steps
- ⬜ **Install the tool** with npm into a local folder
- ⬜ **Download the extension** from its releases page
- ⬜ **Load it** into the Chrome profile you use for Blotato — turn on Developer Mode in the extensions page, then "Load unpacked"
- ⬜ **Sign into Blotato in that same profile** and leave it open

### ⚠️ Four traps I already hit — all written down
1. **It won't be on the normal search path.** The usual "is it installed?" check comes back empty even when it's installed fine. Nobody should reinstall it over this.
2. **Its own health check lies.** It reports the browser as disconnected while it's actually connected and working. There's a second command that tells the truth — trust that one.
3. **It drives whatever tab is in front.** It wandered off Blotato twice on me. Keep Blotato in its own window.
4. **Several Chrome profiles open at once can break the connection.** Close the others.

### The profile name will be different over there
**That's expected, not a problem.** It's just whichever Chrome profile is signed in. Only that one setting differs between the two computers — everything else travels in the repo.

## ⚠️ One shared wallet

The **Blotato account and its credits are the same on both machines.** Two sessions generating at once spend from the same pot.

So: check the live balance rather than a remembered number, and give each machine its own ceiling.

## 🎯 Why that computer matters

The API half is proven and works anywhere — including **free videos from your own uploaded pictures**.

**Two things exist only in the browser**, and they're the two you most want:

- ⬜ **Two references at once** — a Pinterest image to depart from *plus* your logo or character held exactly. No API path accepts two pictures.
- ⬜ **Naming a specific video model** like Kling or Veo.

**First job over there, free:** open Blotato's image maker, list every model, find whether an edit model takes an uploaded reference, screenshot each step, and write the clicks down.

## 📊 Current state

**Balance 11,310 credits.** Nothing spent since the video tests.
