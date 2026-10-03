"""
employee/signals.py

Auto-record salary history when EmployeeWorkInformation.basic_salary changes.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(pre_save, sender="employee.EmployeeWorkInformation")
def record_salary_history_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_salary = old.basic_salary
    new_salary = instance.basic_salary
    if old_salary and new_salary and old_salary != new_salary:
        from employee.models import EmployeeSalaryHistory
        EmployeeSalaryHistory.objects.create(
            employee=instance.employee_id,
            effective_date=timezone.now().date(),
            basic_salary=new_salary,
            increment_reason="Salary updated",
        )
