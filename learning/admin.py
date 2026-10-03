"""
Admin configuration for Learning & Development module
"""

from django.contrib import admin

from .models import (
    Certification,
    CourseCategory,
    CourseEnrollment,
    EmployeeCertification,
    EmployeeSkill,
    LearningPlan,
    LearningPlanItem,
    Skill,
    TrainingBudget,
    TrainingCourse,
)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "description")
    list_filter = ("company",)
    search_fields = ("name", "description")


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "format",
        "level",
        "duration_hours",
        "cost",
        "is_active",
    )
    list_filter = ("category", "format", "level", "is_active", "company")
    search_fields = ("name", "description", "instructor")
    filter_horizontal = ()


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "course",
        "status",
        "enrollment_date",
        "progress_percentage",
    )
    list_filter = ("status", "course", "enrollment_date")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "course__name",
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "description")
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ("employee", "skill", "proficiency_level", "years_experience")
    list_filter = ("proficiency_level", "skill")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "skill__name",
    )


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "issuing_authority", "validity_period_months")
    search_fields = ("name", "issuing_authority", "description")


@admin.register(EmployeeCertification)
class EmployeeCertificationAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "certification",
        "issue_date",
        "expiry_date",
        "is_active",
    )
    list_filter = ("is_active", "certification", "issue_date")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "certification__name",
    )


@admin.register(TrainingBudget)
class TrainingBudgetAdmin(admin.ModelAdmin):
    list_display = (
        "department",
        "year",
        "budget_amount",
        "allocated_amount",
        "remaining_amount",
    )
    list_filter = ("year", "department")
    search_fields = ("department__department",)


@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    list_display = ("employee", "title", "start_date", "end_date", "status")
    list_filter = ("status", "start_date", "end_date")
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "title",
    )


@admin.register(LearningPlanItem)
class LearningPlanItemAdmin(admin.ModelAdmin):
    list_display = ("learning_plan", "description", "target_date", "completed")
    list_filter = ("completed", "target_date")
    search_fields = ("learning_plan__title", "description")
