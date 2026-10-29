# Componentes (`SKILL_DIR/lib/slide_style.py`)

`import slide_style as ss`. Coordenadas em polegadas. Cores pelos papéis (`ss.FOCUS`…).
O exemplo completo, que roda com qualquer mestre e qualquer grade, está em `references/exemplo_componentes.py`.

## Esqueleto

| Função | Uso |
|---|---|
| `new_deck(mestre, prefs, profile_dir)` | Abre o mestre, apaga slides de exemplo, aplica profile + prefs. `drop_master_shapes=("Nome",)` remove formas estáticas do mestre (ex.: tracker fixo) |
| `add_slide(prs, layout)` | `layout` = índice ou nome (ver `profile.json → layouts`) |
| `setup(s, título, subtítulo, panels=())` | Preenche título e subtítulo; remove placeholders de conteúdo vazios |
| `cols(n)` / `rows(n)` | Divide a área útil em n colunas `[(x, w)]` / n faixas `[(y, h)]` |
| `panel_header(s, x, y, w, frase, itálico)` | Cabeçalho do painel; devolve o y onde o visual começa |
| `footer(s, "Sources: …", "notas")` | Rodapé no placeholder do mestre ou logo abaixo da área útil |
| `tracker(s, itens, ativo, x, y)` | Tracker de seção desenhado (opcional) |
| `forbidden_hit(x, y, w, h)` | True se a caixa encosta numa zona proibida |
| `save(prs, caminho)` | Salva e roda `fix_axes` (obrigatório) |

## Gráficos nativos (editáveis no PowerPoint)

| Função | Uso / padrão visual |
|---|---|
| `chart(s, XL_CHART_TYPE.…, (x,y,w,h), cats, [(nome, vals)], fmt)` | Cria o gráfico numa caixa |
| `base_chart(ch, vmax, vmin=0, gap)` | Limpo: sem grade, eixo de valor oculto, fundo transparente |
| `plot_layout(ch, x, y, w, h)` | Área de plotagem em frações; necessária para ancorar anotações com `frame()` |
| `labels(ser._element, fmt, fill, color, pos, points, texts)` | Data labels em pill; `texts=` fixa o texto, `points={i: {...}}` destaca um ponto |
| `color_points(ser, [cores])` | Foco em FOCUS, pares em PEER (**comps-barras**) |
| `combo_line(ch, ACCENT, smin, smax, texts)` + `native_legend(ch)` | Colunas + linha suavizada no 2º eixo (**colunas+linha**) |
| `smooth_line(ch)` | Suaviza um gráfico de linha nos dois níveis do XML |
| `doughnut(s, x, y, d, nomes, vals, cores, center_label)` | Rosca com legenda rica ao lado (**donut**) |
| `frame(gf)` | Caixa do gráfico em polegadas para posicionar anotações |

Truques que funcionaram:
- **Total + recorte da empresa:** `COLUMN_CLUSTERED` com `overlap=100`, o total em PEER atrás e a fatia da empresa em FOCUS na frente. O pill do total fica `outEnd`; um gráfico empilhado não aceita `outEnd`.
- **Barra horizontal com descrição:** texto curto em FG2 depois do pill, explicando o que cada valor representa.
- **Cascata (bridge):** barras sólidas; se o eixo não começar em zero, avisar no rodapé.
- **Linha de mercado:** PEER_DARK 2.5pt, pills `ctr` em cima da linha e `delta_bracket` à direita do último ponto, em vez de uma linha de referência atravessando o gráfico.

## Desenho

| Função | Uso |
|---|---|
| `text(s, x, y, w, h, [[(txt, {bold, italic, color, size})]])` | Caixa de texto com runs |
| `pill(s, cx, y, rótulo, fill, color)` | Etiqueta arredondada centrada em cx |
| `line(…)`, `rect(…)`, `bracket(…)`, `delta_bracket(…)` | Fios, caixas, colchetes de anotação (ACCENT ou AXIS) |
| `legend(s, x, y, rows)` | Legenda com formas: `box`, `dash`, `tick`, `line` |
| `note(s, x, y, w, h, msg)` | Nota 8pt itálica |
| `picture(s, caminho, x, y_base, largura)` | Imagem pousada numa linha de base (**lineup-imagens**) |
| `region_map(s, caixa, grupos, cores, by=…)` | Mapa-múndi por região. `by="continent"`, `"region_wb"`, `"subregion"` ou `"iso"`. Devolve `(px, py)` para ancorar rótulos com linha guia. Rótulos fora do mapa (faixa de cima) ou sobre o oceano (**mapa**) |
| `poly(s, pts, fill)` | Polígono livre editável |
| `cube(s, x, yb, w, a, d, front, top, side)` | Prisma isométrico (d≈0.18): escada, pirâmide, prismas. **Só se `deck_prefs` permitir 3D** |
| `to_back`, `set_alpha` | Funil/zoom translúcido atrás do conteúdo |
| `key_stats(s, x, y, w, h, stats)` | Card de 2–4 números grandes. **Só se `deck_prefs.big_numbers = true`** |

## Padrões do catálogo e como montá-los

| Padrão (`references/exemplos/por-visual/`) | Como montar |
|---|---|
| comps-barras | `BAR_CLUSTERED` + `color_points` + `labels` |
| colunas+linha | `COLUMN_CLUSTERED` + `combo_line` |
| mapa | `region_map` + rótulos com `line(..., AXIS, 0.75, dash=False)` + `pill` |
| donut | `doughnut` + legenda rica com `rect` + `text` |
| bridge-cascata | `COLUMN_STACKED` com uma série invisível de base, ou retângulos com `rect` |
| football-field | `BAR_STACKED` horizontal (base invisível + faixa) + `line` vertical no preço atual |
| heatmap-sensibilidade | tabela de `rect` coloridos por faixa (FOCUS_TINT → FOCUS), caso-base com borda ACCENT |
| matriz-riscos | eixos com `line`, quadrantes em `rect` claros, riscos como `pill` numerados + lista lateral curta |
| timeline | `line` horizontal + marcadores `pill`/`rect` + texto curto em cima e embaixo, alternando |
| funil-piramide | `poly` em trapézios (ou `cube` empilhados se o 3D for permitido) |
| pilares / icones+dado-curto | `rect` ou ícones + 1 dado curto cada; nada de parágrafo |
| organograma | `rect` + `line` em cotovelo |
| tabela | tabela nativa (`slide.shapes.add_table`) com cabeçalho FOCUS e linhas finas; o destaque em ACCENT |
