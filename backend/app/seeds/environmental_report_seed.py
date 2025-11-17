import asyncio
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from backend.app.models.environmental_report import EnvironmentalReport, ElectronicItem
from backend.app.services.environmental_report_service import EnvironmentalReportService


class EnvironmentalReportSeed:
    
    @staticmethod
    async def create_sample_reports():
        """Cria relatórios de exemplo para desenvolvimento"""
        print("🌱 Criando seeds para Environmental Reports...")
        
        sample_reports = [
            {
                "empresa_id": uuid4(),
                "periodo_inicio": datetime.now(timezone.utc) - timedelta(days=60),
                "periodo_fim":  datetime.now(timezone.utc) - timedelta(days=30),
                "itens_processados": {
                    ElectronicItem.LAPTOP: 8,
                    ElectronicItem.CELULAR: 15,
                    ElectronicItem.TABLET: 5,
                    ElectronicItem.MONITOR: 3
                }
            },
            {
                "empresa_id": uuid4(),
                "periodo_inicio": datetime.now(timezone.utc) - timedelta(days=30),
                "periodo_fim": datetime.now(timezone.utc),
                "itens_processados": {
                    ElectronicItem.TECLADO: 12,
                    ElectronicItem.MOUSE: 10,
                    ElectronicItem.HEADSET: 6,
                    ElectronicItem.CPU: 2,
                    ElectronicItem.PLACA_MAE: 3
                }
            },
            {
                "empresa_id": uuid4(), 
                "periodo_inicio": datetime.now(timezone.utc) - timedelta(days=90),
                "periodo_fim": datetime.now(timezone.utc) - timedelta(days=60),
                "itens_processados": {
                    ElectronicItem.LAPTOP: 3,
                    ElectronicItem.CELULAR: 8,
                    ElectronicItem.MONITOR: 2,
                    ElectronicItem.CONTROLE_REMOTO: 10
                }
            }
        ]
        
        created_count = 0
        for report_data in sample_reports:
            try:
                from ..schemas.environmental_report_schema import EnvironmentalReportCreate
                
                report_create = EnvironmentalReportCreate(**report_data)
                await EnvironmentalReportService.create_environmental_report(report_create)
                created_count += 1
                print(f"   ✅ Relatório {created_count} criado")
                
            except Exception as e:
                print(f"   ❌ Erro ao criar relatório: {e}")
        
        print(f"🎉 {created_count} relatórios de exemplo criados!")
        
        # Mostrar estatísticas
        total_reports = await EnvironmentalReport.find_all().count()
        print(f"📊 Total de relatórios no banco: {total_reports}")
    
    @staticmethod
    async def clear_all_reports():
        """Limpa todos os relatórios (para desenvolvimento)"""
        print("🧹 Limpando todos os Environmental Reports...")
        
        reports = await EnvironmentalReport.find_all().to_list()
        for report in reports:
            await report.delete()
        
        print(f"✅ {len(reports)} relatórios removidos")


# Para executar manualmente
async def main():
    seed = EnvironmentalReportSeed()
    await seed.create_sample_reports()

if __name__ == "__main__":
    asyncio.run(main())