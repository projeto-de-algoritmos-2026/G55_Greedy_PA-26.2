"""Caminho de peso máximo em DAG: solução exata para qualquer custo de deslocamento.

Cada show é um vértice, com aresta i -> j quando dá tempo de assistir i e chegar a j.
Toda aresta aponta para um show que começa depois, então o grafo é acíclico e a ordem
de início já é uma ordem topológica.
"""

from collections.abc import Sequence

from app.algorithms.travel_cost import CustoDeslocamento, compativel, ordenar_cronologicamente
from app.models.show import Show


def dag_longest_path(
    shows: Sequence[Show], custo: CustoDeslocamento, ponderado: bool = True
) -> list[Show]:
    """Roteiro de peso máximo, ou de mais shows com `ponderado=False`.

    Relaxa os vértices em ordem de início: melhor[j] é o maior peso de um roteiro que termina
    em j. Entre predecessores de mesmo valor, e no argmax final, vence o de menor índice.

    Complexidade: O(n²).
    """
    ordenados = ordenar_cronologicamente(shows)
    if not ordenados:
        return []

    pesos = [s.peso if ponderado else 1 for s in ordenados]
    melhor = list(pesos)
    pred: list[int | None] = [None] * len(ordenados)
    for j, show in enumerate(ordenados):
        for i in range(j):
            if compativel(ordenados[i], show, custo) and melhor[i] + pesos[j] > melhor[j]:
                melhor[j] = melhor[i] + pesos[j]
                pred[j] = i

    atual: int | None = max(range(len(ordenados)), key=lambda j: (melhor[j], -j))
    roteiro: list[Show] = []
    while atual is not None:
        roteiro.append(ordenados[atual])
        atual = pred[atual]
    return roteiro[::-1]
