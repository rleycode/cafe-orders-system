from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import TableModel


class TableRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_number(self, table_number: int) -> TableModel | None:
        stmt = select(TableModel).where(TableModel.table_number == table_number)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
