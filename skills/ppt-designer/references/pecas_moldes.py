"""Peças de profundidade e moldes de evidência do catálogo, com conteúdo fictício.
Moldes: foto, print, logo e citação real ficam como retângulos cinza rotulados; nada de evidência inventada.
Uso: python3 pecas_moldes.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402

L, C_, RT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM
CH = "3A3A3A"  # chumbo neutro


# ---------- Helpers ----------
def bz(p0, c1, c2, p3, n=14):
    """Cúbica amostrada: devolve pontos de p0 a p3, inclusive."""
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p3[1]))
    return out


def rpoly(pts, r, n=5):
    """Polígono de cantos arredondados, com raio r nas unidades de pts."""
    out = []
    k = len(pts)
    for i in range(k):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % k]
        d1, d2 = math.dist(p1, p0), math.dist(p1, p2)
        t = min(r, d1 / 2, d2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * t / d1, p1[1] + (p0[1] - p1[1]) * t / d1)
        b = (p1[0] + (p2[0] - p1[0]) * t / d2, p1[1] + (p2[1] - p1[1]) * t / d2)
        for j in range(n + 1):
            q = j / n; u = 1 - q
            out.append((u * u * a[0] + 2 * u * q * p1[0] + q * q * b[0], u * u * a[1] + 2 * u * q * p1[1] + q * q * b[1]))
    return out


def K(pts, win):
    """Recorta um polígono numa janela retangular (Sutherland-Hodgman), para nada sair da caixa."""
    x0, y0, x1, y1 = win
    for inside, cross in ((lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
                          (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
                          (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
                          (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
        out = []
        for i, p in enumerate(pts):
            q = pts[i - 1]
            if inside(p):
                if not inside(q): out.append(cross(q, p))
                out.append(p)
            elif inside(q):
                out.append(cross(q, p))
        pts = out
        if not pts: return []
    return pts


def shadow(sp, blur=6, dx=3, dy=4, alpha=.4, color="000000"):
    """Sombra externa suave, em pontos."""
    spPr = sp._element.spPr
    ef = spPr.find(qn("a:effectLst"))
    if ef is None:
        ef = etree.SubElement(spPr, qn("a:effectLst"))
    for c in list(ef): ef.remove(c)
    o = etree.SubElement(ef, qn("a:outerShdw"))
    o.set("blurRad", str(int(blur * 12700))); o.set("dist", str(int(math.hypot(dx, dy) * 12700)))
    o.set("dir", str(int((math.degrees(math.atan2(dy, dx)) % 360) * 60000))); o.set("algn", "ctr"); o.set("rotWithShape", "0")
    cl = etree.SubElement(o, qn("a:srgbClr")); cl.set("val", ss.hx(color))
    al = etree.SubElement(cl, qn("a:alpha")); al.set("val", str(int(alpha * 100000)))
    return sp


def pl(s, m, pts, color, width=1.0):
    """Polilinha aberta, sem preenchimento."""
    q = m.ps(pts) if m else pts
    k = [(round(a * 1000), round(b * 1000)) for a, b in q]
    fb = s.shapes.build_freeform(k[0][0], k[0][1], scale=914.4)
    fb.add_line_segments(k[1:], close=False)
    sp = fb.convert_to_shape()
    sp.shadow.inherit = False
    sp.fill.background()
    sp.line.color.rgb = ss.rgb(color); sp.line.width = Pt(width)
    return sp


def hl(s, m, a, b, color=INK, width=.75, dash=False):
    return ss.line(s, *m.p(a), *m.p(b), color, width, dash=dash)


def rt(s, m, x0, y0, x1, y1, runs, size=8, align=C_, anchor=MID, color=INK):
    """Texto com vários estilos. runs: lista de parágrafos; cada um, lista de (texto, cor|None, bold, italic)."""
    pp = []
    for para in runs:
        rr_ = []
        for r in para:
            if isinstance(r, str): r = (r,)
            r = tuple(r) + (None, False, False)[len(r) - 1:]
            rr_.append((r[0], {"color": r[1] or color, "bold": r[2], "italic": r[3], "size": size}))
        pp.append(rr_)
    return ss.text(s, *m.box(x0, y0, x1, y1), pp, size=size, align=align, anchor=anchor, margin=0.0)


def rrm(s, m, x0, y0, x1, y1, fill, r=None, border=None, width=1.0, alpha=None):
    """Retângulo arredondado na escala da peça, r em unidades de origem."""
    bx = m.box(x0, y0, x1, y1)
    adj = .5 if r is None else min(.5, r * m.sy / min(bx[2], bx[3]))
    sp = rr(s, *bx, fill, adj, border, width)
    if alpha is not None: ss.set_alpha(sp, alpha)
    return sp


def slot(s, m, x0, y0, x1, y1, label="[photo]", fill=G2, size=7, r=None, border=None, width=.75, color=G4):
    """Molde: retângulo cinza claro com rótulo, a ser trocado pelo material real."""
    bx = m.box(x0, y0, x1, y1)
    if r:
        sp = rr(s, *bx, fill, min(.5, r * m.sy / min(bx[2], bx[3])), border, width)
    else:
        sp = ss.rect(s, *bx, fill, border, False, width)
    tx(s, *bx, label, size=size, color=color)
    return sp


def diamond_slot(s, m, cx, cy, ax, ay, label="[photo]", fill=G2, size=7):
    poly(s, m, ((cx, cy - ay), (cx + ax, cy), (cx, cy + ay), (cx - ax, cy)), fill)
    tm(s, m, cx - ax * .6, cy - 12, cx + ax * .6, cy + 12, label, size=size, color=G4)


def oval_slot(s, m, cx, cy, r, label="[photo]", fill=G2, border=W, size=7, width=1.5):
    px, py = m.p((cx, cy))
    oval(s, px, py, 2 * r * m.sx, fill, border=border, width=width)
    tx(s, px - r * m.sx, py - .1, 2 * r * m.sx, .2, label, size=size, color=G4)


def phone(s, m, x0, y0, x1, y1, label="[print]", bezel=None, size=7):
    """Celular: moldura escura arredondada, ilha no topo e tela como molde."""
    bezel = bezel or CH
    bw = x1 - x0
    rrm(s, m, x0, y0, x1, y1, bezel, r=bw * .16)
    pad = bw * .055
    rrm(s, m, x0 + pad, y0 + pad, x1 - pad, y1 - pad, G2, r=bw * .11)
    rrm(s, m, x0 + bw * .36, y0 + pad * 1.6, x1 - bw * .36, y0 + pad * 2.6, bezel)
    tm(s, m, x0 + pad, y0, x1 - pad, y1, label, size=size, color=G4)


def diamond(s, m, cx, cy, a, fill, border=None):
    return poly(s, m, ((cx, cy - a), (cx + a, cy), (cx, cy + a), (cx - a, cy)), fill, edge=border)


# ---------- Fitas ----------
RIB = ((137.8, 0), (58.8, 0), (53, 1.2), (47.4, 3.6), (42.4, 7.3), (38, 12.6), (23.4, 39.2), (20.6, 43.3), (17.3, 46.7), (13, 49.3), (7.3, 51.2), (0, 52.5), (79, 52.5), (86.3, 51.2), (92, 49.3), (96.3, 46.7), (99.6, 43.3), (102.4, 39.2), (117, 12.6), (121.3, 7.3), (126.4, 3.6), (132, 1.2))
RIBW, RIBH = 219, 94


def _rib(ox, oy, mirror=False):
    q = []
    for a, b in RIB:
        u = a / 137.8 * RIBW
        q.append((ox + (RIBW - u if mirror else u), oy + b / 52.5 * RIBH))
    return q


def interlock_ribbons(s, x, y, w, h):
    """Fitas em S entrelaçadas: cada cor passa por cima do cinza anterior. 3R Petroleum p.2."""
    m = M((105, 450, 1440, 825), (x, y, w, h))
    cols = (dark(D, .25), D, dark(F, .3), F, A, light(A, .3))
    ty = 589
    hl(s, m, (105, ty + 47), (1440, ty + 47), G4, 1.75)
    for i, c in enumerate(cols):
        ox = 121 + i * 195
        poly(s, m, _rib(ox + 107, ty, True), G2)
    for i, c in enumerate(cols):
        ox = 121 + i * 195
        poly(s, m, _rib(ox, ty), c)
        tm(s, m, ox + 50, ty + 20, ox + 175, ty + 74, str(2010 + i * 3), size=8, color=W, bold=False)
        up = i % 2 == 0
        sx = ox + 79 if up else ox + 75
        y0, y1 = (ty + 4, ty - 112) if up else (ty + RIBH - 4, ty + RIBH + 112)
        hl(s, m, (sx, y0), (sx, y1), c, .75)
        poly(s, m, ((sx, y1), (sx + 34, y1), (sx, y1 + (18 if up else -18))), c)
        tb = (ty - 104, ty - 50) if up else (ty + RIBH + 50, ty + RIBH + 104)
        tm(s, m, sx + 12, tb[0], min(1440, sx + 330), tb[1], "Dated event", size=7, align=L)


# ---------- Capas ----------
def triangle_sandwich(s, x, y, w, h):
    """Polígonos agudos sobre foto, com fios finos nas arestas. AB InBev p.58."""
    win = (0, 0, 1467, 825)
    m = M(win, (x, y, w, h))
    slot(s, m, 0, 0, 1467, 825, "", G3)
    tm(s, m, 800, 40, 1400, 240, "[photo in greyscale]", size=8, color=W)
    grad(poly(s, m, ((0, 0), (310, 0), (1020, 562), (770, 825), (0, 825)), A), ((0, dark(A, .08)), (1, light(A, .12))), 90)
    poly(s, m, ((1020, 562), (1068, 514), (1467, 812), (1467, 825), (770, 825)), W)
    poly(s, m, ((1022, 480), (1467, 200), (1467, 812)), CH)
    poly(s, m, ((1022, 480), (1467, 75), (1467, 200)), "252525")
    hl(s, m, (1022, 480), (1467, 812), A, 1.0)
    hl(s, m, (310, 0), (1020, 562), W, .75)
    tm(s, m, 60, 280, 700, 410, "Q&A", size=24, align=L)
    hl(s, m, (60, 415), (640, 415), dark(A, .25), .5)
    tm(s, m, 60, 425, 700, 500, "Company name", size=12, color=W, align=L)
    tm(s, m, 60, 755, 700, 800, "Author  |  Author  |  Author", size=6, align=L)


# ---------- Laços ----------
def bowtie_wheel(s, x, y, w, h):
    """Placas em gravata, de canto arredondado, com o pescoço sob a roda cinza. BTG Pactual p.96."""
    m = M((70, 105, 892, 415), (x, y, w, h))
    pL = ((81, 129), (118, 115), (515, 226), (530, 240), (530, 270), (515, 284), (118, 395), (81, 380))
    pR = ((880, 129), (842, 115), (436, 226), (421, 240), (421, 270), (436, 284), (842, 394), (880, 380))
    poly(s, m, rpoly(pL, 15), F, alpha=20)
    poly(s, m, rpoly(pR, 15), D, alpha=15)
    cx, cy = 476, 260
    pc = m.p((cx, cy))
    oval(s, *pc, 2 * 82.5 * m.sx, W)
    oval(s, *pc, 2 * 69.5 * m.sx, G2)
    for a0, a1, c in ((-250, -60, G4), (-70, 120, dark(D, .05))):
        poly(s, m, seg((cx, cy), 28, 40, a0, a1, n=20), c)
        e = math.radians(a1); t = math.radians(a1 + 90)
        px, py = cx + 34 * math.cos(e), cy + 34 * math.sin(e)
        poly(s, m, ((px + 14 * math.cos(e), py + 14 * math.sin(e)), (px - 14 * math.cos(e), py - 14 * math.sin(e)), (px + 18 * math.cos(t), py + 18 * math.sin(t))), c)
    slot(s, m, 330, 112, 430, 150, "[logo]", size=6)
    slot(s, m, 525, 112, 625, 150, "[logo]", size=6)
    for side, xr, al, col in ((-1, 92, L, F), (1, 869, RT, D)):
        ss.line(s, *m.p((xr, 150)), *m.p((xr, 360)), col, 1.0, dash=False)
        for yy, t in ((150, "First effect"), (240, "Second effect"), (330, "Third effect")):
            oval(s, *m.p((xr, yy)), 22 * m.sx, W, border=col, width=2)
            bx = (xr + 18, yy - 13, xr + 260, yy + 8) if side < 0 else (xr - 260, yy - 13, xr - 18, yy + 8)
            tm(s, m, *bx, t, size=7.5, bold=True, color=col, align=al)
            bx2 = (xr + 18, yy + 10, xr + 240, yy + 34) if side < 0 else (xr - 240, yy + 10, xr - 18, yy + 34)
            tm(s, m, *bx2, "One short line", size=6, color=G4, align=al)


def twist_ribbons(s, x, y, w, h):
    """Fitas curvas que nascem fora da página e entram em ladrilhos, com avesso dobrado. BTG Pactual p.86."""
    win = (0, 205, 360, 435)
    m = M(win, (x, y, w, h))
    rows = ((215, 272, light(A, .82), "Closer ties", " with clients", A), (289, 346, light(F, .85), "Wider range", " of services", F), (368, 425, G2, "Deeper", " service level", dark(F, .15)))
    for yt, yb, c, t1, t2, tc in rows:
        rrm(s, m, 135, yt + 6, 360, yt + 52, c, r=9)
        rt(s, m, 168, yt + 6, 352, yt + 52, [[(t1, tc, True), (t2,)]], size=10, align=L)
    # Fita de cima: a dobra sai por baixo como um crescente e entra sob o ladrilho.
    fold = bz((-70, 294), (53, 268), (105, 260), (155, 272)) + bz((155, 272), (108, 284), (12, 292), (-70, 296))
    poly(s, m, K(fold, win), dark(A, .35))
    top = bz((-70, 275), (10, 272), (60, 250), (98, 215)) + [(98, 272)] + [(-70, 296)]
    poly(s, m, K(top, win), light(A, .35))
    mid = bz((-71, 306), (-20, 304), (47, 299), (99, 289)) + bz((99, 346), (48, 337), (-20, 330), (-71, 327))
    poly(s, m, K(mid, win), light(F, .5))
    # Fita de baixo: a dobra fica acima da fita e some atrás do ladrilho.
    fold2 = bz((-69, 346), (53, 372), (105, 381), (155, 368)) + bz((155, 368), (108, 356), (12, 348), (-71, 344))
    poly(s, m, K(fold2, win), D)
    low = [(-71, 344)] + bz((-71, 344), (-10, 348), (50, 352), (99, 368))[1:] + [(99, 425)] + bz((99, 425), (50, 395), (0, 372), (-71, 365))[1:]
    poly(s, m, K(low, win), F)
    for (yt, yb, *_), c in zip(rows, (light(A, .55), light(F, .1), dark(F, .2))):
        R(s, m, 98, yt, 155, yb, c)
        tm(s, m, 98, yt, 155, yb, "[icon]", size=7, color=W)


# ---------- Mapa ----------
def bands_behind_map(s, x, y, w, h):
    """Pentágonos convergentes e faixa diagonal atrás de um mapa opaco. CSN - ArcelorMittal p.23."""
    m = M((30, 130, 1467, 725), (x, y, w, h))
    grad(poly(s, m, ((35, 137), (487, 137), (732, 427), (487, 717), (35, 717)), G2), ((0, "FDFDFD"), (.32, "E8E8E8"), (.65, "D4D4D4"), (1, "C4C4C4")), 0)
    grad(poly(s, m, ((1467, 137), (1027, 137), (732, 427), (1027, 717), (1467, 717)), G2), ((0, "C4C4C4"), (.4, "D4D4D4"), (.65, "EAEAEA"), (1, "FDFDFD")), 0)
    poly(s, m, ((1041, 149), (1093, 230), (480, 629), (427, 547)), dark(F, .35))
    bra = states("BRA")
    bx = m.box(520, 150, 970, 690)
    draw_map(s, bx, bra, G2, W, .5)
    for i in range(5):
        yy = 165 + i * 105
        tm(s, m, 50, yy - 4, 200, yy + 20, str(2005 + i * 5), size=6, bold=True, color=F, align=L)
        slot(s, m, 50, yy + 22, 165, yy + 72, "[logo]", "FFFFFF", size=5, border=G3, width=.5)
        hl(s, m, (168, yy + 47), (182, yy + 47), G4, .75)
        slot(s, m, 185, yy + 22, 300, yy + 72, "[logo]", "FFFFFF", size=5, border=G3, width=.5)
        tm(s, m, 308, yy + 18, 425, yy + 76, "Deal in a line", size=5.5, align=L)
    tm(s, m, 1090, 155, 1450, 190, "Rationale", size=8, bold=True, color=F)
    for yy in (215, 285, 355):
        hl(s, m, (1100, yy), (1450, yy), F, .75)
        tm(s, m, 1100, yy + 4, 1450, yy + 52, "One line why", size=6.5, align=RT)
    R(s, m, 1035, 540, 1467, 725, G1)
    for i, c in enumerate((G4, G3, A)):
        oval(s, *m.p((1062 + i * 26, 562)), 14 * m.sx, c)
    slot(s, m, 1055, 582, 1450, 712, "[print]", G2, size=7)


# ---------- Divisórias ----------
def shard_frame(s, x, y, w, h):
    """Moldura de lascas sobrepostas em volta de um hexágono escuro. CSN - ArcelorMittal p.18."""
    m = M((0, 0, 1467, 825), (x, y, w, h))
    bg = R(s, m, 0, 0, 1467, 825, D)
    grad(bg, ((0, dark(F, .88)), (.55, dark(F, .55)), (1, dark(F, .1))), 40)
    layers = (
        (((0, 0), (345, 0), (184, 395), (283, 825), (0, 825)), dark(F, .1), dark(F, .35), 0),
        (((0, 0), (230, 0), (120, 395), (230, 825), (0, 825)), dark(F, .55), dark(F, .15), 90),
        (((0, 0), (150, 0), (70, 300), (150, 825), (0, 825)), dark(F, .05), dark(F, .3), 90),
        (((0, 300), (70, 300), (150, 825), (0, 825)), dark(F, .7), dark(F, .45), 0),
        (((0, 0), (120, 0), (0, 150)), dark(F, .75), dark(F, .6), 0),
        (((1155, 0), (1467, 0), (1467, 420)), dark(F, .05), dark(F, .35), 40),
        (((1300, 0), (1467, 0), (1467, 225)), dark(F, .5), dark(F, .3), 40),
        (((1467, 445), (1245, 825), (1467, 825)), dark(F, .05), dark(F, .4), 90),
        (((1467, 620), (1385, 825), (1467, 825)), dark(G4, .6), dark(G4, .45), 90),
    )
    for pts, c0, c1, ang in layers:
        grad(poly(s, m, pts, c0), ((0, c0), (1, c1)), ang)
    tm(s, m, 400, 60, 1100, 170, "Section title", size=15, bold=True, color=W)
    for yy, n, on, t in ((340, "I", False, "First argument"), (560, "II", True, "Second argument")):
        cc = W if on else ss.mix(W, dark(F, .6), .7)
        oval(s, *m.p((370, yy + 28)), 62 * m.sx, dark(F, .6), border=cc, width=.75)
        tm(s, m, 340, yy, 400, yy + 56, n, size=7, color=cc, bold=True)
        tm(s, m, 430, yy - 14, 1120, yy + 28, t, size=8, bold=True, color=cc, align=L)
        tm(s, m, 430, yy + 30, 1120, yy + 70, "What this part of the case proves", size=6.5, color=cc, align=L)


def strand_twist(s, x, y, w, h):
    """Feixe de fios afilados que se cruzam numa cintura. CSN - ArcelorMittal p.1."""
    win = (0, 0, 1467, 825)
    m = M(win, (x, y, w, h))
    R(s, m, 0, 0, 1467, 825, dark(D, .85))
    # Panos largos, atrás, que somem no preto.
    sh = bz((1040, 0), (1000, 180), (1030, 380), (1120, 470), 18) + bz((1120, 470), (1190, 380), (1230, 180), (1230, 0), 18)
    grad(poly(s, m, K(sh, win), F), ((0, dark(F, .2), .15), (.3, F, .85), (1, F, 0)), 90)
    grad(poly(s, m, ((810, 0), (640, 0), (340, 825), (450, 825)), F), ((0, F, .22), (1, F, .08)), 90)
    sh2 = bz((590, 590), (540, 640), (490, 740), (450, 825), 10) + [(620, 825)] + bz((680, 700), (660, 650), (630, 610), (590, 590), 10)
    grad(poly(s, m, K(sh2, win), F), ((0, F, .05), (1, F, .55)), 90)
    # Cada fio: duas bordas que se tocam na cintura; largura máxima nas pontas.
    wx, wy = 1185, 430
    ends = (((1060, 0), (1240, 825)), ((1090, 0), (1150, 825)), ((1120, 0), (1270, 825)), ((1165, 0), (1090, 825)), ((1200, 0), (1000, 825)),
            ((1240, 0), (960, 825)), ((1285, 0), (880, 825)), ((1345, 0), (800, 825)), ((1400, 0), (1120, 825)), ((1467, 40), (1050, 825)),
            ((1467, 95), (1180, 825)), ((1467, 150), (770, 825)), ((1130, 0), (1215, 825)), ((1320, 0), (1270, 825)))
    for k, (a, b) in enumerate(ends):
        hw = 9.5
        ca1 = (a[0] + (wx - a[0]) * .55, a[1] + (wy - a[1]) * .4)
        cb1 = (b[0] + (wx - b[0]) * .55, b[1] + (wy - b[1]) * .4)
        e1 = bz((a[0] - hw, a[1]), ca1, ca1, (wx - .8, wy), 8) + bz((wx - .8, wy), cb1, cb1, (b[0] - hw, b[1]), 8)[1:]
        e2 = bz((b[0] + hw, b[1]), cb1, cb1, (wx + .8, wy), 8) + bz((wx + .8, wy), ca1, ca1, (a[0] + hw, a[1]), 8)[1:]
        sp = poly(s, m, K(e1 + e2, win), light(F, .22) if k % 3 else F)
        ss.set_alpha(sp, 80 + (k % 3) * 8)
    slot(s, m, 170, 250, 300, 320, "[logo]", dark(D, .7), size=6.5, color=G3)
    slot(s, m, 330, 250, 460, 320, "[logo]", dark(D, .7), size=6.5, color=G3)
    hl(s, m, (130, 335), (510, 335), W, .75)
    tm(s, m, 60, 340, 580, 395, "Project name", size=8, bold=True, color=W)
    tm(s, m, 60, 395, 580, 440, "One line that frames it", size=6.5, color=W)
    tm(s, m, 15, 765, 500, 815, "Author  |  Author  |  Author", size=6, bold=True, color=W, align=L)


def zoom_beam_dark(s, x, y, w, h):
    """Feixe de um ponto do preço até um painel em degradê, sobre fundo escuro. Cury Construtora p.32."""
    win = (432, 66, 960, 400)
    m = M(win, (x, y, w, h))
    grad(R(s, m, *win, D), ((0, dark(D, .55)), (1, dark(D, .05))), 60)
    # Preço fictício que termina no ápice do feixe.
    pts = [(432 + i * 1.0, 215 + 30 * math.sin(i * .9) * (1 - i / 9)) for i in range(9)]
    pl(s, m, pts + [(440, 245)], light(F, .4), 1.0)
    oval(s, *m.p((440, 245)), .05, W)
    grad(poly(s, m, ((440, 245), (533, 77), (533, 154)), F), ((0, F, .05), (1, F, .55)), 0)
    grad(R(s, m, 533, 77, 960, 154, F), ((0, light(F, .15)), (.75, F, .6), (1, F, 0)), 0)
    for i, (t, a, b) in enumerate((("Bear case", "7.7%", "19.6%"), ("Base case", "31.0%", "27.0%"), ("Bull case", "44.2%", "31.4%"))):
        cx0 = 545 + i * 138
        tm(s, m, cx0, 80, cx0 + 130, 100, t, size=8, color=light(F, .55))
        tm(s, m, cx0, 102, cx0 + 65, 122, a, size=8, color=W, bold=True)
        tm(s, m, cx0 + 65, 102, cx0 + 130, 122, b, size=8, color=W, bold=True)
        tm(s, m, cx0, 124, cx0 + 65, 146, "Upside", size=7, color=W, italic=True)
        tm(s, m, cx0 + 65, 124, cx0 + 130, 146, "IRR", size=7, color=W, italic=True)
        for k, r in enumerate((f"Sales pace: {55 + i * 10}%", f"Units: {620 + i * 45}", f"Price rise: {4 + i * .2:.1f}%", f"Cost rise: {18 - i * 3}%")):
            tm(s, m, cx0 + 2, 162 + k * 17, cx0 + 136, 178 + k * 17, r, size=6, color=W, bold=True, align=L)
    tm(s, m, 533, 236, 700, 258, "Football field", size=8, color=W, bold=True, italic=True, align=L)
    hl(s, m, (525, 260), (955, 260), W, .75)
    for k, (t, a, b) in enumerate((("Our DCF", 690, 860), ("Multiples", 665, 825), ("Street", 650, 800), ("52 weeks", 640, 745))):
        yy = 272 + k * 31
        tm(s, m, 533, yy, 612, yy + 22, t, size=7, color=W, align=L)
        grad(R(s, m, a, yy, b, yy + 22, F), ((0, light(F, .3), .75), (.5, F, .35), (1, light(F, .3), .75)), 0)
        tm(s, m, a - 40, yy, a - 3, yy + 22, str(a // 20), size=7, color=W, bold=True, align=RT)
        tm(s, m, b + 3, yy, b + 40, yy + 22, str(b // 20), size=7, color=W, bold=True, align=L)
    ss.line(s, *m.p((720, 264)), *m.p((720, 396)), W, .75, dash=True)


# ---------- Cena ----------
def seated_table(s, x, y, w, h):
    """Figuras em volta de uma mesa oval, vista de cima; a mesa esconde o tronco. Intelbras p.32."""
    m = M((-160, -108, 160, 108), (x, y, w, h))
    a, b = 118, 62
    figs = ((-90, F), (-62, D), (-28, light(F, .4)), (0, D), (28, F), (62, light(F, .4)), (90, F), (118, D), (152, light(F, .4)), (180, light(A, .55)), (208, light(F, .4)), (240, D))
    for deg, c in figs:
        t = math.radians(deg)
        ex, ey = a * math.cos(t), b * math.sin(t)
        nx, ny = math.cos(t) * b, math.sin(t) * a
        n = math.hypot(nx, ny); nx, ny = nx / n, ny / n
        tx_, ty_ = -ny, nx
        base = (ex - nx * 8, ey - ny * 8)
        top = (ex + nx * 22, ey + ny * 22)
        poly(s, m, ((base[0] + tx_ * 19, base[1] + ty_ * 19), (top[0] + tx_ * 12, top[1] + ty_ * 12), (top[0] - tx_ * 12, top[1] - ty_ * 12), (base[0] - tx_ * 19, base[1] - ty_ * 19)), c)
        px, py = m.p((ex + nx * 33, ey + ny * 33))
        oval(s, px, py, 17 * m.sx, c)
    e = oval(s, *m.p((0, 0)), 2 * a * m.sx, light(F, .65))
    e.height = int(2 * b * m.sy * 914400); e.top = int((m.p((0, 0))[1] - b * m.sy) * 914400)
    shadow(e, 6, 0, 2, .3)
    rt(s, m, -100, -45, 100, 45, [["A board of ", ("founders,", None, True)], ["strategic ", ("partners", None, True), " and"], ["independent ", ("members", None, True)]], size=11)


def book_wall(s, x, y, w, h):
    """Parede escura que liga a capa do livro à placa da citação. RD Saude p.57."""
    m = M((125, 110, 885, 415), (x, y, w, h))
    R(s, m, 125, 110, 885, 415, G1)
    slot(s, m, 139, 137, 255, 307, "[book cover]", W, size=7, border=G4, width=.5)
    pc = light(F, .1)
    R(s, m, 303, 125, 869, 319, pc)
    poly(s, m, ((256, 137), (303, 125), (303, 319), (256, 307)), dark(pc, .35))
    tm(s, m, 325, 137, 850, 225, "[quote from the book]", size=9, color=W)
    hl(s, m, (450, 228), (720, 228), W, .5)
    tm(s, m, 325, 235, 850, 305, "What the idea means for this company, and the call it supports", size=8, color=W, bold=True)
    for i, xs in enumerate((318, 334, 350)):
        yy = 340 + i * 26
        pl(s, m, ((xs, 319), (xs, yy), (372, yy)), dark(pc, .35), 1.0)
        tm(s, m, 380, yy - 11, 860, yy + 11, ("First implication", "Second implication", "Third implication")[i], size=7.5, align=L)


def stone_hexes(s, x, y, w, h, active=1):
    """Hexágonos de pedra em escada sobre feixes diagonais; um deles aceso. RD Saude p.6."""
    win = (55, 70, 840, 520)
    m = M(win, (x, y, w, h))
    R(s, m, *win, dark(F, .25))
    for pts, ang in ((((55, 520), (55, 300), (275, 520)), 45), (((330, 520), (55, 245), (55, 215), (360, 520)), 45), (((690, 70), (840, 70), (840, 220)), 225)):
        grad(poly(s, m, pts, A), ((0, light(F, .15), .85), (1, light(F, .15), .05)), ang)
    hexp = ((77, 144), (105, 88), (182, 88), (210, 144), (182, 200), (105, 200))
    for i, (t, ox, oy) in enumerate((("First section", 0, 0), ("Second section", 139, 157), ("Third section", 282, 311))):
        on = i == active
        c = light(F, .12) if on else "A6A6A6"
        q = [(a + ox, b + oy) for a, b in hexp]
        shadow(poly(s, m, q, c), 6, 3, 4, .4)
        cc = m.p((143.5 + ox, 144 + oy))
        oval(s, *cc, 74 * m.sx, None, border=W, width=1.25)
        tm(s, m, 113 + ox, 130 + oy, 174 + ox, 158 + oy, "[icon]", size=6.5, color=W)
        if on:
            rrm(s, m, 216 + ox, 112 + oy, 620 + ox, 184 + oy, c, r=10)
        tc = W
        tm(s, m, 226 + ox, 112 + oy, 830, 140 + oy, t, size=10, bold=True, color=tc, align=L)
        tm(s, m, 226 + ox, 140 + oy, 830, 182 + oy, "The question it answers", size=7, italic=True, color=tc, align=L)


# ---------- Modais ----------
def _mini_chart(s, m, x0, y0, x1, y1, n=9):
    v = [.28 + .72 * i / (n - 1) for i in range(n)]
    bw = (x1 - x0) / (n * 1.45)
    for i, t in enumerate(v):
        bx = x0 + i * bw * 1.45
        top = y1 - (y1 - y0) * t * .82
        R(s, m, bx, top, bx + bw, y1, D if i < 3 else F)
        if i in (0, 4, 8):
            px = m.p((bx + bw / 2, top))
            ss.pill(s, px[0], px[1] - .19, str(20 + i * 7), fill=D if i < 3 else F, color=W, size=7, h=.16, w=.28)
    hl(s, m, (x0 - 6, y1), (x1 + 6, y1), G4, .5)


def dim_modal(s, x, y, w, h):
    """Slide anterior lavado de cinza, cartão e placa dura em L. Rede D'Or p.27."""
    m = M((0, 0, 960, 540), (x, y, w, h))
    R(s, m, 0, 0, 960, 540, W)
    tm(s, m, 30, 25, 470, 50, "Previous slide content", size=7, color=G4, align=L)
    mini_bars(s, m, 40, 75, 460, 235, n=8, c=G4)
    mini_bars(s, m, 40, 320, 920, 515, n=20, c=G4)
    R(s, m, 0, 0, 960, 540, "000000", alpha=18)
    R(s, m, 174, 125, 774, 428, D)
    R(s, m, 180, 118, 780, 422, G1)
    tm(s, m, 198, 124, 760, 152, "Single chart above its context", size=8, bold=True, color=D, align=L)
    hl(s, m, (198, 156), (764, 156), D, .75)
    _mini_chart(s, m, 205, 180, 755, 405, n=11)


