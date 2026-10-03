"""
App configuration for Talent & Succession Planning module
"""

from django.apps import AppConfig


class TalentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "talent"
    verbose_name = "Talent & Succession Planning"
