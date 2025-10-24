import httpx
import logging

logger = logging.getLogger(__name__)

class GeocodingService:
    
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
                
                # Nominatim requer User-Agent
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