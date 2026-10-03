"""
recruitment/models_proposal.py

Employment Proposal stage models — sits between interview completion and
offer-letter creation. Self-contained snapshot of the ONEIC employment
proposal forms (Permanent and Contractual S-O-M variants).
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from employee.models import Employee
from fits.models import FitsModel


# ────────────────────────────────────────────────────────────────────────────
# Constants — role keys for the approver chains printed on each PDF.
# ────────────────────────────────────────────────────────────────────────────
ROLE_PROJECT_DIRECTOR = "project_director"
ROLE_HEAD_OF_DEPARTMENT = "head_of_department"
ROLE_CHIEF_OPERATION_OFFICER = "chief_operation_officer"
ROLE_LEGAL_ADVISOR = "legal_advisor"
ROLE_GM_HRA = "gm_hra"
ROLE_CFO = "cfo"
ROLE_CEO = "ceo"

ROLE_LABELS = {
    ROLE_PROJECT_DIRECTOR: "Project Director",
    ROLE_HEAD_OF_DEPARTMENT: "Head of Department",
    ROLE_CHIEF_OPERATION_OFFICER: "Chief Operation Officer",
    ROLE_LEGAL_ADVISOR: "Legal Advisor",
    ROLE_GM_HRA: "General Manager HR&A",
    ROLE_CFO: "Chief Financial Officer",
    ROLE_CEO: "Chief Executive Officer",
}

PERMANENT_CHAIN = [
    ROLE_PROJECT_DIRECTOR,
    ROLE_HEAD_OF_DEPARTMENT,
    ROLE_CHIEF_OPERATION_OFFICER,
    ROLE_LEGAL_ADVISOR,
    ROLE_GM_HRA,
    ROLE_CFO,
    ROLE_CEO,
]

CONTRACTUAL_CHAIN = [
    ROLE_HEAD_OF_DEPARTMENT,
    ROLE_CHIEF_OPERATION_OFFICER,
    ROLE_GM_HRA,
]


class EmploymentProposal(FitsModel):
    TEMPLATE_PERMANENT = "permanent"
    TEMPLATE_CONTRACTUAL = "contractual"
    TEMPLATE_CHOICES = [
        (TEMPLATE_PERMANENT, _("Permanent (Full-Time)")),
        (TEMPLATE_CONTRACTUAL, _("Contractual — S-O-M Grade")),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CONVERTED = "converted"
    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Draft")),
        (STATUS_PENDING, _("Pending Approval")),
        (STATUS_APPROVED, _("Approved")),
        (STATUS_REJECTED, _("Rejected")),
        (STATUS_CONVERTED, _("Converted to Offer")),
    ]

    REFERRAL_CHOICES = [
        ("client", _("Client")),
        ("consultancy", _("Consultancy")),
        ("direct", _("Direct")),
        ("staff_number", _("Staff Number")),
    ]

    CONSULTANCY_CHOICES = [
        ("voltech_hr", "Voltech HR"),
        ("zen", "Zen"),
        ("trehan", "Trehan"),
        ("sinclus", "Sinclus"),
        ("alyousuf", "ALYousuf"),
        ("others", _("Others")),
    ]

    CONTRACT_TYPE_CHOICES = [
        ("temporary", _("Temporary")),
        ("permanent", _("Permanent")),
    ]

    MARITAL_CHOICES = [
        ("single", _("Single")),
        ("married", _("Married")),
        ("divorced", _("Divorced")),
        ("widow", _("Widow")),
        ("other", _("Other")),
    ]

    LICENSE_CHOICES = [
        ("none", _("None")),
        ("omani", "Omani"),
        ("gcc", "GCC"),
        ("other", _("Other")),
    ]

    SALARY_BUDGET_CHOICES = [
        ("budgeted", _("Budgeted")),
        ("not_budgeted", _("Not Budgeted")),
        ("contractual", _("Contractual")),
    ]

    LSA_TIER_CHOICES = [
        ("tier_50", "RO 50 (<300)"),
        ("tier_40", "RO 40 (301–500)"),
        ("tier_30", "RO 30 (501–999)"),
        ("tier_20", "RO 20 (1000 & Above)"),
    ]

    FAMILY_STATUS_CHOICES = [
        ("family", _("Family")),
        ("bachelor", _("Bachelor")),
    ]

    proposal_no = models.CharField(max_length=20, unique=True, verbose_name=_("Proposal No"))
    template_type = models.CharField(max_length=20, choices=TEMPLATE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    candidate = models.ForeignKey(
        "recruitment.Candidate", on_delete=models.PROTECT, related_name="proposals"
    )
    interview = models.ForeignKey(
        "recruitment.InterviewSchedule",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="proposals",
    )
    recruitment = models.ForeignKey(
        "recruitment.Recruitment",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="proposals",
    )
    manpower_request = models.ForeignKey(
        "recruitment.ManpowerRequest",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="proposals",
    )

    # ── General section ─────────────────────────────────────────────
    post_applied_for = models.CharField(max_length=200, blank=True)
    grade_group = models.CharField(max_length=50, blank=True)
    division_department = models.CharField(max_length=200, blank=True)
    post_location = models.CharField(max_length=200, blank=True)
    contractual = models.BooleanField(default=False)
    contract_name = models.CharField(max_length=200, blank=True)
    contract_period_from = models.DateField(null=True, blank=True)
    contract_period_to = models.DateField(null=True, blank=True)
    job_no = models.CharField(max_length=50, blank=True)
    reporting_to = models.CharField(max_length=200, blank=True)
    reporting_staff_no = models.CharField(max_length=50, blank=True)
    gsm_cpn_no = models.CharField(max_length=50, blank=True)

    # ── Brief (Recruitment) ─────────────────────────────────────────
    is_new_appointment = models.BooleanField(default=True)
    replacement_staff_no = models.CharField(max_length=50, blank=True)
    candidate_referred = models.CharField(max_length=20, choices=REFERRAL_CHOICES, blank=True)
    referral_staff_number = models.CharField(max_length=50, blank=True)
    consultancy_reg = models.CharField(max_length=20, choices=CONSULTANCY_CHOICES, blank=True)
    consultancy_other = models.CharField(max_length=120, blank=True)
    employment_contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, blank=True)
    employment_contract_months = models.PositiveIntegerField(null=True, blank=True)
    has_relative_in_company = models.BooleanField(default=False)
    relative_name = models.CharField(max_length=120, blank=True)
    relative_staff_no = models.CharField(max_length=50, blank=True)
    relative_location = models.CharField(max_length=120, blank=True)

    # ── Summary of resume ───────────────────────────────────────────
    application_date = models.DateField(null=True, blank=True)
    interview_date = models.DateField(null=True, blank=True)
    applicant_name = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=80, blank=True)
    present_employer = models.CharField(max_length=200, blank=True)
    local_transfer = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, blank=True)
    dob = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=120, blank=True)
    qualification_academic = models.CharField(max_length=200, blank=True)
    qualification_professional = models.CharField(max_length=200, blank=True)
    experience_local_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    experience_overseas_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    lang_arabic = models.BooleanField(default=False)
    lang_english = models.BooleanField(default=False)
    lang_others = models.CharField(max_length=200, blank=True)
    driving_license = models.CharField(max_length=20, choices=LICENSE_CHOICES, blank=True, default="none")

    # ── Salary recommendation ───────────────────────────────────────
    salary_budgeted = models.CharField(max_length=20, choices=SALARY_BUDGET_CHOICES, blank=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    hra_allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    addl_resp_allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    overtime_allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    food_allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    lsa_allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    lsa_tier = models.CharField(max_length=20, choices=LSA_TIER_CHOICES, blank=True)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    # HRC + CEO columns (Permanent template only) — { row_key: {hrc, ceo} }
    salary_columns_json = models.JSONField(default=dict, blank=True)

    # ── Notes ───────────────────────────────────────────────────────
    air_passage_from = models.CharField(max_length=120, blank=True)
    air_passage_to = models.CharField(max_length=120, blank=True, default="MUSCAT")
    air_passage_months = models.PositiveIntegerField(null=True, blank=True)
    family_status = models.CharField(max_length=20, choices=FAMILY_STATUS_CHOICES, blank=True)
    medical_clause = models.BooleanField(default=True)
    salary_increase_clause = models.TextField(blank=True)
    hod_comments = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Employment Proposal")
        verbose_name_plural = _("Employment Proposals")

    def __str__(self):
        return f"{self.proposal_no} — {self.applicant_name or self.candidate.name}"

    def save(self, *args, **kwargs):
        if not self.proposal_no:
            last = EmploymentProposal.objects.order_by("-id").values_list("id", flat=True).first() or 0
            self.proposal_no = f"EP{last + 1:04d}"
        super().save(*args, **kwargs)

    @property
    def chain_role_keys(self):
        return PERMANENT_CHAIN if self.template_type == self.TEMPLATE_PERMANENT else CONTRACTUAL_CHAIN

    @property
    def is_signed_complete(self):
        return self.status == self.STATUS_APPROVED

    @property
    def is_terminal(self):
        return self.status in (self.STATUS_APPROVED, self.STATUS_REJECTED, self.STATUS_CONVERTED)


class ProposalApproval(models.Model):
    """Sequential e-sign chain for an EmploymentProposal."""

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_APPROVED, _("Approved")),
        (STATUS_REJECTED, _("Rejected")),
    ]

    proposal = models.ForeignKey(
        EmploymentProposal, on_delete=models.CASCADE, related_name="approvals"
    )
    role_key = models.CharField(max_length=40)
    role_label = models.CharField(max_length=120)
    sequence = models.PositiveIntegerField()
    approver = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="proposal_approvals"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    feedback = models.TextField(blank=True)
    signature_image = models.TextField(blank=True, verbose_name=_("Signature (base64)"))
    acted_at = models.DateTimeField(null=True, blank=True)
    esign_provider = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("E-Sign Provider"))
    esign_reference = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("E-Sign Reference"))

    class Meta:
        ordering = ["sequence"]
        verbose_name = _("Proposal Approval")
        verbose_name_plural = _("Proposal Approvals")

    def __str__(self):
        return f"{self.proposal.proposal_no} — {self.role_label} ({self.get_status_display()})"


class ProposalRoleAssignment(models.Model):
    """Maps ONEIC organisational role keys to Employee records.

    One row per role_key, configured by HR via /recruitment/proposals/roles/.
    """

    role_key = models.CharField(max_length=40, unique=True)
    role_label = models.CharField(max_length=120)
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="proposal_role_assignments"
    )

    class Meta:
        ordering = ["role_label"]
        verbose_name = _("Proposal Role Assignment")
        verbose_name_plural = _("Proposal Role Assignments")

    def __str__(self):
        return f"{self.role_label} → {self.employee}"


class ProposalStatusLog(models.Model):
    """Audit trail entries for an EmploymentProposal."""

    proposal = models.ForeignKey(
        EmploymentProposal, on_delete=models.CASCADE, related_name="status_logs"
    )
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="proposal_status_logs",
    )
    action = models.CharField(max_length=40)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.proposal.proposal_no} — {self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"
