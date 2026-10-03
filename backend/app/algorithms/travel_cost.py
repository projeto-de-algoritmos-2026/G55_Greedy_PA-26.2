"""Custo de deslocamento entre palcos e relação de compatibilidade entre shows.

Dois modos:

- Uniforme: um tempo constante `delta` entre quaisquer dois shows consecutivos, inclusive no
  mesmo palco. Equivale a trocar cada intervalo [inicio, fim] por [inicio, fim + delta], o que
  preserva a ordem dos términos e mantém as garantias do guloso.
- Matricial: o custo depende do par de palcos. A compatibilidade deixa de ser induzida por
  intervalos na reta e o guloso perde a garantia de otimalidade.

Um roteiro é válido quando, em ordem cronológica, cada par de shows consecutivos é compatível.
Shows não consecutivos não precisam ser compatíveis entre si, porque só se caminha de um show
para o seguinte.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from app.models.palco import MatrizDeslocamento
from app.models.show import Show


@dataclass(frozen=True)
class CustoUniforme:
    """Deslocamento constante de `delta` minutos entre quaisquer dois shows consecutivos."""

    delta: int

    def __post_init__(self) -> None:
        if self.delta < 0:
            raise ValueError(f"delta não pode ser negativo ({self.delta}).")

    def __call__(self, origem: str, destino: str) -> int:
        """Custo de `origem` até `destino`. O(1)."""
        return self.delta


@dataclass(frozen=True)
class CustoMatricial:
    """Deslocamento lido da matriz de tempos de caminhada entre palcos."""

    matriz: MatrizDeslocamento

    def __call__(self, origem: str, destino: str) -> int:
        """Custo de `origem` até `destino`. O(1)."""
        return self.matriz.custo(origem, destino)


CustoDeslocamento = CustoUniforme | CustoMatricial


def compativel(a: Show, b: Show, custo: CustoDeslocamento) -> bool:
    """True se dá para assistir `a` inteiro e chegar a tempo para o início de `b`. O(1).

    A desigualdade é não estrita: terminar e caminhar exatamente até o início de `b` é compatível.
    """
    return a.fim + custo(a.palco, b.palco) <= b.inicio


def compativel_uniforme(a: Show, b: Show, delta: int) -> bool:
    """Compatibilidade no modo uniforme: fim[a] + delta <= inicio[b]. O(1)."""
    return compativel(a, b, CustoUniforme(delta))


def compativel_matricial(a: Show, b: Show, matriz: MatrizDeslocamento) -> bool:
    """Compatibilidade no modo matricial: fim[a] + D[palco a][palco b] <= inicio[b]. O(1)."""
    return compativel(a, b, CustoMatricial(matriz))


def chave_cronologica(show: Show) -> tuple[int, str]:
    """Chave de ordenação por início, com o id desempatando. O(1)."""
    return (show.inicio, show.id)


def ordenar_cronologicamente(shows: Iterable[Show]) -> list[Show]:
    """Shows ordenados por (inicio, id). O(n log n)."""
    return sorted(shows, key=chave_cronologica)


def roteiro_valido(roteiro: Sequence[Show], custo: CustoDeslocamento) -> bool:
    """True se, em ordem cronológica, cada par de shows consecutivos é compatível. O(n log n)."""
    ordenado = ordenar_cronologicamente(roteiro)
    return all(compativel(a, b, custo) for a, b in zip(ordenado, ordenado[1:]))


def peso_total(roteiro: Iterable[Show]) -> int:
    """Soma dos pesos de preferência do roteiro. O(n)."""
    return sum(s.peso for s in roteiro)
