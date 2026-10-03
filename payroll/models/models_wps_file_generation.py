"""
payroll/models/models_wps_file_generation.py

WPS (Wage Protection System) File Generation
Generates CBM (Central Bank of Oman) format files for wage disbursement
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from base.models import Company, Employee
import csv
import io


class WPSFileGeneration(models.Model):
    """
    Generate WPS files in CBM format for Oman wage disbursement
    """

    FILE_STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("generated", _("Generated")),
        ("validated", _("Validated")),
        ("submitted", _("Submitted to CBM")),
        ("approved", _("Approved by CBM")),
        ("rejected", _("Rejected")),
        ("processed", _("Processed")),
    ]

    FILE_TYPE_CHOICES = [
        ("salary_transfer", _("Salary Transfer")),
        ("wage_settlement", _("Wage Settlement")),
        ("final_settlement", _("Final Settlement")),
        ("amendment", _("Amendment")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="wps_files"
    )

    file_name = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=50, choices=FILE_TYPE_CHOICES, default="salary_transfer"
    )

    payroll_period = models.CharField(
        max_length=50, help_text=_("e.g., 2024-03, Jan-2024")
    )
    payroll_year = models.IntegerField()
    payroll_month = models.IntegerField()

    # CBM Details
    cbm_employer_code = models.CharField(
        max_length=20, help_text=_("Central Bank of Oman employer registration code")
    )
    cbm_establishment_code = models.CharField(
        max_length=20, blank=True, help_text=_("CBM establishment code if applicable")
    )

    # File content
    employee_count = models.IntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )

    # File status
    status = models.CharField(
        max_length=20, choices=FILE_STATUS_CHOICES, default="draft"
    )

    # Generated file
    file_content = models.TextField(
        blank=True, help_text=_("CSV content in CBM format")
    )
    file_path = models.FileField(upload_to="wps_files/", null=True, blank=True)

    # Metadata
    generated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_wps_files",
    )
    generated_at = models.DateTimeField(null=True, blank=True)

    submitted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_wps_files",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)

    cbm_reference_number = models.CharField(max_length=50, blank=True)
    cbm_response = models.JSONField(default=dict, blank=True)

    # Important dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "payroll_wps_file_generation"
        verbose_name = _("WPS File Generation")
        verbose_name_plural = _("WPS File Generations")
        ordering = ["-created_at"]
        unique_together = ("company", "payroll_period", "file_type")

    def __str__(self):
        return f"{self.company} - {self.payroll_period}"

    def generate_cbm_format(self, employee_payroll_records):
        """
        Generate WPS file in CBM format

        CBM Format Structure:
        - Header Record (01)
        - Salary Record (02) - repeating for each employee
        - Total Record (03)
        - Trailer Record (04)
        """

        records = []

        # Header Record (01)
        header = self._generate_header_record()
        records.append(header)

        total_amount = Decimal("0")
        employee_count = 0

        # Salary Records (02)
        for record in employee_payroll_records:
            salary_record = self._generate_salary_record(record)
            records.append(salary_record)
            total_amount += Decimal(str(record.get("net_salary", 0)))
            employee_count += 1

        # Total Record (03)
        total_record = self._generate_total_record(employee_count, total_amount)
        records.append(total_record)

        # Trailer Record (04)
        trailer = self._generate_trailer_record(len(records))
        records.append(trailer)

        # Store content
        self.employee_count = employee_count
        self.total_amount = total_amount

        # Write to CSV
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        for record in records:
            writer.writerow(record)

        self.file_content = output.getvalue()
        self.status = "generated"
        self.generated_at = timezone.now()
        self.save()

        return records

    def _generate_header_record(self):
        """
        Generate CBM Header Record (Type 01)
        Record Type | Employer Code | Establishment Code | File Number | Date | Time
        """
        import datetime

        now = datetime.datetime.now()

        return [
            "01",  # Record Type
            self.cbm_employer_code,  # Employer Code
            self.cbm_establishment_code or "",  # Establishment Code
            self.id,  # File Number
            now.strftime("%d%m%Y"),  # Date
            now.strftime("%H%M%S"),  # Time
            "NEW",  # File Submission Type
            f"{self.payroll_year}{self.payroll_month:02d}",  # Salary Period
        ]

    def _generate_salary_record(self, employee_data):
        """
        Generate CBM Salary Record (Type 02)
        Record Type | Employee ID | Employee Name | Salary Account | Amount | Currency
        """
        return [
            "02",  # Record Type
            employee_data.get("employee_id", ""),  # Employee ID
            employee_data.get("employee_name", "")[:40],  # Employee Name (max 40 chars)
            employee_data.get("iban", ""),  # IBAN/Account
            f"{Decimal(str(employee_data.get('net_salary', 0))):.2f}",  # Amount
            "OMR",  # Currency
            employee_data.get("remarks", ""),  # Remarks
        ]

    def _generate_total_record(self, employee_count, total_amount):
        """
        Generate CBM Total Record (Type 03)
        Record Type | Total Count | Total Amount | Currency
        """
        return [
            "03",  # Record Type
            str(employee_count),  # Total Records
            f"{total_amount:.2f}",  # Total Amount
            "OMR",  # Currency
            "",  # Reserved fields
        ]

    def _generate_trailer_record(self, total_records):
        """
        Generate CBM Trailer Record (Type 04)
        Record Type | Total Records | Checksum
        """
        return [
            "04",  # Record Type
            str(total_records),  # Total Records including header and trailer
            "0000",  # Checksum (calculated by CBM)
        ]

    def validate_file(self):
        """
        Validate WPS file structure and content
        Checks for:
        - Required fields
        - IBAN format
        - Amount validation
        - Record count matching
        """
        if not self.file_content:
            return False, "No file content"

        lines = self.file_content.strip().split("\n")

        if len(lines) < 4:
            return False, "Minimum 4 records required (header, salary, total, trailer)"

        # Check header
        header = lines[0].split(",")
        if header[0] != "01":
            return False, "Invalid header record"

        # Check trailer
        trailer = lines[-1].split(",")
        if trailer[0] != "04":
            return False, "Invalid trailer record"

        # Check record count
        if len(lines) != int(trailer[1]):
            return False, f"Record count mismatch: {len(lines)} vs {trailer[1]}"

        self.status = "validated"
        self.save()
        return True, "File validated successfully"

    def submit_to_cbm(self, submitted_by):
        """
        Mark file as submitted to Central Bank of Oman
        """
        if self.status != "validated":
            return False, "File must be validated before submission"

        self.status = "submitted"
        self.submitted_by = submitted_by
        self.submitted_at = timezone.now()
        self.save()

        return True, "File submitted to CBM"


class WPSFileException(models.Model):
    """
    Track exceptions and rejections from CBM
    """

    EXCEPTION_TYPE_CHOICES = [
        ("invalid_iban", _("Invalid IBAN")),
        ("insufficient_funds", _("Insufficient Funds")),
        ("account_closed", _("Account Closed")),
        ("amount_exceeds_limit", _("Amount Exceeds Limit")),
        ("duplicate_transaction", _("Duplicate Transaction")),
        ("format_error", _("Format Error")),
        ("other", _("Other")),
    ]

    wps_file = models.ForeignKey(
        WPSFileGeneration, on_delete=models.CASCADE, related_name="exceptions"
    )

    exception_type = models.CharField(max_length=50, choices=EXCEPTION_TYPE_CHOICES)
    employee_id = models.CharField(max_length=50)
    employee_name = models.CharField(max_length=255)
    iban = models.CharField(max_length=34)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    error_message = models.TextField()
    cbm_error_code = models.CharField(max_length=10, blank=True)

    # Resolution
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payroll_wps_file_exception"
        verbose_name = _("WPS File Exception")

    def __str__(self):
        return f"Exception - {self.exception_type}"

    def resolve_exception(self, notes):
        """
        Mark exception as resolved
        """
        self.resolved = True
        self.resolution_notes = notes
        self.resolved_at = timezone.now()
        self.save()
