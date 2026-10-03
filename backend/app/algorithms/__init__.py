"""Algoritmos do RotaFest. Todo algoritmo de roteiro tem a assinatura f(shows, custo) -> list[Show]."""

from app.algorithms.brute_force import InstanciaGrandeDemais, ResultadoForcaBruta, forca_bruta
from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.heuristics import fifo, maior_peso, spt
from app.algorithms.interval_partitioning import interval_partitioning, profundidade_maxima
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import (
    CustoDeslocamento,
    CustoMatricial,
    CustoUniforme,
    compativel,
    roteiro_valido,
)
from app.algorithms.weighted_scheduling import weighted_interval_scheduling

__all__ = [
    "CustoDeslocamento",
    "CustoMatricial",
    "CustoUniforme",
    "InstanciaGrandeDemais",
    "ResultadoForcaBruta",
    "compativel",
    "dag_longest_path",
    "fifo",
    "forca_bruta",
    "interval_partitioning",
    "interval_scheduling",
    "maior_peso",
    "profundidade_maxima",
    "roteiro_valido",
    "spt",
    "weighted_interval_scheduling",
]
