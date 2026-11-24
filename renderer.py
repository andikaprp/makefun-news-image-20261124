#!/usr/bin/env python3
"""Fresh renderer for news-image-20261124 candidate-v2.
Design base: Gemini-experiment composition (broadsheet masthead, single
hero lead + stat strip, chart furniture, 3-col middle, briefs strip),
plus a code-drawn pictorial panel on every headlined card.
All copy from data.json (census stories-final.json). Renders at 2x,
downscales to 1024x1024."""
import json, os, random
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample
W = 1024 * S
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data.json")))

FD = "/usr/share/fonts/truetype/"
SERIF_B = FD + "liberation/LiberationSerif-Bold.ttf"
SERIF = FD + "liberation/LiberationSerif-Regular.ttf"
SANS_B = FD + "dejavu/DejaVuSans-Bold.ttf"
SANS = FD + "dejavu/DejaVuSans.ttf"

CREAM = (250, 246, 236)
PAPER = (253, 250, 242)
INK = (26, 26, 24)
NAVY = (13, 27, 46)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
TEAL = (14, 110, 110)
GREEN = (22, 120, 60)
GREY = (90, 88, 80)
RULE = (60, 58, 50)

def F(path, px):
    return ImageFont.truetype(path, int(px * S))

def tw(d, txt, font):
    return d.textlength(txt, font=font)

def fit(d, txt, path, start, lo, maxw):
    px = start
    while px > lo and tw(d, txt, F(path, px)) > maxw:
        px -= 0.5
    return px

