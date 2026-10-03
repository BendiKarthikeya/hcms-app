"""
models.py

This module is used to register models for recruitment app

"""

import json
import os
import re
from uuid import uuid4

import django
import requests
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from base.fits_company_manager import FitsCompanyManager
from base.models import Company, JobPosition
from employee.models import Employee
from fits.models import FitsModel, upload_path
from fits_audit.methods import get_diff
from fits_audit.models import FitsAuditInfo, FitsAuditLog
from fits_views.cbv_methods import render_template

# Create your models here.


# --- Post grade (A–F) classification relative to the General Manager line ---
# Grades A/B/C are "below GM" (approval flows to HR Head only); D/E/F are
# "above GM" (approval flows to HR Head -> CEO). Single source of truth reused
# by the recruitment form and the approval-routing logic in views.py.
GRADE_BELOW_GM = ("A", "B", "C")
GRADE_ABOVE_GM = ("D", "E", "F")
GRADE_CHOICES = [
    ("A", _("A — Below General Manager")),
    ("B", _("B — Below General Manager")),
    ("C", _("C — Below General Manager")),
    ("D", _("D — Above General Manager")),
    ("E", _("E — Above General Manager")),
    ("F", _("F — Above General Manager")),
]


def grade_level_label(grade):
    """Return the human label for a post grade, or "" if unset/invalid."""
    g = (grade or "").strip().upper()
    if g in GRADE_ABOVE_GM:
        return _("Above General Manager")
    if g in GRADE_BELOW_GM:
        return _("Below General Manager")
    return ""


def validate_mobile(value):
    """
    This method is used to validate the mobile number using regular expression
    """
    pattern = r"^\+[0-9 ]+$|^[0-9 ]+$"

    if re.match(pattern, value) is None:
        if "+" in value:
            raise forms.ValidationError(
                "Invalid input: Plus symbol (+) should only appear at the beginning \
                    or no other characters allowed."
            )
        raise forms.ValidationError(
            "Invalid input: Only digits and spaces are allowed."
        )


def validate_pdf(value):
    """
    This method is used to validate pdf
    """
    ext = os.path.splitext(value.name)[1]  # Get file extension
    if ext.lower() != ".pdf":
        raise ValidationError(_("File must be a PDF."))


def validate_image(value):
    """
    This method is used to validate the image
    """
    return value


def candidate_photo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.name.replace(' ', '_')}_{filename}_{uuid4()}.{ext}"
    return os.path.join("recruitment/profile/", filename)


class SurveyTemplate(FitsModel):
    """
    SurveyTemplate Model
    """

    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    is_general_template = models.BooleanField(default=False, editable=False)
    company_id = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    objects = FitsCompanyManager("company_id")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Survey Template")
        verbose_name_plural = _("Survey Templates")


class Skill(FitsModel):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        title = self.title
        self.title = title.capitalize()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")


BUDGET_PRIVILEGED_DEPARTMENT_KEYWORDS = ("executive", "execution", "ceo", "sales", "hr")


def _is_privileged_department(dept_name: str) -> bool:
    if not dept_name:
        return False
    low = dept_name.strip().lower()
    return any(kw in low for kw in BUDGET_PRIVILEGED_DEPARTMENT_KEYWORDS)


class Recruitment(FitsModel):
    """
    Recruitment model
    """

    xss_exempt_fields = ["description"]

    POSTING_TYPE_CHOICES = [
        ("internal", _("Internal")),
        ("external", _("External")),
    ]
    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", _("Full Time")),
        ("contract", _("Contract")),
    ]
    posting_type = models.CharField(
        max_length=10,
        choices=POSTING_TYPE_CHOICES,
        default="external",
        verbose_name=_("Posting Type"),
    )
    job_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("Job ID"),
    )
    grade = models.CharField(
        max_length=30, blank=True, null=True, verbose_name=_("Grade")
    )
    band = models.CharField(
        max_length=30, blank=True, null=True, verbose_name=_("Band")
    )
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Budget"),
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="full_time",
        verbose_name=_("Employment Type"),
    )
    expat_allowed = models.BooleanField(
        default=False, verbose_name=_("Expat Allowed")
    )
    location = models.CharField(
        max_length=120, blank=True, null=True, verbose_name=_("Location")
    )
    budget_available = models.BooleanField(
        default=False, verbose_name=_("Budget Available")
    )
    budget_document = models.FileField(
        upload_to="recruitment/budget/",
        blank=True,
        null=True,
        verbose_name=_("Budget Document"),
    )

    title = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Title")
    )
    description = models.TextField(null=True, verbose_name=_("Description"))
    is_event_based = models.BooleanField(
        default=False,
        help_text=_("To start recruitment for multiple job positions"),
    )
    closed = models.BooleanField(
        default=False,
        help_text=_(
            "To close the recruitment, If closed then not visible on pipeline view."
        ),
        verbose_name=_("Closed"),
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_(  
            "To publish a recruitment in website, if false then it \
            will not appear on open recruitment page."
        ),
        verbose_name=_("Is Published"),
    )
    open_positions = models.ManyToManyField(
        JobPosition,
        related_name="open_positions",
        blank=True,
        verbose_name=_("Job Position"),
    )
    job_position_id = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_constraint=False,
        related_name="recruitment",
        verbose_name=_("Job Position"),
        editable=False,
    )
    vacancy = models.IntegerField(default=0, null=True, verbose_name=_("Vacancy"))
    recruitment_managers = models.ManyToManyField(Employee, verbose_name=_("Managers"))
    survey_templates = models.ManyToManyField(
        SurveyTemplate, blank=True, verbose_name=_("Survey Templates")
    )
    company_id = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    start_date = models.DateField(
        default=django.utils.timezone.now, verbose_name=_("Start Date")
    )
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))
    skills = models.ManyToManyField(Skill, blank=True, verbose_name=_("Skills"))
    linkedin_account_id = models.ForeignKey(
        "recruitment.LinkedInAccount",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("LinkedIn Account"),
    )
    linkedin_post_id = models.CharField(max_length=150, null=True, blank=True)
    published_to_linkedin = models.BooleanField(default=False)
    linkedin_posted_at = models.DateTimeField(null=True, blank=True)
    linkedin_external_id = models.CharField(max_length=50, null=True, blank=True)
    published_to_bayt = models.BooleanField(default=False)
    bayt_posted_at = models.DateTimeField(null=True, blank=True)
    bayt_external_id = models.CharField(max_length=50, null=True, blank=True)
    published_to_naukrigulf = models.BooleanField(default=False)
    naukrigulf_posted_at = models.DateTimeField(null=True, blank=True)
    naukrigulf_external_id = models.CharField(max_length=50, null=True, blank=True)
    publish_in_linkedin = models.BooleanField(
        default=True,
        help_text=_(
            "To publish a recruitment in Linkedin, if active is false then it \
            will not post on LinkedIn."
        ),
        verbose_name=_("Post on LinkedIn"),
    )
    objects = FitsCompanyManager()
    default = models.manager.Manager()
    optional_profile_image = models.BooleanField(
        default=False,
        help_text=_("Profile image not mandatory for candidate creation"),
        verbose_name=_("Optional Profile Image"),
    )
    optional_resume = models.BooleanField(
        default=False,
        help_text=_("Resume not mandatory for candidate creation"),
        verbose_name=_("Optional Resume"),
    )
    manpower_request = models.OneToOneField(
        "recruitment.ManpowerRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recruitment_campaign",
        verbose_name=_("Manpower Request"),
    )
    is_public = models.BooleanField(default=False, verbose_name=_("Public on careers page"))
    public_slug = models.SlugField(max_length=120, blank=True, verbose_name=_("Public Slug"))

    raised_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="raised_recruitments",
        verbose_name=_("Raised By"),
    )

    raised_from_employee = models.BooleanField(
        default=False,
        verbose_name=_("Raised from Employee"),
    )

    is_bulk = models.BooleanField(
        default=False,
        verbose_name=_("Bulk Request"),
        help_text=_(
            "True for the umbrella request that groups several positions under a "
            "single approval. On approval it fans out into one published campaign "
            "per BulkRequestLine."
        ),
    )

    justification = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Justification"),
        help_text=_("Business reason for opening this position"),
    )

    approval_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", _( "Pending Approval" )),
            ("approved", _( "Approved" )),
            ("rejected", _( "Rejected" )),
            ("queried", _( "Returned with Query" )),
        ],
        default="pending",
        verbose_name=_("Approval Status"),
    )

    hr_feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("HR Feedback"),
    )

    class Meta:
        """
        Meta class to add the additional info
        """

        unique_together = [
            (
                "job_position_id",
                "start_date",
            ),
            ("job_position_id", "start_date", "company_id"),
        ]
        permissions = (("archive_recruitment", "Archive Recruitment"),)
        verbose_name = _("Recruitment")
        verbose_name_plural = _("Recruitments")

    def total_hires(self):
        """
        This method is used to get the count of
        hired candidates
        """
        return self.candidate.filter(hired=True).count()

    @property
    def grade_level_label(self):
        """'Above General Manager' / 'Below General Manager' for this post's grade."""
        return grade_level_label(self.grade)

    def __str__(self):
        title = (
            f"{self.job_position_id.job_position} {self.start_date}"
            if self.title is None and self.job_position_id
            else self.title
        )

        if not self.is_event_based and self.job_position_id is not None:
            self.open_positions.add(self.job_position_id)

        return title

    def clean(self):
        if self.title is None:
            raise ValidationError({"title": _("This field is required")})
        if self.is_published:
            if self.vacancy <= 0:
                raise ValidationError(
                    _(
                        "Vacancy must be greater than zero if the recruitment is publishing."
                    )
                )

        if self.end_date is not None and (
            self.start_date is not None and self.start_date > self.end_date
        ):
            raise ValidationError(
                {"end_date": _("End date cannot be less than start date.")}
            )
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.publish_in_linkedin:
            self.linkedin_account_id = None
            self.linkedin_post_id = None
        self.is_published = self.posting_type == "external"
        super().save(*args, **kwargs)  # Save the Recruitment instance first
        if not self.job_id:
            self.job_id = f"JB{self.pk:04d}"
            Recruitment.default.filter(pk=self.pk).update(job_id=self.job_id)
        if self.is_event_based and self.open_positions is None:
            raise ValidationError({"open_positions": _("This field is required")})

    def ordered_stages(self):
        """
        This method will returns all the stage respectively to the ascending order of stages
        """
        return self.stage_set.order_by("sequence")

    def is_vacancy_filled(self):
        """
        This method is used to check wether the vaccancy for the recruitment is completed or not
        """
        hired_stage = Stage.objects.filter(
            recruitment_id=self, stage_type="hired"
        ).first()
        if hired_stage:
            hired_candidate = hired_stage.candidate_set.all().exclude(canceled=True)
            if len(hired_candidate) >= self.vacancy:
                return True


