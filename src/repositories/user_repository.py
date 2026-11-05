from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> UserModel | None:
        return await self.session.get(UserModel, user_id)

    async def create(self, username: str, hashed_password: str, role: str) -> UserModel:
        user = UserModel(username=username, hashed_password=hashed_password, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
