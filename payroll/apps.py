"""
App configuration for the 'payroll' app.
"""

from django.apps import AppConfig


class PayrollConfig(AppConfig):
    """
    AppConfig for the 'payroll' app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "payroll"

    def ready(self) -> None:
        ready = super().ready()
        from django.urls import include, path

        from fits.fits_settings import APPS
        from fits.urls import urlpatterns

        APPS.append("payroll")
        urlpatterns.append(
            path("payroll/", include("payroll.urls.urls")),
        )
        try:
            from payroll.scheduler import auto_payslip_generate

            auto_payslip_generate()
        except:
            """
            Migrations are not affected
            """

        return ready