class RecruitmentApproval(FitsModel):
    recruitment = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        related_name="approvals",
        verbose_name=_("Recruitment"),
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="recruitment_approvals",
        verbose_name=_("Approver"),
    )
    sequence = models.PositiveIntegerField(default=1, verbose_name=_("Sequence"))
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", _("Pending")),
            ("approved", _("Approved")),
            ("rejected", _("Rejected")),
            ("queried", _("Returned with Query")),
        ],
        default="pending",
        verbose_name=_("Approval Status"),
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Approved At")
    )
    comments = models.TextField(blank=True, null=True, verbose_name=_("Comments"))
    signature_image = models.TextField(blank=True, verbose_name=_("Signature (base64)"))

    class Meta:
        ordering = ["sequence"]
        verbose_name = _("Recruitment Approval")
        verbose_name_plural = _("Recruitment Approvals")

    def __str__(self):
        return f"{self.recruitment} - {self.approver} ({self.get_status_display()})"


class BulkRequestLine(FitsModel):
    """
    One position line inside a bulk recruitment request (e.g. "20 Electricians").

    The bulk request itself is a single Recruitment with ``is_bulk=True`` and one
    approval chain. Each line is a position + vacancy count. When the bulk request
    is fully approved, every line fans out into its own published Recruitment
    campaign (linked back via ``published_recruitment``) so external candidates
    apply per role; proposals/offers then proceed per-candidate as normal.
    """

    recruitment = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        related_name="bulk_lines",
        verbose_name=_("Bulk Request"),
    )
    title = models.CharField(max_length=120, verbose_name=_("Position / Title"))
    job_position = models.ForeignKey(
        JobPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False,
        related_name="bulk_request_lines",
        verbose_name=_("Job Position"),
    )
    vacancy = models.PositiveIntegerField(default=1, verbose_name=_("Vacancies"))
    published_recruitment = models.ForeignKey(
        Recruitment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bulk_source_line",
        verbose_name=_("Published Campaign"),
        help_text=_("The campaign spawned for this line once the bulk request is approved."),
    )

    objects = FitsCompanyManager(related_company_field="recruitment__company_id")
    default = models.manager.Manager()

    class Meta:
        ordering = ["id"]
        verbose_name = _("Bulk Request Line")
        verbose_name_plural = _("Bulk Request Lines")

    def __str__(self):
        return f"{self.vacancy} × {self.title}"


class Stage(FitsModel):
    """
    Stage model
    """

    stage_types = [
        ("initial", _("Initial")),
        ("applied", _("Applied")),
        ("test", _("Test")),
        ("interview", _("Interview")),
        ("cancelled", _("Cancelled")),
        ("hired", _("Hired")),
    ]
    recruitment_id = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        related_name="stage_set",
        verbose_name=_("Recruitment"),
    )
    stage_managers = models.ManyToManyField(Employee, verbose_name=_("Stage Managers"))
    stage = models.CharField(max_length=50, verbose_name=_("Stage"))
    stage_type = models.CharField(
        max_length=20,
        choices=stage_types,
        default="interview",
        verbose_name=_("Stage Type"),
    )
    sequence = models.IntegerField(null=True, default=0)
    objects = FitsCompanyManager(related_company_field="recruitment_id__company_id")

    def __str__(self):
        return f"{self.stage}"

    class Meta:
        """
        Meta class to add the additional info
        """

        permissions = (("archive_Stage", "Archive Stage"),)
        unique_together = ["recruitment_id", "stage"]
        ordering = ["sequence"]
        verbose_name = _("Stage")
        verbose_name_plural = _("Stages")

    def __str__(self):
        return f"{self.stage} - ({self.recruitment_id.title})"

    def active_candidates(self):
        """
        This method is used to get all the active candidate like related objects
        """
        return {
            "all": Candidate.objects.filter(
                stage_id=self, canceled=False, is_active=True
            )
        }


