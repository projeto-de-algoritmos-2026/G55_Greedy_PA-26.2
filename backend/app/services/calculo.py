"""Preparação das instâncias de cálculo e montagem das respostas de roteiro.

Fica entre as rotas HTTP e os algoritmos: resolve festival, dia, modo de deslocamento e
pesos a partir da requisição, e transforma o roteiro devolvido pelo algoritmo na resposta da API.
"""

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeVar

from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoDeslocamento, CustoMatricial, CustoUniforme, peso_total
from app.algorithms.weighted_scheduling import weighted_interval_scheduling
from app.models.festival import Festival, ModoDeslocamento
from app.models.schemas import Deslocamento, Estrategia, RequisicaoCalculo, RoteiroResponse
from app.models.show import Show
from app.services.loader import carregar_festival

T = TypeVar("T")


class ErroRequisicao(ValueError):
    """Requisição bem formada, mas incoerente com os dados (vira 422)."""


class DiaSemShows(LookupError):
    """O festival não tem shows no dia pedido (vira 404)."""


@dataclass(frozen=True)
class Instancia:
    """Tudo o que um algoritmo precisa para rodar sobre um dia de festival."""

    festival: Festival
    dia: int
    modo: ModoDeslocamento
    custo: CustoDeslocamento
    shows: list[Show]


def preparar_instancia(req: RequisicaoCalculo) -> Instancia:
    """Resolve festival, dia, custo de deslocamento e pesos da requisição. O(n log n).

    Modo e delta ausentes usam o padrão do palcos.json. Pesos para ids que não existem no dia
    levantam ErroRequisicao; dia sem shows levanta DiaSemShows.
    """
    festival = carregar_festival(req.festival_id)
    shows = festival.shows_do_dia(req.dia)
    if not shows:
        raise DiaSemShows(
            f"O festival '{festival.nome}' não tem shows no dia {req.dia} "
            f"(dias disponíveis: 1 a {festival.dias})."
        )

    ids_do_dia = {s.id for s in shows}
    desconhecidos = sorted(set(req.pesos) - ids_do_dia)
    if desconhecidos:
        raise ErroRequisicao(
            f"Pesos para shows que não existem no dia {req.dia}: {', '.join(desconhecidos)}."
        )

    config = festival.deslocamento
    modo = req.modo_deslocamento or config.modo_padrao
    custo: CustoDeslocamento = (
        CustoMatricial(config.matriz)
        if modo == "matricial"
        else CustoUniforme(req.delta_uniforme if req.delta_uniforme is not None else config.delta_uniforme)
    )
    com_pesos = [s.model_copy(update={"peso": req.pesos[s.id]}) if s.id in req.pesos else s for s in shows]
    return Instancia(festival=festival, dia=req.dia, modo=modo, custo=custo, shows=com_pesos)


def restringir(instancia: Instancia, ids: Sequence[str]) -> Instancia:
    """Mesma instância limitada aos shows de `ids`. Ids fora do dia levantam ErroRequisicao. O(n)."""
    desconhecidos = sorted(set(ids) - {s.id for s in instancia.shows})
    if desconhecidos:
        raise ErroRequisicao(f"Shows que não existem no dia {instancia.dia}: {', '.join(desconhecidos)}.")
    escolhidos = set(ids)
    return Instancia(
        festival=instancia.festival,
        dia=instancia.dia,
        modo=instancia.modo,
        custo=instancia.custo,
        shows=[s for s in instancia.shows if s.id in escolhidos],
    )


def cronometrar(funcao: Callable[[], T]) -> tuple[T, float]:
    """Executa `funcao` e devolve o resultado e o tempo em milissegundos. O(custo da função)."""
    inicio = time.perf_counter()
    resultado = funcao()
    return resultado, (time.perf_counter() - inicio) * 1000


def deslocamentos(roteiro: Sequence[Show], custo: CustoDeslocamento) -> list[Deslocamento]:
    """Caminhada entre cada par de shows consecutivos, com custo e folga até o próximo início. O(n)."""
    return [
        Deslocamento(
            de=a.id,
            para=b.id,
            palco_origem=a.palco,
            palco_destino=b.palco,
            custo_min=custo(a.palco, b.palco),
            folga_min=b.inicio - a.fim - custo(a.palco, b.palco),
        )
        for a, b in zip(roteiro, roteiro[1:])
    ]


def montar_roteiro(
    estrategia: Estrategia, roteiro: Sequence[Show], custo: CustoDeslocamento, tempo_ms: float
) -> RoteiroResponse:
    """Resposta de roteiro. As rotas só usam algoritmos exatos, então a otimalidade é garantida. O(n)."""
    return RoteiroResponse(
        estrategia=estrategia,
        otimo_garantido=True,
        roteiro=[s.id for s in roteiro],
        total_shows=len(roteiro),
        peso_total=peso_total(roteiro),
        deslocamentos=deslocamentos(roteiro, custo),
        tempo_execucao_ms=round(tempo_ms, 3),
    )


def maximo_shows(instancia: Instancia) -> RoteiroResponse:
    """Roteiro com mais shows: guloso no modo uniforme, DAG no matricial. O(n log n) ou O(n²)."""
    if instancia.modo == "uniforme":
        roteiro, tempo = cronometrar(lambda: interval_scheduling(instancia.shows, instancia.custo))
        return montar_roteiro("interval_scheduling_guloso", roteiro, instancia.custo, tempo)
    roteiro, tempo = cronometrar(lambda: dag_longest_path(instancia.shows, instancia.custo, ponderado=False))
    return montar_roteiro("dag_longest_path", roteiro, instancia.custo, tempo)


def maxima_satisfacao(instancia: Instancia) -> RoteiroResponse:
    """Roteiro de maior peso: DP no modo uniforme, DAG no matricial. O(n log n) ou O(n²)."""
    if instancia.modo == "uniforme":
        roteiro, tempo = cronometrar(lambda: weighted_interval_scheduling(instancia.shows, instancia.custo))
        return montar_roteiro("weighted_interval_scheduling_dp", roteiro, instancia.custo, tempo)
    roteiro, tempo = cronometrar(lambda: dag_longest_path(instancia.shows, instancia.custo))
    return montar_roteiro("dag_longest_path", roteiro, instancia.custo, tempo)
