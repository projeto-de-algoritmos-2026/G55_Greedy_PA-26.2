# SPEC.md — Documento de Especificação Dirigida à Implementação

**Projeto:** RotaFest (G55_Greedy_PA-26.2)
**Disciplina:** Projeto de Algoritmos — FGA/UnB — 2026.2
**Conteúdo:** Greed (Algoritmos Ambiciosos)
**Versão do documento:** 1.1 (contratos das seções 3 e 4 congelados, ver D-6 a D-12)
**Status:** Aprovado para implementação

---

## 0. Como usar este documento

Este é um documento **spec-driven**: a implementação deve seguir a especificação, e não o contrário. Regras de uso:

1. Nenhuma task pode ser iniciada sem que sua seção de referência nos capítulos 2 a 7 esteja lida.
2. Toda task possui **critério de aceite verificável**. Uma task só é concluída quando o critério passa, não quando o código "funciona".
3. Divergências entre o código e a spec devem ser resolvidas **alterando a spec primeiro**, com registro no capítulo 13 (Log de Decisões).
4. As seções 2, 3 e 4 são **contratos**. Alterá-las quebra trabalho paralelo e exige comunicação explícita entre a dupla.

### Convenção de identificadores

| Prefixo | Significado |
|---|---|
| `E-n` | Épico |
| `T-nnn` | Task |
| `CA-n` | Critério de aceite |
| `R-n` | Risco |
| `D-n` | Decisão registrada |

---

## 1. Visão Geral e Escopo

### 1.1 Problema

Em um festival com múltiplos palcos operando em paralelo, a grade de shows contém conflitos de horário. O frequentador não consegue assistir a tudo e precisa escolher. A escolha é agravada pelo **tempo de caminhada entre palcos**, que a intuição humana tende a ignorar.

### 1.2 Objetivo

Construir uma aplicação web que, dada a grade de um festival e as preferências do usuário, produza roteiros otimizados por meio de algoritmos ambiciosos, exibindo o resultado de forma visualmente legível e comparando o desempenho do guloso contra a solução exata e contra heurísticas ingênuas.

### 1.3 Perguntas que o sistema responde

| # | Pergunta | Algoritmo |
|:-:|---|---|
| Q1 | Qual o maior número de shows que consigo assistir? | Interval Scheduling |
| Q2 | Qual roteiro maximiza minha satisfação total? | Weighted Interval Scheduling |
| Q3 | Quantos palcos a grade exigiria no mínimo? | Interval Partitioning |
| Q4 | Quanto perco usando uma heurística ingênua? | FIFO, SPT, Maior Preferência |

### 1.4 Escopo incluído

- Importação de grade por arquivo CSV.
- Atribuição de pesos de preferência por show.
- Dois modos de tratamento de deslocamento (uniforme e matricial).
- Visualização em grade de horários, timeline e mapa.
- Painel comparativo entre estratégias.
- Verificação de corretude por força bruta.
- Gerador de instâncias sintéticas para medição de desempenho.

### 1.5 Escopo excluído

Registrar explicitamente evita expansão de escopo no meio da semana.

- Autenticação e contas de usuário.
- Persistência em banco de dados. O estado vive na sessão do navegador.
- Scraping de sites de festivais. A grade é um CSV versionado no repositório.
- Roteamento geográfico real. As distâncias entre palcos vêm de matriz fornecida.
- Responsividade para dispositivos móveis. Alvo é desktop.
- Deploy em produção. Execução local documentada é suficiente.

---

## 2. Modelo de Domínio

### 2.1 Glossário

| Termo | Definição |
|---|---|
| **Show** | Apresentação única, com artista, palco, início e fim. Unidade atômica do problema. |
| **Grade** | Conjunto completo de shows de um festival em um dia. |
| **Palco** | Local físico onde um show ocorre. Identificado por código único. |
| **Peso** | Nota de preferência de 1 a 10 atribuída pelo usuário a um show. Ausência equivale a 1. |
| **Deslocamento** | Tempo em minutos para caminhar de um palco a outro. |
| **Compatibilidade** | Relação binária entre dois shows que indica se ambos podem ser assistidos integralmente. |
| **Roteiro** | Subconjunto de shows mutuamente compatíveis, ordenado cronologicamente. |
| **Profundidade** | Número máximo de shows simultâneos em qualquer instante da grade. |

### 2.2 Entidade `Show`

```
Show
├── id           : string   (único, formato "S001")
├── artista      : string
├── palco        : string   (referência a Palco.codigo)
├── inicio       : int      (minutos desde 00:00 do dia do festival)
├── fim          : int      (minutos desde 00:00; fim > inicio)
├── peso         : int      (1 a 10, padrão 1)
└── dia          : int      (1..N, para festivais de múltiplos dias)
```

**Decisão D-1: tempo representado em minutos inteiros desde a meia-noite.**
Justificativa: elimina aritmética de data, simplifica comparações, torna a ordenação trivial e evita bugs de fuso. Shows que atravessam a meia-noite recebem `fim > 1440` (exemplo: show que termina às 01:30 do dia seguinte tem `fim = 1530`). A conversão para exibição é responsabilidade exclusiva do frontend.

### 2.3 Entidade `Palco`

```
Palco
├── codigo       : string   (único, formato "P1")
├── nome         : string
├── x            : float    (coordenada relativa no mapa, 0.0 a 1.0)
└── y            : float    (coordenada relativa no mapa, 0.0 a 1.0)
```

**Decisão D-2: coordenadas relativas, não geográficas.**
Justificativa: elimina dependência de API de mapas e de dados de planta georreferenciada. O mapa é uma imagem estática do layout do festival, e os palcos são posicionados percentualmente sobre ela. Risco R-3 mitigado.

