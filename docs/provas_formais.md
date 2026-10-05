# Provas Formais

Demonstrações de corretude e otimalidade dos algoritmos do RotaFest.

> Os itens abaixo são esboços escritos junto com a implementação de cada algoritmo. A versão final, com todos os passos, substitui cada esboço.

## 1. Interval Scheduling: otimalidade por argumento de troca

**Esboço.** No modo uniforme, dois shows `i` e `j` são compatíveis quando `fim[i] + δ ≤ inicio[j]`, o que equivale a trabalhar com os intervalos transformados `[inicio, fim + δ]` e exigir que não se sobreponham. Como `δ` é o mesmo para todos, a transformação soma uma constante a todo término e preserva a ordem entre eles; ordenar por `fim` ou por `fim + δ` dá a mesma sequência. Seja `G = g1..gk` a solução gulosa e `O = o1..om` uma solução ótima, ambas em ordem cronológica. Por indução, `fim[gr] ≤ fim[or]` para todo `r ≤ k`: vale para `r = 1` porque o guloso escolhe o menor término, e se vale para `r − 1`, então `or` é compatível com `g(r−1)` e estava disponível quando o guloso escolheu `gr`, que portanto termina no máximo junto com `or`. Se `m > k`, `o(k+1)` seria compatível com `gk` e o guloso não teria parado, contradição. Logo `k = m`. Verificação empírica: cardinalidade igual à da força bruta em 500 instâncias aleatórias.

---

### 1.1 Configuração e notação

Seja `S = {s₁, s₂, …, sₙ}` o conjunto de todos os shows do dia, com `inicio[s]` e `fim[s]` em minutos desde a meia-noite (D-1). O parâmetro de deslocamento uniforme é `δ ≥ 0` (D-6).

Defina o **intervalo efetivo** de um show `s` como `Î(s) = [inicio[s], fim[s] + δ]`. Dois shows `i` e `j` com `inicio[i] ≤ inicio[j]` são **compatíveis no Modo A** quando:

```
fim[i] + δ ≤ inicio[j]      ⟺      Î(i) e Î(j) não se sobrepõem
```

Um **roteiro** é um subconjunto de shows mutuamente compatíveis, ordenado cronologicamente. O problema pede o roteiro de cardinalidade máxima.

### 1.2 Preservação da ordem sob transformação uniforme

**Lema 1.1 (a transformação uniforme preserva a ordem dos términos).**  
Para quaisquer shows `i` e `j`:

```
fim[i] ≤ fim[j]   ⟺   fim[i] + δ ≤ fim[j] + δ
```

*Prova:* imediata, pois somar `δ ≥ 0` a ambos os lados de uma desigualdade real preserva a relação de ordem. ∎

**Corolário 1.2.** Ordenar `S` por `fim` crescente (com desempate por `id`) é idêntico a ordenar por `fim + δ` crescente (com o mesmo desempate). Logo o algoritmo `interval_scheduling` — que ordena por `(fim, id)` em `interval_scheduling.py` — opera corretamente sobre os intervalos efetivos sem precisar recalcular a chave de ordenação.

### 1.3 Prova de optimalidade (argumento de troca)

**Teorema 1.3.** O algoritmo guloso por menor horário de término produz, no Modo A, um roteiro de cardinalidade máxima.

**Prova por indução (invariante do passo de troca).**

Seja `G = (g₁, g₂, …, gₖ)` a sequência produzida pelo guloso e `O = (o₁, o₂, …, oₘ)` qualquer solução ótima, ambas ordenadas cronologicamente pelo horário de início. Provamos que `k = m`.

**Invariante:** para todo `r ≤ min(k, m)`,

```
fim_efetivo[gᵣ] ≤ fim_efetivo[oᵣ]
```

onde `fim_efetivo[s] = fim[s] + δ`.

**Base (r = 1).** Na primeira iteração o guloso escolhe o show de menor `fim_efetivo` em `S`. Como `o₁ ∈ S`, temos `fim_efetivo[g₁] ≤ fim_efetivo[o₁]`. ∎ (base)

