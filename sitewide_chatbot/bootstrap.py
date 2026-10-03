"""Bootstraps the sitewide chatbot without modifying existing project files."""

from __future__ import annotations

from typing import Callable

_PATCHED = False


def install() -> None:
    """Inject the chatbot middleware into Django's middleware stack."""
    global _PATCHED
    if _PATCHED:
        return

    try:
        from django.core.handlers.base import BaseHandler
    except Exception:
        return

    original_load_middleware: Callable[..., None] = BaseHandler.load_middleware
    middleware_path = "sitewide_chatbot.middleware.SitewideChatbotMiddleware"

    def patched_load_middleware(self, is_async: bool = False):  # type: ignore[override]
        from django.conf import settings

        middleware = list(getattr(settings, "MIDDLEWARE", []))
        if middleware_path not in middleware:
            middleware.insert(0, middleware_path)
            settings.MIDDLEWARE = middleware
        return original_load_middleware(self, is_async=is_async)

    BaseHandler.load_middleware = patched_load_middleware
    _PATCHED = True
