import uvicorn

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from src.handler import not_found_handler
from src.order.exceptions import NotFoundException
from src.order.router import router as order_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Order Service",
        version="1.0.0",
        default_response_class=UJSONResponse,
    )
    app.include_router(order_router)
    app.add_exception_handler(NotFoundException, not_found_handler)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)
