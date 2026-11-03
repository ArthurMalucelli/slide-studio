# Regras de design

São regras aprendidas em decks reais de equity research, com feedback de quem apresentou.

## A regra central: nada aparece do nada

Como montar: `RECEITA.md`. O dono reprova os dois extremos: peça forte "do nada" e slide totalmente plano, "sem sal". Por isso, uma peça por slide, discreta e presa ao conteúdo. A dobra em cinza claro entre dois painéis ligados vale sem número em comum.

Cunha e sólido precisam passar nos 4 testes. Se falharem em um, troque pela dobra:

| Teste | Passa | Reprovado |
|---|---|---|
| **Origem** | Sai de um elemento de dado real: colada nele, no tom claro da cor dele, com a ponta da altura exata dele | Sai do espaço em branco, do vão entre barras, da borda do gráfico ou do meio de um grupo |
| **Destino** | Abre em algo que expande a origem: subgráfico, tabela, divisão, mapa, com 2 ou mais dados. O leitor aprende o que há dentro | Abre numa frase. Uma frase sobre o dado é rótulo ou colchete em cima do dado, sem feixe nem cartão |
| **Forma = conteúdo** | O sólido é o próprio conteúdo: camadas com nome, 3 ou mais etapas com texto dentro | Sólido ao lado de um gráfico, ou desenhando só 2 valores |
| **Função** | Tirar a peça muda o que o leitor entende | Parede, faixa ou cantoneira de cor em volta de um gráfico que já se lê sozinho. Tirar não muda nada. Painel cinza quase branco, igual em todo o slide, é permitido (ChallengeB p.2, p.7) |

**Um protagonista por slide.** No máximo uma peça forte; o resto fica plano e quieto. Os melhores decks têm gráficos planos: o feixe, a parede ou a pirâmide é um só. Destaque da empresa-foco é a cor da barra, não uma faixa em volta dela.

Exemplos reais: `references/reprovados/`.

## O que a Sabesp e o Nubank fazem e nossos slides não fizeram

Medido e comparado nas rodadas de teste. Tirar os chips não basta: slides sem chips e com cabeçalhos em uma linha ainda foram reprovados como "muito crowded", e o dono apontou o excesso de texto. Orçamento em `RECEITA.md`, passo 8. O que pesa:

| Gabarito | Nossos reprovados |
|---|---|
| Número mora em gráfico; fora dele, é texto em negrito | 28 a 48 chips coloridos soltos em cards |
| Cabeçalho em uma linha, com 1 ou 2 palavras-chave em negrito na cor | Cabeçalho em duas linhas, todo igual |
| Uma família de cor por slide (azuis na Sabesp, roxos no Nubank) | Vermelho, rosa, azul e marinho juntos, com vermelho em tudo |
| 2 a 4 exibits, cada um com área para respirar | Painel dentro de painel, com exibit menor ainda dentro |
| O gráfico é o conteúdo do painel | Caixa de texto no lugar do gráfico |
| Poucos tipos de peça por slide | Gráfico + cards + barrinha + frase + equação no mesmo slide |
| Grade regular: quadrantes ou colunas iguais | Blocos de tamanhos diferentes, encaixados onde sobrou espaço |

**Marca de cor quente (vermelho):** base em azul e marinho, com a cor quente só no destaque de cada exibit. Em teste: ainda não foi avaliado pelo dono do deck.

## Reprovado pelo dono do deck, sem discussão

