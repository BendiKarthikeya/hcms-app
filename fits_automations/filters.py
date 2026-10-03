"""
fits_automations/filters.py
"""

from fits.filters import FitsFilterSet, django_filters
from fits_automations.models import MailAutomation


class AutomationFilter(FitsFilterSet):
    """
    AutomationFilter
    """

    search = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = MailAutomation
        fields = "__all__"
