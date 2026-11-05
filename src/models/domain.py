from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    CLIENT = "client"
    WAITER = "waiter"
    COOK = "cook"
    ADMIN = "admin"


@dataclass
class User:
    id: int
    username: str
    role: UserRole
    hashed_password: str
    created_at: datetime | None = None


@dataclass
class Category:
    id: int
    name: str


@dataclass
class Product:
    id: int
    name: str
    price: float
    category_id: int
    category_name: str | None = None 


@dataclass
class Table:
    id: int
    table_number: int
    seats_count: int


@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    product_name: str | None = None 
    unit_price: float | None = None


@dataclass
class Order:
    id: int
    table_id: int
    status: str
    created_at: datetime
    items: list[OrderItem] = field(default_factory=list)
    total_price: float = 0.0
    table_number: int | None = None
    closed_at: datetime | None = None
