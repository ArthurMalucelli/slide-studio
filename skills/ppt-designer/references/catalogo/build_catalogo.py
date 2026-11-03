"""Gera os .md do catálogo a partir de dados/*.json. Uso: python3 build_catalogo.py"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
FAM = {"profundidade": ("Profundidade", "Sólidos, paredes, feixes, fitas, camadas e luz."),
       "mapas": ("Mapas", "Todos os tratamentos de mapa encontrados."),
       "elementos-navegacao": ("Navegação", "Trackers, agendas e localizadores."),
       "elementos-anotacao": ("Anotação", "Marcas que fazem o gráfico argumentar."),
       "elementos-evidencia": ("Evidência", "Prova própria: pesquisa, campo, código, notícia."),
       "elementos-citacao": ("Citação", "Citações, entrevistas e seus carimbos."),
       "elementos-dado": ("Dispositivos de dado", "Vereditos, fórmulas, notas, matrizes de números."),
       "elementos-estrutura": ("Estrutura", "Árvores, ledgers e sequências."),
       "elementos-identidade-capas": ("Identidade, capas e divisores", "Sistemas de cor, capas, fechamentos e outros."),
       "diagramas": ("Diagramas e composições", "Fluxos, timelines, organogramas, mosaicos, tabelas, composições e estilos de gráfico.")}
ELEM = {"navigation": "elementos-navegacao", "annotation": "elementos-anotacao", "evidence": "elementos-evidencia", "quote": "elementos-citacao",
        "data-device": "elementos-dado", "structure": "elementos-estrutura", "identity": "elementos-identidade-capas", "cover-divider": "elementos-identidade-capas", "other": "elementos-identidade-capas"}


def load(n):
    p = H / "dados" / n
    return json.loads(p.read_text()) if p.exists() else []


def rows():
    for x in load("profundidade.json"):
        yield "profundidade", {"nome": x["technique"], "cat": "", "deck": x["deck"], "pages": x["pages"], "crop": x.get("crop") and "p_" + x["crop"], "q": x["quality"],
                               "faz": "", "como": x["construction"], "uso": x.get("use_for", ""), "asset": x.get("is_image", False), "img": x.get("is_image", False)}
    for src, pre in (("elementos.json", "e_"), ("mapas.json", ""), ("diagramas.json", "")):
        for x in load(src):
            fam = "mapas" if src == "mapas.json" else "diagramas" if src == "diagramas.json" else ELEM.get(x["category"], "elementos-identidade-capas")
            yield fam, {"nome": x["element"], "cat": x.get("category", ""), "deck": x["deck"], "pages": x["pages"], "crop": x.get("crop") and pre + x["crop"], "q": x["quality"],
                        "faz": x.get("what_it_does", ""), "como": x.get("how_built", ""), "uso": x.get("use_for", ""), "asset": x.get("needs_real_asset", False), "img": False}


def main():
    pecas = json.loads((H / "dados" / "pecas.json").read_text()) if (H / "dados" / "pecas.json").exists() else {}
    by = {}
    have = {p.name for p in (H / "crops").glob("*")}
    for fam, r in rows():
        by.setdefault(fam, []).append(r)
    for fam, (t, d) in FAM.items():
        rs = sorted(by.get(fam, []), key=lambda r: (-r["q"], r["deck"]))
        if not rs:
            continue
        out = [f"# {t} ({len(rs)})", "", d, "", "Ordem: qualidade, depois deck. ★★★ é a referência a copiar. Copie a técnica, nunca o conteúdo nem as cores do deck de origem.", ""]
        for r in rs:
            pg = ", ".join(str(p) for p in r["pages"]) if isinstance(r["pages"], list) else str(r["pages"])
            out.append(f"## {'★' * r['q']} {r['nome']}")
            out.append(f"- **Origem:** {r['deck']}, p. {pg}" + (f" · **Tipo:** {r['cat']}" if r["cat"] and fam == "diagramas" else ""))
            jpg = (r["crop"] or "").rsplit(".", 1)[0] + ".jpg"
            if jpg in have:
                out.append(f"- **Recorte:** `crops/{jpg}`")
            pc = pecas.get(r["nome"])
            if pc:
                out.append(f"- **Peça pronta:** `{pc}`")
            if r["faz"]:
                out.append(f"- **Função:** {r['faz']}")
            if r["uso"]:
                out.append(f"- **Serve para:** {r['uso']}")
            if r["asset"]:
                out.append("- **Precisa de material real:** peça ao usuário; nunca invente." if not r["img"] else "- **Na origem é imagem colada:** refaça em formas ou use material real.")
            out.append(f"- **Como montar:** {r['como']}")
            out.append("")
        (H / f"{fam}.md").write_text("\n".join(out))
        print(fam, len(rs))


if __name__ == "__main__":
    main()
