import sqlite3
import time
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
from prometheus_client import Histogram, Gauge, Counter


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

            msg, type = parse_sqlite_integrity_error(db_exception)
            status = 500
            # compose response based on error
            if type == "unique":
                status = 409
            # TODO: add extensive check to differentiate foreign key insertion and deletion errors
            elif type == "foreign":
                status = 400
            elif type == "general":
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


requests_counter = Counter(
    name="http_requests_total",
    documentation="Total number of HTTP requests",
    labelnames=["endpoint", "method", "status"],
)
response_latency_histogram = Histogram(
    name="http_response_latency_seconds",
    documentation="Response Latency of HTTP requests (seconds)",
    labelnames=["endpoint", "method", "status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 3.0, 7.5, 10.0, float("INF")),
)
response_size_histogram = Histogram(
    name="http_response_size_bytes",
    documentation="Response Size of HTTP requests (bytes)",
    labelnames=["endpoint", "method", "status"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, float("INF")),
)
in_progress_request_gauge = Gauge(
    name="http_in_progress_requests_total",
    documentation="Total Number of HTTP requests in progress",
    labelnames=["endpoint", "method"],
)
excluded_endpoints = set(
    [
        "/metrics",
        "/metrics/",
        "/docs",
        "/docs/",
        "/redoc",
        "/redoc/",
        "/openapi.json",
        "/openapi.json/",
        "/health-check",
        "/health-check/",
    ]
)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """A middleware for monitoring all endpoints with Prometheus"""

    async def dispatch(self, request: Request, call_next):
        """
        Track the request and record relevant metrics.
        Exceptions will typically be caught at this stage since the error handler middleware is placed first so no need to use an except block here
        """
        # exclude tracking for metrics, health-check, docs endpoints
        if request.url.path in excluded_endpoints:
            return await call_next(request)

        # get request monitoring details
        # strip trailing slash for non-base path since "/users" and "/users/" are essentially aggregated as different paths
        endpoint = (
            request.url.path[:1]
            if len(request.url.path) > 1 and request.url.path[-1] != "/"
            else request.url.path
        )

        # track time for request
        start_time = time.perf_counter()
        method = request.method

        # record request as in-progress
        in_progress_request_gauge.labels(endpoint=endpoint, method=method).inc()

        try:
            response = await call_next(request)

            # get response monitoring details
            status = response.status_code
            response_size = int(response.headers.get("content-length", 0))
            latency = time.perf_counter() - start_time

            # record request count
            requests_counter.labels(
                endpoint=endpoint, method=method, status=status
            ).inc()

            # record response latency
            response_latency_histogram.labels(
                endpoint=endpoint, method=method, status=status
            ).observe(latency)

            # record response size
            response_size_histogram.labels(
                endpoint=endpoint, method=method, status=status
            ).observe(response_size)
            return response
        finally:
            # remove request from pool
            in_progress_request_gauge.labels(endpoint=endpoint, method=method).dec()