def slip_card(s, x, y, w, h):
    """Cartão com placa em L sobre o gráfico, janela destacada na fase que explica. Rede D'Or p.61."""
    m = M((35, 60, 885, 512), (x, y, w, h))
    for y0, y1, t, c2 in ((100, 255, "Spread over time", True), (355, 490, "Loss ratio over time", False)):
        tm(s, m, 40, y0 - 40, 540, y0 - 12, t, size=7.5, bold=True, color=D, align=L)
        for f, c in (((.45, .42, .35, .28, .34, .42, .48, .52, .55), F),) + (((.72, .7, .62, .55, .6, .68, .72, .76, .8), A),) * c2:
            ss_pts = [(50 + i * 75, y0 + (y1 - y0) * (1 - f_) * .9) for i, f_ in enumerate(f)]
            pl(s, m, ss_pts, c, 1.5)
        hl(s, m, (45, y1), (700, y1), G4, .5)
        for i in range(0, 9, 2):
            tm(s, m, 36 + i * 75, y1 + 1, 76 + i * 75, y1 + 18, f"'{16 + i}", size=6, color=G4)
    a = R(s, m, 75, 92, 395, 250, F, alpha=40); a.line.color.rgb = ss.rgb(D); a.line.width = Pt(1.5); a.line.dash_style = ss.MSO_LINE_DASH_STYLE.DASH
    a = R(s, m, 75, 348, 395, 485, F, alpha=40); a.line.color.rgb = ss.rgb(D); a.line.width = Pt(1.5); a.line.dash_style = ss.MSO_LINE_DASH_STYLE.DASH
    tm(s, m, 75, 96, 395, 122, "Before the shock", size=7.5, color=W, bold=True)
    R(s, m, 552, 139, 880, 508, D)
    R(s, m, 546, 133, 874, 502, G1)
    tm(s, m, 560, 155, 860, 185, "Before the shock", size=10, bold=True, color=D)
    tm(s, m, 565, 200, 855, 265, "•  Constant spread between revenue and costs", size=7.5, align=L)
    rt(s, m, 565, 285, 855, 310, [[("Loss ratio", None, False, True)]], size=8)
    hl(s, m, (640, 312), (780, 312), INK, .5)
    rt(s, m, 565, 314, 855, 338, [[("Claims / Premiums", None, False, True)]], size=8)
    tm(s, m, 565, 370, 855, 435, "•  Loss ratio held steady across the years", size=7.5, align=L)


