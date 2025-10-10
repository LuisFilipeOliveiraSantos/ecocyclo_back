from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security.oauth2 import OAuthFlowsModel
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.config import settings
from app.models.company import Company
from app.schemas.tokens import TokenPayload

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = "HS256"

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, description=description, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            else:
                return None
        return param

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/company/login/access-token")
oauth2_scheme_with_cookies = OAuth2PasswordBearerWithCookie(tokenUrl=f"{settings.API_V1_STR}/company/login/access-token")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    # Proteção extra - truncar se maior que 72 bytes
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

async def authenticate_company(email: str, password: str) -> Company | None:
    company = await Company.find_one({"email": email})
    if not company:
        return None
    if company.hashed_password is None or not verify_password(password, company.hashed_password):
        return None
    return company

def create_access_token_company(subject: str | Any, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_company(token: str = Depends(oauth2_scheme)):
    return await _get_current_company(token)

async def get_current_company_from_cookie(token: str = Depends(oauth2_scheme_with_cookies)):
    return await _get_current_company(token)

async def _get_current_company(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        company_id: UUID | None = payload.get("sub")
        if company_id is None:
            raise credentials_exception
        token_data = TokenPayload(uuid=company_id)
    except JWTError:
        raise credentials_exception
    company = await Company.find_one({"uuid": token_data.uuid})
    if company is None:
        raise credentials_exception
    return company

def get_current_active_company(current_company: Company = Depends(get_current_company)) -> Company:
    if not current_company.is_active:
        raise HTTPException(status_code=400, detail="Inactive company")
    return current_company

def get_current_active_admin_company(current_company: Company = Depends(get_current_company)) -> Company:
    if not current_company.is_active or not current_company.is_admin:
        raise HTTPException(
            status_code=403,
            detail="The company doesn't have enough privileges"
        )
    return current_company