### 2.4 Entidade `MatrizDeslocamento`

Matriz quadrada `D` onde `D[a][b]` é o tempo em minutos para ir do palco `a` ao palco `b`.

**Invariantes obrigatórias:**

- `D[a][a] = 0` para todo palco `a`.
- `D[a][b] = D[b][a]` (simetria).
- `D[a][b] >= 0`.
- A desigualdade triangular **não** é exigida, mas sua violação deve ser sinalizada em log de aviso, porque torna a interpretação do resultado contraintuitiva.

### 2.5 Relação de compatibilidade

Esta é a definição central do projeto. Existem **dois modos**, e a distinção entre eles é o que sustenta a análise algorítmica.

#### Modo A — Deslocamento uniforme

Assume-se um tempo constante `δ` entre **quaisquer dois shows consecutivos do roteiro, inclusive no mesmo palco** (D-6).

```
compativel_A(i, j) ⟺ fim[i] + δ ≤ inicio[j]
```

Aplicar `δ` também ao mesmo palco não é detalhe: se o custo fosse 0 para o mesmo palco e `δ` para palcos distintos, a compatibilidade passaria a depender do par, exatamente como no Modo B, e a garantia de otimalidade do guloso deixaria de valer.

Equivale a executar o algoritmo clássico sobre os intervalos transformados `[inicio, fim + δ]`. Como `δ` é constante, a transformação **preserva a ordem relativa dos términos**, e portanto **todas as garantias de otimalidade do guloso permanecem válidas**. Esta é a demonstração formal a ser escrita na task T-501.

#### Modo B — Deslocamento matricial

O custo depende do par de palcos.

```
compativel_B(i, j) ⟺ fim[i] + D[palco[i]][palco[j]] ≤ inicio[j]
```

**Atenção crítica: no Modo B o guloso por menor horário de término NÃO é comprovadamente ótimo.** A compatibilidade deixa de ser uma relação induzida por intervalos na reta e passa a ser uma relação arbitrária sobre pares. O argumento de troca não se aplica, porque trocar um show por outro de término anterior pode piorar o custo de deslocamento até o próximo.

**Solução exata para o Modo B:** modelar como **caminho máximo em DAG**.

- Vértices: os shows, mais uma fonte artificial `s`.
- Aresta `i → j` se `compativel_B(i, j)` e `inicio[j] ≥ inicio[i]`.
- O grafo é acíclico porque toda aresta aponta para um show de início estritamente posterior.
- Caminho de peso máximo (peso do vértice, não da aresta) resolve Q1 com peso unitário e Q2 com peso de preferência.
- Complexidade: `O(n²)` para construção e relaxação em ordem topológica, que aqui é simplesmente a ordem de início.

**Decisão D-3: o Modo B é resolvido exatamente por DAG, não por guloso.**
Justificativa: honestidade algorítmica. O projeto ganha profundidade ao demonstrar **onde a estratégia gulosa deixa de valer**, em vez de aplicá-la fora de suas hipóteses. O comparativo entre o guloso do Modo A e a solução exata do Modo B vira material de análise, não um defeito.

---

## 3. Contratos de Dados

### 3.1 `grade_festival.csv`

Codificação UTF-8, separador vírgula, cabeçalho obrigatório na primeira linha.

```csv
id,artista,palco,dia,hora_inicio,hora_fim
S001,Artista Alfa,P1,1,14:00,15:00
S002,Artista Beta,P2,1,14:30,15:45
S003,Artista Gama,P1,1,15:20,16:30
```

| Coluna | Tipo | Regra de validação |
|---|---|---|
| `id` | string | Único no arquivo. Obrigatório. |
| `artista` | string | Não vazio. Máximo 80 caracteres. |
| `palco` | string | Deve existir em `palcos.json`. |
| `dia` | inteiro | `>= 1`. |
| `hora_inicio` | `HH:MM` | Formato de 24 horas. Horários antes de 06:00 pertencem à madrugada do dia informado e recebem +1440 minutos (D-7). |
| `hora_fim` | `HH:MM` | Mesma regra de `hora_inicio`. Após a normalização, `fim > inicio` é obrigatório. |

**Regra do dia de festival (D-7):** um dia de festival vai de 06:00 às 05:59 do dia seguinte. A conversão é `minutos(h) = h` se `h >= 360`, senão `h + 1440`. Assim, um show de 23:30 a 01:00 resulta em `inicio=1410, fim=1500`, e um show de 00:30 a 01:30 do dia 1 resulta em `inicio=1470, fim=1530`, ficando corretamente depois dos shows da noite.

**Erros de validação devem falhar de forma explícita**, com mensagem indicando a linha e a coluna. Importação parcial silenciosa é proibida.

### 3.2 `palcos.json`

```json
{
  "festival": "Nome do Festival",
  "mapa": "mapa_festival.svg",
  "palcos": [
    { "codigo": "P1", "nome": "Palco Mundo", "x": 0.20, "y": 0.35 },
    { "codigo": "P2", "nome": "Sunset", "x": 0.65, "y": 0.30 },
    { "codigo": "P3", "nome": "New Dance Order", "x": 0.80, "y": 0.72 }
  ],
  "deslocamento": {
    "modo_padrao": "uniforme",
    "delta_uniforme": 12,
    "matriz": {
      "P1": { "P1": 0, "P2": 12, "P3": 18 },
      "P2": { "P1": 12, "P2": 0, "P3": 9  },
      "P3": { "P1": 18, "P2": 9,  "P3": 0  }
    }
  }
}
```

### 3.3 Payload de preferências

Enviado pelo frontend a cada requisição de cálculo.

