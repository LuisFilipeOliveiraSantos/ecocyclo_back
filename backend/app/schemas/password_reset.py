from pydantic import BaseModel, EmailStr, Field, model_validator

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("As senhas não coincidem")
        return self

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("As senhas não coincidem")
        return self