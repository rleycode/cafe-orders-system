from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.models import TableModel
from pydantic import BaseModel

router = APIRouter(prefix="/tables", tags=["Tables"])


class TableResponse(BaseModel):
    id: int
    table_number: int
    seats_count: int

    class Config:
        from_attributes = True


@router.get("/", response_model=list[TableResponse], summary="Получить список столиков")
async def get_tables(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TableModel))
    return res.scalars().all()
