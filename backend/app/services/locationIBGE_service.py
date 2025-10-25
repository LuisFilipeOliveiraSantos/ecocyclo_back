import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self):
        self.ibge_estados_url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
        self.ibge_cidades_url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        
    
    async def get_estados(self) -> List[Dict[str, str]]:
        """
        Busca todos os estados do Brasil da API do IBGE
        Retorna: [{"sigla": "SP", "nome": "São Paulo"}, ...]
        """
        try:   
            logger.info("🌐 Buscando estados do IBGE...")
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ibge_estados_url, timeout=10.0)
                
                if response.status_code == 200:
                    estados_data = response.json()
                    estados = []

                    for estado in estados_data:
                        estados.append({
                            "sigla": estado.get("sigla"),
                            "nome": estado.get("nome")
                        })

                    estados.sort(key=lambda x: x["nome"])
                    logger.info(f"✅ {len(estados)} estados obtidos com sucesso.")
                    return estados
                else:
                    logger.warning(f"⚠️ Falha ao buscar estados: Status {response.status_code}")
                    return []
        except httpx.TimeoutException:
            logger.error("Timeout na requisição para obter estados do IBGE")
            return []
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao buscar estados do IBGE: {str(e)}")
            return []


    async def get_cidades_por_estado(self, uf: str) -> List[Dict[str, str]]:
        """
        Busca todas as cidades de um estado específico da API do IBGE
        Parâmetros:
            uf: Sigla do estado (ex: "SP")
        Retorna: [{"nome": "São Paulo"}, ...]
        """
        try:
            url = self.ibge_cidades_url.format(uf=uf)
            logger.info(f"🌐 Buscando cidades para o estado {uf} do IBGE...")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    cidades_data = response.json()
                    cidades = []

                    for cidade in cidades_data:
                        cidades.append({
                            "codigo": str(cidade.get("id")),
                            "nome": cidade.get("nome")
                        })

                    cidades.sort(key=lambda x: x["nome"])
                    logger.info(f"✅ {len(cidades)} cidades obtidas com sucesso para o estado {uf}.")
                    return cidades
                else:
                    logger.warning(f"⚠️ Falha ao buscar cidades para o estado {uf}: Status {response.status_code}")
                    return []
        except httpx.TimeoutException:
            logger.error(f"Timeout na requisição para obter cidades do estado {uf} do IBGE")
            return []
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao buscar cidades do estado {uf} do IBGE: {str(e)}")
            return []
                       
ibge_service = LocationService()