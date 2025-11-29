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
        try:
            print(f"🛠️ SERVICE - Validando empresas e descarte...")
            
            
            company = await Company.find_one(Company.uuid == avaliation_data['company_uuid'])
            avaliadora_company = await Company.find_one(
                Company.uuid == avaliation_data['company_avaliadora_uuid']
            )
            discard = await Discard.find_one(Discard.discard_id == avaliation_data['discard_uuid'])
            
            if not company:
                raise NotFoundException(f"Company not found: {avaliation_data['company_uuid']}")
            if not avaliadora_company:
                raise NotFoundException(f"Avaliator company not found: {avaliation_data['company_avaliadora_uuid']}")
            if not discard:
                raise NotFoundException(f"Discard not found: {avaliation_data['discard_uuid']}")
            
            print(f"🔍 Verificando se já existe avaliação para este descarte...")
            existing_rating = await Rating.find_one(
                Rating.discard_uuid == avaliation_data['discard_uuid'] 
            )
            
            if existing_rating:
                raise ValidationException("Este descarte já foi avaliado")
            
            print(f"📝 Criando objeto Rating...")
          
            rating = Rating(
                score=avaliation_data['score'],
                comment=avaliation_data.get('comment', ''),
                discard_uuid=avaliation_data['discard_uuid'],  
                company_uuid=avaliation_data['company_uuid'],  
                company_avaliadora_uuid=avaliation_data['company_avaliadora_uuid']  
            )
            
            await rating.save()
            
            if company:
                await company.update_rating_average()
            
            print(f"✅ Rating criado com UUID: {rating.uuid}")
            return rating
            
        except Exception as e:
            print(f"💥 ERRO NO SERVICE: {str(e)}")
            raise e
    

    @staticmethod
    async def get_avaliation_by_uuid(rating_uuid: UUID) -> Optional[Rating]:
        rating = await Rating.find_one(Rating.uuid == rating_uuid)
        if rating:
            await rating.fetch_all_links()
        return rating

    @staticmethod
    async def get_company_avaliations(company_uuid: UUID, page: int = 1, limit: int = 10) -> List[Rating]:
        company = await Company.find_one(Company.uuid == company_uuid)
        if not company:
            raise NotFoundException("Company not found")
            
        skip = (page - 1) * limit
        ratings = await Rating.find(
            Rating.company_uuid.uuid == company_uuid
        ).sort(-Rating.created_at).skip(skip).limit(limit).to_list()
        
        for rating in ratings:
            await rating.fetch_all_links()
        
        return ratings
    
    @staticmethod
    async def get_company_avaliations(company_uuid: UUID, page: int = 1, limit: int = 10) -> List[Rating]:
        skip = (page - 1) * limit
        ratings = await Rating.find(
            Rating.company_uuid == company_uuid 
        ).sort(-Rating.created_at).skip(skip).limit(limit).to_list()
        
        return ratings
    

    @staticmethod
    async def get_avaliations_by_avaliadora(company_avaliadora_uuid: UUID, page: int = 1, limit: int = 10) -> List[Rating]:
        skip = (page - 1) * limit
        ratings = await Rating.find(
            Rating.company_avaliadora_uuid == company_avaliadora_uuid  
        ).sort(-Rating.created_at).skip(skip).limit(limit).to_list()
        
        return ratings
    
    @staticmethod
    async def update_avaliation(rating_uuid: UUID, update_data: dict) -> Optional[Rating]:
        rating = await Rating.find_one(Rating.uuid == rating_uuid)
        if not rating:
            return None
        
        if 'score' in update_data:
            rating.score = update_data['score']
        if 'comment' in update_data:
            rating.comment = update_data['comment']
        
        rating.updated_at = datetime.now(timezone.utc)
        await rating.save()
        
     
        company = await Company.find_one(Company.uuid == rating.company_avaliadora_uuid)
        if company:
            await company.update_rating_average()
        
        return rating
    
    @staticmethod
    async def delete_avaliation(rating_uuid: UUID) -> bool:
        rating = await Rating.find_one(Rating.uuid == rating_uuid)
        if not rating:
            return False
        
        
        company = await Company.find_one(Company.uuid == rating.company_avaliadora_uuid)
        
        await rating.delete()
        
        if company:
            await company.update_rating_average()
        
        return True
    
    @staticmethod
    async def get_company_summary(company_uuid: UUID) -> CompanyAvaliationsSummary:
        company = await Company.find_one(Company.uuid == company_uuid)
        if not company:
            raise NotFoundException("Company not found")
        
        # Busca direta por UUID!
        ratings = await Rating.find(Rating.company_uuid == company_uuid).to_list()
        
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

avaliation_service = AvaliationService()


# Bob