def verdict_cards(s, x, y, w, h, word=None, n=4):
    """Faixa translúcida sobre foto, cartões brancos e etiqueta numerada pendurada. RBI p.49."""
    win = (0, 0, 960, 540) if word else (30, 250, 930, 505)
    m = M(win, (x, y, w, h))
    slot(s, m, *win, "", G2)
    band = (195, 440) if word else (250, 470)
    grad(R(s, m, win[0], band[0], win[2], band[1], D), ((0, dark(F, .2), .92), (1, dark(F, .4), .92)), 90)
    if word:
        tm(s, m, 40, 40, 920, 170, "[photo]", size=8, color=G4)
        tm(s, m, 200, 195, 760, 280, word, size=26, bold=True, color=W)
    ty = 290 if word else 275
    by = 515 if word else 500
    cw, gap = 192, 26
    x0 = 60
    tabs, heads = ("I", "II", "III", "!"), ("Thesis one", "Thesis two", "Thesis three", "Risks")
    for i in range(n):
        cx = x0 + i * (cw + gap)
        rrm(s, m, cx, ty, cx + cw, by, W, r=20)
        rrm(s, m, cx - 15, ty - 9, cx + 19, ty + 24, F, r=6, border=W, width=1.0)
        tm(s, m, cx - 15, ty - 9, cx + 19, ty + 24, tabs[i], size=7, bold=True, color=W)
        tm(s, m, cx + 22, ty + 4, cx + cw - 6, ty + 32, heads[i], size=6.5, bold=True, italic=tabs[i] == "!", color=F)
        for k in range(3):
            yy = ty + 58 + k * 50
            poly(s, m, ((cx + 22, yy - 8), (cx + 30, yy), (cx + 22, yy + 8), (cx + 14, yy)), W, edge=F, ew=1)
            tm(s, m, cx + 36, yy - 20, cx + cw - 4, yy + 20, "Short point", size=6, align=L)


def rbi_cards_band(s, x, y, w, h):
    """Cartões sobrepostos com aba numerada, numa faixa sobre foto. RBI p.49."""
    verdict_cards(s, x, y, w, h)


def closing_verdict(s, x, y, w, h):
    """Slide final: foto, faixa, veredito grande e quatro cartões. RBI p.49."""
    verdict_cards(s, x, y, w, h, word="BUY!")


def _crown(s, m):
    """Coroa de ondas com telhado escuro, medida no original (Senior p.15)."""
    roofc = dark(D, .25)
    poly(s, m, bz((83, 111), (180, 72), (350, 75), (532, 111), 24), dark(F, .45))
    poly(s, m, bz((362, 111), (520, 60), (780, 62), (862, 111), 24), F)
    roof = [(70, 74)] + bz((70, 74), (180, 100), (340, 112), (445, 108), 16)[1:] + bz((445, 108), (580, 104), (760, 88), (884, 79), 16)[1:] + [(884, 112), (70, 112)]
    poly(s, m, roof, roofc)
    poly(s, m, ((70, 111), (884, 111), (884, 119), (874, 126), (80, 126), (70, 119)), roofc)
    poly(s, m, ((70, 119), (80, 119), (80, 126)), dark(roofc, .4))
    poly(s, m, ((884, 119), (874, 119), (874, 126)), dark(roofc, .4))


def modal_crown(s, x, y, w, h):
    """Folha modal com coroa de fita sobre o slide lavado. Senior Sistemas p.15."""
    m = M((30, 60, 930, 490), (x, y, w, h))
    R(s, m, 30, 60, 930, 490, W)
    mini_lines(s, m, 50, 90, 900, 470, F)
    R(s, m, 30, 60, 930, 490, G1, alpha=60)
    shadow(grad(R(s, m, 77, 123, 874, 474, F), ((0, dark(F, .5)), (1, light(F, .65))), 90), 8, 2, 3, .3)
    R(s, m, 78, 124, 872, 472, G1)
    _crown(s, m)
    tm(s, m, 110, 132, 800, 158, "Strong presence across the main sectors", size=8, bold=True, color=F, align=L)
    tm(s, m, 110, 158, 800, 182, "Solutions adopted by market leaders", size=6.5, italic=True, color=G4, align=L)
    chain = ((240, 250), (360, 375), (480, 250), (600, 375), (720, 250))
    for (ax, ay), (bx, by) in zip(chain, chain[1:]):
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy); ux, uy = -dy / n * 15, dx / n * 15
        poly(s, m, ((ax + ux, ay + uy), (bx + ux, by + uy), (bx - ux, by - uy), (ax - ux, ay - uy)), F)
    for i, v in enumerate(("90%", "70%", "18%", "45%", "35%")):
        cx, cy = chain[i]
        px = m.p((cx, cy))
        oval(s, *px, 100 * m.sx, F if i % 2 else dark(F, .45))
        oval(s, *px, 74 * m.sx, W)
        tm(s, m, cx - 35, cy - 15, cx + 35, cy + 15, v, size=8, bold=True, color=dark(F, .3))
    for cx, cy, t in ((360, 225, "Sector B"), (600, 225, "Sector D"), (235, 375, "Sector A"), (480, 395, "Sector C"), (730, 375, "Sector E")):
        tm(s, m, cx - 75, cy - 12, cx + 75, cy + 12, t, size=7, bold=True, color=F)


def arrow_cards(s, x, y, w, h):
    """Pentágonos que apontam para o gráfico e descem pela borda da folha. Senior Sistemas p.21."""
    m = M((60, 70, 895, 480), (x, y, w, h))
    shadow(grad(R(s, m, 77, 123, 874, 474, F), ((0, dark(F, .5)), (1, light(F, .65))), 90), 8, 2, 3, .3)
    R(s, m, 78, 124, 872, 472, G1)
    _crown(s, m)
    tm(s, m, 95, 133, 700, 155, "Growth and margin rule of thumb", size=8, bold=True, color=F, align=L)
    for i, (a, b) in enumerate(((.47, .23), (.43, .16), (.42, .17), (.46, .2), (.31, .16), (.33, .16))):
        bx = 110 + i * 64
        est = i > 3
        c1, c2 = (light(F, .45), light(D, .55)) if est else (F, dark(D, .15))
        base, ht = 440, 300
        R(s, m, bx, base - ht * a * 1.4, bx + 36, base - ht * b * 1.4, c2)
        R(s, m, bx, base - ht * b * 1.4, bx + 36, base, c1)
        tm(s, m, bx - 8, base + 2, bx + 44, base + 20, str(22 + i) + ("E" if est else ""), size=6.5)
    ss.line(s, *m.p((95, 248)), *m.p((505, 248)), INK, .75, dash=True)
    hl(s, m, (95, 440), (505, 440), G4, .5)
    for k, c in enumerate((F, dark(D, .05), dark(D, .3))):
        o = k * 80
        pts = ((520, 219 + o), (563, 179 + o), (876, 179 + o), (876, 260 + o), (563, 260 + o))
        shadow(poly(s, m, pts, c), 5, 0, 3, .35)
        tm(s, m, 526, 200 + o, 592, 240 + o, "[icon]", size=5, color=W)
        tm(s, m, 594, 184 + o, 870, 256 + o, ("What the rule says", "How it scored", "Why margin holds")[k], size=7.5, bold=True, color=W, align=L)


# ---------- Pirâmide ----------
def slab_pyramid(s, x, y, w, h):
    """Lajes separadas ligadas por tiras diagonais, com faixa que desbota à direita. Senior Sistemas p.7."""
    m = M((550, 118, 942, 294), (x, y, w, h))
    near = "F5FAF9"
    for x0, y0, y1, c, t in ((665, 123, 178, F, "Large companies"), (659, 177, 231, dark(F, .45), "Small and midsize"), (626, 231, 289, dark(D, .1), "Micro companies")):
        grad(R(s, m, x0, y0, 939, y1, c), ((0, c), (.35, ss.mix(c, near, .3)), (1, near)), 0)
        tm(s, m, 738, y0, 935, y1, t, size=8, bold=True, color=W, align=L)
    grad(poly(s, m, ((604, 191), (640, 166), (670, 165), (634, 190)), dark(F, .45)), ((0, dark(F, .5)), (1, dark(F, .3))), 0)
    grad(poly(s, m, ((604, 167), (638, 122), (672, 167)), F), ((0, F), (1, dark(F, .45))), 90)
    grad(poly(s, m, ((578, 252), (643, 218), (687, 221), (622, 255)), dark(D, .1)), ((0, dark(D, .1)), (1, dark(F, .5))), 0)
    grad(poly(s, m, ((575, 227), (589, 189), (686, 189), (700, 227)), dark(F, .45)), ((0, dark(F, .45)), (1, dark(D, .25))), 90)
    shadow(grad(poly(s, m, ((553, 289), (567, 247), (709, 247), (724, 289)), D), ((0, dark(D, .35)), (1, dark(D, .05))), 90), 5, 0, 3, .3)
    for x0, x1, y0, y1, a, b in ((604, 672, 138, 167, "10", "k"), (589, 686, 192, 226, "640", "k"), (567, 709, 250, 288, "4.5", "mn")):
        rt(s, m, x0, y0, x1, y1, [[(a, W, True), (" " + b, W)]], size=9)


def beam_donut_panel(s, x, y, w, h):
    """Feixe da maior fatia do donut que se funde a um painel com linhas emolduradas. Senior Sistemas p.10."""
    m = M((140, 322, 948, 516), (x, y, w, h))
    cc = (215, 419)
    grad(poly(s, m, ((264, 392), (392, 326), (392, 512), (264, 446)), F), ((0, F), (1, dark(D, .25))), 0)
    grad(R(s, m, 392, 326, 944, 512, F), ((0, dark(D, .25)), (1, F)), 0)
    poly(s, m, seg(cc, 38, 70, -92, 105, n=30), F)
    poly(s, m, seg(cc, 38, 70, 105, 220, n=24), dark(D, .25))
    poly(s, m, seg(cc, 38, 70, 220, 268, n=14), light(F, .35))
    for t, a, b in (("60", 260, 427), ("25", 165, 454), ("15", 188, 382)):
        ss.pill(s, *(m.p((a, b))[0], m.p((a, b))[1] - .08), t, fill=dark(D, .2), color=W, size=7, h=.16, w=.26)
    for i, (y0, t, u) in enumerate(((331, "First driver: ", "removes the barrier"), (393, "Second driver: ", "cuts the cost"), (454, "Third driver: ", "closes the data gap"))):
        grad(R(s, m, 409, y0, 937, y0 + 51, F), ((0, F), (1, dark(D, .25))), 0)
        R(s, m, 413, y0 + 3, 891, y0 + 49, G1)
        rt(s, m, 422, y0 + 3, 885, y0 + 49, [[(t, F, True), (u,)]], size=8, align=L)
        oval(s, *m.p((914, y0 + 26)), 26 * m.sx, None, border=W, width=1.25)


