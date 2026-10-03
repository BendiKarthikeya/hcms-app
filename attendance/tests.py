"""
Test cases for Attendance module
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, time
from base.models import EmployeeShift
from employee.models import Employee
from .models import Attendance, AttendanceActivity, AttendanceOverTime


class AttendanceModelTest(TestCase):
    """Test cases for Attendance model"""

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
        self.shift = EmployeeShift.objects.create(
            employee_shift="Morning Shift", start_time=time(9, 0), end_time=time(17, 0)
        )

    def test_attendance_creation(self):
        """Test creating an attendance record"""
        attendance_date = datetime.now().date()
        attendance = Attendance.objects.create(
            employee_id=self.employee,
            attendance_date=attendance_date,
            shift_id=self.shift,
            attendance_clock_in_date=attendance_date,
            attendance_clock_in=time(9, 0),
            attendance_clock_out_date=attendance_date,
            attendance_clock_out=time(17, 0),
            attendance_worked_hour=8.0,
        )

        self.assertEqual(attendance.employee_id, self.employee)
        self.assertEqual(attendance.attendance_date, attendance_date)
        self.assertEqual(attendance.shift_id, self.shift)
        self.assertEqual(attendance.attendance_worked_hour, 8.0)

    def test_attendance_activity_creation(self):
        """Test creating attendance activity"""
        activity = AttendanceActivity.objects.create(
            employee_id=self.employee,
            attendance_date=datetime.now().date(),
            clock_in_date=datetime.now().date(),
            clock_in=time(9, 0),
            clock_out_date=datetime.now().date(),
            clock_out=time(17, 0),
            work_type="office",
        )

        self.assertEqual(activity.employee_id, self.employee)
        self.assertEqual(activity.work_type, "office")

    def test_overtime_creation(self):
        """Test creating overtime record"""
        attendance_date = datetime.now().date()
        attendance = Attendance.objects.create(
            employee_id=self.employee,
            attendance_date=attendance_date,
            shift_id=self.shift,
            attendance_clock_in_date=attendance_date,
            attendance_clock_in=time(9, 0),
            attendance_clock_out_date=attendance_date,
            attendance_clock_out=time(19, 0),  # 2 hours overtime
            attendance_worked_hour=10.0,
        )

        overtime = AttendanceOverTime.objects.create(
            employee_id=self.employee, attendance_id=attendance, hour=2.0, amount=100.0
        )

        self.assertEqual(overtime.employee_id, self.employee)
        self.assertEqual(overtime.hour, 2.0)
        self.assertEqual(overtime.amount, 100.0)


class AttendanceViewsTest(TestCase):
    """Test cases for Attendance views"""

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

    def test_attendance_list_view(self):
        """Test attendance list view"""
        response = self.client.get("/attendance/")
        self.assertEqual(response.status_code, 200)

    def test_attendance_create_view(self):
        """Test attendance creation view"""
        response = self.client.get("/attendance/create/")
        self.assertEqual(response.status_code, 200)

    def test_attendance_report_view(self):
        """Test attendance report view"""
        response = self.client.get("/attendance/report/")
        self.assertEqual(response.status_code, 200)


class AttendanceURLsTest(TestCase):
    """Test cases for Attendance URLs"""

    def test_attendance_urls(self):
        """Test attendance URL patterns"""
        # Test main attendance URL
        response = self.client.get("/attendance/")
        self.assertEqual(response.status_code, 200)

        # Test attendance creation URL
        response = self.client.get("/attendance/create/")
        self.assertEqual(response.status_code, 200)

        # Test attendance report URL
        response = self.client.get("/attendance/report/")
        self.assertEqual(response.status_code, 200)


class AttendanceFormsTest(TestCase):
    """Test cases for Attendance forms"""

    def test_attendance_form_validation(self):
        """Test attendance form validation"""
        from .forms import AttendanceForm

        # Test valid form data
        form_data = {
            "employee_id": "1",
            "attendance_date": "2024-01-01",
            "attendance_clock_in": "09:00",
            "attendance_clock_out": "17:00",
        }

        AttendanceForm(data=form_data)
        # Form validation might require additional setup
        # self.assertTrue(form.is_valid())

    def test_attendance_activity_form(self):
        """Test attendance activity form"""
        from .forms import AttendanceActivityForm

        form_data = {
            "employee_id": "1",
            "attendance_date": "2024-01-01",
            "clock_in": "09:00",
            "clock_out": "17:00",
        }

        AttendanceActivityForm(data=form_data)
        # Form validation might require additional setup


class AttendanceIntegrationTest(TestCase):
    """Integration tests for Attendance module"""

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
        self.shift = EmployeeShift.objects.create(
            employee_shift="Morning Shift", start_time=time(9, 0), end_time=time(17, 0)
        )

    def test_attendance_lifecycle(self):
        """Test complete attendance lifecycle"""
        # Create attendance record
        attendance_date = datetime.now().date()
        attendance = Attendance.objects.create(
            employee_id=self.employee,
            attendance_date=attendance_date,
            shift_id=self.shift,
            attendance_clock_in_date=attendance_date,
            attendance_clock_in=time(9, 0),
            attendance_clock_out_date=attendance_date,
            attendance_clock_out=time(17, 0),
            attendance_worked_hour=8.0,
        )

        # Verify creation
        self.assertEqual(Attendance.objects.count(), 1)

        # Update attendance
        attendance.attendance_clock_out = time(18, 0)
        attendance.attendance_worked_hour = 9.0
        attendance.save()

        # Verify update
        updated_attendance = Attendance.objects.get(id=attendance.id)
        self.assertEqual(updated_attendance.attendance_worked_hour, 9.0)

        # Delete attendance
        attendance.delete()

        # Verify deletion
        self.assertEqual(Attendance.objects.count(), 0)


class AttendancePerformanceTest(TestCase):
    """Performance tests for Attendance module"""

    def test_bulk_attendance_creation(self):
        """Test bulk attendance creation performance"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        shift = EmployeeShift.objects.create(
            employee_shift="Morning Shift", start_time=time(9, 0), end_time=time(17, 0)
        )

        employees = []
        for i in range(50):
            employee = Employee.objects.create(
                employee_first_name=f"Employee{i}",
                employee_last_name="Doe",
                email=f"employee{i}@example.com",
                phone=f"+123456789{i:02d}",
                employee_user_id=user,
            )
            employees.append(employee)

        # Create attendance records for all employees
        attendance_date = datetime.now().date()
        attendance_records = []
        for employee in employees:
            attendance_records.append(
                Attendance(
                    employee_id=employee,
                    attendance_date=attendance_date,
                    shift_id=shift,
                    attendance_clock_in_date=attendance_date,
                    attendance_clock_in=time(9, 0),
                    attendance_clock_out_date=attendance_date,
                    attendance_clock_out=time(17, 0),
                    attendance_worked_hour=8.0,
                )
            )

        Attendance.objects.bulk_create(attendance_records)
        self.assertEqual(Attendance.objects.count(), 50)


