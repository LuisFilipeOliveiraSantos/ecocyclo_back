from typing import Any, List
from uuid import UUID

from beanie.exceptions import RevisionIdWasChanged
from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo import errors

from app import models
from app.schemas.company import CompanyOut, CompanyMapFilter, CompanyMapOut, CompanyMapSimpleOut
from app.auth.auth_company import (
    get_current_active_company,
    get_current_active_admin_company,
)
from app.services.geocoding_service import geocoding_service
from app.services.company_service import company_service

router = APIRouter()


@router.post("/map/filter", response_model=List[CompanyMapOut])
async def get_companies_for_map(
    filter_data: CompanyMapFilter,
    current_company: models.Company = Depends(get_current_active_company)
):
    """
    Get companies for map with filters
    """
    try:
        companies = await company_service.get_companies_for_map(filter_data)
        return companies
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tags/available", response_model=List[str])
async def get_available_tags(
    current_company: models.Company = Depends(get_current_active_company)
):
    """
    Get all available collector tags
    """
    return await company_service.get_available_tags()

@router.get("/map/coletoras", response_model=List[CompanyMapSimpleOut])
async def get_coletoras_for_map(
    tags: List[str] = Query(None, description="Filter by tags"),
    city: str = Query(None, description="Filter by city"),
    uf: str = Query(None, description="Filter by state"),
    min_rating: float = Query(None, ge=1, le=5, description="Minimum rating")
):
    """
    Get collector companies for map with query parameters
    """
    filter_data = CompanyMapFilter(
        tags=tags,
        city=city,
        uf=uf,
        min_rating=min_rating
    )
    
    try:
        companies = await company_service.get_companies_for_map_simple(filter_data)  # ← Use o novo método
        return companies
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))