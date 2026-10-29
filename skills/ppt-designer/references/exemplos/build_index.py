"""Regera INDEX.md, por-proposito/ e por-visual/ a partir de catalog/*.json. Uso: python3 build_index.py"""
import collections, glob, json, os, re, shutil, unicodedata
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
rows = [x for f in sorted(glob.glob("catalog/*.json")) for x in json.load(open(f))]
for x in rows:
    if isinstance(x["visual"], str):
        x["visual"] = [x["visual"]]
slugdeck = lambda f: re.sub(r"[^A-Za-z0-9-]", "", unicodedata.normalize("NFKD", f).encode("ascii", "ignore").decode())
pdfs = {slugdeck(Path(f).stem): Path(f).name for f in glob.glob("pdf/*.pdf")}

PURP = [("recomendacao-exec-summary", "Recomendação / executive summary"), ("tese-pilares-divisor", "Tese em pilares / divisor de seção"),
        ("business-overview", "Business overview (at a glance / in a nutshell)"), ("historico-empresa", "Histórico da empresa"),
        ("industry-overview", "Industry overview"), ("mercado-tam-demanda", "Mercado / TAM e demanda"),
        ("posicionamento-competitivo", "Posicionamento competitivo"), ("modelo-negocio-unit-economics", "Modelo de negócio / unit economics"),
        ("kpis-operacionais", "KPIs operacionais"), ("financials-historicos", "Financials históricos"),
        ("premissas-projecoes", "Premissas e projeções"), ("valuation-dcf", "Valuation: DCF"), ("valuation-multiplos", "Valuation: múltiplos"),
        ("football-field", "Football field"), ("sensibilidade", "Sensibilidade"), ("cenarios", "Cenários bear/base/bull"),
        ("catalisadores", "Catalisadores"), ("riscos", "Riscos"), ("esg", "ESG"),
        ("management-governanca-estrutura", "Management, governança e estrutura societária"), ("pesquisa-primaria", "Pesquisa primária"),
        ("recap", "Recap / fechamento"), ("capa", "Capa"), ("apendice", "Apêndice")]
WHEN = {
    "colunas": "evolução de uma métrica no tempo", "colunas-empilhadas": "evolução + composição",
    "barra-100": "composição/mix comparando grupos", "barras-horizontais": "ranking ou rótulos longos",
    "comps-barras": "empresa-foco vs pares numa métrica", "colunas+linha": "nível (colunas) + taxa/margem (linha)",
    "linha": "tendência contínua, várias séries", "area": "volume acumulado / participação no tempo",
    "scatter-bolhas": "duas métricas cruzadas (ex.: crescimento × margem, múltiplo × ROE)",
    "bridge-cascata": "decompor a variação entre dois totais", "football-field": "faixas de valor por método vs preço atual",
    "heatmap-sensibilidade": "preço-alvo em duas premissas (WACC × g)", "matriz-riscos": "riscos por probabilidade × impacto",
    "donut": "composição de um total (≤5 fatias)", "tabela": "muitas métricas exatas lado a lado",
    "timeline": "eventos, catalisadores ou histórico datados", "mapa": "distribuição geográfica, presença de ativos",
    "lineup-imagens": "produtos, marcas, frota: qualitativo com dado curto", "icones+dado-curto": "visão geral com 3–6 fatos curtos",
    "kpi-numeros-grandes": "poucos números-chave em destaque (só se o deck permitir)", "pilares": "tese em 2–4 razões",
    "organograma": "estrutura societária, holding, management", "funil-piramide": "TAM→SAM→SOM, segmentação",
    "fluxo-processo": "cadeia de valor, modelo de negócio, passo a passo", "flywheel-ciclo": "efeito de rede / ciclo que se reforça",
    "citacao-foto": "pesquisa primária: entrevista com foto e citação", "screenshot-produto": "mostrar o produto/app real",
    "3d-isometrico": "ilustração de escala/posicionamento", "texto-bullets": "evitar; só como exemplo do propósito",
    "foto-capa": "capa e divisores"}
names = dict(PURP)


def vkey(v):
    v = v.lower().strip()
    if v in WHEN or v.startswith("outro:"):
        return v
    return "outro:" + v


bypur, byvis = collections.defaultdict(list), collections.defaultdict(list)
for x in rows:
    bypur[x["purpose"]].append(x)
    for v in x["visual"]:
        byvis[vkey(v)].append(x)
