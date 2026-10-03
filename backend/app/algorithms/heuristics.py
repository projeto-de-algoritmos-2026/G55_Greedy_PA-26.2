"""Heurísticas ingênuas de comparação, sem garantia de otimalidade.

Todas têm a mesma assinatura dos algoritmos exatos, `f(shows, custo)`, e diferem apenas no
critério de ordenação. Como um show processado depois pode começar antes de outro já escolhido,
cada candidato é inserido na posição cronológica e precisa ser compatível com o vizinho
anterior e com o seguinte.
"""

from bisect import bisect_left
from collections.abc import Callable, Sequence

from app.algorithms.travel_cost import CustoDeslocamento, chave_cronologica, compativel
from app.models.show import Show


def _selecionar_em_ordem(
    shows: Sequence[Show], custo: CustoDeslocamento, criterio: Callable[[Show], tuple[int, str]]
) -> list[Show]:
    """Percorre os shows pelo critério e aceita cada um que caiba no roteiro.

    Complexidade: O(n log n) comparações; a inserção em lista custa O(n) no pior caso.
    """
    roteiro: list[Show] = []
    chaves: list[tuple[int, str]] = []
    for show in sorted(shows, key=criterio):
        chave = chave_cronologica(show)
        pos = bisect_left(chaves, chave)
        anterior = roteiro[pos - 1] if pos > 0 else None
        seguinte = roteiro[pos] if pos < len(roteiro) else None
        if (anterior is None or compativel(anterior, show, custo)) and (
            seguinte is None or compativel(show, seguinte, custo)
        ):
            roteiro.insert(pos, show)
            chaves.insert(pos, chave)
    return roteiro


def fifo(shows: Sequence[Show], custo: CustoDeslocamento) -> list[Show]:
    """Escolhe pelo menor horário de início, a intuição natural do frequentador. O(n log n)."""
    return _selecionar_em_ordem(shows, custo, lambda s: (s.inicio, s.id))


def spt(shows: Sequence[Show], custo: CustoDeslocamento) -> list[Show]:
    """Escolhe pela menor duração (Shortest Processing Time). O(n log n) comparações."""
    return _selecionar_em_ordem(shows, custo, lambda s: (s.duracao, s.id))


def maior_peso(shows: Sequence[Show], custo: CustoDeslocamento) -> list[Show]:
    """Escolhe pela maior nota de preferência, ignorando conflitos futuros. O(n log n) comparações."""
    return _selecionar_em_ordem(shows, custo, lambda s: (-s.peso, s.id))
