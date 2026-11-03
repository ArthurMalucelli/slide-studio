"""Elementos do catálogo, lote b: conteúdo fictício em formas nativas editáveis. Copie a função e troque os textos.
Coordenadas de cada peça em pixels do recorte original; o texto escala com a caixa, para manter a proporção da origem.
Uso: python3 pecas_elementos_b.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE, MSO_PATTERN  # noqa: E402

_AL = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
_AN = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


def fz(m, px, floor=4.0):
    """Tamanho em pt a partir do corpo do texto em pixels do recorte."""
    return max(floor, round(px * min(m.sx, m.sy) * 72, 1))


def T_(s, m, x0, y0, x1, y1, t, px=14, color=INK, bold=False, italic=False, al="c", an="m", hi=None,
       wrap=False, track=None, font=None, floor=4.0, rot=None):
    """Texto em px do recorte. '\\n' quebra parágrafo; **trecho** sai em negrito (e na cor hi, se houver)."""
    paras = []
    for line_ in t.split("\n"):
        runs = []
        for i, part in enumerate(re.split(r"\*\*", line_)):
            if not part:
                continue
            on = i % 2 == 1
            runs.append((part, {"bold": bold or on, "italic": italic, "color": (hi or color) if on else color, "size": fz(m, px, floor)}))
        paras.append(runs or [(" ", {"size": fz(m, px, floor)})])
    sp = ss.text(s, *m.box(x0, y0, x1, y1), paras, align=_AL[al], anchor=_AN[an], margin=0.0)
    sp.text_frame.word_wrap = wrap
    for p in sp.text_frame.paragraphs:
        for r in p.runs:
            if track is not None: r.font._element.set("spc", str(int(track * r.font.size.pt)))
            if font: r.font.name = font
    if rot is not None: sp.rotation = rot
    return sp


def wire(s, m, pts, c=INK, wd=.75, dash=False, dots=False):
    """Linha quebrada em segmentos retos; dash=True tracejado, dash='dot' pontilhado."""
    for a, b in zip(pts, pts[1:]):
        ln = ss.line(s, *m.p(a), *m.p(b), c, wd, dash=False)
        if dash == "dot": ln.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT
        elif dash: ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH


def rbox(s, m, x0, y0, x1, y1, fill=None, adj=.15, border=None, width=1.0, dash=False):
    sp = rr(s, *m.box(x0, y0, x1, y1), fill, adj, border, width)
    if dash and border: sp.line.dash_style = dash
    return sp


def disc(s, m, cx, cy, d, fill=None, border=None, width=1.0, dash=False):
    return oval(s, *m.p((cx, cy)), d * m.sx, fill, d * m.sy, border, width, dash)


def shade(sp, blur=4, dist=2, alpha=28, ang=45, c="000000"):
    """Sombra nativa, editável no PowerPoint."""
    sp.shadow.inherit = False
    fx = sp._element.spPr.find(qn("a:effectLst"))
    o = etree.SubElement(fx, qn("a:outerShdw"))
    o.set("blurRad", str(int(blur * 12700))); o.set("dist", str(int(dist * 12700))); o.set("dir", str(int(ang * 60000))); o.set("algn", "tl"); o.set("rotWithShape", "0")
    cl = etree.SubElement(o, qn("a:srgbClr")); cl.set("val", ss.hx(c))
    al = etree.SubElement(cl, qn("a:alpha")); al.set("val", str(int(alpha * 1000)))
    return sp


def mold(s, m, x0, y0, x1, y1, label="[logo]", px=10, fill=G2, round_=False):
    """Molde cinza no lugar de logo, foto ou print reais."""
    if round_:
        disc(s, m, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, fill)
    else:
        R(s, m, x0, y0, x1, y1, fill)
    T_(s, m, x0, y0, x1, y1, label, px, color=G4)


def star(s, m, cx, cy, d, fill, edge=None, wd=.75):
    px_, py_ = m.p((cx, cy)); ww, hh = d * m.sx, d * m.sy
    sp = s.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, Inches(px_ - ww / 2), Inches(py_ - hh / 2), Inches(ww), Inches(hh))
    sp.shadow.inherit = False
    if fill: ss.paint(sp.fill, fill)
    else: sp.fill.background()
    if edge: sp.line.color.rgb = ss.rgb(edge); sp.line.width = Pt(wd)
    else: sp.line.fill.background()
    return sp


def hatch(sp, fore, back, kind=None):
    sp.fill.patterned()
    sp.fill.pattern = kind or MSO_PATTERN.LIGHT_UPWARD_DIAGONAL
    sp.fill.fore_color.rgb = ss.rgb(fore); sp.fill.back_color.rgb = ss.rgb(back)
    return sp


def check(s, m, cx, cy, d, c):
    """Selo de confere: anel aberto com o traço que o atravessa."""
    disc(s, m, cx, cy, d, None, c, 1.25)
    k = d / 2
    poly(s, m, ((cx - k * .55, cy - k * .05), (cx - k * .32, cy - k * .3), (cx - k * .08, cy + k * .12), (cx + k * .72, cy - k * .82), (cx + k * .98, cy - k * .58), (cx - k * .08, cy + k * .62)), c)
    disc(s, m, cx + k * .78, cy - k * .68, d * .03, c)


# ---------- Peças ----------

def phone_field(s, x, y, w, h):
    """Dado proprietário dentro de um celular desenhado, com recado sobre a base. Vasta p.17."""
    m = M((0, 0, 370, 565), (x, y, w, h))
    rbox(s, m, 1, 1, 365, 562, W, .08, light(F, .72), 1.25)
    grad(disc(s, m, 57, 43, 50, F), ((0, F), (1, D)), 60)
    disc(s, m, 54, 40, 25, None, W, 1.5)
    wire(s, m, ((63, 49), (74, 60)), W, 2)
    T_(s, m, 98, 26, 300, 54, "Field evidence", 20, color=F, bold=True, al="l")
    T_(s, m, 98, 54, 300, 74, "Proprietary scraping", 14, color=G4, italic=True, al="l")
    for b in ((27, 180, 32, 208), (27, 220, 32, 275), (335, 245, 340, 310)): R(s, m, *b, G4)
    rbox(s, m, 32, 92, 335, 530, W, .09, INK, 2)
    rbox(s, m, 163, 106, 203, 113, INK, .5)
    mold(s, m, 58, 124, 152, 158)
    bell = [(289 + a, 141 + b) for a, b in ((-3, -14), (3, -14), (8, -8), (9, 2), (13, 8), (13, 11), (-13, 11), (-13, 8), (-9, 2), (-8, -8))]
    sp = poly(s, m, bell, W, edge=INK, ew=.75)
    disc(s, m, 289, 155, 6, INK); disc(s, m, 296, 130, 7, F)
    T_(s, m, 62, 165, 330, 218, "Recurring,\nnon-forgotten use", 23, color=F, bold=True, al="l")
    T_(s, m, 62, 220, 300, 240, "Field app (app store)", 15, al="l")
    rbox(s, m, 52, 255, 313, 515, G2, .1)
    T_(s, m, 78, 266, 280, 288, "Aggregated data", 14, al="l")
    tiles = ((68, 298, "199", "downloads/\nschool", "down"), (190, 298, "44", "ratings / 1k\nstudents", "star"), (68, 392, "~10x", "peer app", "bars"), (190, 392, "44%", "core traffic", "pie"))
    for tx0, ty, num, lab, ico in tiles:
        shade(rbox(s, m, tx0, ty, tx0 + 106, ty + 86, W, .1), 4, 1.5, 22)
        ix, iy = tx0 + 9, ty + 5
        if ico == "down":
            poly(s, m, ((ix + 8, iy), (ix + 13, iy), (ix + 13, iy + 10), (ix + 18, iy + 10), (ix + 10.5, iy + 18), (ix + 3, iy + 10), (ix + 8, iy + 10)), D)
            poly(s, m, ((ix, iy + 16), (ix + 2.5, iy + 16), (ix + 2.5, iy + 21), (ix + 18.5, iy + 21), (ix + 18.5, iy + 16), (ix + 21, iy + 16), (ix + 21, iy + 24), (ix, iy + 24)), D)
        elif ico == "star":
            star(s, m, ix + 12, iy + 12, 24, D)
        elif ico == "bars":
            for k, hh in enumerate((8, 14, 20)): R(s, m, ix + 3 + k * 7, iy + 24 - hh, ix + 8 + k * 7, iy + 24, D)
            wire(s, m, ((ix, iy), (ix, iy + 26), (ix + 26, iy + 26)), D, .75)
        else:
            poly(s, m, seg((ix + 12, iy + 12), 0, 12, 215, 280), light(D, .5)); poly(s, m, seg((ix + 12, iy + 12), 0, 12, -80, 215), D)
        T_(s, m, tx0 + 12, ty + 37, tx0 + 100, ty + 57, num, 18, color=F, bold=True, al="l")
        T_(s, m, tx0 + 12, ty + 56, tx0 + 104, ty + 85, lab, 12, italic=True, al="l", an="t")
    shade(rbox(s, m, 28, 492, 340, 545, light(T, .55), .16, T, 1), 4, 1.5, 20)
    T_(s, m, 28, 492, 340, 545, "Product **actually used**, with strong\nengagement and real presence.", 13.5, hi=F)


def headline_strips(s, x, y, w, h):
    """Manchetes de uma linha em tiras finas, com data e veículo à direita. Vibra p.39."""
    m = M((0, 0, 506, 145), (x, y, w, h))
    grad(R(s, m, 0, 0, 506, 145, D), ((0, dark(D, .6)), (1, dark(D, .35))), 0)
    rows = ((6, 34, "Global major is going after retail. Is Target next?", "Mar, 25"),
            ((57), 86, "Rival in advanced talks to buy 30% stake in Peer", "Mar, 26"),
            (113, 142, "State weighs return to fuel distribution", "Mar, 26"))
    for y0, y1, head, dt in rows:
        R(s, m, 3, y0, 503, y1, None, ss.mix(A, D, .35), width=.5)
        T_(s, m, 14, y0, 415, y1, head, 12.5, color=W, bold=True, al="l")
        T_(s, m, 415, y0, 462, y1, dt, 10.5, color=W, al="r")
        mold(s, m, 467, y0 + 4, 499, y1 - 4, px=8)


def barrel_stack(s, x, y, w, h):
    """Barril desenhado com nível de enchimento ao lado de quatro faixas por barril. 3R Petroleum p.36."""
    m = M((0, 318, 630, 577), (x, y, w, h))
    hoop = G4
    for wx in (16, 176): R(s, m, wx, 340, wx + 8, 565, hoop)
    R(s, m, 24, 352, 176, 378, D); R(s, m, 24, 402, 176, 500, dark(F, .3)); R(s, m, 24, 524, 176, 552, A)
    for y0, c in ((327, D), (378, D), (500, D), (550, A)):
        rbox(s, m, 9, y0, 191, y0 + 25, hoop, .5)
        rbox(s, m, 16, y0 + 6, 184, y0 + 18, c, .5)
    drop = [(100 + 30 * math.sin(k * math.pi / 20) * math.sin(k * math.pi / 40) ** 1.5, 450 - 27 * math.cos(k * math.pi / 20)) for k in range(41)]
    poly(s, m, drop, dark(F, .3), edge=hoop, ew=2)
    T_(s, m, 300, 318, 525, 335, "2026E", 14)
    rows = ((210, 338, 616, 388, D, "**$383.10** of net revenue per barrel sold"), (212, 400, 617, 451, dark(F, .3), "40% of COGS = $153.20"), (212, 462, 617, 513, dark(F, .3), "27% SG&A = $103.50"), (212, 525, 617, 575, A, "33% net income = **$126.40** per barrel"))
    for x0, y0, x1, y1, c, t in rows:
        rbox(s, m, x0, y0, x1, y1, c, .18)
        T_(s, m, x0, y0, x1, y1, t, 15, color=W)


def equation_strip(s, x, y, w, h):
    """Fórmula em números enormes, com legenda em itálico sob cada termo. AB InBev p.6."""
    m = M((0, 0, 517, 100), (x, y, w, h))
    sp = R(s, m, 2, 2, 515, 98, G1, G4, width=.75, dash=True)
    for cx, t, cap in ((85, "8.3%", "Minimum Viable\nMarket Share"), (258, "0.5%", "Average Annual Change\nin Market Share*"), (440, "16.6", "Moat Size\n(in years)")):
        T_(s, m, cx - 85, 4, cx + 85, 58, t, 47, color=A, bold=True)
        T_(s, m, cx - 85, 58, cx + 85, 94, cap, 11, color=dark(G4, .25), italic=True)
    c = INK
    R(s, m, 160, 34, 185, 38, c); disc(s, m, 172.5, 26, 6.5, c); disc(s, m, 172.5, 46, 6.5, c)
    R(s, m, 340, 26, 366, 32, c); R(s, m, 340, 40, 366, 46, c)


def class_ruler(s, x, y, w, h):
    """Régua de classes com logos nas linhas e barra da menor à maior classe atendida. Arezzo&Co p.4."""
    m = M((0, 0, 570, 200), (x, y, w, h))
    cols_ = (135, 218, 302, 386, 468, 553)
    for cx, t in zip(cols_, ("C-", "C+", "B-", "B+", "A-", "A+")):
        T_(s, m, cx - 25, 2, cx + 25, 24, t, 17, bold=True)
        wire(s, m, ((cx, 27), (cx, 197)), light(T, .35), .5)
    rows_ = ((48, 386, 553), (84, 135, 553), (116, 218, 468), (146, 135, 302), (179, 135, 302))
    for yy, a, b in rows_:
        wire(s, m, ((135, yy), (560, yy)), light(T, .55), .5)
        mold(s, m, 8, yy - 12.5, 96, yy + 12.5)
        wire(s, m, ((a, yy), (b, yy)), A, 2.5)
        disc(s, m, a, yy, 12, A); disc(s, m, b, yy, 12, A)


def logo_timeline(s, x, y, w, h):
    """Logos empilhados sobre cada década; o fim da seta alimenta dois recados. Arezzo&Co p.5."""
    m = M((0, 0, 885, 190), (x, y, w, h))
    for cx, t in zip((35, 140, 258, 365, 472, 580), ("1990s", "2000", "2005", "2010", "2015", "2020")):
        for y0, y1 in ((24, 52), (65, 93), (108, 136)):
            mold(s, m, cx - 37, y0, cx + 37, y1, px=11)
        T_(s, m, cx - 40, 160, cx + 40, 182, t, 15, bold=True)
    wire(s, m, ((30, 146), (626, 146)), INK, .75)
    disc(s, m, 30, 146, 8, INK)
    poly(s, m, ((625, 139), (640, 146), (625, 153)), INK)
    wire(s, m, ((632, 146), (632, 30), (666, 30)), INK, .75)
    wire(s, m, ((632, 115), (666, 115)), INK, .75)
    disc(s, m, 662, 30, 8, INK); disc(s, m, 632, 115, 8, INK); disc(s, m, 662, 115, 8, INK); disc(s, m, 632, 30, 8, INK)
    R(s, m, 668, 5, 882, 52, light(T, .45))
    T_(s, m, 676, 5, 878, 52, "Only about **27% of brands**\nthat entered have **stayed**.", 13, al="l")
    R(s, m, 668, 66, 882, 188, light(T, .45))
    T_(s, m, 676, 68, 878, 128, "Even so, most **brands** are no\nreal **threat** to local players,\nwith exceptions:", 13, al="l")
    mold(s, m, 690, 136, 770, 178, px=11); mold(s, m, 780, 136, 860, 178, px=11)


def verdict_frame(s, x, y, w, h):
    """Recomendação em moldura fina, preço e alvo ligados pelo upside, teses numeradas abaixo. BTG Pactual p.2."""
    m = M((0, 0, 900, 415), (x, y, w, h))
    bg = dark(D, .12)
    R(s, m, 0, 0, 900, 288, bg)
    R(s, m, 0, 288, 900, 415, ss.mix(D, F, .3))
    R(s, m, 67, 8, 828, 207, None, W, width=.5)
    for cx in (67, 828):
        R(s, m, cx - 4, 98, cx + 4, 116, bg)
        wire(s, m, ((cx - 5, 102), (cx + 5, 112)), W, .5); wire(s, m, ((cx - 5, 112), (cx + 5, 102)), W, .5)
    T_(s, m, 200, 30, 700, 70, "Recommendation", 31, color=W, track=10)
    R(s, m, 378, 75, 521, 130, ss.mix(A, bg, .68))
    T_(s, m, 378, 75, 521, 130, "BUY", 46, color=A, bold=True, track=4)
    T_(s, m, 90, 142, 265, 162, "Current Price", 17, color=W, bold=True, track=9)
    T_(s, m, 90, 168, 265, 192, "$ 101.5", 22, color=W)
    T_(s, m, 615, 142, 815, 162, "Target Price", 17, color=A, bold=True, track=9)
    T_(s, m, 615, 168, 815, 192, "$ 154.2", 22, color=A)
    wire(s, m, ((258, 168), (360, 168)), W, .5); wire(s, m, ((545, 168), (641, 168)), W, .5)
    wire(s, m, ((258, 162), (258, 174)), W, .5); wire(s, m, ((641, 162), (641, 174)), W, .5)
    ss.text(s, *m.box(360, 150, 545, 182), [[("52%", {"bold": True, "color": A, "size": fz(m, 27)}), ("  UPSIDE", {"bold": True, "color": A, "size": fz(m, 19)})]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0).text_frame.word_wrap = False
    T_(s, m, 200, 262, 700, 284, "Buy supported by three main theses", 15, color=W, italic=True, track=10)
    for nx, n, t in ((36, "01", "Credit\nDeepening"), (334, "02", "Digital\nRetail Unit"), (633, "03", "Partnership\nModel")):
        T_(s, m, nx, 318, nx + 66, 382, n, 55, color=W, al="l")
        T_(s, m, nx + 74, 322, nx + 250, 378, t, 23, color=W, al="l", track=6)
    for cx in (296, 593):
        wire(s, m, ((cx - 5, 344), (cx + 5, 354)), W, .5); wire(s, m, ((cx - 5, 354), (cx + 5, 344)), W, .5)


def maturity_strip(s, x, y, w, h):
    """Escada de vencimentos: célula hachurada por ano e a última em degradê escuro. CSN - ArcelorMittal p.32."""
    m = M((0, 0, 530, 210), (x, y, w, h))
    grad(R(s, m, 0, 0, 530, 210, D), ((0, dark(D, .35)), (.55, D), (1, F)), 25)
    wire(s, m, ((55, 23), (530, 23)), W, .5)
    for i, yr in enumerate(range(2024, 2032)):
        T_(s, m, 90 + i * 55, 2, 145 + i * 55, 21, str(yr), 11, color=W)
    def cell(bx, by, on):
        sp = rbox(s, m, bx, by, bx + 51, by + 19, W, .1, A if on else F, .75)
        if on: grad(sp, ((0, dark(D, .6)), (1, F)), 0)
        else: hatch(sp, F, W)
    for yy, name, n in ((47, "Note 2028", 4), (92, "Note 2029", 5), (137, "Note 2031", 7)):
        T_(s, m, 2, yy, 88, yy + 19, name, 11, color=W)
        for i in range(n): cell(93 + i * 54.5, yy, False)
        cell(93 + n * 54.5, yy, True)
    T_(s, m, 2, 191, 50, 209, "Legend:", 9, color=W)
    cell(63, 191, True); T_(s, m, 118, 191, 165, 209, "Amortizing", 9, color=W, al="l")
    cell(182, 191, False); T_(s, m, 238, 191, 310, 209, "Not Amortizing", 9, color=W, al="l")


def stake_wires(s, x, y, w, h):
    """Organograma em fios: cada participação interrompe a linha entre dois traços, como um I. Cosan p.20."""
    m = M((0, 0, 520, 545), (x, y, w, h))
    grad(R(s, m, 0, 0, 520, 545, D), ((0, dark(D, .6)), (.6, dark(D, .35)), (1, D)), 40)
    c1, c2 = A, light(A, .55)
    def box(x0, y0, x1, y1, label, lit=False, mold_=False):
        R(s, m, x0, y0, x1, y1, ss.mix(A, dark(D, .35), .85) if not lit else ss.mix(A, D, .6), W if lit else c1, width=1.75 if lit else 1)
        if mold_: mold(s, m, x0 + 18, y0 + 14, x1 - 18, y1 - 14, px=11)
        else: T_(s, m, x0, y0, x1, y1, label, 17, color=W, bold=lit)
    def stake(cx, cy, t, c=c1):
        """Dois traços curtos que seguram o percentual."""
        for yy in (cy - 11, cy + 11): wire(s, m, ((cx - 12, yy), (cx + 12, yy)), c, 1)
        T_(s, m, cx - 28, cy - 10, cx + 28, cy + 10, t, 11, color=W, bold=True)
    for cx, cy in ((59, 114), (191, 114), (325, 114), (457, 114)):
        wire(s, m, ((cx, 67), (cx, cy - 11)), c1, 1); wire(s, m, ((cx, cy + 11), (cx, 140)), c1, 1)
    wire(s, m, ((59, 140), (457, 140)), c1, 1)
    wire(s, m, ((249, 140), (249, 162), (457, 162), (457, 192)), c1, 1)
    wire(s, m, ((21, 67), (21, 165)), c2, 1); wire(s, m, ((21, 188), (21, 317), (434, 317), (434, 296)), c2, 1)
    wire(s, m, ((434, 274), (434, 250)), c1, 1)
    wire(s, m, ((245, 250), (245, 274)), c2, 1); wire(s, m, ((245, 296), (245, 353)), c2, 1)
    wire(s, m, ((59, 410), (59, 428), (196, 428), (196, 441)), c1, 1); wire(s, m, ((196, 463), (196, 482)), c1, 1)
    wire(s, m, ((245, 410), (245, 441)), c2, 1); wire(s, m, ((245, 463), (245, 482)), c2, 1)
    wire(s, m, ((480, 250), (480, 428), (294, 428), (294, 441)), c1, 1); wire(s, m, ((294, 463), (294, 482)), c1, 1)
    for cx, cy, t in ((59, 114, "23.3%"), (191, 114, "21.3%"), (325, 114, "10.4%"), (457, 114, "45.0%")): stake(cx, cy, t)
    stake(21, 177, "14.9%", c2); stake(245, 285, "14.9%", c2); stake(434, 285, "70.2%")
    stake(196, 452, "24.6%"); stake(245, 452, "68.0%", c2); stake(294, 452, "7.4%")
    box(5, 10, 118, 67, "", mold_=True); box(137, 10, 250, 67, "", mold_=True); box(269, 10, 382, 67, "", mold_=True); box(401, 10, 514, 67, "Free Float")
    box(188, 192, 302, 250, "", mold_=True); box(401, 192, 514, 250, "HoldCo", True)
    box(5, 353, 118, 410, "Others"); box(188, 353, 302, 410, "HoldCo B", True); box(188, 482, 302, 540, "TARGET", True)


def range_bar(s, x, y, w, h):
    """Faixa de preço na base do slide: o valor baixo circulado, seta afilada até o alto. Cosan p.12."""
    m = M((0, 0, 610, 90), (x, y, w, h))
    R(s, m, 9, 14, 608, 88, dark(D, .4))
    R(s, m, 2, 5, 600, 80, G1, F, width=1)
    T_(s, m, 14, 5, 355, 80, "Bookbuilding Price Range [$/Share]:", 15, bold=True, al="l")
    T_(s, m, 362, 28, 425, 62, "28.0", 19, color=F, bold=True)
    for k in range(2):
        pts = []
        for i in range(48):
            a = 2 * math.pi * i / 48
            r = 1 + .05 * math.sin(a * 3 + k) + .04 * math.sin(a * 7 + k * 2)
            pts.append((393.5 + 31 * r * math.cos(a), 45 + 18.5 * r * math.sin(a)))
        sp = poly(s, m, pts, W, edge=INK, ew=.75); sp.fill.background()
        sp.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT
    grad(poly(s, m, ((438, 44), (522, 42), (522, 48), (438, 46)), F), ((0, F), (.5, F), (1, dark(D, .45))), 0)
    poly(s, m, ((428, 40), (441, 45), (428, 50)), dark(D, .45))
    poly(s, m, ((531, 40), (519, 45), (531, 50)), dark(D, .45))
    T_(s, m, 535, 28, 595, 62, "35.0", 19, color=F, bold=True)


def map_stems(s, x, y, w, h, keys=("SP", "RJ"), labs=(("SP", "72%", .72), ("RJ", "28%", .28)), anchors=((-46.5, -24.0), (-42.2, -22.95))):
    """Silhueta das regiões presa por hastes à barra de participação. Cury Construtora p.13. Estados só dos 9 países de states()."""
    m = M((0, 0, 355, 235), (x, y, w, h))
    br = states("BRA")
    shapes = {k: br[k] for k in keys}
    box = m.box(3, 6, 352, 162)
    px, py = draw_map(s, box, shapes, lambda k: None)
    stops = ((0, light(F, .3)), (.55, F), (1, D))
    for k in keys:
        for r in shapes[k]["rings"]:
            sp = ss.poly(s, [(px(a), py(b)) for a, b in r], F, INK, .75)
            grad(sp, stops, 225)
    bx0, bx1 = 5, 345
    cur = bx0
    bx_of = []
    for i, (name, val, sh) in enumerate(labs):
        nx = cur + (bx1 - bx0) * sh
        b = R(s, m, cur, 192, nx - (1 if i < len(labs) - 1 else 0), 228, F)
        grad(b, ((0, dark(D, .05)), (1, F)) if i == 0 else ((0, F), (1, light(F, .25))), 0)
        T_(s, m, cur + 10, 192, cur + 60, 228, name, 17, color=W, al="l")
        T_(s, m, nx - 60, 192, nx - 6, 228, val, 11.5, color=W, bold=True, al="r")
        bx_of.append((cur + nx) / 2)
        cur = nx
    for (lo, la), bcx, stem in zip(anchors, (160, 295), (None, None)):
        ax, ay = px(lo), py(la)
        fx_, _ = m.p((bcx, 0))
        ss.line(s, ax, ay, ax, m.p((0, 190))[1], F, .75, dash=False)
        ss.rect(s, ax - 9 * m.sx, m.p((0, 186))[1], 18 * m.sx, 6 * m.sy, F)


def return_ladder(s, x, y, w, h):
    """Decomposição de retorno: paralelogramos que encolhem, ligados às caixas de valor. Cury Construtora p.31."""
    m = M((0, 0, 565, 535), (x, y, w, h))
    grad(R(s, m, 0, 2, 560, 97, F), ((0, F), (1, D)), 90)
    T_(s, m, 15, 16, 175, 42, "Exit Year", 16, color=W); T_(s, m, 15, 54, 175, 84, "2030", 20, color=W, bold=True)
    T_(s, m, 195, 16, 335, 42, "Fair P/E", 16, color=W); T_(s, m, 195, 54, 335, 84, "6.7x", 20, color=W, bold=True)
    wire(s, m, ((362, 49), (392, 49)), W, .75); poly(s, m, ((389, 45), (396, 49), (389, 53)), W)
    T_(s, m, 415, 26, 545, 46, "(ROE – g)", 11, color=W)
    wire(s, m, ((430, 48), (532, 48)), W, .75)
    T_(s, m, 415, 50, 545, 70, "ROE × (Ke – g)", 11, color=W)
    for y0, y1 in ((187, 233), (300, 347), (415, 462)):
        wire(s, m, ((57, y0), (57, y1)), F, 1)
    wire(s, m, ((483, 178), (483, 243)), G3, .75); wire(s, m, ((483, 293), (483, 357)), G3, .75); wire(s, m, ((483, 406), (483, 470)), G3, .75)
    rows = ((120, 187, 333, 295, "Earnings CAGR", "14.9%"), (233, 300, 277, 240, "Dividends", "17.0%"), (347, 415, 222, 187, "Multiple\nContraction", "(4.9%)"), (462, 530, 163, 125, "IRR", "27.0%"))
    for i, (y0, y1, xa, xb, lab, val) in enumerate(rows):
        last = i == 3
        my = (y0 + y1) / 2 - 1
        wire(s, m, (((xa + xb) / 2, my), (420, my)), G2, .75)
        p = poly(s, m, ((0, y0), (xa, y0), (xb, y1), (0, y1)), F if last else G1)
        if last: grad(p, ((0, F), (1, D)), 90)
        T_(s, m, 0, y0, xb + (xa - xb) / 2 - 8, y1, lab, 20, color=W if last else INK)
        vy = my - 25
        R(s, m, 420, vy, 547, vy + 50, W, F, width=.75)
        T_(s, m, 420, vy, 547, vy + 50, val, 14, color=F if last else INK, bold=True)


def rosette(s, m, cx, cy, r, c=F, edge=INK):
    """Roseta em linha, com a fita atrás e a posição no meio."""
    for sg in (-1, 1):
        k = r / 22
        poly(s, m, ((cx + sg * 5 * k, cy + 16 * k), (cx + sg * 14 * k, cy + 14 * k), (cx + sg * 26 * k, cy + 42 * k), (cx + sg * 14 * k, cy + 39 * k), (cx + sg * 7 * k, cy + 49 * k), (cx + sg * -3 * k, cy + 20 * k)), W, edge=edge, ew=1)
    pts = []
    for i in range(120):
        a = 2 * math.pi * i / 120
        rr_ = r * (1 + .07 * math.cos(12 * a))
        pts.append((cx + rr_ * math.cos(a) * 1, cy + rr_ * math.sin(a)))
    poly(s, m, pts, W, edge=edge, ew=1)
    disc(s, m, cx, cy, r * 1.36, W, c, 1)
    T_(s, m, cx - r, cy - r, cx + r, cy + r, "1st", r * .68, color=c, bold=True)


def award_panel(s, x, y, w, h):
    """Prêmios em moldura grossa: logo do órgão, roseta com a posição, ano e categoria. Intelbras p.43."""
    m = M((0, 0, 490, 210), (x, y, w, h))
    R(s, m, 3, 3, 487, 205, None, F, width=2)
    mold(s, m, 72, 46, 168, 74)
    rosette(s, m, 240, 47, 25)
    T_(s, m, 300, 20, 445, 42, "2025’s", 15, bold=True)
    T_(s, m, 300, 46, 445, 90, "Security &\nMonitoring", 16)
    mold(s, m, 62, 124, 158, 180)
    rosette(s, m, 233, 141, 25)
    T_(s, m, 300, 134, 445, 156, "2024’s", 15, bold=True)
    T_(s, m, 280, 156, 465, 178, "Electronics sector", 16)


def severity_table(s, x, y, w, h):
    """Tabela de lacunas com selo de gravidade em anel na primeira coluna; só fios, sem preenchimento. Kering - Moncler p.19."""
    m = M((0, 0, 900, 397), (x, y, w, h))
    R(s, m, 0, 0, 900, 30, D)
    cols_ = ((58, 330), (342, 552), (563, 714), (723, 898))
    for (x0, x1), t in zip(cols_, ("Structural weakness", "Why it matters", "Target solution", "Strategic implication")):
        T_(s, m, x0, 0, x1, 30, t, 12, color=W, bold=True, al="l")
    data = ((ss.NEG, "Overdependence on one brand", "Largest earnings engine, but revenue fell by a third in three years.", "Adds a large, profitable brand with its own identity.", "Cuts concentration risk and lifts portfolio quality."),
            (ss.NEG, "Exposed to crowded categories", "Competition is intense and desirability can shift quickly.", "Brings a specialist platform in a less crowded niche.", "Access to a more defensible source of growth."),
            (A, "Margin pressure", "Sector is moving to margin defense over top-line growth.", "Kept margins near 29% as peers fell to 15-16%.", "Improves profitability, not only revenue."),
            (A, "Weak demand in one region", "Softer demand and a shift away from visible luxury.", "Raised its regional share of sales to 49%.", "Reconnects the group with a growth region."),
            (ss.NEG, "Leadership reset", "Turnaround incomplete after several executive changes.", "Stable, brand-first model built on heritage.", "Reduces reliance on an uncertain turnaround."))
    rh = 73.4
    for i, (c, *cells) in enumerate(data):
        y0 = 30 + i * rh
        disc(s, m, 28, y0 + rh / 2, 25, c, D, 1.25)
        disc(s, m, 28, y0 + rh / 2, 11, W, D, .75)
        for k, ((x0, x1), t) in enumerate(zip(cols_, cells)):
            T_(s, m, x0, y0 + 2, x1, y0 + rh - 2, t, 10.5, bold=k == 0, al="l", wrap=True)
        wire(s, m, ((0, y0 + rh), (900, y0 + rh)), G3, .5)


def star_scorecard(s, x, y, w, h):
    """Cinco estrelas preenchidas até a fração exata da nota, com a coluna tracejada de notas. Mercado Libre p.11."""
    m = M((0, 5, 615, 487), (x, y, w, h))
    mold(s, m, 375, 18, 477, 44, "[logo]", 13)
    rbox(s, m, 488, 8, 605, 481, None, .1, D, 1, MSO_LINE_DASH_STYLE.DASH)
    T_(s, m, 488, 18, 605, 54, "SCORE", 21, color=D, bold=True, italic=True)
    for cy, score in ((92, 4.04), (190, 3.82), (312, 3.48), (428, 3.46)):
        mold(s, m, 10, cy - 28, 190, cy + 28, "[logo]", 15)
        for i in range(5):
            f = max(0, min(1, score - i))
            sp = star(s, m, 241 + i * 48.5, cy, 47, W, INK, .5)
            if f >= 1: ss.paint(sp.fill, A)
            elif f > 0: grad(sp, ((0, A), (f, A), (f, W), (1, W)), 0)
        T_(s, m, 500, cy - 16, 593, cy + 16, f"{score:.2f}", 17, color=D, bold=True)


def arrow_formula(s, x, y, w, h):
    """Fração em itálico matemático com seta colorida ao lado do termo que muda, por fase. Rede D'Or p.61."""
    m = M((0, 0, 240, 285), (x, y, w, h))
    mt = "Cambria Math"
    def formula(y0, up):
        T_(s, m, 8, y0 + 18, 118, y0 + 44, "MLR(%) =", 21, italic=True, al="l", font=mt)
        T_(s, m, 125, y0 + 2, 214, y0 + 28, "Claims", 21, italic=True, font=mt)
        wire(s, m, ((125, y0 + 31), (230, y0 + 31)), INK, .75)
        T_(s, m, 122, y0 + 33, 233, y0 + 58, "Premiums", 21, italic=True, font=mt)
        ax = 222; a, b = (y0 + 28, y0 + 2) if up else (y0 + 2, y0 + 28)
        d = 1 if up else -1
        R(s, m, ax - 1.3, min(a, b) + (5 if up else 0), ax + 1.3, max(a, b) - (0 if up else 5), F)
        poly(s, m, ((ax - 6, b + d * 8), (ax + 6, b + d * 8), (ax, b)), F)
    formula(6, False)
    T_(s, m, 8, 92, 236, 178, "In the first phase, costs eased\nmoderately while revenue held\nsteady, lowering the ratio.\nThen the cycle reversed.", 14.5, al="l")
    formula(214, True)