```json
{
  "pesos": { "S001": 8, "S002": 3, "S005": 10 },
  "modo_deslocamento": "matricial",
  "delta_uniforme": 12,
  "dia": 1
}
```

Shows não presentes em `pesos` assumem peso 1. Pesos fora de 1..10 ou para ids inexistentes na grade do dia retornam 422.

Este payload é incorporado a **toda** requisição de cálculo (seções 4.3 a 4.6), junto de `festival_id` (D-8).

---

## 4. Contrato da API

Base: `http://localhost:8000/api`
Todas as respostas em JSON, UTF-8. Erros seguem o padrão do FastAPI com `detail` em português.

### 4.0 `GET /health`

**Resposta 200**
```json
{ "status": "ok" }
```

### 4.0.1 Requisição de cálculo (comum a 4.3, 4.4, 4.5 e 4.6)

```json
{
  "festival_id": "festival-exemplo",
  "dia": 1,
  "modo_deslocamento": "uniforme",
  "delta_uniforme": 12,
  "pesos": { "S001": 8, "S005": 10 }
}
```

| Campo | Regra |
|---|---|
| `festival_id` | Obrigatório. Deve existir em `GET /festivais`. |
| `dia` | Obrigatório. `>= 1`. |
| `modo_deslocamento` | `"uniforme"` ou `"matricial"`. Padrão: `modo_padrao` do `palcos.json`. |
| `delta_uniforme` | Inteiro `>= 0`. Usado apenas no modo uniforme. Padrão: `delta_uniforme` do `palcos.json`. |
| `pesos` | Opcional. Ausência de um show equivale a peso 1. |

`POST /dimensionamento` ignora `modo_deslocamento`, `delta_uniforme` e `pesos`.

### 4.1 `GET /festivais`

Lista os festivais disponíveis no diretório de dados.

**Resposta 200**
```json
[{ "id": "festival-exemplo", "nome": "Festival Exemplo", "dias": 2, "total_shows": 84 }]
```

### 4.2 `GET /festivais/{id}/grade?dia=1`

**Resposta 200**
```json
{
  "festival": "Festival Exemplo",
  "dia": 1,
  "palcos": [ { "codigo": "P1", "nome": "Palco Mundo", "x": 0.2, "y": 0.35 } ],
  "shows": [
    { "id": "S001", "artista": "Artista Alfa", "palco": "P1",
      "inicio": 840, "fim": 900, "peso": 1 }
  ]
}
```

### 4.2.1 `GET /festivais/{id}/mapa`

Retorna o `mapa_festival.svg` do festival (`image/svg+xml`). 404 se o festival não existir (D-10).

### 4.2.2 `POST /festivais/importar`

Importa uma grade própria (tela `/`). Requisição `multipart/form-data` com `arquivo` (CSV da seção 3.1) e `festival_base` (id de festival existente cujo `palcos.json` é reutilizado). O festival importado vive **apenas em memória** no backend, com id `upload-<hash do conteúdo>`, coerente com a ausência de persistência (1.5). CSV inválido retorna 422 com a lista de erros (D-9).

**Resposta 201**
```json
{ "id": "upload-3f9a2c", "nome": "Grade importada", "dias": 1, "total_shows": 40 }
```

**Resposta 422 (erro de validação de CSV, também usada pelo loader)**
```json
{
  "detail": "Grade inválida: 2 erro(s) encontrado(s).",
  "erros": [
    { "linha": 7, "coluna": "palco", "mensagem": "Palco 'P9' não existe em palcos.json." },
    { "linha": 12, "coluna": "hora_fim", "mensagem": "Formato inválido '25:00'; use HH:MM." }
  ]
}
```

### 4.3 `POST /roteiro/maximo-shows`

Resolve Q1. Requisição conforme 4.0.1.

**Resposta 200**
```json
{
  "estrategia": "interval_scheduling_guloso",
  "otimo_garantido": true,
  "roteiro": ["S001", "S004", "S009"],
  "total_shows": 3,
  "peso_total": 3,
  "deslocamentos": [
    { "de": "S001", "para": "S004", "palco_origem": "P1",
      "palco_destino": "P2", "custo_min": 12, "folga_min": 8 }
  ],
  "tempo_execucao_ms": 0.42
}
```

O campo `otimo_garantido` é **obrigatório em toda resposta de roteiro** e reflete se as hipóteses do algoritmo foram satisfeitas. No Modo B com guloso, retorna `false`.

### 4.4 `POST /roteiro/maxima-satisfacao`

Resolve Q2. Mesmo formato de requisição e resposta, com `estrategia` igual a `weighted_interval_scheduling_dp` ou `dag_longest_path`.

### 4.5 `POST /dimensionamento`

Resolve Q3. Requisição conforme 4.0.1.

**Resposta 200**
```json
{
  "palcos_minimos": 4,
  "profundidade_maxima": 4,
  "limite_inferior_atingido": true,
  "palcos_reais": 5,
  "alocacao": { "SALA_1": ["S001", "S009"], "SALA_2": ["S002"] },
  "sobreposicao_por_faixa": [
    { "minuto": 840, "simultaneos": 2 },
    { "minuto": 900, "simultaneos": 4 }
  ]
}
```

### 4.6 `POST /comparativo`

Resolve Q4. Executa todas as estratégias sobre a mesma instância.

