# Análise Experimental

Resultados empíricos do RotaFest. Toda afirmação numérica vem acompanhada do dado que a sustenta.

## 1. Guloso contra solução exata no deslocamento matricial

**Pergunta.** Quando o tempo de caminhada depende do par de palcos, o guloso por menor término deixa de ter garantia de otimalidade. Com que frequência ele de fato erra, e por quanto?

**Método.** Instâncias sintéticas com 4 palcos e densidade de sobreposição 1,5, variando o número de shows (`n` = 10, 20, 40 e 80) e o deslocamento máximo entre palcos (5, 15, 30 e 60 minutos), com 50 seeds por cenário: 800 instâncias. Em cada uma, o número de shows do guloso é comparado ao ótimo do caminho máximo em DAG. O mesmo conjunto rodado com deslocamento uniforme (delta igual à média do intervalo) serve de **grupo de controle**: ali o guloso é comprovadamente ótimo, então qualquer perda indicaria erro no experimento.

Reprodução: `cd backend && uv run python scripts/relatorio_modo_b.py`. Os dados por instância estão em [`dados/modo_b.csv`](./dados/modo_b.csv).

**Resultados por cenário (deslocamento matricial).**

| Cenário | Instâncias | Guloso subótimo | Perda média (shows) | Perda máxima | Perda média (%) |
|---|---:|---:|---:|---:|---:|
| n=10, deslocamento até 5 min | 50 | 0.0% | 0.00 | 0 | 0.0% |
| n=10, deslocamento até 15 min | 50 | 2.0% | 0.02 | 1 | 0.5% |
| n=10, deslocamento até 30 min | 50 | 0.0% | 0.00 | 0 | 0.0% |
| n=10, deslocamento até 60 min | 50 | 4.0% | 0.04 | 1 | 1.3% |
| n=20, deslocamento até 5 min | 50 | 0.0% | 0.00 | 0 | 0.0% |
| n=20, deslocamento até 15 min | 50 | 2.0% | 0.02 | 1 | 0.4% |
| n=20, deslocamento até 30 min | 50 | 14.0% | 0.14 | 1 | 2.5% |
| n=20, deslocamento até 60 min | 50 | 16.0% | 0.18 | 2 | 3.3% |
| n=40, deslocamento até 5 min | 50 | 0.0% | 0.00 | 0 | 0.0% |
| n=40, deslocamento até 15 min | 50 | 6.0% | 0.06 | 1 | 0.5% |
| n=40, deslocamento até 30 min | 50 | 18.0% | 0.18 | 1 | 1.6% |
| n=40, deslocamento até 60 min | 50 | 26.0% | 0.30 | 2 | 2.9% |
| n=80, deslocamento até 5 min | 50 | 0.0% | 0.00 | 0 | 0.0% |
| n=80, deslocamento até 15 min | 50 | 12.0% | 0.12 | 1 | 0.5% |
| n=80, deslocamento até 30 min | 50 | 14.0% | 0.14 | 1 | 0.7% |
| n=80, deslocamento até 60 min | 50 | 38.0% | 0.50 | 3 | 2.5% |

**Totais.**

| Cenário | Instâncias | Guloso subótimo | Perda média (shows) | Perda máxima | Perda média (%) |
|---|---:|---:|---:|---:|---:|
| Matricial, todas | 800 | 9.5% | 0.11 | 3 | 1.0% |
| Matricial, matriz viola a desigualdade triangular | 629 | 9.1% | 0.10 | 3 | 0.9% |
| Matricial, matriz respeita a desigualdade triangular | 171 | 11.1% | 0.13 | 3 | 1.5% |
| Controle: uniforme | 800 | 0.0% | 0.00 | 0 | 0.0% |

**Leitura.**

- O controle uniforme não teve nenhuma perda em 800 instâncias, coerente com a prova de otimalidade do guloso nesse modo.
- No deslocamento matricial, o guloso foi subótimo em 9,5% das instâncias. A frequência cresce com a distância entre palcos: com deslocamento de até 5 minutos ele nunca errou, e com até 60 minutos errou em 4% a 38% das instâncias, conforme `n`.
- A frequência também cresce com o tamanho da grade: com deslocamento de até 60 minutos, foi de 4% (`n` = 10) a 38% (`n` = 80).
- Quando erra, o guloso erra pouco: a perda média é de 1,0% do ótimo e a maior perda observada foi de 3 shows. A falha é real, mas rara e pequena, o que explica por que ela passa despercebida na intuição e só aparece com a solução exata ao lado.
- A violação da desigualdade triangular não aumentou a frequência de erro (9,1% contra 11,1% sem violação). O que pesa é a assimetria entre palcos próximos e distantes, não a violação em si.
- Ressalva: com 50 seeds por cenário, cada ponto percentual equivale a meio show, e cenários vizinhos oscilam (por exemplo, `n` = 10 com 15 e 30 minutos). As tendências acima valem para o conjunto, não para cada linha isolada.

### Verificação de corretude contra força bruta

Os algoritmos exatos foram comparados com a enumeração exaustiva de todos os roteiros válidos em 500 instâncias aleatórias com até 12 shows, variando densidade, número de palcos e deslocamento:

| Propriedade | Instâncias | Divergências |
|---|---:|---:|
| Guloso tem a cardinalidade máxima (deslocamento uniforme) | 500 | 0 |
| DP ponderada tem o peso máximo (deslocamento uniforme) | 500 | 0 |
| DAG tem a cardinalidade e o peso máximos (deslocamento matricial) | 500 | 0 |

Para garantir que o teste distingue um algoritmo certo de um errado: nas mesmas instâncias, 407 das 500 têm conflitos reais (o ótimo não inclui todos os shows), trocar o guloso por FIFO seria detectado em 48 instâncias e trocar a DP pelo guloso, em 292. Reprodução: `cd backend && uv run pytest tests/test_brute_force_equivalence.py`.

## 2. Tempo de execução contra tamanho da instância

## 3. Comparativo entre estratégias no festival de exemplo
