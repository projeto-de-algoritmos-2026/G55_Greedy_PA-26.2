"""Comparativo entre estratégias sobre a mesma instância, e validação contra força bruta."""

from collections.abc import Callable, Sequence
from typing import Literal

from app.algorithms.brute_force import forca_bruta
from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.heuristics import fifo, maior_peso, spt
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoDeslocamento, peso_total
from app.algorithms.weighted_scheduling import weighted_interval_scheduling
from app.models.schemas import (
    ComparativoResponse,
    Estrategia,
    InstanciaResumo,
    ItemValidacao,
    ResultadoEstrategia,
    ValidarResponse,
)
from app.models.show import Show
from app.services.calculo import Instancia, cronometrar

Algoritmo = Callable[[Sequence[Show], CustoDeslocamento], list[Show]]
Metrica = Literal["total_shows", "peso_total"]
HEURISTICAS: dict[Estrategia, Algoritmo] = {"fifo": fifo, "spt": spt, "maior_peso": maior_peso}


def _estrategias(instancia: Instancia) -> list[tuple[Estrategia, Algoritmo, bool]]:
    """Estratégias na ordem do contrato, com o algoritmo e se há garantia de otimalidade.

    O guloso só é ótimo no modo uniforme. A solução exata de peso é a DP no modo uniforme e o
    caminho máximo em DAG no matricial, onde a DP não se aplica.
    """
    uniforme = instancia.modo == "uniforme"
    exata: tuple[Estrategia, Algoritmo, bool] = (
        ("dp_ponderado", weighted_interval_scheduling, True)
        if uniforme
        else ("dag_longest_path", dag_longest_path, True)
    )
    return [
        ("guloso_menor_fim", interval_scheduling, uniforme),
        exata,
        *((nome, algoritmo, False) for nome, algoritmo in HEURISTICAS.items()),
    ]


def comparar(instancia: Instancia) -> ComparativoResponse:
    """Roda as cinco estratégias e calcula a perda de cada heurística contra a exata. O(n²) no pior caso.

    gap = (peso ótimo − peso da heurística) / peso ótimo × 100, com uma casa; 0 se o ótimo for 0.
    """
    resultados: list[ResultadoEstrategia] = []
    for nome, algoritmo, otimo in _estrategias(instancia):
        roteiro, tempo = cronometrar(lambda a=algoritmo: a(instancia.shows, instancia.custo))
        resultados.append(ResultadoEstrategia(
            estrategia=nome,
            otimo_garantido=otimo,
            total_shows=len(roteiro),
            peso_total=peso_total(roteiro),
            tempo_ms=round(tempo, 3),
        ))

    peso_otimo = resultados[1].peso_total
    gap = {
        r.estrategia: round(100 * (peso_otimo - r.peso_total) / peso_otimo, 1) if peso_otimo else 0.0
        for r in resultados
        if r.estrategia in HEURISTICAS
    }
    return ComparativoResponse(
        instancia=InstanciaResumo(
            total_shows=len(instancia.shows), dia=instancia.dia, modo_deslocamento=instancia.modo
        ),
        resultados=resultados,
        gap_percentual=gap,
    )


def validar(instancia: Instancia) -> ValidarResponse:
    """Compara os algoritmos usados pela API com a força bruta. O(2ⁿ), com n ≤ 20.

    Levanta InstanciaGrandeDemais se a instância tiver mais de 20 shows.
    """
    shows, custo = instancia.shows, instancia.custo
    exato = forca_bruta(shows, custo)
    melhor_qtd, melhor_peso = len(exato.max_cardinalidade), peso_total(exato.max_peso)

    if instancia.modo == "uniforme":
        candidatos: list[tuple[Estrategia, Metrica, int, int]] = [
            ("interval_scheduling_guloso", "total_shows", len(interval_scheduling(shows, custo)), melhor_qtd),
            ("weighted_interval_scheduling_dp", "peso_total",
             peso_total(weighted_interval_scheduling(shows, custo)), melhor_peso),
        ]
    else:
        candidatos = [
            ("dag_longest_path", "total_shows", len(dag_longest_path(shows, custo, ponderado=False)), melhor_qtd),
            ("dag_longest_path", "peso_total", peso_total(dag_longest_path(shows, custo)), melhor_peso),
        ]

    itens = [
        ItemValidacao(
            algoritmo=algoritmo,
            metrica=metrica,
            valor_algoritmo=valor,
            valor_forca_bruta=referencia,
            confere=valor == referencia,
        )
        for algoritmo, metrica, valor, referencia in candidatos
    ]
    return ValidarResponse(
        total_shows=len(shows),
        modo_deslocamento=instancia.modo,
        itens=itens,
        todos_conferem=all(i.confere for i in itens),
    )
