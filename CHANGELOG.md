# Changelog

## 0.6.1

- Todo gráfico do slide usa a mesma cor principal; o verificador barra gráfico só em cinza ao lado de gráficos em cor.
- `gerar_imagem.py --objeto`: veículo ou máquina de perfil e nivelado.

## 0.6.0

- Novo catálogo em `references/exemplos/`: 1.647 slides por número de quadrantes e 980 peças por tipo, nas cores originais, com `catalogo.json` para filtrar.

## 0.5.0

- Nova `references/RECEITA.md`: como montar um bom slide, em 9 passos, tirada de Sabesp, Nubank e ChallengeB. O designer não copia slides.
- O roteiro vira argumento encadeado + banco de provas. Mensagem, números e ressalvas são fixos; o designer escolhe as provas, o formato e o texto.
- Novo crítico de roteiro: lê só o roteiro e pergunta se ele dá um bom slide.
- Uma peça de profundidade discreta por slide: cunha quando um número abre em outro, dobra entre painéis ligados. Cunha e sólido passam em 4 testes (origem, destino, forma = conteúdo, função).
- Orçamento de texto: 85 a 130 palavras e 25 a 50 dados por slide, com limite no verificador.
- Novo `scripts/checar_slide.py`: trava para colisão de texto, título, logo, chips soltos, gráficos com 1 ou 2 categorias, linha com 2 pontos e pouco dado.
- Exportação em fila entre agentes, e por cópia própria: nunca mais exporta nem fecha outro deck que esteja aberto.
- `references/reprovados/` e `references/gabarito.md`; ChallengeB entra no catálogo (22 decks, 987 slides).
- Nunca gráfico de barras com só duas barras; linha sem marcador nos pontos; rodapé sempre `Sources: Company Data, Group Calculations.`
- No máximo 3 gráficos por slide. Painéis com volume são a profundidade padrão, e a cunha só entra com abertura real.
- Agente de criatividade para conteúdo qualitativo; `gerar_imagem.py`, `buscar_paleta.py` e `validar_pptx.py`.
- `references/aprovados/`, com peças aprovadas e dados fictícios.
- `panel_header` aceita **palavra-chave**; novos `beam_from_mark` e `dobra`.

## 0.4.1

- Todo slide passa a levar ao menos uma peça do catálogo, salvo no novo modo `visual = "sóbrio"`.
- O plano de layout nomeia a peça, a função e o recorte de origem.
- O crítico de design marca como grave o slide sem peça do catálogo.

## 0.4.0

- Catálogo com 590 técnicas dos 21 decks: mapas, profundidade, diagramas e elementos, com origem, recorte e receita.
- 274 itens do catálogo com peça pronta em `references/pecas_*.py`, em formas editáveis e nas cores de qualquer mestre.
- Mapas com estados de 9 países e países em 1:50m.
- Regra: evidência só com material real. O molde com rótulo cinza não vai para a entrega.
- O `ppt-researcher` passa a listar o material real disponível no roteiro.

## 0.3.0

- Nenhum número ou período em título e cabeçalho de painel.
- Um cabeçalho e um itálico por visual.
- Notas passam para as notas do apresentador, fora da face do slide.
- Sem colunas de texto ao lado do gráfico.
- Data label em estilo único.
- Primeiras peças de profundidade: pirâmide, discos, cartão com cantoneiras, feixe, parede lateral e placas.

## 0.2.0

- Segunda passada no catálogo: tags de visual mais precisas e ranking diversificado.

## 0.1.0

- Primeira versão: `/ppt-researcher` e `/ppt-designer`.
