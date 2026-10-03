"""Endpoints de festivais, grade e mapa."""

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from app.models.schemas import FestivalResumo, GradeResponse, ImportarResponse, ShowGrade
from app.services.loader import (
    caminho_mapa,
    carregar_festival,
    listar_festivais,
    registrar_festival_importado,
)

TAMANHO_MAXIMO_CSV = 1024 * 1024
FESTIVAL_BASE_PADRAO = "festival-exemplo"

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
    arquivo = caminho_mapa(festival)
    if not arquivo.is_file():
        raise HTTPException(status_code=404, detail=f"Mapa do festival '{festival.nome}' não encontrado.")
    return FileResponse(arquivo, media_type="image/svg+xml")


@router.post("/importar", response_model=ImportarResponse, status_code=201)
async def post_importar(
    arquivo: UploadFile = File(description="CSV da grade: id,artista,palco,dia,hora_inicio,hora_fim"),
    festival_base: str = Form(FESTIVAL_BASE_PADRAO, description="Festival cujos palcos e mapa são reaproveitados"),
) -> ImportarResponse:
    """Importa uma grade própria. Fica só em memória e some quando o servidor reinicia."""
    bruto = await arquivo.read(TAMANHO_MAXIMO_CSV + 1)
    if len(bruto) > TAMANHO_MAXIMO_CSV:
        raise HTTPException(status_code=422, detail="O arquivo excede o limite de 1 MB.")
    try:
        conteudo = bruto.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="O arquivo precisa estar em UTF-8.") from None
    festival = registrar_festival_importado(conteudo, festival_base)
    return ImportarResponse(id=festival.id, nome=festival.nome, dias=festival.dias, total_shows=len(festival.shows))
