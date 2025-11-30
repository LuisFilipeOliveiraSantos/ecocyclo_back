from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.item_reference import RiskLevel

class ItemReferenceCreate(BaseModel):
    nome: str = Field(..., example="laptop")
    valor_min: float = Field(..., example=25.0)
    valor_max: float = Field(..., example=40.0)
    co2: float = Field(..., example=15.0)
    agua: float = Field(..., example=500.0)
    energia: float = Field(..., example=120.0)
    reaproveitamento_min: float = Field(..., example=80)
    reaproveitamento_max: float = Field(..., example=90)
    risco: RiskLevel = Field(..., example=RiskLevel.ALTO)
    peso_medio_kg: float = Field(..., example=2.0)
    descricao: str = Field("", example="Notebook/Laptop")

class ItemReferenceUpdate(BaseModel):
    nome: Optional[str] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    co2: Optional[float] = None
    agua: Optional[float] = None
    energia: Optional[float] = None
    reaproveitamento_min: Optional[float] = None
    reaproveitamento_max: Optional[float] = None
    risco: Optional[RiskLevel] = None
    peso_medio_kg: Optional[float] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class ItemReferenceResponse(BaseModel):
    item_id: UUID
    nome: str
    valor_min: float
    valor_max: float
    valor_medio: float
    co2: float
    agua: float
    energia: float
    reaproveitamento_min: float
    reaproveitamento_max: float
    reaproveitamento_medio: float
    risco: RiskLevel
    peso_medio_kg: float
    descricao: str
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True