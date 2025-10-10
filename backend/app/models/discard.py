from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime
from beanie import Document, Link
from pydantic import Field
from .company import Company
from .discard_item import DiscardItem

class DiscardStatus(str, Enum):
    PENDENTE = "pendente"
    COMPLETO = "completo"
    CANCELADO = "cancelado"
    CONFIRMADO = "confirmado"

class Discard(Document):
    discard_id: UUID = Field(default_factory=uuid4)
    data_descarte: datetime | None = None
    status: DiscardStatus = DiscardStatus.PENDENTE
    empresa_solicitante_id: Link[Company] 
    empresa_solicitada_id: Link[Company] 
    itens_descarte: list[Link[DiscardItem]] = []
    local_coleta: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "discards"
        indexes = [
            "discard_id",
            "empresa_solicitante_id",
            "empresa_solicitada_id",
        ]