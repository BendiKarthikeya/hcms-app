"""Chatbot service layer — uses Groq if GROQ_API_KEY is set."""

from __future__ import annotations

import json
import os
from typing import Any

from .knowledge import (
    PRODUCT_OVERVIEW,
    build_fallback_answer,
    build_links,
    rank_features,
)


def _trim_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    trimmed: list[dict[str, str]] = []
    for item in history[-6:]:
        role = item.get("role", "").strip()
        content = item.get("content", "").strip()
        if role in {"user", "assistant"} and content:
            trimmed.append({"role": role, "content": content[:1500]})
    return trimmed


def _build_messages(
    question: str,
    base_url: str,
    current_path: str,
    current_title: str,
    history: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    matches = rank_features(question, limit=8)
    links = build_links(base_url, matches)
    catalog_text = "\n".join(
        f"- {l['title']}: {l['description']}" for l in links
    )
    history_text = _trim_history(history)

    system_prompt = f"""You are Ahmed, the FITS HCMS assistant. FITS HCMS is an enterprise HR platform.

You help users navigate the product and find features. Be friendly, concise, and helpful.

Rules:
- NEVER include URLs, paths, or hyperlinks in your text answer. Navigation buttons are shown separately below your answer.
- Keep answers to 2-3 sentences max.
- Refer to pages by their title only (e.g. "Go to Organization Chart").
- If the user asks what you can help with, summarise the HR modules available: employee management, recruitment, onboarding, leave, attendance, payroll, performance, learning, talent & succession, expenses, and compliance.
- If the question is about navigation, name the best matching page and briefly explain what it does.

Product overview:
{PRODUCT_OVERVIEW}

Current page the user is on:
- title: {current_title or "Unknown"}
- path: {current_path or "/"}

Relevant pages that will be shown as navigation buttons (do NOT repeat paths):
{catalog_text or "No specific pages matched."}""".strip()

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(history_text)
    messages.append({"role": "user", "content": question})
    return messages, links


def _groq_chat(messages: list[dict[str, str]]) -> str | None:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from groq import Groq
        model = os.environ.get("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4,
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as exc:
        print(f"[chatbot] Groq error: {exc}")
        return None


def answer_question(payload: dict[str, Any], base_url: str) -> dict[str, Any]:
    question = str(payload.get("message", "")).strip()
    if not question:
        return {
            "answer": "Ask me anything about FITS HCMS — modules, workflows, or where to find a page.",
            "links": [],
            "mode": "empty",
        }

    current_path = str(payload.get("current_path", "")).strip() or "/"
    current_title = str(payload.get("current_title", "")).strip()
    history = payload.get("history") if isinstance(payload.get("history"), list) else []

    messages, links = _build_messages(
        question, base_url, current_path, current_title, history
    )
    fallback = build_fallback_answer(question, base_url)

    answer = _groq_chat(messages)
    if answer:
        return {
            "answer": answer,
            "links": links or fallback["links"],
            "mode": "groq",
            "model": os.environ.get("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile"),
        }

    return {
        "answer": fallback["answer"],
        "links": fallback["links"],
        "mode": "local",
        "model": None,
    }
