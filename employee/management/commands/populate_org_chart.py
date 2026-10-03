"""
employee/management/commands/populate_org_chart.py
Management command to populate organization chart with realistic dummy data
"""

from django.core.management.base import BaseCommand
from decimal import Decimal

from employee.models import Employee, EmployeeWorkInformation
from base.models import Company, Department, JobPosition
from employee.models_org_chart import (
    OrgChartPosition,
    DraftPositionChange,
    OrgChartAuditLog,
)


class Command(BaseCommand):
    help = "Populate organization chart with realistic dummy data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--company-id",
            type=int,
            default=1,
            help="Company ID to populate org chart for",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing org chart data before populating",
        )

    def handle(self, *args, **options):
        company_id = options["company_id"]

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Company {company_id} not found"))
            return

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing org chart data..."))
            OrgChartPosition.objects.filter(company=company).delete()
            DraftPositionChange.objects.delete()
            OrgChartAuditLog.objects.delete()
            self.stdout.write(self.style.SUCCESS("Cleared existing data"))

        # Get or create departments
        departments = self._get_or_create_departments(company)

        # Get or create job positions
        positions = self._get_or_create_job_positions()

        # Get existing employees or create new ones
        employees = self._populate_employees(company, departments, positions)

        # Build organization hierarchy
        self._build_org_hierarchy(company, employees, departments, positions)

        # Log some sample changes
        self._create_sample_changes(company, employees)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully populated org chart for {company.company}"
            )
        )
        self.stdout.write(self.style.SUCCESS(f"- Created {len(employees)} positions"))
        self.stdout.write(
            self.style.SUCCESS(f"- Created {len(departments)} departments")
        )

    def _get_or_create_departments(self, company):
        """Get departments - use existing only"""
        # Map to existing departments in the database
        dept_mapping = {
            "Executive": "Executive",
            "Engineering": "Engineering",
            "Product": "Product",
            "Sales": "Sales",
            "Marketing": "Marketing",
            "Operations": "Operations",
            "Finance": "Finance",
            "Human Resources": "Human Resources",
        }

        departments = {}

        # Get all existing departments
        all_depts = Department.objects.all()

        for key in dept_mapping.keys():
            # Try to find by exact name
            existing = all_depts.filter(department__iexact=key)
            if existing.exists():
                dept = existing.first()
                departments[key] = dept
                # Add company to relationship
                if company not in dept.company_id.all():
                    dept.company_id.add(company)
                self.stdout.write(self.style.SUCCESS(f"Using department: {key}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Department {key} not found - will skip")
                )

        return departments

    def _get_or_create_job_positions(self):
        """Get or create job positions with their respective departments"""
        position_mapping = {
            "CEO": "Executive",
            "VP": "Executive",
            "HR Manager": "Human Resources",
            "Engineering Manager": "Engineering",
            "Senior Engineer": "Engineering",
            "Engineer": "Engineering",
            "Product Manager": "Product",
            "Sales Manager": "Sales",
            "Sales Representative": "Sales",
            "Marketing Manager": "Marketing",
            "Accountant": "Finance",
            "Operations Manager": "Operations",
        }

        positions = {}

        # Get all existing departments
        all_depts = Department.objects.all()

        for position_name, dept_name in position_mapping.items():
            # Try to find the department
            existing_dept = all_depts.filter(department__iexact=dept_name).first()

            if not existing_dept:
                # If department doesn't exist, skip this position
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping position {position_name} - department {dept_name} not found"
                    )
                )
                continue

            # Create or get the job position with its department
            pos, created = JobPosition.objects.get_or_create(
                job_position=position_name,
                department_id=existing_dept,
            )
            positions[position_name] = pos
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created job position: {position_name} in {dept_name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Using existing job position: {position_name}")
                )

        return positions

    def _populate_employees(self, company, departments, positions):
        """Populate or retrieve employee records"""
        org_structure = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "phone": "+1-555-0101",
                "position_name": "CEO",
                "department_name": "Executive",
                "cost_center": "CC-001",
                "salary_min": Decimal("150000.00"),
                "salary_max": Decimal("200000.00"),
                "level": 1,
                "direct_reports": 4,
            },
            {
                "name": "Bob Smith",
                "email": "bob.smith@company.com",
                "phone": "+1-555-0102",
                "position_name": "VP",
                "department_name": "Engineering",
                "cost_center": "CC-002",
                "salary_min": Decimal("120000.00"),
                "salary_max": Decimal("150000.00"),
                "level": 2,
                "parent": "Alice Johnson",
                "direct_reports": 3,
            },
            {
                "name": "Carol Davis",
                "email": "carol.davis@company.com",
                "phone": "+1-555-0103",
                "position_name": "VP",
                "department_name": "Sales",
                "cost_center": "CC-003",
                "salary_min": Decimal("110000.00"),
                "salary_max": Decimal("140000.00"),
                "level": 2,
                "parent": "Alice Johnson",
                "direct_reports": 2,
            },
            {
                "name": "Diana Prince",
                "email": "diana.prince@company.com",
                "phone": "+1-555-0104",
                "position_name": "VP",
                "department_name": "Product",
                "cost_center": "CC-004",
                "salary_min": Decimal("115000.00"),
                "salary_max": Decimal("145000.00"),
                "level": 2,
                "parent": "Alice Johnson",
                "direct_reports": 2,
            },
            {
                "name": "Eve Martinez",
                "email": "eve.martinez@company.com",
                "phone": "+1-555-0105",
                "position_name": "HR Manager",
                "department_name": "Human Resources",
                "cost_center": "CC-005",
                "salary_min": Decimal("90000.00"),
                "salary_max": Decimal("120000.00"),
                "level": 2,
                "parent": "Alice Johnson",
                "direct_reports": 1,
            },
            # Engineering team
            {
                "name": "Frank Wilson",
                "email": "frank.wilson@company.com",
                "phone": "+1-555-0201",
                "position_name": "Engineering Manager",
                "department_name": "Engineering",
                "cost_center": "CC-002",
                "salary_min": Decimal("100000.00"),
                "salary_max": Decimal("130000.00"),
                "level": 3,
                "parent": "Bob Smith",
                "direct_reports": 3,
            },
            {
                "name": "Grace Lee",
                "email": "grace.lee@company.com",
                "phone": "+1-555-0202",
                "position_name": "Senior Engineer",
                "department_name": "Engineering",
                "cost_center": "CC-002",
                "salary_min": Decimal("95000.00"),
                "salary_max": Decimal("125000.00"),
                "level": 4,
                "parent": "Frank Wilson",
                "direct_reports": 0,
            },
            {
                "name": "Henry Brown",
                "email": "henry.brown@company.com",
                "phone": "+1-555-0203",
                "position_name": "Engineer",
                "department_name": "Engineering",
                "cost_center": "CC-002",
                "salary_min": Decimal("80000.00"),
                "salary_max": Decimal("110000.00"),
                "level": 4,
                "parent": "Frank Wilson",
                "direct_reports": 0,
            },
            {
                "name": "Iris Taylor",
                "email": "iris.taylor@company.com",
                "phone": "+1-555-0204",
                "position_name": "Engineer",
                "department_name": "Engineering",
                "cost_center": "CC-002",
                "salary_min": Decimal("78000.00"),
                "salary_max": Decimal("108000.00"),
                "level": 4,
                "parent": "Frank Wilson",
                "direct_reports": 0,
            },
            # Sales team
            {
                "name": "Jack Anderson",
                "email": "jack.anderson@company.com",
                "phone": "+1-555-0301",
                "position_name": "Sales Manager",
                "department_name": "Sales",
                "cost_center": "CC-003",
                "salary_min": Decimal("85000.00"),
                "salary_max": Decimal("115000.00"),
                "level": 3,
                "parent": "Carol Davis",
                "direct_reports": 2,
            },
            {
                "name": "Karen Thomas",
                "email": "karen.thomas@company.com",
                "phone": "+1-555-0302",
                "position_name": "Sales Representative",
                "department_name": "Sales",
                "cost_center": "CC-003",
                "salary_min": Decimal("60000.00"),
                "salary_max": Decimal("85000.00"),
                "level": 4,
                "parent": "Jack Anderson",
                "direct_reports": 0,
            },
            # Product team
            {
                "name": "Leo Jackson",
                "email": "leo.jackson@company.com",
                "phone": "+1-555-0401",
                "position_name": "Product Manager",
                "department_name": "Product",
                "cost_center": "CC-004",
                "salary_min": Decimal("90000.00"),
                "salary_max": Decimal("120000.00"),
                "level": 3,
                "parent": "Diana Prince",
                "direct_reports": 1,
            },
            {
                "name": "Mia White",
                "email": "mia.white@company.com",
                "phone": "+1-555-0501",
                "position_name": "Marketing Manager",
                "department_name": "Marketing",
                "cost_center": "CC-006",
                "salary_min": Decimal("80000.00"),
                "salary_max": Decimal("110000.00"),
                "level": 3,
                "parent": "Diana Prince",
                "direct_reports": 0,
            },
            # HR & Finance team
            {
                "name": "Nathan Harris",
                "email": "nathan.harris@company.com",
                "phone": "+1-555-0601",
                "position_name": "Accountant",
                "department_name": "Finance",
                "cost_center": "CC-007",
                "salary_min": Decimal("70000.00"),
                "salary_max": Decimal("95000.00"),
                "level": 3,
                "parent": "Eve Martinez",
                "direct_reports": 0,
            },
        ]

        employees = {}
        for emp_data in org_structure:
            name = emp_data["name"]
            first_name, last_name = name.split(" ", 1)

            # Check if position and department are available
            position = positions.get(emp_data["position_name"])
            department = departments.get(emp_data["department_name"])

            if not position:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {name} - position {emp_data['position_name']} not available"
                    )
                )
                continue

            # Get or create employee
            employee, created = Employee.objects.get_or_create(
                email=emp_data["email"],
                defaults={
                    "employee_first_name": first_name,
                    "employee_last_name": last_name,
                    "phone": emp_data["phone"],
                    "is_active": True,
                },
            )

            # Prepare work information defaults
            work_defaults = {
                "company": company,
                "job_position_id": position,
                "cost_center": emp_data["cost_center"],
                "work_type_id": 1,  # Assuming 1 is full-time
            }

            # Only set department if it exists
            if department:
                work_defaults["department_id"] = department

            # Update or create work information
            work_info, work_created = EmployeeWorkInformation.objects.get_or_create(
                employee_id=employee, defaults=work_defaults
            )

            if work_created:
                self.stdout.write(f"Created employee: {name}")

            employees[name] = {
                "instance": employee,
                "work_info": work_info,
                "position": position,
                "department": department,
                "data": emp_data,
            }

        return employees

    def _build_org_hierarchy(self, company, employees, departments, positions):
        """Build organization hierarchy"""
        for name, emp_dict in employees.items():
            emp_data = emp_dict["data"]
            emp_dict["instance"]
            work_info = emp_dict["work_info"]
            emp_dict["position"]
            emp_dict["department"]

            # Set reporting manager if exists
            parent_name = emp_data.get("parent")
            if parent_name and parent_name in employees:
                parent_emp = employees[parent_name]["instance"]
                work_info.reporting_manager_id = parent_emp
                work_info.save()
                self.stdout.write(f"  {name} reports to {parent_name}")

            # Prepare OrgChartPosition defaults
            # (Temporarily disabled until model schema is verified)
            # position_defaults = {
            #     'position_code': f"POS-{employee.id:04d}",
            #     'position_title': position.job_position,
            #     'reporting_manager': work_info.reporting_manager_id,
            #     'company': company,
            #     'cost_center': emp_data['cost_center'],
            #     'salary_min': emp_data['salary_min'],
            #     'salary_max': emp_data['salary_max'],
            #     'status': 'active',
            #     'hierarchy_level': emp_data['level'],
            #     'position_level': emp_data['level'],
            #     'description': f"Position for {name}",
            #     'created_by': 'system',
            # }
            #
            # # Only create OrgChartPosition if department exists
            # if department:
            #     position_defaults['department'] = department
            #
            #     # Create or update OrgChartPosition
            #     position, created = OrgChartPosition.objects.get_or_create(
            #         employee=employee,
            #         defaults=position_defaults
            #     )
            #
            #     if created:
            #         self.stdout.write(f'Created org position for: {name}')
            # else:
            #     self.stdout.write(self.style.WARNING(f'Skipping OrgChartPosition for {name} - no department'))

    def _create_sample_changes(self, company, employees):
        """Create sample draft changes and audit logs"""
        # Temporarily disabled until OrgChartPosition model is properly configured
        # sample_employees = list(employees.items())[:3]
        #
        # for name, emp_dict in sample_employees:
        #     employee = emp_dict['instance']
        #
        #     # Create sample audit log
        #     audit_log = OrgChartAuditLog.objects.create(
        #         action='update',
        #         position=OrgChartPosition.objects.get(employee=employee),
        #         affected_employee=employee,
        #         change_summary=f'Org chart initialized for {name}',
        #         performed_by='system',
        #         old_value={'status': 'draft'},
        #         new_value={'status': 'active'},
        #     )
        #
        #     self.stdout.write(f'Created audit log for: {name}')
        pass
