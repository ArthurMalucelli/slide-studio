# Regras de design

São regras aprendidas em decks reais de equity research, com feedback de quem apresentou.

## Fixas (não negociar)

| Regra | Por quê |
|---|---|
| **Nada de texto grande em destaque.** Sem números gigantes, sem "key takeaways" escritos grandes e sem bloco de parágrafo. Só se o usuário pedir (`deck_prefs.big_numbers = true`) | O slide é visual; texto grande compete com o dado e parece relatório |
| **Título em storytelling, sem número**, ≤ ~55 caracteres, uma linha | O título diz a conclusão; o número vai no gráfico |
| **Cabeçalho de painel conta a história**: frase-conclusão (14pt) + itálico com o que o gráfico mostra, unidade e período (11pt) | Quem lê só os cabeçalhos entende o slide |
| **Nem tudo é gráfico** | Lineup, posicionamento e conteúdo qualitativo funcionam melhor como imagem, ícone ou diagrama com um dado curto |
| **Tudo alinhado à grade do mestre** (`ss.cols`, `ss.rows`, `profile.json`) | Cabeçalhos dos painéis vizinhos na mesma altura, margens iguais |
| **Nada encosta nas zonas proibidas do mestre** (`grid.forbidden`: logos, curvas, faixas) | O mestre cobre essa área |
| **Cor com significado fixo** (tabela abaixo) | Quem lê aprende o código uma vez e o reaproveita no deck inteiro |
| **Fonte em todo slide** (`ss.footer`), notas numa 2ª linha | Padrão universal nos decks de referência |
| **Números exatamente como no roteiro**, texto fixo en-US nos rótulos (`texts=`) | O designer não altera dado; formatação regional do PowerPoint quebra números |
| **Validar no PDF exportado pelo Microsoft PowerPoint** | LibreOffice e Keynote renderizam gráficos de outro jeito e escondem bugs |
| **Legenda com formas desenhadas** ou legenda nativa; nunca o glifo ■ | O glifo sai miúdo e desalinhado |
| **Um único destaque (ACCENT) por painel** | Dois destaques = nenhum |

## Preferências (vêm do `deck_prefs.json`; perguntar no intake)

| Preferência | Opções | Padrão se não houver resposta |
|---|---|---|
| Fundo | branco / do mestre / escuro | branco |
| Barras e blocos de dados | planos / 3D isométrico | planos |
| 3D | só ilustração / também dado / nunca | só ilustração |
| Números grandes / key takeaways | não / sim | **não** |

## Papéis de cor (`ss.FOCUS`…; hex vem do tema do mestre ou de `deck_prefs.palette`)

| Papel | Uso |
|---|---|
| `FOCUS` | empresa-foco, série principal |
| `FOCUS_TINT` | empresa-foco fora de destaque, "restante", regiões não destacadas |
| `ACCENT` | **único** destaque: 2ª série, linha, anotação, colchete |
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
| Data labels e pills | 9pt bold (7.5 em mapa) |
| Legendas e descrições | 8–9pt, FG2 |
| Notas | 8pt itálico, MUTED |
| Fontes no rodapé | 7pt, MUTED |

## Checklist visual (no PNG do PDF do PowerPoint)

- [ ] Título em uma linha e sem número; subtítulo em uma linha
- [ ] Cabeçalhos dos painéis vizinhos na mesma altura; itálicos também
- [ ] Nenhum texto cortado, truncado ou colidindo (pills × barras vizinhas, rótulos × linhas)
- [ ] Nada sobre as zonas proibidas do mestre
- [ ] Cor: FOCUS só na empresa-foco, PEER em terceiros, um ACCENT por painel, NEG só negativo
- [ ] Nenhum número repetido no slide; todos iguais aos do roteiro
- [ ] Sem texto grande, número gigante ou parágrafo (salvo `big_numbers`)
- [ ] Fonte no rodapé; notas, se houver
- [ ] Respeita `deck_prefs` (fundo, 3D, barras)