# ---------- Órbita ----------
def orbit_arcs(s, x, y, w, h):
    """Arcos em D com fios tangentes que levam os rótulos, sobre plano diagonal. Senior Sistemas p.2."""
    m = M((0, 0, 800, 450), (x, y, w, h))
    R(s, m, 0, 0, 800, 450, W)
    poly(s, m, ((624, 0), (800, 0), (800, 450), (286, 450)), "E3E3E3")
    poly(s, m, ((0, 0), (22, 0), (12, 40), (12, 450), (0, 450)), dark(D, .25))
    grad(poly(s, m, ((0, 360), (12, 300), (22, 450), (0, 450)), F), ((0, F), (1, dark(F, .3))), 90)
    for k in range(4):
        o = k * 6
        d = bz((35 + o, 110), (55 + o, 95), (95 + o, 88), (120 + o, 95), 8) + bz((120 + o, 95), (200 + o, 125), (250 + o, 190), (250 + o, 255), 16)[1:] + bz((250 + o, 255), (250 + o, 325), (200 + o, 385), (140 + o, 392), 16)[1:] + bz((140 + o, 392), (105 + o, 395), (65 + o, 380), (40 + o, 345), 8)[1:]
        pl(s, m, d, dark(F, .3), 1.25)
    rows = ((111, 192, 192, "I. Industry and outlook", True), (181, 256, 262, "II. Financials and position", False), (247, 285, 290, "III. Projections", False), (315, 278, 282, "IV. Deal and value creation", False), (382, 190, 240, "V. Exit theses", False))
    for yy, x0, lx, t, on in rows:
        hl(s, m, (x0, yy), (800, yy), dark(F, .3), .75)
        tm(s, m, lx, yy - 34, 760, yy - 3, t, size=8, bold=on, color=dark(F, .3), align=L, anchor=BOT)
    # Esfera de arame: nós numa espiral de Fibonacci; os de trás ficam desbotados.
    cx, cy, r = 85, 225, 84
    nodes = []
    N = 44
    for i in range(N):
        zz = 1 - 2 * (i + .5) / N
        rad = math.sqrt(1 - zz * zz)
        th = i * 2.399963 + .4
        nodes.append((rad * math.cos(th), zz, rad * math.sin(th)))
    pairs = sorted(((math.dist(a, b), i, j) for i, a in enumerate(nodes) for j, b in enumerate(nodes) if i < j))[:104]
    for _, i, j in pairs:
        a, b = nodes[i], nodes[j]
        back = a[2] + b[2] < 0
        ax = max(14, cx + a[0] * r); bx = max(14, cx + b[0] * r)
        hl(s, m, (ax, cy - a[1] * r), (bx, cy - b[1] * r), light(F, .55) if back else dark(F, .15), .5 if back else .75)
    for a in nodes:
        px, py = cx + a[0] * r, cy - a[1] * r
        if px < 16: continue
        back = a[2] < 0
        oval(s, *m.p((px, py)), (5 if back else 8) * m.sx, light(F, .55) if back else dark(F, .35))
    tm(s, m, 40, 205, 130, 245, "[logo]", size=7, color=F, bold=True)


def offset_rounded_modal(s, x, y, w, h):
    """Véu escuro, duas placas arredondadas deslocadas e modal branco por cima. Vasta p.15."""
    m = M((0, 0, 960, 540), (x, y, w, h))
    backdrop(s, m, (0, 0, 960, 540))
    R(s, m, 0, 0, 960, 540, "000000", alpha=60)
    rrm(s, m, 53, 60, 400, 390, F, r=30)
    rrm(s, m, 600, 200, 912, 490, F, r=30)
    rrm(s, m, 67, 74, 898, 475, W, r=30)
    rt(s, m, 100, 78, 865, 112, [["The combination sustains ", ("superior returns", F, True)]], size=9)
    tm(s, m, 100, 114, 865, 140, "Lifetime value over acquisition cost", size=7.5, color=F)
    v = (.72, .82, .52, .2, .12, .5, .55, .62, .68, .72, .76, .78, .8)
    b = (.3, .28, .25, .18, .12, .2, .2, .2, .2, .2, .2, .2, .2)
    for ser, c, dash in ((b, dark(F, .4), False), (v, F, False)):
        pp = [(115 + i * 58, 440 - 210 * t) for i, t in enumerate(ser)]
        pl(s, m, pp, c, 1.5)
        for i in (0, 3, 6, 9, 12):
            a = m.p(pp[i])
            ss.pill(s, a[0], a[1] - .17, str(int(ser[i] * 10) / 1) + "x", fill=c, color=W, size=7, h=.15, w=.3)
    hl(s, m, (100, 445), (860, 445), G4, .5)
    for i in range(0, 13, 2):
        tm(s, m, 95 + i * 58, 447, 135 + i * 58, 465, f"'{21 + i}", size=6.5, color=G4)


# ---------- Moldes de evidência: registro e tese ----------
QT = "[quote from a real interview]"


def _sig(s, m, x0, x1, y, name="Name", ink=INK, fill=G2, size=5.5):
    """Assinatura real: molde cinza sobre fio, com nome impresso abaixo."""
    slot(s, m, x0, y - 22, x1, y - 1, "[signature]", fill, size=5)
    hl(s, m, (x0, y), (x1, y), ink, .5)
    tm(s, m, x0 - 6, y + 1, x1 + 6, y + 15, name, size=size, italic=True, color=ink)


def _tick(s, m, x, y0, y1, c=None):
    R(s, m, x, y0, x + 3, y1, c or D)


def deal_ledger(s, x, y, w, h):
    """Régua de gestão, cartões de negócios alinhados à escala e preço abaixo, com tabela ao lado. Vibra p.6."""
    m = M((0, 0, 440, 185), (x, y, w, h))
    R(s, m, 0, 0, 4, 185, F)
    yrs = [2019 + i for i in range(8)]
    for i, yr in enumerate(yrs):
        tm(s, m, 8 + i * 54, 0, 54 + i * 54, 11, str(yr), size=5.5, bold=True, align=L)
    tm(s, m, 8, 12, 58, 24, "CEO", size=5.5, bold=True, color=F, align=L)
    for a, b in ((60, 155), (160, 255), (260, 350), (355, 438)):
        hl(s, m, (a, 24), (b, 24), F, 1.0)
        tm(s, m, a, 12, b, 24, "[name]", size=5.5, italic=True, color=F)
    for i, cx in enumerate((8, 86, 164, 242)):
        R(s, m, cx, 28, cx + 72, 66, W, F, width=.75)
        R(s, m, cx + 1, 29, cx + 71, 37, light(F, .8))
        tm(s, m, cx + 1, 29, cx + 71, 37, "[date]", size=5, bold=True)
        tm(s, m, cx + 3, 38, cx + 70, 50, "[deal in a line]", size=5, align=L)
        tm(s, m, cx + 3, 51, cx + 40, 64, "[status]", size=5, bold=True, align=L)
        slot(s, m, cx + 41, 52, cx + 70, 64, "[logo]", size=4.5)
    R(s, m, 320, 28, 436, 70, W, F, width=1.25)
    R(s, m, 321, 29, 435, 37, light(F, .8))
    tm(s, m, 321, 29, 435, 37, "[date range]", size=5, bold=True)
    tm(s, m, 324, 38, 400, 66, "[largest deal, with value and status]", size=5, align=L)
    slot(s, m, 402, 48, 434, 66, "[logo]", size=4.5)
    pts = [(14 + i * 6.8, 170 - (.42 + .2 * math.sin(i * .3) + .07 * math.sin(i * 1.1 + 1) + .03 * math.sin(i * 2.7) + .006 * i) * 85) for i in range(44)]
    for a0, a1 in ((60, 110), (180, 245)):
        R(s, m, a0, 76, a1, 170, W, G4, width=.5, dash=True)
        tm(s, m, a0, 77, a1, 89, "[event]", size=5, color=G4)
    pl(s, m, pts, F, 1.0)
    hl(s, m, (14, 170), (312, 170), G4, .5)
    for i, yr in enumerate(yrs[::2]):
        tm(s, m, 14 + i * 72, 171, 74 + i * 72, 183, str(yr), size=5, color=G4, align=L)
    R(s, m, 320, 76, 436, 86, F)
    tm(s, m, 322, 76, 434, 86, "Deal  |  Multiple", size=5, bold=True, color=W)
    for k in range(6):
        yy = 87 + k * 14
        if k == 4: R(s, m, 320, yy, 436, yy + 14, light(F, .8))
        tm(s, m, 322, yy, 370, yy + 14, f"[deal {k + 1}]", size=5, align=L)
        tm(s, m, 372, yy, 434, yy + 14, "[multiple]", size=5, align=RT)
        hl(s, m, (320, yy + 14), (436, yy + 14), G3, .25)


def field_wall(s, x, y, w, h):
    """Parede solta de provas, cada imagem com uma legenda. 3R Petroleum p.51."""
    m = M((0, 0, 440, 215), (x, y, w, h))
    slot(s, m, 0, 0, 175, 85, "[print: video call]")
    tm(s, m, 0, 86, 175, 100, "Name, role", size=6, italic=True, align=L)
    slot(s, m, 0, 103, 175, 197, "[print: video call]")
    tm(s, m, 0, 198, 175, 212, "Name, role", size=6, italic=True, align=L)
    phone(s, m, 208, 25, 280, 178, "[print: call]")
    tm(s, m, 190, 180, 298, 212, "Name, company, what they said", size=6, italic=True)
    slot(s, m, 309, 15, 438, 192, "[photo: on site]")
    tm(s, m, 309, 194, 438, 212, "We visited the site", size=6, italic=True)


