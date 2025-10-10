from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import Enum
from beanie import Document, Indexed
from pydantic import Field


class MetricType(str, Enum):
    IMPACTO_AMBIENTAL = "impacto_ambiental"
    TAXA_RECICLAGEM = "taxa_reciclagem"
    VALOR_ECONOMICO = "valor_economico"



class Metrics(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    

    titulo: str
    descricao: str
    tipo_metrica: MetricType
    valor: float
    
    risco: str | None = None  
    
    taxa_reaproveitamento: float | None = None  # Em porcentagem
  
  
    
    # Timestamps
    reference_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)