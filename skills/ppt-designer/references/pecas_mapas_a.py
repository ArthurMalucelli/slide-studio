"""Peças de mapa do catálogo (lote mapas_a), com conteúdo fictício e só formas editáveis.
Referência de cada uma: references/catalogo/mapas.md.
Uso: python3 pecas_mapas_a.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import functools
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE as DS, MSO_PATTERN  # noqa: E402

L, RT, C = PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.CENTER
REG = {"N": ("AC", "AM", "RR", "RO", "PA", "AP", "TO"), "NE": ("MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"),
       "CO": ("MT", "MS", "GO", "DF"), "SE": ("MG", "ES", "RJ", "SP"), "S": ("PR", "SC", "RS")}
REG_OF = {u: r for r, us in REG.items() for u in us}


# ---------- Helpers ----------
def M2(src, box, ms=1.4):
    """Como M, mas estica até ms vezes no eixo que sobra: faixa em caixa alta ganha respiro; mapa continua sem distorção."""
    m = M(src, box)
    x0, y0, x1, y1 = src; x, y, w, h = box
    fx, fy = w / (x1 - x0), h / (y1 - y0)
    sx, sy = (min(fx, fy * ms), fy) if fx > fy else (fx, min(fy, fx * ms))
    m.sx, m.sy = sx, sy
    m.ox = x + (w - (x1 - x0) * sx) / 2 - x0 * sx
    m.oy = y + (h - (y1 - y0) * sy) / 2 - y0 * sy
    return m


def z(m, px, mn=4.5):
    """Corpo de texto: px da altura de fonte no recorte, escalado para a caixa, nunca abaixo de mn."""
    return round(max(mn, min(px * min(m.sx, m.sy) * 72, 14)), 1)


def lum(c):
    h = ss.hx(c)
    return (int(h[0:2], 16) * .299 + int(h[2:4], 16) * .587 + int(h[4:6], 16) * .114) / 255


def deep(c, t=.5):
    """Mesma cor, escurecida até aguentar texto branco."""
    while lum(c) > t:
        c = dark(c, .15)
    return c


def radial(sp, stops, cx=.5, cy=.5):
    grad(sp, stops, 0)
    gf = sp._element.spPr.find(qn("a:gradFill"))
    for c in gf.findall(qn("a:lin")):
        gf.remove(c)
    pa = etree.SubElement(gf, qn("a:path")); pa.set("path", "circle")
    ft = etree.SubElement(pa, qn("a:fillToRect"))
    for k, v in (("l", cx), ("t", cy), ("r", 1 - cx), ("b", 1 - cy)):
        ft.set(k, str(int(v * 100000)))
    return sp


def soft_shadow(sp, blur=5, dist=2, alpha=35):
    spPr = sp._element.spPr
    ef = spPr.find(qn("a:effectLst"))
    if ef is None:
        ef = etree.SubElement(spPr, qn("a:effectLst"))
    sh = etree.SubElement(ef, qn("a:outerShdw"))
    sh.set("blurRad", str(int(blur * 12700))); sh.set("dist", str(int(dist * 12700))); sh.set("dir", "2700000"); sh.set("rotWithShape", "0")
    cl = etree.SubElement(sh, qn("a:srgbClr")); cl.set("val", "000000")
    al = etree.SubElement(cl, qn("a:alpha")); al.set("val", str(int(alpha * 1000)))
    return sp


def hatch(sp, fg, bg=W):
    sp.fill.patterned(); sp.fill.pattern = MSO_PATTERN.WIDE_UPWARD_DIAGONAL
    sp.fill.fore_color.rgb = ss.rgb(fg); sp.fill.back_color.rgb = ss.rgb(bg)
    return sp


def path(s, pts, color, width=1.0, dash=None, arrow=0):
    """Linha aberta editável (freeform sem preenchimento), em polegadas. dash: DS.*; arrow: tamanho da ponta no fim."""
    k = [(round(a * 1000), round(b * 1000)) for a, b in pts]
    fb = s.shapes.build_freeform(k[0][0], k[0][1], scale=914.4)
    fb.add_line_segments(k[1:], close=False)
    sp = fb.convert_to_shape(); sp.shadow.inherit = False
    sp.fill.background()
    sp.line.color.rgb = ss.rgb(color); sp.line.width = Pt(width)
    if dash:
        sp.line.dash_style = dash
    if arrow:
        (a, b), (c, d) = pts[-2], pts[-1]
        n = math.hypot(c - a, d - b) or 1
        ux, uy = (c - a) / n, (d - b) / n
        ss.poly(s, ((c, d), (c - ux * arrow - uy * arrow * .55, d - uy * arrow + ux * arrow * .55), (c - ux * arrow + uy * arrow * .55, d - uy * arrow - ux * arrow * .55)), color)
    return sp


def contours(s, cs, fill):
    """Vários contornos fechados numa forma só; serve para milhares de pontos sem pesar o arquivo."""
    k0 = [(round(a * 2000), round(b * 2000)) for a, b in cs[0]]
    fb = s.shapes.build_freeform(k0[0][0], k0[0][1], scale=457.2)
    fb.add_line_segments(k0[1:], close=True)
    for c in cs[1:]:
        k = [(round(a * 2000), round(b * 2000)) for a, b in c]
        fb.move_to(*k[0]); fb.add_line_segments(k[1:], close=True)
    sp = fb.convert_to_shape(); sp.shadow.inherit = False
    ss.paint(sp.fill, fill); sp.line.fill.background()
    return sp


def catmull(pts, n=8):
    """Curva suave aberta passando pelos pontos."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * p1[k] + (p2[k] - p0[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    return out + [pts[-1]]


def bez(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * p1[0] + t ** 2 * p2[0], (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * p1[1] + t ** 2 * p2[1]) for t in (i / n for i in range(n + 1))]


def pin(s, cx, ty, hh, fill=W, hole=None, edge=None):
    """Alfinete em gota com a ponta em (cx, ty)."""
    r = hh * .37
    cy = ty - hh + r
    a0 = math.degrees(math.asin(r / (hh - r)))
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in [a0 - i * (180 + 2 * a0) / 24 for i in range(25)]]
    ss.poly(s, pts + [(cx, ty)], fill, edge, .5)
    if hole:
        oval(s, cx, cy, r * 1.02, hole)
    return cx, cy


def star(s, cx, cy, r, fill):
    pts = [(cx + (r if i % 2 == 0 else r * .42) * math.sin(i * math.pi / 5), cy - (r if i % 2 == 0 else r * .42) * math.cos(i * math.pi / 5)) for i in range(10)]
    return ss.poly(s, pts, fill)


def diamond(s, cx, cy, r, fill, edge=None, ew=.75):
    return ss.poly(s, ((cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)), fill, edge, ew)


def mold(s, x, y, w, h, label="[logo]", size=6, is_oval=False):
    """Molde de imagem: foto, print ou logo real entram aqui."""
    sp = oval(s, x + w / 2, y + h / 2, w, G2, h=h) if is_oval else ss.rect(s, x, y, w, h, G2)
    tx(s, x, y, w, h, label, size=size, color=G4)
    return sp


def lab(s, x, y, w, h, t, fill=D, size=6.5, italic=False, adj=.22):
    """Rótulo de dado: retângulo arredondado escuro, texto branco bold."""
    rr(s, x, y, w, h, deep(fill), adj)
    tb = tx(s, x, y, w, h, t, size=size, color=W, bold=True, italic=italic)
    tb.text_frame.word_wrap = False
    return tb


def t1(s, x, y, w, h, t, **k):
    """Texto de uma linha, sem quebra."""
    tb = tx(s, x, y, w, h, t, **k)
    tb.text_frame.word_wrap = False
    return tb


def rich(s, x, y, w, h, runs, size=7, align=L, anchor=MSO_ANCHOR.TOP):
    """Parágrafo com trechos: [(texto, bold, cor)] por linha."""
    para = [[(a, {"bold": b, "color": c, "size": size}) for a, b, c in p] for p in runs]
    return ss.text(s, x, y, w, h, para, align=align, anchor=anchor, margin=0.0)


def clip_ring(r, lo0, lo1, la0, la1):
    def cut(pts, ins, inter):
        out = []
        for i, p in enumerate(pts):
            q = pts[i - 1]
            if ins(p):
                if not ins(q):
                    out.append(inter(q, p))
                out.append(p)
            elif ins(q):
                out.append(inter(q, p))
        return out
    def ix(v):
        return lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / (b[0] - a[0]))
    def iy(v):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / (b[1] - a[1]), v)
    pts = [tuple(p) for p in r]
    for ins, inter in ((lambda p: p[0] >= lo0, ix(lo0)), (lambda p: p[0] <= lo1, ix(lo1)), (lambda p: p[1] >= la0, iy(la0)), (lambda p: p[1] <= la1, iy(la1))):
        if pts:
            pts = cut(pts, ins, inter)
    return pts


def area(r):
    return abs(sum(r[i - 1][0] * r[i][1] - r[i][0] * r[i - 1][1] for i in range(len(r)))) / 2


def cen(shape):
    """Centroide do maior anel, em lon/lat."""
    r = max(shape["rings"], key=area)
    a = cx = cy = 0
    for i in range(len(r)):
        k = r[i - 1][0] * r[i][1] - r[i][0] * r[i - 1][1]
        a += k; cx += (r[i - 1][0] + r[i][0]) * k; cy += (r[i - 1][1] + r[i][1]) * k
    return (cx / (3 * a), cy / (3 * a))


def geo(s, box, shapes, fill, edge=None, ew=.5, keep=True, bounds=None, clip=False, min_area=0, project=None):
    """Como draw_map, com degradê por anel. fill(chave) -> cor | None | (stops, ângulo) | ('radial', stops, cx, cy).
    clip=True corta os anéis em bounds; min_area descarta ilhas (graus²). Devolve (px, py)."""
    pts = [p for v in shapes.values() for r in v["rings"] for p in r]
    lo0, lo1 = (bounds[0], bounds[1]) if bounds else (min(p[0] for p in pts), max(p[0] for p in pts))
    la0, la1 = (bounds[2], bounds[3]) if bounds else (min(p[1] for p in pts), max(p[1] for p in pts))
    x, y, w, h = box
    k = math.cos(math.radians((la0 + la1) / 2))
    sx, sy = w / ((lo1 - lo0) * k), h / (la1 - la0)
    if keep:
        sx = sy = min(sx, sy)
    ox, oy = x + (w - (lo1 - lo0) * k * sx) / 2, y + (h - (la1 - la0) * sy) / 2
    px = lambda lo: ox + (lo - lo0) * k * sx
    py = lambda la: oy + (la1 - la) * sy
    for key, v in shapes.items():
        c = fill(key) if callable(fill) else fill.get(key) if isinstance(fill, dict) else fill
        if not c:
            continue
        for r in v["rings"]:
            if min_area and area(r) < min_area:
                continue
            if clip:
                r = clip_ring(r, lo0, lo1, la0, la1)
                if len(r) < 3:
                    continue
            elif bounds:
                ax, ay = sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)
                if not (lo0 <= ax <= lo1 and la0 <= ay <= la1):
                    continue
            sp = ss.poly(s, [(px(a), py(b)) for a, b in r], c if isinstance(c, str) else W, edge, ew)
            if isinstance(c, tuple):
                if c[0] == "radial":
                    radial(sp, c[1], c[2], c[3])
                else:
                    grad(sp, c[0], c[1])
    return px, py


def merged(shapes, keys):
    """Une estados vizinhos em um contorno só, tirando as arestas compartilhadas."""
    edges = {}
    for k in keys:
        for r in shapes[k]["rings"]:
            pts = [(round(a, 3), round(b, 3)) for a, b in r]
            if pts[0] == pts[-1]:
                pts = pts[:-1]
            for i in range(len(pts)):
                edges[(pts[i - 1], pts[i])] = 1
    keep = {a: b for (a, b) in edges if (b, a) not in edges}
    rings = []
    while keep:
        a = next(iter(keep))
        ring = []
        while a in keep:
            ring.append(a)
            a = keep.pop(a)
        if len(ring) > 2:
            rings.append(ring)
    return {"rings": rings}


def lw(t, size):
    """Largura estimada de um rótulo bold em polegadas (fonte larga)."""
    return len(t) * size * .0095 + .05


def gray_state(u, tones=("D0D0D0", "BDBDBD", "E0E0E0", "A9A9A9", "C7C7C7")):
    """Tons de cinza fixos por estado (o mosaico das fontes)."""
    return tones[sum(ord(c) for c in u) % len(tones)]