| Não pode | Faça |
|---|---|
| **Texto ou valor em destaque do nada:** caixas ou chips soltos com um número (`>27`, `>33`), sem gráfico nem contexto em volta | O valor mora num gráfico, numa linha de tabela ou numa frase. Nada de caixa colorida só para um número |
| **Zoom-out gigante:** feixe que cruza o slide ou abre para um painel de altura inteira | Feixe curto, na mesma linha do dado, com a ponta larga no máximo 3× a estreita |
| **Legenda ao lado do gráfico** | Legenda em cima do gráfico, na horizontal |
| **Painel só de frases soltas,** com fio vertical e muito ar em volta | Frase sem dado não vira painel: entra junto do gráfico que ela explica ou sai |
| **Tabela de texto** com linhas e muito ar, ligada por fios a outro painel | Choice e efeito viram cards, cadeia ou diagrama. Tabela só para números |
| **Quadrante inteiro para pouco dado:** dois valores ocupando um quarto do slide, com ou sem seta | Dois valores viram uma linha dentro de outro painel, ou saem. Área do painel é proporcional ao dado que ele tem |
| **Cor mudando entre painéis:** a mesma série em cores diferentes, ou pares em cinza num gráfico e rosa no outro | Uma cor por significado no slide inteiro: foco, comparação e pares não mudam de um painel para outro |
| **Qualitativo demais:** painel de frases, ícones ou cards onde o gabarito teria número | Todo painel prova com dado. Texto é apoio de um gráfico, não o painel. Se o roteiro só tem frases, avise antes de montar |
| **Slide sem graça:** limpo, correto e vazio | Densidade do gabarito: vários números, mais de um exhibit por slide, anotação no gráfico |
| **Poluído:** muito texto (acima de ~130 palavras), chips de número soltos, painel dentro de painel, cabeçalho em duas linhas | Fora de gráfico, número é texto em negrito (`checar_slide.py` barra mais de 4 chips). No máximo 4 exibits, contando tabela e mapa, sem exibit dentro de exibit |
| **Faixa de KPIs soltos:** losangos ou ícones numa linha com "914 Warehouses", "81.0m Members", parecendo timeline sem ter tempo | Só use linha do tempo para tempo. KPI entra no gráfico ou no itálico, mesmo que o roteiro o liste como bloco |
| **Gráfico em bloco do nada:** um retângulo 98/2 de uma categoria ocupando um quadrante | Composição com 3 ou mais partes, e que abre em algo. 98/2 é uma frase ou um rótulo |
| **Cards grandes arredondados,** rosca gigante com número no meio, equação em caixas e caixas de KPI: "muito feio" | Tabela ou gráfico com rótulo. Rosca só pequena e com 3 ou mais fatias. Card de produto com foto real é outra coisa (ChallengeB p.11, p.14) |
| **Maçaroca de cunhas:** todos os segmentos da barra abrindo ao mesmo tempo em blocos altos, formando uma massa de cor | Cunha pequena, de um ou dois segmentos, para cartões com dado. Compare com a peça aprovada abaixo |
| **Coluna lotada:** dois mapas e um gráfico empilhados no mesmo painel, com rótulos em volta | Um exibit por painel. Tabela e mapa contam como exibits separados: o limite de 4 inclui os dois |
| **Diagrama de colunas cinza com setas-bloco:** colunas altas e vazias, e faixas de cor com texto dentro | Reprovado com o slide inteiro. Ainda não há versão aprovada de diagrama de fluxo |
| **Grupo de ícone + frases centralizadas:** cards cinza com ícone e 2 ou 3 linhas de texto, mesmo copiados do gabarito (Nubank p.16): "uma bosta" | Esse conteúdo vira gráfico ou tabela numérica. Se o roteiro só tem frases, troque de modelo |
| **Foto do nada:** foto real de uma loja colada ao lado de um gráfico que não fala dela | Imagem é parte da prova, ou sai (`RECEITA.md`, passo 5) |
| **Itálico com resultado:** "Per-warehouse share: 73.8% FY19–26", empurrando a unidade para a legenda | Itálico diz métrica, unidade e período. O resultado está no gráfico |
| **Cunha solta:** vão entre a barra e a cunha, ou ponta passando do eixo | Encosta na barra, com a altura exata dela (`RECEITA.md`, passo 4) |
| **Colagem de tipos:** dois gráficos + três cards + barrinhas de progresso + frase solta | Escolha um padrão do gabarito e fique nele |
| **Frase de conclusão solta** embaixo do slide, em faixa escura, caixa com sombra ou com marcador | A conclusão está no título e no subtítulo. Tire |
| **Rótulos no lugar do dado:** painel com a geometria do gabarito, mas caixas de texto onde ele tinha gráfico | Sem o dado, troque de slide do gabarito (passo 5 da transposição) |
| **Nota na face do slide,** mesmo ressalva do roteiro | Vai para as notas do apresentador |
| **Ilustração caseira e flecha fina:** fábrica e loja desenhadas com formas, setas de 1pt | A ideia de diagrama pode ser boa. Ícones de um só traço ou peça do catálogo, e fluxo como faixa grossa com valor |

