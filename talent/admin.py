"""
Admin configuration for Talent & Succession Management module
"""

from django.contrib import admin

from .models import (
    TalentProfile,
    CriticalRole,
    SuccessionPlan,
    NineBoxMatrix,
    CareerPath,
    TalentReview,
    RetentionRisk,
    LeadershipPipeline,
)


@admin.register(TalentProfile)
class TalentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "performance_level",
        "potential_level",
        "readiness_level",
        "last_assessment_date",
    )
    list_filter = ("performance_level", "potential_level", "readiness_level")
    search_fields = ("employee__employee_first_name", "employee__employee_last_name")
    readonly_fields = ("last_assessment_date",)


@admin.register(CriticalRole)
class CriticalRoleAdmin(admin.ModelAdmin):
    list_display = (
        "role_name",
        "department",
        "job_position",
        "criticality_level",
        "vacancy_risk",
    )
    list_filter = ("criticality_level", "vacancy_risk", "department", "company")
    search_fields = ("role_name", "description")


@admin.register(SuccessionPlan)
class SuccessionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "critical_role",
        "primary_successor",
        "secondary_successor",
        "status",
        "estimated_timeline_months",
    )
    list_filter = ("status", "readiness_level")
    search_fields = (
        "critical_role__role_name",
        "primary_successor__employee_first_name",
    )
    readonly_fields = ("created_date", "last_updated")


@admin.register(NineBoxMatrix)
class NineBoxMatrixAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "quadrant",
        "performance_score",
        "potential_score",
        "assessment_date",
    )
    list_filter = ("quadrant", "assessment_date")
    search_fields = ("employee__employee_first_name", "employee__employee_last_name")


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "current_position",
        "target_position",
        "status",
        "target_completion_date",
    )
    list_filter = ("status", "target_completion_date")
    search_fields = ("employee__employee_first_name", "employee__employee_last_name")


@admin.register(TalentReview)
class TalentReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "review_date", "facilitator", "next_review_date")
    list_filter = ("review_date", "next_review_date")
    search_fields = ("title", "description")
    filter_horizontal = ("participants",)


@admin.register(RetentionRisk)
class RetentionRiskAdmin(admin.ModelAdmin):
    list_display = ("employee", "risk_level", "assessed_date", "next_assessment_date")
    list_filter = ("risk_level", "assessed_date")
    search_fields = ("employee__employee_first_name", "employee__employee_last_name")


@admin.register(LeadershipPipeline)
class LeadershipPipelineAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leadership_level",
        "target_level",
        "progress_percentage",
        "mentor",
    )
    list_filter = ("leadership_level", "target_level")
    search_fields = ("employee__employee_first_name", "employee__employee_last_name")
