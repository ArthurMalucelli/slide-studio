"""Elementos do catálogo, lote A: rastreadores, anotações e cartões, com conteúdo fictício. Copie a função e troque os textos.
Coordenadas de cada peça = pixels do recorte original (references/catalogo/crops/). Texto escala com a caixa, com piso legível.
Uso: python3 pecas_elementos_a.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402
from lxml import etree  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from shapely.geometry import Polygon, box as sbox  # noqa: E402

NEG = ss.NEG
L, C_, RT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM


# ---------- Helpers do lote ----------

def fs(m, px, lo=5.0):
    """Tamanho em pt para uma fonte medida em px do recorte, com piso."""
    return round(max(lo, px * m.sy * 72), 1)


def ln(s, m, pts, c=INK, wd=1.0, dash=None, head=False, closed=False):
    """Linha aberta ou fechada, numa forma só, sem preenchimento; head = ponta de seta no fim."""
    k = [(round(a * 1000), round(b * 1000)) for a, b in m.ps(pts)]
    fb = s.shapes.build_freeform(k[0][0], k[0][1], scale=914.4)
    fb.add_line_segments(k[1:], close=closed)
    sp = fb.convert_to_shape()
    sp.shadow.inherit = False
    sp.fill.background()
    sp.line.color.rgb = ss.rgb(c); sp.line.width = Pt(wd)
    if dash:
        sp.line.dash_style = dash
    if head:
        e = sp.line._get_or_add_ln()
        t = etree.SubElement(e, qn("a:tailEnd")); t.set("type", "triangle"); t.set("w", "med"); t.set("len", "med")
    return sp


DASH, SDASH, DOT = MSO_LINE_DASH_STYLE.DASH, MSO_LINE_DASH_STYLE.SQUARE_DOT, MSO_LINE_DASH_STYLE.ROUND_DOT


def smooth(pts, n=8):
    """Catmull-Rom: curva suave passando pelos pontos."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * p1[k] + (p2[k] - p0[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t ** 2 + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def bez(a, b, c, n=24):
    """Curva quadrática de a até c, puxada por b."""
    return [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * b[0] + t * t * c[0], (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * b[1] + t * t * c[1]) for t in (i / n for i in range(n + 1))]


def shadow(sp, blur=4, dist=2, ang=90, alpha=35, color="000000"):
    """Sombra real do PowerPoint, em pt."""
    pr = sp._element.spPr
    for e in pr.findall(qn("a:effectLst")): pr.remove(e)
    ef = etree.SubElement(pr, qn("a:effectLst"))
    o = etree.SubElement(ef, qn("a:outerShdw"))
    o.set("blurRad", str(int(blur * 12700))); o.set("dist", str(int(dist * 12700))); o.set("dir", str(int(ang * 60000))); o.set("algn", "ctr"); o.set("rotWithShape", "0")
    c = etree.SubElement(o, qn("a:srgbClr")); c.set("val", ss.hx(color))
    a = etree.SubElement(c, qn("a:alpha")); a.set("val", str(alpha * 1000))
    return sp


def rrm(s, m, x0, y0, x1, y1, fill=None, r=6, border=None, width=1.0, dash=None):
    """Retângulo arredondado com raio em px do recorte."""
    b = m.box(x0, y0, x1, y1)
    sp = rr(s, *b, fill, min(.5, r / max(.01, min(x1 - x0, y1 - y0))), border, width)
    if dash: sp.line.dash_style = dash
    return sp


def diag(s, m, x0, y0, x1, y1, fill, r=10):
    """Retângulo com dois cantos opostos arredondados (sup. esq. e inf. dir.)."""
    bx = m.box(x0, y0, x1, y1)
    sp = s.shapes.add_shape(MSO_SHAPE.ROUND_2_DIAG_RECTANGLE, Inches(bx[0]), Inches(bx[1]), Inches(bx[2]), Inches(bx[3]))
    sp.adjustments[0] = min(.5, r / min(x1 - x0, y1 - y0)); sp.adjustments[1] = 0
    sp.shadow.inherit = False
    ss.paint(sp.fill, fill); sp.line.fill.background()
    return sp


def mold(s, m, x0, y0, x1, y1, label="[logo]", px=11, alpha=None):
    """Molde cinza no lugar de logo, foto ou print reais."""
    sp = R(s, m, x0, y0, x1, y1, G2, alpha=alpha)
    t = tm(s, m, x0, y0, x1, y1, label, size=fs(m, px, 4.5), color=G4)
    t.text_frame.word_wrap = False
    return sp


def t1(s, m, x0, y0, x1, y1, t, **k):
    """Texto de uma linha, sem quebra."""
    sp = tm(s, m, x0, y0, x1, y1, t, **k)
    sp.text_frame.word_wrap = False
    return sp


def runs(s, m, x0, y0, x1, y1, parts, align=L, anchor=MID, wrap=True):
    """parts = lista de parágrafos; cada um é lista de (texto, dict de estilo)."""
    sp = ss.text(s, *m.box(x0, y0, x1, y1), parts, align=align, anchor=anchor, margin=0.0)
    sp.text_frame.word_wrap = wrap
    return sp


def lab(s, m, cx, cy, t, size=6, fill=D, hpx=None):
    """Rótulo de dado: fundo escuro, texto branco, bold. Largura vem do texto."""
    wi = .05 + len(t) * size * .0092
    hi = size * .0205
    a, b = m.p((cx, cy))
    sp = rr(s, a - wi / 2, b - hi / 2, wi, hi, fill, .25)
    t_ = tx(s, a - wi / 2, b - hi / 2, wi, hi, t, size=size, bold=True, color=W)
    t_.text_frame.word_wrap = False
    return sp


def vfade(s, m, cx, y0, y1, c, wpx=1.5, peak=.5):
    """Fio vertical que some nas pontas: retângulo fino com alfa."""
    sp = R(s, m, cx - wpx / 2, y0, cx + wpx / 2, y1, c)
    return grad(sp, ((0, c, 0), (peak, c, 1), (1, c, 0)), 90)


def hfade(s, m, x0, y0, x1, y1, c, a0=.8, a1=0):
    sp = R(s, m, x0, y0, x1, y1, c)
    return grad(sp, ((0, c, a0), (1, c, a1)), 0)


def radial(sp, stops):
    """Degradê radial do centro para fora, com alfa."""
    grad(sp, stops, 0)
    gf = sp._element.spPr.find(qn("a:gradFill"))
    for e in gf.findall(qn("a:lin")): gf.remove(e)
    pa = etree.SubElement(gf, qn("a:path")); pa.set("path", "circle")
    f = etree.SubElement(pa, qn("a:fillToRect"))
    for k in "ltrb": f.set(k, "50000")
    return sp


def wedge_arrow(s, m, cx, y0, y1, half, head, c):
    """Seta grossa para baixo, como forma única."""
    return poly(s, m, ((cx - half, y0), (cx + half, y0), (cx + half, y1 - head), (cx + head, y1 - head), (cx, y1), (cx - head, y1 - head), (cx - half, y1 - head)), c)


def cross(s, m, cx, cy, r, c, wd=1.5):
    ln(s, m, ((cx - r, cy - r), (cx + r, cy + r)), c, wd)
    ln(s, m, ((cx + r, cy - r), (cx - r, cy + r)), c, wd)


def circ(s, m, cx, cy, rpx, fill=None, border=None, width=1.0, dash=None):
    """Círculo com raio em px do recorte."""
    a, b = m.p((cx, cy))
    sp = oval(s, a, b, 2 * rpx * m.sx, fill, border=border, width=width)
    if dash: sp.line.dash_style = dash
    return sp


def diamond(s, m, cx, cy, rpx, c):
    a, b = m.p((cx, cy)); d = rpx * 2 * m.sx
    sp = s.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(a - d / 2), Inches(b - d / 2), Inches(d), Inches(d))
    sp.shadow.inherit = False
    ss.paint(sp.fill, c); sp.line.fill.background()
    return sp


