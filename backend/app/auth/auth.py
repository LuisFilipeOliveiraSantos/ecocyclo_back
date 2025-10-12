from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
# REMOVER: from passlib.context import CryptContext  # ❌ NÃO É MAIS NECESSÁRIO

from .. import models, schemas
from ..config.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
ALGORITHM = "HS256"


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    Class used to get Authorization token from request HttpOnly cookie instead of
    header. Used to refresh token during SSO login process.
    """

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

        flows = OAuthFlowsModel(
            password=OAuthFlowPassword(tokenUrl=tokenUrl, scopes=scopes)
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> str | None:
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")
oauth2_scheme_with_cookies = OAuth2PasswordBearerWithCookie(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# REMOVER: password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    # Converte para bytes e aplica hash
    password_bytes = password.encode('utf-8')
    # bcrypt automaticamente lida com senhas até 72 bytes
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Converte de volta para string para armazenamento
    return hashed_bytes.decode('utf-8')

def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verify a password against a hash using bcrypt
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_pass.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def authenticate_user(email: str, password: str) -> models.User | None:
    user = await models.User.find_one({"email": email})
    if not user:
        return None
    if user.hashed_password is None or not verify_password(
        password, user.hashed_password
    ):
        return None
    return user


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return await _get_current_user(token)


async def get_current_user_from_cookie(
    token: str = Depends(oauth2_scheme_with_cookies),
):
    return await _get_current_user(token)


async def _get_current_user(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        userid: UUID | None = payload.get("sub")
        if userid is None:
            raise credentials_exception
        token_data = schemas.TokenPayload(uuid=userid)
    except JWTError:
        raise credentials_exception
    user = await models.User.find_one({"uuid": token_data.uuid})
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
