"""
fits_api/api_urls/employee_dashboard_urls.py
Manager Dashboard API URL Routing

Provides REST API endpoints for manager dashboard analytics.
"""

from django.urls import path
from fits_api.api_views.employee.manager_dashboard_views import (
    ManagerKPIDashboardView,
    AttendanceHeatmapView,
    LeaveForecasterView,
    TurnoverRiskAssessmentView,
    DepartmentDistributionView,
    PerformanceReviewsDueView,
    TeamUtilizationMetricsView,
    ComprehensiveDashboardView,
    ApprovalWorkflowAnalyticsView,
)

app_name = "employee_dashboard"

urlpatterns = [
    # Comprehensive endpoint (all data)
    path(
        "comprehensive/",
        ComprehensiveDashboardView.as_view(),
        name="comprehensive-dashboard",
    ),
    # Individual metric endpoints
    path("kpi/", ManagerKPIDashboardView.as_view(), name="kpi-dashboard"),
    path(
        "attendance-heatmap/",
        AttendanceHeatmapView.as_view(),
        name="attendance-heatmap",
    ),
    path("leave-forecast/", LeaveForecasterView.as_view(), name="leave-forecast"),
    path("turnover-risk/", TurnoverRiskAssessmentView.as_view(), name="turnover-risk"),
    path(
        "department-distribution/",
        DepartmentDistributionView.as_view(),
        name="department-distribution",
    ),
    path(
        "performance-reviews-due/",
        PerformanceReviewsDueView.as_view(),
        name="performance-reviews-due",
    ),
    path(
        "team-utilization/",
        TeamUtilizationMetricsView.as_view(),
        name="team-utilization",
    ),
    path(
        "approval-analytics/",
        ApprovalWorkflowAnalyticsView.as_view(),
        name="approval-analytics",
    ),
]
