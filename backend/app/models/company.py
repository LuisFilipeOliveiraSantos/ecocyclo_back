from typing import Annotated, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field, EmailStr, model_validator, HttpUrl

class CompanyType(str, Enum):
    EMPRESA_COLETORA = "coletora"
    EMPRESA_DESCARTANTE = "descartante"

class Companycolectortags(str, Enum):
    Venda_de_material_reciclavel = "venda"
    Doacao_de_material_reciclavel = "doacao"
    Marketplace_de_material_reciclavel = "marketplace"
    Reuso_de_material_reciclavel = "reuso"


class Company(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    cnpj: Annotated[str, Indexed(unique=True)]
    email: Annotated[EmailStr, Indexed(unique=True)]
    nome: Annotated[str, Indexed(unique=True)]
    telefone: str
    hashed_password: str
    company_type: CompanyType
    company_description: Optional[str] = None
    company_colector_tags: Optional[List[Companycolectortags]] = None
    company_photo_url: Optional[HttpUrl] = None
   
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
    rating_average: float = 0.0  # médias de avaliações
    total_ratings: int = 0  # número total de avaliações recebidas
    total_points: int = 0
    total_rewards_redeemed: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @model_validator(mode='after')
    def validate_coletora_tags(self):
        """Valida que empresas coletoras devem ter tags"""
        if (self.company_type == CompanyType.EMPRESA_COLETORA and 
            (not self.company_colector_tags or len(self.company_colector_tags) == 0)):
            raise ValueError("Empresas coletoras devem selecionar pelo menos uma tag")
        return self
    
    def is_coletora(self) -> bool:
        return self.company_type == CompanyType.EMPRESA_COLETORA
    
    def is_descartante(self) -> bool:
        return self.company_type == CompanyType.EMPRESA_DESCARTANTE


    def is_coletora(self) -> bool:
        return self.company_type == CompanyType.EMPRESA_COLETORA
    
    def is_descartante(self) -> bool:
        return self.company_type == CompanyType.EMPRESA_DESCARTANTE

    async def update_rating_average(self):
        """Recalcula a média de avaliações da empresa com base nos Ratings existentes."""
        from app.models.rating import Rating

        # Buscar todas as avaliações associadas a esta empresa
        ratings = await Rating.find(Rating.company_uuid.id == self.id).to_list()

        if not ratings:
            self.rating_average = 0.0
            self.total_ratings = 0
        else:
            total_scores = sum(r.score for r in ratings)
            self.total_ratings = len(ratings)
            self.rating_average = round(total_scores / self.total_ratings, 2)  # arredondar p/ 2 casas

        self.updated_at = datetime.utcnow()
        await self.save()


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