def cohort_stair(s, x, y, w, h):
    """Heatmap de coortes em escada: cada linha para no último ano, com recado no canto vazio. Sabesp p.17."""
    m = M((0, 0, 585, 230), (x, y, w, h))
    lo, hi_ = light(F, .42), dark(D, .1)
    rows_ = (("Unit A", (28.1, 25.2, 22.7, 18.3, 16.9, 14.1, 13.7, 12.3, 11.8, 10.1)), ("Unit B", (37.3, 32.8, 28.9, 24.2, 21.4, 19.3, 18.1, 17.7)), ("Unit C", (28.8, 26.1, 22.3, 20.6, 19.4)),
             ("Unit D", (31.7, 27.3, 24.3, 21.5, 19.3)), ("Unit E", (24.1, 20.9, 18.2, 16.1)), ("Unit F", (38.5, 33.1, 28.2)))
    x0, cw, y0, chh = 62, 47.2, 10, 32.3
    for i, (nm, vals) in enumerate(rows_):
        yy = y0 + i * chh
        T_(s, m, 0, yy, 58, yy + chh, nm, 10, al="r")
        for j, v in enumerate(vals):
            t = (v - 10) / 30
            R(s, m, x0 + j * cw, yy, x0 + (j + 1) * cw, yy + chh, ss.mix(lo, hi_, t))
            T_(s, m, x0 + j * cw, yy, x0 + (j + 1) * cw, yy + chh, f"{v:.1f}%", 9.5, color=W, bold=True)
    for j in range(10):
        T_(s, m, x0 + j * cw - 2, 205, x0 + (j + 1) * cw + 2, 225, f"Year +{j}", 9.5)
    poly(s, m, ((442, 94), (457, 87), (457, 166), (442, 172)), G3)
    R(s, m, 303, 82, 442, 172, G1, INK, width=.75)
    T_(s, m, 303, 82, 442, 172, "**Average:** -2.9%\nper year!", 14)
    R(s, m, 457, 87, 517, 166, dark(D, .55))
    for i, (ox, wd) in enumerate(((4, 26), (8, 38), (8, 30), (12, 34), (8, 22), (4, 30), (8, 42), (12, 26), (8, 34))):
        R(s, m, 457 + ox, 92 + i * 5.5, 457 + ox + wd, 93.5 + i * 5.5, light(A, .2 + .05 * (i % 3)))
    mold(s, m, 484, 142, 516, 165, px=7)
    grad(R(s, m, 534, 48, 541, 198, F), ((0, hi_), (1, lo)), 90)
    for v, yy in ((40, 48), (35, 73), (30, 98), (25, 123), (20, 148), (15, 173), (10, 198)):
        T_(s, m, 544, yy - 8, 562, yy + 8, str(v), 9.5, al="l")
    cx_, cy_ = m.p((574, 123))
    tx(s, cx_ - .4, cy_ - .07, .8, .14, "Losses (%)", size=fz(m, 9.5), rot=-90)


