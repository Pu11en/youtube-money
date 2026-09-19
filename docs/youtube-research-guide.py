"""Builds docs/youtube-research-guide.pdf: one-page cheat sheet for the research tool."""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube-research-guide.pdf")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=20, leading=24, spaceAfter=2, alignment=TA_LEFT)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, leading=15, spaceBefore=9, spaceAfter=3,
                    textColor=colors.HexColor("#1f2937"))
P = ParagraphStyle("P", parent=ss["Normal"], fontSize=10, leading=13, spaceAfter=2)
SMALL = ParagraphStyle("S", parent=P, fontSize=8.5, textColor=colors.HexColor("#4b5563"))
B = ParagraphStyle("B", parent=P, leftIndent=12, bulletIndent=1, spaceAfter=1)
CELL = ParagraphStyle("Cell", parent=P, fontSize=9.5, leading=12, spaceAfter=0)
CELLB = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold")


def table(rows, widths):
    data = [[Paragraph(c, CELLB if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return t


def bullets(items):
    return [Paragraph(i, B, bulletText="•") for i in items]


W = 6.9 * inch
story = [
    Paragraph("YouTube Research: cheat sheet", H1),
    Paragraph("Type <b>research &lt;topic&gt;</b> in Discord. Free. No Blotato credits. Public numbers only.", P),

    Paragraph("Say this", H2),
    table([
        ["You say", "You get"],
        ["research true crime shorts", "25 videos + a scorecard"],
        ["research true crime, most viewed, this year, under 4 min", "same, filtered"],
        ["find outliers in true crime", "small channels that blew up"],
        ["insights", "a plain report: what's true, what's a guess, what needs Studio"],
    ], [3.3 * inch, W - 3.3 * inch]),
    Paragraph("Filters: most relevant / newest / most viewed &nbsp;·&nbsp; today / week / month / year &nbsp;·&nbsp; "
              "under 4 min / 4-20 / over 20 &nbsp;·&nbsp; 1-50 videos", SMALL),

    Paragraph("You get, per video", H2),
    *bullets(["Views, likes, comments, length, date, tags, captions, language",
              "Channel: subscribers, total views, video count, country, age"]),

    Paragraph("The scorecard", H2),
    table([
        ["Number", "Means"],
        ["Median views", "what a normal video does here (ignore the average)"],
        ["Views per day", "views adjusted for age: new video with 500k beats old one with 2M"],
        ["Reach vs subs", "views / subscribers. 595x = tiny channel went huge. <b>The outlier finder.</b>"],
        ["Interaction rate", "(likes + comments) / views. Did people care?"],
        ["Length mix", "Shorts niche or long-form niche?"],
        ["Recency mix", "is the niche still alive?"],
        ["Recurring tags", "the niche's vocabulary"],
        ["Channel concentration", "does one creator own it?"],
    ], [1.6 * inch, W - 1.6 * inch]),

    Paragraph("Example: true crime shorts, 10 videos", H2),
    *bullets(["Typical video 1.7M views; biggest 9.8M",
              "4 Shorts, 5 long docs: filter by length next time",
              "9 of 10 over a year old",
              "One video at 595x its channel size: a breakout",
              "No single channel dominates"]),

    Paragraph("Can't do", H2),
    *bullets(["Watch time, CTR, retention, revenue, demographics (owner-only Studio data)",
              "Search volume or trends (it's one snapshot)",
              "See the thumbnail picture or read comments"]),

    Paragraph("Limits", H2),
    *bullets(["About 95 runs a day, free", "Key is in .env, never pushed to GitHub"]),
    Spacer(1, 4),
    Paragraph("Files: .agents/skills/youtubepro/ &nbsp;·&nbsp; Output: channels/&lt;name&gt;/research/&lt;topic&gt;/ "
              "&nbsp;·&nbsp; ideas/script/thumbnail are written but parked until generation work is done.", SMALL),
]

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch,
                        bottomMargin=0.6 * inch, title="YouTube Research: cheat sheet", author="youtube-money")
doc.build(story)
print(OUT)
