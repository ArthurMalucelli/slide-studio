# Receita de um bom slide

Tirada dos três decks que o dono considera os melhores: Sabesp, Nubank e ChallengeB. Não copie nenhum slide: siga os passos com o seu conteúdo. Os exemplos entre parênteses mostram a técnica (`ChallengeB p.7` = `exemplos/slides/ChallengeB_p007.jpg`).

Cada passo deixa uma linha em `plan.md`. Faça nesta ordem e só escreva código no fim.

## 1. Escreva o argumento em 2 a 4 frases encadeadas

O roteiro traz um rascunho: reescreva se precisar, mantendo a mensagem. Cada frase é um cabeçalho de painel, e lidas em voz alta elas dão o argumento do slide. Os painéis se respondem:

> "...so who pays the bill until then?" → "...and Embraer's cash flow can carry it" (ChallengeB p.7)
> "Airbus and Boeing own the large-jet market..." → "...so below 150 seats only two Western makers remain..." → "...and every Embraer niche has only a handful of rivals" (ChallengeB p.14)

Se as frases não se encadeiam, o slide vai parecer uma pilha de gráficos. Reescreva; se o banco de provas não sustentar, avise o usuário. Cada cabeçalho cabe em uma linha, com 1 ou 2 palavras-chave em negrito.

## 2. Dê a cada frase uma prova de um único tipo

Escolha no banco de provas do roteiro. Use a tabela abaixo como ponto de partida; não use todo o banco.

| A frase diz | Prova |
|---|---|
| Algo cresceu ou caiu | Colunas; com taxa ou margem, colunas + linha em cima |
| Quem é maior | Barras horizontais ordenadas |
| Do que é feito | Rosca pequena, pizza, blocos com largura = parte, com 3 ou mais partes |
| Onde está | Mapa, um só |
| Como funciona ou a sequência | Diagrama de etapas, cadeia com ícones, timeline com datas reais |
| O que é o produto | Foto real recortada + poucos dados |

**Varie os tipos.** Dois gráficos do mesmo tipo já pesam: barras, colunas + linha e área, mais a cadeia ilustrada, formam um bom slide (ChallengeB p.3).

## 3. A grade sai do número de provas

| Provas | Grade | Exemplo |
|---|---|---|
| 2 | Dois painéis largos, altura inteira | ChallengeB p.7 |
| 3 | Um grande e dois pequenos, ou três colunas com uma faixa embaixo | ChallengeB p.2, p.5 |
| 3 + 1 diferente | 2×2 com 3 gráficos e o quarto de outra natureza | ChallengeB p.3, p.4, p.10 |

**Para ver a técnica:** `exemplos/por-formato/` lista os slides por número de quadrantes (nos 1.647 do catálogo, 2 e 3 são os mais comuns, e 4 bem menos), e `exemplos/por-tipo/` lista as peças por tipo, com `★` primeiro. Quadrante recortado perde a ligação com os vizinhos: abra o slide inteiro.

**No máximo 3 gráficos por slide.** Quatro gráficos em quadrantes é demais, segundo o dono. O quarto quadrante, quando existe, é outra coisa: ilustração, cadeia de valor, timeline, citação ou diagrama, ou texto curto preso a um dado. Painel só de frases soltas continua reprovado.

Painéis podem ter altura diferente quando uma prova tem muito mais dado; a grade continua alinhada. Uma prova por painel, com tabela e mapa contando como prova. Os blocos ficam alinhados, e nada entra "onde sobrou espaço".

## 4. Dê profundidade ao slide, com uma peça

Slide totalmente plano sai sem sal: esse erro já foi reprovado várias vezes. No modo visual rico, todo slide de conteúdo tem profundidade visível. Olhe as frases do passo 1:

1. **Padrão, em todo slide:** dois painéis ou mais com volume, ligados por um bloco atrás (`painel_volume`, `ponte_volume`), ou a dobra. Cabeçalho, itálico e gráfico dentro. É a opção mais aprovada e não depende de relação entre números.
2. **Um número abre no que há dentro dele?** Some a cunha ao padrão: é a combinação mais aprovada (última coluna de um painel com volume abrindo em cascata no painel vizinho). Ela sai de um total ou segmento e termina na borda inteira de um painel que detalha esse número. Ligar uma linha à mesma linha de outro gráfico não é abertura, e cunha terminando em rótulo ou no ar é reprovada. Sem isso, nada de cunha.
3. **Etapas ou degraus?** Use o sólido, com o conteúdo dentro.

Em dúvida, fique no padrão. Ele nunca foi reprovado por "aparecer do nada".

| Peça | Como é feita | Exemplo |
|---|---|---|
| Cunha do dado para o detalhe | Sai colada na última barra, curta, e abre na composição daquele mesmo número | ChallengeB p.9: barra de 3Q26 (35.7) → pizza do backlog |
| Painéis com volume **(preferida do dono)** | Painéis cinza (`painel_volume`) com sombra dura, ligados por um bloco atrás (`ponte_volume`). Cabeçalho, itálico e gráfico ficam dentro | ChallengeB p.10, p.14 |
| Dobra entre planos | Painéis em planos diferentes, com trapézio entre eles (`dobra`). Também com o texto dentro | ChallengeB p.7, Sabesp p.13 |
| Cunha da imagem para o que ela contém | Sai do objeto e abre em 3 itens | ChallengeB p.6 |
| Fio tracejado | Liga um item a outro painel | ChallengeB p.13; Sabesp p.13 |
| Sólidos | Só quando o sólido é o conteúdo: etapas ou degraus, com texto dentro | ChallengeB p.6 (etapas), p.8 (degraus com jato em cima) |

