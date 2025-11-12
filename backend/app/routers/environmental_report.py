from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.environmental_report import EnvironmentalReport, ElectronicItem

router = APIRouter()

# Dados de referência SIMPLES
ITEM_DATA = {
    "laptop": {"valor": 32.5, "co2": 15.0, "agua": 500.0, "energia": 120.0},
    "celular": {"valor": 17.5, "co2": 8.0, "agua": 300.0, "energia": 80.0},
    "tablet": {"valor": 22.5, "co2": 10.0, "agua": 400.0, "energia": 100.0},
    "monitor": {"valor": 15.0, "co2": 12.0, "agua": 600.0, "energia": 150.0},
    "teclado": {"valor": 2.0, "co2": 2.0, "agua": 100.0, "energia": 30.0},
    "mouse": {"valor": 1.5, "co2": 1.5, "agua": 80.0, "energia": 25.0},
    "headset": {"valor": 2.0, "co2": 2.5, "agua": 120.0, "energia": 35.0},
    "cpu": {"valor": 55.0, "co2": 20.0, "agua": 800.0, "energia": 200.0},
    "placa_mae": {"valor": 85.0, "co2": 25.0, "agua": 1000.0, "energia": 250.0},
    "controle_remoto": {"valor": 3.0, "co2": 1.0, "agua": 60.0, "energia": 20.0},
}


@router.post("/")
async def criar_relatorio(dados: dict):
    """Cria relatório ambiental"""
    try:
        # Calcular totais
        total_itens = sum(dados["itens_processados"].values())
        receita_total = 0
        co2_total = 0
        agua_total = 0
        energia_total = 0
        
        for item, quantidade in dados["itens_processados"].items():
            if item in ITEM_DATA:
                receita_total += ITEM_DATA[item]["valor"] * quantidade
                co2_total += ITEM_DATA[item]["co2"] * quantidade
                agua_total += ITEM_DATA[item]["agua"] * quantidade
                energia_total += ITEM_DATA[item]["energia"] * quantidade
        
        # Criar relatório
        relatorio = EnvironmentalReport(
            empresa_id=dados["empresa_id"],
            periodo_inicio=dados["periodo_inicio"],
            periodo_fim=dados["periodo_fim"],
            itens_processados=dados["itens_processados"],
            total_itens=total_itens,
            receita_total_estimada=receita_total,
            co2_economizado_kg=co2_total,
            agua_economizada_l=agua_total,
            energia_economizada_kwh=energia_total
        )
        
        await relatorio.insert()
        return {"message": "Relatório criado!", "report_id": relatorio.report_id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro: {str(e)}")


@router.get("/")
async def listar_relatorios(empresa_id: UUID):
    """Lista relatórios de uma empresa"""
    relatorios = await EnvironmentalReport.find(
        EnvironmentalReport.empresa_id == empresa_id
    ).to_list()
    
    return relatorios


@router.get("/{report_id}")
async def buscar_relatorio(report_id: UUID):
    """Busca relatório específico"""
    relatorio = await EnvironmentalReport.find_one(
        EnvironmentalReport.report_id == report_id
    )
    
    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    
    return relatorio


@router.get("/info/itens")
async def itens_disponiveis():
    """Mostra itens disponíveis e seus valores"""
    return {
        "itens_disponiveis": list(ITEM_DATA.keys()),
        "valores_referencia": ITEM_DATA
    }