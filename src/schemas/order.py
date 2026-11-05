from datetime import datetime
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(...)
    quantity: int = Field(..., gt=0)


class OrderCreateRequest(BaseModel):
    table_number: int = Field(...)
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(...)
    user_role: str = Field(...)


class OrderCloseRequest(BaseModel):
    confirm_payment: bool = Field(...)
    user_role: str = Field(...)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str | None = None
    quantity: int
    unit_price: float | None = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    table_id: int
    table_number: int | None = None
    status: str
    created_at: datetime
    closed_at: datetime | None = None
    items: list[OrderItemResponse] = []
    total_price: float = 0.0

    class Config:
        from_attributes = True
