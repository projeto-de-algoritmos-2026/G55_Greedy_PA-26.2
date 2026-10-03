"""Testes da camada de dados: modelos, loader e endpoints de festivais."""

import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models.palco import MatrizDeslocamento
from app.models.show import Show
from app.services.loader import (
    ErroImportacao,
    FestivalNaoEncontrado,
    caminho_festival,
    carregar_festival,
    hhmm_para_minutos,
    ler_grade,
)

PALCOS = {"P1", "P2"}


# --- Conversão de horário e virada do dia de festival -------------------------------

@pytest.mark.parametrize(("hora", "minutos"), [
    ("06:00", 360),
    ("14:00", 840),
    ("23:59", 1439),
    ("00:00", 1440),
    ("01:30", 1530),
    ("05:59", 1799),
])
def test_hhmm_para_minutos_aplica_virada_do_dia_de_festival(hora, minutos):
    assert hhmm_para_minutos(hora) == minutos


@pytest.mark.parametrize("hora", ["24:00", "9:00", "14h30", "12:60", "", "ab:cd"])
def test_hhmm_para_minutos_rejeita_formato_invalido(hora):
    with pytest.raises(ValueError):
        hhmm_para_minutos(hora)


# --- Leitura da grade -------------------------------------------------------------

def test_show_que_atravessa_meia_noite(ler_fixture):
    shows = {s.id: s for s in ler_grade(ler_fixture("grade_valida.csv"), PALCOS)}
    assert (shows["S003"].inicio, shows["S003"].fim) == (1410, 1500)


def test_show_que_comeca_apos_meia_noite_fica_no_fim_do_dia(ler_fixture):
    shows = {s.id: s for s in ler_grade(ler_fixture("grade_valida.csv"), PALCOS)}
    assert (shows["S004"].inicio, shows["S004"].fim) == (1470, 1530)
    assert shows["S004"].inicio > shows["S003"].inicio


def test_grade_valida_preserva_dia_e_peso_padrao(ler_fixture):
    shows = ler_grade(ler_fixture("grade_valida.csv"), PALCOS)
    assert len(shows) == 5
    assert all(s.peso == 1 for s in shows)
    assert [s.dia for s in shows] == [1, 1, 1, 1, 2]


def test_erro_palco_inexistente_cita_linha_e_coluna(ler_fixture):
    with pytest.raises(ErroImportacao) as exc:
        ler_grade(ler_fixture("grade_palco_inexistente.csv"), PALCOS)
    [erro] = exc.value.erros
    assert (erro.linha, erro.coluna) == (4, "palco")
    assert "P9" in erro.mensagem


def test_erro_id_duplicado_cita_linha_original(ler_fixture):
    with pytest.raises(ErroImportacao) as exc:
        ler_grade(ler_fixture("grade_id_duplicado.csv"), PALCOS)
    [erro] = exc.value.erros
    assert (erro.linha, erro.coluna) == (3, "id")
    assert "linha 2" in erro.mensagem


def test_erro_horario_invalido_reporta_todos_os_erros(ler_fixture):
    with pytest.raises(ErroImportacao) as exc:
        ler_grade(ler_fixture("grade_horario_invalido.csv"), PALCOS)
    assert [(e.linha, e.coluna) for e in exc.value.erros] == [(3, "hora_inicio"), (4, "hora_fim")]


def test_importacao_nao_e_parcial(ler_fixture):
    """Uma linha inválida invalida a grade inteira; não há importação parcial."""
    with pytest.raises(ErroImportacao):
        ler_grade(ler_fixture("grade_palco_inexistente.csv"), PALCOS)


def test_cabecalho_invalido():
    with pytest.raises(ErroImportacao) as exc:
        ler_grade("id,artista,palco\nS001,A,P1\n", PALCOS)
    assert exc.value.erros[0].linha == 1


def test_show_com_duracao_nula_ou_negativa():
    csv = "id,artista,palco,dia,hora_inicio,hora_fim\nS001,A,P1,1,15:00,15:00\nS002,B,P1,1,05:00,07:00\n"
    with pytest.raises(ErroImportacao) as exc:
        ler_grade(csv, PALCOS)
    assert [(e.linha, e.coluna) for e in exc.value.erros] == [(2, "hora_fim"), (3, "hora_fim")]


