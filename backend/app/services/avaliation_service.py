from uuid import UUID
from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime, timezone
from app.models.rating import Rating
from app.models.company import Company
from app.models.discard import Discard
from app.schemas.avaliations import CompanyAvaliationsSummary
from app.core.exceptions import NotFoundException, ValidationException

class AvaliationService:
    
    @staticmethod
    async def create_avaliation(avaliation_data: dict) -> Rating:
        # Verificar se as empresas existem
        company = await Company.find_one(Company.uuid == avaliation_data['company_uuid'])
        avaliadora_company = await Company.find_one(Company.uuid == avaliation_data['company_avaliadora_uuid'])
        discard = await Discard.find_one(Discard.uuid == avaliation_data['discard_uuid'])
        
        if not company or not avaliadora_company or not discard:
            raise NotFoundException("Company or discard not found")
        
        # Verificar se já existe avaliação para este descarte
        existing_rating = await Rating.find_one(
            Rating.discard_uuid.id == discard.id
        )
        
        if existing_rating:
            raise ValidationException("This discard has already been rated")
        
        # Criar a avaliação
        rating = Rating(
            score=avaliation_data['score'],
            comment=avaliation_data.get('comment'),
            discard_uuid=discard,
            company_uuid=company,
            company_avaliadora_uuid=avaliadora_company
        )
        
        await rating.insert()
        
        # Atualizar a média de avaliações da empresa
        await company.update_rating_average()
        
        return rating
    
    @staticmethod
    async def get_avaliation_by_uuid(rating_uuid: UUID) -> Optional[Rating]:
        return await Rating.find_one(Rating.uuid == rating_uuid)
    
    @staticmethod
    async def get_company_avaliations(company_uuid: UUID, page: int = 1, limit: int = 10) -> List[Rating]:
        company = await Company.find_one(Company.uuid == company_uuid)
        if not company:
            raise NotFoundException("Company not found")
            
        skip = (page - 1) * limit
        ratings = await Rating.find(
            Rating.company_uuid.id == company.id
        ).sort(-Rating.created_at).skip(skip).limit(limit).to_list()
        
        return ratings
    
    @staticmethod
    async def get_avaliations_by_avaliadora(company_avaliadora_uuid: UUID, page: int = 1, limit: int = 10) -> List[Rating]:
        company = await Company.find_one(Company.uuid == company_avaliadora_uuid)
        if not company:
            raise NotFoundException("Company not found")
            
        skip = (page - 1) * limit
        ratings = await Rating.find(
            Rating.company_avaliadora_uuid.id == company.id
        ).sort(-Rating.created_at).skip(skip).limit(limit).to_list()
        
        return ratings
    
    @staticmethod
    async def update_avaliation(rating_uuid: UUID, update_data: dict) -> Optional[Rating]:
        rating = await Rating.find_one(Rating.uuid == rating_uuid)
        if not rating:
            return None
        
        # Atualizar campos permitidos
        if 'score' in update_data:
            rating.score = update_data['score']
        if 'comment' in update_data:
            rating.comment = update_data['comment']
        
        rating.updated_at = datetime.now(timezone.utc)
        await rating.save()
        
        # Atualizar média da empresa
        company = await Company.get(rating.company_uuid.id)
        if company:
            await company.update_rating_average()
        
        return rating
    
    @staticmethod
    async def delete_avaliation(rating_uuid: UUID) -> bool:
        rating = await Rating.find_one(Rating.uuid == rating_uuid)
        if not rating:
            return False
        
        company_id = rating.company_uuid.id
        
        await rating.delete()
        
        # Atualizar média da empresa
        company = await Company.get(company_id)
        if company:
            await company.update_rating_average()
        
        return True
    
    @staticmethod
    async def get_company_summary(company_uuid: UUID) -> CompanyAvaliationsSummary:
        company = await Company.find_one(Company.uuid == company_uuid)
        if not company:
            raise NotFoundException("Company not found")
        
        # Buscar todas as avaliações da empresa
        ratings = await Rating.find(Rating.company_uuid.id == company.id).to_list()
        
        # Calcular distribuição de notas
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            distribution[rating.score] += 1
        
        return CompanyAvaliationsSummary(
            company_uuid=company_uuid,
            company_name=company.nome,
            company_type=company.company_type,
            average_rating=company.rating_average,
            total_ratings=company.total_ratings,
            rating_distribution=distribution
        )
    
    @staticmethod
    async def get_average_rating(company_uuid: UUID) -> Optional[float]:
        company = await Company.find_one(Company.uuid == company_uuid)
        return company.rating_average if company else None

avaliation_service = AvaliationService()