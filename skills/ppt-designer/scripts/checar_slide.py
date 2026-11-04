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
MIN_NUMEROS = 20
MAX_DADOS = 60
MAX_PALAVRAS = 150
ALVO_PALAVRAS = 130


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
            if not a[4] or not b[4] or a[4] == b[4]:
                continue  # mesmo texto no mesmo lugar é do mestre
            if max(len(a[4]), len(b[4])) <= 2 and not (re.search(r"\d", a[4]) or re.search(r"\d", b[4])):
                continue  # fragmento de letra é ruído de kerning do PDF; número curto colidindo é real
            if inter(a, b) / min(area(a), area(b)) > 0.20:
                out.append(f'"{a[4]}" × "{b[4]}" em ({a[0]:.1f}, {a[1]:.1f}) pol')
    return out


def numeros(words):
    return sum(len(re.findall(r"[0-9][0-9.,]*", w[4])) for w in words)


def palavras(words):
    """Palavras no slide inteiro, sem número e sem ano, medidas como nos decks de referência."""
    return sum(1 for w in words if re.search(r"[A-Za-zÀ-ÿ]{2,}", w[4]) and not re.fullmatch(r"(FY)?(19|20)?\d\d[A-Z*]?|[1-4]Q\d\d[A-Z*]?", w[4].strip("(),;:")))


def dados(words, limite_y=7.0):
    """Números que são dado: sem ano, FY, trimestre, número de página e rodapé."""
    n = 0
    for w in words:
        t = w[4].strip("(),;:")
        if w[1] > limite_y or re.fullmatch(r"(FY)?(19|20)\d\d[A-Z*]?|FY\d\d[A-Z*]?|[1-4]Q\d\d[A-Z*]?|FY\d{2,4}[–-](FY)?\d{2,4}|(19|20)\d\d[–-](19|20)?\d\d", t):
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
        if re.search(r"(?<![A-Za-z-])\d", texto):  # KC-390 ou F35 são nomes, não dados
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

    # Linha divisória fina: "em nada, muita cara de AI". Eixo de gráfico nativo e colchete de 3 lados não caem aqui.
    fios = 0
    for sh in shapes:
        larg, alt = sh.width / IN, sh.height / IN
        if larg < 1.0 or alt > 0.03 or sh.top / IN > grid.get("content_bottom", 6.9) or sh.top / IN < 1.1:
            continue
        cx, cy = (sh.left + sh.width / 2) / IN, (sh.top + sh.height / 2) / IN
        if any(g[0] <= cx <= g[2] and g[1] <= cy <= g[3] for g in caixas_g):
            continue
        fios += 1
    if fios:
        err.append(f"{fios} linhas divisórias finas: tire. Separe com espaço ou cor de fundo.")

    # Profundidade: slide plano é reprovado como "sem sal". Painel = forma preenchida grande; sombra dura ou dobra = duas sobrepostas.
    grandes = [sh for sh in shapes if sh.shape_type in (1, 5) and sh.width / IN > 2 and sh.height / IN > 1.5]
    cunha_grande = any(sh.shape_type == 5 and sh.height / IN > 1.5 for sh in shapes)
    if len(grandes) < 2 and not cunha_grande:
        err.append("Slide sem profundidade: faltam painéis com volume (`painel_volume`, `ponte_volume`) ou dobra.")

    # Dado desenhado em grade de quadrados conta como gráfico: fugir do limite com formas não muda o que o leitor vê.
    def _quadrado(sh):
        try:
            return sh.shape_type == 1 and sh.auto_shape_type in (1, 5) and sh.width / IN < 1 and sh.height / IN < 1
        except (ValueError, NotImplementedError):
            return False
    tamanhos = {}
    for sh in shapes:
        if _quadrado(sh):
            tamanhos.setdefault((round(sh.width / IN, 2), round(sh.height / IN, 2)), []).append(sh)
    # Grade de verdade tem ao menos 3 linhas e 3 colunas; só repetir o tamanho pega chips de uma timeline.
    grades = sum(1 for g in tamanhos.values() if len(g) >= 9 and len({round(sh.left / IN, 1) for sh in g}) >= 3
                 and len({round(sh.top / IN, 1) for sh in g}) >= 3)
    if len(graficos) + grades > 3:
        err.append(f"{len(graficos)} gráficos e {grades} grade(s) de formas no slide (máximo 3). O quarto quadrante é outra coisa: ilustração, timeline, citação, diagrama.")

    # Cores: todo gráfico divide a cor principal com os outros. Rótulos e eixos não contam, só o preenchimento das séries.
    def _cores(ch):
        ns = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        raiz, out = ch._chartSpace, set()
        for caminho in ("//c:ser/c:spPr/a:solidFill/a:srgbClr/@val", "//c:ser/c:spPr/a:ln/a:solidFill/a:srgbClr/@val", "//c:ser/c:dPt/c:spPr/a:solidFill/a:srgbClr/@val"):
            out |= {v.upper() for v in raiz.xpath(caminho)}
        return out - {"FFFFFF", "D62F2F"}
    paletas = [_cores(g.chart) for g in graficos]
    paletas = [p for p in paletas if p]
    def _saturacao(h):
        r, g_, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return max(r, g_, b) - min(r, g_, b)
    if len(paletas) >= 2:
        for i, p in enumerate(paletas):
            outros = set().union(*(q for j, q in enumerate(paletas) if j != i))
            if not (p & outros) and max(_saturacao(h) for h in p) < 40:
                err.append(f"Gráfico {i + 1} só em cinza ({', '.join(sorted(p))}), e os outros em cor: use a mesma cor principal em todos.")
            elif not (p & outros):
                av.append(f"Gráfico {i + 1} não divide nenhuma cor com os outros ({', '.join(sorted(p))}).")

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
        err.append(f"Só {n} dados no slide, fora anos e rodapé (mínimo ~{MIN_NUMEROS}): tende a sair sem sal. Se o roteiro não tem mais, avise o usuário na entrega.")
    if n > MAX_DADOS:
        err.append(f"{n} dados no slide (máximo ~{MAX_DADOS}). O dono reprovou como crowded: corte provas e rótulos, sem reduzir a fonte.")
    pal = palavras(words)
    if pal > MAX_PALAVRAS:
        err.append(f"{pal} palavras no slide (máximo ~{MAX_PALAVRAS}; os melhores têm 85 a 130). Corte texto: itálicos, anotações, legendas longas.")
    elif pal > ALVO_PALAVRAS:
        av.append(f"{pal} palavras no slide; os melhores têm 85 a 130.")
    if not graficos:
        av.append("Nenhum gráfico nativo: confira se o slide prova com dado.")
    if "Sources: Company Data, Group Calculations." not in " ".join(w[4] for w in words).replace("  ", " "):
        av.append("Rodapé diferente de `Sources: Company Data, Group Calculations.`")

    print(f"{Path(pptx).name}: {pal} palavras, {n} dados ({numeros(words)} números com anos), {len(graficos)} gráficos nativos, {len(chips)} chips fora de gráfico")
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
