"""
Data migration: create / repair the demo HR account on every deploy.

Idempotent — `get_or_create` + a final password reset means re-running migrate
on an existing DB simply heals the row and resets the password to the demo
value. Cloud Run deploys run `manage.py migrate --noinput` as part of the
release step, so this provisions the account on production automatically.

Username:  hr@fits.com
Password:  Hr@fits123

Implementation notes
--------------------
- We use ``apps.get_model("auth", "User")`` (historical model) instead of
  ``django.contrib.auth.models.User``. The live User class is monkey-patched
  in base/models.py to expose an ``is_new_employee`` column that has NO
  corresponding migration, so on a fresh DB the live model's queries SELECT
  a column that doesn't exist yet and crash. The historical model only
  knows about the columns Django itself created, so it's safe.
- ``make_password`` is used directly because historical models don't have
  ``set_password()``.
- The HRUser row creation lives behind ``try`` so the migration tolerates
  cases where the HRUser table is missing or the row already exists.
"""

from django.contrib.auth.hashers import make_password
from django.db import migrations


HR_USERNAME = "hr@fits.com"
HR_PASSWORD = "Hr@fits123"


def seed_hr_user(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Employee = apps.get_model("employee", "Employee")
    EmployeeWorkInformation = apps.get_model("employee", "EmployeeWorkInformation")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    hashed = make_password(HR_PASSWORD)

    user, _ = User.objects.get_or_create(
        username=HR_USERNAME,
        defaults={
            "email": HR_USERNAME,
            "first_name": "HR",
            "last_name": "Manager",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "password": hashed,
        },
    )
    # Reset on every run so credentials stay predictable.
    user.email = HR_USERNAME
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.password = hashed
    user.save()

    emp, _ = Employee.objects.get_or_create(
        email=HR_USERNAME,
        defaults={
            "employee_user_id": user,
            "employee_first_name": "HR",
            "employee_last_name": "Manager",
            "phone": "+96890000099",
            "is_active": True,
        },
    )
    if emp.employee_user_id_id != user.id:
        emp.employee_user_id = user
        emp.save(update_fields=["employee_user_id"])
    EmployeeWorkInformation.objects.get_or_create(employee_id=emp)

    # view_offerletter permission (drives _resolve_shared_hr + the
    # @permission_required guards on the letters views).
    try:
        ct = ContentType.objects.get(app_label="recruitment", model="offerletter")
        perm = Permission.objects.get(content_type=ct, codename="view_offerletter")
        user.user_permissions.add(perm)
    except (Permission.DoesNotExist, ContentType.DoesNotExist):
        # Permission may not exist yet on a partial migration run; skip safely.
        pass

    # HRUser row drives the "see everything on Received Recruitments" branch
    # plus the publish-to-careers controls.
    try:
        HRUser = apps.get_model("base", "HRUser")
        HRUser.objects.get_or_create(employee=emp, defaults={"is_hr_staff": True})
    except Exception:
        pass


def noop_reverse(apps, schema_editor):
    # Leaving the user / employee in place on reverse is intentional —
    # rolling back a deploy should NOT delete the HR account.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0020_manpower_query_fields"),
        ("employee", "0001_candidate_perf_indexes"),
        ("base", "0001_candidate_perf_indexes"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(seed_hr_user, noop_reverse),
    ]
