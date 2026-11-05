from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.schemas.order import (
    OrderCloseRequest,
    OrderCreateRequest,
    OrderStatusUpdateRequest,
    OrderResponse,
)
from src.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=201,
    summary="Создать новый заказ",
)
async def create_order(payload: OrderCreateRequest, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    try:
        items_dicts = [item.model_dump() for item in payload.items]
        order = await service.create_new_order(
            table_number=payload.table_number, items_data=items_dicts
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Получить информацию о заказе по ID",
)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    order = await service.order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден.")
    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Изменить статус заказа",
)
async def update_order_status(
    order_id: int,
    payload: OrderStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    try:
        updated_order = await service.change_status(
            order_id=order_id, new_status=payload.status, user_role=payload.user_role
        )
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{order_id}/close",
    response_model=OrderResponse,
    summary="Закрыть заказ и принять оплату",
)
async def close_order(
    order_id: int,
    payload: OrderCloseRequest,
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    try:
        order = await service.close_order(
            order_id=order_id,
            confirm_payment=payload.confirm_payment,
            user_role=payload.user_role,
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
