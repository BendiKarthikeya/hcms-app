"""
Enhanced Leave Request Approval API Views
Location: fits_api/api_views/leave/approval_views.py
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone

from leave.models_enhanced_approvals import (
    ApprovalRequest,
)
from leave.services import ApprovalWorkflowService, ApprovalAnalyticsService
from employee.models import Employee


class ApprovalDashboardView(APIView):
    """
    GET /api/leave/approvals/dashboard/
    Returns approval dashboard for current manager with pending count and analytics.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get pending approvals
        pending_approvals = ApprovalRequest.objects.filter(
            approver=employee, status="pending"
        )

        # Get approval stats
        stats = ApprovalAnalyticsService.get_team_approval_stats(employee)

        # Get urgent items (SLA breached)
        urgent = pending_approvals.filter(sla_deadline__lt=timezone.now()).count()

        # Get escalated items
        escalated = ApprovalRequest.objects.filter(
            escalated_to=employee, status="pending"
        ).count()

        return Response(
            {
                "pending_count": pending_approvals.count(),
                "approved_count": stats["approved"],
                "rejected_count": stats["rejected"],
                "overdue_count": urgent,
                "escalated_to_me": escalated,
                "average_approval_time_hours": stats["average_time"],
                "pending_requests": [
                    {
                        "id": ap.leave_request.id,
                        "employee": str(ap.leave_request.employee_id),
                        "leave_type": str(ap.leave_request.leave_type_id),
                        "start_date": ap.leave_request.start_date.isoformat(),
                        "end_date": ap.leave_request.end_date.isoformat(),
                        "days": ap.leave_request.requested_days,
                        "sla_deadline": ap.sla_deadline.isoformat(),
                        "is_overdue": ap.is_overdue(),
                        "days_until_sla": max(0, ap.days_until_sla_breach()),
                        "sequence": ap.sequence_order,
                    }
                    for ap in pending_approvals[:10]  # Latest 10
                ],
            }
        )


