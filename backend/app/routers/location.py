from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.services.locationIBGE_service import ibge_service
from app.services.geocoding_service import geocoding_service
from app.schemas.location import EstadoSchema, CidadeSchema, EnderecoCEPSchema, LocalizacaoResponse

router = APIRouter(prefix="/location", tags=["location"])

@router.get("/estados", response_model=List[EstadoSchema])
async def get_estados():
    """
    Retorna todos os estados do Brasil
    """
    try:
        estados = await ibge_service.get_estados()
        if not estados:
            raise HTTPException(status_code=503, detail="Serviço de estados indisponível")
        return estados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estados: {str(e)}")

@router.get("/estados/{uf}/cidades", response_model=List[CidadeSchema])
async def get_cidades_por_estado(uf: str):
    """
    Retorna todas as cidades de um estado específico
    """
    if len(uf) != 2:
        raise HTTPException(status_code=400, detail="UF deve ter 2 caracteres")
    
    try:
        cidades = await ibge_service.get_cidades_por_estado(uf)
        if not cidades:
            raise HTTPException(status_code=404, detail=f"Nenhuma cidade encontrada para {uf}")
        return cidades
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cidades: {str(e)}")

@router.get("/cep/{cep}", response_model=LocalizacaoResponse)
async def get_endereco_por_cep(cep: str):
    """
    Busca endereço completo a partir do CEP
    """
    try:
        endereco = await geocoding_service.get_address_from_cep(cep)
        
        if endereco:
            return LocalizacaoResponse(
                success=True,
                data=endereco
            )
        else:
            return LocalizacaoResponse(
                success=False,
                error="Endereço não encontrado para o CEP informado"
            )
            
    except Exception as e:
        return LocalizacaoResponse(
            success=False,
            error=f"Erro ao buscar endereço: {str(e)}"
        )

@router.get("/cep", response_model=LocalizacaoResponse)
async def get_endereco_por_cep_query(cep: str = Query(..., description="CEP no formato 00000-000 ou 00000000")):
    """
    Busca endereço completo a partir do CEP (usando query parameter)
    """
    return await get_endereco_por_cep(cep)