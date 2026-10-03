"""Mede com que frequência e por quanto o guloso perde para o DAG no deslocamento matricial.

Para cada instância sintética, compara o número de shows do guloso por menor término com o
ótimo do caminho máximo em DAG. Um grupo de controle no deslocamento uniforme, em que o guloso
é comprovadamente ótimo, precisa mostrar perda zero e valida o próprio experimento.

Uso: uv run python scripts/relatorio_modo_b.py [--seeds 50] [--saida ../docs/dados/modo_b.csv]
"""

import argparse
import csv
import logging
import sys
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.algorithms.dag_longest_path import dag_longest_path  # noqa: E402
from app.algorithms.interval_scheduling import interval_scheduling  # noqa: E402
from app.algorithms.travel_cost import CustoMatricial, CustoUniforme  # noqa: E402
from scripts.gerar_instancias import gerar_instancia  # noqa: E402

TAMANHOS = (10, 20, 40, 80)
DESLOCAMENTOS_MAX = (5, 15, 30, 60)
DENSIDADE = 1.5
PALCOS = 4
SAIDA_PADRAO = Path(__file__).resolve().parents[2] / "docs" / "dados" / "modo_b.csv"


@dataclass(frozen=True)
class LinhaComparacao:
    """Resultado de uma instância: quantos shows o guloso e o ótimo conseguem."""

    modo: str
    n: int
    deslocamento_max: int
    seed: int
    viola_triangular: bool
    guloso: int
    otimo: int

    @property
    def perda(self) -> int:
        """Shows a menos que o guloso consegue em relação ao ótimo. O(1)."""
        return self.otimo - self.guloso

    @property
    def perda_percentual(self) -> float:
        """Perda relativa ao ótimo, em porcentagem. O(1)."""
        return 100 * self.perda / self.otimo if self.otimo else 0.0


def comparar(n: int, deslocamento_max: int, seed: int, modo: str = "matricial") -> LinhaComparacao:
    """Gera a instância e compara guloso e DAG em número de shows. O(n²).

    No modo "uniforme", usa a média do intervalo de deslocamento como delta constante.
    """
    shows, matriz = gerar_instancia(n, DENSIDADE, PALCOS, seed, deslocamento_max)
    if modo == "matricial":
        custo = CustoMatricial(matriz)
    elif modo == "uniforme":
        custo = CustoUniforme((1 + deslocamento_max) // 2)
    else:
        raise ValueError(f"modo inválido: {modo}")
    return LinhaComparacao(
        modo=modo,
        n=n,
        deslocamento_max=deslocamento_max,
        seed=seed,
        viola_triangular=bool(matriz.violacoes_triangulares()),
        guloso=len(interval_scheduling(shows, custo)),
        otimo=len(dag_longest_path(shows, custo, ponderado=False)),
    )


def executar(seeds: int) -> list[LinhaComparacao]:
    """Roda a grade experimental completa nos dois modos. O(modos · cenários · seeds · n²)."""
    return [
        comparar(n, desl, seed, modo)
        for modo in ("matricial", "uniforme")
        for n in TAMANHOS
        for desl in DESLOCAMENTOS_MAX
        for seed in range(seeds)
    ]


def salvar_csv(linhas: Iterable[LinhaComparacao], caminho: Path) -> None:
    """Escreve uma linha por instância, incluindo a perda calculada. O(linhas)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    colunas = [f.name for f in fields(LinhaComparacao)] + ["perda", "perda_percentual"]
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas, lineterminator="\n")
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(
                asdict(linha) | {"perda": linha.perda, "perda_percentual": f"{linha.perda_percentual:.2f}"}
            )


def _agregar(rotulo: str, linhas: Sequence[LinhaComparacao]) -> str:
    perdas = [l for l in linhas if l.perda > 0]
    freq = 100 * len(perdas) / len(linhas) if linhas else 0.0
    media = sum(l.perda for l in linhas) / len(linhas) if linhas else 0.0
    maxima = max((l.perda for l in linhas), default=0)
    pct = sum(l.perda_percentual for l in linhas) / len(linhas) if linhas else 0.0
    return f"| {rotulo} | {len(linhas)} | {freq:.1f}% | {media:.2f} | {maxima} | {pct:.1f}% |"


def resumo_markdown(linhas: Sequence[LinhaComparacao]) -> str:
    """Tabelas em Markdown com frequência e magnitude da perda do guloso. O(linhas)."""
    cabecalho = (
        "| Cenário | Instâncias | Guloso subótimo | Perda média (shows) | Perda máxima | Perda média (%) |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    matricial = [l for l in linhas if l.modo == "matricial"]
    uniforme = [l for l in linhas if l.modo == "uniforme"]

    partes = ["### Deslocamento matricial por cenário", "", cabecalho]
    partes += [
        _agregar(f"n={n}, deslocamento até {d} min", [l for l in matricial if (l.n, l.deslocamento_max) == (n, d)])
        for n in sorted({l.n for l in matricial})
        for d in sorted({l.deslocamento_max for l in matricial})
    ]
    partes += ["", "### Totais", "", cabecalho]
    partes.append(_agregar("Matricial, todas", matricial))
    partes.append(_agregar("Matricial, matriz viola a desigualdade triangular", [l for l in matricial if l.viola_triangular]))
    partes.append(_agregar("Matricial, matriz respeita a desigualdade triangular", [l for l in matricial if not l.viola_triangular]))
    partes.append(_agregar("Controle: uniforme", uniforme))
    return "\n".join(partes)


def main() -> None:
    logging.disable(logging.WARNING)  # violações triangulares são esperadas nas matrizes aleatórias
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=50, help="instâncias por cenário")
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="arquivo CSV de saída")
    args = parser.parse_args()

    linhas = executar(args.seeds)
    salvar_csv(linhas, args.saida)
    print(resumo_markdown(linhas))
    print(f"\nDados por instância: {args.saida}")


if __name__ == "__main__":
    main()
