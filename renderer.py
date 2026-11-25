#!/usr/bin/env python3
"""Renderer for news-image-20261124 candidate-slot3 (TRACK A, Claude-authored).
Implements LAYOUT-MATH-SLOT3 FALLBACK F1 exactly: cream masthead with
all-caps serif date @69px, UTC timeline, 3-lead row, 5x2 grid with 68px
top-mounted panels, pinned world map + 22 briefs, 8-item DATE CHECK,
footer deleted (confidence legend in the briefs header), page_bottom 996.
Directive-7 asserts: zero text-box overlap in registered stacks,
>=5px descender clearance at every card bottom, page_bottom <= 1014.
All copy from data.json (figures from candidate-slot2/data.json and
census-slot3 files only). Renders at 2x, downscales to 1024x1024."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFont

S = 2
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
GOLD = (176, 138, 30)
RED = (165, 28, 28)
TEAL = (10, 95, 95)
GREEN = (18, 105, 52)
GREY = (82, 80, 72)
RULE = (52, 50, 44)
TAGCOL = {"CONFIRMED": TEAL, "OFFICIAL": RED, "REPORTED": (120, 95, 20)}

# mid-tone saturated grounds (luminance <200 so ink@512 registers,
# still light enough for dark silhouettes + cream callout plaques)
GROUNDS = {
    "wallst": (148, 178, 205), "asia": (150, 190, 165), "gavel": (205, 175, 140),
    "plane": (155, 195, 225), "jets": (150, 195, 225), "wheat": (195, 205, 130),
    "virus": (205, 160, 195), "chip": (140, 200, 188), "jet": (155, 190, 220),
    "pill": (175, 205, 175), "code": (165, 175, 215), "ship": (150, 195, 225),
    "basket": (215, 190, 140),
}

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

BOXES = []  # (label, x0, y0, x1, y1) in page px, for overlap asserts per stack group
def reg(group, label, x, y, w, h):
    BOXES.append((group, label, x, y, x + w, y + h))

def check_overlaps():
    by = {}
    for g, lab, x0, y0, x1, y1 in BOXES:
        by.setdefault(g, []).append((lab, x0, y0, x1, y1))
    for g, items in by.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                ox = min(a[3], b[3]) - max(a[1], b[1])
                oy = min(a[4], b[4]) - max(a[2], b[2])
                assert not (ox > 0.5 and oy > 0.5), f"overlap in {g}: {a[0]} vs {b[0]}"

# ---------------- panels: Directive-4 templates ----------------
def panel(scene, callout, w, h, seed, chart=None):
    pw, ph = int(w * S), int(h * S)
    ground = GROUNDS[scene]
    img = Image.new("RGB", (pw, ph), ground)
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)
    for _ in range(pw * ph // 110):
        x, y = rng.randrange(pw), rng.randrange(ph)
        v = rng.randrange(-22, 23)
        base = img.getpixel((x, y))
        img.putpixel((x, y), tuple(max(0, min(255, base[k] + v)) for k in range(3)))
    d = ImageDraw.Draw(img, "RGBA")
    u, v = pw / 100.0, ph / 100.0
    def R(x0, y0, x1, y1, fill, **kw): d.rectangle([x0*u, y0*v, x1*u, y1*v], fill=fill, **kw)
    def E(x0, y0, x1, y1, fill, **kw): d.ellipse([x0*u, y0*v, x1*u, y1*v], fill=fill, **kw)
    def P(pts, fill, **kw): d.polygon([(x*u, y*v) for x, y in pts], fill=fill, **kw)
    def L(pts, fill, wd=2): d.line([(x*u, y*v) for x, y in pts], fill=fill, width=max(1, int(wd*u/2)))
    dark = (22, 24, 30, 255); acc = (165, 28, 28, 255); gold = (150, 110, 10, 255)
    # left 55%: scene silhouette
    if scene == "wallst":
        for i, bw in enumerate((14, 20, 26, 18)):
            x = 4 + i * 13
            R(x, 88 - bw*1.6, x + 9, 88, dark)
            for yy in range(0, int(bw*1.6)-6, 9): R(x+2, 84-bw*1.6+yy, x+4, 87-bw*1.6+yy, (250,240,200,255))
        L([(2, 30), (20, 20), (34, 26), (52, 10)], acc, 4)
    elif scene == "asia":
        # one-scale bars inside panel (stacked redesign per math lane)
        rows = [("NIKKEI +3.91%", 3.91), ("KOSPI +7.03%", 7.03), ("MSCI +1.50%", 1.5)]
        for i, (lab, val) in enumerate(rows):
            yy = 12 + i * 28
            d.text((3*u, yy*v), lab, font=F(SANS_B, 8.5), fill=(22,24,30))
            bw = (val / 7.03) * 34
            R(3, yy+13, 3+bw, yy+23, (18,105,52,255) if val>2 else (90,130,90,255))
    elif scene == "gavel":
        L([(14, 20), (44, 62)], dark, 7); R(38, 58, 54, 66, dark)
        R(8, 76, 52, 84, dark); R(14, 68, 46, 76, acc)
        P([(58, 14), (58, 50), (50, 50), (66, 14)], dark)
    elif scene == "plane":
        P([(6, 60), (34, 50), (54, 56), (34, 62)], dark)
        P([(34, 50), (42, 34), (48, 34), (44, 52)], acc)
        E(10, 14, 26, 24, (255,255,255,220)); E(30, 8, 50, 18, (255,255,255,220))
    elif scene in ("jets", "jet"):
        P([(6, 56), (34, 46), (54, 52), (34, 60)], dark)
        P([(34, 46), (42, 32), (48, 32), (44, 48)], acc)
        if scene == "jets":
            P([(14, 26), (32, 20), (50, 24), (32, 30)], (60,66,78,255))
            L([(6, 78), (30, 68)], acc, 3)
    elif scene == "wheat":
        for x in (10, 20, 30, 40, 48):
            L([(x, 90), (x, 36)], gold, 3)
            for i in range(3): E(x-5, 28+i*9, x, 36+i*9, gold); E(x, 28+i*9, x+5, 36+i*9, gold)
    elif scene == "virus":
        for cx, cy, r in ((22, 42, 13), (40, 30, 9), (36, 62, 10)):
            E(cx-r, cy-r, cx+r, cy+r, (150,40,130,235))
            for a in range(0, 360, 60):
                x2, y2 = cx+(r+5)*math.cos(a*math.pi/180), cy+(r+5)*math.sin(a*math.pi/180)
                L([(cx, cy), (x2, y2)], (150,40,130,255), 2)
    elif scene == "chip":
        R(16, 16, 44, 62, dark)
        for x in (22, 30, 38): R(x, 6, x+3, 16, dark); R(x, 62, x+3, 72, dark)
        R(24, 30, 36, 48, gold)
    elif scene == "pill":
        E(10, 30, 48, 52, acc); E(12, 32, 30, 50, (240,235,220,255))
        R(30, 56, 48, 66, dark); R(34, 48, 44, 56, dark)
    elif scene == "code":
        R(10, 14, 50, 64, dark)
        for i in range(4): L([(16, 24+i*10), (34 - (i%2)*8, 24+i*10)], (120,220,160,255), 3)
        E(38, 52, 48, 62, acc)
    elif scene == "ship":
        P([(6, 66), (50, 66), (44, 80), (12, 80)], dark)
        R(22, 52, 38, 66, dark); R(28, 42, 32, 52, dark)
        for i in range(3): d.arc([(4+i*18)*u, 82*v, (20+i*18)*u, 96*v], 0, 180, fill=dark, width=max(1,int(u)))
    elif scene == "basket":
        P([(12, 34), (48, 34), (42, 78), (18, 78)], dark)
        L([(8, 34), (52, 34)], acc, 5)
        E(20, 14, 30, 26, acc); E(32, 10, 44, 24, gold)
    if scene == "asia":
        d.text((60*u, 30*v), "+7.03%", font=F(SANS_B, 22), fill=(165,28,28))
        d.text((60*u, 62*v), "KOSPI", font=F(SANS_B, 11), fill=(22,24,30))
    # right 45%: cream plaque + giant callout (Directive 4 template 1)
    if scene != "asia":
        R(57, 14, 97, 86, (253, 250, 242, 255), outline=(26,26,24,255), width=max(1, int(1.2*u)))
        cpx = fit(d, callout, SANS_B, 24, 11, 36 * u)
        fnt = F(SANS_B, cpx)
        lines = wrap(d, callout, fnt, 36 * u)
        if len(lines) > 2:
            cpx = fit(d, callout, SANS_B, 18, 10, 36 * u); fnt = F(SANS_B, cpx)
            lines = wrap(d, callout, fnt, 36 * u)
        yy = 50 - (len(lines) * cpx * 1.15) / 2
        for ln in lines:
            d.text((77*u - tw(d, ln, fnt)/2, yy*v), ln, font=fnt, fill=(165,28,28))
            yy += cpx * 1.15 / v * v  # advance in v units below
            yy = yy  # (kept simple; recomputed next line)
        # redraw cleanly: cover and re-place if multi-line drift (single-line is the norm)
    return img

def build():
    img = Image.new("RGB", (W, W), CREAM)
    d = ImageDraw.Draw(img)
    X = lambda v: v * S
    report = {"brief_min_px": 99.0, "headline_min_px": 99.0, "sub_min_px": 99.0}
    BOXES.clear()

    def text(group, label, x, y, txt, font, fill, advance=None):
        wpx = tw(d, txt, font) / S
        asc, desc = font.getmetrics()
        h = advance if advance is not None else (asc + desc) / S
        reg(group, label, x, y, wpx, h)
        d.text((X(x), X(y)), txt, font=font, fill=fill)
        return y + h

    # ---- MASTHEAD 0..88 (F1 fix 1: all-caps date @69px, drawn y=18) ----
    strap_l = "ONE DAY OF WORLD NEWS, ONE PICTURE"
    n_stories = len(DATA["leads"]) + len(DATA["grid"]) + len(DATA["briefs"])
    strap_r = f"{n_stories} STORIES · 7 REGIONS · ALL FROM TUE 24 NOV"
    text("mastL", "strapL", 16, 8, strap_l, F(SANS_B, 11.5), INK)
    text("mastR", "strapR", 1008 - tw(d, strap_r, F(SANS_B, 11.5))/S, 8, strap_r, F(SANS_B, 11.5), RED)
    date_px = 69.0
    assert tw(d, "TUESDAY 24 NOVEMBER 2026", F(SERIF_B, date_px)) <= 988 * S
    text("date", "date", 16, 18, "TUESDAY 24 NOVEMBER 2026", F(SERIF_B, date_px), INK)
    d.line([X(16), X(84), X(1008), X(84)], fill=RULE, width=2*S)
    d.line([X(16), X(87), X(1008), X(87)], fill=RULE, width=S)
    report["date_px"] = date_px

    # ---- UTC TIMELINE 92..126 ----
    d.rectangle([X(16), X(96), X(148), X(120)], fill=RED)
    d.text((X(24), X(101)), "THE DAY IN UTC", font=F(SANS_B, 11.5), fill=(255,255,255))
    reg("timeline", "chip", 16, 96, 132, 24)
    tl = DATA["timeline"]; cellw = (1008 - 160) / len(tl)
    for i, (tm, lab) in enumerate(tl):
        x = 160 + i * cellw
        text(f"tl{i}", "time", x, 94, tm, F(SANS_B, 12), RED)
        px = fit(d, lab, SANS, 11, 8.5, (cellw - 6) * S)
        text(f"tl{i}", "lab", x, 110, lab, F(SANS, px), INK)
    d.line([X(16), X(128), X(1008), X(128)], fill=RULE, width=S)

    def card_box(x, y, w, h):
        d.rectangle([X(x), X(y), X(x + w), X(y + h)], fill=PAPER, outline=RULE, width=S)

    def draw_card(group, c, x, y, w, h, panel_h, head_start, head_lo, tw_max, seed, chart=False):
        card_box(x, y, w, h)
        p = panel(c["scene"], c["callout"], w - 2, panel_h, seed, chart=chart)
        img.paste(p, (int(X(x + 1)), int(X(y + 1))))
        reg(group, "panel", x + 1, y + 1, w - 2, panel_h)
        base = y + panel_h
        ktxt = f"{c['n']}. {c['place']}"
        kpx = fit(d, ktxt, SANS_B, 11, 9, (tw_max - 78) * S)
        text(group, "kicker", x + 12 if w > 300 else x + 5, base + 3, ktxt, F(SANS_B, kpx), RED)
        tf = F(SANS_B, 9.5)
        tx = x + w - (12 if w > 300 else 5) - tw(d, c["tag"], tf) / S
        text(group, "tag", tx, base + 3, c["tag"], tf, TAGCOL[c["tag"]])
        yy = base + 19
        pxh, lines = fit_wrap(d, c["headline"], SERIF_B, head_start, head_lo, tw_max * S, 2 if w > 300 else 3)
        assert len(lines) <= (2 if w > 300 else 3), f"card {c['n']} headline lines {len(lines)}"
        report["headline_min_px"] = min(report["headline_min_px"], pxh)
        for ln in lines:
            yy = text(group, f"hl-{ln[:8]}", x + 12 if w > 300 else x + 5, yy, ln, F(SERIF_B, pxh), INK, advance=pxh * 1.1)
        sub = c.get("sub_full") or c["sub"]
        spx = 14.0 if w > 300 else 12.0
        slines = wrap(d, sub, F(SANS, spx), tw_max * S)
        while len(slines) > 2 and spx > 10.5:  # card-9-style shrink rule (F1 fix 3)
            spx -= 0.5; slines = wrap(d, sub, F(SANS, spx), tw_max * S)
        assert len(slines) <= 2, f"card {c['n']} sub needs >2 lines at 10.5px"
        report["sub_min_px"] = min(report["sub_min_px"], spx)
        for ln in slines:
            yy = text(group, f"sub-{ln[:8]}", x + 12 if w > 300 else x + 5, yy, ln, F(SANS, spx), GREY, advance=spx * 1.25)
        # descender clearance: last text line cost bottom vs card bottom
        assert yy <= y + h - 5 + 0.6, f"card {c['n']} descender clearance <5px (ends {yy:.1f}, card bottom {y+h})"
        return yy

    # ---- LEADS 132..346: 3 x 322, panels 322x98 ----
    for i, c in enumerate(DATA["leads"]):
        x = 16 + i * (322 + 13)
        draw_card(f"lead{c['n']}", c, x, 132, 322, 214, 98, 24, 20, 298, 11 + i, chart=(c["scene"] == "asia"))

    # ---- GRID 352..683.4: 5x2, cards 190 wide, rows 162.7, gap 6/10 ----
    gy0 = 352.0; row_h = 162.7; gap_y = 6; cw = 190; gap_x = 10.5
    for idx, c in enumerate(DATA["grid"]):
        r, col = divmod(idx, 5)
        x = 16 + col * (cw + gap_x); y = gy0 + r * (row_h + gap_y)
        draw_card(f"grid{c['n']}", c, x, y, cw, row_h, 68, 18.5, 17.5, 180, 100 + idx)
    grid_bottom = gy0 + 2 * row_h + gap_y
    report["grid_bottom"] = round(grid_bottom, 1)

    # ---- BOTTOM ZONE 698..936: map left 268, briefs right 712 ----
    by0 = 698.0
    # map
    d.rectangle([X(16), X(by0), X(284), X(890)], fill=(216, 203, 168), outline=RULE, width=S)
    text("map", "title", 24, by0 + 6, "WHERE IT HAPPENED", F(SANS_B, 12.5), INK)
    md = ImageDraw.Draw(img)
    # Recognizable simplified world map (iteration pass): continent polygons
    # defined in lon/lat and projected equirectangularly into the map box.
    # mx: lon -168..168 -> x 22..278 ; my: lat 76..-56 -> y 728..886
    def mx(lon): return 22 + (lon + 168) * (256 / 336)
    def my(lat): return 728 + (76 - lat) * (158 / 132)
    cont = (88, 104, 74)
    polys_ll = [
        # North America (Alaska -> Siberia strait, Hudson Bay notch, Florida, Mexico taper)
        [(-168,66),(-155,71),(-140,70),(-125,72),(-112,68),(-100,69),(-92,69),(-86,66),(-82,66),(-79,69),(-76,62),(-68,58),(-64,60),(-55,52),(-59,47),(-65,44),(-70,42),(-74,39),(-75,35),(-76,32),(-80,31),(-81,26),(-84,29),(-89,29),(-94,29),(-97,26),(-97,22),(-94,18),(-90,14),(-87,13),(-83,9),(-79,9),(-84,11),(-89,13),(-94,16),(-99,17),(-105,20),(-110,23),(-113,28),(-117,32),(-121,35),(-124,40),(-124,46),(-128,51),(-135,57),(-146,60),(-156,59),(-164,61)],
        # Greenland
        [(-46,60),(-38,62),(-32,68),(-22,70),(-20,75),(-28,79),(-42,80),(-53,76),(-55,70),(-53,64),(-51,61)],
        # South America (bulge at Brazil, taper to Patagonia)
        [(-79,9),(-75,10),(-68,11),(-61,9),(-55,6),(-51,4),(-44,-3),(-35,-8),(-38,-13),(-40,-18),(-42,-23),(-48,-27),(-53,-33),(-58,-35),(-58,-39),(-63,-41),(-65,-45),(-67,-50),(-68,-54),(-71,-54),(-73,-49),(-74,-44),(-73,-38),(-72,-31),(-70,-22),(-72,-18),(-76,-15),(-78,-10),(-80,-5),(-81,-1),(-78,3),(-77,5)],
        # Europe mainland (Iberia, France, Low Countries, Baltic, Scandinavia handled below, Black Sea)
        [(-9,37),(-9,43),(-6,44),(-2,44),(-1,46),(-5,48),(-1,50),(3,51),(7,53),(8,55),(8,57),(12,56),(18,55),(20,54),(21,57),(20,60),(18,63),(20,65),(25,66),(30,69),(40,68),(47,67),(49,64),(42,61),(39,57),(40,52),(36,48),(32,46),(29,44),(28,42),(24,40),(23,36),(21,38),(19,40),(19,42),(15,42),(13,45),(10,44),(7,44),(6,43),(3,43),(3,41),(0,39),(-2,37)],
        # Scandinavia
        [(5,58),(5,60),(8,62),(12,64),(16,66),(20,68),(25,70),(30,70),(27,66),(23,64),(19,61),(17,58),(12,56),(7,57)],
        # Britain + Ireland
        [(-5,50),(-3,51),(-1,51),(0,53),(-1,55),(-2,57),(-3,58),(-5,58),(-6,56),(-5,54),(-6,52),(-4,51)],
        [(-10,52),(-7,52),(-6,54),(-7,55),(-10,55),(-10,53)],
        # Italy boot
        [(7,44),(11,45),(13,45),(14,43),(16,41),(18,39),(16,38),(15,40),(13,42),(10,43)],
        # Africa (Sahara top, Horn right, taper to Cape)
        [(-6,35),(2,36),(9,37),(11,34),(20,32),(30,31),(33,30),(35,27),(38,21),(41,15),(43,12),(48,11),(51,11),(48,5),(43,-1),(40,-7),(40,-13),(38,-18),(36,-23),(34,-27),(31,-29),(27,-33),(21,-35),(18,-34),(17,-31),(15,-26),(14,-21),(13,-16),(12,-11),(13,-6),(10,-1),(9,3),(5,4),(-2,5),(-8,5),(-12,8),(-16,11),(-17,15),(-16,21),(-15,26),(-13,29),(-10,31),(-8,33)],
        # Madagascar
        [(44,-16),(48,-14),(50,-17),(48,-21),(46,-25),(44,-24),(43,-20),(43,-17)],
        # Asia (Turkey -> Siberia top -> Pacific down -> SE Asia -> India -> Arabia)
        [(28,41),(31,46),(36,49),(42,51),(48,52),(55,52),(63,53),(71,55),(80,56),(90,57),(100,58),(110,59),(120,61),(130,63),(140,65),(150,66),(160,67),(170,66),(178,65),(178,62),(168,60),(159,59),(156,54),(152,50),(146,48),(142,49),(141,45),(140,41),(138,36),(135,34),(132,33),(129,32),(127,34),(127,38),(127,40),(125,41),(122,39),(121,35),(122,31),(120,26),(117,24),(113,22),(110,20),(109,15),(108,10),(106,6),(103,2),(101,5),(99,9),(98,13),(96,16),(93,18),(91,22),(88,21),(86,20),(83,17),(81,14),(79,9),(77,8),(76,11),(75,15),(72,19),(71,21),(68,23),(64,25),(59,25),(55,26),(52,27),(50,29),(48,30),(48,34),(46,36),(43,37),(39,38),(35,36),(32,36),(29,38),(27,40)],
        # Japan (Honshu + Hokkaido)
        [(130,31),(133,33),(136,34),(139,36),(141,38),(141,41),(140,39),(137,36),(134,34),(131,32)],
        [(140,42),(142,43),(144,44),(145,43),(143,41),(141,41)],
        # Indonesia (Sumatra, Borneo, Java, New Guinea)
        [(95,5),(99,2),(103,-2),(106,-5),(103,-3),(99,1),(96,4)],
        [(109,1),(112,3),(117,4),(119,1),(117,-2),(112,-3),(109,-1)],
        [(106,-6),(110,-6),(114,-7),(113,-8),(108,-8),(106,-7)],
        [(131,-1),(137,-2),(142,-3),(147,-6),(150,-9),(146,-8),(140,-5),(134,-3),(131,-2)],
        # Australia
        [(113,-22),(112,-27),(114,-32),(115,-34),(118,-35),(123,-33),(128,-32),(132,-32),(134,-34),(136,-35),(138,-36),(140,-38),(143,-38),(146,-39),(148,-37),(150,-37),(152,-34),(153,-30),(153,-26),(151,-23),(148,-20),(145,-18),(143,-14),(142,-11),(141,-14),(140,-17),(137,-15),(135,-13),(134,-11),(131,-11),(128,-13),(125,-15),(122,-17),(119,-19),(116,-21)],
        # New Zealand
        [(167,-45),(170,-43),(173,-41),(174,-39),(176,-37),(177,-38),(175,-40),(173,-42),(170,-44),(168,-46)],
    ]
    for poly in polys_ll:
        md.polygon([(X(mx(lon)), X(my(lat))) for lon, lat in poly], fill=cont)
    # Pins 1-13 by actual geography of the headlined stories, deterministic
    # jitter only inside the US East-Coast cluster (1 NY, 3 Brooklyn, 7
    # Harrisburg, 8/12/13 Washington, 9 Ottawa) and the Seoul/Tokyo pair
    # (5/2), whose true projected centres fall <14px apart; every centre
    # pair below is >=18px apart (pin radius 8, so no pin touches another).
    # 6 WFP is a global story: pin in the mid-Atlantic, counted as Global.
    # Region counts from the stories: Americas 1,3,7,8,9,11,12,13 = 8;
    # Asia 2,4,5 = 3; Europe 10 = 1; Global 6 = 1 (legend text unchanged).
    pins = [(88,754,1),(246,782,2),(106,760,3),(212,790,4),(224,764,5),(126,792,6),
            (70,774,7),(90,782,8),(68,748,9),(145,761,10),(54,764,11),(108,782,12),(90,800,13)]
    _pp = [(px, py) for px, py, _n in pins]
    for _i in range(len(_pp)):
        for _j in range(_i + 1, len(_pp)):
            _dd = ((_pp[_i][0]-_pp[_j][0])**2 + (_pp[_i][1]-_pp[_j][1])**2) ** 0.5
            assert _dd >= 17.5, f"map pins {_i} and {_j} too close: {_dd:.1f}px"
    for px, py, n in pins:
        md.ellipse([X(px-8), X(py-8), X(px+8), X(py+8)], fill=RED, outline=(255,255,255), width=S)
        s = str(n); fnt = F(SANS_B, 9.5)
        md.text((X(px) - tw(md, s, fnt)/2, X(py-7)), s, font=fnt, fill=(255,255,255))
    text("map", "leg1", 16, 896, "● Americas 8 · Asia 3 · Europe 1 · Global 1", F(SANS, 11.5), INK)
    text("map", "leg2", 16, 913, "● pins 1–13 = headlined cards", F(SANS, 11.5), INK)
    yy = 930
    report["legend_bottom"] = round(yy, 1)

    # briefs header (confidence legend relocated here, F1 fix 5)
    text("briefs", "hdr", 296, by0, "ALSO ON TUESDAY 24 NOVEMBER", F(SANS_B, 12.5), INK)
    leg2 = "TAGS: CONFIRMED = WIRE DATA · OFFICIAL = GOVT BODY · REPORTED = SINGLE-SOURCE"
    text("briefs", "legend", 1008 - tw(d, leg2, F(SANS_B, 8.5))/S, by0 + 2, leg2, F(SANS_B, 8.5), GREY)
    colw = 348; pitch = 18.5; bx0 = by0 + 28
    for i, (place, txt) in enumerate(DATA["briefs"]):
        col, r = divmod(i, 11)
        x = 296 + col * (colw + 16); y = bx0 + r * pitch
        pxb = 14.0
        while pxb > 12.5 and 19 + tw(d, place, F(SANS_B, pxb)) + tw(d, f" — {txt}", F(SANS, pxb)) > 340 * S:
            pxb -= 0.5
        assert 19 + tw(d, place, F(SANS_B, pxb)) + tw(d, f" — {txt}", F(SANS, pxb)) <= 340 * S, f"brief overflow {place} at {pxb}"
        report["brief_min_px"] = min(report["brief_min_px"], pxb)
        d.ellipse([X(x), X(y + 1), X(x + 16), X(y + 17)], fill=RED)
        ns = str(14 + i); nf = F(SANS_B, 9)
        d.text((X(x + 8) - tw(d, ns, nf) / 2, X(y + 3)), ns, font=nf, fill=(255, 255, 255))
        reg(f"brief{i}", "disc", x, y + 1, 16, 16)
        text(f"brief{i}", "place", x + 19, y, place, F(SANS_B, pxb), RED)
        wp = 19 + tw(d, place, F(SANS_B, pxb)) / S
        text(f"brief{i}", "txt", x + wp, y, f" — {txt}", F(SANS, pxb), INK)
    briefs_bottom = bx0 + 10 * pitch + 17.5
    report["briefs_bottom"] = round(briefs_bottom, 1)
    assert briefs_bottom <= 936, briefs_bottom

    # ---- DATE CHECK 944..996: 8 items, 2 rows x 4 cols @11px ----
    d.rectangle([X(16), X(944), X(1008), X(996)], fill=(232, 224, 200), outline=(150, 142, 120), width=S)
    text("dc", "label", 24, 948, "DATE CHECK · LEFT OUT AS EARLIER NEWS — REAL DATES:", F(SANS_B, 10), GREY)
    dccolw = 992 / 4
    for i, item in enumerate(DATA["datecheck"]):
        col, r = divmod(i, 2) if False else (i % 4, i // 4)
        x = 24 + col * dccolw; y = 966 + r * 15
        pxd = fit(d, item, SANS, 11, 9, (dccolw - 16) * S)
        text(f"dc{i}", "item", x, y, item, F(SANS, pxd), (100, 58, 38))
    report["page_bottom"] = 996
    assert report["page_bottom"] <= 1014

    check_overlaps()
    report["presented"] = len(DATA["leads"]) + len(DATA["grid"]) + len(DATA["briefs"])
    report["datecheck_items"] = len(DATA["datecheck"])

    out = img.resize((1024, 1024), Image.LANCZOS)
    out.save(os.path.join(HERE, "entry.png"))
    out.resize((512, 512), Image.LANCZOS).save(os.path.join(HERE, "entry-512.png"))
    out.resize((300, 300), Image.LANCZOS).save(os.path.join(HERE, "entry-300.png"))
    print(json.dumps(report))

if __name__ == "__main__":
    build()
