"""Construção compacta de shows e custos para os testes de algoritmos."""

from app.algorithms.travel_cost import CustoMatricial
from app.models.palco import MatrizDeslocamento
from app.models.show import Show
from app.services.loader import hhmm_para_minutos


def show(id_: str, inicio: str, fim: str, palco: str = "P1", peso: int = 1) -> Show:
    """Show a partir de horários HH:MM, com a mesma virada de dia do loader."""
    return Show(
        id=id_, artista=f"Artista {id_}", palco=palco,
        inicio=hhmm_para_minutos(inicio), fim=hhmm_para_minutos(fim), peso=peso,
    )


def custo_matricial(custos: dict[str, dict[str, int]]) -> CustoMatricial:
    return CustoMatricial(MatrizDeslocamento.model_validate(custos))


def ids(shows) -> list[str]:
    return [s.id for s in shows]


# Instância de referência: com delta 12 ou 0, o máximo é 3 shows (S001, S003, S005).
# S001 -> S003 é a fronteira exata fim + 12 == inicio.
REFERENCIA = [
    show("S001", "14:00", "15:00", "P1"),
    show("S002", "14:30", "16:00", "P2"),
    show("S003", "15:12", "16:20", "P1"),
    show("S004", "15:50", "17:30", "P2"),
    show("S005", "16:40", "17:40", "P3"),
    show("S006", "17:00", "18:20", "P1"),
]