**Passo indutivo.** Suponha que o invariante vale para `r − 1`, isto é, `fim_efetivo[g_{r−1}] ≤ fim_efetivo[o_{r−1}]`.

Queremos mostrar que `fim_efetivo[gᵣ] ≤ fim_efetivo[oᵣ]`.

Primeiro, `oᵣ` é compatível com `o_{r−1}`:
```
fim_efetivo[o_{r−1}] ≤ inicio[oᵣ]
```

Pela hipótese de indução:
```
fim_efetivo[g_{r−1}] ≤ fim_efetivo[o_{r−1}] ≤ inicio[oᵣ]
```

Portanto `oᵣ` também é compatível com `g_{r−1}`, ou seja, `oᵣ` estava **disponível** no momento em que o guloso escolheu `gᵣ` (todos os shows ainda não selecionados e compatíveis com o roteiro parcial). O guloso escolhe o de menor `fim_efetivo` entre os disponíveis, então:

```
fim_efetivo[gᵣ] ≤ fim_efetivo[oᵣ]
```

∎ (passo)

**Conclusão (`k = m`).**

Suponha, por absurdo, que `m > k`. O invariante garante que `fim_efetivo[gₖ] ≤ fim_efetivo[oₖ]`. O show `o_{k+1}` é compatível com `oₖ` na solução ótima:

```
fim_efetivo[oₖ] ≤ inicio[o_{k+1}]
```

Combinando com o invariante:

```
fim_efetivo[gₖ] ≤ fim_efetivo[oₖ] ≤ inicio[o_{k+1}]
```

Logo `o_{k+1}` é compatível com `gₖ`. Mas então o guloso não teria parado em `gₖ`: ele teria selecionado pelo menos mais um show, contradizendo `|G| = k`. A contradição mostra que `m > k` é impossível.

Como `G` é um roteiro válido (construção gulosa só adiciona shows compatíveis) e `|G| = |O|`, o guloso produz um roteiro de cardinalidade máxima. ∎

### 1.4 Verificação empírica (T-302)

A prova é corroborada pelos testes de equivalência: `pytest tests/test_brute_force_equivalence.py` confirma cardinalidade idêntica em 500 instâncias aleatórias (`n ≤ 12`, δ ∈ {0, 5, 12, 30}), com todos os roteiros validados por `roteiro_valido`.

---

## 2. Interval Partitioning: limite inferior pela profundidade

**Esboço.** Seja `d` o maior número de shows simultâneos em algum instante. Qualquer alocação usa pelo menos `d` palcos, porque os `d` shows daquele instante precisam de palcos distintos. O guloso processa os shows por início e só abre um palco novo para `s` quando todos os palcos abertos estão ocupados no instante `inicio[s]`; nesse instante há então `(palcos abertos) + 1` shows simultâneos, que é no máximo `d`. Portanto o guloso nunca passa de `d` e atinge exatamente o limite inferior. A implementação confirma isso empiricamente: a varredura de eventos, independente do heap, devolve o mesmo valor em 100 instâncias aleatórias.

---

### 2.1 Configuração e notação

Seja `S = {s₁, …, sₙ}` o conjunto de shows. Um show `s` está **ativo** no instante `t` se `inicio[s] ≤ t < fim[s]`. A **profundidade** no instante `t` é o número de shows ativos em `t`. A **profundidade máxima** é:

```
d = max_{t} |{ s ∈ S : inicio[s] ≤ t < fim[s] }|
```

calculada pela função `profundidade_maxima` em `interval_partitioning.py` via varredura de eventos (D-4).

Uma **alocação** é uma partição de `S` em grupos (recursos/palcos virtuais) tais que dois shows no mesmo grupo nunca estão ativos simultaneamente.

### 2.2 Limite inferior: qualquer alocação usa pelo menos `d` recursos

**Lema 2.1 (limite inferior).** Qualquer alocação válida de `S` usa pelo menos `d` recursos.

