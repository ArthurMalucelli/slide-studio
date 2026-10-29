"""Exemplo com DADOS FICTÍCIOS de como montar painéis com a biblioteca, em qualquer mestre e em qualquer grade.

Cada painel é uma função que recebe só a sua caixa (x, y, w, h). Ele não sabe em que layout está, então o mesmo
painel serve em 2×2, em "1 largo + 2", em 3 colunas etc. A grade sai de ss.cols(n) / ss.rows(n), que leem a área útil
do mestre. O arquivo gera dois slides com os mesmos painéis em grades diferentes:
- slide 1: 2×2;
- slide 2: 1 painel largo em cima + 2 embaixo.

Painéis de exemplo:
- barras de comparação (foco × pares);
- combo colunas + linha;
- mapa por região;
- linha suavizada com colchete de delta.

Copie o arquivo, troque o conteúdo pelo do roteiro e monte a grade que o slide pedir.
Uso: python3 exemplo_componentes.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))   # skills/ppt-designer/lib
import slide_style as ss  # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE, XL_TICK_MARK  # noqa: E402
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR  # noqa: E402

MASTER, OUT = sys.argv[1], sys.argv[2]
LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
PREFS = sys.argv[4] if len(sys.argv) > 4 else None


def q1_comps(s, x, y, w, h):
    """Barras horizontais: foco em FOCUS, pares em PEER, pill por ponto, anotação curta em ACCENT."""
    y0 = ss.panel_header(s, x, y, w, "The company leads its peer group", "Metric by company, units, 2025, illustrative")
    names, vals = ["Peer A", "Company", "Peer B", "Peer C", "Peer D"], [170, 158, 120, 50, 37]
    cats, vv = names[::-1], vals[::-1]
    VMAX, PX, PY, PW, PH = 235, 0.17, 0.02, 0.81, 0.96
    gf, ch = ss.chart(s, XL_CHART_TYPE.BAR_CLUSTERED, (x, y0, w, y + h - y0), cats, [("2025", vv)], fmt="0")
    ss.base_chart(ch, VMAX, gap=45); ss.plot_layout(ch, PX, PY, PW, PH)
    sr = ch.plots[0].series[0]
    ss.color_points(sr, [ss.FOCUS if c == "Company" else ss.PEER for c in cats])
    ie = cats.index("Company")
    ss.labels(sr._element, "0", ss.PEER_DARK, points={ie: {"fill": ss.FOCUS}}, texts=[str(v) for v in vv])
    fx, fy, fw, fh = ss.frame(gf)
    yc = fy + fh * (PY + PH * (1 - (ie + 0.5) / len(cats)))
    xe = fx + fw * (PX + PW * 158 / VMAX) + 0.45
    ss.text(s, xe, yc - 0.2, fx + fw - xe, 0.4, [[("+25 vs 2024", {"bold": True, "color": ss.ACCENT, "size": 8})]],
            anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def q2_combo(s, x, y, w, h):
    """Colunas FOCUS + linha ACCENT suavizada no eixo secundário; ponto negativo em NEG."""
    y0 = ss.panel_header(s, x, y, w, "Growth comes with stable margins", "Revenue (US$ mn) and margin (%), illustrative")
    yrs = ["2021", "2022", "2023", "2024", "2025"]
    rev, mg = [1130, 1244, 1408, 1763, 2205], [-0.02, 0.122, 0.090, 0.117, 0.120]
    gf, ch = ss.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, (x, y0 - 0.06, w, y + h - y0 + 0.06), yrs,
                      [("Revenue (US$ mn)", rev), ("Margin (%)", mg)], fmt="#,##0")
    ss.base_chart(ch, 4500, gap=55); ss.plot_layout(ch, 0.02, 0.13, 0.96, 0.74)
    sb = ch.plots[0].series[0]
    ss.paint(sb.format.fill, ss.FOCUS)
    ss.labels(sb._element, "#,##0", ss.FOCUS, texts=[f"{v:,}" for v in rev])
    ss.combo_line(ch, ss.ACCENT, -0.45, 0.23, texts=[f"{v*100:.1f}%".replace("-", "−") for v in mg],
                  points={0: {"fill": ss.NEG}})
    ss.native_legend(ch)


def q3_map(s, x, y, w, h):
    """Mapa por região: a região-foco em FOCUS, as demais em FOCUS_TINT; rótulos na faixa de cima, ligados por fio."""
    y0 = ss.panel_header(s, x, y, w, "North America concentrates demand", "Share of 20-year demand by region, illustrative")
    LAB = 0.36
    groups = {"North America": ["North America"], "Europe": ["Europe"], "Asia": ["Asia"],
              "Latin America": ["South America"], "Africa": ["Africa"], "Oceania": ["Oceania"]}
    colors = {g: ss.FOCUS if g == "North America" else ss.FOCUS_TINT for g in groups}
    px, py = ss.region_map(s, (x, y0 + LAB + 0.04, w, y + h - y0 - LAB - 0.04), groups, colors, by="continent")
    labs = [("North America", "31%", -100, 45, -110), ("Europe", "22%", 15, 50, 5), ("Asia", "30%", 100, 35, 100)]
    for name, v, alo, ala, llo in labs:
        hi = name == "North America"
        cx = min(max(px(llo), x + 0.45), x + w - 0.45)
        ss.line(s, cx, y0 + LAB, px(alo), py(ala), ss.AXIS, 0.75, dash=False)
        ss.text(s, cx - 0.5, y0, 1.0, 0.15, [[(name, {"bold": True, "color": ss.FOCUS, "size": 7.5})]],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
        ss.pill(s, cx, y0 + 0.16, v, fill=ss.FOCUS if hi else ss.FOCUS_TINT, color=ss.WHITE if hi else ss.FOCUS,
                h=0.19, size=7.5)


def q4_line(s, x, y, w, h):
    """Linha de mercado (PEER_DARK) suavizada, pills nos pontos, colchete de delta à direita do último ponto."""
    y0 = ss.panel_header(s, x, y, w, "Supply has not recovered", "Industry deliveries, units, 2018–2025, illustrative")
    yrs = [str(v) for v in range(2018, 2026)]
    dl = [1816, 1408, 806, 1040, 1238, 1377, 1265, 1515]
    box = (x, y0 - 0.04, w - 1.0, y + h - y0 + 0.04)
    VMAX, PX, PY, PWf, PH = 2000, 0.02, 0.1, 0.96, 0.76
    gf, ch = ss.chart(s, XL_CHART_TYPE.LINE, box, yrs, [("Deliveries", dl)], fmt="#,##0")
    ss.base_chart(ch, VMAX); ss.plot_layout(ch, PX, PY, PWf, PH)
    sr = ch.plots[0].series[0]
    sr.marker.style = XL_MARKER_STYLE.NONE
    sr.format.line.color.rgb = ss.rgb(ss.PEER_DARK); sr.format.line.width = ss.Pt(2.5)
    ss.smooth_line(ch)
    ss.labels(sr._element, "#,##0", ss.PEER_DARK, ss.WHITE, pos="ctr", texts=[f"{v:,}" for v in dl])
    fx, fy, fw, fh = box
    yv = lambda v: fy + fh * (PY + PH * (1 - v / VMAX))
    ss.delta_bracket(s, fx + fw * (PX + PWf * 7.5 / 8) + 0.45, yv(dl[0]), yv(dl[-1]), "−301", "vs 2018")


if __name__ == "__main__":
    prs = ss.new_deck(MASTER, prefs=PREFS)

    # slide 1: grade 2×2
    s = ss.add_slide(prs, LAYOUT)
    ss.setup(s, "Illustrative title that tells the story", "One-line subtitle that completes the idea")
    (lx, cw), (rx, _) = ss.cols(2)
    (ty, rh), (by, _) = ss.rows(2)
    q1_comps(s, lx, ty, cw, rh); q2_combo(s, rx, ty, cw, rh)
    q3_map(s, lx, by, cw, rh); q4_line(s, rx, by, cw, rh)
    ss.footer(s, "Sources: illustrative data only; replace with the slide's sources.", "Notes go on a second line.")

    # slide 2: mesmos painéis, outra grade (1 largo em cima + 2 embaixo)
    s = ss.add_slide(prs, LAYOUT)
    ss.setup(s, "Same panels, different grid", "Panels only know their box, so any layout works")
    full = (ss.G["content_left"], ss.G["content_right"] - ss.G["content_left"])
    q2_combo(s, full[0], ty, full[1], rh)
    q1_comps(s, lx, by, cw, rh); q4_line(s, rx, by, cw, rh)
    ss.footer(s, "Sources: illustrative data only.")
    ss.save(prs, OUT)
