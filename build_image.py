#!/usr/bin/env python3
"""Paint a newspaper front page summing up Monday 23 November 2026.

The story list was researched from public reporting on the morning of
23 Nov 2026 (about 01:00 UTC): AFP wire, BBC, Reuters, AP, NPR, The
Hindu, Jagran Josh, Observer Voice. Every headline below is a paraphrase
of a story that happened or was first reported on 23 November 2026 in
some time zone; where an event itself is older, the page carries the
23 November development and says so in the date-check box. The drawing
code is original to this session. Output is deterministic: fixed palette,
fixed fonts, no clock and no randomness, so re-running the script writes
identical PNG bytes.
"""

from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 20
CONTENT = W - 2 * MARGIN  # 984

CREAM = (247, 243, 234)
PAPER_CARD = (255, 253, 247)
BLACK = (22, 22, 22)
GREY = (74, 74, 74)
PALE = (148, 140, 126)
RED = (172, 32, 28)
NAVY = (18, 32, 58)
BLUE = (28, 62, 112)
TAN = (232, 224, 205)
GOLD = (176, 128, 28)
GREEN = (46, 110, 58)
PURPLE = (110, 46, 96)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ------------------------------------------------------------------ news ---
# (tag, city, headline, one-line deck). All checked against reporting on
# the morning of 23 Nov 2026; see README.md for the source list.
TOP_STORY = (
    "CLIMATE",
    "Antalya, Turkey",
    "COP31 ends in failure - no deal",
    "After the longest climate summit on record, nearly 200 nations left "
    "Antalya with no final agreement: the last draft never once mentioned "
    "fossil fuels. On Monday, Australia's prime minister called the failure "
    "a sign of 'difficult geopolitical times'.",
)
SECOND_STORIES = [
    (
        "UNITED NATIONS",
        "Geneva",
        "Killer-robot talks extended two years",
        "Nations agreed to keep negotiating for two more years on autonomous "
        "weapons, falling short of binding rules on AI killer robots.",
    ),
    (
        "GULF",
        "Strait of Hormuz",
        "Tankers ablaze in the Strait of Hormuz",
        "Iran's navy says tankers breaking its rules were set ablaze in the "
        "strait, as the IRGC warned of unrest and the conflict spread to "
        "Saudi Arabia and Bahrain.",
    ),
]

