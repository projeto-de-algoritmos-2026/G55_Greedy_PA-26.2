"""Rotas de roteiro: contrato, escolha do algoritmo por modo, pesos e erros."""

import pytest

from app.services.loader import carregar_festival

BASE = {"festival_id": "festival-exemplo", "dia": 1}
ROTAS = ["/api/roteiro/maximo-shows", "/api/roteiro/maxima-satisfacao"]
CAMPOS = {"estrategia", "otimo_garantido", "roteiro", "total_shows", "peso_total", "deslocamentos", "tempo_execucao_ms"}


@pytest.mark.parametrize("rota", ROTAS)
@pytest.mark.parametrize("modo", ["uniforme", "matricial"])
def test_contrato_e_otimalidade_garantida(cliente, rota, modo):
    resposta = cliente.post(rota, json=BASE | {"modo_deslocamento": modo})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == CAMPOS
    assert corpo["otimo_garantido"] is True
    assert corpo["total_shows"] == len(corpo["roteiro"]) > 0
    assert len(corpo["deslocamentos"]) == corpo["total_shows"] - 1


@pytest.mark.parametrize(("rota", "modo", "estrategia"), [
    ("/api/roteiro/maximo-shows", "uniforme", "interval_scheduling_guloso"),
    ("/api/roteiro/maximo-shows", "matricial", "dag_longest_path"),
    ("/api/roteiro/maxima-satisfacao", "uniforme", "weighted_interval_scheduling_dp"),
    ("/api/roteiro/maxima-satisfacao", "matricial", "dag_longest_path"),
])
def test_estrategia_depende_do_modo(cliente, rota, modo, estrategia):
    assert cliente.post(rota, json=BASE | {"modo_deslocamento": modo}).json()["estrategia"] == estrategia


@pytest.mark.parametrize("modo", ["uniforme", "matricial"])
def test_deslocamentos_tem_custo_e_folga_coerentes(cliente, modo):
    corpo = cliente.post(ROTAS[0], json=BASE | {"modo_deslocamento": modo, "delta_uniforme": 12}).json()
    shows = {s.id: s for s in carregar_festival("festival-exemplo").shows}
    matriz = carregar_festival("festival-exemplo").deslocamento.matriz
    for d in corpo["deslocamentos"]:
        a, b = shows[d["de"]], shows[d["para"]]
        custo = 12 if modo == "uniforme" else matriz.custo(a.palco, b.palco)
        assert (d["palco_origem"], d["palco_destino"]) == (a.palco, b.palco)
        assert d["custo_min"] == custo
        assert d["folga_min"] == b.inicio - a.fim - custo >= 0


def test_padroes_do_festival_quando_modo_e_delta_sao_omitidos(cliente):
    omitido = cliente.post(ROTAS[0], json=BASE).json()
    explicito = cliente.post(ROTAS[0], json=BASE | {"modo_deslocamento": "uniforme", "delta_uniforme": 12}).json()
    assert omitido["roteiro"] == explicito["roteiro"]


def test_peso_alto_traz_o_show_para_o_roteiro_de_satisfacao(cliente):
    sem_peso = cliente.post(ROTAS[1], json=BASE).json()
    com_peso = cliente.post(ROTAS[1], json=BASE | {"pesos": {"S023": 10}}).json()
    assert "S023" not in sem_peso["roteiro"]
    assert "S023" in com_peso["roteiro"]
    assert com_peso["peso_total"] > sem_peso["peso_total"]


def test_peso_fora_do_intervalo_retorna_422_em_portugues(cliente):
    resposta = cliente.post(ROTAS[1], json=BASE | {"pesos": {"S001": 11}})
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert isinstance(corpo["detail"], str) and "menor ou igual a 10" in corpo["detail"]
    assert corpo["erros"] == [{"campo": "pesos.S001", "mensagem": "Deve ser menor ou igual a 10."}]


def test_peso_para_show_inexistente_retorna_422(cliente):
    resposta = cliente.post(ROTAS[1], json=BASE | {"pesos": {"S999": 5}})
    assert resposta.status_code == 422
    assert "S999" in resposta.json()["detail"]


def test_campos_obrigatorios_e_modo_invalido(cliente):
    sem_dia = cliente.post(ROTAS[0], json={"festival_id": "festival-exemplo"})
    assert sem_dia.status_code == 422 and sem_dia.json()["erros"][0] == {"campo": "dia", "mensagem": "Campo obrigatório."}
    modo = cliente.post(ROTAS[0], json=BASE | {"modo_deslocamento": "teleporte"})
    assert modo.status_code == 422 and "Valor inválido" in modo.json()["detail"]


def test_festival_ou_dia_inexistente_retorna_404(cliente):
    assert cliente.post(ROTAS[0], json={"festival_id": "nao-existe", "dia": 1}).status_code == 404
    resposta = cliente.post(ROTAS[0], json=BASE | {"dia": 9})
    assert resposta.status_code == 404 and "dia 9" in resposta.json()["detail"]
