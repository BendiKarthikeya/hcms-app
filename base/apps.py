"""
This module contains the configuration for the 'base' app.
"""

from django.apps import AppConfig


class BaseConfig(AppConfig):
    """
    Configuration class for the 'base' app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "base"

    def ready(self) -> None:

        super().ready()
        try:
            from base.models import EmployeeShiftDay

            if not EmployeeShiftDay.objects.exists():
                days = [
                    ("monday", "Monday"),
                    ("tuesday", "Tuesday"),
                    ("wednesday", "Wednesday"),
                    ("thursday", "Thursday"),
                    ("friday", "Friday"),
                    ("saturday", "Saturday"),
                    ("sunday", "Sunday"),
                ]

                EmployeeShiftDay.objects.bulk_create(
                    [EmployeeShiftDay(day=day[0]) for day in days]
                )
        except Exception:
            pass

        # Neon/PgBouncer Workaround for Django < 5.0
        try:
            from django.db.backends.postgresql.features import DatabaseFeatures

            DatabaseFeatures.can_use_server_side_cursors = False
            DatabaseFeatures.can_use_chunked_reads = False
        except ImportError:
            pass
