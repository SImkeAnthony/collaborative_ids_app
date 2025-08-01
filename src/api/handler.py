# src/utils/exception_handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            f"Validation Error 422 on {request.method} {request.url} — {exc.errors()}"
        )
        return JSONResponse(
            status_code=422,
            content={"Error 422": exc.errors(), "body": exc.body},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(
            f"HTTP Error {exc.status_code} on {request.method} {request.url} — {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={f"HTTP Error {exc.status_code}": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Error 500 on {request.method} {request.url} — {exc}")
        return JSONResponse(
            status_code=500,
            content={"Unhandled Error 500": "Internal Server Error"},
        )
