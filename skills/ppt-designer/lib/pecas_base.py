"""Base das peças do catálogo (references/pecas_*.py): cores por papel, mapa de coordenadas, degradês e formas.
Coordenadas em polegadas; M converte as medidas do deck de origem para a caixa da peça."""
import json
import math
from pathlib import Path

import slide_style as ss
from lxml import etree
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

D, F, A, T, W = ss.FOCUS_DARK, ss.FOCUS, ss.ACCENT, ss.FOCUS_TINT, ss.WHITE
G1, G2, G3, G4 = "F2F2F2", "D9D9D9", "BFBFBF", "7F7F7F"
INK = ss.FG
dark = lambda c, t=0.22: ss.mix(c, "000000", t)
light = lambda c, t=0.3: ss.mix(c, "FFFFFF", t)


class M:
    """Mapeia coordenadas medidas no deck de origem para a caixa do demo."""
    def __init__(self, src, box, keep=True):
        x0, y0, x1, y1 = src; x, y, w, h = box
        self.sx, self.sy = w / (x1 - x0), h / (y1 - y0)
        if keep:
            self.sx = self.sy = min(self.sx, self.sy)
        self.ox = x + (w - (x1 - x0) * self.sx) / 2 - x0 * self.sx
        self.oy = y + (h - (y1 - y0) * self.sy) / 2 - y0 * self.sy
    def p(self, q): return (self.ox + q[0] * self.sx, self.oy + q[1] * self.sy)
    def ps(self, qs): return [self.p(q) for q in qs]
    def box(self, x0, y0, x1, y1):
        a, b = self.p((x0, y0)), self.p((x1, y1))
        return a[0], a[1], b[0] - a[0], b[1] - a[1]


def grad(sp, stops, angle=0):
    sp.fill.gradient()
    gf = sp._element.spPr.find(qn("a:gradFill"))
    gl = gf.find(qn("a:gsLst"))
    for c in list(gl): gl.remove(c)
    for st in stops:
        pos, col = st[0], st[1]
        gs = etree.SubElement(gl, qn("a:gs")); gs.set("pos", str(int(pos * 100000)))
        cl = etree.SubElement(gs, qn("a:srgbClr")); cl.set("val", ss.hx(col))
        if len(st) > 2:
            al = etree.SubElement(cl, qn("a:alpha")); al.set("val", str(int(st[2] * 100000)))
    for c in gf.findall(qn("a:lin")) + gf.findall(qn("a:path")): gf.remove(c)
    li = etree.SubElement(gf, qn("a:lin")); li.set("ang", str(int(angle * 60000))); li.set("scaled", "0")
    return sp


def poly(s, m, pts, fill, alpha=None, edge=None, ew=0.5):
    sp = ss.poly(s, m.ps(pts) if m else pts, fill, edge, ew)
    if alpha is not None: ss.set_alpha(sp, alpha)
    return sp


def R(s, m, x0, y0, x1, y1, fill=None, border=None, alpha=None, width=1.0, dash=False):
    bx = m.box(x0, y0, x1, y1)
    sp = ss.rect(s, *bx, fill, border, dash, width)
    if alpha is not None: ss.set_alpha(sp, alpha)
    return sp


def rr(s, x, y, w, h, fill, adj=0.2, border=None, width=1.0):
    sp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.adjustments[0] = adj; sp.shadow.inherit = False
    if fill: ss.paint(sp.fill, fill)
    else: sp.fill.background()
    if border: sp.line.color.rgb = ss.rgb(border); sp.line.width = Pt(width)
    else: sp.line.fill.background()
    return sp


def oval(s, cx, cy, d, fill=None, h=None, border=None, width=1.0, dash=False):
    h = h or d
    sp = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - h / 2), Inches(d), Inches(h))
    sp.shadow.inherit = False
    if fill: ss.paint(sp.fill, fill)
    else: sp.fill.background()
    if border:
        sp.line.color.rgb = ss.rgb(border); sp.line.width = Pt(width)
        if dash: sp.line.dash_style = ss.MSO_LINE_DASH_STYLE.DASH
    else: sp.line.fill.background()
    return sp


def tx(s, x, y, w, h, t, size=8, color=INK, bold=False, italic=False, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, rot=None):
    tb = ss.text(s, x, y, w, h, [[(t, {"bold": bold, "italic": italic, "color": color, "size": size})]],
                 align=align, anchor=anchor, margin=0.0)
    if rot is not None: tb.rotation = rot
    return tb


