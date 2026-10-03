"""Weighted Interval Scheduling por programação dinâmica."""

import pytest

from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoUniforme, peso_total, roteiro_valido
from app.algorithms.weighted_scheduling import weighted_interval_scheduling
from tests.fabrica import REFERENCIA, custo_matricial, ids, show

# Contraexemplo do guloso ponderado: o guloso por menor término escolhe A e B (peso 2),
# mas o ótimo é C sozinho (peso 10), um gap de 80%. Se alguém trocar a DP pelo guloso,
# este teste falha.
A = show("S001", "18:00", "19:00", peso=1)
B = show("S002", "19:00", "20:00", peso=1)
C = show("S003", "18:30", "19:30", peso=10)
CONTRAEXEMPLO = [A, B, C]


def test_contraexemplo_guloso_perde_e_dp_acerta():
    sem_delta = CustoUniforme(0)
    guloso = interval_scheduling(CONTRAEXEMPLO, sem_delta)
    dp = weighted_interval_scheduling(CONTRAEXEMPLO, sem_delta)
    assert (ids(guloso), peso_total(guloso)) == (["S001", "S002"], 2)
    assert (ids(dp), peso_total(dp)) == (["S003"], 10)


def test_peso_maximo_em_show_que_se_sobrepoe_a_todos():
    shows = [show(f"S00{i}", f"1{4 + i}:00", f"1{4 + i}:50", f"P{i}") for i in range(1, 5)]
    gigante = show("S009", "14:00", "20:00", "P1", peso=10)
    assert ids(weighted_interval_scheduling([*shows, gigante], CustoUniforme(12))) == ["S009"]


def test_pesos_unitarios_empatam_com_o_guloso_em_cardinalidade():
    delta = CustoUniforme(12)
    assert len(weighted_interval_scheduling(REFERENCIA, delta)) == len(interval_scheduling(REFERENCIA, delta))


def test_empate_prefere_nao_incluir_o_show_de_termino_posterior():
    shows = [show("S001", "14:00", "15:00", peso=5), show("S002", "14:30", "15:30", peso=5)]
    assert ids(weighted_interval_scheduling(shows, CustoUniforme(0))) == ["S001"]


def test_delta_e_considerado_na_busca_de_p():
    shows = [show("S001", "14:00", "15:00", peso=5), show("S002", "15:10", "16:00", peso=5)]
    assert len(weighted_interval_scheduling(shows, CustoUniforme(10))) == 2
    assert len(weighted_interval_scheduling(shows, CustoUniforme(11))) == 1


def test_grade_vazia_e_roteiro_valido():
    assert weighted_interval_scheduling([], CustoUniforme(12)) == []
    assert roteiro_valido(weighted_interval_scheduling(REFERENCIA, CustoUniforme(12)), CustoUniforme(12))


def test_custo_matricial_e_recusado():
    custo = custo_matricial({"P1": {"P1": 0}})
    with pytest.raises(TypeError):
        weighted_interval_scheduling([A], custo)
