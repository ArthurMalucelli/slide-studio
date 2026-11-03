"""Peças de profundidade do catálogo, com conteúdo fictício. Copie a função para o build do slide e troque os textos.
Referência de cada uma: references/catalogo/profundidade.md.
Uso: python3 pecas_profundidade.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402

# ---------- Sólidos ----------

def iso_plates(s, x, y, w, h):
    m = M((197, 253, 680, 567), (x, y, w, h))
    for k, c, t in ((2, light(F, .85), "Base layer"), (1, light(F, .45), "Middle layer"), (0, F, "Top layer")):
        o = 84 * k
        q = lambda P: [(a, b + o) for a, b in P]
        poly(s, m, q(((197, 331), (397, 365), (516, 287), (315, 253))), c)
        poly(s, m, q(((197, 331), (197, 365), (397, 399), (397, 365))), c)
        poly(s, m, q(((397, 365), (516, 287), (516, 321), (397, 399))), c)
        for a, b in (((199, 331), (397, 365)), ((397, 365), (516, 287))):
            ss.line(s, *m.p((a[0], a[1] + o)), *m.p((b[0], b[1] + o)), W, 1.0, dash=False)
        ss.line(s, *m.p((430, 300 + o)), *m.p((560, 300 + o)), INK, 0.75, dash=True)
        oval(s, *m.p((430, 300 + o)), 0.08, D)
        tm(s, m, 565, 285 + o, 680, 315 + o, t, size=8, align=PP_ALIGN.LEFT)



def extruded_rails(s, x, y, w, h):
    m = M((502, 97, 942, 308), (x, y, w, h))
    def rail(yt):
        R(s, m, 503, yt + 11, 931, yt + 18, F)
        poly(s, m, ((503, yt + 11), (513, yt), (942, yt), (931, yt + 11)), light(F, .3))
        poly(s, m, ((931, yt + 11), (942, yt), (942, yt + 7), (931, yt + 18)), dark(F))
    rail(291)
    poly(s, m, ((932, 114), (941, 104), (941, 293), (932, 303)), "C3C3C3")
    poly(s, m, ((502, 114), (512, 104), (941, 104), (932, 114)), "F5F5F5")
    R(s, m, 502, 114, 932, 303, G1)
    rail(97)
    tm(s, m, 512, 125, 922, 165, "Premises", size=11, bold=True)
    tm(s, m, 512, 165, 922, 285, "Three assumptions held across the scenarios", size=9)



def bevel_panel(s, x, y, w, h):
    m = M((70, 141, 504, 747), (x + w * .15, y, w * .7, h), keep=False)
    poly(s, m, ((504, 140), (495, 149), (495, 729), (504, 721)), "BEBFC4")
    poly(s, m, ((504, 141), (80, 141), (70, 150), (495, 150)), light(D, .25))
    R(s, m, 70, 171, 495, 729, "ECEEF4")
    R(s, m, 70, 150, 495, 171, D)
    poly(s, m, ((504, 141), (495, 150), (495, 171), (504, 162)), dark(D, .2))
    R(s, m, 70, 725, 495, 747, D)
    poly(s, m, ((504, 716), (495, 725), (495, 747), (504, 738)), dark(D, .2))
    tm(s, m, 90, 200, 475, 300, "Bull scenario", size=11, bold=True)
    tm(s, m, 90, 320, 475, 680, "Standard card: lips on top and bottom plus a thin side wall", size=9)


# ---------- Paredes ----------



def slab_cards(s, x, y, w, h):
    m = M((60, 80, 950, 330), (x, y, w, h))
    for i in range(3):
        cx = 72.6 + i * 291
        if i < 2: R(s, m, cx + 250, 103, cx + 300, 297, G2)
    R(s, m, 72.6 + 2 * 291 + 250, 103, 950, 297, G2)
    for i, t in enumerate(("Pillar one", "Pillar two", "Pillar three")):
        cx = 72.6 + i * 291
        R(s, m, cx + 9, 94.2, cx + 268.2, 323.2, "A6A6A6")
        R(s, m, cx, 89.6, cx + 259.2, 318.5, "EFEFEF")
        tm(s, m, cx + 15, 100, cx + 245, 310, t, size=9, bold=True)


def wedge_tab_row(s, x, y, w, h):
    """Rampa de título, gabarito Intelbras p.11, e abas dobradas."""
    m = M((0, 0, 300, 150), (x, y, w, h))
    for k, (t, c) in enumerate((("Key takeaway", F), ("Second point", D))):
        yy = 20 + k * 70
        poly(s, m, ((0, yy + 28), (34, yy), (34, yy + 28)), c)
        R(s, m, 34, yy + 26, 300, yy + 28, c)
        tm(s, m, 40, yy, 295, yy + 26, t, size=11, bold=True, align=PP_ALIGN.LEFT)


# ---------- Feixes ----------




def flare_wedges(s, x, y, w, h):
    m = M((69, 164, 660, 346), (x, y, w, h))
    R(s, m, 69, 217, 197, 293, A)
    poly(s, m, ((197, 217), (273, 192), (273, 317), (197, 293)), dark(A, .3))
    R(s, m, 273, 192, 442, 317, A)
    poly(s, m, ((442, 192), (532, 164), (532, 346), (442, 317)), dark(A, .3))
    R(s, m, 532, 164, 660, 346, D)
    for a, b, t, c in ((69, 197, "Small", INK), (273, 442, "Larger", INK), (532, 660, "Barrier", W)):
        tm(s, m, a, 217, b, 293, t, size=9, bold=True, color=c)



# ---------- Fitas e dobras ----------
RIB = ((137.8, 0), (58.8, 0), (53, 1.2), (47.4, 3.6), (42.4, 7.3), (38, 12.6), (23.4, 39.2), (20.6, 43.3), (17.3, 46.7), (13, 49.3), (7.3, 51.2), (0, 52.5), (79, 52.5), (86.3, 51.2), (92, 49.3), (96.3, 46.7), (99.6, 43.3), (102.4, 39.2), (117, 12.6), (121.3, 7.3), (126.4, 3.6), (132, 1.2))


def ribbon_timeline(s, x, y, w, h):
    m = M((-40, -60, 800, 112), (x, y + h * .1, w, h * .8), keep=False)
    cols = (D, dark(F, .3), F, A, T)
    n = 5
    for i in range(n):
        ox = i * 120
        poly(s, m, [(137.8 - a + ox + 67, b) for a, b in RIB], G2)
    ss.line(s, *m.p((-40, 26)), *m.p((800, 26)), "4B4B4B", 1.75, dash=False)
    for i, c in enumerate(cols):
        ox = i * 120
        poly(s, m, [(a + ox, b) for a, b in RIB], c)
        tm(s, m, ox + 25, 8, ox + 115, 45, str(2020 + i * 2), size=8, bold=True, color=W if i < 4 else INK)
        up = i % 2 == 0
        sx = ox + 70
        y0, y1 = (0, -32) if up else (52, 84)
        ss.line(s, *m.p((sx, y0)), *m.p((sx, y1)), INK, .75, dash=False)
        poly(s, m, ((sx, y1), (sx + 15, y1), (sx, y1 + (8 if up else -8))), c)
        tm(s, m, sx + 18, y1 - 14, sx + 118, y1 + 12, "Event", size=8, align=PP_ALIGN.LEFT)


def accordion(s, x, y, w, h):
    m = M((-45, 90, 560, 410), (x, y, w, h))
    R(s, m, -45, 90, 560, 410, D)
    poly(s, m, ((44, 163), (-44, 99), (-44, 241), (45, 241)), dark(light(A, .35)))
    poly(s, m, ((44, 298), (-44, 353), (-44, 230), (44, 230)), dark(A))
    poly(s, m, ((44, 298), (-44, 298), (-44, 401), (44, 366)), dark(light(A, .65)))
    for pts, c, t in ((((43, 162), (454, 162), (488, 196), (454, 230), (43, 230)), light(A, .35), "Diversified units"),
                      (((43, 230), (508, 230), (542, 264), (508, 298), (43, 298)), A, "Driven by deepening trends"),
                      (((43, 298), (415, 298), (449, 332), (415, 366), (43, 366)), light(A, .65), "A strong partnership")):
        poly(s, m, pts, c)
        tm(s, m, 60, pts[0][1], 440, pts[2][1] + 34, t, size=9, bold=True, align=PP_ALIGN.LEFT)




def fold_tabs(s, x, y, w, h):
    m = M((63, 135, 918, 285), (x, y, w, h))
    xe = (63.7, 210.8, 352.6, 495.2, 633.1, 779.5, 917.8)
    cols = (light(A, .8), light(A, .35), A, F, dark(F, .3), D)
    for i, c in enumerate(cols): R(s, m, xe[i], 225, xe[i + 1], 283, c)
    for i, cx in enumerate((76.4, 217.7, 361.1, 503.5, 645.9, 788.2)):
        R(s, m, cx, 138, cx + 113.6, 226, G1)
        tm(s, m, cx + 4, 142, cx + 110, 222, ("2024", "2025", "2026", "2027", "2028", "2029")[i], size=8, bold=True)
        n = cols[i + 1] if i < 5 else dark(D, .3)
        rx = cx + 113.6
        poly(s, m, ((rx, 205), (rx, 226), (rx + 19.7, 226)), n)
        tm(s, m, xe[i] + 5, 228, xe[i + 1] - 5, 280, "Step", size=8, color=INK if i < 2 else W, bold=True)
    poly(s, m, ((77.9, 202.8), (64.2, 228.3), (77.9, 228.3)), light(A, .6))



# ---------- Camadas ----------




# ---------- Luz e cena ----------
def fade_waterfall(s, x, y, w, h):
    bg = ss.rect(s, x, y, w, h, D); grad(bg, ((0, "000000"), (1, "00305F")), 45)
    vals = (.35, .5, .62, .55, .82)
    bw = w / 7
    for i, v in enumerate(vals):
        bx = x + bw * (.6 + i * 1.2)
        bh = (h - .4) * v
        by = y + h - .2 - bh
        sp = ss.rect(s, bx, by, bw, bh, F)
        if i == 3:
            grad(sp, ((0, "1F5A91", .3), (1, "47A4FA")), 90)
        else:
            grad(sp, ((0, "0177C8"), (.6, "0056A0"), (1, "00305F", 0)), 90)
        tx(s, bx, by + .03, bw, .22, ("22", "29", "35", "−6", "48")[i], size=9, color=W, bold=True)
    ss.line(s, x + .1, y + h - .2, x + w - .1, y + h - .2, W, .75, dash=False)


def tube_bars(s, x, y, w, h):
    bw = w / 8
    for i, v in enumerate((.3, .42, .55, .68, .85)):
        bx = x + bw * (.6 + i * 1.5)
        bh = (h - .55) * v
        by = y + h - .25 - bh
        grad(ss.rect(s, bx, by, bw, bh, F), ((0, dark(F, .4)), (.5, light(F, .25)), (1, dark(F, .4))), 0)
        ss.pill(s, bx + bw / 2, by - .22, str(10 + i * 7), fill=F, color=W)
        tx(s, bx - .1, y + h - .22, bw + .2, .2, str(2021 + i), size=8)
    ss.line(s, x + .1, y + h - .25, x + w - .1, y + h - .25, G4, .75, dash=False)



def pinch_pills(s, x, y, w, h):
    n = 4
    pw, ph = w * .6, h * .15
    px = x + w * .22
    pitch = (h - ph) / (n - 1)
    for i in range(n - 1):
        ly = y + ph * .7 + i * pitch
        lh = pitch - ph * .4
        grad(ss.rect(s, px + pw * .06, ly, pw * .88, lh, D), ((0, D), (1, F)), 90)
        r = lh / 2
        oval(s, px + pw * .06, ly + r, r * 2, W); oval(s, px + pw * .94, ly + r, r * 2, W)
    for i, t in enumerate(("Agribusiness", "Construction", "Industry", "Services")):
        py = y + i * pitch
        rr(s, px + .02, py + .025, pw, ph, G3, .35); rr(s, px, py, pw, ph, G1, .35)
        tx(s, px, py, pw, ph, t, size=8)
        oval(s, px, py + ph / 2, ph * .95, W, border=F, width=1.5)
        tx(s, px - .15, py, .3, ph, str(i + 1), size=9, bold=True, color=F)





def iso_stairs(s, x, y, w, h):
    m = M((570, 92, 1422, 771), (x, y, w, h))
    # A seta fica atrás de tudo: a frente dela é o último degrau.
    poly(s, m, ((1379, 622), (1379, 351), (1365, 359), (1312, 331), (1312, 659)), dark(A, .3))
    poly(s, m, ((1320, 92), (1265, 122), (1365, 359), (1422, 328)), dark(A, .3))
    poly(s, m, ((1312, 659), (1312, 331), (1365, 359), (1265, 122), (1137, 242), (1188, 268), (1188, 596)), A)
    # Cada aba tem a cor do seu degrau e sobe junto com ele; o vão branco separa aba e sólido.
    tabs = ((773, 311, 1182, 399, A, "Production forecast", INK), (705, 405, 1112, 493, F, "Technical adjustment", W),
            (638, 499, 1045, 587, dark(F, .35), "Defined discount", W), (570, 593, 978, 707, D, "Certified reserves", W))
    for x0, y0, x1, y1, c, t, tc in tabs:
        R(s, m, x0, y0, x1, y1, c)
        tm(s, m, x0 + 18, y0, x1 - 12, y1, t, size=8, color=tc, bold=True, align=PP_ALIGN.LEFT)
    steps = [(((1312, 431), (1188, 367), (1120, 405), (1245, 468)), ((1245, 696), (1245, 468), (1120, 405), (1120, 633)), ((1312, 659), (1312, 431), (1245, 468), (1245, 696)), F),
             (((1244, 524), (1119, 461), (1052, 498), (1176, 561)), ((1178, 734), (1178, 560), (1053, 497), (1053, 670)), ((1245, 696), (1245, 523), (1178, 560), (1178, 734)), dark(F, .35)),
             (((1177, 618), (1052, 554), (985, 591), (1110, 654)), ((1111, 771), (1111, 653), (986, 589), (986, 708)), ((1178, 734), (1178, 616), (1111, 653), (1111, 771)), D)]
    for top, left, right, c in steps:
        poly(s, m, right, dark(c, .3)); poly(s, m, left, c); poly(s, m, top, light(c, .18))


def iso_columns(s, x, y, w, h):
    m = M((110, 120, 1080, 750), (x, y, w, h))
    # O piso ocupa toda a largura: as colunas nascem nele e o texto acompanha cada topo.
    R(s, m, 110, 537, 1080, 750, G1)
    for cx, t, b, c1, c2, c3, ht in ((195, 173, 578, F, light(F, .3), light(F, .55), "Financial services"),
                                     (303, 301, 631, "404040", G4, "D3D3D3", "New verticals"), (409, 458, 687, G3, G2, "EDEDED", "International")):
        poly(s, m, ((cx, t), (cx + 74, t + 30), (cx + 74, b + 38), (cx, b)), c1)
        poly(s, m, ((cx + 74, t + 30), (cx + 149, t), (cx + 149, b), (cx + 74, b + 38)), c2)
        poly(s, m, ((cx, t), (cx + 74, t - 31), (cx + 149, t), (cx + 74, t + 30)), c3)
        lx = cx + 175
        tm(s, m, lx, t - 40, 1080, t, ht, size=9, bold=True, color=F if c1 == F else (INK if c1 == "404040" else G4), align=PP_ALIGN.LEFT)
        tm(s, m, lx, t, 1080, t + 55, "One line of support", size=8, align=PP_ALIGN.LEFT)


def corner_ribbon(s, x, y, w, h):
    m = M((790, 190, 1410, 400), (x, y, w, h))
    bx = m.box(812, 224, 1383, 396)
    rr(s, bx[0] + .03, bx[1] + .03, bx[2], bx[3], G3, .08)
    # A dobra vai ATRÁS do cartão: só as duas pontas aparecem, acima e à direita dele.
    poly(s, m, ((1233, 200), (1233, 224), (1383, 373), (1405, 373), (1381, 349), (1257, 224)), dark(F, .45))
    rr(s, *bx, G1, .08)
    poly(s, m, ((1233, 200), (1311, 200), (1405, 294), (1405, 372)), F)
    # Texto centrado no meio exato da faixa, a 45 graus.
    cx, cy = m.p((1338.5, 266.5))
    tw, th = 1.1, .22
    tx(s, cx - tw / 2, cy - th / 2, tw, th, "Internal risks", size=8, color=W, bold=True, rot=45)
    tm(s, m, 835, 245, 1210, 375, "The band wraps the corner; its fold shows only at the two ends", size=9, align=PP_ALIGN.LEFT)


def lens_stack(s, x, y, w, h):
    ss.rect(s, x, y, w, h, light(A, .72))
    def lens(tip, reach, c):
        cy = y + h / 2
        up, dn = [], []
        for i in range(31):
            t = i / 30
            ax, ay = x + w * tip, cy
            bx, by = x + w * (tip + .18), y + h * .06
            ex, ey = x + w * reach, y
            px = (1 - t) ** 2 * ax + 2 * t * (1 - t) * bx + t ** 2 * ex
            py = (1 - t) ** 2 * ay + 2 * t * (1 - t) * by + t ** 2 * ey
            up.append((px, py)); dn.append((px, 2 * cy - py))
        ss.poly(s, up + [(x + w, y), (x + w, y + h)] + dn[::-1], c)
    lens(.0, .78, A); lens(.05, .92, F)
    cw, top, ch = w * .205, y + h * .22, h * .56
    for i, t in enumerate(("Edge", "Efficiency", "Capital")):
        cx = x + w * .15 + i * (cw + w * .018)
        rr(s, cx, top, cw, ch, "E1F5FD", .12)
        tx(s, cx + .04, top + .1, cw - .08, .24, t, size=9, bold=True)
        for k in range(3):
            oy = top + .46 + k * .28
            ss.rect(s, cx + .1, oy, cw - .2, .05, light(F, .55))
        tb = .19
        rr(s, cx - tb / 2 + .05, top - tb / 2, tb, tb, A, .2)
        tx(s, cx - tb / 2 + .05, top - tb / 2, tb, tb, ("I", "II", "III")[i], size=7, color=W, bold=True)
    tx(s, x + w * .82, y, w * .17, h, "Buy", size=14, color=W, bold=True)


def half_ring(s, x, y, w, h):
    m = M((0, 130, 610, 500), (x, y, w, h))
    R(s, m, 0, 130, 610, 500, light(T, .65))
    c = (-20, 315)
    cols = (D, F, A, T, G3)
    bounds = (-100, -58, -24, 12, 46, 100)
    for i, col in enumerate(cols):
        poly(s, m, seg(c, 118, 178, bounds[i] + 1.2, bounds[i + 1] - 1.2, xmin=0), col)
    poly(s, m, ((0, 268), (70, 315), (0, 362)), D)
    names = ("Core education", "Digital platforms", "Complements", "Bilingual solutions", "School management")
    for i, col in enumerate(cols):
        yy = 142 + i * 71
        my = yy + 28 - 315
        sx = c[0] + math.sqrt(max(178 ** 2 - my ** 2, 0)) + 22
        bx = m.box(sx, yy, 598, yy + 57)
        rr(s, bx[0] + .02, bx[1] + .02, bx[2], bx[3], G3, .13)
        rr(s, *bx, W, .13, border=col, width=1.5)
        ix, iy = bx[0] + .2, bx[1] + bx[3] / 2
        oval(s, ix, iy, .22, None, border=col, width=1.25)
        tx(s, bx[0] + .38, bx[1], bx[2] - .42, bx[3], names[i], size=8, bold=True, align=PP_ALIGN.LEFT)


def overlap_arrows(s, x, y, w, h):
    b = (190, 20, 1190, 790); m = M(b, (x, y, w, h))
    R(s, m, *b, "A8A8A8")
    for i in range(4):   # o slide anterior continua visível sob o véu
        R(s, m, 215, 70 + i * 110, 1165, 76 + i * 110, "9A9A9A")
    # Feixe sai da seta ativa e passa atrás dos cartões.
    poly(s, m, ((470, 560), (250, 640), (440, 283), (560, 533)), G2)
    arrows = ((200, D, 100), (395, F, 62), (590, light(F, .15), 62), (785, A, 62), (940, light(A, .25), 62))
    for ax, c, al in arrows[::-1]:
        pts = ((ax, 585), (ax + 150, 585), (ax + 150, 535), (ax + 250, 662), (ax + 150, 790), (ax + 150, 740), (ax, 740), (ax + 45, 662))
        poly(s, m, pts, c, alpha=al)
    for (ax, _, _), t in zip(arrows, ("4Q20", "2Q21", "4Q21", "3Q22", "2Q23")):
        tm(s, m, ax + 50, 620, ax + 200, 705, t, size=8, color=W, bold=True)
    R(s, m, 446, 289, 1149, 539, F); R(s, m, 440, 283, 1143, 533, "F5F5F5")
    tm(s, m, 470, 330, 800, 510, "Plans for the proceeds", size=9, align=PP_ALIGN.LEFT)
    tm(s, m, 810, 330, 1120, 510, "$200m", size=14, bold=True, color=F)
    R(s, m, 319, 41, 1016, 291, F); R(s, m, 313, 35, 1010, 285, "EBEBEB")
    tm(s, m, 340, 70, 700, 260, "IPO priced in the round", size=9, align=PP_ALIGN.LEFT)
    tm(s, m, 700, 70, 990, 260, "$690m", size=14, bold=True, color=F)



def modal_sandwich(s, x, y, w, h):
    b = (160, 50, 780, 500); m = M(b, (x, y, w, h))
    backdrop(s, m, b)
    R(s, m, *b, "000000", alpha=30)
    R(s, m, 268, 84, 703, 358, F); R(s, m, 234, 207, 669, 482, F)
    R(s, m, 245, 96, 691, 471, "F5F5F5")
    tm(s, m, 265, 108, 671, 165, "Now the company creates value", size=9, bold=True)
    mini_lines(s, m, 285, 185, 650, 445)


def l_wedges(s, x, y, w, h):
    b = (190, 50, 790, 515); m = M(b, (x, y, w, h))
    backdrop(s, m, b)
    R(s, m, *b, "000000", alpha=35)
    poly(s, m, ((246, 73), (508, 73), (421, 141), (315, 141), (315, 225), (246, 279)), F)
    poly(s, m, ((736, 495), (551, 495), (613, 436), (677, 436), (677, 374), (736, 316)), F)
    R(s, m, 253, 78, 730, 491, W)
    tm(s, m, 275, 92, 708, 150, "Asset value and value creation", size=9, bold=True)
    mini_lines(s, m, 290, 175, 695, 460)


def spotlight(s, x, y, w, h):
    b = (40, 125, 720, 405); m = M(b, (x, y, w, h))
    R(s, m, *b, G1)
    for i in range(5):
        for j in range(2):
            R(s, m, 60 + i * 130, 290 + j * 56, 170 + i * 130, 340 + j * 56, G3)
    R(s, m, *b, W, alpha=55)
    poly(s, m, ((150, 165), (281, 268), (138, 387), (139, 384), (106, 334), (70, 331)), F)
    ax, ay = m.p((93, 372)); oval(s, ax, ay, 112 * m.sx, W)
    R(s, m, 61, 347, 126, 396, F); tm(s, m, 61, 347, 126, 396, "S2", size=9, color=W, bold=True)
    R(s, m, 131, 143, 692, 279, W, F)
    tm(s, m, 150, 150, 672, 270, "The chosen cell stays lit while the page fades", size=9)
    R(s, m, 278, 277, 703, 319, F); tm(s, m, 285, 277, 696, 319, "Caption straddles the card edge", size=8, color=W, bold=True)


def tapered_wall(s, x, y, w, h):
    m = M((0, 120, 945, 492), (x, y, w, h))
    R(s, m, 0, 120.8, 120, 491, G1)
    poly(s, m, ((120, 120.8), (146, 146), (146, 466), (120, 491.2)), G3)
    R(s, m, 146, 146, 932, 466, G1)
    R(s, m, 932, 146, 945, 466, D)
    R(s, m, 146, 446, 945, 466, D)
    tm(s, m, 170, 165, 910, 245, "The main plane sits behind the wall", size=10, bold=True)
    for i, t in enumerate(("Targeting", "Measurability", "Conversion")):
        yy = 260 + i * 58
        tm(s, m, 230 + i * 110, yy, 560 + i * 110, yy + 32, t, size=9, bold=True, color=D)
        ss.line(s, *m.p((230 + i * 110, yy + 38)), *m.p((560 + i * 110, yy + 38)), G3, .5, dash=False)


def gutter_wall(s, x, y, w, h):
    m = M((25, 100, 960, 497), (x, y, w, h))
    R(s, m, 25, 124, 180, 473, G1); R(s, m, 225, 100, 960, 497, G1)
    poly(s, m, ((180, 124), (225, 100), (225, 497), (180, 473)), G3)
    R(s, m, 250, 128, 258, 165, F)
    tm(s, m, 268, 122, 940, 172, "How were these forces built?", size=10, bold=True, align=PP_ALIGN.LEFT)
    for i, t in enumerate(("New entrants", "Rivalry", "Substitutes", "Buyers", "Suppliers")):
        yy = 190 + i * 58
        tm(s, m, 250, yy, 480, yy + 44, t, size=9, bold=True, color=F, align=PP_ALIGN.LEFT)
        R(s, m, 490, yy + 18, 930, yy + 24, G3)


def wall_zoom(s, x, y, w, h):
    m = M((128, 159, 797, 430), (x, y, w, h))
    R(s, m, 128, 182, 268, 407, G2)
    poly(s, m, ((268, 182), (324, 159), (324, 430), (268, 406)), G2)
    R(s, m, 324, 159, 797, 430, "EAF0F7")
    for a, b, wd in (((324, 230), (797, 300), 3), ((430, 159), (520, 430), 3), ((640, 159), (600, 430), 2), ((324, 360), (797, 340), 2), ((324, 180), (797, 200), 1.5), ((740, 159), (780, 430), 1.5)):
        ss.line(s, *m.p(a), *m.p(b), W, wd, dash=False)
    for a, b, c in ((.15, .3, F), (.35, .6, D), (.5, .25, F), (.62, .7, A), (.8, .4, D), (.28, .8, A), (.72, .18, F), (.9, .72, F), (.45, .85, D)):
        oval(s, *m.p((324 + 473 * a, 159 + 271 * b)), 0.1, c)
    for a, b in (((268, 182), (324, 159)), ((268, 406), (324, 430))):
        ss.line(s, *m.p(a), *m.p(b), F, 1, dash=True)
    R(s, m, 128, 182, 268, 407, None, F, dash=True); R(s, m, 324, 159, 797, 430, None, F, dash=True)
    for i, (c, t) in enumerate(((F, "Store A"), (A, "Store B"), (D, "Store C"))):
        yy = 225 + i * 60
        oval(s, *m.p((150, yy)), 0.1, c)
        tm(s, m, 165, yy - 18, 262, yy + 18, t, size=8, bold=True, color=c, align=PP_ALIGN.LEFT)


def plinth(s, x, y, w, h):
    m = M((163, 262, 728, 492), (x, y, w, h))
    for i in range(3):
        R(s, m, 198 + i * 165, 262, 353 + i * 165, 332, T, W)
        tm(s, m, 198 + i * 165, 262, 353 + i * 165, 332, "Photo", color=D, size=8)
    poly(s, m, ((163, 378), (194, 327), (697, 327), (728, 378)), "C9C9C9")
    R(s, m, 163, 376, 728, 492, "DBDBDB")
    tm(s, m, 185, 385, 706, 485, "“The quote sits on the lit front face of the stage, under the people who said it.”", size=9, italic=True, align=PP_ALIGN.LEFT)


def orbit_rows(s, x, y, w, h):
    """Discos com arcos parciais em panel alimentado por uma cunha: Senior p.19."""
    m = M((0, 0, 470, 265), (x, y, w, h))
    grad(poly(s, m, ((0, 45), (58, 8), (58, 255), (0, 215)), G2), ((0, W), (1, G2)), 0)
    R(s, m, 58, 8, 468, 255, "F7F7F7", G2)
    rows = ((112, 62, "Cost discipline"), (168, 132, "Operating leverage"), (112, 205, "Focused footprint"))
    for cx, cy, t in rows:
        ax, ay = cx, cy
        poly(s, m, seg((ax, ay), 30, 32, 110, 250), F)
        sp = oval(s, *m.p((ax, ay)), 46 * m.sx, F, border=light(F, .55), width=1.5)
        grad(sp, ((0, light(A, .4)), (1, F)), 45)
        oval(s, *m.p((ax, ay)), 26 * m.sx, None, border=W, width=1)
        tm(s, m, cx + 30, cy - 24, 458, cy - 2, t, size=9, align=PP_ALIGN.LEFT)
        ss.line(s, *m.p((cx + 24, cy)), *m.p((456, cy)), F, 1, dash=False)
        oval(s, *m.p((456, cy)), .05, F)
        tm(s, m, cx + 30, cy + 3, 458, cy + 24, "Short supporting line", size=8, color=ss.MUTED, align=PP_ALIGN.LEFT)


def beam_bars(s, x, y, w, h):
    m = M((300, 96, 960, 497), (x, y, w, h))
    for i, (bt, st, sb) in enumerate(((300, 330, 390), (260, 290, 370), (220, 245, 335), (150, 260, 333))):
        bx = 330 + i * 45
        if i == 3: bx = 470
        R(s, m, bx + 2.5, bt + 3, bx + 27.5, 423, "000000")
        R(s, m, bx, bt, bx + 25, 420, G2)
        R(s, m, bx, st, bx + 25, sb, F)
    ss.line(s, *m.p((315, 420)), *m.p((510, 420)), G4, 0.75, dash=False)
    poly(s, m, ((495, 260), (495, 333), (590, 497), (590, 96)), F, alpha=86)
    R(s, m, 590, 96, 960, 497, G1, F, width=1.5)
    tm(s, m, 610, 110, 940, 170, "Digital revenue", size=10, bold=True, color=F)
    mini_bars(s, m, 625, 200, 925, 400, n=9)
    tm(s, m, 610, 415, 940, 480, "One segment opens into the card that explains it", size=8)


def donut_flare(s, x, y, w, h):
    m = M((562, 195, 915, 490), (x, y, w, h))
    c = (738, 291)
    R(s, m, 565, 408, 915, 488, "6F6F6F")
    poly(s, m, ((688, 370), (788, 370), (912, 405), (562, 405)), G3)
    R(s, m, 562, 405, 912, 485, G3)
    a = -90
    labs = ((16, D, "16%"), (6, dark(F, .3), "6%"), (5, F, "5%"), (3, A, ""), (70, G3, ""))
    for pct, col, lab in labs:
        b = a + pct * 3.6
        poly(s, m, seg(c, 56, 96, a, b), col)
        poly(s, m, seg(c, 0, 28, a, b, n=max(6, int(pct))), col)
        if lab:
            mid = math.radians((a + b) / 2)
            lx, ly = c[0] + 76 * math.cos(mid), c[1] + 76 * math.sin(mid)
            tm(s, m, lx - 22, ly - 11, lx + 22, ly + 11, lab, size=7, color=W, bold=True)
        a = b
    tm(s, m, 580, 410, 894, 480, "The remaining slice turns into the box that comments on it", size=9, color=INK, bold=True)


def arc_ribbons(s, x, y, w, h):
    m = M((495, 310, 906, 476), (x, y, w, h))
    cols = (light(F, .55), light(F, .25), F, dark(F, .3), D)
    bounds = (-90, -57, -21, 21, 57, 90)
    # Anel externo sólido, sem fio entre as fatias; um círculo branco o separa do anel interno.
    for i, c in enumerate(cols):
        poly(s, m, seg((523.8, 393), 0, 78, bounds[i], bounds[i + 1], n=14), c)
    ax, ay = m.p((523.8, 393)); oval(s, ax, ay, 88 * m.sx, W)
    for i, c in enumerate(cols):
        poly(s, m, seg((523.4, 391), 0, 38, bounds[i], bounds[i + 1], n=10), c)
    tops, lefts = (315.1, 349.7, 383.1, 419.6, 450.8), (524, 566, 580, 566, 524)
    labs = (("One client", "Multiple streams"), ("Same customer", "New needs"), ("Lower risk", "Same ecosystem"), ("Harder to exchange", "Exchange cost"), ("Less sales effort", "Sells all"))
    for t, l, c, (a, b) in zip(tops, lefts, cols, labs):
        R(s, m, l, t, 905.7, t + 21, c)
        tc = INK if c == cols[0] else W
        tm(s, m, max(l, 580) + 8, t, 760, t + 21, a, size=7.5, color=tc, bold=True, align=PP_ALIGN.LEFT)
        tm(s, m, 760, t, 900, t + 21, b, size=7.5, color=tc, bold=True, align=PP_ALIGN.RIGHT)
    a = m.box(499, 373, 557, 407)
    rr(s, *a, D, .25); tx(s, *a, "Cross-sell", size=7, color=W, bold=True)


def bowtie(s, x, y, w, h):
    m = M((348, 180, 917, 493), (x, y, w, h))
    R(s, m, 348, 186, 430, 206, D); tm(s, m, 348, 186, 430, 206, "Core", size=7.5, color=W, bold=True)
    R(s, m, 748, 186, 917, 206, D); tm(s, m, 748, 186, 917, 206, "New unit", size=7.5, color=W, bold=True)
    for i, (t, v) in enumerate((("Sales", "32%"), ("Credit", "16%"), ("Banking", "14%"), ("Assets", "10%"), ("Wealth", "9%"))):
        yy = 206 + i * 57.4
        R(s, m, 348, yy, 430, yy + 57.4, light(A, .25), W, width=.75)
        tm(s, m, 352, yy, 426, yy + 57.4, t, size=7.5)
        R(s, m, 434, yy, 517, yy + 57.4, light(A, .65), W, width=.75)
        tm(s, m, 434, yy, 517, yy + 57.4, v, size=9, bold=True, color=D)
    grad(poly(s, m, ((517, 206), (517, 493), (632, 348)), T), ((0, light(A, .35)), (1, light(A, .85))), 0)
    grad(poly(s, m, ((748, 206), (748, 493), (632, 348)), F), ((0, light(A, .75)), (1, F)), 0)
    R(s, m, 748, 206, 917, 493, F)
    for i, t in enumerate(("Broker", "Bank", "Lending")):
        yy = 206 + i * 95.7
        tm(s, m, 755, yy, 910, yy + 95.7, t, size=9, color=W, bold=True)
        if i: ss.line(s, *m.p((748, yy)), *m.p((917, yy)), W, .75, dash=False)
    ax, ay = m.p((632, 348))
    oval(s, ax, ay, 93 * m.sx, W, border=A)
    tx(s, ax - .4, ay - .15, .8, .3, "Core", size=9, bold=True)


def shard_burst(s, x, y, w, h):
    m = M((0, 0, 470, 270), (x, y, w, h))
    R(s, m, 0, 15, 5, 255, D); R(s, m, 465, 15, 470, 255, D)
    for flip in (False, True):
        q = (lambda P: [(470 - a, b) for a, b in P]) if flip else (lambda P: P)
        for pts, c in ((((122, 36), (38, 22), (122, 66)), dark(F, .25)), (((122, 52), (58, 34), (122, 76)), A), ((  (122, 74), (22, 60), (122, 100)), D),
                       (((122, 92), (66, 80), (122, 112)), F)):
            poly(s, m, q(pts), c)
        grad(poly(s, m, q(((5, 96), (122, 122), (122, 205), (5, 172))), F), ((0, F if flip else D), (1, D if flip else F)), 25)
        poly(s, m, q(((5, 104), (122, 130), (122, 150), (5, 132))), D, alpha=50)
        poly(s, m, q(((5, 145), (122, 175), (122, 205), (5, 172))), dark(F, .25))
        ss.line(s, *m.p(q(((5, 96),))[0]), *m.p(q(((122, 122),))[0]), A, 1.5, dash=False)
        for k, (ln, c) in enumerate(((.0, A), (.2, T), (.4, light(F, .4)))):
            poly(s, m, q(((5 + 30 * k, 184 + k * 10), (122, 212 + k * 9), (122, 215 + k * 9))), c)
    tm(s, m, 25, 120, 75, 155, "+", size=16, color=W, bold=True)
    tm(s, m, 395, 120, 445, 155, "=", size=16, color=W, bold=True)
    R(s, m, 124, 18, 352, 256, D)
    R(s, m, 120, 12, 348, 250, W, F, width=1)
    tm(s, m, 134, 18, 334, 50, "Segment map", size=9, bold=True, align=PP_ALIGN.LEFT)
    for i, t in enumerate(("Automotive retail", "Agribusiness", "Premium", "Technical support", "International")):
        yy = 56 + i * 38
        tm(s, m, 134, yy, 300, yy + 32, t, size=8, italic=True, align=PP_ALIGN.LEFT)
        oval(s, *m.p((325, yy + 16)), .11, F if i > 1 else T)
        if i < 4: ss.line(s, *m.p((134, yy + 36)), *m.p((334, yy + 36)), G3, .5, dash=True)


def nav_tab(s, x, y, w, h):
    m = M((350, 0, 810, 110), (x, y + .25, w, h * .65))
    for a, b, t in ((350, 513, "Overview"), (662, 810, "Risks")):
        R(s, m, a, 0, b, 80, T); tm(s, m, a, 0, b, 80, t, size=9, color=D)
    poly(s, m, ((513, 80), (495, 80), (513, 98)), "000000")
    R(s, m, 513, 0, 662, 98, F); tm(s, m, 513, 0, 662, 98, "Thesis", size=11, color=W, bold=True)


def chevrons(s, x, y, w, h):
    m = M((205, 195, 540, 473), (x, y, w, h))
    for pts, c, f in ((((210, 197), (244, 197), (261, 250), (244, 303), (210, 303), (227, 250)), T, ((210, 197), (219, 197), (236, 250), (219, 303), (210, 303), (227, 250))),
                      (((209, 311), (244, 311), (261, 364), (244, 417), (209, 417), (227, 364)), F, ((209, 311), (218, 311), (236, 364), (218, 417), (209, 417), (227, 364))),
                      (((209, 423), (246, 423), (261, 471), (225, 471)), G2, None),
                      (((303, 357), (269, 357), (251, 306), (269, 255), (303, 255), (286, 306)), A, ((303, 357), (294, 357), (277, 306), (294, 255), (303, 255), (286, 306))),
                      (((303, 471), (269, 471), (251, 418), (269, 365), (303, 365), (286, 418)), D, ((303, 471), (294, 471), (277, 418), (294, 365), (303, 365), (286, 418))),
                      (((251, 197), (288, 197), (303, 249), (267, 249)), G2, None)):
        poly(s, m, pts, c)
        if f: poly(s, m, f, dark(c, .28))
    for yy, t in ((250, "Long horizon"), (306, "Local presence"), (364, "Scale"), (418, "Execution")):
        ss.line(s, *m.p((305, yy)), *m.p((335, yy)), G4, .75, dash=False)
        tm(s, m, 340, yy - 18, 540, yy + 18, t, size=9, align=PP_ALIGN.LEFT)


def tokens(s, x, y, w, h):
    grad(ss.rect(s, x, y, w, h, T), ((0, T), (1, W)), 315)
    for k in (.33, .66):
        ss.line(s, x + w * k, y, x + w * k, y + h, W, 1, dash=False)
        ss.line(s, x, y + h * k, x + w, y + h * k, W, 1, dash=False)
    ss.line(s, x, y + h, x + w, y, F, .75, dash=True)
    sp = oval(s, x + w * .3, y + h * .34, w * .52, F, h=h * .42); ss.set_alpha(sp, 12); sp.rotation = -30
    sp = oval(s, x + w * .3, y + h * .34, w * .52, None, h=h * .42, border=D, dash=True); sp.rotation = -30
    for cx, cy, t in ((.16, .52, "A"), (.3, .34, "B"), (.44, .16, "C"), (.68, .68, "D"), (.84, .82, "E"), (.6, .86, "F")):
        px, py = x + w * cx, y + h * cy
        d = .55
        oval(s, px, py, d, D)
        sp = oval(s, px - .02, py - .02, d - .02, F, border=W, width=1)
        grad(sp, ((0, A), (1, D)), 45)
        tx(s, px - .25, py - .12, .5, .24, t, size=9, color=W, bold=True, italic=True)


def ring_chain(s, x, y, w, h):
    """Faixa em S: retângulo em degradê com 'bolsos' da cor do fundo; os anéis ficam por cima."""
    m = M((135, 170, 720, 450), (x, y, w, h))
    c1, c2, c3, c4 = (241, 253), (359, 368), (478, 253), (594, 368)
    grad(R(s, m, 241, 253, 594, 368, F), ((0, D), (.5, F), (1, D)), 0)
    for p, c in zip((c1, c2, c3, c4), (D, F, F, D)):
        grad(oval(s, *m.p(p), 116 * m.sx, c), ((0, c), (1, F)), 90)
    pockets = ((299, 170, 420, 301, "High quality business"), (536, 170, 720, 316, "Underpriced market"), (135, 305, 301, 450, "Attractive structure"), (418, 320, 537, 450, "Strong cash generation"))
    for x0, y0, x1, y1, t in pockets:
        bx = m.box(x0, y0, x1, y1); rr(s, *bx, W, .2)
    for p, c, n in zip((c1, c2, c3, c4), (D, F, F, D), "1234"):
        ax, ay = m.p(p)
        oval(s, ax, ay, 116 * m.sx, c)
        oval(s, ax, ay, 90 * m.sx, W)
        tx(s, ax - .25, ay - .25, .5, .5, n, size=18, color=c, bold=True)
    for x0, y0, x1, y1, t in pockets:
        tm(s, m, x0 + 6, y0 + 12, x1 - 6, y1 - 12, t, size=8)


def boardroom(s, x, y, w, h):
    m = M((85, 138, 535, 348), (x, y, w, h))
    def chair(cx, cy, d):
        # d: lado da mesa. Encosto curvo, braços e assento apontando para a mesa.
        vx, vy = {"down": (0, 1), "up": (0, -1), "right": (1, 0), "left": (-1, 0)}[d]
        def rc(a, b, hw, hh, col):   # a: ao longo do eixo; b: transversal
            ax, ay = cx + vx * a + (-vy) * b, cy + vy * a + vx * b
            hx_, hy_ = (hw, hh) if vy else (hh, hw)
            bx = m.box(ax - hx_, ay - hy_, ax + hx_, ay + hy_)
            return bx, col
        for a, b, hw, hh, col, adj in ((-19, 0, 18, 2.5, "595959", .5), (-23, 0, 13, 2.2, A, .5), (0, -17, 2.2, 11, "5A5A5A", .3), (0, 17, 2.2, 11, "5A5A5A", .3), (2, 0, 13, 13, A, .28)):
            bx, c = rc(a, b, hw, hh, col)
            rr(s, *bx, c, adj)
    for cx in (195, 265, 335, 405):
        chair(cx, 180, "down"); chair(cx, 306, "up")
    chair(112, 242, "right"); chair(506, 242, "left")
    b = m.box(146, 211, 472, 273)
    grad(rr(s, *b, D, .3), ((0, "272727"), (.5, "808080"), (1, "272727")), 0)
    rr(s, *m.box(158, 222, 462, 263), "595959", .3)


SLIDES = [
    ("Isometric solids give scale without a chart", "Prisms and slabs drawn face by face, each with its own tone",
     [("Staircase into arrow", "3R Petroleum p.28", iso_stairs), ("Slabs fading downward", "Meliuz p.62", iso_plates), ("Columns on a floor", "Meliuz p.82", iso_columns),
      ("Plate with coloured rails", "RD Saúde p.55", extruded_rails), ("Plinth under a picture", "RD Saúde p.76", plinth), ("Card with bevelled lips", "3R Petroleum p.26", bevel_panel)]),
    ("Walls turn flat panels into a space", "A darker trapezoid is enough to make one plane recede",
     [("Tapered wall", "Mercado Libre p.26", tapered_wall), ("Gutter between two pages", "RD Saúde p.20", gutter_wall), ("Legend opening into a map", "RD Saúde p.14", wall_zoom),
      ("Slab cards with link band", "Sabesp p.2", slab_cards), ("Ramp before a title", "Intelbras p.11", wedge_tab_row), ("Orbit discs on a panel", "Senior p.19", orbit_rows)]),
    ("Beams connect the data to its explanation", "The narrow end matches the data; the wide end matches the card",
     [("Solid beam from a bar", "RD Saúde p.39", beam_bars), ("Slice flaring into a box", "RD Saúde p.12", donut_flare), ("Arc ribbons feeding rows", "Intelbras p.30", arc_ribbons),
      ("Bowtie through a hub", "BTG Pactual p.3", bowtie), ("Corridor of flared wedges", "AB InBev p.39", flare_wedges), ("Shard burst between cards", "Vibra p.27", shard_burst)]),
    ("Ribbons and folds imply paper behind the slide", "A small dark triangle or a mirrored tail shows the back of the strip",
     [("Folded ribbon timeline", "Sabesp p.2", ribbon_timeline), ("Accordion fold arrows", "BTG Pactual p.80", accordion), ("Corner ribbon on a card", "Meliuz p.61", corner_ribbon),
      ("Active tab with fold", "BTG Pactual p.31", nav_tab), ("Cards on a stepped base", "Sabesp p.11", fold_tabs), ("Interlocked chevrons", "BTG Pactual p.99", chevrons)]),
    ("Layers separate what matters from the page", "Veils, offset plates and overlaps push the rest of the slide back",
     [("Card between two plates", "Sabesp p.22", modal_sandwich), ("Mitred wedges behind a modal", "RBI p.14", l_wedges), ("Spotlight on a dimmed page", "RD Saúde p.62", spotlight),
      ("Lenses with cards on the edge", "Sabesp p.37", lens_stack), ("Half ring with staggered cards", "Vasta p.6", half_ring), ("Overlapping glass arrows", "3R Petroleum p.103", overlap_arrows)]),
    ("Light and small scenes finish the set", "Gradients suggest volume; these two bar styles are for looks, not exact reading",
     [("Bars dissolving to the floor", "CSN Liability p.8", fade_waterfall), ("Tube bars", "CSN Liability p.4", tube_bars), ("Glossy tokens on a scatter", "Alupar p.10", tokens),
      ("Pinched pill stack", "Senior p.14", pinch_pills), ("Ring chain", "Senior p.15", ring_chain), ("Boardroom plan", "Kering p.25", boardroom)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the technique comes from the source.")
    ss.save(prs, OUT)
