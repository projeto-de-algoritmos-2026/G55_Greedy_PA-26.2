"""Schemas de requisição e resposta da API. Espelhados em frontend/src/types/index.ts."""

from typing import Annotated, Literal

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
    """Item de `GET /festivais`."""

    id: str
    nome: str
    dias: int
    total_shows: int


class ShowGrade(BaseModel):
    """Show como exposto em `GET /festivais/{id}/grade`."""

    id: str
    artista: str
    palco: str
    inicio: int
    fim: int
    peso: int


class GradeResponse(BaseModel):
    """Resposta de `GET /festivais/{id}/grade`."""

    festival: str
    dia: int
    palcos: list[Palco]
    shows: list[ShowGrade]


class ErroLinha(BaseModel):
    """Erro de validação de CSV localizado por linha e coluna."""

    linha: int
    coluna: str
    mensagem: str


class ErroCampo(BaseModel):
    """Erro de validação de um campo da requisição."""

    campo: str
    mensagem: str


class ErroValidacaoResponse(BaseModel):
    """Corpo 422 para requisição malformada."""

    detail: str
    erros: list[ErroCampo]


class ErroImportacaoResponse(BaseModel):
    """Corpo 422 para grade inválida."""

    detail: str
    erros: list[ErroLinha]


class ImportarResponse(FestivalResumo):
    """Resposta 201 de `POST /festivais/importar`."""


class RequisicaoCalculo(BaseModel):
    """Requisição comum às rotas de cálculo. Shows ausentes em `pesos` valem 1."""

    festival_id: str
    dia: int = Field(ge=1)
    modo_deslocamento: ModoDeslocamento | None = None
    delta_uniforme: int | None = Field(default=None, ge=0)
    pesos: dict[str, Annotated[int, Field(ge=PESO_MIN, le=PESO_MAX)]] = Field(default_factory=dict)


class RequisicaoValidar(RequisicaoCalculo):
    """Requisição de `POST /validar`. `shows` restringe a instância a um subconjunto do dia."""

    shows: list[str] | None = None


class Deslocamento(BaseModel):
    de: str
    para: str
    palco_origem: str
    palco_destino: str
    custo_min: int
    folga_min: int


class RoteiroResponse(BaseModel):
    """Resposta de `/roteiro/maximo-shows` e `/roteiro/maxima-satisfacao`."""

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
    """Resposta de `POST /dimensionamento`."""

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
    """Resposta de `POST /comparativo`. gap = (peso ótimo - peso da heurística) / peso ótimo x 100."""

    instancia: InstanciaResumo
    resultados: list[ResultadoEstrategia]
    gap_percentual: dict[str, float]


class ItemValidacao(BaseModel):
    """Comparação de um algoritmo com a força bruta em uma métrica."""

    algoritmo: Estrategia
    metrica: Literal["total_shows", "peso_total"]
    valor_algoritmo: int
    valor_forca_bruta: int
    confere: bool


class ValidarResponse(BaseModel):
    """Resposta de `POST /validar`."""

    total_shows: int
    modo_deslocamento: ModoDeslocamento
    itens: list[ItemValidacao]
    todos_conferem: bool
