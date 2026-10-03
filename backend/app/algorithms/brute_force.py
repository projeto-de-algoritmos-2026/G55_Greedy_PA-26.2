"""Força bruta para validação: enumera todos os roteiros válidos de instâncias pequenas.

Não reaproveita nenhuma lógica dos algoritmos sob teste. A busca decide, show a show em ordem
de início, incluir ou não incluir; um ramo é descartado assim que o show incluído não é
compatível com o anterior. Assim, enumera exatamente todos os roteiros válidos.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.algorithms.travel_cost import (
    CustoDeslocamento,
    compativel,
    ordenar_cronologicamente,
    peso_total,
)
from app.models.show import Show

LIMITE_SHOWS = 20


class InstanciaGrandeDemais(ValueError):
    """A força bruta recusa instâncias com mais de LIMITE_SHOWS shows."""


@dataclass(frozen=True)
class ResultadoForcaBruta:
    """Melhor roteiro por cardinalidade e melhor roteiro por peso, em ordem cronológica."""

    max_cardinalidade: list[Show]
    max_peso: list[Show]


def forca_bruta(shows: Sequence[Show], custo: CustoDeslocamento) -> ResultadoForcaBruta:
    """Encontra o roteiro de mais shows e o de maior peso por busca exaustiva.

    Em empate, fica o primeiro roteiro encontrado. Levanta InstanciaGrandeDemais se n > 20.

    Complexidade: O(2ⁿ) no pior caso.
    """
    if len(shows) > LIMITE_SHOWS:
        raise InstanciaGrandeDemais(
            f"A força bruta aceita no máximo {LIMITE_SHOWS} shows; a instância tem {len(shows)}."
        )

    ordenados = ordenar_cronologicamente(shows)
    melhor_qtd: list[Show] = []
    melhor_peso: list[Show] = []
    melhor_peso_valor = 0
    atual: list[Show] = []

    def explorar(i: int) -> None:
        nonlocal melhor_qtd, melhor_peso, melhor_peso_valor
        if i == len(ordenados):
            if len(atual) > len(melhor_qtd):
                melhor_qtd = list(atual)
            valor = peso_total(atual)
            if valor > melhor_peso_valor:
                melhor_peso, melhor_peso_valor = list(atual), valor
            return
        show = ordenados[i]
        if not atual or compativel(atual[-1], show, custo):
            atual.append(show)
            explorar(i + 1)
            atual.pop()
        explorar(i + 1)

    explorar(0)
    return ResultadoForcaBruta(max_cardinalidade=melhor_qtd, max_peso=melhor_peso)