def candidate_upload_path(instance, filename):
    """
    Generates a unique file path for candidate profile & resume uploads.
    """
    ext = filename.split(".")[-1]
    name_slug = slugify(instance.name) or "candidate"
    unique_filename = f"{name_slug}-{uuid4().hex[:8]}.{ext}"
    return f"recruitment/{name_slug}/{unique_filename}"


class Candidate(FitsModel):
    """
    Candidate model
    """

    choices = [("male", _("Male")), ("female", _("Female")), ("other", _("Other"))]
    offer_letter_statuses = [
        ("not_sent", _("Not Sent")),
        ("sent", _("Sent")),
        ("accepted", _("Accepted")),
        ("rejected", _("Rejected")),
        ("joined", _("Joined")),
    ]
    source_choices = [
        ("application", _("Application Form")),
        ("software", _("Inside software")),
        ("linkedin", _("LinkedIn")),
        ("bayt", _("Bayt.com")),
        ("naukrigulf", _("NaukriGulf")),
        ("other", _("Other")),
    ]
    name = models.CharField(max_length=100, null=True, verbose_name=_("Name"))
    profile = models.ImageField(upload_to=upload_path, null=True)  # 853
    portfolio = models.URLField(max_length=200, blank=True)
    recruitment_id = models.ForeignKey(
        Recruitment,
        on_delete=models.PROTECT,
        null=True,
        related_name="candidate",
        verbose_name=_("Recruitment"),
    )
    job_position_id = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Job Position"),
    )
    stage_id = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_("Stage"),
    )
    converted_employee_id = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="candidate_get",
        verbose_name=_("Employee"),
    )
    schedule_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Schedule date")
    )
    email = models.EmailField(max_length=254, verbose_name=_("Email"))
    mobile = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            validate_mobile,
        ],
        verbose_name=_("Mobile"),
    )
    resume = models.FileField(
        upload_to=upload_path,  # 853
        validators=[
            validate_pdf,
        ],
    )
    referral = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="candidate_referral",
        verbose_name=_("Referral"),
    )
    address = models.TextField(
        null=True, blank=True, verbose_name=_("Address"), max_length=255
    )
    country = models.CharField(
        max_length=30, null=True, blank=True, verbose_name=_("Country")
    )
    dob = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    state = models.CharField(
        max_length=30, null=True, blank=True, verbose_name=_("State")
    )
    city = models.CharField(
        max_length=30, null=True, blank=True, verbose_name=_("City")
    )
    zip = models.CharField(
        max_length=30, null=True, blank=True, verbose_name=_("Zip Code")
    )
    gender = models.CharField(
        max_length=15,
        choices=choices,
        null=True,
        default="male",
        verbose_name=_("Gender"),
    )
    source = models.CharField(
        max_length=20,
        choices=source_choices,
        null=True,
        blank=True,
        verbose_name=_("Source"),
    )
    start_onboard = models.BooleanField(default=False, verbose_name=_("Start Onboard"))
    hired = models.BooleanField(default=False, verbose_name=_("Hired"))
    canceled = models.BooleanField(default=False, verbose_name=_("Canceled"))
    converted = models.BooleanField(default=False, verbose_name=_("Converted"))
    joining_date = models.DateField(
        blank=True, null=True, verbose_name=_("Joining Date")
    )
    history = FitsAuditLog(
        related_name="history_set",
        bases=[
            FitsAuditInfo,
        ],
    )
    sequence = models.IntegerField(null=True, default=0)
    experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, default=0, blank=True, verbose_name=_("Experience (years)")
    )
    notice_period_days = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Notice Period (days)")
    )
    availability_date = models.DateField(
        null=True, blank=True, verbose_name=_("Availability Date")
    )
    project_id = models.ForeignKey(
        "project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Project"),
    )

    cover_letter = models.FileField(
        upload_to="recruitment/candidate/cover_letter/%Y/",
        null=True,
        blank=True,
        verbose_name=_("Cover Letter"),
    )
    graduation_certificate = models.FileField(
        upload_to="recruitment/candidate/certificates/%Y/",
        null=True,
        blank=True,
        verbose_name=_("Graduation Certificate"),
    )
    transcripts = models.FileField(
        upload_to="recruitment/candidate/transcripts/%Y/",
        null=True,
        blank=True,
        verbose_name=_("Transcripts"),
    )
    promoted_to_onboarding = models.BooleanField(
        default=False,
        verbose_name=_("Promoted to Onboarding"),
    )
    probation_end = models.DateField(null=True, editable=False)
    offer_letter_status = models.CharField(
        max_length=10,
        choices=offer_letter_statuses,
        default="not_sent",
        editable=False,
        verbose_name=_("Offer Letter Status"),
    )
    objects = FitsCompanyManager(related_company_field="recruitment_id__company_id")
    last_updated = models.DateField(null=True, auto_now=True)

    converted_employee_id.exclude_from_automation = True
    mail_to_related_fields = [
        ("stage_id__stage_managers__get_mail", "Stage Managers"),
        ("recruitment_id__recruitment_managers__get_mail", "Recruitment Managers"),
    ]
    hired_date = models.DateField(null=True, blank=True, editable=False)

    def __str__(self):
        return f"{self.name}"

    def is_offer_rejected(self):
        """
        Is offer rejected checking method
        """
        first = RejectedCandidate.objects.filter(candidate_id=self).first()
        if first:
            return first.reject_reason_id.count() > 0
        return first

    def get_full_name(self):
        """
        Method will return employee full name
        """
        return str(self.name)

    def get_avatar(self):
        """
        Method will rerun the api to the avatar or path to the profile image
        """
        if self.profile and default_storage.exists(self.profile.name):
            return self.profile.url
        return static("images/ui/default_avatar.jpg")

    def get_company(self):
        """
        This method is used to return the company
        """
        return getattr(
            getattr(getattr(self, "recruitment_id", None), "company_id", None),
            "company",
            None,
        )

    def get_job_position(self):
        """
        This method is used to return the job position of the candidate
        """
        return self.job_position_id.job_position

    def get_email(self):
        """
        Return email
        """
        return self.email

    def get_mail(self):
        """ """
        return self.get_email()

    def phone(self):
        return self.mobile

    def tracking(self):
        """
        This method is used to return the tracked history of the instance
        """
        return get_diff(self)

    def get_last_sent_mail(self):
        """
        This method is used to get last send mail
        """
        from base.models import EmailLog

        return (
            EmailLog.objects.filter(to__icontains=self.email)
            .order_by("-created_at")
            .first()
        )

    def get_interview(self):
        """
        This method is used to get the interview dates and times
        for the candidate for the mail templates
        """

        interviews = InterviewSchedule.objects.filter(candidate_id=self.id)
        if interviews:
            interview_info = "<table>"
            interview_info += "<tr><th>Sl No.</th><th>Date</th><th>Time</th><th>Is Completed</th></tr>"
            for index, interview in enumerate(interviews, start=1):
                interview_info += f"<tr><td>{index}</td>"
                interview_info += (
                    f"<td class='dateformat_changer'>{interview.interview_date}</td>"
                )
                interview_info += (
                    f"<td class='timeformat_changer'>{interview.interview_time}</td>"
                )
                interview_info += (
                    f"<td>{'Yes' if interview.completed else 'No'}</td></tr>"
                )
            interview_info += "</table>"
            return interview_info
        else:
            return ""

    def save(self, *args, **kwargs):
        if self.stage_id is not None:
            self.hired = self.stage_id.stage_type == "hired"

        if self.recruitment_id is not None:
            if not self.recruitment_id.is_event_based and self.job_position_id is None:
                self.job_position_id = self.recruitment_id.job_position_id
            if self.job_position_id is not None and self.job_position_id not in self.recruitment_id.open_positions.all():
                raise ValidationError({"job_position_id": _("Choose valid choice")})
            if self.recruitment_id.is_event_based and self.job_position_id is None:
                raise ValidationError({"job_position_id": _("This field is required.")})
        if self.stage_id and self.stage_id.stage_type == "cancelled":
            self.canceled = True
        if self.canceled:
            cancelled_stage = Stage.objects.filter(
                recruitment_id=self.recruitment_id, stage_type="cancelled"
            ).first()
            if not cancelled_stage:
                cancelled_stage = Stage.objects.create(
                    recruitment_id=self.recruitment_id,
                    stage="Cancelled Candidates",
                    stage_type="cancelled",
                    sequence=50,
                )
            self.stage_id = cancelled_stage
        if (
            self.converted_employee_id
            and Candidate.objects.filter(
                converted_employee_id=self.converted_employee_id
            )
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError(_("Employee is uniques for candidate"))

        if self.converted:
            self.hired = False
            self.canceled = False

        super().save(*args, **kwargs)

    class Meta:
        """
        Meta class to add the additional info
        """

        unique_together = (
            "email",
            "recruitment_id",
        )
        permissions = (
            ("view_history", "View Candidate History"),
            ("archive_candidate", "Archive Candidate"),
        )
        ordering = ["sequence"]
        verbose_name = _("Candidate")
        verbose_name_plural = _("Candidates")
        indexes = [
            models.Index(fields=["recruitment_id", "stage_id"]),
            models.Index(fields=["job_position_id", "stage_id"]),
            models.Index(fields=["is_active", "recruitment_id"]),
            models.Index(fields=["offer_letter_status"]),
            models.Index(fields=["hired"]),
        ]


class RejectReason(FitsModel):
    """
    RejectReason
    """

    title = models.CharField(
        max_length=50,
    )
    description = models.TextField(null=True, blank=True, max_length=255)
    company_id = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    objects = FitsCompanyManager()

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Reject Reason")
        verbose_name_plural = _("Reject Reasons")


class RejectedCandidate(FitsModel):
    """
    RejectedCandidate
    """

    candidate_id = models.OneToOneField(
        Candidate,
        on_delete=models.PROTECT,
        verbose_name="Candidate",
        related_name="rejected_candidate",
    )
    reject_reason_id = models.ManyToManyField(
        RejectReason, verbose_name="Reject reason", blank=True
    )
    description = models.TextField(max_length=255)
    objects = FitsCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )
    history = FitsAuditLog(
        related_name="history_set",
        bases=[
            FitsAuditInfo,
        ],
    )

    class Meta:
        verbose_name = _("Rejected Candidate")
        verbose_name_plural = _("Rejected Candidates")

    def __str__(self) -> str:
        reasons = ", ".join(self.reject_reason_id.values_list("title", flat=True))
        return f"{self.candidate_id} - {reasons if reasons else 'No Reason'}"


