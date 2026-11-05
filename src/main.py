from fastapi import FastAPI
from src.routers import order_router, auth_router, menu_router, table_router

app = FastAPI(
    title="Cafe Orders System API",
    description="123",
    version="1.0.0",
)

app.include_router(auth_router.router)
app.include_router(menu_router.router)
app.include_router(table_router.router)
app.include_router(order_router.router)


@app.get("/")
async def main():
    return {"message": "Система заказов кафе"}
