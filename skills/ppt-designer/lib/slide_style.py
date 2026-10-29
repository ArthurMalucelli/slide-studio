"""Biblioteca de estilo para slides de equity research, para qualquer slide mestre.

Nada aqui tem conteúdo de slide. A biblioteca traz componentes testados no PowerPoint, mais a paleta e a grade lidas
do mestre (via master_profile.py).

Uso mínimo:
    import sys; sys.path.insert(0, "<plugin>/lib")
    import slide_style as ss
    prs = ss.new_deck("mestre.pptx", prefs="deck_prefs.json")   # lê/gera o profile e aplica paleta e fontes
    s = ss.add_slide(prs, layout_index)
    ss.setup(s, "Título storytelling", "Subtítulo")
    ...
    ss.save(prs, "out/slide.pptx")                               # já roda fix_axes()

Cores: use os NOMES dos papéis (ss.FOCUS, ss.ACCENT, ss.PEER…). Eles valem o hex do tema do mestre no momento
de desenhar, o que permite mudar a paleta de um deck sem mexer no script. Um hex literal ("1A56D6") também é aceito.
Grade: ss.G["content_left"], ss.G["column_x"]… (ver profile.json). Helpers: ss.cols(n), ss.rows(n).
"""
import json
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_TICK_MARK, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

import master_profile as mp

LIB = Path(__file__).resolve().parent

# ---------- papéis de cor (tokens resolvidos na hora de desenhar) ----------
FOCUS = "FOCUS"            # empresa-foco, série principal
FOCUS_TINT = "FOCUS_TINT"  # empresa-foco fora de destaque, "restante"
FOCUS_DARK = "FOCUS_DARK"  # lateral de sólidos 3D
FOCUS_TOP = "FOCUS_TOP"    # topo de sólidos 3D
ACCENT = "ACCENT"          # ÚNICO destaque: 2ª série, linha, anotação
PEER = "PEER"              # terceiros/concorrentes (nunca a empresa-foco)
PEER_DARK = "PEER_DARK"    # linha/pill de terceiros
NEG = "NEG"                # só negativo/alerta
FG, FG2, MUTED, AXIS, WHITE = "FG", "FG2", "MUTED", "AXIS", "WHITE"

PALETTE = mp.palette({"dk2": "0B1D4E", "accent1": "1A56D6"})   # padrão até new_deck() carregar o mestre
FONT = "Calibri"
PROFILE = {}
G = {}          # grade do mestre (profile["grid"])
PREFS = {}      # preferências do deck (deck_prefs.json): fundo, 3D, números grandes…


def hx(c):
    """Token de papel ou hex → hex."""
    return PALETTE.get(c, c)


def rgb(h):
    return RGBColor.from_string(hx(h))


def paint(fill, color):
    fill.solid(); fill.fore_color.rgb = rgb(color)


# =====================================================================
# Deck, profile, placeholders e cabeçalhos
# =====================================================================
def load_profile(master, cache_dir=None):
    """Lê <cache_dir>/profile.json se existir (pode ter sido corrigido à mão); senão infere do mestre e grava."""
    cache = Path(cache_dir or Path(master).with_suffix("")).joinpath("profile.json") if cache_dir else None
    if cache and cache.exists():
        return json.loads(cache.read_text())
    prof = mp.profile(master)
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(prof, indent=1, ensure_ascii=False))
    return prof


def apply_profile(prof, prefs=None):
    """Carrega paleta, fonte e grade. prefs (dict) pode sobrescrever: {"palette": {"FOCUS": "…"}, "font": "…"}."""
    global PROFILE, G, FONT, PREFS
    PROFILE, G = prof, prof["grid"]
    PREFS = prefs or {}
    PALETTE.clear(); PALETTE.update(prof["palette"]); PALETTE.update(PREFS.get("palette", {}))
    FONT = PREFS.get("font") or prof["fonts"]["body"]


def new_deck(master, prefs=None, profile_dir=None, keep_slides=False, drop_master_shapes=()):
    """Abre o mestre, apaga os slides de exemplo e aplica profile + prefs.
    prefs: dict ou caminho de deck_prefs.json. drop_master_shapes: nomes de formas do mestre a remover
    (ex.: um tracker estático que o script vai redesenhar)."""
    if isinstance(prefs, (str, Path)):
        prefs = json.loads(Path(prefs).read_text()) if Path(prefs).exists() else {}
    apply_profile(load_profile(master, profile_dir), prefs)
    prs = Presentation(master)
    if not keep_slides:
        ids = prs.slides._sldIdLst
        for sid in list(ids):
            prs.part.drop_rel(sid.rId); ids.remove(sid)
    for m in prs.slide_masters:
        for sh in list(m.shapes):
            if sh.name in drop_master_shapes:
                sh._element.getparent().remove(sh._element)
    return prs


