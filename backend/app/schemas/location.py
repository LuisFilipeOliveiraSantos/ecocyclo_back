from pydantic import BaseModel
from typing import List, Optional

class EstadoSchema(BaseModel):
    sigla: str
    nome: str

class CidadeSchema(BaseModel):
    nome: str
    codigo: str

class EnderecoCEPSchema(BaseModel):
    cep: str
    rua: str
    bairro: str
    cidade: str
    uf: str

class LocalizacaoResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None