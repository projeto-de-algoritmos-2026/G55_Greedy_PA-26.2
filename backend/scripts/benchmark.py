"""Medição de tempo dos algoritmos com n crescente, exportando CSV.

Executa Interval Scheduling (O(n log n)), Weighted Interval Scheduling (O(n log n)),
Interval Partitioning (O(n log n)) e DAG Longest Path (O(n²)) sobre instâncias
sintéticas com seed fixa para reprodutibilidade.

Uso:
    uv run python scripts/benchmark.py --saida resultado.csv
    uv run python scripts/benchmark.py --ns 10 20 50 100 200 500 --repeticoes 3

A curva medida deve ser compatível com O(n log n) para os algoritmos gulosos/DP
e O(n²) para o DAG.
"""

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.algorithms.dag_longest_path import dag_longest_path  # noqa: E402
from app.algorithms.interval_partitioning import interval_partitioning  # noqa: E402
from app.algorithms.interval_scheduling import interval_scheduling  # noqa: E402
from app.algorithms.travel_cost import CustoMatricial, CustoUniforme  # noqa: E402
from app.algorithms.weighted_scheduling import weighted_interval_scheduling  # noqa: E402
from scripts.gerar_instancias import gerar_instancia  # noqa: E402

DELTA = 12
ALGORITMOS = [
    ("interval_scheduling", "O(n log n)"),
    ("weighted_scheduling", "O(n log n)"),
    ("interval_partitioning", "O(n log n)"),
    ("dag_longest_path", "O(n²)"),
]


def medir(n: int, repeticoes: int, seed_base: int) -> dict[str, float]:
    """Mede o tempo médio de cada algoritmo para instâncias de tamanho n.

    Usa sementes diferentes para cada repetição para evitar viés de cache.
    Retorna tempo médio em milissegundos para cada algoritmo.

    Complexidade: O(repeticoes × n²) no pior caso (DAG).
    """
    tempos: dict[str, list[float]] = {nome: [] for nome, _ in ALGORITMOS}

    for rep in range(repeticoes):
        shows, matriz = gerar_instancia(n=n, densidade=1.0, palcos=4, seed=seed_base + rep)
        custo_uniforme = CustoUniforme(DELTA)
        custo_matricial = CustoMatricial(matriz)

        for nome, _ in ALGORITMOS:
            t0 = time.perf_counter()
            if nome == "interval_scheduling":
                interval_scheduling(shows, custo_uniforme)
            elif nome == "weighted_scheduling":
                weighted_interval_scheduling(shows, custo_uniforme)
            elif nome == "interval_partitioning":
                interval_partitioning(shows)
            elif nome == "dag_longest_path":
                dag_longest_path(shows, custo_matricial)
            tempos[nome].append((time.perf_counter() - t0) * 1000)

    return {nome: statistics.mean(vals) for nome, vals in tempos.items()}


def executar_benchmark(
    ns: list[int],
    repeticoes: int,
    seed_base: int,
    saida: Path | None,
    verbose: bool,
) -> list[dict]:
    """Executa o benchmark completo e opcionalmente grava o CSV.

    Retorna lista de dicts com colunas: n, algoritmo, complexidade, tempo_ms_medio.
    """
    linhas: list[dict] = []

    for n in sorted(ns):
        if verbose:
            print(f"  n={n}...", end=" ", flush=True)
        medicoes = medir(n, repeticoes, seed_base)
        for nome, complexidade in ALGORITMOS:
            linhas.append({
                "n": n,
                "algoritmo": nome,
                "complexidade": complexidade,
                "tempo_ms_medio": round(medicoes[nome], 6),
            })
        if verbose:
            print("ok")

    if saida:
        with saida.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["n", "algoritmo", "complexidade", "tempo_ms_medio"])
            writer.writeheader()
            writer.writerows(linhas)
        if verbose:
            print(f"CSV gravado em {saida}")

    return linhas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ns",
        type=int,
        nargs="+",
        default=[10, 20, 50, 100, 200, 300, 500],
        help="valores de n a medir (padrão: 10 20 50 100 200 300 500)",
    )
    parser.add_argument(
        "--repeticoes",
        type=int,
        default=5,
        help="repetições por ponto (padrão: 5)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="semente base do gerador (padrão: 42)",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=None,
        help="arquivo CSV de saída (opcional)",
    )
    args = parser.parse_args()

    print(f"Benchmark: ns={args.ns}, repeticoes={args.repeticoes}, seed={args.seed}")
    linhas = executar_benchmark(args.ns, args.repeticoes, args.seed, args.saida, verbose=True)

    # Resumo por algoritmo
    print("\nResumo (último n):")
    ultimo_n = max(args.ns)
    for linha in linhas:
        if linha["n"] == ultimo_n:
            print(f"  {linha['algoritmo']:30s} {linha['tempo_ms_medio']:10.4f} ms  ({linha['complexidade']})")


if __name__ == "__main__":
    main()
