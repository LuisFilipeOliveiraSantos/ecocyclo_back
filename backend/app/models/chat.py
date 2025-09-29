from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from app.models.company import Company
from app.models.discard import Discard
from beanie import Document, Indexed , Link
from pydantic import Field


class ChatStatus(str, Enum):
    ATIVO = "ativo"
    FINALIZADO = "finalizado"


class Chat(Document):
    """Chat simples entre duas empresas"""
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    
    # Empresas participantes (sempre 2)
    empresa1_uuid: Link["Company"]
    empresa2_uuid: Link["Company"]

    # Relacionado ao descarte (opcional)
    discard_uuid: Link["Discard"] | None = None

    # Status
    status: ChatStatus = ChatStatus.ATIVO
    
    # Última atividade
    last_message_at: datetime | None = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        indexes = [
            [("empresa1_uuid", 1), ("empresa2_uuid", 1)],  # Chat único entre empresas
            [("discard_uuid", 1)],
            [("status", 1)],
            [("last_message_at", -1)],
        ]