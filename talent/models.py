"""
Talent & Succession Planning Models

This module contains models for talent management, succession planning,
9-box matrix, and leadership development.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import Company, Department
from employee.models import Employee


class TalentProfile(models.Model):
    """Comprehensive talent profile for employees"""

    PERFORMANCE_LEVELS = [
        ("low", _("Low")),
        ("medium", _("Medium")),
        ("high", _("High")),
        ("exceptional", _("Exceptional")),
    ]

    POTENTIAL_LEVELS = [
        ("low", _("Low")),
        ("medium", _("Medium")),
        ("high", _("High")),
        ("exceptional", _("Exceptional")),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    performance_level = models.CharField(
        _("Performance Level"), max_length=20, choices=PERFORMANCE_LEVELS
    )
    potential_level = models.CharField(
        _("Potential Level"), max_length=20, choices=POTENTIAL_LEVELS
    )
    career_aspirations = models.TextField(_("Career Aspirations"), blank=True)
    mobility_willingness = models.BooleanField(_("Willing to Relocate"), default=False)
    readiness_level = models.CharField(
        _("Readiness Level"),
        max_length=20,
        choices=[
            ("ready_now", _("Ready Now")),
            ("ready_1_2_years", _("Ready in 1-2 Years")),
            ("ready_3plus_years", _("Ready in 3+ Years")),
            ("not_ready", _("Not Ready")),
        ],
    )
    development_needs = models.TextField(_("Development Needs"), blank=True)
    last_assessment_date = models.DateField(_("Last Assessment Date"))
    next_assessment_date = models.DateField(_("Next Assessment Date"))
    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Talent Profile")
        verbose_name_plural = _("Talent Profiles")

    def __str__(self):
        return f"Talent Profile - {self.employee}"


class CriticalRole(models.Model):
    """Critical organizational roles for succession planning"""

    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    job_position = models.ForeignKey("base.JobPosition", on_delete=models.CASCADE)
    role_name = models.CharField(_("Role Name"), max_length=200)
    description = models.TextField(_("Description"))
    criticality_level = models.CharField(
        _("Criticality Level"),
        max_length=20,
        choices=[
            ("low", _("Low")),
            ("medium", _("Medium")),
            ("high", _("High")),
            ("critical", _("Critical")),
        ],
    )
    vacancy_risk = models.CharField(
        _("Vacancy Risk"),
        max_length=20,
        choices=[
            ("low", _("Low")),
            ("medium", _("Medium")),
            ("high", _("High")),
        ],
    )
    succession_required = models.BooleanField(_("Succession Required"), default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Critical Role")
        verbose_name_plural = _("Critical Roles")

    def __str__(self):
        return self.role_name


class SuccessionPlan(models.Model):
    """Succession plan for critical roles"""

    critical_role = models.ForeignKey(CriticalRole, on_delete=models.CASCADE)
    primary_successor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="primary_successor_for"
    )
    secondary_successor = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="secondary_successor_for",
    )
    readiness_level = models.CharField(
        _("Readiness Level"), max_length=20, choices=TalentProfile.POTENTIAL_LEVELS
    )
    estimated_timeline_months = models.PositiveIntegerField(
        _("Estimated Timeline (Months)")
    )
    development_plan = models.TextField(_("Development Plan"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[
            ("draft", _("Draft")),
            ("active", _("Active")),
            ("completed", _("Completed")),
            ("on_hold", _("On Hold")),
        ],
        default="draft",
    )
    created_date = models.DateField(_("Created Date"), auto_now_add=True)
    last_updated = models.DateField(_("Last Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Succession Plan")
        verbose_name_plural = _("Succession Plans")

    def __str__(self):
        return f"Succession Plan for {self.critical_role}"


class NineBoxMatrix(models.Model):
    """9-Box talent assessment matrix"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    performance_score = models.DecimalField(
        _("Performance Score"), max_digits=5, decimal_places=2
    )
    potential_score = models.DecimalField(
        _("Potential Score"), max_digits=5, decimal_places=2
    )
    assessment_date = models.DateField(_("Assessment Date"))
    assessed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assessed_nine_boxes",
    )
    quadrant = models.CharField(
        _("Quadrant"),
        max_length=20,
        choices=[
            ("underperformer", _("Underperformer")),
            ("core_player", _("Core Player")),
            ("growth_star", _("Growth Star")),
            ("top_talent", _("Top Talent")),
            ("effective_specialist", _("Effective Specialist")),
        ],
    )
    comments = models.TextField(_("Comments"), blank=True)

    class Meta:
        verbose_name = _("9-Box Matrix Assessment")
        verbose_name_plural = _("9-Box Matrix Assessments")

    def __str__(self):
        return f"9-Box - {self.employee} ({self.assessment_date})"


