from typing import List, Optional
from uuid import UUID
from app.models.company import Company, CompanyType, Companycolectortags
from app.schemas.company import CompanyMapFilter, CompanyMapOut
from app.core.exceptions import NotFoundException

class CompanyService:
    
    @staticmethod
    async def get_companies_for_map(filter_data: CompanyMapFilter) -> List[CompanyMapOut]:
        """
        Busca empresas para exibição no mapa com filtros
        """
        query = {"is_active": True, "company_type": CompanyType.EMPRESA_COLETORA}
        
        # Filtro por tags
        if filter_data.tags:
            query["company_colector_tags"] = {"$in": filter_data.tags}
        
        # Filtro por cidade
        if filter_data.city:
            query["cidade"] = {"$regex": filter_data.city, "$options": "i"}
        
        # Filtro por UF
        if filter_data.uf:
            query["uf"] = filter_data.uf.upper()
        
        # Filtro por rating mínimo
        if filter_data.min_rating is not None:
            query["rating_average"] = {"$gte": filter_data.min_rating}
        
        companies = await Company.find(query).to_list()
        
        return [CompanyMapOut(
            uuid=company.uuid,
            nome=company.nome,
            company_type=company.company_type,
            company_colector_tags=company.company_colector_tags,
            latitude=company.latitude,
            longitude=company.longitude,
            rating_average=company.rating_average,
            total_ratings=company.total_ratings,
            cidade=company.cidade,
            uf=company.uf
        ) for company in companies if company.latitude and company.longitude]
    
    @staticmethod
    async def get_available_tags() -> List[str]:
        """
        Retorna todas as tags disponíveis
        """
        return [tag.value for tag in Companycolectortags]
    
    @staticmethod
    async def get_companies_by_tags(tags: List[Companycolectortags]) -> List[Company]:
        """
        Busca empresas coletoras por tags específicas
        """
        return await Company.find({
            "is_active": True,
            "company_type": CompanyType.EMPRESA_COLETORA,
            "company_colector_tags": {"$in": tags}
        }).to_list()
    
    @staticmethod
    async def update_company_tags(company_uuid: UUID, tags: List[Companycolectortags]) -> Company:
        """
        Atualiza as tags de uma empresa coletora
        """
        company = await Company.find_one({
            "uuid": company_uuid,
            "company_type": CompanyType.EMPRESA_COLETORA
        })
        
        if not company:
            raise NotFoundException("Empresa coletora não encontrada")
        
        if not tags:
            raise ValueError("Empresas coletoras devem ter pelo menos uma tag")
        
        company.company_colector_tags = tags
        await company.save()
        return company

company_service = CompanyService()