def cols(n, gap=None, left=None, right=None):
    """n colunas iguais dentro da área de conteúdo do mestre → [(x, w), …]."""
    gap = G.get("gutter", 0.33) if gap is None else gap
    l = G["content_left"] if left is None else left
    r = G["content_right"] if right is None else right
    w = (r - l - gap * (n - 1)) / n
    return [(round(l + i * (w + gap), 3), round(w, 3)) for i in range(n)]


def rows(n, gap=0.3, top=None, bottom=None):
    """n faixas iguais dentro da área de conteúdo → [(y, h), …]. Reserve ~0.58" no topo de cada uma para o cabeçalho."""
    t = G["content_top"] if top is None else top
    b = G["content_bottom"] if bottom is None else bottom
    h = (b - t - gap * (n - 1)) / n
    return [(round(t + i * (h + gap), 3), round(h, 3)) for i in range(n)]


def forbidden_hit(x, y, w, h):
    """True se a caixa encosta numa zona proibida do mestre (logo, curva, faixa decorativa)."""
    for fx, fy, fw, fh in G.get("forbidden", []):
        if x < fx + fw and fx < x + w and y < fy + fh and fy < y + h:
            return True
    return False


def add_slide(prs, layout):
    """layout: índice ou nome do layout (ver profile.json → layouts)."""
    if isinstance(layout, str):
        layout = next(l.index for l in [type("L", (), {"index": i, "name": x.name}) for i, x in
                                        enumerate(prs.slide_layouts)] if l.name == layout)
    return prs.slides.add_slide(prs.slide_layouts[layout])


def ph(slide, idx):
    for p in slide.placeholders:
        if p.placeholder_format.idx == idx:
            return p
    raise KeyError(idx)


def has_ph(slide, idx):
    return any(p.placeholder_format.idx == idx for p in slide.placeholders)


def drop_ph(slide, idx):
    e = ph(slide, idx)._element
    e.getparent().remove(e)


def set_ph(slide, idx, value, color=FG):
    p = ph(slide, idx)
    p.text_frame.text = value
    for r in p.text_frame.paragraphs[0].runs:
        r.font.color.rgb = rgb(color)
    return p


def header_ph(slide, idx, value, kind, box=None):
    """Cabeçalho de painel em placeholder: kind 'h' (14 regular, FG) ou 's' (11 itálico, MUTED). box=(x, w)."""
    p = set_ph(slide, idx, value, FG if kind == "h" else MUTED)
    if box:  # ao mexer em x/largura, regravar y/altura (senão o PowerPoint zera)
        top, h = p.top, p.height
        p.left, p.width, p.top, p.height = Inches(box[0]), Inches(box[1]), top, h
    return p


def setup(slide, title, subtitle=None, panels=(), drop_others=True):
    """Título e subtítulo nos placeholders que o profile identificou; panels: [(idx, texto, 'h'|'s', box|None)].
    drop_others: remove os placeholders de conteúdo vazios (gráficos e desenhos vão em caixas próprias)."""
    t, s = G.get("title"), G.get("subtitle")
    if t and has_ph(slide, t["idx"]):
        set_ph(slide, t["idx"], title, FG)
    else:
        text(slide, G["content_left"], 0.35, G["content_right"] - G["content_left"], 0.6,
             [[(title, {"bold": True, "color": FG, "size": 26})]], margin=0.0)
    if subtitle is not None and s and has_ph(slide, s["idx"]):
        set_ph(slide, s["idx"], subtitle, FG2)
    used = {t and t["idx"], s and s["idx"], *(p[0] for p in panels)}
    for idx, val, kind, box in panels:
        header_ph(slide, idx, val, kind, box)
    if drop_others:
        foot = G.get("footer") and G["footer"]["idx"]
        for p in list(slide.placeholders):
            i = p.placeholder_format.idx
            if i not in used and i != foot and not (p.has_text_frame and p.text_frame.text.strip()):
                p._element.getparent().remove(p._element)