def proof_tokens(s, x, y, w, h):
    """Comprador por faixa: moeda da empresa ligada por fio a uma prova (KPI, bandeira, mapa). Senior Sistemas p.40."""
    m = M((0, 0, 790, 590), (x, y, w, h))
    gf = F
    def band(y0, name, right):
        R(s, m, 0, y0, 787, y0 + 46, gf)
        disc(s, m, 39, y0 + 23, 38, G2); T_(s, m, 20, y0 + 15, 58, y0 + 31, "[logo]", 8, color=G4, floor=3.2)
        T_(s, m, 68, y0, 400, y0 + 46, name, 18, color=W, bold=True, al="l")
        T_(s, m, 420, y0, 770, y0 + 46, right, 15, color=W, al="r")
    def row(y0, lead, rest):
        rbox(s, m, 0, y0, 787, y0 + 70, G1, .16)
        T_(s, m, 23, y0 + 4, 510, y0 + 66, f"**{lead}** {rest}", 14.5, al="l", hi=F, wrap=True)
        return y0 + 35
    def coin(cx, cy, d=42):
        shade(disc(s, m, cx, cy, d, G2), 2, 1, 22)
        T_(s, m, cx - d / 2, cy - 8, cx + d / 2, cy + 8, "[logo]", 8, color=G4, floor=3.2)
    def chip(x0, y0, x1, y1, a, b):
        rbox(s, m, x0, y0, x1, y1, ss.mix(F, W, .1), .2)
        T_(s, m, x0, y0 + 4, x1, y0 + 25, a, 12, color=W); T_(s, m, x0, y0 + 24, x1, y1 - 3, b, 16, color=W, bold=True)
    def dash(a, b, yy): wire(s, m, ((a, yy), (b, yy)), F, .5, dash=True)
    band(2, "Growth Fund", "US$118 bn AUM | Growth Equity")
    cy = row(60, "Tech + GenAI:", "Declared focus on AI software; portfolio asks margins above 15%, growth above 20%.")
    dash(615, 685, cy); chip(535, cy - 26, 615, cy + 26, "EBITDA", "47%"); coin(650, cy, 32); chip(685, cy - 26, 767, cy + 26, "CAGR", "20%")
    cy = row(137, "Expansion:", "Global network supports the move abroad.")
    dash(580, 688, cy); coin(559, cy)
    for k, c in enumerate((A, F, D)): R(s, m, 688, cy - 24 + k * 16, 764, cy - 8 + k * 16, c)
    cy = row(216, "M&A playbook:", "Finances and accelerates consolidation across its portfolio.")
    dash(580, 658, cy); coin(559, cy); chip(658, cy - 26, 765, cy + 26, "+30 deals", "Since 2015")
    band(309, "Buyout Partners", "US$91 bn AUM | Buyout / Growth")
    cy = row(361, "ERP DNA:", "Has already invested in the main rival of the target.")
    for cx in (569, 641, 713): coin(cx, cy, 48)
    cy = row(440, "Proven reach:", "Active portfolio in the region, with offices in 12 countries.")
    dash(580, 688, cy); coin(559, cy)
    disc(s, m, 718, cy, 60, W, F, .75, True)
    c50 = countries_50m()
    latam = {k: v for k, v in c50.items() if v["subregion"] in ("South America", "Central America") and k != "ATF"}
    latam = {k: {"rings": [r for r in v["rings"] if len(r) > 25]} for k, v in latam.items()}
    draw_map(s, m.box(696, cy - 25, 740, cy + 25), {k: v for k, v in latam.items() if v["rings"]}, F, bounds=(-118, -34, -56, 33))
    cy = row(518, "Tech fund:", "Dedicated vehicle raised US$4 bn for technology.")
    dash(580, 646, cy); coin(559, cy); chip(646, cy - 26, 760, cy + 26, "Revenue", "$1.17 bn")


