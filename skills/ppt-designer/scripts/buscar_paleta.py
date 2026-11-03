#!/usr/bin/env python3
"""Busca paletas no Color Hunt e as traduz para os papéis de cor do deck.

Uso:
  buscar_paleta.py navy                 lista as melhores da tag, com o bloco para deck_prefs.json
  buscar_paleta.py green --limite 3     tags em colorhunt.co/palettes (navy, teal, green, purple, blue...)
  buscar_paleta.py --hex 1A365D 015A9C 60C1E5 A1E0EF     traduz uma paleta que o usuário mandou

O site não tem API pública: o script lê o mesmo feed que a página usa e faz uma única chamada. Se falhar, peça os
códigos ao usuário e use --hex. Avalia cada paleta pelo que quebraria no slide, como rótulo branco ilegível; não diz se
ela é bonita, e quem escolhe é o usuário.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

FEED = "https://colorhunt.co/php/feed.php"
UA = {"User-Agent": "Mozilla/5.0 (slide-studio)", "Content-Type": "application/x-www-form-urlencoded"}


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(h):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def papeis(cores):
    """Do tom mais escuro ao mais claro: escuro = FOCUS_DARK, médio = FOCUS, claro = FOCUS_TINT."""
    c = sorted((x.upper().lstrip("#") for x in cores), key=luminancia)
    return {"FOCUS_DARK": c[0], "PEER_DARK": c[0], "FG": c[0], "FG2": c[0], "FOCUS": c[1], "FOCUS_TINT": c[2], "FOCUS_TOP": c[-1]}


def avaliar(p):
    """Devolve o que vai quebrar no slide, por papel."""
    pontos, br = [], "FFFFFF"
    if contraste(p["FOCUS_DARK"], br) < 7:
        pontos.append(f"escuro fraco para texto ({contraste(p['FOCUS_DARK'], br):.1f}:1, ideal 7+)")
    if contraste(p["FOCUS"], br) < 4.5:
        pontos.append(f"rótulo branco no tom médio ilegível ({contraste(p['FOCUS'], br):.1f}:1, mínimo 4.5): use o escuro nos rótulos")
    if contraste(p["FOCUS"], p["FOCUS_TINT"]) < 1.5:
        pontos.append("tons médio e claro quase iguais: duas séries não se separam")
    if contraste(p["FOCUS_TINT"], br) < 1.2:
        pontos.append("tom claro some no fundo branco")
    return pontos


def buscar(tag, limite):
    corpo = urllib.parse.urlencode({"step": 0, "sort": "popular", "tags": tag, "timeframe": 30}).encode()
    pedido = urllib.request.Request(FEED, data=corpo, headers=UA)
    with urllib.request.urlopen(pedido, timeout=15) as r:
        itens = json.loads(r.read().decode())
    out = []
    for it in itens:
        cod = it["code"].upper()
        p = papeis([cod[i:i + 6] for i in range(0, 24, 6)])
        out.append((len(avaliar(p)), -int(it.get("likes", 0)), cod, p))
    out.sort(key=lambda x: x[:2])
    return out[:limite]


def mostrar(p, nome):
    print(f"\n{nome}")
    pts = avaliar(p)
    print("  Sem problema mecânico." if not pts else "\n".join("  ! " + x for x in pts))
    print('  "palette": ' + json.dumps(p))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tag", nargs="?")
    ap.add_argument("--limite", type=int, default=5)
    ap.add_argument("--hex", nargs=4)
    a = ap.parse_args()
    if a.hex:
        mostrar(papeis(a.hex), "Paleta enviada")
        return 0
    if not a.tag:
        ap.error("informe uma tag ou --hex")
    try:
        res = buscar(a.tag, a.limite)
    except Exception as e:
        print(f"Não consegui ler o Color Hunt ({e}). Peça os 4 códigos ao usuário e use --hex.", file=sys.stderr)
        return 2
    if not res:
        print(f"Nenhuma paleta com a tag '{a.tag}'. Veja as tags em colorhunt.co/palettes.", file=sys.stderr)
        return 2
    for _, likes, cod, p in res:
        mostrar(p, f"{cod} ({-likes} likes) colorhunt.co/palette/{cod.lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
