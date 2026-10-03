"""
URL configuration for Omani Labour Law Compliance
"""

from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "omani_compliance"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="config/", permanent=False),
        name="omani_root",
    ),
    path(
        "config/",
        views.OmaniComplianceConfigView.as_view(),
        name="omani_config",
    ),
    path(
        "audit/",
        views.OmaniComplianceAuditView.as_view(),
        name="omani_audit",
    ),
    path(
        "tax-calculations/",
        views.OmaniTaxCalculationsView.as_view(),
        name="omani_tax_calculations",
    ),
    path(
        "reports/compliance/",
        views.OmaniComplianceReportView.as_view(),
        name="omani_compliance_report",
    ),
]
