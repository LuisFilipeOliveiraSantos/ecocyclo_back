from typing import Any
from uuid import UUID

from beanie.exceptions import RevisionIdWasChanged
from fastapi import APIRouter, Depends, HTTPException
from pymongo import errors

from app import models
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.auth.auth_company import (
    get_hashed_password,
    get_current_active_company,
    get_current_active_admin_company,
)

router = APIRouter()

@router.post("", response_model=CompanyOut)
async def register_company(company: CompanyCreate):
    """
    Register a new company.
    """
    # Verificar se já existe company com esse email ou CNPJ
    existing_company = await models.Company.find_one({
        "$or": [
            {"email": company.email},
            {"cnpj": company.cnpj}
        ]
    })
    
    if existing_company:
        raise HTTPException(status_code=400, detail="Company with that email or CNPJ already exists")

    hashed_password = get_hashed_password(company.password)

    new_company = models.Company(
        cnpj=company.cnpj,
        email=company.email,
        telefone=company.telefone,
        hashed_password=hashed_password,
        company_type=company.company_type,
        cep=company.cep,
        rua=company.rua,
        numero=company.numero,
        bairro=company.bairro,
        cidade=company.cidade,
        uf=company.uf,
        complemento=company.complemento,
        referencia=company.referencia,
    )

    try:
        await new_company.create()
        return new_company
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Company with that email or CNPJ already exists")

@router.get("", response_model=list[CompanyOut])
async def get_companies(
    limit: int = 10,
    offset: int = 0,
    admin_company: models.Company = Depends(get_current_active_admin_company),
):
    companies = await models.Company.find_all().skip(offset).limit(limit).to_list()
    return companies

@router.get("/me", response_model=CompanyOut)
async def get_my_company(current_company: models.Company = Depends(get_current_active_company)):
    return current_company

@router.patch("/me", response_model=CompanyOut)
async def update_my_company(
    update: CompanyUpdate,
    current_company: models.Company = Depends(get_current_active_company),
) -> Any:
    """
    Update current company.
    """
    update_data = update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_hashed_password(update_data["password"])
        del update_data["password"]
        del update_data["confirm_password"]

    current_company = current_company.model_copy(update=update_data)
    try:
        await current_company.save()
        return current_company
    except (errors.DuplicateKeyError, RevisionIdWasChanged):
        raise HTTPException(status_code=400, detail="Company with that email or CNPJ already exists")

@router.delete("/me", response_model=CompanyOut)
async def delete_me(current_company: models.Company = Depends(get_current_active_company)):
    await current_company.delete()
    return current_company

@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: UUID,
    admin_company: models.Company = Depends(get_current_active_admin_company),
):
    company = await models.Company.find_one({"uuid": company_id})
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: UUID,
    update: CompanyUpdate,
    admin_company: models.Company = Depends(get_current_active_admin_company),
):
    company = await models.Company.find_one({"uuid": company_id})
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_hashed_password(update_data["password"])
        del update_data["password"]
        del update_data["confirm_password"]

    updated_company = company.model_copy(update=update_data)
    try:
        await updated_company.save()
        return updated_company
    except (errors.DuplicateKeyError, RevisionIdWasChanged):
        raise HTTPException(status_code=400, detail="Company with that email or CNPJ already exists")

@router.delete("/{company_id}", response_model=CompanyOut)
async def delete_company(
    company_id: UUID,
    admin_company: models.Company = Depends(get_current_active_admin_company),
):
    company = await models.Company.find_one({"uuid": company_id})
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    await company.delete()
    return company