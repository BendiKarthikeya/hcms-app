"""
Admin interface for Omani Labour Law Compliance
"""

from django.contrib import admin

from .models import OmaniComplianceAudit, OmaniLabourLawConfig, OmaniTaxCalculation


@admin.register(OmaniLabourLawConfig)
class OmaniLabourLawConfigAdmin(admin.ModelAdmin):
    """Admin interface for Omani Labour Law configuration"""

    list_display = [
        "company",
        "annual_leave_days",
        "maternity_leave_days",
        "daily_working_hours",
        "pasi_enabled",
    ]

    list_filter = ["company", "pasi_enabled"]

    search_fields = ["company__name"]


@admin.register(OmaniComplianceAudit)
class OmaniComplianceAuditAdmin(admin.ModelAdmin):
    """Admin interface for Omani compliance audits"""

    list_display = ["employee", "check_type", "status", "created_at"]

    list_filter = ["check_type", "status", "created_at"]

    search_fields = [
        "employee__employee_first_name",
        "employee__employee_last_name",
        "check_type",
    ]

    readonly_fields = ["created_at"]


@admin.register(OmaniTaxCalculation)
class OmaniTaxCalculationAdmin(admin.ModelAdmin):
    """Admin interface for Omani tax calculations"""

    list_display = ["employee", "month", "gross_salary", "tax_amount", "tax_rate"]

    list_filter = ["month"]

    search_fields = ["employee__employee_first_name", "employee__employee_last_name"]

    readonly_fields = ["created_at"]
