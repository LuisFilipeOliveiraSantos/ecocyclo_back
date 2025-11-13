from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime
from beanie import Document
from pydantic import Field

ITEM_REFERENCE_DATA = {
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
        "reciclavel_min": 70,
        "reaproveitamento_max": 80,
        "risco": "baixo"
    },
    "cpu": {
        "valor_min": 40.0,
        "valor_max": 70.0,
        "co2": 20.0,
        "agua": 800.0,
        "energia": 200.0,
        "reciclavel_min": 85,
        "reaproveitamento_max": 95,
        "risco": "medio"
    },
    "placa_mae": {
        "valor_min": 50.0,
        "valor_max": 120.0,
        "co2": 25.0,
        "agua": 1000.0,
        "energia": 250.0,
        "reciclavel_min": 90,
        "reaproveitamento_max": 95,
        "risco": "alto"
    },
    "controle_remoto": {
        "valor_min": 2.0,
        "valor_max": 4.0,
        "co2": 1.0,
        "agua": 60.0,
        "energia": 20.0,
        "reciclavel_min": 70,
        "reaproveitamento_max": 80,
        "risco": "baixo"
    }
}
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
    detalhes_itens: list[dict]
    risco_ambiental_medio: RiskLevel = RiskLevel.BAIXO
    co2_economizado_kg: float = 0.0
    agua_economizada_l: float = 0.0
    energia_economizada_kwh: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "environmental_reports"
        indexes = ["report_id", "empresa_id"]