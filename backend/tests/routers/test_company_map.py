import pytest
from types import SimpleNamespace
from app.schemas.company import CompanyMapFilter, CompanyMapOut, CompanyMapSimpleOut
from app.models.company import CompanyType
from fastapi import HTTPException

MODULE_PATH = "app.routers.map_filter_company"
pytestmark = pytest.mark.asyncio


def make_company(uuid="11111111-1111-1111-1111-111111111111"):
    return SimpleNamespace(uuid=uuid)


def make_company_map_out(name="Empresa X"):
    return CompanyMapOut(
        uuid="11111111-1111-1111-1111-111111111111",
        nome=name,
        company_photo_url=None,
        telefone="999999999",
        company_description="Descrição da empresa",
        company_type=CompanyType.EMPRESA_COLETORA,
        company_colector_tags=["venda"],
        rating_average=4.5,
        total_ratings=10,
        bairro="Centro",
        rua="Rua Teste",
        numero="123",
        cidade="Recife",
        uf="PE"
    )


def make_company_map_simple_out(name="Coletora Y"):
    return CompanyMapSimpleOut(
        uuid="22222222-2222-2222-2222-222222222222",
        nome=name,
        company_type=CompanyType.EMPRESA_COLETORA,
        company_colector_tags=["venda"],
        latitude=-8.10,
        longitude=-34.90,
        rating_average=4.0,
        total_ratings=5,
        cidade="Recife",
        uf="PE",
        company_photo_url=None,
        telefone="999999999",
        company_description="Descrição simples",
        bairro="Centro",
        rua="Rua Simples",
        numero="456"
    )


# ========================
# POST /map/filter
# ========================
async def test_get_companies_for_map(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])
    fake_company = make_company()
    fake_filter = CompanyMapFilter(tags=["venda"])

    async def fake_get_companies_for_map(filter_data):
        return [make_company_map_out()]

    monkeypatch.setattr(mod.company_service, "get_companies_for_map", fake_get_companies_for_map)
    monkeypatch.setattr(mod, "get_current_active_company", lambda: fake_company)

    result = await mod.get_companies_for_map(fake_filter, current_company=fake_company)
    assert len(result) == 1
    assert result[0].nome == "Empresa X"


# ========================
# GET /tags/available
# ========================
async def test_get_available_tags(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])
    fake_company = make_company()

    async def fake_get_available_tags():
        return ["venda", "reciclagem"]

    monkeypatch.setattr(mod.company_service, "get_available_tags", fake_get_available_tags)
    monkeypatch.setattr(mod, "get_current_active_company", lambda: fake_company)

    result = await mod.get_available_tags(current_company=fake_company)
    assert "venda" in result
    assert "reciclagem" in result


# ========================
# GET /map/coletoras
# ========================
async def test_get_coletoras_for_map(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_get_companies_for_map_simple(filter_data):
        return [make_company_map_simple_out()]

    monkeypatch.setattr(mod.company_service, "get_companies_for_map_simple", fake_get_companies_for_map_simple)

    result = await mod.get_coletoras_for_map(tags=["venda"], city="Recife", uf="PE", min_rating=4)
    assert len(result) == 1
    assert result[0].nome == "Coletora Y"
    assert result[0].rating_average == 4.0
