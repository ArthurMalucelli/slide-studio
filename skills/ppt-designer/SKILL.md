---
name: ppt-designer
description: Turns a slide script (roteiro.md, usually from /ppt-researcher) into a finished equity-research .pptx on ANY master/template, using a recipe drawn from the best decks and a reference catalog of 22 competition decks, then validates it in a PowerPoint-exported PDF with a design-critic subagent. Accepts follow-ups like "ajusta X" that reuse the same script. Use when the user wants a slide built, redesigned or adjusted from a script or data ("/ppt-designer mestre.pptx roteiro.md", "monta o slide", "ajusta o slide").
argument-hint: <mestre.pptx> <roteiro.md>  |  ajusta "<pedido>"
---

# ppt-designer

Você é o **designer**. O roteiro traz o argumento e um banco de provas maior do que cabe. **Fixos:** a mensagem principal, os números e as ressalvas. **Decisão sua:** quais provas entram, em qual formato, quantos painéis, e o texto de títulos e cabeçalhos. Registre em `plan.md` o que escolheu e o que deixou de fora; o que sair e importar vai para as notas do apresentador.

Roteiro antigo, com blocos e ordem de corte, também serve: trate os blocos como banco de provas.

`SKILL_DIR` = a pasta deste SKILL.md. Tudo o que o designer usa mora nela:
- a biblioteca, em `SKILL_DIR/lib`;
- o exportador de PDF, em `SKILL_DIR/scripts`;
- o exemplo de montagem, em `SKILL_DIR/references/exemplo_componentes.py`. Ele mostra os mesmos painéis em duas grades diferentes; a grade sai do slide, não do exemplo.

Leia antes do primeiro slide da sessão:
- `references/RECEITA.md`: como montar um bom slide;
- `references/RULES.md`: regras e preferências;
- `references/COMPONENTS.md`: o que a biblioteca desenha e como;
- `references/PITFALLS.md`: bugs do PowerPoint já resolvidos.
- `references/catalogo/INDEX.md`: catálogo de mapas, profundidade, diagramas e elementos, com peças prontas.

## 0. Pedido de ajuste ("ajusta X", "muda Y")

Se já existe uma versão deste slide na conversa ou na pasta `slides/`:
- **Não refaça a pesquisa nem o intake.** Copie o script da última versão para `_v<N+1>`, mude só o que foi pedido e vá ao passo 5.
- **Se o ajuste for de conteúdo** (dado novo, mensagem diferente), edite o roteiro (`roteiro_v2.md`) e diga isso ao usuário.

## 1. Intake: uma vez por deck

Se a pasta de trabalho já tem `deck_prefs.json`, use-o e só confirme numa linha. Se não tem, faça uma chamada de AskUserQuestion:

1. **Slide mestre** (obrigatório): "Qual o caminho do .pptx/.potx com o slide mestre?" Pode já ter vindo em `$ARGUMENTS`. Sem mestre, não comece.
   - Na mesma chamada, peça o roteiro se ele não veio nos argumentos.
2. **Fundo:**
   - branco;
   - o do mestre (pode ser colorido ou escuro);
   - escuro.
3. **Barras e blocos de dados:**
   - planos;
   - 3D isométrico.
4. **Uso do 3D:**
   - só em ilustrações (escada de produtos, pirâmide de mercado);
   - também em dados;
   - nunca.
5. **Números grandes / key takeaways em destaque:**
   - "Não (padrão)";
   - "Sim, quando fizer sentido".
6. **Paleta:** "Cores do mestre (padrão)", "Quero escolher no Color Hunt" (peça uma tag, como `navy`, ou 4 códigos) ou "Mando a minha". `python3 SKILL_DIR/scripts/buscar_paleta.py <tag>` lista opções e avisa o que quebraria; `--hex` traduz a do usuário. Mostre as opções, e quem escolhe é o usuário. Grave o bloco em `deck_prefs.json` → `palette`.
7. **Nível visual:**
   - "Rico (padrão)": uma peça de profundidade discreta em todo slide de conteúdo;
   - "Sóbrio": sem peça, salvo pedido.

Grave em `deck_prefs.json`, na pasta de trabalho, junto com qualquer override de paleta ou fonte que o usuário pedir:
```json
{"master": "...", "background": "white", "bars": "flat", "use_3d": "illustration_only",
 "big_numbers": false, "visual": "rico", "palette": {}, "font": null}
```

## 2. Profile do mestre

```bash
python3 SKILL_DIR/lib/master_profile.py <mestre.pptx> <pasta>/_master
SKILL_DIR/scripts/export_pdf.sh <pasta>/_master/layouts_preview.pptx   # Windows: export_pdf.ps1
pdftoppm -r 60 -png <pasta>/_master/layouts_preview.pdf <pasta>/_master/layout
```

- **Olhe os PNGs dos layouts.** Eles mostram cada placeholder rotulado `[idx]` e as zonas proibidas em vermelho.
- **O profile é inferido e pode errar.** Confira e corrija **à mão** em `_master/profile.json`:
  - `grid.title` / `grid.subtitle`: qual placeholder é título e qual é subtítulo;
  - `grid.content_*`: a área útil;
  - `grid.forbidden`: logos, curvas e faixas onde nada pode encostar;
  - `palette.FOCUS`: a cor da empresa-foco. Se o mestre não traz a cor da empresa, pergunte ou use a cor da marca.
