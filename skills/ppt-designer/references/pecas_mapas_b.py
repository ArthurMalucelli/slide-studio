"""Peças de mapa do catálogo (lote B), com conteúdo fictício. Copie a função para o build do slide e troque os textos.
Todas as coordenadas de desenho estão em pixels do recorte de origem; M as leva para a caixa recebida.
Uso: python3 pecas_mapas_b.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import copy
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pecas_base import *  # noqa: E402,F403
from pecas_base import dark, light  # noqa: E402

L, C_, RT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE
mix = ss.mix
DASH = ss.MSO_LINE_DASH_STYLE.DASH
DOT = ss.MSO_LINE_DASH_STYLE.ROUND_DOT


# ---------- Texto ----------

def _p(s, m, b, paras, px, al=L, anchor=MID, wrap=False, fill=None, line=None, dash=False, shape=None, adj=None, color=INK,
       spacing=None, font=None):
    """Texto em caixa de pixels do recorte. paras: str ou lista de parágrafos; parágrafo: str ou lista de (texto, opções)."""
    k = m.sx * 72
    if isinstance(paras, str): paras = [paras]
    runs = []
    for pa in paras:
        if isinstance(pa, str): pa = [(pa, {})]
        runs.append([(t, {"bold": o.get("bold", False), "italic": o.get("italic", False), "color": o.get("color", color),
                          "size": round(o.get("px", px) * k, 1)}) for t, o in pa])
    kw = {"shape": shape} if shape else {}
    sp = ss.text(s, *m.box(*b), runs, align=al, anchor=anchor, fill=fill, line=line, dash=dash, margin=0.0, **kw)
    sp.text_frame.word_wrap = wrap
    if adj is not None: sp.adjustments[0] = adj
    for pg in sp.text_frame.paragraphs:
        if spacing: pg.line_spacing = spacing
        if font:
            for r in pg.runs: r.font.name = font
    return sp


def _t(s, m, b, t, px, color=INK, bold=False, italic=False, al=C_, anchor=MID, rot=None, **k):
    sp = _p(s, m, b, [[(t, {"bold": bold, "italic": italic, "color": color})]], px, al=al, anchor=anchor, **k)
    if rot is not None: sp.rotation = rot
    return sp


def _chip(s, m, b, t, px, fill=D, color=W, adj=.25, bold=True, border=None):
    return _t(s, m, b, t, px, color=color, bold=bold, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=adj, line=border)


def _mold(s, m, b, label, px=14, fill=None, round_=None):
    """Molde cinza para foto, print ou logo real."""
    bx = m.box(*b)
    sp = rr(s, *bx, fill or G2, round_) if round_ else ss.rect(s, *bx, fill or G2)
    _t(s, m, b, label, px, color=G4)
    return sp


# ---------- Efeitos ----------

def _effect(sp):
    e = sp._element.spPr.find(qn("a:effectLst"))
    if e is None:
        sp.shadow.inherit = False
        e = sp._element.spPr.find(qn("a:effectLst"))
    return e


def shadow(sp, blur=6, dist=3, ang=45, col="000000", alpha=.35):
    o = etree.SubElement(_effect(sp), qn("a:outerShdw"))
    o.set("blurRad", str(int(blur * 12700))); o.set("dist", str(int(dist * 12700))); o.set("dir", str(int(ang * 60000)))
    o.set("algn", "ctr"); o.set("rotWithShape", "0")
    c = etree.SubElement(o, qn("a:srgbClr")); c.set("val", ss.hx(col))
    etree.SubElement(c, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    return sp


def glow(sp, rad, col, alpha=.55):
    o = etree.SubElement(_effect(sp), qn("a:glow")); o.set("rad", str(int(rad * 12700)))
    c = etree.SubElement(o, qn("a:srgbClr")); c.set("val", ss.hx(col))
    etree.SubElement(c, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    return sp


def soft(sp, rad):
    etree.SubElement(_effect(sp), qn("a:softEdge")).set("rad", str(int(rad * 12700)))
    return sp


def radial(sp, stops):
    """Degradê radial do centro para fora; aceita alfa em cada parada."""
    grad(sp, stops, 0)
    gf = sp._element.spPr.find(qn("a:gradFill"))
    for c in gf.findall(qn("a:lin")): gf.remove(c)
    pa = etree.SubElement(gf, qn("a:path")); pa.set("path", "circle")
    ft = etree.SubElement(pa, qn("a:fillToRect"))
    for side in "ltrb": ft.set(side, "50000")
    return sp


# ---------- Formas ----------

def _multi(s, rings, fill, edge=None, ew=.5):
    """Vários anéis numa forma só (um degradê corre sobre todos). Escala 1/5000 pol., para pontos pequenos."""
    k = 5000
    rs = [[(round(a * k), round(b * k)) for a, b in r] for r in rings if len(r) > 2]
    fb = s.shapes.build_freeform(rs[0][0][0], rs[0][0][1], scale=914400 / k)
    fb.add_line_segments(rs[0][1:], close=True)
    for r in rs[1:]:
        fb.move_to(*r[0]); fb.add_line_segments(r[1:], close=True)
    sp = fb.convert_to_shape(); sp.shadow.inherit = False
    # cada anel vira um a:path próprio: sobreposição não abre buraco (o preenchimento de um só path é par-ímpar)
    pl = sp._element.spPr.find(qn("a:custGeom")).find(qn("a:pathLst"))
    src = pl[0]; cur = None
    for el in list(src):
        if el.tag == qn("a:moveTo"):
            cur = etree.SubElement(pl, qn("a:path")); cur.set("w", src.get("w")); cur.set("h", src.get("h"))
        cur.append(el)
    pl.remove(src)
    ss.paint(sp.fill, fill)
    if edge: sp.line.color.rgb = ss.rgb(edge); sp.line.width = Pt(ew)
    else: sp.line.fill.background()
    return sp


def _dots(s, m, pts, d, fill, alpha=None):
    """Muitos pontos como elipses nativas num grupo só: pts em polegadas, d em pixels do recorte. Um freeform ficaria
    facetado (o PowerPoint arredonda os vértices a 1/576 pol.), e clonar o XML evita o custo de add_shape em cada ponto."""
    g = s.shapes.add_group_shape()
    dd = d * m.sx
    first = g.shapes.add_shape(MSO_SHAPE.OVAL, Inches(pts[0][0] - dd / 2), Inches(pts[0][1] - dd / 2), Inches(dd), Inches(dd))
    first.shadow.inherit = False
    ss.paint(first.fill, fill); first.line.fill.background()
    if alpha is not None: ss.set_alpha(first, alpha)
    nid = max(int(i) for i in s.shapes._spTree.xpath("//@id") if i.isdigit()) + 1
    for i, (cx, cy) in enumerate(pts[1:]):
        el = copy.deepcopy(first._element)
        c = el.find(qn("p:nvSpPr")).find(qn("p:cNvPr")); c.set("id", str(nid + i)); c.set("name", f"Dot {i + 2}")
        off = el.spPr.find(qn("a:xfrm")).find(qn("a:off"))
        off.set("x", str(int(Inches(cx - dd / 2)))); off.set("y", str(int(Inches(cy - dd / 2))))
        g._element.append(el)
    g.shapes._recalculate_extents()
    return g


def _o(s, m, cx, cy, d, fill=None, **k):
    return oval(s, *m.p((cx, cy)), d * m.sx, fill, **k)


def _path(s, m, pts, color, width=1.0, dash=None, cap=None):
    """Linha aberta editável, em pixels do recorte."""
    q = [(round(a * 1000), round(b * 1000)) for a, b in m.ps(pts)]
    fb = s.shapes.build_freeform(q[0][0], q[0][1], scale=914.4)
    fb.add_line_segments(q[1:], close=False)
    sp = fb.convert_to_shape(); sp.shadow.inherit = False
    sp.fill.background(); sp.line.color.rgb = ss.rgb(color); sp.line.width = Pt(width)
    if dash: sp.line.dash_style = dash
    if cap: sp.line._get_or_add_ln().set("cap", cap)
    return sp


def _smooth(pts, n=10):
    """Catmull-Rom pelos pontos dados."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * p1[c] + (p2[c] - p0[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t ** 2
                                   + (3 * p1[c] - p0[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def _rpoly(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0, n=8):
    """Contorno de retângulo com raio próprio em cada canto."""
    out = []
    for (cx, cy, r, a0) in ((x0 + tl, y0 + tl, tl, 180), (x1 - tr, y0 + tr, tr, 270), (x1 - br, y1 - br, br, 0), (x0 + bl, y1 - bl, bl, 90)):
        if r == 0:
            out.append((cx, cy)); continue
        out += [(cx + r * math.cos(math.radians(a0 + 90 * i / n)), cy + r * math.sin(math.radians(a0 + 90 * i / n))) for i in range(n + 1)]
    return out


def _pin(s, m, tipx, tipy, hgt, fill, hole=W):
    """Gota de localização: ponta em (tipx, tipy)."""
    r = hgt * .36
    cy = tipy - hgt + r
    ring = [(tipx, tipy)]
    for i in range(25):
        a = math.radians(150 + 240 * i / 24)
        ring.append((tipx + r * math.cos(a), cy + r * math.sin(a)))
    sp = poly(s, m, ring, fill)
    _o(s, m, tipx, cy, r * .85, hole)
    return sp


def _flag(s, m, cx, cy, d, c1, c2):
    """Bandeira genérica em círculo: três faixas. Sem bandeira real."""
    r = d / 2
    circ = lambda i, n=40: (cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
    poly(s, m, [circ(i) for i in range(40)], c1)
    band = [(x, y) for x, y in _clip([circ(i) for i in range(40)], [(cx - r * .36, cy - r), (cx + r * .36, cy - r), (cx + r * .36, cy + r), (cx - r * .36, cy + r)])]
    poly(s, m, band, c2)


def _magnifier(s, m, cx, cy, d, col=INK):
    r = d * .36
    hx0, hy0 = cx + r * .72, cy + r * .72
    _path(s, m, [(hx0, hy0), (cx + d * .55, cy + d * .55)], col, 3.0 * m.sx * 72 * .55, cap="rnd")
    _o(s, m, cx, cy, r * 2, W, border=col, width=max(.5, 2.2 * m.sx * 72 * .55))


def _chev(s, m, x, y, w, h, fill):
    """Divisa cheia, ponta à direita."""
    t = w * .5
    return poly(s, m, ((x, y), (x + t, y), (x + w, y + h / 2), (x + t, y + h), (x, y + h), (x + w - t, y + h / 2)), fill)


# ---------- Geometria ----------

def _area(r):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:] + r[:1]))) / 2


def _half(r, a, b, c):
    """Mantém o lado a*x + b*y <= c."""
    out = []
    n = len(r)
    for i in range(n):
        p, q = r[i], r[(i + 1) % n]
        dp_, dq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if dp_ <= 0: out.append(p)
        if (dp_ < 0 < dq) or (dq < 0 < dp_):
            t = dp_ / (dp_ - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def _clip(r, conv):
    """Recorta o anel r por um polígono convexo (qualquer sentido)."""
    sg = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(conv, conv[1:] + conv[:1]))
    for u, v in zip(conv, conv[1:] + conv[:1]):
        if not r: break
        nx, ny = v[1] - u[1], u[0] - v[0]
        if sg < 0: nx, ny = -nx, -ny
        r = _half(r, nx, ny, nx * u[0] + ny * u[1])
    return r


def _rect(b):
    return [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])]


def gmap(s, m, box, shapes, fill, edge=None, ew=.5, bounds=None, clip=None, merge=False, minpx=2.5):
    """Mapa: encaixa a extensão (ou bounds) em box, em pixels do recorte, recortando em clip (retângulo ou convexo).
    merge=True junta tudo da mesma cor numa forma só. Devolve ((lon, lat) -> pixel, {cor: forma})."""
    x0, y0, x1, y1 = box
    if bounds is None:
        big = [p for v in shapes.values() for r in v["rings"] if _area(r) >= .25 for p in r]
        bounds = (min(p[0] for p in big), max(p[0] for p in big), min(p[1] for p in big), max(p[1] for p in big))
    lo0, lo1, la0, la1 = bounds
    to = lambda lo, la: (x0 + (lo - lo0) / (lo1 - lo0) * (x1 - x0), y0 + (la1 - la) / (la1 - la0) * (y1 - y0))
    if clip is None: clip = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)
    cv = _rect(clip) if isinstance(clip, tuple) else clip
    buckets = {}
    for key, v in shapes.items():
        c = fill(key) if callable(fill) else fill.get(key) if isinstance(fill, dict) else fill
        if not c: continue
        for ring in v["rings"]:
            r = [to(*p) for p in ring]
            r = _clip(r, cv)
            if len(r) < 3 or _area(r) < minpx: continue
            q = m.ps(r)
            if merge: buckets.setdefault(c, []).append(q)
            else: ss.poly(s, q, c, edge, ew)
    out = {c: _multi(s, rs, c, edge, ew) for c, rs in buckets.items()}
    return to, out


