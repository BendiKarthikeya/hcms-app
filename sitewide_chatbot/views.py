from __future__ import annotations

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .service import answer_question


@require_GET
def health(request):
    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON body."}, status=400)

    result = answer_question(payload, request.build_absolute_uri("/").rstrip("/"))
    return JsonResponse(result)
