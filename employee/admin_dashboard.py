"""
employee/admin_dashboard.py
Django Admin Interface for Manager Dashboard Configuration

Allows administrators to configure dashboard settings, manage team structures,
and view dashboard analytics history.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django import forms

from employee.models import Employee, EmployeeWorkInformation


class ManagerDashboardSettingsForm(forms.ModelForm):
    """Form for dashboard configuration"""

    class Meta:
        model = Employee
        fields = []  # Configuration stored in settings model if needed


@admin.register(Employee)
class ManagerDashboardAdmin(admin.ModelAdmin):
    """Extended admin for manager dashboard with analytics"""

    list_display = (
        "employee_first_name",
        "employee_last_name",
        "is_manager",
        "team_size",
        "team_kpis_link",
    )
    list_filter = ("is_active", "employee_work_info__department_id")
    search_fields = ("employee_first_name", "employee_last_name", "email")

    readonly_fields = ("team_size", "team_members_list", "performance_summary")

    def is_manager(self, obj):
        """Check if employee is a manager"""
        has_subordinates = obj.reporting_manager.exists()
        if has_subordinates:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Manager</span>'
            )
        return format_html('<span style="color: gray;">—</span>')

    is_manager.short_description = _("Manager Status")

    def team_size(self, obj):
        """Display team size"""
        subordinates = Employee.objects.filter(
            employee_work_info__reporting_manager_id=obj, is_active=True
        ).count()
        if subordinates > 0:
            return format_html(
                '<span style="background-color: #e3f2fd; padding: 3px 8px; '
                'border-radius: 12px;">{} direct reports</span>',
                subordinates,
            )
        return "—"

    team_size.short_description = _("Team Size")

    def team_members_list(self, obj):
        """Display list of team members"""
        team = Employee.objects.filter(
            employee_work_info__reporting_manager_id=obj, is_active=True
        )[:10]
        if not team:
            return _("No direct reports")

        html_list = '<ul style="list-style-type: none; padding: 0;">'
        for member in team:
            html_list += f"<li>• {member.get_full_name()}</li>"
        if team.count() >= 10:
            html_list += f"<li><em>+ {team.count() - 10} more...</em></li>"
        html_list += "</ul>"

        return format_html(html_list)

    team_members_list.short_description = _("Team Members")

    def performance_summary(self, obj):
        """Display performance summary"""
        # This would show dashboard analytics summary
        return _("View dashboard for full analytics")

    performance_summary.short_description = _("Performance Summary")

    def team_kpis_link(self, obj):
        """Link to dashboard KPIs"""
        if obj.reporting_manager.exists():
            dashboard_url = f"/api/employee/dashboard/kpi/?manager_id={obj.id}"
            return format_html(
                '<a class="button" href="{}" target="_blank">View KPIs</a>',
                dashboard_url,
            )
        return "—"

    team_kpis_link.short_description = _("Dashboard KPIs")

    fieldsets = (
        (
            _("Personal Information"),
            {"fields": ("employee_first_name", "employee_last_name", "email", "phone")},
        ),
        (_("Work Information"), {"fields": ("employee_work_info",)}),
        (
            _("Team Information (Read-only)"),
            {
                "fields": ("team_size", "team_members_list", "performance_summary"),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
    )


class DepartmentTeamAnalyticsAdmin(admin.ModelAdmin):
    """Admin for department-level team analytics"""

    list_display = ("department_name", "total_staff", "active_staff", "analytics_link")

    def department_name(self, obj):
        """Display department name"""
        return getattr(obj, "department", obj)

    department_name.short_description = _("Department")

    def total_staff(self, obj):
        """Count total staff in department"""
        try:
            from base.models import Department

            dept = Department.objects.get(department=obj)
            staff = EmployeeWorkInformation.objects.filter(department_id=dept).count()
            return staff
        except:
            return 0

    total_staff.short_description = _("Total Staff")

    def active_staff(self, obj):
        """Count active staff"""
        try:
            from base.models import Department

            dept = Department.objects.get(department=obj)
            staff = EmployeeWorkInformation.objects.filter(
                department_id=dept, employee_id__is_active=True
            ).count()
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>', staff
            )
        except:
            return 0

    active_staff.short_description = _("Active Staff")

    def analytics_link(self, obj):
        """Link to department analytics"""
        return format_html(
            '<a class="button" href="/admin/dashboard/department/{}/analytics/">View Analytics</a>',
            obj.id if hasattr(obj, "id") else "",
        )

    analytics_link.short_description = _("Analytics")
