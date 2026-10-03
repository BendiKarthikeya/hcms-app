"""
End-of-Service Benefits (EOSB) & Gratuity Models
Implements Omani Labor Law Royal Decree 35/2003 calculations
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import Company
from employee.models import Employee
from fits.models import FitsModel


class EOSBGratuitySettings(models.Model):
    """
    End-of-Service Benefit & Gratuity Calculation Settings
    Based on Omani Labor Law Royal Decree 35/2003
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="eosb_settings",
        verbose_name=_("Company"),
    )

    # Gratuity Rates (per month of service)
    # Omani Law provides for:
    # Service 0-3 years: Not entitled to gratuity
    # Service 3-5 years: 1/3 of last salary per year
    # Service 5+ years: 1/2 of last salary per year
    # Service 20+ years: Full salary per year (max 12 months)

    gratuity_less_than_3_years = models.FloatField(
        default=0,
        verbose_name=_("Gratuity Rate (< 3 years service)"),
        help_text=_("As proportion of monthly salary"),
    )
    gratuity_3_to_5_years = models.FloatField(
        default=1 / 3,
        verbose_name=_("Gratuity Rate (3-5 years service)"),
        help_text=_("1/3 of last monthly salary per year"),
    )
    gratuity_5_to_20_years = models.FloatField(
        default=1 / 2,
        verbose_name=_("Gratuity Rate (5-20 years service)"),
        help_text=_("1/2 of last monthly salary per year"),
    )
    gratuity_20_plus_years = models.FloatField(
        default=1.0,
        verbose_name=_("Gratuity Rate (20+ years service)"),
        help_text=_("Full monthly salary per year, max 12 months"),
    )

    # Settings
    consider_unpaid_leave = models.BooleanField(
        default=False,
        verbose_name=_("Consider Unpaid Leave in Calculation"),
    )
    include_fixed_allowances = models.BooleanField(
        default=True,
        verbose_name=_("Include Fixed Allowances in Final Salary"),
    )
    include_variable_allowances = models.BooleanField(
        default=True,
        verbose_name=_("Include Variable/Performance Allowances"),
    )
    include_last_bonus = models.BooleanField(
        default=True,
        verbose_name=_("Include Last Year Annual Bonus"),
    )

    # Deductions
    auto_deduct_loans = models.BooleanField(
        default=True,
        verbose_name=_("Auto-deduct Outstanding Loans"),
    )
    auto_deduct_advances = models.BooleanField(
        default=True,
        verbose_name=_("Auto-deduct Outstanding Advances"),
    )

    # System Settings
    requires_hr_approval = models.BooleanField(
        default=True,
        verbose_name=_("Requires HR Approval"),
    )
    requires_director_approval = models.BooleanField(
        default=False,
        verbose_name=_("Requires Director Approval"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated"),
    )

    class Meta:
        verbose_name = _("EOSB Gratuity Settings")
        verbose_name_plural = _("EOSB Gratuity Settings")

    def __str__(self):
        return f"EOSB Settings - {self.company.name}"


class EndOfServiceBenefit(FitsModel):
    """
    End-of-Service Benefit (EOSB) Calculation Record
    Calculates gratuity based on Omani Labor Law
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("calculated", _("Calculated - Pending Review")),
        ("hr_approved", _("HR Approved")),
        ("director_approved", _("Director Approved")),
        ("processed", _("Processed - Paid")),
        ("cancelled", _("Cancelled")),
    ]

    SEPARATION_REASON_CHOICES = [
        ("retirement", _("Retirement")),
        ("resignation", _("Resignation")),
        ("termination_without_cause", _("Termination Without Just Cause")),
        ("termination_with_cause", _("Termination With Just Cause")),
        ("contract_end", _("Contract End")),
        ("death", _("Employee Death")),
        ("disability", _("Disability")),
        ("layoff", _("Layoff/Retrenchment")),
    ]

    # Employee & Period Info
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="end_of_service_benefits",
        verbose_name=_("Employee"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    separation_date = models.DateField(
        verbose_name=_("Separation/Exit Date"),
    )
    separation_reason = models.CharField(
        max_length=50,
        choices=SEPARATION_REASON_CHOICES,
        verbose_name=_("Reason for Separation"),
    )

    # Service Calculation
    initial_employment_date = models.DateField(
        verbose_name=_("Initial Employment Date"),
    )
    total_years_of_service = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Total Years of Service"),
        help_text=_("Calculated from initial employment date to separation date"),
    )
    total_months_of_service = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Total Months of Service"),
    )
    unpaid_leave_days = models.IntegerField(
        default=0,
        verbose_name=_("Unpaid Leave Days (to be deducted)"),
    )
    service_deduction_days = models.IntegerField(
        default=0,
        verbose_name=_("Service Deduction Days"),
        help_text=_("Days to deduct from service calculation"),
    )

    # Salary Components
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Basic Salary (Last Month)"),
    )
    monthly_fixed_allowances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Monthly Fixed Allowances"),
    )
    monthly_variable_allowances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Monthly Variable Allowances (Average)"),
    )
    last_year_annual_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Last Year Annual Bonus"),
    )
    final_monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Final Monthly Salary for Calculation"),
        help_text=_("Sum of components used for gratuity calculation"),
    )

    # Gratuity Calculation
    applicable_gratuity_rate = models.FloatField(
        verbose_name=_("Applicable Gratuity Rate"),
        help_text=_("Based on years of service (0, 1/3, 1/2, or 1.0)"),
    )
    gross_gratuity_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Gross Gratuity Amount"),
    )

    # Deductions
    outstanding_loan_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Outstanding Loan Balance"),
    )
    outstanding_advance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Outstanding Advance"),
    )
    salary_adjustments = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Salary Adjustments"),
    )
    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Other Deductions"),
    )
    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Total Deductions"),
    )

    # Final Amount
    net_eosb_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Net End-of-Service Benefit (Amount to Pay)"),
    )

    # Status & Approvals
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )
    calculated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculated_eosb",
        verbose_name=_("Calculated By"),
    )
    calculated_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Calculation Date"),
    )
    hr_approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hr_approved_eosb",
        verbose_name=_("HR Approved By"),
    )
    hr_approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("HR Approval Date"),
    )
    director_approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="director_approved_eosb",
        verbose_name=_("Director Approved By"),
    )
    director_approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Director Approval Date"),
    )

    # Payment Info
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("bank_transfer", _("Bank Transfer")),
            ("cheque", _("Cheque")),
            ("cash", _("Cash")),
        ],
        default="bank_transfer",
        verbose_name=_("Payment Method"),
    )
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Payment Reference (Cheque/Transfer #)"),
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date Paid"),
    )

    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Additional Notes"),
    )
    hr_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("HR Comments"),
    )
    director_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Director Comments"),
    )

    class Meta:
        verbose_name = _("End-of-Service Benefit")
        verbose_name_plural = _("End-of-Service Benefits")
        ordering = ["-separation_date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["separation_date"]),
        ]

    def __str__(self):
        return f"EOSB - {self.employee.get_name()} ({self.separation_date.strftime('%Y-%m-%d')})"

    def calculate_gratuity(self):
        """Calculate gratuity amount based on Omani Labor Law"""
        settings = self.company.eosb_settings

        # Determine applicable rate
        if self.total_years_of_service < 3:
            self.applicable_gratuity_rate = settings.gratuity_less_than_3_years
        elif self.total_years_of_service < 5:
            self.applicable_gratuity_rate = settings.gratuity_3_to_5_years
        elif self.total_years_of_service < 20:
            self.applicable_gratuity_rate = settings.gratuity_5_to_20_years
        else:
            self.applicable_gratuity_rate = settings.gratuity_20_plus_years

        # Calculate gross gratuity
        self.gross_gratuity_amount = (
            self.final_monthly_salary
            * self.applicable_gratuity_rate
            * self.total_years_of_service
        )

        # Calculate deductions
        self.total_deductions = (
            self.outstanding_loan_balance
            + self.outstanding_advance
            + self.salary_adjustments
            + self.other_deductions
        )

        # Calculate net amount
        self.net_eosb_amount = max(
            0, self.gross_gratuity_amount - self.total_deductions
        )


class ServiceAward(FitsModel):
    """
    Service Awards for Long Service Recognition
    Optional awards given for 5, 10, 15, 20+ years of service
    """

    AWARD_CHOICES = [
        ("5_years", _("5 Years Service Award")),
        ("10_years", _("10 Years Service Award")),
        ("15_years", _("15 Years Service Award")),
        ("20_years", _("20 Years Service Award")),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="service_awards",
        verbose_name=_("Employee"),
    )
    award_type = models.CharField(
        max_length=20,
        choices=AWARD_CHOICES,
        verbose_name=_("Award Type"),
    )
    award_date = models.DateField(
        verbose_name=_("Award Date"),
    )
    award_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Award Amount"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )

    class Meta:
        verbose_name = _("Service Award")
        verbose_name_plural = _("Service Awards")
        ordering = ["-award_date"]

    def __str__(self):
        return f"{self.employee.get_name()} - {self.get_award_type_display()}"
