"""
admin.py

This page is used to register base models with admins site.
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from base.models import (
    Announcement,
    Attachment,
    Company,
    CompanyLeaves,
    DashboardEmployeeCharts,
    Department,
    DynamicEmailConfiguration,
    DynamicPagination,
    EmailLog,
    EmployeeShift,
    EmployeeShiftDay,
    EmployeeShiftSchedule,
    EmployeeType,
    Holidays,
    HRUser,
    JobPosition,
    JobRole,
    MultipleApprovalCondition,
    MultipleApprovalManagers,
    PenaltyAccounts,
    RotatingShift,
    RotatingShiftAssign,
    RotatingWorkType,
    RotatingWorkTypeAssign,
    ShiftRequest,
    ShiftRequestComment,
    Tags,
    WorkType,
    WorkTypeRequest,
    WorkTypeRequestComment,
)

# Register your models here.

admin.site.register(Company)
admin.site.register(Department, SimpleHistoryAdmin)
admin.site.register(JobPosition)
admin.site.register(JobRole)
admin.site.register(EmployeeShift)
admin.site.register(EmployeeShiftSchedule)
admin.site.register(EmployeeShiftDay)
admin.site.register(EmployeeType)
admin.site.register(WorkType)
admin.site.register(RotatingWorkType)
admin.site.register(RotatingWorkTypeAssign)
admin.site.register(RotatingShift)
admin.site.register(RotatingShiftAssign)
admin.site.register(ShiftRequest)
admin.site.register(WorkTypeRequest)
admin.site.register(Tags)
admin.site.register(DynamicEmailConfiguration)
admin.site.register(MultipleApprovalManagers)
admin.site.register(ShiftRequestComment)
admin.site.register(WorkTypeRequestComment)
admin.site.register(DynamicPagination)
admin.site.register(Announcement)
admin.site.register(Attachment)
admin.site.register(EmailLog)
admin.site.register(DashboardEmployeeCharts)
admin.site.register(Holidays)
admin.site.register(CompanyLeaves)
admin.site.register(PenaltyAccounts)
admin.site.register(MultipleApprovalCondition)


class HRUserAdmin(admin.ModelAdmin):
    """
    Admin class for managing HR Users
    """

    list_display = (
        "get_employee_name",
        "is_hr_staff",
        "can_view_all_companies",
        "can_manage_employees",
        "can_manage_leaves",
        "can_manage_attendance",
        "can_manage_payroll",
        "can_manage_recruitment",
        "can_manage_assets",
        "can_manage_biometric",
        "can_manage_pms",
        "can_manage_reports",
        "can_manage_onboarding",
        "can_manage_offboarding",
        "can_manage_projects",
        "can_manage_omani_compliance",
        "can_manage_expenses",
        "can_manage_learning",
        "can_manage_fits_audit",
        "can_manage_helpdesk",
        "can_manage_talent",
        "created_at",
    )
    list_filter = ("is_hr_staff", "can_view_all_companies", "created_at")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "employee__email",
    )
    fieldsets = (
        ("Employee Information", {"fields": ("employee",)}),
        ("HR Staff Status", {"fields": ("is_hr_staff", "can_view_all_companies")}),
        (
            "Module Permissions",
            {
                "fields": (
                    "can_manage_employees",
                    "can_manage_leaves",
                    "can_manage_attendance",
                    "can_manage_payroll",
                    "can_manage_recruitment",
                    "can_manage_assets",
                    "can_manage_biometric",
                    "can_manage_pms",
                    "can_manage_reports",
                    "can_manage_onboarding",
                    "can_manage_offboarding",
                    "can_manage_projects",
                    "can_manage_omani_compliance",
                    "can_manage_expenses",
                    "can_manage_learning",
                    "can_manage_fits_audit",
                    "can_manage_helpdesk",
                    "can_manage_talent",
                ),
                "description": "Select which HR modules this staff member can access",
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_employee_name(self, obj):
        return f"{obj.employee.employee_first_name} {obj.employee.employee_last_name}"

    get_employee_name.short_description = "Employee Name"


admin.site.register(HRUser, HRUserAdmin)
