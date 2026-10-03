#!/usr/bin/env python
"""
Script to populate dummy data for all HCMS features
Run: python populate_dummy_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horilla.settings")
sys.path.insert(0, "/Users/karthikeya/Downloads/Omen-2/hcms")
django.setup()

from django.contrib.auth.models import User
from employee.models import Employee, EmployeeWorkInformation, EmployeeBankDetails
from base.models import Department, JobPosition, EmployeeShift
from recruitment.models import Recruitment, Stage, Candidate
from pms.models import PerformanceRating, Objective, KeyResult
from payroll.models import Payslip, Allowance, Deduction
from leave.models import LeaveType, LeaveRequest, Holiday
from attendance.models import Attendance
from base.models import Company


def create_companies():
    """Create company if not exists"""
    Company.objects.get_or_create(
        code="OMANI_EMP",
        defaults={"name": "Omani Employers Company", "address": "Muscat, Oman"},
    )
    print("✓ Company created/exists")


def create_departments():
    """Create departments"""
    depts = [
        {"code": "IT", "name": "Information Technology"},
        {"code": "HR", "name": "Human Resources"},
        {"code": "FIN", "name": "Finance"},
        {"code": "OPS", "name": "Operations"},
        {"code": "SALES", "name": "Sales"},
    ]
    for dept in depts:
        Department.objects.get_or_create(
            code=dept["code"], defaults={"department": dept["name"]}
        )
    print(f"✓ {len(depts)} Departments created/exist")


def create_job_positions():
    """Create job positions"""
    dept_it = Department.objects.filter(code="IT").first()
    positions = [
        {"code": "SE", "name": "Software Engineer", "dept": dept_it},
        {"code": "PM", "name": "Product Manager", "dept": dept_it},
        {
            "code": "HR_MGR",
            "name": "HR Manager",
            "dept": Department.objects.filter(code="HR").first(),
        },
        {
            "code": "FIN_MGR",
            "name": "Finance Manager",
            "dept": Department.objects.filter(code="FIN").first(),
        },
        {
            "code": "SALES_EXEC",
            "name": "Sales Executive",
            "dept": Department.objects.filter(code="SALES").first(),
        },
    ]
    for pos in positions:
        JobPosition.objects.get_or_create(
            code=pos["code"],
            defaults={"job_position": pos["name"], "department": pos["dept"]},
        )
    print(f"✓ {len(positions)} Job Positions created/exist")


def create_shifts():
    """Create shifts"""
    shifts = [
        {
            "code": "MORNING",
            "name": "Morning Shift",
            "start": "09:00:00",
            "end": "17:00:00",
        },
        {
            "code": "EVENING",
            "name": "Evening Shift",
            "start": "14:00:00",
            "end": "22:00:00",
        },
        {
            "code": "NIGHT",
            "name": "Night Shift",
            "start": "22:00:00",
            "end": "06:00:00",
        },
    ]
    for shift in shifts:
        EmployeeShift.objects.get_or_create(
            shift_name=shift["name"],
            defaults={"start_time": shift["start"], "end_time": shift["end"]},
        )
    print(f"✓ {len(shifts)} Shifts created/exist")


def create_users_and_employees():
    """Create users and employees"""
    employees_data = [
        {
            "email": "john.smith@company.com",
            "first_name": "John",
            "last_name": "Smith",
            "phone": "+968-9145-1234",
            "badge_id": "EMP001",
        },
        {
            "email": "fatima.khan@company.com",
            "first_name": "Fatima",
            "last_name": "Khan",
            "phone": "+968-9156-5678",
            "badge_id": "EMP002",
        },
        {
            "email": "rajesh.patel@company.com",
            "first_name": "Rajesh",
            "last_name": "Patel",
            "phone": "+968-9167-9012",
            "badge_id": "EMP003",
        },
        {
            "email": "sara.johnson@company.com",
            "first_name": "Sara",
            "last_name": "Johnson",
            "phone": "+968-9178-3456",
            "badge_id": "EMP004",
        },
        {
            "email": "ahmed.ali@company.com",
            "first_name": "Ahmed",
            "last_name": "Ali",
            "phone": "+968-9189-7890",
            "badge_id": "EMP005",
        },
    ]

    created_employees = []
    for emp_data in employees_data:
        user, _ = User.objects.get_or_create(
            username=emp_data["email"].split("@")[0],
            defaults={
                "email": emp_data["email"],
                "first_name": emp_data["first_name"],
                "last_name": emp_data["last_name"],
            },
        )

        # Create employee
        it_dept = Department.objects.filter(code="IT").first()
        se_position = JobPosition.objects.filter(code="SE").first()
        morning_shift = EmployeeShift.objects.filter(shift_name="Morning Shift").first()

        employee, created = Employee.objects.get_or_create(
            employee_user_id=user.id,
            defaults={
                "first_name": emp_data["first_name"],
                "last_name": emp_data["last_name"],
                "email": emp_data["email"],
                "phone": emp_data["phone"],
                "date_of_join": datetime.now().date(),
                "badge_id": emp_data["badge_id"],
            },
        )

        # Create work information
        EmployeeWorkInformation.objects.get_or_create(
            employee_id=employee.id,
            defaults={
                "department": it_dept,
                "job_position": se_position,
                "shift": morning_shift,
            },
        )

        # Create bank details
        EmployeeBankDetails.objects.get_or_create(
            employee_id=employee.id,
            defaults={
                "account_holder": emp_data["first_name"],
                "account_number": f"123456789{emp_data['badge_id'][-2:]}",
                "bank_name": "Omani Bank",
            },
        )

        created_employees.append(employee)

    print(f"✓ {len(created_employees)} Employees created/exist")
    return created_employees


def create_leave_types():
    """Create leave types"""
    leave_types = [
        {"code": "AL", "name": "Annual Leave", "days": 20},
        {"code": "SL", "name": "Sick Leave", "days": 10},
        {"code": "MAT", "name": "Maternity Leave", "days": 60},
        {"code": "HAJ", "name": "Hajj Leave", "days": 30},
        {"code": "EMR", "name": "Emergency Leave", "days": 3},
    ]

    for lt in leave_types:
        LeaveType.objects.get_or_create(
            name=lt["name"],
            defaults={
                "code": lt["code"],
                "days_allowed": lt["days"],
            },
        )
    print(f"✓ {len(leave_types)} Leave Types created/exist")


def create_holidays():
    """Create holidays"""
    current_year = datetime.now().year
    holidays = [
        {"date": datetime(current_year, 1, 1).date(), "name": "New Year Day"},
        {"date": datetime(current_year, 4, 15).date(), "name": "Eid Al-Fitr"},
        {"date": datetime(current_year, 6, 15).date(), "name": "Arafat Day"},
        {"date": datetime(current_year, 6, 16).date(), "name": "Eid Al-Adha"},
        {"date": datetime(current_year, 11, 18).date(), "name": "Oman National Day"},
    ]

    for holiday in holidays:
        Holiday.objects.get_or_create(
            holiday_name=holiday["name"],
            holiday_date=holiday["date"],
        )
    print(f"✓ {len(holidays)} Holidays created/exist")


def create_leave_requests(employees):
    """Create leave requests"""
    today = datetime.now().date()
    leave_type = LeaveType.objects.filter(name="Annual Leave").first()

    for idx, emp in enumerate(employees[:3]):
        start_date = today + timedelta(days=10 + idx * 5)
        end_date = start_date + timedelta(days=3)

        LeaveRequest.objects.get_or_create(
            employee_id=emp.id,
            start_date=start_date,
            defaults={
                "end_date": end_date,
                "leave_type": leave_type,
                "reason": f"Vacation plan for {emp.first_name}",
                "status": "approved",
            },
        )

    print(f"✓ {len(employees[:3])} Leave Requests created/exist")


def create_attendance_records(employees):
    """Create attendance records"""
    today = datetime.now().date()
    shift = EmployeeShift.objects.filter(shift_name="Morning Shift").first()

    for emp in employees[:3]:
        for i in range(5):
            date = today - timedelta(days=i)
            Attendance.objects.get_or_create(
                employee_id=emp.id,
                attendance_date=date,
                defaults={
                    "work_type_id": 1,
                    "shift_id": shift.id if shift else None,
                    "attendance_status": "present",
                },
            )

    print(
        f"✓ Attendance records created/exist for {len(employees[:3])} employees (last 5 days)"
    )


def create_performance_ratings(employees):
    """Create performance ratings"""
    for emp in employees[:2]:
        PerformanceRating.objects.get_or_create(
            employee_id=emp.id,
            defaults={
                "performance_rating": 4,
                "overall_competency": 4,
                "collaboration": 5,
                "innovation": 4,
                "customer_focus": 5,
            },
        )

    print(f"✓ Performance Ratings created/exist for {len(employees[:2])} employees")


def create_objectives(employees):
    """Create objectives"""
    for emp in employees[:2]:
        objective, created = Objective.objects.get_or_create(
            employee_id=emp.id,
            defaults={
                "objective_title": f"Complete {emp.first_name}'s Q1 Goals",
                "description": "Achieve quarterly objectives",
                "start_date": datetime.now().date(),
                "end_date": datetime.now().date() + timedelta(days=90),
            },
        )

        if created:
            # Create key results
            KeyResult.objects.create(
                objective=objective,
                key_result="Increase productivity by 25%",
                target_value=25,
                current_value=15,
            )

    print(
        f"✓ Objectives & Key Results created/exist for {len(employees[:2])} employees"
    )


def create_recruitment_data():
    """Create recruitment pipeline"""
    job_title = "Senior Software Engineer"
    recruitment, _ = Recruitment.objects.get_or_create(
        job_title=job_title,
        defaults={
            "description": "Looking for experienced senior engineer",
            "open_positions": 2,
            "closed_positions": 1,
            "is_published": True,
        },
    )

    # Create stages
    stages = ["Applied", "Shortlisted", "InterviewScheduled", "Offered"]
    for stage in stages:
        Stage.objects.get_or_create(
            stage_title=stage,
            recruitment_id=recruitment.id,
        )

    # Create candidates
    candidates_data = [
        {
            "name": "Michael Brown",
            "email": "michael@test.com",
            "phone": "+968-9245-1111",
        },
        {"name": "Lisa Park", "email": "lisa@test.com", "phone": "+968-9256-2222"},
        {"name": "David Chen", "email": "david@test.com", "phone": "+968-9267-3333"},
    ]

    for cand_data in candidates_data:
        Candidate.objects.get_or_create(
            name=cand_data["name"],
            email=cand_data["email"],
            defaults={
                "phone": cand_data["phone"],
                "recruitment_id": recruitment.id,
            },
        )

    print(
        f"✓ Recruitment Pipeline created/exists with {len(candidates_data)} candidates"
    )


def create_payroll_data(employees):
    """Create payroll allowances and deductions"""
    # Create allowances
    allowances_data = [
        {"name": "Basic Salary", "type": "fixed", "amount": 5000},
        {"name": "House Rent Allowance", "type": "fixed", "amount": 1500},
        {"name": "Dearness Allowance", "type": "fixed", "amount": 500},
    ]

    for allowance in allowances_data:
        Allowance.objects.get_or_create(
            name=allowance["name"],
            defaults={
                "is_fixed": True,
                "amount": allowance["amount"],
            },
        )

    # Create deductions
    deductions_data = [
        {"name": "Income Tax", "type": "percentage", "amount": 10},
        {"name": "Social Insurance", "type": "percentage", "amount": 5},
        {"name": "Health Insurance", "type": "fixed", "amount": 100},
    ]

    for deduction in deductions_data:
        Deduction.objects.get_or_create(
            name=deduction["name"],
            defaults={
                "is_fixed": deduction["type"] == "fixed",
                "amount": deduction["amount"],
            },
        )

    # Create payslips
    current_month = datetime.now().replace(day=1)
    for emp in employees[:2]:
        Payslip.objects.get_or_create(
            employee_id=emp.id,
            start_date=current_month,
            defaults={
                "end_date": current_month + timedelta(days=30),
                "basic_pay": 5000,
                "gross_pay": 7000,
                "net_pay": 6050,
                "status": "computed",
            },
        )

    print("✓ Payroll Allowances, Deductions & Payslips created/exist")

    
    
    

def main():
    print("\n" + "=" * 60)
    print("HCMS DUMMY DATA POPULATION")
    print("=" * 60 + "\n")

    try:
        create_companies()
        create_departments()
        create_job_positions()
        create_shifts()
        employees = create_users_and_employees()
        create_leave_types()
        create_holidays()
        create_leave_requests(employees)
        create_attendance_records(employees)
        create_performance_ratings(employees)
        create_objectives(employees)
        create_recruitment_data()
        create_payroll_data(employees)

        print("\n" + "=" * 60)
        print("✅ ALL DUMMY DATA POPULATED SUCCESSFULLY!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