class StageFiles(FitsModel):
    files = models.FileField(upload_to=upload_path, blank=True, null=True)

    def __str__(self):
        return self.files.name.split("/")[-1]


class StageNote(FitsModel):
    """
    StageNote model
    """

    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    description = models.TextField(verbose_name=_("Description"))  # 905
    stage_id = models.ForeignKey(Stage, on_delete=models.CASCADE)
    stage_files = models.ManyToManyField(StageFiles, blank=True)
    updated_by = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True
    )
    candidate_can_view = models.BooleanField(default=False)
    objects = FitsCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )

    def __str__(self) -> str:
        return f"{self.description}"

    def updated_user(self):
        if self.updated_by:
            return self.updated_by
        else:
            return self.candidate_id


class RecruitmentSurvey(FitsModel):
    """
    RecruitmentSurvey model
    """

    question_types = [
        ("checkbox", _("Yes/No")),
        ("options", _("Choices")),
        ("multiple", _("Multiple Choice")),
        ("text", _("Text")),
        ("number", _("Number")),
        ("percentage", _("Percentage")),
        ("date", _("Date")),
        ("textarea", _("Textarea")),
        ("file", _("File Upload")),
        ("rating", _("Rating")),
    ]
    question = models.TextField(null=False, max_length=255)
    template_id = models.ManyToManyField(
        SurveyTemplate, verbose_name="Template", blank=True
    )
    is_mandatory = models.BooleanField(default=False)
    recruitment_ids = models.ManyToManyField(
        Recruitment,
        verbose_name=_("Recruitment"),
    )
    question = models.TextField(null=False)
    job_position_ids = models.ManyToManyField(
        JobPosition, verbose_name=_("Job Positions"), editable=False
    )
    sequence = models.IntegerField(null=True, default=0)
    type = models.CharField(
        max_length=15,
        choices=question_types,
    )
    options = models.TextField(
        null=True, default="", help_text=_("Separate choices by ',  '"), max_length=255
    )
    objects = FitsCompanyManager(related_company_field="recruitment_ids__company_id")

    def __str__(self) -> str:
        return str(self.question)

    def choices(self):
        """
        Used to split the choices
        """
        return self.options.split(", ")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.template_id is None:
            general_template = SurveyTemplate.objects.filter(
                is_general_template=True
            ).first()
            if general_template:
                self.template_id.add(general_template)
                super().save(*args, **kwargs)

    class Meta:
        ordering = [
            "sequence",
        ]


class QuestionOrdering(FitsModel):
    """
    Survey Template model
    """

    question_id = models.ForeignKey(RecruitmentSurvey, on_delete=models.CASCADE)
    recruitment_id = models.ForeignKey(Recruitment, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    objects = FitsCompanyManager(related_company_field="recruitment_ids__company_id")


class RecruitmentSurveyAnswer(FitsModel):
    """
    RecruitmentSurveyAnswer
    """

    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    recruitment_id = models.ForeignKey(
        Recruitment,
        on_delete=models.PROTECT,
        verbose_name=_("Recruitment"),
        null=True,
    )
    job_position_id = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        verbose_name=_("Job Position"),
        null=True,
    )
    answer_json = models.JSONField()
    attachment = models.FileField(upload_to=upload_path, null=True, blank=True)
    objects = FitsCompanyManager(related_company_field="recruitment_id__company_id")

    @property
    def answer(self):
        """
        Used to convert the json to dict
        """
        # Convert the JSON data to a dictionary
        try:
            return json.loads(self.answer_json)
        except json.JSONDecodeError:
            return {}  # Return an empty dictionary if JSON is invalid or empty

    def __str__(self) -> str:
        return f"{self.candidate_id.name}-{self.recruitment_id}"


class SkillZone(FitsModel):
    """ "
    Model for talent pool
    """

    title = models.CharField(max_length=50, verbose_name="Skill Zone")
    description = models.TextField(verbose_name=_("Description"), max_length=255)
    company_id = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    objects = FitsCompanyManager()

    class Meta:
        verbose_name = _("Skill Zone")
        verbose_name_plural = _("Skill Zones")

    def get_active(self):
        return SkillZoneCandidate.objects.filter(is_active=True, skill_zone_id=self)

    def __str__(self) -> str:
        return self.title


