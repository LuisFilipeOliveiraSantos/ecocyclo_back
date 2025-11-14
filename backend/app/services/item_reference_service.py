from uuid import UUID
from app.models.item_reference import ItemReference
from app.schemas.item_reference_schema import ItemReferenceCreate, ItemReferenceUpdate

class ItemReferenceService:
    
    @staticmethod
    async def create_item(item_data: ItemReferenceCreate) -> ItemReference:
        """Cria um novo item na tabela de referência"""
        # Verifica se já existe item com mesmo nome
        existing_item = await ItemReference.find_one(ItemReference.nome == item_data.nome)
        if existing_item:
            raise ValueError(f"Já existe um item com o nome '{item_data.nome}'")
        
        item = ItemReference(**item_data.dict())
        return await item.insert()
    
    @staticmethod
    async def get_item(item_id: UUID) -> ItemReference:
        """Busca um item por ID"""
        item = await ItemReference.find_one(ItemReference.item_id == item_id)
        if not item:
            raise ValueError("Item não encontrado")
        return item
    
    @staticmethod
    async def get_item_by_name(nome: str) -> ItemReference:
        """Busca um item por nome"""
        item = await ItemReference.find_one(ItemReference.nome == nome)
        if not item:
            raise ValueError(f"Item '{nome}' não encontrado")
        return item
    
    @staticmethod
    async def get_all_items(ativos: bool = True) -> list[ItemReference]:
        """Lista todos os itens (opcionalmente só os ativos)"""
        if ativos:
            return await ItemReference.find(ItemReference.ativo == True).to_list()
        return await ItemReference.find_all().to_list()
    
    @staticmethod
    async def update_item(item_id: UUID, update_data: ItemReferenceUpdate) -> ItemReference:
        """Atualiza um item"""
        item = await ItemReferenceService.get_item(item_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            await item.update({"$set": update_dict})
            # Recarrega o item atualizado
            item = await ItemReferenceService.get_item(item_id)
        
        return item
    
    @staticmethod
    async def delete_item(item_id: UUID) -> bool:
        """Deleta um item (soft delete)"""
        item = await ItemReferenceService.get_item(item_id)
        item.ativo = False
        await item.save()
        return True
    
    @staticmethod
    async def get_items_dict() -> dict:
        """Retorna os itens no formato de dicionário para compatibilidade"""
        items = await ItemReferenceService.get_all_items(ativos=True)
        
        items_dict = {}
        for item in items:
            items_dict[item.nome] = {
                "valor_min": item.valor_min,
                "valor_max": item.valor_max,
                "co2": item.co2,
                "agua": item.agua,
                "energia": item.energia,
                "reaproveitamento_min": item.reaproveitamento_min,
                "reaproveitamento_max": item.reaproveitamento_max,
                "risco": item.risco.value,
                "peso_medio_kg": item.peso_medio_kg
            }
        
        return items_dict