import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from muwajjih.adapters.redis_cache import RedisCache
from muwajjih.adapters.sklearn_model import SklearnMuwajjihModel
from muwajjih.api.logging_setup import configure_logging
from muwajjih.api.routes import router, set_dependencies
from muwajjih.config import Settings

logger = logging.getLogger("muwajjih.api")


def _trace_id(request: Request) -> UUID:
    raw = request.headers.get("X-Trace-Id")
    if raw:
        try:
            return UUID(raw)
        except ValueError:
            pass
    return uuid4()


def _error_payload(
    request: Request, code: str, message: str, details: list[dict[str, str]] | None = None
) -> dict[str, Any]:
    trace_id = getattr(request.state, "trace_id", uuid4())
    return {
        "trace_id": str(trace_id),
        "data": None,
        "error": {"code": code, "message": message, "details": details or []},
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    configure_logging(settings.log_level)
    started = time.perf_counter()
    model = SklearnMuwajjihModel.load(settings.model_path, settings.model_version)
    model.warmup()
    cache = RedisCache(settings.redis_url)
    if not cache.ping():
        raise RuntimeError("Redis readiness check failed")
    set_dependencies(app, model=model, cache=cache, settings=settings)
    app.state.started_at = datetime.now(timezone.utc)
    app.state.ready = True
    logger.info(
        "startup_complete",
        extra={
            "trace_id": "system",
            "startup_ms": round((time.perf_counter() - started) * 1000, 2),
        },
    )
    yield
    app.state.ready = False
    cache.close()
    logger.info("shutdown_complete", extra={"trace_id": "system"})


def create_app(*, enable_lifespan: bool = True) -> FastAPI:
    app = FastAPI(
        title="Muwajjih API",
        version="1.0.0",
        lifespan=lifespan if enable_lifespan else None,
    )

    @app.middleware("http")
    async def trace_and_log(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        trace_id = _trace_id(request)
        request.state.trace_id = trace_id
        t0 = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Trace-Id"] = str(trace_id)
        response.headers["X-Response-Time-Ms"] = f"{(time.perf_counter() - t0) * 1000:.2f}"
        logger.info(
            "request_complete",
            extra={"trace_id": trace_id, "path": request.url.path, "method": request.method},
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {"field": ".".join(str(p) for p in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        body = _error_payload(request, "VALIDATION_ERROR", "Request validation failed", details)
        return JSONResponse(status_code=422, content=body)

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        details = []
        if exc.headers and "Retry-After" in exc.headers:
            details.append({"field": "Retry-After", "message": exc.headers["Retry-After"]})
        body = _error_payload(request, "HTTP_ERROR", str(exc.detail), details)
        headers = {"X-Trace-Id": body["trace_id"]}
        if exc.headers:
            headers.update(exc.headers)
        return JSONResponse(status_code=exc.status_code, content=body, headers=headers)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_error",
            extra={"trace_id": getattr(request.state, "trace_id", "unknown")},
        )
        body = _error_payload(request, "INTERNAL_ERROR", "Internal server error")
        return JSONResponse(status_code=500, content=body)

    app.include_router(router, prefix="/v1")
    return app


app = create_app()
