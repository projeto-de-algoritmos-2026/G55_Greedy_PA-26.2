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


def test_benchmark_retorna_pontos_para_cada_algoritmo(cliente):
    """GET /benchmark com n pequeno deve retornar um ponto por algoritmo por n."""
    resposta = cliente.get("/api/benchmark?ns=10&ns=20&repeticoes=1")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["ns"] == [10, 20]
    assert corpo["repeticoes"] == 1
    assert len(corpo["pontos"]) == 8  # 4 algoritmos × 2 valores de n
    algoritmos = {p["algoritmo"] for p in corpo["pontos"]}
    assert algoritmos == {"interval_scheduling", "weighted_scheduling", "interval_partitioning", "dag_longest_path"}
    for ponto in corpo["pontos"]:
        assert ponto["tempo_ms_medio"] >= 0
        assert ponto["complexidade"] in {"O(n log n)", "O(n²)"}


def test_gerador_produz_shows_e_matriz():
    """Verifica que gerar_instancia é determinístico e retorna o número correto de shows."""
    from app.algorithms.gerador import gerar_instancia

    shows1, matriz1 = gerar_instancia(n=15, palcos=3, seed=7)
    shows2, matriz2 = gerar_instancia(n=15, palcos=3, seed=7)
    assert len(shows1) == 15
    assert all(s1.id == s2.id and s1.inicio == s2.inicio for s1, s2 in zip(shows1, shows2))
    assert matriz1.model_dump() == matriz2.model_dump()
    codigos = {s.palco for s in shows1}
    assert codigos <= {"P1", "P2", "P3"}


def test_gerador_raises_on_invalid_args():
    from app.algorithms.gerador import gerar_instancia
    import pytest as _pytest

    with _pytest.raises(ValueError):
        gerar_instancia(n=-1)
    with _pytest.raises(ValueError):
        gerar_instancia(n=5, palcos=0)
    with _pytest.raises(ValueError):
        gerar_instancia(n=5, densidade=0)

