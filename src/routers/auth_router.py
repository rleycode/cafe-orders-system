from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "client"


class UserResponse(BaseModel):
    id: int
    username: str
    role: str


class LoginResponse(BaseModel):
    username: str
    role: str
    message: str


@router.post("/login", response_model=LoginResponse, summary="Вход в систему")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        user = await service.authenticate(payload.username, payload.password)
        return LoginResponse(
            username=user.username,
            role=user.role.value,
            message=f"Вход выполнен. Ваша роль: {user.role.value}",
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Регистрация пользователя",
)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        user = await service.register(payload.username, payload.password, payload.role)
        return UserResponse(id=user.id, username=user.username, role=user.role.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