class SkillZoneCandidate(FitsModel):
    """
    Model for saving candidate data's for future recruitment
    """

    skill_zone_id = models.ForeignKey(
        SkillZone,
        verbose_name=_("Skill Zone"),
        related_name="skillzonecandidate_set",
        on_delete=models.PROTECT,
        null=True,
    )
    candidate_id = models.ForeignKey(
        Candidate,
        on_delete=models.PROTECT,
        null=True,
        related_name="skillzonecandidate_set",
        verbose_name=_("Candidate"),
    )
    # job_position_id=models.ForeignKey(
    #     JobPosition,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     related_name="talent_pool",
    #     verbose_name=_("Job Position")
    # )

    reason = models.CharField(max_length=200, verbose_name=_("Reason"))
    added_on = models.DateField(auto_now_add=True)
    objects = FitsCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )

    def clean(self):
        # Check for duplicate entries in the database
        duplicate_exists = (
            SkillZoneCandidate.objects.filter(
                candidate_id=self.candidate_id, skill_zone_id=self.skill_zone_id
            )
            .exclude(pk=self.pk)
            .exists()
        )

        if duplicate_exists:
            raise ValidationError(
                _(
                    f"Candidate {self.candidate_id} already exists in Skill Zone {self.skill_zone_id}."
                )
            )

        super().clean()

    def __str__(self) -> str:
        return str(self.candidate_id.get_full_name())


class CandidateRating(FitsModel):
    employee_id = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="candidate_rating"
    )
    candidate_id = models.ForeignKey(
        Candidate, on_delete=models.PROTECT, related_name="candidate_rating"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ["employee_id", "candidate_id"]

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.candidate_id} rating {self.rating}"


class RecruitmentGeneralSetting(FitsModel):
    """
    RecruitmentGeneralSettings model
    """

    candidate_self_tracking = models.BooleanField(default=False)
    show_overall_rating = models.BooleanField(default=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)


class InterviewSchedule(FitsModel):
    """
    Interview Scheduling Model
    """

    candidate_id = models.ForeignKey(
        Candidate,
        verbose_name=_("Candidate"),
        related_name="candidate_interview",
        on_delete=models.CASCADE,
    )
    employee_id = models.ManyToManyField(Employee, verbose_name=_("Interviewer"))
    interview_date = models.DateField(verbose_name=_("Interview Date"))
    interview_time = models.TimeField(null=True, blank=True, verbose_name=_("Interview Time"))
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    completed = models.BooleanField(
        default=False, verbose_name=_("Is Interview Completed")
    )
    online_meeting_link = models.URLField(
        blank=True, verbose_name=_("Online Meeting Link")
    )
    meeting_provider = models.CharField(
        max_length=20,
        choices=[("manual", "Manual"), ("teams", "Teams"), ("zoom", "Zoom"), ("meet", "Google Meet")],
        default="manual",
        verbose_name=_("Meeting Provider"),
    )
    invite_sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Invite Sent At"))
    num_rounds = models.PositiveIntegerField(default=1, verbose_name=_("Number of Rounds"))
    objects = FitsCompanyManager("candidate_id__recruitment_id__company_id")

    def __str__(self) -> str:
        return f"{self.candidate_id} -Interview."

    class Meta:
        verbose_name = _("Schedule Interview")
        verbose_name_plural = _("Schedule Interviews")


class Resume(models.Model):
    file = models.FileField(
        upload_to=upload_path,
        validators=[
            validate_pdf,
        ],
    )
    recruitment_id = models.ForeignKey(
        Recruitment, on_delete=models.CASCADE, related_name="resume"
    )
    is_candidate = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recruitment_id} - Resume {self.pk}"


STATUS = [
    ("requested", "Requested"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

FORMATS = [
    ("any", "Any"),
    ("pdf", "PDF"),
    ("txt", "TXT"),
    ("docx", "DOCX"),
    ("xlsx", "XLSX"),
    ("jpg", "JPG"),
    ("png", "PNG"),
    ("jpeg", "JPEG"),
]


class CandidateDocumentRequest(FitsModel):
    title = models.CharField(max_length=100)
    candidate_id = models.ManyToManyField(Candidate)
    format = models.CharField(choices=FORMATS, max_length=10)
    max_size = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    objects = FitsCompanyManager(
        related_company_field="employee_id__employee_work_info__company_id"
    )

    def __str__(self):
        return self.title


class CandidateDocument(FitsModel):
    title = models.CharField(max_length=250)
    candidate_id = models.ForeignKey(
        Candidate, on_delete=models.PROTECT, verbose_name="Candidate"
    )
    document_request_id = models.ForeignKey(
        CandidateDocumentRequest, on_delete=models.PROTECT, null=True
    )
    document = models.FileField(upload_to=upload_path, null=True)
    status = models.CharField(choices=STATUS, max_length=10, default="requested")
    reject_reason = models.TextField(blank=True, null=True, max_length=255)

    def __str__(self):
        return f"{self.candidate_id} - {self.title}"

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        file = self.document

        if len(self.title) < 3:
            raise ValidationError({"title": _("Title must be at least 3 characters")})

        if file and self.document_request_id:
            format = self.document_request_id.format
            max_size = self.document_request_id.max_size
            if max_size:
                if file.size > max_size * 1024 * 1024:
                    raise ValidationError(
                        {"document": _("File size exceeds the limit")}
                    )

            ext = file.name.split(".")[1].lower()
            if format == "any":
                pass
            elif ext != format:
                raise ValidationError(
                    {"document": _("Please upload {} file only.").format(format)}
                )


class LinkedInAccount(FitsModel):
    username = models.CharField(max_length=250, verbose_name=_("App Name"))
    email = models.EmailField(max_length=254, verbose_name=_("Email"))
    api_token = models.CharField(max_length=500, verbose_name=_("API Token"))
    sub_id = models.CharField(max_length=250, unique=True)
    organization_id = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name=_("LinkedIn Organization ID"),
        help_text=_("Numeric LinkedIn company page ID. When set, posts go to the company page instead of personal feed."),
    )
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, verbose_name=_("Company")
    )

    class Meta:
        verbose_name = _("LinkedIn Account")
        verbose_name_plural = _("LinkedIn Accounts")

    def __str__(self):
        return str(self.username)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if not data["email"] == self.email:
                raise ValidationError({"email": _("Email mismatched.")})
            self.sub_id = response.json()["sub"]
        else:
            raise ValidationError(_("Check the credentials"))

    def action_template(self):
        """
        This method for get custom column for managers.
        """
        return render_template(
            path="linkedin/linkedin_action.html",
            context={"instance": self},
        )

    def is_active_toggle(self):
        """
        For toggle is_active field
        """
        url = f"update-isactive-linkedin-account/{self.id}"
        return render_template(
            path="is_active_toggle.html",
            context={"instance": self, "url": url},
        )


def _offer_no():
    return f"OL-{uuid4().hex[:8].upper()}"


