import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

pytestmark = pytest.mark.asyncio


MODULE = "app.routers.location"
def load_module():
    return __import__(MODULE, fromlist=["*"])


# ============================
# ESTADOS
# ============================
async def test_get_estados_success(monkeypatch):
    mod = load_module()

    async def fake_get_estados():
        return [{"sigla": "PE", "nome": "Pernambuco"}]

    monkeypatch.setattr(mod.ibge_service, "get_estados", fake_get_estados)

    result = await mod.get_estados()

    assert len(result) == 1
    assert result[0]["sigla"] == "PE"


async def test_get_estados_empty(monkeypatch):
    mod = load_module()

    async def fake_get_estados():
        return []

    monkeypatch.setattr(mod.ibge_service, "get_estados", fake_get_estados)

    with pytest.raises(HTTPException) as e:
        await mod.get_estados()

    assert e.value.status_code == 503


# ============================
# CIDADES POR ESTADO
# ============================
async def test_get_cidades_por_estado_success(monkeypatch):
    mod = load_module()

    async def fake_get_cidades(uf):
        return [{"id": 1, "nome": "Recife"}]

    monkeypatch.setattr(mod.ibge_service, "get_cidades_por_estado", fake_get_cidades)

    result = await mod.get_cidades_por_estado("PE")

    assert result[0]["nome"] == "Recife"


async def test_get_cidades_por_estado_invalid_uf():
    mod = load_module()

    with pytest.raises(HTTPException) as e:
        await mod.get_cidades_por_estado("PEX")

    assert e.value.status_code == 400


async def test_get_cidades_por_estado_not_found(monkeypatch):
    mod = load_module()

    async def fake_get_cidades(uf):
        return []

    monkeypatch.setattr(mod.ibge_service, "get_cidades_por_estado", fake_get_cidades)

    with pytest.raises(HTTPException) as e:
        await mod.get_cidades_por_estado("PE")

    assert e.value.status_code == 404


# ============================
# CEP POR PATH
# ============================
async def test_get_endereco_por_cep_success(monkeypatch):
    mod = load_module()

    async def fake_get_address(cep):
        return {
            "rua": "Rua Teste",
            "bairro": "Centro",
            "cidade": "Recife",
            "uf": "PE"
        }

    monkeypatch.setattr(mod.geocoding_service, "get_address_from_cep", fake_get_address)

    result = await mod.get_endereco_por_cep("50000-000")

    assert result.success is True
    assert result.data["cidade"] == "Recife"


async def test_get_endereco_por_cep_not_found(monkeypatch):
    mod = load_module()

    async def fake_get_address(cep):
        return None

    monkeypatch.setattr(mod.geocoding_service, "get_address_from_cep", fake_get_address)

    result = await mod.get_endereco_por_cep("50000-000")

    assert result.success is False
    assert "não encontrado" in result.error.lower()


async def test_get_endereco_por_cep_exception(monkeypatch):
    mod = load_module()

    async def fake_get_address(cep):
        raise RuntimeError("Falhou")

    monkeypatch.setattr(mod.geocoding_service, "get_address_from_cep", fake_get_address)

    result = await mod.get_endereco_por_cep("50000-000")

    assert result.success is False
    assert "erro ao buscar" in result.error.lower()


# ============================
# CEP POR QUERY: /cep?cep=...
# ============================
async def test_get_endereco_por_cep_query(monkeypatch):
    mod = load_module()

    async def fake_get_address(cep):
        return {
            "rua": "Rua Teste",
            "bairro": "Centro",
            "cidade": "Recife",
            "uf": "PE"
        }

    monkeypatch.setattr(mod.geocoding_service, "get_address_from_cep", fake_get_address)

    result = await mod.get_endereco_por_cep_query("50000-000")

    assert result.success is True
