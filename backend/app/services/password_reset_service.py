from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import JWTError, jwt
from fastapi import HTTPException
from app.config.config import settings


class passwordResetService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.expire_minutes = 30  

    def create_reset_token(self, company_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)

        to_encode = {"exp": expire, 
                    "sub": str(company_id),
                    "type": "password_reset",
                    "jti": str(uuid4())}
            
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_reset_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "password_reset":
                raise HTTPException(status_code=401, detail="Invalid token type")
            company_id: str = payload.get("sub")

            if company_id is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            return company_id
        
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
    def is_token_expired(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")

            if exp is None:
                return True
            expire_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            return datetime.now(timezone.utc) > expire_time
        
        except JWTError:
            return True
        
password_reset_service = passwordResetService()