def exit_triangle(s, x, y, w, h):
    """Tabela de saída em escada; a linha escolhida abre em faixa acesa com KPIs no vazio. Vibra p.39."""
    m = M((0, 0, 733, 590), (x, y, w, h), keep=False)
    grad(R(s, m, 0, 0, 733, 590, D), ((0, dark(D, .65)), (.7, dark(D, .55)), (1, dark(D, .3))), 90)
    R(s, m, 18, 10, 733, 58, None, A, width=.75)
    cols_ = (120, 173, 221, 269, 316, 363, 409, 456, 502, 546)
    for cx, t in zip(cols_, ("2026\nEoP", "2027E", "2028E", "2029E", "2030E", "2031E", "2032E", "2033E", "2034E", "2035E")):
        T_(s, m, cx - 24, 12, cx + 24, 56, t, 12, color=W, bold=True, floor=3.8)
    T_(s, m, 650, 12, 725, 56, "MOIC\n& IRR", 12, color=W, bold=True)
    wire(s, m, ((648, 58), (648, 590)), W, .5)
    flows = ("2,800", "700", "800", "2,000", "900", "950", "1,000", "1,050")
    term = ("17,400", "17,600", "18,600", "21,600", "21,700", "22,900", "24,300", "25,800", "27,400")
    moic = ("1.7x | 74.8%", "2.0x | 48.1%", "2.2x | 35.8%", "2.6x | 32.4%", "2.8x | 28.5%", "3.0x | 26.0%", "3.2x | 24.2%", "3.4x | 22.8%", "3.7x | 21.8%")
    ys = (86, 146, 207, 268, 329, 391, 452, 514, 575)
    grad(R(s, m, 0, 285, 733, 372, A), ((0, A, .28), (.5, A, .1), (1, A, .02)), 90)
    wire(s, m, ((0, 285), (733, 285)), A, 1); wire(s, m, ((0, 372), (733, 372)), A, .5)
    for k, yy in enumerate(ys):
        on = k == 4
        c = A if on else W
        px = 12 if on else 10.5
        T_(s, m, 8, yy - 10, 86, yy + 10, f"{2027 + k} Exit", px, color=c, bold=True, floor=3.8)
        vals = ["(9,900)"] + list(flows[:k]) + [term[k]]
        for cx, v in zip(cols_, vals):
            T_(s, m, cx - 24, yy - 10, cx + 24, yy + 10, v, px, color=c, bold=on, floor=3.8)
        T_(s, m, 650, yy - 10, 733, yy + 10, moic[k], px, color=c, bold=on, floor=3.8)
    for cx, a, b in ((442, "22.0%", "Final Stake"), (518, "10,300", "Buyout"), (603, "9.0x", "EV/EBITDA")):
        T_(s, m, cx - 40, 313, cx + 40, 330, a, 14, color=A, bold=True)
        T_(s, m, cx - 40, 330, cx + 40, 346, b, 11.5, color=W)
    mold(s, m, 382, 272, 424, 300, px=8)


