"""Builds docs/youtube-research-guide.pdf: a plain-language guide to the research tool."""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube-research-guide.pdf")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=24, leading=30, spaceAfter=6, alignment=TA_LEFT)
H2 = ParagraphStyle("H2", parent=ss["Heading1"], fontSize=16, leading=20, spaceBefore=16, spaceAfter=6,
                    textColor=colors.HexColor("#1f2937"))
H3 = ParagraphStyle("H3", parent=ss["Heading2"], fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=3)
P = ParagraphStyle("P", parent=ss["Normal"], fontSize=10.5, leading=15, spaceAfter=6)
SMALL = ParagraphStyle("S", parent=P, fontSize=9, leading=12, textColor=colors.HexColor("#4b5563"))
B = ParagraphStyle("B", parent=P, leftIndent=14, bulletIndent=2, spaceAfter=3)
CODE = ParagraphStyle("C", parent=P, fontName="Courier", fontSize=9.5, leading=13, backColor=colors.HexColor("#f3f4f6"),
                      borderPadding=(4, 6, 4, 6), leftIndent=6, spaceBefore=2, spaceAfter=8)
CELL = ParagraphStyle("Cell", parent=P, fontSize=9.5, leading=12.5, spaceAfter=0)
CELLB = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold")


def p(t, s=P):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, B, bulletText="•") for i in items]


