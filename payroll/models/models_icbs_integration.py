"""
payroll/models/models_icbs_integration.py

ICBS (Islamic Central Bank System) Integration for Payroll Disbursement
Handles salary transfers to employee bank accounts
Compliant with Islamic banking principles
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from base.models import Company, Employee


class ICBSBankConfiguration(models.Model):
    """
    Configuration for ICBS banking integration
    Stores bank details and API credentials
    """

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="icbs_config"
    )

    # Bank details
    bank_code = models.CharField(max_length=10, help_text=_("ICBS bank code"))
    bank_name = models.CharField(max_length=255)
    company_bank_account = models.CharField(
        max_length=34, help_text=_("Company's bank account IBAN")
    )

    # API Configuration
    api_endpoint = models.URLField()
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)

    # Connection settings
    timeout_seconds = models.IntegerField(default=30)
    retry_attempts = models.IntegerField(default=3)

    # Features
    supports_scheduled_payments = models.BooleanField(default=True)
    supports_bulk_transfers = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)

    # Limits
    daily_limit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("1000000.00")
    )
    monthly_limit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("10000000.00")
    )

    # Islamic compliance
    applies_islamic_principles = models.BooleanField(default=True)
    profit_sharing_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Profit sharing rate for Islamic products"),
    )

    # Metadata
    updated_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll_icbs_bank_configuration"
        verbose_name = _("ICBS Bank Configuration")

    def __str__(self):
        return f"ICBS Config - {self.bank_name}"


class EmployeeBankAccount(models.Model):
    """
    Employee bank account details for salary transfer
    """

    ACCOUNT_TYPE_CHOICES = [
        ("current", _("Current Account")),
        ("savings", _("Savings Account")),
        ("islamic", _("Islamic Account")),
    ]

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="bank_account"
    )

    bank_code = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=50, choices=ACCOUNT_TYPE_CHOICES, default="savings"
    )

    account_holder_name = models.CharField(max_length=255)
    iban = models.CharField(
        max_length=34, unique=True, help_text=_("International Bank Account Number")
    )

    # Account verification
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_bank_accounts",
    )

    # Validity
    is_active = models.BooleanField(default=True)
    bank_verification_reference = models.CharField(
        max_length=100, blank=True, help_text=_("Reference from ICBS verification")
    )

    # Metadata
    added_date = models.DateField(auto_now_add=True)
    last_used_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "payroll_employee_bank_account"
        verbose_name = _("Employee Bank Account")

    def __str__(self):
        return f"{self.employee} - {self.iban}"


class SalaryTransferBatch(models.Model):
    """
    Batch of salary transfers to be processed via ICBS
    """

    BATCH_STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("approved", _("Approved")),
        ("processing", _("Processing")),
        ("submitted", _("Submitted to Bank")),
        ("processed", _("Processed")),
        ("partial_success", _("Partially Successful")),
        ("failed", _("Failed")),
        ("rejected", _("Rejected")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="salary_transfer_batches"
    )

    # Batch details
    batch_name = models.CharField(max_length=255)
    payroll_period = models.CharField(max_length=50)
    batch_date = models.DateField()
    scheduled_payment_date = models.DateField()

    # Status
    status = models.CharField(
        max_length=20, choices=BATCH_STATUS_CHOICES, default="draft"
    )

    # Amount tracking
    total_employees = models.IntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    successful_transfers = models.IntegerField(default=0)
    failed_transfers = models.IntegerField(default=0)

    # Bank details
    bank_reference_number = models.CharField(max_length=50, blank=True)
    icbs_batch_id = models.CharField(max_length=100, blank=True)

    # File
    batch_file = models.FileField(upload_to="icbs_batches/", null=True, blank=True)
    batch_json = models.JSONField(default=dict, blank=True)

    # Approvals
    requested_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_transfer_batches",
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_transfer_batches",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Processing
    submitted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_transfer_batches",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)

    processed_at = models.DateTimeField(null=True, blank=True)

    # Audit
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "payroll_salary_transfer_batch"
        verbose_name = _("Salary Transfer Batch")
        verbose_name_plural = _("Salary Transfer Batches")
        ordering = ["-batch_date"]

    def __str__(self):
        return f"{self.batch_name} - {self.batch_date}"

    def approve_batch(self, approved_by):
        """Approve batch for processing"""
        if self.status == "draft":
            self.status = "approved"
            self.approved_by = approved_by
            self.approved_at = timezone.now()
            self.save()
            return True
        return False

    def submit_to_bank(self, submitted_by):
        """Submit batch to ICBS"""
        if self.status == "approved":
            self.status = "submitted"
            self.submitted_by = submitted_by
            self.submitted_at = timezone.now()
            self.save()
            return True
        return False


class SalaryTransfer(models.Model):
    """
    Individual salary transfer records
    """

    TRANSFER_STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("processing", _("Processing")),
        ("successful", _("Successful")),
        ("failed", _("Failed")),
        ("rejected", _("Rejected")),
        ("reversed", _("Reversed")),
    ]

    batch = models.ForeignKey(
        SalaryTransferBatch, on_delete=models.CASCADE, related_name="transfers"
    )

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="salary_transfers"
    )

    bank_account = models.ForeignKey(
        EmployeeBankAccount, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Amount
    salary_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transfer_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Amount after any deductions/adjustments"),
    )

    # Reference
    sequence_number = models.IntegerField()  # Position in batch
    icbs_reference = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(
        max_length=20, choices=TRANSFER_STATUS_CHOICES, default="pending"
    )

    response_code = models.CharField(max_length=10, blank=True)
    response_message = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payroll_salary_transfer"
        verbose_name = _("Salary Transfer")
        verbose_name_plural = _("Salary Transfers")
        ordering = ["batch", "sequence_number"]

    def __str__(self):
        return f"{self.employee} - {self.transfer_amount}"

    def mark_successful(self, reference_id):
        """Mark transfer as successful"""
        self.status = "successful"
        self.icbs_reference = reference_id
        self.processed_at = timezone.now()
        self.save()

    def mark_failed(self, error_code, error_message):
        """Mark transfer as failed"""
        self.status = "failed"
        self.response_code = error_code
        self.response_message = error_message
        self.processed_at = timezone.now()
        self.save()


class ICBSTransactionLog(models.Model):
    """
    Log all ICBS API interactions for audit trail
    """

    TRANSACTION_TYPE_CHOICES = [
        ("verify_account", _("Verify Account")),
        ("submit_batch", _("Submit Batch")),
        ("check_status", _("Check Status")),
        ("reverse_transfer", _("Reverse Transfer")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="icbs_transaction_logs"
    )

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)

    # API details
    api_endpoint = models.CharField(max_length=255)
    request_payload = models.JSONField()
    response_payload = models.JSONField(blank=True)
    response_status_code = models.IntegerField()

    # Reference
    batch = models.ForeignKey(
        SalaryTransferBatch, on_delete=models.SET_NULL, null=True, blank=True
    )
    icbs_reference_id = models.CharField(max_length=100, blank=True)

    # User
    initiated_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "payroll_icbs_transaction_log"
        verbose_name = _("ICBS Transaction Log")
        ordering = ["-transaction_date"]

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_date}"
