"""Interval Scheduling guloso, incluindo os casos de fronteira obrigatórios."""

from app.algorithms.brute_force import forca_bruta
from app.algorithms.interval_scheduling import interval_scheduling
from app.algorithms.travel_cost import CustoUniforme, roteiro_valido
from tests.fabrica import REFERENCIA, ids, show

DELTA = CustoUniforme(12)


def test_instancia_de_referencia_resulta_em_tres_shows():
    assert ids(interval_scheduling(REFERENCIA, DELTA)) == ["S001", "S003", "S005"]
    assert ids(interval_scheduling(REFERENCIA, CustoUniforme(0))) == ["S001", "S003", "S005"]


def test_empate_de_termino_resolvido_pelo_id():
    shows = [show("S002", "14:30", "15:00"), show("S001", "14:00", "15:00")]
    assert ids(interval_scheduling(shows, DELTA)) == ["S001"]
    assert ids(interval_scheduling(list(reversed(shows)), DELTA)) == ["S001"]


def test_grade_vazia():
    assert interval_scheduling([], DELTA) == []


def test_show_unico():
    unico = show("S001", "14:00", "15:00")
    assert interval_scheduling([unico], DELTA) == [unico]


def test_todos_no_mesmo_horario_seleciona_exatamente_um():
    shows = [show(f"S00{i}", "20:00", "21:00", f"P{i}") for i in range(1, 5)]
    assert ids(interval_scheduling(shows, DELTA)) == ["S001"]


def test_nenhuma_sobreposicao_seleciona_todos():
    shows = [show("S001", "14:00", "15:00"), show("S002", "16:00", "17:00"), show("S003", "18:00", "19:00")]
    assert len(interval_scheduling(shows, DELTA)) == 3


def test_fronteira_fim_mais_delta_igual_inicio():
    shows = [show("S001", "14:00", "15:00"), show("S002", "15:12", "16:00")]
    assert len(interval_scheduling(shows, DELTA)) == 2


def test_show_que_atravessa_meia_noite():
    shows = [show("S001", "23:30", "01:00"), show("S002", "01:12", "02:00"), show("S003", "00:30", "01:30")]
    assert ids(interval_scheduling(shows, DELTA)) == ["S001", "S002"]


def test_delta_zero_equivale_ao_problema_classico():
    shows = [show("S001", "14:00", "15:00"), show("S002", "15:00", "16:00"), show("S003", "14:30", "15:30")]
    assert ids(interval_scheduling(shows, CustoUniforme(0))) == ["S001", "S002"]


def test_delta_enorme_torna_todos_incompativeis():
    assert len(interval_scheduling(REFERENCIA, CustoUniforme(24 * 60))) == 1


def test_resultado_e_valido_e_otimo_na_referencia():
    roteiro = interval_scheduling(REFERENCIA, DELTA)
    assert roteiro_valido(roteiro, DELTA)
    assert len(roteiro) == len(forca_bruta(REFERENCIA, DELTA).max_cardinalidade)
