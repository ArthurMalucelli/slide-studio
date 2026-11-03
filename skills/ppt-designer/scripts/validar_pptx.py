#!/usr/bin/env python3
"""Acha, antes de abrir no PowerPoint, o XML que o faz parar num aviso invisível e recusar tudo depois (-1712, -9074).

Uso: validar_pptx.py arquivo.pptx. Sai com código 1 se achar problema.
"""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
INVALIDO = {"stacked": {"outEnd"}, "percentStacked": {"outEnd"}}


def problemas(caminho):
    out = []
    z = zipfile.ZipFile(caminho)
    for nome in z.namelist():
        if not re.fullmatch(r"ppt/charts/chart\d+\.xml", nome):
            continue
        raiz = ET.fromstring(z.read(nome))
        for barra in raiz.iter(C + "barChart"):
            g = barra.find(C + "grouping")
            ruins = INVALIDO.get(g.get("val") if g is not None else "", set())
            for pos in barra.iter(C + "dLblPos"):
                if pos.get("val") in ruins:
                    out.append(f"{nome}: rótulo '{pos.get('val')}' em barra {g.get('val')}. Use 'ctr' ou 'inEnd'.")
                    break
    return out


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    ps = problemas(sys.argv[1])
    for x in ps:
        print(x, file=sys.stderr)
    return 1 if ps else 0


if __name__ == "__main__":
    sys.exit(main())