# ---------- Brasil escuro ----------
def dark_glow(s, x, y, w, h):
    """Mapa em contorno sobre fundo escuro, estados-corredor brilhando e guias ortogonais dos dois lados. CSN (Liability Management) p.24."""
    m = M2((0, 0, 900, 375), (x, y, w, h))
    grad(R(s, m, 0, 0, 900, 375, D), ((0, dark(D, .65)), (.5, dark(D, .3)), (1, D)), 90)
    br = states("BRA")
    # Só contorno, sem preenchimento; a área ativa brilha do centro para a borda.
    box = m.box(262, 10, 648, 372)
    active = ("MG", "SP", "RJ", "RS")
    px, py = geo(s, box, br, lambda u: ("radial", ((0, light(F, .25)), (.6, F), (1, dark(D, .1))), .5, .5) if u in active else dark(D, .42), W, .4)
    for pts in (((-44.3, -2.6), (-44.6, -5.2), (-42.8, -5.2), (-40.5, -3.8), (-38.6, -3.7)), ((-42.8, -5.2), (-41.0, -7.2), (-37.0, -8.0)), ((-41.0, -7.2), (-35.2, -8.0)),
                ((-43.9, -19.9), (-44.0, -21.2), (-43.2, -22.9)), ((-43.2, -22.9), (-46.6, -23.6), (-46.3, -23.95)), ((-44.0, -21.2), (-47.0, -22.5))):
        path(s, [(px(a), py(b)) for a, b in pts], W, .6)
    fn, fs = z(m, 10), z(m, 9, 4.2)
    def label(xa, xb, ly, a, b, al):
        bx = m.box(xa, ly, xb, ly)
        t1(s, bx[0], bx[1] - .07, bx[2], .14, a, size=fn, color=W, bold=True, align=al)
        t1(s, bx[0], bx[1] + .055, bx[2], .12, b, size=fs, color=G3, align=al)
    gl = light(F, .35)
    xl = 668
    for lo, la, xm, ly, a, b in ((-41.0, -3.3, None, 20, "Northern rail concession", "1,191 km in operation"),
                                 (-37.0, -6.6, 655, 92, "Greenfield rail link", "1,206 km being built"),
                                 (-42.6, -18.2, 620, 168, "Heavy-haul network", "1,674 km, densest network"),
                                 (-43.4, -22.6, 640, 248, "Bulk solids terminal", "Long-dated concession"),
                                 (-43.8, -22.95, 610, 328, "Container terminal", "660k TEU a year")):
        p0 = (px(lo), py(la))
        yy = m.p((0, ly))[1]
        xe = m.p((xl, 0))[0]
        pts = [p0, (p0[0], yy), (xe, yy)] if xm is None else [p0, (m.p((xm, 0))[0], p0[1]), (m.p((xm, 0))[0], yy), (xe, yy)]
        path(s, pts, gl, .75, arrow=.04)
        label(xl + 5, 898, ly, a, b, L)
    for lo, la, a, b in ((-44.6, -15.6, "Regional headquarters", "70+ branches run from base"), (-48.2, -22.3, "Rail terminals", "Two sites under contract"), (-52.8, -30.0, "Border terminal", "Multimodal at the tri-border")):
        yy = py(la)
        path(s, [(px(lo), yy), (m.p((254, 0))[0], yy)], gl, .75, arrow=.04)
        label(4, 248, (yy - m.oy) / m.sy, a, b, C)
    # Quadro de KPI por cima do canto noroeste do mapa.
    R(s, m, 8, 6, 380, 104, dark(D, .55), light(F, .15), width=.5)
    fk = z(m, 9, 4.2)
    for k, ox_ in enumerate((18, 200)):
        cx, cy = m.p((ox_ + 8, 20))
        oval(s, cx, cy, .1, None, border=W, width=.4)
        tx(s, cx - .1, cy - .1, .2, .2, str(k + 1), size=4.2, color=W)
        t1(s, *m.box(ox_ + 22, 10, ox_ + 170, 30), "Asset one" if not k else "Asset two", size=fk, color=W, bold=True, align=L)
        for j, (a, b) in enumerate((("EV", ("$34 bn", "$1.4 bn")[k]), ("EBITDA", ("$4.4 bn", "$140 m")[k]), ("EV/EBITDA", ("7.7x", "10.2x")[k]))):
            yy = 36 + j * 21
            t1(s, *m.box(ox_, yy, ox_ + 90, yy + 20), a, size=fk, color=W, align=L)
            t1(s, *m.box(ox_ + 94, yy, ox_ + 172, yy + 20), b, size=fk, color=W, align=L)
    ss.line(s, *m.p((192, 20)), *m.p((192, 96)), gl, .5, dash=True)


# ---------- Europa ----------
EU = ("FRA", "ESP", "PRT", "ITA", "DEU", "POL", "NLD", "BEL", "LUX", "CHE", "AUT", "CZE", "SVK", "HUN", "SVN", "HRV", "BIH", "SRB", "MNE", "ALB", "MKD", "KOS", "BGR", "ROU", "MDA", "UKR", "BLR")


def europe_tabs(s, x, y, w, h):
    """Mapa por país em degradê escuro-para-foco, com pontos de planta, sob barra de abas ativa. CSN - ArcelorMittal p.26."""
    m = M2((0, 0, 900, 840), (x, y, w, h))
    for a, b, t in ((14, 470, "Europe network"), (484, 690, "Second section"), (702, 900, "Third section")):
        grad(R(s, m, a, 6, b, 84, D), ((0, dark(D, .6)), (1, light(F, .1))), 15)
        t1(s, *m.box(a, 6, b, 84), t, size=z(m, 18, 5.5), color=W, bold=True)
    R(s, m, 14, 6, 470, 84, None, W, width=.5, dash=True)
    R(s, m, 7, 0, 477, 91, None, F, width=.75, dash=True)
    t1(s, *m.box(16, 104, 880, 138), "The wider network absorbs two complementary assets", size=z(m, 22, 6), bold=True, align=L)
    t1(s, *m.box(16, 138, 880, 166), "One anchors long steel; the other adds flat finishing", size=z(m, 18, 5), align=L)
    fz = z(m, 16, 5)
    for cx, t, kind in ((232, "Network", 0), (428, "Recycling", 1), (600, "Target", 2)):
        px_, py_ = m.p((cx, 190))
        if kind == 0:
            oval(s, px_, py_, .06, dark(F, .5), border=F, width=.75)
        elif kind == 1:
            oval(s, px_, py_, .06, dark(D, .7))
        else:
            oval(s, px_, py_, .06, A, border=W, width=.5)
        t1(s, *m.box(cx + 14, 174, cx + 150, 206), t, size=fz, bold=True, align=L)
    c = countries_50m()
    shp = {k: c[k] for k in EU}
    stops = ((0, F), (.45, dark(F, .25)), (1, dark(D, .6)))
    fill = lambda k: (((0, light(F, .36)), (1, light(F, .24))), 90) if k in ("DEU", "PRT") else (stops, 75)
    px, py = geo(s, m.box(24, 232, 890, 745), shp, fill, W, .6, bounds=(-10, 40.5, 36.3, 55.5), min_area=.02)
    d = .05
    for a, b in ((1.5, 47.5), (-.8, 44.8), (2.8, 45.2), (4.5, 44.3), (5.8, 47.9), (2.6, 49.3), (-1.2, 47.2), (4.6, 50.6), (5.6, 50.4), (4.5, 51.3), (6.1, 51.1),
                 (-5, 42.6), (-2, 42.6), (-6.2, 39.4), (-3.2, 39.2), (-1, 38.6), (-.5, 41.3), (13.1, 51.4), (9, 50.2), (11.4, 49.5), (8.8, 48.0), (7.6, 52.8),
                 (17.4, 51.8), (19.2, 53.4), (20.8, 50.6), (22.2, 52.3), (21.3, 49.9), (16.2, 40.8), (20.1, 46.5), (25.5, 46.0), (17.8, 44.3), (19.2, 43.2)):
        grad(oval(s, px(a), py(b), d, F, border=light(F, .15), width=.6), ((0, G4), (1, dark(D, .5))), 0)
    for a, b in ((10.6, 49.8), (12.2, 47.9), (10, 50.9), (5.2, 52.2), (4.6, 52.9)):
        oval(s, px(a), py(b), d, dark(D, .8), border=dark(F, .2), width=.5)
    tg = ((7.4, 53.35), (-8.9, 39.2))
    for a, b in tg:
        oval(s, px(a), py(b), .065, A, border=W, width=.75)
    fs = z(m, 16, 5)
    # Rótulos na margem branca, com fio em cotovelo.
    xa, ya = px(tg[0][0]), py(tg[0][1])
    ly = (ya - m.oy) / m.sy - 32
    yy = m.p((0, ly))[1]
    path(s, [(m.p((60, 0))[0], yy), (xa, yy), (xa, ya - .03)], INK, .6)
    t1(s, *m.box(70, ly - 30, 380, ly), "Target plant one", size=fs, align=L)
    t1(s, *m.box(70, ly + 2, 380, ly + 30), "1.1 Mt/year, long", size=fs, align=L)
    xa, ya = px(tg[1][0]), py(tg[1][1])
    yb = m.p((0, 800))[1]
    path(s, [(xa, ya + .035), (xa, yb), (m.p((400, 0))[0], yb)], INK, .6)
    t1(s, xa + .05, yb - .13, 1.2, .12, "Target plant two", size=fs, align=L)
    t1(s, xa + .05, yb + .01, 1.2, .12, "0.5 Mt/year, rolling", size=fs, align=L)


# ---------- Painéis chanfrados ----------
def chamfer_rail(s, x, y, w, h):
    """Mapa entre painéis chanfrados em degradê, com malha ferroviária e plantas. CSN - ArcelorMittal p.23."""
    m = M2((0, 0, 900, 369), (x, y, w, h))
    rosy = ss.mix(light(F, .35), "A8A8A8", .68)
    fr = dark(F, .35)
    grad(poly(s, m, ((0, 0), (285, 0), (418, 192), (290, 369), (0, 369)), G2), ((0, W), (.5, light(rosy, .5)), (1, rosy)), 0)
    grad(poly(s, m, ((628, 0), (900, 0), (900, 369), (625, 369), (530, 255), (498, 97)), G2), ((0, rosy), (.4, light(rosy, .45)), (1, W)), 0)
    poly(s, m, ((416, 210), (316, 334), (437, 250)), fr)
    poly(s, m, ((498, 97), (603, 26), (522, 115)), fr)
    px, py = geo(s, m.box(298, 54, 602, 330), states("BRA"), "DCDCDC", W, .5)
    for pts in (((-49, -1.6), (-49.7, -5.2), (-47.4, -5.3), (-48.3, -11), (-48.6, -16.5), (-50, -21)), ((-48.6, -9), (-56, -8.5), (-57.2, -7.2)), ((-48.5, -13.5), (-53.2, -13.3), (-53.8, -19)), ((-50.3, -17), (-54, -19.2), (-57, -19))):
        path(s, [(px(a), py(b)) for a, b in pts], fr, .4)
    rnd = random.Random(7)
    pts = [(-44 + rnd.gauss(0, 1.3), -20.3 + rnd.gauss(0, 1.1)) for _ in range(14)] + [(-47.2 + rnd.gauss(0, 1), -23 + rnd.gauss(0, .5)) for _ in range(6)] + [(-38, -4.5), (-37.5, -4.9), (-35.0, -8), (-38.8, -13), (-54.5, -21.5), (-54.9, -22), (-48.7, -2)]
    for a, b in pts:
        oval(s, px(a), py(b), .026, fr)
    fa = z(m, 9)
    t1(s, *m.box(6, 2, 250, 18), "Capex (5y): $3.6 bn", size=fa, bold=True, color=fr, align=L)
    for i, (yr, t) in enumerate((("2025", "Entry into coating"), ("2025", "Into structural pipes"), ("2023", "Global scale, 3 Mt"), ("2018", "Long steel leadership"), ("2005", "Base in flat and long"))):
        yy = 22 + i * 69
        t1(s, *m.box(8, yy - 1, 62, yy + 14), yr, size=fa, bold=True)
        ss.line(s, *m.p((6, yy + 15)), *m.p((80, yy + 15)), G3, .5, dash=False)
        mold(s, *m.box(10, yy + 20, 72, yy + 50), "[logo]", size=4)
        path(s, bez(m.p((109, yy + 30)), m.p((96, yy + 20)), m.p((85, yy + 25)), 8), INK, .5, arrow=.025)
        path(s, bez(m.p((85, yy + 36)), m.p((96, yy + 48)), m.p((109, yy + 41)), 8), INK, .5, arrow=.025)
        mold(s, *m.box(116, yy + 20, 170, yy + 50), "[logo]", size=4)
        ss.line(s, *m.p((176, yy + 16)), *m.p((176, yy + 54)), G3, .5, dash=False)
        tx(s, *m.box(182, yy + 15, 290, yy + 55), t, size=fa, align=L)
    t1(s, *m.box(660, 22, 880, 44), "Rationale", size=z(m, 12, 6), color=fr, bold=True)
    ss.line(s, *m.p((680, 45)), *m.p((860, 45)), fr, .75, dash=False)
    for yy, a, b in ((100, "Verticalization", " from crude steel, capturing downstream margins"), (176, "Structural scale", " and cost leadership through logistics")):
        ss.line(s, *m.p((654, yy - 6)), *m.p((880, yy - 6)), fr, .5, dash=False)
        rich(s, *m.box(664, yy, 866, yy + 34), [[(a, True, INK), (b, False, INK)]], size=fa, anchor=MSO_ANCHOR.MIDDLE)
        ss.line(s, *m.p((654, yy + 40)), *m.p((880, yy + 40)), fr, .5, dash=False)
    poly(s, m, ((552, 279), (900, 279), (900, 369), (622, 369)), G1)
    for i, c in enumerate((F, A, G4)):
        oval(s, *m.p((586 + i * 13, 292)), .03, c)
    t1(s, *m.box(650, 283, 770, 300), "www.news-site.com", size=4.2, color=G4, align=L)
    mold(s, *m.box(805, 284, 885, 302), "[logo]", size=4)
    tx(s, *m.box(622, 306, 892, 334), "Group plans $2 bn more in local investments", size=fa, bold=True, align=L)
    tx(s, *m.box(622, 336, 892, 366), "Wraps up a cycle and adds capacity over five years", size=z(m, 8, 4.2), align=L)
    t1(s, *m.box(322, 330, 400, 362), "27 units", size=z(m, 13, 6.5), bold=True, color=fr, align=L)
    t1(s, *m.box(478, 330, 590, 348), "Crude: 16 Mt", size=fa, bold=True, color=fr, align=L)
    t1(s, *m.box(478, 346, 590, 364), "Ore: 8 Mt", size=fa, bold=True, color=fr, align=L)


# ---------- Cunhas ----------
def funnel_clusters(s, x, y, w, h):
    """Cunha sólida do mapa para barras por cluster, com dobra, rosca e total tracejado. 3R Petroleum p.19."""
    m = M2((0, 0, 900, 265), (x, y, w, h), 1.2)
    R(s, m, 282, 0, 900, 265, "D8D8D8")
    grad(poly(s, m, ((282, 0), (282, 265), (172, 118)), F), ((0, G3), (.6, light(F, .35)), (1, F)), 0)
    hi = {"RN": D, "CE": D, "BA": F, "RJ": dark(F, .3)}
    geo(s, m.box(0, 2, 220, 262), states("BRA"), lambda u: hi.get(u) or gray_state(u), W, .25)
    fh, fb = z(m, 13, 6), z(m, 11, 5.5)
    t1(s, *m.box(298, 12, 560, 42), "Asset portfolio", size=fh, bold=True, color=D, align=L)
    t1(s, *m.box(620, 12, 860, 42), "Consolidated reserves", size=fh, bold=True, color=D, align=L)
    for t, yy, c, ye, yf in (("Cluster one", 52, D, 103, 138), ("Cluster two", 115, F, 140, 175), ("Cluster three", 177, dark(F, .3), 175, 210)):
        R(s, m, 282, yy, 523, yy + 57, c)
        poly(s, m, ((523, yy), (592, ye), (592, yf), (523, yy + 57)), dark(c, .3))
        t1(s, *m.box(282, yy, 523, yy + 57), t, size=fb, color=W, bold=True)
    cx, cy = m.p((700, 150))
    r1 = 80 * min(m.sx, m.sy) * 1.12
    a = -90
    for pct, c, t in ((6, dark(F, .3), "6%"), (85, D, "85%"), (9, F, "9%")):
        b = a + pct * 3.6
        ss.poly(s, seg((cx, cy), r1 * .5, r1, a, b, n=max(4, pct)), c)
        mid = math.radians((a + b) / 2) if t != "85%" else math.radians(75)
        lx, ly = cx + r1 * .76 * math.cos(mid), cy + r1 * .76 * math.sin(mid)
        t1(s, lx - .15, ly - .06, .3, .12, t, size=z(m, 9, 4.5), color=W, bold=True)
        a = b
    R(s, m, 788, 58, 888, 104, None, dark(F, .3), dash=True, width=.75)
    rich(s, *m.box(794, 60, 886, 102), [[("Total:", True, INK)], [("142 bn bbl", True, D)]], size=z(m, 9, 4.5), anchor=MSO_ANCHOR.MIDDLE)
    for i, (t, c) in enumerate((("Offshore", dark(F, .3)), ("Basin", D), ("Onshore", F))):
        yy = 128 + i * 20
        R(s, m, 818, yy - 4, 827, yy + 4, c)
        t1(s, *m.box(832, yy - 9, 895, yy + 9), t, size=4.5, align=L)