**Resposta 200**
```json
{
  "instancia": { "total_shows": 84, "dia": 1, "modo_deslocamento": "uniforme" },
  "resultados": [
    { "estrategia": "guloso_menor_fim", "otimo_garantido": true,
      "total_shows": 7, "peso_total": 38, "tempo_ms": 0.4 },
    { "estrategia": "dp_ponderado", "otimo_garantido": true,
      "total_shows": 5, "peso_total": 52, "tempo_ms": 1.1 },
    { "estrategia": "fifo", "otimo_garantido": false,
      "total_shows": 4, "peso_total": 21, "tempo_ms": 0.3 },
    { "estrategia": "spt", "otimo_garantido": false,
      "total_shows": 6, "peso_total": 25, "tempo_ms": 0.3 },
    { "estrategia": "maior_peso", "otimo_garantido": false,
      "total_shows": 3, "peso_total": 44, "tempo_ms": 0.3 }
  ],
  "gap_percentual": { "fifo": 59.6, "spt": 51.9, "maior_peso": 15.4 }
}
```

**Definição de `gap_percentual` (D-12):** `gap = (peso_otimo − peso_estrategia) / peso_otimo × 100`, arredondado a uma casa, onde `peso_otimo` é o `peso_total` da melhor solução exata do modo (DP ponderada no Modo A, DAG no Modo B). Calculado apenas para as heurísticas. Se `peso_otimo = 0` (grade vazia), o gap é 0.

### 4.7 `POST /validar` (endpoint de desenvolvimento)

Executa força bruta e compara com o resultado dos algoritmos. Recusa instâncias com mais de 20 shows, retornando 422.

---

## 5. Especificação dos Algoritmos

### 5.0 Regra geral de desempate (D-11)

Toda ordenação usa chave composta `(critério, id)`. Exemplo: ordenar por término é ordenar por `(fim_efetivo, id)`. Isso vale para os algoritmos exatos, para as heurísticas e para o partitioning, e torna todos os resultados determinísticos e testáveis.

### 5.1 Interval Scheduling (Q1, Modo A)

```
ENTRADA : lista S de shows, delta
SAIDA   : subconjunto máximo de shows mutuamente compatíveis

1. Para cada s em S: fim_efetivo[s] ← fim[s] + delta
2. Ordenar S por fim_efetivo crescente
3. roteiro ← [] ; ultimo_fim ← -infinito
4. Para cada s em S (na ordem):
5.     Se inicio[s] >= ultimo_fim:
6.         roteiro.append(s)
7.         ultimo_fim ← fim_efetivo[s]
8. Retornar roteiro
```

**Invariante:** ao final de cada iteração, `roteiro` é um conjunto compatível de cardinalidade máxima entre todos os subconjuntos compatíveis dos shows já processados, e `ultimo_fim` é o menor término possível para um conjunto dessa cardinalidade.

**Complexidade:** `O(n log n)`, dominada pela ordenação.

**Prova (argumento de troca), a ser redigida em T-501:** seja `G = g1..gk` a solução gulosa e `O = o1..om` uma solução ótima. Mostra-se por indução que `fim_efetivo[gi] ≤ fim_efetivo[oi]` para todo `i ≤ k`. Se `m > k`, então `o(k+1)` seria compatível com `gk`, e o guloso o teria selecionado, contradição. Logo `k = m`.

### 5.2 Weighted Interval Scheduling (Q2, Modo A)

```
ENTRADA : lista S de shows com pesos, delta
SAIDA   : subconjunto compatível de peso máximo

1. Ordenar S por fim_efetivo crescente, indexando de 1 a n
2. Para cada j: p[j] ← maior índice i < j tal que fim_efetivo[i] <= inicio[j]
                (localizado por busca binária)
3. OPT[0] ← 0
4. Para j de 1 a n:
5.     OPT[j] ← max( peso[j] + OPT[p[j]] , OPT[j-1] )
6. Reconstruir a solução percorrendo OPT de trás para frente
7. Retornar roteiro reconstruído
```

**Complexidade:** `O(n log n)`.

**Contraexemplo obrigatório (T-304):** o guloso por menor término falha com a instância abaixo.

| Show | Início | Fim | Peso |
|---|---|---|---|
| A | 18:00 | 19:00 | 1 |
| B | 19:00 | 20:00 | 1 |
| C | 18:30 | 19:30 | 10 |

Guloso seleciona A e depois B, totalizando peso 2. O ótimo é C sozinho, com peso 10. O gap é de 80%. Este caso deve estar codificado como teste automatizado.

### 5.3 Interval Partitioning (Q3)

```
ENTRADA : lista S de shows
SAIDA   : número mínimo de recursos e alocação

1. Ordenar S por inicio crescente
2. heap ← fila de prioridade vazia (min-heap por horário de liberação)
3. Para cada s em S:
4.     Se heap não vazio E topo(heap).liberacao <= inicio[s]:
5.         recurso ← pop(heap)
6.     Senão:
7.         recurso ← novo recurso
8.     alocar s em recurso
9.     push(heap, recurso com liberacao = fim[s])
10. Retornar tamanho máximo atingido pelo heap
```

**Complexidade:** `O(n log n)`.

**Prova (limite inferior):** seja `d` a profundidade máxima de sobreposição. Nenhuma alocação usa menos de `d` recursos, porque no instante do pico há `d` shows simultâneos exigindo recursos distintos. O guloso abre um novo recurso apenas quando todos os existentes estão ocupados, o que só ocorre em instantes de sobreposição, logo nunca ultrapassa `d`. Portanto o guloso atinge exatamente `d` e é ótimo.

**Decisão D-4:** o cálculo da profundidade máxima é feito por **varredura de eventos** (`sweep line`) independente do algoritmo de partitioning, justamente para servir de verificação cruzada. Se os dois valores divergirem, há bug.

### 5.4 Caminho máximo em DAG (Modo B)

