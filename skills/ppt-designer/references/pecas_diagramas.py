"""Diagramas do catálogo, com conteúdo fictício. Copie a função para o build do slide e troque os textos.
Referência de cada um: references/catalogo/dados/diagramas.json. O texto escala com a caixa recebida.
Uso: python3 pecas_diagramas.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402

LEFT, RIGHT, CEN = PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.CENTER
TOP = MSO_ANCHOR.TOP
NEG = ss.NEG
TINT = ss.FOCUS_TINT
DK = dark(D, .55)   # campo escuro das peças sobre fundo preto


# ---------- Ajudantes ----------

def FIT(src, box, st=1.2):
    """M que preserva a proporção da origem e cede até st vezes para ocupar a caixa."""
    x, y, w, h = box
    a = (src[2] - src[0]) / (src[3] - src[1])
    if w / h > a:
        hh, ww = h, min(w, h * a * st)
    else:
        ww, hh = w, min(h, w / a * st)
    return M(src, (x + (w - ww) / 2, y + (h - hh) / 2, ww, hh), keep=False)


def pt(m, px, lo=4.5):
    return round(max(lo, px * min(m.sx, m.sy) * 72), 1)


def T(s, m, x0, y0, x1, y1, t, px=10, c=INK, b=False, i=False, al=CEN, an=MSO_ANCHOR.MIDDLE, rot=None):
    return tx(s, *m.box(x0, y0, x1, y1), t, size=pt(m, px), color=c, bold=b, italic=i, align=al, anchor=an, rot=rot)


def RT(s, m, x0, y0, x1, y1, paras, px=10, c=INK, al=CEN, an=MSO_ANCHOR.MIDDLE):
    """paras: lista de parágrafos; cada um é lista de (texto, 'b'/'i'/'bi'/'', cor opcional)."""
    out = []
    for p in paras:
        runs = []
        for r in p:
            st = {"size": pt(m, px), "color": r[2] if len(r) > 2 else c, "bold": "b" in r[1], "italic": "i" in r[1]}
            runs.append((r[0], st))
        out.append(runs)
    return ss.text(s, *m.box(x0, y0, x1, y1), out, align=al, anchor=an, margin=0.0)


def RR(s, m, x0, y0, x1, y1, fill, adj=.2, border=None, width=1.0):
    return rr(s, *m.box(x0, y0, x1, y1), fill, adj, border, width)


def shadow(sp, blur=6, dist=2.5, alpha=30, ang=90):
    """Sombra suave nativa."""
    pr = sp._element.spPr
    for e in pr.findall(qn("a:effectLst")): pr.remove(e)
    ef = etree.SubElement(pr, qn("a:effectLst"))
    o = etree.SubElement(ef, qn("a:outerShdw"))
    o.set("blurRad", str(int(blur * 12700))); o.set("dist", str(int(dist * 12700))); o.set("dir", str(ang * 60000)); o.set("algn", "ctr"); o.set("rotWithShape", "0")
    cl = etree.SubElement(o, qn("a:srgbClr")); cl.set("val", "000000")
    a = etree.SubElement(cl, qn("a:alpha")); a.set("val", str(alpha * 1000))
    return sp


def _ends(sp, head=None, tail=None, alpha=None, sz="med"):
    ln = sp._element.spPr.find(qn("a:ln"))
    if alpha is not None:
        a = etree.SubElement(ln.find(qn("a:solidFill"))[0], qn("a:alpha")); a.set("val", str(int(alpha * 1000)))
    for tag, v in (("a:headEnd", head), ("a:tailEnd", tail)):
        if v:
            e = etree.SubElement(ln, qn(tag)); e.set("type", v); e.set("w", sz); e.set("len", sz)


def L(s, m, pts, c=INK, wd=1.0, dash=False, head=None, tail=None, alpha=None, dot=False, sz="med"):
    """Linha aberta: conector se tiver dois pontos, forma livre aberta se tiver mais. head/tail: triangle, diamond, oval."""
    q = m.ps(pts) if m else pts
    if len(q) == 2:
        sp = ss.line(s, q[0][0], q[0][1], q[1][0], q[1][1], c, wd, dash=False)
    else:
        k = [(round(a * 1000), round(b * 1000)) for a, b in q]
        fb = s.shapes.build_freeform(k[0][0], k[0][1], scale=914.4)
        fb.add_line_segments(k[1:], close=False)
        sp = fb.convert_to_shape()
        sp.shadow.inherit = False
        sp.fill.background()
        sp.line.color.rgb = ss.rgb(c); sp.line.width = Pt(wd)
    if dash: sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if dot: sp.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT
    _ends(sp, head, tail, alpha, sz)
    return sp


def fade_line(sp, stops, ang=0):
    """Traço em degradê (a:ln com gradFill)."""
    ln = sp._element.spPr.find(qn("a:ln"))
    for e in list(ln):
        if e.tag in (qn("a:solidFill"), qn("a:gradFill"), qn("a:noFill")): ln.remove(e)
    g = etree.Element(qn("a:gradFill")); gl = etree.SubElement(g, qn("a:gsLst"))
    for st in stops:
        gs = etree.SubElement(gl, qn("a:gs")); gs.set("pos", str(int(st[0] * 100000)))
        cl = etree.SubElement(gs, qn("a:srgbClr")); cl.set("val", ss.hx(st[1]))
        if len(st) > 2:
            a = etree.SubElement(cl, qn("a:alpha")); a.set("val", str(int(st[2] * 100000)))
    li = etree.SubElement(g, qn("a:lin")); li.set("ang", str(ang * 60000)); li.set("scaled", "0")
    ln.insert(0, g)
    return sp


def pattern(sp, prst, fg, bg):
    """Preenchimento de padrão nativo (ex.: narVert para régua de ticks)."""
    pr = sp._element.spPr
    for e in list(pr):
        if e.tag in (qn("a:solidFill"), qn("a:noFill"), qn("a:gradFill")): pr.remove(e)
    p = etree.Element(qn("a:pattFill")); p.set("prst", prst)
    a = etree.SubElement(p, qn("a:fgClr")); etree.SubElement(a, qn("a:srgbClr")).set("val", ss.hx(fg))
    b = etree.SubElement(p, qn("a:bgClr")); etree.SubElement(b, qn("a:srgbClr")).set("val", ss.hx(bg))
    ln = pr.find(qn("a:ln"))
    pr.insert(list(pr).index(ln) if ln is not None else len(pr), p)
    return sp


def mold(s, m, x0, y0, x1, y1, label="[logo]", px=9, fill=G2, c=G4, alpha=None, shape="rect"):
    """Molde cinza para logo, foto ou print reais."""
    if shape == "rect":
        sp = R(s, m, x0, y0, x1, y1, fill, alpha=alpha)
    else:
        sp = RR(s, m, x0, y0, x1, y1, fill, .25)
    T(s, m, x0, y0, x1, y1, label, px=px, c=c, i=True)
    return sp


def dia(s, m, cx, cy, r, fill, border=None, ew=.75):
    return poly(s, m, ((cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)), fill, edge=border, ew=ew)


def ngon(cx, cy, r, n, a0=-90):
    return [(cx + r * math.cos(math.radians(a0 + 360 * i / n)), cy + r * math.sin(math.radians(a0 + 360 * i / n))) for i in range(n)]


def disc(s, m, cx, cy, r, fill=None, border=None, width=1.0, dash=False):
    a, b = m.p((cx, cy))
    k = 2 * r * min(m.sx, m.sy)
    return oval(s, a, b, k, fill, k, border, width, dash)


def check(s, m, cx, cy, r, c, kind="check"):
    """Selo com anel: visto ou xis."""
    disc(s, m, cx, cy, r, None, c, 1.0)
    k = r * .5
    if kind == "check":
        L(s, m, [(cx - k, cy), (cx - k * .2, cy + k * .8), (cx + k, cy - k * .8)], c, 1.25)
    else:
        L(s, m, [(cx - k, cy - k), (cx + k, cy + k)], c, 1.25); L(s, m, [(cx + k, cy - k), (cx - k, cy + k)], c, 1.25)


# Ícones de linha em espaço unitário: polilinhas e, com 3 números, círculos.
_ICO = {
    "factory": [[(.05, .95), (.05, .5), (.35, .68), (.35, .5), (.62, .68), (.62, .12), (.78, .12), (.78, .68), (.95, .68), (.95, .95), (.05, .95)], [(.2, .8), (.35, .8)], [(.45, .8), (.6, .8)], [(.72, .8), (.85, .8)]],
    "cart": [[(.05, .15), (.2, .15), (.32, .65), (.82, .65), (.93, .28), (.24, .28)], (.38, .82, .07), (.74, .82, .07)],
    "truck": [[(.03, .25), (.6, .25), (.6, .72), (.03, .72), (.03, .25)], [(.6, .42), (.82, .42), (.97, .58), (.97, .72), (.6, .72)], (.25, .78, .08), (.78, .78, .08)],
    "store": [[(.1, .42), (.1, .92), (.9, .92), (.9, .42)], [(.05, .42), (.15, .1), (.85, .1), (.95, .42), (.05, .42)], [(.3, .1), (.25, .42)], [(.5, .1), (.5, .42)], [(.7, .1), (.75, .42)], [(.2, .92), (.2, .58), (.42, .58), (.42, .92)], [(.55, .58), (.8, .58), (.8, .78), (.55, .78), (.55, .58)]],
    "people": [(.5, .3, .15), [(.25, .92), (.25, .72), (.35, .55), (.65, .55), (.75, .72), (.75, .92), (.25, .92)], (.17, .42, .1), (.83, .42, .1), [(.03, .85), (.03, .68), (.1, .57), (.25, .57)], [(.97, .85), (.97, .68), (.9, .57), (.75, .57)]],
    "person": [(.5, .28, .18), [(.18, .92), (.18, .72), (.32, .55), (.68, .55), (.82, .72), (.82, .92), (.18, .92)]],
    "phone": [[(.28, .05), (.72, .05), (.72, .95), (.28, .95), (.28, .05)], [(.28, .18), (.72, .18)], [(.28, .8), (.72, .8)], [(.45, .88), (.55, .88)]],
    "doc": [[(.2, .05), (.62, .05), (.82, .25), (.82, .95), (.2, .95), (.2, .05)], [(.62, .05), (.62, .25), (.82, .25)], [(.32, .45), (.7, .45)], [(.32, .6), (.7, .6)], [(.32, .75), (.6, .75)]],
    "chart": [[(.08, .08), (.08, .92), (.95, .92)], [(.25, .92), (.25, .62)], [(.45, .92), (.45, .48)], [(.65, .92), (.65, .55)], [(.85, .92), (.85, .3)], [(.2, .42), (.42, .28), (.6, .35), (.88, .08)]],
    "bank": [[(.05, .35), (.5, .08), (.95, .35), (.05, .35)], [(.08, .92), (.92, .92)], [(.2, .42), (.2, .82)], [(.4, .42), (.4, .82)], [(.6, .42), (.6, .82)], [(.8, .42), (.8, .82)], [(.1, .82), (.9, .82)]],
    "coin": [(.5, .5, .42), [(.62, .34), (.4, .34), (.36, .48), (.62, .52), (.6, .66), (.36, .66)], [(.5, .24), (.5, .76)]],
    "card": [[(.05, .22), (.95, .22), (.95, .8), (.05, .8), (.05, .22)], [(.05, .38), (.95, .38)], [(.15, .62), (.4, .62)]],
    "globe": [(.5, .5, .43), [(.07, .5), (.93, .5)], [(.5, .07), (.32, .3), (.28, .5), (.32, .7), (.5, .93)], [(.5, .07), (.68, .3), (.72, .5), (.68, .7), (.5, .93)]],
    "link": [[(.18, .35), (.4, .13), (.6, .33), (.38, .55), (.18, .35)], [(.4, .65), (.62, .43), (.82, .63), (.6, .85), (.4, .65)]],
    "net": [(.5, .5, .13), (.18, .2, .09), (.82, .2, .09), (.15, .75, .09), (.85, .75, .09), (.5, .9, .07), [(.25, .26), (.41, .41)], [(.75, .26), (.59, .41)], [(.22, .71), (.39, .57)], [(.78, .71), (.61, .57)], [(.5, .63), (.5, .83)]],
    "cash": [[(.05, .25), (.95, .25), (.95, .75), (.05, .75), (.05, .25)], (.5, .5, .14), [(.17, .5), (.25, .5)], [(.75, .5), (.83, .5)]],
    "target": [(.5, .5, .42), (.5, .5, .25), (.5, .5, .07), [(.5, .5), (.92, .1)]],
    "funnel": [[(.08, .12), (.92, .12), (.6, .5), (.6, .88), (.4, .78), (.4, .5), (.08, .12)]],
    "cloud": [[(.25, .72), (.1, .65), (.08, .5), (.2, .4), (.28, .25), (.45, .2), (.6, .28), (.75, .32), (.82, .45), (.93, .55), (.88, .7), (.75, .72)], [(.5, .85), (.5, .48)], [(.38, .6), (.5, .48), (.62, .6)]],
    "gear": [(.5, .5, .3), (.5, .5, .12), [(.5, .08), (.5, .2)], [(.5, .8), (.5, .92)], [(.08, .5), (.2, .5)], [(.8, .5), (.92, .5)], [(.2, .2), (.29, .29)], [(.71, .71), (.8, .8)], [(.8, .2), (.71, .29)], [(.29, .71), (.2, .8)]],
    "syringe": [[(.72, .1), (.9, .28)], [(.81, .19), (.68, .32)], [(.32, .5), (.6, .24), (.76, .4), (.5, .68), (.32, .5)], [(.41, .59), (.12, .88)]],
    "flask": [[(.38, .08), (.62, .08)], [(.42, .08), (.42, .38), (.15, .85), (.2, .93), (.8, .93), (.85, .85), (.58, .38), (.58, .08)], [(.28, .64), (.72, .64)]],
    "pill": [[(.15, .55), (.45, .25), (.6, .15), (.78, .2), (.85, .4), (.8, .5), (.5, .8), (.32, .88), (.17, .8), (.15, .55)], [(.32, .38), (.65, .66)]],
    "shield": [[(.5, .06), (.88, .2), (.88, .5), (.72, .78), (.5, .94), (.28, .78), (.12, .5), (.12, .2), (.5, .06)], [(.32, .5), (.46, .64), (.7, .36)]],
    "bolt": [[(.6, .05), (.25, .55), (.48, .55), (.38, .95), (.75, .42), (.52, .42), (.6, .05)]],
    "cube": [[(.5, .08), (.88, .28), (.88, .72), (.5, .92), (.12, .72), (.12, .28), (.5, .08)], [(.12, .28), (.5, .48), (.88, .28)], [(.5, .48), (.5, .92)]],
}


def ico(s, m, cx, cy, d, kind, c=F, wd=.75):
    """Ícone de linha desenhado com formas nativas; d é o lado na escala de origem."""
    x0, y0 = cx - d / 2, cy - d / 2
    for pr in _ICO[kind]:
        if isinstance(pr, tuple):
            disc(s, m, x0 + pr[0] * d, y0 + pr[1] * d, pr[2] * d, None, c, wd)
        else:
            L(s, m, [(x0 + a * d, y0 + b * d) for a, b in pr], c, wd)


def halo(s, m, cx, cy, r, kind, tint=None, c=F, wd=.75):
    disc(s, m, cx, cy, r, tint or light(F, .85))
    ico(s, m, cx, cy, r * 1.25, kind, c, wd)


def arc(c, r, a0, a1, n=24):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ---------- Portfólio e resumo ----------

def core_rings(s, x, y, w, h):
    """Dois anéis empilhados com cubo e linhas finas abrindo em leque até notas de produto. Senior p.14."""
    m = FIT((0, 0, 468, 480), (x, y, w, h), 1.3)
    def card(x0, y0, x1, y1, t, b):
        R(s, m, x0, y0, x1, y1, G1)
        T(s, m, x0, y0 + 4, x1, y0 + 26, t, px=12, c=F, b=True)
        T(s, m, x0 + 8, y0 + 26, x1 - 8, y1 - 4, b, px=9, c=INK, an=TOP, al=LEFT)
    for yy, t1, t2 in ((25, "Product A", "Product C"), (178, "Product B", "Product D")):
        card(18, yy, 152, yy + 92, t1, "Short note on what this line does for the client.")
        card(339, yy, 468, yy + 92, t2, "Short note on what this line does for the client.")
    card(18, 335, 152, 447, "Product E", "Newer line, joint offer that opens a second source of revenue.")
    card(339, 335, 468, 447, "Product F", "Newer line, sold on top of the installed client base.")
    for a, b in (((191, 128), (153, 70)), ((191, 178), (153, 225)), ((301, 128), (338, 70)), ((301, 178), (338, 225))):
        L(s, m, [a, b], F, .75, dash=True)
    for xa, xb in ((190, 153), (302, 338)):
        L(s, m, [(xa, 389), (xb, 389)], F, .75, dash=True)
    def wire(cx, cy, r, c, wd):
        P = ngon(cx, cy, r, 6)
        L(s, m, P + [P[0]], c, wd)
        for k in (1, 3, 5):
            L(s, m, [(cx, cy), P[k]], c, wd)
    T(s, m, 186, 66, 306, 92, "Core", px=15, c=F, b=True)
    disc(s, m, 246, 153, 57, None, F, .75, True)
    disc(s, m, 246, 153, 44, G2)
    wire(246, 153, 36, G4, 2.0)
    disc(s, m, 246, 153, 15, F)
    T(s, m, 176, 306, 316, 332, "Near Core", px=15, c=F, b=True)
    disc(s, m, 246, 389, 57, None, F, .75, True)
    disc(s, m, 246, 389, 22, G3)
    wire(246, 389, 38, F, 2.0)


def pentagon_field(s, x, y, w, h):
    """Campo tintado em pentágono apontando para a tese à direita; fatos dentro, Entry/Exit/Risks fora. Vasta p.3."""
    m = FIT((0, 0, 510, 244), (x, y, w, h), 1.2)
    poly(s, m, ((0, 14), (258, 14), (292, 118), (258, 224), (0, 224)), light(F, .9))
    T(s, m, 90, 16, 210, 30, "Highlights", px=9, b=True)
    T(s, m, 60, 29, 245, 40, "Investment: entry year to exit year", px=6, c=G4, i=True)
    T(s, m, 30, 38, 74, 50, "Returns:", px=7, b=True)
    T(s, m, 30, 52, 74, 76, "IRR", px=6)
    T(s, m, 30, 62, 74, 78, "28.9%", px=8, b=True)
    L(s, m, [(52, 82), (52, 182)], F, 1.0)
    dia(s, m, 52, 82, 4, F); dia(s, m, 52, 182, 4, F)
    R(s, m, 32, 124, 72, 140, light(F, .9))
    T(s, m, 30, 124, 74, 140, "6 years", px=6, c=G4)
    T(s, m, 30, 187, 74, 212, "2.7x MOIC", px=7, b=True)
    for x0, x1, ti, a, b, va, vb in ((80, 158, "EV/EBITDA", "Entry", "Exit", "8.1x", "7.3x"), (170, 248, "Deal structure", "Offer", "Stake", "$876m", "15.0%")):
        T(s, m, x0, 40, x1, 52, ti, px=7, b=True)
        shadow(RR(s, m, x0, 53, x1, 98, W, .12))
        L(s, m, [((x0 + x1) / 2, 57), ((x0 + x1) / 2, 94)], G3, .5)
        for k, (la, va_) in enumerate(((a, va), (b, vb))):
            xa = x0 + k * (x1 - x0) / 2
            T(s, m, xa, 57, xa + (x1 - x0) / 2, 72, la, px=6, i=True)
            T(s, m, xa, 76, xa + (x1 - x0) / 2, 92, va_, px=7, b=True)
    for yy, ti, a, b in ((116, "Investment Thesis", "I. A portfolio built to stick", "II. Safe and predictable model"), (168, "Value Creation Plan", "I. Regional expansion", "II. Add-on acquisition")):
        T(s, m, 80, yy, 250, yy + 13, ti, px=7, b=True)
        L(s, m, [(105, yy + 15), (225, yy + 15)], F, 1.0)
        T(s, m, 80, yy + 18, 250, yy + 29, a, px=6); T(s, m, 80, yy + 28, 250, yy + 39, b, px=6)
    T(s, m, 340, 26, 470, 40, "Rationale", px=9, b=True)
    def head(yy, t):
        dia(s, m, 293, yy, 3, F)
        T(s, m, 300, yy - 7, 360, yy + 7, t, px=8, b=True, al=LEFT)
    def cards(y0, y1, xs, ti):
        for (x0, x1), t in zip(xs, ti):
            shadow(RR(s, m, x0, y0, x1, y1, W, .12, G3, .5), 3, 1, 20)
            RT(s, m, x0 + 4, y0 + 2, x1 - 4, y1 - 2, [[(t[0], "b")], [(t[1], "")]], px=5.5, al=LEFT)
    head(44, "Entry")
    cards(55, 98, ((290, 356), (361, 427), (432, 498)), (("Trigger", "Seller left the listed market"), ("Timing", "Parent is deleveraging"), ("Price", "Funds plus add-on at a low multiple")))
    head(108, "Exit")
    cards(120, 172, ((290, 392), (397, 498)), (("Buyback by parent", "Contractual path, return on floor multiple"), ("Secondary sale", "Financial buyers active in the niche")))
    head(180, "Risks")
    cards(188, 212, ((290, 356), (361, 427), (432, 498)), (("Integration", "-4.9% IRR"), ("Churn", "-4.8% IRR"), ("Macro", "-3.5% IRR")))


def capsule_columns(s, x, y, w, h):
    """Cápsulas altas com disco de ícone no topo e pilha de logos embaixo, mais faixa de rodapé. Vasta p.12."""
    m = FIT((0, 0, 510, 397), (x, y, w, h), 1.25)
    cols = ((23, 110, F, "bank", "Core Line", "Quality and breadth"), (119, 205, dark(F, .3), "chart", "Digital Platforms", "Innovation"),
            (215, 300, light(F, .55), "net", "Add-ons", "Stickiness"), (311, 396, A, "globe", "Premium Line", "Premium and reach"), (406, 493, G4, "coin", "Back Office", "Efficiency and retention"))
    for x0, x1, c, ic, t, d_ in cols:
        cx = (x0 + x1) / 2
        RR(s, m, x0, 30, x1, 295, W, .28, c, 1.0)
        disc(s, m, cx, 32, 28, W, G2, .75)
        disc(s, m, cx, 32, 21, c)
        ico(s, m, cx, 32, 26, ic, W, .75)
        T(s, m, x0 + 3, 64, x1 - 3, 96, t, px=9.5, b=True)
        T(s, m, x0 + 6, 100, x1 - 6, 128, d_, px=7.5, i=True)
        L(s, m, [(x0 + 10, 137), (x1 - 10, 137)], c, 1.25)
        for k in range(3):
            mold(s, m, x0 + 13, 150 + k * 46, x1 - 13, 186 + k * 46, px=8)
    shadow(RR(s, m, 23, 312, 493, 392, light(F, .9), .22, light(F, .6), .75), 4, 1.5, 20)
    disc(s, m, 62, 352, 27, W, G2, .75); disc(s, m, 62, 352, 21, F); ico(s, m, 62, 352, 26, "bank", W, .75)
    T(s, m, 94, 322, 160, 345, "New line", px=11, c=F, b=True)
    T(s, m, 94, 347, 160, 382, "Public-private alliances", px=7.5, i=True)
    L(s, m, [(166, 324), (166, 382)], G3, .5)
    RT(s, m, 172, 322, 318, 384, [[("A ", ""), ("natural hedge", "b"), (" against the private sector, in a market ", ""), ("rivals skip", "b")]], px=8.5)
    bra = {"BRA": countries_50m()["BRA"]}
    draw_map(s, m.box(322, 318, 396, 386), bra, W, F, .75)
    RT(s, m, 400, 330, 490, 374, [[("Public TAM:", "bi")], [("$460bn", "i")]], px=9)


def option_chain(s, x, y, w, h):
    """Quatro pílulas sobre cartões de contorno com chip de valor; a cor esmaece com a condicionalidade. Vasta p.25."""
    m = FIT((0, 0, 510, 150), (x, y, w, h), 1.35)
    data = ((15, 115, F, "Now", "Region A", "base investment", "$63.3m"), (135, 240, light(F, .4), "If A validates", "Region B", "call option", "$48.4m"),
            (260, 362, A, "If B validates", "Region C", "compound option", "$20.8m"), (383, 486, G3, "Separate option", "Region D", "M&A / deep OTM option", "$129.3m"))
    for x0, x1, c, p, t, d_, v in data:
        RR(s, m, x0, 44, x1, 145, W, .14, c, 1.25)
        cx = (x0 + x1) / 2
        shadow(RR(s, m, cx - 40, 6, cx + 40, 42, c, .32), 4, 1.5, 25)
        T(s, m, cx - 37, 6, cx + 37, 42, p, px=9.5, c=W)
        T(s, m, x0 + 4, 54, x1 - 4, 74, t, px=11, c=c, b=True)
        T(s, m, x0 + 8, 76, x1 - 8, 110, d_, px=9, i=True)
        RR(s, m, x0 + 8, 116, x1 - 8, 138, c, .25)
        T(s, m, x0 + 8, 116, x1 - 8, 138, v, px=10, c=W, b=True)


def staged_deal(s, x, y, w, h):
    """Três colunas de etapas numeradas sobre escuro, chevrons finos e painel final de estrutura. Vibra p.37."""
    m = FIT((0, 0, 510, 206), (x, y, w, h), 1.15)
    N = light(A, .15)
    R(s, m, 0, 0, 510, 206, DK)
    def col(x0, x1):
        sp = R(s, m, x0, 10, x1, 198, D, border=N, width=1.0)
        grad(sp, ((0, dark(D, .45)), (.75, dark(D, .35)), (1, F)), 90)
    def stat(x0, x1, yy, v, l):
        T(s, m, x0, yy, x1, yy + 11, v, px=8, c=N, b=True)
        T(s, m, x0, yy + 10, x1, yy + 19, l, px=4.5, c=W)
    def hd(x0, x1, yy, t):
        T(s, m, x0 + 4, yy, x1 - 4, yy + 16, t, px=5.5, c=W, b=True)
    col(13, 95); hd(13, 95, 12, "1. Fund enters")
    stat(13, 95, 32, "13.3%", "Initial stake"); stat(13, 95, 58, "$5.8bn", "Initial equity")
    hd(13, 95, 84, "2. New block")
    for yy, t in ((108, "Seat A"), (122, "Seat B")):
        R(s, m, 26, yy, 82, yy + 11, None, border=N, width=.5, dash=True); T(s, m, 26, yy, 82, yy + 11, t, px=4.5, c=W)
    stat(13, 95, 150, "23.3%", "Block stake")
    col(125, 210); hd(125, 210, 12, "3. First step: spin-off")
    stat(125, 210, 32, "14.0%", "Holder IRR"); stat(125, 210, 58, "18.1%", "Premium paid")
    hd(125, 210, 84, "4. Second step: merger")
    stat(125, 210, 104, "$7.0bn", "Exit value")
    for a0, a1, c in ((-90, 50, N), (50, 270, dark(N, .45))):
        poly(s, m, seg((167, 160), 10, 20, a0, a1), c)
    T(s, m, 125, 182, 210, 194, "NewCo cap table", px=4.5, c=W)
    col(240, 327); hd(240, 327, 12, "5. Acquisition")
    for k, t in enumerate(("32% cash", "27% bridge", "41% fund cash")):
        R(s, m, 252, 30 + k * 11, 315, 40 + k * 11, None, border=N, width=.5); T(s, m, 252, 30 + k * 11, 315, 40 + k * 11, t, px=4.5, c=W)
    stat(240, 327, 66, "$4.5bn", "Second investment")
    hd(240, 327, 92, "6. Share swap")
    stat(243, 285, 114, "29.9%", "NewCo"); stat(285, 325, 114, "8.7%", "Parent")
    T(s, m, 250, 150, 318, 180, "Average-price structure leaves more risk to the fund", px=4.5, c=W)
    for cx in (110, 225):
        L(s, m, [(cx - 4, 95), (cx + 4, 104), (cx - 4, 113)], W, .75)
    R(s, m, 353, 10, 505, 198, None, border=W, width=.75)
    T(s, m, 353, 16, 505, 32, "Final Structure", px=6.5, c=W, b=True)
    def bx(x0, y0, x1, y1, t, fill=None):
        R(s, m, x0, y0, x1, y1, fill or dark(F, .5), border=N, width=.5); T(s, m, x0, y0, x1, y1, t, px=4.5, c=W)
    bx(366, 50, 402, 64, "Others"); bx(410, 50, 446, 64, "Fund"); bx(454, 50, 492, 64, "[logo]", G4)
    for cx, v in ((384, "68.0%"), (428, "22.0%"), (473, "9.0%")):
        T(s, m, cx - 18, 65, cx + 18, 75, v, px=4.5, c=W)
        L(s, m, [(cx, 76), (cx, 84), (428, 84)], N, .5)
    L(s, m, [(428, 84), (428, 108)], N, .5)
    bx(404, 108, 452, 126, "[logo]", G4)
    L(s, m, [(428, 126), (428, 138)], N, .5); L(s, m, [(396, 150), (396, 138), (462, 138), (462, 150)], N, .5)
    T(s, m, 398, 139, 426, 149, "38.6%", px=4.5, c=W, al=LEFT); T(s, m, 464, 139, 492, 149, "100%", px=4.5, c=W, al=LEFT)
    bx(374, 150, 418, 170, "Unit A"); bx(440, 150, 484, 170, "Unit B")


def treemap_zoom(s, x, y, w, h):
    """Mosaico com um bloco gigante e fatias estreitas que abrem, por uma parede, em um segundo mosaico. 3R p.5."""
    m = FIT((40, 0, 900, 184), (x, y, w, h), 1.6)
    R(s, m, 40, 0, 450, 184, G1)
    R(s, m, 45, 8, 49, 36, F)
    T(s, m, 54, 6, 440, 22, "Market share by production", px=12, b=True, al=LEFT)
    T(s, m, 54, 22, 440, 36, "The incumbent is by far the largest player", px=9.5, al=LEFT)
    R(s, m, 53, 52, 403, 176, D)
    grad(R(s, m, 198, 70, 275, 138, light(D, .28)), ((0, light(D, .28)), (1, light(D, .14))), 90)
    T(s, m, 198, 70, 275, 138, "[logo]", px=11, c=W, i=True)
    T(s, m, 57, 160, 110, 174, "93.5%", px=9, c=W)
    poly(s, m, ((427, 52), (494, 30), (494, 184), (427, 176)), G2)
    R(s, m, 405, 52, 427, 121, dark(F, .3)); T(s, m, 381, 76, 451, 98, "[logo]", px=7, c=W, i=True, rot=-90)
    R(s, m, 405, 123, 427, 151, light(F, .35)); R(s, m, 405, 153, 427, 176, A)
    R(s, m, 494, 30, 718, 184, dark(F, .3)); T(s, m, 494, 30, 718, 184, "[logo]", px=14, c=W, i=True)
    T(s, m, 498, 166, 560, 182, "57.1%", px=9, c=W)
    R(s, m, 721, 30, 816, 184, light(F, .35)); T(s, m, 721, 30, 816, 184, "[logo]", px=11, c=W, i=True)
    T(s, m, 724, 166, 780, 182, "26.6%", px=9, c=W)
    R(s, m, 819, 30, 890, 169, A); T(s, m, 819, 30, 890, 150, "[logo]", px=10, c=W, i=True)
    T(s, m, 822, 150, 870, 167, "16.0%", px=9, c=W)
    R(s, m, 819, 171, 890, 184, TINT)


def lifecycle(s, x, y, w, h):
    """Silhueta em degraus em torno do eixo de caixa, dois donos em duas cores e chave de fases. 3R p.5."""
    m = FIT((40, 40, 850, 215), (x, y, w, h), 1.5)
    c1, c2 = F, D
    T(s, m, 110, 46, 265, 66, "Incumbent focus", px=12, c=c1, b=True)
    T(s, m, 410, 46, 580, 66, "Niche focus", px=12, c=c2, b=True)
    L(s, m, [(85, 96), (85, 201)], INK, 1.25, head="triangle", tail="triangle")
    R(s, m, 78, 144, 92, 150, W)
    T(s, m, 32, 134, 112, 158, "Cash flow", px=10, rot=-90)
    poly(s, m, ((93, 150), (140, 150), (140, 162), (164, 162), (164, 201), (140, 201), (140, 187), (116, 187), (116, 162), (93, 162)), c1)
    T(s, m, 96, 150, 112, 162, "2", px=8, c=W, b=True); T(s, m, 120, 150, 138, 162, "3", px=8, c=W, b=True)
    R(s, m, 188, 88, 283, 151, c1)
    poly(s, m, ((283, 88), (331, 88), (331, 138), (355, 138), (355, 63), (378, 63), (378, 75), (401, 75), (401, 88), (425, 88), (425, 100), (448, 100), (448, 113), (472, 113), (472, 125), (497, 125), (497, 138), (568, 138), (568, 151), (283, 151)), c2)
    L(s, m, [(283, 74), (283, 164)], light(F, .35), 1.0)
    for xx, t in ((212, "4"), (322, "5"), (386, "6")):
        T(s, m, xx - 8, 138, xx + 8, 151, t, px=8, c=W, b=True)
    for k, (t1, t2) in enumerate((("1", "Exploration"), ("2", "Appraisal"), ("3", "Development"), ("4", "Production"))):
        yy = 47 + k * 39.5
        RR(s, m, 606, yy, 708, yy + 36, c1, .18)
        RT(s, m, 606, yy, 708, yy + 36, [[(t1, "b", W)], [(t2, "", W)]], px=9.5)
    for y0, y1, t1, t2 in ((47, 120, "5", "Redevelopment"), (125, 202, "6", "Production recovery")):
        RR(s, m, 715, y0, 836, y1, c2, .15)
        RT(s, m, 719, y0, 832, y1, [[(t1, "b", W)], [(t2, "", W)]], px=9.5)


def spine_banners(s, x, y, w, h):
    """Espinha vertical em painel cinza com bandeiras em cauda de andorinha alternadas. 3R p.24."""
    m = FIT((0, 0, 469, 480), (x, y, w, h), 1.35)
    R(s, m, 34, 11, 451, 447, F); R(s, m, 28, 5, 445, 442, "ECEEF4")
    R(s, m, 140, 17, 338, 50, light(F, .8))
    T(s, m, 140, 17, 338, 50, "Financing History", px=18, c=D, b=True)
    L(s, m, [(238, 60), (238, 418)], INK, 1.5)
    disc(s, m, 238, 60, 6, INK); disc(s, m, 238, 416, 6, INK)
    data = ((80, True, D, "Q4 Y1", "$690m", "IPO", "North cluster"), (137, False, D, "Q2 Y2", "$822m", "Follow-on", "East cluster"),
            (193, True, D, "Q4 Y2", "$2.1bn", "Follow-on", "South cluster"), (250, False, F, "Q3 Y3", "$900m", "Debenture", "South cluster"))
    for yy, right, c, q, a, b, d_ in data:
        if right:
            poly(s, m, ((240, yy), (425, yy), (410, yy + 16), (425, yy + 32), (240, yy + 32)), c)
            T(s, m, 250, yy, 400, yy + 32, q, px=15, c=W, b=True, al=LEFT)
            RT(s, m, 250, yy + 36, 430, yy + 78, [[(a, "b", F), (" - " + b, "b")], [(d_, "b")]], px=13, al=LEFT)
        else:
            poly(s, m, ((236, yy), (50, yy), (65, yy + 16), (50, yy + 32), (236, yy + 32)), c)
            T(s, m, 80, yy, 226, yy + 32, q, px=15, c=W, b=True, al=RIGHT)
            RT(s, m, 50, yy + 36, 226, yy + 78, [[(a, "b", F), (" - " + b, "b")], [(d_, "b")]], px=13, al=RIGHT)
    poly(s, m, ((240, 306), (425, 306), (410, 322), (425, 338), (240, 338)), light(F, .55))
    T(s, m, 250, 306, 400, 338, "Q2 Y4", px=15, c=W, b=True, al=LEFT)
    RT(s, m, 250, 342, 435, 398, [[("$5.1bn", "b", F), (" - Debenture", "b")], [("$900m", "b", F), (" - Follow-on", "b")], [("$2.5bn", "b", F), (" - Loan", "b")]], px=12, al=LEFT)
    T(s, m, 250, 402, 440, 430, "All acquisitions + ops.", px=12, b=True, al=LEFT)


def radar_badges(s, x, y, w, h):
    """Radar de fios com um polígono e selos pentagonais numerados, repetidos numa lista à direita. 3R p.101."""
    m = FIT((0, 0, 510, 271), (x, y, w, h), 1.15)
    c = (123, 145)
    for r in (12, 24, 36, 48, 60):
        P = ngon(*c, r, 5); L(s, m, P + [P[0]], G4, .5)
    for pp in ngon(*c, 60, 5): L(s, m, [c, pp], G3, .35)
    vals = (.7, .4, .28, .66, .75)
    P = [(c[0] + 60 * v * math.cos(math.radians(-90 + 72 * i)), c[1] + 60 * v * math.sin(math.radians(-90 + 72 * i))) for i, v in enumerate(vals)]
    L(s, m, P + [P[0]], F, 1.25)
    for i, (bx, by) in enumerate(ngon(*c, 84, 5)):
        poly(s, m, ngon(bx, by, 14, 5), D)
        T(s, m, bx - 12, by - 9, bx + 12, by + 10, str(i + 1), px=9, c=W)
    poly(s, m, ((483, 23), (490, 30), (490, 247), (483, 253)), G3)
    R(s, m, 263, 28, 483, 250, G1)
    R(s, m, 263, 23, 483, 31, D); poly(s, m, ((263, 23), (270, 19), (490, 19), (483, 23)), light(D, .3))
    R(s, m, 263, 247, 483, 253, D)
    items = (("Rivalry among competitors: 2", "Rivalry has little influence, it only matters when assets are auctioned."),
             ("New entrants: 1", "Capital and know-how needed keep the door mostly closed."),
             ("Power of suppliers: 1", "Suppliers serve many players, with low bargaining power."),
             ("Power of buyers: 3", "Output is sold in volume to large groups that ask for discounts."),
             ("Substitutes: 3", "The energy transition will not change the medium term."))
    for i, (t, d_) in enumerate(items):
        yy = 54 + i * 44
        poly(s, m, ngon(290, yy, 13, 5), D)
        T(s, m, 278, yy - 8, 302, yy + 10, str(i + 1), px=8, c=W)
        T(s, m, 310, yy - 19, 478, yy - 7, t, px=7, b=True, al=LEFT)
        T(s, m, 310, yy - 7, 478, yy + 20, d_, px=6, al=LEFT, an=TOP)


def phase_area(s, x, y, w, h):
    """Colunas de fase sobre área de benefício e curva de esforço, com marcador de kickoff. AB InBev p.81."""
    m = FIT((0, 0, 510, 235), (x, y, w, h), 1.25)
    R(s, m, 0, 0, 32, 235, "3A3A3A")
    T(s, m, -40, 180, 72, 212, "Workstream", px=11, c=W, rot=-90)
    cols = ((42, 147, "DESIGN", "0-4 months"), (158, 262, "PILOT AND WINS", "3-12 months"), (276, 380, "ROLLOUT", "12-30 months"), (394, 498, "SUSTAIN", "30-48 months"))
    for x0, x1, t, d_ in cols:
        R(s, m, x0, 6, x1, 30, "3A3A3A"); T(s, m, x0, 6, x1, 30, t, px=7.5, c=W)
        L(s, m, [(x0 + 12, 46), (x1 - 12, 46)], INK, .5, head="triangle", tail="triangle", sz="sm")
        T(s, m, x0, 32, x1, 43, d_, px=5)
    poly(s, m, ((43, 112), (195, 108), (348, 54), (500, 52), (500, 128), (43, 128)), A)
    cv = [(xx, 58 + 67 / (1 + math.exp(-(xx - 280) / 26))) for xx in range(68, 501, 12)]
    L(s, m, cv, INK, 1.0)
    poly(s, m, ((100, 118), (106, 108), (112, 118)), INK)
    T(s, m, 80, 84, 132, 107, "Formal kickoff", px=5.5)
    R(s, m, 50, 133, 56, 139, A)
    T(s, m, 60, 130, 200, 142, "Programme benefits", px=5, al=LEFT)
    L(s, m, [(180, 136), (225, 136)], INK, .5, tail="triangle")
    T(s, m, 232, 130, 380, 142, "Magnitude of the effort", px=5, al=LEFT)
    bl = (("Set the mandate from the top and show the need for change", "Set up a transformation office and cadence"),
          ("Shift ownership of the change from the bottom up", "Celebrate early wins and unlock constraints"),
          ("Deepen the cultural principles behind the change", "Understand what generates commitment"),
          ("Establish controls that deliver the promised result", "Build long-term capabilities"))
    for (x0, x1, _, _), bs in zip(cols, bl):
        T(s, m, x0 + 2, 150, x1 - 2, 184, bs[0], px=5.5, al=LEFT, an=TOP)
        T(s, m, x0 + 2, 188, x1 - 2, 222, bs[1], px=5.5, al=LEFT, an=TOP)
    for xx in (153, 269, 387):
        L(s, m, [(xx, 150), (xx, 225)], G4, .5)


def long_short_chain(s, x, y, w, h):
    """Cadeia longa sobre cadeia curta na mesma largura, para mostrar a saída do intermediário. AB InBev p.101."""
    m = FIT((0, 68, 510, 395), (x, y, w, h), 1.25)
    R(s, m, 3, 70, 495, 395, G1)
    L(s, m, [(3, 70), (3, 395)], INK, .5, dash=True)
    def row(yl, yi, items, chev, note):
        T(s, m, 16, yl - 9, 160, yl + 9, "Traditional route" if len(items) > 3 else "Direct route", px=11, i=True, al=LEFT)
        for cx, k, t in items:
            ico(s, m, cx, yi, 42, k, INK, .75)
            T(s, m, cx - 40, yi + 24, cx + 40, yi + 39, t, px=8.5)
        for cx in chev:
            L(s, m, [(cx - 6, yi - 11), (cx + 6, yi), (cx - 6, yi + 11)], INK, .75)
        RT(s, m, 20, yi + 45, 470, yi + 77, [[("Each step ", "", G4), ("adds a margin", "", A), (" on the way, and only a ", "", G4), ("few players", "", A), (" keep a good share of the ", "", G4), ("final price", "", A), (".", "", G4)]], px=9.5, al=LEFT)
    row(88, 140, ((42, "factory", "Maker"), (130, "cart", "Wholesaler"), (215, "truck", "Distributor"), (295, "store", "Retailer"), (373, "people", "Consumer")), (88, 174, 256, 335), 0)
    row(252, 305, ((42, "factory", "Maker"), (205, "phone", "Website"), (373, "people", "Consumer")), (125, 290), 0)


def twin_verdict(s, x, y, w, h):
    """Duas cadeias verticais de blocos com sombra dura e linhas de veredito com visto ou xis. BTG p.35."""
    m = FIT((0, 0, 510, 224), (x, y, w, h), 1.25)
    def tile(x0, y0, t, ic, c):
        R(s, m, x0 + 3, y0 + 3, x0 + 78, y0 + 39, G4)
        R(s, m, x0, y0, x0 + 75, y0 + 36, c)
        ico(s, m, x0 + 37, y0 + 13, 17, ic, INK, .5)
        T(s, m, x0, y0 + 22, x0 + 75, y0 + 35, t, px=6, b=True)
    def top(x0, a, b, c):
        mold(s, m, x0, 18, x0 + 58, 36, px=7)
        L(s, m, [(x0 + 60, 27), (x0 + 88, 27)], INK, .5, tail="diamond")
        RT(s, m, x0 + 97, 12, x0 + 225, 42, [[(a, "b", c), (b, "")]], px=7, al=LEFT)
    top(13, "Strong incentive", " to offer full services", F)
    top(264, "Little incentive", " via commission to offer more services", A)
    for k, (t, ic) in enumerate((("Company", "bank"), ("Adviser", "person"), ("Bank", "bank"))):
        y0 = 48 + k * 63
        tile(13, y0, t, ic, light(F, .85))
        tile(264, y0, t, ic, G1)
    for yy in (88, 151):
        L(s, m, [(50, yy - 1), (50, yy + 21)], INK, .75, head="triangle", tail="triangle", sz="sm")
    L(s, m, [(301, 87), (301, 97), (346, 97), (346, 111)], INK, .75)
    L(s, m, [(346, 145), (346, 160), (301, 160), (301, 172)], INK, .75)
    for yy, a, b in ((48, "Tightens the relationship", " with the adviser"), (111, "Greater service", " offerings to clients"), (174, "Raises reach", " in the middle market")):
        R(s, m, 100, yy, 226, yy + 34, light(F, .88))
        check(s, m, 113, yy + 17, 8, F)
        RT(s, m, 126, yy + 2, 224, yy + 32, [[(a, "b", F), (b, "")]], px=6.5, al=LEFT)
    for yy, a, b in ((111, "Fewer services", " for the adviser's clients"), (174, "Closes a key door", " to the middle market")):
        R(s, m, 342, yy, 478, yy + 34, light(NEG, .85))
        check(s, m, 355, yy + 17, 8, NEG, "x")
        RT(s, m, 368, yy + 2, 476, yy + 32, [[(a, "b"), (b, "")]], px=6.5, al=LEFT)


def _arc_arrow(c, r0, r1, a0, a1, tip=16, ov=9):
    """Arco em bloco com ponta de seta no fim; ângulos crescem no sentido horário."""
    out = arc(c, r1, a0, a1) + [(c[0] + (r1 + ov) * math.cos(math.radians(a1)), c[1] + (r1 + ov) * math.sin(math.radians(a1)))]
    rm = (r0 + r1) / 2
    out += [(c[0] + rm * math.cos(math.radians(a1 + tip)), c[1] + rm * math.sin(math.radians(a1 + tip)))]
    out += [(c[0] + (r0 - ov) * math.cos(math.radians(a1)), c[1] + (r0 - ov) * math.sin(math.radians(a1)))]
    out += arc(c, r0, a1, a0)
    return out


def flywheel(s, x, y, w, h):
    """Dois arcos-seta em tons formando um anel em volta do disco de logo, com etiquetas e leques de nota. BTG p.48."""
    m = FIT((0, 0, 510, 222), (x, y, w, h), 1.0)
    c = (253, 115)
    poly(s, m, _arc_arrow(c, 58, 82, -68, 96, 19, 12), D, edge=W, ew=.75)
    poly(s, m, _arc_arrow(c, 58, 82, 116, 276, 19, 12), F, edge=W, ew=.75)
    disc(s, m, *c, 56, W); disc(s, m, *c, 44, W, G3, .5)
    T(s, m, 215, 104, 291, 126, "[logo]", px=11, c=G4, i=True)
    R(s, m, 143, 104, 181, 125, F); T(s, m, 143, 104, 181, 125, "Unit A", px=7.5, c=W)
    R(s, m, 323, 102, 361, 123, D); T(s, m, 323, 102, 361, 123, "Unit B", px=7.5, c=W)
    notes = (((137, 55), (205, 55), LEFT, "Deal origination", "Advisers give valuable access to the mid market"), ((362, 55), (303, 55), RIGHT, "Bank products", "Cross-sell with core units attracts the best advisers"),
             ((137, 167), (190, 167), LEFT, "Better funding", "Balance sheet improves with lower risk and spreads"), ((362, 167), (312, 167), RIGHT, "Value for advisers", "Proximity of the bank to the adviser offices"))
    for a, b, side, t, d_ in notes:
        L(s, m, [a, b], D, .75)
        dia(s, m, a[0], a[1], 3.5, D)
        if side == LEFT:
            RT(s, m, 8, a[1] - 13, 130, a[1] + 22, [[(t, "b")], [(d_, "", F)]], px=6.5, al=RIGHT, an=TOP)
        else:
            RT(s, m, 369, a[1] - 13, 505, a[1] + 22, [[(t, "b")], [(d_, "", F)]], px=6.5, al=LEFT, an=TOP)


def serpentine_eras(s, x, y, w, h):
    """Linha grossa em U com diamantes por era; esmaecida no início e saturada no fim, termina em seta. BTG p.112."""
    m = FIT((0, 90, 510, 372), (x, y, w, h), 1.15)
    tn = (light(F, .75), light(F, .5), F, dark(F, .25), D)
    L(s, m, [(80, 167), (232, 167)], tn[0], 2.25)
    L(s, m, [(232, 167), (384, 167)], tn[1], 2.25)
    L(s, m, [(384, 167), (423, 167)] + arc((423, 217), 50, -90, 90)[1:] + [(323, 267)], tn[2], 2.25)
    L(s, m, [(323, 267), (157, 267)], tn[3], 2.25)
    L(s, m, [(157, 267), (100, 267)] + arc((100, 311), 44, -90, -180)[1:] + [(56, 330)], tn[4], 2.25, tail="triangle")
    for cx, cy, c in ((80, 167, tn[0]), (232, 167, tn[0]), (384, 167, tn[2]), (323, 267, tn[3]), (157, 267, tn[4])):
        dia(s, m, cx, cy, 15, W, c, 1.75)
    for cx, cy, t, c in ((85, 204, "Era A", tn[0]), (237, 197, "Era B", tn[0]), (388, 197, "Era C", tn[2]), (323, 237, "Era D", tn[4]), (157, 240, "Era E", tn[4]), (57, 343, "Today", tn[1])):
        T(s, m, cx - 45, cy - 12, cx + 45, cy + 12, t, px=15, c=c, b=True)
    for x0, x1, yy, a, b in ((20, 150, 121, "Young industry ", "in the country"), (312, 465, 124, "Market opening and ", "entry of foreigners"), (240, 420, 293, "Capital markets ", "boom after the listing wave"), (75, 240, 300, "Technology ", "allows digital entrants")):
        RT(s, m, x0, yy, x1, yy + 34, [[(a, "b", F), (b, "")]], px=11)
    mold(s, m, 200, 112, 275, 128, px=8)
    T(s, m, 195, 130, 280, 146, "Founded", px=11)


def _globe(s, m, c, r, xmin, col):
    """Malha irregular sobre esfera: nós da frente escuros, de trás claros, ligados aos vizinhos em 3D."""
    rnd = random.Random(5)
    n, P = 110, []
    for i in range(n):
        yy = 1 - 2 * (i + .5) / n
        rad = math.sqrt(1 - yy * yy)
        th = i * 2.399963 + rnd.uniform(-.25, .25)
        P.append((rad * math.cos(th), yy, rad * math.sin(th)))
    vis = lambda p: c[0] + r * p[0] > xmin + 2
    seen = set()
    for i, p in enumerate(P):
        near = sorted(range(n), key=lambda j: sum((P[j][k] - p[k]) ** 2 for k in range(3)))[1:4]
        for j in near:
            q = P[j]
            if (min(i, j), max(i, j)) in seen or not (vis(p) and vis(q)):
                continue
            seen.add((min(i, j), max(i, j)))
            front = p[2] + q[2] > 0
            L(s, m, [(c[0] + r * p[0], c[1] + r * p[1]), (c[0] + r * q[0], c[1] + r * q[1])], col if front else light(col, .55), .5 if front else .35, alpha=85 if front else 60)
    for i, p in enumerate(P):
        if vis(p):
            front = p[2] > 0
            disc(s, m, c[0] + r * p[0], c[1] + r * p[1], (3.2 if i % 3 == 0 else 2.2), col if front else light(col, .6))


def wire_globe(s, x, y, w, h):
    """Esfera de arame cortada pelo cartão à esquerda, com fios a rótulos de segmento e ponto final. CSN p.5."""
    m = FIT((0, 0, 510, 258), (x, y, w, h), 1.15)
    T(s, m, 40, 5, 500, 26, "Integrated platform across the group's businesses", px=11, al=LEFT)
    _globe(s, m, (45, 150), 106, 12, D)
    L(s, m, [(12, 0), (12, 258)], D, 1.0)
    rows = ((62, 112, 280, "Segment A", "Largest operation of the company"), (147, 150, 300, "Segment B", "Complementary activities"), (234, 100, 262, "Segment C", "Assets that make sense due to synergies"))
    for yy, xa, xb, t, d_ in rows:
        disc(s, m, xa, yy, 3.5, D)
        L(s, m, [(xa, yy), (xb, yy)], D, .75)
        T(s, m, xa + 50, yy - 16, xb, yy - 1, t, px=8.5, c=D, b=True)
        T(s, m, 296, yy - 15, 425, yy + 15, d_, px=8)
        L(s, m, [(430, yy), (478, yy)], D, .75)
        disc(s, m, 478, yy, 5, D)


def step_columns(s, x, y, w, h, active=None):
    """Fio atravessando a página com tique por coluna e painéis pendurados; active acende uma coluna e apaga as outras. CSN LM p.9."""
    m = FIT((0, 0, 510, 260), (x, y, w, h), 1.15)
    grad(R(s, m, 0, 0, 510, 260, D), ((0, dark(D, .6)), (1, dark(D, .05))), 60)
    cols = ((15, 110, "1st Step", "Divest the non-core plants", ("Limited synergies", "Better fit for a buyer"), ("$3,153m", "6.6% of debt", "EBITDA: $609m")),
            (152, 245, "2nd Step", "Sell the unit to a strategic", ("Market entry for a buyer", "Bolt-on for the buyer"), ("$14,924m", "28.2% of debt", "EBITDA: $1,795m")),
            (276, 370, "3rd Step", "Restructure and sell assets", ("Intercompany deal", "Sale to a strategic"), ("$3,325m", "6.3% of debt", "EBITDA: $4,546m")),
            (400, 493, "4th Step", "Tender offer", ("Funded by the sales", "Repurchase below par"), ("$4,251m", "8.0% of debt", "Avg. price: 67.4%")))
    xr = [0] + [q for c_ in cols for q in (c_[0] + 25, c_[1] - 22)] + [510]
    for a, b in zip(xr[::2], xr[1::2]):
        L(s, m, [(a, 52), (b, 52)], W, .75)
    for k, (x0, x1, st, ti, ch, kp) in enumerate(cols):
        dim = active is not None and active != k
        col = G4 if dim else W
        R(s, m, x0, 33, x1, 245, None, border=light(F, .35), width=.5)
        L(s, m, [(x0 + 25, 46), (x0 + 25, 58)], W, .75); L(s, m, [(x1 - 22, 46), (x1 - 22, 58)], W, .75)
        T(s, m, x0 + 27, 45, x1 - 24, 59, st, px=7, c=col, b=True, i=True)
        T(s, m, x0 + 5, 62, x1 - 5, 92, ti, px=7, c=col, b=True, i=True)
        for j, t in enumerate(ch):
            R(s, m, x0 + 12, 100 + j * 38, x1 - 12, 130 + j * 38, None, border=light(F, .35), width=.5, dash=True)
            T(s, m, x0 + 14, 100 + j * 38, x1 - 14, 130 + j * 38, t, px=6, c=col)
        for j, t in enumerate(kp):
            T(s, m, x0 + 3, 180 + j * 22, x1 - 3, 200 + j * 22, t, px=6.5, c=col, b=j == 0)


def swot_ring(s, x, y, w, h):
    """Quatro cartões com faixa diagonal no canto externo em volta de um anel em quartos. Meliuz p.71."""
    m = FIT((40, 10, 460, 245), (x, y, w, h), 1.1)
    cards = ((73, 28, 233, 118, 1, 1, F, "Strengths", ("Top of mind", "Management and strong culture", "High satisfaction")),
             (268, 28, 428, 118, -1, 1, light(F, .45), "Weaknesses", ("Co-branded card, weak economics", "Revenue concentration")),
             (73, 136, 233, 226, 1, -1, G3, "Threats", ("Commodity product", "No entry barriers", "Fierce competition")),
             (268, 136, 428, 226, -1, -1, light(F, .7), "Opportunities", ("Online expansion", "Inorganic growth", "Banking and credit")))
    for x0, y0, x1, y1, sx_, sy_, c, name, lines in cards:
        RR(s, m, x0, y0, x1, y1, G1, .06)
        RT(s, m, x0 + 22, y0 + 8, x1 - 22, y1 - 8, [[(q, "")] for q in lines], px=8.5)
    for x0, y0, x1, y1, sx_, sy_, c, name, lines in cards:
        cx, cy = (x0 if sx_ > 0 else x1), (y0 if sy_ > 0 else y1)
        Q = lambda a, b: (cx + sx_ * a, cy + sy_ * b)
        poly(s, m, (Q(-7, 62), Q(0, 62), Q(0, 69)), dark(c, .3))
        poly(s, m, (Q(62, -7), Q(62, 0), Q(69, 0)), dark(c, .3))
        poly(s, m, (Q(-7, 28), Q(28, -7), Q(62, -7), Q(-7, 62)), c)
        tc = Q(14, 14)
        rot = -45 if sx_ * sy_ > 0 else 45
        T(s, m, tc[0] - 38, tc[1] - 8, tc[0] + 38, tc[1] + 8, name, px=7.5, c=W, b=True, rot=rot)
    c = (250.5, 127)
    disc(s, m, *c, 49, W)
    for a0, col in ((180, F), (270, light(F, .45)), (0, light(F, .7)), (90, G3)):
        poly(s, m, seg(c, 31, 44, a0 + 2, a0 + 88), col)
    disc(s, m, *c, 30, W)
    T(s, m, c[0] - 25, c[1] - 10, c[0] + 25, c[1] + 10, "[logo]", px=9, c=G4, i=True)


def deadline_band(s, x, y, w, h):
    """Seis cartões com data sobre faixa contínua que escurece, com dobra triangular a cada passo. Sabesp p.11."""
    m = FIT((10, 12, 892, 170), (x, y, w, h), 1.6)
    xe = (15, 166, 310, 456, 597, 746, 888)
    cards = (30, 173, 317, 462, 610, 755)
    cols = (light(A, .8), light(A, .35), A, F, dark(F, .3), D)
    data = (("Y1", "$200m bond", "Duties begin", "Contract signed"), ("Y2", "New books", "Capex seen", "Regulatory accounts"), ("Yearly", "Capex audit", "Or excluded", "Annual valuation"),
            ("Y5", "Capex in", "New tariff", "Tariff review"), ("Y35", "$500m bond", "Reversion", "Bond doubles"), ("Y37", "Assets back", "Shortfall", "Asset reversion"))
    for i, c in enumerate(cols):
        R(s, m, xe[i], 110, xe[i + 1], 167, c)
        T(s, m, xe[i] + 8, 112, xe[i + 1] - 8, 160, data[i][3], px=14, c=INK if i == 0 else W, b=True)
    for i, cx in enumerate(cards):
        R(s, m, cx, 18, cx + 115, 110, G1)
        T(s, m, cx + 2, 20, cx + 113, 42, data[i][0], px=15, b=True)
        T(s, m, cx + 8, 46, cx + 112, 74, data[i][1], px=9.5, al=LEFT, an=TOP)
        T(s, m, cx + 8, 76, cx + 112, 106, data[i][2], px=9.5, al=LEFT, an=TOP)
        n = cols[i + 1] if i < 5 else dark(D, .3)
        rx = cx + 115
        poly(s, m, ((rx, 88), (rx, 110), (rx + 20, 110)), n)
    poly(s, m, ((30, 88), (15, 110), (30, 110)), light(A, .6))


def sorted_bars(s, x, y, w, h):
    """Colunas crescentes: cinza até a quebra, depois cor que escurece; colchetes tracejados até chips de média. Sabesp p.79. No slide real, usar gráfico nativo."""
    m = FIT((0, 10, 510, 241), (x, y, w, h), 1.15)
    n, b0 = 40, 226
    xs = [18 + i * 12 for i in range(n)]
    for i, xx in enumerate(xs):
        if i < 26:
            hh = 28 + (i / 25) ** 1.4 * 27; c = G4
        else:
            t = (i - 26) / 13
            hh = 58 + t ** 1.6 * 145
            c = light(A, .25) if t < .45 else (F if t < .8 else D)
        R(s, m, xx, b0 - hh, xx + 8.5, b0, c)
    L(s, m, [(14, b0), (497, b0)], G4, .5)
    for i in range(0, n, 3):
        T(s, m, xs[i] - 10, b0 + 1, xs[i] + 18, b0 + 11, f"{60 + i}%", px=4, c=G4)
    L(s, m, [(20, 195), (20, 142), (322, 142), (322, 170)], INK, .5, dash=True)
    RR(s, m, 112, 133, 228, 151, W, .2, INK, .5); T(s, m, 112, 133, 228, 151, "Avg: $3.6k/unit", px=7, b=True)
    L(s, m, [(332, 165), (332, 28), (492, 28), (492, 35)], F, .5, dash=True)
    RR(s, m, 363, 19, 461, 37, W, .2, INK, .5); T(s, m, 363, 19, 461, 37, "Avg: $10.5k/unit", px=7, b=True)
    R(s, m, 103, 53, 265, 108, light(A, .82)); R(s, m, 103, 108, 265, 111, F)
    RT(s, m, 110, 56, 258, 106, [[("Reaching ", ""), ("remote and informal", "b"), (" areas spikes ", ""), ("unit costs", "b")]], px=8)


def vase_pyramids(s, x, y, w, h):
    """Pirâmides etárias como silhuetas sólidas, sem eixo nem vão central, lado a lado por ano. RD p.9. No slide real, usar gráfico nativo de barras."""
    m = FIT((0, 18, 510, 200), (x, y, w, h), 1.1)
    w1 = (22, 26, 44, 60, 76, 88, 97, 108, 118, 128, 140, 143, 140, 134, 128, 126, 124, 120)
    w2 = (88, 88, 104, 122, 136, 148, 146, 148, 146, 142, 138, 130, 122, 118, 122, 118, 110, 108)
    ages = ("80+", "70-74", "60-64", "50-54", "40-44", "30-34", "20-24", "10-14", "0-4")
    for cx, wid, lab_, yr in ((146, w1, 28, "Year A"), (404, w2, 285, "Year B")):
        for i, wd in enumerate(wid):
            yy = 27 + i * 8.05
            R(s, m, cx - wd / 2, yy, cx + wd / 2, yy + 7.3, F)
        for i, a in enumerate(ages):
            T(s, m, lab_ - 12, 21 + i * 17, lab_ + 34, 39 + i * 17, a, px=9, c=INK)
        T(s, m, cx - 40, 172, cx + 40, 192, yr, px=12)


def marimekko(s, x, y, w, h):
    """Blocos em torno do zero: largura é participação, altura é margem; líder fino acima, os outros abaixo. RD p.27. No slide real, com dado de planilha, usar tabela de origem."""
    m = FIT((0, 40, 450, 360), (x, y, w, h), 1.15)
    T(s, m, 100, 44, 340, 66, "Profit pool", px=12, b=True)
    R(s, m, 33, 78, 418, 335, G1)
    L(s, m, [(33, 78), (418, 78), (418, 335), (33, 335), (33, 78)], G4, .5)
    Y = lambda v: 120 - v * 21.4
    for v in (2, 0, -2, -4, -6, -8, -10):
        T(s, m, 2, Y(v) - 8, 30, Y(v) + 8, f"{v}%", px=8)
    R(s, m, 33, Y(.8), 280, Y(0), F)
    T(s, m, 33, Y(.8), 280, Y(0), "16%", px=8, c=W, b=True)
    R(s, m, 280, Y(0), 373, Y(-3), A)
    T(s, m, 280, Y(0), 373, Y(0) + 16, "6%", px=8, c=W, b=True)
    R(s, m, 373, Y(0), 418, Y(-8.6), D)
    T(s, m, 373, Y(0), 418, Y(0) + 16, "3%", px=8, c=W, b=True)
    for x0, x1, y0, t, c in ((133, 175, 80, "0.8%", F), (306, 347, 188, "-3%", dark(F, .3)), (375, 416, 310, "-8%", D)):
        R(s, m, x0, y0, x1, y0 + 18, c); T(s, m, x0, y0, x1, y0 + 18, t, px=8, c=W, b=True)
    T(s, m, 150, 338, 300, 356, "% market share", px=8, b=True)


def _eq_bars(s, m, x0, x1, y0, y1, vals, lab_):
    n = len(vals); st = (x1 - x0) / n; bw = st * .78
    for i, v in enumerate(vals):
        bx = x0 + i * st
        yt = y1 - (y1 - y0) * v
        grad(R(s, m, bx, yt, bx + bw, y1, F), ((0, F), (1, D)), 0)
        if i in lab_:
            a, b = bx - 2, bx + bw + 2
            R(s, m, a, yt - 8, b, yt - 1, D); T(s, m, a - 2, yt - 8, b + 2, yt - 1, lab_[i], px=4, c=W, b=True)
    L(s, m, [(x0 - 2, y1), (x1 + 2, y1)], G4, .5)
    for i in range(0, n, 2):
        T(s, m, x0 + i * st - 5, y1 + 1, x0 + i * st + 14, y1 + 9, f"Y{i + 1}", px=4, c=G4)


def chart_equation(s, x, y, w, h):
    """Três gráficos como termos: X e = grandes nas calhas, o último em linha, sobre banda com aba dobrada. RD p.49. No slide real, usar gráficos nativos."""
    m = FIT((0, 8, 510, 141), (x, y, w, h), 1.45)
    R(s, m, 0, 18, 510, 141, G1)
    poly(s, m, ((8, 44), (18, 44), (18, 52)), dark(F, .4))
    R(s, m, 8, 26, 124, 44, F); T(s, m, 8, 26, 124, 44, "ROIC calculation", px=8, c=W)
    T(s, m, 30, 44, 140, 56, "Margin", px=6, b=True); T(s, m, 200, 26, 320, 38, "Turnover", px=6, b=True); T(s, m, 370, 26, 490, 38, "ROIC", px=6, b=True)
    _eq_bars(s, m, 12, 155, 66, 125, (.45, .36, .6, .72, .68, .74, .78, .8, .84, .86, .92, .9, .96, .94), {0: "5%", 7: "6%", 12: "7%"})
    _eq_bars(s, m, 180, 335, 58, 125, (.68, .66, .7, .68, .74, .78, .8, .82, .84, .88, .86, .9, .94, .96), {0: "3.3", 7: "3.9", 13: "4.3"})
    op(s, m, 167, 95, 12, "x", INK); op(s, m, 344, 95, 12, "=", INK)
    P = [(358, 92), (368, 92), (376, 108), (384, 100), (394, 90), (408, 86), (425, 80), (440, 74), (458, 62), (468, 58), (482, 60), (496, 56)]
    L(s, m, P[:7], D, 1.25); L(s, m, P[6:], D, 1.25, dash=True)
    for i, t in ((0, "16%"), (3, "15%"), (6, "21%"), (9, "27%"), (11, "25%")):
        a, b = P[i]
        R(s, m, a - 9, b - 15, a + 9, b - 7, F); T(s, m, a - 10, b - 15, a + 10, b - 7, t, px=4, c=W, b=True)
    L(s, m, [(355, 125), (508, 125)], G4, .5)
    for i in range(0, 12, 2):
        T(s, m, 356 + i * 12.5, 126, 376 + i * 12.5, 134, f"Y{i + 1}", px=4, c=G4)


def op(s, m, cx, cy, d, kind, c=INK):
    t = d * .24
    if kind == "=":
        R(s, m, cx - d / 2, cy - d * .3, cx + d / 2, cy - d * .3 + t, c); R(s, m, cx - d / 2, cy + d * .3 - t, cx + d / 2, cy + d * .3, c)
    else:
        k = d * .5; e = t * .55
        poly(s, m, ((cx - k, cy - k + e), (cx - k + e, cy - k), (cx + k, cy + k - e), (cx + k - e, cy + k)), c)
        poly(s, m, ((cx + k, cy - k + e), (cx + k - e, cy - k), (cx - k, cy + k - e), (cx - k + e, cy + k)), c)


def tangent_circles(s, x, y, w, h):
    """Colunas numeradas com círculos crescentes ligados por fios tangentes e chip de participação no pé. RBI p.28."""
    m = FIT((40, 15, 485, 400), (x, y, w, h), 1.2)
    cols = ((55, 190, "1", "Home market", "31.7%"), (198, 332, "2", "Region", "6.3%"), (338, 472, "3", "Worldwide", "4.7%"))
    for x0, x1, n, t, v in cols:
        RR(s, m, x0, 28, x1, 390, G1, .1)
        cx = (x0 + x1) / 2
        disc(s, m, cx, 55, 18, light(F, .6)); disc(s, m, cx, 55, 14, F)
        T(s, m, cx - 12, 45, cx + 12, 65, n, px=12, c=W, b=True)
        T(s, m, x0, 80, x1, 106, t, px=13, b=True)
        R(s, m, x0 + 13, 308, x1 - 15, 356, F)
        RT(s, m, x0 + 13, 310, x1 - 15, 354, [[("Share", "b", W)], [(v, "", W)]], px=11)
    L(s, m, [(118, 188), (406, 147)], G4, .75); L(s, m, [(118, 220), (406, 261)], G4, .75)
    for cx, r, c, t in ((118, 16, dark(F, .25), "23.6"), (264, 39, F, "418.4"), (406, 60, light(F, .25), "996.2")):
        disc(s, m, cx, 204, r, c)
        T(s, m, cx - r, 194, cx + r, 214, t, px=10 if r > 20 else 7.5, c=W, b=True)


def driver_tree(s, x, y, w, h, lit="left"):
    """Árvore de drivers: caixa ativa em cor, inativa em cinza, X claro entre irmãos; lit muda o ramo aceso. RBI p.30-32."""
    m = FIT((0, 28, 510, 323), (x, y, w, h), 1.15)
    on_l, on_r = lit == "left", lit == "right"
    pale = light(F, .6)
    def bx(x0, y0, x1, y1, t, on, px=15, sub=False):
        c = (light(F, .15) if sub else F) if on else G3
        RR(s, m, x0, y0, x1, y1, c, .12)
        T(s, m, x0, y0, x1, y1, t, px=px, c=W, b=True, i=True)
    def cross(cx, cy, c):
        L(s, m, [(cx - 9, cy - 9), (cx + 9, cy + 9)], c, 1.0); L(s, m, [(cx + 9, cy - 9), (cx - 9, cy + 9)], c, 1.0)
    L(s, m, [(316, 72), (316, 88)], pale, 1.0)
    L(s, m, [(190, 120), (190, 88), (443, 88), (443, 120)], pale, 1.0, head="triangle", tail="triangle")
    bx(200, 40, 432, 72, "Revenue", True, 16)
    bx(146, 122, 236, 165, "Value", on_l); bx(400, 122, 486, 165, "Volume", on_r)
    cross(316, 143, pale)
    L(s, m, [(190, 165), (190, 176)], pale if on_l else G3, 1.0)
    L(s, m, [(122, 210), (122, 176), (255, 176), (255, 210)], pale if on_l else G3, 1.0, head="triangle", tail="triangle")
    L(s, m, [(443, 165), (443, 210)], pale if on_r else G3, 1.0, tail="triangle")
    bx(85, 212, 158, 253, "Price", on_l, 12, True); bx(219, 212, 292, 253, "Traffic", False, 12); bx(407, 212, 480, 253, "Mix", on_r, 12, True)
    cross(188, 232, G3)
    T(s, m, 40, 272, 490, 296, "The company has not adjusted prices in recent years", px=11, c=F, b=True)
    T(s, m, 40, 296, 490, 318, "Average monthly price of the basket (base 100)", px=10, c=G4, i=True)


def cohort_lines(s, x, y, w, h):
    """Trinta linhas de safra, do pálido ao saturado, com legenda vertical em degradê. Nubank p.15. No slide real, usar gráfico nativo de linhas."""
    m = FIT((0, 0, 510, 400), (x, y, w, h), 1.15)
    RT(s, m, 10, 2, 500, 24, [[("New clients now join with higher ", ""), ("engagement", "b", F)]], px=12, al=LEFT)
    T(s, m, 10, 26, 500, 46, "Average products per client by months as a client", px=10, c=G4, al=LEFT)
    T(s, m, 10, 56, 60, 80, "Products per client", px=7, c=G4)
    for i, v in enumerate((4, 3.5, 3, 2.5, 2, 1.5, 1)):
        T(s, m, 8, 89 + i * 46, 30, 103 + i * 46, str(v), px=7.5, c=G4)
    L(s, m, [(34, 88), (34, 368), (478, 368)], INK, .75)
    for i in range(12):
        T(s, m, 40 + i * 38, 371, 60 + i * 38, 385, str(1 + i * 8), px=7, c=G4)
    n = 30
    rnd = random.Random(4)
    for k in range(n):
        t = k / (n - 1)          # 0 = safra antiga, 1 = safra nova
        start = 368 - t * 215
        top_ = 96 + (1 - t) * 8
        end = 448 - t * 390
        pts = []
        steps = 18
        for j in range(steps + 1):
            u = j / steps
            xx = 42 + (end - 42) * u
            prog = (xx - 42) / 405
            yy = top_ + (start - top_) * math.exp(-prog * (3.0 + 2.5 * t) * (1.0))
            yy += rnd.uniform(-1.6, 1.6)
            pts.append((xx, min(yy, 367)))
        L(s, m, pts, ss.mix(light(F, .8), dark(F, .25), t), .75 + .5 * t)
    grad(R(s, m, 402, 176, 424, 300, F), ((0, dark(F, .25)), (1, light(F, .8))), 90)
    T(s, m, 385, 160, 441, 175, "Newest", px=8, b=True); T(s, m, 385, 301, 441, 317, "Oldest", px=8, b=True)


def wheel_throat(s, x, y, w, h):
    """Roda de aro grosso com seis fatias, ícones e logo central; garganta pálida abre em painel com a rosca de receita. Nubank p.2. No slide real, a rosca pode ser nativa."""
    m = FIT((0, 0, 350, 480), (x, y, w, h), 1.0)
    pale = light(F, .88)
    c = (175, 138)
    poly(s, m, ((88, 245), (262, 245), (325, 300), (25, 300)), light(F, .78))
    RR(s, m, 8, 280, 344, 472, pale, .1)
    disc(s, m, *c, 150, F)
    disc(s, m, *c, 132, pale)
    for a in (-120, -60, 0, 60, 120, 180):
        p0 = (c[0] + 45 * math.cos(math.radians(a)), c[1] + 45 * math.sin(math.radians(a)))
        p1 = (c[0] + 133 * math.cos(math.radians(a)), c[1] + 133 * math.sin(math.radians(a)))
        L(s, m, [p0, p1], W, 2.0)
    disc(s, m, *c, 47, W)
    T(s, m, 140, 124, 210, 152, "[logo]", px=13, c=F, i=True)
    for a, k, t in ((-90, "card", "Fees"), (-30, "phone", "Payments"), (30, "card", "Credit"), (90, "chart", "Investing"), (150, "cloud", "Data"), (-150, "coin", "Deposits")):
        rr_ = 90
        cx, cy = c[0] + rr_ * math.cos(math.radians(a)), c[1] + rr_ * math.sin(math.radians(a))
        ico(s, m, cx, cy - 13, 30, k, F, .75)
        T(s, m, cx - 40, cy + 3, cx + 40, cy + 22, t, px=11, c=F, b=True)
    T(s, m, 20, 288, 332, 316, "Revenue breakdown", px=14, b=True)
    dc = (180, 392)
    vals = ((33.0, D), (26.4, F), (12.0, light(F, .35)), (28.6, A))
    a0 = -90
    for v, col in vals:
        a1 = a0 + v * 3.6
        poly(s, m, seg(dc, 42, 76, a0, a1, 20), col)
        am = math.radians((a0 + a1) / 2)
        T(s, m, dc[0] + 59 * math.cos(am) - 26, dc[1] + 59 * math.sin(am) - 8, dc[0] + 59 * math.cos(am) + 26, dc[1] + 59 * math.sin(am) + 8, f"{v:.1f}%", px=8, c=W, b=True)
        a0 = a1
    T(s, m, 140, 370, 220, 414, "$11.5bn", px=11, c=F, b=True)
    for pts, tt, x0, x1, al in (([(240, 350), (262, 342), (335, 342)], "Cards", 262, 335, RIGHT), ([(235, 440), (262, 448), (335, 448)], "Loans", 262, 335, RIGHT), ([(112, 345), (22, 345)], "Others", 22, 90, LEFT), ([(125, 436), (22, 436)], "Fees", 22, 90, LEFT)):
        L(s, m, pts, INK, .5)
        T(s, m, x0, pts[-1][1] - 15, x1, pts[-1][1] - 1, tt, px=8, al=al)


def plate_funnel(s, x, y, w, h):
    """Placas contíguas e centradas, cada uma mais estreita, com número assinado; cunha em degradê liga ao mapa. Nubank p.13."""
    m = FIT((0, 0, 510, 333), (x, y, w, h), 1.15)
    grad(poly(s, m, ((60, 42), (176, 5), (240, 325), (60, 280)), G3), ((0, G4), (1, W, 0)), 0)
    st = {k: v for k, v in states("BRA").items() if k in ("MG", "BA", "GO", "DF", "TO", "PI", "MA", "CE", "RN", "PB", "PE", "AL", "SE", "SP", "RJ", "ES", "PR", "SC", "RS", "MS")}
    tone = lambda k: D if k in ("MG", "BA", "GO", "DF", "TO", "PI", "MA", "CE", "RN", "PB", "PE", "AL", "SE") else (F if k in ("SP", "RJ", "ES") else light(F, .4))
    px_, py_ = draw_map(s, m.box(0, 20, 130, 310), st, tone, W, .25)
    for lo, la, t in ((-44, -14, "9.2"), (-48, -23, "8.4")):
        cx, cy = px_(lo), py_(la)
        rr(s, cx - .13, cy - .07, .26, .14, D, .2)
        tx(s, cx - .13, cy - .07, .26, .14, t, size=pt(m, 9), color=W, bold=True)
    plates = ((174, 503, 4, 68, "Adult population:", "173 million"), (191, 486, 68, 132, "Already served:", "-142.5 million"), (208, 470, 132, 196, "No internet access:", "-7.3 million"),
              (224, 454, 196, 260, "No device:", "-5.2 million"), (240, 437, 260, 325, "TAM:", "~18 million"))
    for x0, x1, y0, y1, a, b in plates:
        R(s, m, x0, y0, x1, y1, light(F, .4))
        RT(s, m, x0 + 4, y0 + 3, x1 - 4, y1 - 3, [[(a, "i", W)], [(b, "b", W)]], px=14)


def logic_column(s, x, y, w, h):
    """Dois leques de logo em cartões tintados e coluna central de contorno bicolor com a cadeia de consequências. Nubank p.33."""
    m = FIT((0, 0, 510, 325), (x, y, w, h), 1.2)
    def side(y0, y1, c, t, reg, off1, off2):
        cy = (y0 + y1) / 2 - 2
        grad(poly(s, m, ((42, cy), (88, y0), (88, y1)), c), ((0, c), (1, light(c, .85))), 0)
        RR(s, m, 85, y0, 247, y1, light(c, .87), .1)
        RR(s, m, 4, cy - 20, 42, cy + 20, c, .2)
        T(s, m, 4, cy - 10, 42, cy + 10, "[logo]", px=7, c=W, i=True)
        T(s, m, 90, y0 + 5, 242, y0 + 36, t, px=8.5, c=c, b=True)
        RT(s, m, 90, y0 + 38, 242, y0 + 64, [[("Regulated as a ", ""), (reg, "b", c)]], px=8)
        T(s, m, 90, y0 + 66, 242, y0 + 80, "Offers:", px=8, c=c, b=True)
        T(s, m, 95, y0 + 84, 242, y0 + 100, off1, px=8, al=LEFT)
        T(s, m, 95, y0 + 106, 242, y0 + 122, off2, px=8, al=LEFT)
    side(10, 143, F, "A full-service digital institution", "LICENCE A", "Credit", "Banking-like products")
    side(190, 323, A, "A digital wallet and payment platform", "LICENCE B", "Payment processing", "Holding balances")
    fade_line(RR(s, m, 266, 1, 508, 322, G1, .1, F, 1.25), ((0, F), (.5, F), (.5, A), (1, A)), 90)
    def half(y0, c, a, a2, b1, b2, cons, tri):
        RT(s, m, 275, y0, 500, y0 + 32, [[(a, "b", c), (a2, "")]], px=10)
        T(s, m, 280, y0 + 38, 340, y0 + 64, b1, px=10)
        L(s, m, [(345, y0 + 51), (428, y0 + 51)], c, .75, tail="triangle")
        T(s, m, 432, y0 + 38, 500, y0 + 64, b2, px=10)
        T(s, m, 275, y0 + 72, 500, y0 + 90, cons, px=11, c=c, b=True)
        if len(tri) == 3:
            for k, t in enumerate(tri):
                x0 = 272 + k * 78
                T(s, m, x0, y0 + 94, x0 + 76, y0 + 124, t, px=9.5)
            for xx in (351, 429):
                L(s, m, [(xx, y0 + 96), (xx, y0 + 122)], F, .75)
        else:
            T(s, m, 275, y0 + 94, 500, y0 + 116, tri[0], px=10)
    half(20, F, "Eligible for", " deposit insurance", "Safer credit", "Lower yields", "Cheaper funding", ("Competitive loans", "Bigger spreads", "More stability"))
    half(192, A, "Not eligible for", " deposit insurance", "Riskier credit", "Higher yields", "More expensive funding", ("Lower spreads",))


def _ribbon(s, m, xs, y0, y1, p, cols, labels):
    """Fita em S (gabarito Sabesp p.2): bloco de cor e fantasma cinza espelhado a cada passo p."""
    from pecas_profundidade import RIB
    X = lambda a, ox: ox + a * p / 120
    Y = lambda b: y0 + (b - RIB_Y0) / (RIB_Y1 - RIB_Y0) * (y1 - y0)
    ys = [b for _, b in RIB]
    RIB_Y0, RIB_Y1 = min(ys), max(ys)
    for xx in xs:
        poly(s, m, [(X(137.8 - a + 67, xx), Y(b)) for a, b in RIB], G2)
    L(s, m, [(xs[0] - p * .2, (y0 + y1) / 2), (xs[-1] + p * 1.75, (y0 + y1) / 2)], G4, 1.25)
    for xx, c, tl in zip(xs, cols, labels):
        poly(s, m, [(X(a, xx), Y(b)) for a, b in RIB], c)
        T(s, m, X(25, xx), y0, X(115, xx), y1, tl, px=9, c=W, b=True)


def ellipsis_heads(s, x, y, w, h):
    """Frase partida em três cabeçalhos com reticências e verbo em negrito; cada pedaço abre um exhibit. Sabesp p.17."""
    m = FIT((0, 0, 900, 395), (x, y, w, h), 1.1)
    RT(s, m, 5, 2, 800, 28, [[("The group has spent decades ", ""), ("buying", "b", F), (" and ", ""), ("turning around", "b", F), (" weak assets...", "")]], px=16, al=LEFT)
    T(s, m, 5, 30, 700, 50, "Seven assets bought since the first deal, each one a turnaround story", px=12, c=G4, i=True, al=LEFT)
    for x0, x1, qx in ((5, 190, 0), (730, 880, 1)):
        R(s, m, x0, 75, x1, 150, G1)
        if qx == 0:
            mold(s, m, x0, 60, x0 + 45, 150, "[foto]", px=9); T(s, m, x0 + 50, 78, x1 - 4, 148, "We bring deep experience and raise the bar on service.", px=10, i=True)
        else:
            mold(s, m, x1 - 45, 60, x1, 150, "[foto]", px=9); T(s, m, x0 + 4, 78, x1 - 50, 148, "They know how to close the gap.", px=10, i=True)
    xs = [195 + i * 80 for i in range(6)]
    cols = (D, dark(F, .25), F, light(F, .3), light(F, .6), A)
    _ribbon(s, m, xs, 92, 140, 80, cols, ("Y1", "Y2", "Y3", "Y4", "Y5", "Y6"))
    for i, (xx, t) in enumerate(zip(xs, ("Asset A", "Asset B", "Asset C", "Asset D", "Asset E", "Asset F"))):
        up = i % 2 == 0
        if up:
            L(s, m, [(xx + 55, 92), (xx + 55, 70)], G4, .5); poly(s, m, ((xx + 55, 70), (xx + 70, 70), (xx + 55, 80)), cols[i]); T(s, m, xx + 72, 64, xx + 150, 84, t, px=12, al=LEFT)
        else:
            L(s, m, [(xx + 55, 140), (xx + 55, 172)], G4, .5); poly(s, m, ((xx + 55, 172), (xx + 70, 172), (xx + 55, 162)), cols[i]); T(s, m, xx + 72, 156, xx + 150, 176, t, px=12, al=LEFT)
    RT(s, m, 5, 186, 440, 210, [[("...driving costs consistently ", ""), ("below the ceiling", "b", F), ("...", "")]], px=15, al=LEFT)
    T(s, m, 5, 210, 440, 228, "Allowed versus real opex", px=12, c=G4, i=True, al=LEFT)
    RT(s, m, 465, 186, 895, 210, [[("...and ", ""), ("replicating efficiency", "b", F), (" in every asset", "")]], px=15, al=LEFT)
    T(s, m, 465, 210, 895, 228, "Losses fall after every acquisition", px=12, c=G4, i=True, al=LEFT)
    for i, (c, v) in enumerate(((G3, (.7, .75, .7, .8, .75, .85)), (F, (.6, .62, .55, .6, .52, .55)))):
        for j, q in enumerate(v):
            bx = 30 + j * 62 + i * 22
            R(s, m, bx, 385 - 140 * q, bx + 20, 385, c)
    L(s, m, [(20, 385), (420, 385)], G4, .5)
    for k, (c, off) in enumerate(((D, 0), (F, 6), (A, 12))):
        P = [(490 + j * 65, 250 + off * 4 + 16 * j + 8 * math.sin(j + k)) for j in range(6)]
        L(s, m, P, c, 1.25)
    L(s, m, [(480, 385), (870, 385)], G4, .5)


def cards_over_ribbon(s, x, y, w, h):
    """Três cartões com sombra dura ligados por banda clara, um exhibit por cartão e fita-cronologia no rodapé. Sabesp p.2. No slide real, o combo é gráfico nativo."""
    m = FIT((0, 0, 510, 239), (x, y, w, h), 1.2)
    R(s, m, 0, 28, 510, 112, "F7F7F7")
    for x0, x1 in ((7, 152), (175, 340), (349, 500)):
        R(s, m, x0 + 5, 9, x1 + 5, 141, G3); R(s, m, x0, 5, x1, 136, G1)
    T(s, m, 12, 8, 150, 19, "Built on two pillars", px=7, b=True, al=LEFT); T(s, m, 12, 18, 150, 27, "Operating data", px=5, c=G4, i=True, al=LEFT)
    for k, (t, ic) in enumerate((("Unit A", "flask"), ("Unit B", "gear"))):
        ico(s, m, 72 + k * 44, 40, 9, ic, F, .5); T(s, m, 57 + k * 44, 45, 95 + k * 44, 54, t, px=4.5, c=F, b=True)
    for i, (a, b, c_) in enumerate((("Links", "9.5m", "8.2m"), ("People", "28.1m", "25.1m"), ("Volume", "2.3bn", "2.0bn"))):
        yy = 58 + i * 22
        T(s, m, 10, yy, 56, yy + 18, a, px=5, al=LEFT); T(s, m, 57, yy, 96, yy + 18, b, px=5.5, c=F, b=True); T(s, m, 101, yy, 140, yy + 18, c_, px=5.5, c=F, b=True)
        L(s, m, [(10, yy + 20), (145, yy + 20)], G3, .35)
    T(s, m, 180, 8, 335, 19, "Location where it matters", px=7, b=True, al=LEFT); T(s, m, 180, 18, 335, 27, "Footprint across the richest area", px=5, c=G4, i=True, al=LEFT)
    tone = lambda k: A if k in ("SP", "RJ", "MG", "PR", "SC", "RS", "ES") else G3
    draw_map(s, m.box(198, 28, 318, 130), states("BRA"), tone, W, .2)
    for x0, t in ((186, "375 sites"), (278, "58% share")):
        R(s, m, x0, 108, x0 + 42, 126, D); T(s, m, x0, 108, x0 + 42, 126, t, px=5, c=W, b=True)
    T(s, m, 354, 8, 495, 19, "Scaling with margin expansion", px=7, b=True, al=LEFT)
    R(s, m, 356, 21, 362, 25, A); T(s, m, 364, 18, 415, 28, "Revenue", px=4.5, al=LEFT); L(s, m, [(418, 23), (426, 23)], D, .75); T(s, m, 428, 18, 490, 28, "Margin", px=4.5, al=LEFT)
    hs = (40, 44, 48, 52, 58, 66)
    for i, hv in enumerate(hs):
        bx = 358 + i * 23
        R(s, m, bx + 4, 127 - hv, bx + 15, 127, A)
        T(s, m, bx - 1, 127, bx + 20, 135, f"Y{i + 1}", px=4, c=G4)
    P = [(358 + i * 23 + 10, 74 - i * 5.5) for i in range(6)]
    L(s, m, P, D, .75)
    for (a, b), t in zip(P, ("45%", "42%", "46%", "48%", "52%", "60%")):
        R(s, m, a - 9, b - 5, a + 9, b + 4, D); T(s, m, a - 10, b - 5, a + 10, b + 4, t, px=4, c=W, b=True)
    xs = [12 + i * 76 for i in range(6)]
    _ribbon(s, m, xs, 186, 216, 76, (D, dark(F, .25), F, light(F, .15), A, A), ("Y1", "Y2", "Y3", "Y4", "Y5", "Y6"))
    for i, (xx, t) in enumerate(zip(xs, ("Foundation of the company", "Listing abroad", "First local listing", "Stake reduction", "Private ownership", "Add-on purchase"))):
        if i % 2 == 0:
            L(s, m, [(xx + 42, 186), (xx + 42, 160)], G4, .4); poly(s, m, ((xx + 42, 160), (xx + 50, 160), (xx + 42, 166)), D)
            T(s, m, xx + 52, 156, min(xx + 130, 508), 178, t, px=5.5, al=LEFT)
        else:
            L(s, m, [(xx + 42, 216), (xx + 42, 238)], G4, .4); poly(s, m, ((xx + 42, 238), (xx + 50, 238), (xx + 42, 232)), D)
            T(s, m, xx + 52, 218, min(xx + 130, 508), 238, t, px=5.5, al=LEFT)


def ecg_timeline(s, x, y, w, h):
    """Uma linha que corre plana, sobe e desce como ECG até a seta, em moldura tracejada, com chips de ano e discos de ícone. RD p.72."""
    m = FIT((0, 0, 510, 354), (x, y, w, h), 1.2)
    R(s, m, 3, 3, 508, 351, G1, border=F, dash=True, width=1.0)
    P = [(3, 175), (43, 175), (70, 135), (120, 228), (145, 175), (215, 175), (243, 135), (295, 230), (320, 175), (415, 177)]
    L(s, m, P, F, 1.5, tail="triangle")
    for cx, cy, r, k in ((70, 54, 25, "doc"), (243, 54, 25, "flask"), (121, 308, 25, "syringe"), (294, 300, 25, "person"), (460, 137, 25, "shield")):
        disc(s, m, cx, cy, r, D); ico(s, m, cx, cy, 30, k, W, .75)
    for x0, x1, y0, t, cy, c0, c1 in ((44, 96, 112, "Y1", 88, 15, 125), (217, 268, 112, "Y4", 88, 185, 300), (96, 147, 234, "Y2", 263, 65, 180), (270, 320, 234, "Y3", 263, 225, 365), (437, 488, 200, "Y5", 178, 410, 508)):
        R(s, m, x0, y0, x1, y0 + 19, D); T(s, m, x0, y0, x1, y0 + 19, t, px=9, c=W, b=True)
    T(s, m, 15, 80, 125, 110, "New law for the sector", px=9.5); T(s, m, 185, 80, 300, 110, "Tests in the channel", px=9.5)
    T(s, m, 65, 254, 180, 281, "Vaccines in the channel", px=9.5); T(s, m, 225, 254, 365, 272, "Remote care", px=9.5)
    T(s, m, 415, 165, 508, 198, "Thesis: care hubs", px=9.5)


def halo_tray(s, x, y, w, h):
    """Colunas com ícone em disco claro e bandeja flutuante de pares ícone-número. Vasta p.24. No slide real, o funil e a barra vêm do roteiro."""
    m = FIT((0, 0, 510, 222), (x, y, w, h), 1.2)
    for cx, k, t, d_, x1 in ((15, "person", "Rival game", "Payoff of each move", 165), (182, "funnel", "Market funnel", "Addressable units", 320), (345, "target", "Where the gain comes from", "Capture by segment", 510)):
        halo(s, m, cx, 13, 11, k)
        T(s, m, cx + 15, 3, x1, 14, t, px=7, c=F, b=True, al=LEFT); T(s, m, cx + 15, 14, x1, 24, d_, px=5.5, c=G4, i=True, al=LEFT)
    T(s, m, 22, 28, 165, 40, "Cautious is the dominant move", px=6, b=True, al=LEFT)
    for j, t in enumerate(("Attack", "Match", "Retreat")): T(s, m, 40 + j * 42, 41, 80 + j * 42, 50, t, px=5)
    grid = (("+0", "+40", "+60"), ("+41", "+65", "+77"), ("-25", "-20", "-15"))
    for i, (r_, l) in enumerate(zip(grid, ("Hard", "Soft", "Out"))):
        T(s, m, 2, 52 + i * 27, 38, 76 + i * 27, l, px=5.5, al=RIGHT)
        for j, v in enumerate(r_):
            on = i == 1 and j == 1
            RR(s, m, 40 + j * 42, 52 + i * 27, 79 + j * 42, 76 + i * 27, F if on else W, .15, None if on else G3, .5)
            T(s, m, 40 + j * 42, 52 + i * 27, 79 + j * 42, 76 + i * 27, v, px=6.5, c=W if on else INK, b=True)
    for i, (rx, cy, hh, c) in enumerate(((46, 44, 22, F), (36, 66, 20, light(F, .35)), (26, 86, 20, A), (15, 106, 18, light(F, .7)))):
        poly(s, m, ((215 - rx, cy - hh / 2), (215 + rx, cy - hh / 2), (215 + rx * .78, cy + hh / 2), (215 - rx * .78, cy + hh / 2)), c)
        a_, b_ = m.p((215, cy + hh / 2)); oval(s, a_, b_, 2 * rx * .78 * m.sx, c, rx * .36 * m.sy)
        a_, b_ = m.p((215, cy - hh / 2)); oval(s, a_, b_, 2 * rx * m.sx, light(c, .45), rx * .4 * m.sy)
    for i, (t, d_, yy) in enumerate((("6,000", "TAM", 38), ("800", "SAM", 60), ("140", "SOM", 82), ("40", "Today", 104))):
        T(s, m, 268, yy, 320, yy + 10, t, px=6.5, c=F, b=True, al=LEFT); T(s, m, 268, yy + 9, 320, yy + 18, d_, px=5.5, al=LEFT)
    RR(s, m, 345, 28, 450, 100, light(F, .55), .06); T(s, m, 345, 28, 450, 100, "~80% new space", px=7, c=W, b=True)
    RR(s, m, 453, 28, 503, 100, F, .1); T(s, m, 453, 28, 503, 100, "~20% from rival", px=6.5, c=W, b=True)
    RR(s, m, 345, 112, 510, 148, light(F, .92), .15, light(F, .6), .5)
    for a0, a1, c in ((-90, 0, F), (0, 270, G2)):
        poly(s, m, seg((364, 130), 7, 13, a0, a1, 16), c)
    RT(s, m, 382, 114, 508, 146, [[("Conversion", "b", F)], [("25% open, 4% rival", "")]], px=6, al=LEFT)
    shadow(RR(s, m, 8, 160, 508, 220, W, .14, G2, .5), 6, 2, 30)
    halo(s, m, 28, 190, 14, "cube")
    RT(s, m, 46, 164, 170, 216, [[("Cautious", "b", F), (" is the dominant move: wins in every case and avoids a price war.", "")]], px=5.5, al=LEFT)
    for cx, k, a, b in ((192, "bank", "~140 units", "by year five"), (302, "card", "$1,045", "real ARPU per unit"), (408, "coin", "+$31m", "incremental revenue")):
        halo(s, m, cx, 190, 16, k)
        RT(s, m, cx + 20, 170, cx + 88, 210, [[(a, "b", F)], [(b, "")]], px=6, al=LEFT)


def fact_cross(s, x, y, w, h):
    """Ficha com fundo que esmaece e contorno que some à direita; KPIs no topo e eixos em cruz com pontas de ponto. Alupar p.13."""
    m = FIT((0, 0, 510, 211), (x, y, w, h), 1.2)
    grad(R(s, m, 5, 5, 505, 208, TINT), ((0, light(F, .82)), (1, W)), 0)
    L(s, m, [(5, 5), (5, 208)], F, 1.25)
    fade_line(L(s, m, [(5, 5), (505, 5)], F, 1.25), ((0, F), (1, F, 0)))
    fade_line(L(s, m, [(5, 208), (505, 208)], F, 1.25), ((0, F), (1, F, 0)))
    for cx, a, b in ((100, "Capex total", "$444m"), (262, "Revenue (30 yrs)", "$75m/yr"), (430, "Length", "730 km")):
        T(s, m, cx - 80, 12, cx + 80, 34, a, px=13, c=D, b=True); T(s, m, cx - 80, 36, cx + 80, 54, b, px=11, c=D, b=True)
    L(s, m, [(38, 62), (476, 62)], F, 1.0, head="oval", tail="oval")
    L(s, m, [(258, 68), (258, 205)], F, 1.0, head="oval", tail="oval")
    left = (("Country:", "Region A"), ("Auction:", "Jun Y1"), ("Start est.:", "Jun Y5"), ("End:", "30 yrs after start"), ("Type:", "500 kV line + subs"))
    right = (("Length:", "~730 km"), ("Projects:", "4"), ("Capex est.:", "$444m"), ("Revenue est.:", "$75m"), ("Rev./capex:", "16.9%"), ("Index:", "CPI (annual)"))
    for i, (a, b) in enumerate(left):
        yy = 76 + i * 24
        T(s, m, 22, yy - 8, 120, yy + 12, a, px=9, i=True, al=LEFT); T(s, m, 140, yy - 8, 250, yy + 12, b, px=9, i=True, al=LEFT)
    for i, (a, b) in enumerate(right):
        yy = 70 + i * 23
        T(s, m, 268, yy - 8, 380, yy + 12, a, px=9, i=True, al=LEFT); T(s, m, 395, yy - 8, 500, yy + 12, b, px=9, i=True, al=LEFT)


def unit_columns(s, x, y, w, h):
    """Três colunas iguais: DRE curta, linha de caixa ligada a duas TIRs e heatmap de sensibilidade, sobre escuro. Alupar p.15."""
    m = FIT((0, 0, 510, 262), (x, y, w, h), 1.15)
    R(s, m, 0, 0, 510, 262, DK)
    def column(x0, x1, name, irr1, irr2, seed):
        wd = x1 - x0
        T(s, m, x0 + 4, 2, x1, 14, name, px=6.5, c=W, b=True, al=LEFT)
        L(s, m, [(x0, 28), (x1, 28)], W, 1.25)
        cols = [x0 + 36 + k * (wd - 36) / 6 for k in range(7)]
        for k in range(6):
            T(s, m, cols[k], 16, cols[k + 1], 27, f"Y{k + 1}", px=4.5, c=W, b=True)
        rnd = random.Random(seed)
        for i, r_ in enumerate(("EBITDA", "Tax", "Capex", "Debt")):
            yy = 30 + i * 13
            T(s, m, x0 + 2, yy, x0 + 36, yy + 12, r_, px=4.5, c=W, al=LEFT)
            for k in range(6):
                T(s, m, cols[k], yy, cols[k + 1], yy + 12, str(rnd.randint(20, 190) * (1 if i in (0,) else -1)), px=4.5, c=W)
        L(s, m, [(x0, 83), (x1, 83)], W, 1.25)
        grad(R(s, m, x0 + 1, 86, x1 - 1, 100, F, border=W, width=.75), ((0, F), (1, DK)), 0)
        T(s, m, x0 + 2, 86, x0 + 36, 100, "FCFE", px=4.5, c=W, b=True, al=LEFT)
        for k in range(6):
            T(s, m, cols[k], 86, cols[k + 1], 100, str(rnd.randint(1, 16)), px=4.5, c=W)
        a = x0 + 12; b = x1 - 12; ca, cb = x0 + wd * .3, x0 + wd * .7
        L(s, m, [(a, 100), (a, 124), (ca - 22, 124)], W, .5); L(s, m, [(b, 100), (b, 124), (cb + 22, 124)], W, .5)
        for cc, la, v in ((ca, "Real", irr1), (cb, "Nominal", irr2)):
            R(s, m, cc - 22, 111, cc + 22, 139, None, border=W, width=.5)
            T(s, m, cc - 22, 111, cc + 22, 122, la, px=4.5, c=W); T(s, m, cc - 22, 122, cc + 22, 138, v, px=7, c=W, b=True)
        poly(s, m, ((x0 + wd * .5 + 2, 118), (x0 + wd * .5 - 4, 126), (x0 + wd * .5, 126), (x0 + wd * .5 - 2, 132), (x0 + wd * .5 + 4, 124), (x0 + wd * .5, 124)), W)
        T(s, m, x0, 146, x1, 156, "% Debt", px=4.5, c=W, b=True)
        hx0, hy0, hx1, hy1 = x0 + 12, 158, x1, 260
        R(s, m, hx0, hy0, hx1, hy1, DK, border=W, width=.75)
        cw_ = (hx1 - hx0) / 6; ch_ = (hy1 - hy0) / 6
        T(s, m, x0 - 2, 200, x0 + 12, 215, "Kd", px=4.5, c=W, b=True)
        for j in range(5):
            T(s, m, hx0 + (j + 1) * cw_, hy0, hx0 + (j + 2) * cw_, hy0 + ch_, f"{70 + 5 * j}%", px=4.5, c=W, b=True)
        for i in range(5):
            T(s, m, hx0, hy0 + (i + 1) * ch_, hx0 + cw_, hy0 + (i + 2) * ch_, f"{8 + i}%", px=4.5, c=W, b=True)
            for j in range(5):
                t = (j + 4 - i) / 8
                R(s, m, hx0 + (j + 1) * cw_, hy0 + (i + 1) * ch_, hx0 + (j + 2) * cw_, hy0 + (i + 2) * ch_, ss.mix(dark(F, .6), F, t))
                T(s, m, hx0 + (j + 1) * cw_, hy0 + (i + 1) * ch_, hx0 + (j + 2) * cw_, hy0 + (i + 2) * ch_, f"{8 + j * .5 - i * .4:.1f}%", px=4.5, c=W)
    column(4, 165, "Unit A", "8.9%", "13.3%", 1); column(177, 338, "Unit B", "13.7%", "16.9%", 2); column(350, 506, "Unit C", "13.5%", "16.7%", 3)
    for xx in (171, 344):
        for a, b in ((30, 90), (110, 140), (165, 250)):
            L(s, m, [(xx, a), (xx, b)], F, .75)


def tick_ruler(s, x, y, w, h):
    """Régua fina de ticks com pontas de seta, bloco cinza dos pares e triângulos claro e escuro sobre a régua. Cosan p.10."""
    m = FIT((0, 0, 510, 236), (x, y, w, h), 1.15)
    c1, c2 = light(F, .35), D
    poly(s, m, ((26, 24), (32, 8), (38, 24)), c1, edge=INK, ew=.35); mold(s, m, 44, 7, 104, 24, px=7); T(s, m, 106, 7, 150, 24, "Start", px=7, al=LEFT)
    poly(s, m, ((208, 24), (214, 8), (220, 24)), c2, edge=INK, ew=.35); mold(s, m, 226, 7, 286, 24, px=7); T(s, m, 288, 7, 330, 24, "Now", px=7, al=LEFT)
    R(s, m, 398, 9, 438, 22, G4); mold(s, m, 444, 7, 502, 24, px=7)
    rows = ((45, "Penetration:", "0.0%", "80.0%", (17, 80), (146, 10.0, "10.0%"), (190, 19.0, "19.0%")),
            (108, "Cost per customer:", "0", "1,400", (350, 433), (45, 250, "250"), (236, 800, "800")),
            (175, "Unit margin:", "0.0%", "70.0%", (90, 175), (225, 30, "30.0%"), (345, 50, "50.0%")))
    for yy, t, lo, hi, band, m1, m2 in rows:
        T(s, m, 22, yy - 8, 300, yy + 9, t, px=10, b=True, i=True, al=LEFT)
        ry = yy + 38
        sp = R(s, m, 28 + 4, ry, 488, ry + 9, G3, border=G4, width=.35)
        pattern(sp, "narVert", G4, W)
        R(s, m, 28 + band[0], ry - 3, 28 + band[1], ry + 12, G4, border=INK, width=.35)
        for xe_, sgn in ((30, -1), (490, 1)):
            poly(s, m, ((xe_, ry - 5), (xe_, ry + 14), (xe_ + sgn * -10, ry + 4.5)), G3, edge=INK, ew=.35)
        T(s, m, 2, ry - 24, 56, ry - 10, lo, px=8); T(s, m, 464, ry - 24, 512, ry - 10, hi, px=8)
        for mk, col in ((m1, c1), (m2, c2)):
            cx = 28 + mk[0]
            poly(s, m, ((cx - 6, ry + 8), (cx, ry - 10), (cx + 6, ry + 8)), col, edge=INK, ew=.35)
            T(s, m, cx - 26, ry - 25, cx + 26, ry - 11, mk[2], px=8)


def row_leaders(s, x, y, w, h):
    """Tabela contornada sobre escuro com linhas-chave em cor; fio grosso sai da borda e termina em losango no insight. Cosan p.11."""
    m = FIT((0, 0, 510, 180), (x, y, w, h), 1.2)
    R(s, m, 0, 0, 510, 180, DK)
    R(s, m, 2, 28, 300, 168, None, border=W, width=.5)
    for a, b, t in ((115, 205, "Pre-offer"), (220, 300, "Post-offer"), (305, 510, "Key insights")):
        L(s, m, [(a, 14), (b, 14)], W, .5, dot=True)
        T(s, m, a, 2, b, 13, t, px=6, c=W, b=True, al=CEN if a < 300 else LEFT)
    cols = ((115, "Shares"), (160, "Stake"), (205, "IPO"), (232, "Shares"), (270, "Stake"))
    for xx, t in cols: T(s, m, xx - 16, 16, xx + 26, 27, t, px=4.5, c=W)
    rows = (("Controlling holders", "628", "88.0%", "(90)", "538", "75.4%", True), ("Holding A", "486", "68.0%", "-", "486", "68.0%", False), ("Holding B", "143", "20.0%", "(90)", "53", "7.4%", False),
            ("Non-controlling", "86", "12.0%", "114", "176", "24.6%", True), ("Financial investors", "86", "12.0%", "(24)", "62", "8.6%", False), ("New investors", "-", "0.0%", "114", "114", "16.0%", True), ("Total shares", "714", "100%", "-", "714", "100%", False))
    y0 = 36
    key_y = []
    for i, r_ in enumerate(rows):
        yy = y0 + i * 19
        c = A if r_[6] else W
        T(s, m, 6, yy, 100, yy + 14, r_[0], px=5, c=c, b=r_[6] or i == 6, al=LEFT)
        for (xx, _), v in zip(cols, r_[1:6]):
            T(s, m, xx - 16, yy, xx + 26, yy + 14, v, px=5, c=c, b=r_[6] or i == 6)
        if r_[6]: key_y.append(yy + 7)
    for yy, t, b in zip(key_y, ("Partial sale keeps control", "Proceeds cut holding debt", "Free float backed by demand"), ("The holder sells a slice and keeps most of the rights after the offer.", "No primary funds, all cash goes to the holders and their debt.", "Book covered three times by long-only and foreign investors.")):
        L(s, m, [(300, yy), (336, yy)], A, 2.0)
        dia(s, m, 340, yy, 4.5, A)
        T(s, m, 348, yy - 8, 508, yy + 7, t, px=7, c=A, b=True, al=LEFT)
        T(s, m, 348, yy + 7, 508, yy + 33, b, px=5.5, c=W, al=LEFT, an=TOP)


def ff_column(s, x, y, w, h):
    """Football field dentro da tabela: barras flutuantes em degradê numa coluna, faixa e tracejado de preço por todas as linhas. Kering p.20. No slide real, as barras podem vir de gráfico nativo empilhado."""
    m = FIT((0, 0, 510, 233), (x, y, w, h), 1.15)
    for a, b, t in ((228, 290, "Value"), (290, 352, "Implied")):
        T(s, m, a, 0, b, 12, t, px=5.5, b=True); L(s, m, [(a + 4, 12), (b - 4, 12)], INK, .35)
    R(s, m, 0, 13, 510, 25, INK)
    T(s, m, 0, 13, 225, 25, "Implied share price value", px=5.5, c=W, b=True)
    for a, t in ((228, "Low"), (259, "High"), (290, "Low"), (321, "High")): T(s, m, a, 13, a + 31, 25, t, px=5, c=W, b=True)
    T(s, m, 356, 13, 505, 25, "Comments", px=5.5, c=W, b=True, al=LEFT)
    R(s, m, 165, 25, 195, 232, light(A, .82))
    rows = (("Analyst targets", 165, 190, "49", "70"), ("52-week range", 160, 187, "45", "59"), ("DDM sensitivity", 128, 158, "21", "41"), ("Precedent deals", 136, 203, "27", "80"), ("P/E comps", 160, 195, "43", "74"), ("EV/EBITDA comps", 145, 175, "33", "58"), ("DCF multiples", 165, 185, "50", "65"))
    for i, (n, a, b, lo, hi) in enumerate(rows):
        y0 = 25 + i * 29.5
        L(s, m, [(0, y0 + 29.5), (510, y0 + 29.5)], G2, .35)
        T(s, m, 2, y0, 108, y0 + 29, n, px=5, c=G4, b=True, al=RIGHT)
        grad(R(s, m, a, y0 + 6, b, y0 + 23, INK), ((0, INK), (1, G3)), 0)
        T(s, m, a - 22, y0 + 6, a - 1, y0 + 23, lo, px=5, al=RIGHT); T(s, m, b + 1, y0 + 6, b + 22, y0 + 23, hi, px=5, al=LEFT)
        for k in range(4):
            T(s, m, 228 + k * 31, y0, 259 + k * 31, y0 + 29, f"{(i + 3) * (k + 2) * 7:,}", px=5)
        RT(s, m, 356, y0 + 2, 506, y0 + 28, [[(f"${lo}-{hi}/sh", "b"), (" sets a clean anchor for this method", "")]], px=5, al=LEFT)
    L(s, m, [(178, 25), (178, 232)], A, .75, dash=True)


def diamond_rail(s, x, y, w, h):
    """Fio fino com tampas nas pontas, três losangos com ícone e colchetes tracejados de nó a nó com legenda. Intelbras p.7."""
    m = FIT((0, 5, 500, 145), (x, y, w, h), 1.2)
    L(s, m, [(8, 63), (492, 63)], F, .75)
    for xx in (8, 492): L(s, m, [(xx, 56), (xx, 70)], F, .75)
    for cx, k, t, al, tx0, tx1, ty in ((60, "link", "Integrated portfolio", LEFT, 3, 150, 15), (250, "net", "Aligned incentives", CEN, 170, 330, 18), (450, "cash", "Cross-sell", RIGHT, 370, 497, 15)):
        dia(s, m, cx, 63, 33, light(F, .82), F, 1.0)
        ico(s, m, cx, 63, 30, k, INK, .75)
        T(s, m, tx0, ty - 9, tx1, ty + 9, t, px=13, al=al)
    L(s, m, [(58, 100), (58, 110), (248, 110), (248, 100)], F, .75, dash=True)
    L(s, m, [(252, 100), (252, 110), (442, 110), (442, 100)], F, .75, dash=True)
    T(s, m, 58, 111, 248, 141, "Three units sold through the same channel", px=11)
    T(s, m, 252, 111, 442, 141, "A single project creates demand for all units", px=11)


def treemap_pair(s, x, y, w, h):
    """Dois retângulos iguais divididos com vãos brancos, antes e depois, cor fixa por acionista. Sabesp p.16."""
    m = FIT((0, 0, 510, 291), (x, y, w, h), 1.15)
    def tile(x0, y0, x1, y1, c, pc, n):
        R(s, m, x0, y0, x1, y1, c)
        T(s, m, x0 + 8, y0 + 8, x1 - 4, y0 + 30, pc, px=15, c=W, b=True, al=LEFT)
        T(s, m, x0 + 6, y1 - 34, x1 - 4, y1 - 4, n, px=12, c=W, al=LEFT, an=MSO_ANCHOR.BOTTOM)
    tile(7, 13, 123, 286, light(F, .35), "50.3%", "State")
    tile(125, 13, 241, 286, D, "49.7%", "Free float")
    tile(264, 13, 500, 195, D, "67.0%", "Free float")
    tile(264, 197, 391, 286, light(F, .35), "18.0%", "State")
    tile(393, 197, 500, 286, F, "15.0%", "New strategic")


def icon_legend(s, x, y, w, h):
    """Duas colunas 100% afastadas, seta fina na cor da faixa com variação no meio e legenda de ícones à esquerda. RD p.3. No slide real, usar gráfico nativo empilhado."""
    m = FIT((0, 0, 450, 445), (x, y, w, h), 1.3)
    cols = (("Line D", "shield", light(F, .25), "11.6%", "11.9%", "+18.1%", 38, 83), ("Line C", "pill", F, "22.4%", "20.8%", "+6.6%", 83, 167), ("Line B", "flask", dark(F, .3), "23.9%", "25.5%", "+22.8%", 167, 258), ("Line A", "doc", D, "41.9%", "41.5%", "+13.9%", 258, 415))
    T(s, m, 20, 8, 110, 26, "Services", px=10, c=F, b=True)
    R(s, m, 148, 12, 182, 30, D); T(s, m, 148, 12, 182, 30, "0.2%", px=7.5, c=W, b=True)
    R(s, m, 386, 12, 420, 30, D); T(s, m, 386, 12, 420, 30, "0.3%", px=7.5, c=W, b=True)
    for name, k, c, a, b, g, y0, y1 in cols:
        R(s, m, 129, y0, 199, y1 - 1, c); T(s, m, 129, y0, 199, y1 - 1, a, px=8, c=W, b=True)
        R(s, m, 368, y0, 438, y1 - 1, c); T(s, m, 368, y0, 438, y1 - 1, b, px=8, c=W, b=True)
        cy = (y0 + y1) / 2
        L(s, m, [(216, cy), (356, cy)], c, 1.0, tail="triangle")
        R(s, m, 256, cy - 10, 316, cy + 10, W)
        T(s, m, 256, cy - 10, 316, cy + 10, g, px=9.5, c=c, b=True)
        dc = cy - 14
        shadow(disc(s, m, 65, dc, 20, c), 3, 1.5, 30)
        ico(s, m, 65, dc, 24, k, W, .75)
        T(s, m, 5, dc + 21, 125, dc + 40, name, px=10, c=c, b=True)
    T(s, m, 129, 420, 199, 442, "Year A", px=10); T(s, m, 368, 420, 438, 442, "Year B", px=10)


def scenario_range(s, x, y, w, h):
    """Placa em degradê com três casos, bullets alinhados e linhas de faixa com brilho no centro, sobre escuro. Vibra p.40."""
    m = FIT((0, 0, 480, 480), (x, y, w, h), 1.4)
    R(s, m, 0, 0, 480, 480, DK)
    Lm = light(A, .15)
    grad(R(s, m, 3, 5, 477, 82, D), ((0, dark(D, .4)), (.6, D), (1, F)), 340)
    cases = ((83, "Bear", "22.9%", "2.3x"), (240, "Base", "28.5%", "2.8x"), (400, "Bull", "33.2%", "3.2x"))
    for cx, t, i_, mo in cases:
        T(s, m, cx - 70, 10, cx + 70, 30, t + " Case", px=11, c=W, b=True)
        T(s, m, cx - 60, 36, cx - 2, 54, i_, px=12, c=Lm, b=True); T(s, m, cx + 2, 36, cx + 60, 54, mo, px=12, c=W, b=True)
        T(s, m, cx - 60, 54, cx - 2, 72, "IRR", px=9, c=W); T(s, m, cx + 2, 54, cx + 60, 72, "MOIC", px=9, c=W)
    bl = (("Weaker sector growth", "Less multiple expansion", "Limited synergies", "Fewer sites join"), ("Steady, healthy growth", "Same entry multiple", "Partial synergies", "Expected sites join"), ("Outpaced growth", "Higher exit multiple", "Strong synergies", "More sites join"))
    for (cx, *_), col in zip(cases, bl):
        for i, t in enumerate(col):
            yy = 92 + i * 34
            T(s, m, cx - 68, yy, cx - 58, yy + 26, "-", px=9, c=W)
            T(s, m, cx - 56, yy, cx + 76, yy + 26, t, px=8.5, c=W, al=LEFT)
    L(s, m, [(3, 232), (477, 232)], W, .75)
    L(s, m, [(111, 232), (111, 470)], W, .5)
    for cx, t in ((172, "Bear"), (285, "Base"), (408, "Bull")): T(s, m, cx - 25, 235, cx + 25, 250, t, px=7, c=G3)
    rows = (("Exit EV/EBITDA", "8.0x", "9.5x", "9.0x", "+1.0x"), ("Exit revenue", "230", "269", "246", "+40"), ("Exit EBITDA", "9.7", "12.1", "10.7", "+2.4"), ("Exit leverage", "0.25x", "0.00x", "0.14x", "(0.14x)"))
    for i, (n, lo, hi, ba, rg) in enumerate(rows):
        y0 = 253 + i * 58
        T(s, m, 3, y0, 106, y0 + 30, n, px=8, c=W, al=RIGHT)
        T(s, m, 140, y0, 180, y0 + 30, lo, px=8, c=W, al=RIGHT)
        grad(R(s, m, 184, y0, 396, y0 + 30, D, border=G4, width=.25), ((0, DK), (.5, F), (1, DK)), 0)
        L(s, m, [(290, y0 + 10), (290, y0 + 20)], W, .5)
        T(s, m, 400, y0, 440, y0 + 30, hi, px=8, c=W, al=LEFT)
        T(s, m, 442, y0, 480, y0 + 30, rg, px=6.5, c=G3)
        T(s, m, 260, y0 + 31, 320, y0 + 46, ba, px=7, c=Lm)


def ghost_wall(s, x, y, w, h):
    """Duas grades 4x2 de logos: a de cima acesa em moldura tracejada escura com sombra, a de baixo apagada. BTG p.30."""
    m = FIT((0, 0, 480, 395), (x, y, w, h), 1.3)
    shadow(R(s, m, 7, 10, 470, 183, W, border=D, dash=True, width=1.0), 6, 2, 35)
    L(s, m, [(470, 22), (480, 22)], D, .75, tail="diamond")
    R(s, m, 7, 213, 470, 385, G1, border=light(F, .6), dash=True, width=.75)
    for r_ in range(2):
        for k in range(4):
            x0 = 22 + k * 112
            mold(s, m, x0, 28 + r_ * 76, x0 + 96, 86 + r_ * 76, px=11, fill=G3, c=INK)
            mold(s, m, x0, 230 + r_ * 76, x0 + 96, 288 + r_ * 76, px=11, fill=G2, c=G3, alpha=45)


def _iso(s, m, cx, base, wd, hh, top, side, front):
    """Bloco isométrico: base é o y do canto da frente."""
    q = wd * .5; k = wd * .25
    poly(s, m, ((cx - q, base - k - hh), (cx, base - 2 * k - hh), (cx + q, base - k - hh), (cx, base - hh)), top)
    poly(s, m, ((cx - q, base - k - hh), (cx, base - hh), (cx, base), (cx - q, base - k)), front)
    poly(s, m, ((cx + q, base - k - hh), (cx, base - hh), (cx, base), (cx + q, base - k)), side)


def _cyl(s, m, cx, base, wd, hh, c):
    grad(R(s, m, cx - wd / 2, base - hh, cx + wd / 2, base, c), ((0, dark(c, .25)), (.5, light(c, .3)), (1, dark(c, .35))), 0)
    a, b = m.p((cx, base)); oval(s, a, b, wd * m.sx, dark(c, .3), wd * .42 * m.sy)
    a, b = m.p((cx, base - hh)); oval(s, a, b, wd * m.sx, light(c, .55), wd * .42 * m.sy)


def process_chain(s, x, y, w, h):
    """Sete ilustrações no mesmo ângulo, feitas com blocos isométricos, setas finas, nome e duas linhas de risco. Sabesp p.41. Blocos simplificam as ilustrações 3D do original."""
    m = FIT((0, 0, 510, 165), (x, y, w, h), 1.1)
    T(s, m, 14, 0, 300, 12, "Key risk and cost per stage", px=7, c=G4, i=True, al=LEFT)
    names = ("Intake", "Pumping", "Mixing", "Settling", "Treating", "Storage", "Delivery")
    r1 = ("Supply risk", "Power outage", "Process failure", "Low efficiency", "Contamination", "Quality loss", "Water loss")
    r2 = ("Upkeep", "Energy cost", "Labour cost", "Sludge cost", "Compliance", "Infrastructure", "Maintenance")
    gs, gf = G4, G3
    for i, n in enumerate(names):
        cx = 38 + i * 72.5
        _iso(s, m, cx, 90, 60, 5, G1, gs, gf)
        if i in (0, 2):
            _iso(s, m, cx - 8, 72, 28, 6, light(F, .55), F, dark(F, .2)); _iso(s, m, cx + 12, 80, 22, 10, G2, gs, gf)
        elif i in (1,):
            _cyl(s, m, cx, 76, 26, 18, G3); _iso(s, m, cx + 14, 82, 14, 8, F, dark(F), D)
        elif i in (3, 5):
            _cyl(s, m, cx, 76, 36, 16, light(F, .6) if i == 3 else G2)
        elif i == 4:
            _cyl(s, m, cx - 8, 74, 22, 24, G2); _iso(s, m, cx + 14, 80, 20, 18, light(F, .55), F, dark(F, .2))
        else:
            _iso(s, m, cx - 9, 78, 20, 30, light(F, .75), light(F, .4), F); _iso(s, m, cx + 10, 82, 20, 20, G2, gs, gf)
        T(s, m, cx - 36, 96, cx + 36, 112, n, px=7, b=True)
        ox_ = 12 if i == 0 else 0
        T(s, m, cx - 30 + ox_, 116, cx + 38, 136, r1[i], px=6.5, c=A, b=True, al=LEFT)
        T(s, m, cx - 30 + ox_, 140, cx + 38, 160, r2[i], px=6.5, c=D, b=True, al=LEFT)
        if i < 6:
            L(s, m, [(cx + 30, 60), (cx + 41, 60)], F, .75, tail="triangle", sz="sm")
    for yy, c_, k in ((126, A, "shield"), (150, D, "coin")):
        disc(s, m, 12, yy, 6, c_); ico(s, m, 12, yy, 7, k, W, .35)


def hex_serpentine(s, x, y, w, h):
    """Fio grosso entra pela esquerda e sai pela direita com curvas de quarto de círculo, passando por hexágonos com aba de ano. RD p.67."""
    m = FIT((0, 0, 510, 231), (x, y, w, h), 1.15)
    wd = 1.75
    path = [(0, 20), (392, 20)] + arc((392, 62), 42, -90, 90)[1:] + [(115, 105)] + arc((115, 145), 40, -90, -180)[1:] + [(75, 148)] + arc((115, 148), 40, 180, 90)[1:] + [(510, 188)]
    L(s, m, path, F, wd)
    items = ((80, 20, "Y1", "Founder A", "starts in the city", 0), (195, 20, "Y2", "Founder B", "starts in the city", 0), (308, 20, "Y3", "Listing", "of the first firm", 0), (425, 62, "Y4", "Rival", "IPO raises $655m", 0),
             (352, 105, "Y5", "Merger", "of both firms", 0), (255, 105, "Y6", "New unit", "bought", 1), (155, 105, "Y7", "New rule", "for the sector", 0), (75, 148, "Y8", "Add-on", "acquired", 0),
             (198, 188, "Y9", "Venture arm", "launched", 1), (318, 188, "Y10", "New services", "allowed", 0), (440, 188, "Y11", "New name", "for the group", 1))
    for cx, cy, yr, a, b, logo in items:
        P = ngon(cx, cy, 21, 6, 0)
        poly(s, m, P, W if logo else G2, edge=F, ew=.75)
        T(s, m, cx - 16, cy - 10, cx + 16, cy + 6, "[logo]" if logo else "[foto]", px=6, c=G4, i=True)
        R(s, m, cx - 12, cy + 12, cx + 12, cy + 22, F); T(s, m, cx - 12, cy + 12, cx + 12, cy + 22, yr, px=5.5, c=W, b=True)
        if cx == 425:
            RT(s, m, 450, cy - 14, 508, cy + 12, [[(a, "b", F)], [(b, "")]], px=6)
        elif cx == 75:
            RT(s, m, 2, cy - 12, 52, cy + 12, [[(a, "b", F)], [(b, "")]], px=6)
        else:
            RT(s, m, cx - 44, cy + 23, cx + 44, cy + 42, [[(a, "b", F), (" " + b, "")]], px=6)


def _tower(s, m, cx, base, ht, col, alpha, wd=.5):
    """Torre de transmissão em arame: mastro treliçado e três braços."""
    W_ = ht * .19
    P = lambda t: (W_ * (1 - t) ** 1.6 + ht * .012)
    Yt = lambda t: base - ht * t
    for sg in (-1, 1):
        L(s, m, [(cx + sg * P(i / 10), Yt(i / 10)) for i in range(11)], col, wd, alpha=alpha)
    for i in range(10):
        a, b = i / 10, (i + 1) / 10
        L(s, m, [(cx - P(a), Yt(a)), (cx + P(b), Yt(b))], col, wd * .7, alpha=alpha)
        L(s, m, [(cx + P(a), Yt(a)), (cx - P(b), Yt(b))], col, wd * .7, alpha=alpha)
        L(s, m, [(cx - P(b), Yt(b)), (cx + P(b), Yt(b))], col, wd * .6, alpha=alpha)
    ends = []
    for t, sp_ in ((.97, .28), (.82, .4), (.67, .3)):
        yy = Yt(t)
        tip = ht * sp_
        for sg in (-1, 1):
            L(s, m, [(cx + sg * P(t), yy), (cx + sg * tip, yy - ht * .01)], col, wd, alpha=alpha)
            L(s, m, [(cx + sg * P(t), yy + ht * .05), (cx + sg * tip, yy - ht * .01)], col, wd, alpha=alpha)
            n = 4
            for j in range(n):
                u = (j + .5) / n
                xa = cx + sg * (P(t) + (tip - P(t)) * u)
                L(s, m, [(xa, yy - ht * .005), (xa + sg * ht * .02, yy + ht * .04 * (1 - u))], col, wd * .6, alpha=alpha)
            L(s, m, [(cx + sg * tip, yy), (cx + sg * tip, yy + ht * .035)], col, wd, alpha=alpha)
            ends.append((cx + sg * tip, yy + ht * .035))
    return ends


def linework_cover(s, x, y, w, h):
    """Capa escura com o objeto do setor em arame, três tamanhos recuando à esquerda e cabos entre eles; bloco de marca no canto. Alupar p.1."""
    m = FIT((0, 0, 510, 287), (x, y, w, h), 1.1)
    bg = dark(D, .6)
    R(s, m, 0, 0, 510, 287, bg)
    col = light(F, .55)
    e1 = _tower(s, m, 35, 268, 58, col, 30, .35)
    e2 = _tower(s, m, 122, 268, 118, col, 45, .35)
    e3 = _tower(s, m, 385, 272, 262, col, 85, .5)
    for k in (0, 2, 4, 1, 3, 5):
        a, b, c = e1[k], e2[k], e3[k]
        for u, v in ((a, b), (b, c)):
            mid = ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2 + 5)
            L(s, m, [u, ((u[0] + mid[0]) / 2, (u[1] + mid[1]) / 2 + 1.5), mid, ((v[0] + mid[0]) / 2, (v[1] + mid[1]) / 2 + 1.5), v], col, .25, alpha=45)
    for yy in range(258, 287, 8):
        L(s, m, [(0, yy), (510, yy)], col, .2, alpha=18)
    mold(s, m, 45, 20, 170, 58, px=12, fill=G4, c=W)
    T(s, m, 40, 62, 205, 88, "EVENT NAME", px=14, c=W, b=True)
    L(s, m, [(10, 89), (205, 89)], W, .75)
    mold(s, m, 50, 97, 105, 128, px=8, fill=G4, c=W); L(s, m, [(113, 97), (113, 128)], W, .5); mold(s, m, 120, 97, 175, 128, px=8, fill=G4, c=W)
    T(s, m, 10, 266, 180, 276, "Author A | a@school.edu", px=5.5, c=W, b=True, al=LEFT)
    T(s, m, 10, 276, 180, 286, "Author B | b@school.edu", px=5.5, c=W, b=True, al=LEFT)




MAPA = {
    "Core and Near Core twin rings with fanned product notes": "core_rings",
    "Tinted pentagon summary field pointing into rationale": "pentagon_field",
    "Capsule columns with icon disc and logo stack": "capsule_columns",
    "Option chain with fading pills and cards": "option_chain",
    "Staged deal columns closing on a final structure panel": "staged_deal",
    "Logo treemap zoomed out from a sliver into a second treemap": "treemap_zoom",
    "Stepped lifecycle silhouette with numbered phase key": "lifecycle",
    "Spine timeline with alternating notched banners": "spine_banners",
    "Numbered badges on radar vertices keyed to a list": "radar_badges",
    "Phase columns over a benefit area and effort curve": "phase_area",
    "Long chain above short chain to show disintermediation": "long_short_chain",
    "Twin vertical chains with check and cross verdict rows": "twin_verdict",
    "Two-tone arc arrows as a two-engine flywheel": "flywheel",
    "Serpentine era timeline with diamonds": "serpentine_eras",
    "Wire globe with leaders to tiered activity rows": "wire_globe",
    "Step columns hanging from a ticked rail": "step_columns",
    "SWOT cards with corner sashes around a quartered ring": "swot_ring",
    "Deadline columns ending in a darkening slanted band": "deadline_band",
    "Sorted bars with colour break and dashed average brackets": "sorted_bars",
    "Age pyramids as paired solid vase silhouettes": "vase_pyramids",
    "Profit pool Marimekko with share as width": "marimekko",
    "Charts as operands in a visual equation": "chart_equation",
    "Numbered market columns with tangent-linked circles": "tangent_circles",
    "Lit driver tree with crosses between siblings": "driver_tree",
    "Cohort lines with a vertical gradient legend": "cohort_lines",
    "Thick-rim icon wheel with a throat into a revenue panel": "wheel_throat",
    "Subtractive funnel of centred offset plates": "plate_funnel",
    "Twin logo fans into a colour-keyed mirrored logic column": "logic_column",
    "Ellipsis exhibit headers reading as one sentence": "ellipsis_heads",
    "Three exhibit cards above an anchoring history footer": "cards_over_ribbon",
    "ECG spike timeline in a dashed frame": "ecg_timeline",
    "Halo-icon exhibit heads over a floating takeaway tray": "halo_tray",
    "Project fact sheet on arrow-tipped cross axes": "fact_cross",
    "Three unit columns: mini income statement, wired returns, sensitivity": "unit_columns",
    "Tick ruler with triangle markers and a peer range block": "tick_ruler",
    "Table rows wired to insight headlines with diamond leaders": "row_leaders",
    "Football field as a table column": "ff_column",
    "Diamond nodes on a capped rail with dashed span brackets beneath": "diamond_rail",
    "Before and after ownership treemap pair": "treemap_pair",
    "Icon-disc legend column with growth arrows between paired stacks": "icon_legend",
    "Scenario glow header over bullets and range rows": "scenario_range",
    "Lit and ghost logo walls in dashed frames": "ghost_wall",
    "Illustrated process chain with a risk row beneath": "process_chain",
    "Serpentine rail threaded through hexagon photos with year tabs": "hex_serpentine",
    "Receding sector-object linework cover": "linework_cover",
}

SLIDES = [
    ("Portfolios read as one structured field", "Rings, capsules and tinted fields group what belongs together",
     [("Twin rings", "Senior p.14", core_rings), ("Pentagon field", "Vasta p.3", pentagon_field), ("Capsule columns", "Vasta p.12", capsule_columns),
      ("Option chain", "Vasta p.25", option_chain), ("Staged deal", "Vibra p.37", staged_deal), ("Treemap zoom", "3R Petroleum p.5", treemap_zoom)]),
    ("Sequences that stay on one axis", "Timelines, phases and scorecards keyed to one list",
     [("Stepped lifecycle", "3R Petroleum p.5", lifecycle), ("Spine banners", "3R Petroleum p.24", spine_banners), ("Radar badges", "3R Petroleum p.101", radar_badges),
      ("Phases over a curve", "AB InBev p.81", phase_area), ("Long and short chain", "AB InBev p.101", long_short_chain), ("Twin verdict chains", "BTG Pactual p.35", twin_verdict)]),
    ("Loops, eras and ticked rails", "One continuous stroke carries the reading order",
     [("Two-engine flywheel", "BTG Pactual p.48", flywheel), ("Serpentine eras", "BTG Pactual p.112", serpentine_eras), ("Wire globe", "CSN p.5", wire_globe),
      ("Step columns on a rail", "CSN Liability p.9", step_columns), ("SWOT with sashes", "Meliuz p.71", swot_ring), ("Deadline band", "Sabesp p.11", deadline_band)]),
    ("Charts built as diagrams", "Shape carries the message; real slides use native charts",
     [("Sorted bars with brackets", "Sabesp p.79", sorted_bars), ("Vase pyramids", "RD Saúde p.9", vase_pyramids), ("Profit pool", "RD Saúde p.27", marimekko),
      ("Charts as operands", "RD Saúde p.49", chart_equation), ("Tangent circles", "RBI p.28", tangent_circles), ("Lit driver tree", "RBI p.30", driver_tree)]),
    ("Wheels, funnels and mirrored logic", "A shape leads the eye from the overview into the argument",
     [("Cohort lines", "Nubank p.15", cohort_lines), ("Wheel with a throat", "Nubank p.2", wheel_throat), ("Plate funnel", "Nubank p.13", plate_funnel),
      ("Mirrored logic column", "Nubank p.33", logic_column), ("Ellipsis headers", "Sabesp p.17", ellipsis_heads), ("Cards over a ribbon", "Sabesp p.2", cards_over_ribbon)]),
    ("Fact sheets and wired tables", "Lines tie each number to what it means",
     [("ECG timeline", "RD Saúde p.72", ecg_timeline), ("Halo tray", "Vasta p.24", halo_tray), ("Fact sheet on a cross", "Alupar p.13", fact_cross),
      ("Unit columns", "Alupar p.15", unit_columns), ("Tick rulers", "Cosan p.10", tick_ruler), ("Row leaders", "Cosan p.11", row_leaders)]),
    ("Valuation and ownership at a glance", "Bars, tiles and rails replace long tables",
     [("Football field column", "Kering p.20", ff_column), ("Diamond rail", "Intelbras p.7", diamond_rail), ("Treemap pair", "Sabesp p.16", treemap_pair),
      ("Icon legend stacks", "RD Saúde p.3", icon_legend), ("Scenario ranges", "Vibra p.40", scenario_range), ("Lit and ghost walls", "BTG Pactual p.30", ghost_wall)]),
    ("Chains, rails and covers", "Long sequences and a cover with no photo",
     [("Process chain", "Sabesp p.41", process_chain), ("Hexagon serpentine", "RD Saúde p.67", hex_serpentine), ("Linework cover", "Alupar p.1", linework_cover)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the technique comes from the source.")
    ss.save(prs, OUT)
