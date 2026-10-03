"""Caminho máximo em DAG: solução exata para o deslocamento matricial."""

import pytest

from app.algorithms.brute_force import forca_bruta
from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoMatricial, CustoUniforme, peso_total, roteiro_valido
from scripts.gerar_instancias import gerar_instancia
from tests.fabrica import REFERENCIA, custo_matricial, ids, show

# No modo matricial o guloso por menor término perde: A termina primeiro, mas fica a 40 min
# do palco P2; B termina depois e permite emendar C no mesmo palco.
CUSTO_LONGE = custo_matricial({"P1": {"P1": 0, "P2": 40}, "P2": {"P1": 40, "P2": 0}})
A = show("S001", "10:00", "11:00", "P1")
B = show("S002", "10:00", "11:10", "P2")
C = show("S003", "11:30", "12:30", "P2")


def test_contraexemplo_do_modo_matricial():
    assert ids(interval_scheduling([A, B, C], CUSTO_LONGE)) == ["S001"]
    assert ids(dag_longest_path([A, B, C], CUSTO_LONGE, ponderado=False)) == ["S002", "S003"]


def test_ponderado_escolhe_maior_peso():
    pesado = show("S004", "10:30", "11:20", "P1", peso=10)
    assert ids(dag_longest_path([A, B, C, pesado], CUSTO_LONGE)) == ["S004"]


def test_grade_vazia_e_show_unico():
    assert dag_longest_path([], CUSTO_LONGE) == []
    assert dag_longest_path([A], CUSTO_LONGE) == [A]


def test_modo_uniforme_sem_peso_iguala_o_guloso_na_referencia():
    delta = CustoUniforme(12)
    assert len(dag_longest_path(REFERENCIA, delta, ponderado=False)) == len(interval_scheduling(REFERENCIA, delta))


@pytest.mark.parametrize("seed", range(100))
def test_dag_supera_ou_iguala_o_guloso_no_modo_matricial(seed):
    shows, matriz = gerar_instancia(n=30, densidade=1.5, palcos=4, seed=seed)
    custo = CustoMatricial(matriz)
    guloso = interval_scheduling(shows, custo)
    dag = dag_longest_path(shows, custo, ponderado=False)
    assert roteiro_valido(dag, custo)
    assert len(dag) >= len(guloso)
    assert peso_total(dag_longest_path(shows, custo)) >= peso_total(guloso)


@pytest.mark.parametrize("seed", range(20))
def test_dag_coincide_com_forca_bruta_em_instancias_pequenas(seed):
    shows, matriz = gerar_instancia(n=12, densidade=1.5, palcos=3, seed=seed)
    custo = CustoMatricial(matriz)
    exato = forca_bruta(shows, custo)
    assert len(dag_longest_path(shows, custo, ponderado=False)) == len(exato.max_cardinalidade)
    assert peso_total(dag_longest_path(shows, custo)) == peso_total(exato.max_peso)
