"""Aplicação FastAPI do RotaFest."""

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import ErroImportacaoResponse, HealthResponse
from app.routers import festivais
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
app.include_router(api)