def _sub(*keys):
    c = countries_50m()
    return {k: c[k] for k in keys if k in c}


_LAC = ("MEX", "GTM", "BLZ", "HND", "SLV", "NIC", "CRI", "PAN", "CUB", "JAM", "HTI", "DOM", "PRI", "BHS", "TTO", "COL", "VEN", "GUY", "SUR", "ECU", "PER", "BOL", "BRA", "PRY", "URY", "CHL", "ARG")
_SA = ("COL", "VEN", "GUY", "SUR", "ECU", "PER", "BOL", "BRA", "PRY", "URY", "CHL", "ARG")


def _latam():
    return _sub(*_LAC)


def _world():
    return {k: v for k, v in countries_50m().items() if k != "ATA"}


def _pip(pt, ring):
    x, y = pt; inside = False
    for (a, b), (c, d) in zip(ring, ring[1:] + ring[:1]):
        if (b > y) != (d > y) and x < (c - a) * (y - b) / (d - b) + a: inside = not inside
    return inside


_SMP = {}


def _sample(shapes, n, hubs, weights=None, seed=1, hub_share=.65, keyname=""):
    """Pontos fictícios lon/lat dentro das formas: parte em volta de polos urbanos, parte espalhada por estado."""
    key = (keyname, n, seed, hub_share)
    if key in _SMP: return _SMP[key]
    rnd = random.Random(seed)
    rings = [(k, r, min(p[0] for p in r), max(p[0] for p in r), min(p[1] for p in r), max(p[1] for p in r))
             for k, v in shapes.items() for r in v["rings"] if _area(r) > .02]
    def inside(lo, la):
        return any(a <= lo <= b and c <= la <= d and _pip((lo, la), r) for _, r, a, b, c, d in rings)
    keys = [k for k, *_ in rings]
    wts = [(weights or {}).get(k, 1) * _area(r) ** .6 for k, r, *_ in rings]
    hw = [h[3] for h in hubs]
    out = []
    while len(out) < n:
        if rnd.random() < hub_share and hubs:
            h = rnd.choices(hubs, hw)[0]
            lo, la = rnd.gauss(h[0], h[2]), rnd.gauss(h[1], h[2] * .85)
        else:
            _, r, a, b, c, d = rnd.choices(rings, wts)[0]
            lo, la = rnd.uniform(a, b), rnd.uniform(c, d)
        if inside(lo, la): out.append((lo, la))
    _SMP[key] = out
    return out


_BR_HUBS = [(-46.6, -23.5, .9, 16), (-43.3, -22.8, .6, 9), (-43.9, -19.9, .7, 7), (-47.1, -22.8, .8, 8), (-49.3, -25.4, .8, 5), (-51.2, -30, .9, 5), (-48.5, -27.5, .7, 3),
            (-38.5, -13, .8, 4), (-34.9, -8.1, .6, 5), (-38.5, -3.8, .7, 4), (-35.2, -5.8, .5, 2), (-49.3, -16.7, .8, 4), (-47.9, -15.8, .4, 2), (-54.6, -20.5, 1, 1.5), (-56.1, -15.6, 1, 1.5),
            (-48.5, -1.4, .7, 1.5), (-44.3, -2.5, .7, 1.2), (-60, -3.1, .5, .6), (-42.8, -5.1, .6, 1.2), (-40.3, -20.3, .6, 3), (-37, -10.9, .5, 1.5), (-35.7, -9.6, .5, 1.5), (-48.8, -21.5, 1.2, 8), (-52, -24, 1.2, 3), (-41, -15, 1.4, 2.5)]

_US_HUBS = [(-74, 40.7, 1.2, 12), (-77, 39, 1.1, 8), (-71.2, 42.3, .9, 5), (-80, 40.4, 1, 5), (-84, 41, 1.6, 9), (-87.7, 41.8, 1.3, 7), (-84.4, 33.8, 1.4, 6), (-81.5, 35.5, 1.2, 6), (-81.5, 28.3, 1.2, 5),
            (-90, 35, 2, 5), (-95.4, 29.8, 1.3, 5), (-97, 32.8, 1.3, 5), (-93.3, 44.9, 1.5, 3), (-90.2, 38.6, 1.3, 4), (-94.5, 39, 1.5, 3), (-104.9, 39.7, 1.1, 3), (-112, 33.4, 1.1, 2), (-118.2, 34, 1, 5),
            (-122, 37.6, .9, 3.5), (-122.3, 47.5, .9, 2.5), (-111.9, 40.7, .8, 1)]


def _voronoi(ring, n, seed=7, k=26):
    """Malha fictícia de células dentro de um anel: serve de municípios onde não há dado municipal. Devolve [(centro, anel)]."""
    a, b = min(p[0] for p in ring), max(p[0] for p in ring)
    c, d = min(p[1] for p in ring), max(p[1] for p in ring)
    rnd = random.Random(seed)
    seeds = []
    while len(seeds) < n:
        q = (rnd.uniform(a, b), rnd.uniform(c, d))
        if _pip(q, ring): seeds.append(q)
    cells = []
    for i, q in enumerate(seeds):
        near = sorted((p for j, p in enumerate(seeds) if j != i), key=lambda p: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)[:k]
        cell = list(ring)
        for p in near:
            nx, ny = p[0] - q[0], p[1] - q[1]
            cell = _half(cell, nx, ny, nx * (p[0] + q[0]) / 2 + ny * (p[1] + q[1]) / 2)
            if len(cell) < 3: break
        if len(cell) > 2: cells.append((q, cell))
    return cells


_SP_CELLS = None


def _sp_cells():
    global _SP_CELLS
    if _SP_CELLS is None:
        ring = max(states("BRA")["SP"]["rings"], key=_area)
        _SP_CELLS = _voronoi(ring, 500, seed=11)
    return _SP_CELLS


_SP_FOOT = "11010011001110110010111001110011011100100110100111110111000110001101100100110000110111111011111010110011001101111001111110100000111011111001001111111000111100001001010111100101111101111001110010111111001000000101101101110111101101111100011111111111110110110000110000110001000100001011101110010101101111011001111100001010111111101001010011100111011011011011101101110001011111110011101001001001101011001110011001111011111101111110001111101111110111100101101110011101111111011011111111110011011011101010"
_SP_ADJ = "03101403430111001410013320101400133011120101000140001034143001021030013002011121002000000400300200110200110011000130201001013111014301000220110000000334133030310140110210130020000000400200104100001000041411201020100010001000010100000011104300000010001003102111030142011120104010330101000003003001000330010120140031414103000003000101100200001000401132200110010030011114101010002110000210010110004100110004101104000000111030100000131011000101003001022010000101010010000000104100000004302211100003000301"


