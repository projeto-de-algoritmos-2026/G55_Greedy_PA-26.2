"""Interval Scheduling guloso: maior número de shows assistidos por completo."""

from collections.abc import Sequence

from app.algorithms.travel_cost import CustoDeslocamento, compativel
from app.models.show import Show


def interval_scheduling(shows: Sequence[Show], custo: CustoDeslocamento) -> list[Show]:
    """Seleciona shows pelo menor horário de término, aceitando cada um que caiba após o último.

    Com custo uniforme, ordenar por `fim` equivale a ordenar por `fim + delta`, e o resultado
    tem cardinalidade máxima (argumento de troca). Com custo matricial a mesma estratégia roda,
    mas sem garantia de otimalidade. Empates de término são resolvidos pelo id.

    Complexidade: O(n log n), dominada pela ordenação.
    """
    roteiro: list[Show] = []
    for show in sorted(shows, key=lambda s: (s.fim, s.id)):
        if not roteiro or compativel(roteiro[-1], show, custo):
            roteiro.append(show)
    return roteiro
