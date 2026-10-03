"""
recruitment/models_manpower.py

Manpower Requisition models — the starting point of the full recruitment lifecycle.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.fits_company_manager import FitsCompanyManager
from base.models import Company, Department, JobPosition
from employee.models import Employee
from fits.models import FitsModel


def _req_no():
    return f"MR-{uuid.uuid4().hex[:8].upper()}"


class ManpowerRequest(FitsModel):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_UNDER_APPROVAL = "under_approval"
    STATUS_QUERIED = "queried"
    STATUS_APPROVED = "approved"
    STATUS_SOURCING = "sourcing"
    STATUS_INTERVIEWING = "interviewing"
    STATUS_OFFER = "offer"
    STATUS_JOINED = "joined"
    STATUS_CLOSED = "closed"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Draft")),
        (STATUS_SUBMITTED, _("Submitted")),
        (STATUS_UNDER_APPROVAL, _("Under Approval")),
        (STATUS_QUERIED, _("Returned with Query")),
        (STATUS_APPROVED, _("Approved")),
        (STATUS_SOURCING, _("Sourcing")),
        (STATUS_INTERVIEWING, _("Interviewing")),
        (STATUS_OFFER, _("Offer Stage")),
        (STATUS_JOINED, _("Joined")),
        (STATUS_CLOSED, _("Closed")),
        (STATUS_REJECTED, _("Rejected")),
    ]

    EMPLOYMENT_CHOICES = [
        ("full_time", _("Full Time")),
        ("part_time", _("Part Time")),
        ("contract", _("Contract")),
        ("intern", _("Intern")),
    ]

    NATIONALITY_CHOICES = [
        ("any", _("Any")),
        ("omani", _("Omani")),
        ("expat", _("Expatriate")),
    ]

    requisition_no = models.CharField(
        max_length=20, default=_req_no, unique=True, verbose_name=_("Requisition No")
    )
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Company")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
    )
    job_position = models.ForeignKey(
        JobPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Job Position"),
    )
    grade = models.CharField(
        max_length=50, blank=True, verbose_name=_("Grade / Level")
    )
    positions_count = models.PositiveIntegerField(
        default=1, verbose_name=_("Positions Required")
    )
    justification = models.TextField(verbose_name=_("Justification"))
    budget_code = models.CharField(
        max_length=100, blank=True, verbose_name=_("Budget Code")
    )
    expected_join_date = models.DateField(
        null=True, blank=True, verbose_name=_("Expected Joining Date")
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_CHOICES,
        default="full_time",
        verbose_name=_("Employment Type"),
    )
    nationality_preference = models.CharField(
        max_length=10,
        choices=NATIONALITY_CHOICES,
        default="any",
        verbose_name=_("Nationality Preference"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name=_("Status"),
    )
    requested_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="manpower_requests",
        verbose_name=_("Requested By"),
    )
    requested_on = models.DateTimeField(default=timezone.now, verbose_name=_("Requested On"))
    closed_positions = models.PositiveIntegerField(default=0, verbose_name=_("Filled Positions"))
    clarification_document = models.FileField(
        upload_to="recruitment/manpower/clarifications/",
        blank=True,
        null=True,
        verbose_name=_("Clarification Document"),
    )
    last_query = models.TextField(blank=True, verbose_name=_("Last Query"))
    query_count = models.PositiveIntegerField(default=0, verbose_name=_("Times Queried"))

    objects = FitsCompanyManager("company_id")

    class Meta:
        ordering = ["-requested_on"]
        verbose_name = _("Manpower Request")
        verbose_name_plural = _("Manpower Requests")

    def __str__(self):
        return f"{self.requisition_no} – {self.job_position}"

    @property
    def is_fully_filled(self):
        return self.closed_positions >= self.positions_count


class ManpowerRequestStatusLog(models.Model):
    request = models.ForeignKey(
        ManpowerRequest,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name=_("Request"),
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, verbose_name=_("Changed By")
    )
    at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["at"]
        verbose_name = _("Status Log")

    def __str__(self):
        return f"{self.request.requisition_no}: {self.from_status} → {self.to_status}"
