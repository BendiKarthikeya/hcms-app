"""
Enhanced Leave Request Approval Workflow Models
Adds: Parallel approvals, SLA escalation, conditional auto-approval, delegation
Location: leave/models_enhanced_approvals.py
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from employee.models import Employee
from base.models import Company
from fits.models import FitsModel


class ApprovalPolicy(FitsModel):
    """
    Defines approval policies for leave requests including SLA rules and escalation.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
        related_name="leave_approval_policies",
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Policy Name"),
        help_text=_("e.g., 'Standard Leave Approval', 'Executive Fast Track'"),
    )

    # SLA Configuration
    sla_hours = models.IntegerField(
        default=24,
        verbose_name=_("SLA Response Time (Hours)"),
        help_text=_("Time allowed for approval decision"),
    )
    escalation_hours = models.IntegerField(
        default=48,
        verbose_name=_("Escalation Time (Hours)"),
        help_text=_("Time before escalating to next level if no response"),
    )

    # Approval Configuration
    allow_parallel_approvals = models.BooleanField(
        default=False,
        verbose_name=_("Allow Parallel Approvals"),
        help_text=_("Multiple approvers can approve simultaneously (else sequential)"),
    )

    auto_approve_threshold_days = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Auto-Approve if Days <="),
        help_text=_(
            "Automatically approve leaves <= this many days without manager intervention"
        ),
    )

    require_manager_confirmation = models.BooleanField(
        default=True,
        verbose_name=_("Require Manager Confirmation After Auto-Approval"),
        help_text=_(
            "Even auto-approved leaves need manager confirmation within 24 hours"
        ),
    )

    allow_override = models.BooleanField(
        default=True,
        verbose_name=_("Allow Approval Override"),
        help_text=_("HR admin can override approval decisions"),
    )

    max_override_count = models.IntegerField(
        default=2,
        verbose_name=_("Maximum Override Count"),
        help_text=_("Maximum number of times a single request can be overridden"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Leave Approval Policy"
        verbose_name_plural = "Leave Approval Policies"
        unique_together = ("company", "name")

    def __str__(self):
        return f"{self.company} - {self.name}"


class ApprovalDelegation(FitsModel):
    """
    Allows managers to delegate approval authority during absence.
    """

    DELEGATION_STATUS = [
        ("active", _("Active")),
        ("expired", _("Expired")),
        ("revoked", _("Revoked")),
    ]

    delegating_manager = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="delegated_from",
        verbose_name=_("Delegating Manager"),
        help_text=_("Manager delegating their approval authority"),
    )

    delegated_to = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="delegated_to_manager",
        verbose_name=_("Delegated To"),
        help_text=_("Employee/Manager receiving approval authority"),
    )

    start_date = models.DateTimeField(
        verbose_name=_("Delegation Start"), default=timezone.now
    )

    end_date = models.DateTimeField(
        verbose_name=_("Delegation End"),
        help_text=_("Delegation automatically expires on this date/time"),
    )

    reason = models.TextField(
        verbose_name=_("Reason for Delegation"),
        help_text=_("e.g., 'Annual leave', 'Medical leave', 'Sabbatical'"),
    )

    status = models.CharField(
        max_length=20,
        choices=DELEGATION_STATUS,
        default="active",
        verbose_name=_("Status"),
    )

    departments = models.ManyToManyField(
        "base.Department",
        blank=True,
        verbose_name=_("Specific Departments"),
        help_text=_("Leave blank to delegate for all departments"),
    )

    is_back_to_original = models.BooleanField(
        default=False,
        verbose_name=_("Back-to-Original on Expiry"),
        help_text=_("Revert to original approver when delegation ends"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revoked_delegations",
    )

    class Meta:
        verbose_name = "Approval Delegation"
        verbose_name_plural = "Approval Delegations"
        constraints = [
            models.UniqueConstraint(
                fields=["delegating_manager", "start_date", "end_date"],
                name="unique_active_delegation",
                condition=models.Q(status="active"),
            )
        ]

    def __str__(self):
        return f"{self.delegating_manager} → {self.delegated_to} ({self.start_date.strftime('%Y-%m-%d')})"

    def is_currently_active(self):
        """Check if delegation is currently active"""
        now = timezone.now()
        return self.status == "active" and self.start_date <= now <= self.end_date

    @classmethod
    def get_current_approver(cls, original_manager, date_time=None):
        """
        Get who should approve instead of original_manager at given date/time
        """
        if date_time is None:
            date_time = timezone.now()

        delegation = cls.objects.filter(
            delegating_manager=original_manager,
            status="active",
            start_date__lte=date_time,
            end_date__gte=date_time,
        ).first()

        return delegation.delegated_to if delegation else original_manager


class ApprovalRequest(FitsModel):
    """
    Individual approval task for a leave request from a specific approver.
    Supports parallel and sequential approvals.
    """

    APPROVAL_STATUS = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("escalated", _("Escalated")),
        ("auto_approved", _("Auto-Approved")),
    ]

    ESCALATION_REASON = [
        ("sla_breach", _("SLA Breach")),
        ("manager_unavailable", _("Manager Unavailable")),
        ("hr_escalation", _("HR Escalation")),
        ("manual", _("Manual Escalation")),
    ]

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="approval_requests"
    )

    approver = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, related_name="approval_tasks"
    )

    sequence_order = models.IntegerField(
        help_text=_("Order in approval chain. Lower = earlier")
    )

    approval_type = models.CharField(
        max_length=20,
        choices=[("sequential", _("Sequential")), ("parallel", _("Parallel"))],
        default="sequential",
    )

    status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default="pending")

    assigned_at = models.DateTimeField(auto_now_add=True)

    sla_deadline = models.DateTimeField(verbose_name=_("SLA Deadline"))

    escalation_deadline = models.DateTimeField(
        verbose_name=_("Escalation Deadline"),
        help_text=_("Auto-escalate if not approved by this time"),
    )

    # Approval details
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approvals_done",
    )
    approval_comment = models.TextField(blank=True)

    # Rejection details
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rejections_done",
    )
    rejection_reason = models.TextField(blank=True)

    # Escalation tracking
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalation_reason = models.CharField(
        max_length=50, choices=ESCALATION_REASON, null=True, blank=True
    )
    escalated_to = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="escalated_approvals",
    )

    # Notification tracking
    notified_count = models.IntegerField(default=0)
    first_notified_at = models.DateTimeField(null=True, blank=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)

    # Auto-approval tracking
    auto_approved = models.BooleanField(default=False)
    confirmation_required = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Approval Request"
        verbose_name_plural = "Approval Requests"
        unique_together = ("leave_request", "approver", "sequence_order")
        ordering = ["leave_request", "sequence_order"]

    def __str__(self):
        return f"{self.leave_request} - {self.approver} ({self.status})"

    def is_overdue(self):
        """Check if approval is overdue (SLA breached)"""
        return self.status == "pending" and self.sla_deadline < timezone.now()

    def is_escalation_due(self):
        """Check if escalation should happen"""
        return self.status == "pending" and self.escalation_deadline < timezone.now()

    def days_until_sla_breach(self):
        """Return days remaining before SLA breach"""
        time_remaining = self.sla_deadline - timezone.now()
        return time_remaining.total_seconds() / 86400  # seconds to days

    def send_reminder(self):
        """Send reminder notification to approver"""
        self.notified_count += 1
        if not self.first_notified_at:
            self.first_notified_at = timezone.now()
        self.last_notified_at = timezone.now()
        self.save()
        # TODO: Implement email notification logic

    def approve(self, approved_by, comment=""):
        """Record approval"""
        self.status = "approved"
        self.approved_at = timezone.now()
        self.approved_by = approved_by
        self.approval_comment = comment
        self.save()

    def reject(self, rejected_by, reason=""):
        """Record rejection"""
        self.status = "rejected"
        self.rejected_at = timezone.now()
        self.rejected_by = rejected_by
        self.rejection_reason = reason
        self.save()

    def escalate(self, escalated_to, reason="manual"):
        """Escalate to next level"""
        self.status = "escalated"
        self.escalated_at = timezone.now()
        self.escalated_to = escalated_to
        self.escalation_reason = reason
        self.save()