# 24 further stories, three columns by eight rows.
MORE_STORIES = [
    ("UKRAINE", "Kyiv region", "14 missing after drone hits Kyiv building",
     "Zelenskiy said at least 14 people were missing after a Russian drone struck a residential building."),
    ("BALTIC", "Gulf of Finland", "Russian cargo ship still burning",
     "The vessel remained on fire off Finland days after the attack; the cause is under investigation."),
    ("MYANMAR", "Naypyidaw", "Myanmar calls ASEAN move 'unfair'",
     "The army-backed government called the ASEAN decision 'unfair and imbalanced'."),
    ("INDONESIA", "Serang", "Search goes on at the candy factory",
     "Rescuers kept pulling bodies from the Fonusa Agung Mulia plant as the search for dozens of missing workers entered a third day."),
    ("INDIA", "New Delhi", "Nepal's PM meets Modi in Delhi",
     "Balendra Shah held bilateral talks with Narendra Modi on his state visit, 22-23 November."),
    ("SOUTH KOREA", "Seoul", "Minister quits over AI cheating scandal",
     "South Korea's education minister resigned amid a scandal over AI-assisted exam cheating."),
    ("PORTUGAL", "Lisbon", "Thousands march over living costs",
     "Crowds filled Lisbon as anger over the cost of living spilled onto the streets."),
    ("PHILIPPINES", "Paranaque", "Manila leads Asia farm talks",
     "The Philippines opens a 23-26 November conference on modernising agriculture across Asia-Pacific."),
    ("CRICKET", "Wellington", "India post a record 720/9 declared",
     "India rewrote the record books at the Basin Reserve in the first Test against New Zealand."),
    ("MARKETS", "New York", "Anthropic options debut; Nasdaq slides",
     "Options on Anthropic shares began trading as the Nasdaq closed about 10% down for the week."),
    ("AVIATION", "United States", "FAA ground-stop chaos lingers",
     "Flight disruptions stretched into Monday after a rare nationwide ground stop."),
    ("TECH", "Worldwide", "Microsoft outage hits Outlook, Teams",
     "A widespread outage disrupted Outlook, Teams and other 365 services."),
    ("FILM", "North America", "'Sunrise on the Reaping' opens at No. 1",
     "The Hunger Games prequel took an estimated $120 million in its opening weekend."),
    ("TURKIYE", "Istanbul", "A lion on the loose",
     "A lion roaming free sparked fear among residents in Turkiye."),
    ("US POLITICS", "Washington", "Trump hits out at Schumer",
     "Trump criticised the Senate Democrat leader amid a push for new party leadership."),
    ("BRAZIL", "Brasilia", "Bolsonaro 'stable' in intensive care",
     "The former president remained in intensive care; doctors describe his condition as stable."),
    ("ISRAEL", "Herzliya", "Netanyahu-Eisenkot talks end with no deal",
     "Coalition talks between the two parties ended without an agreement on forming a government."),
    ("SOUTH SUDAN", "Juba", "24 civilians killed in fresh violence",
     "Fresh fighting in South Sudan killed 24 civilians, officials said."),
    ("NORTH KOREA", "Seoul", "Kim: we seek security, not supremacy",
     "North Korea's leader said the country seeks security rather than supremacy."),
    ("INDIA", "Arunachal", "Shah launches Rs 4,000cr Arunachal push",
     "The home minister unveiled a cooperative vision and infrastructure projects worth Rs 4,000 crore."),
    ("UNITED STATES", "California", "Nine hurt in concert mass shooting",
     "Nine people were hospitalised after a shooting at a private concert in central California."),
    ("AUSTRALIA", "Melbourne", "Molly Meldrum dies at 83",
     "The Countdown legend died at 5:30am in Melbourne; tributes poured in from across Australian music."),
    ("DIPLOMACY", "New Delhi", "India, Bulgaria talk ties and IMEC",
     "The two countries discussed bilateral ties, the IMEC corridor and the Black Sea situation."),
    ("VATICAN", "Vatican City", "Pope given socks from evacuees",
     "Pope Leo XIV received hand-knitted socks from a family evacuated from Russian-occupied Oleshky."),
]

# (time WIB, what happened) — times approximate.
DAY_CLOCK = [
    ("07:02", "UN extends killer-robot talks two more years"),
    ("08:00", "Kim: North Korea seeks security, not supremacy"),
    ("09:00", "Albanese calls COP31 failure 'difficult times'"),
    ("12:30", "India declares a record 720/9d in Wellington"),
    ("16:00", "Nepal's PM meets Modi in New Delhi"),
    ("19:00", "South Korea's minister quits over AI cheating"),
]

DAY_NUMBERS = [
    ("27", "verified stories"),
    ("14", "missing after Kyiv drone strike"),
    ("720/9d", "India's record Test total"),
    ("$120m", "'Sunrise' opens No. 1"),
    ("2 yrs", "more talks on killer robots"),
]

# Numbered dots on the sketch map: (x, y, number, label, label side).
# Label side "r" puts the name right of the dot, "l" left, "b" below,
# "a" above.
MAP_DOTS = [
    (318, 52, "1", "Lisbon", "b"),
    (398, 26, "2", "Kyiv", "a"),
    (436, 56, "3", "Antalya", "r"),
    (505, 46, "4", "New Delhi", "r"),
    (558, 26, "5", "Seoul", "r"),
    (572, 68, "6", "Wellington", "l"),
]

NOT_TODAY = [
    "COP31's collapse happened late Sunday 22 Nov - Monday's news is the fallout: reactions, blame, and what happens next.",
    "'El Chapo Isidro' was captured on 20 Nov - last week's news, not today's.",
    "The Anthropic IPO was 19 Nov; only Monday's options debut is on the page.",
    "The Serang factory fire broke out on Saturday 21 Nov - the page carries Monday's search, not the fire itself.",
]