*Prova:* Seja `t*` o instante em que a profundidade atinge `d`. Nesse instante há `d` shows simultaneamente ativos: `A = {a₁, a₂, …, aₐ}` com `|A| = d`. Em qualquer alocação válida, dois shows ativos ao mesmo tempo não podem compartilhar o mesmo recurso (seriam apresentados simultaneamente no mesmo palco). Logo os `d` shows de `A` exigem `d` recursos distintos, e qualquer alocação usa no mínimo `d` recursos. ∎

### 2.3 O guloso atinge exatamente `d` recursos

**Teorema 2.2 (o guloso é ótimo para Interval Partitioning).** O algoritmo `interval_partitioning` usa exatamente `d` recursos.

*Prova:*

O algoritmo processa os shows em ordem crescente de `inicio` (com desempate por `id`, D-11). Para cada show `s`, ele verifica se existe algum recurso cujo horário de liberação satisfaz `liberacao ≤ inicio[s]` — e, em caso afirmativo, reusa o recurso disponível de menor liberação (min-heap por liberação). Caso contrário, abre um novo recurso.

**O guloso nunca ultrapassa `d`:** suponha que ao processar `s` o guloso abre o `(d+1)`-ésimo recurso. Isso significa que todos os `d` recursos existentes têm `liberacao > inicio[s]`, ou seja, todos estão ocupados por um show que ainda não terminou no instante `inicio[s]`. Somando o próprio `s`, há `d + 1` shows ativos em `inicio[s]`, contradizendo a definição de `d` como profundidade máxima. Logo o guloso nunca precisa de mais de `d` recursos.

**O guloso usa pelo menos `d`:** pelo Lema 2.1, qualquer alocação — incluindo a do guloso — usa no mínimo `d` recursos.

Combinando, o guloso usa exatamente `d` recursos. ∎

### 2.4 Verificação cruzada (D-4 e T-205)

A profundidade `d` é calculada de forma independente pela função `profundidade_maxima` (varredura de eventos), e o partitioning a calcula via `interval_partitioning`. A igualdade `len(interval_partitioning(S)) == profundidade_maxima(S)[0]` é verificada em 100 instâncias aleatórias por `test_partitioning.py`.

---

## 3. Weighted Interval Scheduling: subestrutura ótima da recorrência

**Esboço.** Ordene os shows por `fim + δ` e defina `OPT(j)` como o maior peso de um roteiro usando apenas os `j` primeiros. Em uma solução ótima para os `j` primeiros, ou `j` não aparece, e o resto é ótimo para os `j − 1` primeiros, ou `j` aparece, e então nenhum show entre `p(j) + 1` e `j − 1` pode estar nela (todos terminam depois do início de `j`), de modo que o resto é ótimo para os `p(j)` primeiros. Daí `OPT(j) = max(peso[j] + OPT(p(j)), OPT(j − 1))`. Como os términos transformados estão ordenados, os shows compatíveis com `j` formam um prefixo, e `p(j)` sai por busca binária. O guloso por menor término falha aqui: com A (18:00–19:00, peso 1), B (19:00–20:00, peso 1) e C (18:30–19:30, peso 10), ele escolhe A e B (peso 2), enquanto o ótimo é C (peso 10). Verificação empírica: peso igual ao da força bruta em 500 instâncias aleatórias.

---

### 3.1 Configuração e notação

Seja `S = {s₁, …, sₙ}` ordenado por `fim_efetivo[s] = fim[s] + δ` crescente (com desempate por `id`, D-11). Os shows são indexados de `1` a `n` nessa ordem.

Para cada show `j`, define-se:

```
p(j) = max{ i < j : fim_efetivo[sᵢ] ≤ inicio[sⱼ] }
      (ou 0 se nenhum show anterior é compatível com j)
```

`p(j)` é calculado por `bisect_right` sobre o vetor de `fim_efetivo`, conforme `weighted_scheduling.py`.

