"""
fits_audit/urls.py
"""

from django.urls import path
from fits_audit import views

app_name = "fits_audit"

urlpatterns = [
    path("audit-dashboard/", views.audit_dashboard, name="audit-dashboard"),
    path("audit-detail/<int:log_id>/", views.audit_detail, name="audit-detail"),
]
