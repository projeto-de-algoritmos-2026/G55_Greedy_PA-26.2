"""Leitura e validação dos dados de festival (grade_festival.csv e palcos.json).

A importação é tudo ou nada: todos os erros do CSV são coletados e reportados juntos,
com linha e coluna, e nenhum show é devolvido se houver qualquer erro.
"""

import csv
import io
import json
import re
from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError

from app.models.festival import ConfigDeslocamento, Festival
from app.models.palco import Palco
from app.models.schemas import ErroLinha
from app.models.show import Show

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ARQUIVO_GRADE = "grade_festival.csv"
ARQUIVO_PALCOS = "palcos.json"

COLUNAS = ["id", "artista", "palco", "dia", "hora_inicio", "hora_fim"]
MINUTOS_DIA = 1440
CORTE_DIA_FESTIVAL = 6 * 60  # o dia de festival vai de 06:00 às 05:59
MAX_ARTISTA = 80

_RE_HORA = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
_RE_ID_FESTIVAL = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ErroImportacao(Exception):
    """Grade inválida. Carrega todos os erros encontrados, cada um com linha e coluna."""

    def __init__(self, erros: list[ErroLinha]):
        self.erros = erros
        super().__init__(f"Grade inválida: {len(erros)} erro(s) encontrado(s).")


class FestivalNaoEncontrado(LookupError):
    """Festival inexistente no diretório de dados."""


def hhmm_para_minutos(hora: str) -> int:
    """Converte `HH:MM` em minutos do dia de festival, somando 1440 aos horários antes de 06:00. O(1).

    Horários antes de 06:00 pertencem à madrugada e recebem +1440.
    Levanta ValueError se o formato não for HH:MM de 24 horas.
    """
    m = _RE_HORA.match(hora.strip())
    if not m:
        raise ValueError(f"Formato inválido '{hora}'; use HH:MM de 24 horas.")
    minutos = int(m.group(1)) * 60 + int(m.group(2))
    return minutos if minutos >= CORTE_DIA_FESTIVAL else minutos + MINUTOS_DIA


def ler_grade(conteudo: str, codigos_palcos: set[str]) -> list[Show]:
    """Lê o CSV da grade a partir do texto. O(n).

    Levanta ErroImportacao com todos os erros se qualquer linha for inválida.
    A linha 1 é o cabeçalho, de modo que a numeração coincide com a de um editor.
    """
    leitor = csv.reader(io.StringIO(conteudo.lstrip("﻿")))
    cabecalho = next(leitor, None)
    if cabecalho is None or [c.strip() for c in cabecalho] != COLUNAS:
        raise ErroImportacao([
            ErroLinha(linha=1, coluna="cabeçalho",
                      mensagem=f"Cabeçalho deve ser exatamente: {','.join(COLUNAS)}.")
        ])

    erros: list[ErroLinha] = []
    shows: list[Show] = []
    ids_vistos: dict[str, int] = {}

    for numero, campos in enumerate(leitor, start=2):
        if not any(c.strip() for c in campos):
            continue
        if len(campos) != len(COLUNAS):
            erros.append(ErroLinha(linha=numero, coluna="linha",
                                   mensagem=f"Esperadas {len(COLUNAS)} colunas, encontradas {len(campos)}."))
            continue

        valores = dict(zip(COLUNAS, (c.strip() for c in campos)))
        erros_linha = _validar_linha(numero, valores, codigos_palcos, ids_vistos)
        if erros_linha:
            erros.extend(erros_linha)
            continue

        try:
            shows.append(Show(
                id=valores["id"],
                artista=valores["artista"],
                palco=valores["palco"],
                dia=int(valores["dia"]),
                inicio=hhmm_para_minutos(valores["hora_inicio"]),
                fim=hhmm_para_minutos(valores["hora_fim"]),
            ))
        except ValidationError as e:
            for detalhe in e.errors():
                coluna = str(detalhe["loc"][0]) if detalhe["loc"] else "linha"
                erros.append(ErroLinha(linha=numero, coluna=coluna, mensagem=detalhe["msg"]))

    if erros:
        raise ErroImportacao(erros)
    return shows


