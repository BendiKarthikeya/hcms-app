"""
Admin configuration for Expenses & Travel Management module
"""

from django.contrib import admin

from .models import (
    ExpenseCategory,
    TravelRequest,
    ExpenseClaim,
    Receipt,
    PerDiemRate,
    ExpensePolicy,
    ExpenseReport,
    ExpenseReportItem,
)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "description")
    list_filter = ("company",)
    search_fields = ("name", "description")


@admin.register(TravelRequest)
class TravelRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "travel_type",
        "destination",
        "departure_date",
        "return_date",
        "status",
    )
    list_filter = ("travel_type", "status", "departure_date")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "destination",
        "purpose",
    )
    readonly_fields = ("submitted_date", "approval_date")


@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "category",
        "amount",
        "currency",
        "status",
        "submitted_date",
    )
    list_filter = ("status", "category", "currency", "expense_date")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "description",
    )
    readonly_fields = ("submitted_date", "approval_date", "local_amount")


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "expense_claim",
        "description",
        "amount",
        "receipt_date",
        "uploaded_at",
    )
    list_filter = ("receipt_date", "uploaded_at")
    search_fields = ("expense_claim__description", "description")
    readonly_fields = ("uploaded_at",)


@admin.register(PerDiemRate)
class PerDiemRateAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "city",
        "rate_amount",
        "currency",
        "effective_date",
        "company",
    )
    list_filter = ("country", "city", "currency", "company", "effective_date")
    search_fields = ("country", "city")
    unique_together = ("country", "city", "effective_date")


@admin.register(ExpensePolicy)
class ExpensePolicyAdmin(admin.ModelAdmin):
    list_display = (
        "policy_name",
        "category",
        "max_amount",
        "approval_levels",
        "is_active",
        "company",
    )
    list_filter = (
        "is_active",
        "category",
        "requires_approval",
        "requires_receipt",
        "company",
    )
    search_fields = ("policy_name", "description")


@admin.register(ExpenseReport)
class ExpenseReportAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "report_period_start",
        "report_period_end",
        "total_amount",
        "status",
    )
    list_filter = ("status", "report_period_start", "submitted_date")
    search_fields = ("employee__employee_first_name", "employee__employee_last_name")
    readonly_fields = ("submitted_date", "approved_date", "total_amount")


@admin.register(ExpenseReportItem)
class ExpenseReportItemAdmin(admin.ModelAdmin):
    list_display = ("expense_report", "expense_claim")
    list_filter = ("expense_report",)
    search_fields = (
        "expense_report__employee__employee_first_name",
        "expense_claim__description",
    )
    unique_together = ("expense_report", "expense_claim")
