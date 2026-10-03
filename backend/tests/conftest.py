from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def ler_fixture():
    def _ler(nome: str) -> str:
        return (FIXTURES / nome).read_text(encoding="utf-8")
    return _ler


@pytest.fixture
def cliente():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture(autouse=True)
def _limpar_festivais_importados():
    from app.services.loader import limpar_importados

    yield
    limpar_importados()
