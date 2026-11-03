# Receita de um bom slide

Tirada dos três decks que o dono considera os melhores: Sabesp, Nubank e ChallengeB. Não copie nenhum slide: siga os passos com o seu conteúdo. Os exemplos entre parênteses mostram a técnica (`ChallengeB p.7` = `exemplos/prints/ChallengeB_p007.jpg`).

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

**Varie os tipos.** Um slide de 4 painéis tem 3 ou 4 tipos diferentes: barras, colunas + linha, cadeia ilustrada e área (ChallengeB p.3); colunas, linhas, pizza e barras (ChallengeB p.9). Até um painel pode não ser gráfico, se os outros provarem com dado.

## 3. A grade sai do número de provas

| Provas | Grade | Exemplo |
|---|---|---|
| 2 | Dois painéis largos, altura inteira | ChallengeB p.7 |
| 3 | Três colunas com uma faixa embaixo, ou um painel largo em cima e dois embaixo | ChallengeB p.2, p.5 |
| 4 | 2×2 com painéis iguais | ChallengeB p.3, p.9; Sabesp p.18 |

Nunca mais que 4. Uma prova por painel, com tabela e mapa contando como prova. Os blocos ficam alinhados, e nada entra "onde sobrou espaço".

## 4. Agora procure a ligação (profundidade)

Olhe as frases do passo 1: alguma abre um número de outra? Se sim, desenhe **uma** peça entre os dois painéis. O conteúdo já existe dos dois lados: a peça só mostra a relação.

| Peça | Como é feita | Exemplo |
|---|---|---|
| Cunha do dado para o detalhe | Sai colada na última barra, curta, e abre na composição daquele mesmo número | ChallengeB p.9: barra de 3Q26 (35.7) → pizza do backlog |
| Dobra entre painéis | Dois painéis cinza muito claros (`F4F5F7`) com faixa estreita de 0.37 pol em cinza (`D3D5DA`) | ChallengeB p.7, p.10 |
| Cunha da imagem para o que ela contém | Sai do objeto e abre em 3 itens | ChallengeB p.6 |
| Fio tracejado | Liga um item a outro painel | ChallengeB p.13; Sabesp p.13 |
| Sólidos | Só quando o sólido é o conteúdo: etapas ou degraus, com texto dentro | ChallengeB p.6 (etapas), p.8 (degraus com jato em cima) |

**A peça é discreta.** Cinza claro ou tom claro da origem, nunca cor cheia em área grande, e pequena perto dos painéis que liga. Ela não pode ser o que mais chama atenção no slide. Sem relação no conteúdo, o slide fica sem peça.

## 5. Use imagem real quando o assunto é uma coisa

Quase metade dos slides do ChallengeB tem imagem real: jato recortado, retrato com citação, ilustração isométrica de boa qualidade, print de documento. Ela ocupa entre 3% e 15% do slide: complementa o dado, sem ser o fundo.

- **Nunca monte um prédio ou uma máquina com retângulos.**
- **Busque a imagem de verdade,** de fonte pública, e registre a origem nas notas do apresentador. Se não conseguir, use ícone de um traço e avise o usuário do que faltou.
- Foto de pessoa e citação só com origem real. Nunca invente.

## 6. Cor: uma família com três tons

Escuro, médio e claro da mesma família fazem quase tudo (ChallengeB: marinho, azul, azul claro; Sabesp: marinho, azul, ciano). Cinza para o que é terceiro. Um acento pontual só onde houver alerta. O painel de fundo, quando existe, é um cinza quase branco, igual em todo o slide.

## 7. Anote o gráfico, sem soltar texto

O número mora no gráfico, com rótulo no estilo único. O destaque é uma marca presa ao dado:

- tracejado em volta da região, com a frase ou o número dentro (ChallengeB p.7, p.9; Sabesp p.18);
- colchete somando barras com o resultado ao lado: "Top 5 concentrate 250 units" (ChallengeB p.10);
- delta na ponta da linha: "-301 vs 2018" (ChallengeB p.3).

Toda anotação aponta para um dado que está ali. Frase de conclusão solta embaixo do slide não existe.

## 8. Confira o peso

Medido no PDF dos 13 slides de conteúdo do ChallengeB: 26 a 78 números, com mediana 55, contando anos e rótulos, quase todos dentro de gráficos; 80 a 250 palavras fora dos gráficos.

- Abaixo de ~15 dados, fora anos e rodapé, o slide está pobre: `checar_slide.py` acusa, e você diz ao usuário o que falta.
- Muitos números não pesam dentro de gráficos. Pesam em chips soltos e painéis aninhados.

## 9. Compare e corrija

Exporte, rode `scripts/checar_slide.py` e ponha o PNG ao lado de 2 prints de `gabarito.md`, de preferência do ChallengeB, que usa um mestre parecido. A pergunta não é "ficou igual?", é "parece do mesmo campeonato?". Se não, volte ao passo que falhou.
