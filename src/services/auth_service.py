from sqlalchemy.ext.asyncio import AsyncSession

from src.models.domain import User, UserRole
from src.repositories.user_repository import UserRepository
from src.services.security import hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def authenticate(self, username: str, password: str) -> User:
        user_orm = await self.user_repo.get_by_username(username)
        if not user_orm or not verify_password(password, user_orm.hashed_password):
            raise ValueError("Неверный логин или пароль")
        return self._to_domain(user_orm)

    async def register(self, username: str, password: str, role: str) -> User:
        username = username.strip()
        if not username or not password:
            raise ValueError("Логин и пароль обязательны")

        try:
            role_enum = UserRole(role)
        except ValueError:
            allowed = ", ".join(r.value for r in UserRole)
            raise ValueError(f"Недопустимая роль. Разрешены: {allowed}")

        existing = await self.user_repo.get_by_username(username)
        if existing:
            raise ValueError(f"Пользователь '{username}' уже существует")

        hashed = hash_password(password)
        user_orm = await self.user_repo.create(username, hashed, role_enum.value)
        return self._to_domain(user_orm)

    @staticmethod
    def _to_domain(user_orm) -> User:
        return User(
            id=user_orm.id,
            username=user_orm.username,
            role=UserRole(user_orm.role),
            hashed_password=user_orm.hashed_password,
            created_at=user_orm.created_at,
        )
