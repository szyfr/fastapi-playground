from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User, UserRole
from app.requests.auth_requests import RegisterRequest, LoginRequest, UpdatePasswordRequest
from app.core.auth import verify_password, hash_password, create_access_token
from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    BadRequestException,
)


class AuthController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, request: RegisterRequest) -> User:
        existing = await self.db.execute(select(User).where(User.email == request.email))
        if existing.scalars().first():
            raise ConflictException("Email is already registered")

        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            role=UserRole.USER,
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, request: LoginRequest) -> tuple[User, str]:
        result = await self.db.execute(select(User).where(User.email == request.email))
        user = result.scalars().first()

        if not user or not verify_password(request.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("This account has been deactivated")

        token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return user, token

    async def update_password(self, user: User, request: UpdatePasswordRequest) -> User:
        if not verify_password(request.current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect")

        user.password_hash = hash_password(request.new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user
