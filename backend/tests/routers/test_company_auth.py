import pytest
import asyncio
from datetime import timedelta
from types import SimpleNamespace
from fastapi import HTTPException


MODULE_PATH = "app.routers.company_auth"

pytestmark = pytest.mark.asyncio



def make_company(uuid="11111111-1111-1111-1111-111111111111", is_active=True):
    """Objeto simples com os atributos usados nos endpoints."""
    return SimpleNamespace(uuid=uuid, is_active=is_active)


# --- Testes ---
async def test_login_access_token_success(monkeypatch):
    """
    Caso feliz: authenticate_company retorna company ativo e create_access_token_company
    retorna token. login_access_token deve devolver dict com access_token e token_type.
    """
  
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_authenticate_company(username, password):
        return make_company()

    def fake_create_access_token_company(uuid, expires_delta=None):
        # verificar que expires_delta é um timedelta
        assert isinstance(expires_delta, timedelta)
        return "fake-company-token"

    monkeypatch.setattr(mod, "authenticate_company", fake_authenticate_company)
    monkeypatch.setattr(mod, "create_access_token_company", fake_create_access_token_company)

    from fastapi.security import OAuth2PasswordRequestForm

    form = OAuth2PasswordRequestForm(username="any", password="any", scope="", grant_type="", client_id=None, client_secret=None)

    result = await mod.login_access_token(form)
    assert isinstance(result, dict)
    assert result["access_token"] == "fake-company-token"
    assert result["token_type"] == "bearer"


async def test_login_access_token_incorrect_credentials(monkeypatch):
    """
    authenticate_company retorna None -> deve lançar HTTPException status_code=400
    """
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_authenticate_company(username, password):
        return None

    monkeypatch.setattr(mod, "authenticate_company", fake_authenticate_company)

    from fastapi.security import OAuth2PasswordRequestForm

    form = OAuth2PasswordRequestForm(username="bad", password="bad", scope="", grant_type="", client_id=None, client_secret=None)

    with pytest.raises(HTTPException) as excinfo:
        await mod.login_access_token(form)
    assert excinfo.value.status_code == 400
    assert "Incorrect" in str(excinfo.value.detail) or "email" in str(excinfo.value.detail)


async def test_login_access_token_inactive_company(monkeypatch):
    """
    authenticate_company retorna company com is_active=False -> HTTPException 400 (Inactive company)
    """
    mod = __import__(MODULE_PATH, fromlist=["*"])

    async def fake_authenticate_company(username, password):
        return make_company(is_active=False)

    monkeypatch.setattr(mod, "authenticate_company", fake_authenticate_company)

    from fastapi.security import OAuth2PasswordRequestForm

    form = OAuth2PasswordRequestForm(username="any", password="any", scope="", grant_type="", client_id=None, client_secret=None)

    with pytest.raises(HTTPException) as excinfo:
        await mod.login_access_token(form)
    assert excinfo.value.status_code == 400
    assert "Inactive" in str(excinfo.value.detail)


async def test_test_token_returns_company_direct_call():
    """
    Chamando test_token passando explicitamente um objeto company (já que é um dependency),
    deve retornar o mesmo objeto (ou mapeamento compatível com CompanyOut).
    """
    mod = __import__(MODULE_PATH, fromlist=["*"])
    fake = make_company()
    returned = await mod.test_token(fake)
   
    assert returned is fake


async def test_refresh_token_success_and_inactive(monkeypatch):
    """
    Verifica refresh_token para company ativa (retorna token) e inativa (lança HTTPException).
    A dependência get_current_company_from_cookie é substituída por uma função que retorna o company.
    """
    mod = __import__(MODULE_PATH, fromlist=["*"])

    # Caso sucesso
    async def fake_get_current_company_from_cookie_active():
        return make_company()

    def fake_create_access_token_company(uuid, expires_delta=None):
        assert isinstance(expires_delta, timedelta)
        return "new-refresh-token"

    monkeypatch.setattr(mod, "get_current_company_from_cookie", fake_get_current_company_from_cookie_active)
    monkeypatch.setattr(mod, "create_access_token_company", fake_create_access_token_company)

    result = await mod.refresh_token() 
    assert isinstance(result, dict)
    assert result["access_token"] == "new-refresh-token"
    assert result["token_type"] == "bearer"

  
    async def fake_get_current_company_from_cookie_inactive():
        return make_company(is_active=False)

    monkeypatch.setattr(mod, "get_current_company_from_cookie", fake_get_current_company_from_cookie_inactive)
    with pytest.raises(HTTPException) as excinfo:
        await mod.refresh_token()
    assert excinfo.value.status_code == 400
    assert "Inactive" in str(excinfo.value.detail)