def wedge_funnel(s, x, y, w, h):
    """Cunha cinza saindo do mapa para um funil, com valor por região. Nubank p.13."""
    m = M2((0, 0, 900, 431), (x, y, w, h), 1.2)
    grad(poly(s, m, ((272, 68), (480, 12), (480, 395), (562, 420), (272, 372)), G3), ((0, G4), (.5, G2), (1, W)), 0)
    tones = {"N": light(F, .28), "NE": D, "CO": light(F, .5), "SE": dark(F, .18), "S": F}
    px, py = geo(s, m.box(4, 8, 434, 430), states("BRA"), lambda u: tones[REG_OF[u]], W, .5)
    fv = z(m, 15, 6)
    for t, lo, la in (("2.6", -62, -6.6), ("1.7", -55, -14.2), ("9.2", -41.5, -11), ("8.4", -45, -19.5), ("3.1", -53.2, -29.6)):
        lab(s, px(lo) - .12, py(la) - .065, .24, .13, t, size=fv)
    tint = light(F, .42)
    tc = W if lum(tint) < .62 else INK
    fa, fb = z(m, 15, 6), z(m, 16, 6.5)
    for a, b, x0, x1, yy in (("Total population:", "173 million", 480, 873, 12), ("Already served:", "-142 million", 480, 853, 93), ("No internet:", "-7 million", 520, 853, 176), ("No phone:", "-5 million", 541, 832, 258), ("Addressable:", "~18 million", 562, 811, 339)):
        R(s, m, x0, yy, x1, yy + 80, tint)
        t1(s, *m.box(x0, yy + 4, x1, yy + 40), a, size=fa, italic=True, color=tc)
        t1(s, *m.box(x0, yy + 40, x1, yy + 76), b, size=fb, bold=True, color=tc)


# ---------- Tinta por região ----------
PINS = ((-63, -4.5), (-52.5, -4.5), (-43.5, -5.5), (-39.5, -4.6), (-37.2, -8.2), (-41.6, -12.2), (-55.6, -13), (-49.5, -15.8), (-44.5, -18.2), (-48.9, -21.4), (-47.5, -23.0), (-50.6, -25.0), (-49.8, -23.8), (-53.6, -29.6), (-42.6, -22.0))
TONES = lambda: {"N": light(F, .42), "NE": light(F, .68), "CO": light(F, .2), "SE": D, "S": dark(F, .12)}


def tint_map(s, box, pin_h):
    """Mapa em 5 tons com um alfinete branco por estado. Devolve (px, py, tons)."""
    tones = TONES()
    px, py = geo(s, box, states("BRA"), lambda u: tones[REG_OF[u]], W, .4)
    for lo, la in PINS:
        la_c = tones["SE"] if la < -17 and la > -24 else tones["S"] if la <= -24 else tones["CO"] if lo < -46 and la < -10 else tones["NE"] if lo > -46 else tones["N"]
        pin(s, px(lo), py(la), pin_h, W, la_c)
    return px, py, tones


def tint_counts(s, m, rows, fz, gap=.03):
    """Contagens fora do mapa: rótulo na cor escurecida da região, ligado por guia tracejada."""
    tones = TONES()
    for t, reg, x0, x1, ly, side in rows:
        c = tones[reg]
        yy = m.p((0, ly))[1]
        ss.line(s, m.p((x0, 0))[0], yy, m.p((x1, 0))[0], yy, c if lum(c) < .8 else dark(c, .12), .75, dash=True)
        wd = lw(t, fz)
        lx = m.p((x1, 0))[0] + gap if side == "r" else m.p((x0, 0))[0] - wd - gap
        lab(s, lx, yy - .068, wd, .136, t, fill=c, size=fz)


def region_tint(s, x, y, w, h):
    """Mapa em 5 tons, alfinetes brancos e contagem com guia tracejada, caixa de fatos e painel diagonal com barras. RD Saude p.25."""
    m = M2((0, 0, 900, 392), (x, y, w, h))
    poly(s, m, ((420, 68), (578, 0), (900, 0), (900, 392), (578, 392), (395, 305)), G1)
    tint_map(s, m.box(155, 5, 525, 385), .1)
    tint_counts(s, m, (("121 stores", "N", 262, 345, 62, "l"), ("443 stores", "NE", 432, 470, 72, "r"), ("308 stores", "CO", 268, 305, 245, "l"), ("1,700 stores", "SE", 400, 440, 292, "r"), ("381 stores", "S", 270, 345, 334, "l")), z(m, 10, 4.6))
    bx = m.box(5, 75, 133, 316)
    R(s, m, 5, 75, 133, 316, G1, F, dash=True, width=.75)
    t1(s, bx[0], bx[1] + .03, bx[2], .14, "Company", size=z(m, 13, 6), bold=True, color=D)
    ss.line(s, bx[0] + bx[2] * .15, bx[1] + .18, bx[0] + bx[2] * .85, bx[1] + .18, D, .75, dash=False)
    for i, t in enumerate(("2,953 stores", "574 cities", "26 states", "14 hubs", "96% reach")):
        yy = bx[1] + .29 + i * (bx[3] - .36) / 5
        oval(s, bx[0] + .06, yy, .04, D)
        t1(s, bx[0] + .11, yy - .07, bx[2] - .12, .14, t, size=z(m, 10, 4.5), align=L)
    for base, ttl, ytt, a0, a1, l0, l1 in ((182, "Population within 5 km", 18, 75, 52, "47.9%", "59.4%"), (345, "Population within 5 min", 214, 278, 248, "20.6%", "30.9%")):
        t1(s, *m.box(590, ytt, 800, ytt + 18), ttl, size=z(m, 9, 4.5), italic=True)
        for xb0, yt, l, yr in ((653, a0, l0, "2019"), (812, a1, l1, "2023")):
            R(s, m, xb0 + 5, yt + 3, xb0 + 50, base, "000000")
            R(s, m, xb0, yt, xb0 + 45, base, D)
            lab(s, *m.box(xb0 - 8, yt - 21, xb0 + 54, yt - 3), l, size=z(m, 9, 4.5))
            t1(s, *m.box(xb0 - 5, base + 3, xb0 + 55, base + 22), yr, size=z(m, 9, 4.5), color=G4)
        ss.line(s, *m.p((698, a0 + 8)), *m.p((812, a1 + 8)), A, 1, dash=True)


def triptych(s, x, y, w, h):
    """Três mapas iguais, cada um numa família de cor, mais forte onde o player é mais forte; molde de logo e selo de total. RD Saude p.11."""
    m = M2((0, 0, 900, 313), (x, y, w, h), 1.15)
    br = states("BRA")
    fams = ((light(F, .6), {"N": light(F, .45), "NE": F, "CO": light(F, .8), "SE": light(F, .8), "S": light(F, .88)}, {"RR": light(F, .6), "AP": light(F, .6), "PA": light(F, .45), "TO": light(F, .45)}, F, "1,632"),
            (light(A, .7), {"N": light(A, .7), "NE": light(A, .7), "CO": light(A, .7), "SE": light(A, .45), "S": light(A, .6)}, {"SP": D, "PR": light(A, .4)}, D, "2,953"),
            (G2, {"N": G2, "NE": G2, "CO": G2, "SE": G2, "S": D}, {"SP": light(F, .75), "PR": F, "SC": dark(F, .2), "RS": D}, dark(F, .25), "600"))
    fc = z(m, 14, 6)
    for k, (x0, (base, reg, st, chip, n)) in enumerate(zip((2, 322, 640), fams)):
        mold(s, *m.box(x0 + 62, 4, x0 + 200, 42), "[logo]", size=5)
        geo(s, m.box(x0, 56, x0 + 262, 302), br, lambda u: st.get(u) or reg[REG_OF[u]], W, .35)
        bx = m.box(x0 + 2, 236, x0 + 104, 298)
        rr(s, bx[0] + .03, bx[1] + .03, bx[2], bx[3], "000000", .2)
        rr(s, *bx, deep(chip), .2)
        tx(s, *bx, n + " stores", size=fc, color=W, bold=True)


DATA_A = {"AM": 1, "CE": 1, "PE": 2, "GO": 2, "MG": 3, "ES": 3, "MS": 2, "SP": 60, "PR": 4, "SC": 1, "RS": 5, "RJ": 8}
DATA_B = {"AM": 2, "PA": 5, "MA": 2, "PI": 2, "CE": 10, "RN": 4, "RO": 1, "MT": 6, "BA": 13, "GO": 14, "MG": 62, "ES": 8, "MS": 3, "SP": 302, "PR": 36, "SC": 28, "RS": 49, "RJ": 40, "AC": 1, "RR": 0}


def twin_counts(s, x, y, w, h):
    """Dois mapas por estado com contagem centrada e escala própria em barra vertical. BTG Pactual p.87."""
    m = M2((0, 0, 900, 370), (x, y, w, h), 1.1)
    br = states("BRA")
    pale, strong = light(F, .86), dark(F, .08)
    fz = z(m, 9, 4.5)
    for x0, title, data, vmax in ((6, "Company A", DATA_A, 60), (482, "Company B", DATA_B, 302)):
        col = lambda v: ss.mix(pale, strong, (math.sqrt(v / vmax)) ** 1.5)
        px, py = geo(s, m.box(x0, 22, x0 + 340, 368), br, lambda u: col(data[u]) if data.get(u) else G2, W, .35)
        t1(s, *m.box(x0 + 80, 0, x0 + 260, 20), title, size=z(m, 13, 6.5), bold=True, color=G4)
        for u, v in data.items():
            if not v or u in ("RN", "ES", "SC" if data is DATA_A else ""):
                continue
            lo, la = cen(br[u])
            t = str(v)
            wd = lw(t, fz)
            lab(s, px(lo) - wd / 2, py(la) - .05, wd, .1, t, size=fz, adj=.2)
        lx = x0 + 352
        t1(s, *m.box(lx, 24, lx + 62, 42), "# offices", size=fz, color=G4, align=L)
        grad(R(s, m, lx + 4, 46, lx + 13, 112, F), ((0, strong), (1, pale)), 90)
        t1(s, *m.box(lx + 17, 42, lx + 60, 58), str(vmax), size=fz, color=G4, align=L)
        t1(s, *m.box(lx + 17, 100, lx + 60, 116), "1", size=fz, color=G4, align=L)


def _hub(s, cx, cy, r, c):
    for a in (20, 90, 160, 215, 325):
        ss.line(s, cx, cy, cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a)), c, .5, dash=False)
        oval(s, cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a)), r * .36, W, border=c, width=.5)
    oval(s, cx, cy, r * .6, W, border=c, width=.5)


def _temple(s, cx, cy, r, c):
    ss.poly(s, ((cx - r, cy - r * .35), (cx, cy - r * .85), (cx + r, cy - r * .35)), c)
    for i in range(4):
        xx = cx - r * .75 + i * r * .5
        ss.rect(s, xx - r * .07, cy - r * .3, r * .14, r * .85, c)
    ss.rect(s, cx - r, cy + r * .6, r * 2, r * .14, c)


def twin_minmax(s, x, y, w, h):
    """Dois mapas em rampa, só máximo e mínimo em guias tracejadas curvas, legenda única e hastes até um trilho de ícones. Sabesp p.3."""
    m = M2((0, 0, 900, 751), (x, y, w, h))
    R(s, m, 0, 453, 900, 751, light(T, .62))
    ss.line(s, *m.p((5, 578)), *m.p((900, 578)), A, 1.25, dash=False)
    ss.line(s, *m.p((5, 566)), *m.p((5, 590)), A, 1.25, dash=False)
    br = states("BRA")
    ramp = (light(F, .45), light(F, .25), F, dark(F, .12), dark(F, .3), D)
    v1 = {"PA": 0, "AP": 0, "AC": 0, "RO": 0, "RR": 3, "AM": 2, "MT": 3, "PR": 5, "SP": 4, "MA": 1, "RS": 2, "SC": 3, "PE": 3, "AL": 4, "SE": 4}
    v2 = {"RR": 4, "SP": 5, "MG": 4, "PR": 4, "MS": 2, "GO": 2, "RJ": 3, "ES": 3, "AM": 0, "PA": 0, "AP": 0, "AC": 0, "RO": 0, "MT": 1, "RS": 1, "TO": 1, "BA": 2, "SC": 1}
    fz = z(m, 13, 5.5)
    for x0, vals, base, (t1_, t2_) in ((15, v1, 2, ("99.1%", "95.2%")), (472, v2, 1, ("92.3%", "90.2%"))):
        ramp2 = ramp if vals is v1 else (light(F, .62), light(F, .5), light(F, .3), F, dark(F, .15), dark(F, .3))
        px, py = geo(s, m.box(x0, 32, x0 + 362, 402), br, lambda u: ramp2[vals.get(u, base)], W, .4)
        cxy = m.p((x0 + 192, 406))
        # Guias curvas.
        a0, a1 = (px(-49.3), py(-15)), m.p((x0 + 78, 285))
        path(s, bez(a0, (a1[0] + (a0[0] - a1[0]) * .3, a0[1] + (a1[1] - a0[1]) * .9), a1, 10), INK, .6, DS.DASH)
        lab(s, a1[0] - .2, a1[1] + .01, .34, .13, t1_, size=fz, italic=True)
        b0, b1 = (px(-49), py(-22)), m.p((x0 + 275, 322))
        path(s, [b0, b1], INK, .6, DS.DASH)
        lab(s, b1[0] - .02, b1[1] - .05, .34, .13, t2_, size=fz, italic=True)
        # Haste com capitel até o trilho.
        sx = m.p((x0 + 192, 0))[0]
        ss.line(s, sx - .09, cxy[1], sx + .09, cxy[1], A, 1.75, dash=False)
        ss.line(s, sx, cxy[1], sx, m.p((0, 578))[1], A, 1, dash=True)
    grad(R(s, m, 410, 358, 536, 372, F), ((0, light(F, .55)), (.5, F), (1, D)), 0)
    t1(s, *m.box(390, 376, 440, 400), "0%", size=z(m, 13, 5), color=G4)
    t1(s, *m.box(500, 376, 570, 400), "100%", size=z(m, 13, 5), color=G4)
    r = 52 * min(m.sx, m.sy) * 1.15
    for cx0, t, ic in ((110, "Local jurisdiction", 0), (468, "Concession-based", 1), (787, "Multi-agency", 2)):
        cx, cy = m.p((cx0, 578))
        diamond(s, cx, cy, r, light(F, .35), A, 1)
        if ic == 0:
            pin(s, cx, cy + r * .42, r * .85, None or light(F, .35), W, INK)
        elif ic == 1:
            _hub(s, cx, cy, r * .42, INK)
        else:
            _temple(s, cx, cy, r * .42, INK)
        t1(s, *m.box(cx0 - 105, 640, cx0 + 105, 680), t, size=z(m, 16, 6))


