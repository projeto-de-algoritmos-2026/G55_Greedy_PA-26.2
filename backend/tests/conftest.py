from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def ler_fixture():
    def _ler(nome: str) -> str:
        return (FIXTURES / nome).read_text(encoding="utf-8")
    return _ler
