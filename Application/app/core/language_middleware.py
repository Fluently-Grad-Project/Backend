from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.utils import set_translator

class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lang = request.headers.get("Accept-Language", "en")
        set_translator(lang)
        return await call_next(request)
