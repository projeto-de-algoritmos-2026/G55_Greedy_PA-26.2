"""Rotas de análise: dimensionamento de palcos, comparativo entre estratégias, validação e benchmark."""

import statistics

from fastapi import APIRouter, Query

from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.gerador import gerar_instancia
from app.algorithms.interval_partitioning import interval_partitioning, profundidade_maxima
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoMatricial, CustoUniforme
from app.algorithms.weighted_scheduling import weighted_interval_scheduling
from app.models.schemas import (
    BenchmarkResponse,
    ComparativoResponse,
    DimensionamentoResponse,
    FaixaSobreposicao,
    PontoBenchmark,
    RequisicaoCalculo,
    RequisicaoValidar,
    ValidarResponse,
)
from app.services.calculo import cronometrar, preparar_instancia, restringir
from app.services.comparator import comparar, validar

router = APIRouter(tags=["análise"])


# ---------------------------------------------------------------------------
# Dimensionamento
# ---------------------------------------------------------------------------

@router.post("/dimensionamento", response_model=DimensionamentoResponse)
def post_dimensionamento(req: RequisicaoCalculo) -> DimensionamentoResponse:
    """Número mínimo de palcos para a grade do dia, comparado aos palcos realmente usados."""
    instancia = preparar_instancia(req)
    recursos = interval_partitioning(instancia.shows)
    profundidade, serie = profundidade_maxima(instancia.shows)
    return DimensionamentoResponse(
        palcos_minimos=len(recursos),
        profundidade_maxima=profundidade,
        limite_inferior_atingido=len(recursos) == profundidade,
        palcos_reais=len({s.palco for s in instancia.shows}),
        alocacao={f"SALA_{i}": [s.id for s in recurso] for i, recurso in enumerate(recursos, start=1)},
        sobreposicao_por_faixa=[FaixaSobreposicao(minuto=m, simultaneos=q) for m, q in serie],
    )


# ---------------------------------------------------------------------------
# Comparativo
# ---------------------------------------------------------------------------

@router.post("/comparativo", response_model=ComparativoResponse)
def post_comparativo(req: RequisicaoCalculo) -> ComparativoResponse:
    """Todas as estratégias sobre a mesma instância, com a perda de cada heurística."""
    return comparar(preparar_instancia(req))


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------

@router.post("/validar", response_model=ValidarResponse)
def post_validar(req: RequisicaoValidar) -> ValidarResponse:
    """Compara os algoritmos com a força bruta. Aceita no máximo 20 shows; use `shows` para escolher."""
    instancia = preparar_instancia(req)
    if req.shows is not None:
        instancia = restringir(instancia, req.shows)
    return validar(instancia)


# ---------------------------------------------------------------------------
# Benchmark (T-704)
# ---------------------------------------------------------------------------

_ALGORITMOS_BENCHMARK = [
    ("interval_scheduling", "O(n log n)"),
    ("weighted_scheduling", "O(n log n)"),
    ("interval_partitioning", "O(n log n)"),
    ("dag_longest_path", "O(n²)"),
]


def _medir_ponto(n: int, repeticoes: int, delta: int, seed_base: int) -> list[PontoBenchmark]:
    """Mede o tempo médio de cada algoritmo para instâncias de tamanho n.

    Usa sementes distintas por repetição para evitar viés de cache.
    Complexidade: O(repeticoes × n²).
    """
    tempos: dict[str, list[float]] = {nome: [] for nome, _ in _ALGORITMOS_BENCHMARK}
    for rep in range(repeticoes):
        shows, matriz = gerar_instancia(n=n, densidade=1.0, palcos=4, seed=seed_base + rep)
        custo_u = CustoUniforme(delta)
        custo_m = CustoMatricial(matriz)
        for nome, _ in _ALGORITMOS_BENCHMARK:
            if nome == "interval_scheduling":
                _, ms = cronometrar(lambda: interval_scheduling(shows, custo_u))
            elif nome == "weighted_scheduling":
                _, ms = cronometrar(lambda: weighted_interval_scheduling(shows, custo_u))
            elif nome == "interval_partitioning":
                _, ms = cronometrar(lambda: interval_partitioning(shows))
            else:
                _, ms = cronometrar(lambda: dag_longest_path(shows, custo_m))
            tempos[nome].append(ms)

    return [
        PontoBenchmark(
            n=n,
            algoritmo=nome,
            complexidade=complexidade,
            tempo_ms_medio=round(statistics.mean(tempos[nome]), 6),
        )
        for nome, complexidade in _ALGORITMOS_BENCHMARK
    ]


@router.get("/benchmark", response_model=BenchmarkResponse)
def get_benchmark(
    ns: list[int] = Query(default=[10, 20, 50, 100, 200, 300, 500]),
    repeticoes: int = Query(default=3, ge=1, le=10),
    delta: int = Query(default=12, ge=0),
    seed: int = Query(default=42),
) -> BenchmarkResponse:
    """Mede o tempo real dos algoritmos para valores crescentes de n.

    Gera instâncias sintéticas com `gerar_instancia` e executa os algoritmos reais.
    Adequado para verificar O(n log n) vs O(n²) empiricamente.
    """
    pontos: list[PontoBenchmark] = []
    for n in sorted(set(ns)):
        pontos.extend(_medir_ponto(n, repeticoes, delta, seed))

    return BenchmarkResponse(
        ns=sorted(set(ns)),
        repeticoes=repeticoes,
        delta_uniforme=delta,
        pontos=pontos,
    )
