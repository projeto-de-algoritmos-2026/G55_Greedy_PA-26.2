"""Entidades Palco e MatrizDeslocamento."""

import logging
from itertools import permutations

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

logger = logging.getLogger(__name__)


class Palco(BaseModel):
    """Local físico de um show, posicionado por coordenadas relativas (0 a 1) sobre o mapa."""

    model_config = ConfigDict(frozen=True)

    codigo: str = Field(pattern=r"^P\d+$")
    nome: str = Field(min_length=1)
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class MatrizDeslocamento(RootModel[dict[str, dict[str, int]]]):
    """Tempo de caminhada em minutos entre pares de palcos.

    Invariantes obrigatórias: matriz quadrada, diagonal zero, simetria e
    valores não negativos. A desigualdade triangular não é exigida, mas sua violação
    é registrada em log de aviso.
    """

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def _validar_invariantes(self) -> "MatrizDeslocamento":
        codigos = set(self.root)
        for a, linha in self.root.items():
            if set(linha) != codigos:
                raise ValueError(
                    f"linha '{a}' da matriz deve ter exatamente os palcos {sorted(codigos)}"
                )
        for a, linha in self.root.items():
            if linha[a] != 0:
                raise ValueError(f"D[{a}][{a}] deve ser 0, encontrado {linha[a]}")
            for b, custo in linha.items():
                if custo < 0:
                    raise ValueError(f"D[{a}][{b}] não pode ser negativo ({custo})")
                if custo != self.root[b][a]:
                    raise ValueError(
                        f"matriz não é simétrica: D[{a}][{b}]={custo}, D[{b}][{a}]={self.root[b][a]}"
                    )
        for a, b, c in self.violacoes_triangulares():
            logger.warning(
                "Desigualdade triangular violada: D[%s][%s]=%d > D[%s][%s] + D[%s][%s]=%d",
                a, c, self.root[a][c], a, b, b, c, self.root[a][b] + self.root[b][c],
            )
        return self

    @property
    def palcos(self) -> set[str]:
        """Códigos de palco cobertos pela matriz. O(p)."""
        return set(self.root)

    def custo(self, origem: str, destino: str) -> int:
        """Tempo em minutos de `origem` até `destino`. O(1)."""
        return self.root[origem][destino]

    def violacoes_triangulares(self) -> list[tuple[str, str, str]]:
        """Trios (a, b, c) com D[a][c] > D[a][b] + D[b][c]. O(p³)."""
        return [
            (a, b, c)
            for a, b, c in permutations(sorted(self.root), 3)
            if self.root[a][c] > self.root[a][b] + self.root[b][c]
        ]
