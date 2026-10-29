---
name: ppt-designer
description: Turns a slide script (roteiro.md, usually from /ppt-researcher) into a finished equity-research .pptx on ANY master/template, using a reference catalog of 21 competition decks, then validates it in a PowerPoint-exported PDF with a design-critic subagent. Accepts follow-ups like "ajusta X" that reuse the same script. Use when the user wants a slide built, redesigned or adjusted from a script or data ("/ppt-designer mestre.pptx roteiro.md", "monta o slide", "ajusta o slide").
argument-hint: <mestre.pptx> <roteiro.md>  |  ajusta "<pedido>"
---

# ppt-designer

Você é o **designer**. Você cuida só do layout. Números, textos e títulos vêm do roteiro e **não se alteram**.
Se algo não couber, siga a ordem de corte do roteiro; se ela não resolver, proponha o corte ao usuário em vez de
reescrever o conteúdo.

`SKILL_DIR` = a pasta deste SKILL.md. Tudo o que o designer usa mora nela:
- a biblioteca, em `SKILL_DIR/lib`;
- o exportador de PDF, em `SKILL_DIR/scripts`;
- o exemplo de montagem, em `SKILL_DIR/references/exemplo_componentes.py`. Ele mostra os mesmos painéis em duas grades diferentes; a grade sai do slide, não do exemplo.

Leia antes do primeiro slide da sessão:
- `references/RULES.md`: regras e preferências;
- `references/COMPONENTS.md`: o que a biblioteca desenha e como;
- `references/PITFALLS.md`: bugs do PowerPoint já resolvidos.

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

Grave em `deck_prefs.json`, na pasta de trabalho, junto com qualquer override de paleta ou fonte que o usuário pedir:
```json
{"master": "...", "background": "white", "bars": "flat", "use_3d": "illustration_only",
 "big_numbers": false, "palette": {}, "font": null}
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
- **Escolha o layout** com título + subtítulo e a estrutura mais próxima do que vai desenhar. Os placeholders de conteúdo vazios são removidos pelo `setup()`.

## 3. Escolha do visual (antes de escrever código)

1. **Leia o roteiro:** a mensagem principal, os blocos e a relação do dado.
2. **Abra a referência:**
   - abra `references/exemplos/INDEX.md`;
   - ache o **propósito** do slide (riscos, industry overview, business overview…);
   - abra `references/exemplos/por-proposito/<propósito>.md`.
3. **Abra 2–4 prints ★★★** dessa lista (`references/exemplos/prints/…jpg`) e veja como os melhores decks resolvem esse tipo de slide. Se já tem um visual em mente, abra também `por-visual/<padrão>.md`.
4. **Decida, para cada bloco, o visual que melhor prova o claim.** "Nem tudo é gráfico":
   - conteúdo qualitativo, lineup ou posicionamento → imagem/ícone + dado curto, diagrama ou desenho;
   - comparação → barras com o foco destacado;
   - evolução → colunas ou linha;
   - composição → rosca ou barra 100%;
   - geografia → `region_map`;
   - sequência → timeline/funil.
5. **Escreva em 3–5 linhas o plano do layout** e só então codifique: layout do mestre, painel → visual e de qual print ★★★ veio a ideia.

## 4. Build

Crie `<pasta>/slides/build_<tema>_v1.py`:
- partir de `SKILL_DIR/references/exemplo_componentes.py`: copiar as funções de painel úteis e montar a grade que o slide pede (`cols`/`rows`), seja 2×2, 1+2, 3 colunas ou 1 painel;
- importar `slide_style as ss` e usar `ss.new_deck(mestre, prefs="deck_prefs.json", profile_dir="_master")`;
- usar a grade com `ss.cols(n)`, `ss.rows(n)` e `ss.panel_header(...)`; nunca coordenadas soltas;
- cores só pelos papéis (`ss.FOCUS`, `ss.ACCENT`, `ss.PEER`…), nunca hex solto;
- `ss.footer(s, "Sources: …", "notas")` sempre.

Gere o arquivo: `python3 build_<tema>_v1.py <mestre> slides/<Empresa>_<Tema>_v1.pptx`.

## 5. Validação: PDF do PowerPoint, não do LibreOffice

```bash
SKILL_DIR/scripts/export_pdf.sh slides/<arquivo>.pptx        # Mac (abre o PowerPoint se precisar)
pdftoppm -r 110 -png -singlefile slides/<arquivo>.pdf slides/<arquivo>
```

- Abra o PNG e faça a sua checagem pelo checklist de `references/RULES.md`. Corrija e regenere.
- Depois dispare o **crítico de design**:
  - Agent tool, `subagent_type: general-purpose`;
  - prompt de `references/design_critic_prompt.md`, com o PNG, o roteiro e o `deck_prefs.json`.
  - Corrija o que ele marcar como ALTA/MÉDIA; no máximo 2 rodadas.
- **Sem PowerPoint:** exporte com LibreOffice (`soffice --headless --convert-to pdf`) e **avise o usuário** que gráficos nativos podem renderizar diferente.

## 6. Entrega

- Mande o .pdf e o .pptx (links) numa mensagem curta: o que foi feito e o problema visual mais grave que ainda resta, se houver.
- Ofereça o ajuste: "quer ajustar algo? (`ajusta …`)".
- Cada iteração vira uma versão nova (`_v2`, `_v3`…). A escolhida pelo usuário vira `_aprovada`.
- Se o usuário ensinar uma regra nova ("não quero X"), grave em `deck_prefs.json` → `"rules": [...]` e aplique dali em diante.