class ApproveLeaveRequestView(APIView):
    """
    POST /api/leave/approvals/<approval_id>/approve/
    Approve a pending leave request.

    Body:
    {
        "comment": "Approved - looks good"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, approval_id):
        try:
            employee = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            approval = ApprovalRequest.objects.get(id=approval_id)
        except ApprovalRequest.DoesNotExist:
            return Response(
                {"error": "Approval request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify user is the approver
        if approval.approver != employee and not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to approve this request"},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = request.data.get("comment", "")

        # Approve
        approval.approve(employee, comment)

        # Process workflow
        service = ApprovalWorkflowService(approval.leave_request)
        service.process_approvals()

        return Response(
            {
                "status": "approved",
                "leave_request": {
                    "id": approval.leave_request.id,
                    "status": approval.leave_request.status,
                    "employee": str(approval.leave_request.employee_id),
                },
            }
        )


class RejectLeaveRequestView(APIView):
    """
    POST /api/leave/approvals/<approval_id>/reject/
    Reject a pending leave request.

    Body:
    {
        "reason": "Cannot approve due to project deadline"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, approval_id):
        try:
            employee = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            approval = ApprovalRequest.objects.get(id=approval_id)
        except ApprovalRequest.DoesNotExist:
            return Response(
                {"error": "Approval request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify user is the approver
        if approval.approver != employee and not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to reject this request"},
                status=status.HTTP_403_FORBIDDEN,
            )

        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"error": "Rejection reason is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reject
        approval.reject(employee, reason)

        # Update leave request status
        approval.leave_request.status = "rejected"
        approval.leave_request.reject_reason = reason
        approval.leave_request.save()

        return Response({"status": "rejected", "reason": reason})


class BulkApproveView(APIView):
    """
    POST /api/leave/approvals/bulk-approve/
    Approve multiple leave requests at once.

    Body:
    {
        "request_ids": [1, 2, 3],
        "comment": "Group approved"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            employee = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        request_ids = request.data.get("request_ids", [])
        if not request_ids:
            return Response(
                {"error": "request_ids is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        service = ApprovalWorkflowService(None)
        approved_count = service.bulk_approve(employee, request_ids)

        return Response(
            {
                "approved_count": approved_count,
                "total_requested": len(request_ids),
                "message": f"Successfully approved {approved_count} requests",
            }
        )


class CreateDelegationView(APIView):
    """
    POST /api/leave/approvals/delegations/
    Create approval delegation for absent manager.

    Body:
    {
        "delegated_to": "emp_id",
        "start_date": "2026-03-20T00:00:00Z",
        "end_date": "2026-03-30T23:59:59Z",
        "reason": "Annual leave",
        "departments": [1, 2]  # Optional
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from_manager = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            to_manager_id = request.data.get("delegated_to")
            to_manager = Employee.objects.get(id=to_manager_id)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Delegated manager not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        reason = request.data.get("reason", "")

        if not all([start_date, end_date]):
            return Response(
                {"error": "start_date and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create delegation
        service = ApprovalWorkflowService(None)
        delegation = service.delegate_approval(
            from_manager, to_manager, start_date, end_date, reason
        )

        return Response(
            {
                "id": delegation.id,
                "from": str(from_manager),
                "to": str(to_manager),
                "start_date": delegation.start_date.isoformat(),
                "end_date": delegation.end_date.isoformat(),
                "status": delegation.status,
            },
            status=status.HTTP_201_CREATED,
        )


class ApprovalOverrideView(APIView):
    """
    POST /api/leave/approvals/<approval_id>/override/
    HR admin can override approval decisions.

    Body:
    {
        "action": "approve",  # or "reject" or "reset"
        "reason": "Exception for critical project work"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, approval_id):
        # Check for HR admin permission
        if not request.user.is_staff:
            return Response(
                {"error": "Only HR admin can override approvals"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            employee = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            approval = ApprovalRequest.objects.get(id=approval_id)
        except ApprovalRequest.DoesNotExist:
            return Response(
                {"error": "Approval request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        action = request.data.get("action")
        reason = request.data.get("reason", "")

        if action not in ["approve", "reject", "reset"]:
            return Response(
                {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not reason:
            return Response(
                {"error": "Reason is required for override"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = ApprovalWorkflowService(approval.leave_request)
            service.override_approval(employee, action, reason)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "status": "override_successful",
                "action": action,
                "leave_request": {
                    "id": approval.leave_request.id,
                    "status": approval.leave_request.status,
                },
            }
        )


class ApprovalSLAStatusView(APIView):
    """
    GET /api/leave/approvals/sla-status/
    Get SLA status for all pending approvals.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = Employee.objects.get(employee_user_id=request.user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        pending = ApprovalRequest.objects.filter(approver=employee, status="pending")

        overdue = []
        warning = []
        on_time = []

        for approval in pending:
            if approval.is_overdue():
                overdue.append(
                    {
                        "id": approval.id,
                        "leave_request_id": approval.leave_request.id,
                        "employee": str(approval.leave_request.employee_id),
                        "days_overdue": max(
                            0, (timezone.now() - approval.sla_deadline).days
                        ),
                    }
                )
            elif approval.days_until_sla_breach() < 2:
                warning.append(
                    {
                        "id": approval.id,
                        "leave_request_id": approval.leave_request.id,
                        "employee": str(approval.leave_request.employee_id),
                        "hours_remaining": max(
                            0, approval.days_until_sla_breach() * 24
                        ),
                    }
                )
            else:
                on_time.append(
                    {
                        "id": approval.id,
                        "leave_request_id": approval.leave_request.id,
                        "employee": str(approval.leave_request.employee_id),
                        "hours_remaining": approval.days_until_sla_breach() * 24,
                    }
                )

        return Response(
            {
                "overdue_count": len(overdue),
                "warning_count": len(warning),
                "on_time_count": len(on_time),
                "overdue": overdue,
                "warning": warning,
                "on_time": on_time,
            }
        )
