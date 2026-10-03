"""Importação de grade própria por upload de CSV."""

CSV_VALIDO = (
    "id,artista,palco,dia,hora_inicio,hora_fim\n"
    "S001,Banda Um,P1,1,18:00,19:00\n"
    "S002,Banda Dois,P2,1,18:30,19:30\n"
    "S003,Banda Tres,P1,1,19:20,20:30\n"
)


def _importar(cliente, conteudo, **dados):
    arquivo = conteudo.encode() if isinstance(conteudo, str) else conteudo
    return cliente.post("/api/festivais/importar", files={"arquivo": ("grade.csv", arquivo, "text/csv")}, data=dados)


def test_csv_valido_vira_festival_utilizavel(cliente):
    resposta = _importar(cliente, CSV_VALIDO)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"].startswith("upload-") and corpo["total_shows"] == 3 and corpo["dias"] == 1

    festival_id = corpo["id"]
    assert festival_id in [f["id"] for f in cliente.get("/api/festivais").json()]
    assert len(cliente.get(f"/api/festivais/{festival_id}/grade").json()["shows"]) == 3
    assert cliente.get(f"/api/festivais/{festival_id}/mapa").status_code == 200
    roteiro = cliente.post("/api/roteiro/maximo-shows", json={"festival_id": festival_id, "dia": 1, "delta_uniforme": 0})
    assert roteiro.json()["roteiro"] == ["S001", "S003"]


def test_mesmo_arquivo_gera_mesmo_id(cliente):
    assert _importar(cliente, CSV_VALIDO).json()["id"] == _importar(cliente, CSV_VALIDO).json()["id"]


def test_csv_invalido_retorna_linha_e_coluna(cliente):
    resposta = _importar(cliente, CSV_VALIDO + "S004,Banda Quatro,P9,1,21:00,22:00\n")
    assert resposta.status_code == 422
    assert resposta.json()["erros"] == [
        {"linha": 5, "coluna": "palco", "mensagem": "Palco 'P9' não existe em palcos.json."}
    ]


def test_csv_sem_shows_e_rejeitado(cliente):
    resposta = _importar(cliente, "id,artista,palco,dia,hora_inicio,hora_fim\n")
    assert resposta.status_code == 422
    assert "nenhum show" in resposta.json()["erros"][0]["mensagem"]


def test_festival_base_inexistente_retorna_404(cliente):
    assert _importar(cliente, CSV_VALIDO, festival_base="nao-existe").status_code == 404


def test_arquivo_grande_demais_ou_fora_de_utf8_retorna_422(cliente):
    grande = _importar(cliente, b"x" * (1024 * 1024 + 1))
    assert grande.status_code == 422 and "1 MB" in grande.json()["detail"]
    latin1 = _importar(cliente, "id,artista,palco,dia,hora_inicio,hora_fim\nS001,Canção,P1,1,18:00,19:00\n".encode("latin-1"))
    assert latin1.status_code == 422 and "UTF-8" in latin1.json()["detail"]


def test_arquivo_ausente_retorna_422(cliente):
    resposta = cliente.post("/api/festivais/importar", data={"festival_base": "festival-exemplo"})
    assert resposta.status_code == 422
    assert resposta.json()["erros"][0]["campo"] == "arquivo"