def _lobes(cell, ring):
    """Recortar um anel côncavo pode ligar dois lobos por um lado fora da terra; separa a célula nesses lados."""
    br = []
    n = len(cell)
    for i in range(n):
        p, q = cell[i], cell[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(dx, dy)
        if ln < 1e-6: continue
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        nx, ny = -dy / ln * .004, dx / ln * .004
        if not _pip((mx + nx, my + ny), ring) and not _pip((mx - nx, my - ny), ring): br.append(i)
    if len(br) < 2: return [cell]
    i, j = br[0], br[1]
    return [x for part in (cell[i + 1:j + 1], cell[j + 1:] + cell[:i + 1]) if len(part) > 2 for x in _lobes(part, ring)]


def _sp_mesh(s, m, box, color_of, ew=.2, tint=.3):
    """São Paulo em células, uma forma por classe (cor), com divisas num tom claro da própria classe."""
    cells = _sp_cells()
    ring = max(states("BRA")["SP"]["rings"], key=_area)
    pts = [p for _, r in cells for p in r]
    lo0, lo1, la0, la1 = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
    x0, y0, x1, y1 = box
    to = lambda p: (x0 + (p[0] - lo0) / (lo1 - lo0) * (x1 - x0), y0 + (la1 - p[1]) / (la1 - la0) * (y1 - y0))
    plain = {}
    for i, (q, r) in enumerate(cells):
        for lobe in _lobes(r, ring):
            plain.setdefault(color_of(i), []).append(m.ps([to(p) for p in lobe]))
    for c, rs in plain.items():
        _multi(s, rs, c, light(c, tint), ew)


# ---------- Coropléticos do Brasil ----------

def tier_choropleth_tile(s, x, y, w, h):
    """Mapa em cinco tons e tabela no mesmo ladrilho, com chamada tracejada em cotovelo. Cury Construtora p.7."""
    m = M((0, 0, 900, 358), (x, y, w, h))
    R(s, m, 2, 8, 898, 350, light(T, .72), F, width=.75)
    t1, t2, t3, t4, t5 = dark(D, .5), D, mix(D, F, .55), light(F, .22), light(F, .55)
    cl = {"SP": t1, "MG": t1, "RJ": t1, "PA": t2, "AP": t2, "MA": t2, "PI": t2, "CE": t2, "BA": t2, "GO": t2, "PR": t2, "RS": t2, "PE": t2, "PB": t2, "AM": t3, "AC": t3, "MT": t3, "TO": t4, "RN": t3, "RR": t4,
          "RO": t4, "MS": t4, "AL": t4, "SE": t3, "ES": t4, "SC": t4, "DF": t5}
    gmap(s, m, (12, 14, 345, 342), states("BRA"), cl, W, .25)
    for cx, a, b in ((497, "Region", ""), (653, "Absolute", "gap"), (805, "Relative", "gap")):
        if b:
            _t(s, m, (cx - 80, 34, cx + 80, 60), a, 19, color=D, bold=True)
            _t(s, m, (cx - 80, 58, cx + 80, 84), b, 19, color=D, bold=True)
        else:
            _t(s, m, (cx - 80, 58, cx + 80, 84), a, 19, color=D, bold=True)
    ss.line(s, *m.p((418, 89)), *m.p((888, 89)), D, 1.0, dash=False)
    rows = (("Midwest", "587,115", "10%"), ("South", "712,812", "12%"), ("North", "728,906", "12%"), ("Northeast", "1,634,642", "27%"), ("Southeast", "2,313,841", "39%"))
    for i, (a, b, c) in enumerate(rows):
        yy = 122 + i * 48.5
        _t(s, m, (415, yy - 16, 580, yy + 16), a, 19, color=D, bold=True)
        _t(s, m, (575, yy - 16, 730, yy + 16), b, 18, color=D)
        _t(s, m, (725, yy - 16, 885, yy + 16), c, 18, color=D)
    _path(s, m, [(245, 258), (245, 301), (272, 301)], D, 1.0, dash=DASH)
    _p(s, m, (272, 275, 401, 326), ["Top two states", "hold 29% of gap"], 13.5, al=C_, fill=W, line=D, dash=True)


def three_tier_legend(s, x, y, w, h):
    """Mapa em três classes com linha de quadrados de legenda; sem linhas de chamada. Intelbras p.2."""
    m = M((0, 0, 574, 428), (x, y, w, h))
    a, b, c = F, light(F, .45), light(A, .68)
    cl = {k: b for k in states("BRA")}
    cl.update({k: a for k in ("BA", "MG", "SP", "PR", "SC", "RS", "RJ")})
    cl.update({k: c for k in ("AP", "TO", "AC")})
    cl["RR"] = W; cl["DF"] = W
    gmap(s, m, (88, 10, 428, 365), states("BRA"), {k: v for k, v in cl.items() if k != "RR"}, W, .6)
    # Roraima fica vazado, só com o contorno, como no original
    gmap(s, m, (88, 10, 428, 365), {"RR": states("BRA")["RR"]}, W, b, .6, bounds=_bounds_br())
    for cx, col, t in ((13, a, "15+ units"), (210, b, "5-14 units"), (420, c, "1-4 units")):
        R(s, m, cx, 390, cx + 18, 410, col)
        _t(s, m, (cx + 38, 382, cx + 180, 414), t, 22, al=L)


def _bounds_br():
    big = [p for v in states("BRA").values() for r in v["rings"] if _area(r) >= .25 for p in r]
    return (min(p[0] for p in big), max(p[0] for p in big), min(p[1] for p in big), max(p[1] for p in big))


_REG = {"N": ("AC", "AM", "RR", "RO", "PA", "AP", "TO"), "NE": ("MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"), "CO": ("MT", "MS", "GO", "DF"), "SE": ("SP", "RJ", "MG", "ES"), "S": ("PR", "SC", "RS")}


def region_ramp_values(s, x, y, w, h):
    """Cinco regiões em rampa de um tom, com o percentual fora de cada região na cor dela. Vasta p.27."""
    m = M((0, 0, 613, 555), (x, y, w, h))
    ramp = {"NE": dark(D, .1), "N": mix(D, F, .5), "CO": F, "SE": light(F, .5), "S": light(F, .75)}
    cl = {k: ramp[r] for r, ks in _REG.items() for k in ks}
    box = (62, 35, 560, 548)
    # sombra única atrás de tudo, para o relevo do original
    _, base = gmap(s, m, box, states("BRA"), lambda k: G4, merge=True)
    for sp in base.values(): shadow(sp, 4, 3, 90, "000000", .45)
    gmap(s, m, box, states("BRA"), cl, W, .25)
    _p(s, m, (390, 10, 610, 66), [[("Schools per", {"italic": True})], [("region, % of total", {"italic": True})]], 22)
    for b, t, r in (((505, 85, 610, 115), "26.0%", "NE"), ((10, 118, 100, 148), "22.5%", "N"), ((148, 323, 235, 353), "21.3%", "CO"), ((513, 360, 610, 390), "19.8%", "SE"), ((385, 493, 480, 523), "18.3%", "S")):
        _t(s, m, b, t, 25, color=ramp[r], bold=True, al=L)
    ss.line(s, *m.p((503, 285)), *m.p((613, 282)), A, 1.0, dash=False)


def pill_cluster_card(s, x, y, w, h):
    """Pílulas com as cores dos estados, sem linhas de chamada, em cartão cinza com filete e parede. 3R Petroleum p.2."""
    m = M((0, 0, 760, 622), (x, y, w, h))
    poly(s, m, ((727, 30), (745, 18), (745, 596), (727, 606)), G3)
    R(s, m, 12, 30, 727, 606, G1)
    poly(s, m, ((12, 18), (24, 9), (745, 9), (734, 18)), light(D, .3))
    R(s, m, 12, 18, 734, 31, D)
    poly(s, m, ((734, 18), (745, 9), (745, 21), (734, 31)), dark(D, .3))
    R(s, m, 12, 605, 734, 619, D)
    poly(s, m, ((734, 605), (745, 597), (745, 610), (734, 619)), dark(D, .3))
    R(s, m, 31, 48, 43, 96, D); R(s, m, 31, 96, 43, 127, F)
    _t(s, m, (57, 56, 400, 96), "Location", 33, color=D, bold=True, al=L)
    _p(s, m, (55, 102, 600, 133), [[("Spread", {"bold": True, "color": F}), (" and ", {}), ("diverse", {"bold": True, "color": F}), (" asset portfolio", {})]], 24, color=INK)
    tones = {k: G3 for k in states("BRA")}
    for k in ("AC", "AM", "RO", "PA", "MT", "MG", "RS", "PR"): tones[k] = "A8A8A8" if k in ("MT", "MG", "PR") else G3
    for k in ("TO", "PI", "GO", "MS", "BA", "RO", "RR", "AP", "SC", "SP", "ES", "PE"): tones[k] = G2
    cl = dict(tones); cl.update({"CE": dark(D, .1), "RN": dark(D, .1), "BA": A, "RJ": F})
    gmap(s, m, (35, 158, 445, 580), states("BRA"), cl, W, .35)
    for yy, c, a, b in ((190, dark(D, .1), "Northern", "Cluster"), (296, A, "Central", "Cluster"), (412, F, "Offshore", "Cluster")):
        _p(s, m, (477, yy, 701, yy + 84), [a, b], 28, al=C_, color=W, fill=c, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=.16)


def greyscale_dark_table(s, x, y, w, h):
    """Mapa em cinco cinzas, legenda tracejada e painel escuro com tabela de fios brancos. Meliuz p.106."""
    m = M((0, 0, 900, 396), (x, y, w, h))
    gs = {"p": "D0D0D0", "l": "ABABAB", "m": "757575", "d": "404040", "b": "000000"}
    cl = {k: gs["l"] for k in states("BRA")}
    cl.update({k: gs["p"] for k in ("RR", "AP", "AC", "TO", "RO", "PI", "RN", "PB", "SE", "AL", "CE")})
    cl.update({k: gs["m"] for k in ("MG", "PR", "SC", "RS")})
    cl.update({"SP": gs["b"], "RJ": gs["b"]})
    gmap(s, m, (15, 2, 402, 396), states("BRA"), cl, merge=True)
    R(s, m, 2, 243, 133, 355, W, INK, dash=True, width=.6)
    _t(s, m, (6, 247, 130, 265), "% of total units", 10.5)
    for i, (c, t) in enumerate((("p", "Below 1%"), ("l", "1% to 5%"), ("m", "5% to 10%"), ("d", "10% to 30%"), ("b", "Above 30%"))):
        yy = 268 + i * 17
        R(s, m, 8, yy, 22, yy + 11, gs[c])
        _t(s, m, (27, yy - 2, 130, yy + 13), t, 10, al=L)
    pn = "404040"
    R(s, m, 437, 55, 900, 341, pn)
    _t(s, m, (453, 64, 880, 92), "Unit distribution by region", 16, color=W, bold=True, al=L)
    cols_ = (437, 516, 594, 668, 744, 823, 893)
    rows = (("", "Group A", "Group B", "Group C", "Group D", "Total"), ("Northeast", "721", "229", "922", "239", "2111"), ("North", "230", "76", "290", "57", "653"), ("Midwest", "263", "235", "431", "130", "1059"),
            ("Southeast", "1680", "1807", "1821", "1917", "7225"), ("South", "496", "485", "904", "394", "2279"), ("Total", "3390", "2832", "4368", "2737", "13327"))
    y0, rh = 129, 21.6
    for i, r in enumerate(rows):
        yy = y0 + (i * rh if i == 0 else i * rh + 1)
        for j, t in enumerate(r):
            _t(s, m, (cols_[j] + 7, yy, cols_[j + 1], yy + rh), t, 10, color=W, bold=True, al=L)
    for i in range(len(rows) + 1):
        yy = y0 + i * rh + (1 if i else 0)
        ss.line(s, *m.p((437, yy)), *m.p((893, yy)), W, 1.0 if i in (0, 1, 7) else .75, dash=False)
    for xx in cols_:
        ss.line(s, *m.p((xx, y0)), *m.p((xx, y0 + 7 * rh + 1)), W, .75, dash=False)
    _t(s, m, (445, 285, 880, 305), "Total units in the country: 18,684", 11, color=W, al=L)
    _p(s, m, (445, 312, 880, 332), [[("Share of the four largest ", {}), ("players", {"italic": True}), (": 72%", {})]], 11, color=W)


# ---------- São Paulo em células ----------

def adjacency_tier_map(s, x, y, w, h):
    """Estado em células: rede atual em escuro e tons por distância a ela, saindo do painel. Sabesp p.34."""
    m = M((0, 0, 900, 326), (x, y, w, h))
    sp = R(s, m, 2, 43, 710, 319, G1); shadow(sp, 4, 2, 45, "000000", .35)
    t0, t1, t2, t3 = D, mix(F, D, .1), light(F, .28), light(F, .58)
    pal = {"0": t0, "1": t1, "2": t2, "3": t3, "4": G3}
    _sp_mesh(s, m, (458, 8, 880, 312), lambda i: pal[_SP_ADJ[i]], ew=.15, tint=.45)
    for i, (c, t) in enumerate(((t0, "Current network"), (t1, "Target: direct border"), (t2, "Target: one unit away"), (t3, "Target: two units away"), (G3, "Others"))):
        yy = 87 + i * 20.5
        R(s, m, 23, yy - 6, 37, yy + 6, c)
        _t(s, m, (56, yy - 10, 440, yy + 10), t, 16, al=L)
    _p(s, m, (17, 238, 600, 314), [[("78% of target units ", {"bold": True}), ("share a ", {}), ("direct", {"bold": True})],
                                   [("border with the network. ", {"bold": True}), ("Expansion is a ", {})],
                                   [("network extension", {"bold": True}), (", not greenfield", {})]], 21, anchor=TOP)


def municipal_footprint_chips(s, x, y, w, h):
    """Estado em células, servidas em cor viva e demais em cinza, com dois selos nos cantos. Sabesp p.2."""
    m = M((0, 0, 733, 645), (x, y, w, h))
    R(s, m, 23, 18, 733, 645, G4)
    R(s, m, 13, 2, 718, 636, "EFEFEF")
    _t(s, m, (33, 32, 600, 76), "Location that matters", 37, bold=True, al=L)
    _t(s, m, (30, 80, 700, 114), "A dense footprint across the core state", 26, color=G4, italic=True, al=L)
    _sp_mesh(s, m, (52, 174, 632, 560), lambda i: F if _SP_FOOT[i] == "1" else G3, ew=.15)
    _p(s, m, (51, 505, 234, 607), ["375", "cities"], 30, al=C_, color=W, fill=F, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=.16)
    _p(s, m, (494, 507, 677, 609), ["58%", "coverage"], 28, al=C_, color=W, fill=F, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=.16)
    for sp_ in list(s.shapes)[-2:]:
        for pg in sp_.text_frame.paragraphs:
            for r in pg.runs: r.font.bold = True


def wedge_state_blocks(s, x, y, w, h):
    """Mapa por estado, cunha cinza com a sigla grande e barras por bloco com chave. Sabesp p.7."""
    m = M((0, 0, 900, 282), (x, y, w, h))
    R(s, m, 568, 14, 900, 278, "F2F2F2")
    poly(s, m, ((342, 197), (568, 14), (568, 278), (340, 214)), "E8E8E8")
    a, b, c, d_ = light(F, .45), light(F, .15), F, D
    cl = {k: a for k in states("BRA")}
    cl.update({"TO": a, "PI": b, "PE": b, "SE": b, "PR": b, "RJ": b, "AL": b, "RN": b, "MA": b, "CE": b, "PB": b, "MG": d_, "MT": c, "BA": mix(F, D, .5), "RS": c, "ES": a, "SP": light(F, .72), "DF": W})
    gmap(s, m, (128, 15, 390, 270), states("BRA"), cl, W, .4)
    for yy in (22, 115, 212):
        R(s, m, 0, yy, 3, yy + 60 if yy != 212 else 282, A)
    _path(s, m, [(5, 60), (138, 60)], A, 1.1, dash=DASH)
    R(s, m, 137, 46, 140, 74, A)
    sp = R(s, m, 136, 164, 145, 255, F); grad(sp, ((0, d_), (1, a)), 90)
    _t(s, m, (150, 155, 180, 172), "22", 10, color=G4, al=L)
    _t(s, m, (150, 247, 180, 264), "1", 10, color=G4, al=L)
    _t(s, m, (440, 130, 530, 182), "SP", 36, bold=True)
    ss.line(s, *m.p((655, 30)), *m.p((655, 273)), INK, 1.2, dash=False)
    for yy, t, ln, val, fill in ((60, "Block A", 188, "375", D), (121, "Block D", 71, "141", F), (181, "Block B", 47, "94", F), (242, "Block C", 17, "35", F)):
        R(s, m, 656, yy - 11, 656 + ln, yy + 11, fill)
        _t(s, m, (575, yy - 13, 645, yy + 13), t, 14, al=RT)
        _chip(s, m, (656 + ln + 5, yy - 13, 656 + ln + 48, yy + 13), val, 14)
    _path(s, m, [(782, 101), (795, 103), (797, 175), (805, 182), (797, 189), (795, 260), (782, 262)], F, 1.2)
    _t(s, m, (795, 160, 865, 204), "Unified", 13, color=F, bold=True, rot=90)


# ---------- América Latina ----------

_LB = (-118.4, -34.6, -56, 32.8)


def screening_cards(s, x, y, w, h):
    """Cartões de triagem com bandeira e lupa em fios finos, sobre o oceano; filtros no alto. Nubank p.44."""
    m = M((0, 0, 900, 327), (x, y, w, h))
    hot = ("PER", "BOL", "PRY", "ARG")
    gmap(s, m, (90, 10, 456, 327), _latam(), lambda k: F if k in hot else G3, W, .35, bounds=_LB, clip=(0, 0, 900, 327), minpx=1.5)
    for a, b in (((212, 157), (262, 157)), ((212, 237), (300, 200)), ((455, 230), (372, 230))):
        ss.line(s, *m.p(a), *m.p(b), G3, .6, dash=False)
    def card(b, nm, lines, fx):
        rr(s, *m.box(*b), G1, .14)
        x0, y0 = b[0], b[1]
        _flag(s, m, x0 + fx, y0 + 15, 21, F, W)
        _t(s, m, (x0 + fx + 15, y0 + 3, b[2] - 40, y0 + 27), nm, 12.5, al=L)
        _magnifier(s, m, b[2] - 22, y0 + 17, 22)
        for i, ln in enumerate(lines):
            _p(s, m, (x0 + 8, y0 + 34 + i * (b[3] - y0 - 40) / len(lines), b[2] - 4, y0 + 34 + (i + 1) * (b[3] - y0 - 40) / len(lines)),
               [[(t, {"bold": bo, "color": F if bo else INK}) for t, bo in ln]], 11.5)
    card((2, 118, 212, 206), "Market A profile", ([("Strong, ", 0), ("efficient rivals", 1)], [("Restricted ", 0), ("lending limits", 1)]), 18)
    card((2, 233, 212, 323), "Market B profile", ([("Weak ", 0), ("data rails", 1)], [("Market too ", 0), ("small", 1)]), 20)
    card((455, 170, 695, 291), "Market C profile", ([("Macro", 1), (" instability", 0)], [("Wallet", 1), (" dominance", 0)], [("Policy ", 0), ("volatility", 1)]), 25)
    _p(s, m, (540, 0, 898, 25), [[("Three filters guide the ", {}), ("screening", {"bold": True, "color": F})]], 14.5, al=C_)
    for yy, t in ((29, "Large underserved segments"), (71, "Concentrated incumbents"), (113, "High digital adoption")):
        _chip(s, m, (585, yy, 847, yy + 28), t, 11.5, fill=F, adj=.15)


def latam_summary_card(s, x, y, w, h):
    """Mapa na base de um cartão-resumo com aba e dobras; ativos em cor, demais em cinza. Nubank p.2."""
    m = M((0, 0, 617, 900), (x, y, w, h))
    pale = light(F, .88)
    poly(s, m, _rpoly(68, 60, 535, 887, 0, 0, 80, 80), pale)
    poly(s, m, ((13, 78), (68, 78), (68, 124)), dark(F, .3))
    poly(s, m, ((598, 78), (535, 78), (535, 124)), dark(F, .3))
    R(s, m, 3, 4, 614, 78, F)
    _t(s, m, (3, 4, 614, 78), "Company", 42, color=W, bold=True)
    _t(s, m, (68, 98, 535, 148), "Summary", 37)
    _p(s, m, (92, 168, 525, 410), [[("Founded in the last", {})], [("decade, the company", {})], [("disrupted the sector with a", {})], [("fully digital, fee-free", {"bold": True})], [("product. Today it serves", {})], [("over ", {}), ("ten million clients", {"bold": True})], [("in three countries.", {})]], 25, anchor=TOP)
    hot = ("MEX", "COL", "BRA")
    gmap(s, m, (140, 435, 486, 860), _latam(), lambda k: F if k in hot else G3, W, .35, bounds=_LB, minpx=2)


def ring_percent_circles(s, x, y, w, h):
    """Círculos brancos de anel escuro com o percentual na costa de cada país; placa cinza atrás do cone sul. Mercado Libre p.2."""
    m = M((0, 0, 900, 804), (x, y, w, h))
    poly(s, m, _rpoly(10, 415, 560, 662), G1)
    poly(s, m, _rpoly(5, 415, 16, 662, 4, 0, 0, 4), D)
    poly(s, m, ((16, 475), (29, 487), (16, 499)), D)
    _p(s, m, (82, 460, 480, 620), ["Revenue comes mainly", "from the largest", "economies in the", "region"], 33, anchor=MID)
    pale = light(F, .78)
    def col(k):
        if k == "BRA": return D
        if k in ("MEX", "ARG"): return mix(F, G4, .55)
        if k in ("CUB", "HTI", "DOM", "JAM", "BHS", "PRI", "GUY", "SUR", "TTO"): return "E4E4E4"
        return pale
    gmap(s, m, (142, 5, 887, 800), _latam(), col, bounds=_LB, minpx=4)
    for cx, cy, t in ((305, 58, "20%"), (829, 396, "52%"), (616, 677, "22%")):
        _o(s, m, cx, cy, 102, W, border=INK, width=.75)
        _t(s, m, (cx - 50, cy - 26, cx + 50, cy + 26), t, 33, bold=True)


def diamond_plates(s, x, y, w, h):
    """Losango na costa e placa escura sobre a terra, com frase simples no branco. BTG Pactual p.120."""
    m = M((0, 0, 900, 784), (x, y, w, h))
    mid, pale = light(F, .5), light(F, .85)
    def col(k):
        return {"BRA": F, "COL": mid, "CHL": mid, "PER": pale, "ARG": pale}.get(k, "E2E2E2")
    gmap(s, m, (15, 15, 498, 780), _sub(*_SA), col, W, .5, bounds=(-81.5, -34.6, -56, 12.6), minpx=3)
    plate = "595959"
    R(s, m, 253, 45, 715, 170, plate)
    _t(s, m, (262, 50, 712, 98), "Market A, since entry", 31, color=W, al=L)
    _p(s, m, (280, 98, 712, 165), ["Local broker", "purchase"], 26, color=light(F, .65))
    R(s, m, 243, 528, 704, 654, plate)
    _t(s, m, (252, 533, 700, 583), "Market B, since entry", 31, color=W, al=L)
    _t(s, m, (268, 592, 700, 640), "Regional broker purchase", 26, color=light(F, .65), al=L)
    ss.line(s, *m.p((153, 110)), *m.p((253, 110)), D, 1.0, dash=False)
    ss.line(s, *m.p((142, 594)), *m.p((243, 594)), D, 1.0, dash=False)
    for cx, cy in ((153, 110), (142, 594)):
        poly(s, m, ((cx, cy - 24), (cx + 24, cy), (cx, cy + 24), (cx - 24, cy)), D)
    _p(s, m, (517, 190, 880, 268), ["Might get a banking", "licence within a year"], 28)
    _p(s, m, (296, 670, 880, 748), ["Holds every licence to run as a", "complete investment bank"], 28)


def _brush(s, m, a, c, b, w0=2.5, w1=9.0, col=INK):
    """Seta de pincel: curva de espessura variável com ponta aberta, de a até b, controle c."""
    n = 18
    pts = [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]) for t in (i / n for i in range(n + 1))]
    L_, R_ = [], []
    for i, p in enumerate(pts):
        q0, q1 = pts[max(i - 1, 0)], pts[min(i + 1, n)]
        dx, dy = q1[0] - q0[0], q1[1] - q0[1]; ln = math.hypot(dx, dy) or 1
        t = i / n; wd = (w0 + (w1 - w0) * math.sin(t * math.pi) ** .8 * .9 + 1.0 * t) / 2
        L_.append((p[0] - dy / ln * wd, p[1] + dx / ln * wd)); R_.append((p[0] + dy / ln * wd, p[1] - dx / ln * wd))
    poly(s, m, L_ + R_[::-1], col)
    tx_, ty_ = pts[-1][0] - pts[-3][0], pts[-1][1] - pts[-3][1]; ln = math.hypot(tx_, ty_) or 1
    tx_, ty_ = tx_ / ln, ty_ / ln
    hl = 24
    for sgn in (1, -1):
        ca, sa = math.cos(math.radians(150 * sgn)), math.sin(math.radians(150 * sgn))
        e = (b[0] + hl * (tx_ * ca - ty_ * sa), b[1] + hl * (tx_ * sa + ty_ * ca))
        _path(s, m, [b, e], col, 4.0 * m.sx * 72 * .75, cap="rnd")


