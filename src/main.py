import uvicorn

from fastapi import FastAPI

from src.order.router import router as order_router


def create_app() -> FastAPI:
    app = FastAPI(title="Order Service", version="1.0.0")
    app.include_router(order_router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)
