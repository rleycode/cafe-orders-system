from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ProductModel


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ids(self, product_ids: list[int]) -> list[ProductModel]:
        if not product_ids:
            return []
        stmt = select(ProductModel).where(ProductModel.id.in_(product_ids))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
