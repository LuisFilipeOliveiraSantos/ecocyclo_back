import asyncio
from app.models.company import Company
from app.auth.auth_company import get_hashed_password

# seeds/seed_admin.py
async def create_first_admin():
    existing_admin = await Company.find_one({
        "$or": [
            {"email": "admin@system.com"},
            {"is_admin": True}
        ]
    })
    
    if existing_admin:
        print("Admin já existe")
        return existing_admin

    admin = Company(
        cnpj="00000000000191",
        email="admin@system.com",
        telefone="999999999",
        hashed_password=get_hashed_password("admin"),  # Verifique se esta senha está correta
        company_type="coletora",
        cep="00000-000",
        rua="Admin Street",
        numero="1",
        bairro="Centro",
        cidade="Cidade",
        uf="UF",
        is_admin=True,
        is_active=True  # Garantir que está ativo
    )
    await admin.create()
    print("Admin criado com sucesso!")
    return admin
