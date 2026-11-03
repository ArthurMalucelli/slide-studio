# Profundidade

Gabarito: deck da Intelbras (`references/exemplos/pdf/Intelbras.pdf`). A profundidade dele vem de sólidos, camadas e feixes em volta do dado. Os gráficos continuam planos.

Abra esta página quando o slide tiver segmentação, camadas, conclusão ou zoom em um dado, e veja 1–2 prints antes de desenhar.

| Recurso | Função | Quando usar | Referência |
|---|---|---|---|
| Pirâmide facetada | `pyramid3d` + `tick_leader` | Segmentos ou camadas com hierarquia | `prints/Intelbras_p017.jpg`, `prints/Intelbras_p052.jpg` |
| Cunha lateral | `tri(..., "left")` | Pressão externa sobre parte de uma pirâmide ou lista | `prints/Intelbras_p017.jpg` |
| Discos em núcleo | `nested_discs` + `tick_leader` | Camadas de retenção, do externo ao núcleo | `prints/Intelbras_p011.jpg` |
| Cartão com cantoneiras | `depth_card` | Conclusão ou soma de sinais | `prints/Intelbras_p044.jpg`, `prints/Intelbras_p053.jpg` |
| Triângulo de "portanto" | `tri(..., "down")` | Passagem das evidências para a conclusão | `prints/Intelbras_p053.jpg` |
| Feixe em degradê | `zoom_wedge` | Levar um pedaço do gráfico a um cartão explicativo | `prints/Intelbras_p044.jpg`; `pdf/Intelbras.pdf`, p.49 |
| Painel com parede lateral | `extruded_panel` | Agrupar mapa ou gráfico como peça principal | `prints/Intelbras_p009.jpg` |
| Placas em losango | `diamond_stack` | Unidades, plantas ou lugares, com fotos ou cores | `prints/Intelbras_p052.jpg` |
| Cunha de título | `wedge_tab` | Abrir citação ou bloco de texto | `prints/Intelbras_p011.jpg` |

Exemplo completo, para qualquer mestre: `references/exemplo_profundidade.py`.

## Regras

- **Gráfico com dado segue plano**, salvo `use_3d = "also_data"`. Perspectiva distorce a comparação de alturas.
- `use_3d = "never"` veta `pyramid3d`, `diamond_stack` e `extruded_panel`. Cartões, feixes e triângulos continuam permitidos.
- **No máximo uma peça sólida grande por slide.** Ela sustenta a mensagem; não é enfeite.
- Peça só com o que o roteiro já diz. Não invente camada, segmento ou conclusão para preencher a forma; se faltar conteúdo, proponha ao usuário.
- Tudo é forma editável: nada de imagem colada para simular 3D.
