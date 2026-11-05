from sqlalchemy.ext.asyncio import AsyncSession

from src.models.domain import Order
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.table_repository import TableRepository

ALLOWED_STATUSES = ["created", "preparing", "ready", "paid"]

ROLE_ALLOWED_STATUSES = {
    "cook": ["preparing", "ready"],
    "admin": ALLOWED_STATUSES,
}


class OrderService:

    def __init__(self, session: AsyncSession):
        self.order_repo = OrderRepository(session)
        self.table_repo = TableRepository(session)
        self.product_repo = ProductRepository(session)

    async def create_new_order(
        self, table_number: int, items_data: list[dict]
    ) -> Order:
        if not items_data:
            raise ValueError("Заказ должен содержать хотя бы одну позицию.")

        for item in items_data:
            if item["quantity"] <= 0:
                raise ValueError("Количество товара должно быть больше 0.")

        table = await self.table_repo.get_by_number(table_number)
        if not table:
            raise ValueError(f"Стол с номером {table_number} не найден.")

        product_ids = [item["product_id"] for item in items_data]
        products = await self.product_repo.get_by_ids(product_ids)
        products_by_id = {p.id: p for p in products}

        for item in items_data:
            product = products_by_id.get(item["product_id"])
            if not product:
                raise ValueError(f"Блюдо с ID {item['product_id']} не найдено в меню.")
            if not product.is_available:
                raise ValueError(f"Блюдо '{product.name}' недоступно.")

        created_orm = await self.order_repo.create_order(table.id, items_data)
        order = await self.order_repo.get_by_id(created_orm.id)
        if not order:
            raise RuntimeError("Не удалось получить созданный заказ из БД.")
        return order

    async def change_status(
        self, order_id: int, new_status: str, user_role: str
    ) -> Order:
        if new_status not in ALLOWED_STATUSES:
            raise ValueError(
                f"Недопустимый статус. Разрешены: {', '.join(ALLOWED_STATUSES)}"
            )

        allowed = ROLE_ALLOWED_STATUSES.get(user_role)
        if not allowed or new_status not in allowed:
            raise PermissionError(
                f"Роль '{user_role}' не может устанавливать статус '{new_status}'."
            )

        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Заказ с ID {order_id} не найден.")

        await self.order_repo.update_status(order_id, new_status)
        updated = await self.order_repo.get_by_id(order_id)
        if not updated:
            raise RuntimeError("Не удалось получить обновлённый заказ из БД.")
        return updated

    async def close_order(
        self, order_id: int, confirm_payment: bool, user_role: str
    ) -> Order:
        if user_role not in ["waiter", "admin"]:
            raise PermissionError(
                "Закрывать заказ могут только официант или администратор."
            )

        if not confirm_payment:
            raise ValueError("Оплата не подтверждена.")

        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Заказ с ID {order_id} не найден.")

        if order.status != "ready":
            raise ValueError(
                f"Заказ нельзя закрыть: текущий статус '{order.status}', требуется 'ready'."
            )

        await self.order_repo.close(order_id)
        updated = await self.order_repo.get_by_id(order_id)
        if not updated:
            raise RuntimeError("Не удалось получить закрытый заказ из БД.")
        return updated
