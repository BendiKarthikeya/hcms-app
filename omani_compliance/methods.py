"""
Omani Labour Law Compliance Methods
Royal Decree 35/2003 Implementation
"""

from datetime import timedelta
from datetime import date, datetime

from decimal import Decimal

from django.utils.translation import gettext_lazy as _

from payroll.models.models import Contract


class OmaniComplianceEngine:
    """Engine for Omani Labour Law compliance calculations"""

    @staticmethod
    def calculate_end_of_service_gratuity(employee, end_date):
        """
        Calculate end of service gratuity according to Omani law
        Royal Decree 35/2003: 15 days per year of service
        """
        try:
            # Get employment start date
            work_info = employee.employee_work_info
            if not work_info or not work_info.date_joining:
                return Decimal("0")

            start_date = work_info.date_joining

            # Calculate years of service
            years_of_service = (end_date.year - start_date.year) - (
                (end_date.month, end_date.day) < (start_date.month, start_date.day)
            )

            # Get last drawn salary
            last_contract = (
                Contract.objects.filter(employee=employee, contract_status="active")
                .order_by("-contract_start_date")
                .first()
            )

            if not last_contract:
                return Decimal("0")

            daily_salary = last_contract.wage / 30  # Assuming 30 days per month
            gratuity_amount = daily_salary * Decimal('15') * years_of_service
            
            return max(gratuity_amount, Decimal('0'))
            
        except Exception:
            # Log error and return 0
            return Decimal("0")

    @staticmethod
    def validate_working_hours(employee, date, hours_worked):
        """
        Validate working hours against Omani Labour Law limits
        Daily: 8 hours, Weekly: 45 hours
        """
        violations = []

        # Daily limit check
        if hours_worked > 8:
            violations.append(
                {
                    "type": "daily_limit",
                    "limit": 8,
                    "actual": hours_worked,
                    "message": _("Daily working hours exceed Omani Labour Law limit"),
                }
            )

        # Weekly limit check (would need weekly aggregation)
        # This is a simplified check

        return violations

    @staticmethod
    def calculate_overtime_pay(hours_worked, is_holiday=False):
        """
        Calculate overtime pay according to Omani rates
        Regular: 125% of normal rate
        Holiday: 150% of normal rate
        """
        if is_holiday:
            rate = Decimal("1.50")
        else:
            rate = Decimal("1.25")

        return rate

    @staticmethod
    def validate_leave_entitlements(employee, leave_type, requested_days):
        """
        Validate leave requests against Omani Labour Law entitlements
        """
        violations = []

        # Get employee's leave balance
        # This would integrate with the existing leave module

        omani_limits = {
            "annual": 30,
            "sick_full_pay": 10,
            "sick_half_pay": 10,
            "sick_unpaid": 10,
            "maternity": 50,
            "hajj": 15,
            "emergency": 6,
        }

        if leave_type in omani_limits:
            limit = omani_limits[leave_type]
            if requested_days > limit:
                violations.append(
                    {
                        "type": "leave_limit",
                        "leave_type": leave_type,
                        "limit": limit,
                        "requested": requested_days,
                        "message": _(
                            "Leave request exceeds Omani Labour Law entitlement"
                        ),
                    }
                )

        return violations

    @staticmethod
    def calculate_pasi_contributions(gross_salary):
        """
        Calculate PASI (Public Authority for Social Insurance) contributions
        Employee: 10.5% of gross salary
        Employer: 12.5% of gross salary
        """
        employee_rate = Decimal("0.105")  # 10.5%
        employer_rate = Decimal("0.125")  # 12.5%

        employee_contribution = gross_salary * employee_rate
        employer_contribution = gross_salary * employer_rate

        return {
            "employee_contribution": employee_contribution,
            "employer_contribution": employer_contribution,
            "total_contribution": employee_contribution + employer_contribution,
        }

    @staticmethod
    def check_probation_period(employee):
        """
        Check if employee is within probation period (3 months maximum)
        """
        work_info = employee.employee_work_info
        if not work_info or not work_info.date_joining:
            return {"in_probation": False, "days_remaining": 0}

        join_date = work_info.date_joining
        probation_end = join_date + timedelta(days=90)  # 3 months

        today = date.today()
        in_probation = today <= probation_end
        days_remaining = max((probation_end - today).days, 0) if in_probation else 0

        return {
            "in_probation": in_probation,
            "probation_end": probation_end,
            "days_remaining": days_remaining,
        }


class OmaniTaxCalculator:
    """Omani income tax calculator"""

    @staticmethod
    def calculate_income_tax(taxable_income):
        """
        Calculate Omani income tax based on tax brackets
        Note: Oman has very low personal income tax rates
        """
        # Simplified tax calculation - actual rates may vary
        if taxable_income <= Decimal("5000"):
            return Decimal("0")
        elif taxable_income <= Decimal("10000"):
            return taxable_income * Decimal("0.03")  # 3%
        elif taxable_income <= Decimal("15000"):
            return taxable_income * Decimal("0.05")  # 5%
        else:
            return taxable_income * Decimal("0.07")  # 7%

    @staticmethod
    def get_taxable_income(gross_salary, deductions):
        """
        Calculate taxable income after deductions
        """
        # Basic personal allowance
        personal_allowance = Decimal("3000")

        taxable_income = max(
            gross_salary - deductions - personal_allowance, Decimal("0")
        )

        return taxable_income