def silhouette(s, x, y, w, h, iso="PER"):
    """País inteiro como uma forma só, degradê radial com centro aceso, rotas finas com nós em anel e legenda de traços. Alupar p.13."""
    m = M((0, 0, 731, 900), (x, y, w, h))
    c = countries_50m()
    box = m.box(122, 27, 695, 855)
    geo(s, box, {iso: c[iso]}, ("radial", ((0, light(F, .05)), (.5, dark(F, .3)), (1, dark(D, .55))), .47, .52), G4, .5, min_area=.02)
    mold(s, *m.box(40, 45, 110, 115), "[logo]", size=4)
    cols = (A, light(F, .2), dark(light(F, .25), .1), light(A, .4))
    routes = (((328, 592), (390, 642), (376, 662)), ((575, 700), (610, 672), (634, 660)), ((634, 660), (604, 612), (640, 595), (673, 595)), ((634, 717), (630, 724)))
    for rt, col, wd in zip(routes, cols, (1.75, 1.5, 1.25, 1)):
        path(s, m.ps(rt), col, wd)
        for p in (rt[0], rt[-1]) if len(rt) > 2 or wd == 1 else (rt[0],):
            cx, cy = m.p(p)
            sp = oval(s, cx, cy, .1, col); ss.set_alpha(sp, 30)
            oval(s, cx, cy, .045, col, border=W, width=.5)
    for i, (col, t) in enumerate(zip(cols, ("Route one, 500 kV", "Route two, 220 kV", "Route three, 220 kV", "Route four, 138 kV"))):
        yy = 800 + i * 22
        ss.line(s, *m.p((102, yy)), *m.p((134, yy)), col, 1.25, dash=False)
        t1(s, *m.box(142, yy - 11, 420, yy + 11), t, size=z(m, 11), align=L)


def network(s, x, y, w, h):
    """Rede densa de rotas sobre silhueta radial, com elipses tracejadas agrupando clusters, dentro de painel com KPIs. Alupar p.12."""
    m = M2((0, 0, 900, 833), (x, y, w, h))
    grad(R(s, m, 5, 5, 895, 828, T, F, width=1), ((0, light(F, .82)), (.8, light(F, .9)), (1, W)), 0)
    fk, fv = z(m, 24, 6), z(m, 21, 5.5)
    for cx, a, b in ((200, "Total capex", "$609 m"), (480, "Revenue, 30y", "$103 m/year"), (710, "Total length", "880 km")):
        t1(s, *m.box(cx - 130, 34, cx + 130, 72), a, size=fk, bold=True, color=D)
        t1(s, *m.box(cx - 130, 80, cx + 130, 112), b, size=fv, bold=True, color=F)
    ss.line(s, *m.p((95, 176)), *m.p((835, 176)), F, .75, dash=False)
    diamond(s, *m.p((95, 176)), .025, F); diamond(s, *m.p((835, 176)), .025, F)
    t1(s, *m.box(110, 150, 430, 176), "Plan group two", size=z(m, 19, 5.5), bold=True, italic=True, align=L)
    t1(s, *m.box(520, 150, 830, 176), "Plan group three", size=z(m, 19, 5.5), bold=True, italic=True, align=L)
    t1(s, *m.box(95, 192, 800, 228), "Mapping the transmission lines", size=z(m, 23, 6), bold=True, color=D, align=L)
    mold(s, *m.box(96, 254, 160, 318), "[logo]", size=5)
    c = countries_50m()
    box = m.box(262, 258, 672, 812)
    # Aura dos clusters sob a silhueta; contorno tracejado por cima.
    pts = c["PER"]["rings"][0]
    k = math.cos(math.radians(-9.2))
    sc = min(box[2] / ((max(p[0] for p in pts) - min(p[0] for p in pts)) * k), box[3] / (max(p[1] for p in pts) - min(p[1] for p in pts)))
    lo0, la1 = min(p[0] for p in pts), max(p[1] for p in pts)
    ox = box[0] + (box[2] - (max(p[0] for p in pts) - lo0) * k * sc) / 2
    oy = box[1] + (box[3] - (la1 - min(p[1] for p in pts)) * sc) / 2
    gx, gy = (lambda lo: ox + (lo - lo0) * k * sc), (lambda la: oy + (la1 - la) * sc)
    ell = ((-80.3, -5.7, 2.0, 3.2, 20), (-77.9, -9.5, 2.0, 3.0, -25), (-76.4, -13.9, 2.0, 2.7, -25), (-69.6, -14.4, 1.7, 2.7, 15))
    for lo, la, rx, ry, rot in ell:
        sp = oval(s, gx(lo), gy(la), rx * 2 * sc, W, h=ry * 2 * sc); sp.rotation = rot; ss.set_alpha(sp, 55)
    geo(s, box, {"PER": c["PER"]}, ("radial", ((0, light(F, .05)), (.5, dark(F, .3)), (1, dark(D, .55))), .47, .55), None)
    rnd = random.Random(11)
    spine = [(-80.3, -3.8), (-81, -5.2), (-79.6, -7.2), (-78.2, -9.2), (-77.1, -11.8), (-76.2, -13.6), (-75.2, -15.2), (-73, -16.4), (-71.2, -17.4), (-70.4, -17.9)]
    inner = [(-77, -11.8), (-75.6, -11.4), (-75.0, -13), (-73.8, -13.6), (-72, -13.6), (-70.3, -14.2), (-69.6, -12.7)]
    north = [(-79.6, -7.2), (-77.6, -7.3), (-75.7, -6.6), (-76.4, -8.9), (-75.6, -10.4), (-75.6, -11.4)]
    path(s, [(gx(a), gy(b)) for a, b in spine], A, 1.5)
    path(s, [(gx(a), gy(b)) for a, b in inner], light(A, .15), 1)
    path(s, [(gx(a), gy(b)) for a, b in north], light(F, .15), .75)
    nodes = list(spine + inner + north)
    pe = max(c["PER"]["rings"], key=area)
    for i in range(170):
        a0, b0 = rnd.choice(spine + inner + north + nodes[-30:])
        a1, b1 = a0 + rnd.uniform(-1.2, 1.2), b0 + rnd.uniform(-1, 1)
        a2, b2 = a1 + rnd.uniform(-.7, .7), b1 + rnd.uniform(-.7, .7)
        if not (inside(pe, (a1, b1)) and inside(pe, (a2, b2))):
            continue
        if len(nodes) > 120:
            break
        path(s, [(gx(a0), gy(b0)), (gx(a1), gy(b1)), (gx(a2), gy(b2))], (light(F, .3), light(F, .5), T)[i % 3], .4)
        nodes += [(a1, b1), (a2, b2)]
    extra = ((-73.4, -3.8), (-72.9, -4.0), (-73.2, -4.6), (-72.4, -4.3))
    nodes += list(extra)
    path(s, [(gx(a), gy(b)) for a, b in extra], T, .4)
    for a, b in nodes:
        oval(s, gx(a), gy(b), .022, dark(F, .3), border=W, width=.25)
    for lo, la, rx, ry, rot in ell:
        sp = oval(s, gx(lo), gy(la), rx * 2 * sc, None, h=ry * 2 * sc, border=dark(D, .2), width=.75, dash=True); sp.rotation = rot
    for i, (c_, t) in enumerate(((A, "500 kV"), (dark(F, .1), "220 kV"), (light(F, .15), "220 kV"), (light(F, .4), "50-72 kV"), (light(F, .65), "33-44 kV"))):
        yy = 680 + i * 24
        ss.line(s, *m.p((150, yy)), *m.p((178, yy)), c_, 1, dash=False)
        t1(s, *m.box(184, yy - 9, 300, yy + 9), t, size=z(m, 10), align=L)


def cutout_rows(s, x, y, w, h):
    """Só os estados servidos, ampliados e cortados, em degradê; guias tracejadas em cotovelo até linhas com logo e métrica. Cosan p.8."""
    m = M2((0, 0, 845, 900), (x, y, w, h), 1.15)
    br = states("BRA")
    keep = ("MS", "SP", "RJ", "PR", "SC", "RS")
    bounds = (-58.2, -40.9, -33.8, -17.4)
    px, py = geo(s, m.box(0, 40, 562, 890), {u: br[u] for u in keep}, lambda u: (((0, dark(F, .08)), (.55, dark(F, .5)), (1, "000000")), 0), W, .75, keep=False, bounds=bounds, clip=True, min_area=.01)
    fz = z(m, 16, 5)
    xr = m.p((640, 0))[0]
    t1(s, *m.box(690, 8, 830, 34), "Volume", size=fz, bold=True)
    ss.line(s, *m.p((705, 38)), *m.p((810, 38)), F, 1, dash=False); ss.line(s, *m.p((705, 46)), *m.p((810, 46)), F, 1, dash=False)
    rows = ((-53.3, -18.6, None, 97, "25%", "0.6 m/day"), (-47.4, -21.2, 428, 168, "51%", "0.7 m/day"), (-41.4, -22.36, None, 297, "19%", "2.4 m/day"), (-45.4, -23.75, 468, 453, "99%", "12 m/day"),
            (-48.4, -25.75, 395, 645, "64%", "0.8 m/day"), (-48.5, -27.6, 305, 750, "21%", "1.5 m/day"), (-53.0, -32.75, None, 835, "76%", "1.9 m/day"))
    for lo, la, xm, ly, pc, vol in rows:
        yy = m.p((0, ly))[1]
        xs, ys = px(lo), py(la)
        xmm = m.p((xm, 0))[0] if xm else None
        if xm:
            xmm = max(xmm, xs + .04)
        pts = [(xs, yy), (xr, yy)] if xm is None else [(xs, ys), (xmm, ys), (xmm, yy), (xr, yy)]
        path(s, pts, INK, .6, DS.DASH)
        mold(s, *m.box(562, ly - 34, 632, ly - 4), "[logo]", size=4)
        t1(s, xr + .02, yy - .07, .25, .14, pc, size=fz, align=L)
        rx = xr + .26
        ss.line(s, rx, yy - .08, rx, yy + .08, INK, .5, dash=False)
        t1(s, rx + .03, yy - .07, .55, .14, vol, size=fz, align=L)


def state_share_bar(s, x, y, w, h):
    """Dois estados unidos numa forma em degradê, com sombra suave, sobre barra 100% com hastes. Cury Construtora p.13."""
    m = M2((0, 0, 826, 450), (x, y, w, h), 1.25)
    br = states("BRA")
    R(s, m, 63, 360, 531, 435, F)
    grad(R(s, m, 63, 360, 531, 435, F, G4, width=.75), ((0, dark(F, .08)), (1, D)), 90)
    grad(R(s, m, 532, 360, 736, 435, F, G4, width=.75), ((0, light(F, .3)), (1, F)), 90)
    fz, fp = z(m, 16, 7), z(m, 13, 6)
    t1(s, *m.box(80, 372, 180, 425), "North", size=fz, color=W, align=L)
    t1(s, *m.box(440, 372, 522, 415), "72%", size=fp, color=W, bold=True, align=RT)
    t1(s, *m.box(548, 372, 620, 425), "South", size=fz, color=W, align=L)
    t1(s, *m.box(650, 372, 728, 415), "28%", size=fp, color=W, bold=True, align=RT)
    sh = {"U": merged(br, ("SP", "RJ"))}
    box = m.box(60, 2, 718, 300)
    # Hastes: nascem na barra e somem sob o mapa.
    px, py = None, None
    for cx, top in ((368, 240), (640, 150)):
        ss.line(s, *m.p((cx, top)), *m.p((cx, 350)), F, .75, dash=False)
        R(s, m, cx - 20, 351, cx + 20, 360, F); R(s, m, cx - 10, 346, cx + 10, 352, F)
    px, py = geo(s, box, sh, (((0, dark(F, .4)), (.55, F), (1, light(F, .4))), 135), "000000", .75, min_area=.01)
    for sp in list(s.shapes)[-len(sh["U"]["rings"]):]:
        soft_shadow(sp, 4, 2, 30)


def heat(s, cx, cy, rx, ry, k=1):
    """Mancha de calor nativa: oval com degradê radial e transparência."""
    stops = ((0, D, .95), (.3, F, .85), (.65, A, .55), (1, light(A, .6), .05)) if k else ((0, A, .75), (.55, A, .35), (1, light(A, .6), .03))
    return radial(oval(s, cx, cy, rx * 2, F, h=ry * 2), stops)


