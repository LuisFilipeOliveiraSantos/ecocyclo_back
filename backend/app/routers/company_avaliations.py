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
        print(f"🔍 DEBUG - Iniciando criação de avaliação:")
        print(f"   Current Company UUID: {current_company.uuid}")
        print(f"   Company UUID (avaliada): {avaliation_data.company_uuid}")
        print(f"   Discard UUID: {avaliation_data.discard_uuid}")
        print(f"   Score: {avaliation_data.score}")
        
        avaliation_dict = avaliation_data.model_dump()
        avaliation_dict['company_avaliadora_uuid'] = current_company.uuid
        
        print(f"📤 Dados para service: {avaliation_dict}")
        
       
        rating = await avaliation_service.create_avaliation(avaliation_dict)
        
        print(f"✅ Avaliação criada com sucesso: {rating.uuid}")
        
       
        return AvaliationOut.from_rating(rating)
        
    except Exception as e:
        print(f"❌ ERRO DETALHADO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        
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

    return AvaliationOut.from_rating(rating)



@router.get("/company/{company_uuid}", response_model=List[AvaliationOut])
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
        
        return [AvaliationOut.from_rating(rating) for rating in ratings]
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
       
        return [AvaliationOut.from_rating(rating) for rating in ratings]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/update", response_model=AvaliationOut)
async def update_avaliation(
    rating_uuid: UUID,
    update_data: AvaliationUpdate,
    current_company: Company = Depends(get_current_company)
):
    """
    Update an avaliation (only by the company that created it)
    """
    rating = await avaliation_service.get_avaliation_by_uuid(rating_uuid)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
    if rating.company_avaliadora_uuid != current_company.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this avaliation"
        )
    
    updated_rating = await avaliation_service.update_avaliation(
        rating_uuid, update_data.model_dump(exclude_unset=True)
    )
    
    if not updated_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
  
    return AvaliationOut.from_rating(updated_rating)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
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
    
    if rating.company_avaliadora_uuid != current_company.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this avaliation"
        )
    
    deleted = await avaliation_service.delete_avaliation(rating_uuid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliation not found"
        )
    
    return