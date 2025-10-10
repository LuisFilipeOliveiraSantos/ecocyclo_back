from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field





class RewardStatus(str, Enum):
    DISPONIVEL = "disponivel"
    RESGATADO = "resgatado"
    USADO = "usado"
    EXPIRADO = "expirado"


class Reward(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    
    # Informações básicas
    title: str
    description: str
    reward_status: RewardStatus 
    points_cost: int 
    
    # Valores e disponibilidade
    is_active: bool = True
    
    # Validade
    
    # Relacionamentos
    company_uuid: UUID  
  
    
  
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        indexes = [
            [("company_uuid", 1), ("is_active", 1)],  # Buscar recompensas ativas por empresa
            [("reward_type", 1)],
            [("points_cost", 1)],
            [("expiration_date", 1)],
        ]