## Aprovado pelo dono do deck

**Membership da rodada 9, feito só pela receita (106 palavras, 33 dados):** "tá legal", com a cunha que abre a última coluna na ponte por sócio, encostada na barra. Primeiro slide aprovado sem copiar modelo: painel largo em cima e 3 embaixo, com um gráfico de cada tipo.

**Grade 2×2 regular com 4 provas (teste com dados da Sabesp p.18):** primeiro slide inteiro aprovado depois de seis rodadas ("tá legal, mas dava para ter mais coisa de profundidade"). Não é para copiar: é o resultado dos passos 2 e 3 de `RECEITA.md`.

**Cadeia de cards com cunhas e ícones (aprovada duas vezes):** cards cinza com ícone, título em negrito e texto curto, cada um separado do próximo por uma cunha em perspectiva colorida, com rota alternativa tracejada por cima. Serve para fluxo e processo. Aprovada só como faixa; o resto do slide tem de ser dado.

**Cunha que sai da barra empilhada e abre em cartões com dado:** cada segmento da última barra abre, na cor dele e colado nele, num cartão com a altura proporcional, com os valores do segmento dentro (`beam_from_mark`). O dono gostou: um número abrindo no que há dentro dele.

**Dobra (Sabesp p.13, ChallengeB p.7):** dois painéis cinza em planos diferentes, ligados por uma faixa ou trapézio (`dobra`). O 3D foi aprovado; o conteúdo só de rótulos foi reprovado. Dentro, tem de haver dado. Ao tirá-la de um slide, ele foi reprovado: "tirou a profundidade, ficou meio sem sal".

**Ideias aprovadas, sem execução aprovada até agora:** barra de decomposição abrindo em painéis e diagrama fornecedor → empresa → cliente. Cada uma já tomou duas reprovações na execução; não as use como protagonista sem pedido.

## Fixas (não negociar)

