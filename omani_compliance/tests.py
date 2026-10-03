"""
Test cases for Omani Labour Law Compliance module
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from base.models import Company
from employee.models import Employee
from payroll.models import Contract

from .methods import OmaniComplianceEngine
from .models import OmaniLabourLawConfig


class OmaniComplianceEngineTest(TestCase):
    """Test cases for Omani compliance engine"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create test employee
        self.employee = Employee.objects.create(
            employee_first_name="Test",
            employee_last_name="Employee",
            email="test@example.com",
            employee_work_info__company=self.company,
            employee_work_info__date_joining=date(2023, 1, 1),
        )

        # Create test contract
        self.contract = Contract.objects.create(
            employee=self.employee,
            wage=Decimal("1000"),
            contract_start_date=date(2023, 1, 1),
            contract_status="active",
        )

        # Create Omani configuration
        self.config = OmaniLabourLawConfig.objects.create(company=self.company)

    def test_calculate_end_of_service_gratuity(self):
        """Test end of service gratuity calculation"""
        end_date = date(2026, 1, 1)
        gratuity = OmaniComplianceEngine.calculate_end_of_service_gratuity(
            self.employee, end_date
        )

        # 3 years of service * 15 days/year * (1000/30 daily salary)
        expected_gratuity = (
            Decimal("3") * Decimal("15") * (Decimal("1000") / Decimal("30"))
        )
        self.assertEqual(gratuity, expected_gratuity)

    def test_validate_working_hours(self):
        """Test working hours validation"""
        violations = OmaniComplianceEngine.validate_working_hours(
            self.employee, date.today(), 10
        )

        # Should have daily limit violation
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["type"], "daily_limit")

    def test_calculate_overtime_pay(self):
        """Test overtime pay calculation"""
        regular_rate = OmaniComplianceEngine.calculate_overtime_pay(2, False)
        holiday_rate = OmaniComplianceEngine.calculate_overtime_pay(2, True)

        self.assertEqual(regular_rate, Decimal("1.25"))
        self.assertEqual(holiday_rate, Decimal("1.50"))

    def test_validate_leave_entitlements(self):
        """Test leave entitlement validation"""
        violations = OmaniComplianceEngine.validate_leave_entitlements(
            self.employee, "annual", 35
        )

        # Should have leave limit violation
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["type"], "leave_limit")

    def test_calculate_pasi_contributions(self):
        """Test PASI contributions calculation"""
        contributions = OmaniComplianceEngine.calculate_pasi_contributions(
            Decimal("1000")
        )

        self.assertEqual(contributions["employee_contribution"], Decimal("105.00"))
        self.assertEqual(contributions["employer_contribution"], Decimal("125.00"))
        self.assertEqual(contributions["total_contribution"], Decimal("230.00"))

    def test_check_probation_period(self):
        """Test probation period check"""
        result = OmaniComplianceEngine.check_probation_period(self.employee)

        # Employee joined in 2023, should not be in probation
        self.assertFalse(result["in_probation"])
        self.assertEqual(result["days_remaining"], 0)


class OmaniLabourLawConfigTest(TestCase):
    """Test cases for Omani Labour Law configuration model"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")

    def test_config_creation(self):
        """Test configuration creation"""
        config = OmaniLabourLawConfig.objects.create(company=self.company)

        self.assertEqual(config.annual_leave_days, 30)
        self.assertEqual(config.maternity_leave_days, 50)
        self.assertEqual(config.daily_working_hours, 8)
        self.assertFalse(config.pasi_enabled)

    def test_config_string_representation(self):
        """Test string representation"""
        config = OmaniLabourLawConfig.objects.create(company=self.company)

        self.assertEqual(
            str(config), f"Omani Labour Law Configuration - {self.company.name}"
        )


class OmaniComplianceIntegrationTest(TestCase):
    """Integration tests for Omani compliance"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.employee = Employee.objects.create(
            employee_first_name="Test",
            employee_last_name="Employee",
            email="test@example.com",
            employee_work_info__company=self.company,
            employee_work_info__date_joining=date(2025, 1, 1),  # Recent join
        )

    def test_complete_compliance_check(self):
        """Test complete compliance check workflow"""
        # Check probation period
        probation_result = OmaniComplianceEngine.check_probation_period(self.employee)

        # Should be in probation (recent join)
        self.assertTrue(probation_result["in_probation"])

        # Check working hours
        violations = OmaniComplianceEngine.validate_working_hours(
            self.employee, date.today(), 9
        )

        # Should have daily limit violation
        self.assertEqual(len(violations), 1)
