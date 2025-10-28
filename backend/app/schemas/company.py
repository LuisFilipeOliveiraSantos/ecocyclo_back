from uuid import UUID
from pydantic import BaseModel, EmailStr, model_validator, field_validator, HttpUrl
from typing import Optional, Union, List
from datetime import datetime
from app.models.company import CompanyType, Companycolectortags

class CompanyBase(BaseModel):
    nome: str
    cnpj: str
    email: EmailStr
    telefone: str
    company_type: Union[CompanyType, str]
    company_description: Optional[str] = None
    company_photo_url: Optional[HttpUrl] = None
    
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
    company_colector_tags: Optional[List[Companycolectortags]] = None
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
    
    @model_validator(mode='after')
    def validate_coletora_tags(self):
        """Valida que empresas coletoras devem ter tags"""
        if (self.company_type == CompanyType.EMPRESA_COLETORA and 
            (not self.company_colector_tags or len(self.company_colector_tags) == 0)):
            raise ValueError("Empresas coletoras devem selecionar pelo menos uma tag")
        return self

class CompanyUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    company_description: Optional[str] = None
    company_colector_tags: Optional[List[Companycolectortags]] = None
    company_photo_url: Optional[HttpUrl] = None
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
    
    @model_validator(mode='after')
    def validate_coletora_tags(self):
        """Valida que empresas coletoras devem ter tags"""
        if (hasattr(self, 'company_type') and 
            self.company_type == CompanyType.EMPRESA_COLETORA and 
            self.company_colector_tags is not None and 
            len(self.company_colector_tags) == 0):
            raise ValueError("Empresas coletoras devem selecionar pelo menos uma tag")
        return self

class CompanyOut(CompanyBase):
    uuid: UUID
    company_colector_tags: Optional[List[Companycolectortags]] = None
    is_active: bool
    rating_average: float
    total_ratings: int
    total_points: int
    total_rewards_redeemed: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Schema para filtro de empresas no mapa
class CompanyMapFilter(BaseModel):
    tags: Optional[List[Companycolectortags]] = None
    city: Optional[str] = None
    uf: Optional[str] = None
    min_rating: Optional[float] = None

# Schema para resposta do mapa
class CompanyMapOut(BaseModel):
    uuid: UUID
    nome: str
    company_photo_url: Optional[HttpUrl] = None
    telefone: str
    company_description: str
    company_type: CompanyType
    company_colector_tags: Optional[List[Companycolectortags]] = None
    rating_average: float
    total_ratings: int
    bairro: str
    rua: str
    numero: str
    cidade: str
    uf: str

    class Config:
        from_attributes = True