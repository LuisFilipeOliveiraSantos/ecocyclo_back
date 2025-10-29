from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime
from beanie import Document, Link, PydanticObjectId
from pydantic import Field
from .company import Company


class DiscardStatus(str, Enum):
    PENDENTE = "pendente"
    COMPLETO = "completo"
    CANCELADO = "cancelado"
    CONFIRMADO = "confirmado"
    EM_ANDAMENTO = "Em andamento"

class Discard(Document):
    discard_id: UUID = Field(default_factory=uuid4)
    data_descarte: datetime | None = None
    status: DiscardStatus = DiscardStatus.PENDENTE
    empresa_solicitante_id: UUID
    empresa_solicitada_id: UUID
    itens_descarte: dict = Field(default_factory=dict)
    quantidade_total: int = Field(default=0)
    local_coleta: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "discards"
        indexes = [
            "discard_id",
            "empresa_solicitante_id",
            "empresa_solicitada_id",
        ]