- **Tracker de seção:** se o mestre tem um layout ou master por seção (`Industry Overview`, `Business Model`...), escolha o da seção do slide. Pergunte se não souber.
- **Escolha o layout** com título + subtítulo e a estrutura mais próxima do que vai desenhar. Os placeholders de conteúdo vazios são removidos pelo `setup()`.

## 3. Receita (antes de escrever código)

Não copie slide nenhum. Siga `references/RECEITA.md`, passo a passo: argumento encadeado → uma prova por frase → grade → ligação → imagem real → cor → anotação → peso. Cada passo deixa uma linha em `plan.md`.

Veja antes as imagens de `references/reprovados/` e, em `references/gabarito.md`, 3 a 5 prints de propósito parecido, para ver a técnica. `scripts/medir_slide.py <pdf> <página>` serve para entender as medidas de uma peça.

**Conteúdo qualitativo:** se uma frase não tem prova numérica boa, dispare o agente de criatividade antes de desenhar (Agent tool, `subagent_type: general-purpose`, com `references/criatividade_prompt.md`). Ele devolve 3 representações. Escolha uma pelos testes da receita e registre em `plan.md` as três e o motivo. Se nenhuma passar, deixe simples e avise. Slide só de dados não precisa dele.

**Falta conteúdo?** Não invente, não decore e não troque gráfico por caixa de texto. Diga ao usuário o que falta no roteiro: a pergunta do passo 1 é a que mais revela roteiro fraco.

Peças prontas de `references/pecas_*.py` e `references/catalogo/INDEX.md` servem de apoio para desenhar um elemento, nunca para enfeitar.

## 4. Build

Crie `<pasta>/slides/build_<tema>_v1.py`:
- partir de `SKILL_DIR/references/exemplo_componentes.py`: copiar as funções de painel úteis e montar a grade que o slide pede (`cols`/`rows`), seja 2×2, 1+2, 3 colunas ou 1 painel;
- importar `slide_style as ss` e usar `ss.new_deck(mestre, prefs="deck_prefs.json", profile_dir="_master")`;
- usar a grade com `ss.cols(n)`, `ss.rows(n)` e `ss.panel_header(...)`; nunca coordenadas soltas;
- cores só pelos papéis (`ss.FOCUS`, `ss.ACCENT`, `ss.PEER`…), nunca hex solto;
- `ss.footer(s, "Sources: Company Data, Group Calculations.", notes="…")` sempre: o rodapé é só isso, e as notas e fontes detalhadas do roteiro vão para as notas do apresentador.
- um cabeçalho e um itálico por visual; se um bloco do roteiro tem dois gráficos, separe em dois painéis e registre os novos cabeçalhos no roteiro.

Gere o arquivo: `python3 build_<tema>_v1.py <mestre> slides/<Empresa>_<Tema>_v1.pptx`.

## 5. Validação: PDF do PowerPoint, não do LibreOffice

```bash
SKILL_DIR/scripts/export_pdf.sh slides/<arquivo>.pptx        # Mac (abre o PowerPoint se precisar)
pdftoppm -r 110 -png -singlefile slides/<arquivo>.pdf slides/<arquivo>
python3 SKILL_DIR/scripts/checar_slide.py slides/<arquivo>.pptx --profile _master/profile.json
```

- **O `checar_slide.py` é uma trava:** todo ERRO se corrige antes de seguir, e o que restar por decisão sua vai na entrega, sem chamar de pronto. Passar nele não quer dizer que o slide está bom.
- **Exportação falhou duas vezes:** pare e avise o usuário. Não fique repetindo: `export_pdf.sh` já tenta o que dá, e já exporta um por vez entre agentes.
- Abra o PNG e faça a sua checagem pelo checklist de `references/RULES.md`. Corrija e regenere.
- Ponha o PNG ao lado de 2 prints do gabarito, no mesmo tamanho. Se ele parece de outro campeonato, volte ao passo da receita que falhou.
- Depois dispare o **crítico de design**:
  - Agent tool, `subagent_type: general-purpose`;
  - prompt de `references/design_critic_prompt.md`, com o PNG, o roteiro, o `deck_prefs.json` e 2 prints do gabarito. Não passe sua justificativa do slide: ele precisa olhar sem contexto.
  - Corrija o que ele marcar como ALTA/MÉDIA; no máximo 2 rodadas. Se sobrar ALTA, diga isso ao usuário na entrega, sem chamar de pronto.
- **Sem PowerPoint:** exporte com LibreOffice (`soffice --headless --convert-to pdf`) e **avise o usuário** que gráficos nativos podem renderizar diferente.

## 6. Entrega

- Mande o .pdf e o .pptx (links) numa mensagem curta: o que foi feito e o problema visual mais grave que ainda resta, se houver.
- Ofereça o ajuste: "quer ajustar algo? (`ajusta …`)".
- Cada iteração vira uma versão nova (`_v2`, `_v3`…). A escolhida pelo usuário vira `_aprovada`.
- Se o usuário ensinar uma regra nova ("não quero X"), grave em `deck_prefs.json` → `"rules": [...]` e aplique dali em diante. Se ele reprovar uma peça, proponha levar a regra para `RULES.md` e um exemplo com dados fictícios para `references/reprovados/`; não publique o slide real dele.