def interview_wall(s, x, y, w, h):
    """Cartão do entrevistado principal ligado a moldura com calls, e faixa com contagens. AB InBev p.15."""
    m = M((0, 0, 440, 198), (x, y, w, h))
    R(s, m, 0, 0, 97, 118, light(A, .88), light(A, .4), width=.5)
    slot(s, m, 4, 4, 93, 50, "[print: call]", size=6)
    tm(s, m, 3, 52, 94, 75, "Name, the lead interviewee", size=5.5, bold=True)
    tm(s, m, 3, 76, 94, 116, "[what the main call established, in two lines]", size=5.5)
    hl(s, m, (97, 18), (136, 18), A, .75)
    R(s, m, 136, 5, 140, 32, A)
    hl(s, m, (148, 3), (440, 3), light(A, .3), .75); hl(s, m, (148, 3), (148, 142), light(A, .3), .75); hl(s, m, (148, 142), (440, 142), light(A, .3), .75)
    for i in range(8):
        cx = 155 + (i % 4) * 71; cy = 8 + (i // 4) * 54
        slot(s, m, cx, cy, cx + 66, cy + 38, "[print: call]", size=5.5)
        tm(s, m, cx - 2, cy + 38, cx + 68, cy + 51, "Name | Role", size=5, italic=True)
    R(s, m, 155, 118, 158, 139, A)
    tm(s, m, 162, 117, 436, 140, QT, size=6.5, bold=True, align=L)
    R(s, m, 0, 150, 440, 198, A)
    for cx, t in ((215, "Employees interviewed"), (330, "Countries")):
        tm(s, m, cx - 60, 152, cx, 196, "[N]", size=15, bold=True, color=W, align=RT)
        tm(s, m, cx + 3, 152, cx + 62, 196, t, size=5.5, color=W, align=L)


def mystery_shop(s, x, y, w, h):
    """Tabela de teste próprio com a linha vencedora tracejada, achado, fotos da medição e nota de controles. AB InBev p.38."""
    m = M((0, 0, 440, 295), (x, y, w, h))
    R(s, m, 0, 0, 440, 295, G1)
    cols = (70, 165, 265, 360)
    for cx, t in zip(cols, ("Players", "Avg. time", "Measure", "St. dev.")):
        tm(s, m, cx - 45, 6, cx + 45, 22, t, size=7, bold=True)
    R(s, m, 25, 23, 415, 25, A)
    for k in range(3):
        yy = 28 + k * 30
        slot(s, m, 40, yy + 3, 102, yy + 26, "[logo]", W, size=5.5)
        for cx in cols[1:]:
            tm(s, m, cx - 40, yy, cx + 40, yy + 28, "[n]", size=7, bold=k == 0)
    R(s, m, 122, 28, 412, 56, None, G4, width=.75, dash=True)
    hl(s, m, (25, 118), (415, 118), G3, .25)
    rt(s, m, 25, 122, 415, 165, [["Ours came out ", ("[result]", A, True), " than peers, a gap of ", ("[x]", A, True), " and ", ("[y]", A, True)]], size=7.5, align=L)
    slot(s, m, 25, 168, 130, 288, "[photo: test]", W, size=6)
    slot(s, m, 150, 168, 255, 288, "[photo: test]", W, size=6)
    hl(s, m, (272, 172), (272, 285), G3, .75)
    hl(s, m, (272, 228), (292, 228), G3, .75)
    tm(s, m, 296, 180, 432, 278, "Orders placed on the same day, at the same time and same place", size=6.5, italic=True, color=G4, align=L)


def code_proof(s, x, y, w, h):
    """Duas imagens empilhadas, saída e entrada, com fio de dois tons que sangra à direita. AB InBev p.13."""
    m = M((0, 0, 440, 280), (x, y, w, h))
    tm(s, m, 0, 0, 440, 14, "Word frequency in Python: output", size=7, italic=True, align=L)
    slot(s, m, 0, 18, 440, 158, "[print: word cloud]", size=8)
    tm(s, m, 0, 162, 440, 176, "Word frequency in Python: input", size=7, italic=True, align=L)
    R(s, m, 0, 178, 300, 181, CH); R(s, m, 300, 178, 440, 181, A)
    slot(s, m, 0, 181, 440, 280, "[print: code]", size=8)


def office_visit(s, x, y, w, h):
    """Foto na empresa com moldura de losangos, nome sobre fio e citação entre aspas grandes; etapas acima. Alupar p.18."""
    m = M((0, 0, 440, 180), (x, y, w, h))
    hl(s, m, (0, 0), (0, 178), G3, .5); hl(s, m, (438, 0), (438, 178), G3, .5)
    for i, (cx, t) in enumerate(((88, "First stage"), (212, "Second stage"), (335, "Third stage"))):
        R(s, m, cx - 8, 4, cx + 8, 20, light(F, .8), F, width=.5)
        tm(s, m, cx - 8, 4, cx + 8, 20, str(i + 1), size=6.5, color=F)
        if i: 
            hl(s, m, (cx - 116, 12), (cx - 8, 12), F, .5)
            diamond(s, m, cx - 116, 12, 2.5, F)
        tm(s, m, cx - 60, 21, cx + 60, 35, t, size=6.5, bold=True, italic=True, color=F)
    slot(s, m, 18, 48, 167, 176, "[photo: at the company]", size=6.5, border=F, width=1.0)
    for a, b in ((18, 48), (167, 48), (18, 176), (167, 176)):
        diamond(s, m, a, b, 3, F)
    tm(s, m, 178, 50, 430, 66, "Name", size=8, bold=True, align=L)
    tm(s, m, 178, 66, 430, 80, "Role at the company", size=6.5, color=G4, align=L)
    hl(s, m, (178, 84), (428, 84), F, .75)
    diamond(s, m, 178, 84, 2.5, F); diamond(s, m, 428, 84, 2.5, F)
    tm(s, m, 176, 86, 208, 126, "“", size=22, bold=True, align=L, anchor=TOP)
    tm(s, m, 404, 86, 436, 126, "”", size=22, bold=True, align=RT, anchor=TOP)
    tm(s, m, 212, 106, 402, 170, QT, size=7.5)


def field_scoreboard(s, x, y, w, h):
    """Painel escuro com contagem, linhas de logos e print da call; losango desce ao achado e à barra. BTG Pactual p.26."""
    m = M((0, 0, 440, 182), (x, y, w, h))
    pc = dark(D, .15)
    R(s, m, 0, 0, 440, 114, pc)
    rt(s, m, 6, 2, 200, 36, [[("We went out and talked to ", W), ("[N] offices", light(A, .3), True)]], size=8, align=L)
    for k, yy in enumerate((40, 65, 90)):
        slot(s, m, 8, yy, 62, yy + 18, "[logo]", light(D, .3), size=5.5, color=W)
        hl(s, m, (66, yy + 9), (106, yy + 9), W, .5)
        tm(s, m, 80, yy + 2, 92, yy + 16, "×", size=6, color=W)
        tm(s, m, 110, yy, 200, yy + 18, "[N] offices", size=8, color=W, align=L)
    slot(s, m, 205, 0, 440, 114, "[print: video call]", size=7)
    R(s, m, 205, 0, 440, 14, CH, alpha=70)
    tm(s, m, 207, 0, 300, 14, "[logo]", size=5.5, color=W, align=L)
    tm(s, m, 300, 0, 438, 14, "Call held on [date]", size=5.5, bold=True, color=W, align=RT)
    hl(s, m, (38, 114), (38, 130), INK, .75)
    diamond(s, m, 38, 130, 3, INK)
    rt(s, m, 46, 118, 300, 145, [["However, only ", ("[x]% considered", F, True), " the possibility of making this a long-term goal"]], size=6.5, align=L)
    R(s, m, 45, 150, 280, 172, G4, CH, width=.75)
    R(s, m, 45, 150, 100, 172, light(A, .3), CH, width=.75)
    tm(s, m, 45, 150, 100, 172, "[x]%", size=6.5, bold=True)
    tm(s, m, 220, 150, 278, 172, "[y]%", size=6.5, bold=True, color=W, align=RT)
    rt(s, m, 288, 145, 438, 178, [["What is the main ", ("strategy", F, True), " for this then?"]], size=6.5, align=L)


def tap_walkthrough(s, x, y, w, h):
    """Três celulares sobre uma seta-base, com o toque marcado e rótulos escuros nas pontas. BTG Pactual p.45."""
    m = M((0, 0, 440, 190), (x, y, w, h))
    R(s, m, 0, 0, 215, 28, CH)
    tm(s, m, 6, 0, 210, 28, "We tested the products ourselves", size=6.5, bold=True, color=W, align=L)
    tm(s, m, 90, 34, 350, 50, "Main point of the integration", size=7, bold=True, color=F)
    tm(s, m, 90, 50, 350, 64, "One tap to reach the platform", size=6, bold=True)
    oval_slot(s, m, 40, 50, 16, "[logo]", size=5, border=G4, width=.5)
    oval_slot(s, m, 400, 50, 16, "[logo]", size=5, border=G4, width=.5)
    hl(s, m, (66, 164), (362, 164), CH, 1.0)
    R(s, m, 4, 156, 68, 172, CH)
    tm(s, m, 4, 156, 68, 172, "Start", size=6, bold=True, color=W)
    R(s, m, 364, 156, 436, 172, CH)
    tm(s, m, 364, 156, 436, 172, "End", size=6, bold=True, color=W)
    for cx, t in ((110, "1st touch"), (212, "2nd touch"), (314, "You are in")):
        phone(s, m, cx - 30, 68, cx + 30, 170, "[print]", size=5.5)
        tm(s, m, cx - 45, 172, cx + 45, 186, t, size=6, color=G4, bold=t == "You are in")
    for cx, cy in ((110, 150), (212, 150)):
        oval(s, *m.p((cx + 6, cy)), 18 * m.sx, F, border=W, width=.75)
        tm(s, m, cx - 12, cy - 6, cx + 24, cy + 6, "tap", size=4.5, color=W, bold=True)


def term_sheets(s, x, y, w, h):
    """Três quadros de termos, com três assinaturas sob cada um, em campo escuro. CSN - ArcelorMittal p.32."""
    m = M((0, 0, 440, 292), (x, y, w, h))
    grad(R(s, m, 0, 0, 440, 292, D), ((0, dark(F, .75)), (1, dark(F, .35))), 90)
    hl(s, m, (220, 0), (220, 165), light(F, .3), .5)
    lc = light(F, .4)
    for bx, by, t in ((12, 0, "Bond one, re-tap"), (248, 0, "Bond two"), (130, 158, "Bond three")):
        R(s, m, bx, by, bx + 180, by + 88, None, lc, width=.75)
        tm(s, m, bx, by + 2, bx + 180, by + 18, t, size=7, color=W)
        hl(s, m, (bx + 25, by + 18), (bx + 155, by + 18), W, .5)
        for k, (a, b) in enumerate((("Amount", "[x]mn"), ("Currency", "[ccy]"), ("Cost of debt", "[x]%"), ("Maturity", "[n] years"))):
            yy = by + 21 + k * 16
            tm(s, m, bx + 8, yy, bx + 90, yy + 15, a, size=6, color=W, align=L)
            tm(s, m, bx + 90, yy, bx + 172, yy + 15, b, size=6, color=W, align=RT)
        for i in range(3):
            a0 = bx - 8 + i * 68
            slot(s, m, a0, by + 96, a0 + 60, by + 118, "[signature]", G2, size=5)
            hl(s, m, (a0, by + 118), (a0 + 60, by + 118), W, .5)
            tm(s, m, a0 - 3, by + 119, a0 + 63, by + 131, "Name", size=5.5, color=W)


def signed_termcards(s, x, y, w, h):
    """Quadro de KPIs com título que rompe a borda, garfo e três cartões assinados. Alupar p.2."""
    m = M((0, 0, 440, 265), (x, y, w, h))
    grad(R(s, m, 0, 0, 440, 265, D), ((0, dark(D, .55)), (1, dark(D, .35))), 90)
    lc = light(F, .1)
    pl(s, m, ((110, 10), (4, 10), (4, 68), (436, 68), (436, 10), (330, 10)), lc, .75)
    tm(s, m, 110, 0, 330, 16, "Project summary", size=9, bold=True, color=light(F, .25))
    tm(s, m, 110, 18, 330, 29, "One line that frames the proposal", size=5.5, italic=True, color=W)
    for cx, a, b in ((52, "[x]%", "Avg. IRR"), (165, "[x]%", "Debt"), (270, "[x]%", "Equity"), (385, "[x] bn", "Issuance")):
        tm(s, m, cx - 50, 30, cx + 50, 50, a, size=10, bold=True, color=light(F, .25))
        tm(s, m, cx - 50, 50, cx + 50, 64, b, size=6, italic=True, color=W)
    hl(s, m, (220, 68), (220, 108), lc, .75)
    hl(s, m, (78, 108), (362, 108), lc, .75)
    for cx, t in ((78, "Bridge loan"), (220, "Project finance"), (362, "Green bond")):
        hl(s, m, (cx, 108), (cx, 130), lc, .75)
        R(s, m, cx - 66, 130, cx + 66, 263, None, lc, width=.75)
        tm(s, m, cx - 62, 132, cx + 62, 148, t, size=7, italic=True, color=W)
        hl(s, m, (cx - 60, 149), (cx + 60, 149), lc, .5)
        for k, r in enumerate(("Amount: [x]", "Cost: [x]%", "Maturity: [yr]", "Security: [type]")):
            tm(s, m, cx - 60, 152 + k * 16, cx + 62, 168 + k * 16, r, size=5.5, italic=True, color=W, align=L)
        for i in range(2):
            a0 = cx - 62 + i * 64
            slot(s, m, a0, 222, a0 + 60, 244, "[signature]", G2, size=5)
            hl(s, m, (a0, 244), (a0 + 60, 244), W, .5)
            tm(s, m, a0, 245, a0 + 60, 259, "Name", size=5.5, italic=True, color=W)


# ---------- Moldes: geografia e código ----------
def _pin(s, m, cx, cy, r, c=None, hole=W):
    """Alfinete de mapa: disco e ponta; a ponta marca (cx, cy)."""
    c = c or INK
    top = cy - r * 2.5
    poly(s, m, ((cx - r * .78, top + r * .6), (cx, cy), (cx + r * .78, top + r * .6)), c)
    oval(s, *m.p((cx, top)), 2 * r * m.sx, c)
    oval(s, *m.p((cx, top)), r * .9 * m.sx, hole)


def _star(s, m, cx, cy, r, c):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36); q = r if i % 2 == 0 else r * .45
        pts.append((cx + q * math.cos(a), cy + q * math.sin(a)))
    poly(s, m, pts, c)


def geo_proof(s, x, y, w, h):
    """Dois prints de mapa de calor ligados a rótulos, com KPIs tracejados acima do print do código. Intelbras p.9."""
    m = M((0, 0, 440, 205), (x, y, w, h))
    R(s, m, 0, 0, 440, 205, G1)
    poly(s, m, ((282, 0), (293, 8), (293, 205), (282, 205)), G3)
    R(s, m, 293, 8, 440, 205, W)
    rt(s, m, 6, 2, 278, 56, [["The company leverages a ", ("dense network", None, True), " across major hubs to ensure ", ("availability", None, True), " and strong ", ("channel efficiency", None, True)]], size=7)
    slot(s, m, 4, 62, 142, 124, "[print: city map]", size=6)
    slot(s, m, 142, 84, 280, 172, "[print: heatmap]", W, size=6)
    tm(s, m, 158, 62, 262, 78, "City", size=6.5, color=F)
    R(s, m, 158, 62, 262, 78, None, F, width=.5)
    hl(s, m, (118, 70), (158, 70), F, .5); diamond(s, m, 118, 70, 2.5, F)
    R(s, m, 4, 145, 94, 172, None, F, width=.5)
    tm(s, m, 4, 145, 94, 172, "Metro region", size=6.5, color=F)
    hl(s, m, (94, 158), (175, 158), F, .5); diamond(s, m, 175, 158, 2.5, F)
    _star(s, m, 12, 182, 5, F); tm(s, m, 19, 176, 64, 188, "Peer A", size=5, align=L)
    _star(s, m, 12, 195, 5, D); tm(s, m, 19, 189, 64, 201, "Peer B", size=5, align=L)
    R(s, m, 96, 178, 280, 202, None, A, width=.75, dash=True)
    tm(s, m, 99, 178, 278, 202, "Lead in [market], peers are [more concentrated]", size=5.5)
    for yy, t in ((12, [["Avg. distance to nearest site is ", ("[x] km", F, True)]]), (44, [["Avg. rating per site is ", ("[x]/5", F, True)]])):
        R(s, m, 300, yy, 436, yy + 26, None, A, width=.75, dash=True)
        rt(s, m, 303, yy, 433, yy + 26, t, size=5.5)
    hl(s, m, (284, 25), (300, 25), A, .75)
    slot(s, m, 318, 76, 418, 178, "[print: code]", size=6)
    tm(s, m, 296, 180, 438, 203, "Heat map of site concentration", size=5.5)


def word_freq(s, x, y, w, h):
    """Print do código com legenda, duas tabelas de palavras e linhas tracejadas por tema. Meliuz p.40."""
    m = M((0, 0, 440, 295), (x, y, w, h))
    tm(s, m, 0, 8, 102, 86, "Code written in Python to count word mentions", size=7, bold=True, align=RT)
    R(s, m, 108, 6, 110, 86, INK)
    slot(s, m, 122, 0, 400, 92, "[print: code]", size=7)
    rows = 8
    for tx0, per, mark in ((34, "Q4", {5: "k", 6: "k"}), (240, "Q2", {3: "a", 5: "a", 7: "k"})):
        tm(s, m, tx0, 95, tx0 + 170, 111, per, size=8, bold=True)
        R(s, m, tx0, 112, tx0 + 170, 127, F)
        tm(s, m, tx0, 112, tx0 + 170, 127, "Word frequency", size=6.5, bold=True, color=W)
        R(s, m, tx0, 127, tx0 + 170, 139, G2)
        tm(s, m, tx0, 127, tx0 + 85, 139, "Word", size=6)
        tm(s, m, tx0 + 85, 127, tx0 + 170, 139, "Count", size=6)
        for k in range(rows):
            yy = 139 + k * 15.5
            tm(s, m, tx0, yy, tx0 + 85, yy + 15, "[word]", size=6)
            tm(s, m, tx0 + 85, yy, tx0 + 170, yy + 15, "[n]x", size=6)
            if k in mark:
                R(s, m, tx0 - 2, yy + 1, tx0 + 172, yy + 15, None, INK if mark[k] == "k" else F, width=.75, dash=True)
    R(s, m, 45, 281, 56, 292, None, INK, width=.75, dash=True)
    tm(s, m, 60, 280, 200, 293, "Words tied to theme A", size=5.5, italic=True, align=L)
    R(s, m, 250, 281, 261, 292, None, F, width=.75, dash=True)
    tm(s, m, 265, 280, 410, 293, "Words tied to theme B", size=5.5, italic=True, align=L)


def code_feed_verdict(s, x, y, w, h):
    """Código, celular com feed e donut com logo, ligados por um feixe; caixa de conclusão abaixo. Meliuz p.47."""
    m = M((0, 0, 440, 215), (x, y, w, h))
    slot(s, m, 0, 0, 155, 208, "[print: code]", size=7)
    grad(poly(s, m, ((155, 40), (205, 0), (205, 208), (155, 168)), G3), ((0, G3), (1, G1)), 0)
    phone(s, m, 195, 0, 288, 208, "[print: feed]", size=6.5)
    grad(poly(s, m, ((288, 60), (330, 30), (330, 105), (288, 130)), G2), ((0, G2), (1, W)), 0)
    cc = (372, 66)
    poly(s, m, seg(cc, 22, 42, -90, 225, n=30), F)
    poly(s, m, seg(cc, 22, 42, 225, 270, n=10), G3)
    tm(s, m, 352, 56, 392, 76, "[logo]", size=5.5, color=F, bold=True)
    R(s, m, 335, 113, 342, 120, F); tm(s, m, 344, 110, 382, 123, "Positive", size=5, align=L)
    R(s, m, 386, 113, 393, 120, G3); tm(s, m, 395, 110, 438, 123, "Negative", size=5, align=L)
    R(s, m, 306, 130, 438, 190, None, F, width=.75, dash=True)
    rt(s, m, 310, 130, 434, 190, [["The ", ("model", F, True), " found that ", ("[x]%", F, True), " of mentions were positive"]], size=6.5)


def counter_band(s, x, y, w, h):
    """Faixa escura com contagens em destaque à esquerda e prints das calls com data e nome. Meliuz p.14."""
    m = M((0, 0, 440, 118), (x, y, w, h))
    pc = CH
    R(s, m, 0, 0, 440, 104, pc)
    for yy, t in ((10, "directors"), (36, "current staff"), (65, "former staff")):
        tm(s, m, 6, yy, 30, yy + 18, "[N]", size=8, bold=True, color=light(A, .1))
        tm(s, m, 32, yy, 120, yy + 18, t, size=6.5, color=W, align=L)
    R(s, m, 3, 62, 118, 84, None, W, width=.5, dash=True)
    hl(s, m, (56, 84), (56, 118), G4, .5)
    for cx in (126, 284):
        tm(s, m, cx, 0, cx + 148, 13, "[date]", size=5.5, italic=True, color=W, align=RT)
        slot(s, m, cx, 13, cx + 148, 73, "[print: video call]", size=6)
        tm(s, m, cx, 75, cx + 148, 88, "NAME", size=7, bold=True, color=W)
        tm(s, m, cx, 88, cx + 148, 101, "Role, company", size=5.5, color=W)