def flow_arrows_country(s, x, y, w, h):
    """País destacado com setas de pincel saindo dele, ícone e chamada tracejada com divisas. AB InBev p.35."""
    m = M((0, 0, 900, 892), (x, y, w, h))
    gmap(s, m, (140, 15, 870, 892), _latam(), lambda k: A if k == "BRA" else G2, W, .6, bounds=(-117.3, -34.8, -53.4, 32.7), minpx=4)
    _t(s, m, (290, 40, 760, 74), "Expanding to ten countries in the region", 21, color=G4, italic=True)
    for a, c, b in (((682, 391), (605, 395), (564, 320)), ((672, 464), (605, 490), (538, 440)), ((695, 513), (690, 580), (616, 590)), ((706, 604), (695, 660), (625, 682))):
        _brush(s, m, a, c, b)
    _o(s, m, 735, 475, 74, light(A, .25), border=dark(A, .12), width=.5)
    _t(s, m, (700, 455, 770, 495), "[logo]", 15, color=INK)
    _path(s, m, [(440, 405), (232, 405), (232, 546)], G3, .75, dash=DASH)
    ss.line(s, *m.p((208, 547)), *m.p((255, 547)), G3, .75, dash=False)
    R(s, m, 32, 566, 430, 755, W, G3, dash=True, width=.75)
    for yy, t in ((613, "Increase reach and data depth"), (710, "Become top of mind elsewhere")):
        _chev(s, m, 52, yy - 19, 18, 38, INK)
        _t(s, m, (79, yy - 18, 425, yy + 18), t, 20, al=L)


# ---------- Mundo ----------

def gold_halo_bubbles(s, x, y, w, h, n=2):
    """Mundo cinza plano com bolhas escuras de halo de luz e o % dentro; duas seções empilhadas. Kering - Moncler p.15."""
    m = M((0, 0, 900, 829), (x, y, w, h))
    R(s, m, 0, 0, 900, 829, "F7F7F7")
    world = _world()
    data = (("BRAND A REVENUE BY GEOGRAPHY", "Asia is the largest region", 0, ((197, 227, 68, "14%", "AMERICAS", 197, 287), (474, 200, 88, "34%", "EMEA", 469, 266), (610, 163, 112, "52%", "ASIA", 614, 252))),
            ("BRAND B REVENUE BY GEOGRAPHY", "EMEA exposure diversifies the group", 423, ((204, 660, 68, "6%", "AMERICAS", 207, 722), (481, 634, 112, "66%", "EMEA", 485, 720), (620, 583, 80, "28%", "ASIA", 620, 656))))
    for title, sub_, oy, bub in data[:n]:
        _t(s, m, (0, oy - 5, 880, oy + 25), title, 22, bold=True, al=L)
        _t(s, m, (0, oy + 26, 880, oy + 50), sub_, 17, al=L)
        R(s, m, 0, oy + 58, 898, oy + 64, G4)
        gmap(s, m, (70, oy + 78, 815, oy + 392), world, G3, bounds=(-170, 180, -56, 83), merge=True, minpx=3)
        for cx, cy, d_, t, lab, lx, ly in bub:
            sp = _o(s, m, cx, cy, d_, "595959", border=A, width=max(.5, 2.2 * m.sx * 72))
            glow(sp, 19 * m.sx * 72, A, .42)
            _t(s, m, (cx - d_ / 2, cy - 14, cx + d_ / 2, cy + 14), t, 16 + d_ * .06, color=W, bold=True)
            _t(s, m, (lx - 60, ly - 10, lx + 60, ly + 10), lab, 15, bold=True)


_ACTIVE = ("GRL", "NOR", "FRA", "POL", "SRB", "ROU", "TUR", "IRQ", "IRN", "AFG", "PAK", "CHN", "JPN", "KOR", "PRK", "MMR", "THA", "LAO", "NPL", "BGD", "LKA", "TWN", "OMN", "YEM", "SOM", "ETH", "KEN", "TZA", "UGA", "SDN", "SSD", "EGY", "LBY", "TUN", "DZA", "MAR",
           "MRT", "MLI", "NER", "TCD", "SEN", "GIN", "CIV", "BFA", "GHA", "CMR", "COD", "COG", "CAF", "GAB", "AGO", "ZMB", "ZWE", "MOZ", "BWA", "NAM", "MDG", "MWI", "SYR", "JOR", "PNG", "CUB", "DOM", "HTI", "GTM", "HND", "NIC", "VEN", "GUY", "SUR", "ECU", "BOL", "PRY", "URY", "LSO", "GEO", "ARM", "AZE", "TKM", "UZB", "TJK", "KGZ", "EST", "BIH", "BGR")


def world_brand_stack(s, x, y, w, h):
    """Mundo com países ativos em cor e o resto só em contorno; números empilhados e molde de logo. Meliuz p.88."""
    m = M((0, 0, 900, 426), (x, y, w, h))
    world = _world()
    bd = (-170, 180, -56, 83.6)
    box = (-2, 3, 900, 432)
    act = set(_ACTIVE) | {k for k, v in world.items() if v["continent"] == "Africa" and k not in ("NGA", "ZAF")}
    gmap(s, m, box, world, lambda k: W if k not in act else None, G4, .3, bounds=bd, clip=(0, 0, 900, 426), merge=False, minpx=6)
    gmap(s, m, box, world, lambda k: A if k in act else None, G4, .3, bounds=bd, clip=(0, 0, 900, 426), minpx=3)
    for yy, n_, t, xs in ((280, "44", "countries", 14), (334, "19", "languages", 14), (386, "9", "priorities", 22)):
        _p(s, m, (xs, yy - 22, 200, yy + 22), [[(n_, {"px": 32}), (" " + t, {"px": 15})]], 15)
    _mold(s, m, (598, 358, 745, 412), "[logo]", 15, round_=.15)


# ---------- Corredores e recortes ----------

_CUT = ("PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MG", "ES", "RJ", "SP", "PR")


