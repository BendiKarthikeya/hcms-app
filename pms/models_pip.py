"""
PIP (Performance Improvement Plan) Models
Tracks performance improvement plans for underperforming employees
Follows Omani Labor Law procedures for fair performance management
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from base.models import Company
from employee.models import Employee
from fits.models import FitsModel


class PIPTemplate(FitsModel):
    """
    Template for Performance Improvement Plans
    Pre-defined templates with standard milestones and metrics
    """

    STATUS_CHOICES = [
        ("active", _("Active")),
        ("archived", _("Archived")),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Template Name"),
        help_text=_("e.g., 'Technical Skills Improvement', 'Soft Skills Development'"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )
    duration_days = models.IntegerField(
        default=90,
        verbose_name=_("Default Duration (Days)"),
        help_text=_("Typically 30, 60, or 90 days"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name=_("Status"),
    )

    class Meta:
        verbose_name = _("PIP Template")
        verbose_name_plural = _("PIP Templates")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class PerformanceImprovementPlan(FitsModel):
    """
    Performance Improvement Plan (PIP)
    Formal document outlining performance expectations and improvement goals
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("active", _("Active")),
        ("under_review", _("Under Review")),
        ("successful", _("Successful - Completed")),
        ("unsuccessful", _("Unsuccessful - Termination Eligible")),
        ("cancelled", _("Cancelled")),
    ]

    REASON_CHOICES = [
        ("quality_issues", _("Quality Issues")),
        ("productivity_issues", _("Productivity/Output Issues")),
        ("attendance_issues", _("Attendance/Punctuality Issues")),
        ("behavior_issues", _("Behavior/Conduct Issues")),
        ("technical_skills", _("Technical Skills Gap")),
        ("soft_skills", _("Soft Skills Gap")),
        ("management_issues", _("Management/Leadership Issues")),
        ("other", _("Other")),
    ]

    # Core PIP Info
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
        related_name="performance_improvement_plans",
    )
    template = models.ForeignKey(
        PIPTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("PIP Template"),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("PIP Title"),
        default=_("Performance Improvement Plan"),
    )

    # Timeline
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Start Date"),
    )
    end_date = models.DateField(
        verbose_name=_("End Date"),
        help_text=_("Target completion date"),
    )

    # Review Dates (milestones)
    mid_review_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Mid-Point Review Date"),
        help_text=_("Usually halfway through PIP duration"),
    )

    # Details
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        verbose_name=_("Reason for PIP"),
    )
    reason_details = models.TextField(
        verbose_name=_("Specific Performance Issues"),
        help_text=_("Detailed description of performance gaps"),
    )
    expected_outcomes = models.TextField(
        verbose_name=_("Expected Outcomes & Improvements"),
        help_text=_("Clear, measurable goals employee should achieve"),
    )
    support_provided = models.TextField(
        verbose_name=_("Support & Resources Provided"),
        help_text=_("Training, mentoring, tools, or other support"),
        blank=True,
    )

    # Status Management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )
    initiated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="initiated_pips",
        verbose_name=_("Initiated By (Manager)"),
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_pips",
        verbose_name=_("Approved By (HR/Director)"),
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approval Date"),
    )

    # Employee Acknowledgment
    employee_acknowledged = models.BooleanField(
        default=False,
        verbose_name=_("Employee Acknowledged PIP"),
    )
    acknowledgment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Acknowledgment Date"),
    )

    # Outcome
    outcome = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Final Outcome Assessment"),
    )
    completion_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Completion Status"),
        help_text=_("e.g., 'Improved', 'Partially Improved', 'No Improvement'"),
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Completion Date"),
    )

    # Audit
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )

    class Meta:
        verbose_name = _("Performance Improvement Plan")
        verbose_name_plural = _("Performance Improvement Plans")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return f"PIP - {self.employee.get_name()} ({self.get_status_display()})"

    @property
    def days_remaining(self):
        """Calculate days remaining until end_date"""
        from datetime import date

        if self.status == "active":
            delta = self.end_date - date.today()
            return max(0, delta.days)
        return 0

    @property
    def is_overdue(self):
        """Check if PIP end date has passed"""
        from datetime import date

        return self.status == "active" and date.today() > self.end_date

    @property
    def progress_percentage(self):
        """Calculate progress as percentage of duration"""
        from datetime import date

        if self.status == "active":
            total_days = (self.end_date - self.start_date).days + 1
            elapsed_days = (date.today() - self.start_date).days + 1
            return min(100, int((elapsed_days / total_days) * 100))
        elif self.status == "successful":
            return 100
        return 0


