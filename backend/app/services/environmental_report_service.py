from uuid import UUID
from datetime import datetime, timezone
from typing import List, Dict
from ..models.environmental_report import (
    EnvironmentalReport, 
    ElectronicItem,
    RiskLevel,
    ITEM_REFERENCE_DATA
)
from ..schemas.environmental_report_schema import EnvironmentalReportCreate,EnvironmentalReportUpdate


class EnvironmentalReportService:
    
    @staticmethod
    def _calcular_risco_medio(detalhes_itens: List[dict]) -> RiskLevel:
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
    def _calcular_metricas(itens_processados: Dict[ElectronicItem, int]) -> tuple:
        """Calcula todas as métricas baseadas nos itens processados"""
        total_itens = sum(itens_processados.values())
        detalhes_itens = []
        receita_total = 0.0
        co2_total = 0.0
        agua_total = 0.0
        energia_total = 0.0
        reaproveitamento_total = 0.0

        for item_type, quantidade in itens_processados.items():
            if quantidade == 0:
                continue
                
            dados_item = ITEM_REFERENCE_DATA[item_type]
            
            # Valor médio estimado
            valor_medio = (dados_item['valor_min'] + dados_item['valor_max']) / 2
            receita_item = valor_medio * quantidade
            
            # Taxa de reaproveitamento média
            reaproveitamento_medio = (dados_item['reaproveitamento_min'] + dados_item['reaproveitamento_max']) / 2
            
            # Impacto ambiental
            co2_item = dados_item['co2'] * quantidade
            agua_item = dados_item['agua'] * quantidade
            energia_item = dados_item['energia'] * quantidade
            
            detalhes_itens.append({
                'tipo_item': item_type.value,
                'nome': item_type.value,
                'quantidade': quantidade,
                'reaproveitamento_medio': reaproveitamento_medio,
                'receita_estimada': receita_item,
                'risco': dados_item['risco'],
                'co2_economizado': co2_item,
                'agua_economizada': agua_item,
                'energia_economizada': energia_item,
            })
            
            receita_total += receita_item
            co2_total += co2_item
            agua_total += agua_item
            energia_total += energia_item
            reaproveitamento_total += reaproveitamento_medio * quantidade
        
        # Taxa de reaproveitamento média ponderada
        taxa_reaproveitamento_media = (reaproveitamento_total / total_itens) if total_itens > 0 else 0
        
        return total_itens, taxa_reaproveitamento_media, receita_total, detalhes_itens, co2_total, agua_total, energia_total
    
    @staticmethod
    async def create_environmental_report(report_data: EnvironmentalReportCreate) -> EnvironmentalReport:
        """Cria um novo relatório ambiental"""
        # Calcular todas as métricas
        total_itens, taxa_reaproveitamento, receita_total, detalhes_itens, co2_total, agua_total, energia_total = (
            EnvironmentalReportService._calcular_metricas(report_data.itens_processados)
        )
        
        # Calcular risco ambiental médio
        risco_medio = EnvironmentalReportService._calcular_risco_medio(detalhes_itens)
        
        report = EnvironmentalReport(
            empresa_id=report_data.empresa_id,
            periodo_inicio=report_data.periodo_inicio,
            periodo_fim=report_data.periodo_fim,
            itens_processados={k.value: v for k, v in report_data.itens_processados.items()},
            total_itens=total_itens,
            taxa_reaproveitamento_media=taxa_reaproveitamento,
            receita_total_estimada=receita_total,
            risco_ambiental_medio=risco_medio,
            detalhes_itens=detalhes_itens,
            co2_economizado_kg=co2_total,
            agua_economizada_l=agua_total,
            energia_economizada_kwh=energia_total
        )
        print(report)
        
        return await report.insert()
    
    @staticmethod
    async def get_report_by_id(report_id: UUID) -> EnvironmentalReport:
        """Busca um relatório pelo ID"""
        report = await EnvironmentalReport.find_one(EnvironmentalReport.report_id == report_id)
        
        if not report:
            raise ValueError("Relatório ambiental não encontrado")
            
        return report
    
    @staticmethod
    async def get_reports_by_company(empresa_id: UUID, limit: int = 100) -> List[EnvironmentalReport]:
        """Busca relatórios de uma empresa"""
        reports = await EnvironmentalReport.find(
            EnvironmentalReport.empresa_id == empresa_id
        ).sort(-EnvironmentalReport.data_relatorio).limit(limit).to_list()
        
        return reports
    
    @staticmethod
    async def get_reports_by_period(empresa_id: UUID, inicio: datetime, fim: datetime) -> List[EnvironmentalReport]:
        """Busca relatórios por período"""
        reports = await EnvironmentalReport.find({
            "empresa_id": empresa_id,
            "data_relatorio": {
                "$gte": inicio,
                "$lte": fim
            }
        }).sort(-EnvironmentalReport.data_relatorio).to_list()
        
        return reports
    
    @staticmethod
    async def update_report(report_id: UUID, update_data: EnvironmentalReportUpdate) -> EnvironmentalReport:
        """Atualiza um relatório existente"""
        report = await EnvironmentalReportService.get_report_by_id(report_id)


        update_payload = update_data.model_dump(exclude_unset=True)

        # 2. Verifique se 'itens_processados' está no payload que recebemos
        if 'itens_processados' in update_payload:
            # 3. Calcule as métricas com base nos dados do payload
            total_itens, taxa_reaproveitamento, receita_total, detalhes_itens, co2_total, agua_total, energia_total = (
                EnvironmentalReportService._calcular_metricas(update_payload['itens_processados'])
            )

            risco_medio = EnvironmentalReportService._calcular_risco_medio(detalhes_itens)

            # 4. Crie um dicionário APENAS com as métricas calculadas
            metrics_data = {
                'total_itens': total_itens,
                'taxa_reaproveitamento_media': taxa_reaproveitamento,
                'receita_total_estimada': receita_total,
                'risco_ambiental_medio': risco_medio,
                'detalhes_itens': detalhes_itens,
                'co2_economizado_kg': co2_total,
                'agua_economizada_l': agua_total,
                'energia_economizada_kwh': energia_total,
            }


            update_payload.update(metrics_data)

        update_payload['updated_at'] = datetime.utcnow()

        # 7. Envie o payload final e combinado para o banco
        await report.update({"$set": update_payload})

        return await EnvironmentalReportService.get_report_by_id(report_id)
    @staticmethod
    async def delete_report(report_id: UUID) -> bool:
        """Deleta um relatório"""
        report = await EnvironmentalReportService.get_report_by_id(report_id)
        await report.delete()
        return True
    
    @staticmethod
    async def get_company_stats(empresa_id: UUID) -> dict:
        """Obtém estatísticas consolidadas da empresa"""
        reports = await EnvironmentalReportService.get_reports_by_company(empresa_id)
        
        if not reports:
            return {
                "total_relatorios": 0,
                "total_itens_processados": 0,
                "receita_total": 0,
                "co2_total_economizado": 0,
                "agua_total_economizada": 0,
                "energia_total_economizada": 0
            }
        
        total_itens = sum(report.total_itens for report in reports)
        receita_total = sum(report.receita_total_estimada for report in reports)
        co2_total = sum(report.co2_economizado_kg for report in reports)
        agua_total = sum(report.agua_economizada_l for report in reports)
        energia_total = sum(report.energia_economizada_kwh for report in reports)
        
        return {
            "total_relatorios": len(reports),
            "total_itens_processados": total_itens,
            "receita_total": receita_total,
            "co2_total_economizado": co2_total,
            "agua_total_economizada": agua_total,
            "energia_total_economizada": energia_total,
            "taxa_reaproveitamento_media": sum(report.taxa_reaproveitamento_media for report in reports) / len(reports)
        }