# You were right — and it's better news than that

## ✅ Correction: image-to-image works, through OpenCLI

You said Blotato can do picture-to-picture if we use OpenCLI. **That's now written into the project as the settled answer**, so no future session treats it as an open question.

To be precise about what I found and what you corrected:

- **Blotato's API genuinely cannot do it.** I listed all 37 of its templates. Only two accept an image model, and both only offer **text-to-picture** models. No "edit this picture" model is reachable that way.
- **The website can**, and that's what OpenCLI drives. So picture-to-picture isn't missing — it just lives on the other road.

**Why this one matters more than the rest:** picture-to-picture is how a character keeps the same face across every scene of a video. Without it there's no consistent character, and no faceless channel.

## 🎉 The bigger surprise: this computer is the computer

The old handoff note said the real testing had to wait for your other machine. **It doesn't. Both things it said were missing are here.**

### What I actually checked
- **The Blotato key works here** — 12,420 credits, about $74.
- **OpenCLI is installed here**, version 1.8.7. The reason nobody noticed: it isn't on the normal search path, so the usual "is it installed?" check comes back empty.
- **Your browser is connected and logged into Blotato.** I opened it and looked around: the video editor has an **Image** tool right in the sidebar, which is where the picture-to-picture path starts.

**So there's no waiting step left.** Both roads run from this machine.

### Two traps I wrote down so nobody trips again
- ⚠️ OpenCLI's own health check **says the browser isn't connected when it is.** The other command tells the truth. Don't reinstall anything.
- ⚠️ It drives whichever tab is in front, and it drifted away from Blotato twice while I was looking. Blotato should sit in its own window.

## ⏳ The corrected plan

**The goal, now in two halves:** you say "make a character sheet" and the API makes it. Then you say "the same detective, in the alley" and the website makes it **with that sheet as the reference**. A real picture lands in the thread both times, and the credits match Blotato's bill.

### Free first — no credits, no risk
- ⬜ Fix a false alarm in the code (it thinks it can't find a Blotato template; it can)
- ⬜ Make it save a real **picture**, not just a video — Blotato hands back a one-slide video, so we pull the first frame out
- ⬜ Replace guessed prices with the thirteen models Blotato really offers
- ⬜ Write down the road split and the OpenCLI path so no session re-discovers this
- ⬜ **Walk the website picture-to-picture path by hand, spending nothing** — find the model list and the reference-upload control, screenshot every step
- ⬜ Start a **true crime** channel profile with blanks the tests fill in
- ⬜ Run everything as a zero-spend rehearsal

### Then the paid tests — each waits for a credit limit from you
- ⬜ Character sheet, cheap model then good model → pick the winner
- ⬜ A world, an item, a thumbnail with room for a headline
- ⬜ Upload one of your own pictures, confirm it comes back usable
- ⬜ **The face test:** the same character in a new pose, then in a second scene. If the face holds, the whole pipeline is real. This is the most important test in the project.
- ⬜ Two more reference tests (a world, an item), then mixing two references
- ⬜ Check the credit log against Blotato's real bill, and write the winning models into the channel profile

**Rough cost of the whole thing: around 300 credits — under two dollars.**

## ⬜ Where it stands

**No credits spent. No code changed yet. Nothing pushed to GitHub.**

Saved locally as two save-points: the plan, and the correction to the routing.
