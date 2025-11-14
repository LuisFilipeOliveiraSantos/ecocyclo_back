import asyncio
import os
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar app
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.item_reference import ItemReference, RiskLevel
from app.config.config import settings

async def populate_initial_data():
    """Popula a tabela com os dados do seu ITEM_DATA"""
    
    print("🔗 Conectando ao MongoDB...")
    
    # Inicializa o Beanie (igual na main.py)
    client = AsyncIOMotorClient(settings.MONGO_HOST)
    await init_beanie(
        database=client[settings.MONGO_DB], 
        document_models=[ItemReference]
    )
    
    print("🌱 Populando tabela de itens de referência com seus dados...")
    
    # SEUS DADOS COMPLETOS
    ITEM_DATA = [
        {
            "nome": "laptop",
            "valor_min": 25.0,
            "valor_max": 40.0,
            "co2": 15.0,
            "agua": 500.0,
            "energia": 120.0,
            "reaproveitamento_min": 80,
            "reaproveitamento_max": 90,
            "risco": RiskLevel.ALTO,
            "peso_medio_kg": 2.0,
            "descricao": "Notebook/Laptop"
        },
        {
            "nome": "celular",
            "valor_min": 10.0,
            "valor_max": 25.0,
            "co2": 8.0,
            "agua": 300.0,
            "energia": 80.0,
            "reaproveitamento_min": 80,
            "reaproveitamento_max": 85,
            "risco": RiskLevel.ALTO,
            "peso_medio_kg": 0.2,
            "descricao": "Smartphone"
        },
        {
            "nome": "tablet",
            "valor_min": 15.0,
            "valor_max": 30.0,
            "co2": 10.0,
            "agua": 400.0,
            "energia": 100.0,
            "reaproveitamento_min": 75,
            "reaproveitamento_max": 85,
            "risco": RiskLevel.MEDIO,
            "peso_medio_kg": 0.6,
            "descricao": "Tablet"
        },
        {
            "nome": "monitor",
            "valor_min": 10.0,
            "valor_max": 20.0,
            "co2": 12.0,
            "agua": 600.0,
            "energia": 150.0,
            "reaproveitamento_min": 70,
            "reaproveitamento_max": 85,
            "risco": RiskLevel.ALTO,
            "peso_medio_kg": 4.0,
            "descricao": "Monitor LCD/LED"
        },
        {
            "nome": "teclado",
            "valor_min": 1.0,
            "valor_max": 3.0,
            "co2": 2.0,
            "agua": 100.0,
            "energia": 30.0,
            "reaproveitamento_min": 80,
            "reaproveitamento_max": 90,
            "risco": RiskLevel.BAIXO,
            "peso_medio_kg": 0.8,
            "descricao": "Teclado"
        },
        {
            "nome": "mouse",
            "valor_min": 1.0,
            "valor_max": 2.0,
            "co2": 1.5,
            "agua": 80.0,
            "energia": 25.0,
            "reaproveitamento_min": 75,
            "reaproveitamento_max": 85,
            "risco": RiskLevel.BAIXO,
            "peso_medio_kg": 0.1,
            "descricao": "Mouse"
        },
        {
            "nome": "headset",
            "valor_min": 1.0,
            "valor_max": 3.0,
            "co2": 2.5,
            "agua": 120.0,
            "energia": 35.0,
            "reaproveitamento_min": 70,
            "reaproveitamento_max": 80,
            "risco": RiskLevel.BAIXO,
            "peso_medio_kg": 0.3,
            "descricao": "Headset/Fone de ouvido"
        },
        {
            "nome": "cpu",
            "valor_min": 40.0,
            "valor_max": 70.0,
            "co2": 20.0,
            "agua": 800.0,
            "energia": 200.0,
            "reaproveitamento_min": 85,
            "reaproveitamento_max": 95,
            "risco": RiskLevel.MEDIO,
            "peso_medio_kg": 8.0,
            "descricao": "CPU/Gabinete completo"
        },
        {
            "nome": "placa_mae",
            "valor_min": 50.0,
            "valor_max": 120.0,
            "co2": 25.0,
            "agua": 1000.0,
            "energia": 250.0,
            "reaproveitamento_min": 90,
            "reaproveitamento_max": 95,
            "risco": RiskLevel.ALTO,
            "peso_medio_kg": 0.5,
            "descricao": "Placa-mãe"
        },
        {
            "nome": "controle_remoto",
            "valor_min": 2.0,
            "valor_max": 4.0,
            "co2": 1.0,
            "agua": 60.0,
            "energia": 20.0,
            "reaproveitamento_min": 70,
            "reaproveitamento_max": 80,
            "risco": RiskLevel.BAIXO,
            "peso_medio_kg": 0.1,
            "descricao": "Controle remoto"
        }
    ]
    
    created_count = 0
    for item_data in ITEM_DATA:
        try:
            # Verifica se já existe
            existing = await ItemReference.find_one(ItemReference.nome == item_data["nome"])
            if not existing:
                # Cria o item diretamente sem usar o service
                item = ItemReference(**item_data)
                await item.insert()
                created_count += 1
                print(f"   ✅ {item_data['nome']} criado")
            else:
                print(f"   ⚠️ {item_data['nome']} já existe")
        except Exception as e:
            print(f"   ❌ Erro ao criar {item_data['nome']}: {e}")
    
    print(f"🎉 {created_count} itens criados na tabela de referência!")
    
    # Mostra estatísticas
    total_items = await ItemReference.find_all().count()
    print(f"📊 Total de itens no banco: {total_items}")
    
    # Fecha a conexão
    client.close()
    print("🔌 Conexão com MongoDB fechada")

if __name__ == "__main__":
    asyncio.run(populate_initial_data())