def stair_tree(s, x, y, w, h, active=False):
    """Termos da dívida em degraus, cada um ligado ao anterior por um L com ponto. Alupar p.22. active=True acende o bloco."""
    m = M((0, 0, 615, 225), (x, y, w, h))
    grad(R(s, m, 0, 0, 615, 222, D), ((0, dark(D, .7)), (1, dark(D, .45))), 0)
    c, cs = (A, W) if active else (G4, G4)
    lc = G4
    for yy, v in ((51, "$ 444.0 mn"), (165, "$ 165.0 mn")):
        T_(s, m, 28, yy - 16, 200, yy + 15, v, 22, color=c, bold=True, italic=True, al="l")
        T_(s, m, 28, yy + 15, 205, yy + 31, "Bank project finance | Value", 10.5, color=cs, italic=True, al="l")
    wire(s, m, ((210, 57), (245, 57), (245, 168), (210, 168)), lc, .75)
    wire(s, m, ((245, 112), (295, 112)), lc, .75)
    for p_ in ((210, 57), (210, 168), (245, 112), (295, 112)): disc(s, m, *p_, 4, lc)
    terms = ((320, 32, 320, "Grace Period", "6 months until start-up"), (335, 71, 348, "Lender Confidence", "Predictable revenue and solid ratings"), (368, 109, 384, "Collateral", "Real and fidelity"), (398, 141, 397, "Amortization", "Gradual with cash sweep"), (418, 181, 420, "Maturity", "Dec/2033"))
    leads = ((308, 45, 71, 331), (340, 85, 110, 364), (372, 122, 141, 394), (390, 155, 181, 414))
    for a, b, cc, d_ in leads:
        wire(s, m, ((a, b), (a, cc), (d_, cc)), lc, .75)
        disc(s, m, a, b, 4, lc); disc(s, m, d_, cc, 4, lc)
    for tx0, yy, ix, t, v in terms:
        T_(s, m, tx0, yy - 8, 610, yy + 7, t, 13, color=c, bold=True, al="l")
        T_(s, m, ix, yy + 7, 610, yy + 21, v, 12, color=cs, italic=True, al="l")


def versus_hourglass(s, x, y, w, h):
    """Dois modelos em painéis cortados na diagonal que quase se tocam num X. BTG Pactual p.41."""
    m = M((0, 0, 900, 354), (x, y, w, h))
    T_(s, m, 40, 6, 365, 28, "PRODUCT-ORIENTED", 19, color=D)
    T_(s, m, 540, 6, 865, 28, "CUSTOMER-ORIENTED", 19, color=D)
    poly(s, m, ((35, 35), (375, 35), (445, 190), (375, 350), (35, 350)), G2)
    poly(s, m, ((530, 35), (870, 35), (870, 350), (530, 350), (462, 190)), light(T, .35))
    T_(s, m, 425, 165, 481, 215, "X", 40, color=D, bold=True)
    for bx in (48, 175, 305): mold(s, m, bx, 44, bx + 55, 96, fill=G1, px=11)
    for bx in (540, 668, 798): mold(s, m, bx, 44, bx + 55, 96, px=11)
    wire(s, m, ((48, 102), (368, 102)), G3, .5); wire(s, m, ((538, 100), (858, 100)), G3, .5)
    left = ((155, "Greater Variety of Products", "Advisory, wealth, credit for small\nfirms and affluent clients"), (275, "Credit Expertise", "Long track record in the most\nimportant financial product"))
    right = ((155, "Better User Experience", "A smaller product set, but a\nsharp focus on client needs"), (275, "Data-Driven Culture", "More precise client tracking,\nraising efficiency"))
    for cy, t, d_ in left:
        check(s, m, 75, cy, 42, F)
        T_(s, m, 105, cy - 25, 400, cy - 3, t, 17, color=D, bold=True, al="l")
        T_(s, m, 105, cy - 2, 400, cy + 30, d_, 12, color=G4, al="l")
    for cy, t, d_ in right:
        check(s, m, 837, cy, 42, F)
        T_(s, m, 500, cy - 25, 803, cy - 3, t, 17, color=D, bold=True, al="r")
        T_(s, m, 500, cy - 2, 803, cy + 30, d_, 12, color=G4, al="r")
    cx_, cy_ = m.p((18, 192)); tx(s, cx_ - .7, cy_ - .1, 1.4, .2, "Large Incumbents", size=fz(m, 17), color=D, bold=True, rot=-90)
    cx_, cy_ = m.p((884, 192)); tx(s, cx_ - .7, cy_ - .1, 1.4, .2, "Challengers", size=fz(m, 17), color=D, bold=True, rot=90)


