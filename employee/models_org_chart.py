"""
employee/models_org_chart.py
Organization Chart Models

Defines database models for position management and hierarchy caching.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords

from base.models import Department, Company
from employee.models import Employee


class OrgChartPosition(models.Model):
    """
    Organizational position with hierarchy tracking.

    Represents a position in the organization, including job title,
    reporting structure, cost center, and salary information.
    """

    POSITION_STATUS_CHOICES = [
        ("active", _("Active")),
        ("inactive", _("Inactive")),
        ("draft", _("Draft")),
        ("archived", _("Archived")),
    ]

    # Position Identification
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="org_position",
        help_text=_("Employee occupying this position"),
    )
    position_code = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique position code (e.g., MGMT-001)"),
    )
    position_title = models.CharField(
        max_length=255, help_text=_("Position title (e.g., Development Manager)")
    )

    # Reporting Structure
    reporting_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports_org",
        help_text=_("Direct reporting manager"),
    )

    # Organization Context
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        help_text=_("Department for this position"),
    )
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, help_text=_("Company for this position")
    )

    # Cost & Budget
    cost_center = models.CharField(
        max_length=50,
        default="DEFAULT",
        help_text=_("Cost center code for budget tracking"),
    )
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Minimum salary range"),
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Maximum salary range"),
    )

    # Status & Tracking
    status = models.CharField(
        max_length=20,
        choices=POSITION_STATUS_CHOICES,
        default="active",
        help_text=_("Position status"),
    )
    hierarchy_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Depth in org hierarchy (0=top level)"),
    )
    position_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("Level in organization (1=executive, 5=junior)"),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(
        blank=True, help_text=_("Position description and responsibilities")
    )

    # Audit Trail
    history = HistoricalRecords()

    class Meta:
        db_table = "employee_org_chart_position"
        verbose_name = _("Organization Chart Position")
        verbose_name_plural = _("Organization Chart Positions")
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["department", "hierarchy_level"]),
            models.Index(fields=["cost_center"]),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.position_title} - {self.employee.get_full_name()}"

    def get_direct_reports(self):
        """Get count of direct reports"""
        return OrgChartPosition.objects.filter(
            reporting_manager=self.employee, status="active"
        ).count()

    def get_total_reports(self):
        """Get total reports (including indirect)"""
        total = 0
        direct_reports = OrgChartPosition.objects.filter(
            reporting_manager=self.employee, status="active"
        )
        total += direct_reports.count()
        for report in direct_reports:
            total += report.get_total_reports()
        return total

    def get_hierarchy_path(self):
        """Get list of managers from this position to root"""
        path = [self]
        current = self.reporting_manager
        while current:
            try:
                position = OrgChartPosition.objects.get(employee=current)
                path.append(position)
                current = position.reporting_manager
            except OrgChartPosition.DoesNotExist:
                break
        return path


class PositionHierarchyCache(models.Model):
    """
    Cached organization hierarchy for performance optimization.

    Stores pre-computed hierarchies to avoid expensive recursive queries.
    """

    # Identification
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, help_text=_("Company for this hierarchy")
    )
    root_position = models.ForeignKey(
        OrgChartPosition,
        on_delete=models.CASCADE,
        related_name="as_root_cache",
        help_text=_("Root position for this hierarchy"),
    )

    # Cached Data
    hierarchy_json = models.JSONField(help_text=_("Cached hierarchy structure as JSON"))
    depth = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Maximum depth of hierarchy"),
    )
    employee_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Total employees in this hierarchy"),
    )
    position_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Total positions in this hierarchy"),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_computed = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text=_("Cache expiration time"))
    is_valid = models.BooleanField(
        default=True, help_text=_("Whether cache is still valid")
    )

    class Meta:
        db_table = "employee_position_hierarchy_cache"
        verbose_name = _("Position Hierarchy Cache")
        verbose_name_plural = _("Position Hierarchy Caches")
        indexes = [
            models.Index(fields=["company", "is_valid"]),
            models.Index(fields=["expires_at"]),
        ]
        unique_together = ["company", "root_position"]

    def __str__(self):
        return f"Cache: {self.root_position} - {self.employee_count} employees"

    def is_expired(self):
        """Check if cache has expired"""
        from django.utils import timezone

        return timezone.now() > self.expires_at


class DraftPositionChange(models.Model):
    """
    Draft organizational changes pending approval.

    Allows staging and reviewing changes before committing to database.
    Includes drag-drop moves, position edits, and bulk updates.
    """

    CHANGE_TYPE_CHOICES = [
        ("move", _("Manager Change")),
        ("edit", _("Position Edit")),
        ("create", _("New Position")),
        ("delete", _("Delete Position")),
        ("bulk_update", _("Bulk Update")),
    ]

    APPROVAL_STATUS_CHOICES = [
        ("pending", _("Pending Review")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("committed", _("Committed to DB")),
    ]

    # Identification
    change_id = models.CharField(
        max_length=100, unique=True, help_text=_("Unique change identifier")
    )
    change_type = models.CharField(
        max_length=20, choices=CHANGE_TYPE_CHOICES, help_text=_("Type of change")
    )

    # Change Content
    position = models.ForeignKey(
        OrgChartPosition,
        on_delete=models.CASCADE,
        related_name="draft_changes",
        help_text=_("Position affected by this change"),
    )
    affected_positions = models.ManyToManyField(
        OrgChartPosition,
        related_name="draft_affected",
        blank=True,
        help_text=_("Other positions affected (for bulk changes)"),
    )

    # Change Details
    old_values = models.JSONField(help_text=_("Previous values (for audit trail)"))
    new_values = models.JSONField(help_text=_("New values to apply"))
    change_description = models.TextField(
        help_text=_("Description of what changed and why")
    )

    # Approval Workflow
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
        help_text=_("Approval status"),
    )
    created_by = models.CharField(
        max_length=255, help_text=_("User who initiated the change")
    )
    approved_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("User who approved the change"),
    )
    approval_comment = models.TextField(
        blank=True, help_text=_("Approval/rejection comment")
    )

    # Impact Analysis
    estimated_cost_impact = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Estimated salary/budget impact"),
    )
    affected_team_size = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Number of people affected by this change"),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_effective_date = models.DateField(
        null=True, blank=True, help_text=_("When change should become effective")
    )

    class Meta:
        db_table = "employee_draft_position_change"
        verbose_name = _("Draft Position Change")
        verbose_name_plural = _("Draft Position Changes")
        indexes = [
            models.Index(fields=["position", "approval_status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["scheduled_effective_date"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_change_type_display()}: {self.position} - {self.approval_status}"

    def get_impact_summary(self):
        """Return summary of change impact"""
        return {
            "change_type": self.get_change_type_display(),
            "affected_count": self.affected_positions.count(),
            "team_size_impact": self.affected_team_size,
            "cost_impact": str(self.estimated_cost_impact or 0),
            "status": self.get_approval_status_display(),
        }


class OrgChartAuditLog(models.Model):
    """
    Audit log for all organization chart changes.

    Provides comprehensive tracking of who changed what, when, and why.
    """

    ACTION_CHOICES = [
        ("view", _("Viewed")),
        ("create", _("Created")),
        ("update", _("Updated")),
        ("delete", _("Deleted")),
        ("move", _("Moved")),
        ("export", _("Exported")),
        ("import", _("Imported")),
        ("validate", _("Validated")),
    ]

    # Action Details
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, help_text=_("Action performed")
    )
    position = models.ForeignKey(
        OrgChartPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text=_("Position affected"),
    )
    affected_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="org_audit_logs",
        help_text=_("Employee affected"),
    )

    # Change Details
    old_value = models.JSONField(null=True, blank=True, help_text=_("Previous value"))
    new_value = models.JSONField(null=True, blank=True, help_text=_("New value"))
    change_summary = models.TextField(help_text=_("Summary of the change"))

    # Audit Trail
    performed_by = models.CharField(
        max_length=255, help_text=_("User who performed the action")
    )
    performed_at = models.DateTimeField(
        auto_now_add=True, help_text=_("When the action was performed")
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text=_("IP address of user")
    )

    # Metadata
    request_id = models.CharField(
        max_length=100, null=True, blank=True, help_text=_("Request ID for correlation")
    )

    class Meta:
        db_table = "employee_org_chart_audit_log"
        verbose_name = _("Org Chart Audit Log")
        verbose_name_plural = _("Org Chart Audit Logs")
        indexes = [
            models.Index(fields=["performed_by", "performed_at"]),
            models.Index(fields=["action", "performed_at"]),
            models.Index(fields=["position"]),
        ]
        ordering = ["-performed_at"]

    def __str__(self):
        return (
            f"{self.get_action_display()}: {self.change_summary} by {self.performed_by}"
        )
