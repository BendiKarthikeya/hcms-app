"""
recruitment/models_approvals.py

Approval engine models for Manpower Requests and Offer Letters.
Routing: grade + department (extensible to project/nationality/budget).
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.fits_company_manager import FitsCompanyManager
from base.models import Company, Department
from employee.models import Employee
from fits.models import FitsModel
from recruitment.models_manpower import ManpowerRequest


class ApprovalRule(FitsModel):
    """
    Defines which approval chain applies based on department and grade range.
    First matching rule (highest priority) wins.
    """

    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Company")
    )
    name = models.CharField(max_length=200, verbose_name=_("Rule Name"))
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department (blank = any)"),
    )
    grade_min = models.CharField(
        max_length=50, blank=True, verbose_name=_("Grade Min (blank = any)")
    )
    grade_max = models.CharField(
        max_length=50, blank=True, verbose_name=_("Grade Max (blank = any)")
    )
    priority = models.PositiveIntegerField(default=0, verbose_name=_("Priority"))
    is_active = models.BooleanField(default=True)

    objects = FitsCompanyManager("company_id")

    class Meta:
        ordering = ["-priority"]
        verbose_name = _("Approval Rule")
        verbose_name_plural = _("Approval Rules")

    def __str__(self):
        return f"{self.name} (priority {self.priority})"


class ApprovalStep(FitsModel):
    APPROVER_TYPES = [
        ("user", _("Specific User")),
        ("department_head", _("Department Head")),
        ("manager_of_requester", _("Manager of Requester")),
        ("hr_manager", _("HR Manager")),
        ("finance", _("Finance")),
    ]

    rule = models.ForeignKey(
        ApprovalRule,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name=_("Rule"),
    )
    sequence = models.PositiveIntegerField(default=1, verbose_name=_("Order"))
    approver_type = models.CharField(
        max_length=30, choices=APPROVER_TYPES, default="manager_of_requester"
    )
    approver_user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_steps",
        verbose_name=_("Specific Approver"),
    )
    sla_hours = models.PositiveIntegerField(default=48, verbose_name=_("SLA (hours)"))
    is_optional = models.BooleanField(default=False)

    class Meta:
        ordering = ["sequence"]
        verbose_name = _("Approval Step")

    def __str__(self):
        return f"{self.rule} – Step {self.sequence} ({self.approver_type})"


class ManpowerApproval(models.Model):
    ACTION_PENDING = "pending"
    ACTION_APPROVED = "approved"
    ACTION_REJECTED = "rejected"
    ACTION_DELEGATED = "delegated"
    ACTION_ESCALATED = "auto_escalated"
    ACTION_QUERIED = "queried"

    ACTION_CHOICES = [
        (ACTION_PENDING, _("Pending")),
        (ACTION_APPROVED, _("Approved")),
        (ACTION_REJECTED, _("Rejected")),
        (ACTION_DELEGATED, _("Delegated")),
        (ACTION_ESCALATED, _("Auto Escalated")),
        (ACTION_QUERIED, _("Queried — Returned to Requester")),
    ]

    request = models.ForeignKey(
        ManpowerRequest,
        on_delete=models.CASCADE,
        related_name="approvals",
        verbose_name=_("Request"),
    )
    step = models.ForeignKey(
        ApprovalStep, on_delete=models.SET_NULL, null=True, verbose_name=_("Step")
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="manpower_approvals",
        verbose_name=_("Approver"),
    )
    acted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manpower_approvals_acted",
        verbose_name=_("Acted By (delegation)"),
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, default=ACTION_PENDING
    )
    acted_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = _("Manpower Approval")

    def __str__(self):
        return f"{self.request.requisition_no} – {self.action}"


class OfferApproval(models.Model):
    """Tracks each step in the offer letter approval chain."""

    ACTION_PENDING = "pending"
    ACTION_APPROVED = "approved"
    ACTION_REJECTED = "rejected"
    ACTION_DELEGATED = "delegated"

    ACTION_CHOICES = [
        (ACTION_PENDING, _("Pending")),
        (ACTION_APPROVED, _("Approved")),
        (ACTION_REJECTED, _("Rejected")),
        (ACTION_DELEGATED, _("Delegated")),
    ]

    offer = models.ForeignKey(
        "recruitment.OfferLetter",
        on_delete=models.CASCADE,
        related_name="offer_approvals",
        verbose_name=_("Offer Letter"),
    )
    step = models.ForeignKey(
        ApprovalStep, on_delete=models.SET_NULL, null=True, verbose_name=_("Step")
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="offer_approvals",
        verbose_name=_("Approver"),
    )
    acted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offer_approvals_acted",
        verbose_name=_("Acted By (delegation)"),
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, default=ACTION_PENDING
    )
    acted_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    signature_image = models.TextField(blank=True, verbose_name=_("Signature (base64)"))

    class Meta:
        ordering = ["id"]
        verbose_name = _("Offer Approval")

    def __str__(self):
        return f"{self.offer.offer_no} – Step {self.step.sequence if self.step else '?'} – {self.action}"


class RecruitmentApprovalDelegation(FitsModel):
    delegator = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="manpower_delegations_given",
        verbose_name=_("Delegator"),
    )
    delegate = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="manpower_delegations_received",
        verbose_name=_("Delegate"),
    )
    start_date = models.DateField(verbose_name=_("From"))
    end_date = models.DateField(verbose_name=_("To"))

    class Meta:
        verbose_name = _("Approval Delegation")

    def is_active_today(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.delegator} → {self.delegate} ({self.start_date}–{self.end_date})"
