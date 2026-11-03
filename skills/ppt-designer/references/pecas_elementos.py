"""Elementos do catálogo (nem profundidade nem gráfico), com conteúdo fictício. Copie a função e troque os textos.
Referência de cada um: references/catalogo/elementos-*.md. Número, notícia e citação no slide real vêm do roteiro.
Uso: python3 pecas_elementos.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402


def pline(s, m, pts, c, wd=1.25):
    for a, b in zip(pts, pts[1:]):
        ss.line(s, *m.p(a), *m.p(b), c, wd, dash=False)


def series(x0, x1, base, amp, n=46):
    """Linha de preço fictícia e determinística."""
    return [(x0 + (x1 - x0) * i / (n - 1), base - amp * (.35 * math.sin(i * .19) + .14 * math.sin(i * .71 + 1) + .07 * math.sin(i * 2.3) + 1.1 * (i / n) ** 2)) for i in range(n)]


def op(s, m, cx, cy, d, kind, c=F):
    """Operador grande desenhado com formas: + x = (peso visual sem texto gigante)."""
    t = d * .22
    if kind == "+":
        R(s, m, cx - d / 2, cy - t / 2, cx + d / 2, cy + t / 2, c); R(s, m, cx - t / 2, cy - d / 2, cx + t / 2, cy + d / 2, c)
    elif kind == "=":
        R(s, m, cx - d / 2, cy - d * .28, cx + d / 2, cy - d * .28 + t, c); R(s, m, cx - d / 2, cy + d * .28 - t, cx + d / 2, cy + d * .28, c)
    else:
        k = d * .5; e = t * .5
        poly(s, m, ((cx - k, cy - k + e), (cx - k + e, cy - k), (cx + k, cy + k - e), (cx + k - e, cy + k)), c)
        poly(s, m, ((cx + k, cy - k + e), (cx + k - e, cy - k), (cx - k, cy + k - e), (cx - k + e, cy + k)), c)


def verdict_bracket(s, x, y, w, h):
    """Veredito em T: preço, alvo, upside e TIR em um único traço. 3R p.6."""
    m = M((0, 0, 500, 240), (x, y, w, h))
    grad(R(s, m, 0, 0, 290, 240, D), ((0, D), (1, dark(F, .1))), 90)
    pline(s, m, series(10, 280, 150, 60), W, 1)
    ss.line(s, *m.p((10, 42)), *m.p((280, 42)), W, .75, dash=True)
    a = m.box(232, 30, 288, 54); rr(s, *a, F, .25); tx(s, *a, "$55.6", size=7, color=W, bold=True)
    R(s, m, 290, 0, 500, 240, G1); R(s, m, 495, 0, 500, 240, F); R(s, m, 290, 235, 500, 240, F)
    b = m.box(355, 10, 435, 40); rr(s, *b, F, .2); tx(s, *b, "BUY", size=11, color=W, bold=True)
    for lx, t1, t2 in ((296, "32.9", "Actual"), (448, "55.6", "Target")):
        tm(s, m, lx, 58, lx + 46, 76, t1, size=9, bold=True)
        tm(s, m, lx, 76, lx + 46, 92, t2, size=7)
    ss.line(s, *m.p((344, 68)), *m.p((446, 68)), INK, .75, dash=False)
    for xx in (344, 446): ss.line(s, *m.p((xx, 60)), *m.p((xx, 76)), INK, .75, dash=False)
    ss.line(s, *m.p((395, 68)), *m.p((395, 120)), INK, .75, dash=False)
    ss.line(s, *m.p((385, 120)), *m.p((405, 120)), INK, .75, dash=False)
    ss.text(s, *m.box(300, 124, 490, 150), [[("68.7%", {"bold": True, "color": F, "size": 10}), (" upside", {"color": INK, "size": 9})]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    ss.line(s, *m.p((395, 154)), *m.p((395, 196)), INK, .75, dash=False)
    for yy in (154, 196): ss.line(s, *m.p((385, yy)), *m.p((405, yy)), INK, .75, dash=False)
    ss.text(s, *m.box(300, 200, 490, 226), [[("35.6%", {"bold": True, "color": F, "size": 10}), (" IRR", {"color": INK, "size": 9})]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def formula_ops(s, x, y, w, h):
    """Fórmula com operadores grandes que deságua em tabela de resultado. 3R p.73."""
    m = M((0, 0, 560, 300), (x, y, w, h))
    for yy, hh, title, row, res in ((10, 125, "Cost of equity", ("4.4%", "+", "4.6", "x", "5%", "="), "15.0%"), (155, 125, "Cost of debt", ("8.4%", "+", "IPCA", None, None, "="), "13.2%")):
        R(s, m, 6, yy + 6, 316, yy + hh + 6, F); R(s, m, 0, yy, 310, yy + hh, G2)
        tm(s, m, 10, yy + 4, 300, yy + 26, title, size=8, bold=True, align=PP_ALIGN.LEFT)
        cx = 16
        for t in row:
            if t is None: continue
            if t in "+x=":
                op(s, m, cx + 7, yy + 72, 16, t); cx += 22
            else:
                tm(s, m, cx, yy + 56, cx + 62, yy + 88, t, size=9, align=PP_ALIGN.LEFT); cx += 56
        tm(s, m, cx - 2, yy + 56, 312, yy + 88, res, size=10, bold=True, color=F, align=PP_ALIGN.LEFT)
    poly(s, m, ((332, 30), (332, 270), (392, 150)), dark(F, .1))
    rows = (("Ke", "15.0%"), ("Kd", "13.2%"), ("Tax", "15.3%"), ("E/(D+E)", "72.5%"), ("WACC", "14.0%"))
    for i, (a, b) in enumerate(rows):
        yy = 45 + i * 42
        if i % 2: R(s, m, 405, yy, 556, yy + 42, G2)
        last = i == len(rows) - 1
        tm(s, m, 412, yy, 490, yy + 42, a, size=9, bold=last, align=PP_ALIGN.LEFT)
        tm(s, m, 480, yy, 550, yy + 42, b, size=9, bold=last, align=PP_ALIGN.RIGHT)
    R(s, m, 554, 45, 560, 255, F)


def decision_tree(s, x, y, w, h):
    """Árvore de decisão com o caminho escolhido aceso e folhas no nível do valor. CSN LM p.21."""
    m = M((0, 0, 620, 360), (x, y, w, h))
    R(s, m, 0, 0, 620, 360, G1, INK, width=.75)
    def path(pts, on):
        pline(s, m, pts, F if on else G3, 1.75 if on else 1)
    path(((310, 42), (310, 72), (140, 72), (140, 128)), True); path(((310, 72), (480, 72), (480, 128)), False)
    tm(s, m, 190, 48, 240, 68, "Yes", size=8, bold=True, color=F); tm(s, m, 385, 48, 435, 68, "No", size=8, color=G4)
    path(((160, 165), (160, 205), (70, 205), (70, 268)), True); path(((160, 205), (230, 205), (230, 248)), False)
    path(((460, 165), (460, 205), (390, 205), (390, 248)), True); path(((460, 205), (550, 205), (550, 280)), False)
    for cx, on in ((310, False), (160, True), (460, False)):
        px, py = m.p((cx, 72 if cx == 310 else 205))
        sp = s.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(px - .05), Inches(py - .05), Inches(.1), Inches(.1)); sp.shadow.inherit = False
        ss.paint(sp.fill, F if on else G4); sp.line.fill.background()
    for x0, y0, x1, y1, t in ((95, 12, 525, 42, "Does the buyer accept the first contract?"), (70, 130, 550, 165, "Does the buyer accept the second contract?")):
        R(s, m, x0, y0, x1, y1, W, INK, width=1); tm(s, m, x0, y0, x1, y1, t, size=8, bold=True)
    for x0, y0, t, on in ((20, 270, "14.9", True), (180, 250, "14.3", False), (340, 250, "14.7", True), (500, 282, "14.1", False)):
        R(s, m, x0, y0, x0 + 100, y0 + 62, W if on else G1, F if on else G3, width=1.25)
        tm(s, m, x0, y0 + 4, x0 + 100, y0 + 30, "NPV", size=8, color=INK if on else G4, bold=on)
        tm(s, m, x0, y0 + 30, x0 + 100, y0 + 58, t + " bn", size=9, bold=on, color=INK if on else G4)


def plan_tracker(s, x, y, w, h):
    """O mesmo plano volta antes de cada seção; só o passo atual fica aceso. CSN LM p.9."""
    bg = ss.rect(s, x, y, w, h, D)
    grad(bg, ((0, D), (1, dark(D, .35))), 90)
    n, active = 4, 1
    cw = w / n
    dim = lambda c: ss.mix(c, D, .68)
    ss.line(s, x + .05, y + .22, x + w - .05, y + .22, dim(W), .75, dash=False)
    names = ("Sell plants", "Sell stake", "Move assets", "Tender offer")
    vals = ("3.1 bn", "14.9 bn", "3.3 bn", "4.3 bn")
    for i in range(n):
        cx = x + i * cw
        on = i == active
        tc = W if on else dim(W)
        if on: ss.set_alpha(ss.rect(s, cx + .03, y + .32, cw - .06, h - .4, A), 18)
        for k in (.18, .82):
            ss.line(s, cx + cw * k, y + .12, cx + cw * k, y + .32, tc, .75, dash=False)
        tx(s, cx + cw * .18, y - .0, cw * .64, .18, f"Step {i + 1}", size=7, color=tc, italic=True)
        tx(s, cx + .06, y + .42, cw - .12, .5, names[i], size=9, color=tc, bold=on)
        for k, t in enumerate(("Fit", "Buyer")):
            b = (cx + cw * .13, y + 1.0 + k * .36, cw * .74, .28)
            ss.rect(s, *b, None, tc, width=.75); tx(s, *b, t, size=7, color=tc)
        tx(s, cx + .05, y + h - .55, cw - .1, .3, vals[i], size=9, color=tc, bold=True)


def scribble(s, cx, cy, w, h, seed=0, c=INK):
    """Anel pontilhado irregular, como um círculo feito à mão."""
    for k in range(2):
        pts = []
        for i in range(48):
            a = 2 * math.pi * i / 48
            r = 1 + .05 * math.sin(a * 3 + seed + k) + .04 * math.sin(a * 7 + 2 * seed + k * 2)
            pts.append((cx + w / 2 * r * math.cos(a), cy + h / 2 * r * math.sin(a)))
        sp = ss.poly(s, pts, W, c, 1.25)
        sp.fill.background()
        sp.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT


def scribble_link(s, x, y, w, h):
    """O mesmo número circulado na tabela e no gráfico, sem seta. Cosan p.14."""
    m = M((0, 0, 500, 300), (x, y, w, h))
    R(s, m, 0, 5, 500, 48, G1, F, width=1)
    tm(s, m, 14, 5, 260, 48, "Expanded net debt", size=9, bold=True, color=F, align=PP_ALIGN.LEFT)
    tm(s, m, 270, 5, 350, 48, "9,760", size=9, bold=True, color=F)
    tm(s, m, 390, 5, 480, 48, "7,420", size=9, bold=True, color=F)
    scribble(s, *m.p((435, 27)), 64 * m.sx, 34 * m.sy, 1)
    base = 280
    tops = ((30, 25.7, 0), (130, 25.7, 19.2), (230, 19.2, 10), (330, 10, 7.4), (430, 7.4, 0))
    labs = ("25,724", "(6,491)", "(9,289)", "(2,525)", "7,420")
    for (bx, a, b), lb in zip(tops, labs):
        y0, y1 = base - a * 8, base - b * 8
        grad(R(s, m, bx, y0, bx + 50, y1, F), ((0, D), (1, F)), 90)
        if lb == "7,420":
            tm(s, m, bx - 15, y0 - 24, bx + 65, y0 - 2, lb, size=8, bold=True)
            scribble(s, *m.p((bx + 25, y0 - 13)), 66 * m.sx, 28 * m.sy, 3)
        else:
            tm(s, m, bx - 15, y1 + 1 if lb != "25,724" else y0 - 22, bx + 65, y1 + 22 if lb != "25,724" else y0 - 2, lb, size=8)
    ss.line(s, *m.p((15, base)), *m.p((495, base)), G4, .75, dash=False)


def span_bracket(s, x, y, w, h):
    """Colchete sobre o vazio do gráfico: as notas ocupam os anos sem barras. Cosan p.12."""
    m = M((0, 0, 620, 290), (x, y, w, h))
    for bx, hh in ((10, 150), (55, 200)):
        R(s, m, bx, 270 - hh, bx + 32, 270, F)
    for bx, hh in ((540, 90), (585, 140)):
        R(s, m, bx, 270 - hh, bx + 30, 270, F)
    ss.line(s, *m.p((5, 270)), *m.p((618, 270)), G4, .75, dash=False)
    tm(s, m, 110, 6, 520, 30, "A 56-month gap with no deals", size=9, bold=True, color=F)
    ss.line(s, *m.p((110, 36)), *m.p((520, 36)), F, 1.25, dash=False)
    for xx in (110, 520):
        px, py = m.p((xx, 36))
        sp = s.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(px - .05), Inches(py - .05), Inches(.1), Inches(.1)); sp.shadow.inherit = False
        ss.paint(sp.fill, F); sp.line.fill.background()
    R(s, m, 110, 46, 520, 262, G1)
    for i, (a, b) in enumerate((("The rate shock closed the window: ", "funding moved to fixed income"), ("The market shrank: ", "delistings beat new listings"), ("Appetite fell further: ", "foreign outflows after a scandal"))):
        ss.text(s, *m.box(124, 56 + i * 68, 508, 118 + i * 68), [[(a, {"bold": True, "italic": True, "color": INK, "size": 8}), (b, {"italic": True, "color": F, "size": 8})]], anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def event_flags(s, x, y, w, h):
    """Eventos presos na linha de preço por hastes: compras de insiders. Cury p.22."""
    m = M((0, 0, 620, 280), (x, y, w, h))
    pts = series(10, 610, 215, 55, 70)
    pline(s, m, pts, F, 1)
    ss.line(s, *m.p((10, 262)), *m.p((610, 262)), G4, .75, dash=False)
    for i, t in enumerate(("2021", "2022", "2023", "2024", "2025")):
        tm(s, m, 20 + i * 120, 264, 110 + i * 120, 280, t, size=7)
    for idx, lab, val in ((6, "Buy", "2M"), (28, "Buy", "4M"), (50, "Buy", "6M"), (62, "Buy", "9M")):
        px, py = pts[idx]
        top = py - 95
        ss.line(s, *m.p((px, py)), *m.p((px, top + 44)), F, .75, dash=False)
        R(s, m, px - 7, top, px + 7, top + 44, T, F, width=.75)
        ss.line(s, *m.p((px, top - 6)), *m.p((px, top)), F, .75, dash=False)
        tm(s, m, px - 40, top - 38, px + 40, top - 7, f"{lab} {val}", size=7, bold=True)


def phase_windows(s, x, y, w, h):
    """A mesma janela de tempo cruza gráficos empilhados. Rede D'Or p.61."""
    m = M((0, 0, 500, 300), (x, y, w, h))
    for yy, pts, c in ((0, ((10, 90), (150, 95), (300, 80), (480, 20)), F), (0, ((10, 110), (150, 102), (300, 90), (480, 38)), A), (160, ((10, 110), (150, 72), (300, 40), (480, 58)), F)):
        pline(s, m, [(a, b + yy) for a, b in pts], c, 1.75)
    for yy in (130, 285):
        ss.line(s, *m.p((5, yy)), *m.p((495, yy)), G4, .75, dash=False)
        for i, t in enumerate(("2020", "2021", "2022", "2023")):
            tm(s, m, -20 + i * 155, yy + 1, 60 + i * 155, yy + 15, t, size=7)
    for yy, hh in ((4, 124), (160, 123)):
        ss.set_alpha(R(s, m, 150, yy, 320, yy + hh, A), 35)
        R(s, m, 150, yy, 320, yy + hh, None, F, dash=True)
    tm(s, m, 155, 8, 315, 34, "During the shock", size=9, color=INK, bold=True)


