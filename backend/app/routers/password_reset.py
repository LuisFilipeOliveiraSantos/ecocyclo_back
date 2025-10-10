from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app import models
from uuid import UUID
from app.schemas.password_reset import (
    ForgotPasswordRequest, 
    ResetPasswordRequest, 
    PasswordChangeRequest
)
from app.services.password_reset_service import password_reset_service
from app.services.email_service import email_service
from app.auth.auth_company import (
    get_hashed_password,
    verify_password,
    get_current_active_company,
)

router = APIRouter()

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate password reset process for a company.
    """
    company = await models.Company.find_one({"email": request.email})
    
    # Sempre retornar mesma mensagem por segurança
    if not company or not company.is_active:
        return {
            "message": "Se o email existir em nosso sistema, enviaremos instruções de recuperação"
        }

    reset_token = password_reset_service.create_reset_token(str(company.uuid))
    print("company_UID:", company.uuid)
    
    # Enviar email em background
    background_tasks.add_task(
        email_service.send_password_reset_email,
        company.email,
        reset_token
    )
    
    return {
        "message": "Se o email existir em nosso sistema, enviaremos instruções de recuperação"
    }

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Reset company password using the provided token.
    """
    company_id = password_reset_service.verify_reset_token(request.token)
    
    if not company_id:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
    try:
        company_uuid = UUID(company_id)
        print("Company_ID convertido: {company_uuid}")
    except ValueError as e:
        print(f"❌ Erro na conversão para UUID: {e}")
        raise HTTPException(status_code=400, detail="Token inválido")


    # Debug: buscar a empresa
    company = await models.Company.find_one({"uuid": company_uuid})
    print(f"🔍 Empresa encontrada: {company}")

    company = await models.Company.find_one({"uuid": company_uuid})
    if not company:
        print("❌ Empresa não encontrada no banco")
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
    # Atualizar senha
    company.hashed_password = get_hashed_password(request.new_password)
    await company.save()
    
    return {"message": "Senha redefinida com sucesso"}


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_company: models.Company = Depends(get_current_active_company)
):
    """
    Change password for logged-in company (requires current password)
    """
    # Verificar senha atual
    if not verify_password(request.current_password, current_company.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    # Atualizar senha
    current_company.hashed_password = get_hashed_password(request.new_password)
    await current_company.save()
    
    return {"message": "Senha alterada com sucesso"}