def field_test_phone(s, x, y, w, h):
    """Celular grande com fios para o achado tracejado e a moldura da tabela; segundo celular com o registro. Meliuz p.116."""
    m = M((0, 0, 440, 208), (x, y, w, h))
    R(s, m, 122, 0, 438, 28, None, INK, width=.75, dash=True)
    tm(s, m, 126, 0, 434, 28, "[what we did in the field, in one sentence]", size=6.5, align=L)
    phone(s, m, 0, 0, 84, 208, "[print: app]", size=6.5)
    hl(s, m, (70, 14), (122, 14), INK, .75)
    rrm(s, m, 120, 36, 358, 208, W, r=26, border=INK, width=.75)
    tm(s, m, 130, 40, 350, 55, "Main findings of the field test", size=6.5, bold=True)
    hl(s, m, (130, 56), (350, 56), INK, .75)
    for k in range(3):
        tm(s, m, 134, 60 + k * 30, 348, 90 + k * 30, "[finding from the test, two lines long]", size=6, align=L)
    R(s, m, 134, 152, 346, 200, None, A, width=1.0, dash=True)
    tm(s, m, 136, 152, 344, 200, "[fee table from the app]", size=6.5, color=G4)
    ss.line(s, *m.p((58, 165)), *m.p((134, 176)), A, 1.0, dash=True)
    phone(s, m, 366, 44, 438, 208, "[print: call log]", size=5.5)
    tm(s, m, 362, 30, 440, 44, "Call history", size=6, bold=True)


def chat_bubbles(s, x, y, w, h):
    """Pílula com a pergunta, bolhas cinza com avatar e cartão em L com temas. Meliuz p.124."""
    m = M((0, 0, 440, 205), (x, y, w, h))
    R(s, m, 0, 0, 150, 24, CH)
    tm(s, m, 5, 0, 145, 24, "Why did you choose us?", size=6.5, bold=True, color=W, align=L)
    ss.line(s, *m.p((150, 12)), *m.p((172, 12)), INK, .75, dash=True)
    diamond(s, m, 172, 12, 3, INK)
    rt(s, m, 178, 2, 390, 24, [[("[x]%", F, True), " of those interviewed used it first"]], size=6.5, align=L)
    for bx, by, bw, bh in ((12, 36, 118, 42), (150, 36, 118, 48), (290, 48, 120, 50), (12, 104, 118, 42), (150, 110, 80, 40), ):
        rrm(s, m, bx, by, bx + bw, by + bh, G1, r=9)
        tm(s, m, bx + 4, by, bx + bw - 4, by + bh, "[message from a real customer]", size=5.5, color=G4)
        oval(s, *m.p((bx + 2, by + bh + 7)), 11 * m.sx, G3)
    R(s, m, 233, 123, 437, 205, CH)
    R(s, m, 236, 120, 440, 202, W)
    tm(s, m, 242, 121, 400, 136, "Most mentioned topics", size=6, bold=True, align=L)
    for i, t in enumerate(("Theme one", "Theme two", "Theme three")):
        cx = 272 + i * 65
        oval(s, *m.p((cx, 156)), 28 * m.sx, None, border=INK, width=.75)
        tm(s, m, cx - 12, 150, cx + 12, 162, "[icon]", size=4.5, color=G4)
        tm(s, m, cx - 31, 172, cx + 31, 198, t, size=5.5)


def field_selfie(s, x, y, w, h):
    """Faixa da borda esquerda com lugar e alfinete, foto contornada subindo acima dela. Mercado Libre p.14."""
    m = M((0, 0, 440, 125), (x, y, w, h))
    R(s, m, 0, 78, 240, 122, D)
    tm(s, m, 90, 78, 180, 122, "City, state", size=9, italic=True, color=W, align=RT)
    _pin(s, m, 196, 110, 8, W, D)
    slot(s, m, 212, 0, 438, 122, "[photo: field trip]", size=8, r=8, border=D, width=1.5)


def platform_test(s, x, y, w, h):
    """Print do painel real, com faixa de título e caixas que repetem os números por cima. Mercado Libre p.28."""
    m = M((0, 0, 440, 170), (x, y, w, h))
    R(s, m, 4, 30, 140, 104, None, INK, width=.5, dash=True)
    tm(s, m, 10, 33, 136, 60, "Growth after using the tool:", size=6.5, italic=True, align=L)
    poly(s, m, ((34, 80), (45, 66), (56, 80), (49, 80), (49, 92), (41, 92), (41, 80)), D)
    tm(s, m, 60, 66, 132, 92, "[x]%", size=12, align=L)
    hl(s, m, (4, 118), (140, 118), INK, .5)
    rt(s, m, 8, 122, 138, 166, [["We conclude the tool ", ("holds real value", D, True), " for the seller"]], size=6.5, align=L)
    R(s, m, 155, 0, 440, 170, W, G3, width=.5)
    R(s, m, 155, 0, 440, 16, D)
    tm(s, m, 160, 0, 436, 16, "Website print screen", size=6, italic=True, color=W, align=L)
    slot(s, m, 155, 16, 440, 170, "[print: real dashboard]", size=7.5)
    for a, b, t in ((172, 290, "[x] > [y]"), (305, 425, "[metric] = [x]%")):
        R(s, m, a, 22, b, 54, W, INK, width=.75)
        tm(s, m, a + 2, 24, b - 2, 52, t, size=7.5, bold=True)


def code_receipt(s, x, y, w, h):
    """Ranking de palavras em pílulas ao lado do print do editor. Mercado Libre p.7."""
    m = M((0, 0, 440, 245), (x, y, w, h))
    tm(s, m, 0, 2, 440, 22, "Most common words in the shareholder letters", size=7.5, italic=True, color=G4)
    for cx, t in ((24, "No."), (112, "Transcript"), (205, "Q"), (330, "Python script")):
        tm(s, m, cx - 24, 24, cx + 24 if cx < 100 else cx + 50, 42, t, size=7, bold=True)
    hl(s, m, (2, 44), (438, 44), INK, .75)
    for k in range(5):
        yy = 52 + k * 37
        R(s, m, 6, yy + 3, 40, yy + 26, G2)
        tm(s, m, 6, yy + 3, 40, yy + 26, str(k + 1), size=7)
        c = A if k == 0 else D
        rrm(s, m, 50, yy, 228, yy + 28, c, r=5)
        tm(s, m, 56, yy, 170, yy + 28, "[word]", size=7, bold=True, color=W)
        tm(s, m, 170, yy, 224, yy + 28, "[n]", size=7, bold=True, color=W, align=RT)
    slot(s, m, 240, 50, 436, 240, "[print: code]", size=8, r=12)


def book_authority(s, x, y, w, h):
    """Capa saltando da placa cinza com citação, e tira escura com o que a ideia significa. Mercado Libre p.4."""
    m = M((0, 0, 440, 118), (x, y, w, h))
    R(s, m, 0, 15, 440, 92, G1)
    slot(s, m, 345, 0, 412, 88, "[book cover]", size=5.5, border=G3, width=.5)
    rt(s, m, 10, 20, 338, 88, [["“[quote from the book, with ", ("key words in bold", D, True), "]”"]], size=8, align=L)
    R(s, m, 0, 92, 440, 116, D)
    tm(s, m, 4, 92, 436, 116, "What the idea means for this company", size=8, bold=True, italic=True, color=W)


def zoom_stack(s, x, y, w, h):
    """Prints de call sobrepostos, com bandeirinha escura em cada um, em painel com trilho e entalhe. Mercado Libre p.11."""
    m = M((0, 0, 440, 205), (x, y, w, h))
    R(s, m, 4, 0, 440, 202, G1, G3, width=.25)
    R(s, m, 0, 0, 8, 202, D)
    poly(s, m, ((8, 148), (15, 156), (8, 164)), D)
    tm(s, m, 14, 3, 430, 22, "Interviews with staff across the segments", size=8, italic=True, align=L)
    for ax, ay, bx, by in ((32, 35, 150, 108), (272, 36, 408, 108), (182, 108, 252, 148), (150, 60, 215, 108), (215, 60, 280, 108)):
        R(s, m, ax - 4, ay - 4, ax + 18, ay + 6, D)
        slot(s, m, ax, ay, bx, by, "[print: call]", size=5.5, border=W, width=.75)
    rt(s, m, 60, 152, 400, 196, [[("“[quote from a real interview, with ", None, False, True), ("key words", D, True, True), ("]”", None, False, True)]], size=8)


def race(s, x, y, w, h):
    """Corrida cronometrada: celulares numerados sobre barra tingida, relógio e tempo no fim. Nubank p.8."""
    m = M((0, 0, 440, 135), (x, y, w, h))
    for bx, bn, t, n, tag in ((0, 215, "Our simulation", 3, "[n] steps"), (228, 440, "Peer simulation", 2, "[n] steps")):
        tm(s, m, bx + 4, 0, bn, 12, t, size=6, color=G4, align=L)
        R(s, m, bx + 2, 42, bn, 78, light(F, .5))
        pitch = 45 if n == 3 else 52
        for i in range(n):
            px = bx + 10 + i * pitch
            phone(s, m, px, 14, px + pitch - 4, 100, "[print]", size=5)
            oval(s, *m.p((px + 5, 18)), 14 * m.sx, F, border=W, width=.5)
            tm(s, m, px - 3, 12, px + 13, 24, str(i + 1), size=5, bold=True, color=W)
        ex = bx + 10 + n * pitch
        oval(s, *m.p((ex + 9, 60)), 14 * m.sx, None, border=W, width=1.0)
        tm(s, m, ex + 18, 44, bn - 2, 76, "[time]", size=8, bold=True, color=W, align=L)
        R(s, m, bx + 12, 104, bx + 72, 118, G1)
        tm(s, m, bx + 12, 104, bx + 72, 118, tag, size=5.5, bold=True)
    shadow(rrm(s, m, 352, 92, 438, 133, light(F, .85), r=6), 3, 1, 1, .25)
    tm(s, m, 355, 92, 435, 133, "[the gap as a yearly cost to the user]", size=5.5, bold=True)


def pin_density(s, x, y, w, h):
    """Manchas tonais, alfinetes por concentração e painel de código com selo. Nubank p.25."""
    m = M((0, 0, 440, 290), (x, y, w, h))
    tm(s, m, 0, 0, 270, 16, "Location in the city", size=7, color=G4, align=L)
    outer = ((75, 30), (108, 20), (120, 55), (145, 80), (172, 105), (222, 135), (240, 175), (262, 200), (255, 245), (190, 242), (160, 225), (120, 195), (85, 200), (45, 165), (18, 150), (30, 95), (50, 62))
    poly(s, m, rpoly(outer, 18), light(F, .75))
    poly(s, m, rpoly(((60, 95), (115, 60), (150, 100), (190, 140), (165, 180), (110, 165), (70, 155), (40, 135)), 22), light(F, .45))
    poly(s, m, rpoly(((70, 110), (115, 85), (145, 115), (140, 155), (100, 150), (75, 140)), 18), F)
    poly(s, m, rpoly(((92, 118), (112, 108), (128, 128), (112, 145), (92, 140)), 10), dark(F, .3))
    for cx, cy, r in ((55, 105, 13), (100, 90, 14), (150, 95, 10), (84, 180, 8)):
        _pin(s, m, cx, cy, r, INK)
    rrm(s, m, 275, 8, 438, 182, G2, r=16)
    tm(s, m, 275, 8, 438, 182, "[print: code]", size=7, color=G4)
    rrm(s, m, 404, 0, 440, 34, light(F, .55), r=8)
    tm(s, m, 404, 0, 440, 34, "[logo]", size=4.5, color=D)
    for cy, r, t in ((226, 11, "High concentration"), (264, 9, "Low concentration")):
        _pin(s, m, 298, cy, r, INK if r == 11 else G4)
        tm(s, m, 316, cy - 22, 438, cy, t, size=6, align=L)
    tm(s, m, 40, 248, 230, 262, "Income level", size=6)
    hl(s, m, (0, 247), (280, 247), G3, .5)
    grad(R(s, m, 25, 266, 245, 280, F), ((0, light(F, .75)), (1, dark(F, .3))), 0)


def form_exhibit(s, x, y, w, h):
    """Pílula de título, formulário alto à esquerda, fio vertical, logos e três achados. Nubank p.27."""
    m = M((0, 0, 440, 255), (x, y, w, h))
    rrm(s, m, 0, 0, 332, 34, F, r=6)
    tm(s, m, 10, 0, 325, 34, "What we found across incumbents", size=8.5, color=W, align=L)
    slot(s, m, 5, 50, 150, 252, "[print: real form]", size=7)
    R(s, m, 154, 50, 156, 252, F)
    for i in range(4):
        slot(s, m, 170 + i * 67, 50, 230 + i * 67, 88, "[logo]", size=6)
    for i, (a, b) in enumerate((("Finding one: ", "one short line on what the form shows"), ("Finding two: ", "one short line on what the form shows"), ("Finding three: ", "one short line on what the form shows"))):
        rt(s, m, 170, 98 + i * 52, 438, 146 + i * 52, [[(a, F, True), (b,)]], size=7.5, align=L)


def pin_census(s, x, y, w, h):
    """Print de mapa com alfinetes por rede, legenda que abre numa parede e nota com a leitura. RD Saude p.14."""
    m = M((0, 0, 440, 172), (x, y, w, h))
    R(s, m, 0, 0, 440, 172, G1)
    R(s, m, 3, 15, 88, 155, None, A, width=.75, dash=True)
    pcs = (F, A, ss.NEG, INK)
    for k, (c, t) in enumerate(zip(pcs, ("Our chain", "Chain B", "Chain C", "Other"))):
        _pin(s, m, 14, 42 + k * 33, 5, c)
        tm(s, m, 24, 26 + k * 33, 86, 44 + k * 33, t, size=6, bold=True, color=c if c != A else dark(A, .15), align=L)
    poly(s, m, ((88, 15), (122, 3), (122, 165), (88, 155)), G3)
    slot(s, m, 122, 3, 365, 165, "", W)
    tm(s, m, 126, 148, 361, 163, "[map: real street print]", size=6, color=G4)
    R(s, m, 122, 3, 365, 165, None, A, width=.75, dash=True)
    for cx, cy, c in ((150, 58, A), (178, 50, INK), (195, 88, INK), (218, 68, A), (232, 40, INK), (243, 98, ss.NEG), (258, 75, A), (272, 104, INK), (290, 65, INK), (300, 122, INK), (248, 120, F), (332, 110, INK), (210, 135, INK), (170, 120, A)):
        _pin(s, m, cx, cy, 4.5, c)
    R(s, m, 375, 65, 438, 104, W, A, width=.75, dash=True)
    tm(s, m, 377, 65, 436, 104, "The single reading", size=5.5, bold=True)
    ss.line(s, *m.p((365, 84)), *m.p((375, 84)), A, .75, dash=True)