def ownership_flow(s, x, y, w, h):
    """Árvore de transação em dois passos, cada um numa moldura com título no fio. CSN (Liability Management) p.22."""
    m = M((0, 0, 900, 395), (x, y, w, h))
    grad(R(s, m, 0, 0, 900, 395, D), ((0, dark(D, .35)), (1, ss.mix(D, F, .25))), 35)
    W2 = light(T, .1)
    def box(x0, y0, x1, y1, t, px=11):
        grad(R(s, m, x0, y0, x1, y1, D, W, width=.75), ((0, ss.mix(D, F, .25)), (1, dark(D, .25))), 90)
        T_(s, m, x0, y0, x1, y1, t, px, color=W)
    def chip(cx, cy, t):
        b = (cx - 22, cy - 11, cx + 22, cy + 11)
        sp = R(s, m, *b, dark(D, .2), W2, width=.5, dash=True)
        T_(s, m, *b, t, 9.5, color=W, bold=True)
    mold(s, m, 20, 6, 95, 30, px=9)
    wire(s, m, ((57, 30), (57, 112)), W, .75)
    R(s, m, 30, 54, 84, 72, ss.mix(D, F, .3)); T_(s, m, 30, 54, 84, 72, "Advising", 10, color=W)
    mold(s, m, 8, 112, 84, 138, px=9)
    wire(s, m, ((84, 124), (130, 124)), W, 1); wire(s, m, ((130, 50), (130, 195)), W, 1)
    wire(s, m, ((130, 70), (150, 70)), W, 1); wire(s, m, ((130, 178), (150, 178)), W, 1)
    box(150, 49, 238, 91, "Unit\nSale", 10); box(150, 157, 238, 200, "Bridge Loan\nPayment", 9.5)
    wire(s, m, ((238, 70), (262, 70), (262, 42), (328, 42)), W, 1)
    wire(s, m, ((238, 178), (262, 178), (262, 262), (328, 262)), W, 1)
    # Moldura de cima: sem topo no trecho do título
    wire(s, m, ((470, 8), (328, 8), (328, 192), (896, 192), (896, 8), (756, 8)), W, .75)
    T_(s, m, 470, 0, 756, 15, "Unit sale generates $14.9 bn in proceeds", 11.5, color=W)
    mold(s, m, 335, 94, 408, 116, px=9)
    wire(s, m, ((408, 105), (445, 105)), W, .75); wire(s, m, ((445, 50), (445, 158)), W, .75)
    for yy, t, pct in ((51, "Unit A", "100%"), (105, "Unit B", "100%"), (158, "Unit C", "69%")):
        wire(s, m, ((445, yy), (468, yy)), W, .75)
        box(468, yy - 21, 550, yy + 21, t, 10.5); chip(445, yy + (3 if yy != 105 else 0), pct)
    sp = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, *[Inches(v) for v in m.box(612, 88, 685, 112)]); sp.shadow.inherit = False
    sp.fill.background(); sp.line.color.rgb = ss.rgb(W); sp.line.width = Pt(.75)
    T_(s, m, 565, 136, 712, 154, "Sale Proceeds: $14.9 bn", 10, color=W)
    mold(s, m, 722, 90, 795, 112, px=9)
    wire(s, m, ((768, 47), (768, 90)), W, .75); wire(s, m, ((768, 112), (768, 155)), W, .75)
    wire(s, m, ((768, 47), (794, 47)), W, .75); wire(s, m, ((768, 155), (794, 155)), W, .75)
    box(794, 26, 876, 68, "Unit B", 10.5); box(794, 133, 876, 176, "Unit C", 10.5)
    chip(768, 50, "100%"); chip(768, 152, "69%")
    # Moldura de baixo
    wire(s, m, ((445, 222), (328, 222), (328, 393), (896, 393), (896, 222), (790, 222)), W, .75)
    T_(s, m, 445, 214, 790, 230, "Repayment generates meaningful interest savings", 11.5, color=W)
    T_(s, m, 345, 240, 450, 258, "Bridge Loan:", 10, color=W, al="l")
    T_(s, m, 432, 270, 475, 288, "2026", 9.5, color=W); T_(s, m, 484, 270, 530, 288, "2027", 9.5, color=W)
    T_(s, m, 345, 292, 428, 310, "Debt: Bullet", 10, color=W)
    R(s, m, 432, 293, 476, 307, dark(D, .35)); R(s, m, 484, 293, 532, 307, ss.mix(D, F, .35), W, width=1)
    R(s, m, 354, 344, 390, 356, ss.mix(D, F, .35), W, width=.75); T_(s, m, 397, 342, 520, 358, "Amortization", 8.5, color=W, al="l")
    R(s, m, 354, 367, 390, 379, dark(D, .35)); T_(s, m, 397, 365, 520, 381, "No amortization", 8.5, color=W, al="l")
    wire(s, m, ((545, 238), (545, 298)), W, .75); wire(s, m, ((545, 312), (545, 378)), W, .75)
    wire(s, m, ((538, 303), (552, 293)), W, .75); wire(s, m, ((538, 315), (552, 305)), W, .75)
    wire(s, m, ((556, 258), (890, 258)), W, .5); wire(s, m, ((556, 322), (890, 322)), W, .5)
    hx_ = (672, 722, 764, 806, 856)
    for cx, t in zip(hx_, ("2027E", "2028E", "...", "2030E", "2031E")): T_(s, m, cx - 22, 242, cx + 22, 257, t, 9, color=W, bold=True)
    for yy, nm, vals in ((277, "(+) Interest", ("220", "222", "...", "235", "241")), (306, "(=) Savings", ("161", "139", "...", "107", "94"))):
        T_(s, m, 560, yy - 9, 648, yy + 9, nm, 9, color=W, al="l")
        for cx, v in zip(hx_, vals): T_(s, m, cx - 22, yy - 9, cx + 22, yy + 9, v, 9, color=W)
    for cx, a, b in ((610, "$ 3,478 mn", "Amortization\ntranche"), (730, "$ 623 mn", "Interest\nsavings"), (845, "100%", "Bridge loan\nrepayment")):
        T_(s, m, cx - 55, 330, cx + 55, 350, a, 13, color=W)
        T_(s, m, cx - 55, 351, cx + 55, 381, b, 9.5, color=W)
    sp = R(s, m, 5, 232, 233, 390, ss.mix(D, F, .1), W2, width=.75, dash=True)
    T_(s, m, 14, 238, 225, 258, "Transaction Mechanism:", 13, color=W, bold=True, al="l")
    for i, t in enumerate(("Below-market supply lifts\nupfront capitalization", "By-product contract adds\nacquirer margin", "Tranche repaid in full\nat closing")):
        yy = 264 + i * 42
        disc(s, m, 18, yy + 9, 4, W)
        T_(s, m, 26, yy, 230, yy + 34, t, 10, color=W, al="l", an="t")


