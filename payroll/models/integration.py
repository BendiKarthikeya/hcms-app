from django.db import models
from django.utils.translation import gettext_lazy as _
from fits.models import FitsModel
from base.models import Company

class GLAccount(FitsModel):
    """General Ledger Account codes."""

    code = models.CharField(max_length=50, unique=True, verbose_name=_("Account Code"))
    name = models.CharField(max_length=255, verbose_name=_("Account Name"))
    account_type = models.CharField(
        max_length=50,
        choices=[
            ("Asset", "Asset"),
            ("Liability", "Liability"),
            ("Expense", "Expense"),
            ("Equity", "Equity"),
            ("Revenue", "Revenue"),
        ],
        default="Expense",
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class GLMapping(FitsModel):
    """Mapping between payroll components and GL accounts."""

    MAPPING_TYPE = [
        ("Basic", "Basic Salary"),
        ("Allowance", "Allowance"),
        ("Deduction", "Deduction"),
        ("Tax", "Tax"),
        ("Pension", "Pension"),
    ]
    mapping_type = models.CharField(max_length=50, choices=MAPPING_TYPE)
    component_id = models.IntegerField(
        null=True, blank=True, help_text="ID of Allowance/Deduction if applicable"
    )
    debit_account = models.ForeignKey(
        GLAccount, related_name="debit_mappings", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        GLAccount, related_name="credit_mappings", on_delete=models.PROTECT
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.get_mapping_type_display()} Mapping"


class ICBSConfig(FitsModel):
    """Configuration for ICBS Salary Disbursement."""

    bank_name = models.CharField(max_length=255)
    api_endpoint = models.URLField()
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.bank_name
