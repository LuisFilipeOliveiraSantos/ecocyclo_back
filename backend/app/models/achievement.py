from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field





class Achievement(Document):
    """Conquistas/badges que os usuários podem desbloquear"""
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    
    # Informações básicas
    title: str
    description: str
    empresa_id: UUID

    icon_url: str | None = None
    badge_color: str | None = None
    
    # Critérios
    criteria: dict = Field(default_factory=dict)  # Critérios flexíveis em JSON
    points_reward: int = 0  # Pontos ganhos ao conquistar
    
    # Configurações
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)