"""
Advanced Leave & Attendance Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def leave_policy_engine(request):
    """Leave Policy Engine - configure leave types, accrual rules, carryover policies."""
    return render(request, "leave/leave_policy_engine.html")


@login_required
def approval_workflow(request):
    """7-Stage Approval Workflow for leave requests."""
    return render(request, "leave/approval_workflow.html")


@login_required
def biometric_integration(request):
    """Biometric Device Integration management."""
    return render(request, "attendance/biometric_integration.html")


@login_required
def mobile_clock_in(request):
    """Mobile Clock-In/Out management dashboard."""
    return render(request, "attendance/mobile_clock_in.html")


@login_required
def shift_overtime(request):
    """Shift Scheduling & Overtime management."""
    return render(request, "attendance/shift_overtime.html")
