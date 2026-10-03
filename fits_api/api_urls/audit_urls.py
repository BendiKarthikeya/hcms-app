"""
Audit Log API URLs
Location: fits_api/api_urls/audit_urls.py
"""

from django.urls import path
from fits_api.api_views.audit.views import (
    AuditLogListView,
    AuditStatsView,
    AuditDetailView,
)

app_name = "audit"

urlpatterns = [
    # List and search audit logs
    path("logs/", AuditLogListView.as_view(), name="audit-log-list"),
    # Get audit statistics
    path("logs/stats/", AuditStatsView.as_view(), name="audit-stats"),
    # Get details of specific record's history
    path(
        "logs/<str:model_name>/<str:record_id>/",
        AuditDetailView.as_view(),
        name="audit-detail",
    ),
]