def formula_stairs(s, x, y, w, h):
    """Cada termo da fórmula desce em escada até a sua explicação. Mercado Libre p.94."""
    m = M((0, 0, 620, 270), (x, y, w, h))
    terms = (("Ad cost", 0, 80), ("Conversion", 92, 132), ("Price", 236, 58), ("Score", 306, 58))
    notes = ("Willingness to pay for ads", "Clicks that become purchases", "Revenue of the listed item", "Seller reputation and quality")
    for i, ((t, x0, wd), nt) in enumerate(zip(terms, notes)):
        tm(s, m, x0, 8, x0 + wd, 36, t, size=9, italic=True)
        R(s, m, x0, 38, x0 + wd, 42, F)
        if i < 3: tm(s, m, x0 + wd, 8, x0 + wd + 15, 36, "×", size=9, bold=True)
        cx = x0 + wd / 2
        yy = 228 - i * 50
        ss.line(s, *m.p((cx, 42)), *m.p((cx, yy)), F, .75, dash=False)
        px, py = m.p((cx, yy))
        sp = s.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(px - .05), Inches(py - .05), Inches(.1), Inches(.1)); sp.shadow.inherit = False
        ss.paint(sp.fill, A); sp.line.fill.background()
        tm(s, m, cx + 10, yy - 16, 620, yy + 16, nt, size=8, italic=True, align=PP_ALIGN.LEFT)
    tm(s, m, 366, 8, 386, 36, "=", size=9, bold=True)
    tm(s, m, 388, 8, 450, 36, "Rank", size=9, bold=True, italic=True)
    R(s, m, 388, 38, 450, 42, D)
    ss.line(s, *m.p((456, 24)), *m.p((476, 24)), INK, .75, dash=False)
    tm(s, m, 480, 2, 620, 50, "Best rank wins the first page", size=8, italic=True, align=PP_ALIGN.LEFT)