def footer(slide, sources, notes=None, size=7):
    """Rodapé 'Sources: …' (+ notas numa 2ª linha): no placeholder de rodapé do mestre, se houver; senão numa caixa
    logo abaixo da área de conteúdo, alinhada à direita."""
    body = sources + ("\v" + notes if notes else "")
    f = G.get("footer")
    if f and has_ph(slide, f["idx"]):
        fp = ph(slide, f["idx"])
        span = G["content_right"] - G["content_left"]
        if fp.width / 914400 < span * 0.45:      # rodapé estreito: alarga até a coluna da direita (menos linhas)
            right = fp.left + fp.width
            x = min(c for c in cols(2)[1:2])[0]
            top, h = fp.top, fp.height
            fp.left, fp.width, fp.top, fp.height = Inches(x), right - Inches(x), top, h
        tf = fp.text_frame
    else:
        y = G["content_bottom"] + 0.05
        tf = text(slide, G["content_left"], y, G["content_right"] - G["content_left"], 0.4, "", margin=0.0).text_frame
    tf.text = body  # 1 parágrafo com quebra: sem espaçamento extra
    tf.word_wrap = True
    tf.margin_top = tf.margin_bottom = 0
    for para in tf.paragraphs:
        para.space_before = para.space_after = Pt(0)
        for r in para.runs:
            r.font.size = Pt(size); r.font.color.rgb = rgb(MUTED); r.font.name = FONT


def tracker(slide, items, active, x, y, size=14):
    """Tracker de seção desenhado (opcional): item ativo em bold FOCUS com barra de 3pt acima."""
    for it in items:
        on = it == active
        w = (0.12 if on else 0.112) * len(it) * size / 14 + 0.08
        tb = text(slide, x, y, w, 0.34, [[(it, {"bold": on, "color": FOCUS if on else MUTED, "size": size})]],
                  margin=0.02)
        tb.text_frame.word_wrap = False
        if on:
            line(slide, x + 0.02, y - 0.01, x + w - 0.08, y - 0.01, FOCUS, 3, dash=False)
        x += w + 0.12


