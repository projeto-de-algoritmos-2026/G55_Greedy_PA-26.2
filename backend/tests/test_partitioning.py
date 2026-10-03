"""Interval Partitioning e varredura de eventos independente."""

import pytest

from app.algorithms.interval_partitioning import interval_partitioning, profundidade_maxima
from app.algorithms.travel_cost import CustoUniforme, roteiro_valido
from scripts.gerar_instancias import gerar_instancia
from tests.fabrica import show


def test_profundidade_tres_conhecida():
    shows = [
        show("S001", "14:00", "16:00"), show("S002", "14:30", "15:30"), show("S003", "15:00", "17:00"),
        show("S004", "16:00", "18:00"), show("S005", "17:00", "18:00"),
    ]
    assert len(interval_partitioning(shows)) == 3
    assert profundidade_maxima(shows)[0] == 3


def test_todos_no_mesmo_horario_exige_n_recursos():
    shows = [show(f"S00{i}", "20:00", "21:00") for i in range(1, 6)]
    assert len(interval_partitioning(shows)) == 5


def test_nenhuma_sobreposicao_exige_um_recurso():
    shows = [show("S001", "14:00", "15:00"), show("S002", "15:00", "16:00"), show("S003", "16:30", "17:00")]
    assert len(interval_partitioning(shows)) == 1
    assert profundidade_maxima(shows)[0] == 1


def test_grade_vazia():
    assert interval_partitioning([]) == []
    assert profundidade_maxima([]) == (0, [])


def test_serie_de_sobreposicao_trata_termino_antes_de_inicio():
    shows = [show("S001", "14:00", "15:00"), show("S002", "15:00", "16:00"), show("S003", "14:30", "15:30")]
    _, serie = profundidade_maxima(shows)
    assert serie == [(840, 1), (870, 2), (900, 2), (930, 1), (960, 0)]


@pytest.mark.parametrize("seed", range(100))
def test_heap_e_varredura_concordam_em_instancias_aleatorias(seed):
    shows, _ = gerar_instancia(n=40, densidade=2.0, palcos=4, seed=seed)
    recursos = interval_partitioning(shows)
    assert len(recursos) == profundidade_maxima(shows)[0]
    assert sorted(s.id for r in recursos for s in r) == sorted(s.id for s in shows)
    assert all(roteiro_valido(r, CustoUniforme(0)) for r in recursos)
