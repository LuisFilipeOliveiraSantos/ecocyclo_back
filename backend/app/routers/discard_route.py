from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
from app.schemas.discard_schema import DiscardCreate, DiscardRequest, DiscardResponse
from app.services.discard_service import DiscardService


router = APIRouter()

@router.post("/", response_model=DiscardResponse)
async def create_discard(request: DiscardRequest):
    try:
        discard_data = DiscardCreate(
            empresa_solicitada_id=request.empresa_solicitada_id,
            itens_descarte=request.gemini_itens, 
            quantidade_total=sum(request.gemini_itens.values()),
            data_descarte=request.data_descarte,
            local_coleta=request.local_coleta,
            empresa_solicitante_id = request.empresa_solicitante_id
        )        
        # Criar descarte
        discard = await DiscardService.create_discard(discard_data)
        
        return discard  
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao criar descarte: {str(e)}")
    
# Buscar descarte específico
@router.get("/{discard_id}", response_model=DiscardResponse)
async def get_discard(discard_id: UUID):
    try:
        discard = await DiscardService.get_discard_with_items(discard_id)
        return discard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Listar descartes de uma empresa
@router.get("/company/{empresa_id}", response_model=List[DiscardResponse])
async def get_company_discards(empresa_id: str):
    try:
        discards = await DiscardService.get_discards_by_company(empresa_id)
        return discards
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Cancelar descarte
@router.put("/{discard_id}/cancel", response_model=DiscardResponse)
async def cancel_discard(discard_id: UUID):
    try:
        discard = await DiscardService.cancel_discard(discard_id)
        return discard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