def clipped_map(s, m, frame, shapes, bounds, fill, edge=None, edge_w=.25):
    """Mapa recortado por um quadro em coordenadas do recorte; bounds = (lon0, lon1, lat0, lat1)."""
    x0, y0, x1, y1 = frame
    lo0, lo1, la0, la1 = bounds
    k = math.cos(math.radians((la0 + la1) / 2))
    sc = max((x1 - x0) / ((lo1 - lo0) * k), (y1 - y0) / (la1 - la0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lom, lam = (lo0 + lo1) / 2, (la0 + la1) / 2
    pxy = lambda lo, la: (cx + (lo - lom) * k * sc, cy - (la - lam) * sc)
    clip = sbox(x0, y0, x1, y1)
    for key, v in shapes.items():
        c = fill(key) if callable(fill) else fill
        if not c: continue
        for r in v["rings"]:
            if len(r) < 4: continue
            g = Polygon([pxy(a, b) for a, b in r]).buffer(0).intersection(clip)
            if g.is_empty: continue
            for part in (g.geoms if hasattr(g, "geoms") else [g]):
                if part.geom_type == "Polygon" and part.area > 2:
                    poly(s, m, list(part.simplify(.35).exterior.coords)[:-1], c, edge=edge, ew=edge_w)
    return pxy


# ---------- Rastreadores e navegação ----------

def storyline_rail(s, x, y, w, h, phrase="A Relevant Message", page="6", appendix=False):
    """Trilho lateral cheio, com o número no topo e a frase do argumento girada, alinhada embaixo. AB InBev p.6."""
    m = M((0, 0, 1333, 750), (x, y, w, h))
    R(s, m, 0, 0, 1333, 750, W, G2, width=.5)
    # corpo fantasma do slide, só para dar a proporção do trilho
    R(s, m, 130, 60, 1000, 90, G2)
    R(s, m, 130, 150, 700, 690, G1)
    mini_bars(s, m, 180, 300, 650, 640, 7, G3)
    R(s, m, 760, 150, 1270, 400, G1)
    R(s, m, 760, 430, 1270, 690, G1)
    R(s, m, 0, 0, 84, 750, G4 if appendix else F)
    t1(s, m, 12, 16, 72, 46, page, size=fs(m, 17), color=W)
    a, b = m.p((42, 690))
    ln_ = 620 * m.sy; th = 60 * m.sy
    tb = tx(s, a - ln_ / 2, b - ln_ / 2 - th / 2 + th / 2, ln_, th, phrase, size=fs(m, 36), color=W, align=L, rot=-90)
    tb.text_frame.word_wrap = False


def criteria_track(s, x, y, w, h, active=0):
    """Frase entra por chevrons numa faixa com trilho de três critérios; logos ativos e apagados são a legenda. AB InBev p.40."""
    m = M((0, 0, 900, 171), (x, y, w, h))
    runs(s, m, 0, 0, 186, 46, [[("We chose ", {"size": fs(m, 13), "color": INK}), ("three criteria", {"size": fs(m, 13), "bold": True, "color": F}), (" to judge how each app performs", {"size": fs(m, 13), "color": INK})]], align=C_)
    R(s, m, 233, 2, 900, 43, G1)
    for dx, c in ((0, G2), (20, G2)):
        poly(s, m, ((200 + dx, 22), (222 + dx, 2), (236 + dx, 2), (214 + dx, 22), (236 + dx, 43), (222 + dx, 43)), c)
    ln(s, m, ((270, 33), (900, 33)), INK, .75)
    for cx, t in ((396, "Scalability"), (596, "Customer Captivity"), (790, "Service")):
        t1(s, m, cx - 90, 8, cx + 90, 27, t, size=fs(m, 14))
        rrm(s, m, cx - 14, 28, cx + 14, 38, W, 3, INK, .75)
    t1(s, m, 0, 77, 200, 95, "Monthly Active Users (Mn)", size=fs(m, 11), bold=True, italic=True, align=L)
    ln(s, m, ((0, 97), (318, 97)), INK, .75)
    for i, bx in enumerate((3, 112, 208)):
        mold(s, m, bx, 103, bx + 74, 127, "[logo]", alpha=None if i == active else 35)
    poly(s, m, ((3, 146), (112, 146), (124, 158), (112, 170), (3, 170)), F)
    t1(s, m, 5, 146, 112, 170, "CAGR: 40%", size=fs(m, 10), color=W, bold=True)
    ln(s, m, smooth(((620, 171), (700, 171), (752, 160), (790, 118), (825, 113), (850, 108), (866, 118))), F, 1.5)
    lab(s, m, 878, 118, "4.62", fs(m, 11), D)


def three_level_tracker(s, x, y, w, h, thesis=2, chapter=0, idea=1):
    """Três níveis: abas de capítulo em cima, régua de ideias sob o título e teses no rodapé. BTG Pactual p.56."""
    m = M((0, 0, 900, 179), (x, y, w, h))
    grad(R(s, m, 0, 0, 342, 50, G4), ((0, G4), (1, dark(G4, .25))), 0)
    mold(s, m, 16, 8, 112, 42, "[logo]")
    ch = ("Key to the Past Success", "Inside the Partnership", "Perpetuating the Culture", "No Digital DNA")
    xs = (342, 481, 620, 760, 900)
    R(s, m, 481, 0, 900, 50, T)
    for i, t in enumerate(ch):
        on = i == chapter
        if on:
            poly(s, m, ((334, 50), (342, 50), (342, 58)), INK)
            R(s, m, xs[i], 0, xs[i + 1], 58, D)
        tm(s, m, xs[i] + 6, 2, xs[i + 1] - 6, 52 if on else 48, t, size=fs(m, 15, 5), color=W if on else D, bold=on)
    R(s, m, 25, 66, 28, 94, D)
    runs(s, m, 32, 62, 880, 98, [[("The model promotes ", {"size": fs(m, 24), "color": D}), ("integration between areas", {"size": fs(m, 24), "color": D, "bold": True})]])
    R(s, m, 0, 117, 900, 147, G1)
    ln(s, m, ((0, 147), (690, 147)), G4, .75)
    ln(s, m, ((706, 147), (900, 147)), G3, .5)
    for i, (cx, t) in enumerate(((143, "Never comfortable"), (368, "Integrated Units"), (594, "Lean structure"))):
        on = i == idea
        t1(s, m, cx - 100, 118, cx + 100, 137, t, size=fs(m, 11), bold=on, color=INK if on else G4)
        R(s, m, cx - 13, 143, cx + 13, 151, D if on else W, INK, width=.75)
    cross(s, m, 698, 147, 5, G4, .75)
    ln(s, m, ((25, 157), (875, 157)), G4, .5)
    names = ("FINANCIAL DEEPENING", "DIGITAL", "PARTNERSHIP", "ESG", "VALUATION")
    for i, (cx, t) in enumerate(zip((135, 313, 473, 627, 782), names)):
        t1(s, m, cx - 90, 161, cx + 90, 179, t, size=fs(m, 12), color=D if i == thesis else G4)
    R(s, m, 420, 157, 527, 160, D)
    t1(s, m, 845, 158, 870, 172, "56", size=fs(m, 8, 4.5), color=G4)


def section_tabs(s, x, y, w, h, active=2):
    """Três barras escuras; a aba ativa ganha moldura tracejada dupla um pouco maior. CSN - ArcelorMittal p.26."""
    m = M((0, 0, 900, 59), (x, y, w, h))
    for i, (x0, x1, t) in enumerate(((3, 295, "Europe Unit [Region A]"), (303, 595, "Home Unit [Region B]"), (603, 893, "Logistics [Asset C]"))):
        sp = R(s, m, x0, 8, x1, 50, D)
        grad(sp, ((0, dark(D, .6)), (.5, D), (1, light(D, .2))), 15)
        t1(s, m, x0, 8, x1, 50, t, size=fs(m, 12), color=W, bold=True)
        if i == active:
            R(s, m, x0 - 5, 3, x1 + 6, 55, None, A, width=1, dash=True)
            R(s, m, x0 - 2.5, 5.5, x1 + 3.5, 52.5, None, A, width=.5, dash=True)


def _icon_store(s, m, cx, cy, c):
    k = lambda P: [(cx + a, cy + b) for a, b in P]
    ln(s, m, k(((-27, -8), (-23, -28), (23, -28), (27, -8))), c, 1)
    for i in range(5):
        xa, xb = -27 + i * 10.8, -23 + i * 9.2
        ln(s, m, k(((xb, -28), (xa, -8))), c, .75)
        ln(s, m, smooth(k(((xa, -8), (xa + 5.4, -2), (xa + 10.8, -8))), 4), c, .75)
    ln(s, m, k(((-27, -8), (27, -8))), c, .75)
    ln(s, m, k(((-23, -2), (-23, 27), (23, 27), (23, -2))), c, 1)
    ln(s, m, k(((-27, 27), (27, 27))), c, 1)
    ln(s, m, k(((-17, 4), (-3, 4), (-3, 17), (-17, 17))), c, .75, closed=True)
    ln(s, m, k(((5, 27), (5, 4), (17, 4), (17, 27))), c, .75)


def _icon_camera(s, m, cx, cy, c):
    k = lambda P: [(cx + a, cy + b) for a, b in P]
    ln(s, m, k(((-23, -29), (-23, 29))), c, 1)
    ln(s, m, k(((-23, 2), (-14, 2), (-10, -8))), c, .75)
    ln(s, m, k(((-17, -24), (24, -8), (15, 12), (-14, -3))), c, 1, closed=True)
    ln(s, m, k(((15, 4), (31, 8), (26, 16), (12, 12))), c, .75, closed=True)
    circ(s, m, cx - 2, cy - 12, 2.5, None, c, .75)


def _icon_chart(s, m, cx, cy, c):
    k = lambda P: [(cx + a, cy + b) for a, b in P]
    ln(s, m, k(((-27, -31), (-27, 27), (31, 27))), c, 1)
    ln(s, m, k(((-20, 15), (-8, 2), (-1, 9), (9, -3), (14, 3), (28, -14))), c, 1)
    ln(s, m, k(((17, -14), (28, -15), (28, -4))), c, 1)


def thesis_orbit(s, x, y, w, h, buy=True, active=None):
    """Dois anéis saem pela esquerda, teses em círculos com ícone sobre o anel externo e BUY entre cantos em L. Intelbras p.4."""
    m = M((0, 0, 900, 614), (x, y, w, h))
    bg = light(T, .45)
    R(s, m, 0, 0, 900, 614, bg)
    cx0, cy0 = 62, 307
    for r_ in (146, 285):
        a = math.degrees(math.acos(-cx0 / r_))
        ln(s, m, [(cx0 + r_ * math.cos(math.radians(t)), cy0 + r_ * math.sin(math.radians(t))) for t in [-a + i * 2 * a / 80 for i in range(81)]], F, 1)
    mold(s, m, 8, 285, 176, 330, "[logo]", 16)
    items = ((256, 80, 330, "Channel-led distribution", "fueling market leadership", _icon_store), (355, 307, 418, "Monetizing the network", "through portfolio mix", _icon_camera), (256, 520, 330, "Unlocking a structural", "avenue of growth", _icon_chart))
    for i, (cx, cy, tx0, a, b, ic) in enumerate(items):
        c = F if active is None or i == active else light(F, .65)
        circ(s, m, cx, cy, 50, bg, c, 1)
        ic(s, m, cx, cy, c)
        ss.text(s, *m.box(tx0, cy - 34, 900, cy + 34), [[(a, {"bold": True, "color": c, "size": fs(m, 22)})], [(b, {"bold": True, "color": c, "size": fs(m, 22)})]], anchor=MID, margin=0.0)
    if buy:
        poly(s, m, ((646, 132), (696, 132), (691, 138), (652, 138), (652, 168), (646, 168)), F)
        poly(s, m, ((891, 205), (891, 240), (843, 240), (848, 234), (885, 234), (885, 205)), F)
        t1(s, m, 650, 140, 890, 228, "BUY!", size=fs(m, 84), bold=True, color=INK)


def site_chrome_toc(s, x, y, w, h):
    """Agenda vestida como o site da empresa: barra, busca, carrinho, colunas de links e rodapé. Meliuz p.64."""
    m = M((0, 0, 900, 506), (x, y, w, h))
    R(s, m, 0, 0, 900, 506, W, G2, width=.5)
    R(s, m, 0, 0, 900, 34, F)
    for x0, t in ((12, "Shop"), (108, "About"), (218, "Partners")):
        t1(s, m, x0, 6, x0 + 90, 28, t, size=fs(m, 13), color=W, align=L)
    R(s, m, 605, 7, 782, 27, W)
    circ(s, m, 616, 15, 4.5, None, INK, 1); ln(s, m, ((619.5, 18.5), (624, 23)), INK, 1)
    t1(s, m, 630, 7, 780, 27, "Search...", size=fs(m, 12), align=L)
    t1(s, m, 790, 6, 898, 28, "company.com", size=fs(m, 12, 4.5), color=W, align=RT)
    t1(s, m, 22, 40, 300, 62, "Presentation agenda", size=fs(m, 15, 6), bold=True, align=L)
    # carrinho com selo
    ln(s, m, ((857, 46), (864, 46), (870, 66), (886, 66), (888, 52), (866, 52)), INK, .75)
    for cx in (872, 884): circ(s, m, cx, 71, 2, INK)
    circ(s, m, 878, 45, 7, NEG); t1(s, m, 871, 38, 885, 52, "1", size=fs(m, 8, 4), color=W, bold=True)
    cols = ((64, (("1. Overview", ("1.1 Cover", "1.2 Our call", "1.3 Pioneer of the model", "1.4 Core products", "1.5 Thesis pillars")), ("2. Human Capital", ("2.1 Pillar I", "2.2 A closer look at the team", "2.3 A fieldwork survey", "2.4 Culture in numbers")), ("3. Sector", ("3.1 Pillar II", "3.2 Why the sector grows", "3.3 Limits to growth")))),
            (342, (("", ("3.4 The partner view (I of II)", "3.5 The partner view (II of II)", "3.6 The race for fintech", "3.7 Our credit card", "3.8 M&A and partnerships")), ("4. Ecosystem", ("4.1 Pillar III", "4.2 Benefits of an ecosystem", "4.3 Retention case", "4.4 The top of mind", "4.5 Peer comparison", "4.6 The new app")))),
            (626, (("5. Valuation", ("5.1 Valuation pillar", "5.2 How many users, really?", "5.3 Seeing the revenue", "5.4 Multiples")), ("6. Risks", ("6.1 Risks to watch", "6.2 Investment thesis")))))
    for x0, secs in cols:
        yy = 66 if x0 == 64 else 66 if x0 == 342 else 76
        for head, items in secs:
            if head:
                t1(s, m, x0, yy, x0 + 250, yy + 24, head, size=fs(m, 17, 7), color=G4, align=L); yy += 27
                x_ = x0 + (16 if x0 == 64 else 12)
            else:
                x_ = x0 + 12
            for it in items:
                sp = t1(s, m, x_, yy, x_ + 250, yy + 18, it, size=fs(m, 9, 4.6), color=G4, align=L)
                sp.text_frame.paragraphs[0].runs[0].font.underline = True
                yy += 18
            yy += 6
    ln(s, m, ((22, 443), (872, 443)), G3, .5)
    for x0, items in ((28, ("News", "Black Friday", "Promotions")), (130, ("Clothing", "Appliances", "Services")), (253, ("Electronics", "Food", "Backpacks")), (366, ("FAQ", "Contact us", "About us"))):
        for k, t in enumerate(items):
            t1(s, m, x0, 449 + k * 17, x0 + 110, 466 + k * 17, t, size=fs(m, 9, 4.6), color=G4, align=L)
    for cx, kind in ((795, "f"), (816, "o"), (836, "t"), (857, "p")):
        circ(s, m, cx, 475, 8, None, G4, .75)
        if kind == "o": circ(s, m, cx, 475, 3, None, G4, .5)
        elif kind == "p": poly(s, m, ((cx - 2.5, 471), (cx + 3.5, 475), (cx - 2.5, 479)), G4)
        elif kind == "f": ln(s, m, ((cx + 2, 470), (cx, 470), (cx, 481)), G4, .75); ln(s, m, ((cx - 2, 474), (cx + 2, 474)), G4, .75)
        else: ln(s, m, smooth(((cx - 4, 478), (cx, 477), (cx + 4, 472)), 3), G4, .75)


def verdict_ticket(s, x, y, w, h, active=None):
    """Placa com ticker e BUY, cartão com teses presas num fio com pontos, e rodapé de Upside e TIR. Mercado Libre p.5."""
    m = M((0, 0, 900, 487), (x, y, w, h))
    R(s, m, 0, 0, 900, 487, G2)
    rrm(s, m, 5, 5, 895, 98, G1, 5)
    t1(s, m, 36, 22, 500, 60, "TICK - EXCHANGE", size=fs(m, 26), align=L, color=INK)
    t1(s, m, 36, 60, 500, 86, "Company name", size=fs(m, 17), align=L, color=INK)
    t1(s, m, 650, 25, 864, 78, "BUY", size=fs(m, 36), align=RT, bold=True, color=F)
    shadow(rrm(s, m, 5, 126, 895, 483, W, 6), 3, 2, 90, 40)
    faded = lambda i: active is not None and i != active
    ln(s, m, ((123, 177), (123, 356)), F, 1.75)
    for i, (yy, t) in enumerate(((177, "First Thesis Pillar"), (267, "Scaling the Business"), (356, "Margin for Growth"))):
        circ(s, m, 123, yy, 7, G2 if faded(i) else F)
        t1(s, m, 200, yy - 22, 880, yy + 22, t, size=fs(m, 26), align=L, bold=True, color=G3 if faded(i) else INK)
    ln(s, m, ((5, 414), (895, 414)), G3, .5)
    t1(s, m, 36, 428, 400, 468, "Upside: 29.9%", size=fs(m, 22), bold=True, color=D, align=L)
    t1(s, m, 560, 424, 876, 456, "IRR: 23.2%", size=fs(m, 22), bold=True, color=D, align=RT)
    t1(s, m, 560, 455, 850, 474, "Exit: 2028", size=fs(m, 11, 4.5), italic=True, color=G4, align=RT)


def revenue_tree(s, x, y, w, h, path=("AUV", "Price")):
    """Árvore pequena de receita que volta a cada slide com um ramo aceso, como localizador. Restaurant Brands p.30."""
    m = M((0, 0, 520, 280), (x, y, w, h))
    pale = light(F, .72)
    def arrow(pts):
        ln(s, m, pts, pale, 1.5, head=True)
    ln(s, m, ((298, 49), (298, 65)), pale, 1.5)
    arrow(((298, 65), (141, 65), (141, 96)))
    arrow(((298, 65), (455, 65), (455, 96)))
    ln(s, m, ((141, 150), (141, 173)), pale, 1.5)
    arrow(((141, 173), (58, 173), (58, 204)))
    arrow(((141, 173), (224, 173), (224, 204)))
    arrow(((455, 150), (455, 204)))
    cross(s, m, 298, 137, 11, pale, 1.5)
    cross(s, m, 142, 245, 11, pale, 1.5)
    def node(x0, y0, x1, y1, t, px):
        on = t == "Revenue" or t in path
        diag(s, m, x0, y0, x1, y1, F if on else G3, 9)
        t1(s, m, x0, y0, x1, y1, t, size=fs(m, px, 6), color=W, bold=True, italic=True)
    node(156, 8, 441, 49, "Revenue", 26)
    node(90, 110, 195, 150, "AUV", 26)
    node(402, 110, 508, 150, "Units", 26)
    node(15, 220, 105, 271, "Price", 18)
    node(180, 220, 270, 271, "Traffic", 18)
    node(410, 220, 500, 271, "NRG", 18)


def bubble_locator(s, x, y, w, h, active=(0, 1, 2)):
    """Colunas claras com disco numerado, círculo no tamanho do valor e selo de participação; linhas ligam os círculos. Restaurant Brands p.28."""
    m = M((0, 80, 560, 556), (x, y, w, h))
    cols = (("Home", "23.6", "31.7%", 92, 21, F, 13, 10, 183), ("Region", "418.4", "6.3%", 278, 51, light(F, .12), 20, 193, 362), ("World", "996.2", "4.7%", 461, 77, light(F, .3), 24, 373, 545))
    for i, c in enumerate(cols):
        diag(s, m, c[7], 86, c[8], 550, G1, 22)
    ln(s, m, ((92, 290), (461, 238)), G3, 1); ln(s, m, ((92, 332), (461, 384)), G3, 1)
    for i, (name, v, sh, cx, r_, col, px, x0, x1) in enumerate(cols):
        on = i in active
        mid = (x0 + x1) / 2
        k = (lambda c_: c_) if on else (lambda c_: ss.mix(c_, G1, .75))
        circ(s, m, mid - 1, 122, 23, k(light(F, .55)))
        circ(s, m, mid - 1, 122, 18, k(F))
        t1(s, m, mid - 20, 104, mid + 18, 140, str(i + 1), size=fs(m, 22), bold=True, color=W)
        t1(s, m, x0, 154, x1, 186, name, size=fs(m, 21), bold=True, color=k(INK))
        circ(s, m, cx, 311, r_, k(col))
        t1(s, m, cx - r_, 296, cx + r_, 326, v, size=fs(m, px, 5), bold=True, color=W)
        diag(s, m, mid - 69, 444, mid + 69, 506, k(F), 9)
        ss.text(s, *m.box(mid - 69, 444, mid + 69, 506), [[("Share", {"bold": True, "color": W, "size": fs(m, 18)})], [(sh, {"color": W, "size": fs(m, 18)})]], align=C_, anchor=MID, margin=0.0)


def guest_recolor(s, x, y, w, h, guest=D):
    """O molde não muda: trilho, traço do título, palavra ativa e destaques assumem a cor do convidado, e o logo troca. Sabesp p.17."""
    m = M((0, 0, 900, 506), (x, y, w, h))
    tint = lambda t_: ss.mix(guest, "FFFFFF", t_)
    R(s, m, 0, 0, 900, 506, W, G2, width=.5)
    R(s, m, 0, 0, 27, 506, guest)
    poly(s, m, smooth(((0, 462), (27, 468), (42, 486), (60, 506))) + [(0, 506)], guest)
    for k in range(5):
        ln(s, m, smooth(((0, 50 + k * 16), (14, 40 + k * 16), (27, 26 + k * 16)), 4), tint(.55), .25)
    t1(s, m, 2, 480, 26, 498, "17", size=fs(m, 9, 4.5), color=W, bold=True)
    grad(R(s, m, 56, 20, 60, 45, guest), ((0, guest), (1, tint(.6))), 90)
    t1(s, m, 68, 16, 790, 47, "With the guest bringing the playbook", size=fs(m, 25, 6.5), bold=True, align=L)
    t1(s, m, 68, 49, 790, 68, "A proven platform, built on disciplined deals and cost control", size=fs(m, 13, 4.8), align=L)
    mold(s, m, 806, 12, 890, 40, "[logo]")
    runs(s, m, 68, 82, 800, 103, [[("The guest has spent years ", {"size": fs(m, 14, 5)}), ("acquiring", {"size": fs(m, 14, 5), "bold": True, "color": guest}), (" and ", {"size": fs(m, 14, 5)}), ("turning around", {"size": fs(m, 14, 5), "bold": True, "color": guest}), (" assets", {"size": fs(m, 14, 5)})]], wrap=False)
    t1(s, m, 68, 105, 700, 122, "Seven assets bought, each one a turnaround story", size=fs(m, 10, 4.5), italic=True, color=G4, align=L)
    # citações e fita
    R(s, m, 100, 148, 234, 222, G1)
    mold(s, m, 44, 138, 104, 222, "[foto]", 10)
    tm(s, m, 108, 152, 230, 218, "“We bring deep experience and raise the bar”", size=fs(m, 9, 4.5), italic=True)
    R(s, m, 725, 148, 840, 222, G1)
    mold(s, m, 834, 130, 892, 212, "[foto]", 10)
    tm(s, m, 729, 152, 830, 218, "“They have done it before”", size=fs(m, 9, 4.5), italic=True)
    ln(s, m, ((234, 185), (725, 185)), G3, 1.5)
    yrs = ("2004", "2012", "2018", "2021", "2022", "2024")
    for i, t in enumerate(yrs):
        xx = 255 + i * 72
        col = A if i == 5 else tint(.05 + i * .13) if i != 4 else G2
        poly(s, m, ((xx, 205), (xx + 16, 165), (xx + 66, 165), (xx + 50, 205)), col)
        t1(s, m, xx + 8, 165, xx + 58, 205, t, size=fs(m, 13, 5), bold=True, color=INK if i == 4 else W)
    for i, (t, up) in enumerate((("Asset A", 1), ("Asset B", 0), ("Asset C", 1), ("Asset D", 0), ("Asset E", 1), ("Focus", 0))):
        xx = 263 + i * 72
        t1(s, m, xx, 143 if up else 208, xx + 72, 161 if up else 226, t, size=fs(m, 10, 4.5), align=L, color=guest if i == 5 else INK, bold=i == 5)
    # gráfico de área
    runs(s, m, 68, 244, 470, 263, [[("...driving costs ", {"size": fs(m, 13, 5)}), ("below the ceiling", {"size": fs(m, 13, 5), "bold": True, "color": guest})]], wrap=False)
    t1(s, m, 68, 263, 470, 280, "Regulated vs real costs, bn", size=fs(m, 10, 4.5), italic=True, color=G4, align=L)
    base, xs = 436, [82 + i * 45.4 for i in range(9)]
    reg = (1.9, 2.1, 2.4, 2.8, 3.2, 3.9, 6.2, 7.8, 9.1); real = (1.5, 1.6, 1.9, 2.1, 2.4, 3.3, 4.7, 6.1, 7.2)
    yv = lambda v: base - v * 15
    poly(s, m, [(xs[0], base)] + [(a, yv(b)) for a, b in zip(xs, reg)] + [(xs[-1], base)], tint(.55))
    poly(s, m, [(xs[0], base)] + [(a, yv(b)) for a, b in zip(xs, real)] + [(xs[-1], base)], guest)
    ln(s, m, ((75, base), (450, base)), G3, .5)
    for i in (0, 2, 4, 6, 8):
        t1(s, m, xs[i] - 26, base + 2, xs[i] + 26, base + 18, str(2016 + i), size=fs(m, 9, 4.5))
    lab(s, m, xs[8] - 4, yv(9.1) - 9, "9.1", 4.5, dark(guest, .2))
    lab(s, m, xs[6], yv(6.2) - 9, "6.2", 4.5, dark(guest, .2))
    R(s, m, 88, 318, 192, 344, G1); tm(s, m, 88, 318, 192, 344, "Gap captured", size=fs(m, 9, 4.5), bold=True)
    ln(s, m, ((192, 331), (228, 331)), guest, .75, dash=DASH)
    rrm(s, m, 228, 318, 312, 344, guest, 5); t1(s, m, 228, 318, 312, 344, "Gap 23%", size=fs(m, 9, 4.5), color=W, bold=True)
    # mapa de calor
    runs(s, m, 490, 244, 890, 263, [[("...and ", {"size": fs(m, 13, 5)}), ("replicating efficiency", {"size": fs(m, 13, 5), "bold": True, "color": guest}), (" in every asset", {"size": fs(m, 13, 5)})]], wrap=False)
    t1(s, m, 490, 263, 890, 280, "Losses fall after each deal, %", size=fs(m, 10, 4.5), italic=True, color=G4, align=L)
    for r_, n in enumerate((10, 8, 5, 5, 4, 3)):
        yy = 305 + r_ * 22
        t1(s, m, 470, yy, 512, yy + 21, f"Asset {'ABCDEF'[r_]}", size=fs(m, 8, 4), align=RT)
        for c_ in range(n):
            R(s, m, 516 + c_ * 32, yy, 547 + c_ * 32, yy + 21, tint(min(.85, .05 + c_ * .09 + r_ * .03)))
    rrm(s, m, 690, 356, 816, 416, W, 2, guest, 1)
    ss.text(s, *m.box(692, 358, 814, 414), [[("Average:", {"bold": True, "size": fs(m, 11, 5)})], [("-2.9% a year", {"bold": True, "size": fs(m, 11, 5)})]], align=C_, anchor=MID, margin=0.0)
    grad(R(s, m, 843, 332, 849, 426, guest), ((0, guest), (1, tint(.85))), 90)
    ln(s, m, ((60, 481), (876, 481)), guest, .5)
    words = (("Overview | Edge | ", False), ("Efficiency", True), (" | Capital | Risks", False))
    runs(s, m, 60, 485, 520, 503, [[(a, {"size": fs(m, 11, 5), "bold": b, "color": guest if b else INK}) for a, b in words]], wrap=False)
    t1(s, m, 530, 485, 760, 503, "Sources: company, regulator", size=fs(m, 8, 4), italic=True, color=G4, align=L)


def term_ledger(s, x, y, w, h):
    """Passo a passo em roda e, abaixo, razão de termos em pares com fio que some. Vibra p.31."""
    m = M((0, 0, 292, 495), (x, y, w, h))
    bg = dark(D, .55)
    R(s, m, 0, 0, 292, 495, bg)
    for x0, x1, a_ in ((180, 240, 16), (230, 262, 10)):
        poly(s, m, ((x0, 495), (x1, 300), (x1 + 6, 495)), F, alpha=a_)
    grad(R(s, m, 0, 0, 292, 65, F), ((0, F, .05), (.75, A, .4), (1, A, .05)), 90)
    ln(s, m, ((0, 65), (292, 65)), A, .75)
    t1(s, m, 30, 14, 56, 52, "1.", size=fs(m, 19, 7), bold=True, color=A, align=L)
    t1(s, m, 66, 14, 290, 52, "Entry of the Fund", size=fs(m, 14, 6.5), bold=True, color=A, align=L)
    for i, (yy, n, t, px, a_) in enumerate(((105, "2.", "New Holder Block", 11, .55), (150, "3.", "First Step: Sale", 8, .42), (176, "4.", "Second Step", 6, .22))):
        c = ss.mix(W, bg, 1 - a_)
        t1(s, m, 30, yy - 12, 56, yy + 12, n, size=fs(m, px + 3, 4), color=c, align=L)
        t1(s, m, 66, yy - 12, 290, yy + 12, t, size=fs(m, px, 4), color=c, align=L)
    grad(R(s, m, 0, 150, 292, 192, bg), ((0, bg, 0), (1, bg, 1)), 90)
    blocks = ((236, "Block Trade", ("BRL ", "35.4", ""), "Price per Share", ("", "5", "%"), "Premium"),
              (335, "Cash Out", ("BRL ", "37.1", ""), "Price per Share", ("", "10", "%"), "Premium"),
              (435, "Entry Details", ("BRL ", "5,798", " mn"), "Amount Paid", ("", "13.3", "%"), "Stake"))
    for yy, title, v1, l1, v2, l2 in blocks:
        t1(s, m, 0, yy - 10, 292, yy + 10, title, size=fs(m, 12, 5.5), bold=True, color=W)
        for x0, x1, v, l_ in ((10, 145, v1, l1), (147, 292, v2, l2)):
            runs(s, m, x0, yy + 14, x1, yy + 38, [[(v[0], {"size": fs(m, 10, 5), "bold": True, "color": A}), (v[1], {"size": fs(m, 18, 8), "bold": True, "color": A}), (v[2], {"size": fs(m, 10, 5), "bold": True, "color": A})]], align=C_, wrap=False)
            t1(s, m, x0, yy + 37, x1, yy + 54, l_, size=fs(m, 11, 5), color=W)
        vfade(s, m, 146, yy + 12, yy + 56, A, 1.5)


def bar_segments_captions(s, x, y, w, h):
    """A última coluna empilhada encosta em linhas claras da mesma altura; de uma linha sai o fio até o painel. BTG Pactual p.18."""
    m = M((0, 0, 900, 283), (x, y, w, h))
    top, mid_, low = T, D, dark(G4, .35)
    for i, (t, c) in enumerate((("Private", top), ("High Income", mid_), ("Traditional", low))):
        yy = 31 + i * 16
        R(s, m, 16, yy - 3, 22, yy + 3, c)
        t1(s, m, 25, yy - 8, 150, yy + 8, t, size=fs(m, 9, 4.6), bold=True, color=G4, align=L)
    for x0, (a, b, c), (la, lb, lc) in ((24, (222, 186, 138), ("775", "502", "645")), (97, (212, 155, 91), ("916", "778", "868")), (170, (194, 116, 6), ("1,164", "1,054", "1,483"))):
        R(s, m, x0, a, x0 + 49, 280, low); R(s, m, x0, b, x0 + 49, a - 1, mid_); R(s, m, x0, c, x0 + 49, b - 1, top)
        big = x0 == 170
        t1(s, m, x0, a, x0 + 49, 280, la, size=fs(m, 10, 5), bold=True, color=W)
        t1(s, m, x0, b, x0 + 49, a, lb, size=fs(m, 10, 5), bold=True, color=W)
        if big:
            R(s, m, x0, 40, x0 + 49, 82, F); t1(s, m, x0, 40, x0 + 49, 82, lc, size=fs(m, 10, 5), bold=True, color=W)
        else:
            lab(s, m, x0 + 24.5, (b + c) / 2, lc, fs(m, 10, 5), D)
    ln(s, m, ((0, 281), (232, 281)), INK, .5)
    rows = ((6, 114, light(T, .55), "Private Banking", "High barriers", (("Well served", True),)),
            (116, 192, ss.mix(D, "FFFFFF", .72), "High Income Retail", "Medium barriers", (("Badly served", True),)),
            (194, 280, G2, "Traditional Retail", None, (("Badly served, ", True), ("less demanding", False))))
    for y0, y1, c, a, b, tail in rows:
        R(s, m, 219, y0, 427, y1, c)
        pp = [[(a, {"bold": True, "size": fs(m, 11, 5.5), "color": INK})]]
        if b: pp.append([(b, {"size": fs(m, 13, 5.5), "color": D})])
        pp.append([(t_, {"bold": k, "size": fs(m, 10, 5), "color": F if k else INK}) for t_, k in tail])
        runs(s, m, 229, y0 + 3, 425, y1 - 3, pp)
    ln(s, m, ((427, 122), (473, 122)), G4, .75)
    ln(s, m, ((473, 122), (473, 0), (900, 0)), G4, .75)
    diamond(s, m, 473, 122, 5, INK)
    t1(s, m, 500, 2, 640, 20, "Private Banking", size=fs(m, 12, 5.5), bold=True, color=F)
    R(s, m, 708, 2, 876, 21, D); t1(s, m, 708, 2, 876, 21, "+ High Income", size=fs(m, 11, 5.5), bold=True, color=W)
    for cx, a, b, it in ((570, "TAM, 2020", "$ 1.5 tn", False), (792, "TAM, 2020", "$ 2.5 tn", True)):
        t1(s, m, cx - 70, 23, cx + 70, 40, a, size=fs(m, 10, 5), bold=True, color=G4)
        t1(s, m, cx - 70, 40, cx + 70, 64, b, size=fs(m, 19, 8), italic=True, bold=it, color=INK if it else G4)
    mold(s, m, 483, 72, 563, 106, "[logo]")
    ln(s, m, bez((572, 76), (680, 156), (812, 74)), D, 2.25, head=True)
    t1(s, m, 632, 58, 712, 84, "74%", size=fs(m, 20, 9), bold=True, italic=True, color=F)
    t1(s, m, 602, 84, 742, 102, "TAM increase", size=fs(m, 11, 5), bold=True, color=G4)


def football_banner(s, x, y, w, h):
    """Faixa com preço e múltiplo sobre o football field; tracejada desce por todas as barras até o eixo. CSN LM p.21."""
    m = M((0, 0, 615, 410), (x, y, w, h))
    t1(s, m, 0, 2, 190, 26, "Valuation Approach", size=fs(m, 15, 7), align=C_)
    t1(s, m, 195, 2, 615, 26, "Enterprise Value", size=fs(m, 15, 7), align=C_)
    ln(s, m, ((0, 29), (615, 29)), INK, 1.25); ln(s, m, ((0, 405), (615, 405)), INK, 1.25); ln(s, m, ((192, 29), (192, 405)), INK, 1.25)
    R(s, m, 207, 38, 610, 75, T, A, width=1)
    t1(s, m, 215, 38, 470, 75, "Purchase Value: $ 14.13 bn", size=fs(m, 13, 6), color=F, bold=True, align=L)
    ss.text(s, *m.box(476, 40, 608, 74), [[("Implied Multiple:", {"size": fs(m, 10, 5), "color": G4})], [("7.8x EV/EBITDA", {"size": fs(m, 10, 5), "color": G4})]], align=C_, anchor=MID, margin=0.0)
    ln(s, m, ((405, 75), (405, 405)), A, 1, dash=DASH)
    circ(s, m, 405, 76, 3.5, A)
    rows = (("DCF to Firm", None, 338, 504, 96, "11,400", "19,629"), ("Trading Comps", "(EV/EBITDA FY2)", 332, 429, 162, "11,132", "15,877"), ("Trading Comps", "(EV/EBITDA FY1)", 295, 418, 230, "9,271", "15,378"), ("Trading Comps", "(EV/EBITDA)", 285, 383, 297, "8,765", "13,630"), ("Past Deals", None, 290, 429, 364, "9,030", "15,996"))
    for a, b, x0, x1, yy, lo, hi in rows:
        grad(R(s, m, x0, yy, x1, yy + 28, D), ((0, D), (.5, A), (1, D)), 0)
        pp = [[(a, {"size": fs(m, 11, 5.5)})]] + ([[(b, {"size": fs(m, 11, 5.5)})]] if b else [])
        ss.text(s, *m.box(0, yy - 8, 182, yy + 36), pp, align=RT, anchor=MID, margin=0.0)
        z = fs(m, 11, 5.5)
        off = lambda t_: (.05 + len(t_) * z * .0092) / 2 / m.sx + 3
        lab(s, m, x0 - off(lo), yy + 14, lo, z)
        lab(s, m, x1 + off(hi), yy + 14, hi, z)


def l_note_plate(s, x, y, w, h):
    """Placa em L: faixa no topo com a frase e bloco descendo sobre os últimos anos até o eixo. CSN - ArcelorMittal p.24."""
    m = M((0, 0, 600, 515), (x, y, w, h))
    poly(s, m, ((0, 0), (597, 0), (597, 514), (401, 514), (401, 68), (0, 68)), T)
    ss.text(s, *m.box(16, 6, 392, 62), [[("The plant reached full utilization,", {"bold": True, "size": fs(m, 13, 5.5)})], [("on demand through ", {"size": fs(m, 13, 5.5)}), ("the group's trading arm", {"bold": True, "size": fs(m, 13, 5.5)})]], anchor=MID, margin=0.0)
    pts = ((29, 445), (87, 234), (145, 149), (203, 112), (262, 203), (320, 133), (378, 118), (437, 60), (495, 60), (553, 60))
    vals = ("27%", "67%", "83%", "90%", "73%", "86%", "89%", "100%", "100%", "100%")
    ln(s, m, smooth(pts), D, 1.75)
    for p, v in zip(pts, vals):
        diamond(s, m, p[0], p[1], 4, D)
    z = fs(m, 12, 5.5)
    for i, (p, v) in enumerate(zip(pts, vals)):
        dx = -6 if i in (0, 1, 2) else 0
        lab(s, m, p[0] + dx, p[1] - 22 if i < 7 else p[1] - 19, v, z)
    ln(s, m, ((0, 483), (582, 483)), INK, .75)
    for i, p in enumerate(pts):
        t1(s, m, p[0] - 28, 487, p[0] + 28, 509, str(2016 + i), size=fs(m, 12, 5.5))


def era_dividers(s, x, y, w, h):
    """Barras iguais, tracejadas subindo em cada troca de regime, legenda à direita colada na linha. Cury p.8."""
    m = M((0, 0, 900, 150), (x, y, w, h))
    vals = (57, 55, 52, 55, 55, 62, 56, 66, 102, 132, 136)
    tops = (101, 103, 106, 103, 103, 97, 102, 94, 64, 40, 35)
    for i, (v, t_) in enumerate(zip(vals, tops)):
        x0 = 19 + i * 81.2
        grad(R(s, m, x0, t_, x0 + 47, 148, D), ((0, D), (1, light(F, .25))), 90)
        t1(s, m, x0, t_ + 2, x0 + 47, t_ + 22, str(v), size=fs(m, 10, 5.5), bold=True, color=W)
    ln(s, m, ((0, 149), (900, 149)), INK, .75)
    for cx in (327, 651, 893):
        ln(s, m, ((cx, 8), (cx, 146)), D, .75, dash=DASH)
    for x1, x0, t_ in ((322, 90, "Regime A: funding flat in the fiscal crisis"), (646, 412, "Regime B: gradual recovery, programme renamed"), (889, 658, "Regime C: fast expansion")):
        tm(s, m, x0, 6, x1, 36, t_, size=fs(m, 9, 4.8), color=G4, align=RT, anchor=TOP)


def insider_flags(s, x, y, w, h):
    """Círculo vazado na linha em cada evento, haste tracejada até o rótulo: verbo em bold e quantidade. Meliuz p.19."""
    m = M((0, 0, 900, 330), (x, y, w, h))
    for v, yy in zip(("14.00", "12.00", "10.00", "8.00", "6.00", "4.00", "2.00"), (20, 64, 108, 152, 196, 240, 284)):
        t1(s, m, 0, yy - 10, 46, yy + 10, v, size=fs(m, 12, 5), align=RT)
    key = ((57, 292), (70, 294), (140, 292), (150, 285), (165, 270), (184, 272), (210, 266), (220, 255), (226, 230), (235, 235), (248, 210), (265, 232), (285, 203), (298, 215), (320, 228), (345, 226), (370, 245), (395, 235), (415, 247), (440, 210), (470, 205), (490, 215), (508, 183), (530, 210), (540, 208), (565, 180), (590, 195), (630, 143), (645, 160), (660, 125), (674, 115), (695, 65), (708, 58), (715, 80), (735, 85), (750, 110), (768, 152), (785, 180), (805, 182), (818, 215), (835, 160), (845, 180), (852, 162), (858, 176))
    pts = [(a, b + (0 if i % 42 == 0 else 2.2 * math.sin(i * 1.7) + 1.3 * math.sin(i * 4.1))) for i, (a, b) in enumerate(smooth(key, 3))]
    ln(s, m, pts, dark(G4, .45), 1.25)
    for xx, t in ((90, "Nov-2020"), (264, "Jan-2021"), (420, "Mar-2021"), (590, "May-2021"), (752, "Jul-2021")):
        t1(s, m, xx - 50, 308, xx + 50, 328, t, size=fs(m, 12, 5), color=G4)
    ev = ((184, 272, 170, [("Buy", " of 3.7k shares")], 155), (320, 228, 100, [("Buy", " of 60k shares")], 90), (540, 208, 125, [("Buy", " of 13.5k shares")], 115), (674, 115, 38, [("Sale", " of 8.67 mn")], 28), (768, 152, 82, [("Buyback", "")], 48))
    for cx, cy, top, parts, ly in ev:
        ln(s, m, ((cx, cy - 6.5), (cx, top)), F, .75, dash=DASH)
        circ(s, m, cx, cy, 6.5, None, F, .75)
        z = fs(m, 12, 5.5)
        if cx == 768:
            runs(s, m, 730, 44, 898, 80, [[(parts[0][0], {"bold": True, "size": z})], [("of 98.5k shares", {"size": z})]], align=C_, wrap=False)
        elif cx == 674:
            runs(s, m, 560, 0, 740, 36, [[(parts[0][0], {"bold": True, "size": z}), (parts[0][1], {"size": z})], [("shares, main seller", {"size": z})]], align=C_, wrap=False)
        else:
            runs(s, m, cx - 100, ly - 10, cx + 90, ly + 10, [[(parts[0][0], {"bold": True, "size": z}), (parts[0][1], {"size": z})]], align=C_, wrap=False)


def brush_ring(s, m, cx, cy, rx, ry, c, start=115, sweep=395, wmax=8, tilt=0, jitter=0):
    """Traço de pincel: elipse aberta e afilada nas pontas, como forma fechada única."""
    n = 64
    outer, inner = [], []
    for i in range(n + 1):
        u = i / n
        a = math.radians(start + sweep * u)
        wob = 1 + jitter * math.sin(u * 7) * .03 + (u - .5) * .1
        t_ = wmax * (math.sin(math.pi * u) ** .55) * (.55 + .45 * abs(math.sin(a)))
        for lst, sgn in ((outer, 1), (inner, -1)):
            rx2, ry2 = rx * wob + sgn * t_ / 2, ry * wob + sgn * t_ / 2
            xa, ya = rx2 * math.cos(a), ry2 * math.sin(a)
            lst.append((cx + xa * math.cos(tilt) - ya * math.sin(tilt), cy + xa * math.sin(tilt) + ya * math.cos(tilt)))
    return poly(s, m, outer + inner[::-1], c)


def brush_circle(s, x, y, w, h):
    """Traço de pincel aberto em volta do número vencedor; pares no tracejado fino. Mercado Libre p.68."""
    m = M((0, 0, 820, 75), (x, y, w, h))
    ss.text(s, *m.box(8, 16, 150, 52), [[("Cumulative", {"bold": True, "color": D, "size": fs(m, 12, 6)})], [("Value ratio", {"bold": True, "color": D, "size": fs(m, 12, 6)})]], anchor=MID, margin=0.0)
    brush_ring(s, m, 244, 33, 57, 25, A, 122, 395, 12, -.1)
    brush_ring(s, m, 236, 38, 68, 30, A, 118, 58, 3)
    brush_ring(s, m, 240, 37, 62, 22, A, 128, 46, 2.5)
    brush_ring(s, m, 250, 30, 60, 30, A, -70, 80, 2)
    t1(s, m, 205, 20, 285, 48, "46.9x", size=fs(m, 14, 6.5), bold=True)
    rrm(s, m, 324, 18, 776, 50, None, 3, D, .75, DASH)
    for cx, t in ((364, "10.7x"), (482, "14.2x"), (606, "-0.24x"), (732, "-0.02x")):
        t1(s, m, cx - 50, 20, cx + 50, 48, t, size=fs(m, 14, 6.5), bold=True)
    ln(s, m, ((0, 71), (820, 71)), D, .75)


def _bull(s, m, ox, oy, k, c):
    P = ((0, 8), (3, 6), (12, 5), (22, 5), (27, 3), (28, 0), (30, 3), (33, 1), (33, 5), (37, 8), (38, 11), (35, 11), (31, 9), (29, 13), (28, 18), (29, 24), (26, 24), (25, 17), (15, 17), (11, 24), (8, 24), (9, 16), (5, 14), (3, 20), (2, 13))
    ln(s, m, [(ox + a * k, oy + b * k) for a, b in P], c, .75, closed=True)


def _bear(s, m, ox, oy, k, c):
    P = ((0, 12), (2, 6), (8, 2), (20, 1), (28, 4), (33, 8), (38, 11), (40, 14), (36, 15), (32, 14), (30, 17), (31, 22), (27, 22), (25, 16), (15, 16), (13, 22), (9, 22), (8, 15), (3, 22), (0, 22))
    ln(s, m, [(ox + a * k, oy + b * k) for a, b in P], c, .75, closed=True)


def _icon_hand_coin(s, m, cx, cy, c=INK):
    circ(s, m, cx + 12, cy - 22, 15, None, c, .75); circ(s, m, cx + 12, cy - 22, 11, None, c, .5)
    t1(s, m, cx - 2, cy - 34, cx + 26, cy - 10, "$", size=fs(m, 13, 5), bold=True, color=c)
    for k in range(4):
        ln(s, m, smooth(((cx + 8, cy + 7 + k * 5), (cx + 22, cy + 10 + k * 5), (cx + 38, cy + 7 + k * 5)), 3), c, .75)
    ln(s, m, ((cx - 34, cy + 10), (cx - 24, cy + 4), (cx - 12, cy + 4), (cx + 6, cy - 1), (cx + 14, cy + 1), (cx + 5, cy + 8), (cx + 26, cy + 1), (cx + 32, cy + 5), (cx + 8, cy + 22), (cx - 16, cy + 24), (cx - 22, cy + 30)), c, 1)
    ln(s, m, ((cx - 42, cy + 15), (cx - 32, cy + 7), (cx - 16, cy + 30), (cx - 26, cy + 38)), c, 1, closed=True)


def _icon_target(s, m, cx, cy, c=INK):
    for r_ in (32, 22, 12):
        circ(s, m, cx, cy, r_, None, c, 1)
    ln(s, m, ((cx, cy), (cx + 32, cy - 32)), c, 1)
    ln(s, m, ((cx + 22, cy - 26), (cx + 36, cy - 42), (cx + 38, cy - 34), (cx + 46, cy - 32), (cx + 30, cy - 18)), c, 1)


def price_bull_bear(s, x, y, w, h):
    """Slide escuro: preço sob três linhas-alvo tracejadas, touro e urso, e cartão HOLD com seta de downside. RD Saude p.5."""
    m = M((0, 70, 800, 425), (x, y, w, h))
    R(s, m, 0, 70, 800, 425, D)
    lines = ((120, "29.28", T), (162, "23.26", A), (188, "21.66", light(NEG, .35)))
    key = ((52, 362), (65, 350), (100, 347), (125, 360), (155, 340), (175, 312), (205, 268), (225, 275), (245, 235), (262, 282), (280, 288), (300, 225), (315, 180), (335, 165), (355, 155), (372, 190), (388, 232), (400, 195), (415, 165), (422, 130), (435, 135), (445, 150))
    pts = [(a, b + 3.5 * math.sin(i * 2.3) + 3 * math.sin(i * 5.1) + 1.5 * math.sin(i * 11.3)) for i, (a, b) in enumerate(smooth(key, 8))]
    ln(s, m, pts, light(F, .55), .75)
    for yy, v, c in lines:
        ln(s, m, ((0, yy), (476, yy)), c, .75, dash=DASH)
        lab(s, m, 509, yy, v, fs(m, 11, 5), dark(D, .45))
    R(s, m, 476, 148, 542, 176, None, A, width=.75, dash=True)
    _bull(s, m, 497, 94, .8, T)
    _bear(s, m, 493, 197, .8, light(NEG, .35))
    for i in range(7):
        xx = 55 + i * 66
        a, b = m.p((xx, 402))
        tb = tx(s, a - .2, b - .06, .4, .12, str(2012 + i * 2), size=fs(m, 8, 4.5), color=W, rot=-45)
        tb.text_frame.word_wrap = False
    R(s, m, 552, 79, 788, 386, F)
    R(s, m, 547, 73, 783, 380, G2, T, width=.75, dash=True)
    t1(s, m, 547, 84, 783, 106, "Recommendation", size=fs(m, 14, 6), bold=True, color=F)
    ln(s, m, ((596, 108), (736, 108)), F, 1)
    t1(s, m, 547, 110, 783, 152, "HOLD", size=fs(m, 33, 14), bold=True, color=F)
    _icon_hand_coin(s, m, 596, 202)
    ss.text(s, *m.box(610, 176, 780, 222), [[("Current Price", {"size": fs(m, 15, 6.5)})], [("$ 26.20", {"size": fs(m, 15, 6.5)})]], align=C_, anchor=MID, margin=0.0)
    wedge_arrow(s, m, 673, 235, 285, 10, 16, F)
    ss.text(s, *m.box(690, 240, 782, 272), [[("Downside", {"bold": True, "color": F, "size": fs(m, 10, 5)})], [("-11.35%", {"bold": True, "color": F, "size": fs(m, 10, 5)})]], align=C_, anchor=MID, margin=0.0)
    _icon_target(s, m, 590, 325)
    ss.text(s, *m.box(610, 303, 780, 349), [[("Target Price", {"size": fs(m, 15, 6.5)})], [("$ 23.26", {"size": fs(m, 15, 6.5)})]], align=C_, anchor=MID, margin=0.0)


def brace(s, m, x0, x1, y, h, c, wd=1.25):
    """Chave deitada aberta para cima, ponta central para baixo."""
    r_ = min(h / 2, 8)
    mx = (x0 + x1) / 2
    P = bez((x0, y), (x0, y + h / 2), (x0 + r_, y + h / 2), 6)
    P += bez((mx - r_, y + h / 2), (mx, y + h / 2), (mx, y + h), 6)
    P += bez((mx, y + h), (mx, y + h / 2), (mx + r_, y + h / 2), 6)
    P += bez((x1 - r_, y + h / 2), (x1, y + h / 2), (x1, y), 6)
    ln(s, m, P, c, wd)


def formula_brackets(s, x, y, w, h):
    """Equação centrada, chaves sob termos agrupados e hastes até caixas tracejadas com o significado. Sabesp p.19."""
    m = M((0, 0, 760, 160), (x, y, w, h))
    z = fs(m, 19, 7)
    toks = ((100, "Tariff", False), (133, "=", False), (176, "OPEX", True), (211, "+", False), (224, "(", False), (260, "WACC", True), (303, "x", False), (352, "RAB net", False), (398, ")", False), (412, "+", False), (426, "(", False), (460, "RATE", False), (497, "x", False), (556, "RAB gross", False), (616, ")", False), (628, "±", False), (660, "adj.", True))
    for cx, t, b in toks:
        t1(s, m, cx - 60, 4, cx + 60, 30, t, size=z, bold=b, color=D if b else INK)
    brace(s, m, 228, 396, 31, 14, D); brace(s, m, 428, 614, 31, 14, D)
    t1(s, m, 222, 46, 402, 60, "Remuneration", size=fs(m, 10, 5), bold=True)
    t1(s, m, 428, 46, 614, 60, "Reintegration", size=fs(m, 10, 5), bold=True)
    for cx, y0, y1 in ((176, 30, 97), (247, 40, 97), (660, 30, 92)):
        ln(s, m, ((cx, y0), (cx, y1)), D, 1.25)
    zz = fs(m, 10, 5)
    for x0, y0, x1, parts in ((18, 97, 176, [("Unit costs ", 0), ("locked", 1), (" until the next review", 0)]), (237, 97, 397, [("WACC ", 0), ("fixed for the entire", 1), (" tariff cycle", 0)]), (526, 92, 730, [("Non-manageable costs", 1), (" such as fees and rights are fully ", 0), ("passed through", 1)])):
        rrm(s, m, x0, y0, x1, 155, W, 10, D, 1, DASH)
        runs(s, m, x0 + 7, y0 + 3, x1 - 7, 152, [[(t, {"bold": bool(k), "size": zz}) for t, k in parts]], align=C_)


def gap_wedge(s, x, y, w, h):
    """Cunha sombreada entre as séries desde o evento, com setas curvas até cartões de valor. Sabesp p.19."""
    m = M((0, 0, 560, 210), (x, y, w, h))
    ln(s, m, ((88, 18), (116, 18)), D, 1.75); t1(s, m, 120, 9, 190, 27, "Real cost", size=fs(m, 10, 5), align=L)
    ln(s, m, ((196, 18), (224, 18)), A, 1.75); t1(s, m, 228, 9, 330, 27, "Allowed cost", size=fs(m, 10, 5), align=L)
    t1(s, m, 60, 34, 170, 52, "Privatization", size=fs(m, 10, 5.5), bold=True)
    real = smooth(((50, 80), (105, 125), (149, 148), (247, 158), (346, 145)))
    reg = smooth(((50, 127), (149, 112), (247, 96), (346, 76)))
    x_ = lambda P: [p for p in P if p[0] >= 105]
    poly(s, m, x_(reg) + x_(real)[::-1], light(A, .68))
    ln(s, m, ((105, 62), (105, 180)), F, 1.5, dash=DASH)
    ln(s, m, reg, A, 2); ln(s, m, real, D, 2)
    z = fs(m, 10, 5.5)
    for (cx, cy, v) in ((50, 80, "11.0"), (149, 148, "9.1"), (247, 158, "8.8"), (346, 145, "9.2")):
        lab(s, m, cx, cy, v, z, D)
    for (cx, cy, v) in ((50, 127, "9.7"), (149, 112, "10.1"), (247, 96, "10.6"), (346, 76, "11.1")):
        lab(s, m, cx, cy, v, z, F)
    ln(s, m, ((0, 187), (400, 187)), INK, .75)
    for cx, t in ((50, "2024"), (149, "2025"), (247, "2026"), (346, "2027E")):
        t1(s, m, cx - 40, 192, cx + 40, 209, t, size=fs(m, 10, 5))
    ln(s, m, bez((331, 109), (378, 100), (396, 52)) + [(412, 45)], A, .75, head=True)
    ln(s, m, bez((331, 128), (372, 128), (412, 157)), D, .75, head=True)
    for y0, y1, c, a, b in ((12, 112, light(T, .5), "$ 4.7 bn", "cumulative gain versus the ceiling"), (128, 209, light(T, .5), "$ 1.9 bn gap", "recurring, protected margin")):
        R(s, m, 415, y0, 558, y1, c)
        R(s, m, 415, y0, 558, y0 + 3, A)
        ss.text(s, *m.box(420, y0 + 5, 553, y1 - 2), [[(a, {"bold": True, "size": fs(m, 11, 5.5)})], [(b, {"size": fs(m, 10, 5)})]], align=C_, anchor=MID, margin=0.0)


def fieldset_frames(s, x, y, w, h):
    """Moldura com título colorido sobre a borda, com remendo da cor do painel cortando a linha. Sabesp p.11."""
    m = M((0, 0, 575, 200), (x, y, w, h))
    R(s, m, 0, 0, 575, 200, G1)
    z = fs(m, 13, 6)
    for y0, y1, a, b in ((13, 58, "Miss the annual coverage targets", "Return falls by up to 10 points, lost within the cycle"), (75, 122, "Deviation exceeds the agreed limit", "The regulator blocks all dividend distribution"), (145, 192, "Repeated failure across several years", "The regulator opens the termination process")):
        R(s, m, 5, y0, 570, y1, None, A, width=2)
        half = len(a) * z * .0084 / 2 / m.sx + 8
        R(s, m, 287.5 - half, y0 - 8, 287.5 + half, y0 + 8, G1)
        t1(s, m, 40, y0 - 9, 535, y0 + 9, a, size=z, bold=True, color=F)
        t1(s, m, 10, y0 + 10, 565, y1 - 2, b, size=z)


def compare_row(s, x, y, w, h):
    """Dois cartões com sombra e uma faixa tracejada com brilho que cruza os dois na mesma linha. Vibra p.14."""
    m = M((0, 0, 596, 235), (x, y, w, h))
    kv = (("Client Type", "Large", "Retail"), ("Bargaining Power", "High", "Low"), ("Client Discount", "Higher", "Lower"), ("Operator Margin", "Lower", "Higher"))
    for x0, x1, title, desc, col, side, n in ((3, 291, "Model One", "Credits go to a single large consumer with many units", G1, 1, 2), (303, 590, "Model Two", "Credits go to retail consumers through a consortium", T, 2, 1)):
        shadow(R(s, m, x0, 0, x1, 232, W), 3, 2, 90, 35)
        R(s, m, x0, 0, x1, 232, None, G3, width=.5, dash=True)
        R(s, m, x0, 0, x1, 60, col)
        t1(s, m, x0 + 12, 4, x1, 24, title, size=fs(m, 14, 6.5), bold=True, italic=True, align=L)
        tm(s, m, x0 + 12, 24, x1 - 8, 58, desc, size=fs(m, 10, 5), color=G4, align=L)
        R(s, m, x0, 66, x1, 106, None, G3, width=.5, dash=True)
        t1(s, m, x0 + 12, 74, x0 + 110, 98, "Main player:", size=fs(m, 10, 5), italic=True, bold=True, color=G4, align=L)
        for k in range(n):
            mold(s, m, x0 + 125 + k * 72, 72, x0 + 185 + k * 72, 100, "[logo]")
        for i, row in enumerate(kv):
            yy = 128 + i * 28
            t1(s, m, x0 + 12, yy - 12, x1 - 70, yy + 12, row[0], size=fs(m, 11, 5.5), bold=True, align=L)
            t1(s, m, x1 - 80, yy - 12, x1 - 10, yy + 12, row[side], size=fs(m, 11, 5.5), align=RT)
    hfade(s, m, 0, 198, 200, 227, A, .55, 0)
    grad(R(s, m, 440, 198, 596, 227, A), ((0, A, 0), (1, A, .55)), 0)
    R(s, m, 0, 198, 596, 227, None, G4, width=.5, dash=True)


def deal_ellipses(s, x, y, w, h):
    """Dispersão com duas faixas pelo limite; elipses finas nas ofertas e círculo mais forte na proposta. Vibra p.25."""
    m = M((-24, 0, 900, 215), (x, y, w, h))
    R(s, m, 36, 5, 876, 87, G1); R(s, m, 36, 87, 876, 210, T)
    ln(s, m, ((36, 87), (876, 87)), G3, .5)
    ln(s, m, ((36, 210), (890, 210)), G3, .5)
    z = fs(m, 9, 4.8)
    for v, yy in zip(("4.5x", "4.0x", "3.5x", "3.0x", "2.5x", "2.0x"), (5, 46, 87, 128, 169, 210)):
        t1(s, m, 2, yy - 8, 33, yy + 8, v, size=z, align=RT, color=G4)
    a, b = m.p((-14, 107))
    tb = tx(s, a - .5, b - .06, 1.0, .12, "Net Debt / EBITDA", size=z, color=INK, rot=-90)
    tb.text_frame.word_wrap = False
    t1(s, m, 46, 9, 200, 24, "Threshold Violation", size=z, color=G4, align=L)
    t1(s, m, 46, 190, 220, 206, "Target Leverage Range", size=z, color=D, align=L)
    def rng(cx, y0, y1, t0, t1_, c=D):
        ln(s, m, ((cx, y0), (cx, y1)), c, 1.5)
        circ(s, m, cx, y0, 2.4, c); circ(s, m, cx, y1, 2.4, c)
        lab(s, m, cx, y0 - 11, t0, z, D); lab(s, m, cx, y1 + 11, t1_, z, D)
    for cx, cy, rw, rh, rot_, t, tx0 in ((307, 92, 118, 42, -6, "Offer A", 307), (680, 43, 158, 37, -5, "Offer B", 668)):
        a, b = m.p((cx, cy))
        o = oval(s, a, b, 2 * rw * m.sx, None, h=2 * rh * m.sy, border=D, width=.75, dash=True)
        o.rotation = rot_
        t1(s, m, tx0 - 40, cy - 30 if t == "Offer A" else 18, tx0 + 40, cy - 12 if t == "Offer A" else 34, t, size=fs(m, 10, 5), bold=True, italic=True, color=D)
    circ(s, m, 677, 168, 41, None, F, 2, DASH)
    rng(238, 87, 103, "3.5x", "3.3x"); rng(376, 78, 96, "3.6x", "3.4x")
    rng(571, 54, 62, "3.9x", "3.8x"); rng(784, 28, 46, "4.2x", "4.0x")
    rng(677, 160, 177, "2.6x", "2.4x", F)
    runs(s, m, 726, 155, 880, 183, [[("New Offer", {"size": z, "color": F})], [("(with partner)", {"size": z, "bold": True, "color": F})]])


def tally_plate(s, x, y, w, h, items=(("50", "Orders"), ("19", "Interviewed"))):
    """Placa clara da largura da coluna: numeral em destaque e palavra cinza em tamanho grande. AB InBev p.38."""
    m = M((0, 0, 605, 75), (x, y, w, h))
    R(s, m, 0, 0, 605, 75, G1)
    zn, zw = fs(m, 46), fs(m, 42)
    parts = []
    for i, (n, t) in enumerate(items):
        parts += [(("  " if i else "") + n, {"bold": True, "color": F, "size": zn}), (" " + t, {"color": G4, "size": zw})]
    runs(s, m, 0, 0, 605, 75, [parts], align=C_, wrap=False)


def news_window(s, x, y, w, h):
    """Janela fina com três pontos, logo, manchete, resumo e data; funil claro desce até o gráfico. CSN - ArcelorMittal p.14."""
    m = M((0, 0, 620, 160), (x, y, w, h))
    grad(poly(s, m, ((18, 132), (602, 132), (582, 160), (38, 160)), T), ((0, T), (1, T, .25)), 90)
    shadow(R(s, m, 2, 2, 618, 132, W, INK, width=.75), 3, 2, 90, 35)
    for cx, c in ((22, F), (38, A), (53, NEG)):
        circ(s, m, cx, 16, 5, c)
    mold(s, m, 540, 7, 610, 35, "[logo]")
    t1(s, m, 30, 33, 530, 55, "Company plans to sell assets to cut debt", size=fs(m, 15, 7), bold=True, align=L)
    t1(s, m, 30, 56, 200, 74, "Summary:", size=fs(m, 12, 6), align=L)
    circ(s, m, 58, 89, 1.8, INK)
    tm(s, m, 74, 78, 480, 114, "Plan foresees the sale of a plant next year, with a focus on reducing leverage", size=fs(m, 11, 5.5), align=L, anchor=TOP)
    t1(s, m, 480, 111, 610, 128, "January 16, 2026", size=fs(m, 10, 5), align=RT)


def survey_bar(s, x, y, w, h):
    """Pergunta entre aspas, seta à mão até a barra de duas partes e duas frases com o n. Meliuz p.14."""
    m = M((0, 0, 750, 180), (x, y, w, h))
    t1(s, m, 20, 4, 216, 26, "Field survey", size=fs(m, 13, 6), bold=True)
    ln(s, m, ((118, 28), (118, 57)), G4, .5)
    R(s, m, 27, 57, 207, 145, None, INK, width=.5, dash=True)
    tm(s, m, 35, 60, 200, 142, "“Would you work at the company again?”", size=fs(m, 12, 6))
    # seta à mão: traço afilado com ponta aberta
    top_ = bez((225, 85), (240, 60), (286, 57), 14)
    low_ = bez((225, 88), (246, 72), (286, 58), 14)
    poly(s, m, top_ + low_[::-1], F)
    R(s, m, 296, 34, 580, 88, F)
    R(s, m, 580, 34, 727, 88, dark(G4, .4))
    runs(s, m, 316, 34, 575, 88, [[("63%", {"bold": True, "color": W, "size": fs(m, 15, 7.5)}), ("  YES", {"bold": True, "color": W, "size": fs(m, 11, 6)})]], wrap=False)
    runs(s, m, 584, 34, 716, 88, [[("NO", {"bold": True, "color": W, "size": fs(m, 11, 6)}), ("  37%", {"bold": True, "color": W, "size": fs(m, 15, 7.5)})]], align=RT, wrap=False)
    for yy, n, t in ((120, "29", " former staff interviewed, of whom"), (156, "18", " answered yes to the question")):
        runs(s, m, 336, yy - 18, 745, yy + 18, [[(n, {"bold": True, "color": F, "size": fs(m, 25, 11)}), (t, {"size": fs(m, 14, 6.5)})]], wrap=False)


def survey_chip(s, x, y, w, h):
    """Ícone de formulário sobre placa com o número de respostas, ao lado do tracejado que cerca as barras. Mercado Libre p.13."""
    m = M((0, 0, 625, 225), (x, y, w, h))
    rrm(s, m, 1, 3, 433, 218, None, 8, D, .75, DASH)
    ln(s, m, ((105, 3), (105, 218)), G3, .5)
    z = fs(m, 12, 6)
    for yy, x1, a, b in ((22, 416, "Assortment", "17%"), (98, 329, "Freight", "14%"), (174, 320, "Delivery", "14%")):
        R(s, m, 105, yy, x1, yy + 27, F)
        t1(s, m, 3, yy, 99, yy + 27, a, size=z, color=G4, align=RT)
        t1(s, m, x1 - 60, yy, x1 - 7, yy + 27, b, size=z, bold=True, color=W, align=RT)
    rrm(s, m, 495, 93, 618, 163, G1, 6)
    ss.text(s, *m.box(525, 93, 618, 163), [[("467", {"size": fs(m, 16, 7.5)})], [("answers", {"size": fs(m, 16, 7.5)})]], align=C_, anchor=MID, margin=0.0)
    # ícone genérico de formulário
    poly(s, m, ((469, 82), (501, 82), (523, 104), (523, 157), (517, 163), (469, 163), (463, 157), (463, 88)), D)
    poly(s, m, ((501, 82), (523, 104), (501, 104)), light(D, .5))
    for yy in (116, 129, 142):
        circ(s, m, 479, yy, 2.6, W)
        R(s, m, 487, yy - 1.5, 511, yy + 1.5, W)


def method_stamp_map(s, x, y, w, h):
    """Painel escuro com mapa de calor feito à mão, inserto e selo de método no canto. Mercado Libre p.14. Selo real vira molde; malha urbana do fundo sai, ficam países e estados."""
    m = M((0, 0, 756, 307), (x, y, w, h))
    rrm(s, m, 0, 0, 756, 307, D, 12)
    sea, land = light(T, .25), G1
    geo = countries_50m()
    near = {k: v for k, v in geo.items() if v.get("continent") in ("South America",) or k in ("PAN", "CRI")}
    tile = rrm(s, m, 8, 7, 467, 299, sea, 12)
    bounds = (-78, -21, -37.3, -3.7)
    pxy = clipped_map(s, m, (10, 9, 465, 297), near, bounds, land, W, .25)
    clipped_map(s, m, (10, 9, 465, 297), {k: v for k, v in states("BRA").items()}, bounds, land, G3, .25)
    def heat(lon, lat, r_, hot=False):
        cx, cy = pxy(lon, lat)
        a, b = m.p((cx, cy))
        o = oval(s, a, b, 2 * r_ * m.sx, F)
        radial(o, ((0, NEG, 1), (.18, NEG, .8), (.36, A, .85), (.6, F, .45), (1, F, 0)) if hot else ((0, T, .95), (.25, A, .8), (.55, F, .4), (1, F, 0)))
    for lon, lat, r_, hot in ((-46.5, -23.3, 30, True), (-43.5, -22.5, 20, False), (-48.8, -25.5, 18, False), (-50.5, -28.2, 16, False), (-52, -30, 22, False), (-47.8, -15.8, 15, False), (-38.8, -12.8, 15, False), (-40.2, -5.2, 15, False), (-37.5, -7.5, 15, False), (-58.5, -34.6, 12, False)):
        heat(lon, lat, r_, hot)
    def pin(cx, cy, t, side):
        o = s.shapes.add_shape(MSO_SHAPE.TEAR, *[Inches(v) for v in (m.p((cx - 13, cy - 41))[0], m.p((cx - 13, cy - 41))[1], 26 * m.sx, 26 * m.sx)])
        o.rotation = 135; o.shadow.inherit = False
        ss.paint(o.fill, F); o.line.fill.background()
        circ(s, m, cx, cy - 28, 5, W)
        wi = len(t) * 9.5 + 14
        x0 = cx - wi - 8 if side < 0 else cx + 8
        sp = R(s, m, x0, cy - 22, x0 + wi, cy - 3, dark(G4, .45), alpha=88)
        t1(s, m, x0, cy - 22, x0 + wi, cy - 3, t, size=fs(m, 10, 5.5), color=W)
    a0, b0 = pxy(-46.6, -23.5); a1, b1 = pxy(-43.2, -22.9); a2, b2 = pxy(-58.4, -34.6)
    pin(a0, b0, "Sao Paulo", -1); pin(a1, b1, "Rio de Janeiro", 1); pin(a2, b2, "Buenos Aires", -1)
    # inserto
    rrm(s, m, 484, 8, 736, 159, sea, 7)
    near2 = {k: v for k, v in geo.items() if k in ("MEX", "GTM", "BLZ", "HND", "SLV", "CUB", "USA")}
    b2_ = (-112.5, -79.8, 13, 31)
    q = clipped_map(s, m, (486, 10, 734, 157), near2, b2_, land, G3, .25)
    for lon, lat, r_ in ((-99.1, 19.4, 22), (-100.3, 25.7, 22)):
        cx, cy = q(lon, lat); a, b = m.p((cx, cy))
        radial(oval(s, a, b, 2 * r_ * m.sx, F), ((0, T, .9), (.25, A, .8), (.55, F, .4), (1, F, 0)))
    a3, b3 = q(-99.1, 19.4)
    pin(a3, b3, "Mexico City", -1)
    ss.text(s, *m.box(488, 210, 650, 262), [[("Distribution", {"italic": True, "color": W, "size": fs(m, 15, 7)})], [("Sites Heatmap", {"italic": True, "color": W, "size": fs(m, 15, 7)})]], anchor=MID, margin=0.0)
    R(s, m, 481, 269, 533, 270.5, W)
    rrm(s, m, 660, 210, 756, 276, W, 8)
    mold(s, m, 678, 222, 738, 264, "[logo]", 12)


def browser_card(s, x, y, w, h):
    """Painel cinza com pontos de janela, URL em pílula e cartão branco com logo, manchete e linha de apoio em texto vivo. Rede D'Or p.14."""
    m = M((0, 0, 576, 228), (x, y, w, h))
    rrm(s, m, 0, 0, 576, 228, G2, 5)
    for cx, c in ((27, NEG), (50, A), (72, F)):
        circ(s, m, cx, 22, 8.5, c)
    circ(s, m, 547, 22, 8.5, dark(NEG, .1))
    rrm(s, m, 18, 41, 534, 65, W, 12)
    t1(s, m, 30, 41, 400, 65, "www.outlet.com", size=fs(m, 12, 5.5), align=L)
    R(s, m, 18, 75, 557, 215, W)
    mold(s, m, 250, 80, 326, 108, "[logo]")
    tm(s, m, 28, 112, 548, 164, "New wage floor approved: minimum pay rises by a wide margin", size=fs(m, 18, 8), bold=True, align=L)
    tm(s, m, 28, 164, 548, 212, "The new law reaches every grade of staff, and the sector will feel strong impacts this year", size=fs(m, 14, 6.5), align=L, anchor=TOP)


SLIDES = [
    ("Trackers keep the reader oriented", "Rail, tabs and nested levels show where the argument is",
     [("Storyline rail", "AB InBev p.6", storyline_rail), ("Criteria track with logos", "AB InBev p.40", criteria_track), ("Three-level tracker", "BTG Pactual p.56", three_level_tracker),
      ("Dashed tab tracker", "CSN - ArcelorMittal p.26", section_tabs), ("Thesis orbit agenda", "Intelbras p.4", thesis_orbit), ("Agenda as a website", "Meliuz p.64", site_chrome_toc)]),
    ("Locators repeat so the logic stays visible", "The same small frame returns with a new part lit",
     [("Verdict ticket divider", "Mercado Libre p.5", verdict_ticket), ("Revenue tree locator", "Restaurant Brands p.30", revenue_tree), ("Sized bubbles selector", "Restaurant Brands p.28", bubble_locator),
      ("Guest chrome recolor", "Sabesp p.17", guest_recolor), ("Term ledger under stepper", "Vibra p.31", term_ledger), ("Segments into captions", "BTG Pactual p.18", bar_segments_captions)]),
    ("Annotations make the chart argue", "Marks tie the data to the event or the number that matters",
     [("Price banner over field", "CSN LM p.21", football_banner), ("L-shaped note plate", "CSN - ArcelorMittal p.24", l_note_plate), ("Era dividers over bars", "Cury p.8", era_dividers),
      ("Insider flags on price", "Meliuz p.19", insider_flags), ("Brush ring on the winner", "Mercado Libre p.68", brush_circle), ("Bull and bear on target lines", "RD Saude p.5", price_bull_bear)]),
    ("Formulas and frames carry the reasoning", "Brackets, wedges and shared rows point at the part that counts",
     [("Formula with brackets", "Sabesp p.19", formula_brackets), ("Gap wedge, curved arrows", "Sabesp p.19", gap_wedge), ("Fieldset legend frames", "Sabesp p.11", fieldset_frames),
      ("Row across twin cards", "Vibra p.14", compare_row), ("Deal ellipses on threshold", "Vibra p.25", deal_ellipses), ("Oversized tally plate", "AB InBev p.38", tally_plate)]),
    ("Evidence looks like where it came from", "News, surveys and own data keep the marks of their source",
     [("News window to chart", "CSN - ArcelorMittal p.14", news_window), ("Question to yes/no bar", "Meliuz p.14", survey_bar), ("Survey source chip", "Mercado Libre p.13", survey_chip),
      ("Method stamp on a map", "Mercado Libre p.14", method_stamp_map), ("Browser news card", "Rede D'Or p.14", browser_card)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the device comes from the source.")
    ss.save(prs, OUT)
