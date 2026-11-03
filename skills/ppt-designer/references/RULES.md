# Regras de design

São regras aprendidas em decks reais de equity research, com feedback de quem apresentou.

## Fixas (não negociar)

| Regra | Por quê |
|---|---|
| **Nada de texto grande em destaque.** Sem números gigantes, sem "key takeaways" escritos grandes e sem bloco de parágrafo. Só se o usuário pedir (`deck_prefs.big_numbers = true`) | O slide é visual; texto grande compete com o dado e parece relatório |
| **Nenhum número em título**: título do slide e cabeçalho de painel, ≤ ~55 caracteres no título, uma linha. Inclui período (FY26, 2025) | O título diz a conclusão; o número vai no gráfico e o período, no itálico |
| **Cabeçalho de painel conta a história**: frase-conclusão (14pt) + itálico com o que o gráfico mostra, unidade e período (11pt) | Quem lê só os cabeçalhos entende o slide |
| **Dois níveis de texto por visual, nunca três.** Cada gráfico tem um cabeçalho e um itálico, sem rótulo ou "sub-subtítulo" extra. Dois gráficos sob a mesma ideia viram dois painéis, cada um com o seu cabeçalho | Terceiro nível repete o itálico e polui o topo do gráfico |
| **Sem bloco de notas na face do slide.** Definições e ressalvas vão para as notas do apresentador (`ss.footer(..., notes=...)`); no rodapé, só as fontes | O slide é visual; a ressalva é falada ou vai para o Q&A |
| **Sem colunas de texto ao lado do gráfico** (ano fiscal, escopo, base, descrição por linha). O essencial vai no itálico; o resto, nas notas do apresentador | Vira tabela colada no gráfico e compete com o dado |
| **Data label com um único estilo no slide:** retângulo arredondado, fundo escuro, texto branco bold 9pt. FOCUS na empresa-foco, PEER_DARK em terceiros, NEG em negativo. Nunca fundo claro com texto preto, nem a cor de uma série clara ou do ACCENT | Pills de cores e contrastes diferentes parecem erro |
| **Nem tudo é gráfico** | Lineup, posicionamento e conteúdo qualitativo funcionam melhor como imagem, ícone ou diagrama com um dado curto |
| **Tudo alinhado à grade do mestre** (`ss.cols`, `ss.rows`, `profile.json`) | Cabeçalhos dos painéis vizinhos na mesma altura, margens iguais |
| **Nada encosta nas zonas proibidas do mestre** (`grid.forbidden`: logos, curvas, faixas) | O mestre cobre essa área |
| **Cor com significado fixo** (tabela abaixo) | Quem lê aprende o código uma vez e o reaproveita no deck inteiro |
| **Evidência só com material real.** Foto, print, entrevista, citação e notícia nunca são inventados; o molde com rótulo cinza não vai para a entrega | A banca cobra a origem, e prova falsa derruba o deck |
| **Fonte em todo slide** (`ss.footer`) | Padrão universal nos decks de referência |
| **Números exatamente como no roteiro**, texto fixo en-US nos rótulos (`texts=`) | O designer não altera dado; formatação regional do PowerPoint quebra números |
| **Validar no PDF exportado pelo Microsoft PowerPoint** | LibreOffice e Keynote renderizam gráficos de outro jeito e escondem bugs |
| **Legenda com formas desenhadas** ou legenda nativa; nunca o glifo ■ | O glifo sai miúdo e desalinhado |
| **Um único destaque (ACCENT) por painel** | Dois destaques = nenhum |

## Preferências (vêm do `deck_prefs.json`; perguntar no intake)

| Preferência | Opções | Padrão se não houver resposta |
|---|---|---|
| Fundo | branco / do mestre / escuro | branco |
| Barras e blocos de dados | planos / 3D isométrico | planos |
| 3D | só ilustração / também dado / nunca | só ilustração (peças e limites em `catalogo/INDEX.md`) |
| Números grandes / key takeaways | não / sim | **não** |

## Papéis de cor (`ss.FOCUS`…; hex vem do tema do mestre ou de `deck_prefs.palette`)

| Papel | Uso |
|---|---|
| `FOCUS` | empresa-foco, série principal |
| `FOCUS_TINT` | empresa-foco fora de destaque, "restante", regiões não destacadas |
| `ACCENT` | **único** destaque: 2ª série, linha, anotação, colchete; nunca fundo de data label |
| `PEER` / `PEER_DARK` | terceiros e concorrentes, mercado total; **nunca** a empresa-foco |
| `NEG` | só valor negativo ou alerta |
| `FG` / `FG2` / `MUTED` / `AXIS` | texto principal / descrição / secundário / eixos e fios |
| `FOCUS_DARK` / `FOCUS_TOP` | lateral e topo de sólidos 3D |

Dado de mercado inteiro (todos os fabricantes) vai em `PEER`. A fatia da empresa-foco dentro dele vai em `FOCUS`.

## Tipografia

A fonte é a do tema do mestre ou a de `deck_prefs.font`.

| Elemento | Tamanho |
|---|---|
| Título | o do placeholder do mestre |
| Subtítulo | o do placeholder (≈14pt) |
| Cabeçalho de painel | 14pt regular, FG |
| Itálico do painel | 11pt itálico, MUTED |
| Data labels e pills | 9pt bold branco sobre fundo escuro (7.5 em mapa) |
| Legendas e descrições | 8–9pt, FG2 |
| Fontes no rodapé | 7pt, MUTED |

## Checklist visual (no PNG do PDF do PowerPoint)

- [ ] Título, subtítulo e itálicos de painel em uma linha cada
- [ ] Nenhum número, nem período, no título ou nos cabeçalhos de painel
- [ ] Cada visual com um cabeçalho e um itálico, sem terceiro nível de texto
- [ ] Sem notas na face do slide e sem colunas de texto ao lado do gráfico
- [ ] Todos os data labels no mesmo estilo (fundo escuro, texto branco)
- [ ] Cabeçalhos dos painéis vizinhos na mesma altura; itálicos também
- [ ] Nenhum texto cortado, truncado ou colidindo (pills × barras vizinhas, rótulos × linhas)
- [ ] Nada sobre as zonas proibidas do mestre
- [ ] Cor: FOCUS só na empresa-foco, PEER em terceiros, um ACCENT por painel, NEG só negativo
- [ ] Nenhum número repetido no slide; todos iguais aos do roteiro
- [ ] Sem texto grande, número gigante ou parágrafo (salvo `big_numbers`)
- [ ] Fonte no rodapé; notas do roteiro nas notas do apresentador
- [ ] Respeita `deck_prefs` (fundo, 3D, barras)
