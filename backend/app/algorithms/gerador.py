"""Gerador de instâncias sintéticas para testes e medição de desempenho.

A mesma seed sempre produz a mesma instância (T-301).
Reutilizado pelo benchmark (T-704) e pelos testes de equivalência (T-302, T-303, T-305).
"""

import random

from app.models.palco import MatrizDeslocamento
from app.models.show import Show

INICIO_GRADE = 14 * 60
DURACAO_MIN, DURACAO_MAX = 20, 90
DESLOCAMENTO_MAX = 20


def gerar_instancia(
    n: int,
    densidade: float = 1.0,
    palcos: int = 4,
    seed: int = 0,
    deslocamento_max: int = DESLOCAMENTO_MAX,
) -> tuple[list[Show], MatrizDeslocamento]:
    """Gera `n` shows aleatórios e uma matriz simétrica de deslocamento entre `palcos` palcos.

    `densidade` controla a sobreposição: os inícios são sorteados numa janela de
    `n * 30 / densidade` minutos, então densidades maiores produzem mais conflitos.
    A matriz pode violar a desigualdade triangular, de propósito.

    Complexidade: O(n + palcos²).
    """
    if n < 0 or palcos < 1 or densidade <= 0:
        raise ValueError("n deve ser >= 0, palcos >= 1 e densidade > 0.")

    rng = random.Random(seed)
    codigos = [f"P{i}" for i in range(1, palcos + 1)]
    janela = max(1, round(n * 30 / densidade))

    shows = []
    for i in range(1, n + 1):
        inicio = INICIO_GRADE + rng.randrange(janela)
        shows.append(Show(
            id=f"S{i:03d}",
            artista=f"Artista {i}",
            palco=rng.choice(codigos),
            inicio=inicio,
            fim=inicio + rng.randint(DURACAO_MIN, DURACAO_MAX),
            peso=rng.randint(1, 10),
        ))

    custos: dict[str, dict[str, int]] = {c: {c: 0} for c in codigos}
    for a_idx, a in enumerate(codigos):
        for b in codigos[a_idx + 1:]:
            custos[a][b] = custos[b][a] = rng.randint(1, deslocamento_max)
    return shows, MatrizDeslocamento.model_validate(custos)