def table(rows, widths, header=True):
    data = [[Paragraph(c, CELLB if (header and r == 0) else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
             ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")))
    t.setStyle(TableStyle(style))
    return t


story = [
    p("YouTube Research Tool", H1),
    p("What it can do, what it can't, and how to ask for it. youtube-money, 19 Sep 2026.", SMALL),
    Spacer(1, 8),

    p("The one-paragraph version", H2),
    p("You type <b>research &lt;topic&gt;</b> in a Discord session. The tool asks YouTube for up to 50 public videos "
      "on that topic, pulls the numbers anyone can see on a video page (views, likes, comments, length, date, "
      "channel size), and turns them into a one-page scorecard of the niche. It is free, it spends no Blotato "
      "credits, and it never touches anyone's private YouTube Studio data. The session (Claude or Codex) then "
      "reads that scorecard and tells you what it means. No other AI service is involved."),

    p("What you can ask for", H2),
    table([
        ["Say this", "What you get"],
        ["research true crime shorts", "A snapshot of the 25 most relevant videos for that search."],
        ["research true crime, most viewed, this year, under 4 min",
         "The same, sorted by views, only videos from the last 12 months, only short ones. Any mix of the filters below."],
        ["research MrBallen", "That channel's videos in the sample, plus who else shows up next to them."],
        ["find outliers in <niche>", "The videos that did far better than their channel's size would predict: small channels that blew up."],
        ["insights", "The session reads the snapshot and writes a plain report: what is clearly true, what is a guess, and what would need the owner's private data to confirm."],
        ["ideas / script / thumbnail",
         "Written and ready, but parked. Drew's current focus is image and video generation, so these wait."],
    ], [2.4 * inch, 4.4 * inch]),
    Spacer(1, 6),
    p("Filters you can add in plain words", H3),
    table([
        ["Filter", "Choices", "Default"],
        ["Sort", "most relevant, newest, most viewed, best rated", "most relevant"],
        ["Published", "last hour, today, this week, this month, this year, any time", "any time"],
        ["Length", "under 4 min, 4 to 20 min, over 20 min, any", "any"],
        ["How many", "1 to 50 videos", "25"],
    ], [1.3 * inch, 4.0 * inch, 1.5 * inch]),

    p("What comes back", H2),
    p("Two files are saved in the project folder under <b>channels/&lt;channel&gt;/research/&lt;topic&gt;/</b>: "
      "<b>snapshot.md</b> (the readable scorecard) and <b>snapshot.json</b> (the raw data, for the tools that come after)."),
    p("Per video", H3),
    *bullets([
        "Title, description (first 320 characters), tags, category, language",
        "Views, likes, comments (when the channel shows them; hidden ones stay blank, never zero)",
        "Exact length in seconds, publish date, captions yes/no, HD or not",
        "Whether it was a live stream, made for kids, or has a paid product placement",
        "Thumbnail link (the address only; the tool has not looked at the picture)",
    ]),
    p("Per channel", H3),
    *bullets([
        "Subscriber count (today's rounded number), total channel views, number of videos uploaded",
        "Country, channel age, channel description and topic categories",
    ]),

    KeepTogether([
        p("The scorecard: what each number means", H2),
        table([
            ["Number", "What it tells you", "Watch out"],
            ["Median vs average views", "Median is the typical video. If the average is much higher, one or two viral videos are dragging it up.",
             "Trust the median for 'what does a normal video do here'."],
            ["Views per day", "Views divided by how many days the video has been up. Lets a 2-week-old video with 500k beat a 5-year-old one with 2M.",
             "It is an age-adjusted proxy, not real-time speed."],
            ["Reach vs subscribers", "Views divided by the channel's subscribers. 595x means a tiny channel went huge. This is the outlier finder.",
             "Uses today's subscriber count, not the count when the video was posted."],
            ["Visible interaction rate", "(likes + comments) divided by views. Rough 'did people care' signal.",
             "Not watch time, not satisfaction. Only computed on videos that show all three numbers."],
            ["Length mix", "How many videos are under 4 min, 4 to 20, over 20. Tells you if the niche is Shorts or long-form.",
             "Under 4 minutes does not automatically mean it is a YouTube Short."],
            ["Recency mix", "How many were posted in the last week, month, year, or earlier. Is the niche still alive?", ""],
            ["Recurring tags", "Words several videos share. The vocabulary of the niche.", "Only about 40% of videos show tags at all."],
            ["Channel concentration", "How many different channels are in the sample and who has the most. Is one creator owning the niche?", ""],
            ["Coverage", "For each field, how many of the videos actually had it (e.g. likes 9/10). Tells you how solid the other numbers are.", ""],
        ], [1.5 * inch, 3.0 * inch, 2.3 * inch]),
    ]),

    p("Real example: 'true crime shorts', 10 videos (19 Sep 2026)", H2),
    *bullets([
        "Typical video: 1.7M views. Average 3.6M, so a couple of monsters are in there (max 9.8M).",
        "Length mix: 4 under 4 min, 5 over 20 min. The search mixes Shorts with long documentaries; filter by length next time.",
        "9 of 10 are more than a year old. Nothing recent ranked, so the newest work is not what YouTube surfaces for this phrase.",
        "One video sits at 595x its channel's subscriber count. That is the kind of breakout the competitors skill will hunt for.",
        "Channels: EXPLORE WITH US (2), MrBallen Shorts, Unreal True Crime, Oddities on Elm Street, and others. Nobody dominates.",
        "Shared tags: 'true crime', 'true crime documentary', 'true crime stories', 'explore with us'.",
    ]),

    p("What it cannot do (and will say so instead of guessing)", H2),
    *bullets([
        "<b>Private Studio numbers:</b> watch time, retention, click-through rate, impressions, traffic sources, revenue, audience age or gender. Only the channel owner sees those.",
        "<b>Search volume or trends:</b> a search result is a snapshot of what YouTube showed one time in one region, not a graph over time. The 'about 1,000,000 results' number is an estimate, not demand.",
        "<b>What is in the thumbnail:</b> we get the image address, not the pixels. Ask separately if you want a session to actually look at them.",
        "<b>Comments text:</b> we get the count, not the comments themselves (possible later, separate call).",
        "<b>Guaranteeing anything:</b> the report labels every statement as observed, inferred, or requires Studio. If the data is thin it writes 'Insufficient evidence'.",
    ]),

    p("Cost and limits", H2),
    *bullets([
        "Free. Google gives 10,000 units per day; one research run costs about 102 units, so roughly 95 runs a day.",
        "The key lives in a git-ignored file (.env) in the project folder and is never printed. Restrict it in Google Cloud to 'YouTube Data API v3' only, since it was pasted in chat once.",
        "Zero Blotato credits. Research and insights are the free half of the toolbox.",
    ]),

    p("Where it fits with the rest of the toolbox", H2),
    p("This is the research half of the youtubepro plugin, sitting next to the 12 skills in docs/skills-map.md. "
      "The snapshot feeds <b>competitors</b> (breakout videos) and <b>style-dna</b> (how those videos are built). "
      "The ported <b>insights</b>, <b>ideas</b>, <b>script</b> and <b>thumbnail</b> prompts are in the same folder, "
      "written and reviewed, but parked until the image and video generation work is done."),
    p("Files: .agents/skills/youtubepro/ (SKILL.md, scripts/yt_research.py, prompts/). Output: channels/&lt;name&gt;/research/&lt;topic&gt;/.", SMALL),
]

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.8 * inch,
                        bottomMargin=0.8 * inch, title="YouTube Research Tool: what we can do", author="youtube-money")
doc.build(story)
print(OUT)
