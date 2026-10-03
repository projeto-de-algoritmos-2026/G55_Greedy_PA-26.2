"""Valida a grade de um festival e as invariantes da matriz de deslocamento.

Uso: uv run python scripts/validar_dados.py <festival_id>
"""

import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError  # noqa: E402

from app.services.loader import (  # noqa: E402
    ErroImportacao,
    FestivalNaoEncontrado,
    carregar_festival,
)

MIN_SHOWS = 60


def main(festival_id: str) -> int:
    logging.basicConfig(level=logging.WARNING, format="AVISO: %(message)s")
    try:
        festival = carregar_festival(festival_id)
    except FestivalNaoEncontrado as e:
        print(f"ERRO: {e}")
        return 1
    except ErroImportacao as e:
        print(f"ERRO: {e}")
        for erro in e.erros:
            print(f"  linha {erro.linha}, coluna {erro.coluna}: {erro.mensagem}")
        return 1
    except ValidationError as e:
        print(f"ERRO em palcos.json:\n{e}")
        return 1

    matriz = festival.deslocamento.matriz
    por_dia = Counter(s.dia for s in festival.shows)
    madrugada = sum(1 for s in festival.shows if s.fim > 1440)

    print(f"Festival: {festival.nome} ({festival.id})")
    print(f"Palcos: {', '.join(f'{p.codigo} {p.nome}' for p in festival.palcos)}")
    print(f"Shows: {len(festival.shows)} " + " ".join(f"[dia {d}: {n}]" for d, n in sorted(por_dia.items())))
    print(f"Shows que terminam após a meia-noite: {madrugada}")
    print("Matriz de deslocamento: diagonal zero, simétrica e não negativa (OK)")
    violacoes = matriz.violacoes_triangulares()
    print(f"Desigualdade triangular: {'OK' if not violacoes else f'{len(violacoes)} violação(ões)'}")

    if len(festival.shows) < MIN_SHOWS:
        print(f"ERRO: a grade deve ter no mínimo {MIN_SHOWS} shows.")
        return 1
    print("Resultado: dados válidos.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
