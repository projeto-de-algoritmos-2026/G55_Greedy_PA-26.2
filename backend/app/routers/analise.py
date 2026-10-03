"""Rotas de análise: dimensionamento de palcos, comparativo entre estratégias e validação."""

from fastapi import APIRouter

from app.algorithms.interval_partitioning import interval_partitioning, profundidade_maxima
from app.models.schemas import (
    ComparativoResponse,
    DimensionamentoResponse,
    FaixaSobreposicao,
    RequisicaoCalculo,
    RequisicaoValidar,
    ValidarResponse,
)
from app.services.calculo import preparar_instancia, restringir
from app.services.comparator import comparar, validar

router = APIRouter(tags=["análise"])


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


@router.post("/comparativo", response_model=ComparativoResponse)
def post_comparativo(req: RequisicaoCalculo) -> ComparativoResponse:
    """Todas as estratégias sobre a mesma instância, com a perda de cada heurística."""
    return comparar(preparar_instancia(req))


@router.post("/validar", response_model=ValidarResponse)
def post_validar(req: RequisicaoValidar) -> ValidarResponse:
    """Compara os algoritmos com a força bruta. Aceita no máximo 20 shows; use `shows` para escolher."""
    instancia = preparar_instancia(req)
    if req.shows is not None:
        instancia = restringir(instancia, req.shows)
    return validar(instancia)