```
ENTRADA : lista S, matriz D
SAIDA   : subconjunto compatível de peso máximo sob deslocamento matricial

1. Ordenar S por inicio crescente
2. Para j de 1 a n:
3.     melhor[j] ← peso[j]
4.     pred[j]   ← nulo
5.     Para i de 1 a j-1:
6.         Se fim[i] + D[palco[i]][palco[j]] <= inicio[j]:
7.             Se melhor[i] + peso[j] > melhor[j]:
8.                 melhor[j] ← melhor[i] + peso[j]
9.                 pred[j]   ← i
10. Reconstruir a partir do argmax de melhor
```

**Complexidade:** `O(n²)`. Para `n` na casa de 100 shows, é irrelevante na prática, e o custo é justificado pela exatidão.

### 5.5 Heurísticas de comparação

| Nome | Critério de ordenação | Observação |
|---|---|---|
| `fifo` | Menor horário de início | Intuição natural do frequentador |
| `spt` | Menor duração | Tenta maximizar quantidade de forma ingênua |
| `maior_peso` | Maior peso de preferência | Tenta maximizar satisfação de forma ingênua |

Todas percorrem a lista ordenada selecionando o primeiro compatível. Nenhuma tem garantia de otimalidade, e isso é o ponto.

### 5.6 Força bruta (validação)

Enumera todos os `2ⁿ` subconjuntos, filtra os compatíveis e retorna o de maior cardinalidade e o de maior peso. Limite rígido: `n ≤ 20`. Usada exclusivamente em testes.

---

## 6. Especificação da Interface

### 6.1 Telas

| Tela | Rota | Conteúdo |
|---|---|---|
| Seleção | `/` | Lista de festivais, seleção de dia, upload de CSV próprio |
| Planejador | `/planejador` | Grade, painel de preferências, controles, timeline, mapa |
| Dimensionamento | `/dimensionamento` | Resultado do partitioning e gráfico de sobreposição |
| Comparativo | `/comparativo` | Tabela e gráfico de barras das cinco estratégias |

### 6.2 Componentes do Planejador

| Componente | Responsabilidade |
|---|---|
| `GradeFestival` | Renderiza colunas por palco e linhas por faixa horária. Shows selecionados em cor sólida, descartados em cinza com opacidade reduzida. |
| `PainelPreferencias` | Slider de 1 a 10 por show, com busca por artista. |
| `ControlesOtimizacao` | Alternância entre Q1 e Q2, entre Modo A e Modo B, e campo de `δ`. |
| `TimelineRoteiro` | Lista vertical ordenada com horário, artista, palco e bloco de deslocamento entre itens consecutivos, exibindo custo e folga. |
| `MapaRota` | Imagem estática do mapa com marcadores posicionados por coordenada relativa e linha poligonal numerada ligando os palcos na ordem do roteiro. |
| `BadgeOtimalidade` | Exibe "Ótimo garantido" ou "Sem garantia de otimalidade" conforme o campo `otimo_garantido` da resposta. Obrigatório e não suprimível. |

### 6.3 Estados de interface obrigatórios

Cada componente que consome a API deve tratar: carregando, sucesso, vazio (nenhum show compatível) e erro. Estado de erro deve exibir a mensagem retornada pelo backend, não uma mensagem genérica.

### 6.4 Diretrizes visuais

- Paleta de no máximo cinco cores, uma por palco.
- Contraste mínimo de 4.5:1 entre texto e fundo.
- A grade deve caber em uma tela de 1366x768 sem rolagem horizontal.

---

## 7. Estrutura de Diretórios

```
G55_Greedy_PA-26.2/
├── backend/
│   ├── app/
│   │   ├── algorithms/
│   │   │   ├── __init__.py
│   │   │   ├── interval_scheduling.py
│   │   │   ├── weighted_scheduling.py
│   │   │   ├── interval_partitioning.py
│   │   │   ├── dag_longest_path.py
│   │   │   ├── heuristics.py
│   │   │   ├── brute_force.py
│   │   │   └── travel_cost.py
│   │   ├── models/
│   │   │   ├── show.py
│   │   │   ├── palco.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── loader.py
│   │   │   └── comparator.py
│   │   ├── data/
│   │   │   ├── festival-exemplo/
│   │   │   │   ├── grade_festival.csv
│   │   │   │   ├── palcos.json
│   │   │   │   └── mapa_festival.svg
│   │   ├── routers/
│   │   │   ├── festivais.py
│   │   │   ├── roteiro.py
│   │   │   └── analise.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_interval_scheduling.py
│   │   ├── test_weighted.py
│   │   ├── test_partitioning.py
│   │   ├── test_dag.py
│   │   ├── test_brute_force_equivalence.py
│   │   ├── test_loader.py
│   │   └── fixtures/
│   ├── scripts/
│   │   ├── gerar_instancias.py
│   │   ├── benchmark.py
│   │   └── validar_dados.py
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api.ts
│   │   ├── types/index.ts
│   │   └── utils/tempo.ts
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── SPEC.md
│   ├── provas_formais.md
│   ├── analise_experimental.md
│   └── img/
├── CLAUDE.md
├── README.md
└── .gitignore
```

---

## 8. Backlog de Implementação

Estimativas em horas de trabalho efetivo. Total estimado: **58 horas**, distribuídas entre dois integrantes ao longo de seis dias.

### E-0 — Fundação do Projeto (6h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-001 | Criar repositório, `.gitignore` para Python e Node, e estrutura de diretórios da seção 7 | CA: `tree` reproduz a estrutura especificada | — | 0.5h |
| T-002 | Configurar backend: venv, `requirements.txt`, FastAPI com CORS liberado para `localhost:5173` | CA: `GET /api/health` retorna 200 | T-001 | 1h |
| T-003 | Configurar frontend: Vite, React, TypeScript, Tailwind | CA: `npm run dev` sobe e renderiza página inicial | T-001 | 1.5h |
| T-004 | Definir os tipos TypeScript espelhando os schemas da seção 4 | CA: `types/index.ts` cobre todos os payloads de requisição e resposta | T-003 | 1h |
| T-005 | Montar `grade_festival.csv` do festival escolhido com no mínimo 60 shows | CA: arquivo valida contra as regras de 3.1 | T-001 | 1.5h |
| T-006 | Montar `palcos.json` com coordenadas e matriz de deslocamento | CA: invariantes de 2.4 verificadas por script | T-005 | 0.5h |