def phone_call_stack(s, x, y, w, h):
    """Dois pares de celulares sobrepostos ao lado de uma frase grande com a contagem. RBI p.18."""
    m = M((0, 0, 440, 150), (x, y, w, h))
    for ax, ay, t in ((12, 5, ""), (42, 25, "[call screen]"), (102, 2, ""), (132, 22, "[call screen]")):
        phone(s, m, ax, ay, ax + 58, ay + 118, t, size=4.5)
    rt(s, m, 205, 12, 438, 130, [["We spoke to [N] ", ("sources", None, False), " to understand how the firm supports them and ", ("keeps them on track", F, True)]], size=10, align=L)


def news_card(s, x, y, w, h):
    """Quadro com faixa de manchete, selo do veículo sobreposto, resumo e data. Vibra p.14."""
    m = M((0, 0, 440, 118), (x, y, w, h))
    R(s, m, 1, 2, 439, 116, W, F, width=1.0)
    R(s, m, 1, 6, 439, 34, dark(F, .3))
    tm(s, m, 6, 6, 340, 34, "[headline from a real article]", size=7.5, bold=True, color=W, align=L)
    R(s, m, 352, 0, 436, 38, W, INK, width=.75)
    tm(s, m, 352, 0, 436, 38, "[logo]", size=7, color=G4)
    tm(s, m, 6, 38, 200, 52, "Summary:", size=6.5, color=G4, align=L)
    for k in range(2):
        tm(s, m, 14, 54 + k * 18, 430, 70 + k * 18, "•  [what the article says, in one line]", size=6.5, align=L)
    tm(s, m, 340, 99, 434, 114, "[date]", size=6.5, bold=True, italic=True, align=RT)


# ---------- Moldes: citações ----------
def expert_dossier(s, x, y, w, h):
    """Retrato sobre placa com comparação de métodos, credencial com fio grosso e faixa com a citação. AB InBev p.6."""
    m = M((0, 0, 440, 285), (x, y, w, h))
    R(s, m, 165, 0, 440, 100, G1)
    R(s, m, 437, 40, 440, 100, A)
    tm(s, m, 180, 4, 430, 22, "Common approach", size=7, italic=True, color=G4, align=L)
    tm(s, m, 180, 22, 430, 42, "Metric one > metric two", size=8, align=L)
    tm(s, m, 180, 54, 430, 72, "The expert's approach", size=7, italic=True, color=G4, align=RT)
    tm(s, m, 180, 72, 430, 94, "Metric three > metric four", size=8, align=RT)
    slot(s, m, 0, 12, 165, 218, "[photo: cut-out portrait]", size=7)
    R(s, m, 175, 118, 178, 150, INK)
    tm(s, m, 184, 116, 438, 134, "Role at the institution", size=7.5, bold=True, align=L)
    tm(s, m, 184, 134, 438, 152, "Name", size=7.5, align=L)
    R(s, m, 0, 218, 440, 285, "5A5A5A")
    rt(s, m, 6, 220, 434, 262, [[("“[quote from a real interview, ", W), ("key phrase", A, True), ("]”", W)]], size=8.5, align=L)
    tm(s, m, 6, 264, 434, 283, "[source of the quote]", size=6.5, italic=True, color=G3, align=L)


def pennant_asked(s, x, y, w, h):
    """Placa que afunila em ponta, palavras em destaque, conta-fio até moldura tracejada com três cartões. AB InBev p.20."""
    m = M((0, 0, 440, 255), (x, y, w, h))
    def bead(cx, cy):
        rrm(s, m, cx - 8, cy - 4, cx + 8, cy + 4, W, r=4, border=INK, width=.75)
    hl(s, m, (0, 32), (72, 32), INK, .75)
    bead(40, 32)
    poly(s, m, ((72, 0), (440, 0), (440, 70), (256, 92), (72, 70)), G1)
    for i, t in enumerate(("Word one", "Word two", "Word three")):
        cx = 72 + 61 + i * 123
        tm(s, m, cx - 58, 6, cx + 58, 28, t, size=8, color=dark(A, .1))
        if i: hl(s, m, (cx - 61, 6), (cx - 61, 28), G3, .5)
    tm(s, m, 85, 32, 428, 62, "And this is where the company is headed, as [name] put it", size=6.5)
    hl(s, m, (256, 92), (256, 124), INK, .5)
    bead(256, 124)
    tm(s, m, 72, 109, 240, 122, "We asked [name] about...", size=5.5, color=G4, align=L)
    R(s, m, 72, 124, 440, 252, None, G4, width=.5, dash=True)
    for i, t in enumerate(("Topic one", "Topic two", "Topic three")):
        cx = 78 + i * 121
        R(s, m, cx, 130, cx + 115, 246, G1)
        tm(s, m, cx, 133, cx + 115, 153, t, size=8, color=dark(A, .1))
        tm(s, m, cx + 4, 155, cx + 111, 244, "[what the interviewee said, in a few bold-led lines]", size=6, color=G4)


