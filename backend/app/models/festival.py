"""Agregado Festival: palcos, configuração de deslocamento e grade."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.palco import MatrizDeslocamento, Palco
from app.models.show import Show

ModoDeslocamento = Literal["uniforme", "matricial"]


class ConfigDeslocamento(BaseModel):
    """Bloco `deslocamento` do palcos.json."""

    model_config = ConfigDict(frozen=True)

    modo_padrao: ModoDeslocamento
    delta_uniforme: int = Field(ge=0)
    matriz: MatrizDeslocamento


class Festival(BaseModel):
    """Festival carregado e validado a partir do diretório de dados."""

    model_config = ConfigDict(frozen=True)

    id: str
    nome: str = Field(min_length=1)
    mapa: str
    diretorio: str  # pasta em data/ de onde vêm o mapa e os palcos (a do festival base, se importado)
    palcos: tuple[Palco, ...]
    deslocamento: ConfigDeslocamento
    shows: tuple[Show, ...]

    @model_validator(mode="after")
    def _palcos_consistentes(self) -> "Festival":
        codigos = [p.codigo for p in self.palcos]
        if len(codigos) != len(set(codigos)):
            raise ValueError("códigos de palco duplicados em palcos.json")
        if set(codigos) != self.deslocamento.matriz.palcos:
            raise ValueError(
                f"a matriz de deslocamento deve cobrir exatamente os palcos {sorted(codigos)}"
            )
        return self

    @property
    def dias(self) -> int:
        """Número de dias do festival (maior `dia` da grade). O(n)."""
        return max((s.dia for s in self.shows), default=0)

    def shows_do_dia(self, dia: int) -> list[Show]:
        """Shows do dia ordenados por (inicio, id); o id desempata. O(n log n)."""
        return sorted((s for s in self.shows if s.dia == dia), key=lambda s: (s.inicio, s.id))
