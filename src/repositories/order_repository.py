from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import OrderItemModel, OrderModel, ProductModel, utcnow
from src.models.domain import Order, OrderItem


class OrderRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = (
            select(OrderModel)
            .options(
                selectinload(OrderModel.items).selectinload(OrderItemModel.product),
                selectinload(OrderModel.table),
            )
            .where(OrderModel.id == order_id)
        )
        res = await self.session.execute(stmt)
        order_orm = res.scalar_one_or_none()
        if not order_orm:
            return None

        items = []
        total = 0.0
        for item in order_orm.items:
            p_price = float(item.product.price)
            total += p_price * item.quantity
            items.append(
                OrderItem(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    product_name=item.product.name,
                    unit_price=p_price,
                )
            )

        return Order(
            id=order_orm.id,
            table_id=order_orm.table_id,
            table_number=order_orm.table.table_number if order_orm.table else None,
            status=order_orm.status,
            created_at=order_orm.created_at,
            closed_at=order_orm.closed_at,
            items=items,
            total_price=total,
        )

    async def close(self, order_id: int) -> bool:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        res = await self.session.execute(stmt)
        order_orm = res.scalar_one_or_none()
        if not order_orm:
            return False

        order_orm.status = "paid"
        order_orm.closed_at = utcnow()
        await self.session.commit()
        return True

    async def create_order(self, table_id: int, items_data: list[dict]) -> OrderModel:
        order_orm = OrderModel(table_id=table_id, status="created")
        self.session.add(order_orm)
        await self.session.flush()

        for item in items_data:
            order_item = OrderItemModel(
                order_id=order_orm.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
            )
            self.session.add(order_item)

        await self.session.commit()
        return order_orm

    async def update_status(self, order_id: int, new_status: str) -> bool:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        res = await self.session.execute(stmt)
        order_orm = res.scalar_one_or_none()
        if not order_orm:
            return False

        order_orm.status = new_status
        await self.session.commit()
        return True
