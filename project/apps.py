from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project"

    def ready(self):
        try:
            from django.urls import include, path
            from fits.fits_settings import APP_URLS, APPS
            from fits.urls import urlpatterns

            if "project" not in APPS:
                APPS.append("project")
            urlpatterns.append(
                path("project/", include("project.urls")),
            )
            APP_URLS.append("project.urls")
        except Exception:
            pass
        super().ready()