def staggered_heat(s, x, y, w, h):
    """Dois recortes de mapa desencontrados com calor, estrelas e rótulos com fio; painel dobrado com KPIs. Intelbras p.9."""
    m = M2((0, 0, 900, 413), (x, y, w, h))
    R(s, m, 592, 12, 900, 402, G1)
    poly(s, m, ((578, 0), (592, 12), (592, 402), (578, 413)), G3)
    R(s, m, 0, 0, 578, 413, G1)
    fa = z(m, 13, 5)
    rich(s, *m.box(50, 16, 520, 100), [[("The company runs a ", False, INK), ("dense network", True, INK), (" of resellers across major hubs, ensuring ", False, INK), ("availability", True, INK), (" and ", False, INK), ("channel efficiency", True, INK)]], size=fa, align=C, anchor=MSO_ANCHOR.MIDDLE)
    mold(s, *m.box(3, 125, 305, 283), "[mapa]", size=5)
    rnd = random.Random(3)
    for i in range(30):
        cx, cy = m.p((rnd.uniform(20, 290), rnd.uniform(138, 272)))
        heat(s, cx, cy, .055, .05, 0)
    heat(s, *m.p((133, 183)), .07, .065)
    ss.rect(s, *m.box(305, 175, 568, 345), G2)
    for px_, py_, rx, ry, k in ((430, 235, 90, 62, 0), (370, 280, 70, 45, 0), (500, 290, 60, 50, 0), (460, 255, 60, 48, 0), (425, 228, 30, 28, 1), (462, 258, 26, 34, 1), (462, 305, 12, 22, 1)):
        heat(s, *m.p((px_, py_)), rx * m.sx, ry * m.sy, k)
    star(s, *m.p((420, 230)), .045, F); star(s, *m.p((436, 236)), .045, D)
    t1(s, *m.box(312, 178, 370, 196), "[mapa]", size=5, color=G4, align=L)
    bx = R(s, m, 412, 126, 556, 152, W, F, width=.75); t1(s, *m.box(412, 126, 556, 152), "City", size=fa, align=C)
    ss.line(s, *m.p((302, 141)), *m.p((412, 141)), D, .75, dash=False); diamond(s, *m.p((412, 141)), .02, D)
    R(s, m, 3, 291, 190, 340, W, F, width=.75); tx(s, *m.box(8, 291, 186, 340), "Metropolitan region", size=fa, align=L)
    ss.line(s, *m.p((190, 310)), *m.p((303, 310)), D, .75, dash=False); diamond(s, *m.p((192, 310)), .02, D)
    star(s, *m.p((238, 354)), .035, F); t1(s, *m.box(246, 345, 330, 363), "Rival A", size=z(m, 10), align=L)
    star(s, *m.p((238, 373)), .035, D); t1(s, *m.box(246, 364, 330, 382), "Rival B", size=z(m, 10), align=L)
    def call(a, b, c, d, runs):
        rr(s, *m.box(a, b, c, d), W, .25, border=F, width=.75).line.dash_style = DS.DASH
        rich(s, *m.box(a + 8, b + 2, c - 8, d - 2), runs, size=fa, align=C, anchor=MSO_ANCHOR.MIDDLE)
    call(340, 342, 570, 406, [[("Advantage in ", False, INK), ("market penetration", True, INK), (", as peers are concentrated", False, INK)]])
    call(620, 30, 886, 90, [[("Average distance", True, INK), (" to a reseller is just ", False, INK), ("1.35 km", True, INK)]])
    call(620, 96, 886, 128, [[("Average rating", True, INK), (" is 4.7/5", False, INK)]])
    path(s, [m.p((545, 66)), m.p((605, 64))], F, 1, DS.DASH, arrow=.04)
    mold(s, *m.box(660, 142, 850, 345), "[print]", size=6)
    mold(s, *m.box(800, 150, 842, 192), "[logo]", size=4)
    tx(s, *m.box(620, 352, 886, 396), "Heat map of reseller concentration", size=fa, align=C)


def street_popup(s, x, y, w, h):
    """Cartão com recorte de rua em moldura tracejada, alfinetes por rede e legenda ligada por trapézio. RD Saude p.14."""
    m = M2((0, 0, 900, 446), (x, y, w, h))
    R(s, m, 0, 0, 900, 446, G1)
    R(s, m, 32, 20, 38, 78, F)
    t1(s, *m.box(46, 18, 560, 46), "Presence in the better areas", size=z(m, 17, 7), bold=True, align=L)
    tx(s, *m.box(46, 48, 880, 82), "The chain has wide reach, but it usually sits in the better neighbourhoods", size=z(m, 11, 5), align=L)
    grn = F
    poly(s, m, ((197, 120), (263, 92), (263, 410), (197, 384)), "D0D0D0")
    path(s, [m.p((197, 120)), m.p((263, 92))], grn, .75, DS.DASH)
    path(s, [m.p((197, 384)), m.p((263, 410))], grn, .75, DS.DASH)
    R(s, m, 32, 120, 197, 384, "DADADA", grn, dash=True, width=.75)
    ss.rect(s, *m.box(263, 92, 735, 410), G2)
    t1(s, *m.box(272, 98, 360, 122), "[mapa]", size=6, color=G4, align=L)
    R(s, m, 263, 92, 735, 410, None, grn, dash=True, width=.75)
    cols = (F, A, deep(A, .3) if False else light(F, .45), "000000")
    hh = .125
    pts = {3: [(385, 192), (421, 185), (438, 225), (549, 196), (661, 175), (471, 257), (486, 312), (565, 298), (603, 315), (548, 338), (617, 354), (622, 280), (721, 285)],
           1: [(511, 132), (530, 168), (588, 172), (461, 275), (480, 275)], 0: [(479, 245)], 2: [(500, 245), (645, 135)]}
    for k, ps in pts.items():
        for a, b in ps:
            pin(s, *m.p((a, b)), hh, cols[k], W)
    fz = z(m, 12, 5)
    for i, (c, t) in enumerate(zip(cols, ("Company", "Rival chain", "Second rival", "Small shops"))):
        yy = 170 + i * 65
        pin(s, *m.p((52, yy)), .15, c, W)
        tc = c if c != A and lum(c) < .55 else INK
        t1(s, *m.box(70, yy - 26, 194, yy), t, size=fz, bold=True, color=tc, align=L)
    R(s, m, 757, 212, 875, 277, W, grn, dash=True, width=.75)
    tx(s, *m.box(762, 214, 870, 275), "Just one store in that area", size=z(m, 11, 5), bold=True)


def terrain_plinth(s, x, y, w, h):
    """Recorte de terreno com alfinetes e distância, peanha em trapézio até o gráfico e guias pontilhadas à legenda. Sabesp p.33."""
    m = M2((0, 0, 900, 756), (x, y, w, h))
    R(s, m, 0, 0, 900, 412, G1)
    R(s, m, 25, 440, 875, 756, "F4F4F4")
    poly(s, m, ((0, 412), (900, 412), (875, 440), (25, 440)), G3)
    fz = z(m, 15, 5.5)
    pin(s, *m.p((66, 40)), .11, F, W); rich(s, *m.box(82, 14, 560, 38), [[("Operated", True, INK), (" by one firm, ", False, INK), ("drawn", True, INK), (" by another", False, INK)]], size=fz, anchor=MSO_ANCHOR.MIDDLE)
    pin(s, *m.p((590, 40)), .11, D, W); t1(s, *m.box(606, 14, 880, 38), "Power plant", size=fz, align=L)
    mold(s, *m.box(47, 42, 850, 373), "[mapa]", size=7)
    R(s, m, 596, 42, 850, 178, W, G3, dash=True, width=.5)
    rich(s, *m.box(606, 46, 842, 174), [[("One firm needed the ", False, INK), ("reservoirs full", True, INK), (" to generate; the other had to ", False, INK), ("drain them", True, INK)]], size=fz, align=C, anchor=MSO_ANCHOR.MIDDLE)
    neg = F
    pin(s, *m.p((228, 124)), .13, neg, W); t1(s, *m.box(165, 128, 300, 156), "Reservoir A", size=fz, bold=True)
    p1, p2 = m.p((575, 320)), m.p((735, 348))
    path(s, [p1, p2], neg, 1.25, DS.ROUND_DOT)
    t1(s, *m.box(610, 306, 720, 330), "9.3 km", size=fz, bold=True, color=neg)
    pin(s, *p1, .13, neg, W); t1(s, *m.box(440, 326, 562, 352), "Reservoir B", size=fz, bold=True)
    pin(s, *p2, .13, D, W); t1(s, *m.box(680, 350, 830, 374), "Plant", size=fz, bold=True)
    # Legenda do gráfico; as guias pontilhadas descem dos alfinetes até ela.
    ss.line(s, *m.p((376, 464)), *m.p((405, 464)), A, 1.5, dash=False)
    t1(s, *m.box(415, 452, 600, 476), "Abstraction", size=fz, align=L)
    R(s, m, 620, 459, 650, 468, D)
    t1(s, *m.box(658, 452, 880, 476), "Generation", size=fz, align=L)
    path(s, [m.p((545, 352)), m.p((385, 458))], A, .75, DS.ROUND_DOT)
    path(s, [m.p((735, 348)), m.p((635, 456))], D, .75, DS.ROUND_DOT)
    # Gráfico.
    ss.line(s, *m.p((48, 690)), *m.p((870, 690)), INK, .75, dash=False)
    tops = (643, 610, 606, 645, 535, 596, 652, 640, 572, 620, 645)
    vals = ("58", "99", "105", "56", "194", "118", "47", "63", "140", "88", "56")
    fl = z(m, 12, 5)
    for i, (t, v) in enumerate(zip(tops, vals)):
        cx = 85 + i * 74.6
        R(s, m, cx - 12, t, cx + 12, 690, D)
        lab(s, *m.box(cx - 22, t - 30, cx + 22, t - 6), v, size=fl)
        t1(s, *m.box(cx - 30, 698, cx + 30, 722), str(2015 + i), size=fl, align=C)
    path(s, catmull(m.ps(((85, 510), (150, 570), (225, 612), (300, 603), (385, 650), (460, 668), (535, 622), (600, 590), (680, 618), (755, 648), (830, 585)))), A, 1.5)
    lab(s, *m.box(65, 485, 107, 512), "15", fill=F, size=fl)
    lab(s, *m.box(810, 556, 858, 584), "14", fill=F, size=fl)


def _drop(s, cx, cy, r, c):
    """Selo em gota: círculo com a ponta superior direita em canto vivo."""
    oval(s, cx, cy, r * 2, c)
    ss.rect(s, cx, cy - r, r, r, c)


def phased_rollout(s, x, y, w, h):
    """Mapa pálido em cartão, marcos por fase com selos de status, arco pontilhado e ranking com selos e barras. Vasta p.23."""
    m = M2((0, 0, 900, 399), (x, y, w, h))
    bx = m.box(0, 0, 900, 399)
    rr(s, *bx, W, .06, border=G2, width=.75)
    br = states("BRA")
    pale = light(T, .55)
    geo(s, m.box(2, 30, 258, 396), {u: br[u] for u in REG["NE"] + ("TO", "PA", "GO", "MG", "ES")}, pale, None, keep=False, bounds=(-44, -34.6, -17, -2.6), clip=True)
    mag, lil, dk = F, light(F, .55), D
    fh, fn, fc = z(m, 14, 6), z(m, 13, 5.5), z(m, 12, 5.5)
    t1(s, *m.box(70, 10, 420, 34), "Regional attractiveness ranking", size=fh, bold=True, align=L)
    t1(s, *m.box(46, 158, 170, 182), "Northeast", size=fh, bold=True, italic=True, color=deep(A, .55), align=L)
    a0, a1 = m.p((295, 82)), m.p((176, 262))
    path(s, bez(a0, m.p((180, 110)), a1, 16), lil, .75, DS.ROUND_DOT, arrow=.03)
    pin(s, *m.p((308, 92)), .16, mag, W)
    pin(s, *m.p((174, 296)), .16, dk, W)
    oval(s, *m.p((262, 137)), .075, mag); oval(s, *m.p((262, 180)), .075, mag); oval(s, *m.p((246, 225)), .075, lil)
    for name, xa, yy, cx0, cw, ct, c, cy0 in (("City one", 334, 62, 332, 74, "Entry", mag, 75), ("City two", 288, 137, 400, 74, "Pilot", mag, 126), ("City three", 284, 180, 420, 74, "Pilot", mag, 169), ("City four", 268, 225, 400, 74, "M&A", lil, 213), ("City five", 206, 280, 196, 150, "Second wave", dk, 296)):
        t1(s, *m.box(xa, yy - 12, xa + 170, yy + 12), name, size=fn, bold=True, align=L)
        lab(s, *m.box(cx0, cy0, cx0 + cw, cy0 + 23), ct, fill=c, size=fc, adj=.1)
    # Rosa dos ventos e escala.
    cc = m.p((46, 345))
    oval(s, cc[0], cc[1], .13, None, border=deep(A, .55), width=.4)
    diamond(s, cc[0], cc[1], .055, deep(A, .55))
    ss.line(s, *m.p((22, 384)), *m.p((192, 384)), G4, .5, dash=False)
    for xx, t in ((22, "0"), (107, "250"), (192, "500 km")):
        ss.line(s, *m.p((xx, 379)), *m.p((xx, 389)), G4, .5, dash=False)
        t1(s, *m.box(xx - 20, 364, xx + 40, 378), t, size=4.2, color=G4, align=L)
    t1(s, *m.box(570, 16, 780, 40), "composite score 0-10", size=z(m, 12, 5), italic=True, color=G4, align=L)
    for i, (t, v, c, wd) in enumerate((("City one", "7.7", mag, 207), ("City two", "7.3", mag, 195), ("City three", "7.0", mag, 175), ("City four", "6.8", lil, 165), ("City five", "5.6", dk, 139))):
        yy = 82 + i * 68
        cx, cy = m.p((582, yy))
        _drop(s, cx, cy, .1, c)
        tx(s, cx - .1, cy - .1, .2, .2, str(i + 1), size=z(m, 13, 6), color=W, bold=True)
        t1(s, *m.box(640, yy - 28, 860, yy - 6), t, size=fn, bold=True, align=L)
        R(s, m, 630, yy - 6, 630 + wd, yy + 18, c)
        t1(s, *m.box(636 + wd, yy - 6, 690 + wd, yy + 18), v, size=fn, align=L)


# ---------- Malha municipal ----------
def inside(r, p):
    c = False
    for i in range(len(r)):
        a, b = r[i - 1], r[i]
        if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]:
            c = not c
    return c


def mesh(ring, n, seed=5):
    """Malha fictícia tipo municipal: células de Voronoi cortadas no contorno (sem base municipal no projeto)."""
    rnd = random.Random(seed)
    lo = [p[0] for p in ring]; la = [p[1] for p in ring]
    sites = []
    while len(sites) < n:
        p = (rnd.uniform(min(lo), max(lo)), rnd.uniform(min(la), max(la)))
        if inside(ring, p):
            sites.append(p)
    cells = []
    for i, a in enumerate(sites):
        near = sorted((b for j, b in enumerate(sites) if j != i), key=lambda b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)[:18]
        cell = [tuple(p) for p in ring]
        for b in near:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            nx, ny = b[0] - a[0], b[1] - a[1]
            f = lambda p: (p[0] - mx) * nx + (p[1] - my) * ny
            out = []
            for k in range(len(cell)):
                p, q = cell[k], cell[k - 1]
                fp, fq = f(p), f(q)
                if fp <= 0:
                    if fq > 0:
                        t = fq / (fq - fp); out.append((q[0] + (p[0] - q[0]) * t, q[1] + (p[1] - q[1]) * t))
                    out.append(p)
                elif fq <= 0:
                    t = fq / (fq - fp); out.append((q[0] + (p[0] - q[0]) * t, q[1] + (p[1] - q[1]) * t))
            cell = out
            if len(cell) < 3:
                break
        if len(cell) >= 3:
            cells.append((a, cell))
    return cells


