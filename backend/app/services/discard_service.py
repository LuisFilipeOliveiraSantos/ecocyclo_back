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
        """
        Busca descartes onde a empresa é solicitante OU solicitada
        """
        try:
            empresa_uuid = UUID(empresa_id)
            
            # Usando a sintaxe do MongoDB com $or
            discards = await Discard.find({
                "$or": [
                    {"empresa_solicitante_id": empresa_uuid},
                    {"empresa_solicitada_id": empresa_uuid}
                ]
            }).sort(-Discard.created_at).to_list()
            
            return discards
        except ValueError as e:
            raise ValueError(f"ID da empresa inválido: {empresa_id}")
        
    @staticmethod
    async def cancel_discard(discard_id: UUID) -> Discard:
        discard = await Discard.find_one(Discard.discard_id == discard_id)
        
        if not discard:
            raise ValueError("Descarte não encontrado")
        
        discard.status = DiscardStatus.CANCELADO
        await discard.save()
        return discard