### E-1 — Camada de Dados (5h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-101 | Implementar modelos Pydantic `Show`, `Palco`, `MatrizDeslocamento` | CA: instanciação com dado inválido levanta `ValidationError` | T-002 | 1h |
| T-102 | Implementar `loader.py`: leitura do CSV, conversão `HH:MM` para minutos, tratamento de virada de dia | CA: show `23:30` a `01:00` resulta em `inicio=1410, fim=1500` | T-101 | 1.5h |
| T-103 | Implementar validação com erro por linha e coluna | CA: CSV com palco inexistente falha citando o número da linha | T-102 | 1h |
| T-104 | Implementar `GET /festivais` e `GET /festivais/{id}/grade` | CA: resposta idêntica ao contrato 4.2 | T-102 | 1h |
| T-105 | Escrever `tests/test_loader.py` cobrindo os três casos de erro previstos | CA: `pytest tests/test_loader.py` verde | T-103 | 0.5h |

### E-2 — Núcleo Algorítmico (14h)

**Esta é a espinha dorsal do trabalho. Nenhuma task de E-2 pode ser marcada como concluída sem teste automatizado correspondente.**

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-201 | Implementar `travel_cost.py` com as duas funções de compatibilidade (Modo A e Modo B) | CA: testes cobrindo fronteira exata (`fim + δ == inicio` deve ser compatível) | T-101 | 1h |
| T-202 | Implementar `interval_scheduling.py` conforme 5.1 | CA: retorna 3 na instância de referência; caso de empate de término resolvido deterministicamente | T-201 | 2h |
| T-203 | Implementar `weighted_scheduling.py` conforme 5.2, com busca binária para `p(j)` | CA: resolve o contraexemplo de 5.2 com peso 10, não 2 | T-202 | 3h |
| T-204 | Implementar `interval_partitioning.py` conforme 5.3 com `heapq` | CA: retorna 3 em instância com profundidade 3 conhecida | T-201 | 2h |
| T-205 | Implementar varredura de eventos para profundidade máxima, independente de T-204 | CA: valor idêntico ao de T-204 em 100 instâncias aleatórias | T-204 | 1.5h |
| T-206 | Implementar `dag_longest_path.py` conforme 5.4 | CA: em instância do Modo B, supera ou iguala o guloso em 100% dos casos testados | T-201 | 2.5h |
| T-207 | Implementar as três heurísticas de 5.5 com interface uniforme | CA: assinatura idêntica à dos algoritmos ótimos, permitindo troca direta | T-202 | 1h |
| T-208 | Implementar `brute_force.py` com guarda de `n ≤ 20` | CA: `n = 21` levanta exceção explícita | T-201 | 1h |

### E-3 — Validação de Corretude (6h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-301 | `gerar_instancias.py`: gerador parametrizável por `n`, densidade de sobreposição e número de palcos | CA: seed fixa reproduz instância idêntica | T-101 | 1.5h |
| T-302 | Teste de equivalência: guloso contra força bruta em 500 instâncias com `n ≤ 12` | CA: cardinalidade idêntica em 100% dos casos | T-202, T-208, T-301 | 1.5h |
| T-303 | Teste de equivalência: DP ponderado contra força bruta em 500 instâncias | CA: peso total idêntico em 100% dos casos | T-203, T-208 | 1h |
| T-304 | Codificar o contraexemplo de 5.2 como teste explícito e documentado | CA: teste falha se alguém substituir a DP por guloso | T-203 | 0.5h |
| T-305 | Teste do Modo B: guloso contra DAG, registrando frequência e magnitude da falha do guloso | CA: relatório gerado com percentual de instâncias em que o guloso é subótimo | T-206 | 1.5h |

### E-4 — API de Análise (5h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-401 | `POST /roteiro/maximo-shows` com seleção de modo e campo `otimo_garantido` correto | CA: Modo B com guloso retorna `false` | T-202, T-206 | 1h |
| T-402 | `POST /roteiro/maxima-satisfacao` | CA: contrato 4.4 respeitado | T-203, T-206 | 1h |
| T-403 | `POST /dimensionamento` com alocação e série de sobreposição | CA: `limite_inferior_atingido` é `true` em todas as instâncias válidas | T-204, T-205 | 1h |
| T-404 | `comparator.py` e `POST /comparativo` executando as cinco estratégias | CA: `gap_percentual` calculado em relação à melhor solução exata | T-207 | 1.5h |
| T-405 | `POST /validar` restrito a `n ≤ 20` | CA: `n = 25` retorna 422 com mensagem clara | T-208 | 0.5h |

### E-5 — Documentação Formal (5h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-501 | Redigir prova de otimalidade do Interval Scheduling por argumento de troca, incluindo a preservação sob transformação uniforme | CA: prova completa, sem lacunas, em `provas_formais.md` | T-202 | 1.5h |
| T-502 | Redigir prova do limite inferior do Interval Partitioning | CA: argumento de profundidade máxima formalizado | T-204 | 1h |
| T-503 | Redigir justificativa da recorrência do Weighted Interval Scheduling | CA: subestrutura ótima demonstrada | T-203 | 1h |
| T-504 | Redigir a análise do Modo B, explicando por que o guloso perde a garantia e por que o DAG a recupera | CA: seção com o contraexemplo do Modo B explicitado | T-206 | 1.5h |

