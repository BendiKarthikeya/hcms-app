"""Minimal OpenRouter client for the sitewide chatbot."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OpenRouterError(RuntimeError):
    """Raised when the OpenRouter call fails."""


@dataclass(frozen=True)
class OpenRouterConfig:
    api_key: str
    model: str
    app_name: str
    site_url: str
    api_url: str = "https://openrouter.ai/api/v1/chat/completions"

    @classmethod
    def from_env(cls) -> "OpenRouterConfig | None":
        api_key = (
            os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY") or ""
        ).strip()
        if not api_key:
            return None
        return cls(
            api_key=api_key,
            model=(os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini").strip(),
            app_name=(
                os.getenv("OPENROUTER_APP_NAME") or "FITS HCMS Site Chatbot"
            ).strip(),
            site_url=(
                os.getenv("OPENROUTER_SITE_URL") or "http://127.0.0.1:8000"
            ).strip(),
        )


def chat_completion(
    config: OpenRouterConfig, messages: list[dict[str, str]]
) -> dict[str, Any]:
    payload = {
        "model": config.model,
        "messages": messages,
        "temperature": 0.2,
    }
    request = Request(
        config.api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": config.site_url,
            "X-Title": config.app_name,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise OpenRouterError(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise OpenRouterError(f"OpenRouter network error: {exc.reason}") from exc


def extract_text(response_payload: dict[str, Any]) -> str:
    choices = response_payload.get("choices") or []
    if not choices:
        raise OpenRouterError("OpenRouter returned no choices.")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        text = "".join(text_parts).strip()
        if text:
            return text
    raise OpenRouterError("OpenRouter returned an unexpected response format.")
