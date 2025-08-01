import logging
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_403_FORBIDDEN

logger = logging.getLogger(__name__)

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            client_ip = request.client.host
            if client_ip != "127.0.0.1":
                logger.warning(f"HTTP error 403: Try to access from {client_ip} for request {request.url}")
                # Return a 403 Forbidden response for non-localhost requests
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"HTTP Error 403": "Access restricted to localhost only"}
                )
            response = await call_next(request)
            return response

        except RequestValidationError as ve:
            logger.warning(f"Validation error: {ve} for request {request.url}")
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={"Request validation Error": ve.errors()}
            )
        except HTTPException as he:
            logger.error(f"HTTP exception: {he.detail} for request {request.url}")
            return JSONResponse(
                status_code=he.status_code,
                content={"HTTP Exception Error": he.detail}
            )
        except ValueError as ve:
            logger.error(f"Value error: {ve} for request {request.url}")
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": str(ve)}
            )
        except KeyError as ke:
            logger.error(f"Key error: {ke} for request {request.url}")
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={"Key Error": f"Missing key: {str(ke)}"}
            )
        except Exception as e:
            logger.error(f"Unhandled exception for {request.url}")
            logger.debug(traceback.format_exc())
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={"Unhandled exception": "Internal server error"}
            )