def municipal_pair(s, x, y, w, h):
    """Dois mapas municipais em classes de cor saltando de painéis cinza com sombra, legenda e frase de insight. Sabesp p.24."""
    m = M2((0, 0, 900, 812), (x, y, w, h))
    ring = max(states("BRA")["SP"]["rings"], key=area)
    cells = mesh(ring, 230)
    ramp = (light(F, .85), light(F, .65), light(F, .42), light(F, .2), F, dark(F, .2), dark(F, .4), D)
    def cls(p, mode, r):
        lo, la = p
        if mode == 0:
            if la > -21.9 + .3 * math.sin(lo * 2) and r.random() < .62:
                return None
            v = (-la - 21) * 1.6 + (lo + 50) * -.12 + r.gauss(0, .9)
            if lo > -46.9 and la > -23.6:
                v -= 1
            return ramp[max(0, min(7, int(v)))]
        if la > -21.9 + .3 * math.sin(lo * 2) and r.random() < .6:
            return None
        v = 6 if (la < -23.1 and lo < -46.9) or lo < -50 else 7 if la > -21.5 else 3 + r.gauss(0, 1.1)
        return ramp[max(0, min(7, int(v)))]
    legends = (("< 200: low", "200-230: medium-low", "230-260: medium", "260-300: medium-high", "300-350: high", "350+: critical", "Not operated"), ("< 85%: high digital", "85-90%: good", "90-94%: partial", "94-97%: low", "97%: near analog", "Not operated"))
    fz, fi = z(m, 13, 4.5), z(m, 15, 5.2)
    for k, (py0, px0, py1, legend, runs) in enumerate(((100, 12, 385, legends[0], [[("High-loss areas are geographically concentrated,", True, INK), (" a disproportionate share of lost revenue", False, INK)]]),
                                                       (515, 8, 800, legends[1], [[("Most of the installed base remains analog,", True, INK), (" with the upgrade program running slowly", False, INK)]]))):
        soft_shadow(R(s, m, px0, py0, 755, py1, G1), 5, 2, 35)
        r = random.Random(11 + k)
        mt = py0 - 100 + (0 if k == 0 else -8)
        box = m.box(418, mt, 886, mt + 298)
        pts = ring
        lo0, lo1, la0, la1 = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
        kk = math.cos(math.radians((la0 + la1) / 2))
        sc = min(box[2] / ((lo1 - lo0) * kk), box[3] / (la1 - la0))
        ox, oy = box[0] + (box[2] - (lo1 - lo0) * kk * sc) / 2, box[1] + (box[3] - (la1 - la0) * sc) / 2
        for p, cell in cells:
            ss.poly(s, [(ox + (a - lo0) * kk * sc, oy + (la1 - b) * sc) for a, b in cell], cls(p, k, r) or "DCDCDC", W, .2)
        n = len(legend)
        for i, t in enumerate(legend):
            yy = py0 + 22 + i * (170 / n)
            c = G2 if i == n - 1 else ramp[int(i * 7 / max(1, n - 2))]
            R(s, m, px0 + 18, yy - 7, px0 + 32, yy + 7, c)
            t1(s, *m.box(px0 + 40, yy - 11, px0 + 330, yy + 11), t, size=fz, align=L)
        rich(s, *m.box(px0 + 16, py1 - 92, 640, py1 - 8), runs, size=fi, anchor=MSO_ANCHOR.MIDDLE)
        mold(s, *m.box(680, py1 - 78, 740, py1 - 18), "[logo]", size=4.5)


CITY = [[0,[[11,414],[15,417],[27,420],[36,425],[40,434],[38,447],[39,455],[43,460],[48,460],[63,467],[65,471],[69,473],[72,478],[79,486],[85,503],[85,509],[88,517],[89,523],[94,529],[98,539],[99,544],[102,548],[107,561],[115,575],[120,581],[184,619],[190,619],[293,626],[298,630],[310,656],[347,663],[352,666],[359,666],[383,670],[391,671],[397,666],[404,656],[409,653],[410,648],[414,643],[430,632],[445,633],[451,636],[456,635],[485,638],[492,642],[510,630],[517,618],[521,604],[520,584],[514,569],[524,557],[515,543],[516,541],[525,537],[526,535],[523,528],[510,513],[510,491],[514,487],[524,485],[528,483],[538,485],[542,477],[538,473],[510,462],[510,444],[499,437],[508,387],[512,379],[515,370],[519,364],[519,362],[510,353],[501,347],[487,332],[478,324],[478,313],[471,306],[459,301],[453,296],[404,277],[398,269],[400,250],[410,229],[385,177],[388,165],[381,160],[373,158],[349,148],[325,149],[311,138],[309,122],[316,117],[320,108],[325,103],[327,99],[333,91],[328,80],[327,74],[322,68],[321,62],[316,58],[307,62],[301,64],[292,72],[288,72],[287,78],[280,90],[268,98],[265,108],[270,113],[271,118],[266,125],[260,129],[249,127],[245,129],[244,131],[247,138],[257,144],[256,149],[251,152],[241,153],[230,148],[226,148],[215,144],[207,147],[204,149],[199,156],[198,163],[150,200],[150,249],[167,253],[168,256],[167,259],[146,268],[131,250],[120,242],[96,243],[85,247],[79,253],[72,264],[68,278],[69,288],[73,299],[74,307],[67,313],[62,319],[57,324],[51,337],[52,341],[45,354],[34,362],[30,368],[26,368],[20,372],[19,373],[21,378],[19,383],[23,394],[13,409]]],[2,[[111,557],[127,550],[173,519],[190,512],[207,508],[264,504],[280,502],[292,497],[298,488],[301,477],[301,439],[305,430],[312,422],[355,401],[362,395],[363,387],[353,363],[354,355],[360,348],[373,340],[391,333],[459,312],[473,307],[459,301],[453,296],[404,277],[398,269],[400,250],[410,229],[385,177],[388,165],[381,160],[373,158],[349,148],[325,149],[311,138],[309,122],[316,117],[320,108],[325,103],[327,99],[333,91],[328,80],[327,74],[322,68],[321,62],[316,58],[307,62],[301,64],[292,72],[288,72],[287,78],[280,90],[268,98],[265,108],[270,113],[271,118],[266,125],[260,129],[249,127],[245,129],[244,131],[247,138],[257,144],[256,149],[251,152],[241,153],[230,148],[226,148],[215,144],[207,147],[204,149],[199,156],[198,163],[150,200],[150,249],[167,253],[168,256],[167,259],[146,268],[131,250],[120,242],[96,243],[85,247],[79,253],[72,264],[68,278],[69,288],[73,299],[74,307],[67,313],[62,319],[57,324],[51,337],[52,341],[45,354],[34,362],[30,368],[26,368],[19,373],[21,378],[19,383],[23,394],[13,409],[11,414],[15,417],[27,420],[36,425],[40,434],[38,447],[39,455],[43,460],[48,460],[63,467],[65,471],[69,473],[72,478],[79,486],[85,503],[85,509],[88,517],[89,523],[94,529],[98,539],[99,544],[102,548],[105,558]]],[3,[[114,544],[128,538],[167,508],[182,500],[199,494],[261,483],[278,477],[292,468],[299,455],[302,439],[302,386],[305,370],[309,355],[322,327],[345,290],[354,279],[390,253],[399,244],[405,235],[407,222],[385,177],[388,167],[385,165],[366,155],[347,148],[325,149],[311,138],[267,130],[244,130],[244,131],[247,138],[257,144],[256,149],[251,152],[241,153],[230,148],[226,148],[215,144],[207,147],[204,149],[199,156],[198,163],[150,200],[150,249],[167,253],[168,256],[167,259],[146,268],[131,250],[120,242],[96,243],[85,247],[79,253],[72,264],[68,278],[69,288],[73,299],[74,307],[67,313],[62,319],[57,324],[51,337],[52,341],[45,354],[34,362],[30,368],[26,368],[20,372],[19,373],[21,378],[19,383],[23,394],[13,409],[11,414],[15,417],[27,420],[36,425],[40,434],[38,447],[39,455],[43,460],[48,460],[63,467],[65,471],[69,473],[72,478],[79,486],[85,503],[85,509],[88,517],[89,523],[94,529],[98,539],[98,544]]],[4,[[44,373],[52,376],[85,377],[95,380],[116,392],[135,410],[140,419],[155,454],[162,464],[170,470],[180,471],[192,470],[206,466],[219,461],[240,450],[245,443],[248,435],[255,400],[272,350],[281,317],[287,293],[288,281],[288,270],[285,258],[275,235],[255,205],[231,177],[222,170],[213,166],[205,165],[196,167],[187,174],[150,214],[150,249],[167,253],[168,256],[167,259],[146,268],[131,250],[120,242],[116,242],[82,272],[69,289],[73,299],[74,307],[67,313],[62,319],[57,324],[51,337],[52,341],[45,354],[39,358],[40,368]]],[5,[[79,306],[80,315],[83,324],[87,334],[100,350],[117,361],[139,369],[150,371],[160,372],[168,370],[186,362],[193,357],[205,345],[210,330],[210,313],[208,305],[205,300],[199,295],[191,291],[171,286],[150,285],[111,288],[88,295],[82,300]]],[5,[[234,430],[231,426],[226,422],[215,419],[208,419],[203,422],[198,426],[195,430],[195,436],[195,441],[198,445],[203,449],[215,453],[221,452],[226,449],[231,445],[234,441],[235,436]]],[5,[[203,229],[205,241],[211,252],[215,255],[226,255],[240,252],[250,245],[251,239],[252,223],[248,208],[245,205],[239,204],[224,210],[209,220],[205,225]]],[1,[[305,131],[297,132],[290,135],[284,140],[281,147],[280,155],[281,162],[284,169],[290,174],[297,177],[305,179],[312,177],[319,174],[325,169],[328,162],[330,155],[329,149],[325,149],[311,138],[310,131]]],[1,[[107,412],[103,405],[97,400],[90,397],[82,396],[73,397],[66,400],[60,405],[56,412],[55,420],[56,427],[60,434],[66,439],[73,442],[82,444],[90,442],[97,439],[103,434],[107,427],[109,420]]],[2,[[417,581],[416,587],[418,600],[425,610],[430,614],[444,621],[453,623],[470,625],[478,623],[497,616],[506,611],[520,600],[521,597],[520,584],[514,569],[524,557],[515,543],[516,541],[510,538],[490,533],[470,535],[460,538],[441,552],[425,568]]],[3,[[483,581],[480,577],[472,571],[463,571],[455,577],[452,581],[452,590],[455,594],[463,600],[472,600],[480,594],[483,590]]],[0,[[240,574],[234,569],[229,569],[224,572],[223,579],[229,584],[234,584],[239,581]]]]


def income_contour(s, x, y, w, h):
    """Contornos suavizados de renda (não administrativos), alfinetes em 4 tamanhos, legendas e cartão de código. Nubank p.25."""
    m = M2((0, 0, 900, 782), (x, y, w, h), 1.15)
    ramp = {0: light(F, .78), 1: light(F, .55), 2: light(F, .28), 3: dark(F, .05), 4: dark(F, .25), 5: D}
    base = True
    for lv, ring in CITY:
        pts = m.ps(ring)
        if base:
            ss.poly(s, pts, ramp[1], G4, 1); base = False
        else:
            ss.poly(s, pts, ramp[lv])
    k = min(m.sx, m.sy)
    for cx, ty, hh, c in ((106, 365, 122, "000000"), (197, 300, 122, "000000"), (311, 358, 96, "2B2B2B"), (135, 502, 72, "404040")):
        pin(s, *m.p((cx, ty)), hh * m.sy, c, W if c == "000000" else ramp[3])
    bx = m.box(556, 15, 868, 428)
    rr(s, *bx, G2, .08)
    tx(s, *bx, "[print]", size=7, color=G4)
    mold(s, *m.box(798, 5, 895, 102), "[logo]", size=5)
    fz = z(m, 15, 5.5)
    for ty, hh, c in ((608, 100, "000000"), (640, 88, "2B2B2B"), (676, 72, "404040")):
        pin(s, *m.p((596, ty)), hh * m.sy, c, W)
    tx(s, *m.box(646, 515, 890, 578), "High concentration of branches", size=fz, align=L)
    tx(s, *m.box(636, 612, 890, 675), "Low concentration of branches", size=fz, align=L)
    ss.line(s, *m.p((5, 678)), *m.p((545, 678)), G3, .5, dash=False)
    t1(s, *m.box(68, 682, 490, 706), "Income level", size=z(m, 16, 6))
    grad(R(s, m, 68, 710, 490, 740, F), ((0, ramp[0]), (.5, ramp[2]), (.8, ramp[3]), (1, ramp[5])), 0)
    for xx, t in ((68, "3,500"), (172, "35,000"), (280, "70,000"), (385, "106,000"), (490, "160,000")):
        t1(s, *m.box(xx - 50, 748, xx + 50, 772), t, size=z(m, 13, 4.5), color=G4)


# ---------- América Latina ----------
LATAM = ("MEX", "GTM", "BLZ", "HND", "SLV", "NIC", "CRI", "PAN", "COL", "VEN", "GUY", "SUR", "ECU", "PER", "BOL", "BRA", "PRY", "URY", "ARG", "CHL", "CUB", "HTI", "DOM", "JAM", "PRI", "BHS", "TTO")


def staircase_chips(s, x, y, w, h):
    """América Latina com três países ativos e cartões em escada, ligados por fios finos; cartão de depósitos abaixo. Nubank p.23."""
    m = M2((0, 0, 900, 742), (x, y, w, h), 1.3)
    c = countries_50m()
    act = ("MEX", "COL", "BRA")
    px, py = geo(s, m.box(2, 14, 594, 734), {k: c[k] for k in LATAM if k in c}, lambda k: F if k in act else G2, W, .35, bounds=(-118, -34.5, -56, 33), min_area=.05)
    tint = light(F, .88)
    fz, fl = z(m, 22, 6), z(m, 16, 6)
    for (a, b), (x0, y0, v1, v2), ly in zip(((-97, 26.5), (-73, 11), (-35, -6)), ((350, 4, "4M", "13M"), (548, 130, "1M", "4M"), (690, 263, "89M", "110M")), (53, 184, 316)):
        ss.line(s, *m.p((110 if ly == 53 else 350 if ly == 184 else 590, ly)), *m.p((x0, ly)), G3, .5, dash=False)
        rr(s, *m.box(x0, y0, x0 + 203, y0 + 106), tint, .16)
        for j, (yr, v) in enumerate((("23'", v1), ("25'", v2))):
            yy = y0 + 10 + j * 48
            t1(s, *m.box(x0 + 14, yy, x0 + 76, yy + 38), yr, size=fz, align=L)
            lab(s, *m.box(x0 + 82, yy, x0 + 184, yy + 38), v, fill=F, size=fl, adj=.15)
    rr(s, *m.box(552, 455, 875, 733), tint, .14)
    t1(s, *m.box(552, 468, 875, 512), "Deposits", size=z(m, 26, 7), bold=True, color=F)
    for i, v in enumerate(("6%", "18%", "76%")):
        yy = 530 + i * 64
        mold(s, *m.box(586, yy, 672, yy + 56), "[logo]", size=4.5)
        lab(s, *m.box(714, yy + 4, 830, yy + 50), v, fill=F, size=fl, adj=.15)


