# Logo style test — Blotato as a plain in-door / out-door

Run `logo-style`, 2026-09-19. Ceiling Drew set: **150 credits**. Spent: **100**. Left unspent: 50.
Route: `scripts/blotato/style.py` → `Product Scene Placement` (`f524614b-…`), the only API template
that generates a new picture from a supplied one.

Reference: `channels/drew-brand/assets/logos/logo-arch.png`, 1024×1024, a wide flat gold dome with a
smooth notch cut up from the centre of its base. Outputs in `runs/tests/style/` (git-ignored).

## Measured facts (these were unknown before this run)
- **Cost: exactly 50 credits per generation**, measured twice from the balance (12,420 → 12,370 → 12,320).
  At $6 per 1,000 credits that's **$0.30 a picture**. It is not in any published table; it is now.
- **Turnaround: about 32 seconds** per picture, both times.
- **Upload is free** and worked first try; the reference came back as a public URL.
- The template has **no aspect-ratio input**.

## 01-concrete — gold arch embossed in a dark concrete wall
- Verdict: **FAIL on likeness, PASS on craft**
- Credits: 50
- The picture itself is genuinely good: believable recess, raking light, real shadow depth.
- But the mark is **redrawn, not placed**. The original is wide and flat — roughly twice as wide as
  it is tall, with a straight base running the full width. The output is a **tall horseshoe**, close
  to square, with the base corners rounded and pulled inward. Same idea, different logo.

## 02-neon — gold arch as a neon sign on wet black brick
- Verdict: **FAIL on likeness, PASS on craft**
- Credits: 50
- The scene is excellent — wet brick, glow spill, bokeh city behind.
- **The same distortion, in the same direction**, even though the prompt explicitly said "keep the
  mark's outline exactly as given". Tall horseshoe again, flat wide base gone again. Asking nicely
  does not fix it.

## What the block decides
- **Does this API route hold an exact likeness? No.** Two shots, two different scenes, the same
  systematic re-proportioning. This confirms the `image-taste` note from 2026-09-08 (colour and edge
  shift) and extends it: **the shape drifts too, and prompt wording will not hold it.**
- **Is it useless? No** — it is a strong *stylist*. For anything where the mark only has to read as
  itself (background plates, mood frames, scene stills from a character sheet), 50 credits for this
  quality is good value.
- **For an exact-likeness lock, the route is the website with OpenCLI**, as Drew said. That remains
  the next thing to prove.
- **Do not use this template for a logo lockup, a thumbnail badge, or a watermark.** It will quietly
  hand back a logo that is not Drew's.

## Two defects in the output path, to fix (free)
1. **The file is a JPEG carrying a `.png` name.** `client.download` names the file from the
   requested path, not from what actually arrived. Fix: sniff the bytes or read the content type.
2. **Output is 1080×1350 (4:5), not the 1:1 that went in.** The template offers no ratio control, so
   square output needs a crop step or the website route.
