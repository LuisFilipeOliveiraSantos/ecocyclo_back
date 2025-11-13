from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime
from beanie import Document
from pydantic import Field


class RiskLevel(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio" 
    ALTO = "alto"


class ElectronicItem(str, Enum):
    CELULAR = "celular"
    LAPTOP = "laptop"
    TABLET = "tablet"
    MONITOR = "monitor"
    TECLADO = "teclado"
    MOUSE = "mouse"
    HEADSET = "headset"
    CPU = "cpu"
    PLACA_MAE = "placa_mae"
    CONTROLE_REMOTO = "controle_remoto"


class EnvironmentalReport(Document):
    report_id: UUID = Field(default_factory=uuid4)
    empresa_id: UUID
    data_relatorio: datetime = Field(default_factory=datetime.utcnow)
    periodo_inicio: datetime
    periodo_fim: datetime
    itens_processados: dict = Field(default_factory=dict)
    total_itens: int = 0
    taxa_reaproveitamento_media: float = 0.0
    receita_total_estimada: float = 0.0
    risco_ambiental_medio: RiskLevel = RiskLevel.BAIXO
    co2_economizado_kg: float = 0.0
    agua_economizada_l: float = 0.0
    energia_economizada_kwh: float = 0.0
    
    class Settings:
        name = "environmental_reports"
        indexes = ["report_id", "empresa_id"]