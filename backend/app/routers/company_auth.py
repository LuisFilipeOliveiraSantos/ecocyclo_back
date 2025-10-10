from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import models
from app.schemas.tokens import Token
from app.schemas.company import CompanyOut
from app.auth.auth_company import (
    authenticate_company,
    create_access_token_company,
    get_current_company,
    get_current_company_from_cookie,
    get_current_active_company,
)
from app.config.config import settings

router = APIRouter()

@router.post("/access-token", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login for companies.
    """
    company = await authenticate_company(form_data.username, form_data.password)
    if company is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not company.is_active:
        raise HTTPException(status_code=400, detail="Inactive company")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token_company(company.uuid, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/test-token", response_model=CompanyOut)
async def test_token(current_company: models.Company = Depends(get_current_active_company)):
    """
    Test access token
    """
    return current_company

@router.get("/refresh-token", response_model=Token)
async def refresh_token(current_company: models.Company = Depends(get_current_company_from_cookie)):
    """
    Return a new token for current company
    """
    if not current_company.is_active:
        raise HTTPException(status_code=400, detail="Inactive company")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token_company(current_company.uuid, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}