import os
from typing import Optional
from app.models.company import Company, CompanyType
from app.auth.auth_company import get_hashed_password


class AdminSetupService:
    def __init__(self):
        self.admin_data = self._get_admin_data()
    
    def _get_admin_data(self) -> Optional[dict]:
        """Obtém os dados do admin das variáveis de ambiente"""
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_cnpj = os.getenv("ADMIN_CNPJ")
        
        if not all([admin_email, admin_password, admin_cnpj]):
            return None
            
        return {
            "email": admin_email,
            "cnpj": admin_cnpj,
            "nome": os.getenv("ADMIN_NOME", "Administrador do Sistema"),
            "telefone": os.getenv("ADMIN_TELEFONE", ""),
            "password": admin_password,
            "company_type": CompanyType.EMPRESA_COLETORA,
            "cep": os.getenv("ADMIN_CEP", ""),
            "rua": os.getenv("ADMIN_RUA", ""),
            "numero": os.getenv("ADMIN_NUMERO", ""),
            "bairro": os.getenv("ADMIN_BAIRRO", ""),
            "cidade": os.getenv("ADMIN_CIDADE", ""),
            "uf": os.getenv("ADMIN_UF", ""),
            "company_colector_tags": ["venda", "doacao"],
            "is_admin": True  
        }
    
    async def create_admin_if_not_exists(self) -> bool:
        """Cria o admin se não existir e se os dados estiverem configurados"""
        if not self.admin_data:
            print("⚠️  Dados do admin não configurados no .env")
            return False
        
        # Verificar se já existe algum admin
        existing_admin = await Company.find_one({"is_admin": True})
        if existing_admin:
            print("✅ Admin já existe no sistema")
            return True
        
        # Verificar se já existe company com esse email ou CNPJ
        existing_company = await Company.find_one({
            "$or": [
                {"email": self.admin_data["email"]},
                {"cnpj": self.admin_data["cnpj"]}
            ]
        })
        
        if existing_company:
            print("⚠️  Já existe uma empresa com o email ou CNPJ do admin")
            return False
        
        try:
            # Criar o admin
            hashed_password = get_hashed_password(self.admin_data["password"])
            
            admin_company = Company(
                email=self.admin_data["email"],
                cnpj=self.admin_data["cnpj"],
                nome=self.admin_data["nome"],
                telefone=self.admin_data["telefone"],
                hashed_password=hashed_password,
                company_type=self.admin_data["company_type"],
                cep=self.admin_data["cep"],
                rua=self.admin_data["rua"],
                numero=self.admin_data["numero"],
                bairro=self.admin_data["bairro"],
                cidade=self.admin_data["cidade"],
                uf=self.admin_data["uf"],
                company_colector_tags=self.admin_data["company_colector_tags"],
                is_admin=True,  # ← DEFININDO COMO ADMIN AQUI TAMBÉM
                is_active=True
            )
            
            await admin_company.create()
            print("✅ Admin criado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar admin: {str(e)}")
            return False


# Instância global do serviço
admin_setup_service = AdminSetupService()