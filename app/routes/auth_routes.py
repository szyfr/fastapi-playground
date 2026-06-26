from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.controllers.auth_controller import AuthController
from app.requests.auth_requests import RegisterRequest, LoginRequest, UpdatePasswordRequest
from app.responses import AuthTokenResponse, UserResponse, MessageResponse
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthTokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    controller = AuthController(db)
    user = await controller.register(data)
    _, token = await controller.login(
        type("obj", (object,), {"email": data.email, "password": data.password})()
    )
    return AuthTokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=AuthTokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    controller = AuthController(db)
    user, token = await controller.login(data)
    return AuthTokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.patch("/password", response_model=MessageResponse)
async def update_password(
    data: UpdatePasswordRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    controller = AuthController(db)
    await controller.update_password(user, data)
    return MessageResponse(message="Password updated successfully")
