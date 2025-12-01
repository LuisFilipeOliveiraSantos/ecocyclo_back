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
        try:
            empresa_uuid = UUID(empresa_id)
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
    
    # ADICIONE ESTE MÉTODO AQUI ↓
    @staticmethod
    async def update_discard(
        discard_id: UUID,
        update_data: DiscardCreate,
        new_status: DiscardStatus
    ) -> Discard:

        discard = await Discard.find_one(Discard.discard_id == discard_id)

        if not discard:
            raise ValueError("Descarte não encontrado")

        # Regras de negócio
        if discard.status == DiscardStatus.COMPLETO and new_status != DiscardStatus.COMPLETO:
            raise ValueError("Não é permitido alterar um descarte já finalizado")

        if discard.status == DiscardStatus.CANCELADO and new_status != DiscardStatus.CANCELADO:
            raise ValueError("Não é permitido reativar um descarte cancelado")

        # Converta os IDs string para UUID antes de atribuir
        discard.empresa_solicitante_id = UUID(update_data.empresa_solicitante_id)
        discard.empresa_solicitada_id = UUID(update_data.empresa_solicitada_id)
        discard.itens_descarte = update_data.itens_descarte
        discard.quantidade_total = update_data.quantidade_total
        discard.data_descarte = update_data.data_descarte
        discard.local_coleta = update_data.local_coleta
        discard.status = new_status

        await discard.save()
        return discard