class ApprovalOverride(FitsModel):
    """
    Audit trail for approval decisions overridden by HR/Admins.
    """

    OVERRIDE_ACTION = [
        ("approve", _("Override to Approve")),
        ("reject", _("Override to Reject")),
        ("reset", _("Reset for Re-approval")),
    ]

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="overrides"
    )

    original_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)

    action = models.CharField(max_length=20, choices=OVERRIDE_ACTION)

    overridden_by = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="overrides_done"
    )

    reason = models.TextField(verbose_name=_("Reason for Override"))

    approval_request = models.ForeignKey(
        ApprovalRequest, null=True, blank=True, on_delete=models.SET_NULL
    )

    overridden_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Approval Override"
        verbose_name_plural = "Approval Overrides"
        verbose_name_plural = "Approval Overrides"
        ordering = ["-overridden_at"]

    def __str__(self):
        return f"{self.leave_request} - {self.action} by {self.overridden_by}"


class ApprovalSLAAlert(FitsModel):
    """
    Tracks SLA breaches and escalations for monitoring and analytics.
    """

    ALERT_TYPE = [
        ("warning", _("Warning - 25% of SLA time used")),
        ("critical", _("Critical - 75% of SLA time used")),
        ("breach", _("Breach - SLA exceeded")),
        ("escalated", _("Escalated for SLA breach")),
    ]

    approval_request = models.ForeignKey(
        ApprovalRequest, on_delete=models.CASCADE, related_name="sla_alerts"
    )

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE)

    triggered_at = models.DateTimeField(auto_now_add=True)

    notification_sent = models.BooleanField(default=False)
    escalation_triggered = models.BooleanField(default=False)

    class Meta:
        ordering = ["-triggered_at"]

    def __str__(self):
        return f"{self.approval_request} - {self.alert_type}"


class ApprovalMetrics(models.Model):
    """
    Analytics dashboard for approval performance tracking.
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="approval_metrics"
    )

    approval_period = models.DateField(
        verbose_name=_("Period Date (First day of month)")
    )

    # Volume metrics
    total_requests = models.IntegerField(default=0)
    approved_count = models.IntegerField(default=0)
    rejected_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    auto_approved_count = models.IntegerField(default=0)

    # Performance metrics
    avg_approval_time_hours = models.FloatField(null=True, blank=True)
    sla_compliance_percentage = models.FloatField(null=True, blank=True)
    escalation_count = models.IntegerField(default=0)

    # Bottleneck analysis
    bottleneck_approver = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bottleneck_metrics",
    )
    bottleneck_requests = models.IntegerField(default=0)
    bottleneck_avg_days_pending = models.FloatField(null=True, blank=True)

    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Approval Metrics"
        verbose_name_plural = "Approval Metrics"
        unique_together = ("company", "approval_period")

    def __str__(self):
        return f"{self.company} - {self.approval_period.strftime('%B %Y')}"