def state_ledger(s, x, y, w, h, active=0):
    """Três estados da operação em caixas empilhadas: só a ativa em contraste cheio. Cosan p.31."""
    m = M((0, 0, 600, 550), (x, y, w, h))
    bg = dark(D, .6)
    grad(R(s, m, 0, 0, 600, 550, D), ((0, dark(D, .75)), (.5, bg), (1, dark(D, .3))), 45)
    states_ = (("Post IPO", (8, 157), (("75.4", "%"), ("28.3", "%"), ("7,420", "mm"), ("–", ""))),
               ("Post Note Conversion", (200, 349), (("52.1", "%"), ("23.4", "%"), ("3,575", "mm"), ("22.0", "%"))),
               ("Post Spin-off &\nFollow-on", (393, 540), (("0.0", "%"), ("14.5", "%"), ("0.0", "mm"), ("100.0", "%"))))
    heads = ("Stake\nin Target", "Holding\nDiscount", "Holding Adj.\nNet Debt", "Reduction in\nInterest")
    for k, (title, (y0, y1), vals) in enumerate(states_):
        on = k == active
        dim = lambda c: c if on else ss.mix(c, bg, .8)
        a0, a1 = 195, 392
        wire(s, m, ((a0, y0), (10, y0), (10, y1), (588, y1), (588, y0), (a1, y0)), dim(A), 1 if on else .75)
        if on: wire(s, m, ((10, y1 - 60), (10, y1), (170, y1)), light(A, .55), 1.25)
        if on:
            for cx, c in ((a0, light(A, .35)), (a1, A)):
                px_, py_ = m.p((cx, y0))
                sp = s.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(px_ - 8 * m.sx), Inches(py_ - 8 * m.sy), Inches(16 * m.sx), Inches(16 * m.sy)); sp.shadow.inherit = False
                ss.paint(sp.fill, c); sp.line.fill.background()
        T_(s, m, a0 + 8, y0 - 12, a1 - 8, y0 + (24 if "\n" in title else 12), title, 11, color=dim(W), italic=True, an="t" if "\n" in title else "m")
        for cx, (v, u), hd in zip((91, 226, 368, 511), vals, heads):
            ss.text(s, *m.box(cx - 68, y0 + 40, cx + 68, y0 + 84), [[(v, {"bold": True, "color": dim(W), "size": fz(m, 25)}), (" " + u if u else "", {"bold": True, "color": dim(W), "size": fz(m, 14)})]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0).text_frame.word_wrap = False
            T_(s, m, cx - 68, y0 + 90, cx + 68, y0 + 134, hd, 14, color=dim(A), bold=True)


def piggy(s, m, cx, cy, c, k=1.0):
    """Ícone de linha: cofrinho com moeda em cima."""
    oval(s, *m.p((cx, cy)), 40 * k * m.sx, None, 28 * k * m.sy, c, .75)
    poly(s, m, ((cx + 10 * k, cy - 12 * k), (cx + 21 * k, cy - 15 * k), (cx + 19 * k, cy - 4 * k)), W, edge=c, ew=.75).fill.background()
    wire(s, m, ((cx - 12 * k, cy + 11 * k), (cx - 13 * k, cy + 19 * k), (cx - 7 * k, cy + 19 * k), (cx - 6 * k, cy + 13 * k)), c, .75)
    wire(s, m, ((cx + 12 * k, cy + 11 * k), (cx + 13 * k, cy + 19 * k), (cx + 7 * k, cy + 19 * k), (cx + 6 * k, cy + 13 * k)), c, .75)
    wire(s, m, ((cx - 20 * k, cy), (cx - 26 * k, cy - 3 * k), (cx - 23 * k, cy + 3 * k)), c, .5)
    disc(s, m, cx, cy - 22 * k, 15 * k, None, c, .75)
    T_(s, m, cx - 8 * k, cy - 29 * k, cx + 8 * k, cy - 15 * k, "$", 10 * k, color=c, bold=True)
    disc(s, m, cx + 13 * k, cy - 3 * k, 3 * k, c)


def thesis_ladder(s, x, y, w, h):
    """Três teses em degraus numa diagonal tracejada, terminando no BUY sobre foto. Nubank p.4."""
    m = M((0, 0, 900, 506), (x, y, w, h))
    R(s, m, 0, 0, 900, 506, F)
    p = poly(s, m, ((672, 0), (900, 0), (900, 506), (445, 506)), G2)
    T_(s, m, 690, 110, 860, 160, "[foto]", 18, color=G4)
    ss.set_alpha(poly(s, m, ((517, 312), (900, 312), (900, 506), (445, 506)), F), 72)
    wire(s, m, ((588, 0), (353, 500)), W, .75, dash=True)
    mold(s, m, 6, 6, 60, 38, px=11, fill=W)
    claims = ((356, 103, 537, 113, "**Low-cost** operations powering a\n**high-return model**"), (306, 247, 467, 256, "High usage today, higher\n**monetization tomorrow**"), (232, 400, 401, 406, "**Region X** becomes the next\ncompounding engine"))
    for cx, cy, ix, iy, t in claims:
        T_(s, m, cx - 150, cy - 28, cx + 150, cy + 28, t, 18, color=W, hi=W)
        R(s, m, ix - 30, iy - 38, ix + 30, iy + 28, F)
        piggy(s, m, ix, iy, W, 1.15)
    T_(s, m, 500, 355, 850, 425, "BUY!", 62, color=W, bold=True)
    T_(s, m, 450, 428, 895, 466, "Yes, we want to be partners!", 25, color=W, bold=True)


def question_interrupt(s, x, y, w, h):
    """Slide anterior apagado em cinza sob um painel branco com a pergunta. Nubank p.31."""
    m = M((0, 0, 900, 506), (x, y, w, h))
    R(s, m, 0, 0, 900, 506, G2)
    gh, gh2 = G3, ss.mix(G3, G2, .45)
    poly(s, m, ((0, 0), (32, 0), (42, 60), (28, 240), (42, 400), (34, 506), (0, 506)), gh)
    R(s, m, 48, 22, 52, 66, G4)
    T_(s, m, 60, 18, 720, 48, "Reaching this segment opens a growth path", 25, color=G4, bold=True, al="l")
    T_(s, m, 60, 50, 720, 66, "Loans unlock **mass-market expansion** and **higher revenue per user**", 13, color=G4, al="l")
    T_(s, m, 52, 88, 440, 106, "In one market, **card acquisition** falls short", 14, color=G4, al="l")
    T_(s, m, 476, 88, 860, 106, "A stable share of borrowers stays **card-less**", 14, color=G4, al="l")
    wire(s, m, ((52, 107), (446, 107)), G4, .5); wire(s, m, ((470, 107), (868, 107)), G4, .5)
    R(s, m, 57, 120, 290, 242, gh)
    rbox(s, m, 50, 338, 868, 474, gh2, .14)
    rbox(s, m, 610, 287, 840, 410, gh, .08)
    wire(s, m, ((144, 439), (820, 439)), G4, .75); poly(s, m, ((819, 435), (827, 439), (819, 443)), G4)
    for cx in (215, 392, 565, 740): rbox(s, m, cx - 34, 406, cx + 34, 472, G4, .14)
    T_(s, m, 52, 476, 620, 490, "Overview | Disruption | Monetization | **Expansion** | Multiples | Risks", 9, color=G4, al="l")
    wire(s, m, ((50, 490), (890, 490)), G4, .5)
    shade(rbox(s, m, 65, 125, 833, 403, W, .13), 3, 1, 15)
    T_(s, m, 80, 200, 820, 330, "But can **Competitor X** threaten\nthe leader in the region?", 44, hi=F)


def risk_ids(s, x, y, w, h, drill=None):
    """Riscos com código e cor por família; drill='O1' mantém o mapa e troca o lado direito pela prova. Rede D'Or p.42."""
    m = M((0, 0, 900, 412), (x, y, w, h))
    fam = {"O": D, "S": A, "MG": F}
    for vx in (96, 163, 230, 297, 362, 428, 476): wire(s, m, ((vx, 38), (vx, 405)), G2, .75)
    for hy in (38, 127, 195, 263, 328): wire(s, m, ((30, hy), (476, hy)), G2, .75)
    wire(s, m, ((30, 405), (30, 34)), F, 1); wire(s, m, ((30, 405), (480, 405)), F, 1)
    poly(s, m, ((26, 38), (30, 29), (34, 38)), F); poly(s, m, ((476, 401), (485, 405), (476, 409)), F)
    T_(s, m, 0, 12, 90, 30, "Probability", 13, bold=True, al="l")
    T_(s, m, 492, 396, 560, 414, "Impact", 13, bold=True, al="l")
    tiles = (("O2", 195, 74, 277, 145), ("MG1", 88, 144, 172, 215), ("S2", 252, 152, 335, 222), ("MG2", 365, 157, 447, 229), ("S1", 128, 224, 211, 295), ("O1", 286, 293, 369, 363))
    for code, x0, y0, x1, y1 in tiles:
        c = fam["MG" if code.startswith("MG") else code[0]]
        R(s, m, x0 + 5, y0 + 5, x1 + 5, y1 + 5, dark(D, .7))
        R(s, m, x0, y0, x1, y1, c)
        T_(s, m, x0, y0, x1, y1, code, 12, color=W, bold=True)
    def panel(y0, y1, c, title):
        R(s, m, 561, y0 + 8, 896, y1, c)
        R(s, m, 553, y0, 889, y1 - 5, G1)
        T_(s, m, 553, y0 + 2, 889, y0 + 30, title, 17, color=c, bold=True)
    if not drill:
        for y0, y1, c, title, rows in ((4, 120, D, "Operational Risks", (("O1", "Retaliation from key client"), ("O2", "Expansion plan runs late"))),
                                       (136, 252, A, "Sector Risks", (("S1", "Operators verticalize"), ("S2", "Network de-accreditation"))),
                                       (268, 384, F, "Macro and Policy Risks", (("MG1", "New regulation"), ("MG2", "High unemployment")))):
            panel(y0, y1, c, title)
            for k, (cd, t) in enumerate(rows):
                T_(s, m, 563, y0 + 34 + k * 29, 885, y0 + 62 + k * 29, f"**{cd}** – {t}", 16, al="l", hi=c)
    else:
        c = fam["MG" if drill.startswith("MG") else drill[0]]
        panel(4, 400, c, "Operational Risks")
        T_(s, m, 553, 40, 889, 66, f"**{drill}** – **Retaliation from key client**", 16, hi=c)
        T_(s, m, 553, 68, 889, 158, "With too much revenue tied to one\nclient, a retaliation could cause\nserious problems for the company.", 15.5)
        R(s, m, 565, 178, 569, 204, F); T_(s, m, 576, 178, 800, 204, "Revenue by client", 13, color=D, bold=True, al="l")
        ccx, ccy = 720, 292
        a0 = -90
        for v, col in ((.25, D), (.20, A), (.55, G4)):
            poly(s, m, seg((ccx, ccy), 42, 68, a0, a0 + v * 360, 30), col)
            mid = math.radians(a0 + v * 180)
            lx, ly = ccx + 88 * math.cos(mid), ccy + 82 * math.sin(mid)
            b = (lx - 21, ly - 12, lx + 21, ly + 12)
            rbox(s, m, *b, dark(D, .1), .25); T_(s, m, *b, f"{int(v * 100)}%", 11, color=W, bold=True)
            a0 += v * 360
        for k, (lb, col) in enumerate((("Client A", D), ("Client B", A), ("Others", G4))):
            lx = 590 + k * 95
            R(s, m, lx, 379, lx + 9, 388, col); T_(s, m, lx + 13, 375, lx + 90, 392, lb, 11, al="l")


def risk_ids_drill(s, x, y, w, h):
    """Segunda página do mesmo sistema: mapa mantido e um único risco à direita, com sua prova. Rede D'Or p.43."""
    risk_ids(s, x, y, w, h, drill="O1")


def skim_lede(s, x, y, w, h):
    """Frase de duas linhas em cinza, com fio grosso à esquerda; só as expressões-chave ganham cor. AB InBev p.6."""
    parts = "To size the advantage, we used the **moat approach**, reaching a **long-lasting moat**, showing how **past efforts** have **well-positioned** the group **for the future**, with **better execution**."
    plain = parts.replace("**", "")
    pt_ = min(12, round(w * 72 / (len(plain) / 2 * .56) * .96, 1))
    lh = pt_ * 1.25 * 2 / 72
    yy = y + .02
    ss.rect(s, x, yy, .04, lh, dark(G4, .4))
    runs = []
    for i, part in enumerate(parts.split("**")):
        if part: runs.append((part, {"bold": i % 2 == 1, "color": A if i % 2 else G4, "size": pt_}))
    ss.text(s, x + .08, yy, w - .08, lh, [runs], anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def _mini(s, m, x0, y0, x1, y1, c, variant):
    """Slide em miniatura pintado inteiro com um único protagonista."""
    W_, H_ = x1 - x0, y1 - y0
    fx_ = lambda a: x0 + W_ * a
    fy_ = lambda b: y0 + H_ * b
    R(s, m, x0, y0, x1, y1, W, G3, width=.5)
    tint = light(c, .6)
    if variant == 0:
        T_(s, m, fx_(.03), fy_(.02), fx_(.82), fy_(.1), "Section title in the theme", 14, bold=True, al="l", floor=3.5)
        wire(s, m, ((fx_(.03), fy_(.115)), (fx_(.97), fy_(.115))), c, 1)
        mold(s, m, fx_(.85), fy_(.02), fx_(.97), fy_(.09), px=6)
        bars = ((-.3, .35), (.3, .2), (-.45, .4), (.22, .45), (.5, .3))
        ybase = fy_(.55)
        for i, (v, _) in enumerate(bars):
            bx = fx_(.05 + i * .085)
            y_a, y_b = sorted((ybase, ybase - v * H_ * .45))
            R(s, m, bx, y_a, bx + W_ * .05, y_b, dark(c, .35) if i % 2 else c)
        wire(s, m, ((fx_(.03), ybase), (fx_(.48), ybase)), G4, .5)
        rbox(s, m, fx_(.52), fy_(.15), fx_(.97), fy_(.4), light(c, .85), .1, c, .75)
        mold(s, m, fx_(.55), fy_(.18), fx_(.68), fy_(.26), px=5)
        for i in range(3): R(s, m, fx_(.55), fy_(.29 + i * .03), fx_(.93), fy_(.3 + i * .03), G3)
        for i, hh in enumerate((.18, .1, .08, .05, .06, .1, .13, .2)):
            bx = fx_(.53 + i * .054)
            R(s, m, bx, fy_(.9 - hh), bx + W_ * .036, fy_(.9), c if i < 3 else dark(c, .3))
        ss.set_alpha(R(s, m, fx_(.52), fy_(.55), fx_(.68), fy_(.92), light(c, .4)), 25)
        R(s, m, fx_(.03), fy_(.63), fx_(.48), fy_(.92), G1)
        for i in range(4): R(s, m, fx_(.06), fy_(.68 + i * .05), fx_(.44), fy_(.695 + i * .05), G3)
    else:
        grad(R(s, m, x0, y0, x0 + W_ * .19, y1, c), ((0, c), (1, dark(c, .4))), 90)
        for i in range(4):
            yy = fy_(.2 + i * .17)
            R(s, m, fx_(.03), yy, fx_(.16), yy + H_ * .02, W)
            R(s, m, fx_(.05), yy + H_ * .04, fx_(.14), yy + H_ * .055, light(c, .6))
        T_(s, m, fx_(.22), fy_(.02), fx_(.85), fy_(.1), "Section title in the theme", 14, bold=True, al="l", floor=3.5)
        R(s, m, fx_(.22), fy_(.1), fx_(.74), fy_(.12), c)
        mold(s, m, fx_(.87), fy_(.02), fx_(.98), fy_(.09), px=6)
        for i, hh in enumerate((.1, .16, .24, .38)):
            bx = fx_(.25 + i * .07)
            R(s, m, bx, fy_(.5 - hh), bx + W_ * .05, fy_(.5), c)
        wire(s, m, ((fx_(.22), fy_(.5)), (fx_(.56), fy_(.5))), G4, .5)
        for k, col in enumerate((c, tint)):
            pts = [(fx_(.62 + i * .07), fy_(.2 + k * .1 + .12 * math.sin(i + k) * (1 - i * .1))) for i in range(6)]
            wire(s, m, pts, col, 1)
        for yy in (.56, .77):
            R(s, m, fx_(.22), fy_(yy), fx_(.97), fy_(yy + .17), G1)
            R(s, m, fx_(.24), fy_(yy + .03), fx_(.3), fy_(yy + .14), c)
            R(s, m, fx_(.33), fy_(yy + .06), fx_(.93), fy_(yy + .075), G3)
            R(s, m, fx_(.33), fy_(yy + .1), fx_(.8), fy_(yy + .115), G3)


def brand_takeover(s, x, y, w, h, other=None):
    """O tema inteiro troca de cor quando o protagonista muda. CSN - ArcelorMittal p.14 e 24; Nubank. other = cor do segundo protagonista."""
    m = M((0, 0, 900, 506), (x, y, w, h))
    b = other or ss.NEG
    gap = 4
    _mini(s, m, 0, 0, 450 - gap, 253 - gap, F, 0)
    _mini(s, m, 450 + gap, 0, 900, 253 - gap, b, 0)
    _mini(s, m, 0, 253 + gap, 450 - gap, 506, F, 1)
    _mini(s, m, 450 + gap, 253 + gap, 900, 506, b, 1)


def dark_section(s, x, y, w, h):
    """O deck fica escuro só na seção da operação: tira de páginas e o slide preto com stepper à esquerda. Vibra p.31-40 (sem recorte; base p.34)."""
    m = M((0, -92, 934, 525), (x, y, w, h))
    bg = dark(D, .7)
    tw, gp = 934 / 12 - 6, 6
    for i in range(12):
        tx0 = i * (tw + gp)
        on = 3 <= i <= 10
        R(s, m, tx0, -88, tx0 + tw, -40, bg if on else W, G3 if not on else A, width=.5)
        if on:
            R(s, m, tx0 + 3, -84, tx0 + 18, -44, ss.mix(A, bg, .75)); R(s, m, tx0 + 24, -80, tx0 + tw - 5, -77, A); R(s, m, tx0 + 24, -70, tx0 + tw - 5, -48, ss.mix(A, bg, .85))
        else:
            R(s, m, tx0, -88, tx0 + 7, -40, dark(F, .3)); R(s, m, tx0 + 12, -82, tx0 + tw - 5, -79, G3); R(s, m, tx0 + 12, -72, tx0 + tw - 5, -46, G1)
    T_(s, m, 200, -32, 780, -12, "White for the diagnosis, black for the deal, back to white for Q&A", 15, italic=True, color=INK)
    R(s, m, 0, 0, 934, 525, bg)
    for k in range(5):
        pts = [(i * 39 + 200, 470 + k * 8 + 12 * math.sin(i * .35 + k * .6)) for i in range(19)]
        wire(s, m, pts, ss.mix(A, bg, .78), .25)
    R(s, m, 0, 0, 203, 525, dark(D, .5))
    wire(s, m, ((203, 0), (203, 525)), ss.mix(A, bg, .5), .5)
    T_(s, m, 8, 30, 198, 60, "Structure Overview", 17, color=W, bold=True, al="l")
    steps = ((130, "3", "1st Step:\nSell-off to fund", False), (180, "4", "2nd Step:\nMerger with peer", True), (230, "5", "Acquisition", False))
    for yy, n, t, on in steps:
        if on:
            grad(R(s, m, 0, 158, 203, 208, A), ((0, A, .32), (1, A, .05)), 0)
            wire(s, m, ((0, 158), (203, 158)), A, .75); wire(s, m, ((0, 208), (203, 208)), A, .75)
        c = A if on else ss.mix(W, bg, .55)
        T_(s, m, 16, yy - 14, 44, yy + 14, n + ".", 15, color=W if on else c, bold=on)
        T_(s, m, 46, yy - 16, 200, yy + 16, t, 11, color=c, bold=on, al="l")
    for cy, head, a, b in ((322, "Pre Deal Valuation", "$ 3,317 mn", "$ 5,280 mn"), (391, "Proforma", "$ 725 mn", "$ 8,597 mn"), (460, "Exit", "$ 6,998 mn", "7.5x")):
        T_(s, m, 10, cy - 8, 194, cy + 8, head, 10, color=W, bold=True)
        for cx, v in ((55, a), (150, b)):
            T_(s, m, cx - 50, cy + 12, cx + 50, cy + 30, v, 11.5, color=A, bold=True)
            T_(s, m, cx - 50, cy + 30, cx + 50, cy + 44, "Equity Value", 8, color=W)
    R(s, m, 215, 27, 922, 65, ss.mix(A, bg, .88), ss.mix(A, bg, .4), width=.75)
    T_(s, m, 225, 28, 250, 64, "4.", 16, color=A, bold=True)
    T_(s, m, 255, 28, 915, 64, "The platform merges with a peer in a defensive move, since value lies\nin scale and shared costs rather than in the top line.", 10.5, color=ss.mix(W, bg, .25), al="l")
    box_ = lambda x0, y0, x1, y1, t, c=None: (R(s, m, x0, y0, x1, y1, ss.mix(A, bg, .85), c or ss.mix(W, bg, .55), width=.75), T_(s, m, x0, y0, x1, y1, t, 9.5, color=W))
    mold(s, m, 255, 115, 330, 140, px=9); mold(s, m, 255, 240, 330, 265, px=9)
    wire(s, m, ((297, 140), (297, 240)), W, .75)
    b_ = (275, 175, 319, 197); R(s, m, *b_, bg, W, width=.5, dash=True); T_(s, m, *b_, "100%", 8, color=W, bold=True)
    wire(s, m, ((330, 252), (360, 252)), W, .5); wire(s, m, ((360, 180), (360, 318)), W, .5)
    for yy, t, on in ((200, "Retail", False), (252, "Trading", True), (308, "Central", True)):
        wire(s, m, ((360, yy), (370, yy)), W, .5)
        box_(370, yy - 22, 430, yy + 22, t, A if on else None)
    wire(s, m, ((430, 256), (468, 256), (468, 337), (495, 337)), A, .75, dash=True)
    wire(s, m, ((430, 308), (468, 308)), A, .75, dash=True)
    R(s, m, 495, 95, 922, 243, None, ss.mix(W, bg, .55), width=.5); R(s, m, 672, 90, 748, 100, bg); T_(s, m, 660, 86, 760, 102, "1st Step", 9, italic=True, color=ss.mix(W, bg, .35))
    R(s, m, 495, 263, 922, 410, None, ss.mix(W, bg, .35), width=.5); R(s, m, 672, 258, 748, 268, bg); T_(s, m, 660, 254, 760, 270, "2nd Step", 9, italic=True, color=W)
    for yy in (132, 169, 206): box_(520, yy - 15, 632, yy + 15, "Shareholder")
    wire(s, m, ((632, 132), (672, 132)), W, .5); wire(s, m, ((632, 206), (652, 206), (652, 132)), W, .5); wire(s, m, ((632, 169), (672, 169)), W, .5)
    box_(672, 118, 780, 146, "Manager"); box_(672, 155, 780, 183, "New Fund")
    wire(s, m, ((780, 132), (800, 132), (800, 168), (820, 168)), W, .5); wire(s, m, ((780, 169), (820, 169)), W, .5)
    box_(820, 145, 905, 190, "Generation")
    for yy in (310, 365): mold(s, m, 522, yy - 18, 594, yy + 18, px=9)
    wire(s, m, ((594, 310), (682, 310), (682, 336)), A, .75); wire(s, m, ((594, 365), (682, 365), (682, 340)), A, .75)
    for yy, t in ((310, "61.4%"), (365, "38.6%")):
        b_ = (612, yy - 11, 656, yy + 11); R(s, m, *b_, bg, W, width=.5, dash=True); T_(s, m, *b_, t, 7.5, color=W, bold=True)
    box_(682, 320, 752, 358, "NewCo", A)
    wire(s, m, ((752, 339), (790, 339)), W, .5); wire(s, m, ((790, 310), (790, 365)), W, .5); wire(s, m, ((790, 310), (820, 310)), W, .5); wire(s, m, ((790, 365), (820, 365)), W, .5)
    for yy in (310, 365): mold(s, m, 820, yy - 18, 892, yy + 18, px=9)
    T_(s, m, 234, 415, 500, 430, "Transaction Structure & Key Assumptions", 9.5, color=W, bold=True, al="l")
    wire(s, m, ((234, 430), (922, 430)), W, .5)
    for i, wd in enumerate((640, 590, 660)):
        R(s, m, 248, 442 + i * 28, 248 + wd, 445 + i * 28, ss.mix(W, bg, .55))
        R(s, m, 248, 451 + i * 28, 248 + wd * .7, 454 + i * 28, ss.mix(W, bg, .55))


SLIDES = [
    ("Numbers and proof get their own device", "Phone, strips, barrel, equation and rulers replace a paragraph",
     [("Phone holding data", "Vasta p.17", phone_field), ("Headline strips", "Vibra p.39", headline_strips), ("Barrel economics", "3R Petroleum p.36", barrel_stack),
      ("Giant equation", "AB InBev p.6", equation_strip), ("Class ruler", "Arezzo&Co p.4", class_ruler), ("Logo timeline", "Arezzo&Co p.5", logo_timeline)]),
    ("Frames and strips carry the verdict", "The recommendation, the debt ladder and the price range in one line each",
     [("Verdict frame", "BTG Pactual p.2", verdict_frame), ("Hatched maturity", "CSN - ArcelorMittal p.32", maturity_strip), ("Capped stake wires", "Cosan p.20", stake_wires),
      ("Range bar", "Cosan p.12", range_bar), ("Map stems to bar", "Cury p.13", map_stems), ("Return ladder", "Cury p.31", return_ladder)]),
    ("Ratings and tables that read at a glance", "Rosettes, roundels, stars and arrows mark the state of each row",
     [("Award rosettes", "Intelbras p.43", award_panel), ("Severity roundels", "Kering - Moncler p.19", severity_table), ("Star scorecard", "Mercado Libre p.11", star_scorecard),
      ("Arrow formula", "Rede D'Or p.61", arrow_formula), ("Cohort staircase", "Sabesp p.17", cohort_stair), ("Proof tokens", "Senior Sistemas p.40", proof_tokens)]),
    ("Structures that show the terms of the deal", "Stairs, panels and frames keep the logic of each step visible",
     [("Exit triangle", "Vibra p.39", exit_triangle), ("Stair term tree", "Alupar p.22", stair_tree), ("Versus hourglass", "BTG Pactual p.41", versus_hourglass),
      ("Before and after tree", "CSN Liability p.22", ownership_flow), ("State ledger", "Cosan p.31", state_ledger), ("Thesis ladder", "Nubank p.4", thesis_ladder)]),
    ("The storyline can change the whole page", "Interruptions, risk codes and theme swaps tell the reader where they are",
     [("Question interrupt", "Nubank p.31", question_interrupt), ("Risk IDs", "Rede D'Or p.42", risk_ids), ("Risk drill-down", "Rede D'Or p.43", risk_ids_drill),
      ("Skim-layer lede", "AB InBev p.6", skim_lede), ("Brand takeover", "CSN - ArcelorMittal p.14", brand_takeover), ("Dark deal section", "Vibra p.34", dark_section)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the device comes from the source.")
    ss.save(prs, OUT)
