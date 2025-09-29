from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field


class Message(Document):
    """Mensagem simples no chat"""
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    
    # Referências
    chat_uuid: UUID
    sender_company_uuid: UUID
    
    # Conteúdo
    content: str
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        indexes = [
            [("chat_uuid", 1), ("created_at", -1)],
            [("sender_company_uuid", 1)],
        ]