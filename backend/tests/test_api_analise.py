"""Rotas de análise: dimensionamento, comparativo e validação contra força bruta."""

import pytest

BASE = {"festival_id": "festival-exemplo", "dia": 1}


@pytest.mark.parametrize("dia", [1, 2])
def test_dimensionamento_atinge_o_limite_inferior(cliente, dia):
    corpo = cliente.post("/api/dimensionamento", json=BASE | {"dia": dia}).json()
    assert corpo["palcos_minimos"] == corpo["profundidade_maxima"] == 4
    assert corpo["limite_inferior_atingido"] is True
    assert corpo["palcos_reais"] == 4
    assert list(corpo["alocacao"]) == ["SALA_1", "SALA_2", "SALA_3", "SALA_4"]
    assert sum(len(ids) for ids in corpo["alocacao"].values()) == 32
    assert max(f["simultaneos"] for f in corpo["sobreposicao_por_faixa"]) == 4


@pytest.mark.parametrize(("modo", "exata", "guloso_otimo"), [
    ("uniforme", "dp_ponderado", True),
    ("matricial", "dag_longest_path", False),
])
def test_comparativo_tem_cinco_estrategias_e_otimalidade_por_modo(cliente, modo, exata, guloso_otimo):
    corpo = cliente.post("/api/comparativo", json=BASE | {"modo_deslocamento": modo}).json()
    resultados = {r["estrategia"]: r for r in corpo["resultados"]}
    assert list(resultados) == ["guloso_menor_fim", exata, "fifo", "spt", "maior_peso"]
    assert resultados["guloso_menor_fim"]["otimo_garantido"] is guloso_otimo
    assert resultados[exata]["otimo_garantido"] is True
    assert not any(resultados[h]["otimo_garantido"] for h in ("fifo", "spt", "maior_peso"))
    assert corpo["instancia"] == {"total_shows": 32, "dia": 1, "modo_deslocamento": modo}


def test_gap_percentual_segue_a_formula(cliente):
    pesos = {"S023": 10, "S013": 7, "S002": 4}
    corpo = cliente.post("/api/comparativo", json=BASE | {"pesos": pesos}).json()
    resultados = {r["estrategia"]: r for r in corpo["resultados"]}
    otimo = resultados["dp_ponderado"]["peso_total"]
    assert set(corpo["gap_percentual"]) == {"fifo", "spt", "maior_peso"}
    for heuristica, gap in corpo["gap_percentual"].items():
        assert gap == round(100 * (otimo - resultados[heuristica]["peso_total"]) / otimo, 1)
        assert resultados[heuristica]["peso_total"] <= otimo


@pytest.mark.parametrize("modo", ["uniforme", "matricial"])
def test_validar_subconjunto_confere_com_forca_bruta(cliente, modo):
    ids = [f"S{i:03d}" for i in range(1, 19)]
    resposta = cliente.post("/api/validar", json=BASE | {"modo_deslocamento": modo, "shows": ids, "pesos": {"S005": 9}})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_shows"] == 18
    assert corpo["todos_conferem"] is True
    assert {i["metrica"] for i in corpo["itens"]} == {"total_shows", "peso_total"}


def test_validar_dia_inteiro_retorna_422_orientando_a_usar_shows(cliente):
    resposta = cliente.post("/api/validar", json=BASE)
    assert resposta.status_code == 422
    assert "32" in resposta.json()["detail"] and "`shows`" in resposta.json()["detail"]


def test_validar_com_25_shows_retorna_422(cliente):
    ids = [f"S{i:03d}" for i in range(1, 26)]
    resposta = cliente.post("/api/validar", json=BASE | {"shows": ids})
    assert resposta.status_code == 422
    assert "25" in resposta.json()["detail"]


def test_validar_com_show_de_outro_dia_retorna_422(cliente):
    resposta = cliente.post("/api/validar", json=BASE | {"shows": ["S001", "S040"]})
    assert resposta.status_code == 422
    assert "S040" in resposta.json()["detail"]
