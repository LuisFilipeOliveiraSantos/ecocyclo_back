import pytest
from uuid import UUID
from datetime import datetime
from types import SimpleNamespace
from fastapi import HTTPException

pytestmark = pytest.mark.asyncio

MODULE_PATH = "app.routers.discard_route"



def make_discard(**kwargs):
    base = {
        "id": "11111111-1111-1111-1111-111111111111",
        "empresa_solicitada_id": "empresaA",
        "empresa_solicitante_id": "empresaB",
        "itens_descarte": {"papel": 3},
        "quantidade_total": 3,
        "data_descarte": datetime.utcnow(),
        "local_coleta": "Rua X"
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


# =====================================
# POST /
# =====================================
async def test_create_discard_success(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    fake = make_discard()

    async def fake_create_discard(data):
        return fake

    monkeypatch.setattr(mod.DiscardService, "create_discard", fake_create_discard)

    from app.schemas.discard_schema import DiscardRequest

    payload = DiscardRequest(
        empresa_solicitada_id="empresaA",
        empresa_solicitante_id="empresaB",
        gemini_itens={"papel": 3},
        data_descarte=datetime.utcnow(),
        local_coleta="Rua Z"
    )

    result = await mod.create_discard(payload)

    assert result is fake
    assert result.quantidade_total == 3


async def test_create_discard_error(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_create_discard(data):
        raise RuntimeError("DB error")

    monkeypatch.setattr(mod.DiscardService, "create_discard", fake_create_discard)

    from app.schemas.discard_schema import DiscardRequest

    payload = DiscardRequest(
        empresa_solicitada_id="empresaA",
        empresa_solicitante_id="empresaB",
        gemini_itens={"papel": 3},
        data_descarte=datetime.utcnow(),
        local_coleta="Rua Z"
    )

    with pytest.raises(HTTPException) as e:
        await mod.create_discard(payload)

    assert e.value.status_code == 400
    assert "DB error" in e.value.detail


# =====================================
# GET /{discard_id}
# =====================================
async def test_get_discard_success(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    fake = make_discard()

    async def fake_get_discard_with_items(discard_id):
        return fake

    monkeypatch.setattr(mod.DiscardService, "get_discard_with_items", fake_get_discard_with_items)

    result = await mod.get_discard(UUID(fake.id))

    assert result is fake


async def test_get_discard_not_found(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_get_discard_with_items(discard_id):
        raise ValueError("Descarte não encontrado")

    monkeypatch.setattr(mod.DiscardService, "get_discard_with_items", fake_get_discard_with_items)

    with pytest.raises(HTTPException) as e:
        await mod.get_discard(UUID("11111111-1111-1111-1111-111111111111"))

    assert e.value.status_code == 404
    assert "não encontrado" in e.value.detail.lower()


# =====================================
# GET /company/{empresa_id}
# =====================================
async def test_get_company_discards_success(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    fake_list = [make_discard(id="1"), make_discard(id="2")]

    async def fake_get_discards_by_company(company_id):
        return fake_list

    monkeypatch.setattr(mod.DiscardService, "get_discards_by_company", fake_get_discards_by_company)

    result = await mod.get_company_discards("empresaA")

    assert len(result) == 2


async def test_get_company_discards_error(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_get_discards_by_company(company_id):
        raise RuntimeError("Falha inesperada")

    monkeypatch.setattr(mod.DiscardService, "get_discards_by_company", fake_get_discards_by_company)

    with pytest.raises(HTTPException) as e:
        await mod.get_company_discards("empresaA")

    assert e.value.status_code == 400
    assert "falha" in e.value.detail.lower()


# =====================================
# PUT /{discard_id}/cancel
# =====================================
async def test_cancel_discard_success(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    fake = make_discard()

    async def fake_cancel(discard_id):
        return fake

    monkeypatch.setattr(mod.DiscardService, "cancel_discard", fake_cancel)

    result = await mod.cancel_discard(UUID(fake.id))

    assert result is fake


async def test_cancel_discard_not_found(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_cancel(discard_id):
        raise ValueError("Descarte não existe")

    monkeypatch.setattr(mod.DiscardService, "cancel_discard", fake_cancel)

    with pytest.raises(HTTPException) as e:
        await mod.cancel_discard(UUID("11111111-1111-1111-1111-111111111111"))

    assert e.value.status_code == 404
    assert "não existe" in e.value.detail.lower()


async def test_cancel_discard_error(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_cancel(discard_id):
        raise RuntimeError("Erro DB")

    monkeypatch.setattr(mod.DiscardService, "cancel_discard", fake_cancel)

    with pytest.raises(HTTPException) as e:
        await mod.cancel_discard(UUID("11111111-1111-1111-1111-111111111111"))

    assert e.value.status_code == 400
    assert "erro db" in e.value.detail.lower()