def _render_offer_body(template_text, offer):
    """Render an offer-letter template body with offer + candidate context.

    Supports Django-style {{var}} placeholders so unknown variables render blank
    instead of raising. Used for both DB-selected templates and the default
    text fallback.
    """
    from django.template import Template, Context
    from django.utils import timezone

    candidate = offer.candidate_id
    recruitment = getattr(candidate, "recruitment_id", None)
    company = getattr(recruitment, "company_id", None) if recruitment else None

    ctx = {
        "candidate_name": candidate.name or "",
        "position": offer.position or "",
        "department": offer.department or "",
        "basic_salary": f"{offer.currency} {offer.basic_salary:,.2f}" if offer.basic_salary is not None else "",
        "gross_salary": f"{offer.currency} {offer.gross_salary:,.2f}" if offer.gross_salary else "TBD",
        "currency": offer.currency or "",
        "joining_date": offer.joining_date.strftime("%d %b %Y") if offer.joining_date else "",
        "probation_period": offer.probation_period or "",
        "contract_duration": offer.contract_duration or "Permanent",
        "company_name": company.company if company and hasattr(company, "company") else (getattr(company, "name", "") if company else ""),
        "nationality": getattr(candidate, "country", "") or "",
        "dob": candidate.dob.strftime("%d %b %Y") if getattr(candidate, "dob", None) else "",
        "birth_place": getattr(candidate, "country", "") or "",
        "present_employer": "",
        "reporting_to": "",
        "application_date": candidate.created_at.strftime("%d %b %Y") if getattr(candidate, "created_at", None) else "",
        "interview_date": offer.candidate_id.schedule_date.strftime("%d %b %Y") if getattr(offer.candidate_id, "schedule_date", None) else "",
        "today_date": timezone.now().strftime("%d %b %Y"),
    }
    try:
        return Template(template_text).render(Context(ctx))
    except Exception:
        return template_text


class OfferLetter(FitsModel):
    """
    OfferLetter Model - For managing candidate offer letters
    """

    offer_letter_statuses = [
        ("draft", _("Draft")),
        ("pending_approval", _("Pending Approval")),
        ("sent", _("Sent")),
        ("accepted", _("Accepted")),
        ("rejected", _("Rejected")),
        ("joined", _("Joined")),
    ]

    offer_no = models.CharField(
        max_length=20, default=_offer_no, unique=True, verbose_name=_("Offer No")
    )
    candidate_id = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE,
        related_name="offer_letter",
        verbose_name=_("Candidate"),
    )
    position = models.CharField(max_length=100, verbose_name=_("Position"))
    department = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Department")
    )

    # Compensation details
    basic_salary = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Basic Salary")
    )
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Gross Salary"),
    )
    currency = models.CharField(max_length=3, default="OMR", verbose_name=_("Currency"))

    # Employment details
    ROLE_TYPE_CHOICES = [
        ("full_time", _("Full Time")),
        ("contract", _("Contract")),
    ]
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_TYPE_CHOICES,
        default="full_time",
        verbose_name=_("Role Type"),
    )
    joining_date = models.DateField(verbose_name=_("Joining Date"))
    contract_duration = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duration in months",
        verbose_name=_("Contract Duration (Months)"),
    )
    probation_period = models.IntegerField(
        default=3,
        help_text="Duration in months",
        verbose_name=_("Probation Period (Months)"),
    )

    location = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("Work Location")
    )

    # Terms and conditions
    job_description = models.TextField(
        null=True, blank=True, verbose_name=_("Job Description")
    )
    terms_conditions = models.TextField(
        null=True, blank=True, verbose_name=_("Terms & Conditions")
    )

    # Letter details
    letter_template = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Letter Template"),
        help_text="Use {{basic_salary}}, {{joining_date}}, {{position}}, {{candidate_name}} as placeholders",
    )
    generated_letter = models.TextField(
        null=True, blank=True, editable=False, verbose_name=_("Generated Letter")
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=offer_letter_statuses,
        default="draft",
        verbose_name=_("Status"),
    )
    sent_date = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("Sent Date")
    )
    accepted_date = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("Accepted Date")
    )
    rejected_date = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("Rejected Date")
    )
    rejection_reason = models.TextField(
        null=True, blank=True, verbose_name=_("Rejection Reason")
    )
    approval_submitted_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Approval Submitted At")
    )

    # Phase 6 — Post-offer clearance tracking
    CLEARANCE_STATUS = [
        ("pending", _("Pending")),
        ("in_progress", _("In Progress")),
        ("cleared", _("Cleared")),
        ("blocked", _("Blocked")),
    ]
    JOINING_STATUS = [
        ("not_started", _("Not Started")),
        ("in_progress", _("In Progress")),
        ("joined", _("Joined")),
        ("no_show", _("No Show")),
    ]
    medical_status = models.CharField(max_length=15, choices=CLEARANCE_STATUS, default="pending", verbose_name=_("Medical Status"))
    visa_status = models.CharField(max_length=15, choices=CLEARANCE_STATUS, default="pending", verbose_name=_("Visa Status"))
    labour_clearance_status = models.CharField(max_length=15, choices=CLEARANCE_STATUS, default="pending", verbose_name=_("Labour Clearance"))
    documents_completion_pct = models.PositiveIntegerField(default=0, verbose_name=_("Documents %"))
    joining_status = models.CharField(max_length=15, choices=JOINING_STATUS, default="not_started", verbose_name=_("Joining Status"))
    medical_cleared_at = models.DateTimeField(null=True, blank=True)
    visa_cleared_at = models.DateTimeField(null=True, blank=True)
    labour_cleared_at = models.DateTimeField(null=True, blank=True)

    # Candidate portal — public token-based access for document uploads
    candidate_signature_token = models.UUIDField(
        default=uuid4, unique=True, editable=False,
        verbose_name=_("Candidate Signature Token"),
    )
    candidate_signed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Candidate Signed At")
    )
    portal_token = models.UUIDField(
        default=uuid4, unique=True, editable=False,
        verbose_name=_("Portal Token"),
    )

    @property
    def clearance_statuses(self):
        return [self.medical_status, self.visa_status, self.labour_clearance_status]

    # Audit trail
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offer_letters_created",
        verbose_name=_("Created By"),
    )
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Created On"))
    modified_on = models.DateTimeField(auto_now=True, verbose_name=_("Modified On"))

    objects = FitsCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )

    class Meta:
        verbose_name = _("Offer Letter")
        verbose_name_plural = _("Offer Letters")
        ordering = ["-created_on"]

    def __str__(self):
        return f"Offer Letter - {self.candidate_id.name}"

    def save(self, *args, **kwargs):
        """Generate offer letter content on save"""
        
        # Generate letter if template is set and not already generated
        if self.letter_template and not self.generated_letter:
            try:
                self.generated_letter = _render_offer_body(self.letter_template, self)
            except Exception:
                pass

        # Update candidate offer letter status
        self.candidate_id.offer_letter_status = self.status
        self.candidate_id.save()

        super().save(*args, **kwargs)

    def generate_offer_letter(self, template_text=None):
        """Generate offer letter from template or default text"""

        template = template_text or self.get_default_template()
        self.generated_letter = _render_offer_body(template, self)
        return self.generated_letter

    def get_default_template(self):
        """Return default offer letter template"""
        return """
Dear {{candidate_name}},

We are pleased to offer you the position of {{position}} at {{company_name}}.

Position Details:
- Position: {{position}}
- Department: {{department}}
- Joining Date: {{joining_date}}

Compensation:
- Basic Salary: {{basic_salary}} per month
- Gross Salary: {{gross_salary}} per month

Contract Duration: {contract_duration_months} months
Probation Period: {probation_period_months} months

We look forward to working with you.

Best Regards,
Human Resources Department
{{company_name}}
        """.format(
            contract_duration_months=self.contract_duration or "2 years",
            probation_period_months=self.probation_period,
        )

    def send_offer_letter(self):
        """Send offer letter to candidate via email"""
        from django.core.mail import send_mail
        from django.utils import timezone

        if not self.generated_letter:
            self.generate_offer_letter()

        try:
            send_mail(
                subject=f"Offer Letter - {self.position}",
                message=self.generated_letter,
                from_email="hr@company.com",
                recipient_list=[self.candidate_id.email],
                fail_silently=False,
            )
            self.status = "sent"
            self.sent_date = timezone.now()
            self.save()
            return True
        except Exception:
            return False

    def accept_offer(self):
        """Mark offer as accepted by candidate"""
        from django.utils import timezone

        self.status = "accepted"
        self.accepted_date = timezone.now()
        self.candidate_id.offer_letter_status = "accepted"
        self.save()

    def reject_offer(self, reason=""):
        """Mark offer as rejected by candidate"""
        from django.utils import timezone

        self.status = "rejected"
        self.rejected_date = timezone.now()
        self.rejection_reason = reason
        self.candidate_id.offer_letter_status = "rejected"
        self.save()


