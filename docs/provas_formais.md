# Provas Formais

Demonstrações de corretude e otimalidade dos algoritmos do RotaFest.

> Os itens abaixo são esboços escritos junto com a implementação de cada algoritmo. A versão final, com todos os passos, substitui cada esboço.

## 1. Interval Scheduling: otimalidade por argumento de troca

**Esboço.** No modo uniforme, dois shows `i` e `j` são compatíveis quando `fim[i] + δ ≤ inicio[j]`, o que equivale a trabalhar com os intervalos transformados `[inicio, fim + δ]` e exigir que não se sobreponham. Como `δ` é o mesmo para todos, a transformação soma uma constante a todo término e preserva a ordem entre eles; ordenar por `fim` ou por `fim + δ` dá a mesma sequência. Seja `G = g1..gk` a solução gulosa e `O = o1..om` uma solução ótima, ambas em ordem cronológica. Por indução, `fim[gr] ≤ fim[or]` para todo `r ≤ k`: vale para `r = 1` porque o guloso escolhe o menor término, e se vale para `r − 1`, então `or` é compatível com `g(r−1)` e estava disponível quando o guloso escolheu `gr`, que portanto termina no máximo junto com `or`. Se `m > k`, `o(k+1)` seria compatível com `gk` e o guloso não teria parado, contradição. Logo `k = m`.

## 2. Interval Partitioning: limite inferior pela profundidade

**Esboço.** Seja `d` o maior número de shows simultâneos em algum instante. Qualquer alocação usa pelo menos `d` palcos, porque os `d` shows daquele instante precisam de palcos distintos. O guloso processa os shows por início e só abre um palco novo para `s` quando todos os palcos abertos estão ocupados no instante `inicio[s]`; nesse instante há então `(palcos abertos) + 1` shows simultâneos, que é no máximo `d`. Portanto o guloso nunca passa de `d` e atinge exatamente o limite inferior. A implementação confirma isso empiricamente: a varredura de eventos, independente do heap, devolve o mesmo valor em 100 instâncias aleatórias.

## 3. Weighted Interval Scheduling: subestrutura ótima da recorrência

**Esboço.** Ordene os shows por `fim + δ` e defina `OPT(j)` como o maior peso de um roteiro usando apenas os `j` primeiros. Em uma solução ótima para os `j` primeiros, ou `j` não aparece, e o resto é ótimo para os `j − 1` primeiros, ou `j` aparece, e então nenhum show entre `p(j) + 1` e `j − 1` pode estar nela (todos terminam depois do início de `j`), de modo que o resto é ótimo para os `p(j)` primeiros. Daí `OPT(j) = max(peso[j] + OPT(p(j)), OPT(j − 1))`. Como os términos transformados estão ordenados, os shows compatíveis com `j` formam um prefixo, e `p(j)` sai por busca binária. O guloso por menor término falha aqui: com A (18:00–19:00, peso 1), B (19:00–20:00, peso 1) e C (18:30–19:30, peso 10), ele escolhe A e B (peso 2), enquanto o ótimo é C (peso 10).

## 4. Deslocamento matricial: perda da garantia do guloso e recuperação pelo DAG

**Esboço.** Com custo dependente do par de palcos, a compatibilidade deixa de ser induzida por intervalos na reta: o "término efetivo" de um show depende do palco do show seguinte, que ainda não foi escolhido. O passo de troca falha porque trocar `or` por um `gr` que termina antes pode deixá-lo mais longe do próximo palco. Contraexemplo: A (10:00–11:00, P1), B (10:00–11:10, P2) e C (11:30–12:30, P2), com 40 minutos entre P1 e P2. O guloso pega A, que termina primeiro, e não chega a tempo em C; o ótimo é B seguido de C. A solução exata modela cada show como vértice, com aresta `i → j` quando `fim[i] + D[palco i][palco j] ≤ inicio[j]`. Toda aresta aponta para um show que começa depois, então o grafo é acíclico, a ordem de início é topológica, e o caminho de maior peso, calculado em `O(n²)`, é o roteiro ótimo.
