from dataclasses import dataclass, field
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


@dataclass(slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int = 500
    details: list[dict[str, Any]] = field(default_factory=list)


def error_payload(
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {"code": code, "message": message, "details": details or []}


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message, exc.details),
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error.get("loc", [])),
            "message": error.get("msg", "invalid"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content=error_payload("VALIDATION_ERROR", "Request validation failed", details),
    )


async def integrity_error_handler(_: Request, __: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=error_payload("CONFLICT", "Data conflict", []),
    )


async def generic_error_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_ERROR", "Unexpected server error", []),
    )
