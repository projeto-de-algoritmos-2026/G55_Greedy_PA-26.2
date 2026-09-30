"""Entidade Show (SPEC 2.2)."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

PESO_MIN = 1
PESO_MAX = 10
PESO_PADRAO = 1


class Show(BaseModel):
    """Apresentação única. Tempos em minutos desde 00:00 do dia de festival (D-1, D-7)."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^S\d{3,}$")
    artista: str = Field(min_length=1, max_length=80)
    palco: str = Field(min_length=1)
    inicio: int = Field(ge=0)
    fim: int = Field(ge=0)
    peso: int = Field(default=PESO_PADRAO, ge=PESO_MIN, le=PESO_MAX)
    dia: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def _fim_depois_do_inicio(self) -> "Show":
        if self.fim <= self.inicio:
            raise ValueError(f"fim ({self.fim}) deve ser maior que inicio ({self.inicio})")
        return self

    @property
    def duracao(self) -> int:
        """Duração do show em minutos. O(1)."""
        return self.fim - self.inicio
