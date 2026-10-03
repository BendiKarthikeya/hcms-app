from django.apps import AppConfig


class LeaveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "leave"

    def ready(self):
        try:
            from django.urls import include, path
            from fits.fits_settings import APPS
            from fits.urls import urlpatterns

            if "leave" not in APPS:
                APPS.append("leave")
            urlpatterns.append(
                path("leave/", include("leave.urls")),
            )
        except Exception:
            pass
        super().ready()
