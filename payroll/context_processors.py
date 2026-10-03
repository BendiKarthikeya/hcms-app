"""
context_processor.py

This module is used to register context processor`
"""

from employee.models import Employee
from payroll.models import tax_models as models
from payroll.models.models import Deduction


from django.core.cache import cache



def default_currency(request):
    """
    This method will return the currency
    """
    cached_settings = cache.get("ctx_payroll_settings")
    if cached_settings is None:
        obj = models.PayrollSettings.objects.first()
        if obj is None:
            obj = models.PayrollSettings(currency_symbol="$")
            obj.save()
        cached_settings = {"symbol": obj.currency_symbol, "position": obj.position}
        cache.set("ctx_payroll_settings", cached_settings, 120)
    symbol = cached_settings["symbol"]
    position = cached_settings["position"]
    return {
        "currency": request.session.get("currency", symbol),
        "position": request.session.get("position", position),
    }


def host(request):
    """
    This method will return the host
    """
    protocol = "https" if request.is_secure() else "http"
    return {"host": request.get_host(), "protocol": protocol}


def get_deductions(request):
    """
    This method used to return the deduction
    """
    deductions = Deduction.objects.filter(
        only_show_under_employee=False, employer_rate__gt=0
    )
    return {"get_deductions": deductions}


def get_active_employees(request):
    """
    This method used to return the deduction
    """
    employees = Employee.objects.filter(
        is_active=True, contract_set__isnull=False, payslip__isnull=False
    ).distinct()
    return {"get_active_employees": employees}