def video_quote(s, x, y, w, h, kind="wired"):
    """Print de vídeo com citação ao lado, em três arranjos: 'wired' Alupar p.11, 'grid' Cosan p.6, 'card' Vasta p.13."""
    if kind == "wired":
        m = M((0, 0, 440, 128), (x, y, w, h))
        slot(s, m, 6, 3, 215, 124, "[print: interview still]", size=7, border=D, width=1.0)
        R(s, m, 170, 100, 215, 124, G3)
        tm(s, m, 170, 100, 215, 124, "[call]", size=5, color=W)
        for a, b in ((6, 3), (215, 3), (6, 124), (215, 124)):
            diamond(s, m, a, b, 2.5, D)
        hl(s, m, (215, 62), (243, 62), D, .75); diamond(s, m, 241, 62, 2.5, D)
        R(s, m, 243, 2, 438, 126, W, D, width=.75)
        for a, b in ((243, 2), (438, 2), (243, 126), (438, 126)):
            diamond(s, m, a, b, 2.5, D)
        rt(s, m, 250, 6, 432, 24, [[("Name", None, True), ("  Role", G4)]], size=8, align=L)
        tm(s, m, 250, 26, 432, 122, QT, size=7.5)
    elif kind == "grid":
        m = M((0, 0, 440, 152), (x, y, w, h))
        R(s, m, 1, 1, 439, 151, light(F, .94), dark(F, .3), width=.75)
        for i in range(4):
            cx, cy = 12 + (i % 2) * 96, 22 + (i // 2) * 55
            slot(s, m, cx, cy, cx + 94, cy + 53, "[print: call]", size=6)
        rt(s, m, 215, 18, 430, 106, [[("“[quote from a real interview, with ", None), ("key clauses in bold", None, True), ("]”", None)]], size=8, align=L)
        tm(s, m, 215, 112, 430, 134, "Name, role at the company", size=7.5, bold=True, color=dark(F, .3))
    else:
        m = M((0, 0, 440, 145), (x, y, w, h))
        ca = F
        poly(s, m, rpoly(((5, 0), (440, 0), (440, 142), (5, 142)), 18), light(F, .9))
        slot(s, m, 22, 8, 118, 72, "[print]", size=6, r=6, border=ca, width=1.0)
        for ax, ay in ((130, 8), (130, 42), (22, 78), (55, 78), (88, 78)):
            slot(s, m, ax, ay, ax + 30, ay + 30, "[print]", size=4.5, r=4, border=ca, width=.75)
        tm(s, m, 170, 2, 220, 34, "“", size=20, bold=True, color=ca, align=L, anchor=TOP)
        rrm(s, m, 400, 3, 430, 25, G2, r=3)
        tm(s, m, 400, 3, 430, 25, "[logo]", size=4.5, color=G4)
        rt(s, m, 172, 26, 432, 110, [[("[quote from a real interview, with ", None), ("bold", None, True), (" and ", None), ("accent", ca, True), (" emphasis]", None)]], size=8, align=L)
        R(s, m, 5, 118, 440, 142, dark(F, .3))
        tm(s, m, 12, 118, 435, 142, "Name, role and company", size=7.5, color=W, align=L)


def video_still_quote(s, x, y, w, h):
    """Still de vídeo ligado por fio com losango a um cartão de citação. Alupar p.11."""
    video_quote(s, x, y, w, h, "wired")


def video_grid_quote(s, x, y, w, h):
    """Grade de call 2x2 e citação, em cartão claro com borda. Cosan p.6."""
    video_quote(s, x, y, w, h, "grid")


def video_card_quote(s, x, y, w, h):
    """Cartão que sangra à direita, grade de stills, aspas em destaque e barra de nome. Vasta p.13."""
    video_quote(s, x, y, w, h, "card")


def pentagon_quotes(s, x, y, w, h):
    """Duas faixas pontudas, alternadas, com retrato redondo na ponta plana. BTG Pactual p.33."""
    m = M((0, 0, 440, 142), (x, y, w, h))
    poly(s, m, ((110, 4), (440, 4), (440, 66), (110, 66), (82, 35)), light(A, .85))
    poly(s, m, ((0, 74), (352, 74), (380, 104), (352, 136), (0, 136)), light(F, .85))
    rt(s, m, 112, 8, 382, 48, [[("“[quote from a real interview, ", None), ("key phrase", F, True), ("]”", None)]], size=7, align=L)
    tm(s, m, 112, 48, 382, 63, "Name, role", size=6, color=G4, align=RT)
    rt(s, m, 72, 78, 352, 118, [[("“[quote from a real interview, ", None), ("key phrase", F, True), ("]”", None)]], size=7, align=L)
    tm(s, m, 72, 118, 352, 133, "Name, role", size=6, color=G4, align=RT)
    oval_slot(s, m, 408, 36, 30, "[photo]", size=6)
    oval_slot(s, m, 36, 105, 30, "[photo]", size=6)


def anonymized_quote(s, x, y, w, h):
    """Painel cinza com retrato em losango desfocado e citações de lados alternados. Meliuz p.15."""
    m = M((0, 0, 440, 250), (x, y, w, h))
    R(s, m, 0, 0, 440, 250, G1)
    diamond_slot(s, m, 66, 66, 58, 58, "[photo, blurred]", G3, size=6)
    diamond_slot(s, m, 372, 186, 58, 58, "[photo, blurred]", G3, size=6)
    rt(s, m, 136, 14, 428, 90, [[("“[quote from a real interview, ", None), ("highlighted sentence", F, True), ("]”", None)]], size=8, align=L)
    tm(s, m, 136, 94, 428, 112, "Former employee*", size=7, bold=True, align=L)
    rt(s, m, 12, 132, 304, 206, [[("“[quote from a real interview, ", None), ("highlighted sentence", F, True), ("]”", None)]], size=8, align=RT)
    tm(s, m, 12, 210, 304, 226, "Name, current employee", size=7, bold=True, align=RT)
    tm(s, m, 12, 232, 300, 248, "*Anonymity preserved on request", size=5.5, italic=True, color=G4, align=L)


def name_tab(s, x, y, w, h):
    """Etiqueta de nome com sombra sobre a borda do painel, print da call e citação centrada. Rede D'Or p.15."""
    m = M((0, 0, 425, 200), (x, y, w, h))
    R(s, m, 0, 15, 425, 200, G1)
    shadow(R(s, m, 85, 0, 340, 30, W, G3, width=.5), 4, 1, 2, .35)
    rt(s, m, 85, 0, 340, 30, [[("Name", None, True), (", role at the firm",)]], size=8)
    slot(s, m, 138, 40, 288, 115, "[print: call]", size=7)
    rt(s, m, 18, 122, 408, 195, [[("“[quote from a real interview, with ", None), ("two phrases", A, True), (" in ", None), ("accent", A, True), ("]”", None)]], size=8.5)


def timeline_bookends(s, x, y, w, h):
    """Linha de fitas ao centro, com retrato e citação em cada ponta; último nó na cor do tema. Sabesp p.17."""
    m = M((0, 0, 440, 130), (x, y, w, h))
    rw, rh = 72, 30
    def rb(ox, oy, mirror=False):
        return [(ox + (rw - a / 137.8 * rw if mirror else a / 137.8 * rw), oy + b / 52.5 * rh) for a, b in RIB]
    ty = 50
    hl(s, m, (115, ty + 15), (345, ty + 15), G4, 1.0)
    cols = (D, dark(F, .3), F, light(F, .35), A)
    for i in range(5):
        ox = 112 + i * 40
        poly(s, m, rb(ox + 30, ty, True), G2)
    for i, c in enumerate(cols):
        ox = 112 + i * 40
        poly(s, m, rb(ox, ty), c)
        tm(s, m, ox + 10, ty + 2, ox + 62, ty + 28, str(2004 + i * 5), size=6, bold=True, color=W)
        up = i % 2 == 0
        y0, y1 = (ty + 2, ty - 26) if up else (ty + rh - 2, ty + rh + 26)
        hl(s, m, (ox + 36, y0), (ox + 36, y1), c, .5)
        poly(s, m, ((ox + 36, y1), (ox + 48, y1), (ox + 36, y1 + (6 if up else -6))), c)
        tb = (y1 - 2, y1 + 12) if up else (y1 - 12, y1 + 2)
        tm(s, m, ox + 50 if not up else ox + 38, tb[0] - (10 if up else 0), ox + 104, tb[1] - (10 if up else 0), "Target", size=5.5, bold=i == 4, color=dark(A, .15) if i == 4 else INK, align=L)
    slot(s, m, 0, 8, 42, 122, "[photo]", size=5.5)
    R(s, m, 44, 28, 108, 104, G1)
    tm(s, m, 46, 30, 106, 102, QT, size=5.5, italic=True)
    slot(s, m, 398, 8, 440, 122, "[photo]", size=5.5)
    R(s, m, 332, 28, 396, 104, G1)
    tm(s, m, 334, 30, 394, 102, QT, size=5.5, italic=True)


def quote_spine(s, x, y, w, h):
    """Moldura fina com lombada angular, foto, firma, regra e aspas inclinadas nos cantos. Vibra p.29."""
    m = M((0, 0, 390, 215), (x, y, w, h))
    R(s, m, 0, 0, 390, 215, W, G3, width=.75)
    poly(s, m, ((0, 0), (10, 0), (10, 92), (14, 98), (14, 215), (0, 215)), CH)
    slot(s, m, 18, 5, 172, 92, "[photo: team and source]", size=6.5, border=INK, width=.5)
    tm(s, m, 180, 58, 375, 74, "Name", size=8, bold=True, align=L)
    tm(s, m, 180, 74, 375, 90, "Role at the firm", size=7, italic=True, color=G4, align=L)
    slot(s, m, 290, 6, 382, 48, "[logo]", size=6.5)
    hl(s, m, (14, 97), (390, 97), G3, .75)
    for cx in (24, 356):
        for k in (0, 10):
            poly(s, m, ((cx + k + 5, 104), (cx + k + 9, 104), (cx + k + 4, 120), (cx + k, 120)), INK)
    rt(s, m, 40, 122, 370, 208, [[("[quote from a real interview, ", G4), ("key sentence in bold", None, True), ("]", G4)]], size=8)


# ---------- Moldes: gestão ----------
def handover_ledger(s, x, y, w, h):
    """Linhas tracejadas: logo, quem saiu e datas, seta pontilhada, quem entrou e ano. Kering - Moncler p.7."""
    m = M((0, 0, 440, 250), (x, y, w, h))
    R(s, m, 0, 0, 440, 250, G1)
    for k in range(8):
        yy = 2 + k * 31
        slot(s, m, 6, yy + 5, 86, yy + 26, "[logo]", W, size=5.5)
        tm(s, m, 92, yy, 228, yy + 30, "Name (2015-2020)", size=6, align=RT)
        ss.line(s, *m.p((234, yy + 15)), *m.p((314, yy + 15)), G4, .5, dash=True)
        poly(s, m, ((314, yy + 11), (321, yy + 15), (314, yy + 19)), G4)
        tm(s, m, 328, yy, 438, yy + 30, "Name (2021)", size=6, align=L)
        if k < 7:
            ss.line(s, *m.p((6, yy + 31)), *m.p((436, yy + 31)), G3, .5, dash=True)


def score_ruler(s, x, y, w, h):
    """Trilha com marcas de 0 a 4, fichas de logo pela nota, janela no empate e régua de critérios. Meliuz p.48."""
    m = M((0, 0, 440, 118), (x, y, w, h))
    R(s, m, 0, 0, 296, 30, CH)
    tm(s, m, 5, 0, 292, 30, "We built our own metric to score each peer", size=6.5, bold=True, color=W, align=L)
    ss.line(s, *m.p((6, 30)), *m.p((6, 76)), G4, .5, dash=True)
    ss.line(s, *m.p((6, 76)), *m.p((22, 76)), G4, .5, dash=True)
    R(s, m, 22, 74, 292, 78, G2)
    for i in range(5):
        tx0 = 22 + i * 67.5
        ss.line(s, *m.p((tx0, 58)), *m.p((tx0, 94)), G4, .5, dash=True)
        tm(s, m, tx0 - 8, 95, tx0 + 8, 108, str(i), size=6, color=G4)
    for t, on in ((105, False), (168, False), (185, False), (202, False), (240, True), (260, True)):
        oval_slot(s, m, t, 76, 10, "", G3 if not on else light(F, .5), border=W, width=.75)
        tm(s, m, t - 14, 80, t + 14, 92, "", size=4)
    R(s, m, 226, 58, 274, 94, None, F, width=.75)
    tm(s, m, 100, 44, 290, 57, "[logo] tokens placed by score", size=5.5, color=G4)
    for i, t in enumerate(("Criterion A", "Criterion B", "Criterion C", "Criterion D", "Criterion E", "Criterion F")):
        cx = 300 + (i % 3) * 47
        cy = 0 + (i // 3) * 20
        R(s, m, cx, cy, cx + 45, cy + 18, G1)
        tm(s, m, cx, cy, cx + 45, cy + 18, "Test " + t[-1], size=5, bold=True)
    R(s, m, 300, 44, 440, 116, G1)
    for k, t in enumerate(("1 - Poor", "2 - Fair", "3 - Good", "4 - Excellent")):
        tm(s, m, 305, 47 + k * 17, 436, 63 + k * 17, t, size=6, bold=True, align=L)


def logo_cv(s, x, y, w, h):
    """Quadros tracejados de logos por competência em volta da mesa do conselho. Rede D'Or p.20."""
    m = M((0, 0, 440, 295), (x, y, w, h))
    tm(s, m, 90, 0, 350, 15, "Name", size=8.5, bold=True)
    tm(s, m, 90, 15, 350, 30, "Former chair (years)", size=6.5)
    slot(s, m, 118, 34, 190, 58, "[logo]", size=5.5); slot(s, m, 250, 34, 322, 58, "[logo]", size=5.5)
    R(s, m, 172, 62, 268, 295, light(A, .7))
    oval(s, *m.p((220, 47)), 28 * m.sx, dark(F, .3))
    oval(s, *m.p((220, 47)), 14 * m.sx, D)
    R(s, m, 207, 66, 233, 86, W, G3, width=.25)
    for cy in (108, 188, 262):
        for cx, sgn in ((172, -1), (268, 1)):
            oval(s, *m.p((cx + sgn * 8, cy)), 30 * m.sx, dark(F, .3))
            oval(s, *m.p((cx + sgn * 8, cy)), 15 * m.sx, D)
            R(s, m, (cx if sgn > 0 else cx) - 18 if sgn > 0 else cx + 2, cy - 12, (cx - 2) if sgn > 0 else cx + 18, cy + 12, W, G3, width=.25)
    for bx, by, t in ((0, 62, "Finance"), (0, 180, "Marketing"), (295, 62, "Healthcare"), (295, 180, "Insurance")):
        R(s, m, bx, by, bx + 145, by + 108, None, D, width=.75, dash=True)
        tm(s, m, bx, by + 2, bx + 145, by + 18, t, size=7.5, bold=True, color=D)
        for i in range(4):
            cx = bx + 7 + (i % 2) * 68
            cy = by + 22 + (i // 2) * 41
            slot(s, m, cx, cy, cx + 62, cy + 36, "[logo]", size=5.5)


def year_ticker(s, x, y, w, h):
    """Faixa cheia com bloco de título escuro e quadros tracejados de ano e logo. Senior Sistemas p.23."""
    m = M((0, 0, 440, 70), (x, y, w, h))
    R(s, m, 0, 2, 440, 66, F)
    poly(s, m, ((0, 2), (72, 2), (90, 12), (90, 56), (72, 66), (0, 66)), dark(F, .3))
    tm(s, m, 5, 2, 75, 66, "Deal history", size=7.5, bold=True, color=W)
    for i, yr in enumerate((2021, 2022, 2023, 2024, 2024, 2024, 2025)):
        cx = 96 + i * 49
        R(s, m, cx, 8, cx + 45, 60, None, W, width=.5, dash=True)
        tm(s, m, cx, 9, cx + 45, 26, str(yr), size=6.5, bold=True, color=W)
        sp = R(s, m, cx + 3, 28, cx + 42, 56, W, alpha=35)
        tm(s, m, cx + 3, 28, cx + 42, 56, "[logo]", size=5, color=W)


def one_of_seven(s, x, y, w, h):
    """Imagem de reunião, nota, divisa para a ficha com o resultado e fileira de assinaturas. Vasta p.35."""
    m = M((0, 0, 440, 235), (x, y, w, h))
    hl(s, m, (0, 0), (0, 225), G3, .5); hl(s, m, (438, 0), (438, 225), G3, .5)
    slot(s, m, 12, 5, 170, 140, "[image: board meeting]", size=7)
    shadow(R(s, m, 182, 6, 434, 82, light(F, .92)), 4, 2, 2, .3)
    rt(s, m, 188, 8, 428, 80, [[("Board seats are ", None, False, True), ("in proportion to ownership", None, True, True), (". We added a clause to ", None, False, True), ("secure one seat", None, True, True)]], size=7.5)
    pl(s, m, ((286, 90), (308, 100), (330, 90)), light(F, .6), 2.0)
    shadow(R(s, m, 248, 108, 368, 158, light(F, .85)), 4, 2, 2, .3)
    tm(s, m, 248, 108, 368, 158, "1 of 7", size=15, bold=True, color=dark(F, .2))
    for i in range(5):
        _sig(s, m, 22 + i * 84, 92 + i * 84, 208, "Name")


def mirrored_careers(s, x, y, w, h):
    """Duas carreiras espelhadas em nós hexagonais que se encontram no centro, com placas e caixa ligadas. Cury p.21."""
    m = M((0, 0, 440, 135), (x, y, w, h))
    def hexn(cx, cy, on=False):
        p = ((cx - 12, cy), (cx - 7, cy - 6), (cx + 7, cy - 6), (cx + 12, cy), (cx + 7, cy + 6), (cx - 7, cy + 6))
        poly(s, m, p, F if on else W, edge=None if on else D, ew=.5)
    slot(s, m, 4, 0, 62, 68, "[photo]", size=6)
    slot(s, m, 378, 0, 436, 68, "[photo]", size=6)
    slot(s, m, 66, 52, 100, 68, "[logo]", size=4.5)
    slot(s, m, 340, 52, 374, 68, "[logo]", size=4.5)
    y1, y2 = 18, 44
    hl(s, m, (100, y1), (252, y1), D, .5); hl(s, m, (188, y2), (340, y2), D, .5)
    poly(s, m, ((252, y1 - 3), (258, y1), (252, y1 + 3)), D)
    poly(s, m, ((188, y2 - 3), (182, y2), (188, y2 + 3)), D)
    for cx, yr, on, t in ((115, "[yr]", False, "Role"), (160, "[yr]", False, "Role"), (205, "[yr]", False, "Role")):
        hexn(cx, y1, on)
        tm(s, m, cx - 20, y1 - 18, cx + 20, y1 - 6, yr, size=5, bold=True)
        tm(s, m, cx - 20, y1 + 6, cx + 20, y1 + 16, t, size=4.5)
    for cx, yr, on, t in ((235, "[yr]", True, "CEO"), (280, "[yr]", False, "Role"), (325, "[yr]", False, "Role")):
        hexn(cx, y2, on)
        tm(s, m, cx - 20, y2 - 17, cx + 20, y2 - 6, yr, size=5, bold=True)
        tm(s, m, cx - 20, y2 + 6, cx + 20, y2 + 16, t, size=4.5)
    for ax, t1, t2 in ((2, "Name, outgoing CEO", "[tenure]"), (306, "Name, incoming CEO", "[current role]")):
        R(s, m, ax, 70, ax + 132, 108, W, D, width=.75)
        R(s, m, ax, 70, ax + 3, 108, D)
        tm(s, m, ax + 6, 72, ax + 130, 90, t1, size=5.5, bold=True, align=L)
        tm(s, m, ax + 6, 90, ax + 130, 106, t2, size=5, italic=True, color=G4, align=L)
    R(s, m, 158, 72, 282, 124, W, D, width=.5)
    tm(s, m, 161, 74, 279, 122, "The handover is part of a long-term plan", size=6, bold=True)
    for a, b in ((134, 158), (282, 306)):
        hl(s, m, (a, 90), (b, 90), D, .5)
        hl(s, m, (a, 84), (a, 96), D, .5); hl(s, m, (b, 84), (b, 96), D, .5)


SLIDES = [
    ("Ribbons, shards and strands set the page", "Depth pieces drawn face by face",
     [("Interlocking ribbon timeline", "3R Petroleum p.2", interlock_ribbons), ("Triangle sandwich", "AB InBev p.58", triangle_sandwich), ("Bowtie into wheel", "BTG Pactual p.96", bowtie_wheel),
      ("Twist ribbons into tiles", "BTG Pactual p.86", twist_ribbons), ("Bands behind a map", "CSN p.23", bands_behind_map), ("Shard frame divider", "CSN p.18", shard_frame)]),
    ("Beams and scenes carry the eye to the message", "Depth pieces drawn face by face",
     [("Twisted strand bundle", "CSN p.1", strand_twist), ("Zoom beam on dark", "Cury p.32", zoom_beam_dark), ("Seated-table scene", "Intelbras p.32", seated_table),
      ("Spine wall to quote plate", "RD Saude p.57", book_wall), ("Stone hexagon staircase", "RD Saude p.6", stone_hexes), ("Dim-all modal", "Rede D'Or p.27", dim_modal)]),
    ("Layers pull one message above the page", "Depth pieces drawn face by face",
     [("Slip card over chart", "Rede D'Or p.61", slip_card), ("Cards with number tabs", "RBI p.49", rbi_cards_band), ("Modal with ribbon crown", "Senior p.15", modal_crown),
      ("Pentagon arrow cards", "Senior p.21", arrow_cards), ("Slab pyramid with straps", "Senior p.7", slab_pyramid), ("Beam from donut to panel", "Senior p.10", beam_donut_panel)]),
    ("Arcs, plates and ledgers of deals", "Grey slots mark the real material to bring in",
     [("Orbit arcs and rules", "Senior p.2", orbit_arcs), ("Rounded offset modal", "Vasta p.15", offset_rounded_modal), ("Deal ledger above a stock line", "Vibra p.6", deal_ledger),
      ("Raw field research wall", "3R Petroleum p.51", field_wall), ("Interview wall with tally", "AB InBev p.15", interview_wall), ("Mystery-shop panel", "AB InBev p.38", mystery_shop)]),
    ("Interviews become proof when the call shows", "Grey slots mark the real material to bring in",
     [("Code as method proof", "AB InBev p.13", code_proof), ("Office-visit block", "Alupar p.18", office_visit), ("Field scoreboard", "BTG Pactual p.26", field_scoreboard),
      ("Tap-by-tap walkthrough", "BTG Pactual p.45", tap_walkthrough), ("Signed term sheets", "CSN p.32", term_sheets), ("Geo-heatmap proof", "Intelbras p.9", geo_proof)]),
    ("Code and phones show how the work was done", "Grey slots mark the real material to bring in",
     [("Word-frequency rows", "Meliuz p.40", word_freq), ("Code to feed to verdict", "Meliuz p.47", code_feed_verdict), ("Research counter band", "Meliuz p.14", counter_band),
      ("Field test with leaders", "Meliuz p.116", field_test_phone), ("Chat bubbles as evidence", "Meliuz p.124", chat_bubbles), ("Field-trip photo on a band", "Mercado Libre p.14", field_selfie)]),
    ("Tests and receipts earn the claim", "Grey slots mark the real material to bring in",
     [("Hands-on platform test", "Mercado Libre p.28", platform_test), ("Code as receipt", "Mercado Libre p.7", code_receipt), ("Book cover as authority", "Mercado Libre p.4", book_authority),
      ("Stacked video calls", "Mercado Libre p.11", zoom_stack), ("Timed transaction race", "Nubank p.8", race), ("Pin density map", "Nubank p.25", pin_density)]),
    ("Paperwork, maps and calls ground the thesis", "Grey slots mark the real material to bring in",
     [("Real paperwork as exhibit", "Nubank p.27", form_exhibit), ("Pin census on a street map", "RD Saude p.14", pin_census), ("Stack of call screens", "RBI p.18", phone_call_stack),
      ("News card with stamp", "Vibra p.14", news_card), ("Expert dossier stack", "AB InBev p.6", expert_dossier), ("Pennant into cards", "AB InBev p.20", pennant_asked)]),
    ("Quotes need a face and a frame", "Grey slots mark the real material to bring in",
     [("Video still wired to quote", "Alupar p.11", video_still_quote), ("Pentagon quote ribbons", "BTG Pactual p.33", pentagon_quotes), ("Call grid and transcript", "Cosan p.6", video_grid_quote),
      ("Anonymized quote", "Meliuz p.15", anonymized_quote), ("Name-tab analyst block", "Rede D'Or p.15", name_tab), ("Quotes bookending a timeline", "Sabesp p.17", timeline_bookends)]),
    ("Governance reads better than a biography", "Grey slots mark the real material to bring in",
     [("Video-grid quote card", "Vasta p.13", video_card_quote), ("Quote card with spine", "Vibra p.29", quote_spine), ("Director handover ledger", "Kering p.7", handover_ledger),
      ("Own score ruler", "Meliuz p.48", score_ruler), ("Logo-as-CV clusters", "Rede D'Or p.20", logo_cv), ("Dashed year-logo ticker", "Senior p.23", year_ticker)]),
    ("Signatures and handovers close the case", "Grey slots mark the real material to bring in",
     [("One-of-seven with signatures", "Vasta p.35", one_of_seven), ("Signed term-sheet cards", "Alupar p.2", signed_termcards), ("Mirrored career timelines", "Cury p.21", mirrored_careers),
      ("Closing verdict cards", "RBI p.49", closing_verdict)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the technique comes from the source.")
    ss.save(prs, OUT)
