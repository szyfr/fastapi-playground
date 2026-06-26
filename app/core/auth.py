from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pwdlib import PasswordHash
from app.core.config import settings

pwd_hash = PasswordHash.recommended()


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_hash.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_hash.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def decode_m2m_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.M2M_SECRET, algorithms=[settings.M2M_ALGORITHM])
    except JWTError:
        return None