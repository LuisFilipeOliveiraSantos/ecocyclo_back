from typing import Annotated, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field, EmailStr, model_validator

class CompanyType(str, Enum):
    EMPRESA_COLETORA = "coletora"
    EMPRESA_DESCARTANTE = "descartante"

class Company(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    cnpj: Annotated[str, Indexed(unique=True)]
    email: Annotated[EmailStr, Indexed(unique=True)]
    telefone: str
    hashed_password: str
    company_type: CompanyType
    
    # Endereço
    cep: str
    rua: str
    numero: str 
    bairro: str 
    cidade: str 
    uf: str 
    
    # Opcionais
    complemento: str | None = None
    referencia: str | None = None
    
    # Status e avaliação (valores padrão)
    is_active: bool = True
    rating_average: float = 0.0
    total_ratings: int = 0
    total_points: int = 0
    total_rewards_redeemed: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_coletora(self) -> bool:
        return self.company_type == CompanyType.EMPRESA_COLETORA
    
    def is_descartante(self) -> bool:
        return self.company_type == CompanyType.EMPRESA_DESCARTANTE

    class Settings:
        name = "companies"