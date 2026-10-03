"""
Expenses & Travel Management Models

This module contains models for expense claims, travel management,
receipt processing, and reimbursement workflows.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import Company
from employee.models import Employee


class ExpenseCategory(models.Model):
    """Categories for organizing expenses"""

    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Expense Category")
        verbose_name_plural = _("Expense Categories")

    def __str__(self):
        return self.name


class TravelRequest(models.Model):
    """Travel request model"""

    TRAVEL_TYPES = [
        ("business", _("Business Travel")),
        ("training", _("Training")),
        ("conference", _("Conference")),
        ("client_visit", _("Client Visit")),
    ]

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("submitted", _("Submitted")),
        ("manager_approved", _("Manager Approved")),
        ("finance_approved", _("Finance Approved")),
        ("rejected", _("Rejected")),
        ("completed", _("Completed")),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    travel_type = models.CharField(
        _("Travel Type"), max_length=20, choices=TRAVEL_TYPES
    )
    purpose = models.TextField(_("Purpose of Travel"))
    destination = models.CharField(_("Destination"), max_length=200)
    departure_date = models.DateField(_("Departure Date"))
    return_date = models.DateField(_("Return Date"))
    estimated_cost = models.DecimalField(
        _("Estimated Cost"), max_digits=10, decimal_places=2
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    submitted_date = models.DateTimeField(_("Submitted Date"), auto_now_add=True)
    approved_by_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_travel_requests",
    )
    approved_by_finance = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finance_approved_travel_requests",
    )
    approval_date = models.DateTimeField(_("Approval Date"), null=True, blank=True)
    rejection_reason = models.TextField(_("Rejection Reason"), blank=True)

    class Meta:
        verbose_name = _("Travel Request")
        verbose_name_plural = _("Travel Requests")

    def __str__(self):
        return f"{self.employee} - {self.destination} ({self.departure_date})"


class ExpenseClaim(models.Model):
    """Expense claim model"""

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("submitted", _("Submitted")),
        ("manager_approved", _("Manager Approved")),
        ("finance_approved", _("Finance Approved")),
        ("rejected", _("Rejected")),
        ("paid", _("Paid")),
    ]

    CURRENCY_CHOICES = [
        ("OMR", _("Omani Rial")),
        ("USD", _("US Dollar")),
        ("EUR", _("Euro")),
        ("GBP", _("British Pound")),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    travel_request = models.ForeignKey(
        TravelRequest, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    description = models.TextField(_("Description"))
    expense_date = models.DateField(_("Expense Date"))
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(
        _("Currency"), max_length=3, choices=CURRENCY_CHOICES, default="OMR"
    )
    exchange_rate = models.DecimalField(
        _("Exchange Rate"), max_digits=10, decimal_places=4, default=1.0
    )
    local_amount = models.DecimalField(
        _("Local Amount (OMR)"), max_digits=10, decimal_places=2
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    submitted_date = models.DateTimeField(_("Submitted Date"), auto_now_add=True)
    approved_by_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expense_claims",
    )
    approved_by_finance = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finance_approved_expense_claims",
    )
    approval_date = models.DateTimeField(_("Approval Date"), null=True, blank=True)
    payment_date = models.DateField(_("Payment Date"), null=True, blank=True)
    rejection_reason = models.TextField(_("Rejection Reason"), blank=True)

    class Meta:
        verbose_name = _("Expense Claim")
        verbose_name_plural = _("Expense Claims")

    def __str__(self):
        return f"{self.employee} - {self.description} - {self.amount} {self.currency}"


class Receipt(models.Model):
    """Receipt attachment for expense claims"""

    expense_claim = models.ForeignKey(ExpenseClaim, on_delete=models.CASCADE)
    receipt_file = models.FileField(_("Receipt File"), upload_to="expenses/receipts/")
    description = models.CharField(_("Description"), max_length=200)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    receipt_date = models.DateField(_("Receipt Date"))
    ocr_extracted_data = models.JSONField(
        _("OCR Extracted Data"), null=True, blank=True
    )
    uploaded_at = models.DateTimeField(_("Uploaded At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Receipt")
        verbose_name_plural = _("Receipts")

    def __str__(self):
        return f"Receipt for {self.expense_claim}"


class PerDiemRate(models.Model):
    """Per diem rates by destination"""

    country = models.CharField(_("Country"), max_length=100)
    city = models.CharField(_("City"), max_length=100)
    rate_amount = models.DecimalField(_("Rate Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(
        _("Currency"),
        max_length=3,
        choices=ExpenseClaim.CURRENCY_CHOICES,
        default="OMR",
    )
    effective_date = models.DateField(_("Effective Date"))
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Per Diem Rate")
        verbose_name_plural = _("Per Diem Rates")
        unique_together = ("country", "city", "effective_date")

    def __str__(self):
        return f"{self.city}, {self.country} - {self.rate_amount} {self.currency}"


class ExpensePolicy(models.Model):
    """Expense policy rules"""

    policy_name = models.CharField(_("Policy Name"), max_length=200)
    description = models.TextField(_("Description"))
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    max_amount = models.DecimalField(
        _("Maximum Amount"), max_digits=10, decimal_places=2, null=True, blank=True
    )
    requires_receipt = models.BooleanField(_("Requires Receipt"), default=True)
    requires_approval = models.BooleanField(_("Requires Approval"), default=True)
    approval_levels = models.PositiveIntegerField(_("Approval Levels"), default=1)
    is_active = models.BooleanField(_("Active"), default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Expense Policy")
        verbose_name_plural = _("Expense Policies")

    def __str__(self):
        return self.policy_name


class ExpenseReport(models.Model):
    """Expense report aggregation"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    report_period_start = models.DateField(_("Report Period Start"))
    report_period_end = models.DateField(_("Report Period End"))
    total_amount = models.DecimalField(
        _("Total Amount"), max_digits=12, decimal_places=2, default=0
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=ExpenseClaim.STATUS_CHOICES, default="draft"
    )
    submitted_date = models.DateTimeField(_("Submitted Date"), null=True, blank=True)
    approved_date = models.DateTimeField(_("Approved Date"), null=True, blank=True)
    paid_date = models.DateField(_("Paid Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Expense Report")
        verbose_name_plural = _("Expense Reports")

    def __str__(self):
        return f"Expense Report - {self.employee} ({self.report_period_start} to {self.report_period_end})"


class ExpenseReportItem(models.Model):
    """Items within an expense report"""

    expense_report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE)
    expense_claim = models.ForeignKey(ExpenseClaim, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Expense Report Item")
        verbose_name_plural = _("Expense Report Items")
        unique_together = ("expense_report", "expense_claim")

    def __str__(self):
        return f"{self.expense_report} - {self.expense_claim}"
