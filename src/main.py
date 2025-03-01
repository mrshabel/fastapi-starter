import time
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.core.config import AppConfig

from src.core.database import init_db
from src.api.main import api_router
from src.api.middleware import (
    ExceptionHandlerMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=AppConfig.PROJECT_TITLE,
    summary=AppConfig.PROJECT_DESCRIPTION,
    version=AppConfig.PROJECT_VERSION,
    docs_url="/docs" if AppConfig.IS_DEVELOPMENT else None,
    redoc_url="/redoc" if AppConfig.IS_DEVELOPMENT else None,
    # root_path="/api" if AppConfig.IS_DEVELOPMENT else "/",
    openapi_url="/openapi.json" if AppConfig.IS_DEVELOPMENT else None,
)

# create mount point in development
if AppConfig.IS_DEVELOPMENT:
    # TODO: authorize static file access. https://github.com/fastapi/fastapi/issues/858#issuecomment-876564020
    # alias the path name as /public
    app.mount("/public", StaticFiles(directory=AppConfig.LOCAL_STORAGE_PATH), "uploads")

# declare cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=AppConfig.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=AppConfig.ALLOWED_METHODS,
    allow_headers=["*"],
)


# add middlewares here
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{(process_time * 1000):.2f}"
    return response


app.add_middleware(ExceptionHandlerMiddleware)


# exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom exception handler for all request validation errors"""
    logger.error("Data validation error occurred")
    return JSONResponse(status_code=422, content={"message": exc.errors()})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Custom exception handler for all uncaught exceptions"""
    logger.exception("Fatal. Unhandled exception occurred", exc_info=True)
    return JSONResponse(
        status_code=500, content={"message": "An unexpected error occurred"}
    )


# register all routes
app.include_router(api_router)
