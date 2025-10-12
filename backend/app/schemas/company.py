from uuid import UUID
from pydantic import BaseModel, EmailStr, model_validator, field_validator
from typing import Optional, Union
from datetime import datetime
from app.models.company import CompanyType

class CompanyBase(BaseModel):
    nome: str
    cnpj: str
    email: EmailStr
    telefone: str
    company_type: Union[CompanyType, str]
    
    # Endereço
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    
    # Opcionais
    complemento: Optional[str] = None
    referencia: Optional[str] = None

    @field_validator('company_type')
    @classmethod
    def validate_company_type(cls, v):
        if isinstance(v, str):
            try:
                return CompanyType(v)
            except ValueError:
                raise ValueError(f"company_type must be one of: {[e.value for e in CompanyType]}")
        return v

class CompanyCreate(CompanyBase):
    password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

class CompanyUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    
    # Endereço
    cep: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    complemento: Optional[str] = None
    referencia: Optional[str] = None
    
    # Status
    is_active: Optional[bool] = None
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password and self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

class CompanyOut(CompanyBase):
    uuid: UUID
    is_active: bool
    rating_average: float
    total_ratings: int
    total_points: int
    total_rewards_redeemed: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


