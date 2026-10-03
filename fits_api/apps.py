from django.apps import AppConfig


class FitsApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fits_api"

    def ready(self):
        """
        Initialize API documentation when the app is ready
        """
        # Import and register API documentation components
        import fits_api.schema  # noqa
