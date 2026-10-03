"""
WPS (Wage Protection System) File Generation
Central Bank of Oman compliance for salary disbursement
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from base.models import Company
from employee.models import Employee
from fits.models import FitsModel


class WPSGlobalSettings(models.Model):
    """
    Global WPS Settings for Central Bank of Oman Compliance
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="wps_settings",
        verbose_name=_("Company"),
    )

    # Company Bank Details
    company_bank_name = models.CharField(
        max_length=100,
        verbose_name=_("Company Bank Name"),
    )
    company_bank_code = models.CharField(
        max_length=10,
        verbose_name=_("Bank Code (SWIFT)"),
        help_text=_("4-letter SWIFT code, e.g., NBOMOM"),
    )
    company_bank_account_number = models.CharField(
        max_length=20,
        verbose_name=_("Company Bank Account Number"),
    )
    company_bank_account_iban = models.CharField(
        max_length=34,
        blank=True,
        verbose_name=_("Company Bank Account IBAN"),
        help_text=_("Optional IBAN format"),
    )
    company_cr_number = models.CharField(
        max_length=20,
        verbose_name=_("Company CR (Commercial Registration) Number"),
    )
    company_wps_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("WPS Registration Code"),
        help_text=_("Assigned by Central Bank of Oman"),
    )

    # WPS Configuration
    enable_wps_processing = models.BooleanField(
        default=True,
        verbose_name=_("Enable WPS Processing"),
    )
    wps_submission_frequency = models.CharField(
        max_length=20,
        choices=[
            ("daily", _("Daily")),
            ("weekly", _("Weekly")),
            ("monthly", _("Monthly")),
        ],
        default="monthly",
        verbose_name=_("WPS Submission Frequency"),
    )

    # File Format Version
    WPS_VERSION_CHOICES = [
        ("v1.0", _("WPS Format 1.0 (Legacy)")),
        ("v2.0", _("WPS Format 2.0 (Current)")),
        ("v3.0", _("WPS Format 3.0 (with IBAN)")),
    ]

    wps_format_version = models.CharField(
        max_length=10,
        choices=WPS_VERSION_CHOICES,
        default="v2.0",
        verbose_name=_("WPS File Format Version"),
    )

    # Processing Settings
    auto_generate_wps_file = models.BooleanField(
        default=True,
        verbose_name=_("Auto-Generate WPS File After Payroll"),
    )
    include_end_of_service = models.BooleanField(
        default=True,
        verbose_name=_("Include End-of-Service Settlements"),
    )
    include_loans = models.BooleanField(
        default=True,
        verbose_name=_("Include Loan Deductions"),
    )

    # Compliance
    requires_director_approval = models.BooleanField(
        default=True,
        verbose_name=_("Requires Director Approval"),
    )
    digital_signature_required = models.BooleanField(
        default=False,
        verbose_name=_("Digital Signature Required"),
        help_text=_("For enhanced security"),
    )

    # Audit
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated"),
    )

    class Meta:
        verbose_name = _("WPS Global Settings")
        verbose_name_plural = _("WPS Global Settings")

    def __str__(self):
        return f"WPS Settings - {self.company.name}"


