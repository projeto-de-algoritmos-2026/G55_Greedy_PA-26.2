"""Heurísticas de comparação e interface comum dos algoritmos de roteiro."""

import inspect

import pytest

from app.algorithms.dag_longest_path import dag_longest_path
from app.algorithms.heuristics import fifo, maior_peso, spt
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoMatricial, CustoUniforme, roteiro_valido
from app.algorithms.weighted_scheduling import weighted_interval_scheduling
from scripts.gerar_instancias import gerar_instancia
from tests.fabrica import ids, show

ALGORITMOS = [interval_scheduling, weighted_interval_scheduling, dag_longest_path, fifo, spt, maior_peso]
HEURISTICAS = [fifo, spt, maior_peso]


@pytest.mark.parametrize("algoritmo", ALGORITMOS)
def test_assinatura_comum_permite_troca_direta(algoritmo):
    parametros = list(inspect.signature(algoritmo).parameters)
    assert parametros[:2] == ["shows", "custo"]
    shows, _ = gerar_instancia(n=15, seed=1)
    assert roteiro_valido(algoritmo(shows, CustoUniforme(12)), CustoUniforme(12))


def test_fifo_escolhe_pelo_menor_inicio():
    longo = show("S001", "14:00", "18:00")
    curtos = [show("S002", "14:30", "15:00"), show("S003", "15:30", "16:00")]
    assert ids(fifo([longo, *curtos], CustoUniforme(0))) == ["S001"]


def test_spt_escolhe_pela_menor_duracao():
    longo = show("S001", "14:00", "18:00")
    curtos = [show("S002", "14:30", "15:00"), show("S003", "15:30", "16:00")]
    assert ids(spt([longo, *curtos], CustoUniforme(0))) == ["S002", "S003"]


def test_maior_peso_ignora_conflitos_futuros():
    shows = [show("S001", "14:00", "18:00", peso=9),
             show("S002", "14:30", "15:00", peso=8), show("S003", "15:30", "16:00", peso=8)]
    assert ids(maior_peso(shows, CustoUniforme(0))) == ["S001"]


def test_insercao_no_meio_respeita_os_dois_vizinhos():
    # SPT escolhe primeiro os curtos das pontas; o do meio precisa caber entre eles.
    shows = [show("S001", "14:00", "14:20"), show("S002", "16:00", "16:20"),
             show("S003", "14:30", "15:50"), show("S004", "14:25", "15:59")]
    assert ids(spt(shows, CustoUniforme(10))) == ["S001", "S003", "S002"]


@pytest.mark.parametrize("heuristica", HEURISTICAS)
@pytest.mark.parametrize("seed", range(30))
def test_heuristicas_sempre_produzem_roteiro_valido(heuristica, seed):
    shows, matriz = gerar_instancia(n=25, densidade=1.5, seed=seed)
    for custo in (CustoUniforme(12), CustoMatricial(matriz)):
        assert roteiro_valido(heuristica(shows, custo), custo)
