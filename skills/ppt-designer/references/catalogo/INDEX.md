# Catálogo de peças

Tudo o que foi garimpado nos 21 decks de referência, página por página, além do catálogo por propósito em `references/exemplos/`. Cada entrada traz origem, recorte, função e receita; as principais têm peça pronta.

| Família | Arquivo | Entradas |
|---|---|---:|
| Mapas | `mapas.md` | 67 |
| Profundidade | `profundidade.md` | 158 |
| Diagramas, capas, tabelas e composições | `diagramas.md` | 127 |
| Dispositivos de dado | `elementos-dado.md` | 54 |
| Evidência | `elementos-evidencia.md` | 50 |
| Anotação | `elementos-anotacao.md` | 40 |
| Estrutura | `elementos-estrutura.md` | 32 |
| Navegação | `elementos-navegacao.md` | 26 |
| Identidade, capas e divisores | `elementos-identidade-capas.md` | 21 |
| Citação | `elementos-citacao.md` | 15 |

Os arquivos são longos: use `grep` por palavra ou leia só o começo, onde estão as ★★★.

## Como usar

1. **Parta da mensagem do roteiro,** não da peça. O visual precisa provar o claim.
2. **Ache a família** na tabela abaixo e abra o arquivo dela. Veja o recorte (`crops/…jpg`) das candidatas.
3. **Peça pronta:** copie a função de `references/pecas_*.py` para o build, com os helpers de `lib/pecas_base.py`, e troque só o conteúdo. Sem peça pronta: monte pela receita.
4. **Compare o resultado com o recorte, lado a lado,** e corrija proporção e ordem das camadas. Peça aproximada não serve.

## Do que preciso → onde procurar

| Preciso de | Família | Peças para começar |
|---|---|---|
| Presença geográfica, região, território | Mapas | `pecas_mapas_a.py` (as melhores), `pecas_mapas_b.py` |
| Levar o mapa até um dado | Mapas | Cunha do mapa para colunas ou cartão, em `pecas_mapas_a.py` |
| Veredito, preço-alvo, retorno | Dado | `verdict_bracket` em `pecas_elementos.py`; moldura e bilhete de veredito em `pecas_elementos_a.py` e `_b.py` |
| Fórmula, decomposição, WACC, DuPont | Dado, Diagramas | `formula_ops`, `formula_stairs` em `pecas_elementos.py`; gráficos como termos em `pecas_diagramas.py` |
| Comparar nota, cenário ou payoff | Dado | `square_rating`, `payoff_grid`; placar de estrelas em `pecas_elementos_b.py` |
| Risco com tamanho | Dado, Estrutura | `priced_risks`; códigos com drill-down em `pecas_elementos_b.py` |
| Fazer o gráfico argumentar | Anotação | `scribble_link`, `span_bracket`, `event_flags`, `phase_windows` |
| Explicar um pedaço do dado | Profundidade | `beam_bars`, `donut_flare`, `zoom_wedge` |
| Mostrar camadas ou segmentos | Profundidade | `pyramid3d`, `iso_plates`, `arc_ribbons`, `lens_stack` |
| Dar volume a um cartão ou painel | Profundidade | `tapered_wall`, `gutter_wall`, `bevel_panel`, `slab_cards` |
| Separar uma mensagem do resto da página | Profundidade | `modal_sandwich`, `l_wedges`, `spotlight` |
| Decisão, deal, estrutura societária | Estrutura, Diagramas | `decision_tree`, `cap_table`; ledger de estados em `pecas_elementos_b.py` |
| Fluxo, cadeia de valor, ciclo | Diagramas | `pecas_diagramas.py` |
| Linha do tempo | Diagramas, Profundidade | `ribbon_timeline`; eras em serpentina e ECG em `pecas_diagramas.py` |
| Situar o leitor no deck | Navegação | `plan_tracker`, `nav_tab`; trackers e localizadores em `pecas_elementos_a.py` |
| Tabela com desenho | Diagramas | Linhas ligadas a insights e football field em coluna, em `pecas_diagramas.py` |
| Capa ou divisor | Diagramas, Identidade | Capa em traços em `pecas_diagramas.py`; divisor com facetas em `pecas_moldes.py` |
| Prova própria: entrevista, teste, código, foto | Evidência, Citação | Moldes em `pecas_moldes.py`; **só com material real** |

## Material real

Peças de evidência e citação existem como moldes com rótulos cinza (`[photo]`, `[print]`, `[quote from a real interview]`). Sem o material, não publique o molde nem preencha com algo inventado: peça ao usuário ou escolha outra peça. `browser_news` e `call_stamp` também só recebem notícia e citação reais, vindas do roteiro.

## Mapas

`lib/pecas_base.py` traz `countries_50m()`, `states(iso3)` e `draw_map(...)`. Há estados para RUS, USA, IND, IDN, CHN, BRA, CAN, AUS e ZAF. Não há municípios: as malhas municipais das peças são fictícias e servem só para mostrar a técnica. Em slide real, malha fictícia não pode representar dado; use estados ou traga a geometria.

## Limites

- **Profundidade:** gráfico com dado segue plano, salvo `use_3d = "also_data"`. Perspectiva e degradê que apaga a base atrapalham a leitura do valor. `use_3d = "never"` veta sólidos; cartões, feixes e triângulos continuam permitidos.
- **No máximo uma peça sólida grande por slide.** Ela sustenta a mensagem; não é enfeite.
- **Peça só com o que o roteiro já diz.** Não invente camada, segmento ou conclusão para preencher a forma.
- **Tudo é forma editável.** Nada de imagem colada para simular volume.
- **Tamanho:** muitas peças foram testadas em caixa de cerca de 3,7 × 2,6 pol., com texto pequeno. Em caixa maior, ajuste as fontes para os tamanhos de `RULES.md`.

## Peças mais fracas

Existem, mas confira com mais rigor: `raster_heat_frame` e `process_chain` (fora do mapeamento); `method_stamp_map`, `price_bull_bear`, `logo_cv`, `modal_crown`, `staggered_heat`, `dot_maps`, `dark_glow`.
