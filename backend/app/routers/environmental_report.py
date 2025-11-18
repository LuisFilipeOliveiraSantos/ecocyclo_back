import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException
from ..models.environmental_report import EnvironmentalReport
from ..models.item_reference import ItemReference  # ✅ NOVO IMPORT
from ..schemas.environmental_report_schema import EnvironmentalReportCreate, EnvironmentalReportUpdate
from ..services.environmental_report_service import EnvironmentalReportService

router = APIRouter()

# ❌ REMOVER a variável ITEM_DATA fixa - AGORA VEM DO BANCO

@router.post("/")
async def criar_relatorio(dados: EnvironmentalReportCreate):
    """Cria relatório ambiental - AGORA USA DADOS DO BANCO"""
    try:
        relatorio = await EnvironmentalReportService.create_environmental_report(dados)
        return {"message": "Relatório criado com dados do banco!", "report_id": relatorio.report_id}
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
    """Mostra itens disponíveis - AGORA DO BANCO"""
    # Busca itens ativos do banco
    itens = await ItemReference.find(ItemReference.ativo == True).to_list()
    
    # Formata os dados igual ao formato anterior
    itens_formatados = {}
    for item in itens:
        itens_formatados[item.nome] = {
            "valor_min": item.valor_min,
            "valor_max": item.valor_max,
            "co2": item.co2,
            "agua": item.agua,
            "energia": item.energia,
            "reaproveitamento_min": item.reaproveitamento_min,
            "reaproveitamento_max": item.reaproveitamento_max,
            "risco": item.risco.value  # Converte enum para string
        }
    
    return {
        "itens_disponiveis": list(itens_formatados.keys()),
        "valores_referencia": itens_formatados,
        "total_itens_cadastrados": len(itens),
        "fonte": "banco_de_dados"  # ✅ Para confirmar que vem do banco
    }


@router.put('/{report_id}')
async def atualizar_relatorio(report_id: UUID, dados_atualizados: EnvironmentalReportUpdate):
    """Atualiza relatório - AGORA USA DADOS DO BANCO"""
    try:
        print(dados_atualizados)
        relatorio_atualizado = await EnvironmentalReportService.update_report(report_id, dados_atualizados)
        return relatorio_atualizado
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na atualização do relatório: {str(e)}")


@router.get("/debug/itens-banco")
async def debug_itens_banco():
    """Endpoint de debug - mostra itens direto do banco"""
    itens = await ItemReference.find(ItemReference.ativo == True).to_list()
    
    resultado = []
    for item in itens:
        resultado.append({
            "nome": item.nome,
            "valor_medio": item.valor_medio,
            "reaproveitamento_medio": item.reaproveitamento_medio,
            "risco": item.risco.value,
            "co2": item.co2,
            "ativo": item.ativo
        })
    
    return {
        "total_itens": len(itens),
        "itens": resultado
    }
