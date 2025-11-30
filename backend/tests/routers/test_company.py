from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.asyncio

MODULE_PATH = "app.routers.company"

def make_company(**kwargs):
    base = {
        "uuid": "11111111-1111-1111-1111-111111111111",
        "email": "empresa@empresa.com",
        "cnpj": "96.534.094/0001-58",
        "nome": "Eco Teste",
        "is_admin": False,
        "company_type": "coletora",
        "company_colector_tags": ["marketplace"],
        "is_active": True,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


# ========================
#  TESTE REGISTRO
# ========================
async def test_register_company_success(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_find_one(query):
        return None

    async def fake_create(self):
        return self

    async def fake_save(self):
        return self

    async def fake_get_coords(address):
        return (-8.05, -34.9)

    monkeypatch.setattr(mod.models.Company, "find_one", fake_find_one)
    monkeypatch.setattr(mod.models.Company, "create", fake_create)
    monkeypatch.setattr(mod.models.Company, "save", fake_save)
    monkeypatch.setattr(mod.geocoding_service, "get_coordinates_from_address", fake_get_coords)

    from app.schemas.company import CompanyCreate
    payload = CompanyCreate(
        nome="Eco",
        cnpj="96.534.094/0001-58",
        email="eco@mail.com",
        telefone="9999",
        password="123",
        confirm_password="123",
        company_type="coletora",
        company_colector_tags=["venda"],
        company_description="Desc",
        company_photo_url=None,
        cep="50000-000",
        rua="Rua X",
        numero="10",
        bairro="Centro",
        cidade="Recife",
        uf="PE",
        complemento=None,
        referencia=None
    )

    result = await mod.register_company(payload)
    assert result.nome == "Eco"
    assert result.cnpj == "96.534.094/0001-58"
    assert result.latitude == -8.05
    assert result.longitude == -34.9



# ========================
#  GET /ME
# ========================
async def test_get_my_company(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])
    fake = make_company()

    async def fake_dep():
        return fake

    monkeypatch.setattr(mod, "get_current_active_company", fake_dep)

    result = await mod.get_my_company(fake)
    assert result is fake


# ========================
# GET COMPANIES (ADMIN ONLY)
# ========================
async def test_get_companies(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])

    fake_list = [make_company(nome="A"), make_company(nome="B")]

    def fake_find(query):
        class Q:
            def skip(self, n):
                return self
            def limit(self, n):
                return self
            async def to_list(self):
                return fake_list
        return Q()

    async def fake_admin():
        return make_company(is_admin=True)

    monkeypatch.setattr(mod.models.Company, "find", fake_find)
    monkeypatch.setattr(mod, "get_current_active_admin_company", fake_admin)

    result = await mod.get_companies(admin_company=fake_admin())
    assert len(result) == 2


# ========================
# DELETE /ME
# ========================
async def test_delete_me(monkeypatch):
    mod = __import__(MODULE_PATH, fromlist=["*"])
    fake = make_company()

    async def fake_delete(self):
        return True

    monkeypatch.setattr(mod.models.Company, "delete", fake_delete)

    result = await mod.delete_me(fake)
    assert result is fake