### E-6 — Interface (13h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-601 | `services/api.ts` com cliente tipado para todos os endpoints | CA: nenhum `any` no arquivo | T-004, T-104 | 1h |
| T-602 | Tela de seleção de festival e dia | CA: navegação para `/planejador` com estado preservado | T-601 | 1h |
| T-603 | `GradeFestival`: colunas por palco, blocos posicionados por horário | CA: 60 shows renderizam sem rolagem horizontal em 1366px | T-601 | 3h |
| T-604 | `PainelPreferencias` com sliders e busca | CA: alteração de peso dispara recálculo em menos de 500ms | T-603 | 1.5h |
| T-605 | `ControlesOtimizacao`: alternância Q1/Q2, Modo A/B e campo `δ` | CA: mudança de modo altera o `BadgeOtimalidade` corretamente | T-604 | 1h |
| T-606 | `TimelineRoteiro` com blocos de deslocamento, custo e folga | CA: folga negativa é impossível por construção; exibir folga zero em destaque | T-605 | 2h |
| T-607 | `MapaRota` com marcadores relativos e polilinha numerada | CA: ordem dos marcadores corresponde à ordem cronológica do roteiro | T-606 | 2h |
| T-608 | `BadgeOtimalidade` e tratamento dos quatro estados de interface | CA: estado vazio e estado de erro têm captura de tela em `docs/img` | T-605 | 1.5h |

### E-7 — Telas Analíticas (6h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-701 | Tela de dimensionamento com número mínimo de palcos e comparação com o real | CA: valor exibido igual ao retornado pela API | T-403, T-601 | 1.5h |
| T-702 | Gráfico de sobreposição por faixa horária com pico destacado | CA: pico visualmente coincidente com `profundidade_maxima` | T-701 | 1.5h |
| T-703 | Tela de comparativo com tabela e gráfico de barras das cinco estratégias | CA: gap percentual exibido por estratégia | T-404, T-601 | 2h |
| T-704 | `benchmark.py`: medição de tempo contra `n` crescente, exportando CSV | CA: curva medida compatível com `O(n log n)` e `O(n²)` conforme o algoritmo | T-301 | 1h |

### E-8 — Fechamento (8h)

| ID | Task | Critério de aceite | Dep. | Est. |
|---|---|---|---|:-:|
| T-801 | Redigir `analise_experimental.md` com os resultados de T-305, T-704 e do comparativo | CA: toda afirmação numérica acompanhada do dado que a sustenta | T-305, T-704 | 2h |
| T-802 | Finalizar `README.md` com capturas de tela reais | CA: todos os placeholders substituídos | T-608, T-703 | 1h |
| T-803 | Revisar instruções de instalação em máquina limpa | CA: um integrante segue o README do zero e a aplicação sobe | T-802 | 1h |
| T-804 | Gravar vídeo de apresentação | CA: demonstra Q1, Q2, Q3, Q4 e o contraexemplo, dentro do tempo limite | T-803 | 2h |
| T-805 | Revisão final: remover código morto, padronizar nomes, conferir que `pytest` está integralmente verde | CA: nenhum teste pulado ou marcado como esperado para falhar | Todas | 1h |
| T-806 | Conferir checklist de entrega do capítulo 12 | CA: todos os itens marcados | T-805 | 1h |

---

## 9. Plano de Testes

### 9.1 Pirâmide

| Nível | Quantidade alvo | Escopo |
|---|:-:|---|
| Unitário | ~35 | Cada algoritmo isoladamente, incluindo casos de fronteira |
| Propriedade | ~5 | Equivalência contra força bruta em instâncias aleatórias |
| Integração | ~8 | Endpoints da API com payload real |
| Manual | — | Fluxo completo na interface, registrado por captura de tela |

### 9.2 Casos de fronteira obrigatórios

Cada um destes deve ter teste nomeado explicitamente:

1. Grade vazia. Resultado esperado: roteiro vazio, sem exceção.
2. Show único. Resultado: ele próprio.
3. Todos os shows no mesmo horário. Resultado: exatamente um selecionado; partitioning retorna `n`.
4. Nenhuma sobreposição. Resultado: todos selecionados; partitioning retorna 1.
5. `fim[i] + δ` exatamente igual a `inicio[j]`. Resultado: compatíveis. A desigualdade é não estrita.
6. Empate de horário de término entre dois shows. Resultado: desempate determinístico por `id`, documentado.
7. Show que atravessa a meia-noite.
8. `δ` igual a zero. Resultado: equivale ao problema clássico.
9. `δ` grande o bastante para tornar todos incompatíveis. Resultado: roteiro de tamanho 1.
10. Peso máximo em show que se sobrepõe a todos os demais. Resultado: DP escolhe apenas ele.

### 9.3 Critério de cobertura

Cobertura mínima de 85% no pacote `app/algorithms`. Cobertura de `app/routers` não é exigida.

---

## 10. Cronograma

| Dia | Épicos | Marco de verificação |
|:-:|---|---|
| 1 | E-0, E-1 | Backend serve a grade real e o frontend a renderiza em lista simples |
| 2 | E-2 (T-201 a T-205) | Interval Scheduling e Partitioning passando nos testes unitários |
| 3 | E-2 (T-206 a T-208), E-3 | Todos os algoritmos implementados e validados contra força bruta |
| 4 | E-4, E-6 (T-601 a T-605) | API completa e grade visual interativa funcionando |
| 5 | E-6 (T-606 a T-608), E-7 | Timeline, mapa e telas analíticas prontas |
| 6 | E-5, E-8 | Provas redigidas, análise experimental escrita, vídeo gravado |

