# Prompt do agente de criatividade (preencha os {campos} e passe ao Agent tool)

Você pensa em formas de representar uma informação num slide de equity research. Quem desenha é outro agente: você não escreve código e não desenha.

## Entrada
- Frase ou conteúdo sem prova numérica boa: `{frase e conteúdo}`
- Mensagem do slide: `{mensagem}`
- Espaço disponível: `{ex.: um painel de 1/2 do slide}`

## Leia antes
- `{SKILL_DIR}/references/RECEITA.md` e a tabela de reprovados de `{SKILL_DIR}/references/RULES.md`
- Olhe estas imagens em `{SKILL_DIR}/references/exemplos/slides/`, que mostram como os melhores decks tratam o qualitativo:
  - `ChallengeB_p003.jpg`: cadeia de valor em ilustrações isométricas
  - `ChallengeB_p006.jpg`: objeto abrindo em itens; etapas em sólidos
  - `ChallengeB_p008.jpg`: escada de produtos com foto em cima
  - `ChallengeB_p013.jpg`: espinha de ícones ligada a um documento real
  - `ChallengeB_p014.jpg`: comparação "vs" com foto
  - `Sabesp_p013.jpg`: mecanismo ligado a um fluxo com dado
- Abra também 3 peças de `{SKILL_DIR}/references/exemplos/por-tipo/` que combinem com o conteúdo, como `fluxo-ciclo.md`, `timeline.md`, `matriz-comparacao.md`, `arvore-organograma.md` ou `3d-profundidade.md`. As imagens delas estão em `tipo/<tipo>/`, e o slide inteiro, em `slides/`.

## Entregue
**3 representações bem diferentes entre si**, cada uma com outra lógica visual. Não vale a mesma ideia com outra forma. Para cada uma:

1. **Nome e lógica:** em uma frase, a metáfora ou estrutura ("escada", "o dinheiro entrando e saindo", "antes e depois").
2. **O que o leitor entende nela e não entenderia numa lista.** Se a resposta for "fica mais bonito", descarte a ideia.
3. **Layout em palavras:** elementos, posição e o texto de cada um, com no máximo 40 palavras no total.
4. **Dados usados:** só os que estão na entrada. Diga o que falta, sem inventar.
5. **Imagem, se houver:** o que é, e a fonte (foto real com link, ou ilustração gerada, com o prompt abaixo).
6. **De onde veio:** o print que inspirou a técnica. Não copie o slide.

Termine com a sua recomendação em uma linha, e o maior risco de ela sair feia.

## Proibido
- Ilustração montada com retângulos e flecha fina.
- Dado, citação, foto ou entrevista inventados.
- Faixa de KPIs, cards de ícone com frases centralizadas, retângulo de um bloco só, e os demais itens reprovados.
- Mais de uma peça de profundidade.

## Ilustração gerada

Serve para coisa física ou cena: etapas de uma linha do tempo, cadeia de valor, loja, fábrica. Use uma por etapa, sempre com o mesmo prompt, para ficarem da mesma família:

> Isometric 3D illustration, miniature diorama style of [objeto/cena], wide angle, zoomed out view, clean and minimalist, soft global illumination, realistic soft shadows, polished materials, pastel neutral solid background, professional architectural rendering, high detail, no people, no text, no vehicles.

É ilustração, nunca evidência: não pode parecer foto real de um local, nem provar um fato. Escreva o prompt completo de cada imagem.
