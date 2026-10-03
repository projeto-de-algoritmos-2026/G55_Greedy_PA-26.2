"""Equivalência dos algoritmos exatos contra a força bruta em instâncias aleatórias.

Cada propriedade roda sobre 500 instâncias com até 12 shows, variando número de shows,
densidade de sobreposição, número de palcos e tempo de deslocamento. Além do valor ótimo,
cada roteiro devolvido precisa ser válido. Em caso de falha, a mensagem lista as seeds.
"""

import random
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from app.algorithms.brute_force import forca_bruta
from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import (
    CustoDeslocamento,
    CustoMatricial,
    CustoUniforme,
    peso_total,
    roteiro_valido,
)
from app.algorithms.weighted_scheduling import weighted_interval_scheduling
from app.models.show import Show
from scripts.gerar_instancias import gerar_instancia

QUANTIDADE = 500
N_MAXIMO = 12
DENSIDADES = (0.5, 1.0, 2.0, 4.0)
DELTAS = (0, 5, 12, 30)


@dataclass(frozen=True)
class Caso:
    seed: int
    shows: list[Show]
    custo: CustoDeslocamento


def _instancias(matricial: bool, seed_base: int) -> Iterator[Caso]:
    """Instâncias determinísticas que cobrem também grade vazia, palco único e delta zero."""
    for seed in range(seed_base, seed_base + QUANTIDADE):
        rng = random.Random(seed)
        shows, matriz = gerar_instancia(
            n=rng.randint(0, N_MAXIMO),
            densidade=rng.choice(DENSIDADES),
            palcos=rng.randint(1, 4),
            seed=seed,
            deslocamento_max=rng.choice((5, 15, 30)),
        )
        custo = CustoMatricial(matriz) if matricial else CustoUniforme(rng.choice(DELTAS))
        yield Caso(seed, shows, custo)


def _divergencias(casos: Iterator[Caso], verificar: Callable[[Caso], bool]) -> list[int]:
    return [caso.seed for caso in casos if not verificar(caso)]


def test_guloso_tem_a_cardinalidade_da_forca_bruta_no_modo_uniforme():
    def verificar(caso: Caso) -> bool:
        roteiro = interval_scheduling(caso.shows, caso.custo)
        otimo = forca_bruta(caso.shows, caso.custo).max_cardinalidade
        return roteiro_valido(roteiro, caso.custo) and len(roteiro) == len(otimo)

    falhas = _divergencias(_instancias(matricial=False, seed_base=10_000), verificar)
    assert not falhas, f"guloso divergiu da força bruta nas seeds {falhas}"


def test_dp_ponderada_tem_o_peso_da_forca_bruta_no_modo_uniforme():
    def verificar(caso: Caso) -> bool:
        roteiro = weighted_interval_scheduling(caso.shows, caso.custo)
        otimo = forca_bruta(caso.shows, caso.custo).max_peso
        return roteiro_valido(roteiro, caso.custo) and peso_total(roteiro) == peso_total(otimo)

    falhas = _divergencias(_instancias(matricial=False, seed_base=20_000), verificar)
    assert not falhas, f"DP ponderada divergiu da força bruta nas seeds {falhas}"


def test_dag_tem_cardinalidade_e_peso_da_forca_bruta_no_modo_matricial():
    def verificar(caso: Caso) -> bool:
        otimo = forca_bruta(caso.shows, caso.custo)
        por_quantidade = dag_longest_path(caso.shows, caso.custo, ponderado=False)
        por_peso = dag_longest_path(caso.shows, caso.custo)
        return (
            roteiro_valido(por_quantidade, caso.custo)
            and roteiro_valido(por_peso, caso.custo)
            and len(por_quantidade) == len(otimo.max_cardinalidade)
            and peso_total(por_peso) == peso_total(otimo.max_peso)
        )

    falhas = _divergencias(_instancias(matricial=True, seed_base=30_000), verificar)
    assert not falhas, f"DAG divergiu da força bruta nas seeds {falhas}"