def coin_selector(s, x, y, w, h, active=0):
    """Três moedas com mini-mapa: a ativa escura com o estado aceso, seta sólida e nome em bold; as outras desbotadas. 3R Petroleum p.20."""
    m = M2((0, 0, 900, 87), (x, y, w, h), 1.7)
    br = states("BRA")
    sage = ss.mix(light(F, .55), G3, .7)
    d = 78 * min(m.sx, m.sy) * 1.35
    for k, (cx0, u, t) in enumerate(((54, ("CE", "RN", "PB", "PE"), "Cluster one"), (340, ("BA", "SE"), "Cluster two"), (626, ("RJ", "ES"), "Cluster three"))):
        on = k == active
        cx, cy = m.p((cx0, 43))
        oval(s, cx, cy, d, D if on else sage)
        grey = (lambda v: gray_state(v, ("D8D8D8", "C8C8C8", "E4E4E4", "BDBDBD", "CFCFCF"))) if on else (lambda v: gray_state(v, ("F2F2F2", "E6E6E6", "FAFAFA", "EDEDED", "F6F6F6")))
        q = d * .78
        geo(s, (cx - q / 2, cy - q / 2, q, q), br, lambda v: (A if on else light(F, .55)) if v in u else grey(v), None)
        c = D if on else sage
        ar0, ar1 = cx + d / 2, m.p((cx0 + 92, 0))[0]
        ss.line(s, ar0, cy, ar1 - .05, cy, c, 1.5, dash=False)
        ss.poly(s, ((ar1, cy), (ar1 - .07, cy - .05), (ar1 - .07, cy + .05)), c)
        t1(s, ar1 + .03, cy - .1, .72, .2, t, size=z(m, 12, 5.5), bold=True, color=c, align=L)


def portrait_leaders(s, x, y, w, h):
    """Retratos em círculo ligados por fio com losango ao país de cada conversa, América Latina em três tons. BTG Pactual p.62."""
    m = M2((0, 0, 900, 679), (x, y, w, h), 1.2)
    c = countries_50m()
    op = ("MEX", "COL", "PER", "CHL", "ARG")
    px, py = geo(s, m.box(300, 8, 882, 668), {k: c[k] for k in LATAM if k in c}, lambda k: dark(D, .2) if k in op else F if k == "BRA" else G3, None, bounds=(-118, -34.5, -56, 33), min_area=.05)
    fn, fr = z(m, 19, 5.5), z(m, 17, 5)
    for yy, cty, n, r_ in ((233, (-74.5, 4.5), "First Interviewee", "Executive director, country unit"), (487, (-66.5, -33), "Second Interviewee", "Associate partner, country unit")):
        cy = m.p((0, yy))[1]
        ss.line(s, m.p((138, 0))[0], cy, px(cty[0]), cy, INK, 1, dash=False)
        diamond(s, m.p((138, 0))[0], cy, .03, INK)
        k = 106 * min(m.sx, m.sy) * 1.2
        mold(s, m.p((68, 0))[0] - k / 2, m.p((0, yy - 1))[1] - k / 2, k, k, "[foto]", size=5, is_oval=True)
        t1(s, *m.box(132, yy + 12, 520, yy + 42), n, size=fn, bold=True, color="404040", align=L)
        t1(s, *m.box(132, yy + 48, 530, yy + 76), r_, size=fr, color="404040", align=L)
        t1(s, *m.box(132, yy + 82, 530, yy + 110), "Conversation held on 23/02", size=fr, italic=True, color="404040", align=L)


# ---------- Mundo ----------
HI3 = ("CHN", "JPN", "DEU", "ITA", "GBR", "FRA", "ESP", "KOR", "IDN")
HI2 = ("BRA", "IND", "RUS", "AUS", "ARG", "MEX", "PER", "CHL", "PHL", "MYS", "VNM", "THA", "POL", "COL", "CAN", "TUR", "PRT")
HI1 = ("SAU", "EGY", "NGA", "ZAF", "NZL", "KAZ", "UKR", "IRN", "ROU", "NOR", "SWE", "FIN", "ECU", "PAK", "OMN", "NLD", "GRC", "BOL", "VEN")


def world_score(s, x, y, w, h):
    """Mundo por país em rampa de pontuação, cinza para sem nota, hachura para o excluído e cartão de critérios sobreposto. RBI p.38."""
    m = M2((0, 0, 900, 380), (x, y, w, h), 1.25)
    c = countries_50m()
    merc = lambda la: math.degrees(math.log(math.tan(math.radians(45 + max(la, -60) / 2))))
    shp = {k: {"rings": [[(a, merc(b)) for a, b in r] for r in v["rings"] if area(r) > .08]} for k, v in c.items() if k != "ATA"}
    shp = {k: v for k, v in shp.items() if v["rings"]}
    hs = ("USA", "CAN")
    def fill(k):
        return dark(F, .08) if k in HI3 else light(F, .35) if k in HI2 else light(F, .68) if k in HI1 else G2
    px, py = geo(s, m.box(240, 0, 886, 374), {k: v for k, v in shp.items() if k not in hs}, fill, W, .2, keep=False, bounds=(-170, 180, merc(-56), merc(78)), clip=True)
    n0 = len(s.shapes)
    geo(s, m.box(240, 0, 886, 374), {k: v for k, v in shp.items() if k in hs}, G2, G3, .2, keep=False, bounds=(-170, 180, merc(-56), merc(78)), clip=True)
    for sp in list(s.shapes)[n0:]:
        hatch(sp, G3, W)
    grad(R(s, m, 472, 332, 748, 341, F), ((0, W), (.5, light(F, .4)), (1, dark(F, .08))), 0)
    fz = z(m, 8, 4.5)
    for xx, t in ((472, "Low"), (610, "Medium"), (748, "High")):
        t1(s, *m.box(xx - 35, 343, xx + 35, 356), t, size=fz, color=G4)
    t1(s, *m.box(540, 358, 680, 372), "Expansion score", size=4.5, color=G4)
    bx = m.box(8, 24, 260, 352)
    soft_shadow(rr(s, *bx, W, .06, border=G2, width=.75), 5, 2, 35)
    R(s, m, 60, 16, 208, 30, W)
    t1(s, *m.box(60, 12, 208, 32), "Criteria", size=z(m, 13, 6), bold=True, italic=True, color=F)
    tx(s, *m.box(28, 38, 250, 90), "Which factors best measure growth?", size=z(m, 15, 6), align=L)
    fi = z(m, 10, 4.5)
    for i, (r_, a, b) in enumerate((("I", "Penetration:", " units per capita"), ("II", "Market size:", " addressable pool"), ("III", "Income:", " GDP per capita"), ("IV", "Culture:", " category match"), ("V", "Population:", " log of size"))):
        yy = 112 + i * 46
        bb = m.box(32, yy, 56, yy + 26)
        rr(s, *bb, F, .15)
        tx(s, *bb, r_, size=z(m, 10, 5), color=W, bold=True)
        rich(s, *m.box(66, yy - 8, 252, yy + 34), [[(a, True, INK), (b, False, INK)]], size=fi, anchor=MSO_ANCHOR.MIDDLE)
    mold(s, *m.box(0, 8, 44, 44), "[logo]", size=3.5)


def _us_dots(rnd, n, ring, k=1.0):
    metros = ((-74, 40.7, 9), (-71, 42.3, 3), (-77, 38.9, 5), (-75.2, 40, 3), (-80.2, 25.8, 4), (-81.5, 28.5, 4), (-84.4, 33.7, 5), (-87.7, 41.9, 7), (-83, 42.3, 4), (-81.7, 41.4, 3), (-79.9, 40.4, 2), (-84.5, 39.1, 2), (-86.2, 39.8, 2), (-90.2, 38.6, 2), (-94.6, 39.1, 2), (-93.2, 45, 2),
              (-95.4, 29.8, 5), (-97, 32.8, 5), (-98.5, 29.5, 2), (-90.1, 30, 2), (-86.8, 36.2, 3), (-80.8, 35.2, 3), (-78.6, 35.8, 2), (-118.2, 34, 8), (-117.2, 32.8, 3), (-122.3, 37.8, 4), (-122.3, 47.6, 3), (-112, 33.4, 3), (-105, 39.7, 2), (-111.9, 40.7, 2), (-115.2, 36.2, 2), (-122.6, 45.5, 2))
    tot = sum(a[2] for a in metros)
    out = []
    while len(out) < n:
        if rnd.random() < .52:
            p = (rnd.uniform(-100, -68), rnd.uniform(25, 47)) if rnd.random() < .85 else (rnd.uniform(-124, -100), rnd.uniform(30, 49))
        else:
            v = rnd.random() * tot
            for lo, la, wt in metros:
                v -= wt
                if v <= 0:
                    break
            sd = rnd.choice((.2, .45, .9, 1.5)) * k
            p = (rnd.gauss(lo, sd), rnd.gauss(la, sd * .8))
        if inside(ring, p):
            out.append(p)
    return out


def dot_maps(s, x, y, w, h):
    """Dois mapas de pontos antes/depois, com milhares de pontos numa forma só e cartão colado à esquerda. RBI p.21."""
    m = M2((0, 0, 900, 884), (x, y, w, h), 1.35)
    us = {k: v for k, v in states("USA").items() if k not in ("AK", "HI")}
    ring = max(countries_50m()["USA"]["rings"], key=area)
    bounds = (-125, -66.8, 24.4, 49.5)
    for k, (yy, y1, n, ky, a, b, cy0, cy1) in enumerate(((60, 398, 3200, "2013", "5,677", "1,004", 45, 395), (525, 862, 4200, "2017", "7,086", "1,356", 515, 872))):
        R(s, m, 345, yy - 6, 880, y1, "FAFAFA")
        px, py = geo(s, m.box(340, yy, 880, y1), us, "FAFAFA", "E6E6E6", .3, bounds=bounds)
        rnd = random.Random(21 + k)
        r_ = .0052
        cs = []
        for lo, la in _us_dots(rnd, n, ring, 1 - k * .15):
            ax, ay = px(lo), py(la)
            cs.append(((ax - r_, ay), (ax, ay - r_), (ax + r_, ay), (ax, ay + r_)))
        contours(s, cs, dark(F, .05) if not k else dark(F, .35))
        bx = m.box(8, cy0, 330, cy1)
        soft_shadow(rr(s, *bx, W, .05, border=G2, width=.75), 5, 2, 30)
        R(s, m, 100, cy0 - 8, 240, cy0 + 8, W)
        t1(s, *m.box(90, cy0 - 26, 250, cy0 + 22), ky, size=z(m, 30, 8), bold=True, color=F)
        fn = z(m, 30, 8.5)
        rich(s, *m.box(26, cy0 + 40, 322, cy1 - 12), [[(a, True, F), (" network units", False, INK)], [("", False, INK)], [(b, True, F), (" franchise groups", False, INK)]], size=fn, anchor=MSO_ANCHOR.MIDDLE)
    for dy in (0, 16):
        path(s, m.ps(((148, 432 + dy), (170, 448 + dy), (192, 432 + dy))), G3, 2)


# ---------- Reaproveitamentos ----------
def wedge_drilldown(s, x, y, w, h):
    """Cunha colorida de um segmento da barra para um painel com barras, conclusão e cópia reduzida do mapa. RD Saude p.39."""
    m = M2((0, 0, 900, 759), (x, y, w, h), 1.25)
    R(s, m, 0, 105, 34, 170, G2); R(s, m, 0, 170, 34, 318, F); R(s, m, 0, 318, 34, 748, G2)
    R(s, m, 34, 140, 38, 748, "000000")
    fl = z(m, 15, 5)
    for yy, t in ((126, "1.9"), (243, "2.5"), (532, "7.6")):
        lab(s, *m.box(0, yy - 13, 44, yy + 13), t, fill=G4 if yy != 243 else F, size=fl)
    poly(s, m, ((38, 170), (205, 3), (205, 755), (38, 318)), light(F, .15))
    R(s, m, 205, 3, 900, 755, G1, F, width=1.5)
    # Ícone simples no feixe.
    bx = m.box(92, 212, 175, 268)
    ss.rect(s, *bx, None, W, width=.75)
    ss.line(s, *m.p((133, 268)), *m.p((133, 282)), W, .75, dash=False); ss.line(s, *m.p((118, 282)), *m.p((148, 282)), W, .75, dash=False)
    t1(s, *m.box(240, 14, 890, 60), "Online revenue", size=z(m, 30, 8), bold=True, color=F)
    ss.line(s, *m.p((380, 65)), *m.p((738, 65)), F, 1, dash=False)
    t1(s, *m.box(232, 76, 880, 100), "% of online revenue in the total", size=z(m, 16, 5), italic=True, color=G4, align=L)
    for i, t in enumerate((282, 263, 242, 225, 212, 197, 183, 167, 152, 137, 123, 108)):
        cx = 297 + i * 45.4
        R(s, m, cx, t, cx + 31, 334, F)
    for i in range(6):
        t1(s, *m.box(280 + i * 90.8, 344, 280 + i * 90.8 + 70, 366), str(2024 + i * 2) + " E", size=z(m, 13, 4.5), align=L)
    path(s, m.ps(((340, 170), (372, 142), (470, 132), (800, 132))), dark(F, .35), 1.25, DS.DASH)
    lab(s, *m.box(282, 174, 342, 202), "18.2", size=fl); lab(s, *m.box(370, 124, 432, 152), "24.2%", size=fl); lab(s, *m.box(461, 118, 527, 146), "25.0%", size=fl); lab(s, *m.box(778, 118, 842, 146), "25.0%", size=fl)
    rich(s, *m.box(260, 374, 884, 430), [[("The company has an edge online because stores work as hubs", True, INK)]], size=z(m, 18, 5.5), align=C, anchor=MSO_ANCHOR.MIDDLE)
    pts = m.ps(((356, 478), (356, 462), (746, 462), (746, 478)))
    path(s, pts, F, .75, DS.ROUND_DOT)
    path(s, m.ps(((557, 462), (557, 435))), F, .75, DS.ROUND_DOT)
    ss.line(s, *m.p((546, 435)), *m.p((568, 435)), F, 1.25, dash=False)
    tint_map(s, m.box(425, 470, 685, 740), .06)
    fc = z(m, 11, 4.5)
    tint_counts(s, m, (("121 stores", "N", 450, 485, 480, "l"), ("443 stores", "NE", 618, 655, 514, "r"), ("308 stores", "CO", 475, 535, 642, "l"), ("1,700 stores", "SE", 600, 636, 676, "r"), ("381 stores", "S", 480, 540, 706, "l")), fc)