def wrap(d, txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fit_wrap(d, txt, path, start, lo, maxw, maxlines):
    px = start
    while px > lo:
        lines = wrap(d, txt, F(path, px), maxw)
        if len(lines) <= maxlines:
            return px, lines
        px -= 0.5
    return px, wrap(d, txt, F(path, px), maxw)

# ---------- art panels: one unified flat-scene style ----------
PALETTES = {
    "court":     ((38, 52, 84), (214, 186, 130), (178, 34, 34)),
    "satellite": ((16, 28, 58), (120, 170, 230), (240, 200, 60)),
    "chip":      ((20, 60, 66), (90, 200, 180), (240, 200, 60)),
    "table":     ((52, 44, 84), (170, 160, 220), (220, 90, 70)),
    "ship":      ((24, 62, 96), (140, 190, 225), (220, 90, 70)),
    "plane":     ((40, 90, 140), (200, 225, 245), (240, 200, 60)),
    "shield":    ((70, 40, 40), (225, 170, 120), (240, 200, 60)),
    "file":      ((60, 56, 44), (225, 205, 150), (178, 34, 34)),
    "awacs":     ((48, 70, 100), (190, 205, 225), (220, 90, 70)),
    "desert":    ((120, 84, 44), (235, 200, 140), (178, 34, 34)),
    "virus":     ((66, 30, 60), (220, 140, 200), (240, 200, 60)),
    "jet":       ((36, 60, 90), (170, 200, 230), (220, 90, 70)),
    "jets":      ((30, 70, 110), (180, 215, 240), (240, 200, 60)),
    "wheat":     ((80, 90, 30), (230, 205, 110), (220, 120, 60)),
}

def panel(scene, label, w, h, seed):
    """Render one scene into its own panel-sized image (art containment)."""
    pw, ph = int(w * S), int(h * S)
    top, mid, acc = PALETTES[scene]
    img = Image.new("RGB", (pw, ph), top)
    d = ImageDraw.Draw(img, "RGBA")
    # vertical gradient top -> mid blend
    for i in range(ph):
        t = i / max(ph - 1, 1)
        c = tuple(int(top[k] + (mid[k] - top[k]) * t * 0.55) for k in range(3))
        d.line([(0, i), (pw, i)], fill=c)
    rng = random.Random(seed)
    # grain for colour richness
    for _ in range(pw * ph // 90):
        x, y = rng.randrange(pw), rng.randrange(ph)
        v = rng.randrange(-26, 27)
        base = img.getpixel((x, y))
        img.putpixel((x, y), tuple(max(0, min(255, base[k] + v)) for k in range(3)))
    d = ImageDraw.Draw(img, "RGBA")
    u = pw / 100.0  # unit
    v = ph / 100.0
    def R(x0, y0, x1, y1, fill, **kw): d.rectangle([x0*u, y0*v, x1*u, y1*v], fill=fill, **kw)
    def E(x0, y0, x1, y1, fill, **kw): d.ellipse([x0*u, y0*v, x1*u, y1*v], fill=fill, **kw)
    def P(pts, fill, **kw): d.polygon([(x*u, y*v) for x, y in pts], fill=fill, **kw)
    def L(pts, fill, wd=2): d.line([(x*u, y*v) for x, y in pts], fill=fill, width=max(1, int(wd*u/2)))
    dark = (18, 20, 26, 235); light = (245, 242, 230, 255)
    if scene == "court":  # Peace-Palace-like columns + pediment + split verdict bar
        P([(8, 30), (50, 8), (92, 30)], light)
        R(10, 32, 90, 38, light)
        for x in (14, 30, 46, 62, 78): R(x, 40, x + 7, 78, light)
        R(8, 80, 92, 86, light)
        R(8, 88, 54, 97, acc + (255,)); R(54, 88, 92, 97, dark)
    elif scene == "satellite":
        for _ in range(26): E(rng.uniform(2, 97), rng.uniform(2, 60), 0, 0, light) if False else d.point((rng.uniform(0, pw), rng.uniform(0, ph*0.6)), fill=(255, 255, 255))
        P([(6, 88), (94, 88), (94, 100), (6, 100)], (30, 70, 140, 255))
        d.arc([10*u, 55*v, 90*u, 105*v], 180, 330, fill=acc + (255,), width=max(2, int(2*u)))
        R(42, 34, 58, 52, light); R(20, 38, 40, 50, acc + (255,)); R(60, 38, 80, 50, acc + (255,))
        L([(50, 52), (50, 66)], light, 3); E(46, 64, 54, 74, acc + (255,))
    elif scene == "chip":
        R(30, 18, 70, 66, dark)
        for x in (36, 46, 56): R(x, 6, x + 4, 18, light); R(x, 66, x + 4, 78, light)
        for y in (28, 42, 56): R(18, y, 30, y + 4, light); R(70, y, 82, y + 4, light)
        R(42, 32, 58, 52, acc + (255,))
        P([(14, 96), (30, 82), (46, 96), (62, 82), (78, 96), (94, 82)], acc + (255,))
    elif scene == "table":  # four flags / seats around a table
        R(18, 52, 82, 62, light)
        for i, c in enumerate([(60, 110, 200), (220, 190, 60), (200, 60, 60), (240, 240, 240)]):
            x = 20 + i * 17
            R(x, 22, x + 3, 52, light); P([(x + 3, 22), (x + 15, 26), (x + 3, 31)], c + (255,))
            E(x - 1, 66, x + 6, 76, dark)
    elif scene == "ship":  # warship + drone
        P([(10, 74), (86, 74), (78, 88), (20, 88)], dark)
        R(34, 60, 58, 74, dark); R(44, 48, 50, 60, dark); L([(50, 48), (66, 40)], dark, 3)
        for x in (16, 30, 56, 70): E(x, 78, x + 3, 82, light)
        L([(74, 14), (84, 22)], acc + (255,), 3); L([(84, 14), (74, 22)], acc + (255,), 3)
        E(80, 26, 86, 32, acc + (255,))
        for i in range(4): d.arc([(4+i*24)*u, 88*v, (22+i*24)*u, 100*v], 0, 180, fill=light, width=max(1, int(u)))
    elif scene == "plane":
        for cx, cy, s in ((18, 24, 16), (62, 14, 20), (84, 34, 12)):
            E(cx - s/2, cy - 4, cx + s/2, cy + 4, (255, 255, 255, 200))
        P([(12, 62), (46, 52), (88, 58), (46, 60)], light)
        P([(46, 52), (56, 36), (64, 36), (58, 54)], acc + (255,))
        P([(30, 60), (20, 72), (28, 72), (38, 62)], dark)
        L([(14, 84), (88, 84)], light, 2)
    elif scene == "shield":
        P([(50, 8), (82, 18), (82, 52), (50, 92), (18, 52), (18, 18)], dark)
        P([(50, 16), (74, 24), (74, 50), (50, 82), (26, 50), (26, 24)], acc + (200,))
        for i in range(3): E(38 + i * 10, 40, 44 + i * 10, 48, light)
    elif scene == "file":  # stamped secret files
        R(20, 14, 62, 84, light); R(30, 24, 84, 94, (235, 225, 195, 255))
        for i in range(4): L([(38, 36 + i * 10), (74, 36 + i * 10)], dark, 2)
        # SECRET stamp centred on the front file: whole word on the paper
        sf = F(SANS_B, 6.5)
        sw = tw(d, "SECRET", sf)
        assert sw <= 52 * u, "SECRET stamp wider than front file"
        d.text((57 * u - sw / 2, 58 * v), "SECRET", font=sf, fill=acc + (255,))
        R(14, 88, 86, 92, acc + (255,))
    elif scene == "awacs":  # radar dome plane + inbound trails
        E(38, 26, 62, 38, light)
        P([(10, 62), (44, 54), (90, 60), (44, 64)], light)
        P([(44, 54), (52, 42), (58, 42), (52, 56)], dark)
        for i, yy in enumerate((16, 30, 44)):
            L([(4, yy), (30 - i * 6, yy + 8)], acc + (255,), 3); E(30 - i * 6, yy + 6, 35 - i * 6, yy + 11, acc + (255,))
    elif scene == "desert":  # coaches on a road, strike flash
        R(0, 78, 100, 100, (90, 62, 34, 255))
        for x0 in (8, 52):
            R(x0, 56, x0 + 30, 74, light); R(x0 + 3, 60, x0 + 12, 68, dark); R(x0 + 15, 60, x0 + 27, 68, dark)
            E(x0 + 5, 72, x0 + 11, 79, dark); E(x0 + 20, 72, x0 + 26, 79, dark)
        P([(84, 8), (88, 22), (96, 18), (90, 28), (98, 30), (88, 36), (86, 26), (78, 30)], acc + (255,))
    elif scene == "virus":
        for cx, cy, r in ((34, 44, 15), (62, 34, 11), (56, 62, 13), (78, 58, 8)):
            E(cx - r, cy - r, cx + r, cy + r, acc + (230,))
            for a in range(0, 360, 45):
                import math
                x2, y2 = cx + (r + 6) * math.cos(a * 3.14159 / 180), cy + (r + 6) * math.sin(a * 3.14159 / 180)
                L([(cx, cy), (x2, y2)], acc + (255,), 2); E(x2 - 2, y2 - 2, x2 + 2, y2 + 2, light)
    elif scene in ("jet", "jets"):
        P([(8, 58), (42, 48), (92, 54), (42, 60)], light)
        P([(42, 48), (52, 34), (60, 34), (52, 50)], acc + (255,))
        if scene == "jets":
            P([(20, 30), (44, 24), (70, 28), (44, 32)], (220, 230, 240, 255))
            L([(10, 78), (40, 70)], acc + (255,), 3); L([(16, 86), (52, 74)], light, 2)
        else:
            E(70, 70, 92, 88, (255, 255, 255, 0)); d.arc([66*u, 64*v, 96*u, 94*v], 180, 300, fill=acc + (255,), width=max(2, int(2*u)))
    elif scene == "wheat":  # wheat stalks + blocked route sign
        for x in (18, 32, 46, 60, 74):
            L([(x, 96), (x, 40)], acc + (255,), 3)
            for i in range(4): E(x - 5, 34 + i * 8, x, 42 + i * 8, acc + (255,)); E(x, 34 + i * 8, x + 5, 42 + i * 8, acc + (255,))
        E(76, 10, 96, 30, (200, 40, 40, 255)); L([(80, 26), (92, 14)], light, 4)
    # figure chip: dark pill, bottom-left
    cpx = 13.0
    while cpx > 7 and tw(d, label, F(SANS_B, cpx)) + 14 * S > pw - 6 * S:
        cpx -= 0.5
    fnt = F(SANS_B, cpx)
    cw = tw(d, label, fnt) + 14 * S
    d.rounded_rectangle([4*S, ph - 24*S, 4*S + cw, ph - 5*S], radius=4*S, fill=(12, 12, 14, 235))
    d.text((11*S, ph - 5*S - (cpx * S) * 1.35), label, font=fnt, fill=(255, 255, 255))
    return img

# ---------- page assembly ----------
def build():
    img = Image.new("RGB", (W, W), CREAM)
    d = ImageDraw.Draw(img)
    X = lambda v: v * S
    report = {"brief_min_px": 99, "headline_min_px": 99}

    def kicker(x, y, txt, color=RED, px=11):
        d.text((X(x), X(y)), txt, font=F(SANS_B, px), fill=color)

    # MASTHEAD (Gemini broadsheet band)
    d.rectangle([0, 0, W, X(134)], fill=NAVY)
    d.text((X(16), X(4)), "THE WORLD IN ONE PAGE · VERIFIED TUESDAY EDITION", font=F(SANS_B, 11.5), fill=GOLD)
    src = "SOURCES: DAILY SUMMARY OF · HORIZON · REUTERS · AL JAZEERA"
    d.text((W - X(16) - tw(d, src, F(SANS_B, 11.5)), X(4)), src, font=F(SANS_B, 11.5), fill=(200, 205, 215))
    # TUESDAY strengthened: ~50% larger (19 -> 28px), full-contrast white
    tue = "T U E S D A Y"
    d.text((X(16), X(16)), tue, font=F(SANS_B, 28), fill=(255, 255, 255))
    date_px = fit(d, "24 NOVEMBER 2026", SERIF_B, 100, 80, 976 * S)
    report["date_px"] = date_px
    # date raised so glyph bottoms (y + ~91 at 100px) clear the gold rule
    d.text((X(14), X(35)), "24 NOVEMBER 2026", font=F(SERIF_B, date_px), fill=(255, 255, 255))
    report["date_bottom"] = 35 + 91  # ~126, gold rule at 134: 8px clearance
    assert report["date_bottom"] <= 130
    d.rectangle([0, X(134), W, X(138)], fill=GOLD)

    def card_box(x, y, w, h):
        d.rectangle([X(x), X(y), X(x + w), X(y + h)], fill=PAPER, outline=RULE, width=S)

    def paste_panel(scene, label, x, y, w, h, seed):
        p = panel(scene, label, w, h, seed)
        img.paste(p, (int(X(x)), int(X(y))))

    # HERO (rank 1) + hero2 (rank 2)
    hz = DATA["hero"]; h2 = DATA["hero2"]
    card_box(16, 144, 596, 226)
    paste_panel(hz["scene"], hz["label"], 17, 145, 594, 88, 11)
    kicker(28, 238, f"{hz['n']}. {hz['place']} · {hz['tag']} · {hz['source']}")
    px, lines = fit_wrap(d, hz["headline"], SERIF_B, 36, 30, 572 * S, 2)
    report["hero_px"] = px
    yy = 249
    for ln in lines:
        d.text((X(28), X(yy)), ln, font=F(SERIF_B, px), fill=INK); yy += px * 1.12
    d.text((X(28), X(yy + 2)), hz["sub"], font=F(SANS, 14.5), fill=GREY)
    sy = yy + 24
    assert sy + 16 <= 370, f"hero overflow {sy}"
    d.line([X(28), X(sy), X(600), X(sy)], fill=RULE, width=S)
    sx = 28
    for val, lab in hz["stats"]:
        d.text((X(sx), X(sy + 3)), val, font=F(SERIF_B, 15), fill=RED)
        wv = tw(d, val, F(SERIF_B, 15))
        d.text((X(sx) + wv + X(7), X(sy + 6)), lab, font=F(SANS_B, 10.5), fill=INK)
        sx += (wv + tw(d, lab, F(SANS_B, 10.5))) / S + 26

    card_box(620, 144, 388, 226)
    paste_panel(h2["scene"], h2["label"], 621, 145, 386, 96, 22)
    kicker(632, 248, f"{h2['n']}. {h2['place']} · {h2['tag']} · TAGESSPIEGEL")
    px2, lines2 = fit_wrap(d, h2["headline"], SERIF_B, 26, 22, 364 * S, 2)
    report["hero2_px"] = px2
    yy = 266
    for ln in lines2:
        d.text((X(632), X(yy)), ln, font=F(SERIF_B, px2), fill=INK); yy += px2 * 1.12
    for ln in wrap(d, h2["sub"], F(SANS, 13.5), 364 * S)[:2]:
        d.text((X(632), X(yy + 2)), ln, font=F(SANS, 13.5), fill=GREY); yy += 17
    assert yy <= 368, f"hero2 overflow {yy}"

    # CHART CARD (rank 3): kicker runs the full card width ABOVE the panel
    # (nothing runs under the panel); text left, small-multiples panel right
    cc = DATA["chartcard"]
    card_box(16, 376, 992, 96)
    kick3 = f"{cc['n']}. {cc['place']} · {cc['tag']} · {cc['source']}"
    assert tw(d, kick3, F(SANS_B, 11)) <= 960 * S, "chart kicker too wide"
    kicker(28, 383, kick3)
    px3, lines3 = fit_wrap(d, cc["headline"], SERIF_B, 24, 20, 316 * S, 3)
    yy = 402
    for ln in lines3:
        d.text((X(28), X(yy)), ln, font=F(SERIF_B, px3), fill=INK); yy += px3 * 1.12
    for ln in wrap(d, cc["sub"], F(SANS, 12), 316 * S)[:2]:
        d.text((X(28), X(yy + 1)), ln, font=F(SANS, 12), fill=GREY); yy += 15
    assert yy <= 472, f"chart text overflow {yy}"
    # multiples panel 648x70 at x=352,y=398 (below the kicker line)
    px0, py0, pw, ph = 352, 398, 648, 70
    d.rectangle([X(px0), X(py0), X(px0 + pw), X(py0 + ph)], fill=(244, 238, 222), outline=RULE, width=S)
    d.text((X(px0 + 10), X(py0 + 4)), "ASIA CLOSES · TUESDAY · ONE SCALE", font=F(SANS_B, 10.5), fill=INK)
    maxv = 7.03
    for i, (name, val, lvl) in enumerate(cc["asia"]):
        ry = py0 + 20 + i * 17
        d.text((X(px0 + 10), X(ry)), name, font=F(SANS_B, 11.5), fill=INK)
        bx = px0 + 128; bw = (val / maxv) * 260  # capped ~65%: labels keep right padding
        d.rectangle([X(bx), X(ry + 1), X(bx + bw), X(ry + 12)], fill=GREEN)
        lab3 = f"+{val:.2f}%  ·  {lvl}"
        lx = bx + bw + 8
        assert lx + tw(d, lab3, F(SANS_B, 12)) / S <= px0 + pw - 10, f"chart label clip: {lab3}"
        d.text((X(lx), X(ry)), lab3, font=F(SANS_B, 12), fill=INK)

    # DIVERGING MARKETS STRIP
    dy = 478
    d.text((X(16), X(dy + 2)), "DAY IN MARKETS — DIVERGING", font=F(SANS_B, 11), fill=INK)
    items = DATA["diverging"]; cellw = 992 / len(items); maxabs = 12.0
    for i, (name, val) in enumerate(items):
        cx = 16 + i * cellw + cellw / 2
        col = GREEN if val >= 0 else RED
        lab = f"{name} {val:+.2f}%"
        fnt = F(SANS_B, 11.5)
        d.text((X(cx) - tw(d, lab, fnt) / 2, X(dy + 14)), lab, font=fnt, fill=col)
        half = (abs(val) / maxabs) * (cellw / 2 - 6)
        if val >= 0:
            d.rectangle([X(cx), X(dy + 28), X(cx + half), X(dy + 34)], fill=col)
        else:
            d.rectangle([X(cx - half), X(dy + 28), X(cx), X(dy + 34)], fill=col)
    d.line([X(16), X(dy + 38), X(1008), X(dy + 38)], fill=RULE, width=S)

    # MIDDLE EDITION GRID: 12 compacts, 4 cols x 3 rows
    gy = 524
    d.text((X(16), X(gy)), "THE MIDDLE EDITION · WIRE RANKS 4–12 · 14–16", font=F(SANS_B, 11.5), fill=INK)
    leg = "TAGS: CONFIRMED = WIRE DATA · OFFICIAL = GOVT BODY · REPORTED = SINGLE-SOURCE"
    d.text((W - X(16) - tw(d, leg, F(SANS_B, 9.5)), X(gy + 1)), leg, font=F(SANS_B, 9.5), fill=GREY)
    gy += 18
    cw, chh, gap = 243, 90, 6
    for idx, c in enumerate(DATA["compacts"]):
        r, col = divmod(idx, 4)
        x = 16 + col * (cw + gap); y = gy + r * (chh + gap)
        card_box(x, y, cw, chh)
        paste_panel(c["scene"], c["label"], x + 1, y + 1, 58, chh - 2, 100 + idx)
        tx = x + 66; tw_max = cw - 74
        # kicker/tag clearance: shrink both until a real gap (>=10px) remains
        kpx, tpx = 9.0, 9.0
        ktxt = f"{c['n']}. {c['place']}"
        while kpx > 7 and tw(d, ktxt, F(SANS_B, kpx)) / S + tw(d, c["tag"], F(SANS_B, tpx)) / S > tw_max - 10:
            kpx -= 0.5; tpx = max(7.5, tpx - 0.25)
        assert tw(d, ktxt, F(SANS_B, kpx)) / S + tw(d, c["tag"], F(SANS_B, tpx)) / S <= tw_max - 10, f"card {c['n']} kicker/tag collision"
        kicker(tx, y + 5, ktxt, px=kpx)
        tf = F(SANS_B, tpx)
        d.text((X(x + cw - 5) - tw(d, c["tag"], tf), X(y + 5)), c["tag"], font=tf, fill=TEAL if c["tag"]=="CONFIRMED" else (GREY if c["tag"]=="REPORTED" else RED))
        pxh, linesh = fit_wrap(d, c["headline"], SERIF_B, 18.5, 13, tw_max * S, 3)
        report["headline_min_px"] = min(report["headline_min_px"], pxh)
        yy = y + 19
        for ln in linesh:
            d.text((X(tx), X(yy)), ln, font=F(SERIF_B, pxh), fill=INK); yy += pxh * 1.1
        # sub printed IN FULL (source included): shrink until every line fits
        sub_px = 11.0
        avail = (y + chh - 4) - yy
        while sub_px > 8.5:
            slines = wrap(d, c["sub_full"], F(SANS, sub_px), tw_max * S)
            if len(slines) * sub_px * 1.25 <= avail:
                break
            sub_px -= 0.5
        slines = wrap(d, c["sub_full"], F(SANS, sub_px), tw_max * S)
        assert len(slines) * sub_px * 1.25 <= avail + 0.01, f"card {c['n']} sub does not fit in full"
        for ln in slines:
            d.text((X(tx), X(yy)), ln, font=F(SANS, sub_px), fill=GREY); yy += sub_px * 1.25
        assert yy <= y + chh - 2, f"card {c['n']} overflow"

    # BRIEFS STRIP: Tuesday briefs only (17); Monday items live in DATE CHECK
    by = gy + 3 * chh + 2 * gap + 8
    d.line([X(16), X(by), X(1008), X(by)], fill=RULE, width=S)
    d.text((X(16), X(by + 5)), f"IN BRIEF · {len(DATA['briefs'])} MORE TUESDAY STORIES", font=F(SANS_B, 11.5), fill=INK)
    by += 24
    colw = 992 / 3; GUT = 24  # real gutter: no brief may enter the last 24px of its column
    for i, (place, txt) in enumerate(DATA["briefs"]):
        r, col = divmod(i, 3)
        x = 16 + col * colw; y = by + r * 18
        pxb = 17.0
        while pxb > 11 and tw(d, place, F(SANS_B, pxb)) + tw(d, f" — {txt}", F(SANS, pxb)) > (colw - GUT) * S:
            pxb -= 0.5
        assert tw(d, place, F(SANS_B, pxb)) + tw(d, f" — {txt}", F(SANS, pxb)) <= (colw - GUT) * S, f"brief overflow: {place}"
        report["brief_min_px"] = min(report["brief_min_px"], pxb)
        d.text((X(x), X(y)), place, font=F(SANS_B, pxb), fill=RED)
        wp = tw(d, place, F(SANS_B, pxb))
        d.text((X(x) + wp, X(y)), f" — {txt}", font=F(SANS, pxb), fill=INK)
    nrows = (len(DATA["briefs"]) + 2) // 3
    report["briefs_bottom"] = by + (nrows - 1) * 18 + 16

    # DATE CHECK strip: the 4 Monday items, quiet muted band, real-date label
    dcy = report["briefs_bottom"] + 8
    d.rectangle([X(16), X(dcy), X(1008), X(dcy + 44)], fill=(238, 233, 219), outline=(170, 164, 148), width=S)
    d.text((X(24), X(dcy + 5)), "DATE CHECK · MON 23 NOV — PRIOR-DAY ITEMS, NOT TUESDAY NEWS", font=F(SANS_B, 9.5), fill=GREY)
    dccolw = 992 / 4
    for i, (place, txt) in enumerate(DATA["datecheck"]):
        x = 16 + i * dccolw; y = dcy + 21
        pxd = 11.0
        while pxd > 8.5 and tw(d, place, F(SANS_B, pxd)) + tw(d, f" — {txt}", F(SANS, pxd)) > (dccolw - 16) * S:
            pxd -= 0.5
        assert tw(d, place, F(SANS_B, pxd)) + tw(d, f" — {txt}", F(SANS, pxd)) <= (dccolw - 16) * S, f"datecheck overflow: {place}"
        d.text((X(x + 8), X(y)), place, font=F(SANS_B, pxd), fill=(110, 60, 40))
        wp = tw(d, place, F(SANS_B, pxd))
        d.text((X(x + 8) + wp, X(y)), f" — {txt}", font=F(SANS, pxd), fill=GREY)
    report["datecheck_bottom"] = dcy + 44
    report["page_bottom"] = report["datecheck_bottom"]
    assert report["page_bottom"] <= 1014, report["page_bottom"]  # >=10px clear of canvas edge

    out = img.resize((1024, 1024), Image.LANCZOS)
    out.save(os.path.join(HERE, "entry.png"))
    out.resize((512, 512), Image.LANCZOS).save(os.path.join(HERE, "entry-512.png"))
    out.resize((300, 300), Image.LANCZOS).save(os.path.join(HERE, "entry-300.png"))
    print(json.dumps(report))

if __name__ == "__main__":
    build()