class WPSPeriodicFile(FitsModel):
    """
    WPS File for a specific payroll period
    Generated from payslips and sent to bank for salary disbursement
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("generated", _("Generated - Ready for Review")),
        ("approved", _("Approved")),
        ("submitted", _("Submitted to Bank")),
        ("rejected", _("Rejected by Bank")),
        ("processed", _("Processed by Bank")),
        ("failed", _("Failed")),
    ]

    # Basic Info
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
        related_name="wps_files",
    )
    payroll_period = models.CharField(
        max_length=20,
        verbose_name=_("Payroll Period"),
        help_text=_("e.g., '2024-01' for January 2024"),
    )
    payment_date = models.DateField(
        verbose_name=_("Salary Payment Date"),
    )

    # File Details
    file_reference_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("File Reference Number"),
        help_text=_("Unique identifier from system"),
    )
    file_generation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("File Generation Date"),
    )
    file_version = models.CharField(
        max_length=10,
        verbose_name=_("WPS Format Version"),
    )

    # Content Summary
    total_records = models.IntegerField(
        default=0,
        verbose_name=_("Total Employee Records"),
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_("Total Salary Amount (OMR)"),
    )
    currency = models.CharField(
        max_length=3,
        default="OMR",
        verbose_name=_("Currency Code"),
    )

    # File Content Fields (as JSON for flexibility)
    employee_records = models.JSONField(
        default=list,
        verbose_name=_("Employee Records"),
        help_text=_("Serialized list of employee payment records"),
    )

    # File Management
    file_path = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("File Path"),
    )
    file_size_bytes = models.IntegerField(
        default=0,
        verbose_name=_("File Size (bytes)"),
    )
    file_format = models.CharField(
        max_length=20,
        choices=[
            ("txt", _("Text File (.txt)")),
            ("csv", _("CSV File (.csv)")),
            ("xml", _("XML File (.xml)")),
        ],
        default="txt",
        verbose_name=_("File Format"),
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )

    # Approvals
    generated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_wps_files",
        verbose_name=_("Generated By"),
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_wps_files",
        verbose_name=_("Approved By (Director/CFO)"),
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

    # Bank Submission
    submitted_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Submission Date to Bank"),
    )
    bank_response_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Bank Response Code"),
    )
    bank_response_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Bank Response Message"),
    )
    bank_reference_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Bank Reference Number"),
    )

    # Processing Status
    processing_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Processing Status"),
        help_text=_("e.g., 'Sent', 'Processing', 'Completed', 'Rejected'"),
    )
    processing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Processing Date"),
    )

    # Rejection Handling
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Rejection Reason"),
        help_text=_("Reason provided by bank if rejected"),
    )
    is_resubmitted = models.BooleanField(
        default=False,
        verbose_name=_("Is Resubmitted"),
    )
    resubmission_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resubmission Date"),
    )

    # Audit Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Internal Notes"),
    )

    class Meta:
        verbose_name = _("WPS Periodic File")
        verbose_name_plural = _("WPS Periodic Files")
        ordering = ["-payment_date"]
        unique_together = [["company", "payroll_period"]]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["payment_date"]),
        ]

    def __str__(self):
        return f"WPS File - {self.company.name} ({self.payroll_period})"


class WPSAuditLog(models.Model):
    """
    Audit Log for WPS File Processing
    """

    wps_file = models.ForeignKey(
        WPSPeriodicFile,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        verbose_name=_("WPS File"),
    )

    ACTION_CHOICES = [
        ("created", _("File Created")),
        ("generated", _("File Generated")),
        ("approved", _("File Approved")),
        ("submitted", _("File Submitted")),
        ("bank_response", _("Bank Response Received")),
        ("rejected", _("Rejected by Bank")),
        ("resubmitted", _("Resubmitted")),
        ("processed", _("Processed")),
        ("cancelled", _("Cancelled")),
    ]

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        verbose_name=_("Action"),
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Timestamp"),
    )
    user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
    )
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Details"),
    )

    class Meta:
        verbose_name = _("WPS Audit Log")
        verbose_name_plural = _("WPS Audit Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.wps_file.file_reference_number} - {self.get_action_display()}"


class WPSPaymentException(models.Model):
    """
    Exceptions and Errors in WPS Processing
    """

    EXCEPTION_TYPE_CHOICES = [
        ("invalid_account", _("Invalid Bank Account")),
        ("invalid_iban", _("Invalid IBAN")),
        ("insufficient_funds", _("Insufficient Funds")),
        ("duplicate_record", _("Duplicate Record")),
        ("data_validation_error", _("Data Validation Error")),
        ("bank_error", _("Bank System Error")),
        ("other", _("Other")),
    ]

    wps_file = models.ForeignKey(
        WPSPeriodicFile,
        on_delete=models.CASCADE,
        related_name="exceptions",
        verbose_name=_("WPS File"),
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
    )
    exception_type = models.CharField(
        max_length=30,
        choices=EXCEPTION_TYPE_CHOICES,
        verbose_name=_("Exception Type"),
    )
    error_description = models.TextField(
        verbose_name=_("Error Description"),
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name=_("Is Resolved"),
    )
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Resolution Notes"),
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created Date"),
    )
    resolved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resolved Date"),
    )

    class Meta:
        verbose_name = _("WPS Payment Exception")
        verbose_name_plural = _("WPS Payment Exceptions")
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.employee.get_name()} - {self.get_exception_type_display()}"