for k in [k for k in byvis if k.startswith("outro:") and len(byvis[k]) < 3]:
    byvis["outro (variados)"] += byvis.pop(k)


def ranked(xs):
    """Qualidade desc; dentro da mesma nota, alterna decks (round-robin) para não repetir o mesmo deck no topo."""
    out = []
    for q in (3, 2, 1):
        per = collections.OrderedDict()
        for x in sorted([x for x in xs if x["quality"] == q], key=lambda x: (x["deck"], x["page"])):
            per.setdefault(x["deck"], []).append(x)
        while per:
            for d in list(per):
                out.append(per[d].pop(0))
                if not per[d]:
                    del per[d]
    return out


P = lambda x: f'prints/{x["deck"]}_p{x["page"]:03d}.jpg'
line = lambda x: (f'- `../{P(x)}` ({"★" * x["quality"]}) "{x["message"]}" · visual: {", ".join(x["visual"])} · '
                  f'propósito: {x["purpose"]} · truque: {x.get("layout_trick", "")}')
slug = lambda s: re.sub(r"[^a-z0-9+-]+", "-", s.lower()).strip("-")
for d in ("por-proposito", "por-visual"):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
porder = [p for p, _ in PURP if p in bypur] + sorted(k for k in bypur if k not in names)
for p in porder:
    xs = ranked(bypur[p])
    Path(f"por-proposito/{slug(p)}.md").write_text("\n".join(
        [f"# Propósito: {names.get(p, p)} ({len(xs)} slides)", "",
         "Ordenado por qualidade, alternando decks. Abra 2–4 prints ★★★/★★ antes de desenhar; copie o truque, não o conteúdo.", ""]
        + [line(x) for x in xs]) + "\n")
vorder = [v for v in WHEN if v in byvis] + sorted(k for k in byvis if k not in WHEN)
for v in vorder:
    xs = ranked(byvis[v])
    Path(f"por-visual/{slug(v)}.md").write_text("\n".join(
        [f"# Padrão visual: {v} ({len(xs)} slides)", ""] + ([f"Quando usar: {WHEN[v]}.", ""] if v in WHEN else [])
        + [line(x) for x in xs]) + "\n")
top = lambda xs: ", ".join(f'`{x["deck"]}_p{x["page"]:03d}`' for x in ranked(xs)[:3])
q = collections.Counter(x["quality"] for x in rows)
out = ["# Catálogo de referência: 21 decks de competição de equity research", "",
       f"{len(rows)} slides catalogados por **propósito** (o que o slide faz no deck) e por **padrão visual** (como ele mostra).",
       f"★★★ = referência a copiar ({q[3]} slides, ~10% de cada deck) · ★★ = bom ({q[2]}) · ★ = exemplo do propósito ({q[1]}).", "",
       "## Como usar (designer)", "",
       "1. Identifique o propósito do slide que vai montar e abra `por-proposito/<propósito>.md` (mensagem, visual e truque de cada slide, os melhores primeiro e alternando decks).",
       "2. Abra 2–4 prints do topo (`prints/<Deck>_pNNN.jpg`). Se já tiver um visual em mente, abra também `por-visual/<padrão>.md`.",
       "3. Copie o *truque de layout*, nunca o conteúdo nem as cores do deck de origem. PDFs inteiros (`pdf/`) só se precisar do contexto.", "",
       "## Por propósito", "", "| Propósito | Slides | Arquivo | Melhores exemplos |", "|---|---|---|---|"]
out += [f"| {names.get(p, p)} | {len(bypur[p])} | `por-proposito/{slug(p)}.md` | {top(bypur[p])} |" for p in porder]
out += ["", "## Por padrão visual", "", "| Padrão | Quando usar | Slides | Arquivo | Melhores exemplos |", "|---|---|---|---|---|"]
out += [f"| {v} | {WHEN.get(v, '')} | {len(byvis[v])} | `por-visual/{slug(v)}.md` | {top(byvis[v])} |" for v in vorder]
out += ["", "## Decks", "", "| Deck (prefixo dos prints) | PDF |", "|---|---|"] + [f"| {k} | `pdf/{v}` |" for k, v in sorted(pdfs.items())]
out += ["", "Para regerar este índice depois de editar `catalog/*.json`: `python3 build_index.py`."]
Path("INDEX.md").write_text("\n".join(out) + "\n")
print(len(rows), "slides;", dict(q), "; visuais:", {v: len(byvis[v]) for v in vorder})
