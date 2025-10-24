import httpx
import logging
import re

logger = logging.getLogger(__name__)

class GeocodingService:
    
    # Mapeamento de nomes de estados para siglas
    ESTADO_PARA_SIGLA = {
        'acre': 'AC',
        'alagoas': 'AL', 
        'amapá': 'AP',
        'amazonas': 'AM',
        'bahia': 'BA',
        'ceará': 'CE',
        'distrito federal': 'DF',
        'espírito santo': 'ES',
        'goiás': 'GO',
        'maranhão': 'MA',
        'mato grosso': 'MT',
        'mato grosso do sul': 'MS',
        'minas gerais': 'MG',
        'pará': 'PA',
        'paraíba': 'PB',
        'paraná': 'PR',
        'pernambuco': 'PE',
        'piauí': 'PI',
        'rio de janeiro': 'RJ',
        'rio grande do norte': 'RN',
        'rio grande do sul': 'RS',
        'rondônia': 'RO',
        'roraima': 'RR',
        'santa catarina': 'SC',
        'são paulo': 'SP',
        'sergipe': 'SE',
        'tocantins': 'TO'
    }
    
    async def get_coordinates_from_address(self, address_data: dict) -> tuple[float, float] | None:
        """
        Obtém latitude e longitude a partir dos dados de endereço usando Nominatim (OpenStreetMap)
        """
        query = self._build_query_string(address_data)
        logger.info(f"🔍 Buscando coordenadas para: {query}")
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'q': query,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'br',
                    'addressdetails': 1
                }
                
                headers = {
                    'User-Agent': 'EcocycloApp/1.0 (filipebsg2@gmail.com)'
                }
                
                logger.info(f"🌐 Fazendo requisição para Nominatim...")
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search", 
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                
                logger.info(f"📥 Resposta recebida: Status {response.status_code}")
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ Nominatim retornou status {response.status_code}")
                    return None
                
                data = response.json()
                logger.info(f"📊 Dados recebidos: {len(data) if data else 0} resultados")
                
                if data and len(data) > 0:
                    location = data[0]
                    latitude = location.get('lat')
                    longitude = location.get('lon')
                    
                    if latitude and longitude:
                        logger.info(f"✅ Coordenadas obtidas: {latitude}, {longitude}")
                        return float(latitude), float(longitude)
                    else:
                        logger.warning(f"Coordenadas não encontradas no response: {location}")
                else:
                    logger.warning(f"⚠️ Nenhum resultado encontrado para: {query}")
                
                return None
                
        except httpx.TimeoutException:
            logger.error("⏰ Timeout na requisição para Nominatim")
            return None
        except httpx.RequestError as e:
            logger.error(f"🔌 Erro de conexão com Nominatim: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado no geocoding: {str(e)}")
            return None

    async def get_address_from_cep(self, cep: str) -> dict | None:
        """
        Busca endereço completo a partir do CEP usando Nominatim
        Retorna: {
            "cep": "01310-100",
            "bairro": "Bela Vista", 
            "cidade": "São Paulo",
            "uf": "SP",
        }
        """
        # Limpar e formatar CEP
        cep_limpo = re.sub(r'[^\d]', '', cep)
        
        if len(cep_limpo) != 8:
            logger.error(f"❌ CEP inválido: {cep}")
            return None
            
        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        logger.info(f"🔍 Buscando endereço para CEP: {cep_formatado}")
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'q': f"{cep_formatado}, Brasil",
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'br',
                    'addressdetails': 1
                }
                
                headers = {
                    'User-Agent': 'EcocycloApp/1.0 (filipebsg2@gmail.com)'
                }
                
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search", 
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        location = data[0]
                        address = location.get('address', {})
                        
                        # Extrair UF do nome do estado
                        estado_nome = address.get('state', '').lower()
                        uf = self._converter_estado_para_sigla(estado_nome)
                        
                        # Mapear campos do Nominatim para nosso formato
                        endereco = {
                            "cep": cep_formatado,
                            "rua": self._extract_street(address),
                            "bairro": address.get('suburb') or address.get('neighbourhood') or address.get('quarter') or '',
                            "cidade": address.get('city') or address.get('town') or address.get('village') or address.get('municipality') or '',
                            "uf": uf,
                        }
                        
                        logger.info(f"✅ Endereço encontrado: {endereco['rua']}, {endereco['cidade']}-{endereco['uf']}")
                        return endereco
                    else:
                        logger.warning(f"⚠️ Nenhum endereço encontrado para CEP: {cep_formatado}")
                else:
                    logger.error(f"❌ Erro na requisição: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("⏰ Timeout na busca por CEP")
        except Exception as e:
            logger.error(f"❌ Erro inesperado na busca por CEP: {str(e)}")
            
        return None

    def _converter_estado_para_sigla(self, estado_nome: str) -> str:
        """
        Converte o nome do estado para sigla
        Exemplo: 'pernambuco' → 'PE'
        """
        estado_limpo = estado_nome.lower().strip()
        
        # Remover acentos e caracteres especiais
        estado_limpo = (
            estado_limpo
            .replace('á', 'a')
            .replace('â', 'a')
            .replace('ã', 'a')
            .replace('é', 'e')
            .replace('ê', 'e')
            .replace('í', 'i')
            .replace('ó', 'o')
            .replace('ô', 'o')
            .replace('õ', 'o')
            .replace('ú', 'u')
            .replace('ç', 'c')
        )
        
        return self.ESTADO_PARA_SIGLA.get(estado_limpo, '')

    def _extract_street(self, address: dict) -> str:
        """Extrai o nome da rua do response do Nominatim"""
        street = (
            address.get('road') or 
            address.get('street') or 
            address.get('pedestrian') or 
            address.get('footway') or
            address.get('residential') or
            ''
        )
        return street

    def _build_query_string(self, address_data: dict) -> str:
        """Constrói a string de consulta do endereço"""
        address_parts = [
            f"{address_data.get('rua', '')} {address_data.get('numero', '')}".strip(),
            address_data.get('bairro', ''),
            address_data.get('cidade', ''),
            address_data.get('uf', ''),
            'Brasil'
        ]
        return ', '.join(filter(None, address_parts))

geocoding_service = GeocodingService()