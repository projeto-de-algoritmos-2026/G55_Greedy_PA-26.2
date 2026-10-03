"""Endpoints de festivais, grade e mapa."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.models.schemas import FestivalResumo, GradeResponse, ShowGrade
from app.services.loader import caminho_festival, carregar_festival, listar_festivais

router = APIRouter(prefix="/festivais", tags=["festivais"])


@router.get("", response_model=list[FestivalResumo])
def get_festivais() -> list[FestivalResumo]:
    """Lista os festivais disponíveis no diretório de dados."""
    return [
        FestivalResumo(id=f.id, nome=f.nome, dias=f.dias, total_shows=len(f.shows))
        for f in listar_festivais()
    ]


@router.get("/{festival_id}/grade", response_model=GradeResponse)
def get_grade(festival_id: str, dia: int = Query(default=1, ge=1)) -> GradeResponse:
    """Grade de um dia, com shows ordenados por (inicio, id)."""
    festival = carregar_festival(festival_id)
    shows = festival.shows_do_dia(dia)
    if not shows:
        raise HTTPException(
            status_code=404,
            detail=f"O festival '{festival.nome}' não tem shows no dia {dia} "
                   f"(dias disponíveis: 1 a {festival.dias}).",
        )
    return GradeResponse(
        festival=festival.nome,
        dia=dia,
        palcos=list(festival.palcos),
        shows=[ShowGrade.model_validate(s, from_attributes=True) for s in shows],
    )


@router.get("/{festival_id}/mapa", response_class=FileResponse)
def get_mapa(festival_id: str) -> FileResponse:
    """Imagem SVG do mapa do festival."""
    festival = carregar_festival(festival_id)
    arquivo = caminho_festival(festival_id) / festival.mapa
    if not arquivo.is_file():
        raise HTTPException(status_code=404, detail=f"Mapa do festival '{festival.nome}' não encontrado.")
    return FileResponse(arquivo, media_type="image/svg+xml")
