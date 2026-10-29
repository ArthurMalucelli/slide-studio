# slide-studio

Plugin do Claude Code para montar slides de equity research de **qualquer empresa**, com **qualquer slide mestre**, em duas etapas:

| Skill | O que faz | Entrega |
|---|---|---|
| `/ppt-researcher <empresa> "<tópico>"` | Pesquisa tudo sobre o tópico em fontes primárias. Um subagente crítico caça vãos até não sobrar nenhum relevante, e no fim o roteiro do slide é escrito | `research.md` + `roteiro.md` |
| `/ppt-designer <mestre.pptx> <roteiro.md>` | Lê o mestre e escolhe o visual olhando um catálogo de 973 slides de 21 decks de competição. Depois monta o .pptx e valida no PDF do PowerPoint, com um crítico de design | `.pptx` + `.pdf` |

Depois da v1, peça `ajusta …` (ex.: "ajusta: tira o texto de baixo do gráfico da direita"). O designer gera a v2 com o mesmo roteiro, sem pesquisar de novo.

## Jeito rápido: cole isto no Claude Code

Abra o Claude Code (app desktop, aba **Code**, ou `claude` no terminal), cole o prompt abaixo e mande. O Claude faz a instalação inteira, confere o que falta e te diz o próximo passo.

```text
Quero usar o plugin slide-studio (https://github.com/ArthurMalucelli/slide-studio) para montar slides de
equity research. Faça a instalação completa por mim, rodando os comandos você mesmo:

1. Instale o plugin com o CLI:
   claude plugin marketplace add ArthurMalucelli/slide-studio
   claude plugin install slide-studio@slide-studio
2. Confira o Python 3 e instale as bibliotecas: pip install python-pptx lxml pillow
   (se o pip reclamar de ambiente gerenciado, use --user ou um venv, e me diga qual usou).
3. Confira se o pdftoppm (Poppler) existe. Se não existir, instale: no Mac `brew install poppler`; no Windows
   `choco install poppler` ou `winget install oschwartz10612.Poppler`. Se precisar de senha de administrador, me
   passe o comando para eu rodar.
4. Confira se o Microsoft PowerPoint está instalado. Se não estiver, me avise que a validação vai usar o
   LibreOffice e pode sair diferente.
5. No fim, me mostre uma tabela com o que ficou OK e o que falta eu fazer. Diga também que preciso abrir uma
   sessão nova do Claude Code para as skills aparecerem.

Depois, me explique em 5 linhas como usar /ppt-researcher e /ppt-designer.
```

Na **sessão nova**, para fazer um slide, cole e adapte:

```text
/ppt-researcher <Empresa> "<tópico do slide>"
```
Responda as perguntas: expositivo ou analítico, e quantas rodadas o crítico pode rodar. Quando o roteiro estiver pronto:

```text
/ppt-designer <caminho do seu slide mestre .pptx> research/<Empresa>-<tópico>/roteiro.md
```
Responda as preferências: fundo, 3D e números grandes. Ao receber o slide, peça ajustes em português normal: `ajusta: tira o texto de baixo do gráfico da direita`.

> A fonte do seu slide mestre precisa estar instalada no computador (ex.: Montserrat, no Google Fonts). Sem ela, o PDF sai com outra fonte.

## Instalação manual (se preferir fazer você mesmo)

1. **Plugin.** No Claude Code (terminal ou app desktop, aba Code):
   ```
   /plugin marketplace add ArthurMalucelli/slide-studio
   /plugin install slide-studio@slide-studio
   ```
2. **Python 3** com as bibliotecas:
   ```bash
   pip install python-pptx lxml pillow
   ```
3. **Poppler** (`pdftoppm`, para o Claude ver o slide):
   - Mac: `brew install poppler`
   - Windows: `choco install poppler` ou https://github.com/oschwartz10612/poppler-windows
4. **Microsoft PowerPoint**, para validar. Sem ele, o designer usa o LibreOffice e avisa que gráficos podem sair diferentes.
5. **A fonte do seu mestre instalada** (ex.: Montserrat no Google Fonts). Sem ela, o PDF troca a fonte.

## Uso

```
/ppt-researcher Embraer "riscos"
```
1. **Perguntas iniciais:**
   - o slide é **expositivo** (apresenta fatos) ou **analítico** (defende uma conclusão)?
   - se for analítico, qual ângulo? Pode deixar o agente decidir;
   - quantas rodadas o crítico pode rodar? Sem resposta = sem limite.
2. **Pesquisa e crítica:** o pesquisador pesquisa. Quando acha que terminou, um crítico lista o que falta, e o ciclo se repete.
3. **Saída:** sai `research/Embraer-riscos/roteiro.md`. O roteiro traz:
   - a **mensagem principal** do slide;
   - título, subtítulo e blocos com os números e as fontes.

   Ele **não** diz que gráfico usar.

```
/ppt-designer ~/Desktop/MeuMestre.pptx research/Embraer-riscos/roteiro.md
```
1. **Preferências (uma vez por deck, ficam em `deck_prefs.json`):**
   - caminho do mestre;
   - fundo;
   - barras planas ou 3D;
   - uso do 3D;
   - números grandes em destaque: **padrão não**.
2. **Mestre:** o designer lê o mestre (grade, cores, zonas proibidas) e mostra os layouts.
3. **Referências:** abre o catálogo pelo propósito do slide (ex.: `riscos`) e olha os melhores exemplos.
4. **Build e validação:** monta, exporta o PDF pelo PowerPoint, revisa com o crítico e entrega.

```
ajusta: deixa o mapa da esquerda na largura inteira
```

Se o Claude não reconhecer `/ppt-researcher`, use o nome com prefixo: `/slide-studio:ppt-researcher`.

## O que tem aqui

| Pasta | Conteúdo |
|---|---|
| `skills/ppt-researcher/` | Instruções do pesquisador, prompt do crítico de vãos, modelo de roteiro |
| `skills/ppt-designer/` | Instruções do designer, regras, componentes, armadilhas, prompt do crítico de design |
| `skills/ppt-designer/references/exemplos/` | Catálogo: `INDEX.md`, `por-proposito/`, `por-visual/`, `prints/` (973 slides) e os 21 PDFs |
| `skills/ppt-designer/lib/slide_style.py` | Biblioteca de componentes: gráficos nativos com pills, combo coluna+linha, rosca, mapa por região, 3D isométrico, legendas, rodapé |
| `skills/ppt-designer/lib/master_profile.py` | Lê qualquer mestre e gera `profile.json`: grade, título/subtítulo, rodapé, zonas proibidas, paleta do tema |
| `skills/ppt-designer/references/exemplo_componentes.py` | Exemplo de montagem (dados fictícios): os mesmos painéis em 2 grades diferentes, com qualquer mestre |
| `skills/ppt-designer/scripts/export_pdf.sh` / `.ps1` | Exportam .pptx → PDF pelo PowerPoint (Mac / Windows) |

Teste rápido, sem Claude:
```bash
python3 skills/ppt-designer/references/exemplo_componentes.py MeuMestre.pptx teste.pptx 0
```

## Aviso sobre o catálogo

Os decks de `references/exemplos/` são de equipes de competições de equity research e entram **só como referência de design**. Use o catálogo para aprender o layout; não copie conteúdo.