A variável `OPT(j)` representa o peso máximo de um roteiro compatível usando apenas os shows `s₁, …, sⱼ`.

### 3.2 Subestrutura ótima

**Lema 3.1 (subestrutura ótima).** Para `j ≥ 1`:

```
OPT(j) = max( peso[sⱼ] + OPT(p(j)),   OPT(j − 1) )
```

*Prova:*

Seja `R*` um roteiro ótimo para `{s₁, …, sⱼ}`, com peso `OPT(j)`. Há dois casos:

**Caso 1: `sⱼ ∉ R*`.**  
`R*` é um roteiro compatível de `{s₁, …, sⱼ₋₁}` com peso `OPT(j)`. Portanto `OPT(j) ≤ OPT(j − 1)`.  
Mas `OPT(j − 1)` também é atingível em `{s₁, …, sⱼ}` (basta ignorar `sⱼ`), logo `OPT(j) ≥ OPT(j − 1)`.  
Conclusão: `OPT(j) = OPT(j − 1)`.

**Caso 2: `sⱼ ∈ R*`.**  
Para que `R*` seja válido, nenhum show `sᵢ` com `p(j) < i < j` pode pertencer a `R*`. O motivo: por definição de `p(j)`, todo `sᵢ` com `i > p(j)` satisfaz `fim_efetivo[sᵢ] > inicio[sⱼ]`, ou seja, é incompatível com `sⱼ`. Portanto `R* \ {sⱼ}` é um roteiro de `{s₁, …, s_{p(j)}}`.

Afirmamos que `R* \ {sⱼ}` deve ser ótimo para `{s₁, …, s_{p(j)}}`. Suponha, por absurdo, que exista um roteiro `R'` de `{s₁, …, s_{p(j)}}` com peso maior. Então `R' ∪ {sⱼ}` é um roteiro válido de `{s₁, …, sⱼ}` (pois todo show de `R'` termina efetivamente antes de `inicio[sⱼ]`) com peso maior do que `R*`, contradizendo a otimalidade de `R*`.

Logo `peso(R* \ {sⱼ}) = OPT(p(j))`, e portanto:
```
OPT(j) = peso[sⱼ] + OPT(p(j))
```

**Unificando os casos:**

A solução ótima ou inclui `sⱼ` (Caso 2) ou não inclui (Caso 1). Portanto:

```
OPT(j) = max( peso[sⱼ] + OPT(p(j)),   OPT(j − 1) )
```
∎

### 3.3 Corretude da recorrência e implementação

**Corolário 3.2 (corretude da DP).** Calculando `OPT(0) = 0` e `OPT(j)` pela recorrência do Lema 3.1 para `j = 1, …, n`, obtém-se o peso máximo de um roteiro compatível de `S`.

*Prova por indução em `j`:* `OPT(0) = 0` está correto (roteiro vazio). Assumindo que `OPT(0), …, OPT(j − 1)` estão corretos, o Lema 3.1 garante que `OPT(j)` também está. ∎

**Reconstrução.** Percorrendo `OPT` de trás para frente: se `peso[sⱼ] + OPT(p(j)) > OPT(j − 1)`, inclui-se `sⱼ` e continua de `p(j)`; caso contrário, passa-se a `j − 1`. O desempate prefere não incluir (comparação estrita, D-18), tornando a solução determinística.

**Por que o guloso por menor fim falha.** A estratégia gulosa por menor término pode comprometer um show de peso alto por dois shows de peso baixo. Contraexemplo obrigatório (5.2 e T-304):

| Show | Início | Fim | Peso |
|------|--------|-----|------|
| A    | 18:00  | 19:00 | 1  |
| B    | 19:00  | 20:00 | 1  |
| C    | 18:30  | 19:30 | 10 |

Com `δ = 0`: o guloso ordena por `(fim, id)` → A, C, B. Seleciona A (roteiro: A); C é incompatível com A (18:30 < 19:00); seleciona B (roteiro: A, B). Peso total = 2. O ótimo é `{C}` com peso 10. Gap = 80%.