class CareerPath(models.Model):
    """Career path progression model"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    current_position = models.ForeignKey(
        "base.JobPosition", on_delete=models.CASCADE, related_name="current_positions"
    )
    target_position = models.ForeignKey(
        "base.JobPosition", on_delete=models.CASCADE, related_name="target_positions"
    )
    timeline_months = models.PositiveIntegerField(_("Timeline (Months)"))
    development_activities = models.TextField(_("Development Activities"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[
            ("planned", _("Planned")),
            ("in_progress", _("In Progress")),
            ("completed", _("Completed")),
            ("on_hold", _("On Hold")),
        ],
        default="planned",
    )
    start_date = models.DateField(_("Start Date"), null=True, blank=True)
    target_completion_date = models.DateField(_("Target Completion Date"))

    class Meta:
        verbose_name = _("Career Path")
        verbose_name_plural = _("Career Paths")

    def __str__(self):
        return f"Career Path: {self.current_position} → {self.target_position}"


class TalentReview(models.Model):
    """Talent review meetings and assessments"""

    title = models.CharField(_("Review Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    review_date = models.DateField(_("Review Date"))
    participants = models.ManyToManyField(
        Employee, related_name="talent_reviews_participated"
    )
    facilitator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="facilitated_talent_reviews",
    )
    outcomes = models.TextField(_("Outcomes"), blank=True)
    action_items = models.TextField(_("Action Items"), blank=True)
    next_review_date = models.DateField(_("Next Review Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Talent Review")
        verbose_name_plural = _("Talent Reviews")

    def __str__(self):
        return self.title


class RetentionRisk(models.Model):
    """Employee retention risk assessment"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    risk_level = models.CharField(
        _("Risk Level"),
        max_length=20,
        choices=[
            ("low", _("Low")),
            ("medium", _("Medium")),
            ("high", _("High")),
            ("critical", _("Critical")),
        ],
    )
    risk_factors = models.TextField(_("Risk Factors"))
    mitigation_strategy = models.TextField(_("Mitigation Strategy"), blank=True)
    assessed_date = models.DateField(_("Assessed Date"))
    next_assessment_date = models.DateField(_("Next Assessment Date"))

    class Meta:
        verbose_name = _("Retention Risk")
        verbose_name_plural = _("Retention Risks")

    def __str__(self):
        return f"Retention Risk - {self.employee} ({self.risk_level})"


class LeadershipPipeline(models.Model):
    """Leadership pipeline development"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leadership_level = models.CharField(
        _("Leadership Level"),
        max_length=50,
        choices=[
            ("emerging_leader", _("Emerging Leader")),
            ("team_leader", _("Team Leader")),
            ("department_head", _("Department Head")),
            ("executive", _("Executive")),
        ],
    )
    target_level = models.CharField(
        _("Target Level"),
        max_length=50,
        choices=[
            ("team_leader", _("Team Leader")),
            ("department_head", _("Department Head")),
            ("executive", _("Executive")),
            ("senior_executive", _("Senior Executive")),
        ],
    )
    development_plan = models.TextField(_("Development Plan"))
    mentor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mentored_leaders",
    )
    progress_percentage = models.PositiveIntegerField(_("Progress %"), default=0)

    class Meta:
        verbose_name = _("Leadership Pipeline")
        verbose_name_plural = _("Leadership Pipelines")

    def __str__(self):
        return f"Leadership Pipeline - {self.employee}"
