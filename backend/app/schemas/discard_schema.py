from uuid import UUID
from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel


class DiscardCreate(BaseModel):
    empresa_solicitada_id: str
    itens_descarte: dict
    quantidade_total: int  # Soma de todas as quantidades
    data_descarte: datetime
    local_coleta: str | None = None
    empresa_solicitante_id: str
    
class DiscardRequest(BaseModel):
    gemini_itens: dict
    empresa_solicitada_id: str
    data_descarte: datetime
    empresa_solicitante_id: str
    local_coleta: str | None = None

class DiscardResponse(BaseModel):
    discard_id: UUID
    data_descarte: datetime
    status: str
    empresa_solicitante_id: PydanticObjectId
    empresa_solicitada_id: PydanticObjectId
    itens_descarte: dict
    quantidade_total: int
    local_coleta: str | None
    created_at: datetime

    class Config:
        from_attributes = True