from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel
from ..models.environmental_report import ElectronicItem, RiskLevel


class EnvironmentalReportCreate(BaseModel):
    empresa_id: UUID
    periodo_inicio: datetime
    periodo_fim: datetime
    itens_processados: Dict[str, int]


class EnvironmentalReportUpdate(BaseModel):
    itens_processados: Optional[Dict[str, int]] = None 
    periodo_inicio: Optional[datetime] = None
    periodo_fim: Optional[datetime] = None




class EnvironmentalReportResponse(BaseModel):
    report_id: UUID
    empresa_id: UUID
    data_relatorio: datetime
    periodo_inicio: datetime
    periodo_fim: datetime
    itens_processados: Dict[ElectronicItem, int]
    detalhes_itens: List[dict]
    total_itens: int
    taxa_reaproveitamento_media: float
    receita_total_estimada: float
    risco_ambiental_medio: RiskLevel
    co2_economizado_kg: float
    agua_economizada_l: float
    energia_economizada_kwh: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EnvironmentalReportSummary(BaseModel):
    report_id: UUID
    data_relatorio: datetime
    total_itens: int
    receita_total_estimada: float
    co2_economizado_kg: float
    taxa_reaproveitamento_media: float