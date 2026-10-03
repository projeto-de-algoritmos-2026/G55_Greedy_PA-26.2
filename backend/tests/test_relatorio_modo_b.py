"""Relatório de frequência e magnitude da perda do guloso no deslocamento matricial."""

import csv

import pytest

from scripts.relatorio_modo_b import comparar, executar, resumo_markdown, salvar_csv

SEEDS = 5


@pytest.fixture(scope="module")
def linhas():
    return executar(SEEDS)


def test_relatorio_gera_csv_com_uma_linha_por_instancia(linhas, tmp_path):
    caminho = tmp_path / "dados" / "modo_b.csv"
    salvar_csv(linhas, caminho)
    with caminho.open(encoding="utf-8") as arquivo:
        registros = list(csv.DictReader(arquivo))
    assert len(registros) == len(linhas)
    assert {"modo", "n", "deslocamento_max", "seed", "viola_triangular", "guloso", "otimo",
            "perda", "perda_percentual"} <= set(registros[0])


def test_resumo_traz_percentual_de_instancias_suboptimas(linhas):
    resumo = resumo_markdown(linhas)
    assert "Guloso subótimo" in resumo
    assert "| Matricial, todas |" in resumo
    assert "| Controle: uniforme |" in resumo


def test_dag_nunca_perde_para_o_guloso(linhas):
    assert all(l.perda >= 0 for l in linhas)


def test_controle_uniforme_tem_perda_zero(linhas):
    """No deslocamento uniforme o guloso é ótimo; qualquer perda indicaria erro no experimento."""
    assert all(l.perda == 0 for l in linhas if l.modo == "uniforme")


def test_guloso_perde_de_fato_no_modo_matricial(linhas):
    """A falha do guloso aparece em instâncias aleatórias, não só no contraexemplo montado à mão."""
    assert any(l.perda > 0 for l in linhas if l.modo == "matricial")


def test_perda_percentual_e_modo_invalido():
    linha = comparar(n=0, deslocamento_max=10, seed=0)
    assert (linha.otimo, linha.perda_percentual) == (0, 0.0)
    with pytest.raises(ValueError):
        comparar(n=5, deslocamento_max=10, seed=0, modo="outro")