def _validar_linha(
    numero: int, valores: dict[str, str], codigos_palcos: set[str], ids_vistos: dict[str, int]
) -> list[ErroLinha]:
    erros: list[ErroLinha] = []

    def erro(coluna: str, mensagem: str) -> None:
        erros.append(ErroLinha(linha=numero, coluna=coluna, mensagem=mensagem))

    id_show = valores["id"]
    if not id_show:
        erro("id", "Id é obrigatório.")
    elif id_show in ids_vistos:
        erro("id", f"Id '{id_show}' duplicado; já usado na linha {ids_vistos[id_show]}.")
    else:
        ids_vistos[id_show] = numero

    artista = valores["artista"]
    if not artista:
        erro("artista", "Artista não pode ser vazio.")
    elif len(artista) > MAX_ARTISTA:
        erro("artista", f"Artista excede {MAX_ARTISTA} caracteres ({len(artista)}).")

    if valores["palco"] not in codigos_palcos:
        erro("palco", f"Palco '{valores['palco']}' não existe em palcos.json.")

    if not valores["dia"].isdigit() or int(valores["dia"]) < 1:
        erro("dia", f"Dia deve ser inteiro maior ou igual a 1, encontrado '{valores['dia']}'.")

    horarios: dict[str, int] = {}
    for coluna in ("hora_inicio", "hora_fim"):
        try:
            horarios[coluna] = hhmm_para_minutos(valores[coluna])
        except ValueError as e:
            erro(coluna, str(e))

    if len(horarios) == 2 and horarios["hora_fim"] <= horarios["hora_inicio"]:
        erro("hora_fim",
             f"Show termina ({valores['hora_fim']}) antes de começar ({valores['hora_inicio']}) "
             "no dia de festival, que vai de 06:00 às 05:59.")
    return erros


def carregar_festival_de_diretorio(diretorio: Path) -> Festival:
    """Carrega e valida palcos.json e grade_festival.csv de um diretório. O(n + p³)."""
    dados = json.loads((diretorio / ARQUIVO_PALCOS).read_text(encoding="utf-8"))
    palcos = tuple(Palco.model_validate(p) for p in dados["palcos"])
    deslocamento = ConfigDeslocamento.model_validate(dados["deslocamento"])
    conteudo = (diretorio / ARQUIVO_GRADE).read_text(encoding="utf-8")
    shows = ler_grade(conteudo, {p.codigo for p in palcos})
    return Festival(
        id=diretorio.name,
        nome=dados["festival"],
        mapa=dados["mapa"],
        palcos=palcos,
        deslocamento=deslocamento,
        shows=tuple(shows),
    )


@lru_cache(maxsize=32)
def carregar_festival(festival_id: str) -> Festival:
    """Carrega um festival do diretório de dados, com cache. O(n + p³) na primeira chamada."""
    diretorio = caminho_festival(festival_id)
    return carregar_festival_de_diretorio(diretorio)


def caminho_festival(festival_id: str) -> Path:
    """Resolve o diretório do festival, rejeitando ids fora do padrão (evita path traversal). O(1)."""
    diretorio = DATA_DIR / festival_id
    if not _RE_ID_FESTIVAL.match(festival_id) or not (diretorio / ARQUIVO_PALCOS).is_file():
        raise FestivalNaoEncontrado(f"Festival '{festival_id}' não encontrado.")
    return diretorio


def listar_festivais() -> list[Festival]:
    """Todos os festivais do diretório de dados, em ordem de id. O(f · (n + p³))."""
    return [
        carregar_festival(d.name)
        for d in sorted(DATA_DIR.iterdir())
        if d.is_dir() and (d / ARQUIVO_PALCOS).is_file()
    ]