**A cunha encosta no dado.** A ponta estreita tem a altura exata da barra, do topo até o eixo, sem vão e sem passar do eixo. A caixa do gráfico não dá essa posição: exporte, rode `scripts/medir_slide.py` no seu próprio PDF, pegue o retângulo da barra pela cor e reconstrua. Depois olhe a junção ampliada, a 300 dpi.

**A peça é discreta.** Cinza claro ou tom claro da origem, nunca cor cheia em área grande, e pequena perto dos painéis que liga. Ela não pode ser o que mais chama atenção no slide. No modo sóbrio, o slide pode ficar sem peça.

## 5. Use imagem real quando o assunto é uma coisa

Mockup e ilustração gerados ganham de foto real de produto, que o dono reprovou três vezes por ficar "zoada". Ela ocupa entre 3% e 15% do slide.

**A imagem é parte da prova, ou sai.** O jato aparece porque o painel compara aquele modelo. Foto de uma loja ao lado de um gráfico que não fala dela é "foto do nada", mesmo sendo real. Assunto financeiro ou de número costuma ficar sem imagem, e tudo bem.

- **Nunca monte um prédio ou uma máquina com retângulos.**
- **Produto:** mockup gerado, com o nome da marca quando o slide é sobre ela (`gerar_imagem.py --mockup --marca Nome`). Confira a grafia ampliada, e diga nas notas do apresentador que é ilustrativo. Foto de produto recortada não entra.
- **Foto real** só de pessoa citada ou documento, com origem nas notas do apresentador.
- **Ilustração gerada** serve para etapas, cadeia de valor e cenas: `scripts/gerar_imagem.py "<cena>" saida.png` usa o prompt isométrico padrão e recorta o fundo. Só as que entram no slide: cada uma gasta da conta do Codex do usuário. É ilustração, nunca evidência.
- **Veículo ou máquina anotada:** `gerar_imagem.py --objeto "<objeto>" saida.png`, de perfil e nivelado. Imagem em perspectiva parece torta. Confira ampliada se a linha do objeto está na horizontal; se não estiver, gere de novo.
- **Padronize:** todas quadradas, com o mesmo tamanho, o mesmo ângulo e a mesma escala de objeto no slide. Olhe cada uma ampliada: nada cortado, nada torto. Refaça a que destoar.
- Se nada disso der, use ícone de um traço e avise o usuário do que faltou.
- Foto de pessoa e citação só com origem real. Nunca invente.

## 6. Cor: uma família com três tons

**Todo gráfico do slide usa as mesmas cores:** a série principal na cor principal em todos os gráficos, e a segunda série no tom claro. Cinza é só para terceiros **ao lado** da empresa-foco no mesmo gráfico; um gráfico inteiro em cinza ao lado de gráficos azuis parece erro, mesmo que todos sejam terceiros. Escuro, médio e claro da mesma família fazem quase tudo (ChallengeB: marinho, azul, azul claro; Sabesp: marinho, azul, ciano). Cinza para o que é terceiro. Um acento pontual só onde houver alerta. O painel de fundo, quando existe, é um cinza quase branco, igual em todo o slide.

## 7. Anote o gráfico, sem soltar texto

O número mora no gráfico, com rótulo no estilo único. O destaque é uma marca presa ao dado:

- tracejado em volta da região, com a frase ou o número dentro (ChallengeB p.7, p.9; Sabesp p.18);
- colchete somando barras com o resultado ao lado: "Top 5 concentrate 250 units" (ChallengeB p.10);
- delta na ponta da linha: "-301 vs 2018" (ChallengeB p.3).

Toda anotação aponta para um dado que está ali. Frase de conclusão solta embaixo do slide não existe.

## 8. Corte texto até caber no orçamento

O erro mais comum é texto demais, e o dono reprova como "muito crowded". Medido no PDF, com o mesmo critério:

| Slide | Palavras | Dados | Nota do dono |
|---|---|---|---|
| ChallengeB p.3, p.7, p.9 | 85 a 96 | 25 a 44 | "bem legais" |
| Sabesp p.18 | 152 | 64 | "lindos" |
| Nossos reprovados como crowded | 125 a 295 | 42 a 128 | "muito crowded" |
| Nosso reprovado como sem sal | 72 | 12 | "meio sem sal" |

**Orçamento: 85 a 130 palavras e 25 a 50 dados.** O limite do `checar_slide.py` é 150 palavras e 60 dados, e abaixo de 20 dados ele acusa slide pobre.

Onde cortar primeiro:
- **Itálico:** até ~50 caracteres. Só métrica, unidade e período do gráfico logo abaixo, como `Revenue, US$m, FY19–26`. Nada de resultado, número em destaque ou ressalva: ressalva vai para as notas, número vai no gráfico.
- **Anotação no gráfico:** no máximo uma por painel, com até 4 palavras.
- **Texto embaixo de gráfico ou em cartão:** corte. Se o dado importa, ele é o gráfico.
- **Rótulo em toda barra:** quando há muitas barras, rotule só as pontas e o destaque.
- **Subtítulo:** uma ideia, sem lista de números.
- **Tabela:** menos colunas; tabela de palavras nunca.

Quatro painéis cabem em 90 palavras (ChallengeB p.3): o texto em volta pesa tanto quanto o número de gráficos.

## 9. Compare e corrija

Exporte, rode `scripts/checar_slide.py` e ponha o PNG ao lado de 2 prints de `gabarito.md`, de preferência do ChallengeB, que usa um mestre parecido. A pergunta não é "ficou igual?", é "parece do mesmo campeonato?". Se não, volte ao passo que falhou.
