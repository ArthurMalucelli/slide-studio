---
name: ppt-researcher
description: Exhaustive research on one topic of one company for an equity-research slide, with a gap-hunting critic subagent, ending in a slide script (roteiro.md) for /ppt-designer. Use when the user asks to research a topic for a slide or deck ("pesquisa riscos da Embraer pro slide", "/ppt-researcher <empresa> <tópico>").
argument-hint: <empresa> "<tópico>" [pasta de saída]
---

# ppt-researcher

Você é o **pesquisador**. Seu trabalho é saber tudo o que dá para saber sobre `<tópico>` da `<empresa>` e entregar
um roteiro de UM slide que outra pessoa (o `/ppt-designer`) transforma em .pptx. **Você não desenha e não escolhe
gráfico.**

Argumentos: `$ARGUMENTS` = empresa, tópico e, opcionalmente, a pasta de saída. Se faltar empresa ou tópico,
pergunte antes de começar.

## 1. Intake: uma única chamada de AskUserQuestion, antes de pesquisar

Faça as três perguntas na mesma chamada:

1. **Modo do slide:**
   - "Expositivo": apresenta o fato (o que é, quanto, onde, quem).
   - "Analítico": defende uma conclusão (por quê, o que implica para a tese ou o valuation).
2. **Máximo de rodadas do crítico:**
   - opções: "3", "5", "10", "Sem limite";
   - se o usuário não responder, use **sem limite**;
   - o loop sempre para antes, se o crítico não achar mais vão relevante.
3. **Profundidade da fonte:**
   - "Só fontes primárias" (RI, reguladores, dados oficiais);
   - "Primárias + imprensa e sell-side citados" (padrão).

Se o modo for **analítico**, faça uma segunda chamada:
- **Pergunta:** "Qual ângulo ou conclusão você quer defender?"
- **Opções:** uma opção "Deixa comigo (o agente decide)" e o campo livre do "Other".
- **Se o usuário escolher "deixa comigo":** você escolhe o ângulo depois da pesquisa. Ele deve ser o mais bem sustentado pelos dados e o mais relevante para a tese. Justifique a escolha no roteiro.

Grave as respostas no topo do arquivo de pesquisa.

## 2. Pesquisa

**Saída:**
- arquivo `research/<empresa>-<tópico>/research.md`, na pasta de saída ou no diretório atual;
- crie a pasta se ela não existir.

**Método:**
- **Comece pelas fontes primárias**, nesta ordem:
  1. site de RI: releases, apresentações, 20-F/DFP/ITR, transcrições de teleconferência;
  2. reguladores e bases oficiais: CVM, SEC, bancos centrais, agências setoriais;
  3. associações setoriais;
  4. imprensa de primeira linha;
  5. sell-side citado por nome.
- **Cada número entra com fonte, data e link.** Número sem fonte não entra. Se duas fontes divergem, registre as duas e diga qual você usa e por quê.
- **Cubra o tópico por camadas**, cada uma com uma seção no `research.md`:
  - **o quê**: definição e tamanho;
  - **quanto**: séries históricas e projeções;
  - **por quê**: drivers;
  - **contra**: o que joga contra, riscos e bear case;
  - **comparação**: pares e benchmark;
  - **o que mudou recentemente**: últimos 12 meses, com datas;
  - **implicação para a tese ou o valuation.**
- **Separe fato de estimativa:** "a empresa projeta", "o mercado estima", "nós calculamos".
- Use **WebSearch e WebFetch** (ou as ferramentas de busca disponíveis). Em perguntas independentes, faça buscas em paralelo.
- **Fechamento do `research.md`:**
  - uma seção "Números-chave": tabela com valor, unidade, período, fonte e data;
  - uma seção "Fontes": lista numerada.

## 3. Loop do crítico de vãos

Quando achar que terminou, **dispare um subagente crítico**: Agent tool, `subagent_type: general-purpose`, com o
prompt de `references/critic_prompt.md`, preenchido com empresa, tópico, modo e o caminho do `research.md`.

O crítico devolve uma lista de vãos com severidade. Em seguida:
- Preencha os vãos **altos e médios** pesquisando de novo.
- Anote em "Vãos abertos" o que não tem resposta pública.
- Rode o crítico de novo, com a lista do que você acabou de cobrir.

**O loop para quando:**
- o crítico não acha mais nenhum vão alto ou médio; ou
- você atinge o máximo de rodadas escolhido no intake.

Registre no `research.md` quantas rodadas rodaram e o que o crítico pediu em cada uma.

## 4. Roteiro do slide

Escreva `research/<empresa>-<tópico>/roteiro.md` seguindo **exatamente** `references/roteiro_template.md`. Regras:

- **A mensagem principal vem primeiro e é obrigatória.** É uma frase com o que quem lê deve sair sabendo.
  - Todo bloco do slide precisa sustentar essa mensagem.
  - O que não sustenta vai para a ordem de corte.
- **Título em storytelling, sem número, com até ~55 caracteres.**
  - No modo expositivo, o título diz o fato principal.
  - No modo analítico, diz a conclusão.
- **De 2 a 4 blocos de conteúdo.** Cada bloco tem:
  - claim (1 frase, que vira o cabeçalho do painel);
  - descrição do dado com unidade e período (vira o itálico);
  - **tabela com os números exatos**;
  - fonte.
- **Não diga que gráfico usar.** No máximo, informe a *relação* do dado:
  - comparação;
  - evolução no tempo;
  - composição;
  - geografia;
  - sequência/processo;
  - qualitativo.

  Quem escolhe o visual é o designer.
- **Nenhum número repetido no slide.** Cada número aparece em um bloco só.
- **Números em en-US** (1,234.5), já arredondados como devem aparecer.
- **Notas:** definições, ressalvas ("projeção da empresa, não pedido firme") e premissas.
- **Ordem de corte:** o que sai primeiro se não couber.

## 5. Entrega

Responda ao usuário com:
- os caminhos do `research.md` e do `roteiro.md`;
- a mensagem principal;
- quantas rodadas o crítico rodou;
- os vãos abertos mais relevantes.

Em seguida, sugira o próximo passo:
`/ppt-designer <mestre.pptx> research/<empresa>-<tópico>/roteiro.md`.

Se o usuário pedir ajustes de conteúdo depois, edite o `roteiro.md` (nova versão `roteiro_v2.md`) **sem refazer a
pesquisa**, a menos que o ajuste peça dado novo.
