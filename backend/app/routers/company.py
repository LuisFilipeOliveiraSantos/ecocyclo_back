from typing import Any, List
from uuid import UUID

from beanie.exceptions import RevisionIdWasChanged
from fastapi import APIRouter, Depends, HTTPException
from pymongo import errors

from app import models
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut, CompanyMapFilter, CompanyMapOut
from app.auth.auth_company import (
    get_hashed_password,
    get_current_active_company,
    get_current_active_admin_company,
)
from app.services.geocoding_service import geocoding_service
from app.services.company_service import company_service

router = APIRouter()


@router.post("/register", response_model=CompanyOut)
async def register_company(company: CompanyCreate):
    """
    Register a new company.
    """
    # Verificar se já existe company com esse email ou CNPJ
    existing_company = await models.Company.find_one({
        "$or": [
            {"email": company.email},
            {"cnpj": company.cnpj},
            {"nome": company.nome}
        ]
    })
    
    if existing_company:
        raise HTTPException(status_code=400, detail="Company with that email or CNPJ already exists")

    hashed_password = get_hashed_password(company.password)

    new_company = models.Company(
        nome=company.nome,
        cnpj=company.cnpj,
        email=company.email,
        telefone=company.telefone,
        hashed_password=hashed_password,
        company_type=company.company_type,
        company_description=company.company_description,
        company_colector_tags=company.company_colector_tags,
        company_photo_url=company.company_photo_url,
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
        
        # Obter coordenadas após criar a company
        address_data = {
            'rua': company.rua,
            'numero': company.numero,
            'bairro': company.bairro,
            'cidade': company.cidade,
            'uf': company.uf
        }
        coordinates = await geocoding_service.get_coordinates_from_address(address_data)
        if coordinates:
            new_company.latitude, new_company.longitude = coordinates
            await new_company.save()
        
        return new_company
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Company with that email or CNPJ already exists")


@router.get("/", response_model=list[CompanyOut])
async def get_companies(
    limit: int = 10,
    offset: int = 0,
    admin_company: models.Company = Depends(get_current_active_admin_company),
):
    companies = await models.Company.find({"is_admin":False}).skip(offset).limit(limit).to_list()
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
    
    if "nome" in update_data and update_data["nome"] != current_company.nome:
        # Verificar se outro company já tem esse nome
        existing_company = await models.Company.find_one({
            "nome": update_data["nome"],
            "uuid": {"$ne": current_company.uuid}  # excluir a própria company
        })
        if existing_company:
            raise HTTPException(status_code=400, detail="Company with that name already exists")

    if "password" in update_data:
        update_data["hashed_password"] = get_hashed_password(update_data["password"])
        del update_data["password"]
        del update_data["confirm_password"]

        
    if "company_colector_tags" in update_data:
        # Empresa não coletaora não pode ter tags
        if not current_company.is_coletora():
            raise HTTPException(
                status_code=400, 
                detail="Apenas empresas coletoras podem definir tags"
            )
        
    tags = update_data["company_colector_tags"]
    if not tags or len(tags) == 0:
        raise HTTPException(
            status_code=400, 
            detail="Empresas coletoras devem selecionar pelo menos uma tag"
        )

    # Validar tags se for coletora
    if (current_company.is_coletora() and 
        "company_colector_tags" in update_data and 
        (not update_data["company_colector_tags"] or len(update_data["company_colector_tags"]) == 0)):
        raise HTTPException(
            status_code=400, 
            detail="Empresas coletoras devem selecionar pelo menos uma tag"
        )

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


@router.get("/id", response_model=CompanyMapOut)
async def get_company(
    company_id: UUID,
    admin_company: models.Company = Depends(get_current_active_company),
):
    company = await models.Company.find_one({"uuid": company_id})
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company



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

    
    if "nome" in update_data and update_data["nome"] != company.nome:
        existing_company = await models.Company.find_one({
            "nome": update_data["nome"],
            "uuid": {"$ne": company_id}
        })
        if existing_company:
            raise HTTPException(status_code=400, detail="Company with that name already exists")

    if "password" in update_data:
        update_data["hashed_password"] = get_hashed_password(update_data["password"])
        del update_data["password"]
        del update_data["confirm_password"]

    # Verificar se algum campo de endereço foi atualizado
    address_fields = ['rua', 'numero', 'bairro', 'cidade', 'uf', 'cep']
    address_updated = any(field in update_data for field in address_fields)
    
    updated_company = company.model_copy(update=update_data)
    
    try:
        await updated_company.save()
        
        # Se endereço foi atualizado, buscar novas coordenadas
        if address_updated:
            await updated_company.update_geolocation()
            
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