### 3.4 Verificação empírica (T-303)

`pytest tests/test_weighted.py` e `test_brute_force_equivalence.py` verificam que a DP retorna peso idêntico à força bruta em 500 instâncias aleatórias.

---

## 4. Deslocamento matricial: perda da garantia do guloso e recuperação pelo DAG

**Esboço.** Com custo dependente do par de palcos, a compatibilidade deixa de ser induzida por intervalos na reta: o "término efetivo" de um show depende do palco do show seguinte, que ainda não foi escolhido. O passo de troca falha porque trocar `or` por um `gr` que termina antes pode deixá-lo mais longe do próximo palco. Contraexemplo: A (10:00–11:00, P1), B (10:00–11:10, P2) e C (11:30–12:30, P2), com 40 minutos entre P1 e P2. O guloso pega A, que termina primeiro, e não chega a tempo em C; o ótimo é B seguido de C. A solução exata modela cada show como vértice, com aresta `i → j` quando `fim[i] + D[palco i][palco j] ≤ inicio[j]`. Toda aresta aponta para um show que começa depois, então o grafo é acíclico, a ordem de início é topológica, e o caminho de maior peso, calculado em `O(n²)`, é o roteiro ótimo. Verificação empírica: o DAG iguala a força bruta em 500 instâncias, enquanto o guloso é subótimo em 9,5% de 800 instâncias sintéticas (ver a análise experimental).

---

### 4.1 Por que o guloso perde a garantia no Modo B

No Modo A, a compatibilidade entre dois shows consecutivos `i` e `j` depende apenas de `fim[i]` e `inicio[j]`:

```
compativel_A(i, j)  ⟺  fim[i] + δ ≤ inicio[j]
```

O valor `fim[i] + δ` é uma propriedade **do show `i` sozinho**, independente de qual show virá depois. Isso é o que permite que o argumento de troca da Seção 1.3 funcione: ao comparar `fim_efetivo[gᵣ]` com `fim_efetivo[oᵣ]`, estamos comparando quantidades bem definidas para cada show individualmente.

No Modo B, o custo de deslocamento depende do **par de palcos**:

```
compativel_B(i, j)  ⟺  fim[i] + D[palco[i]][palco[j]] ≤ inicio[j]
```

O "término efetivo" de `i` em relação a `j` é `fim[i] + D[palco[i]][palco[j]]`, que **muda conforme qual show `j` vem em seguida**. Portanto não existe um único escalar `fim_efetivo[i]` associado ao show `i`: seu custo de saída varia dependendo do destino. A relação de compatibilidade deixa de ser induzida por intervalos na reta real e passa a ser uma relação binária arbitrária sobre pares de shows.

**Falha do argumento de troca:** na Seção 1.3, o passo central foi mostrar que `oᵣ` é compatível com `g_{r−1}` porque `fim_efetivo[g_{r−1}] ≤ fim_efetivo[o_{r−1}] ≤ inicio[oᵣ]`. No Modo B, mesmo que `fim[g_{r−1}] ≤ fim[o_{r−1}]`, pode ocorrer:

```
D[palco[g_{r-1}]][palco[oᵣ]]  ≫  D[palco[o_{r-1}]][palco[oᵣ]]
```

de modo que, apesar de `g_{r−1}` terminar antes, o custo de deslocamento até `oᵣ` torna a transição incompatível. O show de menor `fim` não é necessariamente o que deixa mais tempo livre para o próximo.

### 4.2 Contraexemplo explícito (citado no esboço e nos testes T-305)

Considere três shows e a matriz de deslocamento:

| Show | Palco | Início | Fim |
|------|-------|--------|-----|
| A    | P1    | 10:00 (600 min) | 11:00 (660 min) |
| B    | P2    | 10:00 (600 min) | 11:10 (670 min) |
| C    | P2    | 11:30 (690 min) | 12:30 (750 min) |

Matriz `D`:

