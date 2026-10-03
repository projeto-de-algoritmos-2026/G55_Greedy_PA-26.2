"""Aplicação FastAPI do RotaFest."""

from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.algorithms.brute_force import InstanciaGrandeDemais
from app.models.schemas import ErroCampo, ErroImportacaoResponse, ErroValidacaoResponse, HealthResponse
from app.routers import analise, festivais, roteiro
from app.services.calculo import DiaSemShows, ErroRequisicao
from app.services.loader import ErroImportacao, FestivalNaoEncontrado

app = FastAPI(
    title="RotaFest API",
    description="Roteiros de festival otimizados por algoritmos ambiciosos.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FestivalNaoEncontrado)
async def _festival_nao_encontrado(_: Request, exc: FestivalNaoEncontrado) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DiaSemShows)
async def _dia_sem_shows(_: Request, exc: DiaSemShows) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ErroRequisicao)
async def _erro_requisicao(_: Request, exc: ErroRequisicao) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(InstanciaGrandeDemais)
async def _instancia_grande_demais(_: Request, exc: InstanciaGrandeDemais) -> JSONResponse:
    detalhe = f"{exc} Escolha até 20 shows do dia no campo `shows`."
    return JSONResponse(status_code=422, content={"detail": detalhe})


def _mensagem_em_portugues(erro: dict[str, Any]) -> str:
    """Traduz os tipos de erro de validação mais comuns do Pydantic."""
    ctx = erro.get("ctx") or {}
    traducoes = {
        "missing": "Campo obrigatório.",
        "int_parsing": "Deve ser um número inteiro.",
        "int_type": "Deve ser um número inteiro.",
        "string_type": "Deve ser um texto.",
        "list_type": "Deve ser uma lista.",
        "dict_type": "Deve ser um objeto.",
        "json_invalid": "JSON inválido.",
        "greater_than_equal": f"Deve ser maior ou igual a {ctx.get('ge')}.",
        "less_than_equal": f"Deve ser menor ou igual a {ctx.get('le')}.",
        "literal_error": f"Valor inválido; use {ctx.get('expected')}.",
    }
    return traducoes.get(erro["type"], erro["msg"])


@app.exception_handler(RequestValidationError)
async def _erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
    erros = [
        ErroCampo(
            campo=".".join(str(p) for p in e["loc"] if p != "body") or "corpo",
            mensagem=_mensagem_em_portugues(e),
        )
        for e in exc.errors()
    ]
    primeiro = erros[0]
    detalhe = f"Requisição inválida: {primeiro.campo}: {primeiro.mensagem}"
    if len(erros) > 1:
        detalhe += f" (e mais {len(erros) - 1} erro(s))"
    corpo = ErroValidacaoResponse(detail=detalhe, erros=erros)
    return JSONResponse(status_code=422, content=corpo.model_dump())


@app.exception_handler(ErroImportacao)
async def _erro_importacao(_: Request, exc: ErroImportacao) -> JSONResponse:
    corpo = ErroImportacaoResponse(detail=str(exc), erros=exc.erros)
    return JSONResponse(status_code=422, content=corpo.model_dump())


api = APIRouter(prefix="/api")


@api.get("/health", response_model=HealthResponse, tags=["infra"])
def health() -> HealthResponse:
    """Verificação de disponibilidade."""
    return HealthResponse()


api.include_router(festivais.router)
api.include_router(roteiro.router)
api.include_router(analise.router)
app.include_router(api)
