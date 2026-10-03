"""Custo de deslocamento, compatibilidade e validade de roteiro."""

import pytest

from app.algorithms.travel_cost import (
    CustoUniforme,
    compativel,
    compativel_matricial,
    compativel_uniforme,
    ordenar_cronologicamente,
    peso_total,
    roteiro_valido,
)
from app.models.palco import MatrizDeslocamento
from tests.fabrica import custo_matricial, ids, show

MATRIZ = {"P1": {"P1": 0, "P2": 9}, "P2": {"P1": 9, "P2": 0}}


def test_fronteira_exata_fim_mais_delta_igual_inicio_e_compativel():
    a, b = show("S001", "14:00", "15:00"), show("S002", "15:12", "16:00", "P2")
    assert compativel_uniforme(a, b, 12)
    assert not compativel_uniforme(a, b, 13)


def test_fronteira_exata_no_modo_matricial():
    a, b = show("S001", "14:00", "15:00", "P1"), show("S002", "15:09", "16:00", "P2")
    matriz = MatrizDeslocamento.model_validate(MATRIZ)
    assert compativel_matricial(a, b, matriz)
    assert not compativel_matricial(a, show("S003", "15:08", "16:00", "P2"), matriz)


def test_modo_uniforme_aplica_delta_tambem_no_mesmo_palco():
    a, b = show("S001", "14:00", "15:00", "P1"), show("S002", "15:05", "16:00", "P1")
    assert not compativel(a, b, CustoUniforme(12))
    assert compativel(a, b, custo_matricial(MATRIZ))


def test_delta_negativo_e_rejeitado():
    with pytest.raises(ValueError):
        CustoUniforme(-1)


def test_roteiro_valido_exige_apenas_pares_consecutivos():
    # P1 -> P3 custa 30 (viola a triangular), mas P1 -> P2 -> P3 custa 2 + 3.
    custo = custo_matricial({
        "P1": {"P1": 0, "P2": 2, "P3": 30},
        "P2": {"P1": 2, "P2": 0, "P3": 3},
        "P3": {"P1": 30, "P2": 3, "P3": 0},
    })
    a = show("S001", "14:00", "15:00", "P1")
    b = show("S002", "15:02", "15:10", "P2")
    c = show("S003", "15:13", "16:00", "P3")
    assert not compativel(a, c, custo)
    assert roteiro_valido([c, a, b], custo)
    assert not roteiro_valido([a, c], custo)


def test_roteiro_vazio_e_unitario_sao_validos():
    assert roteiro_valido([], CustoUniforme(12))
    assert roteiro_valido([show("S001", "14:00", "15:00")], CustoUniforme(12))


def test_ordenacao_cronologica_desempata_por_id_e_soma_pesos():
    shows = [show("S002", "14:00", "15:00", peso=3), show("S001", "14:00", "14:30", peso=4)]
    assert ids(ordenar_cronologicamente(shows)) == ["S001", "S002"]
    assert peso_total(shows) == 7
