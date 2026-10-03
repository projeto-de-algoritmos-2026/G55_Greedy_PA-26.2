"""Rotas de roteiro: mais shows e maior satisfação."""

from fastapi import APIRouter

from app.models.schemas import RequisicaoCalculo, RoteiroResponse
from app.services.calculo import maxima_satisfacao, maximo_shows, preparar_instancia

router = APIRouter(prefix="/roteiro", tags=["roteiro"])


@router.post("/maximo-shows", response_model=RoteiroResponse)
def post_maximo_shows(req: RequisicaoCalculo) -> RoteiroResponse:
    """Maior número de shows assistidos por completo, considerando o deslocamento."""
    return maximo_shows(preparar_instancia(req))


@router.post("/maxima-satisfacao", response_model=RoteiroResponse)
def post_maxima_satisfacao(req: RequisicaoCalculo) -> RoteiroResponse:
    """Roteiro de maior soma de pesos de preferência, considerando o deslocamento."""
    return maxima_satisfacao(preparar_instancia(req))