class PIPMilestone(FitsModel):
    """
    Performance Improvement Plan Milestones
    Tracks specific measurable milestones within a PIP
    """

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("in_progress", _("In Progress")),
        ("completed", _("Completed")),
        ("completed_with_issues", _("Completed with Issues")),
        ("not_met", _("Not Met")),
    ]

    pip = models.ForeignKey(
        PerformanceImprovementPlan,
        on_delete=models.CASCADE,
        related_name="milestones",
        verbose_name=_("Performance Improvement Plan"),
    )
    milestone_title = models.CharField(
        max_length=255,
        verbose_name=_("Milestone Title"),
        help_text=_("e.g., 'Complete XYZ Training', 'Achieve 95% accuracy'"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )
    target_date = models.DateField(
        verbose_name=_("Target Completion Date"),
    )
    success_criteria = models.TextField(
        verbose_name=_("Success Criteria"),
        help_text=_("How will success be measured?"),
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Completion Date"),
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Completion Comments"),
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order"),
    )

    class Meta:
        verbose_name = _("PIP Milestone")
        verbose_name_plural = _("PIP Milestones")
        ordering = ["order", "target_date"]

    def __str__(self):
        return f"{self.milestone_title} - {self.get_status_display()}"

    @property
    def is_overdue(self):
        """Check if milestone is past target date and not completed"""
        from datetime import date

        return (
            self.status not in ["completed", "completed_with_issues"]
            and date.today() > self.target_date
        )


class PIPReview(FitsModel):
    """
    Periodic PIP Progress Reviews
    Tracks progress reviews at mid-point and end of PIP period
    """

    RATING_CHOICES = [
        ("on_track", _("On Track - Meeting Expectations")),
        ("needs_improvement", _("Needs Improvement - Some Progress")),
        ("not_meeting", _("Not Meeting - No/Insufficient Progress")),
    ]

    pip = models.ForeignKey(
        PerformanceImprovementPlan,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Performance Improvement Plan"),
    )
    review_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Review Date"),
    )
    review_type = models.CharField(
        max_length=20,
        choices=[
            ("initial", _("Initial Discussion")),
            ("mid_point", _("Mid-Point Review")),
            ("final", _("Final Review")),
            ("extension_discussion", _("Extension Discussion")),
        ],
        default="initial",
        verbose_name=_("Review Type"),
    )
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="conducted_pip_reviews",
        verbose_name=_("Reviewed By (Manager)"),
    )
    overall_rating = models.CharField(
        max_length=25,
        choices=RATING_CHOICES,
        verbose_name=_("Overall Progress Rating"),
    )
    achievements = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Achievements & Progress"),
        help_text=_("What the employee has improved"),
    )
    areas_for_improvement = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Areas Still Needing Improvement"),
    )
    recommendations = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Recommendations"),
        help_text=_("Suggested next steps or adjustments"),
    )
    employee_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Employee Comments"),
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Internal Notes"),
    )

    class Meta:
        verbose_name = _("PIP Review")
        verbose_name_plural = _("PIP Reviews")
        ordering = ["-review_date"]

    def __str__(self):
        return (
            f"{self.pip} - {self.get_review_type_display()} ({self.review_date.date()})"
        )


class PIPExtension(models.Model):
    """
    PIP Extension Request
    When an employee needs additional time to meet improvement goals
    """

    STATUS_CHOICES = [
        ("requested", _("Requested")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    pip = models.OneToOneField(
        PerformanceImprovementPlan,
        on_delete=models.CASCADE,
        related_name="extension",
        verbose_name=_("Performance Improvement Plan"),
    )
    requested_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Request Date"),
    )
    current_end_date = models.DateField(
        verbose_name=_("Current PIP End Date"),
    )
    requested_new_end_date = models.DateField(
        verbose_name=_("Requested New End Date"),
    )
    extension_days = models.IntegerField(
        verbose_name=_("Extension Duration (Days)"),
    )
    justification = models.TextField(
        verbose_name=_("Justification for Extension"),
    )
    requested_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_pip_extensions",
        verbose_name=_("Requested By"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="requested",
        verbose_name=_("Status"),
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_pip_extensions",
        verbose_name=_("Approved By (HR/Director)"),
    )
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approval Date"),
    )
    approval_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Approval Comments"),
    )

    class Meta:
        verbose_name = _("PIP Extension")
        verbose_name_plural = _("PIP Extensions")

    def __str__(self):
        return f"Extension Request - {self.pip.employee.get_name()}"
