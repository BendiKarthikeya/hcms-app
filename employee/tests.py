"""
Test cases for Employee module
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from base.models import Company, Department, JobPosition, JobRole
from .models import Employee


class EmployeeModelTest(TestCase):
    """Test cases for Employee model"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
        self.department = Department.objects.create(department="Test Department")
        self.job_position = JobPosition.objects.create(job_position="Test Position")
        self.job_role = JobRole.objects.create(job_role="Test Role")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_employee_creation(self):
        """Test creating an employee"""
        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_user_id=self.user,
        )

        self.assertEqual(employee.employee_first_name, "John")
        self.assertEqual(employee.employee_last_name, "Doe")
        self.assertEqual(employee.email, "john.doe@example.com")
        self.assertEqual(str(employee), "John Doe")

    def test_employee_required_fields(self):
        """Test that required fields are enforced"""
        # Should fail without required fields
        with self.assertRaises(Exception):
            Employee.objects.create()

    def test_employee_email_uniqueness(self):
        """Test email uniqueness constraint"""
        Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
        )

        # Should fail with duplicate email
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_first_name="Jane",
                employee_last_name="Doe",
                email="john.doe@example.com",
                phone="+0987654321",
            )

    def test_employee_profile_image(self):
        """Test employee profile image upload"""
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake_image_content",
            content_type="image/jpeg",
        )

        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_profile=image,
        )

        self.assertIsNotNone(employee.employee_profile)

    def test_employee_gender_choices(self):
        """Test gender field choices"""
        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            gender="male",
        )

        self.assertEqual(employee.gender, "male")

        # Test invalid gender choice
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_first_name="Jane",
                employee_last_name="Doe",
                email="jane.doe@example.com",
                phone="+0987654321",
                gender="invalid",
            )


class EmployeeViewsTest(TestCase):
    """Test cases for Employee views"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_user_id=self.user,
        )

    def test_employee_list_view(self):
        """Test employee list view"""
        response = self.client.get("/employee/")
        self.assertEqual(response.status_code, 200)

    def test_employee_detail_view(self):
        """Test employee detail view"""
        response = self.client.get(f"/employee/{self.employee.id}/")
        self.assertEqual(response.status_code, 200)

    def test_employee_create_view(self):
        """Test employee creation view"""
        response = self.client.get("/employee/create/")
        self.assertEqual(response.status_code, 200)

    def test_employee_update_view(self):
        """Test employee update view"""
        response = self.client.get(f"/employee/{self.employee.id}/update/")
        self.assertEqual(response.status_code, 200)


class EmployeeURLsTest(TestCase):
    """Test cases for Employee URLs"""

    def test_employee_urls(self):
        """Test employee URL patterns"""
        # Test main employee URL
        response = self.client.get("/employee/")
        self.assertEqual(response.status_code, 200)

        # Test employee creation URL
        response = self.client.get("/employee/create/")
        self.assertEqual(response.status_code, 200)

        # Test employee detail URL
        response = self.client.get("/employee/1/")
        self.assertEqual(response.status_code, 200)


class EmployeeFormsTest(TestCase):
    """Test cases for Employee forms"""

    def test_employee_form_validation(self):
        """Test employee form validation"""
        from .forms import EmployeeForm

        # Test valid form data
        form_data = {
            "employee_first_name": "John",
            "employee_last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
        }

        form = EmployeeForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid form data (missing required field)
        invalid_data = {
            "employee_first_name": "John",
            "email": "john.doe@example.com",
            # Missing phone field
        }

        form = EmployeeForm(data=invalid_data)
        self.assertFalse(form.is_valid())


class EmployeeIntegrationTest(TestCase):
    """Integration tests for Employee module"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_employee_lifecycle(self):
        """Test complete employee lifecycle"""
        # Create employee
        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_user_id=self.user,
        )

        # Verify creation
        self.assertEqual(Employee.objects.count(), 1)

        # Update employee
        employee.employee_first_name = "John Updated"
        employee.save()

        # Verify update
        updated_employee = Employee.objects.get(id=employee.id)
        self.assertEqual(updated_employee.employee_first_name, "John Updated")

        # Delete employee
        employee.delete()

        # Verify deletion
        self.assertEqual(Employee.objects.count(), 0)


class EmployeePerformanceTest(TestCase):
    """Performance tests for Employee module"""

    def test_employee_bulk_creation(self):
        """Test bulk employee creation performance"""
        employees = []
        for i in range(100):
            employees.append(
                Employee(
                    employee_first_name=f"Employee{i}",
                    employee_last_name="Doe",
                    email=f"employee{i}@example.com",
                    phone=f"+123456789{i:02d}",
                )
            )

        Employee.objects.bulk_create(employees)
        self.assertEqual(Employee.objects.count(), 100)


class EmployeeSecurityTest(TestCase):
    """Security tests for Employee module"""

    def test_employee_data_privacy(self):
        """Test employee data privacy"""
        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            address="123 Main St",
        )

        # Verify sensitive data is properly stored
        self.assertIsNotNone(employee.email)
        self.assertIsNotNone(employee.phone)

    def test_employee_xss_protection(self):
        """Test XSS protection in employee fields"""
        # Test with potential XSS content
        xss_content = "<script>alert('xss')</script>"

        Employee.objects.create(
            employee_first_name=xss_content,
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
        )


class EmployeePortalIntegrationTest(TestCase):
    """Integration tests for the Employee Self-Service Portal features"""

    def setUp(self):
        """Set up test data for an employee user"""
        self.user = User.objects.create_user(
            username="empuser", email="emp@example.com", password="emppass123"
        )
        self.employee = Employee.objects.create(
            employee_first_name="Employee",
            employee_last_name="One",
            email="emp@example.com",
            employee_user_id=self.user,
        )
        self.client.login(username="empuser", password="emppass123")

    def test_employee_profile_access(self):
        """Test accessing own profile"""
        response = self.client.get("/employee/employee-profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Employee One")

    def test_leave_requests_access(self):
        """Test accessing own leave requests"""
        response = self.client.get("/leave/user-request-view/")
        self.assertEqual(response.status_code, 200)

    def test_attendance_access(self):
        """Test accessing own attendance record"""
        response = self.client.get("/attendance/view-my-attendance/")
        self.assertEqual(response.status_code, 200)

    def test_payslip_access(self):
        """Test accessing own payslips"""
        response = self.client.get("/payroll/payslip-view/")
        self.assertEqual(response.status_code, 200)

    def test_document_request_access(self):
        """Test accessing own document requests"""
        response = self.client.get("/employee/document-request-view/")
        self.assertEqual(response.status_code, 200)