def corridor_cutout(s, x, y, w, h):
    """Só os estados do corredor, ampliados, num único degradê diagonal, com trilho tracejado branco. CSN - ArcelorMittal p.30."""
    m = M((0, 0, 900, 606), (x, y, w, h))
    shapes = {k: states("BRA")[k] for k in _CUT}
    to, sh = gmap(s, m, (95, 8, 582, 582), shapes, lambda k: F, W, 1.25, merge=True)
    for sp in sh.values():
        grad(sp, ((0, dark(F, .78)), (.32, dark(F, .55)), (.72, F), (.88, dark(F, .2)), (1, dark(F, .72))), 110)
    rail = _smooth([(240, 490), (262, 512), (300, 500), (345, 490), (388, 488), (400, 465), (402, 420), (395, 388), (368, 372), (352, 372), (360, 385), (345, 405), (330, 450), (312, 490), (262, 512)], 6)
    _path(s, m, rail, W, 1.25, dash=DASH)
    for cx, cy in ((481, 40), (568, 95), (476, 233), (316, 386), (349, 402), (149, 425), (216, 464), (226, 473), (318, 460), (248, 505), (356, 490), (385, 490), (158, 529)):
        grad(_o(s, m, cx, cy, 25, F, border=light(F, .1), width=max(.6, 2.5 * m.sx * 72)), ((0, dark(F, .75)), (1, F)), 0)
    grad(_o(s, m, 26, 32, 13, F, border=light(F, .1), width=max(.5, 2 * m.sx * 72)), ((0, dark(F, .75)), (1, F)), 0)
    _t(s, m, (42, 18, 300, 46), "Group assets", 16, bold=True, al=L)
    ss.line(s, *m.p((28, 76)), *m.p((28, 87)), INK, 1.5, dash=False); ss.line(s, *m.p((28, 95)), *m.p((28, 106)), INK, 1.5, dash=False)
    _t(s, m, (42, 76, 300, 106), "Rail concession", 16, bold=True, al=L)
    _t(s, m, (568, 328, 890, 356), "Pro forma output: 16.6 Mt", 16, color=dark(F, .55), bold=True, al=L)
    _t(s, m, (568, 366, 890, 396), "Rail network: 1,643 km", 16, color=dark(F, .55), bold=True, al=L)


def corridor_zoom_rail(s, x, y, w, h):
    """Estados do sudeste em degradê, trilho grosso em cor viva, hastes tracejadas e blocos de texto. CSN Liability p.27."""
    m = M((0, 0, 712, 900), (x, y, w, h))
    b = states("BRA")
    # escala fixa pelo original: Minas tem a largura e a altura medidas no recorte
    bd = (-53.4, -40.07, -25.39, -12.0)
    box = (0, 0, 480, 730)
    clip = (10, 25, 520, 790)
    gmap(s, m, box, {k: b[k] for k in ("GO", "MS", "MT", "DF", "PR", "SC", "BA")}, lambda k: None if k == "BA" else G2, W, .5, bounds=bd, clip=clip, merge=True)
    for keys in (("MG", "ES", "RJ"), ("SP",)):
        _, sh = gmap(s, m, box, {k: b[k] for k in keys}, F, W, .75, bounds=bd, clip=clip, merge=True)
        for sp in sh.values():
            grad(sp, ((0, dark(D, .1)), (.55, mix(D, F, .6)), (1, F)), 90)
    wd = max(2.2, 8 * m.sx * 72)
    for r in (_smooth([(326, 332), (333, 373), (318, 376), (295, 390), (280, 430), (283, 480), (302, 570), (306, 580)], 8),
              _smooth([(333, 373), (345, 385), (352, 420), (362, 480), (368, 520), (360, 548), (320, 568), (285, 588), (240, 618), (195, 628), (160, 600), (126, 573)], 8),
              _smooth([(195, 628), (205, 650), (210, 668)], 6)):
        _path(s, m, r, A, wd, cap="rnd")
    stem = G4
    for pts in ([(347, 390), (347, 30), (690, 30)], [(330, 586), (330, 733), (690, 733)], [(164, 608), (164, 883), (640, 883)]):
        _path(s, m, pts, stem, .9, dash=DASH)
    for cx, cy in ((347, 390), (330, 586), (164, 608)):
        poly(s, m, ((cx, cy - 7), (cx + 7, cy), (cx, cy + 7), (cx - 7, cy)), stem)
    olive = dark(A, .4)
    def block(x0, y0, t, a, b_):
        _t(s, m, (x0, y0, 700, y0 + 40), t, 26, color=olive, al=L)
        _p(s, m, (x0, y0 + 42, 700, y0 + 72), [[("Profile: ", {}), (a, {"color": olive})]], 18)
        _p(s, m, (x0, y0 + 77, 700, y0 + 107), [[("Impact: ", {}), (b_, {"color": olive})]], 18)
    block(358, 30, "Northern Corridor", "Ore flow", "~45 Mt of flow")
    block(343, 618, "Port Link", "Industrial flows", "Port and mill")
    block(182, 768, "Southeast Grid", "Steel and cement", "~3-7 Mt a year")


_OPS = ("MT", "MS", "GO", "MG", "SP", "PR", "SC", "RS", "RJ", "ES", "BA", "PI", "CE", "RN", "PB", "PE", "AL", "SE")


def states_only_elbow(s, x, y, w, h):
    """Só os estados de operação, com pontos de anel branco e rótulos em cotovelo no branco deixado pelos demais. CSN - ArcelorMittal p.6."""
    m = M((0, 0, 900, 563), (x, y, w, h))
    b = states("BRA")
    gmap(s, m, (20, 18, 455, 490), {k: b[k] for k in _OPS}, D, W, 1.1)
    for cx, cy, c, al_ in ((167, 178, F, 1), (323, 128, F, 1), (384, 88, D, .6), (413, 125, light(F, .4), 1), (428, 125, light(F, .4), 1), (378, 186, light(F, .4), 1), (247, 215, light(F, .4), 1), (290, 236, light(F, .4), 1),
                           (295, 266, light(F, .4), 1), (254, 271, light(F, .4), 1), (247, 295, F, 1), (291, 295, D, 1), (286, 304, light(F, .4), 1), (326, 300, D, 1), (237, 324, D, 1), (288, 326, F, 1), (307, 327, dark(D, .2), 1), (323, 314, D, 1), (193, 339, light(F, .4), 1), (195, 395, F, 1)):
        _o(s, m, cx, cy, 20, c, border=W, width=max(.75, 2 * m.sx * 72))
    for pts in ([(440, 145), (440, 248), (660, 248)], [(320, 330), (320, 388), (838, 388)], [(252, 330), (252, 550), (498, 550)]):
        _path(s, m, pts, G3, .75, dash=DOT)
    for x0, y0, a, b_, c_ in ((450, 170, "Plant Alpha", "Installed capacity: 1.4 Mt/year", "Cement EBITDA margin: 26.3%"), (605, 310, "Plant Beta", "Installed capacity: 5.5 Mt/year", "Steel EBITDA margin: 10.0%"), (262, 470, "Plant Gamma", "Installed capacity: 42.0 Mt/year", "Mining EBITDA margin: 41.0%")):
        _t(s, m, (x0, y0, 890, y0 + 30), a, 23, color=mix(F, D, .4), bold=True, italic=True, al=L)
        _t(s, m, (x0, y0 + 32, 890, y0 + 52), b_, 15, al=L)
        _t(s, m, (x0, y0 + 52, 890, y0 + 72), c_, 15, al=L)


_EU = ("PRT", "ESP", "FRA", "BEL", "NLD", "LUX", "DEU", "CHE", "AUT", "ITA", "POL", "CZE", "SVK", "HUN", "SVN", "HRV", "BIH", "SRB", "MNE", "ALB", "MKD", "GRC", "BGR", "ROU", "MDA", "UKR", "BLR", "LTU", "LVA", "EST", "XKX", "KOS")


def band_highlight_country(s, x, y, w, h):
    """Faixa em degradê desde a borda esquerda e continente escuro, com dois países em destaque. CSN Liability p.11."""
    m = M((0, 0, 900, 568), (x, y, w, h))
    sp = R(s, m, 0, 11, 888, 558, T)
    grad(sp, ((0, light(T, .55)), (.7, W), (1, W)), 0)
    R(s, m, 0, 9, 660, 12, F); R(s, m, 0, 556, 888, 559, F)
    shp = {}
    for k, v in _sub(*_EU).items():
        rings = []
        for r in v["rings"]:
            la = sum(p[1] for p in r) / len(r); lo = sum(p[0] for p in r) / len(r)
            if lo < -20 or lo > 42 or la < 27 or (lo < -12 and la > 30): continue
            r2 = [(a + 6.5, b + 7.6) for a, b in r] if la < 30 else r
            # meridianos convergentes, como numa cônica: o oeste do continente abre e o centro não muda
            rings.append([(15 + (a - 15) * math.cos(math.radians(b)) / .629, b) for a, b in r2])
        shp[k] = {"rings": rings}
    bd, box = (-31.3, 42.5, 32.5, 59.95), (0, 0, 900, 555)
    cl = (0, 0, 900, 555)
    rest = {k: v for k, v in shp.items() if k not in ("DEU", "PRT")}
    _, sh = gmap(s, m, box, rest, D, light(D, .12), .3, bounds=bd, clip=cl, merge=True, minpx=4)
    for q in sh.values(): grad(q, ((0, mix(D, F, .3)), (1, D)), 0)
    for keys, a_, b_ in ((("DEU",), light(F, .25), mix(F, D, .1)), (("PRT",), light(F, .15), F)):
        _, sh = gmap(s, m, box, {k: shp[k] for k in keys}, F, light(D, .2), .3, bounds=bd, clip=cl, merge=True, minpx=4)
        for q in sh.values(): grad(q, ((0, a_), (1, b_)), 60)
    _t(s, m, (240, 104, 490, 130), "Plant Alpha (Country A)", 15.5, al=C_)
    ss.line(s, *m.p((233, 132)), *m.p((495, 132)), F, 1.2, dash=False)
    _p(s, m, (250, 138, 480, 180), [[("1.1 Mt/year steel", {"bold": True, "color": F})], [("capacity", {"bold": True, "color": F})]], 15.5, al=C_)
    _t(s, m, (22, 368, 202, 394), "Plant Beta (Country B)", 13, al=C_)
    ss.line(s, *m.p((30, 396)), *m.p((212, 396)), F, 1.2, dash=False)
    _p(s, m, (22, 402, 202, 446), [[("0.5 Mt/year steel", {"bold": True, "color": F})], [("capacity", {"bold": True, "color": F})]], 14.5, al=C_)


def framed_tile_asset_dots(s, x, y, w, h):
    """Mapa em ladrilho com borda escura à esquerda e embaixo, pontos por tipo e cadeia de três caixas. CSN Liability p.16."""
    m = M((0, 0, 900, 759), (x, y, w, h))
    sp = R(s, m, 6, 2, 896, 570, T)
    grad(sp, ((0, light(T, .5)), (.45, light(T, .55)), (1, light(T, .92))), 0)
    clip = (7, 3, 895, 568)
    bd = (-60.2, -34.8, -28.8, 1.6)
    box = (-3, 3, 456, 569)
    active = ("CE", "PB", "PE", "AL", "SE", "BA", "MG", "ES", "RJ", "SP", "GO", "DF")
    gmap(s, m, box, _sub("VEN", "COL", "GUY", "SUR", "BOL", "PER", "PRY", "ARG", "URY"), W, G3, .5, bounds=bd, clip=clip, minpx=4)
    gmap(s, m, box, states("BRA"), lambda k: G2 if k in active else "F1F1F1", W, .9, bounds=bd, clip=clip)
    for cx, cy, c in ((359, 94, F), (188, 337, F), (249, 327, F), (311, 450, F), (293, 454, F), (293, 464, F), (440, 185, dark(D, .1)), (218, 394, dark(D, .1)), (226, 387, light(F, .55))):
        _o(s, m, cx, cy, 10, c)
    R(s, m, 6, 2, 8, 570, D); R(s, m, 6, 568, 236, 570, D)
    R(s, m, 658, 16, 882, 134, W, INK, width=.5)
    for yy, c, t in ((40, F, "Grinding"), (75, dark(D, .1), "Integrated assets"), (110, light(F, .55), "Clinker")):
        _o(s, m, 675, yy, 9, c)
        _t(s, m, (691, yy - 12, 878, yy + 12), t, 15, color=light(F, .55) if c == light(F, .55) else F if c == F else D, al=L)
    def panel(b, head, lines):
        sq = R(s, m, *b, T); grad(sq, ((0, light(T, .35)), (1, light(T, .8))), 0)
        _t(s, m, (b[0] + 20, b[1] + 8, b[2] - 5, b[1] + 48), head, 18, color=D, al=L)
        step = (b[3] - b[1] - 58) / len(lines)
        for i, t in enumerate(lines):
            yy = b[1] + 54 + i * step
            _o(s, m, b[0] + 22, yy + step / 2, 4, D)
            _t(s, m, (b[0] + 46, yy, b[2] - 5, yy + step), t, 15, color=D, al=L)
    panel((540, 155, 886, 320), "The group has 20 assets:", ("8 mining units", "7 integrated assets", "5 grinding units"))
    panel((540, 345, 886, 548), "What did each deal add?", ("First: grinding-only assets", "Second: integrated capacity", "Third: eight northeast assets"))
    for b in ((287, 663, 345, 725), (593, 663, 641, 725)):
        R(s, m, *b, light(T, .4))
    for x0, t, a, b_, c_ in ((15, "Raw Materials", "Limestone, clay and", "correctives are extracted", "as key inputs"), (345, "Clinker Production", "Raw meal fired in kilns", "to make clinker, the", "key intermediate"), (641, "Cement Grinding", "Clinker ground with", "gypsum and slag into", "finished cement")):
        bx = R(s, m, x0, 638, x0 + (272 if x0 == 15 else 248), 748, W); shadow(bx, 3, 1.5, 45, "000000", .25)
        R(s, m, x0, 637, x0 + (272 if x0 == 15 else 248), 639, D); R(s, m, x0, 637, x0 + 2, 748, D)
        wd = 272 if x0 == 15 else 248
        _t(s, m, (x0, 652, x0 + wd, 680), t, 16.5, color=INK, al=C_)
        _p(s, m, (x0 + 4, 682, x0 + wd - 4, 740), [a, b_, c_], 14.5, al=C_)