def square_rating(s, x, y, w, h):
    """Nota em cinco quadrados, com o último preenchido na proporção. AB InBev p.50."""
    m = M((0, 0, 560, 300), (x, y, w, h))
    rows = ((("How ", False), ("intuitive", True), (" is the platform?", False)), 5.0), ((("How ", False), ("quick", True), (" is the response?", False)), 4.8), ((("How do you rate ", False), ("service", True), ("?", False)), 4.1)
    for i, (q, v) in enumerate(rows):
        yy = 10 + i * 66
        ss.text(s, *m.box(0, yy, 300, yy + 50), [[(t, {"bold": b, "color": F if b else INK, "size": 10}) for t, b in q]], anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
        for k in range(5):
            bx = 320 + k * 38
            R(s, m, bx, yy + 12, bx + 26, yy + 38, G2)
            fill = max(0, min(1, v - k))
            if fill: R(s, m, bx, yy + 12, bx + 26 * fill, yy + 38, G4 if fill == 1 else D)
            if fill == 1: R(s, m, bx, yy + 12, bx + 26, yy + 38, D)
        tm(s, m, 512, yy + 10, 556, yy + 40, f"{v:.1f}", size=9, bold=True)
    pline(s, m, ((415, 210), (415, 262), (345, 262)), G4, .75)
    R(s, m, 0, 225, 345, 296, G1)
    ss.text(s, *m.box(12, 228, 335, 293), [[("Field note: ", {"bold": True, "italic": True, "color": F, "size": 8}), ("owners praised ease of delivery in every visit", {"italic": True, "color": INK, "size": 8})]], anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def payoff_grid(s, x, y, w, h):
    """Matriz de payoff: o próprio resultado sobre o do rival, com o equilíbrio aceso. Vasta p.24."""
    m = M((0, 0, 560, 310), (x, y, w, h))
    cols_, rows_ = ("Defend", "Share", "Retreat"), ("Aggressive", "Cautious", "Stay out")
    vals = (("+0", "+25", "+40", "+35", "+60", "+25"), ("+41", "+30", "+65", "+50", "+77", "+25"), ("-25", "+15", "-20", "+65", "-15", "+85"))
    for j, c in enumerate(cols_):
        tm(s, m, 130 + j * 142, 2, 262 + j * 142, 26, c, size=9)
    for i, r in enumerate(rows_):
        yy = 30 + i * 84
        tm(s, m, 0, yy, 122, yy + 74, r, size=9, align=PP_ALIGN.RIGHT)
        for j in range(3):
            bx = 130 + j * 142
            on = i == 1 and j == 1
            if on: rr(s, *m.box(bx - 6, yy - 6, bx + 138, yy + 80), T, .2)
            b = m.box(bx, yy, bx + 132, yy + 74)
            rr(s, *b, F if on else W, .18, border=None if on else G3, width=1)
            tc = W if on else INK
            ss.text(s, *b, [[(vals[i][j * 2], {"bold": True, "color": tc, "size": 10})], [("/ " + vals[i][j * 2 + 1], {"italic": True, "color": tc, "size": 8})]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    oval(s, *m.p((215, 296)), .1, F)
    tm(s, m, 225, 284, 500, 308, "Equilibrium: cautious, share", size=8, bold=True, color=F, align=PP_ALIGN.LEFT)


def priced_risks(s, x, y, w, h):
    """Riscos na matriz, com o mesmo código no cartão que dá o custo em TIR. Vasta p.40."""
    m = M((0, 0, 640, 290), (x, y, w, h))
    cs = 40
    filled = {(0, 1): ("E3", D), (2, 2): ("E2", D), (2, 3): ("M1", T), (4, 3): ("E1", D), (4, 4): ("C1", F)}
    for i in range(5):
        for j in range(5):
            bx, by = 28 + i * (cs + 5), 8 + (4 - (4 - j)) * (cs + 5)
            lab = filled.get((i, j))
            R(s, m, bx, by, bx + cs, by + cs, lab[1] if lab else G2)
            if lab: tm(s, m, bx, by, bx + cs, by + cs, lab[0], size=8, bold=True, color=INK if lab[1] == T else W)
    ss.line(s, *m.p((22, 4)), *m.p((22, 240)), INK, .75, dash=False); ss.line(s, *m.p((22, 240)), *m.p((262, 240)), INK, .75, dash=False)
    tm(s, m, 90, 243, 262, 262, "Impact", size=7); lx, ly = m.p((8, 122)); tx(s, lx - .4, ly - .08, .8, .16, "Likelihood", size=7, rot=-90)
    cards = (("C1", F, "Core churn rises", "4.9"), ("E2", D, "Margin stalls", "3.5"), ("M1", T, "Macro headwinds", "2.3"), ("E3", D, "New region fails", "2.4"))
    for i, (cd, c, t, irr) in enumerate(cards):
        yy = 6 + i * 70
        R(s, m, 280, yy, 636, yy + 60, G1)
        R(s, m, 280, yy, 330, yy + 60, c); tm(s, m, 280, yy, 330, yy + 60, cd, size=9, bold=True, color=INK if c == T else W)
        tm(s, m, 338, yy, 470, yy + 60, t, size=8, bold=True, align=PP_ALIGN.LEFT)
        tm(s, m, 470, yy, 512, yy + 60, "IRR", size=7, color=ss.MUTED)
        ax, ay = m.p((522, yy + 30))
        ss.poly(s, [(ax - .05, ay - .04), (ax + .05, ay - .04), (ax, ay + .05)], ss.NEG)
        tm(s, m, 530, yy, 634, yy + 60, f"({irr}%)", size=8, bold=True, color=ss.NEG)


def browser_news(s, x, y, w, h):
    """Notícia redigitada em moldura de navegador; dispensa print. 3R p.56. No slide real, texto e veículo são os verdadeiros."""
    gap = .1
    hh = (h - gap) / 2
    for k, (outlet, head, sub_) in enumerate((("Outlet name", "Government wants to slow the privatizations", "Governor asks the company to halt the sales"), ("Outlet name", "Company ends divestment process in four hubs", "The decision was announced today"))):
        yy = y + k * (hh + gap)
        wx, wd = x + w * .1, w * .8
        rr(s, wx + .03, yy + .03, wd, hh, G3, .05); rr(s, wx, yy, wd, hh, G2, .05)
        for i, c in enumerate(("EE5F57", "F5BD2E", "28C840")):
            oval(s, wx + .1 + i * .11, yy + .09, .07, c)
        oval(s, wx + wd - .11, yy + .09, .08, "C94A44")
        rr(s, wx + .1, yy + .17, wd - .35, .11, W, .5)
        by = yy + .33
        ss.rect(s, wx + .08, by, wd - .16, hh - .4, W)
        tx(s, wx + .1, by + .02, wd - .2, .2, outlet, size=8, bold=True, color=F)
        tx(s, wx + .15, by + .22, wd - .3, .34, head, size=9, bold=True)
        tx(s, wx + .15, by + .56, wd - .3, .24, sub_, size=8, color=G4)


def call_stamp(s, x, y, w, h):
    """Carimbo de data e participantes sobre a citação, para entrevista sem foto. CSN p.31."""
    m = M((0, 0, 620, 170), (x, y + h * .2, w, h * .6))
    R(s, m, 0, 0, 620, 32, D)
    tm(s, m, 12, 0, 610, 32, "FEBRUARY 27, 4:00 PM. CALL WITH THE CREDIT ANALYST", size=8, bold=True, color=W, align=PP_ALIGN.LEFT)
    tm(s, m, 6, 42, 50, 84, "“", size=20, bold=True, color=F)
    ss.text(s, *m.box(56, 44, 566, 160), [[("The stake grants ", {"color": INK, "size": 9}), ("preferred rates across the chain", {"bold": True, "color": D, "size": 9}), (", a hard-to-replicate asset and a ", {"color": INK, "size": 9}), ("structural edge", {"bold": True, "color": D, "size": 9}), (" over peers.", {"color": INK, "size": 9})]], anchor=MSO_ANCHOR.TOP, margin=0.0)
    tm(s, m, 572, 42, 616, 84, "”", size=20, bold=True, color=F)


def cap_table(s, x, y, w, h):
    """Mesma árvore antes e depois: só os percentuais mudam, com o delta ao lado. Vibra p.31."""
    m = M((0, 0, 660, 290), (x, y, w, h))
    holders = ("Fund", "Float", "Bank")
    pre = ("0.0%", "90.3%", "9.7%")
    post = (("13.3%", "+13.3"), ("85.4%", "-4.9"), ("1.3%", "-8.4"))
    def tree(ox, vals, is_post):
        cw_ = 100
        R(s, m, ox + cw_ * 2 - 4, 6, ox + cw_ * 3 - 8, 30, T); tm(s, m, ox + cw_ * 2 - 4, 6, ox + cw_ * 3 - 8, 30, "Second step", size=7, color=D, bold=True)
        ybus, yc = 190, 228
        for i, hd in enumerate(holders):
            bx = ox + i * cw_
            R(s, m, bx, 34, bx + cw_ - 8, 80, W, F, width=1)
            tm(s, m, bx, 34, bx + cw_ - 8, 80, hd, size=8, bold=True)
            cx = bx + (cw_ - 8) / 2
            ss.line(s, *m.p((cx, 80)), *m.p((cx, ybus)), F, 1, dash=False)
            v = vals[i][0] if is_post else vals[i]
            b = m.box(cx - 36, 104, cx + 36, 130)
            rr(s, *b, F, .3); tx(s, *b, v, size=7.5, bold=True, color=W)
            if is_post:
                tm(s, m, cx - 40, 136, cx + 40, 160, vals[i][1], size=7.5, bold=True, color=F if vals[i][1][0] == "+" else ss.NEG)
        ss.line(s, *m.p((ox + 46, ybus)), *m.p((ox + 246, ybus)), F, 1, dash=False)
        ss.line(s, *m.p((ox + 146, ybus)), *m.p((ox + 146, yc)), F, 1, dash=False)
        R(s, m, ox + 76, yc, ox + 216, yc + 48, D); tm(s, m, ox + 76, yc, ox + 216, yc + 48, "Company", size=8, bold=True, color=W)
    tree(0, pre, False)
    poly(s, m, ((304, 95), (312, 95), (340, 150), (312, 205), (304, 205), (332, 150)), G4)
    tree(362, post, True)


SLIDES = [
    ("Numbers get their own devices", "A verdict, a formula or a rating can replace a paragraph",
     [("Verdict T-bracket", "3R Petroleum p.6", verdict_bracket), ("Oversized operators", "3R Petroleum p.73", formula_ops), ("Formula in stairs", "Mercado Libre p.94", formula_stairs),
      ("Partial-fill rating", "AB InBev p.50", square_rating), ("Payoff grid", "Vasta p.24", payoff_grid), ("Risks priced in return", "Vasta p.40", priced_risks)]),
    ("Annotations make the chart argue", "Marks tie the data to the event or to the number that matters",
     [("Same number, ringed twice", "Cosan p.14", scribble_link), ("Notes in the empty years", "Cosan p.12", span_bracket), ("Events on the price line", "Cury p.22", event_flags),
      ("Phase window across charts", "Rede D'Or p.61", phase_windows), ("News in a browser shell", "3R Petroleum p.56", browser_news), ("Dated call above a quote", "CSN p.31", call_stamp)]),
    ("Structures carry the logic of the deal", "The same frame returns so the reader knows where the argument is",
     [("Decision tree, lit path", "CSN Liability p.21", decision_tree), ("Plan returning as tracker", "CSN Liability p.9", plan_tracker), ("Before and after cap table", "Vibra p.31", cap_table)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the device comes from the source.")
    ss.save(prs, OUT)
