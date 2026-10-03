"""FITS HCMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import importlib.util

from django.conf.urls.static import static

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from recruitment.views.views import careers as careers_view
import notifications.urls



def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)


urlpatterns = [
    path("", RedirectView.as_view(url="/ui/login/", permanent=False)),
    path("admin/", admin.site.urls),
    path("careers/", careers_view, name="careers"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("base.urls")),
    path("", include("fits_automations.urls")),
    path("", include("fits_views.urls")),
    path("employee/", include("employee.urls")),
    path("fits-widget/", include("fits_widgets.urls")),
    re_path(
        "^inbox/notifications/", include(notifications.urls, namespace="notifications")
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("health/", health_check),
    # Include additional app URLs
    path("recruitment/", include("recruitment.urls")),
    path("ui/", include("ui.urls")),
    path("ui/chatbot/", include("sitewide_chatbot.urls")),
    path("leave/", include("leave.urls")),
    path("pms/", include("pms.urls")),
    path("onboarding/", include("onboarding.urls")),
    path("asset/", include("asset.urls")),
    path("attendance/", include("attendance.urls")),
    path("biometric/", include("biometric.urls")),
    path("payroll/", include("payroll.urls.urls")),
    path("learning/", include("learning.urls")),
    path("talent/", include("talent.urls")),
    path("expenses/", include("expenses.urls")),
    path("omani-compliance/", include("omani_compliance.urls")),
    path("project/", include("project.urls")),
    path("report/", include("report.urls")),
    path("audit/", include("fits_audit.urls")),
]

if all(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("rest_framework", "rest_framework_simplejwt", "drf_yasg")
):
    urlpatterns.insert(8, path("api/", include("fits_api.urls")))

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
