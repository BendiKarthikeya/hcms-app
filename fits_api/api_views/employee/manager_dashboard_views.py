"""
fits_api/api_views/employee/manager_dashboard_views.py
Manager Dashboard REST API Views

Provides REST endpoints for fetching manager dashboard analytics data including KPIs,
attendance heatmaps, leave forecasting, and turnover risk analysis.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta

from employee.dashboard_service import ManagerDashboardService, ApprovalAnalyticsDashboard


class ManagerKPIDashboardView(APIView):
    """
    GET: Fetch KPI metrics for manager's team

    Returns:
        - total_team_size: Number of direct reports
        - active_today: Employees present today
        - on_leave: Employees on approved leave
        - absent: Employees absent without leave
        - avg_attendance_rate: Team attendance percentage (30-day avg)
        - avg_performance_score: Average team performance (if PMS enabled)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch KPI dashboard data"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = ManagerDashboardService(manager)
        kpis = service.get_team_kpis()

        return Response(
            {"status": "success", "data": kpis, "timestamp": date.today().isoformat()}
        )


class AttendanceHeatmapView(APIView):
    """
    GET: Fetch attendance heatmap data for calendar visualization

    Query Parameters:
        - days_back: Number of days to include (default: 30, max: 90)

    Returns:
        Heatmap data keyed by date (YYYY-MM-DD) with:
        - present: # of employees present
        - absent: # of employees absent
        - late: # of employees who clocked in late
        - total: Total team members expected
        - present_percentage, absent_percentage, late_percentage
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch attendance heatmap"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        days_back = min(int(request.GET.get("days_back", 30)), 90)

        service = ManagerDashboardService(manager)
        heatmap = service.get_attendance_heatmap(days_back=days_back)

        return Response(
            {
                "status": "success",
                "data": heatmap,
                "days_back": days_back,
                "generated_at": date.today().isoformat(),
            }
        )


class LeaveForecasterView(APIView):
    """
    GET: Forecast leave usage for upcoming period

    Query Parameters:
        - forecast_days: Number of days to forecast (default: 90, max: 365)

    Returns:
        - total_leaves_upcoming: Total approved leave requests
        - leaves_by_type: Breakdown by leave type
        - leaves_by_week: Weekly distribution
        - critical_dates: Dates with 3+ team members on leave
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch leave forecast"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        forecast_days = min(int(request.GET.get("forecast_days", 90)), 365)

        service = ManagerDashboardService(manager)
        forecast = service.get_leave_forecast(forecast_days=forecast_days)

        # Convert defaultdicts to regular dicts for JSON serialization
        forecast["leaves_by_type"] = dict(forecast["leaves_by_type"])
        forecast["leaves_by_week"] = dict(forecast["leaves_by_week"])

        return Response(
            {
                "status": "success",
                "data": forecast,
                "forecast_period_days": forecast_days,
                "forecast_until": (
                    date.today() + timedelta(days=forecast_days)
                ).isoformat(),
            }
        )


class TurnoverRiskAssessmentView(APIView):
    """
    GET: Identify employees at risk of attrition

    Risk Calculation Factors:
        - Tenure (>5 years or <1 year)
        - Recent leave patterns (>10 days/month)
        - Performance scores (if PMS enabled)
        - Salary grade (entry-level positions)

    Returns:
        - at_risk_employees: List with risk scores and factors
        - total_risk_score: Sum of all risk scores
        - avg_risk_score: Average risk per employee
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch turnover risk assessment"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = ManagerDashboardService(manager)
        risk_data = service.get_turnover_risk_assessment()

        return Response(
            {
                "status": "success",
                "data": risk_data,
                "assessment_date": date.today().isoformat(),
                "recommendation": _(
                    "Review high-risk employees for retention strategies"
                ),
            }
        )


class DepartmentDistributionView(APIView):
    """
    GET: Get team distribution by department

    Returns:
        dict: Department names mapped to employee counts
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch department distribution"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = ManagerDashboardService(manager)
        distribution = service.get_department_distribution()

        return Response(
            {
                "status": "success",
                "data": distribution,
                "total_team_size": sum(distribution.values()),
            }
        )


class PerformanceReviewsDueView(APIView):
    """
    GET: Get performance reviews due in the next N days

    Query Parameters:
        - days_ahead: Number of days to check (default: 30)

    Returns:
        List of due reviews with:
        - employee_name, employee_id
        - objective_title, due_date
        - days_remaining
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch performance reviews due"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        days_ahead = min(int(request.GET.get("days_ahead", 30)), 365)

        service = ManagerDashboardService(manager)
        reviews_due = service.get_performance_reviews_due(days_ahead=days_ahead)

        return Response(
            {
                "status": "success",
                "data": reviews_due,
                "days_ahead": days_ahead,
                "total_due": len(reviews_due),
            }
        )


class TeamUtilizationMetricsView(APIView):
    """
    GET: Get team utilization and capacity metrics

    Returns:
        - total_capacity: Total capacity in hours/week
        - utilized_capacity: Currently assigned hours
        - utilization_percentage: % of capacity utilized
        - available_capacity: Remaining available hours
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch team utilization metrics"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = ManagerDashboardService(manager)
        utilization = service.get_team_utilization_metrics()

        return Response(
            {
                "status": "success",
                "data": utilization,
                "capacity_health": (
                    _("Healthy")
                    if utilization["utilization_percentage"] <= 100
                    else _("Over-allocated")
                ),
            }
        )


class ComprehensiveDashboardView(APIView):
    """
    GET: Fetch complete dashboard data (all metrics consolidated)

    This is a convenience endpoint that combines all dashboard data.
    Use specific endpoints if you need only certain metrics.

    Returns:
        Complete dashboard object with:
        - kpis, attendance_heatmap, leave_forecast
        - turnover_risk, department_distribution
        - performance_reviews_due, team_utilization
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch comprehensive dashboard"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = ManagerDashboardService(manager)
        dashboard_data = service.get_complete_dashboard_data()

        # Convert defaultdicts to regular dicts
        if "leave_forecast" in dashboard_data:
            dashboard_data["leave_forecast"]["leaves_by_type"] = dict(
                dashboard_data["leave_forecast"]["leaves_by_type"]
            )
            dashboard_data["leave_forecast"]["leaves_by_week"] = dict(
                dashboard_data["leave_forecast"]["leaves_by_week"]
            )

        if "turnover_risk" in dashboard_data:
            dashboard_data["turnover_risk"]["risk_factors"] = dict(
                dashboard_data["turnover_risk"]["risk_factors"]
            )

        return Response(
            {
                "status": "success",
                "data": dashboard_data,
                "generated_at": date.today().isoformat(),
            }
        )


class ApprovalWorkflowAnalyticsView(APIView):
    """
    GET: Get approval workflow performance metrics

    Returns metrics from 7-Stage Approval Workflow including:
        - pending_approvals: # of approvals awaiting action
        - total_approved: Total approved this period
        - total_rejected: Total rejected
        - overdue_count: # of SLA breaches
        - sla_compliance_percentage: % of on-time approvals
        - avg_approval_time: Average time to approve (hours)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch approval workflow analytics"""
        try:
            manager = request.user.employee_get
        except AttributeError:
            return Response(
                {"error": _("User is not an employee")},
                status=status.HTTP_403_FORBIDDEN,
            )

        analytics = ApprovalAnalyticsDashboard(manager)
        metrics = analytics.get_approval_metrics()

        return Response(
            {
                "status": "success",
                "data": metrics,
                "timestamp": date.today().isoformat(),
            }
        )
