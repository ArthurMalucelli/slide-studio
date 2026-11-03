#!/usr/bin/env python3
"""Verificador mecânico: acha no .pptx e no PDF exportado o que o dono do deck já reprovou.

Uso:  checar_slide.py slide.pptx [slide.pdf] [--profile _master/profile.json]
      checar_slide.py --so-pdf deck.pdf <página>     (só colisão e contagem; serve para calibrar no gabarito)

ERRO: o slide não está pronto. AVISO: olhe e decida. Sai com código 1 se houver ERRO.
Passar aqui não quer dizer que o slide está bom: só que não tem esses defeitos.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

IN = 914400
LIMITE_CHIPS = 4          # chips com número fora de gráfico
MIN_NUMEROS = 15
MAX_DADOS = 80


def palavras_pdf(pdf, pagina=1):
    """Palavras e linhas do PDF, em polegadas. Cada palavra: (x0, y0, x1, y1, texto)."""
    with tempfile.NamedTemporaryFile(suffix=".html") as t:
        r = subprocess.run(["pdftotext", "-bbox-layout", "-f", str(pagina), "-l", str(pagina), str(pdf), t.name],
                           capture_output=True)
        if r.returncode:
            raise SystemExit(f"pdftotext falhou em {pdf} p.{pagina}: {r.stderr.decode(errors='ignore')[:200]}")
        html = re.sub(r'xmlns="[^"]+"', "", Path(t.name).read_text(errors="ignore"))
    root = ET.fromstring(html)
    conv = lambda e, k: float(e.attrib[k]) / 72
    box = lambda e: (conv(e, "xMin"), conv(e, "yMin"), conv(e, "xMax"), conv(e, "yMax"))
    words, lines = [], []
    for ln in root.iter("line"):
        toks = []
        for w in ln.iter("word"):
            words.append((*box(w), (w.text or "").strip()))
            toks.append(words[-1][4])
        lines.append((*box(ln), toks))
    return words, lines


def linhas_do_texto(texto, rect, lines):
    """Em quantas linhas o PDF quebrou este texto. None se não achar o começo dele dentro da caixa."""
    toks = texto.split()
    for ln in lines:
        if ln[4] and ln[4][0] == toks[0] and rect[0] - .15 <= ln[0] <= rect[2] and rect[1] - .25 <= ln[1] <= rect[3] + .1:
            n, i = 1, len(ln[4])
            j = lines.index(ln) + 1
            while i < len(toks) and j < len(lines) and lines[j][4][:1] == toks[i:i + 1]:
                i += len(lines[j][4]); n += 1; j += 1
            return n
    return None


def inter(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def area(a):
    return max(1e-6, (a[2] - a[0]) * (a[3] - a[1]))


def colisoes(words):
    """Palavra sobre palavra. Fontes de sobreposição real, e não só caixas vizinhas: exige 20% da menor."""
    out = []
    for i, a in enumerate(words):
        for b in words[i + 1:]:
            if not a[4] or not b[4] or a[4] == b[4] or max(len(a[4]), len(b[4])) <= 2:
                continue  # mesmo texto no mesmo lugar é do mestre; fragmento de letra é ruído de kerning do PDF
            if inter(a, b) / min(area(a), area(b)) > 0.20:
                out.append(f'"{a[4]}" × "{b[4]}" em ({a[0]:.1f}, {a[1]:.1f}) pol')
    return out


def numeros(words):
    return sum(len(re.findall(r"[0-9][0-9.,]*", w[4])) for w in words)


def dados(words, limite_y=7.0):
    """Números que são dado: sem ano, FY, trimestre, número de página e rodapé."""
    n = 0
    for w in words:
        t = w[4].strip("(),;:")
        if w[1] > limite_y or re.fullmatch(r"(FY)?(19|20)\d\d[A-Z*]?|FY\d\d[A-Z*]?|[1-4]Q\d\d[A-Z*]?|(FY)?\d{2,4}[–-]\d{2,4}", t):
            continue
        n += len(re.findall(r"[0-9][0-9.,]*", t))
    return n


def _shapes(container):
    for sh in container.shapes:
        if sh.shape_type == 6:  # grupo
            yield from _shapes(sh)
        else:
            yield sh


def _rect(sh):
    return (sh.left / IN, sh.top / IN, (sh.left + sh.width) / IN, (sh.top + sh.height) / IN)


def _maior_fonte(sh):
    sizes = [r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs if r.font.size]
    return max(sizes) if sizes else None


def checar(pptx, pdf, profile):
    from pptx import Presentation

    prs = Presentation(pptx)
    s = prs.slides[0]
    words, lines = palavras_pdf(pdf)
    err, av = [], []
    shapes = list(_shapes(s))
    graficos = [sh for sh in s.shapes if getattr(sh, "has_chart", False) and sh.has_chart]
    caixas_g = [_rect(g) for g in graficos]

    for c in colisoes(words):
        err.append("Texto sobre texto: " + c)

    # Título: uma linha, sem bater no logo, no tamanho do mestre, sem número
    grid = (profile or {}).get("grid", {})
    tit = s.shapes.title
    if tit is None and grid.get("title"):
        tit = next((p for p in s.placeholders if p.placeholder_format.idx == grid["title"]["idx"]), None)
    if tit is not None and tit.has_text_frame:
        texto = tit.text_frame.text.strip()
        if len(texto) > 55:
            err.append(f"Título com {len(texto)} caracteres (máximo ~55): encurte no roteiro, não reduza a fonte.")
        if re.search(r"\d", texto):
            err.append(f'Número no título: "{texto}".')
        fonte, mestre = _maior_fonte(tit), grid.get("title", {}).get("font_pt")
        if fonte and mestre and fonte < mestre - 0.5:
            err.append(f"Título reduzido para {fonte:g}pt; o mestre usa {mestre:g}pt. Encurte o texto.")
        if texto and (linhas_do_texto(texto, _rect(tit), lines) or 1) > 1:
            err.append("Título em mais de uma linha.")

    # Zonas proibidas e logos
    zonas = []
    for z in grid.get("forbidden", []):
        x, y, w, h = z
        if x <= 0.01 and h > 5:  # faixa lateral: o profile inferido costuma errar a largura
            continue
        zonas.append((x, y, x + w, y + h))
    for src in (s.slide_layout, s.slide_layout.slide_master):
        for sh in src.shapes:
            if sh.shape_type == 13 and sh.width / IN < 3 and (sh.top + sh.height) / IN < 1.2 and sh.left / IN > 8:
                zonas.append(_rect(sh))
    for z in zonas:
        for w in words:
            if w[4] and w[1] < grid.get("content_bottom", 99) and inter(z, w) / area(w) > 0.05:
                err.append(f'Texto sobre zona proibida ou logo: "{w[4]}" em ({w[0]:.1f}, {w[1]:.1f}) pol')
                break

    # Cabeçalho de painel em mais de uma linha (fonte ≥ 13pt, fora de título e subtítulo)
    for sh in shapes:
        if not sh.has_text_frame or not sh.text_frame.text.strip() or sh == tit:
            continue
        idx = sh.placeholder_format.idx if sh.is_placeholder else None
        if idx is not None and idx == grid.get("subtitle", {}).get("idx"):
            continue
        fonte = _maior_fonte(sh)
        if fonte and fonte >= 13.5 and len(sh.text_frame.paragraphs) == 1:
            if (linhas_do_texto(sh.text_frame.text.strip(), _rect(sh), lines) or 1) > 1:
                err.append(f'Cabeçalho em mais de uma linha: "{sh.text_frame.text[:60]}". Encurte.')

    # Chips com número fora de gráfico: é o que mais polui
    chips = []
    for sh in shapes:
        if sh.shape_type != 1 or not sh.has_text_frame:
            continue
        t = sh.text_frame.text.strip()
        if not t or not re.search(r"\d", t) or len(t) > 14 or sh.height / IN > 0.42:
            continue
        if sh.fill.type != 1:  # sem preenchimento sólido é texto, não chip
            continue
        cx, cy = (sh.left + sh.width / 2) / IN, (sh.top + sh.height / 2) / IN
        if not any(g[0] <= cx <= g[2] and g[1] <= cy <= g[3] for g in caixas_g):
            chips.append(t)
    if len(chips) > LIMITE_CHIPS:
        err.append(f"{len(chips)} chips com número fora de gráfico (máx. {LIMITE_CHIPS}): {', '.join(chips[:8])}… "
                   "Fora de gráfico, número é texto em negrito.")

    # Gráficos: duas barras, dois pontos, marcador
    for g in graficos:
        ch = g.chart
        try:
            cats = list(ch.plots[0].categories)
        except Exception:
            continue
        xml = ch._chartSpace.xml
        linha = "<c:lineChart" in xml
        barra = "<c:barChart" in xml
        if barra and not linha and len(cats) <= 2 and len(list(ch.plots[0].series)) <= 2:
            err.append(f"Gráfico de barras com {len(cats)} categorias: {list(cats)}.")
        if linha and len(cats) <= 2:
            err.append(f"Gráfico de linha com {len(cats)} pontos: {list(cats)}.")
        if linha and re.search(r'<c:marker>\s*<c:symbol val="(?!none)', xml):
            err.append("Linha com marcador nos pontos.")

    # Densidade e exibits
    n = dados(words, grid.get("content_bottom", 7.0))
    if n < MIN_NUMEROS:
        err.append(f"Só {n} dados no slide, fora anos e rodapé (mínimo ~{MIN_NUMEROS}). Se o roteiro não tem mais, avise o usuário na entrega.")
    if n > MAX_DADOS:
        err.append(f"{n} dados no slide (máximo ~{MAX_DADOS}). O dono reprovou como crowded: corte provas, sem reduzir a fonte.")
    if len(graficos) < 2:
        av.append(f"{len(graficos)} gráfico nativo. O gabarito quase sempre prova com 2 ou mais exibits; mapa desenhado conta.")
    if "Sources: Company Data, Group Calculations." not in " ".join(w[4] for w in words).replace("  ", " "):
        av.append("Rodapé diferente de `Sources: Company Data, Group Calculations.`")

    print(f"{Path(pptx).name}: {n} dados ({numeros(words)} números com anos), {len(graficos)} gráficos nativos, {len(chips)} chips fora de gráfico")
    for e in err:
        print("  ERRO  ", e)
    for a in av:
        print("  AVISO ", a)
    if not err:
        print("  Nenhum defeito mecânico. Isso não quer dizer que o slide está bom.")
    return 1 if err else 0


def main():
    a = sys.argv[1:]
    if a and a[0] == "--so-pdf":
        words, _ = palavras_pdf(a[1], int(a[2]))
        c = colisoes(words)
        print(f"{Path(a[1]).name} p.{a[2]}: {numeros(words)} números, {len(c)} colisões")
        for x in c[:10]:
            print("  ", x)
        return 0
    prof = None
    if "--profile" in a:
        i = a.index("--profile")
        prof = json.loads(Path(a[i + 1]).read_text())
        del a[i:i + 2]
    if not a:
        raise SystemExit(__doc__)
    pptx = a[0]
    pdf = a[1] if len(a) > 1 else str(Path(pptx).with_suffix(".pdf"))
    if not Path(pdf).exists():
        raise SystemExit(f"Falta o PDF exportado: {pdf}")
    return checar(pptx, pdf, prof)


if __name__ == "__main__":
    sys.exit(main())
