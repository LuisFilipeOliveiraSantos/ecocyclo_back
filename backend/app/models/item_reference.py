from uuid import UUID, uuid4
from datetime import datetime
from beanie import Document
from pydantic import Field
from enum import Enum

class RiskLevel(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"

class ItemReference(Document):
    item_id: UUID = Field(default_factory=uuid4)
    nome: str  # "laptop", "celular", etc.
    valor_min: float = Field(gt=0)
    valor_max: float = Field(gt=0)
    co2: float = Field(gt=0)  # kg de CO2 economizado por item
    agua: float = Field(gt=0)  # litros de água economizados por item
    energia: float = Field(gt=0)  # kWh economizados por item
    reaproveitamento_min: float = Field(ge=0, le=100)
    reaproveitamento_max: float = Field(ge=0, le=100)
    risco: RiskLevel
    peso_medio_kg: float = Field(gt=0)
    descricao: str = ""
    ativo: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "item_references"
        indexes = [
            "item_id",
            "nome",
            "ativo"
        ]
    
    @property
    def valor_medio(self) -> float:
        return (self.valor_min + self.valor_max) / 2
    
    @property
    def reaproveitamento_medio(self) -> float:
        return (self.reaproveitamento_min + self.reaproveitamento_max) / 2