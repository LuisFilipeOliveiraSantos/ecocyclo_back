from uuid import UUID
from datetime import datetime
from beanie import PydanticObjectId
from app.models.discard import Discard, DiscardStatus
from app.schemas.discard_schema import DiscardCreate


class DiscardService:
    
    @staticmethod
    async def create_discard(discard_data: DiscardCreate) -> Discard:



        
        discard = Discard(
            empresa_solicitante_id=discard_data.empresa_solicitante_id,
            empresa_solicitada_id=discard_data.empresa_solicitada_id,
            itens_descarte=discard_data.itens_descarte,
            quantidade_total=discard_data.quantidade_total,
            data_descarte=discard_data.data_descarte,
            local_coleta=discard_data.local_coleta,
            status=DiscardStatus.CONFIRMADO
        )
        
        return await discard.insert()
    
    @staticmethod
    async def get_discard_with_items(discard_id: UUID) -> Discard:
        discard = await Discard.find_one(Discard.discard_id == discard_id)
        
        if not discard:
            raise ValueError("Descarte não encontrado")
            
        return discard
    
    @staticmethod
    async def get_discards_by_company(empresa_id: str) -> list[Discard]:
        empresa_object_id = PydanticObjectId(empresa_id)
        
        discards = await Discard.find(
            Discard.empresa_solicitante_id == empresa_object_id
        ).to_list()
        
        return discards
    
    @staticmethod
    async def cancel_discard(discard_id: UUID) -> Discard:
        discard = await Discard.find_one(Discard.discard_id == discard_id)
        
        if not discard:
            raise ValueError("Descarte não encontrado")
        
        discard.status = DiscardStatus.CANCELADO
        await discard.save()
        return discard