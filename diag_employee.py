"""
Diagnostic script to count queries and time the employee view logic directly.
Run: python diag_employee.py
"""

import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fits.settings")

import django

django.setup()

from django.db import connection, reset_queries
from django.conf import settings

settings.DEBUG = True  # Enable query logging

from employee.filters import EmployeeFilter
from employee.models import Employee
from django.db import models as dj_models
from accessibility.models import DefaultAccessibility

print("=== Diagnosing employee_view query count ===\n")

# --- Step 1: Check filter instantiation cost ---
print("--- Step 1: EmployeeFilter() instantiation ---")
reset_queries()
t0 = time.time()
f = EmployeeFilter()
t1 = time.time()
qs = connection.queries
print(f"  Time: {(t1 - t0) * 1000:.0f}ms, Queries: {len(qs)}")
for q in qs:
    print(f"    {float(q['time']):.3f}s: {q['sql'][:80]}")

# --- Step 2: Employee queryset with prefetch ---
print("\n--- Step 2: Employee queryset with prefetch ---")
reset_queries()
t0 = time.time()
queryset = Employee.objects.select_related(
    "employee_work_info",
    "employee_work_info__reporting_manager_id",
    "employee_work_info__job_position_id",
    "employee_work_info__department_id",
    "employee_work_info__company_id",
    "employee_user_id",
).prefetch_related(
    dj_models.Prefetch(
        "default_accessibility",
        queryset=DefaultAccessibility.objects.filter(feature="profile_edit"),
        to_attr="profile_edit_access",
    )
)
employees_list = list(queryset[:20])  # Fetch first 20
t1 = time.time()
qs = connection.queries
print(f"  Time: {(t1 - t0) * 1000:.0f}ms, Queries: {len(qs)}")
for q in qs:
    print(f"    {float(q['time']):.3f}s: {q['sql'][:100]}")

# --- Step 3: check_online per employee ---
print("\n--- Step 3: check_online for first 10 employees ---")
reset_queries()
t0 = time.time()
for i, emp in enumerate(employees_list[:10]):
    before = len(connection.queries)
    emp.check_online()
    after = len(connection.queries)
    if after > before:
        print(f"  Employee {i}: {after - before} query(s):")
        for q in connection.queries[before:after]:
            print(f"    {float(q['time']):.3f}s: {q['sql'][:120]}")
t1 = time.time()
qs = connection.queries
print(f"  Total Time: {(t1 - t0) * 1000:.0f}ms, Queries: {len(qs)}")

# --- Step 4: edit_accessibility per employee ---
print("\n--- Step 4: edit_accessibility for first 10 employees ---")
reset_queries()
t0 = time.time()
results = []
for emp in employees_list[:10]:
    if hasattr(emp, "profile_edit_access"):
        results.append(bool(emp.profile_edit_access))
    else:
        results.append(
            emp.default_accessibility.filter(feature="profile_edit").exists()
        )
t1 = time.time()
qs = connection.queries
print(f"  Time: {(t1 - t0) * 1000:.0f}ms, Queries: {len(qs)}")

print("\n=== Done ===")
