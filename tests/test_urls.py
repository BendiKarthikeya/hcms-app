from django.http import JsonResponse
from django.urls import path


def health_check(_request):
    return JsonResponse({"status": "ok"}, status=200)


urlpatterns = [
    path("health/", health_check),
]