| De \ Para | P1 | P2 |
|-----------|----|----|
| P1        | 0  | 40 |
| P2        | 40 | 0  |

**Guloso por menor `fim`:** ordena por `(fim, id)` → A (660), B (670), C (750). Seleciona A. Verifica C: `fim[A] + D[P1][P2] = 660 + 40 = 700 > 690 = inicio[C]`. Incompatível. Roteiro final: **{A}**, cardinalidade 1.

**Ótimo:** `{B, C}`. Verifica: `fim[B] + D[P2][P2] = 670 + 0 = 670 ≤ 690 = inicio[C]`. Compatível. Roteiro: **{B, C}**, cardinalidade 2.

O guloso escolheu A porque termina antes de B, mas a proximidade de B ao palco de C viabiliza a transição. Trocar A por B — um show de fim ligeiramente posterior — melhora o resultado. O argumento de troca é inválido aqui.

### 4.3 Como o DAG recupera a garantia de optimalidade

**Modelagem.** Constrói-se um grafo dirigido `G = (V, E)` onde:

- `V = S` (os shows são os vértices, mais uma fonte artificial `s₀` de peso 0 com aresta para todos).
- `E` contém a aresta `i → j` se e somente se `compativel_B(i, j)` e `inicio[j] > inicio[i]`.

**Aciclicidade.** Toda aresta `i → j` satisfaz `inicio[j] > inicio[i]` por construção. Portanto não existem ciclos no grafo: qualquer caminho percorre shows com início estritamente crescente. Ordenar os shows por `(inicio, id)` fornece uma **ordem topológica** de `G`. (Implementado em `dag_longest_path.py`, que chama `ordenar_cronologicamente`.)

**Equivalência entre roteiros e caminhos.** Um roteiro válido no Modo B é exatamente um caminho de `s₀` a algum vértice de `S` em `G`: a sequência de shows é compatível par a par, e a relação de compatibilidade é precisamente a condição de existência da aresta.

**Caminho de peso máximo em DAG.** Definindo `melhor[j]` como o maior peso de um caminho que termina em `sⱼ`, a recorrência de relaxação topológica é:

```
melhor[j] = peso[sⱼ] + max{ melhor[i] : i → j ∈ E } ∪ {0}
```

A relação é válida porque `G` é acíclico: ao processar `sⱼ` em ordem topológica, todos os predecessores `sᵢ` já foram processados. Isso garante a **subestrutura ótima**: qualquer prefixo de um caminho ótimo é ele mesmo um caminho ótimo para o subproblema correspondente.

**Corretude.** A DP sobre DAG em ordem topológica calcula exatamente `OPT = max_j melhor[j]`, que corresponde ao roteiro de maior peso válido no Modo B. Isso elimina a ambiguidade do argumento de troca: o DAG considera **todos os predecessores compatíveis** de cada show, escolhendo o que maximiza o peso acumulado, sem assumir que "terminar antes" é globalmente melhor.

**Complexidade.** Construção das arestas: `O(n²)` (para cada par `(i, j)`, verifica `compativel_B`). Relaxação topológica: `O(n²)` (para cada `j`, percorre todos `i < j`). Total: `O(n²)`, adequado para `n ∼ 100` shows de um dia de festival.

### 4.4 Verificação empírica (T-305 e T-303)

- `test_brute_force_equivalence.py` confirma que o DAG retorna peso idêntico à força bruta em 500 instâncias aleatórias do Modo B.
- `scripts/relatorio_modo_b.py` documenta em `docs/dados/modo_b.csv` que o guloso por menor término é subótimo em **9,5% das 800 instâncias sintéticas** do Modo B, enquanto no grupo de controle uniforme o percentual é **0%**. Essa assimetria valida que a falha é estrutural (ausência de transformação uniforme), e não um artefato das instâncias.

---

*Referências: KLEINBERG; TARDOS, Algorithm Design, cap. 4; CORMEN et al., Introduction to Algorithms, 4. ed., cap. 15; material da disciplina PA-FGA/UnB 2026.2.*
