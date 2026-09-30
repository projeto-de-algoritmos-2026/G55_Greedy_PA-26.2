# RotaFest

**Conteúdo da Disciplina:** Greed (Algoritmos Ambiciosos)<br>

## Alunos

| Foto | Nome | Matrícula |
| :---: | :--- | ---: |
| ![Gabriel Lima](https://github.com/gabriel-lima258.png?size=100) | **Gabriel Lima** | 222037610 |
| ![Mateus Bastos](https://github.com/MateuSansete.png?size=100) | **Mateus Bastos** | 211062240 |

---

## Sobre

**RotaFest** é um planejador de roteiro para festivais de música que resolve um problema que todo frequentador conhece: em um festival com vários palcos simultâneos, é impossível assistir a tudo. Dois shows que você quer ver começam no mesmo horário, e ainda existe o tempo de caminhada entre um palco e outro.

O projeto modela a grade do festival como um **conjunto de intervalos** (cada show é um intervalo com horário de início, horário de término e palco de origem) e aplica algoritmos ambiciosos para responder a três perguntas distintas:

1. **Qual o maior número de shows que consigo assistir por completo?**
   Resolvido por *Interval Scheduling* guloso, com garantia de otimalidade.

2. **Qual o roteiro que maximiza minha satisfação, e não apenas a quantidade?**
   Cada show recebe uma nota de preferência de 1 a 10. Aqui o guloso **deixa de ser ótimo**, e a solução correta exige *Weighted Interval Scheduling* por programação dinâmica. O confronto entre os dois é o núcleo analítico do trabalho.

3. **Quantos palcos, no mínimo, o festival precisaria para acomodar toda a grade?**
   Resolvido por *Interval Partitioning* com fila de prioridade, comparando o resultado com o número de palcos que o festival efetivamente utilizou.

### O diferencial: custo de deslocamento

A modelagem ingênua trata dois shows como compatíveis sempre que um termina antes do outro começar. Isso é falso no mundo real: se o próximo show está em um palco a doze minutos de caminhada, o intervalo efetivamente ocupado é maior do que a duração do show.

O RotaFest resolve isso aplicando uma **transformação sobre os intervalos antes de executar o guloso**. O horário de término de cada show é inflado pelo tempo de deslocamento até o palco do show seguinte, com base em uma matriz de distâncias entre palcos. O algoritmo guloso opera sobre os intervalos transformados e **permanece comprovadamente ótimo**, porque a transformação preserva a relação de ordem entre os términos. A demonstração formal dessa equivalência consta na documentação do projeto.

### Público e aplicação

A saída é uma grade visual no formato que o público já conhece dos aplicativos oficiais de festival, com os shows selecionados em destaque e os descartados em cinza, mais uma rota desenhada sobre o mapa do evento. O objetivo é tornar o comportamento do algoritmo **legível para quem não conhece o algoritmo**.

---

## Funcionalidades e Algoritmos

### Algoritmos implementados

| # | Algoritmo | Estratégia | Complexidade | Ótimo? |
|:-:|---|---|:-:|:-:|
| 1 | **Interval Scheduling** | Guloso por menor horário de término | O(n log n) | Sim |
| 2 | **Weighted Interval Scheduling** | Programação dinâmica com busca binária | O(n log n) | Sim |
| 3 | **Interval Partitioning** | Guloso por horário de início com min-heap | O(n log n) | Sim |
| 4 | **Heurísticas de comparação** | FIFO, SPT e maior preferência | O(n log n) | Não |

#### 1. Interval Scheduling (maximização de quantidade)

Ordena os shows pelo horário de término e seleciona iterativamente o primeiro compatível com o último escolhido. A otimalidade é demonstrada por **argumento de troca**: qualquer solução ótima pode ser transformada na solução gulosa sem redução de cardinalidade.

#### 2. Weighted Interval Scheduling (maximização de satisfação)

Com pesos, o guloso falha. O projeto inclui um **contraexemplo mínimo explícito**, em que um show de peso alto e longa duração é descartado pelo guloso em favor de dois shows curtos de peso baixo. A solução exata usa a recorrência `OPT(j) = max(peso[j] + OPT(p(j)), OPT(j-1))`, onde `p(j)` é o último show compatível com `j`, localizado por busca binária.

#### 3. Interval Partitioning (dimensionamento de palcos)

Processa os shows por horário de início mantendo um min-heap dos horários de liberação de cada palco. O **limite inferior** é a profundidade máxima de sobreposição da grade, e o guloso nunca ultrapassa esse limite, o que fecha a prova de otimalidade em poucas linhas.

#### 4. Heurísticas de comparação

Implementadas exclusivamente para contraste empírico:

- **FIFO** (*First In, First Out*): seleciona por ordem de início.
- **SPT** (*Shortest Processing Time*): seleciona por menor duração.
- **Maior preferência**: seleciona pela maior nota, ignorando conflitos futuros.

### Funcionalidades da aplicação

- [x] Importação da grade do festival via CSV ou JSON
- [x] Atribuição de nota de preferência de 1 a 10 por show
- [x] Grade visual por palco e faixa horária, com selecionados e descartados
- [x] Cálculo de custo de deslocamento a partir da matriz de distâncias entre palcos
- [x] Timeline lateral com horários efetivos e atrasos previstos
- [x] Rota contínua sobre o mapa do festival com marcadores numerados
- [x] Painel comparativo entre o guloso, a solução ótima ponderada e as heurísticas
- [x] Gráfico de sobreposição por faixa horária, evidenciando o pico que define o número mínimo de palcos
- [x] Verificador por força bruta para instâncias com até 15 shows
- [x] Gerador de instâncias sintéticas para teste de desempenho

---

## Tecnologias Utilizadas

<!-- AJUSTAR: confirmar ou substituir a stack abaixo -->

### Frontend

| Tecnologia | Uso |
|---|---|
| **React 18** | Construção da interface |
| **TypeScript** | Tipagem estática dos modelos de intervalo |
| **Vite** | Bundler e servidor de desenvolvimento |
| **TailwindCSS** | Estilização da grade e dos componentes |
| **Leaflet** | Renderização do mapa e da rota entre palcos |
| **Recharts** | Gráficos de sobreposição e do comparativo |

### Backend

| Tecnologia | Uso |
|---|---|
| **Python 3.11+** | Linguagem dos algoritmos |
| **FastAPI** | API REST que expõe os endpoints de cálculo |
| **Pydantic** | Validação dos payloads de entrada |
| **heapq** | Fila de prioridade do Interval Partitioning |
| **pytest** | Testes unitários e verificação contra força bruta |
| **Uvicorn** | Servidor ASGI |

---

## Estrutura do Projeto

```
G55_Greedy_PA-26.2/
├── backend/
│   ├── app/
│   │   ├── algorithms/
│   │   │   ├── interval_scheduling.py
│   │   │   ├── weighted_scheduling.py
│   │   │   ├── interval_partitioning.py
│   │   │   ├── heuristics.py
│   │   │   └── travel_cost.py
│   │   ├── models/
│   │   │   └── show.py
│   │   ├── data/
│   │   │   ├── grade_festival.csv
│   │   │   └── matriz_palcos.json
│   │   └── main.py
│   ├── tests/
│   │   ├── test_optimality.py
│   │   └── test_brute_force.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   └── provas_formais.md
└── README.md
```

---

## Instalação e Execução

### Pré-requisitos

- Python 3.11 ou superior
- Node.js 18 ou superior
- npm ou yarn

### 1. Clonando o Repositório

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G55_Greedy_PA-26.2.git
cd G55_Greedy_PA-26.2
```

### 2. Configurando o Backend

```bash
cd backend

# Criar e ativar o ambiente virtual
python -m venv venv

# Linux ou macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Instalar as dependências
pip install -r requirements.txt

# Executar o servidor
uvicorn app.main:app --reload --port 8000
```

O backend ficará disponível em `http://localhost:8000`.
A documentação interativa da API fica em `http://localhost:8000/docs`.

### 3. Configurando o Frontend

```bash
# A partir da raiz do projeto, em outro terminal
cd frontend

# Instalar as dependências
npm install

# Criar o arquivo de variáveis de ambiente
echo "VITE_API_URL=http://localhost:8000" > .env

# Executar em modo de desenvolvimento
npm run dev
```

O frontend ficará disponível em `http://localhost:5173`.

### 4. Executando os Testes

```bash
cd backend
pytest -v
```

A suíte inclui a verificação das soluções gulosas contra força bruta em instâncias reduzidas, que é a evidência empírica da corretude.

---

## Uso

1. Acesse `http://localhost:5173` com o backend em execução.
2. Selecione o festival na lista ou carregue sua própria grade em CSV.
3. Ajuste a **nota de preferência** de cada show no painel lateral, de 1 a 10. Shows sem nota recebem peso neutro.
4. Defina o **tempo médio de deslocamento entre palcos** ou carregue a matriz de distâncias personalizada.
5. Escolha o modo de otimização:
   - **Máximo de shows**: executa o Interval Scheduling guloso.
   - **Máxima satisfação**: executa o Weighted Interval Scheduling por programação dinâmica.
6. Clique em **"Gerar Roteiro"**. A aplicação irá:
   - Executar o algoritmo selecionado sobre os intervalos transformados.
   - Calcular os custos reais de deslocamento e gerar a timeline lateral com os horários e possíveis atrasos.
   - Desenhar a rota contínua no mapa com marcadores numerados.
7. Use a aba **"Dimensionamento"** para executar o Interval Partitioning e visualizar o número mínimo de palcos ao lado do gráfico de sobreposição por faixa horária.
8. Clique em **"Ver Comparativo (Greed vs Outros)"** para visualizar a comparação direta contra FIFO e SPT.

---

## Screenshots

<!-- AJUSTAR: substituir pelos prints reais -->

| Grade do festival | Rota no mapa |
| :---: | :---: |
| ![Grade](./docs/img/grade.png) | ![Mapa](./docs/img/mapa.png) |

| Comparativo entre estratégias | Dimensionamento de palcos |
| :---: | :---: |
| ![Comparativo](./docs/img/comparativo.png) | ![Partitioning](./docs/img/partitioning.png) |

---

## Vídeo de Apresentação

<!-- AJUSTAR: inserir o link -->

[Assista à apresentação do projeto](LINK_DO_VIDEO)

---

## Referências

- KLEINBERG, Jon; TARDOS, Éva. *Algorithm Design*. Boston: Pearson, 2006. Capítulo 4: Greedy Algorithms.
- CORMEN, Thomas H. et al. *Introduction to Algorithms*. 4. ed. Cambridge: MIT Press, 2022. Capítulo 15: Greedy Algorithms.
- Material da disciplina Projeto de Algoritmos, FGA/UnB, 2026.2.

---

## Licença

Projeto acadêmico desenvolvido para a disciplina Projeto de Algoritmos da Universidade de Brasília, campus Gama.
