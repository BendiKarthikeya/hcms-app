from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
import random

from base.models import Company, Department, JobPosition
from employee.models import Employee


class Command(BaseCommand):
    help = "Seed demo data for all modules based on existing employees"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Number of demo records to create per module (default: 20)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        limit = options.get("limit", 20)

        company, _ = Company.objects.get_or_create(
            company="DemoCo",
            defaults={
                "hq": True,
                "address": "1 Demo Street",
                "country": "Oman",
                "state": "Muscat",
                "city": "Muscat",
                "zip": "0000",
            },
        )

        # Prefer existing 'Management' department if available, else use first existing department
        if Department.objects.filter(department="Management").exists():
            dept = Department.objects.filter(department="Management").first()
        elif Department.objects.exists():
            dept = Department.objects.first()
        else:
            try:
                dept = Department.objects.create(department="Management")
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        "Unable to create Department automatically: %s" % e
                    )
                )
                return
        if company not in dept.company_id.all():
            dept.company_id.add(company)

        jobpos, _ = JobPosition.objects.get_or_create(
            job_position="General Manager", defaults={"department_id": dept}
        )
        if company not in jobpos.company_id.all():
            jobpos.company_id.add(company)

        # Get first 20 employees for seeding
        employees = list(Employee.objects.all()[:limit])
        if not employees:
            self.stderr.write(self.style.ERROR("No employees found in database"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(employees)} employees"))

        # Seed Onboarding
        self.seed_onboarding_data(employees, company)

        # Seed Employee additional data
        self.seed_employee_data(employees)

        # Seed Attendance
        self.seed_attendance_data(employees)

        # Seed Talent & Succession
        self.seed_talent_data(employees, dept, jobpos, company)

        # Seed Expenses
        self.seed_expense_data(employees, company)

        # Seed Leave
        self.seed_leave_data(employees)

        # Seed Asset
        self.seed_asset_data(employees)

        # Seed Project
        self.seed_project_data(employees)

        # Seed PMS (Performance)
        self.seed_pms_data(employees)

        self.stdout.write(self.style.SUCCESS("✅ All demo data seeded successfully!"))

    def seed_onboarding_data(self, employees, company):
        """Seed onboarding task data"""
        self.stdout.write("Seeding Onboarding data...")
        try:
            from onboarding.models import OnboardingTask
            from recruitment.models import Recruitment

            # Get or create a recruitment
            recruitments = Recruitment.objects.all()
            if not recruitments:
                self.stdout.write('  ℹ No recruitment found, skipping onboarding')
                return

            recruitment = recruitments.first()
            stages = recruitment.onboarding_stage.all()
            if not stages:
                self.stdout.write('  ℹ No onboarding stages found')
                return

            stage = stages.first()
            task_count = 0

            task_titles = [
                "Equipment Setup",
                "IT Access Setup",
                "Team Introduction",
                "Training Sessions",
                "Documentation Review",
            ]
            for task_title in task_titles:
                task, created = OnboardingTask.objects.get_or_create(
                    task_title=task_title,
                    stage_id=stage,
                    defaults={
                        "stage_id": stage,
                    },
                )
                if created:
                    # Add task managers
                    sample_employees = employees[:3]
                    task.employee_id.set(sample_employees)
                    task_count += 1

            self.stdout.write(f"  ✓ Created {task_count} onboarding tasks")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_employee_data(self, employees):
        """Add employee notes and additional info"""
        self.stdout.write("Seeding Employee Notes & Info...")
        try:
            from employee.models import EmployeeNote

            note_count = 0
            for emp in employees[:15]:
                note, created = EmployeeNote.objects.get_or_create(
                    employee_id=emp,
                    description=f"Performance note for {emp.get_full_name()}: {random.choice(['High performer', 'Team player', 'Quick learner', 'Reliable', 'Creative thinker'])}",
                    defaults={
                        "updated_by": emp,
                    },
                )
                if created:
                    note_count += 1

            self.stdout.write(f"  ✓ Created {note_count} employee notes")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_attendance_data(self, employees):
        """Seed attendance data with proper model handling"""
        self.stdout.write("Seeding Attendance data...")
        try:
            from attendance.models import Attendance

            attendance_count = 0
            today = date.today()

            # Use raw SQL to insert attendance records to avoid complex model validations

            for emp in employees[:12]:
                # Create last 15 days of attendance
                for day_offset in range(1, 16):
                    att_date = today - timedelta(days=day_offset)

                    # Skip weekends (Saturday=5, Sunday=6)
                    if att_date.weekday() >= 5:
                        continue

                    # Check if attendance already exists
                    if Attendance.objects.filter(
                        employee_id=emp, attendance_date=att_date
                    ).exists():
                        continue

                    try:
                        work_type = (
                            emp.employee_work_info.work_type_id
                            if hasattr(emp, "employee_work_info")
                            else None
                        )
                        shift = (
                            emp.employee_work_info.shift_id
                            if hasattr(emp, "employee_work_info")
                            else None
                        )

                        in_hour = random.randint(8, 10)
                        in_min = random.randint(0, 59)
                        out_hour = random.randint(16, 18)
                        out_min = random.randint(0, 59)

                        # Create attendance using raw INSERT to bypass model validations
                        Attendance.objects.create(
                            employee_id=emp,
                            attendance_date=att_date,
                            work_type_id=work_type,
                            shift_id=shift,
                            attendance_clock_in=f"{in_hour:02d}:{in_min:02d}",
                            attendance_clock_out=f"{out_hour:02d}:{out_min:02d}",
                        )
                        attendance_count += 1
                    except Exception:
                        # Skip this record and continue
                        continue

            self.stdout.write(f"  ✓ Created {attendance_count} attendance records")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_talent_data(self, employees, dept, jobpos, company):
        """Seed talent management data"""
        self.stdout.write("Seeding Talent & Succession data...")
        try:
            from talent.models import TalentProfile, CriticalRole, SuccessionPlan

            for i, emp in enumerate(employees[:5]):
                tp, created = TalentProfile.objects.get_or_create(
                    employee=emp,
                    defaults={
                        "performance_level": random.choice(["high", "medium", "low"]),
                        "potential_level": random.choice(["high", "medium", "low"]),
                        "career_aspirations": f"Advance to {random.choice(['Manager', 'Senior Manager', 'Director'])}",
                        "mobility_willingness": random.choice([True, False]),
                        "readiness_level": random.choice(
                            [
                                "not_ready",
                                "ready_3_5_years",
                                "ready_1_2_years",
                                "ready_now",
                            ]
                        ),
                        "development_needs": f"{random.choice(['Leadership', 'Technical', 'Management'])} training",
                        "last_assessment_date": date.today()
                        - timedelta(days=random.randint(10, 90)),
                        "next_assessment_date": date.today()
                        + timedelta(days=random.randint(100, 365)),
                    },
                )
                if created:
                    self.stdout.write(f"  ✓ TalentProfile: {emp.employee_first_name}")

            # Create succession plans
            cr, _ = CriticalRole.objects.get_or_create(
                department=dept,
                job_position=jobpos,
                role_name="General Manager",
                defaults={
                    "description": "Oversees operations and strategy",
                    "criticality_level": "critical",
                    "vacancy_risk": "high",
                    "succession_required": True,
                    "company": company,
                },
            )

            if employees:
                sp, created = SuccessionPlan.objects.get_or_create(
                    critical_role=cr,
                    primary_successor=employees[0],
                    defaults={
                        "secondary_successor": employees[1]
                        if len(employees) > 1
                        else None,
                        "readiness_level": "high",
                        "estimated_timeline_months": random.randint(6, 24),
                        "development_plan": f"{random.choice(['Mentorship', 'Training', 'Coaching'])} + leadership course",
                        "status": "active",
                    },
                )
                if created:
                    
                    self.stdout.write('  ✓ SuccessionPlan created')
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_expense_data(self, employees, company):
        """Seed expense data"""
        self.stdout.write("Seeding Expense data...")
        try:
            from expenses.models import ExpenseCategory, ExpenseClaim

            categories = ["Travel", "Meals", "Equipment", "Training", "Office Supplies"]

            for category_name in categories:
                cat, _ = ExpenseCategory.objects.get_or_create(
                    name=category_name,
                    defaults={
                        "description": f"{category_name} related expenses",
                        "company": company,
                    },
                )

            # Create expense claims
            expense_count = 0
            for emp in employees[:10]:
                cat = ExpenseCategory.objects.filter(company=company).first()
                if not cat:
                    cat, _ = ExpenseCategory.objects.get_or_create(
                        name="General",
                        defaults={
                            "description": "General expenses",
                            "company": company,
                        },
                    )

                ec, created = ExpenseClaim.objects.get_or_create(
                    employee=emp,
                    description=f"{emp.employee_first_name} - {random.choice(['Conference', 'Meeting', 'Travel'])}: Day {random.randint(1, 30)}",
                    expense_date=date.today() - timedelta(days=random.randint(1, 30)),
                    defaults={
                        "category": cat,
                        "amount": random.uniform(50, 1000),
                        "currency": "OMR",
                        "exchange_rate": 1.0,
                        "local_amount": random.uniform(50, 1000),
                        "status": random.choice(["submitted", "approved", "rejected"]),
                    },
                )
                if created:
                    expense_count += 1

            self.stdout.write(f"  ✓ Created {expense_count} expense claims")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_leave_data(self, employees):
        """Seed leave data"""
        self.stdout.write("Seeding Leave data...")
        try:
            from leave.models import LeaveRequest, LeaveType

            leave_types = LeaveType.objects.all()
            if not leave_types:
                LeaveType.objects.get_or_create(
                    name="Annual Leave", defaults={"count": 20}
                )
                leave_types = LeaveType.objects.all()

            leave_count = 0
            for emp in employees[:12]:
                for i in range(2):
                    leave_type = random.choice(leave_types)
                    start = date.today() + timedelta(days=random.randint(5, 30))

                    lr, created = LeaveRequest.objects.get_or_create(
                        employee_id=emp,
                        leave_type_id=leave_type,
                        start_date=start,
                        end_date=start + timedelta(days=random.randint(1, 5)),
                        defaults={
                            "leave_comments": f"Leave request for {emp.employee_first_name}",
                            "status": random.choice(
                                ["pending_approval", "approved", "rejected"]
                            ),
                        },
                    )
                    if created:
                        leave_count += 1

            self.stdout.write(f"  ✓ Created {leave_count} leave requests")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_asset_data(self, employees):
        """Seed asset data"""
        self.stdout.write("Seeding Asset data...")
        try:
            from asset.models import Asset, AssetCategory

            categories = ["Laptop", "Monitor", "Phone", "Tablet", "Printer"]
            asset_count = 0

            for category_name in categories:
                cat, _ = AssetCategory.objects.get_or_create(
                    asset_category_name=category_name
                )

            for i, emp in enumerate(employees[:12]):
                category = AssetCategory.objects.all().first()
                if not category:
                    category, _ = AssetCategory.objects.get_or_create(
                        asset_category_name="Equipment"
                    )

                asset, created = Asset.objects.get_or_create(
                    asset_name=f"{random.choice(['Dell', 'HP', 'Apple', 'Samsung'])} {random.choice(['Laptop', 'Monitor', 'Phone'])} - {emp.badge_id or emp.id}",
                    asset_category_id=category,
                    defaults={
                        "asset_description": f"Asset assigned to {emp.get_full_name()}",
                        "asset_purchase_date": date.today()
                        - timedelta(days=random.randint(30, 365)),
                        "asset_purchase_cost": random.randint(500, 3000),
                    },
                )
                if created:
                    asset_count += 1

            self.stdout.write(f"  ✓ Created {asset_count} assets")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_project_data(self, employees):
        """Seed project data"""
        self.stdout.write("Seeding Project data...")
        try:
            from project.models import Project

            project_count = 0
            project_names = [
                "Mobile App Development",
                "Website Redesign",
                "Data Migration",
                "Cloud Migration",
                "API Integration",
            ]

            for project_name in project_names:
                proj, created = Project.objects.get_or_create(
                    title=project_name,
                    defaults={
                        "description": f"Demo {project_name} project",
                        "start_date": date.today()
                        - timedelta(days=random.randint(10, 90)),
                        "end_date": date.today()
                        + timedelta(days=random.randint(30, 180)),
                        "status": random.choice(["InProgress", "OnHold", "Completed"]),
                    },
                )
                if created:
                    project_count += 1
                    # Add team members
                    team = random.sample(employees, min(3, len(employees)))
                    proj.managers.set(team)

            self.stdout.write(f"  ✓ Created {project_count} projects")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")

    def seed_pms_data(self, employees):
        """Seed Performance Management System data"""
        self.stdout.write("Seeding PMS (Performance) data...")
        try:
            from pms.models import Objective, EmployeeObjective

            objective_count = 0
            objectives = [
                "Improve code quality",
                "Increase productivity",
                "Enhance customer satisfaction",
                "Reduce defects",
                "Improve team collaboration",
            ]

            for emp in employees[:10]:
                for obj_title in objectives[:2]:
                    obj, _ = Objective.objects.get_or_create(
                        title=obj_title,
                        defaults={
                            "description": f"{obj_title} for improved performance",
                        },
                    )

                    emp_obj, created = EmployeeObjective.objects.get_or_create(
                        employee_id=emp,
                        objective_id=obj,
                        defaults={
                            "start_date": date.today() - timedelta(days=30),
                            "end_date": date.today() + timedelta(days=150),
                        },
                    )
                    if created:
                        objective_count += 1

            self.stdout.write(f"  ✓ Created {objective_count} employee objectives")
        except Exception as e:
            self.stderr.write(f"  ✗ Error: {str(e)[:100]}")
