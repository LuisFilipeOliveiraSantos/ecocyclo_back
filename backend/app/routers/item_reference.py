from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from app.schemas.item_reference_schema import (
    ItemReferenceCreate, 
    ItemReferenceUpdate, 
    ItemReferenceResponse
)
from app.services.item_reference_service import ItemReferenceService

router = APIRouter()

@router.post("/", response_model=ItemReferenceResponse)
async def criar_item(item_data: ItemReferenceCreate):
    """Cria um novo item na tabela de referência"""
    try:
        item = await ItemReferenceService.create_item(item_data)
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ItemReferenceResponse])
async def listar_itens(ativos: bool = True):
    """Lista todos os itens da tabela de referência"""
    items = await ItemReferenceService.get_all_items(ativos)
    return items

@router.get("/{item_id}", response_model=ItemReferenceResponse)
async def buscar_item(item_id: UUID):
    """Busca um item específico por ID"""
    try:
        item = await ItemReferenceService.get_item(item_id)
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/nome/{nome}", response_model=ItemReferenceResponse)
async def buscar_item_por_nome(nome: str):
    """Busca um item específico por nome"""
    try:
        item = await ItemReferenceService.get_item_by_name(nome)
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{item_id}", response_model=ItemReferenceResponse)
async def atualizar_item(item_id: UUID, update_data: ItemReferenceUpdate):
    """Atualiza um item da tabela de referência"""
    try:
        item = await ItemReferenceService.update_item(item_id, update_data)
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{item_id}")
async def deletar_item(item_id: UUID):
    """Deleta um item (soft delete)"""
    try:
        await ItemReferenceService.delete_item(item_id)
        return {"message": "Item deletado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/data/dict")
async def obter_dados_em_dict():
    """Retorna os dados em formato de dicionário para compatibilidade"""
    items_dict = await ItemReferenceService.get_items_dict()
    return items_dict