"""
Seed (or repair) the demo HR account: hr@fits.com / Hr@fits123.

Idempotent — safe to run multiple times. Resets the password every run so the
credentials stay predictable for demos.

Usage:
    python manage.py seed_hr_user
"""

from django.contrib.auth.models import Permission, User
from django.core.management.base import BaseCommand
from django.db import transaction


HR_USERNAME = "hr@fits.com"
HR_PASSWORD = "Hr@fits123"


class Command(BaseCommand):
    help = "Create / repair the hr@fits.com demo HR account."

    @transaction.atomic
    def handle(self, *args, **options):
        from employee.models import Employee, EmployeeWorkInformation

        u, created = User.objects.get_or_create(
            username=HR_USERNAME,
            defaults={
                "email": HR_USERNAME,
                "first_name": "HR",
                "last_name": "Manager",
                "is_active": True,
            },
        )
        u.set_password(HR_PASSWORD)
        u.email = HR_USERNAME
        u.is_active = True
        u.is_staff = True
        u.is_superuser = True
        u.save()
        self.stdout.write(
            f"  {'created' if created else 'updated'} user: {HR_USERNAME}"
        )

        emp, e_created = Employee.objects.get_or_create(
            email=HR_USERNAME,
            defaults={
                "employee_user_id": u,
                "employee_first_name": "HR",
                "employee_last_name": "Manager",
                "phone": "+96890000099",
                "is_active": True,
            },
        )
        if emp.employee_user_id_id != u.id:
            emp.employee_user_id = u
            emp.save(update_fields=["employee_user_id"])
        EmployeeWorkInformation.objects.get_or_create(employee_id=emp)
        self.stdout.write(
            f"  {'created' if e_created else 'updated'} employee record"
        )

        # Permissions
        try:
            perm = Permission.objects.get(
                content_type__app_label="recruitment",
                codename="view_offerletter",
            )
            u.user_permissions.add(perm)
            self.stdout.write("  granted recruitment.view_offerletter")
        except Permission.DoesNotExist:
            pass

        # HRUser row drives "see everything on Received Recruitments" + careers publish
        try:
            from base.models import HRUser
            HRUser.objects.get_or_create(
                employee=emp, defaults={"is_hr_staff": True}
            )
            self.stdout.write("  HRUser.is_hr_staff = True")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  HRUser unavailable: {exc}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Login: {HR_USERNAME} / {HR_PASSWORD}"
        ))
