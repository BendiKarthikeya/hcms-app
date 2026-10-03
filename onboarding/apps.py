from django.apps import AppConfig


class OnboardingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "onboarding"

    def ready(self):
        from django.urls import include, path

        from fits.fits_settings import APPS
        from fits.urls import urlpatterns

        APPS.append("onboarding")
        urlpatterns.append(
            path("onboarding/", include("onboarding.urls")),
        )
        super().ready()
