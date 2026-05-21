from fastapi import Header

from app.core.config import get_settings
from app.core.errors import AppError


async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise AppError(code="UNAUTHORIZED", message="Missing or invalid API key", status_code=401)