class CandidateScreeningProfile(models.Model):
    SCREENING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("screened", "Screened"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
    ]

    candidate = models.OneToOneField(
        'Candidate',
        on_delete=models.CASCADE,
        related_name='screening_profile'
    )

    extracted_skills = models.JSONField(default=list, blank=True)
    years_experience = models.IntegerField(default=0)
    education = models.JSONField(default=list, blank=True)
    previous_positions = models.JSONField(default=list, blank=True)

    # Personal details extracted from CV
    extracted_nationality = models.CharField(max_length=100, blank=True)
    extracted_present_employer = models.CharField(max_length=200, blank=True)
    extracted_marital_status = models.CharField(max_length=20, blank=True)
    extracted_dob = models.DateField(null=True, blank=True)
    extracted_place_of_birth = models.CharField(max_length=120, blank=True)
    extracted_qualification_academic = models.CharField(max_length=200, blank=True)
    extracted_qualification_professional = models.CharField(max_length=200, blank=True)
    extracted_experience_local_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    extracted_experience_overseas_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    extracted_lang_arabic = models.BooleanField(default=False)
    extracted_lang_english = models.BooleanField(default=False)
    extracted_lang_others = models.CharField(max_length=200, blank=True)
    extracted_driving_license = models.CharField(max_length=20, blank=True)

    matching_score = models.IntegerField(default=0)
    matching_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    summary = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=SCREENING_STATUS_CHOICES, default="pending"
    )
    recommendation = models.CharField(
        max_length=100,
        choices=[
            ("auto_shortlist", "Auto-Shortlist"),
            ("interview", "Interview"),
            ("reject", "Reject"),
        ],
        null=True,
        blank=True,
    )

    screened_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    screened_at = models.DateTimeField(auto_now_add=True)
    ai_model = models.CharField(max_length=100, null=True, blank=True)

    # ONEIC Interview Evaluation Form fields (HR&A/IAF/3.0/17)
    scoring_breakdown = models.JSONField(default=dict, blank=True)
    ai_reasoning = models.TextField(blank=True)
    oneic_grand_total = models.FloatField(default=0)
    oneic_percentage = models.FloatField(default=0)

    # HR Override — set when HR manually promotes a candidate the AI marked as Reject
    hr_override = models.BooleanField(default=False)
    hr_override_justification = models.TextField(blank=True, null=True)


class JobApplication(models.Model):
    recruitment = models.ForeignKey(
        "Recruitment",
        on_delete=models.CASCADE,
        related_name="job_applications",
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    why_apply = models.TextField(blank=True, null=True)
    resume_path = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("applied", "Applied"),
            ("screened", "Screened"),
            ("rejected", "Rejected"),
        ],
        default="applied",
    )
    score = models.IntegerField(null=True, blank=True)
    ai_reason = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    rejection_justification = models.TextField(blank=True, null=True)
    rejection_email_sent = models.BooleanField(default=False)
    hr_override = models.BooleanField(default=False)
    hr_override_justification = models.TextField(blank=True, null=True)
    excluded_by_second_filter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} → {self.recruitment.title}"


class JobEmailTemplate(models.Model):
    name              = models.CharField(max_length=100)
    selection_subject = models.CharField(max_length=200)
    selection_body    = models.TextField()
    rejection_subject = models.CharField(max_length=200)
    rejection_body    = models.TextField()
    is_default        = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            JobEmailTemplate.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class OfferLetterTemplate(models.Model):
    """Pre-built offer letter templates HR can select when drafting an offer."""
    name = models.CharField(max_length=200, verbose_name=_("Template Name"))
    body_html = models.TextField(
        verbose_name=_("Body HTML"),
        help_text="Use {{candidate_name}}, {{position}}, {{department}}, {{joining_date}}, {{basic_salary}}, {{company_name}} as placeholders",
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Offer Letter Template")
        verbose_name_plural = _("Offer Letter Templates")

    def __str__(self):
        return self.name


class OfferLetterApproval(models.Model):
    """Multi-step approval chain for offer letters before they are sent to the candidate."""

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    offer_letter = models.ForeignKey(
        OfferLetter,
        on_delete=models.CASCADE,
        related_name="approvals",
        verbose_name=_("Offer Letter"),
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="offer_letter_approvals",
        verbose_name=_("Approver"),
    )
    sequence = models.PositiveIntegerField(verbose_name=_("Sequence"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name=_("Status"))
    feedback = models.TextField(blank=True, verbose_name=_("Feedback / Rejection Reason"))
    signature_image = models.TextField(blank=True, verbose_name=_("Signature (base64)"))
    acted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Acted At"))
    esign_provider = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("E-Sign Provider"))
    esign_reference = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("E-Sign Reference"))

    class Meta:
        ordering = ["sequence"]
        verbose_name = _("Offer Letter Approval")
        verbose_name_plural = _("Offer Letter Approvals")

    def __str__(self):
        return f"{self.offer_letter} — step {self.sequence} ({self.get_status_display()})"


