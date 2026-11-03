#!/usr/bin/env python3
"""Mede um slide de PDF, para transpor a composição. Uso: medir_slide.py <arquivo.pdf> <página>
Lista, em polegadas de um slide de 13,333 de largura: formas preenchidas (maiores primeiro) e blocos de texto."""
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

pdf, page = sys.argv[1], sys.argv[2]
with tempfile.TemporaryDirectory() as d:
    svg, html = Path(d) / "p.svg", Path(d) / "p.html"
    subprocess.run(["pdftocairo", "-svg", "-f", page, "-l", page, pdf, str(svg)], check=True, stderr=subprocess.DEVNULL)
    r = subprocess.run(["pdftotext", "-bbox-layout", "-f", page, "-l", page, pdf, str(html)], stderr=subprocess.DEVNULL)
    root = ET.parse(svg).getroot()
    W = float(re.sub(r"[a-z]", "", root.get("width")))
    k = 13.333 / W
    shapes = []

    def hexcolor(c):
        m = re.findall(r"([\d.]+)%", c or "")
        return "".join(f"{round(float(v) * 2.55):02X}" for v in m[:3]) if len(m) >= 3 else c

    def walk(el, skip=False):
        tag = el.tag.split("}")[-1]
        if tag in ("defs", "symbol", "clipPath", "mask"):
            return
        if tag == "path" and el.get("fill") not in (None, "none") and el.get("d"):
            nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", el.get("d"))]
            xs, ys = nums[0::2], nums[1::2]
            if xs and ys and not el.get("transform"):
                b = (min(xs) * k, min(ys) * k, (max(xs) - min(xs)) * k, (max(ys) - min(ys)) * k)
                if b[2] * b[3] > 0.01:
                    n = el.get("d").count("L") + el.get("d").count("C")
                    shapes.append((b[2] * b[3], b, hexcolor(el.get("fill")), el.get("fill-opacity", "1"), n))
        for c in el:
            walk(c)

    walk(root)
    print("FORMAS (x, y, larg, alt | cor | opacidade | n. de vértices)")
    for _, b, c, o, n in sorted(shapes, key=lambda t: -t[0])[:60]:
        print(f"  {b[0]:6.2f} {b[1]:5.2f} {b[2]:6.2f} {b[3]:5.2f} | {c} | {o} | {n}")
    print("TEXTO (x, y, larg, alt | texto)")
    if r.returncode or not html.exists():   # o pdftotext quebra em algumas páginas: as formas continuam valendo
        print("  (posições indisponíveis nesta página; texto corrido)")
        print(subprocess.run(["pdftotext", "-layout", "-f", page, "-l", page, pdf, "-"], capture_output=True, text=True).stdout[:3000])
        sys.exit(0)
    t = re.sub(r'xmlns="[^"]+"', "", html.read_text(errors="ignore"))
    for bl in re.findall(r'<block xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</block>', t, re.S):
        x0, y0, x1, y1 = [float(v) * k for v in bl[:4]]
        words = " ".join(re.findall(r">([^<>]+)</word>", bl[4]))[:90]
        print(f"  {x0:6.2f} {y0:5.2f} {x1 - x0:6.2f} {y1 - y0:5.2f} | {words}")