# ---------- Pontos ----------

def two_owner_dots_tile(s, x, y, w, h):
    """Mapa pálido em ladrilho com tabela, pontos de dois donos e etiquetas na divisa entre mapa e tabela. Vibra p.17."""
    m = M((0, 0, 900, 496), (x, y, w, h))
    sp = R(s, m, 0, 0, 900, 490, T)
    grad(sp, ((0, light(T, .55)), (1, light(T, .85))), 0)
    ss.line(s, *m.p((0, 491)), *m.p((900, 491)), INK, .5, dash=False)
    bd = (-59.8, -34.6, -29.3, 2.9)
    box = (0, 0, 417, 487)
    clip = (0, 0, 417, 487)
    keep = ("MT", "GO", "MG", "BA", "SP", "PE", "RJ", "PB", "AL", "ES", "SE", "RN")
    gmap(s, m, box, _sub("BOL", "PRY", "ARG", "URY"), "E9E9E9", W, .6, bounds=bd, clip=clip)
    gmap(s, m, box, states("BRA"), lambda k: G2 if k in keep else "E9E9E9", W, .6, bounds=bd, clip=clip)
    for cx, cy in ((380, 138), (322, 182), (381, 182), (283, 261), (209, 355), (257, 355), (121, 404), (178, 396)):
        _o(s, m, cx, cy, 10, F)
    for cx, cy in ((365, 156), (307, 207), (52, 249), (290, 282), (250, 313), (300, 392)):
        _o(s, m, cx, cy, 10, dark(D, .35))
    q = R(s, m, 17, 14, 299, 84, G1, INK, width=.6); ss.set_alpha(q, 70)
    _o(s, m, 37, 34, 9, F); _o(s, m, 37, 64, 9, dark(D, .35))
    _t(s, m, (58, 22, 295, 46), "Group A generation plant", 15.5, color=F, al=L)
    _t(s, m, (58, 52, 295, 76), "Group B generation plant", 15.5, color=dark(D, .35), al=L)
    ccol = (645, 765, 862)
    for cx, t in zip(ccol, ("Hydro", "Wind", "Solar")):
        _t(s, m, (cx - 37, 10, cx + 37, 34), t, 17, bold=True)
    ss.line(s, *m.p((467, 46)), *m.p((898, 46)), INK, .8, dash=False)
    rows = ((82, "Group A", "-", "280", "1,542", 0), (149, "% of total", "0%", "15%", "85%", 1), (215, "Group B", "402", "1,085", "400", 0), (282, "% of total", "21%", "60%", "22%", 1), (347, "NewCo", "402", "1,365", "1,942", 0), (413, "% of total", "10.8%", "36.8%", "52.4%", 1))
    pale = light(T, .35)
    for x0, x1, y0, y1 in ((472, 898, 66, 306), (472, 898, 331, 433)):
        R(s, m, x0, y0, x1, y1, pale)
    for x0, y0, y1 in ((468, 68, 306), (468, 330, 433)):
        _path(s, m, [(x0 + 16, y0), (x0, y0), (x0, y1), (x0 + 16, y1)], G3, 1.2)
    for yy, a, b_, c, d_, bo in rows:
        _t(s, m, (472, yy - 16, 578, yy + 16), a, 16, bold=bool(bo))
        for cx, t in zip(ccol, (b_, c, d_)):
            _t(s, m, (cx - 37, yy - 16, cx + 37, yy + 16), t, 16, bold=bool(bo))
    _t(s, m, (365, 254, 455, 278), "Pre-deal", 15, color=G4, bold=True)
    _t(s, m, (360, 376, 460, 400), "Pro forma", 15, color=G4, bold=True)


def dot_density_no_outline(s, x, y, w, h):
    """Rede densa: o contorno do país nasce dos pontos; legenda embaixo e cartões sobre o leste vazio. Vibra p.23."""
    m = M((0, 0, 900, 396), (x, y, w, h))
    sp = R(s, m, 0, 10, 340, 386, G1); grad(sp, ((0, "F5F5F5"), (1, W)), 0)
    ss.line(s, *m.p((0, 9)), *m.p((900, 9)), INK, 1.0, dash=False)
    b = states("BRA")
    bd = _bounds_br()
    box = (10, 10, 334, 372)
    lo0, lo1, la0, la1 = bd
    px = lambda p: m.p((box[0] + (p[0] - lo0) / (lo1 - lo0) * (box[2] - box[0]), box[1] + (la1 - p[1]) / (la1 - la0) * (box[3] - box[1])))
    wts = {"SP": 4, "MG": 3, "RJ": 2.5, "PR": 2.5, "SC": 2.5, "RS": 2.5, "BA": 1.5, "PE": 2.5, "CE": 2, "GO": 1.5, "AM": .1, "PA": .35, "RR": .2, "AP": .2, "AC": .2, "MT": .5, "TO": .4, "RO": .5}
    wide = [(a, b_, c * 1.5, d_) for a, b_, c, d_ in _BR_HUBS]
    wts.update({"AM": .25, "PA": .5, "RR": .3, "AP": .3, "AC": .3, "MT": .9, "TO": .7, "RO": .8, "MS": 1, "MA": 1, "PI": 1, "BA": 2})
    pale = _sample(b, 320, wide, wts, seed=4, hub_share=.4, keyname="br_pale")
    dk = _sample(b, 1300, wide, wts, seed=3, hub_share=.5, keyname="br_dark")
    _dots(s, m, [px(p) for p in pale], 3.2, light(F, .55))
    _dots(s, m, [px(p) for p in dk[:1150]], 2.8, dark(F, .25))
    _dots(s, m, [px(p) for p in dk[1150:]], 4.6, dark(F, .25))
    q = R(s, m, 41, 315, 259, 385, G2, INK, width=.6)
    _o(s, m, 55, 335, 6, dark(F, .25)); _o(s, m, 55, 367, 6, light(F, .62))
    _t(s, m, (72, 322, 255, 348), "Group A stations", 16, color=dark(F, .25), al=L)
    _t(s, m, (72, 355, 255, 380), "Group B stations", 16, color=G4, al=L)
    R(s, m, 320, 41, 889, 146, light(T, .55), F, width=.75)
    _p(s, m, (338, 52, 880, 136), ["Unlocking nationwide expansion by pivoting from the", "old footprint to a network of +7,600 points of sale"], 17, color=dark(F, .25), spacing=1.5)
    R(s, m, 320, 177, 889, 326, G1, F, width=.75)
    for yy, a, b_, c, col, bo in ((211, "Volume through old channel", "[000 m3]", "5.4", G4, False), (254, "Addressable stations", "[#]", "1,500", G4, False), (297, "Volume per station per year", "[000 m3]", "0.0036", dark(F, .25), False)):
        _t(s, m, (337, yy - 14, 640, yy + 14), a, 16, color=col, al=L)
        _t(s, m, (625, yy - 14, 705, yy + 14), b_, 15, color=col)
        _t(s, m, (770, yy - 14, 850, yy + 14), c, 15, color=col)
    for cx, t in ((431, "[Unit]"), (535, "2026"), (640, "2027"), (745, "2028"), (849, "2029")):
        _t(s, m, (cx - 45, 368, cx + 45, 391), t, 15.5, bold=True)
    ss.line(s, *m.p((40, 394)), *m.p((888, 394)), INK, 1.0, dash=False)


def map_breaks_card_strips(s, x, y, w, h):
    """Mapa cinza que vaza do cartão e cruza o fio do rodapé, com marcadores e faixas de KPI. Vibra p.27."""
    m = M((0, 0, 900, 611), (x, y, w, h))
    R(s, m, 193, 0, 899, 517, light(T, .82), F, width=1.5)
    R(s, m, 0, 0, 9, 70, dark(F, .3))
    R(s, m, 0, 604, 645, 609, F)
    _mold(s, m, (665, 572, 868, 610), "[logo]", 15)
    lg, dg = mix(A, F, .3), dark(F, .3)
    R(s, m, 210, 402, 867, 500, light(T, .75), INK, width=.5)
    for yy in (75, 166, 257):
        q = R(s, m, 380, yy, 867, yy + 83, F)
        grad(q, ((0, light(F, .82)), (.4, light(F, .8)), (1, light(F, .92))), 0)
        q.line.color.rgb = ss.rgb(G2); q.line.width = Pt(.75)
    bd = (-74.0, -34.8, -53.3, 5.3)
    box = (0, 0, 505, 650)
    clip = (0, 0, 900, 603)
    gmap(s, m, box, _sub("BOL", "PRY", "URY", "ARG", "CHL", "PER"), lambda k: None if k in ("PER", "CHL") else G3, W, .75, bounds=bd, clip=clip)
    gmap(s, m, box, _sub("BRA"), G3, None, bounds=bd, clip=clip)
    for cx, cy in ((171, 88), (320, 71), (448, 95), (222, 227), (311, 240), (328, 230), (240, 283), (379, 277), (425, 282), (448, 197), (285, 399), (320, 369), (311, 343)):
        _o(s, m, cx, cy, 7.5, dark(F, .3)); _o(s, m, cx + 10, cy, 7.5, mix(A, F, .3))
    for cx, cy in ((293, 54), (399, 110), (497, 117), (502, 132), (490, 160), (473, 174), (459, 197), (72, 237), (136, 252), (329, 265), (340, 226), (322, 352), (208, 341), (124, 417), (170, 436), (198, 458), (226, 462), (344, 311)):
        _o(s, m, cx, cy, 7.5, mix(A, F, .3))
    for b, c in (((374, 76, 385, 87), mix(A, F, .3)), ((495, 141, 506, 152), mix(A, F, .3)), ((347, 319, 358, 330), mix(A, F, .3))):
        R(s, m, *b, c)
    R(s, m, 386, 305, 400, 317, dark(F, .3))
    for yy, n_, u, t, nx in ((75, "698", " mn", "Liters per year", 515), (166, "32.1", " %", "Market share", 522), (257, "8.9", "K+", "Points of sale", 522)):
        _p(s, m, (nx, yy + 8, 680, yy + 75), [[(n_, {"px": 46, "bold": True, "color": dark(F, .1)}), (u, {"px": 30, "bold": True, "color": dark(F, .1)})]], 30)
        _t(s, m, (682, yy + 25, 862, yy + 60), t, 21, color=G4, al=L)
    _sq = lambda cx, cy, c: R(s, m, cx - 5.5, cy - 5.5, cx + 5.5, cy + 5.5, c)
    _sq(420, 436, lg); _sq(420, 474, dg)
    _t(s, m, (449, 420, 655, 454), "Group A factory", 21, color=lg, al=L)
    _t(s, m, (449, 458, 655, 492), "Group B factory", 21, color=dg, al=L)
    _o(s, m, 669, 440, 6, lg); _o(s, m, 669, 476, 6, dg)
    _t(s, m, (699, 424, 862, 458), "Group A DC", 21, color=lg, al=L)
    _t(s, m, (699, 459, 862, 493), "Group B DC", 21, color=dg, al=L)


