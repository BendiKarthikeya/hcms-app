"""
payroll/models/models_gratuity.py

Gratuity and End-of-Service Benefits (EOSB) Calculation
Implements Royal Decree 35/2003 of Oman
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from base.models import Company, Employee


class GratuityConfig(models.Model):
    """
    Configuration for gratuity calculations per Omani law
    Royal Decree 35/2003
    """

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="gratuity_config"
    )

    # Basic rates
    wage_type = models.CharField(
        max_length=50,
        choices=[
            ("monthly", _("Monthly Salary")),
            ("daily", _("Daily Wage")),
            ("hourly", _("Hourly Wage")),
        ],
        default="monthly",
    )

    # Service period rates (per year of service)
    first_3_years_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.50"),
        help_text=_("Gratuity rate for first 3 years (0.50 = 50% of monthly salary)"),
    )

    next_2_years_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.75"),
        help_text=_("Gratuity rate for years 4-5 (0.75 = 75% of monthly salary)"),
    )

    above_5_years_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text=_("Gratuity rate for years 6+ (1.00 = 100% of monthly salary)"),
    )

    # Limits per Royal Decree
    max_gratuity_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("50000"),
        help_text=_("Maximum gratuity amount (OMR 50,000 per decree)"),
    )

    min_service_months = models.IntegerField(
        default=12, help_text=_("Minimum service period for gratuity eligibility")
    )

    # Tax configuration
    applies_tax = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.20"),
        help_text=_("Tax rate on gratuity (20% in Oman)"),
    )

    updated_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll_gratuity_config"
        verbose_name = _("Gratuity Configuration")

    def __str__(self):
        return f"Gratuity Config - {self.company}"


class EmployeeGratuity(models.Model):
    """
    Calculate and store employee gratuity at separation
    """

    SEPARATION_REASON_CHOICES = [
        ("resignation", _("Employee Resignation")),
        ("termination", _("Employer Termination")),
        ("retirement", _("Retirement")),
        ("death", _("Death of Employee")),
        ("contract_end", _("Contract End")),
        ("health", _("Health Reasons")),
    ]

    GRATUITY_STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("calculated", _("Calculated")),
        ("approved", _("Approved")),
        ("paid", _("Paid")),
        ("disputed", _("Disputed")),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="gratuity_records"
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # Employment period
    employment_start_date = models.DateField()
    separation_date = models.DateField()
    total_days_worked = models.IntegerField(compute=True)
    total_months_worked = models.IntegerField(compute=True)
    total_years_worked = models.DecimalField(
        max_digits=5, decimal_places=2, compute=True
    )

    # Separation details
    separation_reason = models.CharField(
        max_length=50, choices=SEPARATION_REASON_CHOICES, default="resignation"
    )
    separation_notes = models.TextField(blank=True)

    # Salary information
    final_monthly_salary = models.DecimalField(max_digits=15, decimal_places=2)
    final_daily_wage = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        compute=True,
        help_text=_("Calculated as final_monthly_salary / 30"),
    )

    # Gratuity calculation
    applicable_years = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        compute=True,
        help_text=_("Years applicable for gratuity calculation"),
    )
    gratuity_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        compute=True,
        help_text=_("Applicable rate per Omani law"),
    )
    calculated_gratuity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        compute=True,
        help_text=_("Gratuity before tax"),
    )

    # Deductions and net amount
    outstanding_loans = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    other_deductions = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, compute=True)
    net_gratuity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        compute=True,
        help_text=_("Net amount after all deductions"),
    )

    # Status
    status = models.CharField(
        max_length=20, choices=GRATUITY_STATUS_CHOICES, default="draft"
    )

    # Approvals
    calculated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculated_gratuities",
    )
    calculated_at = models.DateTimeField(null=True, blank=True)

    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_gratuities",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    paid_date = models.DateField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll_employee_gratuity"
        verbose_name = _("Employee Gratuity")
        verbose_name_plural = _("Employee Gratuities")
        ordering = ["-separation_date"]

    def __str__(self):
        return f"{self.employee} - Gratuity"

    def calculate_gratuity(self):
        """
        Calculate gratuity based on Omani law (Royal Decree 35/2003)
        """
        config = GratuityConfig.objects.filter(company=self.company).first()
        if not config:
            return

        # Calculate service period
        self.total_days_worked = (
            self.separation_date - self.employment_start_date
        ).days
        self.total_months_worked = self.total_days_worked // 30
        self.total_years_worked = Decimal(self.total_months_worked) / Decimal("12")

        # Check minimum service requirement
        if self.total_months_worked < config.min_service_months:
            self.calculated_gratuity = Decimal("0")
            self.net_gratuity = Decimal("0")
            self.status = "calculated"
            self.save()
            return

        # Determine applicable rate
        years = float(self.total_years_worked)

        if years <= 3:
            self.gratuity_rate = config.first_3_years_rate
            self.applicable_years = self.total_years_worked
        elif years <= 5:
            self.gratuity_rate = config.next_2_years_rate
            # First 3 years at first rate, rest at next rate
            self.applicable_years = self.total_years_worked
        else:
            self.gratuity_rate = config.above_5_years_rate
            self.applicable_years = self.total_years_worked

        # Calculate final daily wage
        self.final_daily_wage = self.final_monthly_salary / Decimal("30")

        # Calculate gratuity: days worked * daily wage * applicable rate
        self.calculated_gratuity = min(
            self.final_daily_wage
            * Decimal(self.total_days_worked)
            * self.gratuity_rate,
            config.max_gratuity_amount,
        )

        # Calculate tax (20% for government employees in Oman)
        if config.applies_tax:
            self.tax_amount = self.calculated_gratuity * config.tax_rate
        else:
            self.tax_amount = Decimal("0")

        # Calculate net gratuity
        self.net_gratuity = (
            self.calculated_gratuity
            - self.tax_amount
            - self.outstanding_loans
            - self.other_deductions
        )

        self.status = "calculated"
        self.calculated_by = None  # Will be set by user
        self.calculated_at = timezone.now()
        self.save()

    def approve_gratuity(self, approved_by):
        """
        Approve gratuity calculation
        """
        if self.status == "calculated":
            self.status = "approved"
            self.approved_by = approved_by
            self.approved_at = timezone.now()
            self.save()

    def mark_as_paid(self):
        """
        Mark gratuity as paid
        """
        if self.status == "approved":
            self.status = "paid"
            self.paid_date = timezone.now().date()
            self.save()


class GratuityCertificate(models.Model):
    """
    Generate and store gratuity settlement certificates
    """

    gratuity = models.OneToOneField(
        EmployeeGratuity, on_delete=models.CASCADE, related_name="certificate"
    )

    certificate_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(auto_now_add=True)

    # File handling
    pdf_file = models.FileField(
        upload_to="gratuity_certificates/", null=True, blank=True
    )

    # Signature tracking
    signed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    signed_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "payroll_gratuity_certificate"
        verbose_name = _("Gratuity Certificate")

    def __str__(self):
        return f"Certificate - {self.certificate_number}"

    def generate_pdf(self):
        """
        Generate gratuity settlement certificate PDF
        """
        from django.template.loader import render_to_string
        from weasyprint import HTML

        context = {
            "gratuity": self.gratuity,
            "certificate": self,
        }

        html_string = render_to_string("payroll/gratuity_certificate.html", context)

        HTML(string=html_string).write_pdf(
            self.pdf_file.path if hasattr(self.pdf_file, "path") else None
        )