def mini_tint(s, x, y, w, h):
    """O mapa de 5 tons em um terço do tamanho, em cartão, com selo de total. RD Saude p.2."""
    m = M2((0, 0, 733, 390), (x, y, w, h), 1.15)
    R(s, m, 0, 0, 733, 390, G1)
    R(s, m, 728, 0, 733, 390, F)
    tint_map(s, m.box(160, 6, 545, 388), .09)
    fc = z(m, 15, 5)
    tint_counts(s, m, (("121 stores", "N", 122, 165, 123, "l"), ("443 stores", "NE", 538, 608, 123, "r"), ("308 stores", "CO", 250, 320, 262, "l"), ("1,700 stores", "SE", 435, 510, 298, "r"), ("381 stores", "S", 290, 330, 357, "l")), fc)
    bx = m.box(8, 283, 144, 374)
    R(s, m, 8, 283, 144, 374, dark(F, .05), W, dash=True, width=.5)
    t1(s, *m.box(8, 288, 144, 316), "2,953 stores", size=z(m, 14, 5), color=W, bold=True)
    pin(s, *m.p((26, 346)), .1, W, dark(F, .05))
    tx(s, *m.box(44, 318, 142, 372), "14 hubs", size=z(m, 12, 5), color=W, align=L)


def clipped_rules(s, x, y, w, h):
    """Metade leste do mapa em degradê escondida atrás do cartão da frente, com rabiscos brancos e títulos sobre fios longos. Alupar p.3."""
    m = M2((0, 0, 840, 466), (x, y, w, h), 1.15)
    c = countries_50m()
    geo(s, m.box(8, 24, 282, 466), {"BRA": c["BRA"]}, (((0, D), (.5, dark(F, .1)), (1, F)), 0), None, keep=False, bounds=(-57.6, -34.7, -31, 4.6), clip=True, min_area=.05)
    for pts in (((45, 150), (58, 122), (82, 128), (60, 148), (78, 170), (108, 155), (140, 148), (155, 165)), ((112, 155), (118, 178)), ((207, 168), (240, 158)), ((255, 165), (258, 188)),
                ((40, 215), (32, 258), (20, 268), (46, 268), (70, 282)), ((122, 248), (145, 225)), ((155, 205), (170, 207)), ((108, 282), (145, 287)), ((165, 248), (190, 258), (178, 320), (208, 300)),
                ((190, 335), (160, 355), (125, 370), (90, 385), (50, 412), (62, 430), (78, 436))):
        path(s, m.ps(pts), W, 1.25)
    R(s, m, 0, 0, 7, 466, W); R(s, m, 5, 0, 8, 466, D)
    fh, fs = z(m, 19, 6.5), z(m, 15, 5.5)
    for yy, x0, xt, a, b in ((131, 232, 252, "Transmission", "44 assets and 10,095 km of lines"), (249, 222, 274, "Generation", "798 MW installed across 16 plants"), (372, 186, 226, "International", "Presence in three countries, 1,591 km")):
        xe = 790 + (30 if yy == 249 else 0)
        ss.line(s, *m.p((x0, yy)), *m.p((xe, yy)), D, 1, dash=False)
        diamond(s, *m.p((xe, yy)), .03, D)
        t1(s, *m.box(xt, yy - 34, 700, yy - 2), a, size=fh, bold=True, italic=True, color=dark(D, .2), align=L)
        t1(s, *m.box(max(xt + 18, 292 - (yy > 300) * 40), yy + 8, 830, yy + 38), b, size=fs, color=G4, align=L)


ACT = ("MA", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MG", "RJ", "SP", "MS", "PR", "DF")


def logo_bracket(s, x, y, w, h):
    """Estados ativos com guias tracejadas até uma coluna de logos e um colchete tracejado até o texto. Rede D'Or p.17."""
    m = M2((0, 0, 1180, 718), (x, y, w, h), 1.2)
    px, py = geo(s, m.box(12, 8, 712, 714), states("BRA"), lambda u: D if u in ACT else gray_state(u), W, .25)
    xb = 905
    for (lo, la), ly in (((-37.2, -7.8), 225), ((-39, -13), 337), ((-41.3, -22.2), 484), ((-46.3, -24), 537)):
        yy = m.p((0, ly))[1]
        path(s, [(px(lo), yy), (m.p((xb, 0))[0], yy)], D, .6, DS.DASH)
    yy0 = m.p((0, 113))[1]
    xs = m.p((528, 0))[0]
    path(s, [(xs, py(-2.6)), (xs, yy0), (m.p((xb, 0))[0], yy0)], D, .6, DS.DASH)
    for ly in (113, 225, 337, 484, 537):
        bx = m.box(600, ly - 24, 790, ly + 22)
        mold(s, bx[0] + bx[2] * .1, bx[1], bx[2] * .8, bx[3], "[logo]", size=z(m, 12, 5))
    path(s, m.ps(((xb, 85), (xb, 537))), D, .6, DS.DASH)
    path(s, m.ps(((xb, 311), (950, 311))), D, .6, DS.DASH)
    tx(s, *m.box(956, 230, 1178, 392), "Regional brands keep their name while the group adds scale", size=z(m, 15, 6), align=L)


def active_mini(s, x, y, w, h, active=ACT, title="I. Spread national presence"):
    """Mapa mini com estados ativos em cor escura e inativos em cinzas, sob título numerado com fio. Rede D'Or p.8; p.9 troca os estados."""
    m = M2((0, 0, 693, 450), (x, y, w, h), 1.25)
    R(s, m, 0, 0, 693, 450, G1)
    t1(s, *m.box(8, 4, 680, 36), title, size=z(m, 26, 8), bold=True, color=D, align=L)
    ss.line(s, *m.p((3, 42)), *m.p((685, 42)), D, 1.5, dash=False)
    t1(s, *m.box(8, 52, 680, 84), "States where the company operates", size=z(m, 22, 6), color=G4, align=L)
    geo(s, m.box(160, 100, 500, 440), states("BRA"), lambda u: D if u in active else gray_state(u), W, .2)


def dot_clusters(s, x, y, w, h):
    """Estados em degradê contínuo norte-sul, pontos de dois donos colados por metrópole, placas translúcidas e tabela. Cury Construtora p.24."""
    m = M2((0, 0, 900, 754), (x, y, w, h), 1.3)
    br = states("BRA")
    c0, c1 = dark(light(D, .1), .05), light(F, .3)
    lat = lambda la, lo: max(0, min(1, (6 - la) / 40 * .78 + (lo + 74) / 40 * .22))
    n0 = len(s.shapes)
    px, py = geo(s, m.box(28, 34, 742, 750), br, F, W, 1)
    for u, sp in zip([u for u, v in br.items() for _ in v["rings"]], list(s.shapes)[n0:]):
        r = max(br[u]["rings"], key=area)
        lo = sum(p[0] for p in r) / len(r)
        t0, t1_ = lat(max(p[1] for p in r), lo), lat(min(p[1] for p in r), lo)
        grad(sp, ((0, ss.mix(c0, c1, t0)), (1, ss.mix(c0, c1, t1_))), 90)
    rnd = random.Random(4)
    bright = light(F, .25)
    placed = []
    def cluster(lo, la, n, sd, c):
        # Pontos colados, mas sem empilhar: descarta o que cairia em cima de outro.
        for _ in range(n * 30):
            if n <= 0:
                break
            cx, cy = px(lo + rnd.gauss(0, sd)), py(la + rnd.gauss(0, sd * .8))
            if any((cx - a) ** 2 + (cy - b) ** 2 < .042 ** 2 for a, b in placed):
                continue
            placed.append((cx, cy)); n -= 1
            oval(s, cx, cy, .042, c, border=dark(c, .15), width=.4)
    cluster(-47.6, -22.2, 7, .55, dark(D, .1)); cluster(-46.2, -23.5, 3, .3, dark(D, .1)); cluster(-43.6, -22.75, 3, .3, dark(D, .1))
    cluster(-63.5, -4.8, 7, .8, bright)
    cluster(-36.8, -7.2, 4, .3, bright); cluster(-49.2, -16.6, 5, .4, bright); cluster(-44.5, -19, 9, .8, bright)
    cluster(-48.5, -22.3, 10, .9, bright); cluster(-43.6, -22.9, 4, .35, bright); cluster(-46.6, -23.6, 4, .4, bright)
    fz = z(m, 13, 5)
    for xx, c, t in ((300, dark(D, .1), "Peer A"), (408, bright, "Peer B")):
        oval(s, *m.p((xx, 19)), .06, c, border=dark(c, .15), width=.4)
        t1(s, *m.box(xx + 10, 6, xx + 80, 32), t, size=fz, align=L)
    # Tabela por cima do canto inferior esquerdo.
    R(s, m, 6, 460, 238, 698, W, D, width=1)
    t1(s, *m.box(10, 472, 90, 500), "Region", size=fz, bold=True, color=D); t1(s, *m.box(110, 464, 236, 508), "Market", size=fz, bold=True, color=D)
    ss.line(s, *m.p((6, 510)), *m.p((238, 510)), "000000", 1, dash=False)
    for i, (a, b) in enumerate((("Midwest", "$13 bn"), ("South", "$22 bn"), ("North", "$11 bn"), ("Northeast", "$22 bn"), ("Southeast", "$59 bn"))):
        yy = 516 + i * 36
        t1(s, *m.box(10, yy, 106, yy + 34), a, size=fz, bold=True, color=D); t1(s, *m.box(110, yy, 234, yy + 34), b, size=fz)
    # Placas sangrando à direita.
    for y0, y1, xx, a, p, q in ((330, 402, 652, "Avg price per unit:", "A: 336k", "B: 239k"), (405, 475, 650, "Landbank years left:", "A: 2", "B: 8"), (479, 549, 606, "Land in incentive zone:", "A: 65%", "B: 45%")):
        sp = R(s, m, xx, y0, 900, y1, F)
        grad(sp, ((0, F, .6), (1, light(F, .2), .95)), 0)
        t1(s, *m.box(xx + 8, y0 + 8, 894, y0 + 36), a, size=fz, color=W, align=RT)
        t1(s, *m.box(xx + 8, y0 + 38, 776, y0 + 66), p, size=fz, color=W, align=RT)
        t1(s, *m.box(780, y0 + 38, 894, y0 + 66), q, size=fz, color=W, align=RT)


# ---------- Escala ----------
DW, DH = 3.7, 2.6  # caixa de projeto: acima dela a peça cresce por inteiro, fontes e fios inclusive


def fit(fn):
    """Desenha na caixa de projeto e amplia tudo para a caixa pedida, sem mudar proporção entre texto, marcas e mapa."""
    @functools.wraps(fn)
    def wrap(s, x, y, w, h, *a, **k):
        q = min(w / DW, h / DH)
        if q <= 1.02:
            return fn(s, x, y, w, h, *a, **k)
        n0 = len(s.shapes._spTree)
        fn(s, x, y, w / q, h / q, *a, **k)
        E = 914400
        for el in list(s.shapes._spTree)[n0:]:
            for xf in el.iter(qn("a:xfrm")):
                off, ext = xf.find(qn("a:off")), xf.find(qn("a:ext"))
                off.set("x", str(int(x * E + (int(off.get("x")) - x * E) * q))); off.set("y", str(int(y * E + (int(off.get("y")) - y * E) * q)))
                ext.set("cx", str(int(int(ext.get("cx")) * q))); ext.set("cy", str(int(int(ext.get("cy")) * q)))
            for rp in el.iter(qn("a:rPr")):
                if rp.get("sz"):
                    rp.set("sz", str(int(int(rp.get("sz")) * q)))
            for ln in el.iter(qn("a:ln")):
                if ln.get("w"):
                    ln.set("w", str(int(int(ln.get("w")) * q)))
    return wrap


for _n in ("dark_glow", "europe_tabs", "chamfer_rail", "funnel_clusters", "wedge_funnel", "region_tint", "triptych", "twin_counts", "twin_minmax", "silhouette", "network", "cutout_rows",
           "state_share_bar", "staggered_heat", "street_popup", "terrain_plinth", "phased_rollout", "municipal_pair", "income_contour", "staircase_chips", "coin_selector", "portrait_leaders",
           "world_score", "dot_maps", "wedge_drilldown", "mini_tint", "clipped_rules", "logo_bracket", "active_mini", "dot_clusters"):
    globals()[_n] = fit(globals()[_n])


# ---------- Galeria ----------
SLIDES = [
    ("Brazil maps as showpieces", "Dark slide, chamfered panels and wedges that carry the map into the data",
     [("Dark outline with glow", "CSN Liability p.24", dark_glow), ("Europe gradient under tabs", "CSN-AM p.26", europe_tabs), ("Between chamfered panels", "CSN-AM p.23", chamfer_rail),
      ("Funnel wedge to clusters", "3R Petroleum p.19", funnel_clusters), ("Grey wedge into funnel", "Nubank p.13", wedge_funnel), ("Region tint with pins", "RD Saude p.25", region_tint)]),
    ("Comparisons, silhouettes and territory cut-outs", "Small multiples, min/max leaders and single-shape countries",
     [("Hue per competitor", "RD Saude p.11", triptych), ("Twin counts, own scales", "BTG Pactual p.87", twin_counts), ("Twin min/max, icon rail", "Sabesp p.3", twin_minmax),
      ("Silhouette with routes", "Alupar p.13", silhouette), ("Network with dashed clusters", "Alupar p.12", network), ("Cut-out with logo rows", "Cosan p.8", cutout_rows)]),
    ("Zooms into local geography", "Share bars, street tiles and plinths; street rasters stay as image moulds",
     [("Silhouette on share bar", "Cury p.13", state_share_bar), ("Staggered zooms with heat", "Intelbras p.9", staggered_heat), ("Street popup, trapezoid legend", "RD Saude p.14", street_popup),
      ("Terrain tile on a plinth", "Sabesp p.33", terrain_plinth), ("Phased rollout card", "Vasta p.23", phased_rollout), ("Municipal pair on panels", "Sabesp p.24", municipal_pair)]),
    ("Contours, chips and selectors", "Smoothed bands, staircase cards, navigation coins and world scoring",
     [("Income contours with pins", "Nubank p.25", income_contour), ("Staircase chips", "Nubank p.23", staircase_chips), ("Mini-map coin selector", "3R Petroleum p.20", coin_selector),
      ("Portrait leaders", "BTG Pactual p.62", portrait_leaders), ("World score, hatched", "RBI p.38", world_score), ("Before/after dot maps", "RBI p.21", dot_maps)]),
    ("Reusable small formats", "Drill-downs, cards, long rules, logo brackets and plated KPIs",
     [("Wedge drill-down", "RD Saude p.39", wedge_drilldown), ("Mini tint card", "RD Saude p.2", mini_tint), ("Clipped map, long rules", "Alupar p.3", clipped_rules),
      ("Logos and bracket", "Rede D'Or p.17", logo_bracket), ("Active-state mini", "Rede D'Or p.8", active_mini), ("Gradient, dots and plates", "Cury p.24", dot_clusters)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the technique comes from the source.")
    ss.save(prs, OUT)
