from http import HTTPStatus

from fastapi.responses import UJSONResponse
from starlette.requests import Request

from src.order.exceptions import NotFoundException


async def not_found_handler(request: Request, exc: NotFoundException) -> UJSONResponse:
    return UJSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"detail": str(exc)},
    )