def test_artista_vazio_e_longo_e_dia_invalido():
    csv = (
        "id,artista,palco,dia,hora_inicio,hora_fim\n"
        "S001,,P1,1,14:00,15:00\n"
        f"S002,{'x' * 81},P1,1,16:00,17:00\n"
        "S003,C,P1,0,18:00,19:00\n"
    )
    with pytest.raises(ErroImportacao) as exc:
        ler_grade(csv, PALCOS)
    assert [(e.linha, e.coluna) for e in exc.value.erros] == [(2, "artista"), (3, "artista"), (4, "dia")]


def test_linha_com_colunas_faltando():
    csv = "id,artista,palco,dia,hora_inicio,hora_fim\nS001,A,P1,1,14:00\n"
    with pytest.raises(ErroImportacao) as exc:
        ler_grade(csv, PALCOS)
    assert exc.value.erros[0].linha == 2


# --- Modelos -----------------------------------------------------------------------

def test_show_com_fim_antes_do_inicio_e_invalido():
    with pytest.raises(ValidationError):
        Show(id="S001", artista="A", palco="P1", inicio=900, fim=840)


@pytest.mark.parametrize("peso", [0, 11])
def test_show_com_peso_fora_do_intervalo_e_invalido(peso):
    with pytest.raises(ValidationError):
        Show(id="S001", artista="A", palco="P1", inicio=840, fim=900, peso=peso)


@pytest.mark.parametrize("matriz", [
    {"P1": {"P1": 0, "P2": 5}, "P2": {"P1": 7, "P2": 0}},   # assimétrica
    {"P1": {"P1": 1, "P2": 5}, "P2": {"P1": 5, "P2": 0}},   # diagonal não nula
    {"P1": {"P1": 0, "P2": -5}, "P2": {"P1": -5, "P2": 0}}, # negativa
    {"P1": {"P1": 0, "P2": 5}, "P2": {"P2": 0}},            # não quadrada
])
def test_matriz_invalida_levanta_validation_error(matriz):
    with pytest.raises(ValidationError):
        MatrizDeslocamento.model_validate(matriz)


def test_violacao_triangular_gera_aviso_mas_e_aceita(caplog):
    matriz = {
        "P1": {"P1": 0, "P2": 2, "P3": 30},
        "P2": {"P1": 2, "P2": 0, "P3": 3},
        "P3": {"P1": 30, "P2": 3, "P3": 0},
    }
    with caplog.at_level(logging.WARNING):
        m = MatrizDeslocamento.model_validate(matriz)
    assert m.custo("P1", "P3") == 30
    assert "triangular" in caplog.text


# --- Festival de exemplo e API -----------------------------------------------------

def test_festival_exemplo_e_valido():
    festival = carregar_festival("festival-exemplo")
    assert len(festival.shows) >= 60
    assert festival.deslocamento.matriz.violacoes_triangulares() == []


@pytest.mark.parametrize("festival_id", ["../app", "inexistente", "Festival-Exemplo"])
def test_festival_id_invalido_nao_escapa_do_diretorio(festival_id):
    with pytest.raises(FestivalNaoEncontrado):
        caminho_festival(festival_id)


@pytest.fixture
def cliente():
    return TestClient(app)


def test_health(cliente):
    resposta = cliente.get("/api/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_get_festivais(cliente):
    resposta = cliente.get("/api/festivais")
    assert resposta.status_code == 200
    assert {"id": "festival-exemplo", "nome": "Festival Cerrado Sonoro", "dias": 2, "total_shows": 64} in resposta.json()


def test_get_grade_segue_contrato(cliente):
    resposta = cliente.get("/api/festivais/festival-exemplo/grade", params={"dia": 1})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"festival", "dia", "palcos", "shows"}
    assert set(corpo["palcos"][0]) == {"codigo", "nome", "x", "y"}
    assert set(corpo["shows"][0]) == {"id", "artista", "palco", "inicio", "fim", "peso"}
    chaves = [(s["inicio"], s["id"]) for s in corpo["shows"]]
    assert chaves == sorted(chaves)


def test_get_grade_dia_inexistente_retorna_404(cliente):
    resposta = cliente.get("/api/festivais/festival-exemplo/grade", params={"dia": 9})
    assert resposta.status_code == 404
    assert "dia 9" in resposta.json()["detail"]


def test_get_grade_festival_inexistente_retorna_404(cliente):
    resposta = cliente.get("/api/festivais/nao-existe/grade")
    assert resposta.status_code == 404
    assert "não encontrado" in resposta.json()["detail"]


def test_get_mapa(cliente):
    resposta = cliente.get("/api/festivais/festival-exemplo/mapa")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("image/svg+xml")