class MedicalLetterTemplate(models.Model):
    """Pre-built templates for medical clearance letters."""
    name = models.CharField(max_length=200, verbose_name=_("Template Name"))
    body_html = models.TextField(
        verbose_name=_("Body HTML"),
        help_text="Use {{candidate_name}}, {{position}}, {{company_name}} as placeholders",
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Medical Letter Template")
        verbose_name_plural = _("Medical Letter Templates")

    def __str__(self):
        return self.name


class VisaLetterTemplate(models.Model):
    """Pre-built templates for visa support letters."""
    name = models.CharField(max_length=200, verbose_name=_("Template Name"))
    body_html = models.TextField(
        verbose_name=_("Body HTML"),
        help_text="Use {{candidate_name}}, {{position}}, {{company_name}} as placeholders",
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Visa Letter Template")
        verbose_name_plural = _("Visa Letter Templates")

    def __str__(self):
        return self.name


def _medical_letter_no():
    return f"ML-{uuid4().hex[:8].upper()}"


def _visa_letter_no():
    return f"VL-{uuid4().hex[:8].upper()}"


class MedicalLetter(models.Model):
    """Medical clearance letter for a candidate — requires HR e-sign only."""

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("signed", _("Signed")),
        ("sent", _("Sent")),
    ]

    doc_no = models.CharField(
        max_length=20, default=_medical_letter_no, unique=True, verbose_name=_("Document No")
    )
    candidate_id = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE,
        related_name="medical_letter",
        verbose_name=_("Candidate"),
    )
    content = models.TextField(blank=True, verbose_name=_("Letter Content"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    hr_signed = models.BooleanField(default=False)
    hr_signature = models.TextField(blank=True, verbose_name=_("HR Signature (base64)"))
    hr_signed_by = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="medical_letters_signed", verbose_name=_("Signed By"),
    )
    hr_signed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="medical_letters_created", verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Medical Letter")
        verbose_name_plural = _("Medical Letters")

    def __str__(self):
        return f"Medical Letter — {self.candidate_id}"


class VisaLetter(models.Model):
    """Visa support letter for a candidate — requires HR e-sign only."""

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("signed", _("Signed")),
        ("sent", _("Sent")),
    ]

    doc_no = models.CharField(
        max_length=20, default=_visa_letter_no, unique=True, verbose_name=_("Document No")
    )
    candidate_id = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE,
        related_name="visa_letter",
        verbose_name=_("Candidate"),
    )
    content = models.TextField(blank=True, verbose_name=_("Letter Content"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    hr_signed = models.BooleanField(default=False)
    hr_signature = models.TextField(blank=True, verbose_name=_("HR Signature (base64)"))
    hr_signed_by = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="visa_letters_signed", verbose_name=_("Signed By"),
    )
    hr_signed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="visa_letters_created", verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Visa Letter")
        verbose_name_plural = _("Visa Letters")

    def __str__(self):
        return f"Visa Letter — {self.candidate_id}"


class OfferLetterStatusLog(models.Model):
    """Full audit trail — every state change on an offer letter."""

    offer_letter = models.ForeignKey(
        OfferLetter, on_delete=models.CASCADE, related_name="status_logs",
        verbose_name=_("Offer Letter"),
    )
    from_status = models.CharField(max_length=30, blank=True, verbose_name=_("From"))
    to_status = models.CharField(max_length=30, verbose_name=_("To"))
    actor = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="offer_status_logs", verbose_name=_("Actor"),
    )
    note = models.TextField(blank=True, verbose_name=_("Note"))
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = _("Offer Letter Status Log")
        verbose_name_plural = _("Offer Letter Status Logs")

    def __str__(self):
        return f"{self.offer_letter.offer_no}: {self.from_status} → {self.to_status}"


class MedicalLetterStatusLog(models.Model):
    """Full audit trail — every state change on a medical letter."""

    medical_letter = models.ForeignKey(
        MedicalLetter, on_delete=models.CASCADE, related_name="status_logs",
        verbose_name=_("Medical Letter"),
    )
    from_status = models.CharField(max_length=30, blank=True, verbose_name=_("From"))
    to_status = models.CharField(max_length=30, verbose_name=_("To"))
    actor = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="medical_status_logs", verbose_name=_("Actor"),
    )
    note = models.TextField(blank=True, verbose_name=_("Note"))
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = _("Medical Letter Status Log")
        verbose_name_plural = _("Medical Letter Status Logs")

    def __str__(self):
        return f"{self.medical_letter.doc_no}: {self.from_status} → {self.to_status}"


class VisaLetterStatusLog(models.Model):
    """Full audit trail — every state change on a visa letter."""

    visa_letter = models.ForeignKey(
        VisaLetter, on_delete=models.CASCADE, related_name="status_logs",
        verbose_name=_("Visa Letter"),
    )
    from_status = models.CharField(max_length=30, blank=True, verbose_name=_("From"))
    to_status = models.CharField(max_length=30, verbose_name=_("To"))
    actor = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="visa_status_logs", verbose_name=_("Actor"),
    )
    note = models.TextField(blank=True, verbose_name=_("Note"))
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = _("Visa Letter Status Log")
        verbose_name_plural = _("Visa Letter Status Logs")

    def __str__(self):
        return f"{self.visa_letter.doc_no}: {self.from_status} → {self.to_status}"


# Register supplementary model modules so Django discovers them
from recruitment.models_manpower import ManpowerRequest, ManpowerRequestStatusLog  # noqa: F401,E402
from recruitment.models_approvals import (  # noqa: F401,E402
    ApprovalRule,
    ApprovalStep,
    ManpowerApproval,
    RecruitmentApprovalDelegation,
)

from recruitment.models_interview import (  # noqa: F401,E402
    EvaluationCriteria,
    InterviewEvaluation,
    EvaluationScore,
    InterviewRound,
)

from recruitment.models_proposal import (  # noqa: F401,E402
    EmploymentProposal,
    ProposalApproval,
    ProposalRoleAssignment,
    ProposalStatusLog,
)


def _portal_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"recruitment/portal_uploads/{instance.offer_id}/{uuid4().hex}.{ext}"


class CandidatePortalUpload(models.Model):
    DOCUMENT_TYPES = [
        ("medical", _("Medical Certificate")),
        ("marksheet", _("Academic Marksheet / Degree")),
        ("experience", _("Experience Certificate")),
        ("passport", _("Passport Copy")),
        ("id_card", _("National ID / Civil ID")),
        ("other", _("Other Document")),
    ]

    offer = models.ForeignKey(
        OfferLetter,
        on_delete=models.CASCADE,
        related_name="portal_uploads",
        verbose_name=_("Offer Letter"),
    )
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, verbose_name=_("Document Type")
    )
    label = models.CharField(
        max_length=100, blank=True, verbose_name=_("Label"),
        help_text=_("Optional custom label, e.g. 'MSc Degree 2022'"),
    )
    file = models.FileField(upload_to=_portal_upload_path, verbose_name=_("File"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]
        verbose_name = _("Candidate Portal Upload")
        verbose_name_plural = _("Candidate Portal Uploads")

    def __str__(self):
        return f"{self.get_document_type_display()} — {self.offer.candidate_id.name}"

    @property
    def filename(self):
        return self.file.name.rsplit("/", 1)[-1] if self.file else ""


class OnboardingDocument(models.Model):
    """A document the candidate must e-sign in the portal after the offer letter
    is fully approved internally. Batch 1 = the offer letter; batch 2 = the
    standard onboarding documents (T&C, Code of Conduct, NDA, Data Privacy)
    which are released only after HR approves the signed offer letter."""

    STATUS_AWAITING = "awaiting_signature"
    STATUS_SIGNED = "signed"
    STATUS_APPROVED = "approved"
    STATUS_CHOICES = [
        (STATUS_AWAITING, _("Awaiting Signature")),
        (STATUS_SIGNED, _("Signed — Awaiting HR Approval")),
        (STATUS_APPROVED, _("Approved")),
    ]

    offer = models.ForeignKey(
        OfferLetter,
        on_delete=models.CASCADE,
        related_name="sign_documents",
        verbose_name=_("Offer Letter"),
    )
    doc_key = models.CharField(max_length=40, verbose_name=_("Document Key"))
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    body_html = models.TextField(blank=True, verbose_name=_("Body"))
    batch = models.PositiveIntegerField(default=1, verbose_name=_("Batch"))
    sequence = models.PositiveIntegerField(default=1, verbose_name=_("Sequence"))
    released = models.BooleanField(default=False, verbose_name=_("Released to Candidate"))
    candidate_signature = models.TextField(blank=True, verbose_name=_("Candidate Signature"))
    candidate_signed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_AWAITING,
        verbose_name=_("Status"),
    )
    hr_note = models.TextField(blank=True, verbose_name=_("HR Note"))
    hr_acted_by = models.ForeignKey(
        "employee.Employee", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    hr_acted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["batch", "sequence"]
        verbose_name = _("Onboarding Document")
        verbose_name_plural = _("Onboarding Documents")

    def __str__(self):
        return f"{self.title} — {self.offer.candidate_id.name}"
