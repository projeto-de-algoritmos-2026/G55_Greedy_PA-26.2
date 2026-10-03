"""Força bruta usada como referência de corretude."""

import pytest

from app.algorithms.brute_force import LIMITE_SHOWS, InstanciaGrandeDemais, forca_bruta
from app.algorithms.travel_cost import CustoUniforme, peso_total
from scripts.gerar_instancias import gerar_instancia
from tests.fabrica import REFERENCIA, ids, show


def test_mais_de_vinte_shows_e_recusado():
    shows, _ = gerar_instancia(n=LIMITE_SHOWS + 1, seed=0)
    with pytest.raises(InstanciaGrandeDemais):
        forca_bruta(shows, CustoUniforme(0))


def test_vinte_shows_e_aceito():
    shows, _ = gerar_instancia(n=LIMITE_SHOWS, densidade=2.0, seed=0)
    assert forca_bruta(shows, CustoUniforme(0)).max_cardinalidade


def test_instancia_de_referencia():
    resultado = forca_bruta(REFERENCIA, CustoUniforme(12))
    assert ids(resultado.max_cardinalidade) == ["S001", "S003", "S005"]


def test_maior_cardinalidade_e_maior_peso_podem_diferir():
    shows = [show("S001", "18:00", "19:00"), show("S002", "19:00", "20:00"), show("S003", "18:30", "19:30", peso=10)]
    resultado = forca_bruta(shows, CustoUniforme(0))
    assert ids(resultado.max_cardinalidade) == ["S001", "S002"]
    assert (ids(resultado.max_peso), peso_total(resultado.max_peso)) == (["S003"], 10)


def test_grade_vazia():
    resultado = forca_bruta([], CustoUniforme(0))
    assert resultado.max_cardinalidade == [] and resultado.max_peso == []


def test_resultado_e_deterministico():
    shows, _ = gerar_instancia(n=12, seed=7)
    assert forca_bruta(shows, CustoUniforme(5)) == forca_bruta(list(reversed(shows)), CustoUniforme(5))