def tm(s, m, x0, y0, x1, y1, t, **k):
    return tx(s, *m.box(x0, y0, x1, y1), t, **k)


def seg(c, r0, r1, a0, a1, n=24, xmin=None):
    """Segmento de anel; ângulos em graus, 0 à direita, positivo para baixo."""
    out = [(c[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    out += [(c[0] + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)), c[1] + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    if xmin is not None: out = [(max(x, xmin), y) for x, y in out]
    return out


def mini_bars(s, m, x0, y0, x1, y1, n=7, c=F):
    bw = (x1 - x0) / (n * 1.4)
    for i in range(n):
        bx = x0 + i * bw * 1.4
        R(s, m, bx, y1 - (y1 - y0) * (.3 + .7 * i / (n - 1)), bx + bw, y1, c)
    ss.line(s, *m.p((x0 - 4, y1)), *m.p((x1 + 4, y1)), G4, .5, dash=False)


def mini_lines(s, m, x0, y0, x1, y1, c=F):
    for k, (pts, col) in enumerate((((.72, .55, .62, .3, .35), light(c, .45)), ((.95, .85, .7, .68, .66), c))):
        ps = [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * v) for i, v in enumerate(pts)]
        for a, b in zip(ps, ps[1:]):
            ss.line(s, *m.p(a), *m.p(b), col, 1.5, dash=False)
    ss.line(s, *m.p((x0, y1)), *m.p((x1, y1)), G4, .5, dash=False)


def backdrop(s, m, b):
    """Slide anterior: só um fantasma de linhas, sem disputar cor com a peça."""
    R(s, m, *b, G2)
    x0, y0, x1, y1 = b
    for i in range(6):
        yy = y0 + (y1 - y0) * (.1 + i * .16)
        R(s, m, x0 + 15, yy, x1 - 15, yy + 5, G3)


def gallery(prs, layout, slides, source_note):
    """Monta slides de amostra: [(título, subtítulo, [(nome, referência, função)])], 3 colunas por 2 linhas."""
    x0, x1, y0, y1 = ss.G["content_left"] + 0.26, ss.G["content_right"], ss.G["content_top"] - 0.03, ss.G["content_bottom"] + 0.05
    gap, lab = 0.28, 0.22
    cw = (x1 - x0 - 2 * gap) / 3
    ch = (y1 - y0 - 0.14) / 2
    for title, sub_, cells in slides:
        s = prs.slides.add_slide(layout)
        ss.setup(s, title, sub_)
        for i, (name, src, fn) in enumerate(cells):
            cx = x0 + (i % 3) * (cw + gap)
            cy = y0 + (i // 3) * (ch + .14)
            ss.text(s, cx, cy, cw, lab, [[(name, {"bold": True, "color": INK, "size": 9}), ("  " + src, {"italic": True, "color": ss.MUTED, "size": 8})]], anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
            fn(s, cx, cy + lab + .03, cw, ch - lab - .05)
        ss.footer(s, source_note)


# ---------- Mapas ----------
_GEO50, _ADM1 = None, None


def countries_50m():
    """Países em 1:50m: {ISO3: {name, continent, region_wb, subregion, rings}}. Dados: Natural Earth (domínio público)."""
    global _GEO50
    if _GEO50 is None:
        _GEO50 = json.loads((Path(__file__).resolve().parent / "geo" / "countries_50m.json").read_text())
    return _GEO50


def states(iso3):
    """Estados em 1:50m: {sigla: {name, rings}}. Disponível só para RUS, USA, IND, IDN, CHN, BRA, CAN, AUS, ZAF."""
    global _ADM1
    if _ADM1 is None:
        _ADM1 = json.loads((Path(__file__).resolve().parent / "geo" / "admin1_50m.json").read_text())
    return _ADM1[iso3]


def draw_map(s, box, shapes, fill, edge=None, edge_w=0.5, keep=True, bounds=None):
    """Desenha {chave: {rings}} como formas editáveis. fill: cor, dict {chave: cor} ou função(chave) -> cor|None
    (None não desenha). Projeção equirretangular com correção de latitude. Devolve (px, py), lon/lat -> polegadas."""
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
            ss.poly(s, [(px(a), py(b)) for a, b in r], c, edge, edge_w)
    return px, py
