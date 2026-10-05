# Roteiro de Apresentação — RotaFest

Guia para demonstração das **quatro questões da disciplina** e do **contraexemplo**, com o sistema ao vivo.

> **Pré-condição:** `docker compose up --build` (ou backend + frontend via uv/npm) em execução.  
> URL: `http://localhost:5173` | API Docs: `http://localhost:8000/docs`

---

## Q1 — Qual o maior número de shows que consigo assistir por completo?

**Algoritmo:** Interval Scheduling guloso (modo uniforme) / DAG Longest Path (modo matricial)  
**Complexidade:** O(n log n) / O(n²) | **Otimalidade:** garantida em ambos os modos.

### Demonstração ao vivo

1. Acesse `http://localhost:5173`, selecione **Festival Exemplo**, Dia 1.
2. No Planejador, escolha modo **Uniforme**, clique em **"Máximo de shows"**.
3. Observe o badge **"Ótimo garantido"** na resposta.
4. Repita com modo **Matricial** — ainda mostra "Ótimo garantido" (agora via DAG).
5. Compare a timeline: no matricial, mostra o custo real de deslocamento entre palcos.

### Via API (reprodução direta)

```bash
curl -s -X POST http://localhost:8000/api/roteiro/maximo-shows \
  -H "Content-Type: application/json" \
  -d '{"festival_id":"festival-exemplo","dia":1,"modo_deslocamento":"uniforme"}' \
  | python3 -m json.tool | head -20
```

---

## Q2 — Qual o roteiro que maximiza minha satisfação?

**Algoritmo:** Weighted Interval Scheduling (DP, modo uniforme) / DAG de maior peso (matricial)  
**Complexidade:** O(n log n) / O(n²) | **Otimalidade:** garantida.

### Demonstração ao vivo

1. Na mesma tela, atribua notas altas (ex: 10) a 2-3 shows que se sobrepõem.
2. Clique em **"Máxima satisfação"**.
3. Observe que o roteiro seleciona **menos shows** mas de maior peso total — o algoritmo descartou shows de nota baixa para incluir os de alta nota.
4. Compare com o roteiro de **Q1**: o de quantidade não é o mesmo de satisfação quando os pesos diferem.

### Via API

```bash
curl -s -X POST http://localhost:8000/api/roteiro/maxima-satisfacao \
  -H "Content-Type: application/json" \
  -d '{"festival_id":"festival-exemplo","dia":1,"modo_deslocamento":"uniforme","pesos":{"S005":10,"S010":9,"S023":8}}' \
  | python3 -m json.tool | head -20
```

---

## Q3 — Quantos palcos, no mínimo, o festival precisaria?

**Algoritmo:** Interval Partitioning com min-heap  
**Complexidade:** O(n log n) | **Otimalidade:** atingida (palcos_minimos == profundidade_maxima).

### Demonstração ao vivo

1. No Planejador, clique em **"Dimensionamento"** no cabeçalho.
2. Observe os três cards: **Mínimo necessário = 4**, **Real = 4**, **Suficiente**.
3. O gráfico de barras abaixo mostra a sobreposição temporal real — o pico de 4 shows simultâneos justifica o lower bound de 4 palcos.
4. Isso confirma que o festival `festival-exemplo` está otimamente dimensionado.

### Via API

```bash
curl -s -X POST http://localhost:8000/api/dimensionamento \
  -H "Content-Type: application/json" \
  -d '{"festival_id":"festival-exemplo","dia":1}' \
  | python3 -m json.tool
```

---

## Q4 — Onde e por quanto o guloso ponderado perde a otimalidade?

**Demonstração:** Comparativo ao vivo + experimento de 800 instâncias.

### Demonstração ao vivo (contraexemplo instantâneo)

1. No Planejador, clique em **"Comparativo"** no cabeçalho.
2. Atribua notas altas a shows com tempo longo e sobreposição (ex: S023=10, S013=7, S005=8, S010=9).
3. Observe na tabela: **Guloso obtém peso 17**, **DAG obtém peso 32** — gap de **46,9%**.
4. O guloso escolheu quantidade (10 shows) ignorando preferência; o DAG escolheu qualidade (8 shows de alto peso).
5. O badge **"Não"** na coluna Ótimo Garantido confirma que o guloso não tem garantia.

### Via API (contraexemplo mínimo documentado)

```bash
curl -s -X POST http://localhost:8000/api/comparativo \
  -H "Content-Type: application/json" \
  -d '{"festival_id":"festival-exemplo","dia":1,"modo_deslocamento":"matricial","pesos":{"S023":10,"S013":7,"S005":8,"S010":9}}' \
  | python3 -m json.tool
```

Resposta esperada: `gap_percentual.fifo = 46.9`, `gap_percentual.spt = 75.0`.

### Experimento de escala (800 instâncias)

```bash
cd backend && uv run python scripts/relatorio_modo_b.py
```

- Guloso subótimo em **9,5% de 800 instâncias** no modo matricial.
- Controle uniforme: **0% de falhas** em 800 instâncias (confirma a prova).
- Perda máxima observada: **3 shows**.

---

## Contraexemplo Mínimo (para o guloso ponderado)

O contraexemplo teórico do guloso por menor término com pesos está em `docs/provas_formais.md` (seção Weighted Interval Scheduling).

**Instância mínima:**

| Show | Início | Fim | Peso |
|---|---|---|---|
| A | 0 | 5 | 3 |
| B | 4 | 9 | 3 |
| C | 0 | 10 | 7 |

- Guloso por menor término escolhe A (fim=5), depois B (fim=9) → **peso total = 6**.
- Ótimo: escolhe apenas C → **peso total = 7**.
- O guloso falhou mesmo com os intervalos bem separados.

---

## Benchmark (bônus)

```bash
# CLI
cd backend && uv run python scripts/benchmark.py --ns 10 50 100 500 --repeticoes 3

# Interface web
http://localhost:5173/benchmark → clicar em "Rodar Benchmark"
```

Demonstra empiricamente O(n log n) vs O(n²): com n=1000, DAG leva ~95ms enquanto Interval Scheduling leva <1ms.
