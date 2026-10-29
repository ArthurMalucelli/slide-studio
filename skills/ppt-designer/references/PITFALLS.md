# Armadilhas já resolvidas (PowerPoint + python-pptx)

| Sintoma | Causa | Correção |
|---|---|---|
| Barras todas da mesma altura no PowerPoint | Falta `<c:orientation>` no valAx | `ss.save()` já roda `fix_axes()`; nunca salve com `prs.save` direto |
| Combo quebrado ou linha no eixo errado | Algum valAx ficou `delete=1` | Use `combo_line()`: os dois valAx ficam `delete=0` e invisíveis |
| Linha que não suaviza | `<c:smooth val="0"/>` no lineChart sobrepõe o da série; python-pptx grava `<c:smooth/>` sem val | `smooth_line(ch)` grava 1 nos dois níveis |
| Pill de total não aceita `outEnd` | Gráfico empilhado não tem `outEnd` | Use `COLUMN_CLUSTERED` com `overlap=100` |
| Label de várias linhas truncado | Quebra automática do PowerPoint | `labels()` usa `wrap="none"`; ou desenhe o texto como forma |
| Texto de bolha quebrando ("Honeywel/l") | word wrap | `tb.text_frame.word_wrap = False` |
| Freeform 3D ou mapa distorcido | custGeom arredonda para inteiro | `poly()` usa 1/1000 pol. (`scale=914.4`) |
| Placeholder pula para y=0 | Mudou só x/largura | Regrave top/height (`header_ph` já faz) |
| Número com vírgula ou ponto trocado | Formato regional do PowerPoint | `labels(..., texts=[...])` com texto fixo en-US |
| Pills de duas séries se tocando | Escalas parecidas nos dois eixos | Ajuste `vmax` / `smin`/`smax` para separar as faixas |
| Rótulos de mapa colidindo | Rótulo em cima do país | Rótulos fora do mapa (faixa) ou sobre o oceano, com linha guia |
| Mapa achatado ou esticado | Caixa sem proporção | `region_map(keep_aspect=True)`; com `False`, até ~30% de esticada passa |
| Export PowerPoint erro -600 | PowerPoint fechado | `open -a "Microsoft PowerPoint"`, espere ~8 s e tente de novo (o script já tenta) |
| Export erro -50 / -1712 / -9074 | Caminho fora do alcance do PowerPoint (sandbox, /tmp) ou timeout | Salve e exporte dentro da pasta do usuário (Documents/Desktop), não em /tmp |
| Fonte trocada no PDF | Fonte do tema não instalada | Instale a fonte (ex.: Google Fonts) ou defina `deck_prefs.font` |
| Forma do mestre aparecendo por cima (tracker fixo, número de página duplicado) | Está no slide master | `new_deck(..., drop_master_shapes=("Nome da forma",))` |