def panel_header(slide, x, y, w, head, sub):
    """Cabeçalho desenhado: frase-conclusão 14pt + itálico 11pt (o que o gráfico mostra, unidade, período).
    Devolve o y onde o visual começa."""
    hd = text(slide, x, y, w, 0.28, [[(head, {"color": FG, "size": 14})]], anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    hd.text_frame.word_wrap = False
    text(slide, x, y + 0.28, w, 0.23, [[(sub, {"italic": True, "color": MUTED, "size": 11})]],
         anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    return y + 0.58


# =====================================================================
# Formas e texto
# =====================================================================
def text(slide, x, y, w, h, runs, size=9, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         fill=None, line=None, dash=False, shape=MSO_SHAPE.RECTANGLE, margin=0.04):
    """runs: lista de parágrafos; cada parágrafo = lista de (texto, {bold, italic, color, size}). Aceita str."""
    sp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = 0.18
    sp.shadow.inherit = False
    if fill:
        paint(sp.fill, fill)
    else:
        sp.fill.background()
    if line:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(1)
        if dash:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        sp.line.fill.background()
    tf = sp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    if isinstance(runs, str):
        runs = [[(runs, {})]]
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for t, st in para:
            r = p.add_run(); r.text = t
            f = r.font; f.name = FONT; f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", False); f.italic = st.get("italic", False)
            f.color.rgb = rgb(st.get("color", FG))
    return sp


def note(slide, x, y, w, h, msg):
    """Nota de painel: 8pt itálico MUTED."""
    return text(slide, x, y, w, h, [[(msg, {"italic": True, "color": MUTED, "size": 8})]], margin=0.0)


def line(slide, x1, y1, x2, y2, color=MUTED, width=1, dash=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(width)
    if dash:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return c


def rect(slide, x, y, w, h, fill=None, border=None, dash=False, width=1.0):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.shadow.inherit = False
    if fill:
        paint(sp.fill, fill)
    else:
        sp.fill.background()
    if border:
        sp.line.color.rgb = rgb(border); sp.line.width = Pt(width)
        if dash:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        sp.line.fill.background()
    return sp


def pill(slide, cx, y, label, fill=FOCUS, color=WHITE, border=None, w=None, h=0.2, size=9):
    """Etiqueta arredondada centrada em cx (mesmo visual dos data labels)."""
    w = w or 0.12 + 0.075 * len(label)
    sp = text(slide, cx - w / 2, y, w, h, [[(label, {"bold": True, "color": color, "size": size})]],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fill=fill, line=border,
              shape=MSO_SHAPE.ROUNDED_RECTANGLE, margin=0.0)
    sp.text_frame.word_wrap = False
    return sp


def bracket(slide, xa, ya, xb, yb, level, label, color=FOCUS):
    """Colchete em cotovelo de (xa,ya) a (xb,yb) passando pela altura `level`, com pill no meio."""
    line(slide, xa, ya, xa, level, color)
    line(slide, xa, level, xb, level, color)
    line(slide, xb, level, xb, yb, color)
    pill(slide, (xa + xb) / 2, level - 0.11, label, fill=color, h=0.22)


def legend(slide, x, y, rows, size=9, gap=0.25):
    """Legenda desenhada com formas (nunca o glifo ■). rows = [[(kind, cor, rótulo), ...], ...];
    kind: 'box' (quadrado), 'dash' (faixa tracejada), 'tick' (traço vertical), 'line' (linha horizontal)."""
    for r, row in enumerate(rows):
        xx, yy = x, y + r * 0.21
        for kind, col, lab in row:
            if kind == "box":
                rect(slide, xx, yy + 0.04, 0.13, 0.13, fill=col)
            elif kind == "dash":
                rect(slide, xx - 0.03, yy + 0.04, 0.2, 0.13, border=col, dash=True, width=1.25)
            elif kind == "tick":
                line(slide, xx + 0.065, yy + 0.02, xx + 0.065, yy + 0.19, col, 1.75, dash=False)
            else:
                line(slide, xx - 0.02, yy + 0.105, xx + 0.17, yy + 0.105, col, 2.25, dash=False)
            w = 0.075 * len(lab) + 0.1
            text(slide, xx + 0.22, yy, w, 0.21, [[(lab, {"color": FG2, "size": size})]],
                 anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
            xx += 0.22 + w + gap


def key_stats(slide, x, y, w, h, stats, title="Key stats"):
    """Card branco com borda navy: até 4 números grandes + rótulo curto, divisórias finas."""
    text(slide, x, y, w, h, "", fill=WHITE, line=FOCUS, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x + w / 2 - 0.75, y + 0.04, 1.5, 0.26, [[(title, {"bold": True, "italic": True, "color": FOCUS, "size": 12})]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    tw = w / len(stats)
    for i, (v, lb) in enumerate(stats):
        xx = x + i * tw
        text(slide, xx, y + 0.3, tw, 0.4, [[(v, {"bold": True, "color": FOCUS, "size": 18})]],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
        text(slide, xx + 0.08, y + 0.72, tw - 0.16, h - 0.8, [[(lb, {"color": FG2, "size": 8})]],
             align=PP_ALIGN.CENTER, margin=0.0)
        if i:
            line(slide, xx, y + 0.36, xx, y + h - 0.18, PEER, 0.75, dash=False)


def picture(slide, path, x, y_base, width):
    """Imagem (PNG com fundo transparente de preferência) pousada numa linha de base, proporção preservada."""
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(0), width=Inches(width))
    pic.top = Inches(y_base) - pic.height
    return pic


# =====================================================================
# 3D isométrico (estilo Sabesp/Intelbras): freeforms editáveis
# =====================================================================
def poly(slide, pts, fill, line_color=None):
    """Polígono livre em polegadas. Coordenadas em 1/1000 pol.: o custGeom grava inteiros."""
    k = [(round(x * 1000), round(y * 1000)) for x, y in pts]
    fb = slide.shapes.build_freeform(k[0][0], k[0][1], scale=914.4)
    fb.add_line_segments(k[1:], close=True)
    sp = fb.convert_to_shape()
    sp.shadow.inherit = False
    paint(sp.fill, fill)
    if line_color:
        sp.line.color.rgb = rgb(line_color); sp.line.width = Pt(0.5)
    else:
        sp.line.fill.background()
    return sp


def cube(slide, x, yb, w, a, d, front=FOCUS, top=FOCUS_TINT, side=FOCUS_DARK, show_side=True):
    """Prisma isométrico: frente w×a com base em yb, profundidade (d, -0.6d). d≈0.18 fica bom."""
    dy = -0.6 * d
    poly(slide, [(x, yb - a), (x + w, yb - a), (x + w + d, yb - a + dy), (x + d, yb - a + dy)], top)
    if show_side:
        poly(slide, [(x + w, yb - a), (x + w + d, yb - a + dy), (x + w + d, yb + dy), (x + w, yb)], side)
    poly(slide, [(x, yb - a), (x + w, yb - a), (x + w, yb), (x, yb)], front)


def to_back(slide, shape):
    """Manda uma forma para trás de tudo (útil para funis/zooms translúcidos)."""
    tree = slide.shapes._spTree
    tree.remove(shape._element); tree.insert(2, shape._element)


def set_alpha(shape, alpha_pct):
    """Transparência do preenchimento sólido (alpha_pct = opacidade, ex. 28)."""
    clr = shape.fill._xPr.find(qn("a:solidFill"))[0]
    a = etree.SubElement(clr, qn("a:alpha")); a.set("val", str(int(alpha_pct * 1000)))


# =====================================================================
# Gráficos nativos (XML ajustado para o PowerPoint renderizar certo)
# =====================================================================
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
C15 = "http://schemas.microsoft.com/office/drawing/2012/chart"


def E(tag, **attrs):
    el = etree.Element(qn(tag))
    for k, v in attrs.items():
        el.set(k, str(v))
    return el


def sub(parent, tag, **attrs):
    el = E(tag, **attrs); parent.append(el); return el


def solid(parent, hexcolor):
    sf = sub(parent, "a:solidFill"); sub(sf, "a:srgbClr", val=hx(hexcolor))


def sppr(fill=None, line_color=None, dash=False, width=12700):
    sp = E("c:spPr")
    if fill:
        solid(sp, fill)
    else:
        sub(sp, "a:noFill")
    ln = sub(sp, "a:ln", w=width)
    if line_color:
        solid(ln, line_color)
        if dash:
            sub(ln, "a:prstDash", val="dash")
    else:
        sub(ln, "a:noFill")
    return sp


def txpr(color=WHITE, size=9, bold=True):
    tx = E("c:txPr")
    sub(tx, "a:bodyPr", wrap="none", lIns=38100, tIns=19050, rIns=38100, bIns=19050, anchor="ctr")
    sub(tx, "a:lstStyle")
    p = sub(tx, "a:p"); ppr = sub(p, "a:pPr")
    d = sub(ppr, "a:defRPr", sz=int(size * 100), b=1 if bold else 0)
    solid(d, color)
    sub(d, "a:latin", typeface=FONT)
    sub(p, "a:endParaRPr", lang="en-US")
    return tx


def _roundrect_ext():
    ext_lst = E("c:extLst")
    ext = sub(ext_lst, "c:ext", uri="{CE6537A1-D6FC-4f65-9D91-7224C49458BB}")
    sp = etree.SubElement(ext, f"{{{C15}}}spPr", nsmap={"c15": C15})
    geom = etree.SubElement(sp, f"{{{A}}}prstGeom", prst="roundRect")
    etree.SubElement(geom, f"{{{A}}}avLst")
    etree.SubElement(sp, f"{{{A}}}noFill")
    ln = etree.SubElement(sp, f"{{{A}}}ln"); etree.SubElement(ln, f"{{{A}}}noFill")
    return ext_lst


def _label_body(el, fmt, fill, color, pos, border=None, dash=False, rich=None):
    if rich is not None:
        tx = sub(el, "c:tx"); r = sub(tx, "c:rich")
        sub(r, "a:bodyPr", wrap="none", lIns=38100, tIns=19050, rIns=38100, bIns=19050, anchor="ctr")
        sub(r, "a:lstStyle")
        for i, line_txt in enumerate(rich.split("\n")):
            p = sub(r, "a:p"); ppr = sub(p, "a:pPr"); ppr.set("algn", "ctr")
            d = sub(ppr, "a:defRPr", sz=900, b=1); solid(d, color); sub(d, "a:latin", typeface=FONT)
            run = sub(p, "a:r"); rp = sub(run, "a:rPr", lang="en-US", sz=900 if i == 0 else 800, b=1)
            solid(rp, color); sub(rp, "a:latin", typeface=FONT)
            t = sub(run, "a:t"); t.text = line_txt
    sub(el, "c:numFmt", formatCode=fmt, sourceLinked=0)
    el.append(sppr(fill, border, dash, 9525))
    el.append(txpr(color))
    sub(el, "c:dLblPos", val=pos)
    for tag, v in (("showLegendKey", 0), ("showVal", 1), ("showCatName", 0), ("showSerName", 0),
                   ("showPercent", 0), ("showBubbleSize", 0)):
        sub(el, f"c:{tag}", val=v)
    el.append(_roundrect_ext())


def labels(ser, fmt, fill, color=WHITE, pos="outEnd", points=None, texts=None):
    """Data labels em pill (retângulo arredondado). ser = series._element.
    texts: texto fixo por ponto (evita formatação regional). points = {idx: dict(fill, color, border, dash, rich, delete, pos)}."""
    for old in ser.findall(qn("c:dLbls")):
        ser.remove(old)
    d = E("c:dLbls")
    pts = {i: {} for i in range(len(texts or []))}
    for i, o in (points or {}).items():
        pts.setdefault(i, {}).update(o)
    for i, t in enumerate(texts or []):
        pts[i].setdefault("rich", t)
    for idx, o in sorted(pts.items()):
        lb = sub(d, "c:dLbl"); sub(lb, "c:idx", val=idx)
        if o.get("delete"):
            sub(lb, "c:delete", val=1); continue
        _label_body(lb, fmt, o.get("fill", fill), o.get("color", color), o.get("pos", pos),
                    o.get("border"), o.get("dash", False), o.get("rich"))
    _label_body(d, fmt, fill, color, pos)
    ser.find(qn("c:cat")).addprevious(d)


def chart(slide, kind, box, cats, series, fmt="0.0"):
    """Gráfico nativo numa caixa (x, y, w, h). series = [(nome, valores), ...]."""
    cd = CategoryChartData(number_format=fmt)
    cd.categories = cats
    for name, vals in series:
        cd.add_series(name, vals)
    x, y, w, h = box
    gf = slide.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    return gf, gf.chart


def base_chart(ch, vmax, vmin=0, gap=60):
    """Visual padrão: fundo transparente, sem grade, eixo de valor oculto, eixo de categoria fino."""
    ch.font.name = FONT; ch.font.size = Pt(9); ch.font.color.rgb = rgb(FG)
    ch.has_legend = False
    ch.has_title = False
    cs = ch._chartSpace
    for old in cs.findall(qn("c:spPr")):
        cs.remove(old)
    sp = sppr(None, None)
    tx = cs.find(qn("c:txPr"))
    (tx.addprevious(sp) if tx is not None else cs.find(qn("c:chart")).addnext(sp))
    va = ch.value_axis
    va.maximum_scale = vmax; va.minimum_scale = vmin
    va.has_major_gridlines = False; va.visible = False
    ca = ch.category_axis
    ca.has_major_gridlines = False
    ca.format.line.color.rgb = rgb(AXIS); ca.format.line.width = Pt(0.75)
    ca.tick_labels.font.size = Pt(9); ca.tick_labels.font.name = FONT
    ca.tick_labels.font.color.rgb = rgb(FG2)
    ca.major_tick_mark = XL_TICK_MARK.NONE
    plot = ch.plots[0]
    plot.gap_width = gap
    plot.vary_by_categories = False


def plot_layout(ch, x, y, w, h):
    """Área de plotagem manual (frações 0–1 da caixa). Necessária para posicionar anotações com frame()."""
    pa = ch._chartSpace.find(qn("c:chart")).find(qn("c:plotArea"))
    old = pa.find(qn("c:layout"))
    if old is not None:
        pa.remove(old)
    lay = E("c:layout"); ml = sub(lay, "c:manualLayout")
    sub(ml, "c:layoutTarget", val="inner"); sub(ml, "c:xMode", val="edge"); sub(ml, "c:yMode", val="edge")
    for k, v in (("x", x), ("y", y), ("w", w), ("h", h)):
        sub(ml, f"c:{k}", val=v)
    pa.insert(0, lay)


def color_points(series, colors):
    for i, col in enumerate(colors):
        pt = series.points[i]
        paint(pt.format.fill, col)
        pt.format.line.fill.background()


def frame(gf):
    """(x, y, w, h) da caixa do gráfico em polegadas, para ancorar anotações nas barras."""
    k = 914400
    return gf.left / k, gf.top / k, gf.width / k, gf.height / k


def combo_line(ch, color, smin, smax, texts=None, points=None, fmt="0.0%"):
    """Move a 2ª série do barChart para uma linha suavizada no eixo secundário (sem marcador, pills no centro).
    Os 2 valAx ficam delete=0 e invisíveis: com delete=1 o PowerPoint ignora as escalas."""
    pa = ch._chartSpace.find(qn("c:chart")).find(qn("c:plotArea"))
    bar = pa.find(qn("c:barChart"))
    ser = bar.findall(qn("c:ser"))[1]
    bar.remove(ser)
    for t in ("c:invertIfNegative", "c:dLbls", "c:spPr", "c:marker", "c:smooth"):
        for e in ser.findall(qn(t)):
            ser.remove(e)
    sp = E("c:spPr"); ln = sub(sp, "a:ln", w=28575, cap="rnd"); solid(ln, color); sub(ln, "a:round")
    ser.find(qn("c:tx")).addnext(sp)
    mk = E("c:marker"); sub(mk, "c:symbol", val="none")
    sp.addnext(mk)
    sub(ser, "c:smooth", val=1)
    labels(ser, fmt, color, WHITE, pos="ctr", points=points, texts=texts)
    lc = E("c:lineChart"); sub(lc, "c:grouping", val="standard"); sub(lc, "c:varyColors", val=0)
    lc.append(ser); sub(lc, "c:marker", val=1)
    sub(lc, "c:smooth", val=1)
    sub(lc, "c:axId", val=50001); sub(lc, "c:axId", val=50002)
    bar.addnext(lc)
    va = ch.value_axis
    va.visible = True
    va.major_tick_mark = XL_TICK_MARK.NONE; va.minor_tick_mark = XL_TICK_MARK.NONE
    va.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    va.format.line.fill.background()
    last_ax = pa.findall(qn("c:valAx"))[-1]
    cat = E("c:catAx"); sub(cat, "c:axId", val=50001)
    sc = sub(cat, "c:scaling"); sub(sc, "c:orientation", val="minMax")
    sub(cat, "c:delete", val=1); sub(cat, "c:axPos", val="b")
    sub(cat, "c:majorTickMark", val="none"); sub(cat, "c:minorTickMark", val="none"); sub(cat, "c:tickLblPos", val="nextTo")
    sub(cat, "c:crossAx", val=50002); sub(cat, "c:crosses", val="autoZero")
    sub(cat, "c:auto", val=1); sub(cat, "c:lblAlgn", val="ctr"); sub(cat, "c:lblOffset", val=100); sub(cat, "c:noMultiLvlLbl", val=0)
    val = E("c:valAx"); sub(val, "c:axId", val=50002)
    sc = sub(val, "c:scaling"); sub(sc, "c:orientation", val="minMax")
    sub(sc, "c:max", val=smax); sub(sc, "c:min", val=smin)
    sub(val, "c:delete", val=0); sub(val, "c:axPos", val="r")
    sub(val, "c:numFmt", formatCode=fmt, sourceLinked=0)
    sub(val, "c:majorTickMark", val="none"); sub(val, "c:minorTickMark", val="none"); sub(val, "c:tickLblPos", val="none")
    vsp = sub(val, "c:spPr"); vl = sub(vsp, "a:ln"); sub(vl, "a:noFill")
    sub(val, "c:crossAx", val=50001); sub(val, "c:crosses", val="max"); sub(val, "c:crossBetween", val="between")
    last_ax.addnext(cat); cat.addnext(val)


def native_legend(ch, hide=()):
    """Legenda nativa no topo, fora da plotagem; hide = índices de série a omitir."""
    c = ch._chartSpace.find(qn("c:chart"))
    for old in c.findall(qn("c:legend")):
        c.remove(old)
    lg = E("c:legend"); sub(lg, "c:legendPos", val="t")
    for i in hide:
        le = sub(lg, "c:legendEntry"); sub(le, "c:idx", val=i); sub(le, "c:delete", val=1)
    sub(lg, "c:overlay", val=0)
    lg.append(txpr(FG2, 9, False))
    c.find(qn("c:plotArea")).addnext(lg)


def doughnut(slide, x, y, d, names, values, colors, center_label=None, hole=55):
    """Rosca nativa (12h, sentido horário, borda branca 2pt). Legenda rica fica ao lado, desenhada."""
    cd = CategoryChartData(number_format="0.0")
    cd.categories = names
    cd.add_series("s", values)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(d), Inches(d), cd)
    ch = gf.chart
    ch.has_legend = False; ch.has_title = False
    dn = ch._chartSpace.find(qn("c:chart")).find(qn("c:plotArea")).find(qn("c:doughnutChart"))
    for tag, val in (("c:firstSliceAng", 0), ("c:holeSize", hole)):
        el = dn.find(qn(tag))
        if el is None:
            el = sub(dn, tag)
        el.set("val", str(val))
    cs = ch._chartSpace
    for old in cs.findall(qn("c:spPr")):
        cs.remove(old)
    cs.find(qn("c:chart")).addnext(sppr(None, None))
    plot_layout(ch, 0.02, 0.02, 0.96, 0.96)
    sr = ch.plots[0].series[0]
    for i, col in enumerate(colors):
        pt = sr.points[i]
        paint(pt.format.fill, col)
        pt.format.line.color.rgb = rgb(WHITE); pt.format.line.width = Pt(2)
    if center_label:
        text(slide, x, y + d / 2 - 0.16, d, 0.32, [[(center_label, {"bold": True, "color": FOCUS, "size": 14})]],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    return gf, ch


# =====================================================================
# Componentes extras: mapa por região, linha suavizada, colchete de delta
# =====================================================================
_GEO = None


def geo():
    """Países (Natural Earth 1:110m, simplificado): {ISO3: {name, continent, region_wb, subregion, rings}}."""
    global _GEO
    if _GEO is None:
        _GEO = json.loads((LIB / "geo" / "countries_110m.json").read_text())
    return _GEO


def region_map(slide, box, groups, colors, by="iso", default=None, lat=(-56, 80), lon=(-170, 180),
               keep_aspect=True, border=None):
    """Mapa-múndi com países agrupados em regiões, desenhado como freeforms editáveis.
    groups: {"North America": ["USA", "CAN"], …} (by="iso") ou {"Europe": ["Europe"]} (by="continent" |
    "region_wb" | "subregion"). colors: {"North America": FOCUS, …}. default: cor dos países fora dos grupos
    (None = não desenha). keep_aspect: encolhe e centraliza para não distorcer; False preenche a caixa
    (estica até ~30% sem incomodar). border=None: sem fronteira entre países (só a cor separa
    as regiões); WHITE mostra cada país. Devolve (px, py): lon/lat → polegadas, para ancorar rótulos e linhas guia.
    Rótulos: fora do mapa (faixa de cima/baixo) ou sobre o oceano, ligados por line(…, AXIS, 0.75, dash=False)."""
    x, y, w, h = box
    sx, sy = lon[1] - lon[0], lat[1] - lat[0]
    if keep_aspect:
        mw = min(w, h * sx / sy / 0.92)
        mh = mw * sy * 0.92 / sx
        x, y, w, h = x + (w - mw) / 2, y + (h - mh) / 2, mw, mh
    px = lambda lo: x + (lo - lon[0]) / sx * w
    py = lambda la: y + (lat[1] - la) / sy * h
    member = {}
    for g, keys in groups.items():
        for iso, c in geo().items():
            if (iso if by == "iso" else c.get(by)) in keys:
                member[iso] = g
    for iso, c in geo().items():
        col = colors.get(member[iso]) if iso in member else default
        if not col or iso in ("ATA", "GRL") and iso not in member:
            continue
        for ring in c["rings"]:
            pts = [(px(min(max(lo, lon[0]), lon[1])), py(min(max(la, lat[0]), lat[1]))) for lo, la in ring]
            poly(slide, pts, col, line_color=border or col)
    return px, py


def smooth_line(ch):
    """Suaviza a linha nos DOIS níveis (série e lineChart); o <c:smooth val=0> do lineChart sobrepõe o da série."""
    for lc in ch._chartSpace.iter(qn("c:lineChart")):
        for sm in lc.findall(qn("c:smooth")):
            lc.remove(sm)
        lc.find(qn("c:axId")).addprevious(E("c:smooth", val=1))
        for ser in lc.findall(qn("c:ser")):
            for sm in ser.findall(qn("c:smooth")):
                ser.remove(sm)
            ser.append(E("c:smooth", val=1))


def delta_bracket(slide, x, y_from, y_to, label, sub=None, color=ACCENT, tick=0.07):
    """Colchete vertical curto (ex.: à direita do último ponto) mostrando a distância entre dois níveis,
    com o delta ao lado. Evita linha de referência atravessando o gráfico."""
    line(slide, x, y_from, x, y_to, color, 1.25, dash=False)
    line(slide, x - tick, y_from, x, y_from, color, 1.25, dash=False)
    line(slide, x - tick, y_to, x, y_to, color, 1.25, dash=False)
    runs = [[(label, {"bold": True, "color": color, "size": 10})]]
    if sub:
        runs.append([(sub, {"color": color, "size": 8})])
    text(slide, x + 0.08, (y_from + y_to) / 2 - 0.2, 1.0, 0.4, runs, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def fix_axes(prs):
    """python-pptx grava valAx sem <c:orientation> e <c:delete/> sem val: o PowerPoint descarta a escala
    (barras todas da mesma altura). Rodar sempre antes de salvar (save() já faz)."""
    for sl in prs.slides:
        for shp in sl.shapes:
            if not getattr(shp, "has_chart", False):
                continue
            cs = shp.chart._chartSpace
            for sc in cs.iter(qn("c:scaling")):
                if sc.find(qn("c:orientation")) is None:
                    lb = sc.find(qn("c:logBase"))
                    o = E("c:orientation", val="minMax")
                    (lb.addnext(o) if lb is not None else sc.insert(0, o))
            for d in cs.iter(qn("c:delete")):
                if d.get("val") is None:
                    d.set("val", "1")


def save(prs, path):
    fix_axes(prs)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    print("saved", path)