_CITY = [(138, 6), (144, 6), (148, 10), (148, 12), (144, 18), (144, 23), (136, 33), (138, 36), (134, 41), (136, 45), (134, 51), (136, 56), (134, 58), (134, 67), (138, 70), (138, 84), (136, 88), (139, 90), (144, 82), (152, 76), (157, 70), (160, 70), (168, 76), (178, 72), (186, 78), (189, 78), (192, 73), (197, 70), (202, 72), (205, 70), (211, 74), (219, 72), (228, 89), (228, 92), (222, 96), (214, 105), (218, 112), (214, 116), (216, 119), (222, 123), (220, 126), (222, 136), (220, 142), (216, 144), (212, 147), (214, 153), (208, 159), (210, 161), (202, 168), (198, 166), (190, 168), (181, 166), (177, 168), (176, 160), (173, 158), (162, 160), (157, 154), (152, 152), (146, 156), (141, 150), (134, 148), (130, 152), (130, 165), (126, 170), (115, 180), (111, 180), (108, 183), (106, 187), (104, 196), (106, 201), (114, 206), (114, 208), (100, 221), (104, 224), (100, 229), (102, 237), (108, 240), (106, 245), (112, 251), (110, 278), (112, 299), (116, 305), (114, 312), (116, 319), (118, 325), (118, 332), (116, 334), (118, 339), (116, 344), (118, 350), (108, 360), (110, 363), (99, 372), (93, 364), (86, 364), (82, 362), (79, 366), (75, 368), (58, 370), (45, 378), (41, 378), (40, 375), (42, 370), (48, 363), (48, 357), (42, 353), (42, 349), (35, 342), (28, 340), (26, 337), (24, 325), (22, 319), (26, 314), (26, 308), (37, 310), (40, 308), (40, 295), (38, 292), (38, 285), (45, 284), (48, 282), (44, 270), (40, 266), (31, 266), (30, 258), (36, 253), (30, 247), (42, 235), (37, 230), (35, 232), (32, 229), (28, 220), (28, 212), (32, 206), (26, 202), (28, 199), (26, 189), (28, 181), (26, 178), (32, 170), (32, 164), (40, 162), (44, 156), (44, 152), (48, 148), (45, 144), (39, 148), (25, 152), (22, 147), (22, 136), (29, 134), (44, 121), (46, 112), (44, 104), (48, 101), (42, 92), (44, 88), (38, 78), (31, 70), (28, 74), (24, 71), (22, 58), (14, 45), (16, 40), (12, 37), (14, 33), (19, 30), (25, 30), (32, 34), (35, 34), (41, 24), (49, 26), (54, 24), (62, 29), (60, 32), (63, 34), (67, 34), (72, 39), (72, 43), (76, 46), (82, 40), (87, 42), (94, 48), (102, 48), (106, 41), (112, 38), (118, 27), (116, 25), (120, 24), (128, 16), (126, 15), (131, 14), (133, 16), (136, 12)]


def city_coverage_circles(s, x, y, w, h):
    """Silhueta municipal cinza com círculos translúcidos que reforçam onde se cruzam; números e molde de foto. AB InBev p.33."""
    m = M((0, 0, 900, 386), (x, y, w, h))
    cells = _voronoi(_CITY, 48, seed=5)
    _multi(s, [m.ps(r) for _, r in cells], G3, "CFCFCF", .2)
    for cx, cy, d_ in ((118, 97, 40), (180, 112, 32), (97, 150, 76), (125, 140, 52), (157, 145, 30), (55, 172, 60), (80, 228, 56), (75, 260, 54)):
        q = _o(s, m, cx, cy, d_, A); ss.set_alpha(q, 45)
    _t(s, m, (254, 2, 700, 20), "The team went to the field to check how widely brands spread", 9.5, color=G4, al=L)
    R(s, m, 254, 22, 900, 115, G1)
    for yy in (22, 73, 115):
        ss.line(s, *m.p((254, yy)), *m.p((900, yy)), G4, .6, dash=True)
    _t(s, m, (268, 20, 330, 74), "27", 46, color=A, bold=True, al=L)
    _p(s, m, (331, 26, 420, 70), ["Stores", "visited"], 12.5)
    _t(s, m, (420, 20, 508, 74), "10+", 46, color=A, bold=True, al=L)
    _p(s, m, (514, 26, 640, 70), ["Districts", "in the city"], 12.5)
    _p(s, m, (265, 80, 890, 110), [[("Customers", {"bold": True, "color": A}), (" see the brand from ", {}), ("start to finish", {"bold": True, "color": A}), (", even when they are unaware", {})]], 11.5)
    for b in ((257, 127, 421, 240), (421, 127, 593, 188), (257, 240, 388, 378), (388, 240, 462, 378), (421, 188, 593, 240), (462, 240, 593, 378)):
        q = R(s, m, *b, G2, W, width=.75)
    _t(s, m, (257, 127, 593, 378), "[foto]", 18, color=G4)
    R(s, m, 603, 330, 606, 378, A)
    _p(s, m, (615, 334, 895, 378), ["Pictures of the store entrance,", "the beverage aisle and the", "cashier at three retail chains"], 10.5, color=G4)


_CODE = (
    ("import", "tabular"), ("import", "maps_client  # local helper"), ("", ""), ("key", "= open('KEY.txt').read()  # private"), ("client", "= maps_client.Client(key)"), ("", ""),
    ("def", "get_place(name):"), ("    try:", ""), ("    #", "name = 'Sample Store Inc.'"), ("    reply", "= client.places(query=name)"), ("    rows", "= reply.get('results')[0]"), ("    return", "rows"),
    ("    except", "Exception as e:"), ("    print", "(e)"), ("    return", "None"), ("", ""), ("book", "= tabular.load('Stores.xlsx')"), ("sheet", "= book.active"), ("", ""), ("last", "= sheet.max_row"), ("", ""),
    ("for", "i in range(2, 50):"), ("    try:", ""), ("    info", "= get_place(sheet.cell(i, 1).value)"), ("    sheet.cell(i, 3)", ".value = info['address']"), ("    sheet.cell(i, 2)", ".value = info['name']"), ("    sheet.cell(i, 4)", ".value = info['place_id']"), ("    sheet.cell(i, 5)", ".value = info['rating']"),
)


def code_plus_dot_map(s, x, y, w, h, iso="USA", n=620):
    """Cartão de código ao lado de mapa por estado com muitos pontos; iso e n trocam país e quantidade. AB InBev p.124."""
    m = M((0, 0, 900, 399), (x, y, w, h))
    poly(s, m, _rpoly(0, 8, 352, 394, 22, 22, 22, 22), dark(D, .72))
    kw, nm = light(A, .25), light(F, .6)
    paras, nums = [], []
    for i, (a, b) in enumerate(_CODE):
        nums.append([(str(i + 1), {"color": G4})])
        paras.append([(a + " ", {"color": kw}), (b, {"color": G2})] if a or b else [(" ", {"color": G2})])
    lh = (392 - 11) / len(_CODE)
    pt_ = lh * m.sx * 72
    _p(s, m, (6, 11, 26, 392), nums, 8.6, al=RT, anchor=TOP, spacing=Pt(pt_), font="Courier New")
    _p(s, m, (34, 11, 350, 392), paras, 8.6, anchor=TOP, spacing=Pt(pt_), font="Courier New")
    st = states(iso)
    pale = light(T, .55)
    if iso == "USA":
        low = {k: v for k, v in st.items() if k not in ("AK", "HI")}
        box = (462, 34, 882, 302); bd = (-124.8, -66.9, 24.5, 49.4)
        to, _ = gmap(s, m, box, low, pale, W, .75, bounds=bd)
        gmap(s, m, (470, 250, 535, 302), {"AK": {"rings": [r for r in st["AK"]["rings"] if r[0][0] < 0]}}, pale, W, .4, minpx=1)
        gmap(s, m, (556, 280, 588, 299), {"HI": st["HI"]}, pale, None, minpx=.3)
        pts = _sample(low, n, _US_HUBS, {"TX": 2, "CA": 1.5, "FL": 1.5, "MT": .5, "WY": .5, "NV": .5}, seed=9, hub_share=.62, keyname="us")
        _dots(s, m, [m.p(to(*p)) for p in pts], 4.8, A)
    else:
        to, _ = gmap(s, m, (462, 20, 882, 385), st, pale, W, .75)
        pts = _sample(st, n, (), seed=9, hub_share=0, keyname=iso)
        _dots(s, m, [m.p(to(*p)) for p in pts], 12 if n < 60 else 5.5, A)


_CA_BIG = [(-79.4, 43.7, 26), (-73.6, 45.5, 22), (-75.7, 45.4, 16), (-114, 51, 20), (-113.5, 53.5, 20), (-123.1, 49.3, 18), (-97.1, 49.9, 18), (-71.2, 46.8, 12), (-63.6, 44.7, 10), (-66, 45.3, 8)]


def canada_dots_kpi_strip(s, x, y, w, h):
    """Províncias só em contorno fraco, círculos proporcionais no sul e faixa branca de KPIs por cima do norte vazio. RBI p.32."""
    m = M((0, 0, 900, 513), (x, y, w, h))
    bd = (-140.5, -50.3, 41.7, 75.7)
    to, _ = gmap(s, m, (-10, 0, 880, 513), states("CAN"), W, G3, .5, bounds=bd, clip=(0, 0, 900, 513), minpx=3)
    ca = {k: states("CAN")[k] for k in ("BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL")}
    hubs = [(-123, 49.3, .7, 4), (-114, 51.5, 1.5, 2), (-113.5, 53.5, 1.5, 2), (-120, 50.5, 1.5, 1), (-97, 50, 1.5, 1), (-79.5, 43.8, .8, 5), (-76, 45, 1.2, 3), (-72.5, 46, 1.1, 4), (-70, 47.5, 1, 1.5), (-66, 46, 1.1, 2), (-63, 45.3, .8, 1.5), (-81.5, 43, .7, 1)]
    grey = _sample(ca, 75, hubs, {"SK": 3, "MB": 1.5}, seed=21, hub_share=.65, keyname="ca_grey")
    grey = [p for p in grey if p[1] < 57]
    _dots(s, m, [m.p(to(*p)) for p in grey], 4, "A6A6A6")
    small = [p for p in _sample(ca, 90, hubs, seed=22, hub_share=.95, keyname="ca_red") if p[1] < 56]
    red = dark(F, .05)
    _dots(s, m, [m.p(to(*p)) for p in small], 6, red, alpha=80)
    for lo, la, d_ in _CA_BIG:
        o_ = _o(s, m, *to(lo, la), d_ * .72, red, border=dark(red, .3), width=.4); ss.set_alpha(o_, 72)
    sp = poly(s, m, _rpoly(10, 4, 895, 193, 20, 20, 20, 20), W, edge=G2, ew=1.0)
    ss.set_alpha(sp, 90); shadow(sp, 3, 1, 90, "000000", .1)
    for x0, x1, a, b_ in ((66, 263, "Areas", "97"), (351, 549, "Residents", "7.6 mn"), (642, 840, "Stores", "697")):
        _p(s, m, (x0, 37, x1, 164), [[(a, {"px": 25})], [(b_, {"px": 33, "bold": True})]], 25, al=C_, color=W, fill=red, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=.14)
    for cx in (293, 578):
        for dx in (0, 19):
            _path(s, m, [(cx + dx, 76), (cx + dx + 18, 96), (cx + dx, 116)], G3, 2.2 * m.sx * 72 * 1.2)


_BUB_BIG = [(-46.6, -23.6, 78), (-48.0, -23.3, 44), (-43.3, -22.8, 40), (-49.5, -23.4, 60), (-51.2, -25.2, 46), (-44.8, -21.2, 44), (-48.5, -21.5, 42), (-47, -22.2, 36), (-43.9, -19.9, 30), (-38.5, -12.9, 72), (-39.0, -14.4, 56), (-36.6, -13.0, 42),
            (-38.5, -3.8, 50), (-37.3, -4.4, 40), (-35.3, -5.8, 40), (-35.9, -7.3, 32), (-49.3, -16.7, 26), (-51.8, -30.0, 24), (-60, -3.1, 26), (-48.5, -1.5, 22), (-44.3, -2.8, 22), (-36.7, -9.6, 20), (-48.5, -26.5, 18), (-42.8, -5.1, 20),
            (-42.8, -11.5, 22), (-50.3, -20.8, 34), (-53.4, -24.9, 30), (-52.3, -20.8, 22), (-64.5, -9.3, 22), (-40.3, -20.3, 18)]


def proportional_city_bubbles(s, x, y, w, h):
    """Brasil branco em fio fino e círculos translúcidos proporcionais, em cartão numerado com aba. Meliuz p.5."""
    m = M((0, 0, 606, 900), (x, y, w, h))
    sp = R(s, m, 44, 22, 600, 890, G1); shadow(sp, 5, 2, 45, "000000", .4)
    poly(s, m, ((44, 212), (104, 212), (44, 253)), dark(F, .35))
    R(s, m, 0, 6, 104, 212, F)
    _t(s, m, (0, 24, 104, 78), "02", 34, color=W, bold=True)
    R(s, m, 20, 100, 82, 180, None, W, width=max(.6, 2 * m.sx * 72))
    for yy in (130, 146, 162):
        ss.line(s, *m.p((30, yy)), *m.p((72, yy)), W, max(.6, 1.6 * m.sx * 72), dash=False)
    _t(s, m, (30, 104, 72, 126), "$", 18, color=W, bold=True)
    _t(s, m, (150, 50, 540, 92), "RECEIPT SCANNING", 28)
    ss.line(s, *m.p((175, 92)), *m.p((516, 92)), INK, .75, dash=False)
    _p(s, m, (120, 108, 570, 175), [[("Scanning receipts gives", {"italic": True})], [("the consumer cashback", {"italic": True})]], 22, al=C_)
    _t(s, m, (75, 248, 450, 272), "Distribution across the country", 15, italic=True, al=L)
    b = states("BRA")
    to, _ = gmap(s, m, (97, 285, 545, 755), b, W, G4, .5)
    wts = {"SP": 3, "MG": 3, "BA": 2, "PR": 2, "RS": 2, "SC": 1.5, "CE": 1.5, "GO": 1.5, "AM": .12, "PA": .35, "MT": .12, "MS": .2, "RR": .1, "AP": .1, "TO": .7, "RO": .7, "AC": .3, "MA": .6, "PI": .4}
    pts = _sample(b, 90, _BR_HUBS, wts, seed=6, hub_share=.1, keyname="br_bub")
    rnd = random.Random(2)
    for lo, la, d_ in _BUB_BIG:
        q = _o(s, m, *to(lo, la), d_ * .92, F); ss.set_alpha(q, 45)
    for lo, la in pts:
        q = _o(s, m, *to(lo, la), rnd.choice((9, 10, 11, 12, 14)), F); ss.set_alpha(q, 50)
    _t(s, m, (62, 765, 150, 815), "61%", 36, color=F, bold=True, al=L)
    _p(s, m, (176, 765, 480, 815), [[("of penetration across", {"bold": True})], [("the country's cities", {"bold": True})]], 19)
    _p(s, m, (66, 830, 170, 875), [[("1.1", {"px": 36, "bold": True, "color": F}), (" mn", {"px": 25, "bold": True, "color": F})]], 25)
    _p(s, m, (176, 825, 480, 875), [[("offers activated", {"bold": True})], [("in the last quarter", {"bold": True})]], 19)


