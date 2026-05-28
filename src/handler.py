from http import HTTPStatus

from fastapi.responses import JSONResponse
from starlette.requests import Request

from src.order.exceptions import NotFoundException


async def not_found_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"detail": str(exc)},
    )
