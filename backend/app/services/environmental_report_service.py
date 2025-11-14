from uuid import UUID
from datetime import datetime
from typing import List, Dict
from app.models.environmental_report import EnvironmentalReport
from app.models.item_reference import ItemReference, RiskLevel  # ✅ NOVO IMPORT
from app.schemas.environmental_report_schema import EnvironmentalReportCreate, EnvironmentalReportUpdate

class EnvironmentalReportService:
    
    @staticmethod
    async def _get_item_data_from_db() -> Dict:
        """Busca dados dos itens DO BANCO DE DADOS"""
        items = await ItemReference.find(ItemReference.ativo == True).to_list()
        
        item_data = {}
        for item in items:
            item_data[item.nome] = {
                "valor_min": item.valor_min,
                "valor_max": item.valor_max,
                "valor_medio": item.valor_medio,
                "co2": item.co2,
                "agua": item.agua,
                "energia": item.energia,
                "reaproveitamento_min": item.reaproveitamento_min,
                "reaproveitamento_max": item.reaproveitamento_max,
                "reaproveitamento_medio": item.reaproveitamento_medio,
                "risco": item.risco,
                "peso_medio_kg": item.peso_medio_kg
            }
        
        return item_data
    
    @staticmethod
    async def _calcular_metricas(itens_processados: Dict[str, int]) -> tuple:
        """Calcula métricas USANDO DADOS DO BANCO"""
        item_data = await EnvironmentalReportService._get_item_data_from_db()
        
        total_itens = sum(itens_processados.values())
        detalhes_itens = []
        receita_total = 0.0
        co2_total = 0.0
        agua_total = 0.0
        energia_total = 0.0
        reaproveitamento_total = 0.0
        
        for item_nome, quantidade in itens_processados.items():
            if item_nome in item_data and quantidade > 0:
                dados = item_data[item_nome]
                
                # Usa valor médio do banco
                receita_item = dados["valor_medio"] * quantidade
                co2_item = dados["co2"] * quantidade
                agua_item = dados["agua"] * quantidade
                energia_item = dados["energia"] * quantidade
                
                detalhes_itens.append({
                    'tipo_item': item_nome,
                    'nome': item_nome,
                    'quantidade': quantidade,
                    'reaproveitamento_medio': dados["reaproveitamento_medio"],
                    'receita_estimada': receita_item,
                    'risco': dados["risco"],
                    'co2_economizado': co2_item,
                    'agua_economizada': agua_item,
                    'energia_economizada': energia_item,
                    'peso_total_kg': dados["peso_medio_kg"] * quantidade
                })
                
                receita_total += receita_item
                co2_total += co2_item
                agua_total += agua_item
                energia_total += energia_item
                reaproveitamento_total += dados["reaproveitamento_medio"] * quantidade
        
        # Taxa de reaproveitamento média ponderada
        taxa_reaproveitamento_media = (reaproveitamento_total / total_itens) if total_itens > 0 else 0
        
        return total_itens, taxa_reaproveitamento_media, receita_total, detalhes_itens, co2_total, agua_total, energia_total
    
    @staticmethod
    async def create_environmental_report(report_data: EnvironmentalReportCreate) -> EnvironmentalReport:
        """Cria relatório USANDO DADOS DO BANCO"""
        # Calcular métricas com dados do banco
        total_itens, taxa_reaproveitamento, receita_total, detalhes_itens, co2_total, agua_total, energia_total = (
            await EnvironmentalReportService._calcular_metricas(report_data.itens_processados)
        )
        
        # Calcular risco ambiental médio
        from app.services.environmental_report_service import EnvironmentalReportService as ERService
        risco_medio = await ERService._calcular_risco_medio(detalhes_itens)
        
        report = EnvironmentalReport(
            empresa_id=report_data.empresa_id,
            periodo_inicio=report_data.periodo_inicio,
            periodo_fim=report_data.periodo_fim,
            itens_processados=report_data.itens_processados,
            total_itens=total_itens,
            taxa_reaproveitamento_media=taxa_reaproveitamento,
            receita_total_estimada=receita_total,
            risco_ambiental_medio=risco_medio,
            detalhes_itens=detalhes_itens,
            co2_economizado_kg=co2_total,
            agua_economizada_l=agua_total,
            energia_economizada_kwh=energia_total
        )
        
        return await report.insert()
    
    @staticmethod
    async def _calcular_risco_medio(detalhes_itens: List[dict]) -> RiskLevel:
        """Calcula o risco ambiental médio baseado nos itens processados"""
        risco_pontos = {
            RiskLevel.BAIXO: 1,
            RiskLevel.MEDIO: 2,
            RiskLevel.ALTO: 3
        }
        
        total_pontos = 0
        total_itens = 0
        
        for detalhe in detalhes_itens:
            total_pontos += risco_pontos[detalhe['risco']] * detalhe['quantidade']
            total_itens += detalhe['quantidade']
        
        if total_itens == 0:
            return RiskLevel.BAIXO
            
        risco_medio = total_pontos / total_itens
        
        if risco_medio >= 2.5:
            return RiskLevel.ALTO
        elif risco_medio >= 1.5:
            return RiskLevel.MEDIO
        else:
            return RiskLevel.BAIXO
    
    @staticmethod
    async def get_report_by_id(report_id: UUID) -> EnvironmentalReport:
        """Busca um relatório pelo ID"""
        report = await EnvironmentalReport.find_one(EnvironmentalReport.report_id == report_id)
        if not report:
            raise ValueError("Relatório não encontrado")
        return report
    
    @staticmethod
    async def get_reports_by_company(empresa_id: UUID) -> List[EnvironmentalReport]:
        """Busca relatórios de uma empresa"""
        reports = await EnvironmentalReport.find(
            EnvironmentalReport.empresa_id == empresa_id
        ).sort(-EnvironmentalReport.created_at).to_list()
        return reports
    
    @staticmethod
    async def update_report(report_id: UUID, update_data: EnvironmentalReportUpdate) -> EnvironmentalReport:
        """Atualiza um relatório existente"""
        report = await EnvironmentalReportService.get_report_by_id(report_id)
        
        # Se itens_processados foram atualizados, recalcular métricas
        if update_data.itens_processados is not None:
            total_itens, taxa_reaproveitamento, receita_total, detalhes_itens, co2_total, agua_total, energia_total = (
                await EnvironmentalReportService._calcular_metricas(update_data.itens_processados)
            )
            
            risco_medio = await EnvironmentalReportService._calcular_risco_medio(detalhes_itens)
            
            # Atualiza os campos calculados
            report.itens_processados = update_data.itens_processados
            report.total_itens = total_itens
            report.taxa_reaproveitamento_media = taxa_reaproveitamento
            report.receita_total_estimada = receita_total
            report.risco_ambiental_medio = risco_medio
            report.detalhes_itens = detalhes_itens
            report.co2_economizado_kg = co2_total
            report.agua_economizada_l = agua_total
            report.energia_economizada_kwh = energia_total
        
        await report.save()
        return report