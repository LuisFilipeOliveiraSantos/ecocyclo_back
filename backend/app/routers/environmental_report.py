import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException
from ..models.environmental_report import EnvironmentalReport
from ..schemas.environmental_report_schema import EnvironmentalReportCreate,EnvironmentalReportUpdate
from ..services.environmental_report_service import EnvironmentalReportService
router = APIRouter()

# Dados de referência SIMPLES
ITEM_DATA = {
    "laptop": {
        "valor_min": 25.0,
        "valor_max": 40.0,
        "co2": 15.0,
        "agua": 500.0,
        "energia": 120.0,
        "reaproveitamento_min": 80,
        "reaproveitamento_max": 90,
        "risco": "alto"
    },
    "celular": {
        "valor_min": 10.0,
        "valor_max": 25.0,
        "co2": 8.0,
        "agua": 300.0,
        "energia": 80.0,
        "reaproveitamento_min": 80,
        "reaproveitamento_max": 85,
        "risco": "alto"
    },
    "tablet": {
        "valor_min": 15.0,
        "valor_max": 30.0,
        "co2": 10.0,
        "agua": 400.0,
        "energia": 100.0,
        "reaproveitamento_min": 75,
        "reaproveitamento_max": 85,
        "risco": "medio"
    },
    "monitor": {
        "valor_min": 10.0,
        "valor_max": 20.0,
        "co2": 12.0,
        "agua": 600.0,
        "energia": 150.0,
        "reaproveitamento_min": 70,
        "reaproveitamento_max": 85,
        "risco": "alto"
    },
    "teclado": {
        "valor_min": 1.0,
        "valor_max": 3.0,
        "co2": 2.0,
        "agua": 100.0,
        "energia": 30.0,
        "reaproveitamento_min": 80,
        "reaproveitamento_max": 90,
        "risco": "baixo"
    },
    "mouse": {
        "valor_min": 1.0,
        "valor_max": 2.0,
        "co2": 1.5,
        "agua": 80.0,
        "energia": 25.0,
        "reaproveitamento_min": 75,
        "reaproveitamento_max": 85,
        "risco": "baixo"
    },
    "headset": {
        "valor_min": 1.0,
        "valor_max": 3.0,
        "co2": 2.5,
        "agua": 120.0,
        "energia": 35.0,
        "reaproveitamento_min": 70,
        "reaproveitamento_max": 80,
        "risco": "baixo"
    },
    "cpu": {
        "valor_min": 40.0,
        "valor_max": 70.0,
        "co2": 20.0,
        "agua": 800.0,
        "energia": 200.0,
        "reaproveitamento_min": 85,
        "reaproveitamento_max": 95,
        "risco": "medio"
    },
    "placa_mae": {
        "valor_min": 50.0,
        "valor_max": 120.0,
        "co2": 25.0,
        "agua": 1000.0,
        "energia": 250.0,
        "reaproveitamento_min": 90,
        "reaproveitamento_max": 95,
        "risco": "alto"
    },
    "controle_remoto": {
        "valor_min": 2.0,
        "valor_max": 4.0,
        "co2": 1.0,
        "agua": 60.0,
        "energia": 20.0,
        "reaproveitamento_min": 70,
        "reaproveitamento_max": 80,
        "risco": "baixo"
    }
}


@router.post("/")
async def criar_relatorio(dados: EnvironmentalReportCreate):
    """Cria relatório ambiental"""
    try:
        relatorio = await EnvironmentalReportService.create_environmental_report(dados)

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

@router.put('/{report_id}')
async def atualizar_relatorio(report_id: UUID,dados_atualizados: EnvironmentalReportUpdate):
    """Buscar relatório"""
    try:
      print(dados_atualizados)
      relatorio_atualizado =  await EnvironmentalReportService.update_report(report_id,dados_atualizados)
      return relatorio_atualizado
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na atualização do relatório: {str(e)}")

