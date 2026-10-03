"""
employee/dashboard_service.py
Manager Dashboard Analytics Service Layer

This module provides comprehensive analytics and business logic for manager dashboards,
including KPI calculations, attendance heatmaps, leave forecasting, and risk analysis.
"""

from datetime import timedelta, date
from django.db.models import Count, Sum, F
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from collections import defaultdict

from employee.models import Employee, EmployeeWorkInformation


class ManagerDashboardService:
    """
    Service layer for manager dashboard analytics and reporting.
    Calculates KPIs, attendance patterns, leave forecasts, and risk indicators.
    """

    def __init__(self, manager_employee):
        """Initialize with manager employee instance"""
        self.manager = manager_employee
        self.team_members = self._get_team_members()
        self.today = date.today()

    def _get_team_members(self):
        """Get all direct subordinates of manager"""
        return Employee.objects.filter(
            employee_work_info__reporting_manager_id=self.manager, is_active=True
        ).distinct()

    # ==================== KPI METRICS ====================

    def get_team_kpis(self):
        """
        Calculate key performance indicators for the team.
        Returns:
            dict: KPI metrics including attendance %, leave usage, etc.
        """
        team_members = self.team_members
        kpis = {
            "total_team_size": team_members.count(),
            "active_today": 0,
            "on_leave": 0,
            "absent": 0,
            "avg_attendance_rate": 0.0,
            "avg_performance_score": 0.0,
        }
        
        if apps.is_installed('leave'):
            from leave.models import LeaveRequest
            # On leave today
            today_leaves = LeaveRequest.objects.filter(
                employee_id__in=team_members,
                start_date__lte=self.today,
                end_date__gte=self.today,
                status='approved'
            )
            kpis['on_leave'] = today_leaves.count()


        if apps.is_installed('attendance'):
            from attendance.models import Attendance
            
            # Today's attendance stats
            today_attendance = Attendance.objects.filter(
                employee_id__in=team_members,
                attendance_date=self.today,
                attendance_validated=True
            )
            kpis['active_today'] = today_attendance.count()

            # calculate leave first
            kpis['on_leave'] = today_leaves.count()

            # FIX: exclude leave from absent
            kpis['absent'] = team_members.count() - kpis['active_today'] - kpis['on_leave']
            
            # Attendance rate for last 30 days
            thirty_days_ago = self.today - timedelta(days=30)
            total_expected = team_members.count() * 20  # ~20 working days/month
            total_marked = Attendance.objects.filter(
                employee_id__in=team_members,
                attendance_date__range=[thirty_days_ago, self.today],
                attendance_validated=True
            ).count()
            
            if total_expected > 0:
                kpis['avg_attendance_rate'] = round((total_marked / total_expected) * 100, 2)
        
        
        

            from attendance.models import Attendance

            # Today's attendance stats
            today_attendance = Attendance.objects.filter(
                employee_id__in=team_members,
                attendance_date=self.today,
                attendance_validated=True,
            )

            kpis['active_today'] = today_attendance.count()

            # calculate leave first
            kpis['on_leave'] = today_leaves.count()

            # FIX: exclude leave from absent
            kpis['absent'] = team_members.count() - kpis['active_today'] - kpis['on_leave']
            

            # Attendance rate for last 30 days
            thirty_days_ago = self.today - timedelta(days=30)
            total_expected = team_members.count() * 20  # ~20 working days/month
            total_marked = Attendance.objects.filter(
                employee_id__in=team_members,
                attendance_date__range=[thirty_days_ago, self.today],
                attendance_validated=True,
            ).count()

            if total_expected > 0:

                kpis["avg_attendance_rate"] = round(
                    (total_marked / total_expected) * 100, 2
                )

        if apps.is_installed("leave"):
            from leave.models import LeaveRequest

            # On leave today
            today_leaves = LeaveRequest.objects.filter(
                employee_id__in=team_members,
                start_date__lte=self.today,
                end_date__gte=self.today,
                status="approved",
            )
            kpis["on_leave"] = today_leaves.count()


                
        
        
        

        # Performance scores (if PMS installed)
        if apps.is_installed("pms"):
            from pms.models import EmployeeObjective

            objectives = EmployeeObjective.objects.filter(employee_id__in=team_members)
            if objectives.exists():
                total_score = sum([obj.get_progress_percentage() for obj in objectives])
                kpis["avg_performance_score"] = round(
                    total_score / objectives.count(), 2
                )

        return kpis

    # ==================== ATTENDANCE HEATMAP ====================

    def get_attendance_heatmap(self, days_back=30):
        """
        Minimal working attendance heatmap (no late logic)
        """
        heatmap_data = defaultdict(
            lambda: {"present": 0, "absent": 0, "late": 0, "total": 0}
        )

        if not apps.is_installed("attendance"):
            return heatmap_data

        from attendance.models import Attendance

        start_date = self.today - timedelta(days=days_back)
        end_date = self.today

        attendances = Attendance.objects.filter(
            employee_id__in=self.team_members,
            attendance_date__range=[start_date, end_date]
        )

        # Aggregate by date
        for attendance in attendances:
            date_key = attendance.attendance_date.strftime('%Y-%m-%d')
            heatmap_data[date_key]['total'] += 1
            
            if attendance.attendance_validated:
                heatmap_data[date_key]['present'] += 1
            else:
                heatmap_data[date_key]['absent'] += 1
        
        # Percentages
        for date_key, stats in heatmap_data.items():
            if stats['total'] > 0:
                stats['present_percentage'] = round((stats['present'] / stats['total']) * 100, 2)
                stats['absent_percentage'] = round((stats['absent'] / stats['total']) * 100, 2)
                stats['late_percentage'] = 0
        
        return dict(heatmap_data)
    
    
    # ==================== LEAVE FORECASTING ====================

    def get_leave_forecast(self, forecast_days=90):
        """
        Forecast leave usage for the next N days.
        Returns:
            dict: Forecasted leave data with counts and patterns
        """
        forecast_data = {
            "total_leaves_upcoming": 0,
            "leaves_by_type": defaultdict(int),
            "leaves_by_week": defaultdict(int),
            "critical_dates": [],  # Dates with 3+ team members on leave
        }

        if not apps.is_installed("leave"):
            return forecast_data
        
        from leave.models import LeaveRequest
        
        start_date = self.today
        end_date = self.today + timedelta(days=forecast_days)

        upcoming_leaves = LeaveRequest.objects.filter(
            employee_id__in=self.team_members,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status="approved",
        )

        forecast_data["total_leaves_upcoming"] = upcoming_leaves.count()

        # Group by leave type
        forecast_data['leaves_by_type'] = {}

        for leave in upcoming_leaves:
           lt = str(leave.leave_type_id)  # safe fallback
           forecast_data['leaves_by_type'][lt] = forecast_data['leaves_by_type'].get(lt, 0) + 1
        
        # Find critical leave dates (3+ people)
        leave_count_by_date = defaultdict(int)
        for leave in upcoming_leaves:
            current_date = leave.start_date
            while current_date <= leave.end_date:
                leave_count_by_date[current_date.strftime("%Y-%m-%d")] += 1
                current_date += timedelta(days=1)

        forecast_data["critical_dates"] = [
            date_str for date_str, count in leave_count_by_date.items() if count >= 3
        ]

        # Weekly breakdown
        for week_offset in range((forecast_days // 7) + 1):
            week_start = start_date + timedelta(weeks=week_offset)
            week_end = week_start + timedelta(days=6)
            week_key = f"Week {week_offset + 1}"

            week_leaves = (
                upcoming_leaves.filter(
                    start_date__lte=week_end, end_date__gte=week_start
                )
                .values("employee_id")
                .distinct()
                .count()
            )

            forecast_data["leaves_by_week"][week_key] = week_leaves

        # Convert defaultdicts to regular dicts for JSON serialization
        forecast_data["leaves_by_type"] = dict(forecast_data["leaves_by_type"])
        forecast_data["leaves_by_week"] = dict(forecast_data["leaves_by_week"])

        return forecast_data

    # ==================== TURNOVER RISK ANALYSIS ====================

    def get_turnover_risk_assessment(self):
        """
        Identify employees at risk of attrition based on multiple factors.
        Returns:
            dict: Risk assessment with flagged employees and risk scores
        """
        risk_data = {
            "at_risk_employees": [],
            "total_risk_score": 0.0,
            "risk_factors": defaultdict(list),
        }

        team_members = self.team_members

        for employee in team_members:
            risk_score = 0.0
            risk_factors = []

            # Factor 1: Tenure (employees > 5 years or < 1 year)
            joining = getattr(employee, 'date_of_joining', None)
            tenure_years = None

            if joining:
                tenure_years = (self.today - joining).days / 365.25

            if tenure_years is not None and tenure_years > 5:
                risk_score += 15
                risk_factors.append(_("Long tenure (>5 years)"))
            elif tenure_years is not None and tenure_years < 1:
                risk_score += 20
                risk_factors.append(_("New employee (<1 year)"))
            
            # Factor 2: Recent leave patterns (high leave usage)
            if apps.is_installed("leave"):
                from leave.models import LeaveRequest
                
                last_30_days_leaves = LeaveRequest.objects.filter(
                    employee_id=employee,
                    start_date__gte=self.today - timedelta(days=30),
                    status='approved'
                ).aggregate(days=Sum('requested_days'))['days'] or 0
                
                if last_30_days_leaves > 10:
                    risk_score += 25
                    risk_factors.append(_("High leave usage (>10 days/month)"))
            
            # Factor 3: Performance concerns (if PMS installed)
            if apps.is_installed('pms'):
                from pms.models import EmployeeObjective
                
                recent_objectives = EmployeeObjective.objects.filter(
                    employee_id=employee,
                    start_date__gte=self.today - timedelta(days=180)
                )
                if recent_objectives.exists():
                    avg_progress = (
                        sum(
                            [obj.get_progress_percentage() for obj in recent_objectives]
                        )
                        / recent_objectives.count()
                    )
                    if avg_progress < 50:
                        risk_score += 30
                        risk_factors.append(_("Low performance (<50%)"))

            # Factor 4: Salary grade (entry level = higher risk)
            try:
                work_info = employee.employee_work_info
                if work_info and hasattr(work_info, "salary_grade"):
                    # Entry level positions have higher turnover
                    if "Entry" in str(work_info.salary_grade):
                        risk_score += 10
                        risk_factors.append(_("Entry-level position"))
            except:
                pass

            if risk_score > 0:
                risk_data["at_risk_employees"].append(
                    {
                        "employee_id": employee.id,
                        "name": employee.get_full_name(),
                        "risk_score": round(risk_score, 2),
                        "risk_factors": risk_factors,
                        "risk_level": _("High")
                        if risk_score >= 60
                        else (_("Medium") if risk_score >= 40 else _("Low")),
                    }
                )

            risk_data["total_risk_score"] += risk_score

        # Sort by risk score (highest first)
        risk_data["at_risk_employees"].sort(key=lambda x: x["risk_score"], reverse=True)

        if team_members.count() > 0:
            risk_data["avg_risk_score"] = round(
                risk_data["total_risk_score"] / team_members.count(), 2
            )

        return risk_data

    # ==================== DEPARTMENT BREAKDOWN ====================

    def get_department_distribution(self):
        """
        Get team distribution by department.
        Returns:
            dict: Department names and employee counts
        """
        dept_distribution = defaultdict(int)

        team_work_info = EmployeeWorkInformation.objects.filter(
            employee_id__in=self.team_members
        ).select_related("department_id")

        for work_info in team_work_info:
            if work_info.department_id:
                dept_distribution[work_info.department_id.department] += 1
            else:
                dept_distribution["Unassigned"] += 1

        return dict(dept_distribution)

    # ==================== PERFORMANCE REVIEW DUE ====================

    def get_performance_reviews_due(self, days_ahead=30):
        """
        Get performance reviews due for team members in the next N days.
        Returns:
            list: Employees with due performance reviews
        """
        due_reviews = []

        if not apps.is_installed("pms"):
            return due_reviews

        from pms.models import EmployeeObjective

        end_date = self.today + timedelta(days=days_ahead)

        upcoming_reviews = EmployeeObjective.objects.filter(
            employee_id__in=self.team_members,
            end_date__range=[self.today, end_date],
            status__in=["in_progress", "pending_review"],
        ).select_related("employee_id")

        for objective in upcoming_reviews:
            days_remaining = (objective.end_date - self.today).days
            due_reviews.append(
                {
                    "employee_id": objective.employee_id.id,
                    "employee_name": objective.employee_id.get_full_name(),
                    "objective_title": objective.title,
                    "due_date": objective.end_date.strftime("%Y-%m-%d"),
                    "days_remaining": days_remaining,
                }
            )

        return due_reviews

    # ==================== TEAM UTILIZATION ====================

    def get_team_utilization_metrics(self):
        """
        Calculate team utilization and capacity metrics.
        Returns:
            dict: Utilization percentages and capacity data
        """
        metrics = {
            "total_capacity": 0,
            "utilized_capacity": 0,
            "utilization_percentage": 0.0,
            "available_capacity": 0,
        }

        if not apps.is_installed("project"):
            return metrics

        from project.models import Task

        team_members = self.team_members
        total_team = team_members.count()

        if total_team == 0:
            return metrics

        # Assume standard capacity is 40 hours/week per person
        metrics["total_capacity"] = total_team * 40

        # Get assigned tasks for current week
        start_of_week = self.today - timedelta(days=self.today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        assigned_tasks = Task.objects.filter(
            task_members__in=team_members,
            end_date__range=[start_of_week, end_of_week],
            status__in=['open', 'in_progress']
        ).distinct()

        # Task model does not provide estimated hours in all deployments.
        # Use conservative fixed-hour estimation to avoid field coupling.
        estimated_hours_per_task = 5
        total_hours = assigned_tasks.count() * estimated_hours_per_task
        metrics['utilized_capacity'] = min(total_hours, metrics['total_capacity'])
        metrics['available_capacity'] = max(0, metrics['total_capacity'] - metrics['utilized_capacity'])
        
        if metrics['total_capacity'] > 0:
            metrics['utilization_percentage'] = round(
                (metrics['utilized_capacity'] / metrics['total_capacity']) * 100, 2
            )

        return metrics

    # ==================== CONSOLIDATED DASHBOARD DATA ====================

    def get_complete_dashboard_data(self):
        """
        Get all dashboard data consolidated.
        Returns:
            dict: Complete dashboard dataset
        """
        return {
            "kpis": self.get_team_kpis(),
            "attendance_heatmap": self.get_attendance_heatmap(),
            "leave_forecast": self.get_leave_forecast(),
            "turnover_risk": self.get_turnover_risk_assessment(),
            "department_distribution": self.get_department_distribution(),
            "performance_reviews_due": self.get_performance_reviews_due(),
            "team_utilization": self.get_team_utilization_metrics(),
        }


class ApprovalAnalyticsDashboard:
    """
    Analytics for 7-Stage Approval Workflow (from Phase 1).
    Provides insights into approval performance and SLA compliance.
    """

    def __init__(self, manager_employee):
        """Initialize with manager employee instance"""
        self.manager = manager_employee
        self.today = date.today()

    def get_approval_metrics(self):
        """Get approval workflow performance metrics"""
        if not apps.is_installed("leave"):
            return {}

        try:
            from leave.models_enhanced_approvals import (
                ApprovalRequest,
                ApprovalMetrics,
                ApprovalSLAAlert,
            )

            company = (
                self.manager.employee_work_info.company_id
                if self.manager.employee_work_info
                else None
            )

            metrics = {
                "pending_approvals": ApprovalRequest.objects.filter(
                    approver=self.manager, status="pending"
                ).count(),
                "total_approved": ApprovalRequest.objects.filter(
                    approver=self.manager, status="approved"
                ).count(),
                "total_rejected": ApprovalRequest.objects.filter(
                    approver=self.manager, status="rejected"
                ).count(),
                "overdue_count": ApprovalRequest.objects.filter(
                    approver=self.manager, status="pending", sla_deadline__lt=self.today
                ).count(),
            }

            # SLA compliance
            current_month_start = self.today.replace(day=1)
            current_month_metrics = ApprovalMetrics.objects.filter(
                company=company, approval_period=current_month_start
            ).first()

            if current_month_metrics:
                metrics["sla_compliance_percentage"] = round(
                    (
                        current_month_metrics.on_time_count
                        / max(current_month_metrics.total_approvals, 1)
                    )
                    * 100,
                    2,
                )
                metrics["avg_approval_time"] = round(
                    current_month_metrics.avg_approval_time_hours, 2
                )

            return metrics
        except ImportError:
            return {}
