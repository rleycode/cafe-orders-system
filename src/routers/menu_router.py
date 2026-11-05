from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.models import CategoryModel, ProductModel
from pydantic import BaseModel

router = APIRouter(prefix="/menu", tags=["Menu"])


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category_id: int

    class Config:
        from_attributes = True


class ProductCreateRequest(BaseModel):
    name: str
    price: float
    category_id: int


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    summary="Получить список категорий",
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CategoryModel))
    return res.scalars().all()


@router.get(
    "/products",
    response_model=list[ProductResponse],
    summary="Получить всё меню",
)
async def get_products(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ProductModel))
    return res.scalars().all()


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=201,
    summary="Добавить позицию в меню",
)
async def create_product(
    payload: ProductCreateRequest, db: AsyncSession = Depends(get_db)
):
    product = ProductModel(
        name=payload.name, price=payload.price, category_id=payload.category_id
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product