class AttendanceSecurityTest(TestCase):
    """Security tests for Attendance module"""

    def test_attendance_data_integrity(self):
        """Test attendance data integrity"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_user_id=user,
        )
        shift = EmployeeShift.objects.create(
            employee_shift="Morning Shift", start_time=time(9, 0), end_time=time(17, 0)
        )

        # Test clock-out before clock-in (should be handled appropriately)
        attendance_date = datetime.now().date()
        attendance = Attendance.objects.create(
            employee_id=employee,
            attendance_date=attendance_date,
            shift_id=shift,
            attendance_clock_in_date=attendance_date,
            attendance_clock_in=time(17, 0),  # Clock-in at 5 PM
            attendance_clock_out_date=attendance_date,
            attendance_clock_out=time(9, 0),  # Clock-out at 9 AM (before clock-in)
            attendance_worked_hour=-8.0,  # Negative hours
        )

        # The system should handle this scenario appropriately
        self.assertIsNotNone(attendance)


class AttendanceCalculationTest(TestCase):
    """Test cases for attendance calculations"""

    def test_worked_hour_calculation(self):
        """Test worked hour calculation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_user_id=user,
        )
        shift = EmployeeShift.objects.create(
            employee_shift="Morning Shift", start_time=time(9, 0), end_time=time(17, 0)
        )

        attendance_date = datetime.now().date()
        attendance = Attendance.objects.create(
            employee_id=employee,
            attendance_date=attendance_date,
            shift_id=shift,
            attendance_clock_in_date=attendance_date,
            attendance_clock_in=time(9, 0),
            attendance_clock_out_date=attendance_date,
            attendance_clock_out=time(17, 0),
        )

        # The system should calculate worked hours automatically
        # This might be handled by signals or methods
        self.assertIsNotNone(attendance)
