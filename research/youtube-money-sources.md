# YouTube money build: every source, tool and service we'll use

## How it works with any AI in any Discord thread
- **The project folder IS the plugin.** Every Discord session starts inside its folder, so whatever AI runs the thread (Claude, Codex, DeepSeek/DSH) reads the same instructions and skills from that folder.
- **One instruction file for all AIs:** `AGENTS.md` in the folder. Codex and DSH read it directly; Claude reads it through a one-line `CLAUDE.md` that points to it. **Written once, never copied per AI.**
- **One skills folder:** `.agents/skills/`, with a link so Claude's `.claude/skills/` points to the same place. Each flow ("find a channel to study", "clone its style", "write a script", "grade it", "make scenes", "post it") is one skill.
- **Small scripts do the real work** (pulling transcripts, calling Blotato, checking credits). Any AI can run a script, so nothing depends on one AI's special features.
- **Blotato is reached by plain web calls from those scripts**, not only through its connector (MCP), because every AI can run a script but not every AI has connectors set up.
- ✅ **Your blotato-automations folder already works this way** (`.agents/skills/` plus shared scripts), so we build on that pattern.
- ✅ **/gowork can now use every Codex model, picked per step** (saved on the bot's test copy, not live yet; it goes live when the bot restarts). Saying "go work codex" means the bot picks the best of your 5 Codex models for each step: gpt-5.6-luna for easy steps, sol, terra and 5.5 for everyday steps, gpt-6-astra for hard ones.

## Paid services (only these) and free tools
### 💲 Paid
- **Blotato** (you already pay):
  - Images: 17 models, from Flux Schnell (1 credit) to Nano Banana Pro (50 credits)
  - Video: 12 models, including Kling, Veo, Runway and Framepack
  - Voiceover: 20 built-in voices, **free**
  - Research: turns a link, topic or YouTube video into source material, **free**
  - Posting to YouTube and 8 other platforms, **free**
  - Post analytics, comment and DM replies
  - Plans: $29 = 1,250 credits, $97 = 5,000, $499 = 28,000; extra credits $6 per 1,000
- **Your AI subscriptions** (Claude, Codex, DeepSeek) do the thinking and writing.
- 🚫 **Never:** Kie.ai, HeyGen, Apify, OpenAI API keys, Perplexity keys, Bright Data, or other outside paid generators. Many templates use these; we take their prompt text only.
### ✅ Free tools already on this machine
- **yt-dlp:** pulls YouTube transcripts, titles, view counts and subscriber counts.
- **OpenCLI:** drives Blotato's website in your logged-in Chrome. It's for what the API can't do: choosing a specific video model (Kling, Veo…) and animating your own photos. ⬜ The Blotato command set for it still needs building.
- **ffmpeg + Pillow:** a free local video assembler, already built in Cinco Vid (zoom/pan, word-pop captions, music), as a backup to Blotato's stitching.
- **Your installed writing skills:** interviewer (Story Bank), humanizer, no-ai-slop, hook extractor.

## Where the writing quality comes from (proven people, checked)
### The 5 rules the grader scores (each has real proof)
- **Paddy Galloway** (strategist for MrBeast, Mark Rober; claims ~50B views): prove the title's promise within **10 seconds**, add one specific tease, then go straight in with no "let's get into it". YouTube's own "Intro" metric checks who's still watching at **30 seconds**.
- **MrBeast's leaked production guide** (517M subscribers): the first minute matters most; add a fresh surprise around **3:00 and 6:00**; never signal the end early; end fast after the payoff.
- **"But / therefore" (South Park creators, used by Kallaway, 458K subs):** every beat links to the next with "but" or "therefore", never "and then". It's the easiest rule to check by machine.
- **Open loops (George Blackman, Ali Abdaal's scriptwriter; Jake Tran, faceless documentary channel, 1.84M subs):** the viewer should always be waiting for something in the next **60–90 seconds**. Setup, then tension, then payoff; giving the payoff first cost one of Blackman's videos **43% of viewers**.
- **Start from the wrong belief (Derek Muller, Veritasium, 21.3M subs):** his PhD study showed that naming the common misconception first nearly **doubled test scores** versus a clear explanation alone.
### Extra rules
- **Johnny Harris (7.96M):** state the promise by 1:00; active sentences ("who did what to whom"); a visual note every 1–2 sentences.
- **Kurzgesagt (25.6M):** check every fact; plan a visual comparison for every idea.
- **Jake Tran:** his hit videos share one fill-in-the-blank structure, and writers kept results using his structure in their own words. **This proves "copy structure, not wording" works.**
- **YouTube's official rule** (the "inauthentic content" policy, updated July 2025, split into 3 parts around July 2026): videos that "mimic existing formats… to a degree that the videos feel interchangeable" can't earn money. The same pattern is allowed if "each video has a distinct storyline, focus, or concept." → **our grader gets an "interchangeable?" check.**

## Prompt building blocks we copy from
### GitHub
- **yashaiguy faceless-youtube-agents:** closest to our whole flow (top videos → "Viral DNA" → long script). We drop its "copy exact opening lines" part. ⚠️ No license: reference only, rewritten.
- **AgriciDaniel claude-youtube** (379 stars, MIT): the best retention script template (hook in 3 parts, mid-video call to action at 25%, re-hook at 60%) plus a quality checklist.
- **writing-dna-skill** (1,965 stars, MIT): the most careful style extractor (6 layers; "copy the method, never the content").
- **yaxeen storytelling-skills** (MIT): open-loop tracker, re-hook where attention drops (40–60% in), "what winners have that flops don't".
- **Jakeschincariol youtube-agent-skill** (MIT): a hook scorer plus 21 hook formulas. It's the only one tested honestly: it catches bad hooks but can't predict hits.
- **Fabric "wow per minute"** (44k stars): scores surprise and insight per minute, which fits curiosity channels.
- Smaller extras: a style-to-JSON profile, voice-DNA prompt, hook formulas, a hook rubric.
### n8n and Blotato templates
- **Blotato "Clone Viral Reels" (Blotato's founder):** the best "keep the structure, change the content" rules.
- **n8n 4110 (135k views):** "must keep / may change" lists.
- **n8n 13676:** the best-written style prompt (good and bad example sentences, 6th-grade level).
- **n8n 2648:** a two-part style extractor (structure + voice traits with quotes).
- **n8n 9342:** the only true long-form writer (2,500–3,000 words, with a reference-script slot).
- **n8n 18255:** how to pick which competitor videos to study (videos that beat that channel's own average).
- **Blotato's official skills:** post-grader (hook = 50% of the score, "top 3 fixes") and viral-hooks (100 hooks).
- ⬜ **Blotato's in-app "YouTube Video Script" prompt** is only visible inside your logged-in account. It's free to look at.
### Real operators (Reddit / X): helpful but mostly unproven
- **Upper-Mountain (r/aitubers, 52 upvotes, commenters vouch):** a multi-pass writer: structure → a draft written for the ear → add detail → remove the AI tone.
- **Leo Grundström (36.8K followers, runs faceless channels, sells a course):** his Claude script method. ⚠️ He pastes a competitor's script on the same topic, which is content reuse; we take structure only.
- **Brilliant-Shift (r/aitubers):** match each drop in the retention graph to the exact sentence. This feeds the grader once videos are live.
- **Hamza Khalid (352K views on X):** a 5-video channel clone flow. ⚠️ Promotional, no channel of his own.
- **woody_research, zhacker:** ⚠️ inconsistent income claims or promotional links. Used only as examples of structure.
- ⚠️ **The Reddit/X search was cut off twice**, so this part is not complete.

## Rules, risks and what isn't proven yet
- ✅ **Copy structure, never wording.** Style DNA stores only measurements (pacing, loop spacing, sentence length), never phrases.
- ✅ **Every fact has a source**, from Blotato's free research.
- ⚠️ **No public prompt has proof of results.** No repo or template shows a channel's before/after numbers. The proof comes from the creator rules above, and later from **your own retention graphs**.
- ⚠️ **Nobody checks that a script didn't copy the source's words.** We add an overlap check ourselves.
- ⚠️ **Blotato's AI video template has never been run live in your folders.** The first real video should be a small, cheap test.
- ⬜ **The folder for this build doesn't exist yet.** All research is saved and ready to move into it.
