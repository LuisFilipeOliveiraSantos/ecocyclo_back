import httpx
from app.config.config import settings  

class CNPJValidator:
    
    async def validate(self, cnpj: str) -> dict:
        """Valida CNPJ usando Brasil API (gratuita)"""
        cnpj_clean = "".join(filter(str.isdigit, cnpj))
        

        if len(cnpj_clean) != 14:
            return {"valid": False, "error": "CNPJ deve ter 14 dígitos"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_clean}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "valid": True,
                        "company_name": data.get("razao_social"),
                        "trade_name": data.get("nome_fantasia"),
                        "opening_date": data.get("data_inicio_atividade"),
                        "situation": data.get("descricao_situacao_cadastral"),
                        "address": {
                            "street": data.get("logradouro"),
                            "number": data.get("numero"),
                            "district": data.get("bairro"),
                            "city": data.get("municipio"),
                            "state": data.get("uf"),
                            "cep": data.get("cep")
                        }
                    }
                else:
                    return {"valid": False, "error": "CNPJ não encontrado na Receita Federal"}
                    
        except httpx.TimeoutException:
            return {"valid": False, "error": "Timeout na consulta do CNPJ"}
        except Exception as e:
            return {"valid": False, "error": f"Erro na validação: {str(e)}"}

# Instância global
cnpj_validator = CNPJValidator()