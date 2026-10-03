"""Interval Partitioning: número mínimo de palcos para acomodar a grade inteira.

A profundidade máxima é calculada por uma varredura de eventos independente do heap,
para servir de verificação cruzada: os dois valores precisam ser sempre iguais.
"""

import heapq
from collections.abc import Sequence

from app.algorithms.travel_cost import ordenar_cronologicamente
from app.models.show import Show


def interval_partitioning(shows: Sequence[Show]) -> list[list[Show]]:
    """Aloca os shows no menor número de recursos (palcos) sem sobreposição.

    Processa os shows por início e reaproveita o recurso que libera mais cedo se ele já estiver
    livre (liberação <= início); senão abre um novo. Empates de liberação ficam com o recurso
    de menor índice. O número de recursos é igual à profundidade máxima, que é o limite inferior.

    Complexidade: O(n log n).
    """
    recursos: list[list[Show]] = []
    livres: list[tuple[int, int]] = []  # (horário de liberação, índice do recurso)
    for show in ordenar_cronologicamente(shows):
        if livres and livres[0][0] <= show.inicio:
            _, indice = heapq.heappop(livres)
        else:
            indice = len(recursos)
            recursos.append([])
        recursos[indice].append(show)
        heapq.heappush(livres, (show.fim, indice))
    return recursos


def profundidade_maxima(shows: Sequence[Show]) -> tuple[int, list[tuple[int, int]]]:
    """Maior número de shows simultâneos, por varredura de eventos.

    Retorna `(profundidade, serie)`, em que `serie` lista `(minuto, simultaneos)` a cada instante
    em que a contagem muda. No mesmo minuto, términos são processados antes de inícios, porque
    um show que termina às 15:00 não se sobrepõe a outro que começa às 15:00.

    Complexidade: O(n log n).
    """
    eventos = sorted([(s.fim, -1) for s in shows] + [(s.inicio, 1) for s in shows])
    serie: list[tuple[int, int]] = []
    atual = maximo = 0
    for minuto, variacao in eventos:
        atual += variacao
        maximo = max(maximo, atual)
        if serie and serie[-1][0] == minuto:
            serie[-1] = (minuto, atual)
        else:
            serie.append((minuto, atual))
    return maximo, serie