# -------------------------------------------------------------- utilities ---
class Pen:
    """Font cache and text measuring for one drawing context."""

    def __init__(self, draw: ImageDraw.ImageDraw):
        self.draw = draw
        self._fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

    def font(self, path: str, size: int) -> ImageFont.FreeTypeFont:
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(path, size)
        return self._fonts[key]

    def measure(self, text: str, path: str, size: int) -> float:
        return self.draw.textlength(text, font=self.font(path, size))

    def lines(self, text: str, path: str, size: int, width: int) -> list[str]:
        out: list[str] = []
        current = ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if self.measure(trial, path, size) <= width or not current:
                current = trial
            else:
                out.append(current)
                current = word
        if current:
            out.append(current)
        return out

    def one_line(self, text: str, path: str, size: int, width: int) -> str:
        if self.measure(text, path, size) <= width:
            return text
        cut = text
        while cut and self.measure(cut + "...", path, size) > width:
            cut = cut[:-1].rstrip()
        return cut + "..."


def rule(draw: ImageDraw.ImageDraw, x0: int, y: int, x1: int,
         thick: int = 2, colour=BLACK) -> None:
    draw.line([(x0, y), (x1, y)], fill=colour, width=thick)


class Page:
    """Lays out the front page band by band, top to bottom."""

    def __init__(self) -> None:
        self.img = Image.new("RGB", (W, H), CREAM)
        self.d = ImageDraw.Draw(self.img)
        self.p = Pen(self.d)

    # -- masthead ---------------------------------------------------
    def masthead(self) -> int:
        d, p = self.d, self.p
        # Dark navy band with the paper's name.
        d.rectangle([0, 0, W, 34], fill=NAVY)
        d.text((MARGIN, 8), "THE WORLD IN ONE IMAGE  |  ONE DAY, EVERYWHERE  |  No. 327",
               font=p.font(SANS_B, 12), fill=CREAM)
        right = "MONDAY EDITION"
        d.text((W - MARGIN - p.measure(right, SANS_B, 12), 8), right,
               font=p.font(SANS_B, 12), fill=(232, 200, 120))
        d.text((MARGIN, 42), "Monday 23 November 2026",
               font=p.font(SERIF_B, 48), fill=BLACK)
        deck = ("Twenty-seven verified stories from Monday - a climate summit ends "
                "in failure, the robots wait for rules, and a record falls in Wellington.")
        for i, line in enumerate(p.lines(deck, SANS, 13, CONTENT)):
            d.text((MARGIN, 104 + i * 17), line, font=p.font(SANS, 13), fill=GREY)
        rule(d, MARGIN, 140, W - MARGIN, 3)
        return 150

    # -- numbers strip ----------------------------------------------
    def numbers(self, y: int) -> int:
        d, p = self.d, self.p
        cell = CONTENT // len(DAY_NUMBERS)
        for i, (big, small) in enumerate(DAY_NUMBERS):
            x = MARGIN + i * cell
            d.rectangle([x + 2, y, x + cell - 2, y + 40], fill=PAPER_CARD,
                        outline=PALE)
            d.text((x + 10, y + 5), big, font=p.font(SERIF_B, 17),
                   fill=RED if i % 2 == 0 else BLUE)
            d.text((x + 10, y + 24), small, font=p.font(SANS, 10), fill=GREY)
        return y + 48

    # -- top stories -------------------------------------------------
    def top_stories(self, y: int) -> int:
        d, p = self.d, self.p
        left_w = 640
        right_w = CONTENT - left_w - 12
        rx = MARGIN + left_w + 12

        tag, city, head, deck = TOP_STORY
        d.rectangle([MARGIN, y, MARGIN + left_w, y + 116], fill=PAPER_CARD,
                    outline=BLACK)
        d.rectangle([MARGIN, y, MARGIN + 8, y + 116], fill=RED)
        d.text((MARGIN + 18, y + 8), f"{tag}  -  {city.upper()}",
               font=p.font(SANS_B, 11), fill=RED)
        d.text((MARGIN + 18, y + 26), head, font=p.font(SERIF_B, 24),
               fill=BLACK)
        for i, line in enumerate(p.lines(deck, SANS, 12, left_w - 36)):
            d.text((MARGIN + 18, y + 60 + i * 16), line,
                   font=p.font(SANS, 12), fill=GREY)
        # Red "NO DEAL" stamp, tilted, straddling the lead card's top-right
        # corner so it never covers the headline or the deck.
        stamp = Image.new("RGBA", (130, 38), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        sd.rectangle([3, 3, 126, 34], outline=RED, width=4)
        sd.text((65, 8), "NO DEAL", font=p.font(SANS_B, 19), fill=RED,
                anchor="ma")
        stamp = stamp.rotate(12, expand=True, resample=Image.BICUBIC)
        self.img.paste(stamp, (MARGIN + left_w - 132, y - 12), stamp)

        for slot, (tag, city, head, deck) in enumerate(SECOND_STORIES):
            sy = y + slot * 59
            d.rectangle([rx, sy, rx + right_w, sy + 57], fill=PAPER_CARD,
                        outline=PALE)
            d.rectangle([rx, sy, rx + 6, sy + 57],
                        fill=BLUE if slot == 0 else RED)
            d.text((rx + 14, sy + 4), f"{tag}  -  {city.upper()}",
                   font=p.font(SANS_B, 9), fill=BLUE)
            head_fit = p.one_line(head, SERIF_B, 13, right_w - 28)
            d.text((rx + 14, sy + 16), head_fit, font=p.font(SERIF_B, 13),
                   fill=BLACK)
            for j, line in enumerate(p.lines(deck, SANS, 9, right_w - 28)[:2]):
                d.text((rx + 14, sy + 35 + j * 11), line,
                       font=p.font(SANS, 9), fill=GREY)
        return y + 116

    # -- timeline ----------------------------------------------------
    def clock(self, y: int) -> int:
        d, p = self.d, self.p
        d.text((MARGIN, y), "THE DAY, AS IT UNFOLDED  (WIB, approximate)",
               font=p.font(SANS_B, 11), fill=BLACK)
        axis = y + 38
        rule(d, MARGIN, axis, W - MARGIN, 2, PALE)
        slot = CONTENT // len(DAY_CLOCK)
        for i, (when, what) in enumerate(DAY_CLOCK):
            cx = MARGIN + i * slot + slot // 2
            d.ellipse([cx - 5, axis - 5, cx + 5, axis + 5], fill=RED,
                      outline=CREAM)
            d.text((cx - p.measure(when, SANS_B, 11) / 2, axis - 20), when,
                   font=p.font(SANS_B, 11), fill=BLACK)
            for j, line in enumerate(p.lines(what, SANS, 9, slot - 12)[:2]):
                d.text((cx - slot // 2 + 6, axis + 10 + j * 12), line,
                       font=p.font(SANS, 9), fill=GREY)
        return y + 76

    # -- story grid --------------------------------------------------
    def grid(self, y: int) -> int:
        d, p = self.d, self.p
        cols = 3
        gap = 10
        card_w = (CONTENT - gap * (cols - 1)) // cols
        row_h = 44
        palette = [RED, BLUE, GOLD, GREEN, PURPLE, (150, 90, 20)]
        for i, (tag, city, head, deck) in enumerate(MORE_STORIES):
            row, col = divmod(i, cols)
            x = MARGIN + col * (card_w + gap)
            cy = y + row * (row_h + 3)
            d.rectangle([x, cy, x + card_w, cy + row_h], fill=PAPER_CARD,
                        outline=PALE)
            d.rectangle([x, cy, x + 4, cy + row_h],
                        fill=palette[i % len(palette)])
            title = p.one_line(head, SANS_B, 11, card_w - 16)
            d.text((x + 12, cy + 4), title, font=p.font(SANS_B, 11), fill=BLACK)
            body = f"{tag} - {city} - {deck}"
            for j, line in enumerate(p.lines(body, SANS, 9, card_w - 16)[:2]):
                d.text((x + 12, cy + 19 + j * 11), line,
                       font=p.font(SANS, 9), fill=GREY)
        rows = (len(MORE_STORIES) + cols - 1) // cols
        return y + rows * (row_h + 3) - 3

    # -- sketch map + one-line verdict -------------------------------
    def map_verdict(self, y: int) -> int:
        d, p = self.d, self.p
        map_w = 620
        map_h = 88
        d.rectangle([MARGIN, y, MARGIN + map_w, y + map_h], fill=PAPER_CARD,
                    outline=BLACK)
        d.text((MARGIN + 10, y + 6), "WHERE IT HAPPENED - SCHEMATIC, NOT TO SCALE",
               font=p.font(SANS_B, 10), fill=BLUE)
        for (bx, by, bw, bh) in [(28, 18, 120, 42), (150, 48, 90, 24),
                                 (300, 10, 130, 30), (330, 46, 80, 26),
                                 (440, 14, 130, 40), (560, 54, 44, 20)]:
            d.ellipse([MARGIN + bx, y + by, MARGIN + bx + bw, y + by + bh],
                      fill=TAN, outline=PALE)
        for (px, py, num, label, side) in MAP_DOTS:
            d.ellipse([MARGIN + px - 8, y + py - 8, MARGIN + px + 8, y + py + 8],
                      fill=RED, outline=CREAM)
            d.text((MARGIN + px - 3, y + py - 6), num,
                   font=p.font(SANS_B, 10), fill=(255, 255, 255))
            if not label:
                continue
            lw = p.measure(label, SANS_B, 9)
            if side == "r":
                lx, ly = MARGIN + px + 11, y + py - 5
            elif side == "l":
                lx, ly = MARGIN + px - 11 - lw, y + py - 5
            elif side == "a":
                lx, ly = MARGIN + px - lw / 2, y + py - 20
            else:
                lx, ly = MARGIN + px - lw / 2, y + py + 10
            d.text((lx, ly), label, font=p.font(SANS_B, 9), fill=BLACK)
        key = ("1 Lisbon  2 Kyiv  3 Antalya  4 New Delhi  5 Seoul  "
               "6 Wellington")
        d.text((MARGIN + 10, y + map_h - 14), key,
               font=p.font(SANS, 9), fill=GREY)

        vx = MARGIN + map_w + 12
        vw = CONTENT - map_w - 12
        d.rectangle([vx, y, vx + vw, y + map_h], fill=BLACK)
        d.text((vx + 12, y + 8), "THE DAY IN ONE LINE",
               font=p.font(SANS_B, 10), fill=(232, 200, 120))
        verdict = ("The climate talks failed, the robots wait, and the world "
                   "kept moving - one Monday, every continent.")
        for i, line in enumerate(p.lines(verdict, SERIF, 12, vw - 24)):
            d.text((vx + 12, y + 26 + i * 16), line,
                   font=p.font(SERIF, 12), fill=CREAM)
        d.text((vx + 12, y + map_h - 18),
               "Watch tomorrow: COP31 fallout, the Wellington Test, Wall St open.",
               font=p.font(SANS, 9), fill=(200, 200, 200))
        return y + map_h + 10

    # -- date check + footer -----------------------------------------
    def date_check(self, y: int) -> int:
        d, p = self.d, self.p
        d.rectangle([MARGIN, y, W - MARGIN, y + 50], fill=TAN, outline=PALE)
        d.text((MARGIN + 10, y + 6), "DATE CHECK - LEFT OFF ON PURPOSE",
               font=p.font(SANS_B, 10), fill=RED)
        for i, item in enumerate(NOT_TODAY):
            d.text((MARGIN + 10, y + 20 + i * 10), "- " + item,
                   font=p.font(SANS, 9), fill=GREY)
        return y + 58

    def footer(self, y: int) -> None:
        d, p = self.d, self.p
        rule(d, MARGIN, y, W - MARGIN, 2)
        foot = ("Sources, 23 Nov 2026 ~01:00 UTC: AFP, BBC, Reuters, AP, NPR, "
                "The Hindu, Jagran Josh. 27 stories. One image, one day.")
        d.text((MARGIN, y + 6), foot, font=p.font(SANS, 9), fill=GREY)

    def render(self) -> Image.Image:
        y = self.masthead()
        y = self.numbers(y)
        y = self.top_stories(y + 8)
        y = self.clock(y + 8)
        y = self.grid(y + 8)
        y = self.map_verdict(y + 8)
        y = self.date_check(y)
        self.footer(y)
        return self.img


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    sheet = Page().render()
    sheet.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
