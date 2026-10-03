"""Weighted Interval Scheduling por programação dinâmica: roteiro de maior satisfação."""

from bisect import bisect_right
from collections.abc import Sequence

from app.algorithms.travel_cost import CustoDeslocamento, CustoUniforme, ordenar_cronologicamente
from app.models.show import Show


def weighted_interval_scheduling(shows: Sequence[Show], custo: CustoDeslocamento) -> list[Show]:
    """Subconjunto compatível de peso máximo no modo uniforme.

    Ordena por `fim + delta` e, para cada show j, encontra por busca binária p(j), o último
    show que termina (já somado o delta) até o início de j. A recorrência é
    OPT(j) = max(peso[j] + OPT(p(j)), OPT(j - 1)). Em empate na reconstrução, j não é incluído.

    Só aceita custo uniforme: a busca binária depende de todos os términos serem deslocados
    pelo mesmo delta. Para custo matricial, use o caminho máximo em DAG.

    Complexidade: O(n log n).
    """
    if not isinstance(custo, CustoUniforme):
        raise TypeError("A DP ponderada exige custo uniforme; use dag_longest_path no modo matricial.")

    ordenados = sorted(shows, key=lambda s: (s.fim, s.id))
    n = len(ordenados)
    fim_efetivo = [s.fim + custo.delta for s in ordenados]

    # p[j] (1-indexado): quantidade de shows anteriores a j cujo fim efetivo cabe antes de j.
    p = [0] * (n + 1)
    for j in range(1, n + 1):
        p[j] = bisect_right(fim_efetivo, ordenados[j - 1].inicio, 0, j - 1)

    opt = [0] * (n + 1)
    for j in range(1, n + 1):
        opt[j] = max(ordenados[j - 1].peso + opt[p[j]], opt[j - 1])

    escolhidos: list[Show] = []
    j = n
    while j > 0:
        if ordenados[j - 1].peso + opt[p[j]] > opt[j - 1]:
            escolhidos.append(ordenados[j - 1])
            j = p[j]
        else:
            j -= 1
    return ordenar_cronologicamente(escolhidos)