| Regra | Por quê |
|---|---|
| **Nada de texto grande em destaque.** Sem números gigantes, sem "key takeaways" escritos grandes e sem bloco de parágrafo. Só se o usuário pedir (`deck_prefs.big_numbers = true`) | O slide é visual; texto grande compete com o dado e parece relatório |
| **Nenhum número em título**: título do slide e cabeçalho de painel, ≤ ~55 caracteres no título, uma linha. Inclui período (FY26, 2025) | O título diz a conclusão; o número vai no gráfico e o período, no itálico |
| **Cabeçalho de painel conta a história**: frase-conclusão em **uma linha** (14pt), com 1 ou 2 palavras-chave em negrito na cor, + itálico com o que o gráfico mostra, unidade e período (11pt) | Quem lê só os cabeçalhos entende o slide |
| **Título e cabeçalho que não cabem são encurtados, nunca reduzidos.** O título fica no tamanho do mestre, sem chegar no logo. Registre a troca em `plan.md` | Reduzir a fonte quebra a hierarquia entre os slides |
| **Dois níveis de texto por visual, nunca três.** Cada gráfico tem um cabeçalho e um itálico, sem rótulo ou "sub-subtítulo" extra. Dois gráficos sob a mesma ideia viram dois painéis, cada um com o seu cabeçalho | Terceiro nível repete o itálico e polui o topo do gráfico |
| **Sem bloco de notas na face do slide.** Definições e ressalvas vão para as notas do apresentador (`ss.footer(..., notes=...)`); no rodapé, só as fontes | O slide é visual; a ressalva é falada ou vai para o Q&A |
| **Sem colunas de texto ao lado do gráfico** (ano fiscal, escopo, base, descrição por linha). O essencial vai no itálico; o resto, nas notas do apresentador | Vira tabela colada no gráfico e compete com o dado |
| **Data label com um único estilo no slide:** retângulo arredondado, fundo escuro, texto branco bold 9pt. FOCUS na empresa-foco, PEER_DARK em terceiros, NEG em negativo. Nunca fundo claro com texto preto, nem a cor de uma série clara ou do ACCENT | Pills de cores e contrastes diferentes parecem erro |
| **Nem tudo é gráfico** | Lineup, posicionamento e conteúdo qualitativo funcionam melhor como imagem, ícone ou diagrama com um dado curto |
| **Tudo alinhado à grade do mestre** (`ss.cols`, `ss.rows`, `profile.json`) | Cabeçalhos dos painéis vizinhos na mesma altura, margens iguais |
| **Nada encosta nas zonas proibidas do mestre** (`grid.forbidden`: logos, curvas, faixas) | O mestre cobre essa área |
| **Cor com significado fixo** (tabela abaixo) | Quem lê aprende o código uma vez e o reaproveita no deck inteiro |
| **Evidência só com material real.** Foto, print, entrevista, citação e notícia nunca são inventados; o molde com rótulo cinza não vai para a entrega | A banca cobra a origem, e prova falsa derruba o deck |
| **Gráfico de barras nunca com só duas barras.** Dois valores viram dado direto: dois rótulos lado a lado com o período embaixo, dentro de outro painel | Duas barras gastam meio slide para dizer um número |
| **Linha sem marcador nos pontos.** Linha contínua, com o rótulo em cima dela; área em degradê embaixo dá corpo | Bolinha polui e parece gráfico padrão |
| **Fonte em todo slide, sempre simplificada:** `Sources: Company Data, Group Calculations.` As fontes detalhadas vão para as notas do apresentador | O rodapé não compete com o slide; o detalhe fica para o Q&A |
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
| Nível visual | rico / sóbrio | **rico** |

## Papéis de cor (`ss.FOCUS`…; hex vem do tema do mestre ou de `deck_prefs.palette`)

| Papel | Uso |
|---|---|
| `FOCUS` | empresa-foco, série principal |
| `FOCUS_TINT` | empresa-foco fora de destaque, "restante", regiões não destacadas |
| `ACCENT` | **único** destaque: anotação, colchete ou o ponto que importa. Segunda série usa `FOCUS_DARK` ou `FOCUS_TINT`; nunca fundo de data label |
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
| Cabeçalho de painel | 14pt, FG, com 1 ou 2 palavras-chave em negrito (`**assim**` em `ss.panel_header`) |
| Itálico do painel | 11pt itálico, MUTED |
| Data labels e pills | 9pt bold branco sobre fundo escuro (7.5 em mapa) |
| Legendas e descrições | 8–9pt, FG2 |
| Fontes no rodapé | 7pt, MUTED |

## Checklist visual (no PNG do PDF do PowerPoint)

- [ ] `scripts/checar_slide.py` sem ERRO
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
- [ ] Cada peça passa nos 4 testes (origem, destino, forma = conteúdo, função); no máximo um protagonista
- [ ] Nenhum gráfico de barras com só duas barras; nenhuma linha com marcador
- [ ] Nenhum item de "Reprovado pelo dono do deck"
- [ ] Tem algo que parece "do nada"? Se você precisa explicar por que a peça está ali, ela sai
- [ ] Lado a lado com os prints ★★★ escolhidos, o slide parece do mesmo nível
- [ ] Rodapé só com `Sources: Company Data, Group Calculations.`
- [ ] Notas e fontes detalhadas nas notas do apresentador
- [ ] Respeita `deck_prefs` (fundo, 3D, barras)
