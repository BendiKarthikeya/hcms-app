"""
Omani Labour Law Compliance Models
Royal Decree 35/2003 Implementation
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import Company
from employee.models import Employee
from fits.models import FitsModel


class OmaniLabourLawConfig(FitsModel):
    """Configuration for Omani Labour Law compliance"""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Company")
    )

    # Leave entitlements according to Royal Decree 35/2003
    annual_leave_days = models.IntegerField(
        default=30, verbose_name=_("Annual Leave Days")
    )

    sick_leave_full_pay_days = models.IntegerField(
        default=10, verbose_name=_("Sick Leave Full Pay Days")
    )

    sick_leave_half_pay_days = models.IntegerField(
        default=10, verbose_name=_("Sick Leave Half Pay Days")
    )

    sick_leave_unpaid_days = models.IntegerField(
        default=10, verbose_name=_("Sick Leave Unpaid Days")
    )

    maternity_leave_days = models.IntegerField(
        default=50, verbose_name=_("Maternity Leave Days")
    )

    hajj_leave_days = models.IntegerField(default=15, verbose_name=_("Hajj Leave Days"))

    emergency_leave_days = models.IntegerField(
        default=6, verbose_name=_("Emergency Leave Days")
    )

    # Working hours
    daily_working_hours = models.IntegerField(
        default=8, verbose_name=_("Daily Working Hours")
    )

    weekly_working_hours = models.IntegerField(
        default=45, verbose_name=_("Weekly Working Hours")
    )

    # Overtime rates
    overtime_regular_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.25,
        verbose_name=_("Regular Overtime Rate"),
    )

    overtime_holiday_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.50,
        verbose_name=_("Holiday Overtime Rate"),
    )

    # End of service gratuity
    gratuity_days_per_year = models.IntegerField(
        default=15, verbose_name=_("Gratuity Days Per Year")
    )

    # Probation period
    probation_period_months = models.IntegerField(
        default=3, verbose_name=_("Probation Period (Months)")
    )

    # PASI integration
    pasi_enabled = models.BooleanField(
        default=False, verbose_name=_("PASI Integration Enabled")
    )

    pasi_employee_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.105,
        verbose_name=_("PASI Employee Rate"),
    )

    pasi_employer_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.125,
        verbose_name=_("PASI Employer Rate"),
    )

    class Meta:
        verbose_name = _("Omani Labour Law Configuration")
        verbose_name_plural = _("Omani Labour Law Configurations")


class OmaniComplianceAudit(FitsModel):
    """Audit trail for Omani compliance checks"""

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, verbose_name=_("Employee")
    )

    check_type = models.CharField(max_length=100, verbose_name=_("Check Type"))

    description = models.TextField(verbose_name=_("Description"))

    status = models.CharField(
        max_length=20,
        choices=[
            ("compliant", _("Compliant")),
            ("non_compliant", _("Non-Compliant")),
            ("warning", _("Warning")),
        ],
        verbose_name=_("Status"),
    )

    details = models.JSONField(default=dict, verbose_name=_("Details"))

    class Meta:
        verbose_name = _("Omani Compliance Audit")
        verbose_name_plural = _("Omani Compliance Audits")


class OmaniTaxCalculation(FitsModel):
    """Omani tax calculation records"""

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, verbose_name=_("Employee")
    )

    month = models.DateField(verbose_name=_("Month"))

    gross_salary = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Gross Salary")
    )

    taxable_income = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Taxable Income")
    )

    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Tax Amount")
    )

    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Tax Rate")
    )

    class Meta:
        verbose_name = _("Omani Tax Calculation")
        verbose_name_plural = _("Omani Tax Calculations")
