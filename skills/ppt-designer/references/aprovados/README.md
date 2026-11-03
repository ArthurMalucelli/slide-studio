# Peças aprovadas

Os dados, a empresa ("Company") e os produtos são fictícios. As imagens servem para estudar a técnica, não para copiar.

| Imagem | O que ela faz | O que copiar da técnica |
|---|---|---|
| `volume-cunha-cascata.jpg` | Dois painéis com volume: a última coluna do primeiro abre por cunha na cascata do segundo, que decompõe aquele mesmo total. | Painel cinza com sombra dura (`painel_volume`). Cunha desenhada depois dos painéis (`beam_from_mark`): ponta estreita com a altura exata da coluna, larga na borda inteira do painel vizinho. Coordenadas da coluna medidas no PDF (`scripts/medir_slide.py`), não calculadas. A cascata começa no valor da coluna e termina fechando a soma. |
| `cunha-na-ponte.jpg` | Uma coluna em destaque, entre colunas claras, abre por cunha numa ponte que explica o valor dela. | Só as colunas citadas ficam na cor forte. Destino com borda tracejada, sem painel cinza. Cunha na cor clara das colunas, enviada para trás do gráfico (`ss.poly` + `ss.to_back`), colada na coluna, sem vão e sem passar do eixo. Colchete liga as duas colunas da ponte que formam a conta. |
