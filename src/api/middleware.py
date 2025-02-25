from fastapi import Request, HTTPException
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.core.exceptions import (
    AppException,
)
from src.utils.database import parse_sqlite_integrity_error
from sqlalchemy.exc import IntegrityError
import sqlite3


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except AppException as app_exception:
            logger.error(f"Application Error: {str(app_exception)}")

            return JSONResponse(
                status_code=app_exception.status_code,
                content={
                    "message": str(app_exception.message),
                },
            )

        except (HTTPException, StarletteHTTPException) as http_exception:
            logger.error(f"HTTP Error: {str(http_exception.detail)}")

            return JSONResponse(
                status_code=http_exception.status_code,
                content={
                    "message": str(http_exception.detail),
                },
            )
        except (IntegrityError, sqlite3.IntegrityError) as db_exception:
            logger.error(f"Database Error: {str(db_exception)}", exc_info=True)

            msg = parse_sqlite_integrity_error(db_exception)
            status = 500
            # compose response based on error
            if "UNIQUE constraint failed" in str(db_exception):
                status = 409
            elif "FOREIGN KEY constraint failed" in str(db_exception):
                status = 400
            elif "CHECK constraint failed" in str(db_exception):
                status = 400

            return JSONResponse(
                status_code=status,
                content={"message": msg},
            )

        except Exception as e:
            logger.exception(f"Internal server error: {str(e)}")

            return JSONResponse(
                status_code=500,
                content={
                    "message": "An unexpected error occurred",
                },
            )
