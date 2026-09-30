"""Schemas de requisição e resposta da API (SPEC 4). Espelhados em frontend/src/types/index.ts."""

from typing import Literal

from pydantic import BaseModel, Field

from app.models.festival import ModoDeslocamento
from app.models.palco import Palco
from app.models.show import PESO_MAX, PESO_MIN

Estrategia = Literal[
    "interval_scheduling_guloso",
    "weighted_interval_scheduling_dp",
    "dag_longest_path",
    "guloso_menor_fim",
    "dp_ponderado",
    "fifo",
    "spt",
    "maior_peso",
]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class FestivalResumo(BaseModel):
    """Item de `GET /festivais` (4.1)."""

    id: str
    nome: str
    dias: int
    total_shows: int


class ShowGrade(BaseModel):
    """Show como exposto em `GET /festivais/{id}/grade` (4.2)."""

    id: str
    artista: str
    palco: str
    inicio: int
    fim: int
    peso: int


class GradeResponse(BaseModel):
    """Resposta de `GET /festivais/{id}/grade` (4.2)."""

    festival: str
    dia: int
    palcos: list[Palco]
    shows: list[ShowGrade]


class ErroLinha(BaseModel):
    """Erro de validação de CSV localizado por linha e coluna (3.1)."""

    linha: int
    coluna: str
    mensagem: str


class ErroImportacaoResponse(BaseModel):
    """Corpo 422 para grade inválida (4.2.2)."""

    detail: str
    erros: list[ErroLinha]


class ImportarResponse(FestivalResumo):
    """Resposta 201 de `POST /festivais/importar` (4.2.2)."""


class RequisicaoCalculo(BaseModel):
    """Requisição comum às rotas de cálculo (4.0.1, D-8)."""

    festival_id: str
    dia: int = Field(ge=1)
    modo_deslocamento: ModoDeslocamento | None = None
    delta_uniforme: int | None = Field(default=None, ge=0)
    pesos: dict[str, int] = Field(default_factory=dict)

    def peso_invalido(self) -> str | None:
        """Retorna o id do primeiro peso fora de [1, 10], ou None. O(k)."""
        return next((i for i, p in self.pesos.items() if not PESO_MIN <= p <= PESO_MAX), None)


class Deslocamento(BaseModel):
    de: str
    para: str
    palco_origem: str
    palco_destino: str
    custo_min: int
    folga_min: int


class RoteiroResponse(BaseModel):
    """Resposta de `/roteiro/maximo-shows` e `/roteiro/maxima-satisfacao` (4.3, 4.4)."""

    estrategia: Estrategia
    otimo_garantido: bool
    roteiro: list[str]
    total_shows: int
    peso_total: int
    deslocamentos: list[Deslocamento]
    tempo_execucao_ms: float


class FaixaSobreposicao(BaseModel):
    minuto: int
    simultaneos: int


class DimensionamentoResponse(BaseModel):
    """Resposta de `POST /dimensionamento` (4.5)."""

    palcos_minimos: int
    profundidade_maxima: int
    limite_inferior_atingido: bool
    palcos_reais: int
    alocacao: dict[str, list[str]]
    sobreposicao_por_faixa: list[FaixaSobreposicao]


class InstanciaResumo(BaseModel):
    total_shows: int
    dia: int
    modo_deslocamento: ModoDeslocamento


class ResultadoEstrategia(BaseModel):
    estrategia: Estrategia
    otimo_garantido: bool
    total_shows: int
    peso_total: int
    tempo_ms: float


class ComparativoResponse(BaseModel):
    """Resposta de `POST /comparativo` (4.6). `gap_percentual` segue D-12."""

    instancia: InstanciaResumo
    resultados: list[ResultadoEstrategia]
    gap_percentual: dict[str, float]
