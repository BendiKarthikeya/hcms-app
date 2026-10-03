"""
Leave Request Approval API URLs
Location: fits_api/api_urls/leave_approval_urls.py
"""

from django.urls import path
from fits_api.api_views.leave.approval_views import (
    ApprovalDashboardView,
    ApproveLeaveRequestView,
    RejectLeaveRequestView,
    BulkApproveView,
    CreateDelegationView,
    ApprovalOverrideView,
    ApprovalSLAStatusView,
)

app_name = "leave_approvals"

urlpatterns = [
    # Dashboard
    path(
        "approvals/dashboard/",
        ApprovalDashboardView.as_view(),
        name="approval-dashboard",
    ),
    # Single approval actions
    path(
        "approvals/<int:approval_id>/approve/",
        ApproveLeaveRequestView.as_view(),
        name="approve-request",
    ),
    path(
        "approvals/<int:approval_id>/reject/",
        RejectLeaveRequestView.as_view(),
        name="reject-request",
    ),
    # Bulk operations
    path("approvals/bulk-approve/", BulkApproveView.as_view(), name="bulk-approve"),
    # Delegation management
    path(
        "approvals/delegations/",
        CreateDelegationView.as_view(),
        name="create-delegation",
    ),
    # Override (HR admin only)
    path(
        "approvals/<int:approval_id>/override/",
        ApprovalOverrideView.as_view(),
        name="override-approval",
    ),
    # SLA monitoring
    path("approvals/sla-status/", ApprovalSLAStatusView.as_view(), name="sla-status"),
]
