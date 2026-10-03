"""
pms/models_pip_workflow.py

Performance Improvement Plan (PIP) Workflow Model
Manages traditional PIP workflow with stages, milestones, and outcomes
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models import Company, Employee
from datetime import timedelta
from django.utils import timezone


class PerformanceImprovementPlanWorkflow(models.Model):
    """
    Traditional PIP workflow model with 4 stages:
    1. Draft (initial creation)
    2. Active (started)
    3. Review (periodic reviews)
    4. Completed (final outcome)
    """

    PIP_STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("active", _("Active")),
        ("review", _("Review")),
        ("completed", _("Completed")),
        ("failed", _("Failed")),
        ("extended", _("Extended")),
    ]

    PIP_OUTCOME_CHOICES = [
        ("success", _("Success - Expectations Met")),
        ("unsuccessful", _("Unsuccessful - Terminated")),
        ("extended", _("Extended for 30 more days")),
        ("pending", _("Pending")),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="pip_workflows"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )

    # Basic information
    title = models.CharField(max_length=255, help_text=_("PIP Title"))
    description = models.TextField(
        help_text=_("Detailed description of performance issues")
    )
    objectives = models.TextField(
        help_text=_("Specific, measurable objectives for improvement")
    )

    # Timeline
    start_date = models.DateField(auto_now_add=True)
    day_30_review_date = models.DateField(null=True, blank=True)
    day_60_review_date = models.DateField(null=True, blank=True)
    day_90_review_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Status tracking
    status = models.CharField(
        max_length=20, choices=PIP_STATUS_CHOICES, default="draft", db_index=True
    )
    outcome = models.CharField(
        max_length=20, choices=PIP_OUTCOME_CHOICES, default="pending"
    )

    # Supporting manager and HR
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_pip_workflows",
    )
    hr_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hr_pip_workflows",
    )

    # Flags
    is_extended = models.BooleanField(default=False)
    extension_reason = models.TextField(blank=True)

    # Metadata
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_pip_workflows",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pms_performance_improvement_plan_workflow"
        verbose_name = _("Performance Improvement Plan Workflow")
        verbose_name_plural = _("Performance Improvement Plan Workflows")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee} - {self.title}"

    def activate(self):
        """Activate the PIP"""
        if self.status == "draft":
            self.status = "active"
            self.day_30_review_date = timezone.now().date() + timedelta(days=30)
            self.day_60_review_date = timezone.now().date() + timedelta(days=60)
            self.day_90_review_date = timezone.now().date() + timedelta(days=90)
            self.save()

    def record_review(self, day_number):
        """Record milestone review (30, 60, 90 days)"""
        if self.status == "active":
            self.status = "review"
            self.save()

    def complete_pip(self, outcome):
        """Complete the PIP with final outcome"""
        self.status = "completed"
        self.outcome = outcome
        self.end_date = timezone.now().date()
        self.save()

    def extend_pip(self, reason, additional_days=30):
        """Extend PIP for additional period"""
        if self.status == "completed" and self.outcome == "unsuccessful":
            self.is_extended = True
            self.status = "active"
            self.extension_reason = reason
            self.outcome = "pending"
            self.end_date = timezone.now().date() + timedelta(days=additional_days)
            self.save()


class PIPMilestone(models.Model):
    """
    Milestones within a PIP workflow
    Tracks progress toward objectives
    """

    MILESTONE_STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("in_progress", _("In Progress")),
        ("completed", _("Completed")),
        ("not_met", _("Not Met")),
    ]

    pip = models.ForeignKey(
        PerformanceImprovementPlanWorkflow,
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_date = models.DateField()

    status = models.CharField(
        max_length=20, choices=MILESTONE_STATUS_CHOICES, default="pending"
    )

    evidence = models.TextField(
        blank=True, help_text=_("Evidence of milestone achievement")
    )
    reviewed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    reviewed_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pms_pip_milestone"
        ordering = ["target_date"]

    def __str__(self):
        return f"{self.pip} - {self.title}"


class PIPReview(models.Model):
    """
    Periodic reviews at 30, 60, and 90 days
    """

    REVIEW_TYPE_CHOICES = [
        ("day_30", _("30-Day Review")),
        ("day_60", _("60-Day Review")),
        ("day_90", _("90-Day Review")),
        ("final", _("Final Review")),
    ]

    pip = models.ForeignKey(
        PerformanceImprovementPlanWorkflow,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES)
    review_date = models.DateField(auto_now_add=True)

    # Review details
    employee_progress_note = models.TextField()
    manager_feedback = models.TextField()
    hr_comments = models.TextField(blank=True)

    # Assessment
    progress_percentage = models.IntegerField(default=0)  # 0-100
    is_on_track = models.BooleanField(default=True)

    reviewed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pms_pip_review"
        unique_together = ("pip", "review_type")

    def __str__(self):
        return f"{self.pip} - {self.get_review_type_display()}"


class PIPFeedback(models.Model):
    """
    Weekly or periodic feedback during PIP period
    """

    pip = models.ForeignKey(
        PerformanceImprovementPlanWorkflow,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    feedback_date = models.DateField(auto_now_add=True)
    feedback_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pip_feedback_given",
    )

    feedback_text = models.TextField()
    is_positive = models.BooleanField(default=False)

    class Meta:
        db_table = "pms_pip_feedback"
        ordering = ["-feedback_date"]

    def __str__(self):
        return f"Feedback on {self.feedback_date}"
