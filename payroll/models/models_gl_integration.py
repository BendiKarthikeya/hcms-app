"""
payroll/models/models_gl_integration.py

General Ledger (GL) Integration for Payroll
Creates journal entries for all payroll transactions
Supports multiple chart of accounts configurations
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from base.models import Company, Employee


class GLAccount(models.Model):
    """
    Chart of Accounts for GL integration
    Defines mapping of expense/asset accounts for payroll
    """

    ACCOUNT_TYPE_CHOICES = [
        ("asset", _("Asset")),
        ("liability", _("Liability")),
        ("equity", _("Equity")),
        ("revenue", _("Revenue")),
        ("expense", _("Expense")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="gl_accounts"
    )

    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)

    # Account details
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # GL configuration
    is_cash_account = models.BooleanField(default=False)
    requires_cost_center = models.BooleanField(default=False)
    requires_department = models.BooleanField(default=False)

    # Payroll mapping
    payroll_category = models.CharField(
        max_length=50,
        choices=[
            ("salary_expense", _("Salary Expense")),
            ("allowance_expense", _("Allowance Expense")),
            ("deduction_payable", _("Deduction Payable")),
            ("tax_payable", _("Tax Payable")),
            ("advance_asset", _("Employee Advance")),
            ("loan_asset", _("Employee Loan")),
            ("benefits_liability", _("Benefits Liability")),
        ],
        blank=True,
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll_gl_account"
        verbose_name = _("GL Account")
        verbose_name_plural = _("GL Accounts")
        ordering = ["account_code"]

    def __str__(self):
        return f"{self.account_code} - {self.account_name}"


class CostCenter(models.Model):
    """
    Cost Centers for GL allocation
    Tracks payroll expenses by department/location
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="cost_centers"
    )

    cost_center_code = models.CharField(max_length=20)
    cost_center_name = models.CharField(max_length=255)

    department = models.ForeignKey(
        "base.Department", on_delete=models.SET_NULL, null=True, blank=True
    )

    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payroll_cost_center"
        unique_together = ("company", "cost_center_code")

    def __str__(self):
        return f"{self.cost_center_code} - {self.cost_center_name}"


class JournalEntry(models.Model):
    """
    Journal Entries for payroll transactions
    Double-entry bookkeeping for all payroll debit/credit
    """

    ENTRY_TYPE_CHOICES = [
        ("salary", _("Salary Payment")),
        ("allowance", _("Allowance Payment")),
        ("deduction", _("Deduction")),
        ("tax", _("Tax")),
        ("advance", _("Advance Payment")),
        ("loan", _("Loan Transaction")),
        ("adjustment", _("Adjustment")),
    ]

    ENTRY_STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("posted", _("Posted")),
        ("reversed", _("Reversed")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="journal_entries"
    )

    # Entry identification
    entry_number = models.CharField(max_length=50, unique=True)
    entry_type = models.CharField(max_length=50, choices=ENTRY_TYPE_CHOICES)
    entry_date = models.DateField()
    posting_date = models.DateField(null=True, blank=True)

    # Reference
    payroll_period = models.CharField(max_length=50)
    description = models.TextField()

    # Status
    status = models.CharField(
        max_length=20, choices=ENTRY_STATUS_CHOICES, default="draft"
    )

    # Totals
    total_debit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    total_credit = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )

    # Metadata
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_journal_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    posted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_journal_entries",
    )
    posted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payroll_journal_entry"
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
        ordering = ["-entry_date"]

    def __str__(self):
        return f"JE {self.entry_number} - {self.entry_date}"

    def is_balanced(self):
        """Check if entry is balanced (debit = credit)"""
        return self.total_debit == self.total_credit

    def post_entry(self, posted_by):
        """Post journal entry to GL"""
        if self.status == "draft" and self.is_balanced():
            self.status = "posted"
            self.posted_by = posted_by
            self.posted_at = timezone.now()
            self.save()
            return True
        return False


class JournalEntryLine(models.Model):
    """
    Individual debit/credit lines in a journal entry
    """

    journal_entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="lines"
    )

    account = models.ForeignKey(GLAccount, on_delete=models.SET_NULL, null=True)

    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Amount
    debit_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    credit_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )

    # Reference
    reference_doc = models.CharField(max_length=255, blank=True)
    line_description = models.TextField(blank=True)

    # Employee reference (if applicable)
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "payroll_journal_entry_line"
        ordering = ["journal_entry", "id"]

    def __str__(self):
        return f"Line {self.id} - {self.account}"


class GLPayrollMapping(models.Model):
    """
    Configuration mapping payroll elements to GL accounts
    Used for automated journal entry creation
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="gl_payroll_mappings"
    )

    # Payroll element
    element_type = models.CharField(
        max_length=50,
        choices=[
            ("salary", _("Basic Salary")),
            ("allowance", _("Allowance")),
            ("deduction", _("Deduction")),
            ("tax", _("Tax")),
            ("advance", _("Advance")),
            ("loan", _("Loan")),
        ],
    )
    element_name = models.CharField(max_length=255)

    # GL account mapping
    expense_account = models.ForeignKey(
        GLAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mapped_expense_elements",
    )
    payable_account = models.ForeignKey(
        GLAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mapped_payable_elements",
    )

    # Settings
    create_je_automatically = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)

    class Meta:
        db_table = "payroll_gl_payroll_mapping"
        unique_together = ("company", "element_type", "element_name")

    def __str__(self):
        return f"{self.element_name} → {self.expense_account}"


class TrialBalance(models.Model):
    """
    Trial Balance report from GL
    For audit and reconciliation purposes
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="trial_balances"
    )

    from_date = models.DateField()
    to_date = models.DateField()

    # Summary
    total_debit = models.DecimalField(max_digits=15, decimal_places=2)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2)

    # Generated
    generated_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payroll_trial_balance"
        verbose_name = _("Trial Balance")
        verbose_name_plural = _("Trial Balances")

    def __str__(self):
        return f"TB {self.from_date} to {self.to_date}"

    def is_balanced(self):
        """Check if trial balance is balanced"""
        return self.total_debit == self.total_credit
