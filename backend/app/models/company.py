from typing import Annotated, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field, EmailStr, field_validator





class Company(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    razao_social: str
    cnpj: Annotated[str, Indexed(unique=True)] | None = None
    email: EmailStr | None = None
    telefone: str | None = None
    hashed_password: str | None = None
    
    # Endereço
    cep: str
    rua: str
    numero: str 
    complemento: str | None = None
    bairro: str 
    cidade: str 
    uf: str 
    referencia: str | None = None
    
    
    horario_funcionamento: str | None = None
    
    materiais_aceitos: List[str] | None = None  
    capacidade_max: int | None = None 
    
    # Status e avaliação
    is_active: bool = True
    rating_average: float = 0.0
    total_ratings: int = 0
    total_points: int = 0  # Pontos acumulados pela empresa
    
   
    total_rewards_redeemed: int = 0  # Total de recompensas resgatadas
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('materiais_aceitos')
    @classmethod
    def validate_materiais_aceitos(cls, v, info):
        """Valida que apenas empresas coletoras podem ter materiais aceitos"""
        if v is not None and info.data.get('company_type') != CompanyType.EMPRESA_COLETORA:
            raise ValueError('Apenas empresas coletoras podem ter materiais aceitos')
        return v
    
    @field_validator('capacidade_max')
    @classmethod  
    def validate_capacidade_max(cls, v, info):
        """Valida que apenas empresas coletoras podem ter capacidade máxima"""
        if v is not None and info.data.get('company_type') != CompanyType.EMPRESA_COLETORA:
            raise ValueError('Apenas empresas coletoras podem ter capacidade máxima')
        return v
    
    @field_validator('horario_funcionamento')
    @classmethod
    def validate_horario_funcionamento(cls, v, info):
        """Valida que apenas empresas coletoras podem ter horário de funcionamento"""
        if v is not None and info.data.get('company_type') != CompanyType.EMPRESA_COLETORA:
            raise ValueError('Apenas empresas coletoras podem ter horário de funcionamento')
        return v
  
    
    def is_coletora(self) -> bool:
        """Retorna True se a empresa é coletora"""
        return self.company_type == CompanyType.EMPRESA_COLETORA
    
    def is_descartante(self) -> bool:
        """Retorna True se a empresa é descartante"""
        return self.company_type == CompanyType.EMPRESA_DESCARTANTE
    
    def can_offer_rewards(self) -> bool:
        """Retorna True se a empresa pode oferecer recompensas"""
        return self.is_active
    
    def get_reward_stats(self) -> dict:
        """Retorna estatísticas de recompensas da empresa"""
        return {
            "total_redeemed": self.total_rewards_redeemed,
        }