# ---------- Mapa-raster e bairros ----------

def _heat(s, m, cx, cy, d_, hot=False):
    """Mancha de calor: elipses com borda suave empilhadas. hot=True chega ao vermelho no centro."""
    k = m.sx * 72
    soft(_alpha(_o(s, m, cx, cy, d_ * 1.5, F), 72), d_ * .32 * k)
    soft(_alpha(_o(s, m, cx, cy, d_ * .85, A), 85), d_ * .2 * k)
    if hot:
        soft(_o(s, m, cx, cy, d_ * .62, ss.NEG), d_ * .14 * k)


def _alpha(sp, a):
    ss.set_alpha(sp, a)
    return sp


def raster_heat_frame(s, x, y, w, h):
    """Dois mapas com manchas de calor, pinos e placas, em moldura escura que sangra à direita. Mercado Libre p.14."""
    m = M((0, 0, 900, 369), (x, y, w, h))
    poly(s, m, _rpoly(5, 5, 900, 365, 20, 0, 0, 20), D)
    # painel principal
    sea, land = light(T, .55), G1
    pb = (14, 13, 558, 359)
    poly(s, m, _rpoly(*pb, 18, 18, 18, 18), sea)
    cv = _rpoly(*pb, 18, 18, 18, 18, n=4)
    bd = (-75.2, -21.2, -35.8, -2.9)
    gmap(s, m, pb, _sub("BRA", "BOL", "PRY", "ARG", "URY", "CHL", "PER", "COL", "VEN", "GUY", "SUR", "ECU"), land, G3, .5, bounds=bd, clip=cv)
    gmap(s, m, pb, {k: v for k, v in states("BRA").items()}, land, G2, .35, bounds=bd, clip=cv)
    for cx, cy, d_, hot in ((408, 48, 44, 0), (358, 70, 58, 0), (383, 105, 56, 0), (283, 137, 50, 0), (258, 195, 58, 0), (337, 195, 52, 0), (268, 266, 54, 0), (236, 283, 66, 0), (181, 338, 30, 0), (300, 230, 92, 1)):
        _heat(s, m, cx, cy, d_, bool(hot))
    # painel do México
    pc = (578, 16, 870, 192)
    poly(s, m, _rpoly(*pc, 12, 12, 12, 12), sea)
    cv2_ = _rpoly(*pc, 12, 12, 12, 12, n=4)
    gmap(s, m, pc, _sub("MEX", "GTM", "BLZ", "HND", "SLV", "CUB", "NIC"), land, G3, .5, bounds=(-113, -80.5, 13.5, 30.5), clip=cv2_, minpx=2)
    gmap(s, m, pc, {"US": countries_50m().get("USA", {"rings": []})}, land, G3, .5, bounds=(-113, -80.5, 13.5, 30.5), clip=cv2_, minpx=2)
    for cx, cy, d_ in ((728, 78, 58), (736, 152, 54), (765, 172, 30)):
        _heat(s, m, cx, cy, d_)
    plate = "595959"
    for b, t in (((174, 201, 276, 225), "Hub A"), ((332, 186, 495, 209), "Hub B"), ((47, 319, 172, 342), "Hub C"), ((602, 125, 725, 148), "Hub D")):
        q = R(s, m, *b, plate); ss.set_alpha(q, 90)
        _t(s, m, (b[0] + 10, b[1], b[2], b[3]), t, 16, color=W, al=L)
    for tipx, tipy, hh in ((300, 226, 48), (335, 208, 46), (180, 344, 48), (737, 148, 47)):
        _pin(s, m, tipx, tipy, hh, ss.NEG)
    _p(s, m, (585, 258, 780, 315), [[("Network heatmap", {"italic": True})], [("by metro area", {"italic": True})]], 19, color=W)
    ss.line(s, *m.p((576, 324)), *m.p((637, 324)), W, 1.0, dash=False)
    poly(s, m, _rpoly(788, 254, 900, 330, 16, 0, 0, 16), W)
    _t(s, m, (788, 254, 900, 330), "[logo]", 15, color=G4)


_STREETS = (
    (((0, 20), (40, 26), (86, 18)), ((10, 60), (50, 52), (130, 72)), ((30, 0), (46, 40), (40, 92)), ((90, 0), (82, 40), (110, 92)), ((0, 40), (30, 44), (60, 74))),
    (((0, 38), (60, 20), (130, 30)), ((5, 70), (40, 60), (86, 88)), ((50, 0), (70, 30), (64, 92)), ((100, 0), (96, 48), (120, 92)), ((16, 12), (30, 50), (22, 92))),
    (((0, 25), (50, 28), (120, 16)), ((0, 58), (60, 60), (100, 72)), ((28, 0), (32, 45), (46, 92)), ((70, 0), (64, 50), (70, 92)), ((104, 0), (92, 40), (120, 60))))


def neighbourhood_thumbs(s, x, y, w, h):
    """Três cartões de bairro: miniatura de ruas com pino e polígono, selo, nome, fio pontilhado e valor. Vasta p.23."""
    m0 = M((0, 0, 900, 140), (x, y + (h - w * 140 / 900) / 2, w, w * 140 / 900))
    m = m0
    pink = F
    poly(s, m, _rpoly(2, 2, 898, 138, 12, 12, 12, 12), W, edge=G2, ew=.75)
    _p(s, m, (11, 5, 500, 23), [[("Target neighbourhoods ", {"bold": True, "color": pink}), ("(Geodata)", {"bold": True, "italic": True, "color": pink})]], 11.5)
    cards = ((3, 292, "City A", F, "Central District", "65", ((24, 52), (58, 46), (100, 70), (56, 92)), (68, 66), ()),
             (303, 594, "City B", D, "Garden Avenue", "55", ((344, 72), (384, 54), (420, 58), (416, 96), (372, 102)), (372, 73), ((304, 28), (340, 26), (352, 30), (344, 50), (304, 60))),
             (604, 893, "City C", F, "Harbour Quarter", "48", ((660, 62), (682, 56), (690, 94), (668, 100)), (669, 70), ((700, 26), (745, 26), (745, 62), (722, 70), (706, 50))))
    for x0, x1, city, col, name, val, pg, pin_, water in cards:
        poly(s, m, _rpoly(x0, 26, x1, 134, 8, 8, 8, 8), W, edge=G2, ew=.75)
        tw = 135 if x0 == 3 else 135 if x0 == 303 else 140
        poly(s, m, _rpoly(x0 + 1, 27, x0 + tw, 133, 7, 0, 0, 7), G1)
        ox, oy = x0, 30
        cv = _rect((x0 + 1, 27, x0 + tw, 133))
        idx = cards.index((x0, x1, city, col, name, val, pg, pin_, water))
        if water:
            poly(s, m, _clip(list(water), cv), light(T, .35))
        for st in _STREETS[idx]:
            pts = [(ox + a, oy + b) for a, b in _smooth(st, 5)]
            # a rua fica dentro da miniatura
            pts = [p for p in pts if cv[0][0] <= p[0] <= cv[1][0] and 27 <= p[1] <= 133]
            if len(pts) > 1: _path(s, m, pts, W, .9)
        for k_ in range(6):   # malha fina de quarteirões
            xx = x0 + 12 + k_ * (tw - 18) / 5
            _path(s, m, [(xx, 28), (xx + 8, 132)], W, .35)
            yy_ = 34 + k_ * 18
            _path(s, m, [(x0 + 2, yy_), (x0 + tw - 1, yy_ + 5)], W, .35)
        _t(s, m, (x0 + 3, 120, x0 + 40, 133), "[mapa]", 6.5, color=G4, al=L)
        poly(s, m, pg, pink, alpha=28, edge=pink, ew=.35)
        _pin(s, m, pin_[0], pin_[1], 28, pink)
        tx0 = x0 + tw + 10
        _chip(s, m, (tx0, 39, tx0 + 53, 55), city, 9.5, fill=col, adj=.15, bold=False)
        _t(s, m, (tx0, 60, x1 - 2, 82), name, 11.5, al=L)
        _path(s, m, [(tx0, 85), (x1 - 8, 85)], F, .6, dash=DOT)
        _p(s, m, (tx0 + 4, 90, x1 - 2, 122), [[("$ ", {"px": 11}), (val, {"px": 19, "color": F}), ("/m²-month", {"px": 11})]], 11)


# ---------- Galeria ----------

SLIDES = [
    ("Choropleths by tier let the region carry the message", "Tiles, legends and values placed so the map needs no leader lines",
     [("Tier map and table in a tile", "Cury p.7", tier_choropleth_tile), ("Three classes, legend squares", "Intelbras p.2", three_tier_legend), ("Values in the region's tint", "Vasta p.27", region_ramp_values),
      ("Pills keyed to states", "3R Petroleum p.2", pill_cluster_card), ("Grey classes, dark table", "Meliuz p.106", greyscale_dark_table), ("Wedge from state into bars", "Sabesp p.7", wedge_state_blocks)]),
    ("Municipal meshes and heat fields show fine-grained reach", "Cell meshes stand in for municipalities; street rasters become moulds",
     [("Adjacency tiers breakout", "Sabesp p.34", adjacency_tier_map), ("Footprint with corner chips", "Sabesp p.2", municipal_footprint_chips), ("Coverage circles", "AB InBev p.33", city_coverage_circles),
      ("Heat maps in a dark frame", "Mercado Libre p.14", raster_heat_frame), ("Neighbourhood thumbnails", "Vasta p.23", neighbourhood_thumbs), ("Dot density, no outline", "Vibra p.23", dot_density_no_outline)]),
    ("Regional maps carry cards, plates and arrows", "Labels sit over water or empty land, so nothing covers the data",
     [("Screening cards on leaders", "Nubank p.44", screening_cards), ("Map in a summary card", "Nubank p.2", latam_summary_card), ("Ring-percent circles", "Mercado Libre p.2", ring_percent_circles),
      ("Diamonds and dark plates", "BTG Pactual p.120", diamond_plates), ("Flow arrows out of a country", "AB InBev p.35", flow_arrows_country), ("Pale map, two-owner dots", "Vibra p.17", two_owner_dots_tile)]),
    ("World maps and dot layers scale the footprint", "One grey or white mass, with bubbles and dots drawn on top",
     [("Gold-halo bubbles", "Kering p.15", gold_halo_bubbles), ("Brand world, stacked numbers", "Meliuz p.88", world_brand_stack), ("Code card and dot map", "AB InBev p.124", code_plus_dot_map),
      ("Province map, KPI strip", "RBI p.32", canada_dots_kpi_strip), ("Translucent city circles", "Meliuz p.5", proportional_city_bubbles), ("Map breaking out of a card", "Vibra p.27", map_breaks_card_strips)]),
    ("Corridor cut-outs isolate the operating geography", "Only the relevant states or countries stay; the rest of the slide holds the labels",
     [("Corridor in one gradient", "CSN-Arcelor p.30", corridor_cutout), ("Corridor zoom with rail", "CSN LM p.27", corridor_zoom_rail), ("Operating states, elbows", "CSN-Arcelor p.6", states_only_elbow),
      ("Gradient band, two countries", "CSN LM p.11", band_highlight_country), ("Framed tile, asset dots", "CSN LM p.16", framed_tile_asset_dots)]),
]

if __name__ == "__main__":
    MASTER, OUT = sys.argv[1], sys.argv[2]
    LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    prs = ss.new_deck(MASTER, prefs=sys.argv[4] if len(sys.argv) > 4 else None, profile_dir=sys.argv[5] if len(sys.argv) > 5 else None)
    gallery(prs, prs.slide_layouts[LAYOUT], SLIDES, "Sources: reference decks as labelled. All content is illustrative; only the technique comes from the source.")
    ss.save(prs, OUT)
