#!/usr/bin/env python3
"""Gera uma ilustração isométrica pelo Codex CLI e recorta o fundo.

Uso:
  gerar_imagem.py "a large warehouse retail store" saida.png
  gerar_imagem.py --recortar entrada.png saida.png     só recorta o fundo de uma imagem que já existe
  gerar_imagem.py --prompt "a large warehouse retail store"   só imprime o prompt, para o usuário gerar onde quiser

A imagem é ilustração, nunca evidência. Usa a conta do Codex do usuário: gere só as que entram no slide. Sem Codex ou
sem imagem gerada, sai com código 3: passe o prompt ao usuário.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROMPT = ("Isometric 3D illustration, miniature diorama style of {cena}, wide angle, zoomed out view, clean and "
          "minimalist, soft global illumination, realistic soft shadows, polished materials, pastel neutral solid "
          "background, professional architectural rendering, high detail, no people, no text, no vehicles.")
PASTA = Path.home() / ".codex" / "generated_images"


def recortar(entrada, saida, tolerancia=26):
    """Torna transparente o fundo liso ligado às bordas. A sombra suave fica, e isso é bom."""
    from collections import deque

    from PIL import Image

    im = Image.open(entrada).convert("RGBA")
    w, h = im.size
    px = im.load()
    borda = [px[x, y] for x in (0, w - 1) for y in (0, h - 1)]
    ref = tuple(sum(c[i] for c in borda) // 4 for i in range(3))
    perto = lambda c: sum(abs(c[i] - ref[i]) for i in range(3)) <= tolerancia
    fila = deque((x, y) for x in range(w) for y in (0, h - 1))
    fila.extend((x, y) for y in range(h) for x in (0, w - 1))
    visto = set()
    while fila:
        x, y = fila.popleft()
        if (x, y) in visto or not (0 <= x < w and 0 <= y < h) or not perto(px[x, y]):
            continue
        visto.add((x, y))
        px[x, y] = (*px[x, y][:3], 0)
        fila.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    caixa = im.getbbox()
    im.crop(caixa).save(saida)
    return len(visto) / (w * h)


def gerar(cena, saida):
    if not shutil.which("codex"):
        return None
    with tempfile.TemporaryDirectory() as t:
        pedido = ("Generate one image with your image generation tool, using exactly this prompt. Do not draw it with "
                  "code. End your answer with the absolute path of the image. If you have no image tool, say so and "
                  f"stop. Prompt: {PROMPT.format(cena=cena)}")
        r = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-C", t, pedido], capture_output=True, text=True,
                           timeout=240)
    # O caminho vem da resposta do próprio Codex: procurar a imagem mais nova pega a de outro agente em paralelo.
    achados = re.findall(re.escape(str(PASTA)) + r"[^\s)\]]+\.png", r.stdout + r.stderr)
    return Path(achados[-1]) if achados and Path(achados[-1]).exists() else None


def main():
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "--prompt":
        print(PROMPT.format(cena=a[1]))
        return 0
    if len(a) == 3 and a[0] == "--recortar":
        print(f"Fundo removido: {recortar(a[1], a[2]):.0%} da imagem. Confira as bordas: {a[2]}")
        return 0
    if len(a) != 2:
        raise SystemExit(__doc__)
    bruta = gerar(a[0], a[1])
    if bruta is None:
        print("Não consegui gerar. Passe este prompt ao usuário:\n" + PROMPT.format(cena=a[0]), file=sys.stderr)
        return 3
    print(f"Fundo removido: {recortar(bruta, a[1]):.0%} da imagem. Confira as bordas: {a[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
