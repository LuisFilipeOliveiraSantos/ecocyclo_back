from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from beanie import PydanticObjectId

from app.schemas.avaliations import (
    AvaliationCreate, 
    AvaliationOut, 
    AvaliationUpdate,
    CompanyAvaliationsSummary
)
from app.services.avaliation_service import avaliation_service
from app.auth.auth_company import get_current_company
from app.models.company import Company
router = APIRouter()

@router.post("/", response_model=AvaliationOut, status_code=status.HTTP_201_CREATED)
async def create_avaliation(
    avaliation_data: AvaliationCreate,
    current_company: Company = Depends(get_current_company)
):
    """
    Create a new avaliation
    """
    try:
        # A empresa autenticada deve ser a avaliadora
        avaliation_dict = avaliation_data.model_dump()
        avaliation_dict['company_avaliadora_uuid'] = current_company.uuid
        
        rating = await avaliation_service.create_avaliation(avaliation_dict)
        return rating
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{rating_uuid}", response_model=AvaliationOut)
async def get_avaliation(rating_uuid: UUID):
    """
    Get specific avaliation by UUID
    """
    rating = await avaliation_service.get_avaliation_by_uuid(rating_uuid)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    return rating

@router.get("/company/{company_uuid}/summary", response_model=CompanyAvaliationsSummary)
async def get_company_avaliations_summary(company_uuid: UUID):
    """
    Get summary of avaliations for a company
    """
    try:
        summary = await avaliation_service.get_company_summary(company_uuid)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/company/{company_uuid}/avaliations", response_model=List[AvaliationOut])
async def get_company_avaliations(
    company_uuid: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all avaliations for a company with pagination
    """
    try:
        ratings = await avaliation_service.get_company_avaliations(company_uuid, page, limit)
        return ratings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/my/avaliations", response_model=List[AvaliationOut])
async def get_my_avaliations(
    current_company: Company = Depends(get_current_company),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get avaliations made by current company
    """
    try:
        ratings = await avaliation_service.get_avaliations_by_avaliadora(
            current_company.uuid, page, limit
        )
        return ratings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{rating_uuid}", response_model=AvaliationOut)  # ✅ MUDADO PARA PATCH
async def update_avaliation(
    rating_uuid: UUID,
    update_data: AvaliationUpdate,
    current_company: Company = Depends(get_current_company)
):
    """
    Update an avaliation (only by the company that created it)
    
    Partial update - send only the fields you want to change.
    Example: {"comment": "Novo comentário"} or {"score": 4}
    """
    # Verificar se a avaliação pertence à empresa autenticada
    rating = await avaliation_service.get_avaliation_by_uuid(rating_uuid)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
    if rating.company_avaliadora_uuid.uuid != current_company.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this avaliation"
        )
    
    # Usar exclude_unset=True para PATCH (só atualiza campos enviados)
    updated_rating = await avaliation_service.update_avaliation(
        rating_uuid, update_data.model_dump(exclude_unset=True)
    )
    
    if not updated_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
    return updated_rating

@router.delete("/{rating_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avaliation(
    rating_uuid: UUID,
    current_company: Company = Depends(get_current_company)
):
    """
    Delete an avaliation (only by the company that created it)
    """
    rating = await avaliation_service.get_avaliation_by_uuid(rating_uuid)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
    if rating.company_avaliadora_uuid.uuid != current_company.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this avaliation"
        )
    
    success = await avaliation_service.delete_avaliation(rating_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
    return None