**Decisão D-5: as provas formais (E-5) ficam no Dia 6, mas cada uma deve ser esboçada em parágrafo único no dia em que seu algoritmo for implementado.** Justificativa: escrever a prova do zero ao final da semana, sem o raciocínio fresco, é a principal causa de provas fracas.

### 10.1 Divisão sugerida entre a dupla

| Integrante | Frente principal | Frente de apoio |
|---|---|---|
| A | Backend e algoritmos (E-1, E-2, E-3, E-4) | Provas formais (E-5) |
| B | Frontend e visualização (E-0 frontend, E-6, E-7) | Dados e análise experimental |

Ponto de sincronização obrigatório ao final do Dia 1, quando os contratos das seções 3 e 4 devem estar congelados, e ao final do Dia 3, quando a API deve estar estável para consumo.

---

## 11. Definition of Done

Uma task está concluída quando **todos** os itens abaixo são verdadeiros:

- [ ] O critério de aceite declarado na tabela do backlog passa.
- [ ] Existe teste automatizado, exceto para tasks exclusivamente de interface.
- [ ] O código não contém `TODO`, `FIXME` nem código comentado.
- [ ] Funções públicas possuem docstring com complexidade declarada.
- [ ] O commit referencia o que foi feito sem referenciar algo do spec.
- [ ] Nenhum teste existente quebrou.

---

## 12. Checklist de Entrega

- [ ] Repositório público com o nome correto e acesso verificado.
- [ ] `README.md` completo, com capturas reais e sem placeholders.
- [ ] `docs/provas_formais.md` com as quatro provas do E-5.
- [ ] `docs/analise_experimental.md` com dados e gráficos.
- [ ] `pytest` integralmente verde na branch principal.
- [ ] Instruções de instalação testadas do zero.
- [ ] Vídeo de apresentação publicado e linkado.
- [ ] Contraexemplo do guloso ponderado demonstrado no vídeo.
- [ ] Histórico de commits mostrando contribuição de ambos os integrantes.

---

## 13. Riscos e Log de Decisões

### 13.1 Riscos

| ID | Risco | Prob. | Impacto | Mitigação |
|---|---|:-:|:-:|---|
| R-1 | Transcrição da grade consome mais tempo que o previsto | Média | Médio | Limitar a 60 shows de um único dia; ampliar apenas se sobrar tempo |
| R-2 | Frontend consome tempo do núcleo algorítmico | **Alta** | **Alto** | E-2 e E-3 têm prioridade absoluta. Se o Dia 4 chegar sem E-3 concluído, cortar T-607 (mapa) |
| R-3 | Mapa do festival indisponível ou sem layout utilizável | Baixa | Médio | Mitigado por D-2: imagem estática com coordenadas relativas manuais |
| R-4 | Confusão entre Modo A e Modo B gera resultado incorreto sem ninguém notar | Média | **Alto** | `otimo_garantido` obrigatório na API e `BadgeOtimalidade` não suprimível na interface |
| R-5 | Provas formais escritas às pressas no último dia | Média | Alto | Mitigado por D-5: esboço no dia da implementação |
| R-6 | Divergência de contrato entre backend e frontend | Média | Médio | Congelamento das seções 3 e 4 ao final do Dia 1 |

### 13.2 Log de Decisões

| ID | Decisão | Justificativa | Seção |
|---|---|---|---|
| D-1 | Tempo em minutos inteiros desde a meia-noite | Elimina aritmética de data e bugs de fuso | 2.2 |
| D-2 | Coordenadas relativas em mapa estático | Remove dependência de API de mapas | 2.3 |
| D-3 | Modo B resolvido por DAG, não por guloso | Honestidade algorítmica; vira material de análise | 2.5 |
| D-4 | Profundidade máxima calculada por varredura independente | Verificação cruzada contra o partitioning | 5.3 |
| D-5 | Provas esboçadas no dia da implementação | Evita provas fracas escritas sem contexto | 10 |
| D-6 | No Modo A, `δ` vale para todo par consecutivo, inclusive no mesmo palco | Custo dependente do par quebraria a transformação uniforme e a garantia do guloso | 2.5 |
| D-7 | Dia de festival de 06:00 às 05:59; horários antes de 06:00 recebem +1440 | Shows que começam após a meia-noite ficariam no início do dia | 3.1 |
| D-8 | `pesos` e `festival_id` fazem parte de toda requisição de cálculo | Sem pesos na requisição, Q2 é impossível | 4.0.1 |
| D-9 | Upload de CSV via `POST /festivais/importar`, reaproveitando `palcos.json` de festival base, só em memória | A tela `/` previa upload sem endpoint; CSV sozinho não traz palcos nem matriz | 4.2.2 |
| D-10 | `GET /health` e `GET /festivais/{id}/mapa` no contrato; mapa em SVG | Endpoints usados por CA e pela interface não estavam contratados; SVG é versionável | 4.0, 4.2.1 |
| D-11 | Toda ordenação desempata por `id` | Resultados determinísticos em todos os algoritmos, não só no término | 5.0 |
| D-12 | `gap_percentual` definido sobre `peso_total` contra a melhor solução exata | A métrica não estava definida; o exemplo de 4.6 confirma essa leitura | 4.6 |

---

## 14. Referências

- KLEINBERG, Jon; TARDOS, Éva. *Algorithm Design*. Boston: Pearson, 2006. Capítulo 4.
- CORMEN, Thomas H. et al. *Introduction to Algorithms*. 4. ed. Cambridge: MIT Press, 2022. Capítulo 15.
- Material da disciplina Projeto de Algoritmos, FGA/UnB, 2026.2.