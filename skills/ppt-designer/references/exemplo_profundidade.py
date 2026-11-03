"""Exemplo com DADOS FICTÍCIOS das peças de profundidade, em qualquer mestre. Gabarito: deck Intelbras.
Uso: python3 exemplo_profundidade.py <mestre.pptx> <saida.pptx> [layout] [deck_prefs.json] [profile_dir]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import slide_style as ss  # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE  # noqa: E402
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR  # noqa: E402

MASTER, OUT = sys.argv[1], sys.argv[2]
LAYOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
PREFS = sys.argv[4] if len(sys.argv) > 4 else None
PROFILE = sys.argv[5] if len(sys.argv) > 5 else None


def label(s, x, y, w, head, body, color=None, align=PP_ALIGN.LEFT):
    ss.text(s, x, y - 0.2, w, 0.4, [[(head, {"bold": True, "color": color or ss.FG, "size": 9}),
                                     (body, {"color": ss.FG, "size": 9})]], anchor=MSO_ANCHOR.MIDDLE, margin=0.0, align=align)


def pyramid_panel(s, x, y, w, h):
    y0 = ss.panel_header(s, x, y, w, "Each layer defends the one below", "Client segments by switching cost, illustrative")
    pw, ph = 2.2, y + h - y0 - 0.05
    cx = x + w - pw / 2 - 0.1
    anchors = ss.pyramid3d(s, cx, y0, pw, ph, layers=4)
    rows = [("Enterprise", " mission critical"), ("Corporate", " installer-led"),
            ("Mid-tier", " partly exposed"), ("Residential", " price wins")]
    for (xl, _, ym), (hd, bd) in zip(anchors, rows):
        tx = x + 0.75
        ss.tick_leader(s, xl, ym, tx + 1.95, ss.FOCUS)
        label(s, tx, ym, 1.92, hd, bd)
    ss.tri(s, x + 0.38, y0 + ph * 0.5, 0.28, ph * 0.42, "left", ss.FOCUS_TINT)
    ss.text(s, x - 0.02, y0 + ph * 0.5, 0.42, ph * 0.42, [[("Price", {"bold": True, "color": ss.FG, "size": 8})]],
            anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def discs_panel(s, x, y, w, h):
    y0 = ss.panel_header(s, x, y, w, "Loyalty deepens toward the core", "Layers of the channel relationship, illustrative")
    d = y + h - y0 - 0.08
    cx = x + d / 2 + 0.25
    colors = [ss.FOCUS_DARK, ss.FOCUS, ss.ACCENT, ss.FOCUS_TINT]
    anchors = ss.nested_discs(s, cx, y0 + d / 2, d, colors)
    labs = [("Generational", " years of relationship"), ("Supplier", " program lock-in"), ("Payment", " shorter receivables")]
    tx = x + d + 1.0
    for i, (hd, bd) in enumerate(labs):
        ym = y0 + d * (0.2 + 0.3 * i)
        xs = cx + d * 0.42 if i != 1 else anchors[1][0] - 0.1
        ss.tick_leader(s, xs, ym, tx - 0.05, [ss.FOCUS_DARK, ss.FOCUS, ss.ACCENT][i])
        label(s, tx + 0.03, ym, x + w - tx - 0.05, hd, bd)


def card_panel(s, x, y, w, h):
    y0 = ss.panel_header(s, x, y, w, "Three signals confirm the inflection", "Card with offset corners, illustrative")
    cy, ch = y0 + 0.05, y + h - y0 - 0.1
    ss.depth_card(s, x + 0.05, cy, w - 0.1, ch)
    tw = (w - 0.9) / 3
    for i, t in enumerate(("Days fall", "Margin recovers", "Costs stabilize")):
        tx = x + 0.2 + i * (tw + 0.2)
        ss.text(s, tx, cy + 0.12, tw, ch * 0.45, [[(t, {"bold": True, "color": ss.FG, "size": 11})]],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
        if i:
            ss.text(s, tx - 0.2, cy + 0.12, 0.2, ch * 0.45, [[("+", {"bold": True, "color": ss.CARD_EDGE, "size": 16})]],
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    ss.tri(s, x + w / 2 - 0.3, cy + ch * 0.55, 0.6, 0.15, "down")
    ss.text(s, x + 0.2, cy + ch * 0.68, w - 0.4, ch * 0.28,
            [[("Execution drives the recovery", {"bold": True, "italic": True, "color": ss.FG, "size": 11})]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def wedge_panel(s, x, y, w, h):
    y0 = ss.panel_header(s, x, y, w, "One segment explains the change", "Mix by segment, %, with zoom to a card, illustrative")
    bx, bw = x + 0.1, 1.5
    by, bh = y0 + 0.05, y + h - y0 - 0.1
    ss.rect(s, bx, by, bw, bh * 0.3, ss.FOCUS); ss.rect(s, bx, by + bh * 0.3, bw, bh * 0.7, ss.FOCUS_TINT)
    ss.text(s, bx, by, bw, bh * 0.3, [[("29%", {"bold": True, "color": ss.WHITE, "size": 9})]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margin=0.0)
    cx0 = x + w * 0.5
    ss.zoom_wedge(s, (bx + bw, by), (bx + bw, by + bh * 0.3), (cx0, by), (cx0, by + bh))
    ss.rect(s, cx0, by, x + w - cx0, bh, ss.CARD)
    ss.text(s, cx0 + 0.12, by, x + w - cx0 - 0.24, bh, [[("Exposed revenue sits in the mass-market segment", {"color": ss.FG, "size": 11})]],
            anchor=MSO_ANCHOR.MIDDLE, margin=0.0)


def panel_extruded(s, x, y, w, h):
    y0 = ss.panel_header(s, x, y, w, "The network is denser than peers", "Panel with side wall, content on top, illustrative")
    ss.extruded_panel(s, x, y0 + 0.02, w - 0.3, y + h - y0 - 0.04)
    gf, ch = ss.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, (x + 0.15, y0 + 0.1, w - 0.6, y + h - y0 - 0.2),
                      ["2021", "2022", "2023", "2024"], [("Stores", [120, 150, 190, 240])], fmt="0")
    ss.base_chart(ch, 300, gap=90)
    sr = ch.plots[0].series[0]; ss.paint(sr.format.fill, ss.FOCUS)
    ss.labels(sr._element, "0", ss.FOCUS, texts=["120", "150", "190", "240"])


def panel_diamonds(s, x, y, w, h):
    y0 = ss.panel_header(s, x, y, w, "Five plants spread the risk", "Plates in zigzag; pass photos instead of colors, illustrative")
    n, ph = 5, (y + h - y0) / (1 + 4 * 0.62)
    colors = [ss.FOCUS_DARK, ss.FOCUS, ss.ACCENT, ss.FOCUS, ss.FOCUS_DARK]
    anchors = ss.diamond_stack(s, x + 0.95, y0, 1.5, ph, colors)
    for i, (ax, ay) in enumerate(anchors):
        ss.line(s, ax - 0.1, ay, x + w - 0.1, ay, ss.AXIS, 0.75, dash=False)
        ss.text(s, x + 2.3, ay - 0.2, w - 2.4, 0.19, [[(f"Plant {'ABCDE'[i]}", {"bold": True, "color": ss.FG, "size": 9})]],
                anchor=MSO_ANCHOR.BOTTOM, margin=0.0)


if __name__ == "__main__":
    prs = ss.new_deck(MASTER, prefs=PREFS, profile_dir=PROFILE)
    s = ss.add_slide(prs, LAYOUT)
    ss.setup(s, "Depth pieces, solid shapes", "Pyramid, nested discs, card with corners and gradient zoom")
    (lx, cw), (rx, _) = ss.cols(2)
    (ty, rh), (by, _) = ss.rows(2)
    pyramid_panel(s, lx, ty, cw, rh); discs_panel(s, rx, ty, cw, rh)
    card_panel(s, lx, by, cw, rh); wedge_panel(s, rx, by, cw, rh)
    ss.footer(s, "Sources: illustrative data only.")
    s = ss.add_slide(prs, LAYOUT)
    ss.setup(s, "Depth pieces, panels and plates", "Panel with side wall and zigzag plates")
    panel_extruded(s, lx, ty, cw, ty + rh + rh + 0.3 - ty); panel_diamonds(s, rx, ty, cw, rh + rh + 0.3)
    ss.footer(s, "Sources: illustrative data only.")
    ss.save(prs, OUT)
