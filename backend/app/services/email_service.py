import logging
from app.config.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    async def send_password_reset_email(self, email: str, reset_token: str):
        # """Envia email com link de reset de password"""
        # reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"  # Ajustar após ter o serviço no front funcionando
        
        # Em produção, integrar com serviço de email real (SendGrid, AWS SES, etc.)
        # Por enquanto, apenas log
        logger.info(f"Password reset email sent to {email}")
        logger.info(f"Reset URL: {reset_token}")
        
        # Exemplo de implementação real:
        # await real_email_service.send(
        #     to_email=email,
        #     subject="Redefinição de Senha - Ecocyclo",
        #     template="password_reset.html",
        #     context={"reset_url": reset_url}
        # )

        
        print(f"📧 Email de reset enviado para: {email}")
        print(f"🔗 Link: {reset_token}")

email_service = EmailService()