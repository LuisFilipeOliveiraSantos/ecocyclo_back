from typing import Annotated, List, Optional
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
    nome: Annotated[str, Indexed(unique=True)]
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
    
    # Geolocalização
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Status e avaliação (valores padrão)
    is_active: bool = True
    is_admin: bool = False  
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

    async def update_geolocation(self):
        """Atualiza as coordenadas de geolocalização"""
        from app.services.geocoding_service import geocoding_service
        
        address_data = {
            'rua': self.rua,
            'numero': self.numero,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf
        }
        
        coordinates = await geocoding_service.get_coordinates_from_address(address_data)
        if coordinates:
            self.latitude, self.longitude = coordinates
            await self.save()

    class Settings:
        name = "companies"